import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from source import *

# --- Page Configuration ---
st.set_page_config(page_title="QuLab: Lab 46: Ethical Checklist Application", layout="wide")
st.sidebar.image("https://www.quantuniversity.com/assets/img/logo5.jpg")
st.sidebar.divider()
st.title("QuLab: Lab 46: Ethical Checklist Application")
st.divider()

# --- Core Application State ---
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'Home'

# --- Static Data from source.py (loaded once) ---
if 'course_models_data' not in st.session_state:
    st.session_state.course_models_data = course_models
if 'tier_df_data' not in st.session_state:
    st.session_state.tier_df_data = tier_df
if 'ethical_checklist_questions' not in st.session_state:
    st.session_state.ethical_checklist_questions = ETHICAL_CHECKLIST
if 'oversight_policy_data' not in st.session_state:
    st.session_state.oversight_policy_data = OVERSIGHT_POLICY
if 'regulatory_map_data' not in st.session_state:
    st.session_state.regulatory_map_data = REGULATORY_MAP
if 'governance_policy_document_content' not in st.session_state:
    st.session_state.governance_policy_document_content = compile_governance_policy()

# --- Interactive User Input & Results State ---
if 'selected_checklist_model_name' not in st.session_state:
    st.session_state.selected_checklist_model_name = st.session_state.course_models_data[0]['model'] if st.session_state.course_models_data else None

if 'user_checklist_answers' not in st.session_state:
    st.session_state.user_checklist_answers = {model['model']: {} for model in st.session_state.course_models_data}
    # Pre-populate examples
    if 'Credit Default XGBoost' in st.session_state.user_checklist_answers:
        st.session_state.user_checklist_answers['Credit Default XGBoost'] = {
            1: 'yes', 2: 'yes', 3: 'yes', 4: 'yes', 5: 'yes',
            6: 'partial', 7: 'yes', 8: 'partial', 9: 'yes', 10: 'yes'
        }
    if 'Trading RL Agent' in st.session_state.user_checklist_answers:
        st.session_state.user_checklist_answers['Trading RL Agent'] = {
            1: 'yes', 2: 'no', 3: 'no', 4: 'partial', 5: 'partial',
            6: 'no', 7: 'yes', 8: 'no', 9: 'no', 10: 'partial'
        }

if 'ethical_evaluation_results' not in st.session_state:
    st.session_state.ethical_evaluation_results = {}

# --- Helper Function for Display ---
def calculate_pillar_scores_for_display(model_name, user_answers_for_model, ethical_checklist_data):
    pillar_score_data = {
        'Fairness': {'score': 0, 'max_score': 0},
        'Accountability': {'score': 0, 'max_score': 0},
        'Transparency': {'score': 0, 'max_score': 0},
        'Privacy': {'score': 0, 'max_score': 0},
        'Security': {'score': 0, 'max_score': 0},
        'Reliability': {'score': 0, 'max_score': 0}
    }
    
    for q_item in ethical_checklist_data:
        q_id = q_item['id']
        pillar = q_item['pillar']
        weight = q_item['weight']
        answer = user_answers_for_model.get(q_id, 'no')
        
        points = weight if answer == 'yes' else weight * 0.5 if answer == 'partial' else 0
        
        if pillar in pillar_score_data:
            pillar_score_data[pillar]['score'] += points
            pillar_score_data[pillar]['max_score'] += weight
    
    final_pillar_scores_pct = {}
    for pillar, scores in pillar_score_data.items():
        if scores['max_score'] > 0:
            final_pillar_scores_pct[pillar] = (scores['score'] / scores['max_score']) * 100
        else:
            final_pillar_scores_pct[pillar] = 0
            
    return final_pillar_scores_pct

# Pre-run ethical checklist for the example models
for model_name_iter, answers_iter in st.session_state.user_checklist_answers.items():
    if answers_iter and model_name_iter not in st.session_state.ethical_evaluation_results:
        result_iter = apply_checklist(model_name_iter, answers_iter)
        pillar_scores_iter = calculate_pillar_scores_for_display(model_name_iter, answers_iter, st.session_state.ethical_checklist_questions)
        st.session_state.ethical_evaluation_results[model_name_iter] = {
            'score': result_iter['score'],
            'grade': result_iter['grade'],
            'gaps': result_iter['gaps'],
            'pillar_scores': pillar_scores_iter
        }

