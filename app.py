
# app.py - 完整版（适配角色A的数据 + 角色B的后端）
import streamlit as st
st.set_page_config(
    page_title="健康服务",
    layout="wide",
    initial_sidebar_state="auto"
)

# ========== 最终质感版 · 年轻简约健康绿 ==========
st.markdown("""
<style>
/* 整体背景：干净浅绿渐变，无杂乱图案，高级柔和 */
.stApp {
    background: linear-gradient(135deg, #F7FBFA 0%, #EFF8F5 100%);
    background-attachment: fixed;
}

/* 标题：稳重健康绿 */
h1, h2, h3, h4, h5, h6 {
    color: #1A5E43 !important;
    font-weight: 600 !important;
}

/* 正文 */
p, li, span {
    color: #3D5158 !important;
    line-height: 1.6 !important;
}

/* 按钮：柔和青绿，大圆角，年轻不土 */
div.stButton > button {
    background-color: #2CCF9F;
    color: white;
    border-radius: 14px;
    padding: 0.6em 1.5em;
    font-size: 15px;
    border: none;
    box-shadow: 0 4px 10px rgba(44, 207, 159, 0.15);
}
div.stButton > button:hover {
    background-color: #26B88E;
    box-shadow: 0 6px 14px rgba(44, 207, 159, 0.2);
}

/* 输入框：简洁圆润 */
.stTextInput > div > div,
.stNumberInput > div > div,
.stSelectbox > div > div,
.stTextArea > div > div 
    {
    border-radius: 12px !important;
    border: 1px solid #D6E9E2 !important;
    }

/* 侧边栏：干净柔和 */
section[data-testid="stSidebar"] {
    background-color: #F2F9F6;
}

/* 卡片：简约白，高级不花哨 */
.element-container {
    background-color: rgba(255, 255, 255, 0.9);
    border-radius: 16px;
    padding: 1.1rem;
    box-shadow: 0 4px 12px rgba(0, 80, 50, 0.05);
    margin-bottom: 1rem;
}
</style>
""", unsafe_allow_html=True)

# ==================== 下面放你原来的全部代码 ====================
import os
os.environ["CUDA_VISIBLE_DEVICES"]="-1"
import cv2
import pandas as pd
import json
import sys
from datetime import datetime

# 添加backend路径，导入角色B的模块
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# 导入角色B的类
from backend.module import Food, User
from backend.rule_engine import RuleEngine
# ========== 新增：图像识别导入 ==========
from backend.api import recognize_food_from_image,initialize

# ========== 新增：初始化后端 ==========
try:
    initialize()
    image_recognition_ready = True
    st.success("✅ 图像识别模块已就绪")
except Exception as e:
    image_recognition_ready = False
    st.warning(f"⚠️ 图像识别模块初始化失败：{e}")

# ========== 页面配置 ==========
st.set_page_config(
    page_title="饮食助手 - 高钠食物风险检测",
    page_icon="🍎",
    layout="wide"
)

# ========== 标题和说明 ==========
st.title("🍎 饮食健康助手")
st.markdown("### 检测食物中的高钠风险，守护心血管健康")
st.markdown("---")

# ========== 侧边栏：病人信息 ==========
with st.sidebar:
    st.header("👤 病人信息")
    
    patient_name = st.text_input("姓名", value="测试患者")
    age = st.number_input("年龄（岁）", min_value=2, max_value=120, value=35, step=1)
    
    st.subheader("血压信息")
    sbp = st.number_input("收缩压（高压）mmHg", min_value=50, max_value=250, value=120, step=5)
    dbp = st.number_input("舒张压（低压）mmHg", min_value=30, max_value=150, value=80, step=5)
    
    st.subheader("疾病状况（可多选）")
    has_kidney_disease = st.checkbox("肾病")
    has_diabetes = st.checkbox("糖尿病")
    has_heart_failure = st.checkbox("心力衰竭")
    has_diabetes_and_hypertension=st.checkbox("糖尿病加高血压")
    has_hypertension=st.checkbox("高血压")
    has_healthy=st.checkbox("普通")
    
    st.subheader("特殊人群")
    is_pregnant = st.checkbox("孕妇")
    is_lactating = st.checkbox("哺乳期")
    
    st.subheader("自定义钠摄入限制（可选）")
    custom_limit = st.number_input("每日钠摄入上限（mg）", min_value=0, max_value=5000, value=0, step=50)
    if custom_limit == 0:
        custom_limit = None
    
    st.markdown("---")
    st.caption("⚠️ 高钠食物会增加高血压和心血管疾病风险")

