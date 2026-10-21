import re
from .skill_matcher import find_skills

DEFAULT_WEIGHTS = {
    "required_skills": 50,   # how many required skills are present
    "preferred_skills": 15,  # nice-to-have skills
    "evidence": 15,          # skills shown in projects/experience, not just listed
    "completeness": 20,      # expected sections present
}

PREFERRED_MARKERS = r"nice to have|good to have|preferred|bonus"


def split_job_requirements(job_text: str):
    """Text before a 'nice to have' marker is required; text after is preferred."""
    match = re.search(PREFERRED_MARKERS, job_text, flags=re.IGNORECASE)
    if not match:
        return find_skills(job_text), set()
    required = find_skills(job_text[:match.start()])
    preferred = find_skills(job_text[match.start():]) - required
    return required, preferred


def _completeness(sections: dict) -> float:
    checks = [
        "summary" in sections,
        "education" in sections,
        "skills" in sections,
        "experience" in sections or "projects" in sections,
    ]
    return sum(checks) / len(checks)


def score_resume(sections: dict, job_text: str, weights: dict = None) -> dict:
    weights = weights or DEFAULT_WEIGHTS
    resume_text = "\n".join(sections.values())
    resume_skills = find_skills(resume_text)
    proof_skills = find_skills(
        sections.get("experience", "") + "\n" + sections.get("projects", "")
    )

    required, preferred = split_job_requirements(job_text)
    matched_req = required & resume_skills
    matched_pref = preferred & resume_skills

    # component -> ratio between 0 and 1, or None if it doesn't apply
    ratios = {
        "required_skills": len(matched_req) / len(required) if required else None,
        "preferred_skills": len(matched_pref) / len(preferred) if preferred else None,
        "evidence": len(proof_skills & resume_skills) / len(resume_skills) if resume_skills else None,
        "completeness": _completeness(sections),
    }

    # Skip components that don't apply, and rescale the rest to 100.
    active = {k: r for k, r in ratios.items() if r is not None}
    total_weight = sum(weights[k] for k in active)
    score = sum(weights[k] * r for k, r in active.items()) / total_weight * 100

    return {
        "score": round(score, 1),
        "breakdown": {k: round(r * 100, 1) for k, r in active.items()},
        "required_missing": sorted(required - resume_skills),
        "preferred_missing": sorted(preferred - resume_skills),
        "not_demonstrated": sorted(resume_skills - proof_skills),
    }