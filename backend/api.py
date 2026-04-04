import os
from modle import Food, User
from data_loader import FoodData
from rule_engine import RuleEngine
from ultralytics import YOLO

food_db = None
_recognition_model = None

def initialize(csv_path="food_nutrition_simple.csv"):
    global food_db
    food_db = FoodData(csv_path)
#返回中文名提供可自行选择的菜单
def get_food_list():
    if food_db is None:
        raise RuntimeError("先调用initialize（），初始化数据")
    return food_db.get_all_chinese()

def get_food_by_name(chinese_name):
    if food_db is None:
        raise RuntimeError("调用initialize，先初始化数据")
    sodium = food_db.get_sodium_by_chinese(chinese_name)
    if sodium is not None:
        return Food(chinese_name,sodium)
    return None

def create_user(name, age=None, diseases=None, sbp=None, dbp=None, custom_limit=None):
    return User(name, age, diseases, sbp, dbp, custom_limit)

def add_meal(user, food, weight_g):
    user.add_meal(food, weight_g)

def get_today_summary(user):
    today_sodium = user.get_today_sodium()
    remaining = max(0.00, user.daily_limit - today_sodium)
    is_exceeded = today_sodium > user.daily_limit
    return {
        "today_sodium": round(today_sodium,2),
        "daily_limit": user.daily_limit,
        "remaining": round(remaining,2),
        "is_exceeded": is_exceeded
    }

def evaluate_food_risk(food_list, user):
    engine = RuleEngine()
    return engine.check_risk(food_list, user)
#图像识别模型
def _load_recognition_model():
    global _recognition_model
    if _recognition_model is None:
        model_path = r"D:\桌面\项目1\runs\classify\models\food101_cls\weights\best.pt"
        if not os.path.exists(model_path):
            raise FileNotFoundError("模型路径错误，检查best.pt位置")
        _recognition_model = YOLO(model_path)
    return _recognition_model
#识别食物
def recognize_food_from_image(image_path):
    if food_db is None:
        raise RuntimeError("请先调用 initialize() 初始化数据")
    model = _load_recognition_model()
#使用cpu防止版本不兼容
    results = model.predict(image_path, imgsz=224, verbose=False, device="cpu")
    top1_idx = results[0].probs.top1
    confident = results[0].probs.top1conf.item()
    english_name = model.names[top1_idx]

    chinese_name, sodium = food_db.get_by_label(english_name)
    if chinese_name is None:
        chinese_name = english_name
        sodium = 0.00
    return english_name, confident, chinese_name, sodium