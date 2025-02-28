import json
import torch
from transformers import BertTokenizer
from datasets import IntentSlotDataset
from models import JointBert
from detector import JointIntentSlotDetector
import jieba
import numpy as np


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


device = "cpu"

tokenizer = BertTokenizer.from_pretrained("result/tokenizer")

with open('data/test.json', 'r') as f:
    test_data = json.load(f)


# -----------load data-----------------
dataset = IntentSlotDataset.load_from_path(
    data_path=test_data,
    intent_label_path='data/intent_labels.txt',
    slot_label_path='data/slot_labels.txt',
    tokenizer=tokenizer,
    word_tokenizer=jieba  # 传入外部词分词器
)

# -----------load model-----------
model = JointBert.from_pretrained(
    'result/model/model_epoch7',
    slot_label_num=dataset.slot_label_num,
    intent_label_num=dataset.intent_label_num
)
model.resize_token_embeddings(len(tokenizer))  # 关键步骤
model = model.to(device).eval()

detector = JointIntentSlotDetector(
    model=model,
    tokenizer=tokenizer,
    intent_dict=dataset.intent_label_dict,
    slot_dict=dataset.slot_label_dict
)

intent_acc_results = []
slot_precision_results = []
slot_recall_results = []
for item in test_data:
    outputs = detector.detect(item['text'])
    print(outputs)
    label_slots = filter_slots(item['text'], item['slots'])

    intent_acc_results.append(float(outputs['intent'] == item['intent']))
    slot_precision_results.append(calculate_slot_precision(outputs['slots'], label_slots))
    slot_recall_results.append(calculate_slot_precision(label_slots, outputs['slots']))

print(f"意图识别准确率：{np.mean(intent_acc_results)}, 槽位识别准确率：{np.mean(slot_precision_results)}, 召回准确率：{np.mean(slot_recall_results)}")
