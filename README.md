The following `README.md` file is designed to provide a comprehensive overview of the Streamlit application for the "QuLab: Lab 46: Ethical Checklist Application" project.

---

# QuLab: Lab 46: Ethical Checklist Application

![QuantUniversity Logo](https://www.quantuniversity.com/assets/img/logo5.jpg)

## Project Title: QuantAlpha AI Governance Framework: Ethical Checklist and Policy Generation

## Project Description

Welcome to the **QuantAlpha AI Governance Framework: Ethical Checklist and Policy Generation** application. This Streamlit-powered interactive lab project is designed for CFA Charterholders and Investment Professionals to simulate the critical process of establishing robust AI governance within a financial institution.

In an era where AI models are increasingly central to financial decision-making, ensuring their ethical operation, transparency, and accountability is paramount. This application guides users through the workflow of a Senior Risk Analyst, Alex Chen, at QuantAlpha Investments, as he systematically evaluates AI models for risk, ethical considerations, and compliance readiness. The goal is to culminate in the generation of a comprehensive AI governance policy document.

The application demonstrates how to:
*   Implement a five-pillar AI governance framework.
*   Build a model risk tiering system to classify models by risk factors (High, Medium, Low).
*   Apply a 10-question ethical checklist to score AI models against responsible AI standards and identify governance gaps.
*   Define human oversight policies for AI-driven decisions.
*   Map internal controls to external regulatory requirements (e.g., SR 11-7, EU AI Act).
*   Generate a formal, structured AI governance policy document.

This project underscores the importance of a systematic approach to responsible AI, ensuring that financial innovations are deployed ethically, compliantly, and with due diligence.

## Features

This application offers a multi-page interactive experience, covering key aspects of AI governance:

1.  **Home Page**: An introduction to the project's context, objectives, and the scenario involving Alex Chen and QuantAlpha Investments.
2.  **Framework Overview**: Explains QuantAlpha's foundational Five-Pillar AI Governance Framework (Principles, Organization, Lifecycle Controls, Monitoring & Incident Response, Regulatory Compliance).
3.  **Model Risk Tiering**:
    *   Presents a system to categorize AI models into High, Medium, or Low-risk tiers based on factors like decision impact, autonomy, and financial exposure.
    *   Includes a quantitative scoring mechanism and displays assigned tiers and governance requirements for various example models.
4.  **Ethical Checklist**:
    *   An interactive 10-question checklist aligned with FATPSR (Fairness, Accountability, Transparency, Privacy, Security, Reliability) principles.
    *   Allows users to select an AI model and answer questions with 'yes', 'partial', or 'no'.
    *   Calculates an overall ethical score (percentage) and assigns a grade (A, B, C, F).
    *   Visualizes pillar-wise ethical scores using an interactive radar chart (Plotly).
    *   Identifies and lists specific governance gaps based on 'partial' or 'no' answers.
5.  **Human Oversight Policy**:
    *   Outlines QuantAlpha's three levels of human involvement for AI decisions: Human-in-the-Loop, Human-on-the-Loop, and Human-out-of-the-Loop.
    *   Describes the application context for each oversight level with examples.
6.  **Regulatory Mapping**:
    *   Demonstrates how internal governance controls are mapped to external regulatory requirements (e.g., SR 11-7, EU AI Act, ECOA, FINRA).
    *   Highlights QuantAlpha's commitment to compliance and provides an audit trail.
7.  **Governance Policy Document**:
    *   Generates a formal, structured AI Governance Policy Document dynamically, compiling all principles, policies, and mappings discussed in previous sections.
    *   Serves as an official reference for standardizing practices and communicating policies.
8.  **Final Report**:
    *   Provides a comprehensive summary of model risk tiers and ethical evaluation results across all models.
    *   Lists detailed ethical gaps for models with deficiencies.
    *   Offers key takeaways and actionable insights for QuantAlpha Investments.
9.  **Persistent State**: Utilizes Streamlit's `st.session_state` to maintain user inputs and evaluation results across page navigations and reruns.

## Getting Started

Follow these instructions to set up and run the Streamlit application on your local machine.

### Prerequisites

Before you begin, ensure you have met the following requirements:

*   **Python 3.8+**: Download and install Python from [python.org](https://www.python.org/downloads/).
*   **Git**: Install Git from [git-scm.com](https://git-scm.com/downloads) to clone the repository.

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/qualtalpha-ai-governance.git
    cd qualtalpha-ai-governance
    ```
    *(Note: Replace `https://github.com/your-username/qualtalpha-ai-governance.git` with the actual repository URL.)*

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    ```

3.  **Activate the virtual environment:**
    *   **On Windows:**
        ```bash
        .\venv\Scripts\activate
        ```
    *   **On macOS/Linux:**
        ```bash
        source venv/bin/activate
        ```

4.  **Install dependencies:**
    Create a `requirements.txt` file in the project root with the following content:
    ```
    streamlit
    pandas
    plotly
    ```
    Then install them:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

To run the Streamlit application:

1.  Ensure your virtual environment is activated (if you created one).
2.  Navigate to the project root directory where `app.py` is located.
3.  Execute the Streamlit command:
    ```bash
    streamlit run app.py
    ```

This will open the application in your default web browser (usually at `http://localhost:8501`).

### Basic Interaction

*   **Navigation**: Use the sidebar on the left to navigate through the different sections of the AI Governance Framework.
*   **Ethical Checklist**: On the "3. Ethical Checklist" page, select an AI model, answer the 10 questions using the radio buttons, and click the "Generate Evaluation Report" button to see the results. Your answers and evaluations are saved per model within the current session.
*   **Review**: Explore the "Final Report" page for a summary of all model evaluations and key takeaways.

## Project Structure

The project directory is organized as follows:

```
qualtalpha-ai-governance/
├── app.py
├── source.py
└── requirements.txt
└── README.md
```

*   `app.py`: The main Streamlit application file. This script orchestrates the UI, page navigation, and displays content for each section of the AI Governance Framework.
*   `source.py`: Contains the static data (e.g., `course_models`, `tier_df`, `ETHICAL_CHECKLIST`, `OVERSIGHT_POLICY`, `REGULATORY_MAP`) and core logic functions (e.g., `apply_checklist`, `compile_governance_policy`) used by `app.py`. This separation keeps the main application file cleaner and organizes data and helper functions.
*   `requirements.txt`: Lists all Python dependencies required to run the application.
*   `README.md`: This file, providing an overview and instructions for the project.

## Technology Stack

*   **Python**: The core programming language used for the application logic.
*   **Streamlit**: The open-source app framework used to build the interactive web application with Python.
*   **Pandas**: Utilized for data manipulation and display, particularly for tabular data like model risk tiers.
*   **Plotly Graph Objects**: Used to generate interactive data visualizations, specifically the radar chart for pillar-wise ethical scores.

## Contributing

This is a lab project, primarily for educational purposes. However, if you find any bugs or have suggestions for improvements, feel free to:

1.  Fork the repository.
2.  Create a new branch (`git checkout -b feature/AmazingFeature`).
3.  Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4.  Push to the branch (`git push origin feature/AmazingFeature`).
5.  Open a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
*(Note: A `LICENSE` file containing the MIT License text should be created in the project root.)*

## Contact

For any questions, suggestions, or feedback regarding this QuLab project, please reach out to:

*   **QuantUniversity Support**: [info@quantuniversity.com](mailto:info@quantuniversity.com)
*   **Website**: [www.quantuniversity.com](https://www.quantuniversity.com/)

---