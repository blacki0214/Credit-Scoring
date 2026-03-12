import os
import pickle
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
from sklearn.metrics import (
    average_precision_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
)

BASE_DIR = os.path.join(os.path.dirname(__file__), "..")
ARTIFACT_DIR = os.path.join(BASE_DIR, "output", "alternative_model")

MODELS = {
    "normal_xgboost": {
        "model": os.path.join(ARTIFACT_DIR, "best_model_xgboost.pkl"),
        "features": os.path.join(ARTIFACT_DIR, "feature_cols.pkl"),
    },
    "user_friendly_xgboost": {
        "model": os.path.join(ARTIFACT_DIR, "best_model_user_friendly_xgboost.pkl"),
        "features": os.path.join(ARTIFACT_DIR, "user_friendly_feature_cols.pkl"),
    },
}

X_FILES = {
    "X_test": os.path.join(ARTIFACT_DIR, "X_test.csv"),
    "X_test_scaled": os.path.join(ARTIFACT_DIR, "X_test_scaled.csv"),
}
Y_FILE = os.path.join(ARTIFACT_DIR, "y_test.csv")
REPORT_FILE = os.path.join(ARTIFACT_DIR, "model_comparison_detailed.csv")


def _load_pickle(path: str):
    with open(path, "rb") as f:
        return pickle.load(f)


def _load_y(path: str) -> np.ndarray:
    y_df = pd.read_csv(path)
    if y_df.shape[1] == 1:
        y = y_df.iloc[:, 0].values
    elif "default" in y_df.columns:
        y = y_df["default"].values
    else:
        y = y_df.iloc[:, -1].values
    return y.astype(int)


def _load_x_candidates() -> Dict[str, pd.DataFrame]:
    candidates: Dict[str, pd.DataFrame] = {}
    for name, path in X_FILES.items():
        if os.path.exists(path):
            candidates[name] = pd.read_csv(path)
    return candidates


def _add_user_friendly_engineered_features(x_df: pd.DataFrame) -> pd.DataFrame:
    enriched = x_df.copy()

    if (
        "loan_to_maturity_ratio" not in enriched.columns
        and "loan_amount" in enriched.columns
        and "maturity_score" in enriched.columns
    ):
        enriched["loan_to_maturity_ratio"] = enriched["loan_amount"] / (enriched["maturity_score"] + 0.1)

    if (
        "academic_maturity" not in enriched.columns
        and "academic_year" in enriched.columns
        and "maturity_score" in enriched.columns
    ):
        enriched["academic_maturity"] = enriched["academic_year"] * enriched["maturity_score"]

    if (
        "gpa_x_maturity" not in enriched.columns
        and "gpa_latest" in enriched.columns
        and "maturity_score" in enriched.columns
    ):
        enriched["gpa_x_maturity"] = enriched["gpa_latest"] * enriched["maturity_score"]

    if "gpa_gap_from_4" not in enriched.columns and "gpa_latest" in enriched.columns:
        enriched["gpa_gap_from_4"] = 4.0 - enriched["gpa_latest"]

    if (
        "living_x_income_potential" not in enriched.columns
        and "living_status" in enriched.columns
        and "major_income_potential" in enriched.columns
    ):
        enriched["living_x_income_potential"] = (
            enriched["living_status"] * enriched["major_income_potential"]
        )

    if (
        "loan_x_income_potential" not in enriched.columns
        and "loan_amount" in enriched.columns
        and "major_income_potential" in enriched.columns
    ):
        enriched["loan_x_income_potential"] = (
            enriched["loan_amount"] * enriched["major_income_potential"]
        )

    return enriched


def _select_feature_matrix(
    feature_cols: List[str], x_candidates: Dict[str, pd.DataFrame]
) -> Tuple[pd.DataFrame, str]:
    for name, x_df in x_candidates.items():
        missing = [c for c in feature_cols if c not in x_df.columns]
        if not missing:
            return x_df[feature_cols], name

        # Try reconstructing user-friendly engineered features from raw columns.
        enriched = _add_user_friendly_engineered_features(x_df)
        missing_after_enrich = [c for c in feature_cols if c not in enriched.columns]
        if not missing_after_enrich:
            return enriched[feature_cols], f"{name} (+derived)"

    missing_report = {
        name: [c for c in feature_cols if c not in x_df.columns][:10]
        for name, x_df in x_candidates.items()
    }
    raise ValueError(
        "Could not match feature columns to available X_test files. "
        f"Missing examples: {missing_report}"
    )


def _best_f1_threshold(y_true: np.ndarray, y_proba: np.ndarray) -> float:
    precision, recall, thresholds = precision_recall_curve(y_true, y_proba)

    if len(thresholds) == 0:
        return 0.5

    # precision/recall have one extra element compared to thresholds.
    f1_values = 2 * precision[:-1] * recall[:-1] / (precision[:-1] + recall[:-1] + 1e-12)
    best_idx = int(np.argmax(f1_values))
    return float(thresholds[best_idx])


