-- PostgreSQL reference schema (SQLAlchemy creates tables in code; this file is
-- the human-readable DDL and a set of reusable analytical queries).

CREATE TABLE IF NOT EXISTS jobs (
    id                SERIAL PRIMARY KEY,
    job_id            VARCHAR(50) UNIQUE NOT NULL,
    title             VARCHAR(200) NOT NULL,
    company           VARCHAR(200) NOT NULL,
    location_raw      VARCHAR(200),
    city              VARCHAR(100),
    work_mode         VARCHAR(20),
    description       TEXT,
    posted_at         DATE,
    salary_min        NUMERIC,
    salary_max        NUMERIC,
    currency          VARCHAR(10),
    source            VARCHAR(50),
    experience_level  VARCHAR(20)
);

CREATE INDEX IF NOT EXISTS idx_jobs_city ON jobs(city);
CREATE INDEX IF NOT EXISTS idx_jobs_posted_at ON jobs(posted_at);
CREATE INDEX IF NOT EXISTS idx_jobs_company ON jobs(company);

CREATE TABLE IF NOT EXISTS skills (
    id        SERIAL PRIMARY KEY,
    name      VARCHAR(100) UNIQUE NOT NULL,
    category  VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS job_skills (
    job_id    INTEGER REFERENCES jobs(id) ON DELETE CASCADE,
    skill_id  INTEGER REFERENCES skills(id) ON DELETE CASCADE,
    PRIMARY KEY (job_id, skill_id)
);

-- Top 20 skills with demand %
WITH total AS (SELECT COUNT(*) AS n FROM jobs)
SELECT s.name,
       s.category,
       COUNT(js.job_id) AS job_count,
       ROUND(100.0 * COUNT(js.job_id) / total.n, 1) AS demand_pct
FROM skills s
JOIN job_skills js ON js.skill_id = s.id
CROSS JOIN total
GROUP BY s.name, s.category, total.n
ORDER BY job_count DESC
LIMIT 20;

-- Skill combinations (self-join)
SELECT s1.name AS skill_a, s2.name AS skill_b, COUNT(*) AS times_together
FROM job_skills js1
JOIN job_skills js2 ON js1.job_id = js2.job_id AND js1.skill_id < js2.skill_id
JOIN skills s1 ON s1.id = js1.skill_id
JOIN skills s2 ON s2.id = js2.skill_id
GROUP BY s1.name, s2.name
ORDER BY times_together DESC
LIMIT 12;

-- Highest paying skills (window function)
WITH skill_salary AS (
    SELECT s.name AS skill,
           AVG((j.salary_min + j.salary_max) / 2) AS avg_salary,
           COUNT(*) AS postings
    FROM skills s
    JOIN job_skills js ON js.skill_id = s.id
    JOIN jobs j ON j.id = js.job_id
    WHERE j.salary_min IS NOT NULL AND j.salary_max IS NOT NULL
    GROUP BY s.name
)
SELECT skill, ROUND(avg_salary, 0) AS avg_salary, postings,
       RANK() OVER (ORDER BY avg_salary DESC) AS salary_rank
FROM skill_salary
ORDER BY avg_salary DESC
LIMIT 15;
