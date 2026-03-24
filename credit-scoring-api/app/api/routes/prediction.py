from fastapi import APIRouter, HTTPException, status, Request, Depends
from app.models.schemas import (
    PredictionRequest, PredictionResponse, LoanOfferResponse,
    SimpleLoanRequest, CreditScoreResponse, SimpleLoanApplicationResponse,
    LoanLimitResponse, LoanTermsRequest, LoanTermsResponse,
    StudentLoanRequest, StudentLoanLimitResponse, StudentCreditScoreResponse,
)
from app.services.prediction_service import prediction_service
from app.services.loan_offer_service import loan_offer_service
from app.services.smart_loan_offer import SmartLoanOfferService
from app.services.request_converter import request_converter
from app.services.feature_engineering import FeatureEngineer
from app.services.loan_limit_calculator import loan_limit_calculator
from app.services.loan_terms_calculator import loan_terms_calculator
from app.services.score_mapper import probability_to_credit_score
from app.services.student_prediction_service import student_prediction_service
from app.services.student_application_logger import student_application_logger
from app.core.security import verify_api_key
from app.auth.firebase_auth import verify_firebase_token
from app.core.config import settings
import logging
from typing import List

logger = logging.getLogger(__name__)

router = APIRouter()

# Import limiter from main app
from slowapi import Limiter
from app.core.security import get_client_ip

limiter = Limiter(key_func=get_client_ip)


@router.post("/calculate-limit", response_model=LoanLimitResponse, status_code=status.HTTP_200_OK)
@limiter.limit(f"{settings.RATE_LIMIT_CALCULATE_LIMIT}/minute")
async def calculate_loan_limit(
    request: Request,
    application: SimpleLoanRequest,
    user: dict = Depends(verify_firebase_token),
):
    """
    Calculate Loan Limit Endpoint (Step 1)
    
    Calculate credit score and maximum loan limit based on customer profile.
    This is the FIRST step in the loan application flow.
    
    *Flow:*
    1. User fills in personal information (age, income, employment, etc.)
    2. System calculates credit score
    3. System calculates maximum loan limit
    4. User sees their credit score and loan limit
    5. User proceeds to Step 2 to select loan purpose
    
    *Request Body:*
    - full_name: Customer's full name
    - age: Age (18-100)
    - monthly_income: Monthly income in VND
    - employment_status: EMPLOYED, SELF_EMPLOYED, or UNEMPLOYED
    - years_employed: Years in current employment
    - home_ownership: RENT, OWN, MORTGAGE, or LIVING_WITH_PARENTS
    - years_credit_history: Years of credit history
    - has_previous_defaults: Ever defaulted?
    - currently_defaulting: Currently in default?
    
    *Returns:*
    - credit_score: Calculated credit score (300-850)
    - loan_limit_vnd: Maximum loan amount in VND
    - risk_level: Risk assessment (Low/Medium/High/Very High)
    - approved: Whether customer qualifies
    - message: Explanation
    """
    try:
        logger.info(f"Loan limit calculation for: {application.full_name}")
        
        # Convert simple request to internal format
        internal_request = request_converter.convert_simple_to_prediction(application)
        
        # Calculate annual income
        annual_income_vnd = application.monthly_income * 12
        
        # Get ML model prediction (probability + risk level)
        prediction_result = prediction_service.predict(internal_request)
        risk_level = prediction_result.risk_level
        
        # Derive credit score from ML probability (non-linear)
        credit_score = probability_to_credit_score(prediction_result.probability)
        
        # HARD CAPS (Business Rules)
        # 1. Currently defaulting -> Auto reject, cap at 580 (Very Poor)
        if application.currently_defaulting:
            credit_score = min(credit_score, 580)
            risk_level = "Very High"
        # 2. Previous defaults -> Cap at 650 (Fair)
        elif application.has_previous_defaults:
            credit_score = min(credit_score, 650)
        # 3. Young/Unemployed -> Cap at 680 (Fair)
        elif application.age <= 22 or application.employment_status == "UNEMPLOYED":
            credit_score = min(credit_score, 680)
        # 4. New to credit -> Cap at 700 (Good)
        elif application.years_credit_history == 0:
            credit_score = min(credit_score, 700)
        # 5. Low income (<10M) -> Cap at 720 (Good)
        elif application.monthly_income < 10000000:
            credit_score = min(credit_score, 720)
        
        # Check minimum credit score
        min_credit_score = 600
        if credit_score < min_credit_score:
            return LoanLimitResponse(
                credit_score=credit_score,
                loan_limit_vnd=0.0,
                risk_level="Very High",
                approved=False,
                message=(
                    f"Credit score ({credit_score}) is below minimum requirement ({min_credit_score}). "
                    f"Please improve your credit history before applying."
                )
            )
        
        # Calculate maximum loan limit
        max_loan, limit_reason = loan_limit_calculator.calculate_max_loan(
            credit_score=credit_score,
            annual_income_vnd=annual_income_vnd,
            monthly_income_vnd=application.monthly_income,
            risk_level=risk_level
        )
        
        # Check approval threshold (30% default probability)
        approved = prediction_result.probability < 0.30
        
        if not approved:
            message = (
                f"Credit score: {credit_score}. Risk level: {risk_level}. "
                f"Default probability ({prediction_result.probability:.1%}) exceeds acceptable threshold. "
                f"Loan limit: 0 VND."
            )
            max_loan = 0.0
        else:
            message = (
                f"Credit score: {credit_score}. Risk level: {risk_level}. "
                f"Maximum loan limit: {max_loan:,.0f} VND. {limit_reason}"
            )
        
        logger.info(
            f"Loan limit calculated - Credit score: {credit_score}, "
            f"Limit: {max_loan:,.0f} VND, Risk: {risk_level}, Approved: {approved}"
        )
        
        return LoanLimitResponse(
            credit_score=credit_score,
            loan_limit_vnd=max_loan,
            risk_level=risk_level,
            approved=approved,
            message=message
        )
        
    except Exception as e:
        logger.error(f"Loan limit calculation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Loan limit calculation failed: {str(e)}"
        )


