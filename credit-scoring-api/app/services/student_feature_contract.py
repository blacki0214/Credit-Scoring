"""Shared feature contract for student model training and serving."""

from __future__ import annotations

from typing import List

# Expected model feature order from training artifact.
STUDENT_MODEL_FEATURE_ORDER: List[str] = [
    "age",
    "program_level",
    "living_status",
    "academic_year",
    "maturity_score",
    "gpa_latest",
    "major_income_potential",
    "loan_amount",
    "debt_ratio",
    "high_pressure_flag",
    "behavior_risk_score",
    "behavior_volatility",
    "severe_behavior_flag",
    "support_numeric",
    "has_buffer",
    "thin_support_flag",
    "debt_x_behavior",
    "debt_x_support",
    "debt_x_living",
    "behavior_under_pressure",
    "shock_vulnerability",
    "financial_stress_index",
    "academic_resilience",
    "risk_compounding",
    "loan_to_maturity_ratio",
]

# Feature constants
MATURITY_MAP = {1: 0.2, 2: 0.4, 3: 0.6, 4: 0.8, 5: 0.9}

MAJOR_INCOME_MAP = {
    "technology": 0.9,
    "engineering": 0.85,
    "medicine": 0.9,
    "business": 0.75,
    "finance": 0.8,
    "law": 0.8,
    "education": 0.55,
    "arts": 0.45,
    "social_science": 0.5,
    "other": 0.6,
}

LIVING_MAP = {
    "dormitory": 0,
    "with_parents": 1,
    "renting": 2,
}