# ========== 加载数据 ==========
@st.cache_data
def load_food_data():
    """读取角色A提供的 food_data.csv"""
    csv_path = 'data/food_data.csv'
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        return df
    else:
        st.error("❌ 未找到 data/food_data.csv 文件")
        return pd.DataFrame()

@st.cache_data
def load_rule_json():
    """读取角色A提供的 rule.json（备用）"""
    json_path = 'data/rule.json'
    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        return {}

# ========== 创建User对象 ==========
def create_user():
    """
    根据侧边栏输入创建角色B的User对象
    """
    # 收集疾病列表
    diseases = []
    if has_kidney_disease:
        diseases.append("肾病")
    if has_diabetes:
        diseases.append("糖尿病")
    if has_heart_failure:
        diseases.append("心力衰竭")
    if has_hypertension:
        diseases.append("高血压")
    if is_pregnant:
        diseases.append("孕妇")
    if is_lactating:
        diseases.append("哺乳期")
    if has_healty:
        diseases.append("普通")
    
    # 创建User对象（User类会自动根据年龄和血压添加对应疾病）
    user = User(
        User_name=patient_name,
        age=age,
        diseases=diseases,
        sbp=sbp,
        dbp=dbp,
        custom_limit=custom_limit if custom_limit and custom_limit > 0 else None
    )
    
    return user

# ========== 创建Food对象列表 ==========
def create_food_objects(food_items):
    """
    根据食物名称列表创建角色B的Food对象列表
    参数 food_items: list of (food_name, weight_g)
    返回: list of (Food对象, weight_g)
    """
    food_df = load_food_data()
    food_objects = []
    
    for food_name, weight in food_items:
        # 从CSV中查找钠含量
        row = food_df[food_df['chinese_name'] == food_name]
        if not row.empty:
            sodium_per_100g = row['sodium_per_100g'].values[0]
            food_obj = Food(name=food_name, sodium_per_100g=sodium_per_100g)
            food_objects.append((food_obj, weight))
        else:
            st.warning(f"未找到食物：{food_name}")
    
    return food_objects

# ========== 风险检测（调用角色B的RuleEngine） ==========
def check_risk_with_backend(food_items, user):
    """
    调用角色B的 RuleEngine 进行风险检测
    返回: (risk_result, total_sodium)
        risk_result: "红灯" 或 "绿灯"
        total_sodium: 总钠摄入量
    """
    # 创建Food对象列表
    food_objects = create_food_objects(food_items)
    
    if not food_objects:
        return "无法检测", 0
    
    # 调用角色B的RuleEngine
    engine = RuleEngine()
    result = engine.check_risk(food_objects, user)
    
    # 计算总钠摄入量
    total_sodium = sum(food.per_meal_sodium(weight) for food, weight in food_objects)
    
    return result, total_sodium

# ========== 加载食物列表 ==========
food_df = load_food_data()
if not food_df.empty:
    food_names = food_df['chinese_name'].tolist()
else:
    food_names = []

# ========== 主要内容区域 ==========
tab1, tab2, tab3, tab4= st.tabs(["📋 选择食物", "🔍 批量检测", "📊 食物数据库","📷 拍照识别"])

