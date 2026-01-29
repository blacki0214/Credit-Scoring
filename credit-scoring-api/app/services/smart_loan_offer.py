import logging
import math
import pandas as pd
from typing import Dict, Any
from app.services.loan_limit_calculator import loan_limit_calculator
from app.services.loan_terms_calculator import loan_terms_calculator
from app.services.feature_engineering import FeatureEngineer
from app.services.model_loader import model_loader

logger = logging.getLogger(__name__)


class SmartLoanOfferService:
    """Generate smart loan offers based on credit score and ML risk assessment."""
    
    def __init__(self):
        self.feature_engineer = FeatureEngineer()
        self.approval_threshold = 0.30  # 30% default probability threshold
        self.min_credit_score = 600  # Minimum credit score for approval
    
    def generate_offer(
        self,
        request_dict: Dict[str, Any],
        age: int,
        years_employed: float,
        employment_status: str,
        home_ownership: str,
        loan_purpose: str,
        annual_income_vnd: float,
        monthly_income_vnd: float,
        credit_score: int
    ) -> Dict[str, Any]:
        """
        Generate smart loan offer with automatic loan limit calculation.
        
        Simplified Process:
        1. Check minimum credit score
        2. Get ML model risk assessment
        3. Calculate maximum loan limit (based on credit score + risk)
        4. Calculate loan terms (based on purpose)
        5. Make approval decision
        6. Return personalized offer
        """
        
        # Step 1: Check credit score - reject if too low
        if credit_score < self.min_credit_score:
            return {
                "approved": False,
                "loan_amount_vnd": 0.0,
                "max_amount_vnd": 0.0,
                "interest_rate": None,
                "monthly_payment_vnd": None,
                "loan_term_months": None,
                "credit_score": credit_score,
                "risk_level": "Very High",
                "approval_message": (
                    f"Loan application rejected. Credit score ({credit_score}) is below "
                    f"minimum requirement ({self.min_credit_score}). Please improve your "
                    f"credit history before reapplying."
                )
            }
        
        # Step 2: Engineer features for ML prediction
        df = pd.DataFrame([request_dict])
        features_df = self.feature_engineer.transform(df)
        
        # Step 3: Get ML model prediction
        prediction_proba = model_loader.lgbm_model.predict_proba(features_df)[0]
        probability = float(prediction_proba[1])  # Probability of default (class 1)
        
        # Determine risk level
        if probability < 0.15:
            risk_level = "Low"
        elif probability < 0.30:
            risk_level = "Medium"
        elif probability < 0.50:
            risk_level = "High"
        else:
            risk_level = "Very High"
        
        # Step 4: Calculate maximum loan limit
        max_loan_amount, limit_reason = loan_limit_calculator.calculate_max_loan(
            credit_score=credit_score,
            annual_income_vnd=annual_income_vnd,
            monthly_income_vnd=monthly_income_vnd,
            risk_level=risk_level
        )
        
        # Step 5: Determine approval
        approved = probability < self.approval_threshold
        
        # Step 6: Calculate loan details if approved
        if approved:
            # Calculate loan terms based on purpose
            loan_terms = loan_terms_calculator.calculate_loan_terms(
                loan_amount=max_loan_amount,
                loan_purpose=loan_purpose,
                credit_score=credit_score
            )
            
            # Generate approval message
            approval_message = (
                f"Loan approved! Maximum loan: {max_loan_amount:,.0f} VND. "
                f"{risk_level} risk at {loan_terms['interest_rate']}% APR. "
                f"Credit score: {credit_score}."
            )
            
            return {
                "approved": True,
                "loan_amount_vnd": max_loan_amount,
                "max_amount_vnd": max_loan_amount,
                "interest_rate": loan_terms["interest_rate"],
                "monthly_payment_vnd": loan_terms["monthly_payment_vnd"],
                "loan_term_months": loan_terms["loan_term_months"],
                "credit_score": credit_score,
                "risk_level": risk_level,
                "approval_message": approval_message
            }
        else:
            # Rejection
            return {
                "approved": False,
                "loan_amount_vnd": 0.0,
                "max_amount_vnd": 0.0,
                "interest_rate": None,
                "monthly_payment_vnd": None,
                "loan_term_months": None,
                "credit_score": credit_score,
                "risk_level": risk_level,
                "approval_message": (
                    f"Loan application rejected. {risk_level} risk. "
                    f"Default probability ({probability:.1%}) exceeds acceptable threshold. "
                    f"Please improve your credit profile and reapply."
                )
            }
