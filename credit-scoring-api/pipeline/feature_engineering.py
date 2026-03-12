"""
Feature Engineering Module
Transforms raw Firestore data into 64 engineered features for LightGBM model

Based on: MODEL_RETRAINING_PIPELINE.md
"""

import pandas as pd
import numpy as np


def engineer_features(df):
    """
    Transform raw Firestore data into model features
    
    Args:
        df: DataFrame from Firestore export with columns:
            - age, monthly_income, employment_status, years_employed
            - home_ownership, loan_purpose, years_credit_history
            - has_previous_defaults, currently_defaulting
        
    Returns:
        features: DataFrame with 64 engineered features
    """
    
    features = pd.DataFrame()
    
    # ===== DEMOGRAPHIC FEATURES =====
    features['AGE'] = df['age']
    features['AGE_NORMALIZED'] = (df['age'] - 18) / (100 - 18)  # 0-1 scale
    
    # Age bins
    features['AGE_18_25'] = (df['age'] <= 25).astype(int)
    features['AGE_26_35'] = ((df['age'] > 25) & (df['age'] <= 35)).astype(int)
    features['AGE_36_50'] = ((df['age'] > 35) & (df['age'] <= 50)).astype(int)
    features['AGE_51_PLUS'] = (df['age'] > 50).astype(int)
    
    # ===== INCOME FEATURES =====
    features['MONTHLY_INCOME'] = df['monthly_income']
    features['ANNUAL_INCOME'] = df['monthly_income'] * 12
    features['INCOME_LOG'] = np.log1p(df['monthly_income'])
    
    # Income bins (in millions VND)
    features['INCOME_BELOW_10M'] = (df['monthly_income'] < 10000000).astype(int)
    features['INCOME_10M_20M'] = ((df['monthly_income'] >= 10000000) & 
                                   (df['monthly_income'] < 20000000)).astype(int)
    features['INCOME_20M_50M'] = ((df['monthly_income'] >= 20000000) & 
                                   (df['monthly_income'] < 50000000)).astype(int)
    features['INCOME_50M_PLUS'] = (df['monthly_income'] >= 50000000).astype(int)
    
    # ===== EMPLOYMENT FEATURES =====
    features['YEARS_EMPLOYED'] = df['years_employed']
    features['YEARS_EMPLOYED_RATIO'] = df['years_employed'] / (df['age'] - 18 + 0.01)
    
    # Employment status (one-hot encoding)
    features['EMP_EMPLOYED'] = (df['employment_status'] == 'EMPLOYED').astype(int)
    features['EMP_SELF_EMPLOYED'] = (df['employment_status'] == 'SELF_EMPLOYED').astype(int)
    features['EMP_UNEMPLOYED'] = (df['employment_status'] == 'UNEMPLOYED').astype(int)
    
    # Employment stability indicators
    features['JOB_STABLE'] = (features['YEARS_EMPLOYED'] >= 2).astype(int)
    features['JOB_UNSTABLE'] = (features['YEARS_EMPLOYED'] < 1).astype(int)
    
    # ===== HOME OWNERSHIP FEATURES =====
    features['HOME_RENT'] = (df['home_ownership'] == 'RENT').astype(int)
    features['HOME_OWN'] = (df['home_ownership'] == 'OWN').astype(int)
    features['HOME_MORTGAGE'] = (df['home_ownership'] == 'MORTGAGE').astype(int)
    features['HOME_WITH_PARENTS'] = (df['home_ownership'] == 'LIVING_WITH_PARENTS').astype(int)
    
    # ===== LOAN PURPOSE FEATURES =====
    features['PURPOSE_HOME'] = (df['loan_purpose'] == 'HOME').astype(int)
    features['PURPOSE_CAR'] = (df['loan_purpose'] == 'CAR').astype(int)
    features['PURPOSE_BUSINESS'] = (df['loan_purpose'] == 'BUSINESS').astype(int)
    features['PURPOSE_EDUCATION'] = (df['loan_purpose'] == 'EDUCATION').astype(int)
    features['PURPOSE_PERSONAL'] = (df['loan_purpose'] == 'PERSONAL').astype(int)
    
    # ===== CREDIT HISTORY FEATURES =====
    features['YEARS_CREDIT_HISTORY'] = df['years_credit_history'].fillna(0)
    features['HAS_CREDIT_HISTORY'] = (df['years_credit_history'] > 0).astype(int)
    features['CREDIT_HISTORY_SHORT'] = (df['years_credit_history'] < 2).astype(int)
    features['CREDIT_HISTORY_LONG'] = (df['years_credit_history'] >= 5).astype(int)
    
    # ===== DEFAULT HISTORY FEATURES =====
    features['HAS_PREVIOUS_DEFAULTS'] = df['has_previous_defaults'].astype(int)
    features['CURRENTLY_DEFAULTING'] = df['currently_defaulting'].astype(int)
    features['ANY_DEFAULT_HISTORY'] = (
        features['HAS_PREVIOUS_DEFAULTS'] | features['CURRENTLY_DEFAULTING']
    ).astype(int)
    
    # ===== INTERACTION FEATURES =====
    # Income to age ratio (earning power)
    features['INCOME_PER_AGE'] = features['MONTHLY_INCOME'] / (features['AGE'] + 1)
    
    # Employment stability score
    features['EMPLOYMENT_STABILITY'] = (
        features['EMP_EMPLOYED'] * features['YEARS_EMPLOYED']
    )
    
    # Financial stability composite
    features['FINANCIAL_STABILITY'] = (
        (features['HOME_OWN'] | features['HOME_MORTGAGE']) * 
        features['JOB_STABLE'] * 
        (1 - features['ANY_DEFAULT_HISTORY'])
    ).astype(int)
    
    # Risk composite
    features['HIGH_RISK_FLAG'] = (
        features['CURRENTLY_DEFAULTING'] | 
        (features['EMP_UNEMPLOYED'] & (features['INCOME_BELOW_10M']))
    ).astype(int)
    
    # Credit maturity
    features['CREDIT_MATURITY'] = (
        features['YEARS_CREDIT_HISTORY'] * features['AGE_NORMALIZED']
    )
    
    # Income stability
    features['INCOME_STABILITY'] = (
        features['INCOME_LOG'] * features['YEARS_EMPLOYED_RATIO']
    )
    
    # Employment income interaction
    features['EMP_INCOME_INTERACTION'] = (
        features['EMP_EMPLOYED'] * features['INCOME_LOG']
    )
    
    # Home ownership income interaction
    features['HOME_INCOME_INTERACTION'] = (
        features['HOME_OWN'] * features['INCOME_LOG']
    )
    
    # ===== RATIO FEATURES =====
    # Income adequacy for loan purpose
    income_m = df['monthly_income'] / 1_000_000  # in millions
    features['INCOME_HOME_RATIO'] = features['PURPOSE_HOME'] * income_m
    features['INCOME_CAR_RATIO'] = features['PURPOSE_CAR'] * income_m
    features['INCOME_BUSINESS_RATIO'] = features['PURPOSE_BUSINESS'] * income_m
    
    # Age-employment consistency
    expected_years = df['age'] - 22  # Assuming work starts at 22
    features['EMPLOYMENT_GAP'] = (expected_years - df['years_employed']).clip(lower=0)
    
    # ===== RISK INDICATORS =====
    # Young with no history
    features['YOUNG_NO_HISTORY'] = (
        (features['AGE'] < 25) & (features['YEARS_CREDIT_HISTORY'] == 0)
    ).astype(int)
    
    # Unemployed with defaults
    features['UNEMPLOYED_WITH_DEFAULTS'] = (
        features['EMP_UNEMPLOYED'] & features['HAS_PREVIOUS_DEFAULTS']
    ).astype(int)
    
    # Low income high risk purpose
    features['LOW_INCOME_RISKY_PURPOSE'] = (
        features['INCOME_BELOW_10M'] & 
        (features['PURPOSE_BUSINESS'] | features['PURPOSE_PERSONAL'])
    ).astype(int)
    
    # ===== COMPOSITE SCORES =====
    # Employment score (0-3)
    features['EMPLOYMENT_SCORE'] = (
        features['EMP_EMPLOYED'] * 2 + 
        features['EMP_SELF_EMPLOYED'] * 1 +
        (features['YEARS_EMPLOYED'] >= 3).astype(int)
    )
    
    # Housing score (0-3)
    features['HOUSING_SCORE'] = (
        features['HOME_OWN'] * 3 + 
        features['HOME_MORTGAGE'] * 2 +
        features['HOME_RENT'] * 1
    )
    
    # Credit history score (0-3)
    features['CREDIT_SCORE'] = (
        (features['YEARS_CREDIT_HISTORY'] >= 1).astype(int) +
        (features['YEARS_CREDIT_HISTORY'] >= 3).astype(int) +
        (features['YEARS_CREDIT_HISTORY'] >= 5).astype(int)
    ) * (1 - features['ANY_DEFAULT_HISTORY'])
    
    # Overall stability score
    features['STABILITY_SCORE'] = (
        features['EMPLOYMENT_SCORE'] + 
        features['HOUSING_SCORE'] + 
        features['CREDIT_SCORE']
    )
    
    # Fill any NaN values
    features = features.fillna(0)
    
    return features


