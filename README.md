# 基于BERT的对话意图和槽位联合识别模块

本仓库实现了一个基于BERT的意图和槽位联合预测功能，参考[bert-intent-slot-detector](https://github.com/Linear95/bert-intent-slot-detector)

本仓库添加了智能家居领域的数据集，并且提供了制作数据集的脚本，用户可以跟据自己的需要构建自己的数据集。

## News

- Last update on Feb. 24, 2025

## 运行环境
- Python 3.9.2
- Pytorch 2.0.1
- Huggingface Transformers 4.49.0

直接创建环境
```angular2html
# 1. 先通过Conda创建环境
conda env create -f environment.yml

# 2. 激活环境
conda activate 环境名称

# 3. 安装Pip包（在已激活的环境中）
pip install -r requirements.txt
```

## 直接使用训练好的模型

在release_2.0中下载`bert-base-chinese.zip`和`result.zip`这两个文件并且解压到该项目的根目录，运行`python test.py`，查看结果。

如果希望训练一个自己的模型，接着往下看

## 数据准备

1. 生成数据集：通过运行`python data_generate.py`脚本，自动生成`data.json`数据集。数据集以json格式给出，每条数据包括三个关键词：`text`表示待检测的文本，`intent`代表文本的类别标签，`slots`是文本中包括的所有槽位以及对应的槽值，以字典形式给出。

```json
{
  "text": "请帮我开启一楼的三号灯",
  "domain": "app",
  "intent": "OPEN",
  "slots": {
    "room": "一楼",
    "device": "三号灯"
  }
}
```

2. 数据增强：通过运行`python data_augment.py`脚本，基于`data.json`中的数据扩充数据集，同时打乱样本的顺序，生成`train.json`文件

3. 生成验证集：通过运行`python split_test_data.py`脚本，从`data.json`随机提取样本作为验证集，自动生成`test.json`验证集

5. 生成意图标签和槽位标签：通过运行`python extract_labels.py`生成意图标签和槽位标签。意图标签以txt格式给出，每行一个意图，未识别意图以`[UNK]`标签表示。槽位标签包括三个特殊标签： `[PAD]`表示输入序列中的padding token, `[UNK]`表示未识别序列标签, `[O]`表示没有槽位的token标签。对于有含义的槽位标签，又分为以'B_'开头的槽位开始的标签, 以及以'I_'开头的其余槽位标记两种。

```txt
[UNK]
OPEN
CLOSE
```
```txt
[PAD]
[UNK]
[O]
I_room
B_room
I_device
B_device
```

## 模型训练

可以使用以下命令进行模型训练，这里我们选择在`bert-base-chinese`预训练模型基础上进行finetune：
```bash
python train.py \
       --tokenizer_path "bert-base-chinese" \
       --model_path "bert-base-chinese" \
       --train_data_path "data/train.json" \
       --test_data_path "data/test.json" \
       --intent_label_path "data/intent_labels.txt" \
       --slot_label_path "data/slot_labels.txt" \
       --save_dir "result" \
       --batch_size 64 \
       --train_epochs 5
```

## 意图与槽位预测
训练结束后，我们通过在`JointIntentSlotDetector`类中加载训练好的模型进行意图与槽位预测。
```python
from detector import JointIntentSlotDetector

model = JointIntentSlotDetector.from_pretrained(
    model_path='result/model/model_epoch7',
    tokenizer_path='result/tokenizer/',
    intent_label_path='data/intent_labels.txt',
    slot_label_path="data/slot_labels.txt"
)

print(model.detect('可以启动二楼的射灯吗'))

# outputs:
# {'text': '可以启动二楼的射灯吗', 'intent': 'OPEN', 'slots': {'room': ['二楼'], 'device': ['射灯']}}
```
