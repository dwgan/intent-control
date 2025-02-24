from detector import JointIntentSlotDetector
import time

start1_time = time.perf_counter()
model = JointIntentSlotDetector.from_pretrained(
    model_path='./result/model/model/model_epoch6',
    tokenizer_path='./result/model/model/model_epoch6',
    intent_label_path='./data/SMP2019/intent_labels.txt',
    slot_label_path='./data/SMP2019/slot_labels.txt'
)
start2_time = time.perf_counter()
all_text = ['请打开卧室的灯', "开门", "关上门", "给老王发短信说我饿了", "打开厨房的灯", "打开厨房空调"]
for i in all_text:
    print(model.detect(i))
end_time = time.perf_counter()
time1 = (end_time - start1_time) / 3600
time2 = (end_time - start2_time) / 3600
print("所有检测时间（包括加载模型）：", time1, "s", "除去模型加载时间：", time2, "s",
      "总预测数据量：", len(all_text), "平均预测一条的时间（除去加载模型）：", time2 / len(all_text), "s/条")
