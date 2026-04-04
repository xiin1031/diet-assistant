from datetime import datetime,date
from typing import Optional,List

class Food:
#食物类名称，钠含量记录
    def __init__(self,name:str,sodium_per_100g:float):
        if sodium_per_100g < 0:
            raise ValueError("钠含量不能为负数")#钠含量为负值时输出，防止污染数据库
        self.name = name
        self.sodium_per_100g = sodium_per_100g

    def per_meal_sodium(self,weight_g:float):
        if weight_g < 0:
            raise ValueError("食物重量不能为负数")
        return self.sodium_per_100g * weight_g/100
#食物单位为克，钠含量单位为毫克


class User:
#用户信息记录
#数据来源：中国居民膳食指南2022，中国高血压防治指南2024，WHO标准
     DAILY_LIMITS = {"高血压":2000,
                     "轻度高血压":2000,
                      "中度高血压":800,
                      "重度高血压":0,
        #其他病症补充
                      "肾病":1500,
                      "糖尿病":2300,
                      "糖尿病加高血压":2000,
                      "心力衰竭":2000,
        #其他
                      "孕妇":2000,
                      "哺乳期":2000,
        #根据年龄划分
                      "儿童_2-3岁":800,
                      "儿童_4-6岁":1200,
                      "儿童_7-10岁":1600,
                      "儿童_11岁以上":2000,
        #正常
                      "普通":2000}
     def __init__(self,
                 User_name:str,
                 age:int  = None,
                 diseases:list = None,
                 sbp:float  = None,#高压
                 dbp:float  = None,#低压
                 custom_limit:float = None):
        self.User_name =User_name
        self.age = age
        self.sbp = sbp
        self.dbp = dbp
        self.meal_history = []
        self.custom_limit = custom_limit

    #疾病类型处理
        diseases = diseases or []
        diseases = [d.strip() for d in diseases if d]

    #分类血压
        if sbp is not None and dbp is not None:
            if sbp >= 180 or dbp >= 110:
                diseases.append("重度高血压")
            elif sbp >= 160 or dbp >= 100:
                diseases.append("中度高血压")
            elif sbp >= 140 or dbp >= 90:
                diseases.append("轻度高血压")

    #根据年龄分类
        if age is not None:
            if 2 <= age <= 3:
                diseases.append("儿童_2-3岁")
            elif 4 <= age <= 6:
                diseases.append("儿童_4-6岁")
            elif 7 <= age <= 10:
                diseases.append("儿童_7-10岁")
            elif age >= 11:
                diseases.append("儿童_11岁以上")
    #防止同一种疾病重复输出使列表干净
        self.diseases = list(set(diseases))
    #取最低可摄取钠量,大写daily_limits为固定标准不可变，小写为User个人数据
        limit_list = [self.DAILY_LIMITS.get(d,2000) for d in self.diseases]
        self.daily_limit = min(limit_list) if limit_list else 2000
     #如有医嘱按官方医嘱
        if custom_limit is not None:
            self.daily_limit = custom_limit
#每日饮食记录
     def add_meal(self, food, weight_g:float):
         sodium = food.per_meal_sodium(weight_g)
         self.meal_history.append({
             "food": food,
             "weight_g": weight_g,
             "sodium_mg": sodium,
             "time": datetime.now()
         })
#今日摄入钠量记录
     def get_today_sodium(self)-> float:
         today = date.today()
         total = 0.00
         for record in self.meal_history:
             if record["time"].date() == today:
                 total += record["sodium_mg"]
         return total
#判断今日钠含量
     def is_normal(self,add_sodium = 0):
         if self.get_today_sodium() + add_sodium > self.daily_limit:
             return True
         else:
             return False
#用户信息总汇
     def summary(self)-> str:
         disease_str = "、".join(self.diseases) if self.diseases else "普通"
         return (f"{self.User_name} | 状况：{disease_str} | "
                 f"每日钠上限：{self.daily_limit} mg")
