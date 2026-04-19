import streamlit as st
import pandas as pd

# 1. 网页基本设置
st.set_page_config(page_title="X-Bank AI 治理控制台", layout="wide")
st.title("🛡️ X-Bank AI 治理与合规控制台 (Demo)")
st.markdown("刘桐睿 德勤数字化精英挑战赛原型展示台")

# 2. 创建两个功能切换卡片
tab1, tab2 = st.tabs(["🔴 Agentic Shield 意图防火墙", "🟢 白盒决策翻译官 (X-Explain)"])

# ====== 功能 1：意图防火墙 ======
with tab1:
    st.subheader("高危指令拦截模拟")
    user_input = st.text_area("模拟客户/黑客输入 Prompt (尝试输入包含'电话'、'VIP'、'绕过'等字眼)：", height=100)
    
    if st.button("提交指令测试"):
        # 极简版的规则拦截逻辑
        danger_words = ["电话", "手机", "VIP", "隐私", "绕过", "密码"]
        if any(word in user_input for word in danger_words):
            st.error("🚨 拦截成功！触发红灯预警！")
            st.warning("**拦截日志：** 识别到越权意图，企图获取敏感客户信息。动作：已阻断。")
        elif user_input == "":
            st.info("请输入指令。")
        else:
            st.success("✅ 绿灯通过：该请求合规，已放行至业务大模型。")

# ====== 功能 2：白盒决策 ======
with tab2:
    st.subheader("信贷审批可解释性模拟 (SHAP归因)")
    
    col1, col2 = st.columns([1, 2]) # 左右分栏
    
    with col1: # 左侧放滑动条
        income = st.slider("客户年收入 (万)", 0, 100, 30)
        debt = st.slider("现有负债率 (%)", 0, 100, 60)
        tenure = st.slider("在职时间 (年)", 0, 40, 5)
        submit_btn = st.button("生成信用评估")

    with col2: # 右侧放结果
        if submit_btn:
            # 极简的模拟打分逻辑
            score = (income * 0.4) - (debt * 0.6) + (tenure * 0.2)
            
            if score < -10:
                st.error("❌ 审批结果：拒绝贷款")
                
                # 画一个简单的贡献度图表 (模拟 SHAP)
                st.markdown("**决策因子特征归因 (黑盒拆解)：**")
                chart_data = pd.DataFrame(
                    {"贡献度": [income * 0.4, -(debt * 0.6), tenure * 0.2]}, 
                    index=["收入正向贡献", "高负债率扣分", "工龄正向贡献"]
                )
                st.bar_chart(chart_data)
                
                st.info(" **Agent白盒翻译自动生成客户解释信：**\n尊敬的客户您好，很遗憾本次未能通过审批。经评估，您的**现有负债率偏高**是主要原因。建议您在未来半年内适当降低信用卡账单比例后再次申请，我们将期待为您服务。")
            else:
                st.success("✅ 审批结果：通过贷款")