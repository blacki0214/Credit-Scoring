"""
Loan Limit Calculator Service

Calculates maximum loan amount based on:
- Credit score (from ML model)
- Annual income
- DTI (Debt-to-Income) ratio constraints
- Risk level from ML model

Replaces the complex tier-based system with a simpler credit score-based approach.
"""
import logging
from typing import Tuple

logger = logging.getLogger(__name__)


class LoanLimitCalculator:
    """Calculate maximum loan amount based on credit score and income."""
    
    def __init__(self):
        # DTI limits by risk level
        self.dti_limits = {
            "Low": 0.43,      # 43% DTI for low risk
            "Medium": 0.36,   # 36% DTI for medium risk
            "High": 0.28,     # 28% DTI for high risk
            "Very High": 0.20 # 20% DTI for very high risk
        }
        
        # Default loan term for DTI calculation (months)
        self.default_term_months = 36  # 3 years
        
    def calculate_base_multiplier(self, credit_score: int) -> Tuple[float, str]:
        """
        Calculate income multiplier based on credit score.
        
        Credit Score Ranges:
        - 780+: 5.0x annual income (excellent credit)
        - 740-779: 4.0x annual income (very good credit)
        - 700-739: 3.0x annual income (good credit)
        - 650-699: 2.5x annual income (fair credit)
        - 600-649: 2.0x annual income (poor credit)
        - <600: 1.5x annual income (very poor credit)
        
        Returns: (multiplier, reason)
        """
        if credit_score >= 780:
            return 5.0, "excellent credit (780+)"
        elif credit_score >= 740:
            return 4.0, "very good credit (740-779)"
        elif credit_score >= 700:
            return 3.0, "good credit (700-739)"
        elif credit_score >= 650:
            return 2.5, "fair credit (650-699)"
        elif credit_score >= 600:
            return 2.0, "poor credit (600-649)"
        else:
            return 1.5, "very poor credit (<600)"
    
    def calculate_max_loan(
        self,
        credit_score: int,
        annual_income_vnd: float,
        monthly_income_vnd: float,
        risk_level: str
    ) -> Tuple[float, str]:
        """
        Calculate maximum loan amount.
        
        Formula:
        1. Income-based limit = annual_income × credit_score_multiplier
        2. DTI-based limit = monthly_income × dti_limit × term_months
        3. Final limit = min(income_based, dti_based)
        4. Apply risk adjustment if needed
        
        Args:
            credit_score: Credit score (300-850)
            annual_income_vnd: Annual income in VND
            monthly_income_vnd: Monthly income in VND
            risk_level: Risk level from ML model (Low/Medium/High/Very High)
        
        Returns:
            (max_loan_amount, calculation_reason)
        """
        # Step 1: Calculate income-based limit
        base_multiplier, credit_reason = self.calculate_base_multiplier(credit_score)
        income_based_limit = annual_income_vnd * base_multiplier
        
        # Step 2: Calculate DTI-based limit
        dti_limit = self.dti_limits.get(risk_level, 0.28)  # Default to 28% if unknown
        dti_based_limit = monthly_income_vnd * dti_limit * self.default_term_months
        
        # Step 3: Take the more conservative limit
        max_loan = min(income_based_limit, dti_based_limit)
        
        # Step 4: Apply risk adjustment
        risk_adjustment = 1.0
        if risk_level == "High":
            risk_adjustment = 0.7
            risk_reason = "high risk adjustment (-30%)"
        elif risk_level == "Very High":
            risk_adjustment = 0.5
            risk_reason = "very high risk adjustment (-50%)"
        else:
            risk_reason = "no risk adjustment"
        
        adjusted_loan = max_loan * risk_adjustment
        
        # Build explanation
        limiting_factor = "income-based" if income_based_limit < dti_based_limit else "DTI-based"
        reason = (
            f"{credit_reason}, {limiting_factor} limit "
            f"({income_based_limit:,.0f} vs {dti_based_limit:,.0f} VND), "
            f"{risk_reason}"
        )
        
        logger.info(
            f"Loan limit calculation - Credit score: {credit_score}, "
            f"Multiplier: {base_multiplier}x, "
            f"Income-based: {income_based_limit:,.0f} VND, "
            f"DTI-based: {dti_based_limit:,.0f} VND, "
            f"Risk: {risk_level} ({risk_adjustment:.0%}), "
            f"Final: {adjusted_loan:,.0f} VND"
        )
        
        return adjusted_loan, reason
    
    def calculate_dti_ratio(
        self,
        monthly_payment: float,
        monthly_income: float
    ) -> float:
        """
        Calculate debt-to-income ratio.
        
        Args:
            monthly_payment: Monthly loan payment in VND
            monthly_income: Monthly income in VND
        
        Returns:
            DTI ratio (0.0 to 1.0)
        """
        if monthly_income <= 0:
            return 1.0  # Invalid income
        
        return min(monthly_payment / monthly_income, 1.0)
    
    def validate_loan_amount(
        self,
        requested_amount: float,
        max_loan_amount: float,
        monthly_income: float,
        monthly_payment: float
    ) -> Tuple[bool, str]:
        """
        Validate if requested loan amount is acceptable.
        
        Args:
            requested_amount: Amount customer wants to borrow
            max_loan_amount: Maximum calculated loan amount
            monthly_income: Monthly income in VND
            monthly_payment: Estimated monthly payment in VND
        
        Returns:
            (is_valid, reason)
        """
        # Check if requested amount exceeds maximum
        if requested_amount > max_loan_amount:
            return False, (
                f"Requested amount ({requested_amount:,.0f} VND) exceeds "
                f"maximum eligible amount ({max_loan_amount:,.0f} VND)"
            )
        
        # Check DTI ratio
        dti_ratio = self.calculate_dti_ratio(monthly_payment, monthly_income)
        if dti_ratio > 0.43:  # Maximum acceptable DTI
            return False, (
                f"Monthly payment ({monthly_payment:,.0f} VND) would result in "
                f"DTI ratio of {dti_ratio:.1%}, exceeding maximum 43%"
            )
        
        return True, "Loan amount is within acceptable limits"


# Singleton instance
loan_limit_calculator = LoanLimitCalculator()
