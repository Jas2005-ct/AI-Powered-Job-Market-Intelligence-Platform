"""Page 1: Executive Summary."""
from __future__ import annotations

import plotly.express as px
import streamlit as st

from dashboard.data_loader import empty_guard, load_all

st.set_page_config(page_title="Executive Summary", page_icon="📌", layout="wide")
st.title("📌 Executive Summary")

data = load_all()
summary = data["executive_summary"]

if empty_guard(summary, "Run `python -m src.pipeline` to generate data."):
    st.stop()

row = summary.iloc[0]
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Jobs", f"{int(row['total_jobs']):,}")
c2.metric("Total Companies", f"{int(row['total_companies']):,}")
c3.metric("Hiring Locations", f"{int(row['total_locations']):,}")

skills = data["top_skills"]
locations = data["top_hiring_locations"]
c4.metric(
    "Top Skill",
    f"{skills.iloc[0]['skill']} ({skills.iloc[0]['demand_pct']:.0f}%)" if not skills.empty else "—",
)

st.divider()
left, right = st.columns(2)

with left:
    st.subheader("Top Hiring Locations")
    if not empty_guard(locations):
        fig = px.bar(
            locations.sort_values("openings", ascending=True),
            x="openings",
            y="city",
            color="work_mode",
            orientation="h",
            text="openings",
            color_discrete_sequence=px.colors.qualitative.Plotly,
        )
        fig.update_traces(textposition="outside")
        fig.update_layout(height=420, margin=dict(l=10, r=40, t=10, b=10))
        st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("Work Mode Mix")
    mix = data["work_mode_mix"]
    if not empty_guard(mix):
        fig = px.pie(mix, values="postings", names="work_mode", hole=0.45)
        fig.update_layout(height=420)
        st.plotly_chart(fig, use_container_width=True)

st.subheader("Top 10 Skills by Demand")
top10 = skills.head(10)
if not empty_guard(top10):
    fig = px.bar(
        top10.sort_values("demand_pct"),
        x="demand_pct",
        y="skill",
        orientation="h",
        text="demand_pct",
        labels={"demand_pct": "Demand (% of jobs)"},
    )
    fig.update_traces(texttemplate="%{text:.0f}%", textposition="outside")
    fig.update_layout(height=400, margin=dict(l=10, r=50, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)
