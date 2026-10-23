import re
from functools import lru_cache

from .section_parser import SECTION_ALIASES

# Starting values, to be tuned on labelled examples.
THRESHOLD = 0.45
STRONG_THRESHOLD = 0.60

# Sections whose text must never be embedded.
EXCLUDED_SECTIONS = {"header", "personal", "interests"}

_HEADINGS = {a for aliases in SECTION_ALIASES.values() for a in aliases}


@lru_cache(maxsize=1)
def _model():
    """Load the embedding model once per server process."""
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer("all-MiniLM-L6-v2")


def _clean_line(line: str) -> str:
    line = re.sub(r"^[\s\-*\u2022\u25aa\u2013\u2014]+", "", line)
    return re.sub(r"\s+", " ", line).strip(" .")


def _lines(text: str) -> list:
    """Clean lines, drop headings and one-word fragments, split run-on sentences."""
    out = []
    for raw in text.splitlines():
        line = _clean_line(raw)
        if len(line.split()) < 2:
            continue
        if re.sub(r"[^a-z ]", "", line.lower()).strip() in _HEADINGS:
            continue
        out.extend(s.strip() for s in re.split(r"(?<=[.!?])\s+", line) if len(s.split()) >= 2)
    return out


def _passages(text: str) -> list:
    """Single lines plus adjacent pairs, so wrapped bullets stay together."""
    lines = _lines(text)
    pairs = [f"{lines[i]} {lines[i + 1]}" for i in range(len(lines) - 1)]
    return lines + pairs


def match_requirements(sections: dict, job_text: str, threshold: float = THRESHOLD) -> list:
    """For each job requirement, find the closest passage in the resume.

    Similarity measures textual relevance, not proof of a skill.
    """
    from sentence_transformers import util

    requirements = _lines(job_text)
    evidence = [
        (name, passage)
        for name, text in sections.items()
        if name not in EXCLUDED_SECTIONS
        for passage in _passages(text)
    ]
    if not requirements or not evidence:
        return []

    model = _model()
    req_emb = model.encode(requirements, convert_to_tensor=True)
    ev_emb = model.encode([p for _, p in evidence], convert_to_tensor=True)
    sims = util.cos_sim(req_emb, ev_emb)

    strong = max(STRONG_THRESHOLD, threshold)
    results = []
    for i, requirement in enumerate(requirements):
        j = int(sims[i].argmax())
        score = float(sims[i][j])
        met = score >= threshold
        results.append({
            "requirement": requirement,
            "score": round(score, 2),
            "met": met,
            "match_quality": "strong" if score >= strong else "possible" if met else "weak",
            "evidence": evidence[j][1] if met else "",
            "evidence_section": evidence[j][0] if met else "",
        })
    return results