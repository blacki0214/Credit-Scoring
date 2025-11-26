import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from app.services.model_loader import model_loader
import logging

logger = logging.getLogger(__name__)


class FeatureEngineer:
    """Handle feature engineering for predictions"""
    
    def __init__(self):
        self.feature_columns = None
        self.categorical_encodings = {}
        self._load_metadata()
    
    def _load_metadata(self):
        """Load feature metadata from model"""
        try:
            if model_loader.lgbm_model:
                # Get feature names directly from the model
                self.feature_columns = model_loader.lgbm_model.feature_name_
                logger.info(f"Loaded {len(self.feature_columns)} feature columns from model")
        except Exception as e:
            logger.warning(f"Could not load feature names from model: {e}")
    
    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transform input data to match model expectations
        
        The model expects 64 features from the Home Credit dataset.
        Since we only have basic loan application data, we'll map what we can
        and fill the rest with reasonable defaults.
        """
        
        # Create a copy to avoid modifying original
        data = df.copy()
        
        # Get expected features from model
        if not self.feature_columns:
            raise ValueError("Model feature names not available")
        
        # Create dataframe with all expected features, filled with defaults
        aligned_data = pd.DataFrame(0.0, index=data.index, columns=self.feature_columns)
        
        # Map available fields to model features with intelligent defaults
        feature_mapping = self._create_feature_mapping(data)
        
        for model_feature, value in feature_mapping.items():
            if model_feature in aligned_data.columns:
                aligned_data[model_feature] = value
        
        return aligned_data
    
    def _create_feature_mapping(self, data: pd.DataFrame) -> Dict[str, float]:
        """Map input data to model features with reasonable defaults"""
        
        mapping = {}
        
        # Extract input values
        row = data.iloc[0] if len(data) > 0 else {}
        
        # Basic demographics
        age = row.get('person_age', 30)
        income = row.get('person_income', 50000)
        emp_length = row.get('person_emp_length', 5)
        
        # Loan information
        loan_amount = row.get('loan_amnt', 10000)
        loan_rate = row.get('loan_int_rate', 10) / 100
        loan_pct_income = row.get('loan_percent_income', 0.2)
        credit_score = row.get('credit_score', 700)
        cred_hist_length = row.get('cb_person_cred_hist_length', 10)
        
        # Default indicators
        has_default = 1 if row.get('cb_person_default_on_file', 'N') == 'Y' else 0
        prev_default = 1 if row.get('previous_loan_defaults_on_file', 'N') == 'Y' else 0
        
        # Map to model features
        # Basic demographics
        mapping['age_years'] = age
        mapping['employment_years'] = emp_length
        
        # Income ratios (simulated from loan data)
        mapping['annuity_income_ratio'] = min(loan_pct_income, 1.0)
        mapping['credit_income_ratio'] = loan_amount / max(income, 1)
        mapping['goods_income_ratio'] = (loan_amount * 0.8) / max(income, 1)  # Assume goods = 80% of loan
        mapping['income_per_person'] = income  # Assume single person
        
        # Employment flags
        mapping['has_job_flag'] = 1 if emp_length > 0 else 0
        
        # Raw application data
        mapping['raw_income_total'] = income
        mapping['raw_credit_amt'] = loan_amount
        mapping['raw_annuity_amt'] = loan_amount * loan_pct_income / 12  # Monthly payment estimate
        mapping['raw_goods_price'] = loan_amount * 0.8
        mapping['raw_cnt_fam_members'] = 1  # Assume single
        mapping['raw_days_employed'] = -emp_length * 365 if emp_length > 0 else 0
        
        # Missing flags
        mapping['app_missing_income_flag'] = 0
        mapping['app_missing_credit_flag'] = 0
        mapping['app_missing_annuity_flag'] = 0
        mapping['app_missing_goods_flag'] = 0
        
        # Bureau features (credit history)
        # Use credit score and history length to estimate
        credit_quality = (credit_score - 300) / 550  # Normalize 300-850 to 0-1
        
        mapping['total_credit_sum'] = loan_amount * (1 + cred_hist_length * 0.5)
        mapping['total_credit_debt'] = loan_amount * (0.3 - credit_quality * 0.2)  # Lower debt for higher scores
        mapping['total_utilization'] = 0.3 - credit_quality * 0.2
        mapping['active_loans_count'] = 1 + prev_default  # More loans if had defaults
        mapping['closed_loans_count'] = max(0, cred_hist_length - 2)
        mapping['max_overdue_ratio'] = has_default * 0.5
        mapping['raw_bureau_records'] = cred_hist_length
        mapping['bur_raw_total_credit_sum'] = mapping['total_credit_sum']
        mapping['bur_raw_total_credit_debt'] = mapping['total_credit_debt']
        mapping['raw_total_overdue_amount'] = has_default * loan_amount * 0.1
        mapping['raw_overdue_loans_count'] = has_default
        mapping['raw_has_overdue_flag'] = has_default
        
        # Credit card features
        mapping['cc_avg_utilization'] = 0.3 - credit_quality * 0.2
        mapping['cc_max_utilization'] = 0.5 - credit_quality * 0.3
        mapping['cc_payment_ratio'] = 1.0 - has_default * 0.3
        mapping['cc_total_months'] = cred_hist_length * 12
        mapping['cc_active_month_ratio'] = 0.8
        mapping['cc_has_overdue_flag'] = has_default
        mapping['raw_cc_records'] = min(cred_hist_length, 24)
        mapping['cc_raw_limit_avg'] = income * 0.3
        mapping['cc_raw_balance_avg'] = income * 0.1
        mapping['cc_raw_total_payment'] = income * 0.05 * cred_hist_length
        mapping['cc_raw_total_drawings'] = income * 0.04 * cred_hist_length
        mapping['cc_raw_overdue_months'] = has_default * 3
        mapping['cc_raw_max_dpd'] = has_default * 30
        mapping['cc_raw_invalid_limit_flag'] = 0
        
        # Days past due features
        mapping['dpd_mean'] = has_default * 5
        mapping['dpd_max'] = has_default * 30
        mapping['on_time_ratio'] = 1.0 - has_default * 0.2
        mapping['num_payments'] = cred_hist_length * 12
        mapping['dpd_gt30_flag'] = has_default
        
        # Installment features
        mapping['ins_payment_ratio'] = 1.0 - has_default * 0.2
        mapping['ins_payment_variance'] = has_default * 0.1
        mapping['ins_early_ratio'] = (1.0 - has_default) * 0.3
        mapping['raw_instalments_count'] = cred_hist_length * 12
        mapping['raw_payments_count'] = cred_hist_length * 12
        mapping['ins_raw_total_instalment'] = loan_amount * cred_hist_length
        mapping['ins_raw_total_payment'] = loan_amount * cred_hist_length * (1 + loan_rate)
        mapping['ins_raw_on_time_count'] = int(cred_hist_length * 12 * (1 - has_default * 0.2))
        mapping['ins_raw_late_count'] = int(cred_hist_length * 12 * has_default * 0.2)
        mapping['ins_raw_max_dpd'] = has_default * 30
        mapping['ins_raw_missing_amount_flag'] = 0
        mapping['ins_raw_missing_days_flag'] = 0
        
        # Missing data flags
        mapping['missing_income_flag'] = 0
        mapping['missing_bureau_flag'] = 0
        mapping['missing_cc_flag'] = 0
        mapping['missing_installment_flag'] = 0
        
        return mapping