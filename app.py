import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# Import domain logic + canonical policy content
from source import (
    ETHICAL_CHECKLIST,
    OVERSIGHT_POLICY,
    REGULATORY_MAP,
    tier_model,
    apply_ethical_checklist,
    get_model_tiers_dataframe,
)

# -----------------------------------------------------------------------------
# Page configuration
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="QuLab: Lab 46: Ethical Checklist Application",
    layout="wide",
)

# -----------------------------------------------------------------------------
# Data: synthetic but finance-native models used throughout the learning flow
# (Kept explicit so users can audit assumptions and reproduce all numbers.)
# -----------------------------------------------------------------------------
COURSE_MODELS_PARAMS = [
    {'model_name': 'Credit Default XGBoost', 'decision_impact': 'automated_decision', 'autonomy_level': 'human_approves',
        'regulatory_exposure': 'high_risk_regulated', 'client_facing': True, 'financial_impact_usd': 50_000_000},
    {'model_name': 'Trading RL Agent', 'decision_impact': 'autonomous_action', 'autonomy_level': 'human_monitors',
        'regulatory_exposure': 'sector_specific', 'client_facing': False, 'financial_impact_usd': 100_000_000},
    {'model_name': 'News Sentiment (FinBERT)', 'decision_impact': 'informational', 'autonomy_level': 'human_executes',
     'regulatory_exposure': 'none', 'client_facing': False, 'financial_impact_usd': 0},
    {'model_name': 'Research Copilot (RAG)', 'decision_impact': 'advisory', 'autonomy_level': 'human_executes',
     'regulatory_exposure': 'general', 'client_facing': True, 'financial_impact_usd': 0},
    {'model_name': 'Portfolio Rebalancing Agent', 'decision_impact': 'recommendation', 'autonomy_level': 'human_approves',
        'regulatory_exposure': 'sector_specific', 'client_facing': False, 'financial_impact_usd': 50_000_000},
    {'model_name': 'ESG Research Agent', 'decision_impact': 'advisory', 'autonomy_level': 'human_executes',
        'regulatory_exposure': 'general', 'client_facing': False, 'financial_impact_usd': 0},
]

# -----------------------------------------------------------------------------
# Utility: traceable tier score decomposition (no hidden arithmetic)
# -----------------------------------------------------------------------------
_DECISION_IMPACT_POINTS = {
    "informational": 1,
    "advisory": 2,
    "recommendation": 3,
    "automated_decision": 4,
    "autonomous_action": 5,
}

_AUTONOMY_POINTS = {
    "human_executes": 1,
    "human_approves": 2,
    "human_monitors": 3,
    "human_reviews_after": 4,
    "fully_autonomous": 5,
}

_REGULATORY_POINTS = {
    "none": 0,
    "general": 1,
    "sector_specific": 2,
    "high_risk_regulated": 3,
}


def compute_tier_breakdown(model: dict) -> dict:
    """Return score components used in S so a user can audit every point."""
    s_impact = _DECISION_IMPACT_POINTS[model["decision_impact"]]
    s_autonomy = _AUTONOMY_POINTS[model["autonomy_level"]]
    s_reg = _REGULATORY_POINTS[model["regulatory_exposure"]]
    s_client = 2 if model["client_facing"] else 0

    fin = float(model["financial_impact_usd"])
    if fin > 10_000_000:
        s_fin = 3
    elif fin > 1_000_000:
        s_fin = 2
    elif fin > 100_000:
        s_fin = 1
    else:
        s_fin = 0

    total = s_impact + s_autonomy + s_reg + s_client + s_fin
    return {
        "Model": model["model_name"],
        "S_impact": s_impact,
        "S_autonomy": s_autonomy,
        "S_regulatory": s_reg,
        "S_client_facing": s_client,
        "S_financial_impact": s_fin,
        "S_total": total,
    }


def assumptions_box(lines: list[str], title: str = "Assumptions & Traceability") -> None:
    with st.expander(title, expanded=False):
        st.markdown("\n".join([f"- {line}" for line in lines]))


def evidence_box(lines: list[str], title: str = "Evidence you should expect to have on hand") -> None:
    st.info("\n".join([f"- {line}" for line in lines]))


# -----------------------------------------------------------------------------
# Session state init
# -----------------------------------------------------------------------------
if "current_page" not in st.session_state:
    st.session_state.current_page = "Home"

if "tier_df" not in st.session_state:
    st.session_state.tier_df = get_model_tiers_dataframe(COURSE_MODELS_PARAMS)

