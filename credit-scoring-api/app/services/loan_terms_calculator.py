"""
Loan Terms Calculator Service

Calculates loan terms based on loan purpose:
- Interest rate by purpose and credit score
- Loan term (duration) by purpose
- Monthly payment calculation

This service is called AFTER the user selects their loan purpose.
"""
import logging
import math
from typing import Tuple, Dict

logger = logging.getLogger(__name__)


class LoanTermsCalculator:
    """Calculate loan terms based on purpose and credit score."""
    
    def __init__(self):
        # Purpose-based configurations
        self.purpose_config = {
            "HOME": {
                "base_rate": 6.5,      # Base annual interest rate %
                "term_months": 240,     # 20 years
                "description": "Home loan - secured by property"
            },
            "CAR": {
                "base_rate": 7.5,
                "term_months": 60,      # 5 years
                "description": "Car loan - secured by vehicle"
            },
            "BUSINESS": {
                "base_rate": 9.0,
                "term_months": 84,      # 7 years
                "description": "Business loan - investment"
            },
            "EDUCATION": {
                "base_rate": 8.0,
                "term_months": 60,      # 5 years
                "description": "Education loan - investment in future"
            },
            "DEBT_CONSOLIDATION": {
                "base_rate": 10.0,
                "term_months": 48,      # 4 years
                "description": "Debt consolidation"
            },
            "HOME_IMPROVEMENT": {
                "base_rate": 9.5,
                "term_months": 36,      # 3 years
                "description": "Home improvement"
            },
            "MEDICAL": {
                "base_rate": 8.5,
                "term_months": 24,      # 2 years
                "description": "Medical expenses"
            },
            "PERSONAL": {
                "base_rate": 11.0,
                "term_months": 36,      # 3 years
                "description": "Personal loan - unsecured"
            }
        }
    
    def calculate_interest_rate(
        self,
        loan_purpose: str,
        credit_score: int
    ) -> Tuple[float, str]:
        """
        Calculate interest rate based on purpose and credit score.
        
        Formula: base_rate + credit_score_adjustment
        
        Credit Score Adjustments:
        - 780+: -2.0% (excellent)
        - 740-779: -1.0% (very good)
        - 700-739: 0% (good)
        - 650-699: +1.5% (fair)
        - 600-649: +3.0% (poor)
        - <600: +5.0% (very poor)
        
        Args:
            loan_purpose: Purpose of the loan
            credit_score: Credit score (300-850)
        
        Returns:
            (interest_rate, explanation)
        """
        # Get base rate from purpose
        purpose_data = self.purpose_config.get(
            loan_purpose,
            self.purpose_config["PERSONAL"]  # Default to personal
        )
        base_rate = purpose_data["base_rate"]
        
        # Calculate credit score adjustment
        if credit_score >= 780:
            adjustment = -2.0
            credit_tier = "excellent"
        elif credit_score >= 740:
            adjustment = -1.0
            credit_tier = "very good"
        elif credit_score >= 700:
            adjustment = 0.0
            credit_tier = "good"
        elif credit_score >= 650:
            adjustment = 1.5
            credit_tier = "fair"
        elif credit_score >= 600:
            adjustment = 3.0
            credit_tier = "poor"
        else:
            adjustment = 5.0
            credit_tier = "very poor"
        
        final_rate = base_rate + adjustment
        
        # Ensure rate is within reasonable bounds
        final_rate = max(4.0, min(25.0, final_rate))
        
        explanation = (
            f"{purpose_data['description']}: base {base_rate}% "
            f"+ {adjustment:+.1f}% ({credit_tier} credit) = {final_rate}%"
        )
        
        logger.info(
            f"Interest rate calculation - Purpose: {loan_purpose}, "
            f"Credit score: {credit_score}, Base: {base_rate}%, "
            f"Adjustment: {adjustment:+.1f}%, Final: {final_rate}%"
        )
        
        return final_rate, explanation
    
    def get_loan_term(self, loan_purpose: str) -> Tuple[int, str]:
        """
        Get loan term (duration) based on purpose.
        
        Args:
            loan_purpose: Purpose of the loan
        
        Returns:
            (term_months, description)
        """
        purpose_data = self.purpose_config.get(
            loan_purpose,
            self.purpose_config["PERSONAL"]
        )
        
        term_months = purpose_data["term_months"]
        term_years = term_months // 12
        
        description = f"{term_months} months ({term_years} years) - {purpose_data['description']}"
        
        return term_months, description
    
    def calculate_monthly_payment(
        self,
        principal: float,
        annual_rate: float,
        months: int
    ) -> float:
        """
        Calculate monthly payment using loan amortization formula.
        
        Formula: P * [r(1+r)^n] / [(1+r)^n - 1]
        Where:
        - P = principal (loan amount)
        - r = monthly interest rate (annual_rate / 12 / 100)
        - n = number of months
        
        Args:
            principal: Loan amount in VND
            annual_rate: Annual interest rate (%)
            months: Loan term in months
        
        Returns:
            Monthly payment in VND
        """
        if principal <= 0 or months <= 0:
            return 0.0
        
        if annual_rate == 0:
            # No interest, simple division
            return principal / months
        
        # Convert annual rate to monthly rate
        monthly_rate = annual_rate / 100 / 12
        
        # Amortization formula
        if monthly_rate > 0:
            payment = principal * (
                monthly_rate * (1 + monthly_rate) ** months
            ) / (
                (1 + monthly_rate) ** months - 1
            )
        else:
            payment = principal / months
        
        return round(payment, 2)
    
    def calculate_total_payment(
        self,
        monthly_payment: float,
        months: int
    ) -> float:
        """
        Calculate total payment over loan term.
        
        Args:
            monthly_payment: Monthly payment in VND
            months: Loan term in months
        
        Returns:
            Total payment in VND
        """
        return monthly_payment * months
    
    def calculate_total_interest(
        self,
        principal: float,
        total_payment: float
    ) -> float:
        """
        Calculate total interest paid over loan term.
        
        Args:
            principal: Loan amount in VND
            total_payment: Total payment in VND
        
        Returns:
            Total interest in VND
        """
        return total_payment - principal
    
    def calculate_loan_terms(
        self,
        loan_amount: float,
        loan_purpose: str,
        credit_score: int
    ) -> Dict:
        """
        Calculate complete loan terms.
        
        Args:
            loan_amount: Loan amount in VND
            loan_purpose: Purpose of the loan
            credit_score: Credit score (300-850)
        
        Returns:
            Dictionary with all loan terms:
            - interest_rate: Annual interest rate %
            - loan_term_months: Loan duration in months
            - monthly_payment_vnd: Monthly payment
            - total_payment_vnd: Total payment over term
            - total_interest_vnd: Total interest paid
            - rate_explanation: How rate was calculated
            - term_explanation: Why this term
        """
        # Calculate interest rate
        interest_rate, rate_explanation = self.calculate_interest_rate(
            loan_purpose, credit_score
        )
        
        # Get loan term
        loan_term_months, term_explanation = self.get_loan_term(loan_purpose)
        
        # Calculate monthly payment
        monthly_payment = self.calculate_monthly_payment(
            loan_amount, interest_rate, loan_term_months
        )
        
        # Calculate totals
        total_payment = self.calculate_total_payment(
            monthly_payment, loan_term_months
        )
        total_interest = self.calculate_total_interest(
            loan_amount, total_payment
        )
        
        logger.info(
            f"Loan terms calculated - Amount: {loan_amount:,.0f} VND, "
            f"Purpose: {loan_purpose}, Rate: {interest_rate}%, "
            f"Term: {loan_term_months} months, "
            f"Monthly: {monthly_payment:,.0f} VND"
        )
        
        return {
            "interest_rate": interest_rate,
            "loan_term_months": loan_term_months,
            "monthly_payment_vnd": monthly_payment,
            "total_payment_vnd": total_payment,
            "total_interest_vnd": total_interest,
            "rate_explanation": rate_explanation,
            "term_explanation": term_explanation
        }


# Singleton instance
loan_terms_calculator = LoanTermsCalculator()