# ========== Tab 1: 单个食物选择 ==========
with tab1:
    st.subheader("单个食物风险检测")
    
    if food_names:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            selected_food = st.selectbox("选择食物", food_names)
        
        with col2:
            quantity = st.number_input("份量 (克)", min_value=10, max_value=500, value=100, step=10)
        
        if st.button("检测风险", type="primary"):
            # 创建User对象
            user = create_user()
            
            # 调用后端检测
            food_items = [(selected_food, quantity)]
            result, total_sodium = check_risk_with_backend(food_items, user)
            
            # 显示用户信息摘要
            st.info(user.summary())
            
            # 显示结果
            if result == "红灯":
                st.error(f"⚠️ 红灯！总钠摄入量 {total_sodium:.0f}mg 超过每日建议摄入量 {user.daily_limit}mg")
            else:
                st.success(f"✅ 绿灯！总钠摄入量 {total_sodium:.0f}mg 未超过每日建议摄入量 {user.daily_limit}mg")
            
            with st.expander("查看详细分析"):
                st.write(f"**食物：** {selected_food}")
                st.write(f"**份量：** {quantity}g")
                st.write(f"**钠摄入量：** {total_sodium:.0f} mg")
                st.write(f"**每日限制：** {user.daily_limit} mg")
                st.write(f"**风险等级：** {result}")
                
                # 显示今日总摄入（如果有历史记录）
                today_sodium = user.get_today_sodium()
                if today_sodium > 0:
                    st.write(f"**今日已摄入：** {today_sodium:.0f} mg")
                    st.write(f"**剩余额度：** {user.daily_limit - today_sodium:.0f} mg")
    else:
        st.warning("⚠️ 未找到食物数据，请确保 data/food_data.csv 文件存在")

# ========== Tab 2: 批量检测 ==========
with tab2:
    st.subheader("批量检测多份食物")
    
    if food_names:
        selected_foods = st.multiselect("选择多个食物", food_names)
        
        # 为每个选中的食物设置份量
        quantities = {}
        if selected_foods:
            st.write("设置每份食物的重量：")
            cols = st.columns(min(len(selected_foods), 3))
            for i, food in enumerate(selected_foods):
                with cols[i % 3]:
                    quantities[food] = st.number_input(f"{food} (克)", min_value=10, max_value=500, value=100, key=food)
        
        if st.button("批量检测", type="primary"):
            if selected_foods:
                # 创建User对象
                user = create_user()
                
                # 构建食物列表
                food_items = [(food, quantities.get(food, 100)) for food in selected_foods]
                result, total_sodium = check_risk_with_backend(food_items, user)
                
                # 显示用户信息摘要
                st.info(user.summary())
                
                # 显示结果
                if result == "红灯":
                    st.error(f"⚠️ 红灯！总钠摄入量 {total_sodium:.0f}mg 超过每日建议摄入量 {user.daily_limit}mg")
                else:
                    st.success(f"✅ 绿灯！总钠摄入量 {total_sodium:.0f}mg 未超过每日建议摄入量 {user.daily_limit}mg")
                
                with st.expander("查看详细清单"):
                    for food, weight in food_items:
                        row = food_df[food_df['chinese_name'] == food]
                        if not row.empty:
                            sodium_per_100g = row['sodium_per_100g'].values[0]
                            sodium_actual = sodium_per_100g * weight / 100
                            st.write(f"- {food} ({weight}g): {sodium_actual:.0f}mg 钠")
            else:
                st.warning("请至少选择一种食物")
    else:
        st.warning("⚠️ 未找到食物数据")