if "tier_breakdown_df" not in st.session_state:
    st.session_state.tier_breakdown_df = pd.DataFrame(
        [compute_tier_breakdown(m) for m in COURSE_MODELS_PARAMS]
    ).set_index("Model")

if "ethical_evaluation_results" not in st.session_state:
    # Store per-model evaluation outputs (so the final report is a committee packet)
    st.session_state.ethical_evaluation_results = {}

# -----------------------------------------------------------------------------
# Sidebar: workflow navigation + progress cues
# -----------------------------------------------------------------------------
st.sidebar.image("https://www.quantuniversity.com/assets/img/logo5.jpg")
st.sidebar.divider()
st.sidebar.title("QuantAlpha AI Governance")

PAGES = [
    "Home",
    "1. Framework Overview",
    "2. Model Risk Tiering",
    "3. Ethical Checklist",
    "4. Human Oversight Policy",
    "5. Regulatory Mapping",
    "6. Governance Policy Document",
    "7. Final Report",
]

page_selection = st.sidebar.selectbox(
    "Navigate the governance workflow",
    PAGES,
    index=PAGES.index(
        st.session_state.current_page) if st.session_state.current_page in PAGES else 0
)
st.session_state.current_page = page_selection


st.sidebar.divider()
st.sidebar.caption(
    "All numeric outputs in this app are computed from documented rules. No hidden scoring.")

# -----------------------------------------------------------------------------
# Main header
# -----------------------------------------------------------------------------
st.title("QuLab: Lab 46: Ethical Checklist Application")
st.divider()

# =============================================================================
# Page: Home
# =============================================================================
if st.session_state.current_page == "Home":
    st.header(
        "Introduction: Ethical Governance as a Decision Workflow (Not a Vibe Check)")

    st.markdown(
        """
In this lab, you will play the role of **Alex Chen (Governance & Risk Officer)** at QuantAlpha, a financial services firm deploying AI models.
Your objective is to produce a **defensible, audit-ready recommendation** for whether a model is:
- **Deployable now**
- **Deployable with controls**
- **Blocked pending remediation**

This app is designed for investment professionals: the goal is *decision usefulness* and *traceability*.
        """
    )

    st.success(
        "Traceability pledge: every number you see is computable from explicit, documented rules "
        "(tier score components; checklist weights; grade thresholds)."
    )

    st.markdown("### What you will do in this workflow")
    st.markdown(
        """
1. Understand the governance framework (principles + operating pillars).
2. Tier each model by risk (so governance effort scales with impact).
3. Apply a weighted ethical checklist (controls & evidence).
4. Choose an appropriate human oversight level (who can stop/override the model).
5. Map requirements to controls (audit trail).
6. Generate a governance policy artifact (what a committee can sign).
7. Produce a final recommendation packet.
        """
    )

    st.markdown("### Micro-case anchor (finance-native)")
    st.markdown(
        "A **credit decision model** is closer to a capital allocation decision than a research dashboard: "
        "errors are asymmetric, regulated, and reputationally contagious—so the control bar is higher."
    )

    assumptions_box(
        [
            "This lab uses synthetic model metadata (impact, autonomy, regulatory exposure, client-facing, financial impact).",
            "Tier score is additive and transparently decomposed later.",
            "Checklist scoring is weighted and the rubric (Yes/Partial/No → points) is explicit.",
        ],
        title="Assumptions & what 'no black box' means here",
    )

# =============================================================================
# Page: 1. Framework Overview
# =============================================================================
elif st.session_state.current_page == "1. Framework Overview":
    st.header("Framework Map: Principles (FATPSR) + Operating Pillars")

    st.markdown(
        """
QuantAlpha uses a governance framework that combines:

**A) Principles (FATPSR):** what “good” must mean in high-stakes finance contexts  
- **Fairness, Accountability, Transparency, Privacy, Security, Reliability**

**B) Operating pillars:** how the organization enforces those principles in practice  
- Ownership & roles  
- Lifecycle gates (development → validation → deployment → monitoring)  
- Monitoring & incident response  
- Regulatory mapping & auditability
        """
    )

    st.markdown("### Why this matters (decision relevance)")
    st.info(
        "In finance, governance is not optional documentation. It is a control system that allocates validation "
        "budget, defines escalation paths, and creates audit-ready evidence."
    )

    st.markdown("### Quick checkpoint (to build intuition)")
    q = st.radio(
        "If a model is accurate but has no documented bias testing for a regulated use case, what is the governance implication?",
        [
            "It is deployable because performance dominates.",
            "It may be blocked because controls/evidence are missing, regardless of performance.",
            "It only needs more monitoring after deployment.",
        ],
        index=None,
        key="quiz_framework_q1",
    )
    if q:
        if q.startswith("It may be blocked"):
            st.success(
                "Correct. Governance treats missing controls (evidence) as a deployment blocker in regulated contexts.")
        else:
            st.warning(
                "Watch-out: performance does not substitute for control coverage. "
                "In regulated contexts, missing bias testing / explainability evidence is often a hard stop."
            )