# --- Sidebar Navigation ---
st.sidebar.title("QuantAlpha AI Governance")
page_selection = st.sidebar.selectbox(
    "Navigate QuantAlpha AI Governance",
    [
        "Home",
        "1. Framework Overview",
        "2. Model Risk Tiering",
        "3. Ethical Checklist",
        "4. Human Oversight Policy",
        "5. Regulatory Mapping",
        "6. Governance Policy Document",
        "7. Final Report"
    ]
)
st.session_state.current_page = page_selection

# --- Main Content ---

if st.session_state.current_page == "Home":
    st.title("Introduction: Ensuring Responsible AI at QuantAlpha Investments")

    st.markdown(f"""
    Welcome, **CFA Charterholders and Investment Professionals**!
    As AI models become increasingly integral to financial decision-making, ensuring their ethical operation, transparency, and accountability is paramount. At **QuantAlpha Investments**, we are committed to upholding the highest standards of responsible AI.

    Meet Alex Chen, a Senior Risk Analyst at QuantAlpha. His role involves evaluating AI models to identify potential risks, ensure compliance with internal policies and external regulations, and ultimately build client trust. Today, Alex is tasked with applying QuantAlpha's newly adopted AI Governance Framework to several critical models used across the firm, from credit assessment to algorithmic trading. This exercise will help him systematically assess model risks, ethical considerations, and compliance readiness, culminating in a comprehensive AI governance policy document.

    This application will guide you through Alex's workflow, demonstrating how to:
    *   Implement a five-pillar AI governance framework.
    *   Build a model risk tiering system to classify models by risk factors.
    *   Apply a 10-question ethical checklist to score AI models and identify governance gaps.
    *   Define human oversight policies for AI-driven decisions.
    *   Map regulatory compliance, linking controls to requirements.
    *   Generate a formal AI governance policy document.

    Let's begin by navigating through the sections in the sidebar.
    """)

elif st.session_state.current_page == "1. Framework Overview":
    st.header("1. Understanding the Foundation: The Five-Pillar AI Governance Framework")
    st.markdown(f"""
    Before diving into specific model evaluations, Alex reviews QuantAlpha's overarching AI governance framework. This framework, inspired by leading financial industry standards, provides the structural foundation for managing AI risks. It outlines the core principles, organizational responsibilities, lifecycle controls, monitoring processes, and regulatory mappings essential for responsible AI deployment. For Alex, understanding these pillars helps him contextualize every subsequent task, ensuring his evaluations align with QuantAlpha's strategic commitment to ethical AI.

    The five pillars are:
    1.  **Principles:** Core ethical commitments like Fairness, Accountability, Transparency, Privacy, Security, and Reliability (FATPSR). These guide all AI initiatives.
    2.  **Organization:** Defines roles, responsibilities (e.g., AI Governance Committee, Model Risk Management), and clear escalation paths.
    3.  **Lifecycle Controls:** Checkpoints at each phase of a model's lifecycle, from data acquisition to development, validation, deployment, monitoring, and retirement.
    4.  **Monitoring & Incident Response:** Continuous surveillance of models in production, defining alert thresholds, and a protocol for detecting, containing, investigating, remediating, and preventing AI incidents.
    5.  **Regulatory Compliance:** Mapping AI use cases to applicable financial regulations (e.g., SR 11-7, EU AI Act, ECOA, FINRA, GDPR) and tracking evolving requirements.

    These pillars are not theoretical; they form the operational backbone of how QuantAlpha manages AI risk.
    """)
    st.subheader("Five-Pillar AI Governance Framework Diagram (Conceptual)")
    st.info("Imagine a diagram with 'Principles' at the core, surrounded by 'Organization', 'Lifecycle Controls', 'Monitoring & Incident Response', and 'Regulatory Compliance' as interconnected pillars supporting responsible AI deployment.")

