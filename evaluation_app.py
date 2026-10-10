import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="LLM Evaluation Dashboard",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Student Support Copilot")
st.subheader("AI Evaluation Dashboard")

st.write(
    "Compare the rule-based baseline with Gemini's "
    "ticket classification performance."
)

st.info(
    "Your rule-based baseline achieved 100% category "
    "and priority accuracy on the five current test cases. "
    "This is an initial test, not a measure of general accuracy."
)

results = [
    {
        "Method": "Rule-based baseline",
        "Test cases": 5,
        "Category accuracy": "100%",
        "Priority accuracy": "100%"
    },
    {
        "Method": "Gemini LLM",
        "Test cases": 2,
        "Category accuracy": "100% (2 completed)",
        "Priority accuracy": "100% (2 completed)"
    }
]

df = pd.DataFrame(results)

col1, col2, col3 = st.columns(3)

col1.metric("Baseline Test Cases", 5)
col2.metric("Gemini Tests Completed", "2 / 5")
col3.metric("Gemini Completion Rate", "40%")

st.subheader("Evaluation Comparison")
st.dataframe(df, use_container_width=True, hide_index=True)

st.caption(
    "Gemini results are based only on completed tests. "
    "Uncompleted tests are not counted as passes or failures."
)