# =============================================================================
# Page: 2. Model Risk Tiering
# =============================================================================
elif st.session_state.current_page == "2. Model Risk Tiering":
    st.header("Model Risk Tiering: Allocate Governance Effort by Materiality")

    st.markdown(
        """
Tiering is a **resource allocation mechanism**: high-impact + high-autonomy + regulated + client-facing + high USD impact
should trigger heavier validation and stronger oversight.

You will see two views:
1) **Tier results** (score, tier, required governance)
2) **Score decomposition** (component-by-component so the numbers are auditable)
        """
    )

    # --- KEEP FORMULAE (unchanged) ---
    st.markdown(r"The scoring mechanism for model risk is based on an additive score $S$, which aggregates points from various attributes:")
    st.markdown(
        r"""
$$
S = S_{\text{impact}} + S_{\text{autonomy}} + S_{\text{regulatory}} + S_{\text{client\_facing}} + S_{\text{financial\_impact}}
$$""")
    st.markdown(
        r"where $S_{\text{impact}}$ is the score based on `decision_impact` (e.g., informational=1, automated_decision=4),")
    st.markdown(
        r"where $S_{\text{autonomy}}$ is the score based on `autonomy_level` (e.g., human_executes=1, fully_autonomous=5),")
    st.markdown(
        r"where $S_{\text{regulatory}}$ is the score based on `regulatory_exposure` (e.g., none=0, high_risk_regulated=3),")
    st.markdown(
        r"where $S_{\text{client\_facing}}$ is a bonus score if `client_facing` is True, and")
    st.markdown(
        r"where $S_{\text{financial\_impact}}$ is the score based on `financial_impact_usd` (e.g., >$10M = 3 points).")

    assumptions_box(
        [
            "Decision impact, autonomy, and regulatory exposure use fixed point mappings (shown in the decomposition table).",
            "Client-facing adds +2 points (reputational + conduct risk amplification).",
            "Financial impact points are discretized by materiality thresholds (>$10M, >$1M, >$100k).",
            "Tier thresholds: Tier 1 if S≥10; Tier 2 if 6≤S<10; Tier 3 if S<6.",
        ],
        title="Assumptions behind tier scoring (explicit rules)",
    )

    st.subheader("Tier Results (committee view)")
    st.dataframe(st.session_state.tier_df.set_index("model"))

    st.caption(
        "Interpretation: This is not predictive performance. It is governance materiality. "
        "Tier determines minimum controls and sign-off burden."
    )

    st.subheader("Score Decomposition (audit view)")
    st.dataframe(st.session_state.tier_breakdown_df)

    st.markdown("### Quick checkpoint (to build intuition)")
    q2 = st.radio(
        "A model is Tier 1 primarily because it is (pick the best answer):",
        [
            "Mathematically complex.",
            "High impact/autonomy/regulatory/client-facing/financial materiality.",
            "Hard to explain.",
        ],
        index=None,
        key="quiz_tiering_q1",
    )
    if q2:
        if q2.startswith("High impact"):
            st.success(
                "Correct. Tiering is about materiality and governance burden, not model complexity.")
        else:
            st.warning(
                "Watch-out: complexity can matter, but tiering here is driven by impact, autonomy, regulation, and materiality.")