@router.post("/calculate-terms", response_model=LoanTermsResponse, status_code=status.HTTP_200_OK)
@limiter.limit(f"{settings.RATE_LIMIT_CALCULATE_TERMS}/minute")
async def calculate_loan_terms(
    request: Request,
    loan_terms_request: LoanTermsRequest,
    user: dict = Depends(verify_firebase_token),
):
    """
    Calculate Loan Terms Endpoint (Step 2)
    
    Calculate loan terms (interest rate, duration, monthly payment) based on
    loan purpose and credit score.
    
    This is the SECOND step in the loan application flow.
    
    *Flow:*
    1. User has credit score and loan limit from Step 1
    2. User selects loan purpose (HOME, CAR, BUSINESS, etc.)
    3. User enters desired loan amount (must be ≤ loan limit)
    4. System calculates interest rate, term, and monthly payment
    
    *Request Body:*
    - loan_amount: Desired loan amount in VND
    - loan_purpose: Purpose (HOME, CAR, BUSINESS, EDUCATION, etc.)
    - credit_score: Credit score from Step 1
    
    *Returns:*
    - loan_amount_vnd: Loan amount
    - loan_purpose: Purpose
    - interest_rate: Annual interest rate %
    - loan_term_months: Loan duration in months
    - monthly_payment_vnd: Monthly payment
    - total_payment_vnd: Total payment over term
    - total_interest_vnd: Total interest paid
    - rate_explanation: How rate was calculated
    - term_explanation: Why this term
    """
    try:
        logger.info(
            f"Loan terms calculation - Amount: {loan_terms_request.loan_amount:,.0f} VND, "
            f"Purpose: {loan_terms_request.loan_purpose}, Credit score: {loan_terms_request.credit_score}"
        )
        
        # Calculate loan terms
        loan_terms = loan_terms_calculator.calculate_loan_terms(
            loan_amount=loan_terms_request.loan_amount,
            loan_purpose=loan_terms_request.loan_purpose,
            credit_score=loan_terms_request.credit_score
        )
        
        logger.info(
            f"Loan terms calculated - Rate: {loan_terms['interest_rate']}%, "
            f"Term: {loan_terms['loan_term_months']} months, "
            f"Monthly: {loan_terms['monthly_payment_vnd']:,.0f} VND"
        )
        
        return LoanTermsResponse(
            loan_amount_vnd=loan_terms_request.loan_amount,
            loan_purpose=loan_terms_request.loan_purpose,
            interest_rate=loan_terms["interest_rate"],
            loan_term_months=loan_terms["loan_term_months"],
            monthly_payment_vnd=loan_terms["monthly_payment_vnd"],
            total_payment_vnd=loan_terms["total_payment_vnd"],
            total_interest_vnd=loan_terms["total_interest_vnd"],
            rate_explanation=loan_terms["rate_explanation"],
            term_explanation=loan_terms["term_explanation"]
        )
        
    except Exception as e:
        logger.error(f"Loan terms calculation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Loan terms calculation failed: {str(e)}"
        )



