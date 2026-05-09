import streamlit as st
import pandas as pd
from datetime import datetime

# =============================
# X-Bank X-Explain 白盒化演示 Demo
# 极简复赛版：现场输入 → 模型决策 → 白盒归因 → 客户解释 → 审计留痕
# =============================

st.set_page_config(
    page_title="X-Bank X-Explain",
    page_icon="🏦",
    layout="wide",
)

# ---------- 页面样式 ----------
st.markdown(
    """
    <style>
    /* 强制浅色主题下的文字颜色，避免评委电脑/浏览器使用深色主题时出现“白字白底” */
    .stApp {
        background: #F5F7F4;
        color: #1D2939;
    }

    .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp p, .stApp label,
    .stApp span, .stApp div, .stApp li {
        color: #1D2939;
    }

    .main-header {
        background: linear-gradient(135deg, #06231F 0%, #0E3B32 100%);
        padding: 1.4rem 1.6rem;
        border-radius: 20px;
        color: white;
        margin-bottom: 1.1rem;
        box-shadow: 0 14px 36px rgba(6, 35, 31, 0.18);
    }

    .main-header h1 {
        margin: 0;
        font-size: 2rem;
        letter-spacing: -0.03em;
    }

    .main-header p {
        margin: .45rem 0 0 0;
        color: #DDE8DE;
        font-size: 1rem;
    }

    .card {
        background: white;
        border: 1px solid #E5E7EB;
        border-radius: 18px;
        padding: 1.1rem 1.2rem;
        box-shadow: 0 8px 24px rgba(16, 24, 40, 0.06);
        margin-bottom: 1rem;
    }

    .step-title {
        font-size: .8rem;
        color: #667085;
        font-weight: 800;
        letter-spacing: .08em;
        text-transform: uppercase;
        margin-bottom: .35rem;
    }

    .decision-pass {
        background: #ECFDF3;
        color: #027A48;
        border: 1px solid #ABEFC6;
        padding: 1rem;
        border-radius: 16px;
        font-size: 1.15rem;
        font-weight: 800;
        text-align: center;
        margin-bottom: .75rem;
    }

    .decision-review {
        background: #FFFAEB;
        color: #B54708;
        border: 1px solid #FEDF89;
        padding: 1rem;
        border-radius: 16px;
        font-size: 1.15rem;
        font-weight: 800;
        text-align: center;
        margin-bottom: .75rem;
    }

    .decision-reject {
        background: #FEF3F2;
        color: #B42318;
        border: 1px solid #FECDCA;
        padding: 1rem;
        border-radius: 16px;
        font-size: 1.15rem;
        font-weight: 800;
        text-align: center;
        margin-bottom: .75rem;
    }

    .explain-box {
        background: #F8FAFC;
        border-left: 5px solid #86BC25;
        border-radius: 14px;
        padding: 1rem 1.1rem;
        line-height: 1.68;
        color: #344054;
    }

    .audit-box {
        background: #071D19;
        color: #DDF4E8;
        border-radius: 14px;
        padding: 1rem 1.1rem;
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", monospace;
        font-size: .86rem;
        line-height: 1.6;
    }

    .hint {
        color: #667085;
        font-size: .9rem;
        line-height: 1.5;
    }

    div[data-testid="stMetric"] {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 16px;
        padding: .8rem .95rem;
        box-shadow: 0 6px 18px rgba(16, 24, 40, 0.05);
    }

    .main-header, .main-header *, .audit-box, .audit-box * {
        color: #FFFFFF !important;
    }

    .main-header p {
        color: #DDE8DE !important;
    }

    .card, .card *, div[data-testid="stMetric"], div[data-testid="stMetric"] * {
        color: #1D2939 !important;
    }

    .step-title, .hint, .stCaption, .stCaption * {
        color: #667085 !important;
    }

    .explain-box, .explain-box * {
        color: #344054 !important;
    }

    .decision-pass, .decision-pass * {
        color: #027A48 !important;
    }

    .decision-review, .decision-review * {
        color: #B54708 !important;
    }

    .decision-reject, .decision-reject * {
        color: #B42318 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- 简化评分模型 ----------
def clamp(x, low, high):
    return max(low, min(high, x))


def score_application(income, debt_ratio, tenure, credit_years, inquiries, overdue_count):
    """
    演示用白盒评分模型：
    - 不追求真实授信准确性
    - 目标是展示“每个因子如何影响结果”
    """

    base_score = 60

    factors = {
        "收入水平": clamp((income - 25) * 0.45, -8, 16),
        "现有负债率": clamp((45 - debt_ratio) * 0.38, -18, 10),
        "在职稳定性": clamp((tenure - 3) * 0.9, -5, 10),
        "征信历史长度": clamp((credit_years - 4) * 0.75, -5, 9),
        "近期征信查询": clamp((3 - inquiries) * 1.2, -8, 4),
        "逾期记录": -12 if overdue_count >= 2 else (-7 if overdue_count == 1 else 2),
    }

    final_score = round(clamp(base_score + sum(factors.values()), 0, 100), 1)
    approval_prob = round(clamp((final_score - 35) / 55, 0.02, 0.98) * 100, 1)

    if final_score >= 68:
        decision = "通过"
        cls = "decision-pass"
        action = "自动通过，并生成审批解释摘要。"
    elif final_score >= 58:
        decision = "人工复核"
        cls = "decision-review"
        action = "进入人工复核，由客户补充材料后重新评估。"
    else:
        decision = "暂缓 / 拒绝"
        cls = "decision-reject"
        action = "暂缓授信，输出可理解的拒贷原因与改善建议。"

    return final_score, approval_prob, decision, cls, action, factors


def build_factor_df(factors):
    df = pd.DataFrame(
        {
            "因子": list(factors.keys()),
            "贡献分": [round(v, 1) for v in factors.values()],
        }
    )
    df["方向"] = df["贡献分"].apply(lambda x: "正向" if x >= 0 else "负向")
    return df.sort_values("贡献分", ascending=True).reset_index(drop=True)


def build_explanation(decision, factor_df):
    negative = factor_df[factor_df["贡献分"] < 0].sort_values("贡献分").head(3)
    positive = factor_df[factor_df["贡献分"] > 0].sort_values("贡献分", ascending=False).head(2)

    if decision == "通过":
        opening = "您的本次贷款申请已通过系统评估。"
    elif decision == "人工复核":
        opening = "您的本次申请目前进入人工复核环节，并非直接拒绝。"
    else:
        opening = "很遗憾，您的本次申请暂未通过自动审批。"

    if len(negative) > 0:
        neg_text = "、".join(negative["因子"].tolist())
    else:
        neg_text = "未发现明显负向因素"

    if len(positive) > 0:
        pos_text = "、".join(positive["因子"].tolist())
    else:
        pos_text = "当前正向支撑因素仍需进一步积累"

    suggestions = []
    neg_factors = negative["因子"].tolist()
    if "现有负债率" in neg_factors:
        suggestions.append("适当降低信用卡账单或其他短期负债")
    if "近期征信查询" in neg_factors:
        suggestions.append("减少短期内重复申请贷款或信用卡")
    if "逾期记录" in neg_factors:
        suggestions.append("保持连续按时还款，积累新的正向还款记录")
    if "在职稳定性" in neg_factors:
        suggestions.append("补充工资流水、社保记录或稳定收入证明")
    if not suggestions:
        suggestions.append("保持当前良好信用记录，后续可申请更优授信额度")

    suggestion_text = "；".join(suggestions)

    return f"""
尊敬的客户您好，{opening}

本次评估并非只依据一个黑盒分数，而是对影响结果的主要因素进行了拆解。

主要负向因素：{neg_text}。  
主要正向因素：{pos_text}。

建议您后续可以：{suggestion_text}。

如您认为评估结果与实际情况不符，可以提交补充材料进入人工复核。X-Bank 将保留本次模型版本、输入变量、解释结果和人工复核记录，以支持后续查询与合规审计。
"""


# ---------- 顶部 ----------
st.markdown(
    """
    <div class="main-header">
        <h1>🏦 X-Bank X-Explain 白盒化信贷解释中台</h1>
        <p>现场演示：输入客户画像 → 生成审批结果 → 拆解决策因子 → 输出客户可读解释 → 留存审计证据。</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------- 初始化状态 ----------
if "has_result" not in st.session_state:
    st.session_state.has_result = False

if "audit_log" not in st.session_state:
    st.session_state.audit_log = []


# ---------- 页面布局 ----------
left, right = st.columns([0.95, 1.45], gap="large")

with left:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="step-title">Step 1 · 现场输入客户画像</div>', unsafe_allow_html=True)
    st.subheader("客户申请信息")

    with st.form("input_form", clear_on_submit=False):
        income = st.slider("客户年收入（万元）", 5, 100, 18)
        debt_ratio = st.slider("现有负债率（%）", 0, 100, 72)
        tenure = st.slider("当前在职时间（年）", 0, 30, 2)
        credit_years = st.slider("征信历史长度（年）", 0, 25, 3)
        inquiries = st.slider("近6个月征信查询次数", 0, 15, 8)
        overdue_count = st.slider("近24个月逾期次数", 0, 5, 1)

        st.markdown("---")
        occupation = st.selectbox(
            "职业类型（仅用于公平性监控，不参与评分）",
            ["快递骑手 / 灵活就业", "企业职员", "个体工商户", "国企员工", "自由职业者"],
            index=0,
        )
        region = st.selectbox(
            "所在地区（仅用于公平性监控，不参与评分）",
            ["上海", "杭州", "南京", "广州", "成都", "武汉"],
            index=0,
        )

        submitted = st.form_submit_button("生成白盒化审批结果", use_container_width=True)

    if submitted:
        score, prob, decision, cls, action, factors = score_application(
            income, debt_ratio, tenure, credit_years, inquiries, overdue_count
        )
        factor_df = build_factor_df(factors)
        explanation = build_explanation(decision, factor_df)

        st.session_state.has_result = True
        st.session_state.result = {
            "score": score,
            "prob": prob,
            "decision": decision,
            "cls": cls,
            "action": action,
            "factor_df": factor_df,
            "explanation": explanation,
            "inputs": {
                "年收入": income,
                "负债率": debt_ratio,
                "在职时间": tenure,
                "征信历史": credit_years,
                "征信查询": inquiries,
                "逾期次数": overdue_count,
                "职业": occupation,
                "地区": region,
            },
        }

    st.markdown(
        '<p class="hint">说明：职业和地区不会进入自动评分，只用于事后公平性监控，防止特定职业或地区被系统性误伤。</p>',
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)


with right:
    if not st.session_state.has_result:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="step-title">Step 2 · 等待现场生成</div>', unsafe_allow_html=True)
        st.subheader("请先在左侧输入客户信息")
        st.info("点击“生成白盒化审批结果”后，这里会现场出现审批结果、因子贡献图、客户解释信和审计留痕按钮。")
        st.markdown("</div>", unsafe_allow_html=True)

    else:
        r = st.session_state.result

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="step-title">Step 2 · 模型输出</div>', unsafe_allow_html=True)
        st.subheader("审批结果")
        st.markdown(
            f'<div class="{r["cls"]}">审批结果：{r["decision"]}</div>',
            unsafe_allow_html=True,
        )

        m1, m2, m3 = st.columns(3)
        m1.metric("白盒评分", f"{r['score']}/100")
        m2.metric("通过概率", f"{r['prob']}%")
        m3.metric("下一步", r["action"])

        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="step-title">Step 3 · 白盒归因</div>', unsafe_allow_html=True)
        st.subheader("为什么是这个结果？")

        chart_df = r["factor_df"].set_index("因子")[["贡献分"]]
        st.bar_chart(chart_df, height=260)
        st.dataframe(
            r["factor_df"].sort_values("贡献分", ascending=False),
            use_container_width=True,
            hide_index=True,
        )

        st.caption("此处用 SHAP-like 贡献分模拟白盒解释机制。真实项目中可替换为银行现有模型的 SHAP、LIME 或内部解释引擎输出。")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="step-title">Step 4 · 白盒翻译官</div>', unsafe_allow_html=True)
        st.subheader("客户可读解释")
        st.markdown(f'<div class="explain-box">{r["explanation"]}</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="step-title">Step 5 · 审计留痕</div>', unsafe_allow_html=True)
        st.subheader("合规与审计证据")

        if st.button("写入审计日志", use_container_width=True):
            record = {
                "时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "模型版本": "X-Explain-v1.0",
                "审批结果": r["decision"],
                "白盒评分": r["score"],
                "敏感变量处理": "职业/地区不参与评分，仅用于公平性监控",
                "下一步动作": r["action"],
            }
            st.session_state.audit_log.insert(0, record)
            st.success("已留痕：模型版本、审批结果、输入摘要、解释文本和下一步动作已记录。")

        if len(st.session_state.audit_log) > 0:
            st.dataframe(pd.DataFrame(st.session_state.audit_log), use_container_width=True, hide_index=True)
        else:
            st.markdown(
                """
                <div class="audit-box">
                等待写入审计日志……<br>
                审计日志将记录：模型版本、输入摘要、评分结果、解释文本、敏感变量处理方式、下一步动作。
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("</div>", unsafe_allow_html=True)