# =============================================================================
# Page: 3. Ethical Checklist
# =============================================================================
elif st.session_state.current_page == "3. Ethical Checklist":
    st.header("Ethical Checklist: Score Control Coverage (Weighted, Evidence-Based)")

    st.markdown(
        """
This section treats ethics as **controls and evidence**, not slogans.
Each question is tagged to a governance pillar and assigned a weight reflecting materiality.
You will score a model and receive:

- **Raw points vs max points**
- **% score and grade**
- **Gaps list (action plan)**
- **Pillar diagnostic (radar)**
- **A decision recommendation with guardrails**
        """
    )

    # --- KEEP FORMULAE (unchanged) ---
    st.markdown(r"For each question, a score is awarded based on the answer:")
    st.markdown(r"*   'yes': full weight ($W_q$)")
    st.markdown(r"*   'partial': half weight ($0.5 \times W_q$)")
    st.markdown(r"*   'no': zero weight (0)")
    st.markdown(
        r"The total score $S$ for a model is the sum of points from all questions:")
    st.markdown(r"""
$$
S = \sum_{q \in \text{Checklist}} P_q
$$""")
    st.markdown(r"where $P_q$ is the points received for question $q$.")
    st.markdown(
        r"The maximum possible score $S_{\text{max}}$ is the sum of all question weights:")
    st.markdown(r"""
$$
S_{\text{max}} = \sum_{q \in \text{Checklist}} W_q
$$""")
    st.markdown(r"The percentage score $\text{Pct}$ is then calculated as:")
    st.markdown(r"""
$$
\text{Pct} = \frac{S}{S_{\text{max}}} \times 100
$$""")
    st.markdown(r"Finally, a grade is assigned based on the percentage score:")
    st.markdown(r"""
$$
\text{Grade} = \begin{cases} \text{A} & \text{if } \text{Pct} \ge 90 \\ \text{B} & \text{if } \text{Pct} \ge 75 \\ \text{C} & \text{if } \text{Pct} \ge 60 \\ \text{F} & \text{if } \text{Pct} < 60 \end{cases}
$$""")

    evidence_box(
        [
            "Bias test report (coverage, thresholds, results, sign-off)",
            "Model card / validation memo (assumptions, limitations, performance, stability)",
            "Explainability artifacts (reason codes, local explanation examples, governance sign-off)",
            "Audit logs and access controls (who changed what, when)",
            "Incident runbook (monitoring metrics, triggers, escalation, kill-switch)",
        ]
    )

    model_names = [m["model_name"] for m in COURSE_MODELS_PARAMS]
    selected_model = st.selectbox(
        "Choose the model you are evaluating for committee sign-off",
        model_names,
        index=model_names.index(
            "Credit Default XGBoost") if "Credit Default XGBoost" in model_names else 0,
    )

    tier_row = st.session_state.tier_df[st.session_state.tier_df["model"]
                                        == selected_model]
    tier_value = int(tier_row["tier"].iloc[0]) if not tier_row.empty else None

    st.markdown("### Step 1: Answer the controls (weights shown explicitly)")

    answers = {}
    with st.expander("Control questions (answer Yes / Partial / No)", expanded=True):
        st.caption(
            "Tip: 'Partial' must still be evidence-based (e.g., bias testing exists but missing segments, thresholds, or approvals)."
        )
        for q in ETHICAL_CHECKLIST:
            col1, col2 = st.columns([3, 2])
            with col1:
                st.markdown(
                    f"**Q{q['id']} ({q['pillar']}, weight={q['weight']}):** {q['question']}")
            with col2:
                answers[q["id"]] = st.selectbox(
                    "Answer",
                    ["yes", "partial", "no"],
                    index=2,
                    key=f"ans_{selected_model}_{q['id']}",
                    help=(
                        "Yes = documented evidence + sign-off. "
                        "Partial = evidence exists but incomplete coverage/thresholds/approvals. "
                        "No = absent."
                    ),
                )
            st.caption(
                "Evidence expectation: a named artifact (report/memo/log/runbook), not verbal assurance.")

    st.markdown("### Step 2: Compute results (traceable)")

    result = apply_ethical_checklist(selected_model, answers)

    st.session_state.ethical_evaluation_results[selected_model] = {
        "score_pct": float(result["score_percentage"]),
        "raw_score": float(result["raw_score"]),
        "max_score": float(result["max_possible_score"]),
        "grade": result["grade"],
        "gaps": int(result["gaps_count"]),
        "gaps_details": result["gaps_details"],
        "full": result["full_checklist_results"],
        "tier": tier_value,
    }

    a, b, c, d = st.columns(4)
    a.metric("Raw points", f"{result['raw_score']:.1f}")
    b.metric("Max points", f"{result['max_possible_score']:.1f}")
    c.metric("Ethical Score (%)", f"{result['score_percentage']:.1f}")
    d.metric("Grade", result["grade"])

    st.markdown("### Step 3: Guardrails (to prevent score misinterpretation)")
    hard_stops = []
    if tier_value == 1 and answers.get(2) != "yes":
        hard_stops.append(
            "Bias testing (Q2) is not 'yes' for a Tier 1 model → treat as deployment blocker pending remediation.")

    if hard_stops:
        st.error("Deployment guardrail triggered:\n" +
                 "\n".join([f"- {x}" for x in hard_stops]))
        recommendation = "BLOCKED pending remediation (guardrail triggered)"
    else:
        if tier_value == 1 and result["grade"] in ["A", "B"]:
            recommendation = "Deployable with controls (committee sign-off + monitoring + evidence pack required)"
        elif result["grade"] == "A":
            recommendation = "Deployable (subject to standard monitoring + documentation)"
        elif result["grade"] == "B":
            recommendation = "Deployable with remediation plan and defined owners"
        elif result["grade"] == "C":
            recommendation = "Not production-ready without remediation"
        else:
            recommendation = "BLOCKED pending remediation"

    st.success(f"**Recommendation:** {recommendation}")
    st.caption("Decision translation: the score is control coverage. A high score is necessary but not sufficient if a critical control is missing.")

    st.subheader("Identified Governance Gaps (action plan)")
    if result["gaps_count"] == 0:
        st.success("No gaps identified (all controls marked 'yes').")
    else:
        st.dataframe(pd.DataFrame(result["gaps_details"]))

    st.subheader("Pillar Diagnostic (do not treat as performance)")
    pill = {}
    for row in result["full_checklist_results"]:
        p = row["pillar"]
        pill.setdefault(p, {"earned": 0.0, "max": 0.0})
        pill[p]["earned"] += float(row["points_earned"])
        pill[p]["max"] += float(row["weight"])

    pillars = list(pill.keys())
    values = [(pill[p]["earned"] / pill[p]["max"] * 100.0)
              if pill[p]["max"] else 0.0 for p in pillars]
    pillars_plot = pillars + [pillars[0]] if pillars else []
    values_plot = values + [values[0]] if values else []

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=values_plot, theta=pillars_plot,
                  fill="toself", name="Control coverage by pillar (%)"))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=False,
        height=420,
        margin=dict(l=40, r=40, t=40, b=40),
    )
    st.plotly_chart(fig, use_container_width=True)

    st.warning(
        "Guardrail: a symmetric radar does not imply deployability. One critical gap (e.g., bias testing in regulated contexts) "
        "can dominate the decision regardless of the overall shape."
    )

    st.markdown("### Quick checkpoint (common misconception)")
    q3 = st.radio(
        "What does an ethical checklist score primarily represent?",
        [
            "Predictive accuracy and robustness.",
            "Governance control coverage and evidence readiness.",
            "Expected financial return.",
        ],
        index=None,
        key="quiz_checklist_q1",
    )
    if q3:
        if q3.startswith("Governance control coverage"):
            st.success(
                "Correct. This score measures control coverage and evidence readiness.")
        else:
            st.warning(
                "Watch-out: this score is not a performance metric. It is a governance/evidence readiness measure.")

