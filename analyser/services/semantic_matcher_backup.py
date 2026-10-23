import re
from functools import lru_cache

# A starting guess, not a law of nature. We'll tune it on real data.
THRESHOLD = 0.45


@lru_cache(maxsize=1)
def _model():
    """Load the model once and reuse it. Loading takes seconds, so never do it per request."""
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer("all-MiniLM-L6-v2")


def _chunks(text: str, window: int = 1) -> list:
    """Split text into lines, optionally joining `window` consecutive lines.

    PDF text is hard-wrapped, so one bullet is often split over two lines.
    Joining neighbours keeps a sentence's meaning together.
    """
    lines = [re.sub(r"^[\-–•*\s]+", "", l).strip(" .") for l in re.split(r"[\n;]+|\.\s+", text)]
    lines = [l for l in lines if len(l.split()) >= 2]
    if not lines:
        return []
    if window == 1:
        return lines
    return [" ".join(lines[i:i + window]) for i in range(max(1, len(lines) - window + 1))]


def match_requirements(resume_text: str, job_text: str, threshold: float = THRESHOLD) -> list:
    """For each job requirement, find the most similar resume passage."""
    from sentence_transformers import util

    requirements = _chunks(job_text, window=1)
    evidence = _chunks(resume_text, window=2)
    if not requirements or not evidence:
        return []

    model = _model()
    req_emb = model.encode(requirements, convert_to_tensor=True)
    ev_emb = model.encode(evidence, convert_to_tensor=True)
    sims = util.cos_sim(req_emb, ev_emb)  # one row per requirement, one column per resume passage

    results = []
    for i, requirement in enumerate(requirements):
        j = int(sims[i].argmax())
        score = float(sims[i][j])
        results.append({
            "requirement": requirement,
            "score": round(score, 2),
            "met": score >= threshold,
            "evidence": evidence[j],
        })
    return results