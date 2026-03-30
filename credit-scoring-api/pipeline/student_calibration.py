"""Fit and persist isotonic calibration for student model probabilities."""

from __future__ import annotations

import json
import pickle
from pathlib import Path
from typing import Dict

import numpy as np
import pandas as pd
from sklearn.isotonic import IsotonicRegression
from sklearn.metrics import brier_score_loss, roc_auc_score


def _project_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent


def _artifact_dir() -> Path:
    return _project_root() / "output" / "alternative_model"


def _add_missing_phase1_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    if "financial_stress_index" not in out.columns:
        out["financial_stress_index"] = out["debt_ratio"] * out["behavior_volatility"]
    if "academic_resilience" not in out.columns:
        out["academic_resilience"] = out["gpa_latest"] * out["support_numeric"]
    if "risk_compounding" not in out.columns:
        out["risk_compounding"] = (
            out["severe_behavior_flag"] + out["thin_support_flag"] + out["high_pressure_flag"]
        )
    if "loan_to_maturity_ratio" not in out.columns:
        out["loan_to_maturity_ratio"] = out["loan_amount"] / (out["maturity_score"] + 0.1)
    return out


def _load_xy(split: str, model_feature_names: list[str]) -> tuple[pd.DataFrame, np.ndarray]:
    artifact_dir = _artifact_dir()
    x = pd.read_csv(artifact_dir / f"X_{split}.csv")
    y = pd.read_csv(artifact_dir / f"y_{split}.csv").iloc[:, 0].to_numpy()
    x = _add_missing_phase1_features(x)
    x = x[model_feature_names]
    return x, y


def _metrics(y: np.ndarray, p: np.ndarray) -> Dict[str, float]:
    return {
        "auc_default": float(roc_auc_score(y, p)),
        "brier": float(brier_score_loss(y, p)),
        "prob_mean": float(np.mean(p)),
        "prob_p50": float(np.quantile(p, 0.50)),
        "prob_p95": float(np.quantile(p, 0.95)),
    }


def fit_isotonic_calibrator() -> Dict[str, object]:
    artifact_dir = _artifact_dir()

    with open(artifact_dir / "best_model_phase1.pkl", "rb") as f:
        model = pickle.load(f)

    feature_names = list(model.get_booster().feature_names or [])

    x_val, y_val = _load_xy("val", feature_names)
    x_test, y_test = _load_xy("test", feature_names)

    p_val_raw = model.predict_proba(x_val)[:, 1]
    p_test_raw = model.predict_proba(x_test)[:, 1]

    calibrator = IsotonicRegression(out_of_bounds="clip")
    calibrator.fit(p_val_raw, y_val)

    p_test_cal = calibrator.predict(p_test_raw)

    with open(artifact_dir / "student_calibrator_isotonic.pkl", "wb") as f:
        pickle.dump(calibrator, f)

    report = {
        "calibrator": "isotonic",
        "fit_split": "val",
        "eval_split": "test",
        "raw": _metrics(y_test, p_test_raw),
        "calibrated": _metrics(y_test, p_test_cal),
        "delta": {
            "brier_improvement": float(
                _metrics(y_test, p_test_raw)["brier"] - _metrics(y_test, p_test_cal)["brier"]
            )
        },
        "output_calibrator": str(artifact_dir / "student_calibrator_isotonic.pkl"),
    }

    report_path = artifact_dir / "student_calibration_report.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


if __name__ == "__main__":
    result = fit_isotonic_calibrator()
    print(json.dumps(result, indent=2))
