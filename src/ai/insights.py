"""AI insight generation.

Uses the Gemini API when GEMINI_API_KEY is configured, and falls back to a
deterministic rule-based generator so the dashboard always works offline.
"""
from __future__ import annotations

import json

from config import settings

SYSTEM_PROMPT = (
    "You are a career data analyst. You are given aggregate statistics about the "
    "Data Analyst job market. Be concise, specific, and cite the numbers you are given. "
    "Never invent statistics. Answer in short markdown paragraphs and bullet lists."
)


def _model():
    if not settings.GEMINI_API_KEY:
        return None
    try:
        import google.generativeai as genai

        genai.configure(api_key=settings.GEMINI_API_KEY)
        return genai.GenerativeModel(settings.GEMINI_MODEL)
    except Exception:
        return None


def _ask(prompt: str) -> str | None:
    model = _model()
    if model is None:
        return None
    try:
        response = model.generate_content(f"{SYSTEM_PROMPT}\n\n{prompt}", request_options={"timeout": 20})
        return response.text or None
    except Exception:
        return None


def build_context(data: dict) -> dict:
    """Reduce all dashboard DataFrames to a compact JSON-serialisable context."""
    summary = data.get("executive_summary")
    skills = data.get("top_skills")
    locations = data.get("top_hiring_locations")
    paying = data.get("highest_paying_skills")
    combos = data.get("skill_combinations")
    mix = data.get("work_mode_mix")

    context: dict = {"market": {}}
    if summary is not None and not summary.empty:
        row = summary.iloc[0]
        context["market"] = {
            "total_jobs": int(row.get("total_jobs", 0)),
            "total_companies": int(row.get("total_companies", 0)),
            "total_locations": int(row.get("total_locations", 0)),
        }
    if skills is not None and not skills.empty:
        context["top_skills"] = [
            {"skill": r.skill, "demand_pct": float(r.demand_pct), "jobs": int(r.job_count)}
            for r in skills.head(12).itertuples()
        ]
    if locations is not None and not locations.empty:
        context["top_locations"] = [
            {"city": r.city, "openings": int(r.openings), "work_mode": r.work_mode}
            for r in locations.head(6).itertuples()
        ]
    if paying is not None and not paying.empty:
        context["highest_paying_skills"] = [
            {"skill": r.skill, "avg_salary": float(r.avg_salary), "currency": "mixed (INR/USD)"}
            for r in paying.head(8).itertuples()
        ]
    if combos is not None and not combos.empty:
        context["skill_combinations"] = [
            {"skills": [r.skill_a, r.skill_b], "jobs": int(r.times_together)}
            for r in combos.head(6).itertuples()
        ]
    if mix is not None and not mix.empty:
        context["work_mode_mix"] = [
            {"mode": r.work_mode, "postings": int(r.postings)} for r in mix.itertuples()
        ]
    return context


def market_summary(context: dict) -> tuple[str, str]:
    """Return (markdown, source) where source is 'gemini' or 'rule-based'."""
    prompt = "Write an executive market summary for Data Analyst job seekers using this data:\n" + json.dumps(context, indent=2)
    answer = _ask(prompt)
    if answer:
        return answer, "gemini"

    market = context.get("market", {})
    skills = context.get("top_skills", [])
    locations = context.get("top_locations", [])
    lines = [
        f"The dataset covers **{market.get('total_jobs', 0):,} Data Analyst postings** from "
        f"**{market.get('total_companies', 0):,} companies** across "
        f"**{market.get('total_locations', 0):,} locations**."
    ]
    if skills:
        top = skills[:4]
        lines.append(
            "The most demanded skills are "
            + ", ".join(f"**{s['skill']}** ({s['demand_pct']:.0f}%)" for s in top)
            + ". A candidate who combines these has the broadest coverage of advertised roles."
        )
    if locations:
        lines.append(
            "Hiring is concentrated in "
            + ", ".join(f"**{loc['city']}** ({loc['openings']} openings)" for loc in locations[:3])
            + "."
        )
    lines.append(
        "Recommendation: prioritise SQL and a business-intelligence tool early, then add Python "
        "and statistics to move into higher-paying, analysis-heavy roles."
    )
    return "\n\n".join(lines), "rule-based"


def next_skills(current_skills: list[str], context: dict) -> tuple[list[dict], str]:
    """Recommend the next skills to learn. Returns (recommendations, source)."""
    skills = context.get("top_skills", [])
    paying = context.get("highest_paying_skills", [])
    prompt = (
        "A beginner knows these skills: "
        + (", ".join(current_skills) or "none")
        + ". Based on this market data, recommend the next 3 skills to learn, "
        "with a one-line reason each. Return a markdown bullet list only.\n"
        + json.dumps({"top_skills": skills, "highest_paying_skills": paying}, indent=2)
    )
    answer = _ask(prompt)
    if answer:
        return [{"text": answer}], "gemini"

    pay_lookup = {p["skill"]: p["avg_salary"] for p in paying}
    max_pay = max(pay_lookup.values(), default=1) or 1
    owned = {s.lower() for s in current_skills}
    ranked = []
    for item in skills:
        if item["skill"].lower() in owned:
            continue
        pay_score = pay_lookup.get(item["skill"], 0) / max_pay
        ranked.append({**item, "score": item["demand_pct"] * (1 + pay_score)})
    ranked.sort(key=lambda x: x["score"], reverse=True)
    return ranked[:3], "rule-based"
