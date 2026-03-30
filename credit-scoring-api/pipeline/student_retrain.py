"""
Student Model Retraining Script (Phase 1)

Re-engineers features from raw CSVs using the SAME formula as
student_prediction_service._engineer(), then retrains the XGBoost model.

Usage:
    cd credit-scoring-api
    python pipeline/student_retrain.py

Outputs:
    output/alternative_model/best_model_phase1.pkl
    output/alternative_model/best_threshold_phase1.pkl
"""
from __future__ import annotations

import pickle
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.metrics import f1_score, roc_auc_score
from sklearn.model_selection import train_test_split

# ── Path setup ────────────────────────────────────────────────────────────────

SCRIPT_DIR   = Path(__file__).resolve().parent          # credit-scoring-api/pipeline/
API_ROOT     = SCRIPT_DIR.parent                         # credit-scoring-api/
PROJECT_ROOT = API_ROOT.parent                           # Credit-Scoring/

RAW_DIR   = PROJECT_ROOT / "data" / "raw"
OUT_DIR   = PROJECT_ROOT / "output" / "alternative_model"
OUT_DIR.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(API_ROOT))
from app.services.student_feature_contract import (
    LIVING_MAP,
    MAJOR_INCOME_MAP,
    MATURITY_MAP,
    STUDENT_MODEL_FEATURE_ORDER,
)

# ── Constants (mirrors student_prediction_service.py) ────────────────────────

PARENTAL_SUPPORT_MAP = {"none": 0.0, "low": 0.25, "medium": 0.5, "high": 1.0}
SAVING_ASSET_TO_BUFFER = {0: False, 1: True}  # saving_asset_status → has_buffer

# Raw living_status values → LIVING_MAP values
DEMO_LIVING_MAP = {"dorm": 0, "family": 1, "rent": 2}

PROGRAM_LEVEL_MAP = {"university": 0, "college": 0, "postgraduate": 1}


# ── Load & merge raw data ─────────────────────────────────────────────────────

def load_raw() -> pd.DataFrame:
    """Merge the four raw CSVs into one joined DataFrame."""
    acad = pd.read_csv(RAW_DIR / "academic_raw"  / "student_academic_profile.csv")
    demo = pd.read_csv(RAW_DIR / "demographic_raw"/ "student_profile.csv")
    fin  = pd.read_csv(RAW_DIR / "financial_raw"  / "student_financial_profile.csv")
    loan = pd.read_csv(RAW_DIR / "loan_raw"        / "student_loan_profile.csv")

    df = demo.merge(acad, on="user_id", how="inner")
    df = df.merge(fin,  on="user_id", how="inner")
    df = df.merge(loan, on="user_id", how="inner")
    print(f"[load] {len(df):,} rows after merge")
    return df


# ── Feature engineering (mirrors _engineer in student_prediction_service.py) ─

def _derive_monthly_from_loan(row: pd.Series) -> tuple[float, float]:
    """
    Raw data doesn't have monthly_income/expenses directly.
    Derive from debt_ratio (monthly_expenses / (income + expenses))
    and expected_income (annual → monthly / 12).
    """
    annual_income  = float(row["expected_income"])
    monthly_income = annual_income / 12.0
    dr = float(row["debt_ratio"])             # = expenses / (income + expenses)
    # dr = e / (m + e)  →  e = dr * m / (1 - dr)
    monthly_expenses = (dr * monthly_income) / max(1.0 - dr, 0.01)
    return monthly_income, monthly_expenses


