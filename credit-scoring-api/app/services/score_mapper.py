"""
Score Mapper Service

Two independent, non-conflicting score mappers:

1. probability_to_credit_score      — Regular loan model (LightGBM)
   Scale: 300–850  |  Formula: linear  |  Used by: /calculate-limit, /apply

2. student_probability_to_credit_score — Student loan model (XGBoost Phase-1)
   Scale: 600–850  |  Formula: non-linear (power)  |  Used by: /student/calculate-limit

Keeping them separate prevents any calibration change on one model
from accidentally affecting the other.
"""


def probability_to_credit_score(probability: float) -> int:
    """
    Regular loan mapper: prob (0–1) → credit score (300–850). STABLE — do not modify.

    Linear formula so the LightGBM output maps cleanly to the full 300–850 scale.

    | Default Probability | Credit Score |
    |---------------------|--------------|
    | 0.00                | 850          |
    | 0.25                | 712          |
    | 0.50                | 575          |
    | 0.75                | 437          |
    | 1.00                | 300          |
    """
    raw = 850 - (probability * 550)
    return int(round(max(300, min(850, raw))))


def student_probability_to_credit_score(probability: float) -> int:
    """
    Student loan mapper: prob (0–1) → credit score (600–850). STABLE — do not modify.

    Non-linear (power curve) on a tighter 600–850 scale because student
    applicants are a narrower, lower-exposure risk band than regular borrowers.

    Formula: 850 - int((prob ** 0.6) * 250)  →  clamped to [600, 850]

    | Default Probability | Credit Score |
    |---------------------|--------------|
    | 0.00                | 850          |
    | 0.20                | 716          |
    | 0.50                | 685          |
    | 0.80                | 641          |
    | 1.00                | 600          |
    """
    score = 850 - int((probability ** 0.6) * 250)
    return max(600, min(850, score))


def credit_score_to_rating(credit_score: int) -> str:
    """
    Map credit score to a human-readable rating label.

    Args:
        credit_score: Credit score (300–850)

    Returns:
        Rating string
    """
    if credit_score >= 780:
        return "Excellent"
    elif credit_score >= 740:
        return "Very Good"
    elif credit_score >= 700:
        return "Good"
    elif credit_score >= 650:
        return "Fair"
    elif credit_score >= 600:
        return "Poor"
    else:
        return "Very Poor"
