import logging
import re

from .skill_matcher import find_skills
from .semantic_matcher import match_requirements

DEFAULT_WEIGHTS = {
    "required_skills": 40,   # required skills present (keywords)
    "preferred_skills": 10,  # nice-to-have skills (keywords)
    "semantic": 20,          # requirements matched by meaning (embeddings)
    "evidence": 15,          # skills shown in projects/experience, not just listed
    "completeness": 15,      # expected sections present
}

PREFERRED_MARKERS = r"nice to have|good to have|preferred|bonus"
EXCLUDED_SECTIONS = {"header", "personal"}  # never scored or embedded


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


def _semantic(sections: dict, job_text: str) -> list:
    try:
        return match_requirements(sections, job_text)
    except Exception:
        logging.exception("Semantic matching failed; scoring without it")
        return []


def score_resume(sections: dict, job_text: str, weights: dict = None) -> dict:
    weights = weights or DEFAULT_WEIGHTS
    resume_text = "\n".join(v for k, v in sections.items() if k not in EXCLUDED_SECTIONS)
    resume_skills = find_skills(resume_text)
    proof_skills = find_skills(
        sections.get("experience", "") + "\n" + sections.get("projects", "")
    )

    required, preferred = split_job_requirements(job_text)
    matched_req = required & resume_skills
    matched_pref = preferred & resume_skills
    matches = _semantic(sections, job_text)

    # component -> ratio between 0 and 1, or None if it doesn't apply
    ratios = {
        "required_skills": len(matched_req) / len(required) if required else None,
        "preferred_skills": len(matched_pref) / len(preferred) if preferred else None,
        "semantic": sum(m["met"] for m in matches) / len(matches) if matches else None,
        "evidence": len(proof_skills & resume_skills) / len(resume_skills) if resume_skills else None,
        "completeness": _completeness(sections),
    }

    # Skip components that don't apply, and rescale the rest to 100.
    active = {k: r for k, r in ratios.items() if r is not None}
    total_weight = sum(weights.get(k, 0) for k in active)
    if total_weight == 0:
        score = 0.0
    else:
        score = sum(weights.get(k, 0) * r for k, r in active.items()) / total_weight * 100

    return {
        "score": round(score, 1),
        "breakdown": {k: round(r * 100, 1) for k, r in active.items()},
        "required_missing": sorted(required - resume_skills),
        "preferred_missing": sorted(preferred - resume_skills),
        "not_demonstrated": sorted(resume_skills - proof_skills),
        "semantic": [
            {
                "requirement": m["requirement"],
                "score": m["score"],
                "met": m["met"],
                "match_quality": m["match_quality"],
                "evidence": m["evidence"][:120],
                "evidence_section": m["evidence_section"],
            }
            for m in matches
        ],
    }