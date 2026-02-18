import pandas as pd
import json

# --- Global Constants ---

ETHICAL_CHECKLIST = [
    {'id': 1, 'question': 'Could errors significantly harm clients or stakeholders?', 'pillar': 'Reliability', 'weight': 3},
    {'id': 2, 'question': 'Has the model been tested for demographic bias?', 'pillar': 'Fairness', 'weight': 3},
    {'id': 3, 'question': 'Can the model explain its individual decisions?', 'pillar': 'Transparency', 'weight': 2},
    {'id': 4, 'question': 'Is there a process for human review of outputs?', 'pillar': 'Accountability', 'weight': 3},
    {'id': 5, 'question': 'Has the model been stress-tested under adverse conditions?', 'pillar': 'Reliability', 'weight': 2},
    {'id': 6, 'question': 'Is all AI-generated content labeled as such?', 'pillar': 'Transparency', 'weight': 1},
    {'id': 7, 'question': 'Does the model use customer data with proper consent?', 'pillar': 'Privacy', 'weight': 2},
    {'id': 8, 'question': 'Is there an incident response plan if the model fails?', 'pillar': 'Accountability', 'weight': 2},
    {'id': 9, 'question': 'Has an independent team validated the model?', 'pillar': 'Reliability', 'weight': 2},
    {'id': 10, 'question': 'Are model decisions logged for audit?', 'pillar': 'Accountability', 'weight': 2}
]

OVERSIGHT_POLICY = {
    'human_in_the_loop': {
        'description': 'Human APPROVES every AI decision before execution',
        'applies_to': ['Credit decisions > $100K', 'Trade recommendations > $1M',
                       'Client-facing communications', 'Regulatory filings'],
        'example': 'Rebalancing agent (D3-T3-C3): trade ticket requires human sign-off',
    },
    'human_on_the_loop': {
        'description': 'AI executes; human MONITORS and can intervene',
        'applies_to': ['Algorithmic trading within pre-set limits',
                       'Automated screening (flagged items reviewed)',
                       'Portfolio risk alerts'],
        'example': 'Audit logging (D4-T1-C3): anomaly alerts trigger human review',
    },
    'human_out_of_the_loop': {
        'description': 'AI operates autonomously; periodic human REVIEW',
        'applies_to': ['Internal sentiment dashboards', 'Data preprocessing',
                       'Document classification for non-client use'],
        'example': 'FinBERT sentiment scoring: runs overnight, PM reviews in morning',
    },
}

REGULATORY_MAP = {
    'SR 11-7 (US Banking)': {
        'requires': ['Model documentation', 'Independent validation',
                     'Ongoing monitoring', 'Effective challenge'],
        'our_controls': ['D4-T1-C2 validation', 'D4-T1-C1 stress test',
                         'D4-T1-C3 audit log', 'Tiered governance'],
    },
    'EU AI Act (High-Risk)': {
        'requires': ['Transparency', 'Human oversight', 'Bias testing',
                     'Automatic logging', 'Documentation'],
        'our_controls': ['D4-T3 XAI (SHAP/LIME/Tree)', 'Oversight policy',
                         'D4-T2 fairness testing', 'D4-T1-C3 logging',
                         'Governance policy doc'],
    },
    'ECOA (US Fair Lending)': {
        'requires': ['No discrimination', 'Adverse action reasons',
                     'Fair treatment'],
        'our_controls': ['D4-T2-C1 fairness metrics',
                         'D4-T3-C1 SHAP reason codes',
                         'D4-T2-C2 bias mitigation'],
    },
    'FINRA (Broker-Dealer AI)': {
        'requires': ['Supervised communications', 'Customer data privacy',
                     'Suitability of AI recommendations'],
        'our_controls': ['Oversight policy', 'Privacy pillar',
                         'Human-in-loop for client-facing'],
    },
}


# --- Core Logic Functions ---

