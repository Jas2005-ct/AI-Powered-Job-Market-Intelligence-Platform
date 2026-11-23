"""End-to-end pipeline: collect -> clean -> store -> analyse.

Run with: python -m src.pipeline
"""
from __future__ import annotations

import json

from config import settings
from src.analysis import sql_queries
from src.collection.job_collector import collect_jobs
from src.cleaning.cleaner import clean_jobs
from src.database import db


def run(count: int | None = None) -> dict:
    settings.PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    raw = collect_jobs(count or settings.SAMPLE_JOBS)
    cleaned = clean_jobs(raw)

    engine = db.init_db()
    loaded = db.load_cleaned_jobs(cleaned, engine)

    analyses = {
        "executive_summary": sql_queries.executive_summary(engine),
        "top_skills": sql_queries.top_skills(engine),
        "top_hiring_locations": sql_queries.top_hiring_locations(engine),
        "highest_paying_skills": sql_queries.highest_paying_skills(engine),
        "salary_by_experience": sql_queries.salary_by_experience(engine),
        "salary_by_city": sql_queries.salary_by_city(engine),
        "salary_distribution": sql_queries.salary_distribution(engine),
        "skill_combinations": sql_queries.skill_combinations(engine),
        "skill_trends": sql_queries.skill_trends(engine),
        "work_mode_mix": sql_queries.work_mode_mix(engine),
        "skills_by_experience": sql_queries.skills_by_experience(engine),
        "skill_growth": sql_queries.skill_growth(engine),
    }

    for name, frame in analyses.items():
        frame.to_csv(settings.PROCESSED_DIR / f"{name}.csv", index=False)

    summary = {
        "raw_records": len(raw),
        "cleaned_records": len(cleaned),
        "loaded_records": loaded,
        "tables": list(analyses),
    }
    (settings.PROCESSED_DIR / "pipeline_summary.json").write_text(json.dumps(summary, indent=2))
    return summary


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