# =============================================================================
# Page: 4. Human Oversight Policy
# =============================================================================
elif st.session_state.current_page == "4. Human Oversight Policy":
    st.header("Human Oversight Policy: Who Can Stop the Model, When, and How Fast")

    st.markdown(
        """
Human oversight is a **control choice**: it defines who has authority to approve, override, or stop model-driven actions,
and what escalation path exists when the model behaves unexpectedly.

This is analogous to trading controls (limits, approvals, kill-switches) and credit controls (manual review triggers).
        """
    )

    st.subheader("Oversight Levels (operational definitions)")
    for level, desc in OVERSIGHT_POLICY.items():
        with st.expander(level, expanded=False):
            st.write(desc)

    assumptions_box(
        [
            "Oversight thresholds in this lab (e.g., $100k, $1M) are illustrative and should be calibrated to your risk appetite.",
            "Oversight is not a substitute for fairness testing, transparency, or incident readiness.",
            "Oversight must be consistent with Tier: Tier 1 models typically require stronger oversight or stricter guardrails.",
        ],
        title="Oversight assumptions & calibration",
    )

    st.markdown("### Quick checkpoint")
    q4 = st.radio(
        "A model can be 'human-on-the-loop' and still be unacceptable to deploy because:",
        [
            "Monitoring is slower than automation.",
            "Oversight does not replace required evidence-based controls (e.g., bias tests, explainability artifacts).",
            "Humans always catch errors.",
        ],
        index=None,
        key="quiz_oversight_q1",
    )
    if q4:
        if q4.startswith("Oversight does not replace"):
            st.success(
                "Correct. Oversight is one control; it does not replace missing evidence-based controls.")
        else:
            st.warning(
                "Watch-out: oversight helps, but missing required controls can still block deployment.")

