import os
import streamlit as st
import pandas as pd

from llm_triage import triage_ticket_with_llm
from triage import triage_ticket

from database import (
    initialize_db,
    add_analysis_method_column,
    save_ticket,
    get_all_tickets,
    update_ticket_status,
)


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Student Support Copilot",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# CUSTOM DESIGN SYSTEM


st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&display=swap');

:root {
    --bg: #f6f7fb;
    --surface: #ffffff;
    --border: #e8eaf2;
    --text: #20243a;
    --muted: #777f96;
    --purple: #7657e8;
}

.stApp {
    background: var(--bg);
    color: var(--text);
    font-family: 'DM Sans', sans-serif;
}

[data-testid="stHeader"] {
    background: rgba(246, 247, 251, 0.94);
}

.block-container {
    max-width: 1500px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

section[data-testid="stSidebar"] {
    background: #171a2d;
    border-right: 1px solid #282c43;
}

section[data-testid="stSidebar"] > div {
    padding: 1.5rem 1rem;
}

section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
    color: #dce0f0;
}

section[data-testid="stSidebar"] label {
    color: #e4e6f3;
}

section[data-testid="stSidebar"] [data-testid="stRadio"] label {
    padding: 8px 10px;
    border-radius: 10px;
}

h1, h2, h3, h4 {
    color: #20243a !important;
    letter-spacing: -0.5px;
}

p, label, .stMarkdown {
    color: #4e566f;
}

[data-testid="stMetric"] {
    background: #ffffff;
    border: 1px solid #e8eaf2;
    padding: 22px;
    border-radius: 18px;
    min-height: 125px;
    box-shadow: 0 5px 20px rgba(35, 39, 75, 0.045);
}

[data-testid="stMetricLabel"] {
    color: #777f96 !important;
    font-size: 0.88rem;
}

[data-testid="stMetricValue"] {
    color: #20243a !important;
    font-weight: 800;
}

.stTextArea textarea,
.stTextInput input {
    background: #ffffff !important;
    color: #20243a !important;
    border: 1px solid #dfe3ef !important;
    border-radius: 12px !important;
}

.stTextArea textarea:focus,
.stTextInput input:focus {
    border-color: #9279f5 !important;
    box-shadow: 0 0 0 2px rgba(118, 87, 232, 0.12) !important;
}

[data-baseweb="select"] > div {
    background: #ffffff;
    border-color: #dfe3ef;
    border-radius: 11px;
}

.stButton > button,
.stFormSubmitButton > button {
    background: #7657e8 !important;
    color: #ffffff !important;
    border: 1px solid #7657e8 !important;
    border-radius: 11px !important;
    font-weight: 700 !important;
    min-height: 43px;
    transition: all 0.2s ease;
}

.stButton > button *,
.stFormSubmitButton > button * {
    color: #ffffff !important;
}

.stButton > button:hover,
.stFormSubmitButton > button:hover {
    background: #6243d3 !important;
    border-color: #6243d3 !important;
    box-shadow: 0 5px 14px rgba(118, 87, 232, 0.18);
}

[data-testid="stDataFrame"] {
    border: 1px solid #e8eaf2;
    border-radius: 13px;
}

div[data-testid="stVerticalBlockBorderWrapper"] {
    background: #ffffff;
    border-color: #e8eaf2;
    border-radius: 18px;
    box-shadow: 0 4px 18px rgba(35, 39, 75, 0.035);
}

hr {
    border-color: #e8eaf2;
}

div[data-testid="stAlert"] {
    border-radius: 12px;
}

div[data-testid="stCaptionContainer"] {
    color: #777f96;
}

.brand-title {
    font-size: 1.35rem;
    font-weight: 800;
    color: #ffffff;
    line-height: 1.3;
}

.brand-subtitle {
    font-size: 0.78rem;
    color: #aeb4d0;
    margin-top: 5px;
}

.small-muted {
    color: #aeb4d0;
    font-size: 0.78rem;
    letter-spacing: 1px;
}

