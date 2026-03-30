"""Generate threshold and calibration report for student model artifacts."""

from __future__ import annotations

import json
import pickle
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List

import numpy as np
import pandas as pd
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    precision_recall_fscore_support,
    roc_auc_score,
)


@dataclass
class ThresholdMetrics:
    threshold: float
    approve_rate: float
    precision_approve: float
    recall_approve: float
    f1_approve: float
    bad_approve_rate: float


def _project_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent


def _artifact_dir() -> Path:
    return _project_root() / "output" / "alternative_model"


def _add_missing_phase1_features(df: pd.DataFrame) -> pd.DataFrame:
    """Backfill engineered features when test artifact has legacy columns."""
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


def _compute_threshold_metrics(prob_default: np.ndarray, y_default: np.ndarray, threshold: float) -> ThresholdMetrics:
    # approved means likely non-default
    y_good = (y_default == 0).astype(int)
    approved = (prob_default < threshold).astype(int)

    precision, recall, f1, _ = precision_recall_fscore_support(
        y_good,
        approved,
        average="binary",
        zero_division=0,
    )
    approve_rate = float(np.mean(approved))
    bad_approve_rate = 1.0 - float(precision)

    return ThresholdMetrics(
        threshold=float(threshold),
        approve_rate=approve_rate,
        precision_approve=float(precision),
        recall_approve=float(recall),
        f1_approve=float(f1),
        bad_approve_rate=float(bad_approve_rate),
    )


def _recommend_threshold(rows: List[ThresholdMetrics], max_bad_approve_rate: float = 0.25) -> ThresholdMetrics:
    constrained = [r for r in rows if r.bad_approve_rate <= max_bad_approve_rate]
    if constrained:
        return max(constrained, key=lambda r: (r.recall_approve, r.f1_approve))
    return max(rows, key=lambda r: r.f1_approve)


def generate_report() -> Dict[str, object]:
    artifact_dir = _artifact_dir()

    x_test = pd.read_csv(artifact_dir / "X_test.csv")
    y_test = pd.read_csv(artifact_dir / "y_test.csv").iloc[:, 0].to_numpy()

    with open(artifact_dir / "best_model_phase1.pkl", "rb") as f:
        model = pickle.load(f)

    with open(artifact_dir / "best_threshold_phase1.pkl", "rb") as f:
        current_threshold = float(pickle.load(f))

    x_test = _add_missing_phase1_features(x_test)
    model_features = list(model.get_booster().feature_names or [])
    x_test = x_test[model_features]

    prob_default = model.predict_proba(x_test)[:, 1]

    auc_default = float(roc_auc_score(y_test, prob_default))
    ap_default = float(average_precision_score(y_test, prob_default))
    brier = float(brier_score_loss(y_test, prob_default))

    thresholds = np.linspace(0.10, 0.80, 71)
    rows = [_compute_threshold_metrics(prob_default, y_test, t) for t in thresholds]
    recommended = _recommend_threshold(rows)

    current = _compute_threshold_metrics(prob_default, y_test, current_threshold)

    report = {
        "model": "student_xgboost_phase1",
        "dataset": "output/alternative_model/X_test.csv",
        "rows": int(len(y_test)),
        "base_metrics": {
            "auc_default": auc_default,
            "average_precision_default": ap_default,
            "brier_score": brier,
        },
        "policy": {
            "max_bad_approve_rate": 0.25,
            "selection_rule": "max_recall_under_bad_approve_cap_else_max_f1",
        },
        "current_threshold": asdict(current),
        "recommended_threshold": asdict(recommended),
        "top_candidates": [
            asdict(x)
            for x in sorted(rows, key=lambda r: (r.recall_approve, r.f1_approve), reverse=True)[:5]
        ],
    }

    output_path = artifact_dir / "threshold_selection_report.json"
    output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


if __name__ == "__main__":
    result = generate_report()
    print(json.dumps(result["recommended_threshold"], indent=2))
