import logging
import math
import pandas as pd
from typing import Dict, Any
from app.services.tier_calculator import TierCalculator
from app.services.feature_engineering import FeatureEngineer
from app.services.model_loader import model_loader

logger = logging.getLogger(__name__)


class SmartLoanOfferService:
    """Generate smart loan offers based on customer tier and risk profile."""
    
    def __init__(self):
        self.tier_calculator = TierCalculator()
        self.feature_engineer = FeatureEngineer()
        self.approval_threshold = 0.30  # 30% default probability threshold
        self.min_credit_score = 600  # Minimum credit score for approval
        
        # Risk-based interest rates (annual %)
        self.interest_rates = {
            "Low": 8.5,
            "Medium": 12.0,
            "High": 16.0,
            "Very High": 20.0
        }
    
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
        Generate smart loan offer with automatic tier-based amount calculation.
        
        Process:
        1. Calculate customer tier based on profile
        2. Determine maximum loan based on tier and DTI limits
        3. Get ML model risk assessment
        4. Make approval decision
        5. Return personalized offer
        """
        
        # Step 1: Calculate tier
        tier, income_multiplier, tier_reason = self.tier_calculator.calculate_tier(
            age=age,
            years_employed=years_employed,
            employment_status=employment_status,
            home_ownership=home_ownership,
            loan_purpose=loan_purpose
        )
        
        # Step 2: Check credit score - reject if too low
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
                ),
                "loan_tier": "NONE",
                "tier_reason": f"Credit score too low (minimum {self.min_credit_score} required)"
            }
        
        # Step 3: Calculate maximum loan amount
        max_loan_amount = self.tier_calculator.calculate_max_loan(
            annual_income_vnd=annual_income_vnd,
            monthly_income_vnd=monthly_income_vnd,
            income_multiplier=income_multiplier,
            loan_purpose=loan_purpose
        )
        
        # Step 4: Engineer features for prediction
        df = pd.DataFrame([request_dict])
        features_df = self.feature_engineer.transform(df)
        
        # Step 5: Get ML model prediction
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
        
        # Step 6: Determine approval (credit score already checked above)
        approved = probability < self.approval_threshold
        
        # Step 7: Get interest rate
        interest_rate = self.interest_rates.get(risk_level, 20.0)
        
        # Step 8: Calculate loan details if approved
        if approved:
            # Determine loan term based on purpose
            loan_term = self._get_loan_term(loan_purpose)
            
            # Calculate monthly payment
            monthly_payment = self._calculate_monthly_payment(
                max_loan_amount,
                interest_rate,
                loan_term
            )
            
            # Generate approval message
            approval_message = (
                f"Loan approved. {tier} tier. Maximum recommended: {max_loan_amount:,.0f} VND. "
                f"{risk_level} risk at {interest_rate}% APR."
            )
            
            return {
                "approved": True,
                "loan_amount_vnd": max_loan_amount,
                "max_amount_vnd": max_loan_amount,
                "interest_rate": interest_rate,
                "monthly_payment_vnd": monthly_payment,
                "loan_term_months": loan_term,
                "credit_score": credit_score,
                "risk_level": risk_level,
                "approval_message": approval_message,
                "loan_tier": tier,
                "tier_reason": tier_reason
            }
        else:
            # Rejection
            return {
                "approved": False,
                "loan_amount_vnd": 0.0,
                "max_amount_vnd": 0.0,
                "interest_rate": interest_rate,
                "monthly_payment_vnd": None,
                "loan_term_months": None,
                "credit_score": credit_score,
                "risk_level": risk_level,
                "approval_message": (
                    f"Loan application rejected. {risk_level} risk. "
                    f"Default probability ({probability:.1%}) exceeds acceptable threshold. "
                    f"Please improve your credit profile and reapply."
                ),
                "loan_tier": "NONE",
                "tier_reason": "Application rejected due to high risk"
            }
    
    def _get_loan_term(self, loan_purpose: str) -> int:
        """Get appropriate loan term based on purpose."""
        terms = {
            "HOME": 240,  # 20 years
            "CAR": 60,    # 5 years
            "BUSINESS": 84,  # 7 years
            "EDUCATION": 60,  # 5 years
            "DEBT_CONSOLIDATION": 48,  # 4 years
            "HOME_IMPROVEMENT": 36,  # 3 years
            "MEDICAL": 24,  # 2 years
            "PERSONAL": 36  # 3 years
        }
        return terms.get(loan_purpose, 36)
    
    def _calculate_monthly_payment(
        self,
        principal: float,
        annual_rate: float,
        months: int
    ) -> float:
        """Calculate monthly payment using loan amortization formula."""
        if annual_rate == 0:
            return principal / months
        
        # Convert annual rate to monthly rate
        monthly_rate = annual_rate / 100 / 12
        
        # Amortization formula: P * [r(1+r)^n] / [(1+r)^n - 1]
        if monthly_rate > 0:
            payment = principal * (monthly_rate * (1 + monthly_rate) ** months) / \
                     ((1 + monthly_rate) ** months - 1)
        else:
            payment = principal / months
        
        return round(payment, 2)
