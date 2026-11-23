"""Database engine/session helpers and loading of cleaned jobs."""
from __future__ import annotations

from datetime import date
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import settings
from src.collection.job_collector import SKILL_CATALOG
from src.database.models import Base, Job, JobSkill, Skill


def get_database_url() -> tuple[str, bool]:
    """Return (url, uses_sqlite)."""
    if settings.USE_SQLITE_FALLBACK:
        path: Path = settings.SQLITE_PATH
        path.parent.mkdir(parents=True, exist_ok=True)
        return f"sqlite:///{path}", True
    return settings.DATABASE_URL, False


def get_engine():
    url, is_sqlite = get_database_url()
    kwargs = {"connect_args": {"check_same_thread": False}} if is_sqlite else {}
    return create_engine(url, **kwargs)


def init_db(engine=None):
    engine = engine or get_engine()
    Base.metadata.create_all(engine)
    return engine


def get_session(engine=None):
    engine = engine or get_engine()
    return sessionmaker(bind=engine)()


def load_cleaned_jobs(cleaned_jobs: list[dict], engine=None) -> int:
    """Upsert cleaned jobs (and their skills) into the database. Returns rows loaded."""
    engine = engine or init_db()
    session = get_session(engine)
    try:
        skill_lookup = {s.name: s for s in session.query(Skill).all()}
        for name, category in SKILL_CATALOG.items():
            if name not in skill_lookup:
                skill = Skill(name=name, category=category)
                session.add(skill)
                skill_lookup[name] = skill
        session.flush()

        loaded = 0
        for record in cleaned_jobs:
            if session.query(Job).filter_by(job_id=record["job_id"]).first():
                continue
            posted = record.get("posted_at")
            job = Job(
                job_id=record["job_id"],
                title=record["title"],
                company=record["company"],
                location_raw=record["location_raw"],
                city=record["city"],
                work_mode=record["work_mode"],
                description=record["description"],
                posted_at=date.fromisoformat(posted) if isinstance(posted, str) and posted else None,
                salary_min=record["salary_min"],
                salary_max=record["salary_max"],
                currency=record["currency"],
                source=record["source"],
                experience_level=record["experience_level"],
            )
            for skill_name in record.get("skills", []):
                skill = skill_lookup.get(skill_name)
                if skill:
                    job.skills.append(JobSkill(skill=skill))
            session.add(job)
            loaded += 1
        session.commit()
        return loaded
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
