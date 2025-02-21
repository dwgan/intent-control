# Intent-Control

这是一个用于意图识别的项目，利用与训练的[bert-slot](https://huggingface.co/google-bert/bert-base-chinese/tree/main)进行微调，添加了智能领域的数据进行微调，可用于控制空调、灯、门的开关。

配合语音识别模块，可实现智能语音控制。

## 如何配置环境

```bash
conda env create -f environment.yml
pip install -r pip_requirements.txt
```

## 参考

> https://github.com/Linear95/bert-intent-slot-detector
> 
> https://github.com/mzc421/NLP/tree/main/bert-intent-slot
