"""Shared cached data access for all Streamlit pages."""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config import settings  # noqa: E402

TABLES = [
    "executive_summary",
    "top_skills",
    "top_hiring_locations",
    "highest_paying_skills",
    "salary_by_experience",
    "salary_by_city",
    "salary_distribution",
    "skill_combinations",
    "skill_trends",
    "work_mode_mix",
    "skills_by_experience",
    "skill_growth",
]


@st.cache_data(show_spinner="Loading job market data...")
def load_table(name: str) -> pd.DataFrame:
    path = settings.PROCESSED_DIR / f"{name}.csv"
    if not path.exists():
        from src.pipeline import run

        run()
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path)


@st.cache_data(show_spinner="Loading all datasets...")
def load_all() -> dict[str, pd.DataFrame]:
    return {name: load_table(name) for name in TABLES}


def empty_guard(frame: pd.DataFrame, message: str = "No data available.") -> bool:
    if frame is None or frame.empty:
        st.info(message)
        return True
    return False
