import os
import argparse
import json

import numpy as np

import torch
from torch.utils.data import DataLoader

import transformers
from transformers import BertTokenizer, BertConfig
from transformers import get_linear_schedule_with_warmup

from datasets import IntentSlotDataset
from models import JointBert
from tools import save_module

from detector import JointIntentSlotDetector

import jieba
import random

def evaluate_model(args, model, tokenizer, test_data, intent_dict, slot_dict):

    def calculate_slot_precision(p_slots, o_slots):
        results = []
        for slot_name, slot_value_list in p_slots.items():
            for slot_value in slot_value_list:
                results.append(float(slot_name in o_slots and slot_value in o_slots[slot_name]))
                
        if len(results) == 0:
            return 1.
        return np.mean(results)

    def filter_slots(text, slots):
        outputs = {}
        for slot_name, slot_value_list in slots.items():
            if not isinstance(slot_value_list, list):
                slot_value_list = [slot_value_list]
            output_value_list = []
            for slot_value in slot_value_list:
                if slot_value in text:
                    output_value_list.append(slot_value)
            if len(output_value_list) > 0:
                outputs[slot_name] = output_value_list
        return outputs
                           
    detector = JointIntentSlotDetector(
        model=model,
        tokenizer=tokenizer,
        intent_dict=intent_dict,
        slot_dict=slot_dict
    )

    intent_acc_results = []
    slot_precision_results = []
    slot_recall_results = []
    for item in test_data:
        outputs = detector.detect(item['text'])
        label_slots = filter_slots(item['text'], item['slots'])
        
        intent_acc_results.append(float(outputs['intent'] == item['intent']))
        slot_precision_results.append(calculate_slot_precision(outputs['slots'], label_slots))
        slot_recall_results.append(calculate_slot_precision(label_slots, outputs['slots']))
        
    return np.mean(intent_acc_results), np.mean(slot_precision_results), np.mean(slot_recall_results)
                                      
    