def tier_model(model_name: str, decision_impact: str, autonomy_level: str,
               regulatory_exposure: str, client_facing: bool, financial_impact_usd: float) -> dict:
    """
    Classify an AI model into a governance tier based on risk factors.

    Args:
        model_name (str): Name of the AI model.
        decision_impact (str): Impact of the model's decisions
                               ('informational', 'advisory', 'recommendation',
                               'automated_decision', 'autonomous_action').
        autonomy_level (str): Level of human intervention
                              ('human_executes', 'human_approves', 'human_monitors',
                              'human_reviews_after', 'fully_autonomous').
        regulatory_exposure (str): Regulatory exposure
                                   ('none', 'general', 'sector_specific',
                                   'high_risk_regulated').
        client_facing (bool): True if the model is client-facing, False otherwise.
        financial_impact_usd (float): Estimated maximum financial impact in USD.

    Returns:
        dict: A dictionary containing the model name, score, tier, and governance requirements.
    """
    score = 0

    # Decision impact (1-5)
    score += { 'informational':1, 'advisory':2, 'recommendation':3,
              'automated_decision':4, 'autonomous_action':5}[
                  decision_impact]

    # Autonomy (1-5)
    score += { 'human_executes':1, 'human_approves':2,
              'human_monitors':3, 'human_reviews_after':4,
              'fully_autonomous':5}[autonomy_level]

    # Regulatory (0-3)
    # Using 'none':0 to align with typical scoring where higher risk = higher score.
    score += {'none':0, 'general':1, 'sector_specific':2,
              'high_risk_regulated':3}[regulatory_exposure]

    # Client-facing bonus
    if client_facing: score += 2

    # Financial impact
    if financial_impact_usd > 10_000_000: score += 3
    elif financial_impact_usd > 1_000_000: score += 2
    elif financial_impact_usd > 100_000: score += 1

    tier = 1 if score >= 10 else 2 if score >= 6 else 3

    return {'model': model_name, 'score': score, 'tier': tier,
            'governance_requirements': {
                1: 'Full validation + bias + XAI + committee approval + annual review',
                2: 'Validation + monitoring + manager approval + biennial review',
                3: 'Documentation + basic testing + self-certification + triennial review'
            }[tier]}


def apply_ethical_checklist(model_name: str, answers: dict) -> dict:
    """
    Score a model against the ethical checklist and return structured results.

    Args:
        model_name (str): The name of the model being evaluated.
        answers (dict): A dictionary where keys are question IDs and values are
                        'yes', 'no', or 'partial'.

    Returns:
        dict: A dictionary containing the model name, overall score percentage,
              grade, number of gaps, and detailed results for each question.
    """
    score = 0
    max_score = 0
    results_details = []

    for q in ETHICAL_CHECKLIST:
        ans = answers.get(q['id'], 'no')  # Default to 'no' if answer not provided
        pts = q['weight'] if ans == 'yes' else q['weight'] * 0.5 if ans == 'partial' else 0
        score += pts
        max_score += q['weight']
        results_details.append({**q, 'answer': ans, 'points_earned': pts})

    pct = (score / max_score * 100) if max_score > 0 else 0
    grade = 'A' if pct >= 90 else 'B' if pct >= 75 else 'C' if pct >= 60 else 'F'

    gaps = [r for r in results_details if r['answer'] != 'yes']

    return {
        'model': model_name,
        'score_percentage': pct,
        'raw_score': score,
        'max_possible_score': max_score,
        'grade': grade,
        'gaps_count': len(gaps),
        'gaps_details': [{'id': g['id'], 'pillar': g['pillar'], 'question': g['question']} for g in gaps],
        'full_checklist_results': results_details
    }


