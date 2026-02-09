import logging
from app.models.schemas import SimpleLoanRequest, PredictionRequest

logger = logging.getLogger(__name__)

# VND to USD conversion rate
VND_TO_USD = 1 / 25000


class RequestConverter:
    """Convert customer-friendly requests to internal prediction format"""
    
    def convert_simple_to_prediction(self, simple_req: SimpleLoanRequest) -> PredictionRequest:
        """Convert SimpleLoanRequest to PredictionRequest with calculated fields"""
        
        # Convert VND to USD for internal processing
        annual_income_usd = (simple_req.monthly_income * 12) * VND_TO_USD
        
        # Use a reference loan amount (2x annual income) since we calculate max loan separately
        reference_loan_amount_vnd = simple_req.monthly_income * 12 * 2
        loan_amount_usd = reference_loan_amount_vnd * VND_TO_USD
        
        # Calculate credit score based on customer profile
        credit_score = self._calculate_credit_score(simple_req, reference_loan_amount_vnd)
        
        # Map employment status
        home_ownership_map = {
            "RENT": "RENT",
            "OWN": "OWN",
            "MORTGAGE": "MORTGAGE",
            "LIVING_WITH_PARENTS": "OTHER"
        }
        
        # Map loan purpose to loan intent
        # Note: loan_purpose is now optional. Use "PERSONAL" as default for ML model compatibility
        # The actual purpose doesn't affect credit score calculation since we use a reference loan amount
        purpose_map = {
            "PERSONAL": "PERSONAL",
            "EDUCATION": "EDUCATION",
            "MEDICAL": "MEDICAL",
            "BUSINESS": "VENTURE",
            "HOME_IMPROVEMENT": "HOMEIMPROVEMENT",
            "DEBT_CONSOLIDATION": "DEBTCONSOLIDATION",
            "CAR": "PERSONAL",  # Map CAR to PERSONAL for ML model
            "HOME": "PERSONAL"   # Map HOME to PERSONAL for ML model
        }
        
        # Use default "PERSONAL" if loan_purpose is not provided
        loan_purpose = simple_req.loan_purpose or "PERSONAL"
        
        # Calculate loan grade based on credit score and defaults
        loan_grade = self._calculate_loan_grade(credit_score, simple_req.has_previous_defaults)
        
        # Calculate interest rate based on grade
        interest_rate = self._get_interest_rate(loan_grade)
        
        # Calculate loan as percentage of income
        loan_percent_income = min(loan_amount_usd / max(annual_income_usd, 1), 1.0)
        
        # Create PredictionRequest
        return PredictionRequest(
            person_age=simple_req.age,
            person_income=annual_income_usd,
            person_emp_length=simple_req.years_employed,
            person_home_ownership=home_ownership_map.get(simple_req.home_ownership, "OTHER"),
            loan_amnt=loan_amount_usd,
            loan_intent=purpose_map.get(loan_purpose, "PERSONAL"),
            loan_grade=loan_grade,
            loan_int_rate=interest_rate,
            loan_percent_income=loan_percent_income,
            cb_person_cred_hist_length=simple_req.years_credit_history,
            credit_score=credit_score,
            cb_person_default_on_file="Y" if simple_req.currently_defaulting else "N",
            previous_loan_defaults_on_file="Y" if simple_req.has_previous_defaults else "N"
        )
    
    def calculate_credit_score_with_breakdown(
        self, 
        age: int,
        monthly_income: float,
        years_employed: float,
        home_ownership: str,
        years_credit_history: int,
        employment_status: str,
        has_previous_defaults: bool,
        currently_defaulting: bool,
        loan_amount: float
    ) -> dict:
        """Calculate credit score with detailed breakdown for dashboard"""
        
        breakdown = {
            "base_score": 600,
            "age_adjustment": 0,
            "income_adjustment": 0,
            "employment_adjustment": 0,
            "home_ownership_adjustment": 0,
            "credit_history_adjustment": 0,
            "employment_status_adjustment": 0,
            "defaults_adjustment": 0,
            "debt_to_income_adjustment": 0,
            "final_score": 0
        }
        
        score = 600
        
        # Age factor
        if age >= 35:
            breakdown["age_adjustment"] = 50
        elif age >= 25:
            breakdown["age_adjustment"] = 30
        else:
            breakdown["age_adjustment"] = 10
        score += breakdown["age_adjustment"]
        
        # Income factor
        monthly_income_millions = monthly_income / 1000000
        if monthly_income_millions >= 30:
            breakdown["income_adjustment"] = 50
        elif monthly_income_millions >= 20:
            breakdown["income_adjustment"] = 40
        elif monthly_income_millions >= 15:
            breakdown["income_adjustment"] = 30
        elif monthly_income_millions >= 10:
            breakdown["income_adjustment"] = 20
        else:
            breakdown["income_adjustment"] = 10
        score += breakdown["income_adjustment"]
        
        # Employment factor
        if years_employed >= 10:
            breakdown["employment_adjustment"] = 40
        elif years_employed >= 5:
            breakdown["employment_adjustment"] = 30
        elif years_employed >= 2:
            breakdown["employment_adjustment"] = 20
        else:
            breakdown["employment_adjustment"] = 10
        score += breakdown["employment_adjustment"]
        
        # Home ownership factor
        if home_ownership == "OWN":
            breakdown["home_ownership_adjustment"] = 30
        elif home_ownership == "MORTGAGE":
            breakdown["home_ownership_adjustment"] = 20
        else:
            breakdown["home_ownership_adjustment"] = 5
        score += breakdown["home_ownership_adjustment"]
        
        # Credit history factor
        if years_credit_history >= 10:
            breakdown["credit_history_adjustment"] = 40
        elif years_credit_history >= 5:
            breakdown["credit_history_adjustment"] = 30
        elif years_credit_history >= 2:
            breakdown["credit_history_adjustment"] = 20
        elif years_credit_history >= 1:
            breakdown["credit_history_adjustment"] = 10
        score += breakdown["credit_history_adjustment"]
        
        # Employment status factor
        if employment_status == "EMPLOYED":
            breakdown["employment_status_adjustment"] = 20
        elif employment_status == "SELF_EMPLOYED":
            breakdown["employment_status_adjustment"] = 10
        else:
            breakdown["employment_status_adjustment"] = -30
        score += breakdown["employment_status_adjustment"]
        
        # Defaults
        if currently_defaulting:
            breakdown["defaults_adjustment"] = -150
        elif has_previous_defaults:
            breakdown["defaults_adjustment"] = -80
        score += breakdown["defaults_adjustment"]
        
        # DTI ratio removed from credit score calculation (FIXED CIRCULAR LOGIC)
        # DTI should be checked separately when calculating max loan amount,
        # not as part of credit score calculation.
        # Credit score should only reflect:
        # - Payment history (defaults)
        # - Credit history length
        # - Income stability (employment)
        # - Demographics (age, home ownership)
        breakdown["debt_to_income_adjustment"] = 0
        
        # Final score
        breakdown["final_score"] = max(300, min(850, score))
        
        return breakdown
    
    def _calculate_credit_score(self, req: SimpleLoanRequest, reference_loan_amount: float) -> int:
        """Calculate estimated credit score based on customer profile"""
        
        breakdown = self.calculate_credit_score_with_breakdown(
            req.age,
            req.monthly_income,
            req.years_employed,
            req.home_ownership,
            req.years_credit_history,
            req.employment_status,
            req.has_previous_defaults,
            req.currently_defaulting,
            reference_loan_amount
        )
        
        return breakdown["final_score"]
    
    def _calculate_loan_grade(self, credit_score: int, has_defaults: bool) -> str:
        """Calculate loan grade based on credit score"""
        
        if has_defaults:
            # Poor grade if has defaults
            if credit_score >= 700:
                return "D"
            elif credit_score >= 650:
                return "E"
            else:
                return "F"
        
        # Grade based on credit score
        if credit_score >= 780:
            return "A"
        elif credit_score >= 740:
            return "B"
        elif credit_score >= 700:
            return "C"
        elif credit_score >= 660:
            return "D"
        elif credit_score >= 620:
            return "E"
        else:
            return "F"
    
    def _get_interest_rate(self, grade: str) -> float:
        """Get interest rate based on loan grade"""
        
        rates = {
            "A": 5.5,
            "B": 8.5,
            "C": 11.5,
            "D": 14.5,
            "E": 17.5,
            "F": 20.0,
            "G": 23.0
        }
        
        return rates.get(grade, 15.0)


# Singleton instance
request_converter = RequestConverter()