@router.post("/predict", response_model=PredictionResponse, status_code=status.HTTP_200_OK)
async def predict_loan(request: PredictionRequest):
    """
    Main Prediction Endpoint
    
    Predict loan default probability based on applicant information
    
    *Request Body:*
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
    
    *Returns:*
    - prediction: 0 (No Default) or 1 (Default)
    - probability: Probability of default (0-1)
    - risk_level: Low/Medium/High/Very High
    - confidence: Model confidence score
    - message: Risk assessment message
    """
    try:
        logger.info(f"Prediction request - Age: {request.person_age}, Income: {request.person_income}")
        
        # Get prediction
        result = prediction_service.predict(request)
        
        logger.info(f"Prediction complete: {result.risk_level} risk (probability: {result.probability:.2%})")
        
        return result
        
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {str(e)}"
        )


@router.post("/batch-predict", status_code=status.HTTP_200_OK)
@limiter.limit(f"{settings.RATE_LIMIT_BATCH}/minute")
async def batch_predict(
    request: Request,
    prediction_requests: List[PredictionRequest],
    api_key: str = Depends(verify_api_key)
):
    """
    Batch Prediction Endpoint
    
    Predict multiple loan applications at once
    
    *Returns:*
    - predictions: List of prediction results
    - count: Number of predictions made
    """
    try:
        logger.info(f"Batch prediction request - {len(prediction_requests)} applications")
        
        # Process all predictions
        predictions = []
        for pred_request in prediction_requests:
            result = prediction_service.predict(pred_request)
            predictions.append(result)
        
        # Calculate summary statistics
        high_risk_count = sum(1 for p in predictions if p.risk_level == "HIGH")
        medium_risk_count = sum(1 for p in predictions if p.risk_level == "MEDIUM")
        low_risk_count = sum(1 for p in predictions if p.risk_level == "LOW")
        
        logger.info(
            f"Batch prediction complete - High: {high_risk_count}, "
            f"Medium: {medium_risk_count}, Low: {low_risk_count}"
        )
        
        return {
            "predictions": predictions,
            "count": len(predictions),
            "summary": {
                "high_risk": high_risk_count,
                "medium_risk": medium_risk_count,
                "low_risk": low_risk_count
            }
        }
        
    except Exception as e:
        logger.error(f"Batch prediction error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch prediction failed: {str(e)}"
        )


@router.post("/loan-offer", response_model=LoanOfferResponse, status_code=status.HTTP_200_OK)
async def get_loan_offer(request: PredictionRequest):
    """
    Loan Offer Endpoint (VND Currency)
    
    Get loan approval decision and offer details in Vietnamese Dong (VND)
    
    *Request Body:*
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
    
    *Returns:*
    - approved: Whether loan is approved (true/false)
    - loan_amount_vnd: Approved loan amount in VND
    - requested_amount_vnd: Requested amount in VND
    - max_amount_vnd: Maximum eligible amount in VND
    - interest_rate: Annual interest rate (%)
    - monthly_payment_vnd: Estimated monthly payment in VND
    - loan_term_months: Loan term in months
    - risk_level: Risk assessment (Low/Medium/High/Very High)
    - approval_message: Detailed approval/rejection message
    
    *Note:* Exchange rate: 1 USD = 25,000 VND (approximate)
    """
    try:
        logger.info(f"Loan offer request - Age: {request.person_age}, Income: {request.person_income}, Loan: {request.loan_amnt}")
        
        # Get risk prediction first
        prediction_result = prediction_service.predict(request)
        
        # Calculate loan offer
        offer = loan_offer_service.calculate_offer(
            request=request,
            probability=prediction_result.probability,
            risk_level=prediction_result.risk_level
        )
        
        logger.info(f"Loan offer generated: Approved={offer.approved}, Amount={offer.loan_amount_vnd:,.0f} VND")
        
        return offer
        
    except Exception as e:
        logger.error(f"Loan offer error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Loan offer calculation failed: {str(e)}"
        )