elif st.session_state.current_page == "2. Model Risk Tiering":
    st.header("2. Quantifying Model Risk with a Tiering System")
    st.markdown(f"""
    Alex knows that not all AI models pose the same level of risk. A trading model handling millions in client assets requires more stringent oversight than an internal sentiment analysis tool. To allocate QuantAlpha's governance resources effectively, he uses a **Model Risk Tiering System**. This system assigns a risk tier (High, Medium, or Low) based on several factors, including the model's decision impact, autonomy, regulatory exposure, whether it's client-facing, and its potential financial impact. The higher the risk tier, the more rigorous the governance requirements.
    """)

    st.markdown(r"The scoring mechanism for model risk is based on an additive score $S$, which aggregates points from various attributes:")
    st.markdown(r"$$ S = S_{\text{impact}} + S_{\text{autonomy}} + S_{\text{regulatory}} + S_{\text{client\_facing}} + S_{\text{financial\_impact}} $$")
    st.markdown(r"where $S_{\text{impact}}$ is the score based on `decision_impact` (e.g., informational=1, automated_decision=4),")
    st.markdown(r"where $S_{\text{autonomy}}$ is the score based on `autonomy_level` (e.g., human_executes=1, fully_autonomous=5),")
    st.markdown(r"where $S_{\text{regulatory}}$ is the score based on `regulatory_exposure` (e.g., none=0, high_risk_regulated=3),")
    st.markdown(r"where $S_{\text{client\_facing}}$ is a bonus score if `client_facing` is True, and")
    st.markdown(r"where $S_{\text{financial\_impact}}$ is the score based on `financial_impact_usd` (e.g., >$10M = 3 points).")

    st.markdown(r"Based on the total score $S$, the model is assigned a tier:")
    st.markdown(r"$$ \text{Tier} = \begin{cases} 1 & \text{if } S \ge 10 \\ 2 & \text{if } 6 \le S < 10 \\ 3 & \text{if } S < 6 \end{cases} $$")
    st.markdown(f"""
    Each tier dictates specific governance requirements, ensuring that high-risk models receive comprehensive validation and oversight, while lower-risk models have proportional controls.
    """)

    st.subheader("QuantAlpha's AI Model Risk Tiers")
    st.dataframe(st.session_state.tier_df_data[['model', 'score', 'tier', 'governance_requirements']].style.set_properties(**{'font-size': '12pt'}))
    st.markdown(f"""
    **Explanation of Execution**

    The table above clearly shows each AI model's calculated risk score, its assigned tier, and the corresponding governance requirements. For Alex, this table is crucial:
    *   **Credit Default XGBoost** and **Trading RL Agent** are Tier 1 (High Risk), signaling that they require Alex to perform extensive validation, bias testing, explainability analysis (XAI), and committee approval.
    *   **Portfolio Rebalancing Agent** is Tier 2 (Medium Risk), requiring validation, monitoring, and manager approval.
    *   Internal tools like **News Sentiment (FinBERT)**, **Research Copilot (RAG)**, and **ESG Research Agent** are Tier 3 (Low Risk), needing less intensive oversight, primarily documentation and basic testing.

    This tiering system allows Alex and QuantAlpha to efficiently allocate their risk management resources, focusing on the models that pose the greatest potential impact. It prevents over-governing low-risk models and under-governing high-risk ones, mitigating potential liabilities.
    """)

