import pandas as pd
import numpy as np
from typing import Dict, List
from app.services.model_loader import ModelLoader
from app.models.schemas import CustomerInput, PredictionResult, LoanEstimation
import logging

logger = logging.getLogger(__name__)


class PredictionService:
    def __init__(self):
        self.model_loader = ModelLoader()
        self.lgbm_model = self.model_loader.lgbm_model
        self.metadata = self.model_loader.metadata
        self.threshold = self.metadata['models']['lightgbm']['threshold']
        
    def predict(self, customer_data: CustomerInput) -> PredictionResult:
        """
        Main prediction method
        """
        try:
            # Prepare features
            features = self._prepare_features(customer_data)
            
            # Get prediction probability
            probability = float(self.lgbm_model.predict_proba(features)[:, 1][0])
            
            # Determine risk level
            risk_level = self._calculate_risk_level(probability)
            
            # Make decision
            decision = "REJECT" if probability >= self.threshold else "APPROVE"
            
            # Calculate loan estimation
            loan_estimation = self._calculate_loan_estimation(customer_data, probability)
            
            # Get risk factors
            risk_factors = self._get_risk_factors(customer_data, probability)
            
            return PredictionResult(
                customer_id=customer_data.customer_id,
                default_probability=probability,
                threshold=self.threshold,
                risk_level=risk_level,
                decision=decision,
                confidence=abs(probability - self.threshold),
                loan_estimation=loan_estimation,
                risk_factors=risk_factors,
                model_version="LightGBM v1.0"
            )
            
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            raise
    
    def _prepare_features(self, customer_data: CustomerInput) -> pd.DataFrame:
        """
        Convert customer input to model features
        """
        # Create base features
        data = {
            'age_years': customer_data.age_years,
            'employment_years': customer_data.employment_years,
            'AMT_INCOME_TOTAL': customer_data.annual_income,
            'AMT_CREDIT': customer_data.requested_amount,
            'total_utilization': customer_data.credit_card_usage / 100,
            'dpd_mean': customer_data.days_past_due_avg,
            'cc_avg_utilization': customer_data.credit_card_usage / 100,
            'NAME_EDUCATION_TYPE_Higher_education': 1 if customer_data.higher_education else 0,
            'NAME_INCOME_TYPE_Working': 1 if customer_data.employment_status == "working" else 0,
        }
        
        # Calculate derived features
        data['credit_income_ratio'] = customer_data.requested_amount / customer_data.annual_income
        
        # Create DataFrame
        df = pd.DataFrame([data])
        
        # Fill missing features with 0
        df = df.reindex(columns=self.lgbm_model.feature_name_, fill_value=0)
        
        return df
    
    def _calculate_risk_level(self, probability: float) -> str:
        """
        Determine risk level based on probability
        """
        if probability < 0.2:
            return "VERY_LOW"
        elif probability < 0.4:
            return "LOW"
        elif probability < 0.6:
            return "MEDIUM"
        elif probability < 0.8:
            return "HIGH"
        else:
            return "CRITICAL"
    
    def _calculate_loan_estimation(self, customer_data: CustomerInput, probability: float) -> LoanEstimation:
        """
        Calculate loan amount estimation based on risk
        """
        income = customer_data.annual_income
        requested = customer_data.requested_amount
        
        # Risk-based multipliers
        if probability < 0.2:  # Very Low Risk
            max_multiplier = 5.0
            interest_rate = 5.5
        elif probability < 0.4:  # Low Risk
            max_multiplier = 4.0
            interest_rate = 6.5
        elif probability < 0.6:  # Medium Risk
            max_multiplier = 3.0
            interest_rate = 8.0
        elif probability < 0.8:  # High Risk
            max_multiplier = 2.0
            interest_rate = 10.0
        else:  # Critical Risk
            max_multiplier = 1.0
            interest_rate = 15.0
        
        # Calculate amounts
        max_eligible = income * max_multiplier
        approved_amount = min(requested, max_eligible)
        
        # Default loan term: 72 months (6 years)
        loan_term_months = 72
        
        # Calculate monthly payment: P * [r(1+r)^n] / [(1+r)^n - 1]
        monthly_rate = interest_rate / 100 / 12
        monthly_payment = approved_amount * (monthly_rate * (1 + monthly_rate)**loan_term_months) / ((1 + monthly_rate)**loan_term_months - 1)
        
        # Recommendation
        if approved_amount >= requested:
            recommendation = "APPROVE_FULL"
        elif approved_amount >= requested * 0.7:
            recommendation = "APPROVE_PARTIAL"
        else:
            recommendation = "REJECT"
        
        return LoanEstimation(
            requested_amount=requested,
            approved_amount=round(approved_amount, 2),
            max_eligible_amount=round(max_eligible, 2),
            interest_rate=interest_rate,
            loan_term_months=loan_term_months,
            monthly_payment=round(monthly_payment, 2),
            recommendation=recommendation
        )
    
    def _get_risk_factors(self, customer_data: CustomerInput, probability: float) -> List[Dict]:
        """
        Analyze risk factors
        """
        factors = []
        
        # Age factor
        if customer_data.age_years < 25:
            factors.append({
                "factor": "Young age (higher risk)",
                "impact": "negative",
                "value": f"{customer_data.age_years} years"
            })
        elif customer_data.age_years > 60:
            factors.append({
                "factor": "Senior age (moderate risk)",
                "impact": "neutral",
                "value": f"{customer_data.age_years} years"
            })
        
        # Employment factor
        if customer_data.employment_years < 2:
            factors.append({
                "factor": "Short employment history",
                "impact": "negative",
                "value": f"{customer_data.employment_years} years"
            })
        elif customer_data.employment_years >= 5:
            factors.append({
                "factor": "Stable employment",
                "impact": "positive",
                "value": f"{customer_data.employment_years} years"
            })
        
        # Loan-to-income ratio
        ratio = customer_data.requested_amount / customer_data.annual_income
        if ratio > 4:
            factors.append({
                "factor": "High loan-to-income ratio",
                "impact": "negative",
                "value": f"{ratio:.1f}x"
            })
        elif ratio < 2:
            factors.append({
                "factor": "Low loan-to-income ratio",
                "impact": "positive",
                "value": f"{ratio:.1f}x"
            })
        
        # Credit usage
        if customer_data.credit_card_usage > 80:
            factors.append({
                "factor": "High credit utilization",
                "impact": "negative",
                "value": f"{customer_data.credit_card_usage}%"
            })
        elif customer_data.credit_card_usage < 30:
            factors.append({
                "factor": "Low credit utilization",
                "impact": "positive",
                "value": f"{customer_data.credit_card_usage}%"
            })
        
        # Payment history
        if customer_data.days_past_due_avg > 15:
            factors.append({
                "factor": "Frequent late payments",
                "impact": "negative",
                "value": f"{customer_data.days_past_due_avg} days average"
            })
        elif customer_data.days_past_due_avg == 0:
            factors.append({
                "factor": "Perfect payment history",
                "impact": "positive",
                "value": "0 days late"
            })
        
        # Education
        if customer_data.higher_education:
            factors.append({
                "factor": "Higher education",
                "impact": "positive",
                "value": "Yes"
            })
        
        return factors


# Singleton instance
prediction_service = PredictionService()