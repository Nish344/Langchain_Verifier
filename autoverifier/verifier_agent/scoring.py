# verifier_agent/scoring.py
from typing import List

def compute_trust_score(cred: float, stance: str, fallacies: List[str], content_len: int) -> float:
    """
    Deterministic scoring:
      - base = cred (0..1)
      - stance bonus: +0.05 if assertion, -0.05 if speculation/question
      - fallacy penalty: -0.10 per fallacy (cap 2)
      - length bonus: +0.05 if content >= 600 chars
    Returns float in [0,1], rounded to 3 decimals.
    """
    base = float(max(0.0, min(1.0, cred)))
    stance_bonus = 0.05 if stance == "assertion" else (-0.05 if stance in {"speculation", "question"} else 0.0)
    fallacy_penalty = -0.10 * min(len(fallacies or []), 2)
    length_bonus = 0.05 if content_len >= 600 else 0.0
    score = base + stance_bonus + fallacy_penalty + length_bonus
    score = max(0.0, min(1.0, round(score, 3)))
    return score