@router.post("/batch-loan-offers", status_code=status.HTTP_200_OK)
@limiter.limit(f"{settings.RATE_LIMIT_BATCH}/minute")
async def batch_loan_offers(
    request: Request,
    prediction_requests: List[PredictionRequest],
    api_key: str = Depends(verify_api_key)
):
    """
    Batch Loan Offers Endpoint (VND Currency)
    
    Process multiple loan applications and get offers in VND
    
    *Returns:*
    - offers: List of loan offer results
    - count: Number of offers processed
    - summary: Statistics of approvals and rejections
    """
    try:
        logger.info(f"Batch loan offers request - {len(prediction_requests)} applications")
        
        # Process all loan offers
        offers = []
        for pred_request in prediction_requests:
            offer = loan_offer_service.generate_offer(pred_request.model_dump())
            offers.append(offer)
        
        logger.info(f"Batch loan offers complete: {len(offers)} results")
        
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
        logger.error(f"Batch loan offers error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch loan offers failed: {str(e)}"
        )


@router.post("/apply", response_model=SimpleLoanApplicationResponse, status_code=status.HTTP_200_OK)
@limiter.limit(f"{settings.RATE_LIMIT_APPLY}/minute")
async def apply_for_loan(
    request: Request,
    application: SimpleLoanRequest,
    user: dict = Depends(verify_firebase_token),
):
    """
    Loan Application Endpoint - Get Credit Score and Loan Limit
    
    Submit your loan application to get:
    1. Your credit score (300-850)
    2. Maximum loan amount you qualify for
    
    *Request Body:*
    - full_name: Customer's full name
    - age: Age (18-100)
    - monthly_income: Monthly income in VND
    - employment_status: EMPLOYED, SELF_EMPLOYED, or UNEMPLOYED
    - years_employed: Years in current employment
    - home_ownership: RENT, OWN, MORTGAGE, or LIVING_WITH_PARENTS
    - years_credit_history: How many years have you had credit/loans? (0 if none)
    - has_previous_defaults: Have you ever defaulted on a loan? (true/false)
    - currently_defaulting: Are you currently in default? (true/false)
    
    *Returns:*
    - credit_score: Your calculated credit score (300-850)
    - loan_limit_vnd: Maximum loan amount in VND
    """
    try:
        logger.info(f"Loan application from: {application.full_name}")
        
        # Convert simple request to full internal format
        internal_request = request_converter.convert_simple_to_prediction(application)
        
        # Get ML model prediction (probability + risk level)
        prediction_result = prediction_service.predict(internal_request)
        risk_level = prediction_result.risk_level
        
        # Get proper credit score
        credit_score = probability_to_credit_score(prediction_result.probability)
        
        # EXACT SAME HARD CAPS AS /calculate-limit
        if application.currently_defaulting:
            credit_score = min(credit_score, 580)
            risk_level = "Very High"
        elif application.has_previous_defaults:
            credit_score = min(credit_score, 650)
        elif application.age <= 22 or application.employment_status == "UNEMPLOYED":
            credit_score = min(credit_score, 680)
        elif application.years_credit_history == 0:
            credit_score = min(credit_score, 700)
        elif application.monthly_income < 10000000:
            credit_score = min(credit_score, 720)
        
        logger.info(f"Calculated credit score: {credit_score}")
        
        # Calculate annual income
        annual_income_vnd = application.monthly_income * 12
        
        # Generate smart loan offer (without loan_purpose - only credit score and limit)
        smart_service = SmartLoanOfferService()
        offer = smart_service.generate_offer(
            request_dict=internal_request.model_dump(),
            age=application.age,
            years_employed=application.years_employed,
            employment_status=application.employment_status,
            home_ownership=application.home_ownership,
            loan_purpose=None,  # Not needed for credit score/limit calculation
            annual_income_vnd=annual_income_vnd,
            monthly_income_vnd=application.monthly_income,
            credit_score=credit_score # Use the potentially capped credit score
        )
        
        # Return only credit score and loan limit
        response = SimpleLoanApplicationResponse(
            credit_score=offer['credit_score'],
            loan_limit_vnd=offer['max_amount_vnd']
        )
        
        logger.info(
            f"Application processed: Score={response.credit_score}, "
            f"Limit={response.loan_limit_vnd:,.0f} VND"
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Loan application error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Loan application failed: {str(e)}"
        )


