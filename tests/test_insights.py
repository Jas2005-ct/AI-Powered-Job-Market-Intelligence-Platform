import pandas as pd

from src.ai.insights import build_context, market_summary, next_skills


def sample_data() -> dict:
    return {
        "executive_summary": pd.DataFrame(
            [{"total_jobs": 100, "total_companies": 20, "total_locations": 5}]
        ),
        "top_skills": pd.DataFrame(
            [
                {"skill": "SQL", "demand_pct": 85.0, "job_count": 85, "category": "Database / Query"},
                {"skill": "Python", "demand_pct": 60.0, "job_count": 60, "category": "Programming"},
                {"skill": "Excel", "demand_pct": 55.0, "job_count": 55, "category": "Spreadsheet"},
            ]
        ),
        "highest_paying_skills": pd.DataFrame(
            [{"skill": "Python", "avg_salary": 900000.0, "postings": 10, "salary_rank": 1}]
        ),
        "top_hiring_locations": pd.DataFrame(
            [{"city": "Bengaluru", "openings": 40, "work_mode": "Hybrid"}]
        ),
        "skill_combinations": pd.DataFrame([{"skill_a": "SQL", "skill_b": "Excel", "times_together": 30}]),
        "work_mode_mix": pd.DataFrame([{"work_mode": "Hybrid", "postings": 40}]),
    }


def test_build_context_is_serialisable():
    context = build_context(sample_data())
    assert context["market"]["total_jobs"] == 100
    assert context["top_skills"][0]["skill"] == "SQL"


def test_fallback_market_summary_mentions_numbers():
    text, source = market_summary(build_context(sample_data()))
    assert source in {"gemini", "rule-based"}
    assert "100" in text


def test_fallback_next_skills_excludes_owned():
    context = build_context(sample_data())
    recs, source = next_skills(["SQL"], context)
    assert source in {"gemini", "rule-based"}
    if source == "rule-based":
        names = [r["skill"] for r in recs]
        assert "SQL" not in names
        assert "Python" in names