def _threshold_metrics(y_true: np.ndarray, y_proba: np.ndarray, threshold: float) -> Dict[str, float]:
    y_pred = (y_proba >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()

    approved_mask = y_pred == 0
    approval_rate = float(np.mean(approved_mask))
    bad_rate_approved = float(np.mean(y_true[approved_mask])) if np.any(approved_mask) else np.nan

    return {
        "threshold": float(threshold),
        "f1": float(f1_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "tn": int(tn),
        "fp": int(fp),
        "fn": int(fn),
        "tp": int(tp),
        "approval_rate": approval_rate,
        "bad_rate_approved": bad_rate_approved,
    }


def evaluate_model(name: str, model_path: str, feature_path: str, y_true: np.ndarray, x_candidates: Dict[str, pd.DataFrame]) -> Dict[str, float]:
    model = _load_pickle(model_path)
    feature_cols = _load_pickle(feature_path)

    x_eval, source_name = _select_feature_matrix(feature_cols, x_candidates)
    y_proba = model.predict_proba(x_eval)[:, 1]

    best_threshold = _best_f1_threshold(y_true, y_proba)
    m_05 = _threshold_metrics(y_true, y_proba, 0.5)
    m_best = _threshold_metrics(y_true, y_proba, best_threshold)

    result = {
        "model": name,
        "x_source": source_name,
        "n_features": len(feature_cols),
        "roc_auc": float(roc_auc_score(y_true, y_proba)),
        "pr_auc": float(average_precision_score(y_true, y_proba)),
        "brier": float(brier_score_loss(y_true, y_proba)),
        "proba_mean": float(np.mean(y_proba)),
        "proba_std": float(np.std(y_proba)),
        "f1_at_0.5": m_05["f1"],
        "approval_at_0.5": m_05["approval_rate"],
        "bad_rate_approved_at_0.5": m_05["bad_rate_approved"],
        "best_threshold_f1": m_best["threshold"],
        "best_f1": m_best["f1"],
        "approval_at_best_f1": m_best["approval_rate"],
        "bad_rate_approved_at_best_f1": m_best["bad_rate_approved"],
    }
    return result


def _pct(x: float) -> str:
    if pd.isna(x):
        return "nan"
    return f"{x * 100:.2f}%"


def _print_easy_summary(result_df: pd.DataFrame) -> None:
    rank_df = result_df.sort_values(by=["roc_auc", "pr_auc"], ascending=False).reset_index(drop=True)
    winner = rank_df.iloc[0]

    print("\n=== Quick Read ===")
    print(f"Best overall model: {winner['model']}")
    print(
        f"Why: ROC-AUC={winner['roc_auc']:.4f}, PR-AUC={winner['pr_auc']:.4f}, "
        f"Brier={winner['brier']:.4f} (lower is better)"
    )

    if len(rank_df) >= 2:
        runner_up = rank_df.iloc[1]
        print(
            f"Gap vs {runner_up['model']}: "
            f"ROC-AUC {winner['roc_auc'] - runner_up['roc_auc']:+.4f}, "
            f"PR-AUC {winner['pr_auc'] - runner_up['pr_auc']:+.4f}, "
            f"Brier {winner['brier'] - runner_up['brier']:+.4f}"
        )

    summary_cols = [
        "model",
        "n_features",
        "roc_auc",
        "pr_auc",
        "brier",
        "f1_at_0.5",
        "approval_at_0.5",
        "bad_rate_approved_at_0.5",
        "best_threshold_f1",
        "best_f1",
    ]
    compact = rank_df[summary_cols].copy()
    compact = compact.rename(
        columns={
            "model": "model",
            "n_features": "features",
            "roc_auc": "roc_auc",
            "pr_auc": "pr_auc",
            "brier": "brier",
            "f1_at_0.5": "f1@0.5",
            "approval_at_0.5": "approval@0.5",
            "bad_rate_approved_at_0.5": "bad_rate_approved@0.5",
            "best_threshold_f1": "best_thr_f1",
            "best_f1": "best_f1",
        }
    )

    for col in ["roc_auc", "pr_auc", "brier", "f1@0.5", "best_thr_f1", "best_f1"]:
        compact[col] = compact[col].map(lambda v: f"{v:.4f}")
    for col in ["approval@0.5", "bad_rate_approved@0.5"]:
        compact[col] = compact[col].map(_pct)

    with pd.option_context("display.max_columns", None, "display.width", 200):
        print(compact.to_string(index=False))


def main() -> None:
    if not os.path.exists(Y_FILE):
        raise FileNotFoundError(f"Missing y_test file: {Y_FILE}")

    x_candidates = _load_x_candidates()
    if not x_candidates:
        raise FileNotFoundError("No X_test files found in output/alternative_model")

    y_true = _load_y(Y_FILE)

    rows = []
    for model_name, paths in MODELS.items():
        if not os.path.exists(paths["model"]):
            print(f"Skipping {model_name}: missing model file")
            continue
        if not os.path.exists(paths["features"]):
            print(f"Skipping {model_name}: missing feature list")
            continue

        try:
            rows.append(
                evaluate_model(
                    model_name,
                    paths["model"],
                    paths["features"],
                    y_true,
                    x_candidates,
                )
            )
        except Exception as exc:
            print(f"Skipping {model_name}: {exc}")

    if not rows:
        raise RuntimeError("No models could be evaluated.")

    result_df = pd.DataFrame(rows)

    float_cols = [
        "roc_auc",
        "pr_auc",
        "brier",
        "proba_mean",
        "proba_std",
        "f1_at_0.5",
        "approval_at_0.5",
        "bad_rate_approved_at_0.5",
        "best_threshold_f1",
        "best_f1",
        "approval_at_best_f1",
        "bad_rate_approved_at_best_f1",
    ]

    # Always save a machine-readable report for Excel/BI use.
    result_df.sort_values(by=["roc_auc", "pr_auc"], ascending=False).to_csv(REPORT_FILE, index=False)

    _print_easy_summary(result_df)
    print(f"\nSaved detailed report: {REPORT_FILE}")

    print("\n=== Model Comparison (same y_test holdout) ===")
    with pd.option_context("display.max_columns", None, "display.width", 220):
        printable = result_df.copy()
        for col in float_cols:
            if col in printable.columns:
                printable[col] = printable[col].map(lambda v: f"{v:.4f}" if pd.notna(v) else "nan")
        print(printable.to_string(index=False))


if __name__ == "__main__":
    main()
