# AI-Powered Job Market Intelligence Platform

> A portfolio-grade analytics product that analyses the **Data Analyst job market** itself
> instead of the usual sales/Netflix/Titanic datasets. It demonstrates SQL, Python,
> PostgreSQL, an interactive Streamlit dashboard and Gemini-powered career insights.

## What it answers

- What skills are most demanded for Data Analysts?
- Which cities have the most openings, and what is the remote/hybrid mix?
- What salary ranges are offered, and which skills pay the most?
- Which tools do companies request most?
- Which skill combinations appear together?
- What should a beginner learn next?

## Architecture

```
Job Data Collection
  -> Data Cleaning (normalise skills, locations, salaries)
  -> PostgreSQL (via SQLAlchemy; SQLite fallback for local demo)
  -> SQL Analysis (JOINs, CTEs, window functions)
  -> Python EDA (Pandas / NumPy / Plotly)
  -> AI Insight Generation (Gemini API, with offline fallback)
  -> Interactive Dashboard (Streamlit, 4 pages)
  -> Business Recommendations
```

## Quick start

```bash
python -m venv .venv && . .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                           # Windows: copy .env.example .env
python -m src.pipeline                         # collect -> clean -> store -> analyse
streamlit run dashboard/app.py
```

By default the project uses a local SQLite database (`data/processed/job_market.db`) so it
runs without any credentials. Set `USE_SQLITE_FALLBACK=false` and a `DATABASE_URL` to use
PostgreSQL. Set `GEMINI_API_KEY` to enable live AI insights; otherwise the app uses a
deterministic rule-based fallback.

## Dashboard pages

1. **Executive Summary** — total jobs, companies, top skill, top hiring location, work-mode mix.
2. **Skills Analysis** — top 20 skills, demand %, weekly trends, skill combinations.
3. **Salary Analysis** — highest-paying skills, salary by city, by experience, distribution.
4. **AI Recommendations** — Gemini-generated market narrative and beginner learning path.

## Repository layout

```
config/          configuration
src/collection/  data collection (synthetic generator + CSV loader)
src/cleaning/    normalisation of skills, locations, salaries
src/database/    SQLAlchemy models and loading logic
src/analysis/    all SQL queries behind the dashboard
src/ai/          Gemini integration (phase 3)
src/pipeline.py  orchestrator
dashboard/       Streamlit application (phase 2+)
sql/             reference PostgreSQL DDL and queries
tests/           unit tests for cleaning
```

## Roadmap

- [x] Phase 1 — data pipeline, database schema, SQL analysis
- [ ] Phase 2 — dashboard v1 (summary, skills, salary)
- [ ] Phase 3 — AI recommendations
- [ ] Phase 4 — trends, experience splits, polish
