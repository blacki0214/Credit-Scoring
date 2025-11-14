from pydantic import BaseModel, Field, validator
from typing import List, Dict, Optional
from enum import Enum


class EmploymentStatus(str, Enum):
    WORKING = "working"
    SELF_EMPLOYED = "self_employed"
    RETIRED = "retired"
    UNEMPLOYED = "unemployed"
    STUDENT = "student"


class CustomerInput(BaseModel):
    customer_id: str = Field(..., description="Unique customer identifier")
    age_years: float = Field(..., ge=18, le=75, description="Customer age in years")
    employment_years: float = Field(..., ge=0, le=50, description="Years of employment")
    annual_income: float = Field(..., ge=10000, le=10000000, description="Annual income in USD")
    requested_amount: float = Field(..., ge=1000, le=5000000, description="Requested loan amount in USD")
    credit_card_usage: float = Field(..., ge=0, le=200, description="Credit card usage percentage")
    days_past_due_avg: float = Field(..., ge=0, le=90, description="Average days past due")
    higher_education: bool = Field(..., description="Has higher education")
    employment_status: EmploymentStatus = Field(..., description="Employment status")
    
    class Config:
        schema_extra = {
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


class LoanEstimation(BaseModel):
    requested_amount: float
    approved_amount: float
    max_eligible_amount: float
    interest_rate: float
    loan_term_months: int
    monthly_payment: float
    recommendation: str


class PredictionResult(BaseModel):
    customer_id: str
    default_probability: float
    threshold: float
    risk_level: str
    decision: str
    confidence: float
    loan_estimation: LoanEstimation
    risk_factors: List[Dict]
    model_version: str