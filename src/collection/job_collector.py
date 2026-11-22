"""Job data collection.

The project ships with a deterministic synthetic dataset generator so the full
pipeline runs out of the box. Replace ``collect_jobs`` with a real scraper/API
client that yields the same raw schema (job_id, title, company, location,
description, posted_at, salary, source) and nothing downstream needs to change.
"""
from __future__ import annotations

import csv
import random
from dataclasses import dataclass, asdict
from datetime import date, timedelta
from pathlib import Path
from typing import Iterable

# Canonical skills used by the cleaning/analysis layers.
SKILL_CATALOG: dict[str, str] = {
    "SQL": "Database / Query",
    "Python": "Programming",
    "Excel": "Spreadsheet",
    "Power BI": "BI / Visualization",
    "Tableau": "BI / Visualization",
    "Statistics": "Analytics",
    "Data Visualization": "Analytics",
    "ETL": "Data Engineering",
    "Machine Learning": "Advanced Analytics",
    "R": "Programming",
    "Oracle": "Database / Query",
    "Snowflake": "Database / Query",
    "Azure": "Cloud",
    "AWS": "Cloud",
    "Alteryx": "Analytics",
    "SPSS": "Analytics",
    "Git": "Tooling",
}

COMPANIES = [
    "Accenture", "Deloitte", "Infosys", "Wipro", "TCS", "Capgemini", "Cognizant",
    "IBM", "Microsoft", "Amazon", "Google", "Flipkart", "Zomato", "Swiggy",
    "HDFC Bank", "ICICI Bank", "Paytm", "PhonePe", "Adobe", "SAP",
]

LOCATIONS = [
    "Bengaluru, Karnataka", "Bangalore", "Hyderabad, Telangana", "Mumbai, Maharashtra",
    "Delhi NCR", "New Delhi", "Pune, Maharashtra", "Chennai, Tamil Nadu",
    "Kolkata, West Bengal", "Remote", "Hybrid - Bengaluru", "Gurugram, Haryana",
]

WORK_MODES = ["Onsite", "Onsite", "Onsite", "Hybrid", "Remote"]

SALARY_TEMPLATES = [
    "₹6,00,000 - ₹9,00,000 per year",
    "₹8,00,000 - ₹12,00,000 per year",
    "$70,000 - $95,000 a year",
    "$85,000 - $110,000 a year",
    "₹4,50,000 - ₹7,00,000 per year",
    "Not disclosed",
]

TITLE_LEVELS = [
    ("Junior Data Analyst", "Junior"),
    ("Data Analyst", "Mid"),
    ("Data Analyst I", "Junior"),
    ("Senior Data Analyst", "Senior"),
    ("Business Data Analyst", "Mid"),
    ("Analytics Analyst", "Mid"),
    ("Data Analyst II", "Mid"),
    ("Lead Data Analyst", "Senior"),
]

# Variants deliberately injected so cleaning has real work to do.
SKILL_ALIASES = {
    "SQL": ["SQL", "MS SQL Server", "T-SQL", "PostgreSQL"],
    "Python": ["Python", "Python 3", "Python (Pandas)"],
    "Excel": ["Excel", "Microsoft Excel", "MS Excel", "Advanced Excel"],
    "Power BI": ["Power BI", "PowerBI", "Microsoft Power BI"],
    "Tableau": ["Tableau", "Tableau Desktop"],
    "Statistics": ["Statistics", "Statistical Analysis"],
    "Data Visualization": ["Data Visualization", "Data Visualisation"],
    "ETL": ["ETL", "ETL Pipelines"],
    "Machine Learning": ["Machine Learning", "ML"],
    "R": ["R", "R Programming"],
    "Oracle": ["Oracle", "Oracle SQL"],
    "Snowflake": ["Snowflake", "Snowflake SQL"],
    "Azure": ["Azure", "Microsoft Azure"],
    "AWS": ["AWS", "Amazon Web Services"],
    "Alteryx": ["Alteryx"],
    "SPSS": ["SPSS", "IBM SPSS"],
    "Git": ["Git", "GitHub"],
}


@dataclass
class JobPosting:
    job_id: str
    title: str
    company: str
    location: str
    description: str
    posted_at: str
    salary: str
    source: str


def generate_sample_jobs(count: int = 600, seed: int = 42) -> list[JobPosting]:
    """Generate a reproducible, realistically messy set of Data Analyst jobs."""
    rng = random.Random(seed)
    today = date.today()
    jobs: list[JobPosting] = []
    for i in range(count):
        title, _level = rng.choice(TITLE_LEVELS)
        company = rng.choice(COMPANIES)
        location = rng.choice(LOCATIONS)
        chosen = rng.sample(list(SKILL_CATALOG), k=rng.randint(3, 7))
        mentions = [rng.choice(SKILL_ALIASES[skill]) for skill in chosen]
        description = (
            f"We are hiring a {title} at {company}. "
            f"Key skills: {', '.join(mentions)}. "
            "You will build dashboards, write queries and turn data into decisions. "
            f"This role is based in {location}."
        )
        posted = today - timedelta(days=rng.randint(0, 90))
        jobs.append(
            JobPosting(
                job_id=f"DA-{10000 + i}",
                title=title,
                company=company,
                location=location,
                description=description,
                posted_at=posted.isoformat(),
                salary=rng.choice(SALARY_TEMPLATES),
                source=rng.choice(["LinkedIn", "Indeed", "Glassdoor", "Naukri"]),
            )
        )
    return jobs


def load_jobs_from_csv(path: str | Path) -> list[JobPosting]:
    """Ingest a CSV with the raw schema columns."""
    with open(path, newline="", encoding="utf-8") as handle:
        return [JobPosting(**row) for row in csv.DictReader(handle)]


def collect_jobs(count: int = 600, seed: int = 42, csv_path: str | Path | None = None) -> list[dict]:
    """Return raw job records as dictionaries."""
    jobs: Iterable[JobPosting] = (
        load_jobs_from_csv(csv_path) if csv_path else generate_sample_jobs(count, seed)
    )
    return [asdict(job) for job in jobs]