elif st.session_state.current_page == "3. Ethical Checklist":
    st.header("3. Ethical Evaluation using a Comprehensive Checklist")
    st.markdown(f"""
    Having identified the risk tiers, Alex now needs to perform a deeper ethical evaluation, especially for the high-risk models. QuantAlpha utilizes a **10-question AI Ethical Checklist** aligned with the FATPSR principles. This checklist helps Alex systematically assess specific ethical considerations, identify potential gaps, and score models against QuantAlpha's responsible AI standards. It's not just a pass/fail mechanism but a diagnostic tool to pinpoint areas needing improvement before a model reaches production or for ongoing monitoring.
    """)

    st.markdown(r"For each question, a score is awarded based on the answer:")
    st.markdown(r"*   'yes': full weight ($W_q$)")
    st.markdown(r"*   'partial': half weight ($0.5 \times W_q$)")
    st.markdown(r"*   'no': zero weight (0)")

    st.markdown(r"The total score $S$ for a model is the sum of points from all questions:")
    st.markdown(r"$$ S = \sum_{q \in \text{Checklist}} P_q $$")
    st.markdown(r"where $P_q$ is the points received for question $q$.")
    st.markdown(r"The maximum possible score $S_{\text{max}}$ is the sum of all question weights:")
    st.markdown(r"$$ S_{\text{max}} = \sum_{q \in \text{Checklist}} W_q $$")
    st.markdown(r"The percentage score $\text{Pct}$ is then calculated as:")
    st.markdown(r"$$ \text{Pct} = \frac{S}{S_{\text{max}}} \times 100 $$")
    st.markdown(r"Finally, a grade is assigned based on the percentage score:")
    st.markdown(r"$$ \text{Grade} = \begin{cases} \text{A} & \text{if } \text{Pct} \ge 90 \\ \text{B} & \text{if } \text{Pct} \ge 75 \\ \text{C} & \text{if } \text{Pct} \ge 60 \\ \text{F} & \text{if } \text{Pct} < 60 \end{cases} $$")

    st.subheader("Apply Ethical Checklist")

    model_options = [model['model'] for model in st.session_state.course_models_data]
    
    current_selection = st.session_state.selected_checklist_model_name
    index_val = model_options.index(current_selection) if current_selection in model_options else 0

    selected_model_name = st.selectbox(
        "Select an AI Model for Evaluation:",
        options=model_options,
        index=index_val,
        key='ethical_checklist_model_selector'
    )
    st.session_state.selected_checklist_model_name = selected_model_name

    current_answers = st.session_state.user_checklist_answers.get(selected_model_name, {})

    st.markdown("---")
    st.subheader(f"Questions for: {selected_model_name}")
    col1, col2 = st.columns([3, 1])
    col1.markdown("**Question**")
    col2.markdown("**Answer**")
    st.markdown("---")

    answers_updated = False
    for q_item in st.session_state.ethical_checklist_questions:
        question_id = q_item['id']
        question_text = q_item['question']
        pillar = q_item['pillar']
        
        # Display question and capture answer using st.radio
        ans_key = f"answer_{selected_model_name}_{question_id}"
        default_answer = current_answers.get(question_id, 'no') # Default to 'no' if not answered yet
        
        new_answer = st.radio(
            f"**Q{question_id} ({pillar}):** {question_text}",
            options=['yes', 'partial', 'no'],
            index=['yes', 'partial', 'no'].index(default_answer),
            key=ans_key,
            horizontal=True
        )
        if new_answer != default_answer:
            st.session_state.user_checklist_answers[selected_model_name][question_id] = new_answer
            answers_updated = True
    
    if answers_updated:
        st.rerun()

    if st.button(f"Generate Evaluation Report for {selected_model_name}"):
        # Call the apply_checklist function from source.py
        answers_for_model = st.session_state.user_checklist_answers.get(selected_model_name, {})
        raw_result = apply_checklist(selected_model_name, answers_for_model)

        # Recalculate pillar scores for the radar chart (display logic)
        pillar_scores_for_display = calculate_pillar_scores_for_display(
            selected_model_name, answers_for_model, st.session_state.ethical_checklist_questions
        )
        
        # Update session state with results
        st.session_state.ethical_evaluation_results[selected_model_name] = {
            'score': raw_result['score'],
            'grade': raw_result['grade'],
            'gaps': raw_result['gaps'],
            'pillar_scores': pillar_scores_for_display
        }
        st.success(f"Ethical evaluation for {selected_model_name} completed!")
        st.rerun()

    st.markdown("---")
    st.subheader("Ethical Evaluation Results")

    if selected_model_name in st.session_state.ethical_evaluation_results:
        results = st.session_state.ethical_evaluation_results[selected_model_name]
        st.metric(label="Overall Score", value=f"{results['score']:.1f}%", delta=f"Grade: {results['grade']}")

        # Radar Chart for Pillar Scores
        st.subheader("Pillar-wise Ethical Scores (Radar Chart)")
        pillar_labels = list(results['pillar_scores'].keys())
        pillar_values = list(results['pillar_scores'].values())

        if pillar_labels and pillar_values:
            fig = go.Figure(data=go.Scatterpolar(
                r=pillar_values + [pillar_values[0]], # Close the loop
                theta=pillar_labels + [pillar_labels[0]], # Close the loop
                fill='toself'
            ))
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, range=[0, 100])
                ),
                showlegend=False,
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No pillar scores available to display radar chart.")
        
        st.subheader("Identified Governance Gaps")
        if results['gaps'] > 0:
            st.warning(f"There are {results['gaps']} gaps to address for this model:")
            gaps_found = []
            current_answers_full = st.session_state.user_checklist_answers.get(selected_model_name, {})
            for q_item in st.session_state.ethical_checklist_questions:
                if current_answers_full.get(q_item['id'], 'no') != 'yes':
                    gaps_found.append(f"Q{q_item['id']} ({q_item['pillar']}): {q_item['question']}")
            
            for gap in gaps_found:
                st.markdown(f"- {gap}")
        else:
            st.success("No significant governance gaps identified for this model! Well done.")
    else:
        st.info(f"No evaluation results yet for {selected_model_name}. Please answer the questions and click 'Generate Evaluation Report'.")

    st.markdown(f"""
    **Explanation of Execution**

    The checklist results provide Alex with actionable insights:
    *   The **Credit Default XGBoost** model, being relatively well-governed (achieving a "B" grade in our example), shows "PARTIAL" answers for Q6 (AI-generated content labeling) and Q8 (incident response plan), indicating minor areas for improvement. Alex would recommend clearer guidelines for labeling credit decision rationales and solidifying the incident response protocol for this model.
    *   The **Trading RL Agent**, on the other hand, received an "F" grade with significant gaps in our example. This is a critical finding for Alex. The "FAIL" answers for Q2 (bias testing), Q3 (explainability), Q6 (labeling), Q8 (incident response), and Q9 (independent validation) highlight major deficiencies. This model is **not ready for production deployment** without substantial work. Alex would escalate these findings, recommending a dedicated team to address bias testing, improve model explainability, develop a robust incident response, and ensure independent validation. These gaps directly correspond to the pillars of Fairness, Transparency, Accountability, and Reliability.

    This process allows Alex to move beyond generic "AI risk" to specific, quantifiable ethical deficiencies and define clear action items for the model development teams.
    """)

