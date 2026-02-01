from fastapi import APIRouter
from app.services.model_loader import model_loader
from app.core.config import settings

router = APIRouter()


@router.get("/health")
async def health_check():
    """Check API health status"""
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "models_loaded": model_loader.lgbm_model is not None
    }


@router.get("/ping")
async def ping():
    """🏓 Simple Ping Endpoint"""
    return {"message": "pong"}