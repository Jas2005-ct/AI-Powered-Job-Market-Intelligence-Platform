"""Streamlit entry point for the Job Market Intelligence dashboard."""
from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dashboard.data_loader import load_table  # noqa: E402

st.set_page_config(
    page_title="Job Market Intelligence | Data Analysts",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.sidebar.title("📊 Job Market Intelligence")
st.sidebar.caption("Data Analyst roles • SQL + Python + AI")
st.sidebar.markdown(
    """
    **Navigate** with the pages menu above.

    1. Executive Summary
    2. Skills Analysis
    3. Salary Analysis
    4. AI Recommendations
    """
)

if st.sidebar.button("🔄 Refresh data"):
    from src.pipeline import run

    with st.spinner("Rebuilding the dataset..."):
        run()
    st.cache_data.clear()
    st.sidebar.success("Data refreshed!")
    st.rerun()

summary = load_table("executive_summary")
total_jobs = int(summary["total_jobs"].iloc[0]) if not summary.empty else 0

col1, col2, col3 = st.columns([3, 1, 1])
with col1:
    st.title("AI-Powered Job Market Intelligence Platform")
    st.markdown(
        "A data-driven view of the **Data Analyst job market** — the skills, cities, "
        "salaries and tools that actually matter, with AI-generated career guidance."
    )
with col2:
    st.metric("Jobs analysed", f"{total_jobs:,}")
with col3:
    st.metric("Dashboard pages", 4)

st.divider()
st.subheader("What this platform answers")
st.markdown(
    """
- **Which skills** are most demanded (and which pay the most)?
- **Which cities** have the most openings, and what is the remote/hybrid mix?
- **Which tools** appear together in real job descriptions?
- **What should a beginner learn next** to maximise employability?
"""
)

st.info("Use the left sidebar to open a dashboard page. Data is generated locally on first run.")
