from fastapi import APIRouter, HTTPException, status
from app.models.schemas import PredictionRequest, PredictionResponse, LoanOfferResponse, SimpleLoanRequest, CreditScoreResponse
from app.services.prediction_service import prediction_service
from app.services.loan_offer_service import loan_offer_service
from app.services.request_converter import request_converter
import logging
from typing import List

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/predict", response_model=PredictionResponse, status_code=status.HTTP_200_OK)
async def predict_loan(request: PredictionRequest):
    """
    🎯 Main Prediction Endpoint
    
    Predict loan default probability based on applicant information
    
    **Request Body:**
    - person_age: Age of the person (18-100)
    - person_income: Annual income
    - person_emp_length: Employment length in years
    - person_home_ownership: Home ownership status (RENT/OWN/MORTGAGE/OTHER)
    - loan_amnt: Loan amount requested
    - loan_intent: Purpose of loan (PERSONAL/EDUCATION/MEDICAL/VENTURE/etc.)
    - loan_grade: Loan grade (A-G)
    - loan_int_rate: Interest rate
    - loan_percent_income: Loan as percentage of income
    - cb_person_cred_hist_length: Credit history length in years
    - credit_score: Credit score (300-850)
    - cb_person_default_on_file: Previous default on file (Y/N)
    - previous_loan_defaults_on_file: Previous loan defaults (Y/N)
    
    **Returns:**
    - prediction: 0 (No Default) or 1 (Default)
    - probability: Probability of default (0-1)
    - risk_level: Low/Medium/High/Very High
    - confidence: Model confidence score
    - message: Risk assessment message
    """
    try:
        logger.info(f"📥 Prediction request - Age: {request.person_age}, Income: {request.person_income}")
        
        # Get prediction
        result = prediction_service.predict(request)
        
        logger.info(f"✅ Prediction complete: {result.risk_level} risk (probability: {result.probability:.2%})")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Prediction error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {str(e)}"
        )