# =============================================================================
# Page: 5. Regulatory Mapping
# =============================================================================
elif st.session_state.current_page == "5. Regulatory Mapping":
    st.header("Regulatory Traceability: Requirement → Control → Evidence")

    st.markdown(
        """
This page is a **traceability matrix**. In an audit conversation, you need to answer:
- Which requirement applies?
- Which internal control satisfies it?
- What evidence artifact proves it was executed?

The goal is not to memorize regulations; it is to produce defensible mappings.
        """
    )

    st.subheader("Legend (to reduce cognitive load)")
    st.info(
        "Control codes (e.g., D4-T1-C2) are internal identifiers that should map to lifecycle stage and control category. "
        "In a mature program, each control must have an evidence artifact (report/log/sign-off)."
    )

    rows = []
    for reg_name, details in REGULATORY_MAP.items():
        # Each regulation has multiple requirements and controls
        for req, ctrl in zip(details['requires'], details['our_controls']):
            rows.append({
                "Regulation / Standard": reg_name,
                "Requirement": req,
                "Our Control": ctrl,
                "Evidence example (what you should show)": "Validation memo / test report / audit log / runbook",
            })
    st.dataframe(pd.DataFrame(rows))

    st.markdown("### Decision translation")
    st.caption(
        "If a requirement has no mapped control + evidence artifact, treat it like a compliance gap—"
        "not an optional model improvement suggestion."
    )

# =============================================================================
# Page: 6. Governance Policy Document
# =============================================================================
elif st.session_state.current_page == "6. Governance Policy Document":
    st.header("Governance Policy Artifact: What the Committee Signs")

    st.markdown(
        """
A policy document is how governance becomes institutional:
- roles and responsibilities
- lifecycle gates
- tier-based control requirements
- monitoring + incident response
- evidence expectations for audits

This page produces a **committee-facing artifact**—but remember: strong statements must be backed by operational capability.
        """
    )

    st.subheader("Policy Document (sample template)")
    st.markdown(
        """
**QuantAlpha AI Governance Policy (Sample)**  
**Version:** 1.0  
**Effective Date:** 2026-02-18  
**Approved By:** AI Governance Committee  

**Purpose:** Ensure responsible, auditable, and regulator-aligned deployment of AI models in financial decision-making.  

**Scope:** All AI/ML systems used in client-facing decisions, trading, credit, research, and internal risk tooling.  

**Principles (FATPSR):** Fairness, Accountability, Transparency, Privacy, Security, Reliability.  

**Tiering:** Models are classified into Tier 1–3 based on documented risk factors. Tier determines minimum control requirements.  

**Validation & Monitoring:** Tier 1 requires independent validation, bias testing, explainability artifacts, monitoring, and annual review.  
Tier 2 requires validation, monitoring, manager approval, and biennial review.  
Tier 3 requires documentation, basic testing, self-certification, and triennial review.  

**Human Oversight:** Oversight level is selected based on tier and decision criticality, with escalation paths and intervention authority defined.  

**Regulatory Mapping:** Applicable standards (e.g., SR 11-7, ECOA) must map to controls and evidence artifacts.  

**Incident Response:** Trigger thresholds, escalation SLAs, and kill-switch procedures must be documented and tested.  
        """
    )

    assumptions_box(
        [
            "This is a sample template; thresholds and obligations must be calibrated to your institution and jurisdiction.",
            "Any quantitative compliance statement (e.g., fairness thresholds) must have a defined test method + evidence artifact.",
        ],
        title="Assumptions & guardrails for policy credibility",
    )

