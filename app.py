import streamlit as st
import pandas as pd
from datetime import datetime

# =========================
# X-Bank X-Explain Demo
# 德勤数字化精英挑战赛复赛版
# =========================

st.set_page_config(
    page_title="X-Bank X-Explain 白盒化信贷解释中台",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- CSS：银行感 + 德勤绿 ----------
st.markdown(
    """
    <style>
    :root {
        --xb-green: #86BC25;
        --xb-dark: #06231F;
        --xb-card: #FFFFFF;
        --xb-bg: #F4F7F5;
        --xb-muted: #667085;
        --xb-border: #E5E7EB;
        --xb-red: #B42318;
        --xb-amber: #B54708;
    }

    .stApp {
        background: linear-gradient(180deg, #F5F8F4 0%, #EDF3EE 100%);
    }

    div[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #06231F 0%, #0B332D 100%);
    }

    div[data-testid="stSidebar"] * {
        color: #F8FAFC !important;
    }

    .hero {
        padding: 1.35rem 1.6rem;
        border-radius: 22px;
        background: linear-gradient(135deg, #06231F 0%, #0B332D 65%, #1B4D3E 100%);
        color: white;
        box-shadow: 0 18px 45px rgba(6, 35, 31, 0.20);
        border: 1px solid rgba(255,255,255,0.08);
        margin-bottom: 1rem;
    }

    .hero h1 {
        font-size: 2.05rem;
        margin: 0 0 .35rem 0;
        letter-spacing: -0.02em;
    }

    .hero p {
        color: #DDE8DE;
        margin: 0;
        font-size: 1rem;
        line-height: 1.55;
    }

    .pill {
        display: inline-block;
        padding: .25rem .65rem;
        border-radius: 999px;
        background: rgba(134,188,37,.16);
        color: #D8F7A2;
        border: 1px solid rgba(134,188,37,.35);
        font-size: .78rem;
        font-weight: 700;
        margin-bottom: .7rem;
    }

    .section-card {
        background: var(--xb-card);
        border: 1px solid var(--xb-border);
        border-radius: 20px;
        padding: 1.15rem 1.25rem;
        box-shadow: 0 10px 26px rgba(16, 24, 40, 0.06);
        margin-bottom: 1rem;
    }

    .small-title {
        font-size: .8rem;
        color: #667085;
        text-transform: uppercase;
        letter-spacing: .08em;
        font-weight: 800;
        margin-bottom: .35rem;
    }

    .decision-pass {
        background: #ECFDF3;
        color: #027A48;
        border: 1px solid #ABEFC6;
        border-radius: 18px;
        padding: 1rem;
        font-size: 1.1rem;
        font-weight: 800;
        text-align: center;
    }

    .decision-review {
        background: #FFFAEB;
        color: #B54708;
        border: 1px solid #FEDF89;
        border-radius: 18px;
        padding: 1rem;
        font-size: 1.1rem;
        font-weight: 800;
        text-align: center;
    }

    .decision-reject {
        background: #FEF3F2;
        color: #B42318;
        border: 1px solid #FECDCA;
        border-radius: 18px;
        padding: 1rem;
        font-size: 1.1rem;
        font-weight: 800;
        text-align: center;
    }

    .explain-box {
        background: #F8FAFC;
        border-left: 5px solid #86BC25;
        padding: 1rem 1.1rem;
        border-radius: 14px;
        line-height: 1.68;
        color: #344054;
    }

    .audit-box {
        background: #061B18;
        color: #D7F2E8;
        padding: 1rem 1.1rem;
        border-radius: 16px;
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
        font-size: .85rem;
        line-height: 1.65;
        border: 1px solid rgba(134,188,37,.25);
    }

    .caption-muted {
        color: #667085;
        font-size: .86rem;
        line-height: 1.45;
    }

    div[data-testid="stMetric"] {
        background: white;
        border: 1px solid #E5E7EB;
        padding: .85rem 1rem;
        border-radius: 18px;
        box-shadow: 0 8px 22px rgba(16, 24, 40, 0.05);
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }

    .stTabs [data-baseweb="tab"] {
        background: white;
        border-radius: 999px;
        border: 1px solid #E5E7EB;
        padding: 10px 18px;
        font-weight: 700;
    }

    .stTabs [aria-selected="true"] {
        background: #06231F !important;
        color: white !important;
        border: 1px solid #86BC25 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- 业务参数 ----------
SCENARIOS = {
    "35岁快递员｜被秒拒后投诉": {
        "income": 18,
        "debt": 72,
        "tenure": 2,
        "credit_years": 3,
        "inquiries": 8,
        "overdue": 1,
        "account_years": 1,
        "loan_amount": 3,
        "occupation": "灵活就业 / 快递骑手",
        "region": "上海",
        "need": "3万元消费贷，用于家庭周转",
    },
    "28岁白领｜边界样本需人工复核": {
        "income": 32,
        "debt": 48,
        "tenure": 4,
        "credit_years": 5,
        "inquiries": 4,
        "overdue": 0,
        "account_years": 2,
        "loan_amount": 8,
        "occupation": "企业职员",
        "region": "杭州",
        "need": "8万元消费贷，用于装修尾款",
    },
    "42岁优质客户｜低风险通过": {
        "income": 68,
        "debt": 22,
        "tenure": 11,
        "credit_years": 13,
        "inquiries": 1,
        "overdue": 0,
        "account_years": 8,
        "loan_amount": 15,
        "occupation": "国企员工",
        "region": "南京",
        "need": "15万元消费贷，用于教育支出",
    },
}

FEATURE_DESCRIPTIONS = {
    "收入水平": "收入越高，偿债能力越强，正向贡献越高。",
    "现有负债率": "负债率越高，未来还款压力越大，负向影响越强。",
    "在职稳定性": "持续在职时间越长，收入稳定性越高。",
    "征信历史长度": "征信记录越长，模型对客户还款行为的判断越稳定。",
    "近期征信查询": "短期内多次查询可能意味着资金需求集中，风险上升。",
    "逾期记录": "近期逾期记录会显著影响审批结果。",
    "本行关系时长": "与本行关系越长，可用于交叉验证的行为数据越充分。",
}


def clamp(value, low, high):
    return max(low, min(high, value))


def calculate_score(income, debt, tenure, credit_years, inquiries, overdue, account_years):
    """模拟白盒化评分逻辑：返回总分、通过概率、因子贡献。
    注意：职业、地区不进入评分，只用于公平性监控和审计分层。
    """

    base_score = 58.0

    contributions = {
        "收入水平": clamp((income - 25) * 0.48, -9, 18),
        "现有负债率": clamp((45 - debt) * 0.35, -18, 11),
        "在职稳定性": clamp((tenure - 3) * 0.85, -4, 10),
        "征信历史长度": clamp((credit_years - 4) * 0.70, -5, 10),
        "近期征信查询": clamp((3 - inquiries) * 1.15, -8, 4),
        "逾期记录": -12 if overdue >= 2 else (-7 if overdue == 1 else 2),
        "本行关系时长": clamp((account_years - 2) * 0.55, -3, 6),
    }

    raw_score = base_score + sum(contributions.values())
    score = round(clamp(raw_score, 0, 100), 1)
    approval_probability = round(clamp((score - 35) / 55, 0.02, 0.98) * 100, 1)

    if score >= 68:
        decision = "通过"
        risk_level = "低风险"
        decision_class = "decision-pass"
        next_action = "自动通过，并生成可解释审批摘要。"
    elif score >= 58:
        decision = "人工复核"
        risk_level = "中风险"
        decision_class = "decision-review"
        next_action = "进入人工仲裁通道，由客户经理补充材料后复核。"
    else:
        decision = "暂缓 / 拒绝"
        risk_level = "高风险"
        decision_class = "decision-reject"
        next_action = "暂缓授信，向客户输出可理解的拒贷原因与改善建议。"

    return {
        "score": score,
        "approval_probability": approval_probability,
        "decision": decision,
        "risk_level": risk_level,
        "decision_class": decision_class,
        "next_action": next_action,
        "base_score": base_score,
        "contributions": contributions,
    }


def build_factor_table(contributions):
    df = (
        pd.DataFrame(
            [
                {
                    "因子": k,
                    "贡献分": round(v, 1),
                    "方向": "正向" if v >= 0 else "负向",
                    "业务解释": FEATURE_DESCRIPTIONS[k],
                }
                for k, v in contributions.items()
            ]
        )
        .sort_values("贡献分", ascending=True)
        .reset_index(drop=True)
    )
    return df


def build_customer_explanation(result, df):
    negative = df[df["贡献分"] < 0].sort_values("贡献分").head(3)
    positive = df[df["贡献分"] > 0].sort_values("贡献分", ascending=False).head(2)

    if result["decision"] == "通过":
        opening = "您的本次申请已通过系统评估。"
    elif result["decision"] == "人工复核":
        opening = "您的申请目前进入人工复核环节，并非直接拒绝。"
    else:
        opening = "很遗憾，您的本次申请暂未通过自动审批。"

    neg_text = "；".join([f"{row['因子']}对结果产生了较大负向影响" for _, row in negative.iterrows()])
    pos_text = "；".join([f"{row['因子']}形成了正向支持" for _, row in positive.iterrows()])

    if not neg_text:
        neg_text = "系统未发现显著负向因素"
    if not pos_text:
        pos_text = "当前正向支撑因素仍需进一步积累"

    advice = []
    if "现有负债率" in negative["因子"].values:
        advice.append("建议优先降低信用卡账单或其他短期负债，使负债率回落到更稳健区间")
    if "近期征信查询" in negative["因子"].values:
        advice.append("建议减少短期内重复申请贷款或信用卡，等待征信查询次数自然回落")
    if "逾期记录" in negative["因子"].values:
        advice.append("建议保持连续按时还款，形成新的正向还款记录")
    if "在职稳定性" in negative["因子"].values:
        advice.append("可补充稳定收入证明、社保流水或工资流水，以便人工复核")
    if not advice:
        advice.append("建议保持当前还款与账户行为，后续可申请更优授信额度")

    advice_text = "；".join(advice) + "。"

    return f"""
尊敬的客户您好，{opening}

本次评估中，系统并非仅输出一个黑盒分数，而是对影响结果的主要因素进行了拆解：
- 主要负向因素：{neg_text}。
- 主要正向因素：{pos_text}。

因此，系统建议：{advice_text}

如您认为评估结果与实际情况不符，可提交补充材料进入人工复核。X-Bank 将保留本次模型版本、输入变量、解释结果和人工复核记录，以支持后续查询与合规审计。
"""


def fairness_note(occupation, region):
    return f"""
白盒化治理说明：
- “职业：{occupation}”与“地区：{region}”不直接进入自动评分公式。
- 这些字段仅用于事后公平性监控：例如检查特定职业或地区群体是否出现异常拒贷率。
- 若群体拒贷率超过阈值，系统会触发模型偏差排查，并进入人工仲裁与模型整改流程。
"""


def add_audit_record(scenario_name, result, inputs):
    if "audit_records" not in st.session_state:
        st.session_state.audit_records = []

    record = {
        "时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "案例": scenario_name,
        "模型版本": "XCR-WhiteBox-v2.1",
        "评分": result["score"],
        "结果": result["decision"],
        "风险等级": result["risk_level"],
        "敏感变量处理": "职业/地区不参与评分，仅用于公平性监控",
        "下一步": result["next_action"],
        "客户画像摘要": f"收入{inputs['income']}万｜负债率{inputs['debt']}%｜工龄{inputs['tenure']}年｜查询{inputs['inquiries']}次｜逾期{inputs['overdue']}次",
    }
    st.session_state.audit_records.insert(0, record)


# ---------- 顶部 Hero ----------
st.markdown(
    """
    <div class="hero">
        <span class="pill">X-Explain · AI Credit Decision Whiteboxing</span>
        <h1>🏦 X-Bank AI 白盒化信贷解释中台</h1>
        <p>把“模型只给分数”升级为“客户能理解、客户经理能解释、合规能留痕、审计能追溯”的 AI 治理闭环。</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------- Sidebar ----------
st.sidebar.markdown("## 演示控制台")
scenario_name = st.sidebar.radio("选择演示案例", list(SCENARIOS.keys()), index=0)
scenario = SCENARIOS[scenario_name]

st.sidebar.markdown("---")
st.sidebar.markdown("### 案例背景")
st.sidebar.write(f"**职业**：{scenario['occupation']}")
st.sidebar.write(f"**地区**：{scenario['region']}")
st.sidebar.write(f"**贷款用途**：{scenario['need']}")
st.sidebar.caption("提示：职业与地区不会进入评分，只用于公平性审计。")

# ---------- Tabs ----------
tab_explain, tab_audit, tab_script = st.tabs(
    ["01｜单客白盒解释", "02｜审计留痕与治理闭环", "03｜复赛演示剧本"]
)

with tab_explain:
    left, mid, right = st.columns([1.05, 1.25, 1.35], gap="large")

    with left:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="small-title">Customer Profile</div>', unsafe_allow_html=True)
        st.subheader("客户画像输入")

        with st.form("credit_form"):
            income = st.slider("年收入（万元）", 5, 100, scenario["income"])
            debt = st.slider("现有负债率（%）", 0, 100, scenario["debt"])
            tenure = st.slider("当前在职时间（年）", 0, 30, scenario["tenure"])
            credit_years = st.slider("征信历史长度（年）", 0, 25, scenario["credit_years"])
            inquiries = st.slider("近6个月征信查询次数", 0, 15, scenario["inquiries"])
            overdue = st.slider("近24个月逾期次数", 0, 5, scenario["overdue"])
            account_years = st.slider("本行账户关系（年）", 0, 20, scenario["account_years"])
            loan_amount = st.slider("本次申请额度（万元）", 1, 50, scenario["loan_amount"])
            submitted = st.form_submit_button("生成白盒化评估报告", use_container_width=True)

        st.markdown("</div>", unsafe_allow_html=True)

    inputs = {
        "income": income,
        "debt": debt,
        "tenure": tenure,
        "credit_years": credit_years,
        "inquiries": inquiries,
        "overdue": overdue,
        "account_years": account_years,
        "loan_amount": loan_amount,
    }

    result = calculate_score(income, debt, tenure, credit_years, inquiries, overdue, account_years)
    df_factors = build_factor_table(result["contributions"])
    customer_letter = build_customer_explanation(result, df_factors)

    with mid:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="small-title">Decision Output</div>', unsafe_allow_html=True)
        st.subheader("审批结果与风险信号")

        st.markdown(
            f'<div class="{result["decision_class"]}">审批结果：{result["decision"]}｜{result["risk_level"]}</div>',
            unsafe_allow_html=True,
        )

        m1, m2, m3 = st.columns(3)
        m1.metric("白盒评分", f"{result['score']}/100")
        m2.metric("通过概率", f"{result['approval_probability']}%")
        m3.metric("申请额度", f"{loan_amount}万")

        st.markdown("#### SHAP-like 因子贡献拆解")
        chart_df = df_factors.set_index("因子")[["贡献分"]]
        st.bar_chart(chart_df, height=250)

        st.dataframe(
            df_factors.sort_values("贡献分", ascending=False),
            use_container_width=True,
            hide_index=True,
            column_config={
                "贡献分": st.column_config.NumberColumn(format="%.1f"),
            },
        )
        st.caption("Demo 中的贡献分为可解释性模拟结果，用于展示白盒化机制；真实项目中可替换为 SHAP、LIME 或银行内部模型解释引擎输出。")
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown('<div class="section-card">', unsafe_allow_html=True)
        st.markdown('<div class="small-title">X-Explain Translator</div>', unsafe_allow_html=True)
        st.subheader("客户可读解释信")
        st.markdown(f'<div class="explain-box">{customer_letter}</div>', unsafe_allow_html=True)

        st.markdown("#### 公平性与合规提示")
        st.info(fairness_note(scenario["occupation"], scenario["region"]))

        if st.button("写入审计留痕", use_container_width=True):
            add_audit_record(scenario_name, result, inputs)
            st.success("已写入审计日志：模型版本、输入变量、解释结果与下一步动作均已留痕。")
        elif submitted:
            st.caption("评估报告已生成。点击“写入审计留痕”可模拟第三道防线取证。")
        st.markdown("</div>", unsafe_allow_html=True)

with tab_audit:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="small-title">Governance Loop</div>', unsafe_allow_html=True)
    st.subheader("从单笔解释到治理闭环")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("模型版本", "XCR-v2.1")
    c2.metric("敏感变量入模", "否")
    c3.metric("人工仲裁通道", "已开启")
    c4.metric("审计证据链", "可追溯")

    st.markdown(
        """
        <div class="audit-box">
        [1] 客户提交申请 → [2] 模型输出评分 → [3] 白盒化归因拆解 → [4] 生成客户解释信<br>
        → [5] 若低于阈值则触发人工复核 → [6] 审计日志自动留痕 → [7] 汇总到模型健康度与公平性监控看板
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### 审计日志")
    if "audit_records" not in st.session_state or len(st.session_state.audit_records) == 0:
        st.warning("暂无审计记录。请回到“单客白盒解释”页，点击“写入审计留痕”。")
    else:
        audit_df = pd.DataFrame(st.session_state.audit_records)
        st.dataframe(audit_df, use_container_width=True, hide_index=True)

    st.markdown("### 风险响应矩阵")
    response_df = pd.DataFrame(
        [
            ["白盒评分 < 58", "高风险", "拒绝/暂缓 + 输出解释信 + 开放人工复核", "客户经理、合规、模型风险管理"],
            ["58 ≤ 白盒评分 < 68", "中风险", "进入人工仲裁，补充收入/流水/担保材料", "客户经理、信审岗"],
            ["群体拒贷率异常", "模型偏差风险", "触发公平性排查与模型重训评估", "模型风险管理、IT审计"],
            ["解释缺失或证据链不完整", "审计风险", "禁止自动放款，补齐审批解释与日志", "IT审计、内控合规"],
        ],
        columns=["触发条件", "风险等级", "系统动作", "责任方"],
    )
    st.dataframe(response_df, use_container_width=True, hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)

with tab_script:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<div class="small-title">Presentation Playbook</div>', unsafe_allow_html=True)
    st.subheader("建议的 3 分钟演示路径")

    st.markdown(
        """
        **第 1 步：讲痛点，用故事开场。**  
        “一位 35 岁快递员申请 3 万元消费贷被秒拒，客户经理只能看到一个分数，无法解释为什么。客户投诉后，合规部门也找不到完整的模型证据链。”

        **第 2 步：切到单客白盒解释。**  
        选择“35岁快递员｜被秒拒后投诉”，点击生成评估报告。让评委看到系统不仅输出拒绝，还能拆出负债率、征信查询、逾期记录等关键因子。

        **第 3 步：强调“职业/地区不入模”。**  
        说明 Demo 保留职业和地区字段，但它们只用于公平性监控，不参与自动评分。这能直接回应赛题中的“特定职业/区域拒贷率异常”问题。

        **第 4 步：展示客户解释信。**  
        读一句解释信：“本次并非只给出黑盒分数，而是说明主要负向因素与可改善建议。”这就是白盒化翻译官的客户价值。

        **第 5 步：写入审计留痕。**  
        点击“写入审计留痕”，切到审计页，展示模型版本、输入摘要、解释结果、责任动作都被留痕。最后收束到三道防线：业务能解释，合规能监控，IT审计能追溯。
        """
    )

    st.success("一句话收尾：X-Explain 不是让 AI 慢下来，而是让每一次 AI 决策都能被客户理解、被业务执行、被监管解释、被审计追溯。")
    st.markdown("</div>", unsafe_allow_html=True)