.hero {
    background: linear-gradient(120deg, #ffffff 0%, #f0edff 100%);
    border: 1px solid #e5defe;
    border-radius: 22px;
    padding: 30px 32px;
    margin-bottom: 24px;
    box-shadow: 0 8px 26px rgba(91, 69, 170, 0.045);
}

.hero-eyebrow {
    color: #7657e8;
    font-size: 0.77rem;
    font-weight: 800;
    letter-spacing: 1.5px;
    text-transform: uppercase;
}

.hero-title {
    color: #20243a;
    font-size: 2.1rem;
    font-weight: 800;
    line-height: 1.2;
    margin-top: 10px;
}

.hero-description {
    color: #69718a;
    font-size: 1rem;
    margin-top: 12px;
    max-width: 760px;
    line-height: 1.7;
}

.section-heading {
    font-size: 1.15rem;
    font-weight: 800;
    color: #20243a;
    margin-bottom: 4px;
}

.result-card {
    background: #ffffff;
    border: 1px solid #e8eaf2;
    border-radius: 16px;
    padding: 20px;
    margin: 12px 0;
}

.result-label {
    color: #777f96;
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 7px;
}

.result-value {
    color: #20243a;
    font-size: 1.05rem;
    font-weight: 700;
}

footer {
    visibility: hidden;
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# DATABASE
# =========================================================

initialize_db()
add_analysis_method_column()


# =========================================================
# HELPERS
# =========================================================

def show_hero(eyebrow, title, description):
    st.markdown(
        f"""
        <div class="hero">
            <div class="hero-eyebrow">{eyebrow}</div>
            <div class="hero-title">{title}</div>
            <div class="hero-description">{description}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def priority_label(priority):
    labels = {
        "High": "🔴 High",
        "Medium": "🟠 Medium",
        "Low": "🟢 Low",
    }
    return labels.get(priority, priority)


def get_ticket_counts(tickets):
    return {
        "Total": len(tickets),
        "Open": sum(t["status"] == "Open" for t in tickets),
        "In Progress": sum(
            t["status"] == "In Progress" for t in tickets
        ),
        "Resolved": sum(t["status"] == "Resolved" for t in tickets),
        "High Priority": sum(
            t["priority"] == "High" for t in tickets
        ),
    }


# =========================================================
# SIDEBAR NAVIGATION
# =========================================================

with st.sidebar:
    st.markdown(
        """
        <div style="padding: 5px 0 22px 0;">
            <div style="font-size: 2.1rem;">🎓</div>
            <div class="brand-title">Student Support</div>
            <div class="brand-title" style="color:#a78bfa;">
                Copilot
            </div>
            <div class="brand-subtitle">
                AI-powered ticket intelligence
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    st.markdown(
        '<div class="small-muted">WORKSPACE</div>',
        unsafe_allow_html=True,
    )

    page = st.radio(
        "Navigation",
        [
            "Dashboard",
            "Submit Ticket",
            "Ticket History",
            "Evaluation",
        ],
        label_visibility="collapsed",
        key="main_navigation",
    )

    st.divider()

    st.markdown(
        """
        <div style="background:#17233a; border:1px solid #2a3853;
                    padding:15px; border-radius:14px;">
            <div style="font-weight:700; color:#f1f5f9;">
                ✨ AI Engine
            </div>
            <div style="font-size:0.8rem; color:#a8b7ce;
                        margin-top:6px;">
                Gemini with rule-based fallback
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div style="color:#73839d; font-size:0.75rem; '
        'margin-top:25px;">STUDENT SUPPORT COPILOT · v1.0</div>',
        unsafe_allow_html=True,
    )


# =========================================================
# LOAD TICKETS
# =========================================================

tickets = get_all_tickets()
counts = get_ticket_counts(tickets)


# =========================================================
# DASHBOARD PAGE
# =========================================================

if page == "Dashboard":

    show_hero(
        "STUDENT SUPPORT INTELLIGENCE",
        "Your support command center.",
        "Turn incoming student issues into organized, prioritized "
        "support tickets with AI-assisted analysis and actionable insights.",
    )

    st.markdown(
        '<div class="section-heading">Overview</div>',
        unsafe_allow_html=True,
    )
    st.caption("A live summary of the tickets saved in your database.")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Tickets", counts["Total"])
    c2.metric("Open Tickets", counts["Open"])
    c3.metric("In Progress", counts["In Progress"])
    c4.metric("Resolved", counts["Resolved"])

    st.write("")

    if tickets:
        import plotly.express as px

        chart_theme = {
            "template": "plotly_dark",
            "paper_bgcolor": "#17191d",
            "plot_bgcolor": "#17191d",
            "font": {"color": "#e5e7eb", "family": "Arial"},
            "margin": {"l": 12, "r": 12, "t": 30, "b": 12},
        }

        category_counts = (
            pd.Series([t.get("category", "Other") for t in tickets])
            .value_counts()
            .rename_axis("Category")
            .reset_index(name="Tickets")
        )

        priority_order = ["High", "Medium", "Low"]
        priority_df = pd.DataFrame({
            "Priority": priority_order,
            "Tickets": [
                sum(t.get("priority") == level for t in tickets)
                for level in priority_order
            ],
        })

        status_df = (
            pd.Series([t.get("status", "Unknown") for t in tickets])
            .value_counts()
            .rename_axis("Status")
            .reset_index(name="Tickets")
        )

        method_df = (
            pd.Series([
                t.get("analysis_method", "Unknown") or "Unknown"
                for t in tickets
            ])
            .value_counts()
            .rename_axis("Analysis Method")
            .reset_index(name="Tickets")
        )

        st.markdown("### Ticket Analytics")
        st.caption(
            "Explore ticket categories, priority, workflow status, "
            "and analysis methods."
        )

        col1, col2 = st.columns(2)

        
        with col1:
            with st.container(border=True):
                st.markdown("#### Tickets by Category")

                fig = px.bar(
                    category_counts,
                    x="Tickets",
                    y="Category",
                    orientation="h",
                    text="Tickets",
                    color="Category",
                    color_discrete_sequence=[
    "#3B82F6",
    "#22C55E",
    "#F59E0B",
    "#EF4444",
],
                )
                fig.update_layout(**chart_theme)
                fig.update_layout(
                    template="plotly_dark",
                    paper_bgcolor="#17191D",
                    plot_bgcolor="#17191D",
                    font=dict(color="#FFFFFF", size=13),
                    yaxis={"categoryorder": "total ascending"},
                    xaxis_title="Number of Tickets",
                    yaxis_title="",
                    showlegend=False,
                    height=330,
                )
                fig.update_traces(
                    textposition="outside",
                    cliponaxis=False,
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True,
                    config={"displayModeBar": False},
                )

        with col2:
            with st.container(border=True):
                st.markdown("#### Priority Distribution")

                fig = px.bar(
                    priority_df,
                    x="Priority",
                    y="Tickets",
                    text="Tickets",
                    color="Priority",
                    color_discrete_map={
                        "High": "#EF4444",
                        "High Priority": "#EF4444",
                        "Medium": "#F59E0B",
                        "Medium Priority": "#F59E0B",
                        "Low": "#22C55E",
                        "Low Priority": "#22C55E",
                    },
                )
                fig.update_layout(**chart_theme)
                fig.update_layout(
                    template="plotly_dark",
                    paper_bgcolor="#17191D",
                    plot_bgcolor="#17191D",
                    font=dict(color="#FFFFFF", size=13),
                    xaxis_title="Priority Level",
                    yaxis_title="Number of Tickets",
                    showlegend=False,
                    height=330,
                )
                fig.update_traces(
                    textposition="outside",
                    cliponaxis=False,
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True,
                    config={"displayModeBar": False},
                )

                st.metric(
                    "High-Priority Tickets",
                    counts["High Priority"],
                )

    else:
        with st.container(border=True):
            st.markdown("### Ticket Analytics")
            st.info(
                "Your charts will appear after you submit your first ticket."
            )

    st.write("")

    with st.container(border=True):
        st.markdown("### 🕒 Recent Tickets")

        if tickets:
            recent_tickets = [
                {
                    "ID": t["id"],
                    "Ticket": t["ticket"],
                    "Category": t["category"],
                    "Priority": priority_label(t["priority"]),
                    "Status": t["status"],
                    "Analysis Method": t.get(
                        "analysis_method", "Unknown"
                    ),
                }
                for t in tickets[:5]
            ]

            st.dataframe(
                recent_tickets,
                use_container_width=True,
                hide_index=True,
            )

            if st.button("View all tickets →", key="view_all_tickets"):
                st.session_state["main_navigation"] = "Ticket History"
                st.rerun()
        else:
            st.info("No tickets yet. Submit your first student issue.")

    st.write("")
    
    def go_to_submit_ticket():
        st.session_state["main_navigation"] = "Submit Ticket"

    st.button(
        "＋ Create a support ticket",
        type="primary",
        on_click=go_to_submit_ticket,
    )

# =========================================================
# SUBMIT TICKET PAGE
# =========================================================

elif page == "Submit Ticket":

    show_hero(
        "AI TICKET WORKSPACE",
        "Let's resolve a student issue.",
        "Describe the problem below. The copilot will classify the "
        "ticket, assign priority, recommend a next step, and save it.",
    )

    form_col, info_col = st.columns([1.5, 1])

    with form_col:
        with st.container(border=True):
            st.markdown("### ✍️ Describe the issue")

            with st.form("ticket_submission_form"):
                ticket_text = st.text_area(
                    "Student's message",
                    placeholder=(
                        "Example: I paid for my course, "
                        "but my batch is not visible."
                    ),
                    height=170,
                )

                submitted = st.form_submit_button(
                    "✨ Analyze and Save Ticket",
                    use_container_width=True,
                )

            if submitted:
                if not ticket_text.strip():
                    st.warning(
                        "Please describe the student's issue first."
                    )
                else:
                    clean_ticket = ticket_text.strip()

                    try:
                        with st.spinner(
                            "Analyzing your ticket with Gemini..."
                        ):
                            result = triage_ticket_with_llm(clean_ticket)

                        analysis_method = "Gemini LLM"

                        st.session_state["latest_analysis"] = {
                            "result": result,
                            "method": analysis_method,
                        }

                    
                    except Exception as error:
                        print(
                             "Gemini error:",
                        f"{type(error).__name__}: {error}",
                        )
                        st.error(f"Debug: {type(error).__name__}: {error}")

                        result = triage_ticket(clean_ticket)
                        analysis_method = "Rule-based fallback"

                        st.session_state["latest_analysis"] = {
                            "result": result,
                            "method": analysis_method,
                        }

                        st.warning(
                            "Gemini was unavailable. The rule-based "
                            "fallback analyzed your ticket instead."
                        )

                    try:
                        ticket_id = save_ticket(
                            result, analysis_method
                        )

                        st.session_state["latest_ticket_id"] = ticket_id

                        st.success(
                            f"Ticket #{ticket_id} analyzed and saved!"
                        )

                    except Exception as error:
                        print(
                            "Ticket saving error:",
                            f"{type(error).__name__}: {error}",
                        )

                        st.error(
                            "Analysis completed, but the ticket could "
                            "not be saved. Check the terminal for details."
                        )

    with info_col:
        with st.container(border=True):
            st.markdown("### 🧠 What the copilot does")

            st.markdown(
                """
                **01 · Understand**  
                Analyze the student's message.

                **02 · Classify**  
                Identify the support category.

                **03 · Prioritize**  
                Assign High, Medium, or Low priority.

                **04 · Recommend**  
                Suggest an appropriate support action.

                **05 · Save**  
                Store the ticket for follow-up.
                """
            )

            st.divider()

            st.markdown("**Supported categories**")

            st.markdown(
                """
                - Course Access Issue
                - Payment Issue
                - Account Issue
                - Academic Support
                - General Inquiry
                """
            )

    latest = st.session_state.get("latest_analysis")

    if latest:
        result = latest["result"]
        method = latest["method"]

        st.write("")

        show_hero(
            "ANALYSIS RESULT",
            "Ticket intelligence report",
            "Review the classification and recommended next action.",
        )

        r1, r2, r3 = st.columns(3)

        r1.metric("Category", result["category"])
        r2.metric("Priority", result["priority"])
        r3.metric("Analysis Engine", method)

        with st.container(border=True):
            st.markdown("### 💡 Recommended Action")
            st.write(result["recommended_action"])

            st.markdown("### 📝 Submitted Ticket")
            st.write(result["ticket"])

# =========================================================
# TICKET HISTORY PAGE
# =========================================================

elif page == "Ticket History":

    show_hero(
        "TICKET MANAGEMENT",
        "Every issue, organized.",
        "Search your saved tickets, filter by category and priority, "
        "and keep track of progress from one workspace.",
    )

    if not tickets:
        st.info(
            "No tickets have been saved yet. Submit a ticket to get started."
        )
    else:
        search_text = st.text_input(
            "🔎 Search tickets",
            placeholder="Search ticket text or category...",
        )

        f1, f2, f3 = st.columns(3)

        categories = sorted({
            t["category"] for t in tickets
        })

        with f1:
            selected_category = st.selectbox(
                "Category",
                ["All"] + categories,
            )

        with f2:
            selected_priority = st.selectbox(
                "Priority",
                ["All", "High", "Medium", "Low"],
            )

        with f3:
            selected_status = st.selectbox(
                "Status",
                ["All", "Open", "In Progress", "Resolved"],
            )

        filtered = []

        for ticket in tickets:
            matches_search = (
                search_text.strip().lower() in
                (
                    str(ticket["ticket"]) + " " +
                    str(ticket["category"])
                ).lower()
            )

            matches_category = (
                selected_category == "All"
                or ticket["category"] == selected_category
            )

            matches_priority = (
                selected_priority == "All"
                or ticket["priority"] == selected_priority
            )

            matches_status = (
                selected_status == "All"
                or ticket["status"] == selected_status
            )

            if (
                matches_search
                and matches_category
                and matches_priority
                and matches_status
            ):
                filtered.append(ticket)

        st.caption(
            f"Showing {len(filtered)} of {len(tickets)} tickets"
        )

        display_rows = []

        for t in filtered:
            display_rows.append({
                "ID": t["id"],
                "Ticket": t["ticket"],
                "Category": t["category"],
                "Priority": priority_label(t["priority"]),
                "Status": t["status"],
                "Analysis Method": t.get(
                    "analysis_method", "Unknown"
                ),
                "Created At": t.get("created_at", ""),
            })

        with st.container(border=True):
            st.dataframe(
                display_rows,
                use_container_width=True,
                hide_index=True,
            )

        st.write("")

        with st.container(border=True):
            st.markdown("### 🔄 Update Ticket Status")

            id_to_ticket = {
                t["id"]: t for t in tickets
            }

            selected_id = st.selectbox(
                "Select ticket ID",
                list(id_to_ticket.keys()),
                format_func=lambda ticket_id: (
                    f"#{ticket_id} — "
                    f"{id_to_ticket[ticket_id]['ticket'][:65]}"
                ),
            )

            new_status = st.selectbox(
                "New status",
                ["Open", "In Progress", "Resolved"],
                key="history_new_status",
            )

            if st.button(
                "Update Status",
                key="history_update_status",
                type="primary",
            ):
                updated = update_ticket_status(
                    selected_id, new_status
                )

                if updated:
                    st.success(
                        f"Ticket #{selected_id} updated to {new_status}."
                    )
                    st.rerun()
                else:
                    st.error("The selected ticket could not be updated.")


# =========================================================
# EVALUATION PAGE
# =========================================================

elif page == "Evaluation":

    show_hero(
        "MODEL QUALITY",
        "Measure before you improve.",
        "Run test cases and measure the quality of your ticket classifier.",
    )

    st.markdown("### 🧪 Rule-Based Evaluation")

    st.write(
        "Run your current test suite to check whether the rule-based "
        "classifier predicts the expected category and priority."
    )

    if st.button("▶ Run Evaluation", use_container_width=True):
        import subprocess
        import sys

        with st.spinner("Running evaluation test suite..."):
            try:
                evaluation = subprocess.run(
                    [sys.executable, "evaluate_rules.py"],
                    capture_output=True,
                    text=True,
                    timeout=60,
                    cwd=os.path.dirname(os.path.abspath(__file__)),
                )

                st.session_state["evaluation_output"] = evaluation.stdout
                st.session_state["evaluation_error"] = evaluation.stderr
                st.session_state["evaluation_returncode"] = evaluation.returncode

            except subprocess.TimeoutExpired:
                st.error("Evaluation timed out. Please try again.")

            except Exception as error:
                st.error(f"Could not run evaluation: {error}")

    if "evaluation_returncode" in st.session_state:
        output = st.session_state.get("evaluation_output", "")
        error_output = st.session_state.get("evaluation_error", "")
        returncode = st.session_state["evaluation_returncode"]

        st.markdown("### 📊 Evaluation Results")

        if output:
            st.code(output, language="text")

        if returncode == 0:
            st.success("Evaluation script completed successfully.")
        else:
            st.error(
                "Some tests may have failed, or the evaluation script "
                "encountered an error."
            )

        if error_output:
            st.markdown("### Error details")
            st.code(error_output, language="text")

    st.markdown("### 📌 What is being tested?")

    st.markdown(
        """
        - Category predictions against expected labels.
        - Priority predictions against expected labels.
        - Payment, account, course access, and academic tickets.
        - General inquiries and other test cases.
        """
    )

    st.info(
        "This evaluates the rule-based classifier only. It does not "
        "measure Gemini's accuracy."
    )


# =========================================================
# FOOTER
# =========================================================

st.markdown("---")

st.markdown(
    """
    <div style="text-align:center; color:#73839d; font-size:0.8rem;
                padding:8px 0;">
        Built with Python · Streamlit · Gemini · SQLite
        <br>
        Student Support Copilot — AI-assisted ticket triage
    </div>
    """,
    unsafe_allow_html=True,
)