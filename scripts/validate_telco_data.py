import pandas as pd
import numpy as np
import sys
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score
from sklearn.preprocessing import OrdinalEncoder
try:
    import xgboost as xgb
except ImportError:
    print("XGBoost not installed. Using Random Forest.")
    from sklearn.ensemble import RandomForestClassifier as xgb # Fallback
    
# Config
DATA_PATH = Path(r"d:\Project_A\Credit-Scoring\data\data-processing\alternative_data\flat_telco_test.csv")
EXPECTED_FEATURES = [
    'telco_account_age_days', 'telco_avg_revenue_mean', 'telco_recharge_count_mean',
    'wallet_txn_count', 'wallet_avg_amount', 'has_ewallet_data'
] # Subset of features expected by 01_feature_engineering

def validate_data():
    print("--- 1. Data Loading & Schema Check ---")
    if not DATA_PATH.exists():
        print(f"ERROR: File not found at {DATA_PATH}")
        return

    print(f"Loaded data shape: {df.shape}")
    
    # Drop IDs and Dates for modeling
    drop_cols = ['loan_id', 'user_id', 'loan_approval_date', 'loan_product_type']
    modeling_df = df.drop(columns=[c for c in drop_cols if c in df.columns], errors='ignore')

    # Handle Categoricals
    object_cols = modeling_df.select_dtypes(include=['object']).columns
    print(f"Categorical columns to encode: {object_cols.tolist()}")
    encoder = OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1)
    modeling_df[object_cols] = encoder.fit_transform(modeling_df[object_cols].astype(str))
    modeling_df.fillna(-1, inplace=True)

    # Check for Leakage
    print("\n--- 2. Leakage Analysis (Correlation with default_flag) ---")
    if 'default_flag' not in df.columns:
        print("Target 'default_flag' not found. Cannot check leakage.")
    else:
        # potential leakage features
        potential_leakage = ['loan_stress', 'loan_stress_bucket', 'delta_topup_count', 'delta_block_rate']
        
        # Encoding loan_stress_bucket if needed
        if 'loan_stress_bucket' in df.columns and df['loan_stress_bucket'].dtype == 'O':
            try:
                # Simple ordinal mapping for check
                mapping = {'LOW': 1, 'MEDIUM': 2, 'HIGH': 3}
                df['loan_stress_bucket_encoded'] = df['loan_stress_bucket'].map(mapping).fillna(0)
                potential_leakage.append('loan_stress_bucket_encoded')
            except:
                pass
            
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        correlations = df[numeric_cols].corr()['default_flag'].sort_values(ascending=False)
        
        print("Top Correlations with default_flag:")
        print(correlations.head(5))
        print(correlations.tail(5))

        for col in potential_leakage:
            if col in df.columns:
                corr = df[col].corr(df['default_flag']) if np.issubdtype(df[col].dtype, np.number) else "N/A"
                print(f"Correlation '{col}' vs 'default_flag': {corr}")
                if isinstance(corr, float) and abs(corr) > 0.5:
                     print(f"  -> WARNING: High correlation indicating potential LEAKAGE.")

    # Model Based Validation
    print("\n--- 3. Model Training Validation (Checking Data Quality) ---")
    if 'default_flag' not in modeling_df.columns:
        return

    X = modeling_df.drop(columns=['default_flag'])
    y = modeling_df['default_flag']

    # Scenario A: With Suspicious Features
    print("Training XGBoost WITH 'loan_stress'...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    if 'XGBClassifier' in str(xgb):
        model = xgb.XGBClassifier(use_label_encoder=False, eval_metric='logloss')
    else:
        model = xgb(n_estimators=100, max_depth=5, random_state=42) # RF Fallback
        
    model.fit(X_train, y_train)
    preds = model.predict_proba(X_test)[:, 1]
    auc_with = roc_auc_score(y_test, preds)
    print(f"AUC (With loan_stress): {auc_with:.4f}")

    # Feature Importance
    if hasattr(model, 'feature_importances_'):
        imps = pd.Series(model.feature_importances_, index=X.columns).sort_values(ascending=False)
        print("Top 5 Features:")
        print(imps.head(5))
    
    # Scenario B: Without Suspicious Features
    suspicious = ['loan_stress', 'loan_stress_bucket', 'loan_stress_bucket_encoded']
    drop_obs = [c for c in suspicious if c in X.columns]
    if drop_obs:
        print(f"\nTraining XGBoost WITHOUT {drop_obs}...")
        X_train_clean = X_train.drop(columns=drop_obs)
        X_test_clean = X_test.drop(columns=drop_obs)
        
        model.fit(X_train_clean, y_train)
        preds_clean = model.predict_proba(X_test_clean)[:, 1]
        auc_without = roc_auc_score(y_test, preds_clean)
        print(f"AUC (Without loan_stress): {auc_without:.4f}")
        
        diff = auc_with - auc_without
        print(f"Performance Drop due to removal: {diff:.4f}")
        if diff > 0.1:
            print("CONCLUSION: 'loan_stress' contains MASSIVE information. High probability of LEAKAGE.")
        elif auc_without > 0.6:
            print("CONCLUSION: Data has good predictive power even without suspicious features. GOOD for training.")
        else:
            print("CONCLUSION: Data is weak/noisy without 'loan_stress'.")

    # Check for Bias
    print("\n--- 4. Bias Analysis ---")
    sensitive_attrs = ['age', 'birth_year', 'has_partner', 'num_dependents', 'has_academic']
    
    for attr in sensitive_attrs:
        if attr in df.columns:
            print(f"\nAttribute: {attr}")
            try:
                if df[attr].nunique() < 10:
                    group_stats = df.groupby(attr)['default_flag'].mean()
                    print(f"Default Rate by {attr}:")
                    print(group_stats)
                    range_diff = group_stats.max() - group_stats.min()
                    if range_diff > 0.1: # Threshold 10%
                        print(f"  -> WARNING: Significant disparity ({range_diff:.2%}) detected.")
                else:
                    # For continuous vars like age
                    corr = df[attr].corr(df['default_flag'])
                    print(f"Correlation with default_flag: {corr:.4f}")
            except Exception as e:
                print(f"Could not analyze {attr}: {e}")

if __name__ == "__main__":
    validate_data()
