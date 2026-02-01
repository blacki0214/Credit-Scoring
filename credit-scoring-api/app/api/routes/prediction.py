from fastapi import APIRouter, HTTPException, status
from app.models.schemas import (
    PredictionRequest, PredictionResponse, LoanOfferResponse, 
    SimpleLoanRequest, CreditScoreResponse,
    LoanLimitResponse, LoanTermsRequest, LoanTermsResponse  # NEW SCHEMAS
)
from app.services.prediction_service import prediction_service
from app.services.loan_offer_service import loan_offer_service
from app.services.smart_loan_offer import SmartLoanOfferService
from app.services.request_converter import request_converter
from app.services.feature_engineering import FeatureEngineer
from app.services.loan_limit_calculator import loan_limit_calculator  # NEW
from app.services.loan_terms_calculator import loan_terms_calculator  # NEW
import logging
from typing import List

logger = logging.getLogger(_name_)

router = APIRouter()


@router.post("/calculate-limit", response_model=LoanLimitResponse, status_code=status.HTTP_200_OK)
async def calculate_loan_limit(application: SimpleLoanRequest):
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
    - loan_purpose: Loan purpose (for reference only, not used in limit calculation)
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
        
        # Convert simple request to internal format and calculate credit score
        internal_request = request_converter.convert_simple_to_prediction(application)
        credit_score = internal_request.credit_score
        
        # Calculate annual income
        annual_income_vnd = application.monthly_income * 12
        
        # Get ML model risk assessment
        prediction_result = prediction_service.predict(internal_request)
        risk_level = prediction_result.risk_level
        
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
async def calculate_loan_terms(request: LoanTermsRequest):
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
            f"Loan terms calculation - Amount: {request.loan_amount:,.0f} VND, "
            f"Purpose: {request.loan_purpose}, Credit score: {request.credit_score}"
        )
        
        # Calculate loan terms
        loan_terms = loan_terms_calculator.calculate_loan_terms(
            loan_amount=request.loan_amount,
            loan_purpose=request.loan_purpose,
            credit_score=request.credit_score
        )
        
        logger.info(
            f"Loan terms calculated - Rate: {loan_terms['interest_rate']}%, "
            f"Term: {loan_terms['loan_term_months']} months, "
            f"Monthly: {loan_terms['monthly_payment_vnd']:,.0f} VND"
        )
        
        return LoanTermsResponse(
            loan_amount_vnd=request.loan_amount,
            loan_purpose=request.loan_purpose,
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
async def batch_predict(requests: List[PredictionRequest]):
    """
    Batch Prediction Endpoint
    
    Predict multiple loan applications at once
    
    *Returns:*
    - predictions: List of prediction results
    - count: Number of predictions made
    """
    try:
        logger.info(f"Batch prediction request for {len(requests)} applications")
        
        results = []
        for request in requests:
            result = prediction_service.predict(request)
            results.append(result)
        
        logger.info(f"Batch prediction complete: {len(results)} results")
        
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
async def batch_loan_offers(requests: List[PredictionRequest]):
    """
    Batch Loan Offers Endpoint (VND Currency)
    
    Process multiple loan applications and get offers in VND
    
    *Returns:*
    - offers: List of loan offer results
    - count: Number of offers processed
    - summary: Statistics of approvals and rejections
    """
    try:
        logger.info(f"Batch loan offer request for {len(requests)} applications")
        
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


@router.post("/apply", response_model=LoanOfferResponse, status_code=status.HTTP_200_OK)
async def apply_for_loan(application: SimpleLoanRequest):
    """
    Smart Loan Recommendation Endpoint
    
    Get personalized loan recommendation based on your profile.
    The system automatically:
    1. Calculates your credit score
    2. Determines your loan tier (PLATINUM/GOLD/SILVER/BRONZE)
    3. Recommends maximum loan amount you qualify for
    4. Assesses risk and sets interest rate
    
    *NO NEED to specify loan amount* - the system calculates the maximum you can safely borrow!
    
    *Request Body:*
    - full_name: Customer's full name
    - age: Age (18-100)
    - monthly_income: Monthly income in VND
    - employment_status: EMPLOYED, SELF_EMPLOYED, or UNEMPLOYED
    - years_employed: Years in current employment
    - home_ownership: RENT, OWN, MORTGAGE, or LIVING_WITH_PARENTS
    - loan_purpose: HOME, CAR, BUSINESS, EDUCATION, MEDICAL, DEBT_CONSOLIDATION, HOME_IMPROVEMENT, or PERSONAL
    - years_credit_history: How many years have you had credit/loans? (0 if none)
    - has_previous_defaults: Have you ever defaulted on a loan? (true/false)
    - currently_defaulting: Are you currently in default? (true/false)
    
    *Returns:*
    - approved: Whether you qualify for a loan (true/false)
    - loan_amount_vnd: Maximum recommended loan amount in VND
    - max_amount_vnd: Maximum eligible amount in VND
    - interest_rate: Annual interest rate (%)
    - monthly_payment_vnd: Estimated monthly payment in VND
    - loan_term_months: Loan term in months
    - credit_score: Your calculated credit score
    - risk_level: Risk assessment
    - loan_tier: Your tier (PLATINUM/GOLD/SILVER/BRONZE)
    - tier_reason: Why you were assigned this tier
    - approval_message: Detailed approval/rejection message
    
    *Loan Tiers:*
    - PLATINUM: Best rates, highest amounts (4.5x+ annual income)
    - GOLD: Great rates, high amounts (3.5x annual income)
    - SILVER: Good rates, moderate amounts (2.5x annual income)
    - BRONZE: Standard rates, conservative amounts (1.5x annual income)
    """
    try:
        logger.info(f"Smart loan application from: {application.full_name}, Purpose: {application.loan_purpose}")
        
        # Convert simple request to full internal format
        internal_request = request_converter.convert_simple_to_prediction(application)
        
        logger.info(f"Calculated credit score: {internal_request.credit_score}")
        
        # Calculate annual income
        annual_income_vnd = application.monthly_income * 12
        
        # Generate smart loan offer with tier-based calculation
        smart_service = SmartLoanOfferService()
        offer = smart_service.generate_offer(
            request_dict=internal_request.model_dump(),
            age=application.age,
            years_employed=application.years_employed,
            employment_status=application.employment_status,
            home_ownership=application.home_ownership,
            loan_purpose=application.loan_purpose,
            annual_income_vnd=annual_income_vnd,
            monthly_income_vnd=application.monthly_income,
            credit_score=internal_request.credit_score
        )
        
        logger.info(
            f"Application processed: Tier={offer['loan_tier']}, "
            f"Approved={offer['approved']}, Amount={offer['loan_amount_vnd']:,.0f} VND, "
            f"Score={offer['credit_score']}"
        )
        
        return offer
        
    except Exception as e:
        logger.error(f"Smart loan application error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Smart loan recommendation failed: {str(e)}"
        )


@router.post("/credit-score", response_model=CreditScoreResponse, status_code=status.HTTP_200_OK)
async def calculate_credit_score(application: SimpleLoanRequest):
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
    - loan_purpose: Loan purpose (used for context only)
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
        
        logger.info(f"Credit score calculated: {response.credit_score} (Grade: {response.loan_grade})")
        
        return response
        
    except Exception as e:
        logger.error(f"Credit score calculation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Credit score calculation failed: {str(e)}"
        )