# ========== Tab 3: 食物数据库 ==========
with tab3:
    st.subheader("食物钠含量数据库")
    
    if not food_df.empty:
        display_df = food_df[['chinese_name', 'sodium_per_100g']].copy()
        display_df = display_df.rename(columns={
            'chinese_name': '食物名称',
            'sodium_per_100g': '钠含量(mg/100g)'
        })
        st.dataframe(display_df, use_container_width=True)
        
        search_term = st.text_input("🔍 搜索食物", placeholder="输入食物名称")
        if search_term:
            filtered = food_df[food_df['chinese_name'].str.contains(search_term, na=False)]
            filtered_display = filtered[['chinese_name', 'sodium_per_100g']].rename(columns={
                'chinese_name': '食物名称',
                'sodium_per_100g': '钠含量(mg/100g)'
            })
            st.dataframe(filtered_display, use_container_width=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            avg_sodium = food_df['sodium_per_100g'].mean()
            st.metric("平均钠含量", f"{avg_sodium:.0f} mg/100g")
        with col2:
            max_row = food_df.loc[food_df['sodium_per_100g'].idxmax()]
            st.metric("最高钠含量食物", max_row['chinese_name'], f"{max_row['sodium_per_100g']:.0f} mg")
        with col3:
            st.metric("食物总数", len(food_df))
    else:
        st.info("📭 食物数据库为空")

    st.caption("📝 数据来源：Food-101 Nutritional Information") 


# ========== Tab 4: 拍照识别 ==========
with tab4:
    st.subheader("📷 拍照/上传图片识别食物")
    st.info("💡 拍摄或上传食物图片，系统会自动识别食物名称并计算钠含量")
    
    # 检查图像识别是否可用
    if not image_recognition_ready:
        st.error("❌ 图像识别功能不可用，请检查后端配置")
        st.stop()
    
    # 选择输入方式
    input_method = st.radio("选择输入方式", ["📸 拍照", "📁 上传图片"], horizontal=True)
    
    uploaded_image = None
    
    if input_method == "📸 拍照":
        uploaded_image = st.camera_input("拍照识别食物")
    else:
        uploaded_image = st.file_uploader("上传食物图片", type=["jpg", "jpeg", "png"])
    
    if uploaded_image is not None:
        # 显示图片
        st.image(uploaded_image, caption="上传的图片", width=300)
        
        if st.button("🔍 识别食物", type="primary"):
            with st.spinner("识别中，请稍候..."):
                try:
                    # 保存临时图片
                    import tempfile
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
                        tmp_file.write(uploaded_image.getvalue())
                        tmp_path = tmp_file.name
                    
                    # 调用角色B的识别函数
                    english_name, confidence, chinese_name, sodium = recognize_food_from_image(tmp_path)
                    
                    # 删除临时文件
                    os.unlink(tmp_path)
                    
                    # ========== 显示识别结果 ==========
                    st.success(f"✅ 识别成功！")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("识别食物", chinese_name)
                        st.metric("英文名称", english_name)
                    with col2:
                        st.metric("置信度", f"{confidence:.1%}")
                        st.metric("钠含量 (每100g)", f"{sodium} mg")
                    
                    # ========== 系统建议 ==========
                    st.markdown("---")
                    st.subheader("📋 系统建议")
                    
                    # 根据钠含量给出初步建议
                    if sodium <= 120:
                        sodium_level = "低钠"
                        sodium_color = "🟢"
                        sodium_advice = "该食物钠含量较低，可放心食用。"
                    elif sodium <= 400:
                        sodium_level = "中钠"
                        sodium_color = "🟡"
                        sodium_advice = "该食物钠含量中等，建议适量食用，注意控制份量。"
                    else:
                        sodium_level = "高钠"
                        sodium_color = "🔴"
                        sodium_advice = "该食物钠含量较高，高血压、肾病患者应尽量避免。"
                    
                    # 获取患者每日限制
                    user = create_user()
                    user_daily_limit = user.daily_limit
                    
                    # 计算一份100g占每日限制的比例
                    sodium_per_100g = sodium
                    ratio = (sodium_per_100g / user_daily_limit) * 100
                    
                    # 根据比例给出更具体的建议
                    if ratio > 50:
                        portion_advice = f"⚠️ **警告**：仅100g该食物就占您每日钠摄入限制的 {ratio:.0f}%，建议避免食用或只吃极少份量（<30g）。"
                    elif ratio > 25:
                        portion_advice = f"⚡ **注意**：100g该食物占您每日钠摄入限制的 {ratio:.0f}%，建议控制在50g以内。"
                    else:
                        portion_advice = f"✅ **尚可**：100g该食物仅占您每日钠摄入限制的 {ratio:.0f}%，可适量食用。"
                    
                    # 根据患者健康状况给出个性化建议
                    health_advice = []
                    
                    if "高血压" in user.diseases or any("高血压" in d for d in user.diseases):
                        health_advice.append("🔴 您有高血压，每日钠摄入应控制在2000mg以下，高钠食物会使血压升高。")
                    if "肾病" in user.diseases:
                        health_advice.append("🟠 您有肾脏疾病，肾脏排钠能力下降，需严格控制钠摄入。")
                    if "糖尿病" in user.diseases:
                        health_advice.append("🟡 您有糖尿病，低钠饮食有助于控制血压，降低心血管风险。")
                    if "心力衰竭" in user.diseases:
                        health_advice.append("🟠 您有心力衰竭，钠摄入过多会加重水肿和心脏负担。")
                    
                    # 从侧边栏获取特殊人群信息
                    if is_pregnant:
                        health_advice.append("🤰 您处于孕期，控制钠摄入有助于预防妊娠高血压。")
                    if is_lactating:
                        health_advice.append("🤱 您处于哺乳期，低钠饮食对母婴健康都有益。")
                    
                    if not health_advice:
                        health_advice.append("✅ 您暂无特殊健康状况，但仍建议每日钠摄入不超过2000mg。")
                    
                    # 显示所有建议
                    st.markdown(f"""
                    ### {sodium_color} 食物钠含量评估：**{sodium_level}**（{sodium} mg/100g）
                    - {sodium_advice}
                    - {portion_advice}
                    
                    ### 💊 针对您的健康状况：
                    {''.join([f'- {advice}' for advice in health_advice])}
                    
                    ### 📝 食用建议：
                    | 您的状况 | 建议食用量 |
                    |---------|-----------|
                    | 健康人群 | 每日不超过200g |
                    | 有高血压/肾病 | 不建议食用或少于30g |
                    | 其他慢性病 | 每日不超过100g |
                    """)
                    
                    st.caption(f"📌 您的每日钠摄入上限为 **{user_daily_limit} mg**，请注意控制全天总量。")
                    
                    # ========== 加入风险检测 ==========
                    st.markdown("---")
                    st.subheader("➕ 将此食物加入风险检测")
                    
                    col1, col2 = st.columns([2, 1])
                    with col1:
                        confirm_quantity = st.number_input("份量 (克)", min_value=10, max_value=500, value=100, step=10, key="recog_quantity")
                    with col2:
                        st.write("")
                        st.write("")
                        if st.button("检测此食物", type="primary"):
                            user = create_user()
                            food_items = [(chinese_name, confirm_quantity)]
                            result, total_sodium = check_risk_with_backend(food_items, user)
                            
                            st.info(user.summary())
                            
                            # 计算占每日限制的比例
                            ratio_this = (total_sodium / user.daily_limit) * 100
                            
                            if result == "红灯":
                                st.error(f"⚠️ 红灯！摄入 {total_sodium:.0f}mg 钠，占您每日限制的 {ratio_this:.0f}%，已超标！")
                                st.warning("建议：今日剩余时间请选择低钠食物，多喝水帮助排钠。")
                            else:
                                st.success(f"✅ 绿灯！摄入 {total_sodium:.0f}mg 钠，占您每日限制的 {ratio_this:.0f}%，在安全范围内。")
                
                except Exception as e:
                    st.error(f"识别失败：{str(e)}")
                    st.info("提示：请确保后端模型文件 best.pt 存在且路径正确")
# ========== 底部信息 ==========
st.markdown("---")
st.caption("⚠️ 本工具仅供参考，不能替代专业医疗建议")
