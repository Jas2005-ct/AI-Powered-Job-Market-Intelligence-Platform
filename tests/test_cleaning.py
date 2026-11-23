from src.cleaning.cleaner import (
    clean_jobs,
    extract_skills,
    normalize_location,
    normalize_skill,
    parse_salary,
)


def test_normalize_skill_aliases():
    assert normalize_skill("MS Excel") == "Excel"
    assert normalize_skill("PowerBI") == "Power BI"
    assert normalize_skill("unknown") is None


def test_normalize_location():
    assert normalize_location("Bangalore") == ("Bengaluru", "Onsite")
    assert normalize_location("Hybrid - Bengaluru") == ("Bengaluru", "Hybrid")
    assert normalize_location("Remote") == ("Remote", "Remote")


def test_parse_salary_inr_lakh():
    lo, hi, currency = parse_salary("₹6,00,000 - ₹9,00,000 per year")
    assert currency == "INR"
    assert lo == 600000 and hi == 900000


def test_extract_skills_finds_canonical_names():
    skills = extract_skills("Need SQL, PowerBI and advanced Excel skills.")
    assert "SQL" in skills and "Power BI" in skills and "Excel" in skills


def test_single_letter_skill_uses_word_boundaries():
    assert "R" not in extract_skills("We are hiring a data analyst to build reports.")


def test_clean_jobs_deduplicates():
    raw = [
        {
            "job_id": "A-1",
            "title": "Data Analyst",
            "company": "Acme",
            "location": "Bangalore",
            "description": "SQL and Excel",
            "posted_at": "2026-01-01",
            "salary": "$70,000 - $90,000 a year",
            "source": "Indeed",
        },
        {
            "job_id": "A-1",
            "title": "Data Analyst",
            "company": "Acme",
            "location": "Bangalore",
            "description": "SQL and Excel",
            "posted_at": "2026-01-01",
            "salary": "$70,000 - $90,000 a year",
            "source": "Indeed",
        },
    ]
    assert len(clean_jobs(raw)) == 1
