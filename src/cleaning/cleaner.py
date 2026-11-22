"""Data cleaning and normalisation.

Scraped job descriptions are messy: skill names have aliases, locations have
variants, salaries are free text. This module turns raw records into a clean,
analysis-ready schema.
"""
from __future__ import annotations

import re

from src.collection.job_collector import SKILL_CATALOG, SKILL_ALIASES

# Skill alias -> canonical name lookup (case-insensitive).
_ALIAS_LOOKUP: dict[str, str] = {}
for canonical, aliases in SKILL_ALIASES.items():
    for alias in aliases:
        _ALIAS_LOOKUP[alias.lower()] = canonical
for canonical in SKILL_CATALOG:
    _ALIAS_LOOKUP[canonical.lower()] = canonical

_CITY_MAP = {
    "bangalore": "Bengaluru",
    "bengaluru": "Bengaluru",
    "bengaluru, karnataka": "Bengaluru",
    "hyderabad": "Hyderabad",
    "hyderabad, telangana": "Hyderabad",
    "mumbai": "Mumbai",
    "mumbai, maharashtra": "Mumbai",
    "delhi": "Delhi NCR",
    "delhi ncr": "Delhi NCR",
    "new delhi": "Delhi NCR",
    "pune": "Pune",
    "pune, maharashtra": "Pune",
    "chennai": "Chennai",
    "chennai, tamil nadu": "Chennai",
    "kolkata": "Kolkata",
    "kolkata, west bengal": "Kolkata",
    "gurugram": "Gurugram",
    "gurugram, haryana": "Gurugram",
}


def normalize_skill(name: str) -> str | None:
    """Map a free-text skill mention to its canonical name."""
    key = name.strip().lower()
    return _ALIAS_LOOKUP.get(key)


def normalize_location(raw: str) -> tuple[str, str]:
    """Return (city, work_mode) from a raw location string."""
    text = (raw or "").strip()
    lower = text.lower()
    if "remote" in lower:
        return "Remote", "Remote"
    if "hybrid" in lower:
        for city, canonical in _CITY_MAP.items():
            if city in lower:
                return canonical, "Hybrid"
        return "Hybrid", "Hybrid"
    return _CITY_MAP.get(lower, text or "Unknown"), "Onsite"


def parse_salary(raw: str) -> tuple[float | None, float | None, str]:
    """Extract (min, max, currency) from salary free text.

    Handles INR lakh notation, USD ranges, hourly rates and 'Not disclosed'.
    Stored values are normalised to yearly amounts in the source currency.
    """
    text = (raw or "").strip()
    if not text or "not disclosed" in text.lower():
        return None, None, "N/A"

    currency = "INR" if ("₹" in text or "lakh" in text.lower()) else "USD"
    numbers = [float(n.replace(",", "")) for n in re.findall(r"[\d,]+(?:\.\d+)?", text)]
    if not numbers:
        return None, None, currency

    def yearly(value: float) -> float:
        if currency == "INR" and "lakh" in text.lower() or (currency == "INR" and value < 100):
            return value * 100_000
        if "hour" in text.lower():
            return value * 2080
        return value

    lo, hi = yearly(numbers[0]), yearly(numbers[-1])
    if lo > hi:
        lo, hi = hi, lo
    return lo, hi, currency


def parse_experience(title: str, description: str) -> str:
    """Infer experience level from title/description keywords."""
    text = f"{title} {description}".lower()
    if any(w in text for w in ("senior", "lead", "principal", "5+ years")):
        return "Senior"
    if any(w in text for w in ("junior", "entry", "intern", "graduate", "i ")):
        return "Junior"
    return "Mid"


def extract_skills(description: str) -> list[str]:
    """Find canonical skills mentioned in a description.

    Word boundaries matter: without them, the alias "R" would match the letter
    "r" in almost every English word and inflate demand to ~100%.
    """
    lower = description.lower()
    found = set()
    for canonical, aliases in SKILL_ALIASES.items():
        for alias in aliases:
            if re.search(rf"\b{re.escape(alias.lower())}\b", lower):
                found.add(canonical)
                break
    return sorted(found)


def clean_jobs(raw_jobs: list[dict]) -> list[dict]:
    """Clean a batch of raw job records."""
    cleaned: list[dict] = []
    seen: set[str] = set()
    for job in raw_jobs:
        job_id = (job.get("job_id") or "").strip()
        if not job_id or job_id in seen:
            continue
        seen.add(job_id)

        city, work_mode = normalize_location(job.get("location", ""))
        min_sal, max_sal, currency = parse_salary(job.get("salary", ""))
        title = (job.get("title") or "").strip()
        description = (job.get("description") or "").strip()

        cleaned.append(
            {
                "job_id": job_id,
                "title": title,
                "company": (job.get("company") or "Unknown").strip(),
                "location_raw": job.get("location", ""),
                "city": city,
                "work_mode": work_mode,
                "description": description,
                "posted_at": job.get("posted_at"),
                "salary_min": min_sal,
                "salary_max": max_sal,
                "currency": currency,
                "source": job.get("source", "Unknown"),
                "experience_level": parse_experience(title, description),
                "skills": extract_skills(description),
            }
        )
    return cleaned
