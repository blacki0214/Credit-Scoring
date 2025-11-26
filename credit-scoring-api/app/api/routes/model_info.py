from fastapi import APIRouter
from app.services.model_loader import model_loader

router = APIRouter()


@router.get("/model/info")
async def get_model_info():
    """
    ℹ️ Get Model Information
    
    Returns model metadata and performance metrics
    """
    try:
        metadata = model_loader.metadata
        
        if not metadata:
            return {
                "model_name": "LightGBM",
                "version": "1.0",
                "features_count": len(model_loader.lgbm_model.feature_name_),
                "status": "loaded"
            }
        
        lgbm_info = metadata.get('models', {}).get('lightgbm', {})
        
        return {
            "model_name": "LightGBM",
            "version": "1.0",
            "features_count": len(model_loader.lgbm_model.feature_name_),
            "threshold": float(lgbm_info.get('threshold', 0.5)),
            "performance": {
                "roc_auc": float(lgbm_info.get('metrics', {}).get('roc_auc', 0)),
                "f1": float(lgbm_info.get('metrics', {}).get('f1', 0)),
                "precision": float(lgbm_info.get('metrics', {}).get('precision', 0)),
                "recall": float(lgbm_info.get('metrics', {}).get('recall', 0)),
                "balanced_accuracy": float(lgbm_info.get('metrics', {}).get('balanced_accuracy', 0))
            },
            "training_date": metadata.get('training_date', 'N/A')
        }
    except Exception as e:
        return {
            "error": str(e),
            "model_name": "LightGBM",
            "features_count": len(model_loader.lgbm_model.feature_name_) if model_loader.lgbm_model else 0
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