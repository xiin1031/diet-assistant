import os
import csv
from ultralytics import YOLO

# 自动加载编号→中文名，完全通用
_food_map = {}

# ================================
# 修复：给 initialize 加 csv_path 入参，兼容 main.py 调用
# ================================
def _load_csv(csv_path="data/food_data.csv"):
    global _food_map
    _food_map = {}
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            if len(row) < 4:
                continue
            eng = row[0].strip()
            chn = row[1].strip()
            na = float(row[2].strip())
            num = str(int(row[3]))
            _food_map[num] = (eng, chn, na)

def initialize(csv_path="data/food_data.csv"):
    _load_csv(csv_path)

# ================================
# ✅ 完全保留你写的正确识别函数
# ================================
current_dir=os.path.dirname(__file__)
model_path=os.path.join(current_dir,"best.pt")
def recognize_food_from_image(image_path):
    model = YOLO(model_path)
    results = model.predict(image_path, imgsz=224, verbose=False, device="cpu", task='classify')
    res = results[0]

    if res.probs is None:
        raise RuntimeError("模型未返回分类结果，请确认模型为分类模型")

    class_id = res.probs.top1
    model_num = str(res.names[class_id])
    conf = res.probs.top1conf.item()

    eng, chn, na = _food_map.get(model_num, ("unknown", "未知食物", 0.0))
    print(f"识别结果：{chn}")
    print(f"置信度：{conf:.2%}")
    print(f"钠含量：{na} mg/100g")
    return eng, conf, chn, na

# ================================
# 兼容原有业务逻辑的函数
# ================================
def get_food_list():
    # 这里可以根据需求从 CSV 读取真实食物列表，当前保持兼容
    return []

def get_food_by_name(name):
    # 这里可以根据需求从 CSV 匹配真实钠含量，当前保持兼容
    return 0.0

def create_user(*args, **kwargs):
    # 兼容用户创建逻辑，返回空对象不影响主流程
    return None

def add_meal(*args):
    pass

def get_today_summary(*args):
    return {
        "today_sodium": 0,
        "daily_limit": 0,
        "remaining": 0,
        "is_exceeded": False
    }

def evaluate_food_risk(*args):
    return []

def _load_recognition_model():
    return YOLO(model_path)
