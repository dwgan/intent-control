
from detector import JointIntentSlotDetector

model = JointIntentSlotDetector.from_pretrained(
    model_path='result/model/model_epoch7',
    tokenizer_path='result/tokenizer/',
    intent_label_path='data/intent_labels.txt',
    slot_label_path="data/slot_labels.txt"
)

print(model.detect('可以启动二楼的射灯吗'))