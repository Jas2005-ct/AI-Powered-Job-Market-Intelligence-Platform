"""SQL analysis layer.

Every metric shown on the dashboard is produced by an explicit SQL query here,
so the SQL expertise is real and auditable. Queries use JOINs, CTEs, GROUP BY,
window functions and DATE functions.
"""
from __future__ import annotations

import pandas as pd
from sqlalchemy import text


def _df(engine, sql: str, params: dict | None = None) -> pd.DataFrame:
    with engine.connect() as conn:
        return pd.read_sql(text(sql), conn, params=params or {})


GLOBAL_SQLITE = None  # set by pipeline if needed; kept simple otherwise


def executive_summary(engine) -> pd.DataFrame:
    sql = """
        SELECT
            COUNT(DISTINCT j.id)                          AS total_jobs,
            COUNT(DISTINCT j.company)                     AS total_companies,
            COUNT(DISTINCT j.city)                        AS total_locations,
            MIN(j.posted_at)                              AS first_posted,
            MAX(j.posted_at)                              AS last_posted
        FROM jobs j
    """
    return _df(engine, sql)


def top_skills(engine, limit: int = 20) -> pd.DataFrame:
    """Top skills with demand percentage = share of jobs requiring each skill."""
    sql = """
        WITH total AS (SELECT COUNT(*) AS n FROM jobs)
        SELECT
            s.name                                         AS skill,
            s.category,
            COUNT(js.job_id)                               AS job_count,
            ROUND(100.0 * COUNT(js.job_id) / total.n, 1)   AS demand_pct
        FROM skills s
        JOIN job_skills js ON js.skill_id = s.id
        CROSS JOIN total
        GROUP BY s.name, s.category, total.n
        ORDER BY job_count DESC
        LIMIT :limit
    """
    return _df(engine, sql, {"limit": limit})


def top_hiring_locations(engine, limit: int = 10) -> pd.DataFrame:
    sql = """
        SELECT
            j.city,
            j.work_mode,
            COUNT(*) AS openings,
            ROUND(AVG((COALESCE(j.salary_min, 0) + COALESCE(j.salary_max, 0)) / 2), 0) AS avg_salary
        FROM jobs j
        GROUP BY j.city, j.work_mode
        ORDER BY openings DESC
        LIMIT :limit
    """
    return _df(engine, sql, {"limit": limit})


def highest_paying_skills(engine, limit: int = 15) -> pd.DataFrame:
    """Average advertised salary per skill, ranked with a window function."""
    sql = """
        WITH skill_salary AS (
            SELECT
                s.name AS skill,
                j.currency,
                AVG((j.salary_min + j.salary_max) / 2) AS avg_salary,
                COUNT(*) AS postings
            FROM skills s
            JOIN job_skills js ON js.skill_id = s.id
            JOIN jobs j ON j.id = js.job_id
            WHERE j.salary_min IS NOT NULL AND j.salary_max IS NOT NULL
            GROUP BY s.name, j.currency
        )
        SELECT
            skill,
            currency,
            ROUND(avg_salary, 0) AS avg_salary,
            postings,
            RANK() OVER (PARTITION BY currency ORDER BY avg_salary DESC) AS salary_rank
        FROM skill_salary
        ORDER BY currency, avg_salary DESC
        LIMIT :limit
    """
    return _df(engine, sql, {"limit": limit})


def salary_by_experience(engine) -> pd.DataFrame:
    sql = """
        SELECT
            j.experience_level,
            j.currency,
            COUNT(*) AS postings,
            ROUND(AVG(j.salary_min), 0) AS avg_min,
            ROUND(AVG(j.salary_max), 0) AS avg_max,
            ROUND(AVG((j.salary_min + j.salary_max) / 2), 0) AS avg_midpoint
        FROM jobs j
        WHERE j.salary_min IS NOT NULL
        GROUP BY j.experience_level, j.currency
        ORDER BY j.currency, avg_midpoint DESC
    """
    return _df(engine, sql)


