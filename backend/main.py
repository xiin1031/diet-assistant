# 这是一个示例 Python 脚本。

# 按 Shift+F10 执行或将其替换为您的代码。
# 按 双击 Shift 在所有地方搜索类、文件、工具窗

def print_hi(name):
    # 在下面的代码行中使用断点来调试脚本。
    print(f'Hi, {name}')  # 按 Ctrl+F8 切换断点。


# 按装订区域中的绿色按钮以运行脚本。
# 访问 https://www.jetbrains.com/help/pycharm/ 获取 PyCharm 帮助
from module import Food,User
from datetime import datetime,date

import os
from api import (
    initialize,
    get_food_list,
    get_food_by_name,
    create_user,
    add_meal,
    get_today_summary,
    recognize_food_from_image
)

if __name__ == "__main__":
    csv_path = "nutrition(3).csv"
    if not os.path.exists(csv_path):
        print(f"错误：未找到文件 {csv_path}")
        exit()

    initialize(csv_path)
    print("数据初始化成功！")

    #用户手动选择测试
    print("\n食物列表前5项:", get_food_list()[:5])
    rice = get_food_by_name("白米饭")
    if rice:
        user = create_user("小明", age=20)
        add_meal(user, rice, 200)
        summary = get_today_summary(user)
        print(f"\n用户 {user.name} 的今日摄入:")
        print(f"今日钠摄入: {summary['today_sodium']} mg")
        print(f"每日上限: {summary['daily_limit']} mg")
        print(f"剩余可摄入: {summary['remaining']} mg")
        print(f"是否超标: {'是' if summary['is_exceeded'] else '否'}")
    else:
        print("\n未找到白米饭的数据，请检查CSV文件")


    print("\n--- 图像识别测试 ---")
    if os.path.exists("test.jpg"):
        try:
            eng_name, confidence, chn_name, sodium = recognize_food_from_image("test.jpg")
            print(f"识别结果: {chn_name} ({eng_name})")
            print(f"置信度: {confidence:.2f}")
            print(f"钠含量: {sodium} mg/100g")
        except Exception as e:
            print(f"图像识别失败: {e}")
    else:
        print("未找到 test.jpg，跳过图像识别测试（你可以放一张图片到项目里测试）")
import os
if os.path.exists("test.jpg"):
    eng, conf, chn, sodium = recognize_food_from_image("test.jpg")
    print(...)
else:
    print("未找到 test.jpg，跳过图像识别测试")

#调用示例：
if __name__ == "__main__":
# 1. 创建食物对象（名称，每克钠含量mg）
    rice = Food("白米饭", 0.1)    # 1克米饭含0.1mg钠
    salt = Food("食用盐", 390)    # 1克盐含390mg钠
    bread = Food("全麦面包", 0.4) # 1克面包含0.4mg钠


# 2. 创建用户：小明，5岁，有糖尿病，血压正常
    xiaoming = User(User_name="小明", age=5, diseases=["糖尿病"])

# 3. 显示用户信息
    print("===== 用户信息 =====")
    print(xiaoming.summary())

# 4. 吃米饭 150克
    xiaoming.add_meal(rice, 150)
    print("\n===== 吃完饭后 =====")
    print(f"今日已摄入钠：{xiaoming.get_today_sodium()} mg")

