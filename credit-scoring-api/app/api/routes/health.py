from fastapi import APIRouter
from app.services.model_loader import model_loader
from app.services.student_prediction_service import student_prediction_service
from app.core.config import settings

router = APIRouter()


@router.get("/health")
async def health_check():
    """Check API health status"""
    student_status = student_prediction_service.validate_runtime_assets(strict=False)
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "models_loaded": model_loader.lgbm_model is not None,
        "student_model_ready": student_status["ok"],
        "student_threshold": student_status["threshold"],
        "student_model_loaded": student_status["model_loaded"],
        "student_calibrator_loaded": student_status.get("calibrator_loaded", False),
    }


@router.get("/ping")
async def ping():
    """ Simple Ping Endpoint"""
    return {"message": "pong"}