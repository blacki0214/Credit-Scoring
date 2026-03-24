"""
Student Prediction Service

Loads the Phase 1 XGBoost alternative model and engineers
the 25 features expected by that model from a StudentLoanRequest.

Model path (local dev): output/alternative_model/best_model_phase1.pkl
Threshold:              output/alternative_model/best_threshold_phase1.pkl
"""
import pickle
import logging
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Tuple
from app.services.score_mapper import student_probability_to_credit_score

logger = logging.getLogger(__name__)

# ── Feature constants ────────────────────────────────────────────────────────
MATURITY_MAP = {1: 0.2, 2: 0.4, 3: 0.6, 4: 0.8, 5: 0.9}

MAJOR_INCOME_MAP = {
    "technology": 0.9, "engineering": 0.85, "medicine": 0.9,
    "business": 0.75, "finance": 0.8, "law": 0.8,
    "education": 0.55, "arts": 0.45, "social_science": 0.5,
    "other": 0.6,
}

LIVING_MAP = {
    "dormitory": 0,     # lowest cost → lower financial stress
    "with_parents": 1,
    "renting": 2,       # highest cost → more pressure
}

# Default threshold if pkl not found
DEFAULT_THRESHOLD = 0.3623


class StudentPredictionService:
    """Predict default probability for student loan applicants."""

    def __init__(self):
        self._model = None
        self._threshold: float = DEFAULT_THRESHOLD
        self._load()

    # ── Loading ──────────────────────────────────────────────────────────────

    def _load(self):
        # __file__ = .../credit-scoring-api/app/services/student_prediction_service.py
        # parent x3 = credit-scoring-api/
        # parent x4 = project root (Credit-Scoring/)
        api_root    = Path(__file__).resolve().parent.parent.parent
        project_root = api_root.parent
        model_path     = project_root / "output" / "alternative_model" / "best_model_phase1.pkl"
        threshold_path = project_root / "output" / "alternative_model" / "best_threshold_phase1.pkl"

        if not model_path.exists():
            logger.warning(
                f"Student model not found at {model_path}. "
                "Endpoint will return 503 until model is available."
            )
            return

        with open(model_path, "rb") as f:
            self._model = pickle.load(f)
        logger.info(f"Student model loaded from {model_path}")

        if threshold_path.exists():
            with open(threshold_path, "rb") as f:
                self._threshold = float(pickle.load(f))
            logger.info(f"Student threshold loaded: {self._threshold:.4f}")
        else:
            logger.warning(f"Threshold file not found, using default {DEFAULT_THRESHOLD}")

    @property
    def is_ready(self) -> bool:
        return self._model is not None

    # ── Feature Engineering ──────────────────────────────────────────────────

    def _engineer(self, raw: dict) -> pd.DataFrame:
        """Build the 25-feature DataFrame from raw student request fields."""
        d = {}

        # User-supplied fields
        d["gpa_latest"]             = raw["gpa_latest"]
        d["academic_year"]          = raw["academic_year"]
        d["loan_amount"]            = raw["loan_amount"]
        d["has_buffer"]             = int(raw["has_buffer"])
        d["monthly_income"]         = raw.get("monthly_income", 0.0)

        # Derived: major income potential
        d["major_income_potential"] = MAJOR_INCOME_MAP.get(
            raw.get("major", "other"), 0.6
        )

        # Derived: living / support
        living_code = LIVING_MAP.get(raw.get("living_status", "dormitory"), 0)
        d["living_status"]          = living_code
        d["support_numeric"]        = max(0.1, raw.get("monthly_income", 0) / 5_000_000)

        # Derived: maturity score from year
        d["maturity_score"]         = MATURITY_MAP.get(raw["academic_year"], 0.4)

        # Derived: debt ratio (monthly expenses vs income)
        monthly_expenses = raw.get("monthly_expenses", 2_000_000)
        monthly_income   = max(raw.get("monthly_income", 1), 1)
        d["debt_ratio"]             = min(monthly_expenses / (monthly_income + monthly_expenses), 0.99)

        # Behavioral priors (neutral — updated after real data)
        d["behavior_risk_score"]    = 5.0
        d["behavior_volatility"]    = 0.3
        d["behavior_under_pressure"]= 5.0
        d["shock_vulnerability"]    = 0.5

        # Binary flags
        d["severe_behavior_flag"]   = 0
        d["thin_support_flag"]      = 1 if d["support_numeric"] < 0.3 else 0
        d["high_pressure_flag"]     = 1 if living_code == 2 else 0
        d["program_level"]          = 1 if raw.get("program_level", "undergraduate") == "postgraduate" else 0

        # Engineered interaction features (Phase 1)
        d["financial_stress_index"] = d["debt_ratio"] * d["behavior_volatility"]
        d["academic_resilience"]    = d["gpa_latest"] * d["support_numeric"]
        d["risk_compounding"]       = (
            d["severe_behavior_flag"] + d["thin_support_flag"] + d["high_pressure_flag"]
        )
        d["loan_to_maturity_ratio"] = d["loan_amount"] / (d["maturity_score"] + 0.1)

        return pd.DataFrame([d])

    # ── Prediction ───────────────────────────────────────────────────────────

    def predict(self, raw: dict) -> Tuple[float, str, int]:
        """
        Returns:
            (default_probability, risk_level, credit_score)
        """
        if self._model is None:
            raise RuntimeError("Student model is not loaded")

        model = self._model
        features = self._engineer(raw)
        prob = float(model.predict_proba(features)[0][1])

        if prob < 0.25:
            risk = "Low"
        elif prob < 0.45:
            risk = "Medium"
        elif prob < 0.65:
            risk = "High"
        else:
            risk = "Very High"

        # Use centralized student score mapper (score_mapper.py)
        score = student_probability_to_credit_score(prob)
        return prob, risk, score


# Singleton
student_prediction_service = StudentPredictionService()
