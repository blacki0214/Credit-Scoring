import logging
from app.models.schemas import PredictionRequest, LoanOfferResponse

logger = logging.getLogger(__name__)

# USD to VND exchange rate (approximate)
USD_TO_VND = 25000


class LoanOfferService:
    """Service for calculating loan offers in VND"""
    
    def __init__(self):
        # Default loan term in months
        self.default_loan_term = 36
        
        # Risk-based approval thresholds
        self.approval_threshold = 0.30  # Approve if probability < 30%
        
        # Risk-based interest rates (annual %)
        self.interest_rates = {
            "Low": 8.5,      # < 15% default probability
            "Medium": 12.0,  # 15-30% default probability
            "High": 16.0,    # 30-50% default probability
            "Very High": 20.0  # > 50% default probability
        }
        
        # Risk-based loan amount adjustments
        self.loan_amount_factors = {
            "Low": 1.0,       # Full amount
            "Medium": 0.75,   # 75% of requested
            "High": 0.5,      # 50% of requested
            "Very High": 0.0  # Rejected
        }
    
    def calculate_offer(
        self, 
        request: PredictionRequest, 
        probability: float, 
        risk_level: str
    ) -> LoanOfferResponse:
        """Calculate loan offer based on risk assessment"""
        
        # Convert USD to VND
        requested_amount_vnd = request.loan_amnt * USD_TO_VND
        income_vnd = request.person_income * USD_TO_VND
        
        # Determine approval
        approved = probability < self.approval_threshold
        
        # Calculate max eligible amount based on income and risk
        # Rule: Max loan = 5x annual income, adjusted by risk
        base_max_amount = income_vnd * 5
        risk_factor = self.loan_amount_factors.get(risk_level, 0.5)
        max_amount_vnd = base_max_amount * risk_factor
        
        # Calculate approved amount
        if approved:
            # Approve up to requested amount, but not more than max eligible
            approved_amount_vnd = min(requested_amount_vnd, max_amount_vnd)
        else:
            approved_amount_vnd = 0
        
        # Get interest rate based on risk
        interest_rate = self.interest_rates.get(risk_level, 20.0)
        
        # Calculate monthly payment if approved
        monthly_payment_vnd = None
        loan_term_months = None
        
        if approved and approved_amount_vnd > 0:
            loan_term_months = self.default_loan_term
            monthly_payment_vnd = self._calculate_monthly_payment(
                approved_amount_vnd, 
                interest_rate, 
                loan_term_months
            )
        
        # Generate approval message
        approval_message = self._generate_message(
            approved, 
            risk_level, 
            probability, 
            approved_amount_vnd,
            requested_amount_vnd
        )
        
        return LoanOfferResponse(
            approved=approved,
            loan_amount_vnd=approved_amount_vnd,
            requested_amount_vnd=requested_amount_vnd,
            max_amount_vnd=max_amount_vnd,
            interest_rate=interest_rate,
            monthly_payment_vnd=monthly_payment_vnd,
            loan_term_months=loan_term_months,
            credit_score=request.credit_score,
            risk_level=risk_level,
            approval_message=approval_message
        )
    
    def _calculate_monthly_payment(
        self, 
        principal: float, 
        annual_rate: float, 
        months: int
    ) -> float:
        """Calculate monthly payment using amortization formula"""
        if annual_rate == 0:
            return principal / months
        
        # Convert annual rate to monthly rate
        monthly_rate = annual_rate / 100 / 12
        
        # Amortization formula: P * [r(1+r)^n] / [(1+r)^n - 1]
        payment = principal * (monthly_rate * (1 + monthly_rate) ** months) / \
                  ((1 + monthly_rate) ** months - 1)
        
        return round(payment, 2)
    
    def _generate_message(
        self, 
        approved: bool, 
        risk_level: str, 
        probability: float,
        approved_amount: float,
        requested_amount: float
    ) -> str:
        """Generate approval/rejection message"""
        
        if approved:
            if approved_amount >= requested_amount:
                return f"Loan approved! {risk_level} risk applicant. Full amount granted."
            else:
                return f"Loan partially approved. {risk_level} risk. Approved {approved_amount:,.0f} VND of {requested_amount:,.0f} VND requested."
        else:
            if risk_level == "Very High":
                return f"Loan rejected. Very high default risk ({probability:.1%}). Unable to approve at this time."
            else:
                return f"Loan rejected. Default risk ({probability:.1%}) exceeds approval threshold. Please improve credit profile and reapply."


# Singleton instance
loan_offer_service = LoanOfferService()
