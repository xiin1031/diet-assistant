from modle import User

class RuleEngine:
    def check_risk(self, food_list, user):
        total_sodium = sum(food.per_meal_sodium(weight) for food, weight in food_list)
        if total_sodium > user.daily_limit:
            return "红灯"
        else:
            return "绿灯"