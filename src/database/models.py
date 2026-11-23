"""SQLAlchemy ORM models for the job market warehouse."""
from __future__ import annotations

from sqlalchemy import Column, Date, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True)
    job_id = Column(String(50), unique=True, nullable=False, index=True)
    title = Column(String(200), nullable=False)
    company = Column(String(200), nullable=False, index=True)
    location_raw = Column(String(200))
    city = Column(String(100), index=True)
    work_mode = Column(String(20), index=True)
    description = Column(Text)
    posted_at = Column(Date, index=True)
    salary_min = Column(Float)
    salary_max = Column(Float)
    currency = Column(String(10))
    source = Column(String(50))
    experience_level = Column(String(20), index=True)

    skills = relationship("JobSkill", back_populates="job", cascade="all, delete-orphan")


class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    category = Column(String(100))

    jobs = relationship("JobSkill", back_populates="skill", cascade="all, delete-orphan")


class JobSkill(Base):
    __tablename__ = "job_skills"

    job_id = Column(Integer, ForeignKey("jobs.id"), primary_key=True)
    skill_id = Column(Integer, ForeignKey("skills.id"), primary_key=True)

    job = relationship("Job", back_populates="skills")
    skill = relationship("Skill", back_populates="jobs")