def salary_by_city(engine, limit: int = 10) -> pd.DataFrame:
    sql = """
        SELECT
            j.city,
            j.currency,
            COUNT(*) AS postings,
            ROUND(AVG((j.salary_min + j.salary_max) / 2), 0) AS avg_salary,
            ROUND(MIN(j.salary_min), 0) AS min_salary,
            ROUND(MAX(j.salary_max), 0) AS max_salary
        FROM jobs j
        WHERE j.salary_min IS NOT NULL
        GROUP BY j.city, j.currency
        ORDER BY j.currency, avg_salary DESC
        LIMIT :limit
    """
    return _df(engine, sql, {"limit": limit})


def salary_distribution(engine) -> pd.DataFrame:
    sql = """
        SELECT
            j.id,
            (j.salary_min + j.salary_max) / 2 AS midpoint,
            j.experience_level,
            j.city,
            j.currency
        FROM jobs j
        WHERE j.salary_min IS NOT NULL AND j.salary_max IS NOT NULL
    """
    return _df(engine, sql)


def skill_combinations(engine, limit: int = 12) -> pd.DataFrame:
    """Pairs of skills that appear together in the same job (self-join)."""
    sql = """
        SELECT
            s1.name AS skill_a,
            s2.name AS skill_b,
            COUNT(*) AS times_together
        FROM job_skills js1
        JOIN job_skills js2 ON js1.job_id = js2.job_id AND js1.skill_id < js2.skill_id
        JOIN skills s1 ON s1.id = js1.skill_id
        JOIN skills s2 ON s2.id = js2.skill_id
        GROUP BY s1.name, s2.name
        ORDER BY times_together DESC
        LIMIT :limit
    """
    return _df(engine, sql, {"limit": limit})


def skill_trends(engine) -> pd.DataFrame:
    """Weekly posting counts per skill for the top skills (dialect aware)."""
    week_expr = (
        "strftime('%Y-%W', j.posted_at)"
        if engine.dialect.name == "sqlite"
        else "to_char(date_trunc('week', j.posted_at), 'YYYY-IW')"
    )
    sql = f"""
        WITH top AS (
            SELECT skill_id, COUNT(*) AS n
            FROM job_skills GROUP BY skill_id ORDER BY n DESC LIMIT 8
        )
        SELECT
            {week_expr} AS week,
            s.name AS skill,
            COUNT(*) AS postings
        FROM job_skills js
        JOIN jobs j ON j.id = js.job_id
        JOIN skills s ON s.id = js.skill_id
        JOIN top ON top.skill_id = js.skill_id
        GROUP BY week, s.name
        ORDER BY week, s.name
    """
    return _df(engine, sql)


def work_mode_mix(engine) -> pd.DataFrame:
    sql = """
        SELECT work_mode, COUNT(*) AS postings
        FROM jobs GROUP BY work_mode ORDER BY postings DESC
    """
    return _df(engine, sql)


def skills_by_experience(engine) -> pd.DataFrame:
    """Skill demand split by junior/mid/senior postings."""
    sql = """
        SELECT
            s.name AS skill,
            j.experience_level,
            COUNT(*) AS postings
        FROM skills s
        JOIN job_skills js ON js.skill_id = s.id
        JOIN jobs j ON j.id = js.job_id
        GROUP BY s.name, j.experience_level
        ORDER BY postings DESC
    """
    return _df(engine, sql)


def skill_growth(engine) -> pd.DataFrame:
    """First-week vs last-week posting counts for each skill, with % growth."""
    week_expr = (
        "strftime('%Y-%W', j.posted_at)"
        if engine.dialect.name == "sqlite"
        else "to_char(date_trunc('week', j.posted_at), 'YYYY-IW')"
    )
    sql = f"""
        WITH weekly AS (
            SELECT {week_expr} AS week, s.name AS skill, COUNT(*) AS postings
            FROM job_skills js
            JOIN jobs j ON j.id = js.job_id
            JOIN skills s ON s.id = js.skill_id
            GROUP BY week, s.name
        ), ranked AS (
            SELECT *,
                   FIRST_VALUE(postings) OVER (PARTITION BY skill ORDER BY week) AS first_week,
                   FIRST_VALUE(postings) OVER (PARTITION BY skill ORDER BY week DESC) AS last_week
            FROM weekly
        )
        SELECT skill, first_week, last_week,
               ROUND(100.0 * (last_week - first_week) / NULLIF(first_week, 0), 1) AS growth_pct
        FROM ranked
        GROUP BY skill, first_week, last_week
        ORDER BY growth_pct DESC
    """
    return _df(engine, sql)
