# 基于BERT的对话意图和槽位联合识别模块

本仓库是intentslot这个项目在数梅派上的部署版本，所有的参数使用release版本训练得到，该版本添加了使用数梅派调用语音检测的模块，以及发送串口指令模块

## News

- Last update on Mar. 3, 2025

## 运行环境
- Python 3.12.8
- Pytorch 2.6.0
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

在release_2.0中下载`bert-base-chinese.zip`和`result.zip`这两个文件并且解压到该项目的根目录，运行`python test.py '请打开二楼的灯'`，查看结果。

## 参考

本项目地址
> https://github.com/dwgan/intentslot

参考
> https://github.com/Linear95/bert-intent-slot-detector
>
>  https://github.com/mzc421/NLP/tree/main/bert-intent-slot

