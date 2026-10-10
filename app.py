
import os
import sys
import subprocess
from datetime import datetime

import pandas as pd
import plotly.express as px
import streamlit as st

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
# DESIGN SYSTEM — BLACK + EMERALD
# =========================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&display=swap');

:root {
    --bg: #080b09;
    --surface: #101612;
    --surface2: #151e18;
    --border: #293a2f;
    --text: #f1f7f2;
    --muted: #9aaca0;
    --green: #22c55e;
    --green-light: #4ade80;
}

.stApp {
    background: var(--bg);
    color: var(--text);
    font-family: 'DM Sans', sans-serif;
}

[data-testid="stHeader"] {
    background: rgba(8, 11, 9, 0.96);
}

.block-container {
    max-width: 1500px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

section[data-testid="stSidebar"] {
    background: #0b100d;
    border-right: 1px solid var(--border);
}

section[data-testid="stSidebar"] > div {
    padding: 1.5rem 1rem;
}

section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
section[data-testid="stSidebar"] label {
    color: #dce8df;
}

section[data-testid="stSidebar"] [data-testid="stRadio"] label {
    padding: 8px 10px;
    border-radius: 10px;
}

section[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
    background: #17251b;
}

h1, h2, h3, h4,
[data-testid="stMarkdownContainer"] h1,
[data-testid="stMarkdownContainer"] h2,
[data-testid="stMarkdownContainer"] h3,
[data-testid="stMarkdownContainer"] h4 {
    color: var(--text) !important;
    letter-spacing: -0.4px;
}

p, label, .stMarkdown {
    color: #c2cec5;
}

[data-testid="stMetric"] {
    background: linear-gradient(145deg, #151e18, #0e130f);
    border: 1px solid #2b3e31;
    padding: 20px;
    border-radius: 17px;
    min-height: 118px;
    box-shadow: 0 8px 28px rgba(0, 0, 0, 0.16);
    transition: border-color 0.2s ease, transform 0.2s ease;
}

[data-testid="stMetric"]:hover {
    border-color: #3d8053;
    transform: translateY(-2px);
}

[data-testid="stMetricLabel"] {
    color: var(--muted) !important;
    font-size: 0.86rem;
}

[data-testid="stMetricValue"] {
    color: var(--green-light) !important;
    font-weight: 800;
}

.stTextArea textarea,
.stTextInput input {
    background: #0d120f !important;
    color: var(--text) !important;
    border: 1px solid #304137 !important;
    border-radius: 12px !important;
}

.stTextArea textarea:focus,
.stTextInput input:focus {
    border-color: var(--green) !important;
    box-shadow: 0 0 0 2px rgba(34, 197, 94, 0.15) !important;
}

[data-baseweb="select"] > div {
    background: #111813;
    color: var(--text);
    border-color: #304137;
    border-radius: 11px;
}

[data-baseweb="popover"],
[data-baseweb="menu"] {
    background: #111813;
}

.stButton > button,
.stFormSubmitButton > button {
    background: linear-gradient(135deg, #16a34a, #15803d) !important;
    color: white !important;
    border: 1px solid #22c55e !important;
    border-radius: 11px !important;
    font-weight: 700 !important;
    min-height: 43px;
    transition: all 0.2s ease;
}

.stButton > button *,
.stFormSubmitButton > button * {
    color: white !important;
}

.stButton > button:hover,
.stFormSubmitButton > button:hover {
    background: linear-gradient(135deg, #22c55e, #16a34a) !important;
    border-color: #4ade80 !important;
    box-shadow: 0 5px 20px rgba(34, 197, 94, 0.18);
}

[data-testid="stDataFrame"] {
    border: 1px solid var(--border);
    border-radius: 13px;
    overflow: hidden;
}

div[data-testid="stVerticalBlockBorderWrapper"] {
    background: linear-gradient(145deg, #111713, #0d120f);
    border: 1px solid var(--border);
    border-radius: 17px;
    box-shadow: 0 5px 22px rgba(0, 0, 0, 0.14);
}

hr {
    border-color: var(--border);
}

div[data-testid="stAlert"] {
    border-radius: 12px;
}

div[data-testid="stCaptionContainer"] {
    color: var(--muted);
}

.brand-title {
    font-size: 1.28rem;
    font-weight: 800;
    color: #f1f7f2;
    line-height: 1.3;
}

.brand-subtitle {
    font-size: 0.76rem;
    color: #9aaca0;
    margin-top: 5px;
}

.small-muted {
    color: #8fa497;
    font-size: 0.75rem;
    letter-spacing: 1.5px;
    font-weight: 700;
}

.hero {
    background:
        radial-gradient(ellipse at 95% 5%, rgba(34, 197, 94, 0.13), transparent 42%),
        linear-gradient(120deg, #131c16 0%, #0c110e 100%);
    border: 1px solid #2a4433;
    border-radius: 22px;
    padding: 29px 31px;
    margin-bottom: 24px;
    box-shadow: 0 12px 35px rgba(0, 0, 0, 0.20);
}

.hero-eyebrow {
    color: var(--green-light);
    font-size: 0.75rem;
    font-weight: 800;
    letter-spacing: 1.8px;
    text-transform: uppercase;
}

.hero-title {
    color: #f1f7f2;
    font-size: 2.05rem;
    font-weight: 800;
    line-height: 1.2;
    margin-top: 10px;
}

.hero-description {
    color: #a8b9ad;
    font-size: 0.96rem;
    margin-top: 12px;
    max-width: 800px;
    line-height: 1.7;
}

.section-heading {
    font-size: 1.13rem;
    font-weight: 800;
    color: #f1f7f2;
    margin-bottom: 4px;
}

.result-card {
    background: #111813;
    border: 1px solid #2a3b30;
    border-radius: 16px;
    padding: 20px;
    margin: 12px 0;
}

.result-label {
    color: var(--muted);
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 7px;
}

.result-value {
    color: var(--green-light);
    font-size: 1.05rem;
    font-weight: 700;
}

div[data-testid="stForm"] {
    border-color: var(--border);
}

.stProgress > div > div > div > div {
    background-color: var(--green);
}

footer {
    visibility: hidden;
}
</style>
""", unsafe_allow_html=True)


# =========================================================
# DATABASE INITIALIZATION
# =========================================================

initialize_db()
add_analysis_method_column()


# =========================================================
# HELPER FUNCTIONS
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
    icons = {
        "High": "🔴 High",
        "Medium": "🟠 Medium",
        "Low": "🟢 Low",
    }
    return icons.get(priority, str(priority))


def get_ticket_counts(ticket_list):
    return {
        "Total": len(ticket_list),
        "Open": sum(t.get("status") == "Open" for t in ticket_list),
        "In Progress": sum(
            t.get("status") == "In Progress" for t in ticket_list
        ),
        "Resolved": sum(
            t.get("status") == "Resolved" for t in ticket_list
        ),
        "High Priority": sum(
            t.get("priority") == "High" for t in ticket_list
        ),
    }


def chart_layout(fig, height=340):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(
            family="DM Sans, sans-serif",
            color="#dce8df",
            size=12,
        ),
        margin=dict(l=12, r=12, t=35, b=12),
        height=height,
        hoverlabel=dict(
            bgcolor="#17251b",
            bordercolor="#22c55e",
            font=dict(color="#f1f7f2"),
        ),
        legend=dict(
            bgcolor="rgba(0,0,0,0)",
            font=dict(color="#c2cec5"),
        ),
    )
    fig.update_xaxes(
        showgrid=True,
        gridcolor="rgba(130,160,140,0.12)",
        zerolinecolor="rgba(130,160,140,0.15)",
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor="rgba(130,160,140,0.12)",
        zerolinecolor="rgba(130,160,140,0.15)",
    )
    return fig


def safe_ticket_date(ticket):
    value = ticket.get("created_at")
    if not value:
        return pd.NaT
    return pd.to_datetime(value, errors="coerce")


def go_to_history():
    st.session_state["main_navigation"] = "Ticket History"


def go_to_submit():
    st.session_state["main_navigation"] = "Submit Ticket"


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:
    st.markdown(
        """
        <div style="padding:5px 0 22px 0;">
            <div style="font-size:2rem;">🎓</div>
            <div class="brand-title">Student Support</div>
            <div class="brand-title" style="color:#4ade80;">Copilot</div>
            <div class="brand-subtitle">AI-powered ticket intelligence</div>
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
        <div style="background:#121d16;border:1px solid #2a4433;
                    padding:15px;border-radius:14px;">
            <div style="font-weight:700;color:#4ade80;">✦ AI Engine</div>
            <div style="font-size:0.79rem;color:#a8b7ad;margin-top:6px;">
                Gemini with rule-based fallback
            </div>
            <div style="font-size:0.73rem;color:#819487;margin-top:10px;">
                CLASSIFY · PRIORITIZE · RECOMMEND
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div style="color:#73877a;font-size:0.72rem;margin-top:25px;">
            STUDENT SUPPORT COPILOT · v1.0
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# LOAD TICKETS
# =========================================================

tickets = get_all_tickets() or []
counts = get_ticket_counts(tickets)


# =========================================================
# DASHBOARD
# =========================================================

if page == "Dashboard":

    show_hero(
        "STUDENT SUPPORT INTELLIGENCE",
        "Your support command center.",
        "Turn incoming student issues into organized, prioritized support "
        "tickets with AI-assisted analysis and actionable insights.",
    )

    st.markdown(
        '<div class="section-heading">Overview</div>',
        unsafe_allow_html=True,
    )
    st.caption("A live summary of tickets saved in your database.")

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("🎫 Total Tickets", counts["Total"])
    k2.metric("🟡 Open Tickets", counts["Open"])
    k3.metric("⚙️ In Progress", counts["In Progress"])
    k4.metric("✅ Resolved", counts["Resolved"])

    st.write("")

    if tickets:
        st.markdown("### 📊 Ticket Analytics")
        st.caption(
            "Explore ticket categories, urgency, workflow status, "
            "and the distribution of tickets over time."
        )

        category_counts = (
            pd.Series([
                t.get("category", "Other") or "Other"
                for t in tickets
            ])
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
        priority_df = priority_df[priority_df["Tickets"] > 0]

        status_order = ["Open", "In Progress", "Resolved"]
        status_df = pd.DataFrame({
            "Status": status_order,
            "Tickets": [
                sum(t.get("status") == level for t in tickets)
                for level in status_order
            ],
        })
        status_df = status_df[status_df["Tickets"] > 0]

        left, right = st.columns(2)

        with left:
            with st.container(border=True):
                st.markdown("#### Tickets by Category")

                fig = px.bar(
                    category_counts.sort_values("Tickets"),
                    x="Tickets",
                    y="Category",
                    orientation="h",
                    text="Tickets",
                    color="Tickets",
                    color_continuous_scale=["#17472a", "#22c55e", "#86efac"],
                    hover_data={"Category": True, "Tickets": True},
                )
                chart_layout(fig, 350)
                fig.update_layout(
                    coloraxis_showscale=False,
                    xaxis_title="Number of Tickets",
                    yaxis_title="",
                    showlegend=False,
                )
                fig.update_traces(
                    textposition="outside",
                    cliponaxis=False,
                    marker_line_width=0,
                )
                st.plotly_chart(
                    fig,
                    use_container_width=True,
                    config={"displayModeBar": False},
                    key="category_chart",
                )

        with right:
            with st.container(border=True):
                st.markdown("#### Priority Distribution")

                if not priority_df.empty:
                    priority_colors = {
                        "High": "#fb7185",
                        "Medium": "#fbbf24",
                        "Low": "#4ade80",
                    }

                    fig = px.pie(
                        priority_df,
                        names="Priority",
                        values="Tickets",
                        hole=0.68,
                        color="Priority",
                        color_discrete_map=priority_colors,
                        custom_data=["Tickets"],
                    )
                    chart_layout(fig, 350)
                    fig.update_traces(
                        textposition="inside",
                        textinfo="percent",
                        insidetextfont=dict(color="#ffffff", size=13),
                        marker=dict(
                            line=dict(color="#101612", width=4)
                        ),
                        hovertemplate=(
                            "<b>%{label}</b><br>"
                            "Tickets: %{value}<br>"
                            "Share: %{percent}<extra></extra>"
                        ),
                    )
                    fig.update_layout(
                        showlegend=True,
                        legend=dict(orientation="h", y=-0.08),
                    )
                    st.plotly_chart(
                        fig,
                        use_container_width=True,
                        config={"displayModeBar": False},
                        key="priority_chart",
                    )
                else:
                    st.info("Priority information is not available yet.")

        lower_left, lower_right = st.columns(2)

        with lower_left:
            with st.container(border=True):
                st.markdown("#### Workflow Status")

                if not status_df.empty:
                    status_colors = {
                        "Open": "#fbbf24",
                        "In Progress": "#60a5fa",
                        "Resolved": "#4ade80",
                    }
                    fig = px.bar(
                        status_df,
                        x="Status",
                        y="Tickets",
                        color="Status",
                        text="Tickets",
                        color_discrete_map=status_colors,
                        hover_data={"Status": True, "Tickets": True},
                    )
                    chart_layout(fig, 320)
                    fig.update_layout(
                        xaxis_title="",
                        yaxis_title="Tickets",
                        showlegend=False,
                    )
                    fig.update_traces(
                        textposition="outside",
                        cliponaxis=False,
                    )
                    st.plotly_chart(
                        fig,
                        use_container_width=True,
                        config={"displayModeBar": False},
                        key="status_chart",
                    )
                else:
                    st.info("No workflow status data is available.")

        with lower_right:
            with st.container(border=True):
                st.markdown("#### Ticket Activity")

                timeline = pd.DataFrame([
                    {
                        "Created": safe_ticket_date(t),
                        "Ticket ID": t.get("id"),
                    }
                    for t in tickets
                ])
                timeline = timeline.dropna(subset=["Created"])

                if not timeline.empty:
                    timeline["Date"] = timeline["Created"].dt.strftime(
                        "%Y-%m-%d"
                    )
                    daily = (
                        timeline.groupby("Date")
                        .size()
                        .reset_index(name="Tickets")
                        .sort_values("Date")
                    )
                    daily["Cumulative Tickets"] = daily["Tickets"].cumsum()

                    fig = px.area(
                        daily,
                        x="Date",
                        y="Cumulative Tickets",
                        markers=True,
                        custom_data=["Tickets"],
                    )
                    chart_layout(fig, 320)
                    fig.update_traces(
                        line=dict(color="#4ade80", width=3),
                        fillcolor="rgba(34,197,94,0.18)",
                        marker=dict(color="#4ade80", size=7),
                        hovertemplate=(
                            "<b>%{x}</b><br>"
                            "Cumulative tickets: %{y}<br>"
                            "Tickets created that day: %{customdata[0]}"
                            "<extra></extra>"
                        ),
                    )
                    fig.update_layout(
                        xaxis_title="Date",
                        yaxis_title="Total tickets",
                        showlegend=False,
                    )
                    st.plotly_chart(
                        fig,
                        use_container_width=True,
                        config={"displayModeBar": False},
                        key="activity_chart",
                    )
                else:
                    st.info(
                        "Ticket activity will appear when saved tickets "
                        "have readable creation dates."
                    )

        st.write("")
        a, b, c = st.columns(3)
        a.metric("🔴 High Priority", counts["High Priority"])
        a.metric if False else None
        b.metric(
            "🤖 Gemini Analyses",
            sum(
                "gemini" in str(t.get("analysis_method", "")).lower()
                for t in tickets
            ),
        )
        c.metric(
            "🧩 Rule-Based Analyses",
            sum(
                "rule" in str(t.get("analysis_method", "")).lower()
                for t in tickets
            ),
        )

    else:
        with st.container(border=True):
            st.markdown("### 📈 Ticket Analytics")
            st.info(
                "Your analytics will appear after you submit your first ticket."
            )
            st.markdown(
                "Start by submitting a student issue. The copilot will "
                "classify it, assign a priority, and recommend an action."
            )
            st.button(
                "＋ Create your first ticket",
                type="primary",
                on_click=go_to_submit,
                use_container_width=True,
            )

    st.write("")

    with st.container(border=True):
        st.markdown("### 🕒 Recent Tickets")

        if tickets:
            recent_rows = [
                {
                    "ID": t.get("id", ""),
                    "Ticket": t.get("ticket", ""),
                    "Category": t.get("category", ""),
                    "Priority": priority_label(t.get("priority", "")),
                    "Status": t.get("status", ""),
                    "Analysis Method": t.get("analysis_method", "Unknown"),
                }
                for t in tickets[:5]
            ]
            st.dataframe(
                recent_rows,
                use_container_width=True,
                hide_index=True,
            )
            st.button(
                "View all tickets →",
                key="dashboard_view_all",
                on_click=go_to_history,
            )
        else:
            st.caption("No tickets have been submitted yet.")

    st.write("")
    st.button(
        "＋ Create a support ticket",
        type="primary",
        on_click=go_to_submit,
    )

    
# =========================================================
# SUBMIT TICKET
# =========================================================

elif page == "Submit Ticket":

    show_hero(
        "AI TICKET WORKSPACE",
        "Let's resolve a student issue.",
        "Describe the student's problem. The copilot will classify the "
        "ticket, assign priority, recommend a next step, and save it.",
    )

    form_col, info_col = st.columns([1.45, 1])

    with form_col:
        with st.container(border=True):
            st.markdown("### ✍️ Describe the issue")

            with st.form("ticket_submission_form", clear_on_submit=False):
                ticket_text = st.text_area(
                    "Student's message",
                    placeholder=(
                        "Example: I paid for my course, "
                        "but my batch is not visible."
                    ),
                    height=180,
                    max_chars=5000,
                )

                submitted = st.form_submit_button(
                    "✦ Analyze and Save Ticket",
                    use_container_width=True,
                    type="primary",
                )

            if submitted:
                clean_ticket = ticket_text.strip()

                if not clean_ticket:
                    st.warning("Please describe the student's issue first.")

                else:
                    result = None
                    analysis_method = "Rule-based fallback"
                    gemini_failed = False

                    try:
                        with st.spinner("Analyzing ticket with Gemini..."):
                            result = triage_ticket_with_llm(clean_ticket)

                        analysis_method = "Gemini LLM"

                    except Exception as error:
                        gemini_failed = True

                        # Technical details go to the terminal, not the UI.
                        print(
                            "Gemini error:",
                            f"{type(error).__name__}: {error}",
                        )

                        try:
                            with st.spinner(
                                "Gemini is unavailable. Using rule-based analysis..."
                            ):
                                result = triage_ticket(clean_ticket)

                            analysis_method = "Rule-based fallback"

                        except Exception as fallback_error:
                            print(
                                "Rule-based fallback error:",
                                f"{type(fallback_error).__name__}: "
                                f"{fallback_error}",
                            )
                            st.error(
                                "Ticket analysis failed. Please check the "
                                "terminal for details and try again."
                            )
                            result = None

                    if result is not None:
                        required_keys = [
                            "category",
                            "priority",
                            "recommended_action",
                        ]

                        if not all(key in result for key in required_keys):
                            st.error(
                                "The analysis returned an unexpected result. "
                                "Please check the classifier output."
                            )

                        else:
                            st.session_state["latest_analysis"] = {
                                "result": result,
                                "method": analysis_method,
                                "ticket": clean_ticket,
                            }

                            try:
                                ticket_id = save_ticket(
                                    result,
                                    analysis_method,
                                )

                                st.session_state["latest_ticket_id"] = ticket_id

                                if gemini_failed:
                                    st.warning(
                                        "Gemini was unavailable, so the "
                                        "rule-based fallback was used."
                                    )

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
                                    "not be saved. Check the terminal for "
                                    "technical details."
                                )

    with info_col:
        with st.container(border=True):
            st.markdown("### 🧠 How the copilot works")

            steps = [
                ("01", "Understand", "Analyze the student's message."),
                ("02", "Classify", "Identify the support category."),
                ("03", "Prioritize", "Assign High, Medium, or Low priority."),
                ("04", "Recommend", "Suggest an appropriate support action."),
                ("05", "Save", "Store the ticket for follow-up."),
            ]

            for number, title, description in steps:
                st.markdown(
                    f"""
                    <div style="
                        display:flex; gap:13px; align-items:flex-start;
                        padding:12px 0;
                        border-bottom:1px solid #26372c;">
                        <div style="
                            color:#4ade80; font-weight:800;
                            font-size:0.85rem; min-width:26px;">
                            {number}
                        </div>
                        <div>
                            <div style="
                                color:#f1f7f2; font-weight:700;">
                                {title}
                            </div>
                            <div style="
                                color:#9aaca0; font-size:0.84rem;
                                margin-top:3px;">
                                {description}
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            st.write("")
            st.markdown("**Supported categories**")

            categories = [
                "📚 Course Access Issue",
                "💳 Payment Issue",
                "👤 Account Issue",
                "📝 Academic Support",
                "💬 General Inquiry",
            ]

            for category in categories:
                st.markdown(f"- {category}")

    # Display the latest analysis stored in this session.
    latest = st.session_state.get("latest_analysis")

    if latest:
        result = latest["result"]
        method = latest["method"]

        st.write("")
        show_hero(
            "ANALYSIS RESULT",
            "Ticket intelligence report",
            "Review the classification, priority, and recommended next action.",
        )

        r1, r2, r3 = st.columns(3)
        r1.metric("📂 Category", result.get("category", "Unknown"))
        r2.metric(
            "🚦 Priority",
            priority_label(result.get("priority", "Unknown")),
        )
        r3.metric("⚙️ Analysis Engine", method)

                # Drafted response based on the knowledge base
        drafted_reply = result.get("drafted_reply")

        if drafted_reply:
            with st.container(border=True):
                st.markdown("### ✉️ Drafted Student Reply")
                st.write(drafted_reply)

                st.caption(
                    "Review this draft before sending it to a student."
                )

                st.button(
                    "📋 Copy reply",
                    on_click=lambda reply=drafted_reply: st.session_state.update(
                        {"reply_to_copy": reply}
                    ),
                    key="copy_drafted_reply",
                )

        # Knowledge-base citations
        citations = result.get("citations")

        if citations:
            with st.container(border=True):
                st.markdown("### 📚 Knowledge-Base Sources")
                st.text(citations)

        # Human escalation decision
        routing = result.get("routing_decision")

        if routing:
            with st.container(border=True):
                st.markdown("### 🚦 Ticket Routing")
                st.write(f"**Decision:** {routing}")
                st.write(
                    "**Reason:** "
                    + result.get(
                        "escalation_reason",
                        "No additional reason provided.",
                    )
                )

            ticket_id = st.session_state.get("latest_ticket_id")
            if ticket_id is not None:
                st.caption(f"Saved ticket reference: #{ticket_id}")

        with st.expander("View analyzed student message"):
            st.write(latest.get("ticket", ""))


# =========================================================
# TICKET HISTORY
# =========================================================

elif page == "Ticket History":

    show_hero(
        "TICKET MANAGEMENT",
        "Ticket history",
        "Search saved tickets, filter by status or priority, "
        "and update their progress.",
    )

    if not tickets:
        with st.container(border=True):
            st.markdown("### No tickets to display")
            st.info(
                "Submit a student issue to start building your ticket history."
            )
            st.button(
                "＋ Submit a ticket",
                type="primary",
                on_click=go_to_submit,
            )

    else:
        st.markdown("### 🔎 Find tickets")

        filter_col1, filter_col2 = st.columns([1.5, 1])

        with filter_col1:
            search_text = st.text_input(
                "Search ticket text or category",
                placeholder="Search by keyword...",
                key="history_search",
            )

        with filter_col2:
            status_filter = st.selectbox(
                "Filter by status",
                ["All", "Open", "In Progress", "Resolved"],
                key="history_status_filter",
            )

        filter_col3, filter_col4 = st.columns(2)

        with filter_col3:
            priority_filter = st.selectbox(
                "Filter by priority",
                ["All", "High", "Medium", "Low"],
                key="history_priority_filter",
            )

        with filter_col4:
            category_options = sorted({
                str(t.get("category", "Unknown"))
                for t in tickets
            })
            category_filter = st.selectbox(
                "Filter by category",
                ["All"] + category_options,
                key="history_category_filter",
            )

        filtered = []

        for ticket in tickets:
            search_blob = (
                str(ticket.get("ticket", ""))
                + " "
                + str(ticket.get("category", ""))
            ).lower()

            if search_text.strip().lower() not in search_blob:
                continue

            if (
                status_filter != "All"
                and ticket.get("status") != status_filter
            ):
                continue

            if (
                priority_filter != "All"
                and ticket.get("priority") != priority_filter
            ):
                continue

            if (
                category_filter != "All"
                and ticket.get("category") != category_filter
            ):
                continue

            filtered.append(ticket)

        st.write("")

        total_col, open_col, resolved_col = st.columns(3)
        total_col.metric("Matching Tickets", len(filtered))
        open_col.metric(
            "Open",
            sum(t.get("status") == "Open" for t in filtered),
        )
        resolved_col.metric(
            "Resolved",
            sum(t.get("status") == "Resolved" for t in filtered),
        )

        st.write("")

        with st.container(border=True):
            st.markdown("### 📋 Saved tickets")

            if filtered:
                display_rows = [
                    {
                        "ID": t.get("id", ""),
                        "Ticket": t.get("ticket", ""),
                        "Category": t.get("category", ""),
                        "Priority": priority_label(
                            t.get("priority", "")
                        ),
                        "Status": t.get("status", ""),
                        "Analysis Method": t.get(
                            "analysis_method", "Unknown"
                        ),
                        "Created At": t.get("created_at", ""),
                    }
                    for t in filtered
                ]

                st.dataframe(
                    display_rows,
                    use_container_width=True,
                    hide_index=True,
                )
            else:
                st.info("No tickets match the selected filters.")

        st.write("")

        with st.container(border=True):
            st.markdown("### 🔄 Update ticket status")

            id_to_ticket = {
                t["id"]: t for t in tickets if "id" in t
            }

            if id_to_ticket:
                selected_id = st.selectbox(
                    "Select ticket",
                    list(id_to_ticket.keys()),
                    format_func=lambda ticket_id: (
                        f"#{ticket_id} — "
                        f"{str(id_to_ticket[ticket_id].get('ticket', ''))[:65]}"
                    ),
                    key="history_selected_ticket",
                )

                current_status = id_to_ticket[selected_id].get(
                    "status", "Open"
                )

                st.caption(f"Current status: **{current_status}**")

                new_status = st.selectbox(
                    "New status",
                    ["Open", "In Progress", "Resolved"],
                    index=(
                        ["Open", "In Progress", "Resolved"].index(
                            current_status
                        )
                        if current_status in [
                            "Open", "In Progress", "Resolved"
                        ]
                        else 0
                    ),
                    key="history_new_status",
                )

                if st.button(
                    "Update Status",
                    key="history_update_status",
                    type="primary",
                ):
                    try:
                        updated = update_ticket_status(
                            selected_id,
                            new_status,
                        )

                        if updated:
                            st.success(
                                f"Ticket #{selected_id} updated to "
                                f"{new_status}."
                            )
                            st.rerun()
                        else:
                            st.error(
                                "The selected ticket could not be updated."
                            )

                    except Exception as error:
                        print(
                            "Status update error:",
                            f"{type(error).__name__}: {error}",
                        )
                        st.error(
                            "Unable to update the ticket status. "
                            "Check the terminal for details."
                        )


# =========================================================
# EVALUATION
# =========================================================

elif page == "Evaluation":

    show_hero(
        "MODEL QUALITY",
        "Measure before you improve.",
        "Run the rule-based test suite to check category and priority "
        "predictions against your expected results.",
    )

    st.markdown("### 🧪 Rule-based evaluation")

    st.write(
        "This runs your existing `evaluate_rules.py` test script. "
        "It does not change your database or ticket records."
    )

    if st.button(
        "▶ Run Evaluation",
        use_container_width=True,
        type="primary",
    ):
        with st.spinner("Running evaluation test suite..."):
            try:
                script_path = os.path.join(
                    os.path.dirname(os.path.abspath(__file__)),
                    "evaluate_rules.py",
                )

                evaluation = subprocess.run(
                    [sys.executable, script_path],
                    capture_output=True,
                    text=True,
                    timeout=60,
                    cwd=os.path.dirname(os.path.abspath(__file__)),
                )

                st.session_state["evaluation_output"] = (
                    evaluation.stdout
                )
                st.session_state["evaluation_error"] = (
                    evaluation.stderr
                )
                st.session_state["evaluation_returncode"] = (
                    evaluation.returncode
                )

            except subprocess.TimeoutExpired:
                st.error("Evaluation timed out. Please try again.")

            except Exception as error:
                print(
                    "Evaluation error:",
                    f"{type(error).__name__}: {error}",
                )
                st.error(
                    "Could not run the evaluation. Check the terminal "
                    "for technical details."
                )

    if "evaluation_returncode" in st.session_state:
        output = st.session_state.get("evaluation_output", "")
        error_output = st.session_state.get("evaluation_error", "")
        returncode = st.session_state["evaluation_returncode"]

        st.write("")

        with st.container(border=True):
            st.markdown("### 📊 Evaluation results")

            if output:
                st.code(output, language="text")
            else:
                st.caption("The evaluation script returned no standard output.")

            if returncode == 0:
                st.success("Evaluation script completed successfully.")
            else:
                st.error(
                    "The evaluation script reported an error or failed tests."
                )

            if error_output:
                with st.expander("Technical details"):
                    st.code(error_output, language="text")

    with st.container(border=True):
        st.markdown("### 📌 What is being tested?")

        st.markdown("""
        - Category predictions against expected labels.
        - Priority predictions against expected labels.
        - Payment, account, course access, and academic tickets.
        - General inquiries and other test cases.
        """)

        st.info(
            "This page evaluates the rule-based classifier only. "
            "It does not measure Gemini's accuracy."
        )


# =========================================================
# FOOTER
# =========================================================

st.markdown("---")

st.markdown(
    """
    <div style="
        text-align:center;
        color:#73877a;
        font-size:0.79rem;
        padding:12px 0;">
        Built with Python · Streamlit · Gemini · SQLite · Plotly
        <br>
        Student Support Copilot — AI-assisted ticket triage
    </div>
    """,
    unsafe_allow_html=True,
)