@router.post("/credit-score", response_model=CreditScoreResponse, status_code=status.HTTP_200_OK)
@limiter.limit(f"{settings.RATE_LIMIT_CALCULATE_LIMIT}/minute")
async def calculate_credit_score(
    request: Request,
    application: SimpleLoanRequest,
    user: dict = Depends(verify_firebase_token),
):
    """
    Credit Score Calculator Endpoint (For Dashboard)
    
    Calculate credit score from customer information without applying for loan.
    Perfect for dashboard analytics and customer insights.
    
    *Request Body:*
    - full_name: Customer's full name
    - age: Age (18-100)
    - monthly_income: Monthly income in VND
    - employment_status: EMPLOYED, SELF_EMPLOYED, or UNEMPLOYED
    - years_employed: Years in current employment
    - home_ownership: RENT, OWN, MORTGAGE, or LIVING_WITH_PARENTS
    - years_credit_history: How many years have you had credit/loans?
    - has_previous_defaults: Have you ever defaulted on a loan?
    - currently_defaulting: Are you currently in default?
    
    *Returns:*
    - full_name: Customer name
    - credit_score: Calculated credit score (300-850)
    - loan_grade: Loan grade (A-G)
    - risk_level: Risk assessment
    - score_breakdown: Detailed breakdown showing how score was calculated
    
    *Use Cases:*
    - Display credit score on customer dashboard
    - Show score improvements over time
    - Analytics and reporting
    - Credit score tracking
    """
    try:
        logger.info(f"Credit score calculation for: {application.full_name}")
        
        # For credit score calculation, use a standard 3-year personal loan as reference
        reference_loan_amount = application.monthly_income * 12 * 2  # 2x annual income
        
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
            reference_loan_amount
        )
        
        # ML Pipeline calculation
        internal_request = request_converter.convert_simple_to_prediction(application)
        prediction_result = prediction_service.predict(internal_request)
        credit_score = probability_to_credit_score(prediction_result.probability)
        risk_level = prediction_result.risk_level
        
        # EXACT SAME HARD CAPS AS /calculate-limit
        if application.currently_defaulting:
            credit_score = min(credit_score, 580)
            risk_level = "Very High"
        elif application.has_previous_defaults:
            credit_score = min(credit_score, 650)
        elif application.age <= 22 or application.employment_status == "UNEMPLOYED":
            credit_score = min(credit_score, 680)
        elif application.years_credit_history == 0:
            credit_score = min(credit_score, 700)
        elif application.monthly_income < 10000000:
            credit_score = min(credit_score, 720)
        
        response = CreditScoreResponse(
            full_name=application.full_name,
            credit_score=credit_score, # Use the potentially capped credit score
            loan_grade=internal_request.loan_grade,
            risk_level=risk_level, # Use the potentially updated risk_level
            score_breakdown=score_details
        )
        
        logger.info(f"Credit score calculated: {response.credit_score} (Grade: {response.loan_grade})")
        
        return response
        
    except Exception as e:
        logger.error(f"Credit score calculation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Credit score calculation failed: {str(e)}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# Student Alternative Model Endpoint
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/student/credit-score", response_model=StudentCreditScoreResponse, status_code=status.HTTP_200_OK)
@limiter.limit(f"{settings.RATE_LIMIT_CALCULATE_LIMIT}/minute")
async def student_credit_score(
    request: Request,
    application: StudentLoanRequest,
    user: dict = Depends(verify_firebase_token),
):
    """
    Student Credit Score Endpoint.

    Returns only student scoring result (no loan limit calculation).
    """
    if not student_prediction_service.is_ready:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Student model not loaded. Please contact support.",
        )

    try:
        logger.info(f"Student credit score request — user: {user.get('uid', 'unknown')}")

        # Hard gate aligned with student loan policy
        if application.academic_year == 1 and application.gpa_latest < 2.0:
            return StudentCreditScoreResponse(
                credit_score=600,
                risk_level="Very High",
                approved=False,
                message=(
                    "Sinh viên năm nhất cần GPA ≥ 2.0 để đủ điều kiện. "
                    "Hãy cải thiện kết quả học tập và thử lại."
                ),
                default_probability=None,
                approval_threshold=DEFAULT_STUDENT_THRESHOLD,
                score_model="student_xgboost_phase1",
                score_range="600-850",
            )

        raw = application.model_dump()
        default_prob, risk_level, credit_score = student_prediction_service.predict(raw)
        approved = default_prob < DEFAULT_STUDENT_THRESHOLD

        message = (
            f"Điểm tín dụng sinh viên: {credit_score}. "
            f"Mức rủi ro: {risk_level}."
        )

        return StudentCreditScoreResponse(
            credit_score=credit_score,
            risk_level=risk_level,
            approved=approved,
            message=message,
            default_probability=default_prob,
            approval_threshold=DEFAULT_STUDENT_THRESHOLD,
            score_model="student_xgboost_phase1",
            score_range="600-850",
        )

    except Exception as e:
        logger.error(f"Student credit score calculation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Student credit score calculation failed: {str(e)}",
        )

