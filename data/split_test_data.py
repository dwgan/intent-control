import json
import random
import os


def split_dataset(input_file, test_ratio=0.05, seed=42):
    """
    数据集分割函数
    :param input_file: 原始数据集路径
    :param test_ratio: 测试集比例 (默认5%)
    :param seed: 随机种子 (确保可重复性)
    :return: (训练集, 测试集)
    """
    # 读取原始数据
    with open(input_file, 'r', encoding='utf-8') as f:
        dataset = json.load(f)

    # 设置随机种子
    random.seed(seed)

    # 计算测试集数量
    total = len(dataset)
    test_size = max(1, round(total * test_ratio))  # 至少保留1个样本

    # 随机采样
    test_indices = random.sample(range(total), test_size)
    test_set = [dataset[i] for i in test_indices]

    # 训练集为剩余样本
    train_set = [sample for idx, sample in enumerate(dataset) if idx not in test_indices]

    return train_set, test_set


def save_datasets(train_data, test_data, output_dir="output"):
    """保存分割后的数据集"""
    os.makedirs(output_dir, exist_ok=True)

    train_path = os.path.join(output_dir, "train.json")
    test_path = os.path.join(output_dir, "test.json")

    # with open(train_path, 'w', encoding='utf-8') as f:
    #     json.dump(train_data, f, ensure_ascii=False, indent=2)

    with open(test_path, 'w', encoding='utf-8') as f:
        json.dump(test_data, f, ensure_ascii=False, indent=2)

    return train_path, test_path


if __name__ == "__main__":
    # 配置参数
    INPUT_FILE = "data.json"  # 原始数据集路径
    OUTPUT_DIR = "./"  # 输出目录
    TEST_RATIO = 0.05  # 测试集比例

    # 执行分割
    train_data, test_data = split_dataset(INPUT_FILE, TEST_RATIO)

    # 保存结果
    train_path, test_path = save_datasets(train_data, test_data, OUTPUT_DIR)

    # 打印统计信息
    print(f"数据集分割完成")
    print(f"原始数据量: {len(train_data) + len(test_data)}")
    print(f"训练集数量: {len(train_data)} ({len(train_data) / (len(train_data) + len(test_data)):.1%})")
    print(f"测试集数量: {len(test_data)} ({len(test_data) / (len(train_data) + len(test_data)):.1%})")
    # print(f"训练集路径: {train_path}")
    print(f"测试集路径: {test_path}")