from detector import JointIntentSlotDetector
import argparse

def main():
    # 设置命令行参数解析
    parser = argparse.ArgumentParser(description='意图和槽位检测脚本')
    parser.add_argument(
        'query',
        nargs='?',  # 允许可选参数
        default='请帮我我打开楼上的灯',  # 默认查询
        type=str,
        help='需要检测的查询文本（默认：可以启动二楼的射灯吗）'
    )
    args = parser.parse_args()

    # 加载预训练模型
    model = JointIntentSlotDetector.from_pretrained(
        model_path='result/model/model_epoch4',
        tokenizer_path='result/tokenizer/',
        intent_label_path='data/intent_labels.txt',
        slot_label_path="data/slot_labels.txt"
    )

    # 执行检测并输出结果
    print(f"检测查询：{args.query}")
    print(model.detect(args.query))

if __name__ == "__main__":
    main()