"""Page 2: Skills Analysis — demand %, trends and skill combinations."""
from __future__ import annotations

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from dashboard.data_loader import empty_guard, load_all

st.set_page_config(page_title="Skills Analysis", page_icon="🧠", layout="wide")
st.title("🧠 Skills Analysis")

data = load_all()
skills = data["top_skills"]

left, right = st.columns([2, 1])
with left:
    st.subheader("Top 20 Skills")
    if not empty_guard(skills):
        fig = px.bar(
            skills.sort_values("job_count", ascending=True),
            x="job_count",
            y="skill",
            color="category",
            orientation="h",
            hover_data=["demand_pct"],
            labels={"job_count": "Number of jobs"},
        )
        fig.update_layout(height=620, margin=dict(l=10, r=30, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("Demand %")
    if not empty_guard(skills):
        st.dataframe(
            skills[["skill", "demand_pct", "job_count"]].head(20).style.format({"demand_pct": "{:.1f}%"}),
            hide_index=True,
            use_container_width=True,
            height=620,
        )

st.divider()
st.subheader("Skill Demand Over Time")
trends = data["skill_trends"]
if not empty_guard(trends, "Add more dated postings to see trends."):
    fig = go.Figure()
    for skill in sorted(trends["skill"].unique()):
        subset = trends[trends["skill"] == skill].sort_values("week")
        fig.add_trace(go.Scatter(x=subset["week"], y=subset["postings"], mode="lines+markers", name=skill))
    fig.update_layout(height=420, xaxis_title="Week", yaxis_title="Postings")
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Skills That Appear Together")
combos = data["skill_combinations"]
if not empty_guard(combos):
    combos = combos.copy()
    combos["pair"] = combos["skill_a"] + " + " + combos["skill_b"]
    fig = px.bar(
        combos.sort_values("times_together", ascending=True),
        x="times_together",
        y="pair",
        orientation="h",
        text="times_together",
        labels={"times_together": "Jobs requiring both"},
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(height=460, margin=dict(l=10, r=50, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)