def _compile_governance_policy_data() -> dict:
    """
    Compiles the raw data for the AI Governance Policy document.
    This function does not perform any printing.

    Returns:
        dict: A dictionary containing all sections and metadata of the policy.
    """
    policy = {
        'title': 'AI MODEL GOVERNANCE POLICY',
        'version': '1.0',
        'effective_date': '2025-03-01',
        'approved_by': 'AI Governance Committee',
        'sections': {
            '1_Principles': 'Fairness, Accountability, Transparency, Privacy, Security, Reliability (FATPSR)',
            '2_Scope': 'All AI/ML models used in investment, risk, client service, and operational decisions',
            '3_Tiering': '3-tier risk classification (see Step 2). Tier determines governance requirements.',
            '4_Lifecycle': '6-phase lifecycle with controls at each: Data -> Build -> Validate -> Deploy -> Monitor -> Retire',
            '5_Oversight': '3-level human oversight: in-loop (approve), on-loop (monitor), out-of-loop (review)',
            '6_Bias': 'Mandatory fairness testing for Tier 1 models. Four-fifths rule compliance required before deployment.',
            '7_XAI': 'SHAP required for Tier 1; surrogate tree for executive reporting; LIME for vendor models.',
            '8_Monitoring': 'Continuous audit logging (D4-T1-C3). 4-check anomaly detection. Monthly dashboard review.',
            '9_Incident': 'Detect -> Contain -> Investigate -> Remediate -> Document -> Prevent. Max 24h response for Tier 1.',
            '10_Regulatory': 'Annual regulatory mapping review. Compliance officer signs off on each Tier 1 deployment.',
        },
        'sign_off': ['CRO: ___________', 'CTO: ___________', 'CLO: ___________', 'Head of Data Science: ___________', 'AI Governance Officer: ___________'],
    }
    return policy


# --- Data Processing and Display Functions ---

def get_model_tiers_dataframe(models_parameters_list: list) -> pd.DataFrame:
    """
    Processes a list of model parameters to determine their risk tiers and returns a DataFrame.

    Args:
        models_parameters_list (list): A list of dictionaries, where each dictionary
                                       contains the arguments for the tier_model function.

    Returns:
        pd.DataFrame: A DataFrame containing the tiering results for each model.
    """
    results = [tier_model(**params) for params in models_parameters_list]
    return pd.DataFrame(results)


def display_model_tiering_results(tier_df: pd.DataFrame):
    """
    Prints the formatted model risk tiering results from a DataFrame.

    Args:
        tier_df (pd.DataFrame): DataFrame containing model tiering results.
    """
    print("MODEL RISK TIERING")
    print("=" * 70)
    print(tier_df[['model', 'score', 'tier', 'governance_requirements']].to_string(index=False))


def display_ethical_checklist_summary(model_name: str, checklist_result: dict):
    """
    Prints a formatted summary of the ethical checklist results for a model.

    Args:
        model_name (str): The name of the model.
        checklist_result (dict): The result dictionary returned by apply_ethical_checklist.
    """
    score_pct = checklist_result['score_percentage']
    grade = checklist_result['grade']
    raw_score = checklist_result['raw_score']
    max_score = checklist_result['max_possible_score']
    results_details = checklist_result['full_checklist_results']
    gaps_details = checklist_result['gaps_details']

    print(f"\nETHICAL CHECKLIST: {model_name}")
    print(f"Score: {raw_score:.0f}/{max_score} ({score_pct:.0f}%) Grade: {grade}")
    print("-" * 60)
    for r in results_details:
        status = 'PASS' if r['answer'] == 'yes' else 'PARTIAL' if r['answer'] == 'partial' else 'FAIL'
        print(f"  [{status:>7s}] Q{r['id']}: {r['question'][:50]}")

    if gaps_details:
        print(f"\nGAPS TO ADDRESS ({len(gaps_details)}):")
        for g in gaps_details:
            print(f"  Q{g['id']} ({g['pillar']}): {g['question']}")


def display_oversight_policy_summary():
    """
    Prints a formatted summary of the human oversight policy.
    """
    print("\nHUMAN OVERSIGHT POLICY")
    print("=" * 60)
    for level, policy in OVERSIGHT_POLICY.items():
        print(f"\n{level.upper().replace('_', ' ')}:")
        print(f"  Description: {policy['description']}")
        print(f"  Applies to: {', '.join(policy['applies_to'][:2])}{'...' if len(policy['applies_to']) > 2 else ''}")
        print(f"  Course example: {policy['example']}")