def _derive_support_sources(row: pd.Series) -> list[str]:
    """Infer support_sources list from financial CSV categorical columns."""
    sources: list[str] = []
    if row.get("parental_support", "none") not in ("none", ""):
        sources.append("family")
    # bnpl_repayment_hist being 'good' or 'average' implies part-time ability
    if row.get("bnpl_repayment_hist", "poor") in ("good", "average"):
        sources.append("part_time")
    # saving_asset_status = 1 implies scholarship / savings
    if int(row.get("saving_asset_status", 0)) == 1:
        sources.append("scholarship")
    return sources


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Build the 25-feature design matrix from raw merged data."""
    records = []

    for _, row in df.iterrows():
        d: dict = {}

        # ── Base fields ───────────────────────────────────────────────────────
        d["age"]          = int(row["age"])
        d["program_level"] = PROGRAM_LEVEL_MAP.get(str(row.get("program_level", "university")), 0)

        living_raw        = str(row.get("living_status", "dorm"))
        living_code       = DEMO_LIVING_MAP.get(living_raw, 0)
        d["living_status"] = living_code

        academic_year     = int(row.get("academic_year", 1))
        d["academic_year"] = academic_year

        d["maturity_score"] = MATURITY_MAP.get(academic_year, 0.4)

        gpa = float(row.get("gpa_latest", 2.0))
        d["gpa_latest"] = gpa

        major_raw         = str(row.get("major_income_potential", "low"))
        # major_income_potential in academic CSV is low/medium/high ; need to map to numeric
        MAJOR_POT_MAP = {"low": 0.45, "medium": 0.65, "high": 0.875}
        d["major_income_potential"] = MAJOR_POT_MAP.get(major_raw.lower(), 0.6)

        d["loan_amount"]  = float(row.get("loan_amount", 20_000_000))

        # ── Derived monthly financials ────────────────────────────────────────
        monthly_income, monthly_expenses = _derive_monthly_from_loan(row)

        # ensure minimum ≥ 1 to avoid div/0
        monthly_income_c   = max(monthly_income, 1.0)
        monthly_expenses_c = max(monthly_expenses, 0.0)

        d["debt_ratio"]    = min(
            monthly_expenses_c / (monthly_income_c + monthly_expenses_c), 0.99
        )

        # ── Support / buffer ─────────────────────────────────────────────────
        has_buffer   = bool(int(row.get("saving_asset_status", 0)))
        d["has_buffer"] = int(has_buffer)

        support_sources   = _derive_support_sources(row)
        support_count     = len(support_sources)
        has_family_support = "family" in support_sources

        d["support_numeric"] = max(0.1, monthly_income / 5_000_000)

        # ── Behavioral signals (EXACT formula from _engineer) ─────────────────
        gpa_signal  = min(1.0, (3.2 - gpa) / 2.2)
        year_signal = min(1.0, (3.0 - float(academic_year)) / 2.0)
        support_gap = max(0.0, 1.0 - min(1.0, d["support_numeric"]))
        expense_pressure = min(1.0, monthly_expenses_c / max(monthly_income_c + monthly_expenses_c, 1.0))
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

        # ── Binary flags ─────────────────────────────────────────────────────
        d["severe_behavior_flag"] = int(
            d["debt_ratio"] > 0.75 and (not has_buffer) and d["support_numeric"] < 0.5
        )
        d["thin_support_flag"] = 1 if d["support_numeric"] < 0.3 else 0
        d["high_pressure_flag"] = 1 if living_code == 2 else 0

        # ── Interaction features ─────────────────────────────────────────────
        d["debt_x_behavior"] = d["debt_ratio"] * d["behavior_risk_score"]
        d["debt_x_support"]  = d["debt_ratio"] * d["support_numeric"]
        d["debt_x_living"]   = d["debt_ratio"] * living_code

        d["financial_stress_index"] = d["debt_ratio"] * d["behavior_volatility"]
        d["academic_resilience"]    = d["gpa_latest"] * d["support_numeric"]
        d["risk_compounding"]       = (
            d["severe_behavior_flag"] + d["thin_support_flag"] + d["high_pressure_flag"]
        )
        d["loan_to_maturity_ratio"] = d["loan_amount"] / (d["maturity_score"] + 0.1)

        records.append(d)

    X = pd.DataFrame(records)[STUDENT_MODEL_FEATURE_ORDER]
    return X


# ── Training ─────────────────────────────────────────────────────────────────

def train(df: pd.DataFrame) -> None:
    y = df["default"].astype(int).values
    X = engineer_features(df)

    print(f"[train] Feature shape: {X.shape}")
    print(f"[train] Class distribution: {y.sum()} defaults / {len(y)} total ({y.mean():.1%})")

    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    scale_pos = (y_train == 0).sum() / max((y_train == 1).sum(), 1)
    print(f"[train] scale_pos_weight = {scale_pos:.2f}")

    model = xgb.XGBClassifier(
        n_estimators=400,
        max_depth=5,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        min_child_weight=5,
        scale_pos_weight=scale_pos,
        eval_metric="logloss",
        use_label_encoder=False,
        random_state=42,
        n_jobs=-1,
    )

    model.fit(
        X_train, y_train,
        eval_set=[(X_val, y_val)],
        verbose=50,
    )

    probs_val = model.predict_proba(X_val)[:, 1]
    auc = roc_auc_score(y_val, probs_val)
    print(f"\n[eval] Validation AUC: {auc:.4f}")

    # Find threshold maximising F1
    best_thresh, best_f1 = 0.5, 0.0
    for t in np.linspace(0.2, 0.7, 51):
        f1 = f1_score(y_val, (probs_val >= t).astype(int))
        if f1 > best_f1:
            best_f1, best_thresh = f1, round(float(t), 4)

    print(f"[eval] Best F1 = {best_f1:.4f}  @ threshold = {best_thresh:.4f}")

    model_path = OUT_DIR / "best_model_phase1.pkl"
    thresh_path = OUT_DIR / "best_threshold_phase1.pkl"

    with open(model_path, "wb") as f:
        pickle.dump(model, f)
    with open(thresh_path, "wb") as f:
        pickle.dump(best_thresh, f)

    print(f"\n[save] Model   → {model_path}")
    print(f"[save] Threshold → {thresh_path}")
    print("\n✅  Retraining complete. Restart the API server to load the new model.")


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    df = load_raw()
    train(df)