elif st.session_state.current_page == "4. Human Oversight Policy":
    st.header("4. Structuring Human Oversight for AI Decisions")
    st.markdown(f"""
    AI model decisions vary in their potential impact and need for human intervention. Alex needs to ensure that QuantAlpha has a clear **Human Oversight Policy** that defines appropriate levels of human involvement for different types of AI decisions. This policy prevents fully automated decisions in high-stakes scenarios while allowing AI to operate autonomously where human review is less critical, thereby optimizing efficiency without compromising safety or accountability. This also directly supports the "Accountability" and "Transparency" pillars of the governance framework.

    QuantAlpha recognizes three levels of human oversight:
    *   **Human-in-the-Loop:** Human approval is *required* before AI decisions are executed. Used for high-stakes, irreversible decisions.
    *   **Human-on-the-Loop:** AI executes decisions, but humans *monitor* and can *intervene* if necessary. Used for automated processes within defined boundaries.
    *   **Human-out-of-the-Loop:** AI operates autonomously; humans *periodically review* outputs or processes. Used for low-stakes, internal operations.
    """)

    st.subheader("QuantAlpha's Human Oversight Policy")
    for level, policy in st.session_state.oversight_policy_data.items():
        st.markdown(f"### {level.replace('_', ' ').upper()}:")
        st.markdown(f"- **Description**: {policy['description']}")
        st.markdown(f"- **Applies to**: {', '.join(policy['applies_to'])}")
        st.markdown(f"- **Course Example**: _{policy['example']}_")

    st.markdown(f"""
    **Explanation of Execution**

    The human oversight policy clearly delineates when and how humans must interact with AI systems. For Alex, this is critical for designing appropriate controls for each model. For instance:
    *   The **Credit Default XGBoost** model, given its `automated_decision` nature and high financial impact, would fall under "Human-in-the-Loop" for critical decisions exceeding a certain threshold (e.g., > $100K).
    *   The **Trading RL Agent**, while `autonomous_action`, if constrained by `pre-set limits`, could be managed under "Human-on-the-Loop", allowing for real-time monitoring and intervention.
    *   The **News Sentiment (FinBERT)** model, being `informational`, would likely be "Human-out-of-the-Loop", with periodic reviews of its general output quality.

    This policy helps Alex ensure that QuantAlpha implements robust human checks where risk is highest, aligning with the "Accountability" pillar and managing operational risk effectively.
    """)

