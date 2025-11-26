from pydantic import BaseModel, Field, validator, ConfigDict
from typing import List, Dict, Optional
from enum import Enum


class EmploymentStatus(str, Enum):
    WORKING = "working"
    SELF_EMPLOYED = "self_employed"
    RETIRED = "retired"
    UNEMPLOYED = "unemployed"
    STUDENT = "student"


class CustomerInput(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "customer_id": "CUST12345",
                "age_years": 35,
                "employment_years": 5,
                "annual_income": 50000,
                "requested_amount": 150000,
                "credit_card_usage": 42,
                "days_past_due_avg": 3,
                "higher_education": True,
                "employment_status": "working"
            }
        }
    )
    
    customer_id: str = Field(..., description="Unique customer identifier")
    age_years: float = Field(..., ge=18, le=75, description="Customer age in years")
    employment_years: float = Field(..., ge=0, le=50, description="Years of employment")
    annual_income: float = Field(..., ge=10000, le=10000000, description="Annual income in USD")
    requested_amount: float = Field(..., ge=1000, le=5000000, description="Requested loan amount in USD")
    credit_card_usage: float = Field(..., ge=0, le=200, description="Credit card usage percentage")
    days_past_due_avg: float = Field(..., ge=0, le=90, description="Average days past due")
    higher_education: bool = Field(..., description="Has higher education")
    employment_status: EmploymentStatus = Field(..., description="Employment status")


class LoanEstimation(BaseModel):
    requested_amount: float
    approved_amount: float
    max_eligible_amount: float
    interest_rate: float
    loan_term_months: int
    monthly_payment: float
    recommendation: str


class PredictionResult(BaseModel):
    model_config = ConfigDict(protected_namespaces=())  # Fix model_version warning
    
    customer_id: str
    default_probability: float
    threshold: float
    risk_level: str
    decision: str
    confidence: float
    loan_estimation: LoanEstimation
    risk_factors: List[Dict]
    model_version: str  # Now OK with protected_namespaces=()


class SimpleLoanRequest(BaseModel):
    """Simplified customer-friendly loan request"""
    
    # Personal Information
    full_name: str = Field(..., description="Customer's full name")
    age: int = Field(..., description="Age", ge=18, le=100)
    monthly_income: float = Field(..., description="Monthly income in VND", ge=0)
    employment_status: str = Field(..., description="Employment status (EMPLOYED, SELF_EMPLOYED, UNEMPLOYED)")
    years_employed: float = Field(..., description="Years in current employment", ge=0)
    
    # Residence Information
    home_ownership: str = Field(..., description="Home ownership (RENT, OWN, MORTGAGE, LIVING_WITH_PARENTS)")
    
    # Loan Details
    loan_amount: float = Field(..., description="Requested loan amount in VND", ge=0)
    loan_purpose: str = Field(..., description="Loan purpose (PERSONAL, EDUCATION, MEDICAL, BUSINESS, HOME_IMPROVEMENT, DEBT_CONSOLIDATION)")
    
    # Credit History (Simple questions)
    years_credit_history: int = Field(0, description="How many years have you had credit/loans?", ge=0)
    has_previous_defaults: bool = Field(False, description="Have you ever defaulted on a loan?")
    currently_defaulting: bool = Field(False, description="Are you currently in default on any loan?")
    
    class Config:
        json_schema_extra = {
            "example": {
                "full_name": "Nguyen Van A",
                "age": 30,
                "monthly_income": 15000000,
                "employment_status": "EMPLOYED",
                "years_employed": 5.0,
                "home_ownership": "RENT",
                "loan_amount": 100000000,
                "loan_purpose": "PERSONAL",
                "years_credit_history": 3,
                "has_previous_defaults": False,
                "currently_defaulting": False
            }
        }


