import json
import random


def augment_dataset(input_file, output_file, copy_times=1):
    """
    数据集增强函数
    :param input_file: 原始数据集路径
    :param output_file: 增强后输出路径
    :param copy_times: 每个样本复制的次数（默认为1次）
    """
    # 读取原始数据
    with open(input_file, 'r', encoding='utf-8') as f:
        original_data = json.load(f)

    # 复制样本
    augmented_data = original_data * (copy_times + 1)

    # 高质量随机打乱（使用不同随机种子多次打乱）
    for _ in range(3):
        random.Random(_).shuffle(augmented_data)

    # 保存增强后的数据
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(augmented_data, f, ensure_ascii=False, indent=2)

    # 打印统计信息
    print(f"成功处理：{len(original_data)} → {len(augmented_data)} 条")
    print(f"保存路径：{output_file}")
    print("数据分布示例：")
    for sample in augmented_data[:3]:
        print(f" - {sample['text'][:15]}...")


if __name__ == "__main__":
    # 配置参数
    INPUT_PATH = "data.json"  # 原始数据集路径
    OUTPUT_PATH = "train.json"  # 输出路径
    COPY_TIMES = 1  # 每个样本复制次数

    # 执行增强
    augment_dataset(INPUT_PATH, OUTPUT_PATH, COPY_TIMES)