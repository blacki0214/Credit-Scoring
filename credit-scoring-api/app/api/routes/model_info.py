from fastapi import APIRouter
from app.services.model_loader import model_loader

router = APIRouter()


@router.get("/model/info")
async def get_model_info():
    """
    ℹ️ Get Model Information
    
    Returns model metadata and performance metrics
    """
    metadata = model_loader.metadata
    
    return {
        "model_name": "LightGBM",
        "version": "1.0",
        "features_count": len(model_loader.lgbm_model.feature_name_),
        "threshold": metadata['models']['lightgbm']['threshold'],
        "performance": metadata['models']['lightgbm']['metrics'],
        "training_date": metadata.get('training_date', 'N/A')
    }


@router.get("/model/features")
async def get_model_features():
    """
    📋 Get Model Features
    
    Returns list of all features used by the model
    """
    return {
        "features": model_loader.lgbm_model.feature_name_,
        "count": len(model_loader.lgbm_model.feature_name_)
    }