elif st.session_state.current_page == "5. Regulatory Mapping":
    st.header("5. Navigating the Regulatory Landscape: Compliance Mapping")
    st.markdown(f"""
    QuantAlpha operates in a heavily regulated industry. For Alex, it's not enough to define internal governance; he must also demonstrate **regulatory compliance**. This involves mapping external regulatory requirements (e.g., SR 11-7, EU AI Act, ECOA, FINRA) to the specific internal governance controls and tools that QuantAlpha has implemented. This exercise proves due diligence, identifies any compliance gaps, and provides a clear audit trail for regulators, reinforcing the "Regulatory Compliance" pillar.
    """)

    st.subheader("QuantAlpha's Regulatory Compliance Mapping")
    for reg, details in st.session_state.regulatory_map_data.items():
        st.markdown(f"### {reg}:")
        for i, (req, ctrl) in enumerate(zip(details['requires'], details['our_controls'])):
            st.markdown(f"- **Requirement**: {req}")
            st.markdown(f"  **Our Control**: {ctrl}")
        st.markdown("---")

    st.markdown(f"""
    **Explanation of Execution**

    This mapping demonstrates to Alex (and external auditors) how QuantAlpha's internal governance mechanisms directly address specific regulatory mandates. For example:
    *   The requirement for 'Independent validation' under **SR 11-7** is met by QuantAlpha's 'D4-T1-C2 validation' control.
    *   The **EU AI Act's** 'Bias testing' requirement is addressed by 'D4-T2 fairness testing'.
    *   **ECOA's** 'No discrimination' requirement is covered by 'D4-T2-C1 fairness metrics' and 'D4-T2-C2 bias mitigation'.

    This systematic approach ensures that Alex can confidently affirm QuantAlpha's commitment to compliance, minimizing legal and reputational risks associated with AI deployment. Any requirement without a corresponding control would immediately signal a critical compliance gap for Alex to address.
    """)

elif st.session_state.current_page == "6. Governance Policy Document":
    st.header("6. Formalizing Governance: Generating the AI Governance Policy Document")
    st.markdown(f"""
    After assessing individual models, defining oversight, and mapping regulations, Alex's final task is to compile all these elements into a formal **AI Governance Policy Document**. This document is crucial for QuantAlpha's AI Governance Committee. It serves as an official reference, standardizing practices across the firm, communicating policies to all stakeholders, and acting as a living document that can be updated as AI technology and regulations evolve. For Alex, generating this document solidifies all his previous analysis into a coherent, actionable policy framework.
    """)

    policy = st.session_state.governance_policy_document_content
    st.subheader(policy['title'])
    st.markdown(f"**Version**: {policy['version']}")
    st.markdown(f"**Effective Date**: {policy['effective_date']}")
    st.markdown(f"**Approved By**: {policy['approved_by']}")
    st.markdown("---")

    for section_key, content in policy['sections'].items():
        st.markdown(f"### {section_key.upper().replace('_',' ')}")
        st.markdown(f" {content}")
        st.markdown("")

    st.markdown("---")
    st.subheader("SIGN-OFFS:")
    for sign_off_line in policy['sign_off']:
        st.markdown(f"- {sign_off_line}")

    st.markdown(f"""
    **Explanation of Execution**

    The generated output is a structured policy document ready for review and adoption by QuantAlpha's AI Governance Committee. This document summarizes all key aspects of AI governance, from foundational principles to operational controls and regulatory mappings. For Alex, this is the ultimate deliverable, demonstrating how a systematic approach to AI governance allows the firm to deploy AI responsibly, manage risk proactively, and maintain trust with clients and regulators. It formalizes QuantAlpha's commitment to ethical AI and provides a clear roadmap for all AI initiatives.
    """)

