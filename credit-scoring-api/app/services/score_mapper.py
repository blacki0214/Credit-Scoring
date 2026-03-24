"""
Score Mapper Service

Converts the ML model's default probability output into a
standardized credit score on the 300–850 scale.

Formula:  credit_score = round(850 - probability * 550)

| Default Probability | Credit Score | Meaning       |
|---------------------|--------------|---------------|
| 0.00                | 850          | Perfect       |
| 0.05                | 822          | Excellent     |
| 0.25                | 712          | Good          |
| 0.50                | 575          | Fair          |
| 0.75                | 437          | Poor          |
| 1.00                | 300          | Very Poor     |
"""


def probability_to_credit_score(probability: float) -> int:
    """
    Map default probability (0.0–1.0) → credit score (300–850).

    Linear mapping: lower probability → higher score.

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
