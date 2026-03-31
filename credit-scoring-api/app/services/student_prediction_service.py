"""
Student Prediction Service

Loads the Phase 1 XGBoost alternative model and engineers
the 25 features expected by that model from a StudentLoanRequest.

Model path (local dev): output/alternative_model/best_model_phase1.pkl
Threshold:              output/alternative_model/best_threshold_phase1.pkl
"""
import pickle
import logging
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Any, Dict, List, Tuple
from app.services.score_mapper import student_probability_to_credit_score
from app.core.config import settings
from app.services.student_feature_contract import (
    LIVING_MAP,
    MAJOR_INCOME_MAP,
    MATURITY_MAP,
    STUDENT_MODEL_FEATURE_ORDER,
)

logger = logging.getLogger(__name__)

# Default threshold if pkl not found
DEFAULT_THRESHOLD = 0.3623


class StudentPredictionService:
    """Predict default probability for student loan applicants."""

    def __init__(self):
        self._model = None
        self._calibrator = None
        self._threshold: float = DEFAULT_THRESHOLD
        self._model_path: Path | None = None
        self._threshold_path: Path | None = None
        self._calibrator_path: Path | None = None
        self._load()

    # ── Loading ──────────────────────────────────────────────────────────────

    def _load(self):
        # __file__ = .../credit-scoring-api/app/services/student_prediction_service.py
        # parent x3 = credit-scoring-api/
        # parent x4 = project root (Credit-Scoring/)
        api_root = Path(__file__).resolve().parent.parent.parent
        project_root = api_root.parent

        model_candidates = [
            settings.STUDENT_MODEL_PATH,
            project_root / "output" / "alternative_model" / "best_model_phase1.pkl",
            api_root / "models" / "best_model_phase1.pkl",
        ]
        threshold_candidates = [
            settings.STUDENT_THRESHOLD_PATH,
            project_root / "output" / "alternative_model" / "best_threshold_phase1.pkl",
            api_root / "models" / "best_threshold_phase1.pkl",
        ]
        calibrator_candidates = [
            settings.STUDENT_CALIBRATOR_PATH,
            project_root / "output" / "alternative_model" / settings.STUDENT_CALIBRATOR_FILENAME,
            api_root / "models" / settings.STUDENT_CALIBRATOR_FILENAME,
        ]

        model_path = next((p for p in model_candidates if p.exists()), model_candidates[0])
        threshold_path = next((p for p in threshold_candidates if p.exists()), threshold_candidates[0])
        calibrator_path = next((p for p in calibrator_candidates if p.exists()), calibrator_candidates[0])
        self._model_path = model_path
        self._threshold_path = threshold_path
        self._calibrator_path = calibrator_path

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

        if settings.STUDENT_CALIBRATION_ENABLED and calibrator_path.exists():
            with open(calibrator_path, "rb") as f:
                self._calibrator = pickle.load(f)
            logger.info(f"Student calibrator loaded from {calibrator_path}")
        elif settings.STUDENT_CALIBRATION_ENABLED:
            logger.warning(
                "Student calibrator not found at %s. Using raw model probabilities.",
                calibrator_path,
            )

    def validate_runtime_assets(self, strict: bool = False) -> Dict[str, Any]:
        """Validate model artifacts and model-feature compatibility."""
        issues: List[str] = []
        warnings: List[str] = []

        if self._model_path is None or not self._model_path.exists():
            issues.append("student_model_artifact_missing")

        if self._threshold_path is None or not self._threshold_path.exists():
            warnings.append("student_threshold_artifact_missing_using_default")

        if settings.STUDENT_CALIBRATION_ENABLED:
            if self._calibrator_path is None or not self._calibrator_path.exists():
                warnings.append("student_calibrator_artifact_missing_using_raw_probability")
            elif self._calibrator is None:
                warnings.append("student_calibrator_not_loaded")

        if not (0.0 < float(self._threshold) < 1.0):
            issues.append("student_threshold_out_of_range")

        if self._model is None:
            issues.append("student_model_not_loaded")
        else:
            try:
                feature_names = list(self._model.get_booster().feature_names or [])
                if feature_names and feature_names != STUDENT_MODEL_FEATURE_ORDER:
                    issues.append("student_model_feature_mismatch")
            except Exception:
                warnings.append("student_model_feature_names_unavailable")

        status = {
            "ok": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "model_path": str(self._model_path) if self._model_path else "",
            "threshold_path": str(self._threshold_path) if self._threshold_path else "",
            "calibrator_path": str(self._calibrator_path) if self._calibrator_path else "",
            "threshold": float(self._threshold),
            "model_loaded": self._model is not None,
            "calibrator_loaded": self._calibrator is not None,
        }

        if strict and issues:
            raise RuntimeError(
                "Student model preflight failed: " + ", ".join(issues)
            )

        return status

    @property
    def is_ready(self) -> bool:
        return self._model is not None

    @property
    def threshold(self) -> float:
        return self._threshold

    def classify_decision_band(self, probability: float) -> Tuple[str, bool, bool]:
        """Classify probability into decision policy bands.

        Returns:
            (decision_band, approved, manual_review)
        """
        margin = max(0.0, min(settings.STUDENT_MANUAL_REVIEW_MARGIN, 0.25))
        lower = max(0.0, self._threshold - margin)
        upper = min(1.0, self._threshold + margin)

        if probability < lower:
            return "auto_approve", True, False
        if probability <= upper:
            return "manual_review", False, True
        return "auto_reject", False, False

    def _calibrate_probability(self, probability: float) -> float:
        """Apply optional probability calibration artifact."""
        if self._calibrator is None:
            return probability

        try:
            calibrated = self._calibrator.predict(np.array([probability], dtype=float))[0]
        except Exception as exc:
            logger.warning("Student probability calibration failed: %s", exc)
            return probability

        return float(max(0.0, min(1.0, calibrated)))

    # ── Feature Engineering ──────────────────────────────────────────────────

    def _engineer(self, raw: dict) -> pd.DataFrame:
        """Build the 25-feature DataFrame from raw student request fields."""
        d = {}

        # User-supplied fields
        d["age"]                    = int(raw["age"])
        d["program_level"]          = 1 if raw.get("program_level", "undergraduate") == "postgraduate" else 0
        d["living_status"]          = LIVING_MAP.get(raw.get("living_status", "dormitory"), 0)
        d["gpa_latest"]             = raw["gpa_latest"]
        d["academic_year"]          = raw["academic_year"]
        loan_amount = raw.get("loan_amount")
        if loan_amount is None:
            loan_amount = settings.STUDENT_SCORING_REFERENCE_LOAN_AMOUNT
        d["loan_amount"]            = float(loan_amount)
        d["has_buffer"]             = int(raw["has_buffer"])

        # Derived: major income potential
        d["major_income_potential"] = MAJOR_INCOME_MAP.get(
            raw.get("major", "other"), 0.6
        )

        # Normalize optional financial inputs to avoid None arithmetic.
        raw_monthly_income = raw.get("monthly_income")
        monthly_income_val = (
            float(raw_monthly_income) if raw_monthly_income is not None else 0.0
        )
        raw_monthly_expenses = raw.get("monthly_expenses")
        monthly_expenses_val = (
            float(raw_monthly_expenses)
            if raw_monthly_expenses is not None
            else 2_000_000.0
        )

        # Derived: living / support
        living_code = d["living_status"]
        d["support_numeric"]        = max(0.1, monthly_income_val / 5_000_000)

        # Derived: maturity score from year
        d["maturity_score"]         = MATURITY_MAP.get(raw["academic_year"], 0.4)

        # Derived: debt ratio (monthly expenses vs income)
        monthly_expenses = max(monthly_expenses_val, 0.0)
        monthly_income   = max(monthly_income_val, 1.0)
        d["debt_ratio"]             = min(monthly_expenses / (monthly_income + monthly_expenses), 0.99)

        # Behavioral signals inferred from current profile.
        # Keep values in conservative ranges close to training scale.
        support_sources = raw.get("support_sources") or []
        if not isinstance(support_sources, list):
            support_sources = []
        support_count = len([s for s in support_sources if isinstance(s, str) and s.strip()])
        has_family_support = any(
            isinstance(s, str) and s.strip().lower() == "family"
            for s in support_sources
        )

        gpa = float(d["gpa_latest"])
        academic_year = int(d["academic_year"])
        has_buffer = bool(d["has_buffer"])

        # Allow negative values: GPA > 3.2 or year > 3 actively reduces risk score
        gpa_signal  = min(1.0, (3.2 - gpa) / 2.2)                    # [-0.36 (GPA 4.0) … +1.0 (GPA 0)]
        year_signal = min(1.0, (3.0 - float(academic_year)) / 2.0)   # [-1.0 (yr 5) … +1.0 (yr 1)]
        support_gap = max(0.0, 1.0 - min(1.0, d["support_numeric"]))
        expense_pressure = min(1.0, monthly_expenses / max(monthly_income + monthly_expenses, 1.0))
        living_risk = 1.0 if living_code == 2 else (0.35 if living_code == 1 else 0.2)

        behavior_risk_score = (
            4.6
            + 1.6 * expense_pressure
            + 1.0 * gpa_signal
            + 0.8 * support_gap
            + 0.6 * year_signal
            + 0.5 * living_risk
            - 0.8 * (1.0 if has_buffer else 0.0)
            - 0.25 * min(2, support_count)
            - (0.4 if has_family_support else 0.0)
        )
        d["behavior_risk_score"] = float(max(2.5, min(8.5, behavior_risk_score)))

        volatility = (
            0.22
            + 0.18 * expense_pressure
            + 0.10 * support_gap
            + 0.10 * year_signal
            + (0.05 if support_count == 0 else 0.0)
            - (0.04 if has_buffer else 0.0)
        )
        d["behavior_volatility"] = float(max(0.12, min(0.65, volatility)))

        pressure = (
            4.6
            + 1.5 * expense_pressure
            + 0.8 * support_gap
            + (0.6 if living_code == 2 else 0.0)
            + (0.5 if not has_buffer else 0.0)
            + 0.4 * year_signal
        )
        d["behavior_under_pressure"] = float(max(2.0, min(8.5, pressure)))

        shock_vulnerability = (
            0.38
            + 0.28 * support_gap
            + 0.20 * expense_pressure
            + (0.12 if not has_buffer else -0.08)
            + (0.08 if support_count == 0 else 0.0)
        )
        d["shock_vulnerability"] = float(max(0.05, min(0.95, shock_vulnerability)))

        # Binary flags
        d["severe_behavior_flag"]   = int(
            d["debt_ratio"] > 0.75 and (not has_buffer) and d["support_numeric"] < 0.5
        )
        d["thin_support_flag"]      = 1 if d["support_numeric"] < 0.3 else 0
        d["high_pressure_flag"]     = 1 if living_code == 2 else 0

        # Interaction features expected by training schema
        d["debt_x_behavior"]        = d["debt_ratio"] * d["behavior_risk_score"]
        d["debt_x_support"]         = d["debt_ratio"] * d["support_numeric"]
        d["debt_x_living"]          = d["debt_ratio"] * living_code

        # Engineered interaction features (Phase 1)
        d["financial_stress_index"] = d["debt_ratio"] * d["behavior_volatility"]
        d["academic_resilience"]    = d["gpa_latest"] * d["support_numeric"]
        d["risk_compounding"]       = (
            d["severe_behavior_flag"] + d["thin_support_flag"] + d["high_pressure_flag"]
        )
        d["loan_to_maturity_ratio"] = d["loan_amount"] / (d["maturity_score"] + 0.1)

        df = pd.DataFrame([d])
        return df[STUDENT_MODEL_FEATURE_ORDER]

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
        raw_prob = float(model.predict_proba(features)[0][1])
        prob = self._calibrate_probability(raw_prob)

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
