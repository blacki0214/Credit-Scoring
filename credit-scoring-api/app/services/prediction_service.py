import numpy as np
import pandas as pd
import logging
from app.models.schemas import PredictionRequest, PredictionResponse
from app.services.model_loader import model_loader
from app.services.feature_engineering import FeatureEngineer

logger = logging.getLogger(__name__)


class PredictionService:
    """Service for making credit score predictions"""
    
    def __init__(self):
        self.feature_engineer = FeatureEngineer()
    
    def predict(self, request: PredictionRequest) -> PredictionResponse:
        """Make prediction from request data"""
        try:
            # Convert request to DataFrame
            input_data = pd.DataFrame([request.model_dump()])
            
            # Apply feature engineering
            processed_data = self.feature_engineer.transform(input_data)
            
            # Get active model and threshold
            model = model_loader.get_active_model()
            threshold = model_loader.get_threshold()
            
            # Make prediction with probability
            probability = model.predict_proba(processed_data)[0][1]
            
            # Apply optimized threshold
            prediction = 1 if probability >= threshold else 0
            
            # Determine risk level
            risk_level = self._get_risk_level(probability)
            
            # Calculate confidence (distance from decision boundary)
            confidence = abs(probability - threshold) / max(threshold, 1 - threshold)
            
            return PredictionResponse(
                prediction=int(prediction),
                probability=float(probability),
                risk_level=risk_level,
                confidence=float(confidence),
                message=self._get_message(risk_level, probability)
            )
            
        except Exception as e:
            logger.error(f"Prediction error: {str(e)}")
            raise
    
    def _get_risk_level(self, probability: float) -> str:
        """Determine risk level from probability"""
        if probability < 0.25:
            return "Low"
        elif probability < 0.50:
            return "Medium"
        elif probability < 0.75:
            return "High"
        else:
            return "Very High"
    
    def _get_message(self, risk_level: str, probability: float) -> str:
        """Generate message based on risk level"""
        messages = {
            "Low": f"Low default risk ({probability:.1%}). Applicant likely to repay.",
            "Medium": f"Medium default risk ({probability:.1%}). Further review recommended.",
            "High": f"High default risk ({probability:.1%}). Careful consideration advised.",
            "Very High": f"Very high default risk ({probability:.1%}). Approval not recommended."
        }
        return messages.get(risk_level, "")


# Singleton instance
prediction_service = PredictionService()