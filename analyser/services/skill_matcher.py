import re

# Canonical skill -> variants that should count as the same skill.
SKILL_VOCAB = {
    "python": ["python"],
    "java": ["java"],
    "javascript": ["javascript", "java script", "js"],
    "sql": ["sql"],
    "mysql": ["mysql"],
    "postgresql": ["postgresql", "postgres"],
    "mongodb": ["mongodb", "mongo"],
    "django": ["django"],
    "flask": ["flask"],
    "fastapi": ["fastapi"],
    "react": ["react", "reactjs", "react.js"],
    "html": ["html", "html5"],
    "css": ["css", "css3"],
    "git": ["git", "github"],
    "rest api": ["rest api", "rest apis", "restful", "rest"],
    "docker": ["docker"],
    "aws": ["aws", "amazon web services"],
    "oop": ["oop", "oops", "object oriented", "object-oriented"],
    "machine learning": ["machine learning", "ml"],
    "pandas": ["pandas"],
    "numpy": ["numpy"],
}


def _contains(text: str, variant: str) -> bool:
    """Whole-word match, so 'java' doesn't match inside 'javascript'."""
    pattern = r"(?<![a-z0-9])" + re.escape(variant) + r"(?![a-z0-9])"
    return re.search(pattern, text) is not None

def find_skills(text: str) -> set:
    """Return the set of canonical skills mentioned in the text."""
    text = text.lower()
    text = re.sub(r"java\s+script", "javascript", text)  # stop 'java' matching inside it
    return {
        skill
        for skill, variants in SKILL_VOCAB.items()
        if any(_contains(text, v) for v in variants)
    }


def match_resume_to_job(resume_text: str, job_text: str) -> dict:
    resume_skills = find_skills(resume_text)
    job_skills = find_skills(job_text)
    matched = resume_skills & job_skills
    missing = job_skills - resume_skills
    pct = round(100 * len(matched) / len(job_skills), 1) if job_skills else 0.0
    return {
        "job_skills": sorted(job_skills),
        "matched": sorted(matched),
        "missing": sorted(missing),
        "match_percent": pct,
    }
