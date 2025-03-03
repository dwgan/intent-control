from detector import JointIntentSlotDetector
import time

start1_time = time.perf_counter()
model = JointIntentSlotDetector.from_pretrained(
    model_path='./result/model/model/model_epoch4',
    tokenizer_path='result/tokenizer',
    intent_label_path='data/intent_labels.txt',
    slot_label_path='data/slot_labels.txt'
)
start2_time = time.perf_counter()
all_text = ['请帮我开启厨房的彩灯', "请关掉一楼的彩灯", "请帮我启动厨房的灯带", "请帮我启动二楼的大门", "请关闭车库的二号灯", "请开启餐厅的充电桩", "请帮我关闭书房的窗帘", "请关掉车库的空调"]
for i in all_text:
    print(model.detect(i))
end_time = time.perf_counter()
time1 = (end_time - start1_time) / 3600
time2 = (end_time - start2_time) / 3600
print("所有检测时间（包括加载模型）：", time1, "s", "除去模型加载时间：", time2, "s",
      "总预测数据量：", len(all_text), "平均预测一条的时间（除去加载模型）：", time2 / len(all_text), "s/条")
