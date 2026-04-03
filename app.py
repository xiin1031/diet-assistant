# app.py - 饮食助手前端界面
import streamlit as st
import pandas as pd
import json

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
    st.markdown("请填写以下信息：")
    
    patient_name = st.text_input("姓名", value="测试患者")
    has_hypertension = st.checkbox("是否患有高血压？", value=True)
    has_kidney_disease = st.checkbox("是否患有肾脏疾病？", value=False)
    age = st.slider("年龄", 18, 100, 65)
    
    st.markdown("---")
    st.caption("⚠️ 高钠食物会增加高血压和心血管疾病风险")

# ========== 主要内容区域 ==========
tab1, tab2, tab3 = st.tabs(["📋 选择食物", "🔍 批量检测", "📊 食物数据库"])

# ========== Tab 1: 单个食物选择 ==========
with tab1:
    st.subheader("单个食物风险检测")
    
    # 模拟食物数据（实际应从角色A的CSV读取）
    food_list = [
        "咸菜", "腊肉", "火腿肠", "方便面", "薯片", 
        "新鲜蔬菜", "苹果", "鸡胸肉", "米饭", "豆腐"
    ]
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        selected_food = st.selectbox("选择食物", food_list)
    
    with col2:
        quantity = st.number_input("份量 (克)", min_value=10, max_value=500, value=100, step=10)
    
    if st.button("检测风险", type="primary", key="single_check"):
        # 调用后端逻辑（这里先用模拟函数）
        result = mock_check_risk(selected_food, has_hypertension, quantity)
        
        # 显示结果
        if result["risk"] == "红灯":
            st.error(f"⚠️ {result['message']}")
        elif result["risk"] == "黄灯":
            st.warning(f"⚡ {result['message']}")
        else:
            st.success(f"✅ {result['message']}")
        
        # 显示详细信息
        with st.expander("查看详细分析"):
            st.write(f"**食物名称：** {selected_food}")
            st.write(f"**钠含量：** {result['sodium_mg']} mg")
            st.write(f"**风险等级：** {result['risk']}")
            st.write(f"**建议：** {result['advice']}")

# ========== Tab 2: 批量检测 ==========
with tab2:
    st.subheader("批量检测多份食物")
    st.info("💡 输入多个食物，系统会列出所有高风险项")
    
    # 多选食物
    selected_foods = st.multiselect(
        "选择多个食物",
        food_list,
        default=["咸菜", "米饭", "火腿肠"]
    )
    
    if st.button("批量检测", type="primary", key="batch_check"):
        if selected_foods:
            results = []
            for food in selected_foods:
                result = mock_check_risk(food, has_hypertension, 100)
                results.append({
                    "食物": food,
                    "钠含量(mg)": result["sodium_mg"],
                    "风险等级": result["risk"],
                    "建议": result["advice"]
                })
            
            # 显示表格
            df_results = pd.DataFrame(results)
            st.dataframe(df_results, use_container_width=True)
            
            # 统计红灯数量
            red_count = len([r for r in results if r["风险等级"] == "红灯"])
            if red_count > 0:
                st.error(f"⚠️ 发现 {red_count} 种高风险食物，建议避免食用！")
            else:
                st.success("✅ 所选食物风险较低")
        else:
            st.warning("请至少选择一种食物")

# ========== Tab 3: 食物数据库 ==========
with tab3:
    st.subheader("食物钠含量数据库")
    
    # 模拟数据库（实际应从角色A的CSV读取）
    food_db = pd.DataFrame({
        "食物名称": food_list,
        "钠含量(mg/100g)": [1850, 1500, 1200, 2100, 500, 10, 5, 60, 15, 8],
        "风险等级": ["高", "高", "高", "高", "中", "低", "低", "低", "低", "低"]
    })
    
    st.dataframe(food_db, use_container_width=True)
    
    # 搜索功能
    search_term = st.text_input("🔍 搜索食物", placeholder="输入食物名称")
    if search_term:
        filtered = food_db[food_db["食物名称"].str.contains(search_term, na=False)]
        st.dataframe(filtered, use_container_width=True)
    
    st.caption("📝 数据来源：角色A提供的食物数据库")

# ========== 底部信息 ==========
st.markdown("---")
st.caption("⚠️ 本工具仅供参考，不能替代专业医疗建议")

# ========== 模拟后端函数（等待角色B替换） ==========
def mock_check_risk(food_name, has_hypertension, quantity=100):
    """
    模拟风险检测函数
    实际应由角色B的 RuleEngine 替换
    """
    # 模拟食物钠含量数据库
    sodium_db = {
        "咸菜": 1850, "腊肉": 1500, "火腿肠": 1200, "方便面": 2100,
        "薯片": 500, "新鲜蔬菜": 10, "苹果": 5, "鸡胸肉": 60,
        "米饭": 15, "豆腐": 8
    }
    
    sodium_per_100g = sodium_db.get(food_name, 50)
    actual_sodium = sodium_per_100g * (quantity / 100)
    
    # 风险判断逻辑
    if has_hypertension and sodium_per_100g > 500:
        risk = "红灯"
        message = f"⚠️ 高风险！{food_name}钠含量过高({sodium_per_100g}mg/100g)，高血压患者应避免"
        advice = "建议选择低钠替代品，每日钠摄入控制在2000mg以下"
    elif sodium_per_100g > 800:
        risk = "红灯"
        message = f"⚠️ 高风险！{food_name}钠含量过高({sodium_per_100g}mg/100g)"
        advice = "尽量避免食用"
    elif sodium_per_100g > 300:
        risk = "黄灯"
        message = f"⚡ 中等风险！{food_name}钠含量中等({sodium_per_100g}mg/100g)，建议适量"
        advice = "注意控制份量，每日不超过1份"
    else:
        risk = "绿灯"
        message = f"✅ 低风险！{food_name}钠含量较低({sodium_per_100g}mg/100g)，可放心食用"
        advice = "可作为日常饮食选择"
    
    return {
        "risk": risk,
        "message": message,
        "advice": advice,
        "sodium_mg": actual_sodium
    }

# ========== 运行说明 ==========
# 在终端输入：streamlit run app.py