def validate_features(df):
    """
    Validate input data quality before feature engineering
    
    Args:
        df: Raw DataFrame from Firestore
        
    Returns:
        valid_df: Cleaned DataFrame
        invalid_count: Number of invalid rows removed
    """
    original_count = len(df)
    
    # Required columns
    required_cols = [
        'age', 'monthly_income', 'employment_status', 'years_employed',
        'home_ownership', 'loan_purpose', 'years_credit_history',
        'has_previous_defaults', 'currently_defaulting'
    ]
    
    # Check for missing required columns
    missing_cols = set(required_cols) - set(df.columns)
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")
    
    # Remove rows with invalid values
    valid_df = df.copy()
    
    # Age validation
    valid_df = valid_df[(valid_df['age'] >= 18) & (valid_df['age'] <= 100)]
    
    # Income validation
    valid_df = valid_df[valid_df['monthly_income'] > 0]
    
    # Years employed validation
    valid_df = valid_df[valid_df['years_employed'] >= 0]
    
    # Credit history validation
    valid_df['years_credit_history'] = valid_df['years_credit_history'].fillna(0).clip(lower=0)
    
    # Boolean validation
    valid_df['has_previous_defaults'] = valid_df['has_previous_defaults'].fillna(False)
    valid_df['currently_defaulting'] = valid_df['currently_defaulting'].fillna(False)
    
    invalid_count = original_count - len(valid_df)
    
    return valid_df, invalid_count


def get_feature_names():
    """
    Return list of all 64 feature names in correct order
    
    Returns:
        list: Feature names matching model training
    """
    # Create dummy data to extract feature names
    dummy_df = pd.DataFrame({
        'age': [30],
        'monthly_income': [20000000],
        'employment_status': ['EMPLOYED'],
        'years_employed': [5.0],
        'home_ownership': ['RENT'],
        'loan_purpose': ['CAR'],
        'years_credit_history': [3.0],
        'has_previous_defaults': [False],
        'currently_defaulting': [False],
    })
    
    dummy_features = engineer_features(dummy_df)
    return dummy_features.columns.tolist()