@router.post("/student/calculate-limit", response_model=StudentLoanLimitResponse, status_code=status.HTTP_200_OK)
@limiter.limit(f"{settings.RATE_LIMIT_CALCULATE_LIMIT}/minute")
async def student_calculate_limit(
    request: Request,
    application: StudentLoanRequest,
    user: dict = Depends(verify_firebase_token),
):
    """
    Student Loan Limit Endpoint — Alternative Model (XGBoost)

    Calculates credit score and loan limit (5M–10M VND) for students
    using the alternative credit scoring model trained on student profiles.

    *Hard rules applied before model:*
    - Year-1 students with GPA < 2.0 are auto-rejected
    - Loan amount must be 5,000,000–10,000,000 VND (enforced by schema)
    - Risk = High / Very High → loan capped at 5,000,000 VND

    *Returns the same shape as /calculate-limit for Flutter compatibility.*
    """
    if not student_prediction_service.is_ready:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Student model not loaded. Please contact support.",
        )

    try:
        logger.info(f"Student loan request — user: {user.get('uid', 'unknown')}")
        user_id = user.get("uid", "unknown")
        raw = application.model_dump()

        # ── Hard gate: Year-1 + low GPA ────────────────────────────────────
        if application.academic_year == 1 and application.gpa_latest < 2.0:
            try:
                student_application_logger.log_application(
                    user_id=user_id,
                    request_payload=raw,
                    credit_score=600,
                    loan_limit_vnd=0.0,
                    risk_level="Very High",
                    approved=False,
                    model_score=None,
                    status="rejected",
                    reason="hard_gate_year1_low_gpa",
                )
            except Exception as log_error:
                logger.warning(
                    "Student application logging failed for hard gate: %s", log_error
                )

            return StudentLoanLimitResponse(
                credit_score=600,
                loan_limit_vnd=0.0,
                risk_level="Very High",
                approved=False,
                message=(
                    "Sinh viên năm nhất cần GPA ≥ 2.0 để đủ điều kiện vay. "
                    "Hãy cải thiện kết quả học tập và thử lại."
                ),
                default_probability=None,
                approval_threshold=DEFAULT_STUDENT_THRESHOLD,
                score_model="student_xgboost_phase1",
                score_range="600-850",
            )

        # ── Model prediction ────────────────────────────────────────────────
        default_prob, risk_level, credit_score = student_prediction_service.predict(raw)

        # ── Loan limit (5M–10M hard cap) ────────────────────────────────────
        loan_limit, limit_reason = loan_limit_calculator.calculate_student_loan(
            credit_score=credit_score,
            risk_level=risk_level,
        )

        # ── Approval decision ───────────────────────────────────────────────
        approved = default_prob < DEFAULT_STUDENT_THRESHOLD

        if not approved:
            message = (
                f"Điểm tín dụng: {credit_score}. Xác suất rủi ro ({default_prob:.1%}) "
                f"vượt ngưỡng chấp nhận. Hạn mức: 0 VND."
            )
            loan_limit = 0.0
        else:
            message = (
                f"Điểm tín dụng: {credit_score}. {limit_reason}. "
                f"Hạn mức vay: {loan_limit:,.0f} VND."
            )

        try:
            student_application_logger.log_application(
                user_id=user_id,
                request_payload=raw,
                credit_score=credit_score,
                loan_limit_vnd=loan_limit,
                risk_level=risk_level,
                approved=approved,
                model_score=default_prob,
                status="scored",
            )
        except Exception as log_error:
            logger.warning("Student application logging failed: %s", log_error)

        logger.info(
            f"Student loan calculated — score={credit_score}, "
            f"limit={loan_limit:,.0f} VND, risk={risk_level}, approved={approved}"
        )

        return StudentLoanLimitResponse(
            credit_score=credit_score,
            loan_limit_vnd=loan_limit,
            risk_level=risk_level,
            approved=approved,
            message=message,
            default_probability=default_prob,
            approval_threshold=DEFAULT_STUDENT_THRESHOLD,
            score_model="student_xgboost_phase1",
            score_range="600-850",
        )

    except Exception as e:
        logger.error(f"Student loan calculation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Student loan calculation failed: {str(e)}",
        )


# Approval threshold for student model (conservative)
DEFAULT_STUDENT_THRESHOLD = 0.45