def display_regulatory_compliance_mapping():
    """
    Prints a formatted summary of the regulatory compliance mapping.
    """
    print("\nREGULATORY COMPLIANCE MAPPING")
    print("=" * 60)
    for reg, details in REGULATORY_MAP.items():
        print(f"\n{reg}:")
        for req, ctrl in zip(details['requires'], details['our_controls']):
            print(f"  Requirement: {req}")
            print(f"  Our Control: {ctrl}")


def display_governance_policy_document(policy_data: dict):
    """
    Prints the formatted AI Governance Policy document.

    Args:
        policy_data (dict): The policy dictionary returned by _compile_governance_policy_data.
    """
    print("\n" + "=" * 60)
    print(f"{policy_data['title']} v{policy_data['version']}")
    print(f"Effective: {policy_data['effective_date']}")
    print("=" * 60)

    for section, content in policy_data['sections'].items():
        print(f"\n{section.upper().replace('_','')}:")
        print(f" {content}")

    print(f"\nAPPROVED BY:")
    for s in policy_data['sign_off']:
        print(f" {s}")


# --- Main Execution Block (for demonstration/script usage) ---

def main():
    """
    Orchestrates the execution of the model tiering, ethical checklist,
    and policy compilation, simulating the original notebook flow.
    """
    # Define the models Alex needs to tier (synthetic data)
    course_models_params = [
        {'model_name': 'Credit Default XGBoost', 'decision_impact': 'automated_decision', 'autonomy_level': 'human_approves', 'regulatory_exposure': 'high_risk_regulated', 'client_facing': True, 'financial_impact_usd': 50_000_000},
        {'model_name': 'Trading RL Agent', 'decision_impact': 'autonomous_action', 'autonomy_level': 'human_monitors', 'regulatory_exposure': 'sector_specific', 'client_facing': False, 'financial_impact_usd': 100_000_000},
        {'model_name': 'News Sentiment (FinBERT)', 'decision_impact': 'informational', 'autonomy_level': 'human_executes', 'regulatory_exposure': 'none', 'client_facing': False, 'financial_impact_usd': 0},
        {'model_name': 'Research Copilot (RAG)', 'decision_impact': 'advisory', 'autonomy_level': 'human_executes', 'regulatory_exposure': 'general', 'client_facing': True, 'financial_impact_usd': 0},
        {'model_name': 'Portfolio Rebalancing Agent', 'decision_impact': 'recommendation', 'autonomy_level': 'human_approves', 'regulatory_exposure': 'sector_specific', 'client_facing': False, 'financial_impact_usd': 50_000_000},
        {'model_name': 'ESG Research Agent', 'decision_impact': 'advisory', 'autonomy_level': 'human_executes', 'regulatory_exposure': 'general', 'client_facing': False, 'financial_impact_usd': 0},
    ]

    # Process and display model tiering
    tier_df = get_model_tiers_dataframe(course_models_params)
    display_model_tiering_results(tier_df)

    # Alex applies the checklist to the high-risk 'Credit Default XGBoost' model (well-governed)
    credit_result = apply_ethical_checklist('Credit Default XGBoost', {
        1:'yes', 2:'yes', 3:'yes', 4:'yes', 5:'yes',
        6:'partial', 7:'yes', 8:'partial', 9:'yes', 10:'yes'
    })
    display_ethical_checklist_summary('Credit Default XGBoost', credit_result)

    # Alex applies the checklist to the 'Trading RL Agent' (with expected gaps)
    rl_result = apply_ethical_checklist('Trading RL Agent', {
        1:'yes', 2:'no', 3:'no', 4:'partial', 5:'partial',
        6:'no', 7:'yes', 8:'no', 9:'no', 10:'partial'
    })
    display_ethical_checklist_summary('Trading RL Agent', rl_result)

    # Display oversight policy
    display_oversight_policy_summary()

    # Display regulatory compliance mapping
    display_regulatory_compliance_mapping()

    # Alex compiles the governance policy
    governance_policy_document_data = _compile_governance_policy_data()
    display_governance_policy_document(governance_policy_document_data)


if __name__ == "__main__":
    main()
