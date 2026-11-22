"""Page 3: Salary Analysis."""
from __future__ import annotations

import numpy as np
import plotly.express as px
import streamlit as st

from dashboard.data_loader import empty_guard, load_all

st.set_page_config(page_title="Salary Analysis", page_icon="💰", layout="wide")
st.title("💰 Salary Analysis")

data = load_all()

st.subheader("Highest Paying Skills")
paying = data["highest_paying_skills"]
if not empty_guard(paying):
    fig = px.bar(
        paying.sort_values("avg_salary", ascending=True),
        x="avg_salary",
        y="skill",
        orientation="h",
        color="avg_salary",
        color_continuous_scale="Viridis",
        hover_data=["postings", "salary_rank"],
        labels={"avg_salary": "Average advertised salary"},
    )
    fig.update_layout(height=480, margin=dict(l=10, r=40, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)

col1, col2 = st.columns(2)
with col1:
    st.subheader("Salary by City")
    by_city = data["salary_by_city"]
    if not empty_guard(by_city):
        fig = px.bar(by_city.sort_values("avg_salary", ascending=True), x="avg_salary", y="city", orientation="h")
        fig.update_layout(height=420)
        st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Salary by Experience Level")
    by_exp = data["salary_by_experience"]
    if not empty_guard(by_exp):
        fig = px.bar(
            by_exp,
            x="experience_level",
            y=["avg_min", "avg_max"],
            barmode="group",
            labels={"value": "Salary", "experience_level": "Level"},
            title="Average salary range by seniority",
        )
        fig.update_layout(height=420)
        st.plotly_chart(fig, use_container_width=True)

st.subheader("Salary Distribution")
dist = data["salary_distribution"]
if not empty_guard(dist):
    currencies = sorted(dist["currency"].dropna().unique())
    chosen = st.selectbox("Currency", currencies, index=0 if currencies else None)
    dist = dist[dist["currency"] == chosen]
    fig = px.histogram(
        dist,
        x="midpoint",
        nbins=40,
        color="experience_level",
        marginal="box",
        labels={"midpoint": "Advertised salary midpoint"},
    )
    fig.update_layout(height=480)
    st.plotly_chart(fig, use_container_width=True)

    q1, q2, q3 = st.columns(3)
    values = dist["midpoint"].dropna()
    q1.metric("Median", f"{np.median(values):,.0f}")
    q2.metric("25th percentile", f"{np.percentile(values, 25):,.0f}")
    q3.metric("75th percentile", f"{np.percentile(values, 75):,.0f}")