elif st.session_state.current_page == "7. Final Report":
    st.header("7. Conclusion: Actionable Insights and Future Steps")
    st.markdown(f"""
    Through this detailed workflow, Alex Chen has successfully applied QuantAlpha's AI Governance Framework. He has:
    *   Categorized AI models by their risk tiers, enabling proportional governance.
    *   Identified specific ethical gaps in high-risk models, particularly the Trading RL Agent, necessitating immediate remediation efforts.
    *   Clarified human oversight requirements for various AI-driven decisions.
    *   Mapped QuantAlpha's controls to relevant financial regulations, ensuring compliance.
    *   Compiled a formal AI Governance Policy Document to guide future AI deployments.

    The "Ethical AI Evaluation Report" derived from this process (summarized below) provides QuantAlpha's AI Governance Committee with concrete data, identified gaps, and clear recommendations. For the Trading RL Agent, Alex will recommend a project to implement bias testing, improve explainability, and develop a comprehensive incident response plan, aligning it with Tier 1 governance requirements before it can proceed to full production.

    This hands-on exercise underscores that responsible AI is an ongoing process of assessment, adaptation, and continuous improvement. By integrating these governance practices into their daily operations, CFA Charterholders and Investment Professionals like Alex ensure that AI innovations not only drive financial performance but also uphold ethical standards and regulatory compliance.
    """)

    st.subheader("Summary of Model Risk Tiers")
    st.dataframe(st.session_state.tier_df_data[['model', 'score', 'tier', 'governance_requirements']].style.set_properties(**{'font-size': '12pt'}))

    st.subheader("Summary of Ethical Evaluation Results")
    if st.session_state.ethical_evaluation_results:
        summary_data = []
        for model_name, results in st.session_state.ethical_evaluation_results.items():
            summary_data.append({
                'Model': model_name,
                'Ethical Score (%)': f"{results['score']:.1f}",
                'Grade': results['grade'],
                'Gaps Identified': results['gaps']
            })
        st.dataframe(pd.DataFrame(summary_data).set_index('Model'))

        st.markdown("---")
        st.subheader("Detailed Ethical Gaps for Models with Deficiencies")
        for model_name, results in st.session_state.ethical_evaluation_results.items():
            if results['gaps'] > 0:
                with st.expander(f"Gaps for {model_name} (Grade: {results['grade']})"):
                    current_answers_full = st.session_state.user_checklist_answers.get(model_name, {})
                    gaps_found = []
                    for q_item in st.session_state.ethical_checklist_questions:
                        if current_answers_full.get(q_item['id'], 'no') != 'yes':
                            gaps_found.append(f"Q{q_item['id']} ({q_item['pillar']}): {q_item['question']}")
                    for gap in gaps_found:
                        st.markdown(f"- {gap}")
    else:
        st.info("No ethical evaluation results available yet. Please complete the 'Ethical Checklist' page.")

    st.subheader("Key Takeaways for QuantAlpha Investments")
    st.markdown("""
    *   **Proportional Governance**: The tiering system efficiently directs resources. Tier 1 models like 'Credit Default XGBoost' and 'Trading RL Agent' require the highest scrutiny.
    *   **Urgent Remediation for Trading RL Agent**: Significant gaps in bias testing, explainability, and independent validation mean this model is **not ready for production**. A dedicated project for remediation is critical.
    *   **Clear Oversight**: The Human Oversight Policy provides clear guidelines for human interaction with AI, balancing automation with accountability.
    *   **Regulatory Readiness**: The compliance mapping confirms that QuantAlpha's controls align with key financial regulations, minimizing legal and reputational risks.
    *   **Formalized Policy**: The AI Governance Policy Document serves as the official blueprint for all AI initiatives, ensuring consistent and responsible practices across the firm.
    """)


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