# =============================================================================
# Page: 7. Final Report
# =============================================================================
elif st.session_state.current_page == "7. Final Report":
    st.header("Final Report: Committee Decision Packet (Tier + Ethics + Actions)")

    if not st.session_state.ethical_evaluation_results:
        st.warning(
            "No checklist evaluations have been completed yet. Go to **3. Ethical Checklist** and evaluate at least one model.")
    else:
        # --- Executive Summary ---
        st.subheader("Executive Summary")
        
        total_models = len(st.session_state.ethical_evaluation_results)
        tier1_models = sum(1 for r in st.session_state.ethical_evaluation_results.values() if r.get("tier") == 1)
        tier2_models = sum(1 for r in st.session_state.ethical_evaluation_results.values() if r.get("tier") == 2)
        tier3_models = sum(1 for r in st.session_state.ethical_evaluation_results.values() if r.get("tier") == 3)
        
        avg_score = sum(r["score_pct"] for r in st.session_state.ethical_evaluation_results.values()) / total_models
        total_gaps = sum(r["gaps"] for r in st.session_state.ethical_evaluation_results.values())
        
        grade_counts = {}
        for r in st.session_state.ethical_evaluation_results.values():
            grade_counts[r["grade"]] = grade_counts.get(r["grade"], 0) + 1
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Models Evaluated", total_models)
        col2.metric("Average Ethical Score", f"{avg_score:.1f}%")
        col3.metric("Total Gaps Identified", total_gaps)
        col4.metric("Tier 1 Models", tier1_models)
        
        if avg_score >= 80:
            st.success(f"**Overall Assessment:** Portfolio demonstrates strong governance readiness with an average score of {avg_score:.1f}%.")
        elif avg_score >= 60:
            st.warning(f"**Overall Assessment:** Portfolio shows moderate governance readiness ({avg_score:.1f}%). Remediation required before deployment.")
        else:
            st.error(f"**Overall Assessment:** Portfolio has significant governance gaps ({avg_score:.1f}%). Substantial remediation needed.")
        
        st.divider()
        
        # --- Portfolio Summary Table ---
        st.subheader("Portfolio Summary (governance readiness, not performance)")

        summary_rows = []
        for model_name, r in st.session_state.ethical_evaluation_results.items():
            summary_rows.append({
                "Model": model_name,
                "Tier": r.get("tier", None),
                "Ethical Score (%)": round(r["score_pct"], 1),
                "Raw / Max": f"{r['raw_score']:.1f} / {r['max_score']:.1f}",
                "Grade": r["grade"],
                "Gaps (#)": r["gaps"],
            })
        summary_df = pd.DataFrame(summary_rows).set_index("Model")
        st.dataframe(summary_df, use_container_width=True)

        st.markdown("### Decision translation (how to use this table)")
        st.caption(
            "Use Tier to allocate governance burden; use checklist grade + gap severity to decide deploy / deploy-with-controls / block. "
            "Scores are comparable only as control coverage—not as economic value or model skill."
        )
        
        st.divider()
        
        # --- Tier Distribution Visualization ---
        st.subheader("Portfolio Tier Distribution")
        col1, col2 = st.columns(2)
        
        with col1:
            tier_data = {"Tier 1": tier1_models, "Tier 2": tier2_models, "Tier 3": tier3_models}
            fig_tier = go.Figure(data=[go.Pie(
                labels=list(tier_data.keys()),
                values=list(tier_data.values()),
                hole=0.4,
                marker_colors=['#FF6B6B', '#FFA07A', '#98D8C8']
            )])
            fig_tier.update_layout(
                title="Models by Risk Tier",
                height=300,
                margin=dict(l=20, r=20, t=40, b=20)
            )
            st.plotly_chart(fig_tier, use_container_width=True)
            
        with col2:
            grade_data = {g: grade_counts.get(g, 0) for g in ['A', 'B', 'C', 'F']}
            fig_grade = go.Figure(data=[go.Bar(
                x=list(grade_data.keys()),
                y=list(grade_data.values()),
                marker_color=['#4CAF50', '#8BC34A', '#FFC107', '#F44336']
            )])
            fig_grade.update_layout(
                title="Models by Ethical Grade",
                xaxis_title="Grade",
                yaxis_title="Count",
                height=300,
                margin=dict(l=20, r=20, t=40, b=20)
            )
            st.plotly_chart(fig_grade, use_container_width=True)
        
        st.divider()
        
        # --- Individual Model Recommendations ---
        st.subheader("Individual Model Recommendations")
        
        for model_name, r in st.session_state.ethical_evaluation_results.items():
            with st.expander(f"📋 {model_name} — Tier {r.get('tier', 'N/A')} | Grade {r['grade']} | {r['score_pct']:.1f}%", expanded=False):
                col1, col2, col3 = st.columns(3)
                col1.metric("Tier", r.get("tier", "N/A"))
                col2.metric("Grade", r["grade"])
                col3.metric("Gaps", r["gaps"])
                
                # Determine recommendation
                tier_val = r.get("tier")
                grade = r["grade"]
                
                if tier_val == 1 and grade in ["A", "B"]:
                    rec = "✅ **Deployable with controls** (committee sign-off + monitoring + evidence pack required)"
                    rec_color = "success"
                elif tier_val == 1 and r["gaps"] > 0:
                    rec = "🚫 **BLOCKED** pending remediation (Tier 1 with gaps)"
                    rec_color = "error"
                elif grade == "A":
                    rec = "✅ **Deployable** (subject to standard monitoring + documentation)"
                    rec_color = "success"
                elif grade == "B":
                    rec = "⚠️ **Deployable with remediation plan** and defined owners"
                    rec_color = "warning"
                elif grade == "C":
                    rec = "⚠️ **Not production-ready** without remediation"
                    rec_color = "warning"
                else:
                    rec = "🚫 **BLOCKED** pending remediation"
                    rec_color = "error"
                
                if rec_color == "success":
                    st.success(rec)
                elif rec_color == "warning":
                    st.warning(rec)
                else:
                    st.error(rec)
                
                if r["gaps"] > 0:
                    st.markdown("**Identified Gaps:**")
                    st.dataframe(pd.DataFrame(r["gaps_details"]), use_container_width=True)
                else:
                    st.info("✅ No gaps identified — all controls marked 'yes'")
        
        st.divider()
        
        # --- Action Plan Summary ---
        st.subheader("Consolidated Action Plan")
        
        all_gaps_by_pillar = {}
        for model_name, r in st.session_state.ethical_evaluation_results.items():
            for gap in r["gaps_details"]:
                pillar = gap["pillar"]
                if pillar not in all_gaps_by_pillar:
                    all_gaps_by_pillar[pillar] = []
                all_gaps_by_pillar[pillar].append({
                    "Model": model_name,
                    "Question ID": gap["id"],
                    "Question": gap["question"]
                })
        
        if total_gaps > 0:
            st.warning(f"**Total gaps across portfolio:** {total_gaps}")
            for pillar, gaps in sorted(all_gaps_by_pillar.items()):
                with st.expander(f"{pillar} — {len(gaps)} gap(s)", expanded=False):
                    st.dataframe(pd.DataFrame(gaps), use_container_width=True)
                    st.caption(
                        f"**Recommended action:** Assign owner, define evidence artifact, set remediation ETA for each {pillar} gap."
                    )
        else:
            st.success("✅ No gaps identified across the portfolio. All models have complete control coverage.")
        
        st.divider()
        
        # --- Guardrails ---
        st.subheader("Guardrails (prevent misinterpretation)")
        st.warning(
            "1) Ethical score is control coverage, not predictive accuracy.\n"
            "2) A single critical gap can block deployment even with a high score.\n"
            "3) Tier drives required controls; it does not prove the model is acceptable.\n"
            "4) This report is a governance readiness assessment, not a business case or performance evaluation."
        )
        
        st.divider()
        
        # --- Next Steps ---
        st.subheader("Recommended Next Steps")
        st.markdown("""
        1. **Committee Review:** Present this report to the AI Governance Committee for formal review and sign-off
        2. **Gap Remediation:** Assign owners and deadlines for each identified gap
        3. **Evidence Collection:** Ensure all required artifacts (test reports, audit logs, runbooks) are documented and accessible
        4. **Deployment Planning:** For approved models, define monitoring thresholds, escalation procedures, and review cycles
        5. **Regulatory Alignment:** Validate that all Tier 1 models have complete regulatory mapping and evidence trails
        6. **Ongoing Monitoring:** Establish periodic review cadence (annual for Tier 1, biennial for Tier 2, triennial for Tier 3)
        """)
        
        st.info("💡 **Export Recommendation:** Download this report as PDF for committee records and audit documentation.")


# License
st.caption('''
---
## QuantUniversity License

© QuantUniversity 2026  
This notebook was created for **educational purposes only** and is **not intended for commercial use**.  

- You **may not copy, share, or redistribute** this notebook **without explicit permission** from QuantUniversity.  
- You **may not delete or modify this license cell** without authorization.  
- This notebook was generated using **QuCreate**, an AI-powered assistant.  
- Content generated by AI may contain **hallucinated or incorrect information**. Please **verify before using**.  

All rights reserved. For permissions or commercial licensing, contact: [info@qusandbox.com](mailto:info@qusandbox.com)
''')