class PredictionRequest(BaseModel):
    """Request schema for credit scoring prediction"""
    
    # Personal Information
    person_age: int = Field(..., description="Age of the person", ge=18, le=100)
    person_income: float = Field(..., description="Annual income", ge=0)
    person_emp_length: float = Field(..., description="Employment length in years", ge=0)
    person_home_ownership: str = Field(..., description="Home ownership status (RENT, OWN, MORTGAGE, OTHER)")
    
    # Loan Information
    loan_amnt: float = Field(..., description="Loan amount", ge=0)
    loan_intent: str = Field(..., description="Loan intent (PERSONAL, EDUCATION, MEDICAL, VENTURE, etc.)")
    loan_grade: str = Field(..., description="Loan grade (A-G)")
    loan_int_rate: float = Field(..., description="Interest rate", ge=0, le=100)
    loan_percent_income: float = Field(..., description="Loan as percentage of income", ge=0, le=1)
    
    # Credit History
    cb_person_cred_hist_length: int = Field(..., description="Credit history length in years", ge=0)
    credit_score: int = Field(..., description="Credit score", ge=300, le=850)
    cb_person_default_on_file: str = Field(..., description="Default on file (Y/N)")
    previous_loan_defaults_on_file: str = Field(..., description="Previous loan defaults (Y/N)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "person_age": 30,
                "person_income": 60000,
                "person_emp_length": 5.0,
                "person_home_ownership": "MORTGAGE",
                "loan_amnt": 15000,
                "loan_intent": "PERSONAL",
                "loan_grade": "B",
                "loan_int_rate": 8.5,
                "loan_percent_income": 0.25,
                "cb_person_cred_hist_length": 8,
                "credit_score": 720,
                "cb_person_default_on_file": "N",
                "previous_loan_defaults_on_file": "N"
            }
        }


class LoanOfferResponse(BaseModel):
    """Simplified loan offer response in VND"""
    
    approved: bool = Field(..., description="Whether the loan is approved")
    loan_amount_vnd: float = Field(..., description="Approved loan amount in VND")
    requested_amount_vnd: float = Field(..., description="Requested loan amount in VND")
    max_amount_vnd: float = Field(..., description="Maximum eligible loan amount in VND")
    interest_rate: float = Field(..., description="Annual interest rate (%)")
    monthly_payment_vnd: Optional[float] = Field(None, description="Estimated monthly payment in VND")
    loan_term_months: Optional[int] = Field(None, description="Loan term in months")
    credit_score: int = Field(..., description="Customer's credit score (300-850)")
    risk_level: str = Field(..., description="Risk level (Low, Medium, High, Very High)")
    approval_message: str = Field(..., description="Approval or rejection message")
    
    class Config:
        json_schema_extra = {
            "example": {
                "approved": True,
                "loan_amount_vnd": 375000000,
                "requested_amount_vnd": 375000000,
                "max_amount_vnd": 500000000,
                "interest_rate": 8.5,
                "monthly_payment_vnd": 11500000,
                "loan_term_months": 36,
                "credit_score": 720,
                "risk_level": "Low",
                "approval_message": "Loan approved! Low risk applicant."
            }
        }


class PredictionResponse(BaseModel):
    """Response schema for credit scoring prediction"""
    
    prediction: int = Field(..., description="Predicted class (0=No Default, 1=Default)")
    probability: float = Field(..., description="Probability of default", ge=0, le=1)
    risk_level: str = Field(..., description="Risk level (Low, Medium, High, Very High)")
    confidence: Optional[float] = Field(None, description="Model confidence score", ge=0, le=1)
    message: Optional[str] = Field(None, description="Additional information or warnings")
    
    class Config:
        json_schema_extra = {
            "example": {
                "prediction": 0,
                "probability": 0.25,
                "risk_level": "Low",
                "confidence": 0.95,
                "message": "Low default risk"
            }
        }


class HealthResponse(BaseModel):
    """Response schema for health check"""
    
    status: str
    version: str
    models_loaded: bool


class CreditScoreResponse(BaseModel):
    """Response schema for credit score calculation"""
    
    full_name: str = Field(..., description="Customer's full name")
    credit_score: int = Field(..., description="Calculated credit score (300-850)")
    loan_grade: str = Field(..., description="Loan grade (A-G)")
    risk_level: str = Field(..., description="Risk level assessment")
    score_breakdown: Dict = Field(..., description="Breakdown of score calculation")
    
    class Config:
        json_schema_extra = {
            "example": {
                "full_name": "Nguyen Van A",
                "credit_score": 785,
                "loan_grade": "B",
                "risk_level": "Low",
                "score_breakdown": {
                    "base_score": 650,
                    "age_adjustment": 30,
                    "income_adjustment": 40,
                    "employment_adjustment": 35,
                    "home_ownership_adjustment": 20,
                    "credit_history_adjustment": 20,
                    "employment_status_adjustment": 10,
                    "defaults_adjustment": 0,
                    "debt_to_income_adjustment": -20,
                    "final_score": 785
                }
            }
        }


class ModelInfoResponse(BaseModel):
    """Response schema for model information"""
    
    model_type: str
    models_loaded: bool
    metadata: Optional[dict] = None