def train(args):
    #-----------set cuda environment-------------
    os.environ["CUDA_VISIBLE_DEVICES"] = args.cuda_devices
    device = "cuda" if torch.cuda.is_available() and not args.no_cuda else "cpu"

    #-----------load tokenizer-----------
    tokenizer = BertTokenizer.from_pretrained(args.tokenizer_path)
    # 你的领域关键词
    custom_tokens = [
        # 意图
        "打开", "关闭", "开启", "关上", "启动", "关掉",
        # 房间位置
        "厨房", "书房", "二楼", "车库", "客厅", "餐厅", "卧室", "一楼",
        # 设备名称
        "大门", "充电桩", "光伏", "冰箱", "阀门", "窗帘", "风扇", "空调", "充电桩", "一号灯", "二号灯", "三号灯", "四号灯", "大灯", "射灯", "灯带", "彩灯", "总开关"
    ]
    tokenizer.add_tokens(custom_tokens)
    save_module(tokenizer, args.save_dir, module_name="tokenizer", additional_name="")

    #-----------数据增强：同义词替换-----------
    with open(args.train_data_path, 'r') as f:
        raw_train_data = json.load(f)

    synonym_enhancement = False # 同义词增强
    if synonym_enhancement == True:
        def augment_data(raw_data):
            synonyms = {"厨房": ["灶间", "厨房间"], "空调": ["冷气机"]}
            augmented = []
            for example in raw_data:
                new_text = example["text"]
                for word, syns in synonyms.items():
                    if word in new_text and random.random() < 0.3:
                        new_text = new_text.replace(word, random.choice(syns))
                augmented.append({"text": new_text, "intent": example["intent"], "slots": example["slots"]})
            return raw_data + augmented  # 原始数据 + 增强数据

        augmented_train_data = augment_data(raw_train_data)
    else:
        augmented_train_data = raw_train_data # 不用同义词增强

    #-----------load data-----------------
    dataset = IntentSlotDataset.load_from_path(
        data_path=augmented_train_data,
        intent_label_path=args.intent_label_path,
        slot_label_path=args.slot_label_path,
        tokenizer=tokenizer,
        word_tokenizer=jieba  # 传入外部词分词器
    )

    with open(args.test_data_path, 'r') as f:
        test_data = json.load(f)


    #-----------load model-----------
    model = JointBert.from_pretrained(
        args.model_path,
        slot_label_num = dataset.slot_label_num,
        intent_label_num = dataset.intent_label_num
    )
    model.resize_token_embeddings(len(tokenizer))  # 关键步骤
    print(model)
    model = model.to(device).train()
    save_module(model, args.save_dir, module_name='model', additional_name="epoch0")
     
    dataloader = DataLoader(
        dataset,
        shuffle=True,
        batch_size=args.batch_size,
        collate_fn=dataset.batch_collate_fn)

    #-----------calculate training steps-----------
    if args.max_training_steps > 0:
        total_steps = args.max_training_steps
    else:
        total_steps = len(dataset) * args.train_epochs // args.gradient_accumulation_steps // args.batch_size
        

    print('calculated total optimizer update steps : {}'.format(total_steps))

    #-----------prepare optimizer and schedule------------
    parameter_names_no_decay = ['bias', 'LayerNorm.weight']
    optimizer_grouped_parameters = [
        {'params': [
            para for para_name, para in model.named_parameters()
            if not any(nd_name in para_name for nd_name in parameter_names_no_decay)
            ],
         'weight_decay': args.weight_decay},
        {'params': [
            para for para_name, para in model.named_parameters()
            if any(nd_name in para_name for nd_name in parameter_names_no_decay)
            ],
         'weight_decay': 0.0}
    ]
    optimizer = transformers.AdamW(optimizer_grouped_parameters, lr=args.learning_rate, eps=args.adam_epsilon)
    scheduler = get_linear_schedule_with_warmup(optimizer, num_warmup_steps=args.warmup_steps, num_training_steps=total_steps)

    #-----------training-------------
    update_steps = 0
    total_loss = 0.
    
    for epoch in range(args.train_epochs):
        step = 0
        for batch in dataloader:
            step += 1
            input_ids, intent_labels, slot_labels = batch
        
            outputs = model(
                input_ids=torch.tensor(input_ids).long().to(device),
                intent_labels=torch.tensor(intent_labels).long().to(device),
                slot_labels=torch.tensor(slot_labels).long().to(device)
            )

            loss = outputs['loss']
            total_loss += loss.item()
            
            if args.gradient_accumulation_steps > 1:
                loss = loss/args.gradient_accumulation_steps

            loss.backward()

            if step % args.gradient_accumulation_steps == 0:
                torch.nn.utils.clip_grad_norm_(model.parameters(), args.max_grad_norm)

                optimizer.step()
                scheduler.step()
                model.zero_grad()
                update_steps += 1

                if args.logging_steps > 0 and update_steps % args.logging_steps == 0:
                    print("total step {} epoch {} : loss {}".format(update_steps, epoch, total_loss / args.logging_steps))
                    total_loss = 0.

                if args.saving_steps > 0 and update_steps % args.saving_steps == 0:
                
                    save_module(model, args.save_dir, module_name='model', additional_name="model_step{}".format(update_steps))
                    

        if args.saving_epochs > 0 and (epoch+1) % args.saving_epochs == 0:
            save_module(model, args.save_dir, module_name='model', additional_name="model_epoch{}".format(epoch))


        if update_steps > total_steps:
            break


        intent_acc, slot_prec, slot_recall = evaluate_model(
            args=args,
            model=model,
            tokenizer=tokenizer,
            test_data=test_data,
            intent_dict=dataset.intent_label_dict,
            slot_dict=dataset.slot_label_dict
        )
        print('*****evaluation results*****')
        print('intent accuracy: {}; slot precision: {}; slot recall: {}'.format(intent_acc, slot_prec, slot_recall))


                                           


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    
    # environment parameters
    parser.add_argument("--cuda_devices", type=str, default='0', help='set cuda device numbers')
    parser.add_argument("--no_cuda", action='store_true', default=False, help='whether use cuda device for training')
    
    # model parameters
    parser.add_argument("--tokenizer_path", type=str, default='bert-base-chinese',  help="pretrained tokenizer loading path")
    parser.add_argument("--model_path", type=str, default='bert-base-chinese',  help="pretrained model loading path")

    # data parameters
    parser.add_argument("--train_data_path", type=str, default='data/train.json',  help="training data path")
    parser.add_argument("--test_data_path", type=str, default='data/test.json',  help="testing data path")
    parser.add_argument("--slot_label_path", type=str, default='data/slot_labels.txt',  help="slot label path")
    parser.add_argument("--intent_label_path", type=str, default='data/intent_labels.txt',  help="intent label path")

    # training parameters
    parser.add_argument("--save_dir", type=str, default='result',  help="directory to save the model")
    parser.add_argument("--max_training_steps", type=int, default=0, help = 'max training step for optimizer, if larger than 0')
    parser.add_argument("--gradient_accumulation_steps", type=int, default=1, help="number of updates steps to accumulate before performing a backward() pass.")
    parser.add_argument("--saving_steps", type=int, default=300, help="parameter update step number to save model")
    parser.add_argument("--logging_steps", type=int, default=10, help="parameter update step number to print logging info.")
    parser.add_argument("--eval_steps", type=int, default=10, help="parameter update step number to print logging info.")
    parser.add_argument("--saving_epochs", type=int, default=1, help="parameter update epoch number to save model")
    
    parser.add_argument("--batch_size", type=int, default=64, help = 'training data batch size')
    parser.add_argument("--train_epochs", type=int, default=10, help = 'training epoch number')

    parser.add_argument("--learning_rate", type=float, default=5e-5, help = 'learning rate')
    parser.add_argument("--adam_epsilon", type=float, default=1e-8, help="epsilon for Adam optimizer")
    parser.add_argument("--warmup_steps", type=int, default=0, help="warmup step number")
    parser.add_argument("--weight_decay", type=float, default=0.0, help="weight decay rate")
    parser.add_argument("--max_grad_norm", type=float, default=1.0, help="maximum norm for gradients")
        
    args = parser.parse_args()

    train(args)





                                      
