import json
import random
from collections import defaultdict
from itertools import product
from collections import OrderedDict

# 配置参数
OUTPUT_FILE = 'data.json'
SAMPLES_PER_COMBINATION = 2  # 每个基础组合生成样本数
SPECIAL_CASE_RATIO = 0.1  # 特殊案例比例

# 设备标准化映射
device_mapping = {
    "一号灯": "一号灯", "二号灯": "二号灯", "三号灯": "三号灯", "四号灯": "四号灯",
    "大灯": "大灯", "射灯": "射灯", "灯带": "灯带", "彩灯": "彩灯",
    "充电桩": "充电桩"
}

# 意图动词库
verbs = {
    "OPEN": ["打开", "开启", "启动"],
    "CLOSE": ["关闭", "关上", "关掉"]
}

# 房间位置库
rooms = ["厨房", "书房", "二楼", "车库", "客厅", "餐厅", "卧室", "一楼"]

# 设备名称库
devices = [
    "大门", "充电桩", "光伏", "冰箱", "阀门", "窗帘", "风扇",
    "空调", "总开关", "一号灯", "二号灯", "三号灯", "四号灯",
    "大灯", "射灯", "灯带", "彩灯"
]

# 自然语言模板库
templates = [
    "请帮我{v}{room}的{device}",
    "把{room}的{device}{v}一下",
    "可以{v}{room}的{device}吗？",
    "麻烦{v}{device}",
    "{v}那个{room}的{device}吧",
    "需要{v}{device}",
    "请{v}{room}的{device}",
    "帮我操作下{v}{device}",
    "现在要{v}{room}的{device}吗？",
    "系统请{v}{device}"
]


def generate_base_combinations():
    """生成有效的基础组合"""
    combinations = []
    for intent, vs in verbs.items():
        for v in vs:
            for r in rooms:
                for d in devices:
                    # 过滤无效组合规则
                    if valid_combination(r, d):
                        combinations.append((intent, v, r, d))
    return combinations


def valid_combination(room, device):
    """验证组合有效性"""
    # 总开关和光伏不需要房间
    if device in ["总开关", "光伏"] and room is not None:
        return False
    # 其他设备需要房间（允许房间为None）
    return True


def process_text(text):
    """后处理生成的文本"""
    text = text.replace(" 的", "的").replace("的的", "的")
    text = text.replace("  ", " ").strip()
    if text.endswith("的"):
        text = text[:-1]
    return text

def build_ordered_sample(text, intent, device, room=None):
    """构建有序的样本结构"""
    sample = OrderedDict()
    sample["text"] = text
    sample["domain"] = "app"
    sample["intent"] = intent
    # 关键修改：先添加room（如果存在）
    slots = OrderedDict()
    if room:
        slots["room"] = room
    slots["device"] = device

    sample["slots"] = slots
    return sample

def generate_dataset():
    """生成完整数据集"""
    base_combinations = generate_base_combinations()
    dataset = []

    # 生成基础样本
    for _ in range(SAMPLES_PER_COMBINATION):
        random.shuffle(base_combinations)
        for intent, verb, room, device in base_combinations:
            template = random.choice(templates)

            # 处理占位符
            room_str = f"{room}" if room else ""
            device_str = device

            # 生成原始文本
            raw_text = template.format(
                v=verb,
                room=room_str,
                device=device_str
            )

            # 后处理文本
            final_text = process_text(raw_text)

            # 改进的slot生成逻辑
            slot_device = device_mapping.get(device, device)

            dataset.append(build_ordered_sample(final_text, intent, slot_device, room))

        # 特殊案例使用统一构建方式
        special_samples = [
            build_ordered_sample("打开所有灯", "OPEN", "灯"),
            build_ordered_sample("启动车库系统", "OPEN", "总开关", "车库"),
            build_ordered_sample("关闭全部设备", "CLOSE", "总开关")
        ]

        dataset.extend(special_samples)

    # 去重处理
    unique_dataset = []
    seen_texts = set()
    for sample in dataset:
        if sample["text"] not in seen_texts:
            unique_dataset.append(sample)
            seen_texts.add(sample["text"])

    return unique_dataset


if __name__ == "__main__":
    # 生成数据
    dataset = generate_dataset()

    # 保存文件
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(dataset, f, ensure_ascii=False, indent=2)

    # 打印统计信息
    print(f"数据集已生成，总计 {len(dataset)} 条数据")
    print(f"文件已保存至: {OUTPUT_FILE}")
    print("\n数据分布示例:")

    stats = defaultdict(int)
    for sample in dataset:
        key = (sample["intent"], sample["slots"]["device"])
        stats[key] += 1

    for (intent, device), count in list(stats.items())[:5]:
        print(f"{intent}-{device}: {count} 条")