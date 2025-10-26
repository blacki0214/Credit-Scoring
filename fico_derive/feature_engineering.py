import pandas as pd
import numpy as np
from process_data import load_datasets

def derive_fico_features(app, bureau, install, credit=None):
    """Derive FICO-style traditional credit features."""
    
    # --- Repayment Simulation ---
    install["DAYS_ENTRY_PAYMENT"] = install["DAYS_ENTRY_PAYMENT"].fillna(0)
    install["dpd"] = (install["DAYS_ENTRY_PAYMENT"] - install["DAYS_INSTALMENT"]).clip(lower=0)
    install["on_time"] = (install["dpd"] == 0).astype(int)

    repay_feat = install.groupby("SK_ID_CURR").agg({
        "dpd": ["mean", "max"],
        "on_time": "mean",
        "SK_ID_PREV": "count"
    })
    repay_feat.columns = ["dpd_mean", "dpd_max", "on_time_ratio", "num_payments"]
    repay_feat.reset_index(inplace=True)

    # --- Amounts Owed ---
    bureau["CREDIT_ACTIVE_FLAG"] = (bureau["CREDIT_ACTIVE"] == "Active").astype(int)
    owed_feat = bureau.groupby("SK_ID_CURR").agg({
        "AMT_CREDIT_SUM": "sum",
        "AMT_CREDIT_SUM_DEBT": "sum",
        "CREDIT_ACTIVE_FLAG": "sum"
    }).reset_index()
    owed_feat["total_utilization"] = (
        owed_feat["AMT_CREDIT_SUM_DEBT"] / owed_feat["AMT_CREDIT_SUM"].replace(0, np.nan)
    ).clip(upper=1.5)

    # Optional: credit card utilization
    if credit is not None:
        card_util = credit.groupby("SK_ID_CURR").agg({
            "AMT_BALANCE": "mean",
            "AMT_CREDIT_LIMIT_ACTUAL": "mean"
        }).reset_index()
        card_util["credit_card_utilization"] = (
            card_util["AMT_BALANCE"] / card_util["AMT_CREDIT_LIMIT_ACTUAL"].replace(0, np.nan)
        ).clip(upper=1.5)
        owed_feat = owed_feat.merge(card_util[["SK_ID_CURR", "credit_card_utilization"]], on="SK_ID_CURR", how="left")
    else:
        owed_feat["credit_card_utilization"] = np.nan

    # --- Credit History Length ---
    bureau["CREDIT_AGE_MONTHS"] = abs(bureau["DAYS_CREDIT"]) / 30.44
    hist_feat = bureau.groupby("SK_ID_CURR").agg({
        "CREDIT_AGE_MONTHS": ["min", "max", "mean"]
    }).reset_index()
    hist_feat.columns = ["SK_ID_CURR", "oldest_account_m", "newest_account_m", "aaoa_m"]

    # --- Merge ---
    fico = app[["SK_ID_CURR", "TARGET"]]
    fico = fico.merge(repay_feat, on="SK_ID_CURR", how="left")
    fico = fico.merge(owed_feat, on="SK_ID_CURR", how="left")
    fico = fico.merge(hist_feat, on="SK_ID_CURR", how="left")

    # --- Handle missing and invalid values ---
    # Replace infinite values (from division by zero)
    fico = fico.replace([np.inf, -np.inf], np.nan)

    # Fill all remaining NaN with 0
    fico = fico.fillna(0)

    # Add thin file flag
    fico["thin_file_flag"] = (fico["AMT_CREDIT_SUM"] == 0).astype(int)

    return fico


if __name__ == "__main__":
    app, bureau, install, credit = load_datasets()
    fico = derive_fico_features(app, bureau, install, credit)
    fico.to_csv("./output/fico_style_features.csv", index=False)
    print("FICO-style feature table saved to fico_style_features.csv")
    print(fico.head())
