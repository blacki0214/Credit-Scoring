from fastapi import APIRouter, Depends, HTTPException, Query
from app.services.model_loader import model_loader
from app.services.student_prediction_service import student_prediction_service
from app.services.student_application_logger import student_application_logger
from app.core.config import settings
from app.core.security import verify_api_key

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


@router.get("/student/monitoring/summary")
async def student_monitoring_summary(
    hours: int = Query(default=settings.STUDENT_MONITORING_WINDOW_HOURS, ge=1, le=720),
    api_key: str = Depends(verify_api_key),
):
    """Quick monitoring summary for student canary rollout KPIs."""
    try:
        summary = student_application_logger.get_monitoring_summary(window_hours=hours)
        summary["student_decision_policy"] = settings.STUDENT_DECISION_POLICY
        summary["student_manual_review_margin"] = settings.STUDENT_MANUAL_REVIEW_MARGIN
        summary["student_threshold"] = student_prediction_service.threshold
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Student monitoring summary failed: {e}")