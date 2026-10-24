"""Evaluate cosine-similarity cutoffs against the hand-labelled examples.

Run from the project root with the activated venv:
    python scripts/tune_semantic_threshold.py

These small examples are a learning aid, not a representative benchmark.
"""
import json
import os
from pathlib import Path

# Use the already-installed local model; calibration should not need network.
os.environ["HF_HUB_OFFLINE"] = "1"

from sentence_transformers import SentenceTransformer, util


ROOT = Path(__file__).resolve().parents[1]
PAIRS = json.loads((ROOT / "analyser/data/semantic_labels.json").read_text(encoding="utf-8"))


def main():
    model = SentenceTransformer("all-MiniLM-L6-v2")
    requirements = [row["requirement"] for row in PAIRS]
    lines = [row["resume_line"] for row in PAIRS]
    scores = util.cos_sim(
        model.encode(requirements, convert_to_tensor=True),
        model.encode(lines, convert_to_tensor=True),
    ).diagonal().tolist()
    labels = [row["match"] for row in PAIRS]

    print(f"{len(PAIRS)} labelled pairs ({sum(labels)} matches, {len(labels) - sum(labels)} non-matches)")
    print("threshold  accuracy  precision  recall")
    for step in range(30, 71, 5):
        threshold = step / 100
        predicted = [score >= threshold for score in scores]
        tp = sum(p and y for p, y in zip(predicted, labels))
        fp = sum(p and not y for p, y in zip(predicted, labels))
        fn = sum(not p and y for p, y in zip(predicted, labels))
        accuracy = sum(p == y for p, y in zip(predicted, labels)) / len(labels)
        precision = tp / (tp + fp) if tp + fp else 0
        recall = tp / (tp + fn) if tp + fn else 0
        print(f"   {threshold:.2f}       {accuracy:.0%}       {precision:.0%}       {recall:.0%}")


if __name__ == "__main__":
    main()
