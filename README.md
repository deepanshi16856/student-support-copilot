# Student Support Copilot

### AI-Powered Student Support Ticket Triage Agent

Student Support Copilot is an AI-powered application that helps organize student support tickets, identify their categories and priorities, draft helpful responses, and decide when a ticket should be escalated to a human support agent.

The project combines rule-based classification, Google Gemini, a knowledge base, and SQLite storage in a Streamlit dashboard.

## Features

* **Automatic ticket classification:** Categorizes tickets into Course Access Issue, Payment Issue, Account Issue, Academic Support, and General Inquiry.
* **Priority detection:** Assigns High, Medium, or Low priority.
* **AI-generated replies:** Uses Google Gemini to draft responses to student queries.
* **Knowledge-base citations:** Retrieves relevant guidance and displays source references.
* **Escalation decisions:** Identifies tickets that need human support based on priority, risk indicators, or missing guidance.
* **Rule-based fallback:** Provides an alternative when Gemini is unavailable.
* **Ticket management:** Stores ticket records in SQLite.
* **Streamlit dashboard:** Displays ticket statistics, priorities, classifications, and ticket history.
* **Evaluation report:** Tests classification performance against 36 labeled sample tickets.

## Technology Stack

* Python
* Streamlit
* Google Gemini API (`google-genai`)
* Pandas
* Plotly
* SQLite
* python-dotenv

## Project Structure

```text
Support Ticket Triage Agent/
├── app.py
├── triage.py
├── llm_triage.py
├── knowledge_base.py
├── database.py
├── evaluate.py
├── evaluate_rules.py
├── evaluate_llm.py
├── evaluation_app.py
├── test_triage.py
├── test_llm_triage.py
├── test_gemini.py
├── student_support_guide.md
├── evaluation_results.txt
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

The SQLite database is created locally when the application initializes.

## Installation and Setup

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd "Support Ticket Triage Agent"
```

Replace `YOUR_GITHUB_REPOSITORY_URL` with your actual GitHub repository URL.

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure the Gemini API key

Create a `.env` file in the project root and add your own Gemini API key:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

Keep your actual API key private. **Never upload `.env` to GitHub.**

### 5. Run the application

```bash
python -m streamlit run app.py
```

Streamlit will provide a local URL to open the dashboard in your browser.

## How It Works

1. A student submits a support ticket.
2. The application analyzes the ticket and predicts its category and priority.
3. The knowledge base retrieves potentially relevant guidance.
4. Gemini generates a suggested reply when the API is available.
5. The application displays relevant sources and an escalation recommendation.
6. Ticket information is stored in SQLite for tracking and review.

## Evaluation

The current rule-based classifier was evaluated against 36 labeled sample tickets.

| Category            |    Passed | Accuracy on test set |
| ------------------- | --------: | -------------------: |
| Course Access Issue |       7/7 |                 100% |
| Payment Issue       |       7/7 |                 100% |
| Account Issue       |       7/7 |                 100% |
| Academic Support    |       8/8 |                 100% |
| General Inquiry     |       7/7 |                 100% |
| **Overall**         | **36/36** |             **100%** |

Run the evaluation with:

```bash
python evaluate.py
```

These results reflect the current hand-labeled test set. They do not guarantee 100% accuracy on unseen or real-world student tickets.

## Future Improvements

* Expand testing with unseen and real-world-style support tickets.
* Improve knowledge-base retrieval and relevance scoring.
* Add authentication and role-based access for support agents.
* Add ticket assignment, status updates, and response feedback.
* Build a React frontend and connect it to a Python API.
* Evaluate AI-generated responses for relevance, correctness, and citation quality.

## Important Note

The included `student_support_guide.md` contains sample guidance created for this prototype. It is not an official university or education-provider policy document. In a production deployment, the knowledge base should use verified institutional policies.

## Project Goal

This project demonstrates practical use of Python, LLM integration, knowledge-base retrieval, ticket classification, database operations, and evaluation in an AI-assisted student support workflow.
