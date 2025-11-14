from fastapi import APIRouter, HTTPException, status
from app.models.schemas import CustomerInput, PredictionResult
from app.services.prediction_service import prediction_service
import logging
from typing import List

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/predict", response_model=PredictionResult, status_code=status.HTTP_200_OK)
async def predict_loan(customer: CustomerInput):
    """
    🎯 Main Prediction Endpoint
    
    Predict loan default probability and estimate maximum loan amount
    
    **Request Body:**
    - customer_id: Unique identifier
    - age_years: Customer age (18-75)
    - employment_years: Years of employment (0-50)
    - annual_income: Annual income in USD
    - requested_amount: Requested loan amount
    - credit_card_usage: Credit usage percentage (0-200)
    - days_past_due_avg: Average days late (0-90)
    - higher_education: Has higher education (true/false)
    - employment_status: working/self_employed/retired/unemployed/student
    
    **Returns:**
    - Default probability
    - Risk level
    - Approval decision
    - Loan estimation (amount, interest rate, monthly payment)
    - Risk factors analysis
    """
    try:
        logger.info(f"📥 Prediction request for customer: {customer.customer_id}")
        
        # Get prediction
        result = prediction_service.predict(customer)
        
        logger.info(f"✅ Prediction complete: {result.decision} (probability: {result.default_probability:.2%})")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Prediction error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {str(e)}"
        )


@router.post("/batch-predict", status_code=status.HTTP_200_OK)
async def batch_predict(customers: List[CustomerInput]):
    """
    📊 Batch Prediction Endpoint
    
    Predict multiple customers at once
    """
    try:
        logger.info(f"📥 Batch prediction request for {len(customers)} customers")
        
        results = []
        for customer in customers:
            result = prediction_service.predict(customer)
            results.append(result)
        
        logger.info(f"✅ Batch prediction complete: {len(results)} results")
        
        return {"predictions": results, "count": len(results)}
        
    except Exception as e:
        logger.error(f"❌ Batch prediction error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch prediction failed: {str(e)}"
        )