@router.post("/batch-predict", status_code=status.HTTP_200_OK)
async def batch_predict(requests: List[PredictionRequest]):
    """
    📊 Batch Prediction Endpoint
    
    Predict multiple loan applications at once
    
    **Returns:**
    - predictions: List of prediction results
    - count: Number of predictions made
    """
    try:
        logger.info(f"📥 Batch prediction request for {len(requests)} applications")
        
        results = []
        for request in requests:
            result = prediction_service.predict(request)
            results.append(result)
        
        logger.info(f"✅ Batch prediction complete: {len(results)} results")
        
        return {
            "predictions": results, 
            "count": len(results),
            "summary": {
                "high_risk": sum(1 for r in results if r.risk_level in ["High", "Very High"]),
                "medium_risk": sum(1 for r in results if r.risk_level == "Medium"),
                "low_risk": sum(1 for r in results if r.risk_level == "Low")
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Batch prediction error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch prediction failed: {str(e)}"
        )


@router.post("/loan-offer", response_model=LoanOfferResponse, status_code=status.HTTP_200_OK)
async def get_loan_offer(request: PredictionRequest):
    """
    💰 Loan Offer Endpoint (VND Currency)
    
    Get loan approval decision and offer details in Vietnamese Dong (VND)
    
    **Request Body:**
    - person_age: Age of the person (18-100)
    - person_income: Annual income in USD (will be converted to VND)
    - person_emp_length: Employment length in years
    - person_home_ownership: Home ownership status (RENT/OWN/MORTGAGE/OTHER)
    - loan_amnt: Loan amount requested in USD (will be converted to VND)
    - loan_intent: Purpose of loan (PERSONAL/EDUCATION/MEDICAL/VENTURE/etc.)
    - loan_grade: Loan grade (A-G)
    - loan_int_rate: Interest rate
    - loan_percent_income: Loan as percentage of income
    - cb_person_cred_hist_length: Credit history length in years
    - credit_score: Credit score (300-850)
    - cb_person_default_on_file: Previous default on file (Y/N)
    - previous_loan_defaults_on_file: Previous loan defaults (Y/N)
    
    **Returns:**
    - approved: Whether loan is approved (true/false)
    - loan_amount_vnd: Approved loan amount in VND
    - requested_amount_vnd: Requested amount in VND
    - max_amount_vnd: Maximum eligible amount in VND
    - interest_rate: Annual interest rate (%)
    - monthly_payment_vnd: Estimated monthly payment in VND
    - loan_term_months: Loan term in months
    - risk_level: Risk assessment (Low/Medium/High/Very High)
    - approval_message: Detailed approval/rejection message
    
    **Note:** Exchange rate: 1 USD = 25,000 VND (approximate)
    """
    try:
        logger.info(f"💰 Loan offer request - Age: {request.person_age}, Income: {request.person_income}, Loan: {request.loan_amnt}")
        
        # Get risk prediction first
        prediction_result = prediction_service.predict(request)
        
        # Calculate loan offer
        offer = loan_offer_service.calculate_offer(
            request=request,
            probability=prediction_result.probability,
            risk_level=prediction_result.risk_level
        )
        
        logger.info(f"✅ Loan offer generated: Approved={offer.approved}, Amount={offer.loan_amount_vnd:,.0f} VND")
        
        return offer
        
    except Exception as e:
        logger.error(f"❌ Loan offer error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Loan offer calculation failed: {str(e)}"
        )


@router.post("/batch-loan-offers", status_code=status.HTTP_200_OK)
async def batch_loan_offers(requests: List[PredictionRequest]):
    """
    📊 Batch Loan Offers Endpoint (VND Currency)
    
    Process multiple loan applications and get offers in VND
    
    **Returns:**
    - offers: List of loan offer results
    - count: Number of offers processed
    - summary: Statistics of approvals and rejections
    """
    try:
        logger.info(f"📥 Batch loan offer request for {len(requests)} applications")
        
        offers = []
        for req in requests:
            # Get prediction
            prediction_result = prediction_service.predict(req)
            
            # Calculate offer
            offer = loan_offer_service.calculate_offer(
                request=req,
                probability=prediction_result.probability,
                risk_level=prediction_result.risk_level
            )
            offers.append(offer)
        
        logger.info(f"✅ Batch loan offers complete: {len(offers)} results")
        
        # Calculate summary
        approved_count = sum(1 for o in offers if o.approved)
        rejected_count = len(offers) - approved_count
        total_approved_amount = sum(o.loan_amount_vnd for o in offers if o.approved)
        
        return {
            "offers": offers,
            "count": len(offers),
            "summary": {
                "approved": approved_count,
                "rejected": rejected_count,
                "total_approved_amount_vnd": total_approved_amount,
                "approval_rate": f"{(approved_count / len(offers) * 100):.1f}%"
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Batch loan offers error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch loan offers failed: {str(e)}"
        )


@router.post("/apply", response_model=LoanOfferResponse, status_code=status.HTTP_200_OK)
async def apply_for_loan(application: SimpleLoanRequest):
    """
    🎯 Simple Loan Application Endpoint (Customer-Friendly)
    
    Apply for a loan with simple, customer-friendly information.
    The system will automatically calculate credit score and other internal metrics.
    
    **Request Body:**
    - full_name: Customer's full name
    - age: Age (18-100)
    - monthly_income: Monthly income in VND
    - employment_status: EMPLOYED, SELF_EMPLOYED, or UNEMPLOYED
    - years_employed: Years in current employment
    - home_ownership: RENT, OWN, MORTGAGE, or LIVING_WITH_PARENTS
    - loan_amount: Requested loan amount in VND
    - loan_purpose: PERSONAL, EDUCATION, MEDICAL, BUSINESS, HOME_IMPROVEMENT, or DEBT_CONSOLIDATION
    - years_credit_history: How many years have you had credit/loans? (0 if none)
    - has_previous_defaults: Have you ever defaulted on a loan? (true/false)
    - currently_defaulting: Are you currently in default? (true/false)
    
    **Returns:**
    - approved: Whether loan is approved (true/false)
    - loan_amount_vnd: Approved loan amount in VND
    - requested_amount_vnd: Requested amount in VND
    - max_amount_vnd: Maximum eligible amount in VND
    - interest_rate: Annual interest rate (%)
    - monthly_payment_vnd: Estimated monthly payment in VND
    - loan_term_months: Loan term in months
    - credit_score: Calculated credit score
    - risk_level: Risk assessment
    - approval_message: Detailed approval/rejection message
    
    **Example:**
    Send customer information and get instant loan decision!
    All amounts in Vietnamese Dong (VND).
    """
    try:
        logger.info(f"🎯 Loan application from: {application.full_name}, Amount: {application.loan_amount:,.0f} VND")
        
        # Convert simple request to internal format
        internal_request = request_converter.convert_simple_to_prediction(application)
        
        logger.info(f"📊 Calculated credit score: {internal_request.credit_score}")
        
        # Get risk prediction
        prediction_result = prediction_service.predict(internal_request)
        
        # Calculate loan offer
        offer = loan_offer_service.calculate_offer(
            request=internal_request,
            probability=prediction_result.probability,
            risk_level=prediction_result.risk_level
        )
        
        logger.info(f"✅ Application processed: Approved={offer.approved}, Amount={offer.loan_amount_vnd:,.0f} VND, Score={offer.credit_score}")
        
        return offer
        
    except Exception as e:
        logger.error(f"❌ Loan application error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Loan application processing failed: {str(e)}"
        )


@router.post("/credit-score", response_model=CreditScoreResponse, status_code=status.HTTP_200_OK)
async def calculate_credit_score(application: SimpleLoanRequest):
    """
    📊 Credit Score Calculator Endpoint (For Dashboard)
    
    Calculate credit score from customer information without applying for loan.
    Perfect for dashboard analytics and customer insights.
    
    **Request Body:**
    - full_name: Customer's full name
    - age: Age (18-100)
    - monthly_income: Monthly income in VND
    - employment_status: EMPLOYED, SELF_EMPLOYED, or UNEMPLOYED
    - years_employed: Years in current employment
    - home_ownership: RENT, OWN, MORTGAGE, or LIVING_WITH_PARENTS
    - loan_amount: Requested loan amount in VND (used for debt-to-income ratio)
    - loan_purpose: PERSONAL, EDUCATION, MEDICAL, etc.
    - years_credit_history: How many years have you had credit/loans?
    - has_previous_defaults: Have you ever defaulted on a loan?
    - currently_defaulting: Are you currently in default?
    
    **Returns:**
    - full_name: Customer name
    - credit_score: Calculated credit score (300-850)
    - loan_grade: Loan grade (A-G)
    - risk_level: Risk assessment
    - score_breakdown: Detailed breakdown showing how score was calculated
    
    **Use Cases:**
    - Display credit score on customer dashboard
    - Show score improvements over time
    - Analytics and reporting
    - Credit score tracking
    """
    try:
        logger.info(f"📊 Credit score calculation for: {application.full_name}")
        
        # Get detailed score breakdown
        score_details = request_converter.calculate_credit_score_with_breakdown(
            application.age,
            application.monthly_income,
            application.years_employed,
            application.home_ownership,
            application.years_credit_history,
            application.employment_status,
            application.has_previous_defaults,
            application.currently_defaulting,
            application.loan_amount
        )
        
        # Convert to internal format to get loan grade
        internal_request = request_converter.convert_simple_to_prediction(application)
        
        # Get risk level from prediction
        prediction_result = prediction_service.predict(internal_request)
        
        response = CreditScoreResponse(
            full_name=application.full_name,
            credit_score=score_details["final_score"],
            loan_grade=internal_request.loan_grade,
            risk_level=prediction_result.risk_level,
            score_breakdown=score_details
        )
        
        logger.info(f"✅ Credit score calculated: {response.credit_score} (Grade: {response.loan_grade})")
        
        return response
        
    except Exception as e:
        logger.error(f"❌ Credit score calculation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Credit score calculation failed: {str(e)}"
        )