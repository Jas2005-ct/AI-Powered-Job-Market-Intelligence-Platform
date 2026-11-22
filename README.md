# AI-Powered Job Market Intelligence Platform

> A portfolio-grade analytics product that analyses the **Data Analyst job market** itself
> instead of the usual sales / Netflix / Titanic datasets. It demonstrates SQL, Python,
> PostgreSQL, an interactive Streamlit dashboard and Gemini-powered career insights.

## What it answers

- What skills are most demanded for Data Analysts? (with demand % and weekly trends)
- Which cities have the most openings, and what is the remote/hybrid mix?
- What salary ranges are offered, and which skills pay the most?
- Which tools and skill combinations appear together in real job descriptions?
- What should a beginner learn next to maximise employability?

## Architecture

```
Job Data Collection (synthetic generator / CSV loader)
  -> Data Cleaning (normalise skill aliases, locations, salaries; word-boundary skill extraction)
  -> PostgreSQL (SQLAlchemy models; SQLite fallback for a zero-config local demo)
  -> SQL Analysis (JOINs, CTEs, window functions, date bucketing, self-joins)
  -> Python EDA (Pandas / NumPy / Plotly)
  -> AI Insight Generation (Gemini API with deterministic offline fallback)
  -> Interactive Dashboard (Streamlit, 4 pages)
  -> Business Recommendations
```

## Quick start

```bash
python -m venv .venv && . .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python -m src.pipeline                         # collect -> clean -> load -> analyse
streamlit run dashboard/app.py
```

By default the project uses a local SQLite database (`data/processed/job_market.db`) so it
runs without credentials. To use PostgreSQL, set `USE_SQLITE_FALLBACK=false` and a real
`DATABASE_URL` (the reference DDL is in `sql/schema.sql`). Set `GEMINI_API_KEY` to enable
live AI insights; without it the app uses a rule-based engine built from the SQL results.

## Dashboard pages

1. **Executive Summary** — total jobs, companies, locations, top skill, top hiring location, work-mode mix.
2. **Skills Analysis** — top 20 skills, demand %, weekly trends, demand by experience, growth, skill combinations.
3. **Salary Analysis** — highest-paying skills, salary by city, by experience level, distribution with percentiles.
4. **AI Recommendations** — Gemini-generated market narrative, personalised "learn next" suggestions, high-coverage skill pairs.

## SQL techniques demonstrated

- `JOIN` / self-join (`job_skills` to itself for skill combinations)
- `CTE` (`WITH total`, `WITH skill_salary`, `WITH weekly`, `WITH ranked`)
- `GROUP BY` and aggregate functions (`COUNT`, `AVG`, `MIN`, `MAX`)
- Window functions (`RANK() OVER`, `FIRST_VALUE() OVER`)
- Date bucketing (`date_trunc` on PostgreSQL, `strftime` on SQLite)
- Indexed relational schema (`jobs`, `skills`, `job_skills`)

## Repository layout

```
config/           configuration from environment variables
src/collection/   data collection (synthetic generator + CSV loader)
src/cleaning/     normalisation of skills, locations, salaries
src/database/     SQLAlchemy models and loading logic
src/analysis/     all SQL queries behind the dashboard
src/ai/           Gemini integration with offline fallback
src/pipeline.py   orchestrator
dashboard/        Streamlit application (4 pages)
sql/              reference PostgreSQL DDL and queries
tests/            unit tests for cleaning and AI fallbacks
```

## Verification

```bash
python -m pytest tests -q
python -m src.pipeline
```

## Roadmap

- [x] Phase 1 — data pipeline, database schema, SQL analysis
- [x] Phase 2 — dashboard v1 (summary, skills, salary)
- [x] Phase 3 — AI recommendations
- [x] Phase 4 — trends, experience splits, growth, refresh control, documentation
