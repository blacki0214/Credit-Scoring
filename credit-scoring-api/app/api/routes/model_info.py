from fastapi import APIRouter
from app.services.model_loader import model_loader

router = APIRouter()


@router.get("/model/info")
async def get_model_info():
    """
    Get Model Information
    
    Returns model metadata and performance metrics
    """
    try:
        from app.core.config import settings
        metadata = model_loader.metadata
        
        # Determine which model is active
        model_name = "XGBoost" if settings.USE_XGBOOST else "LightGBM"
        model_key = "xgboost" if settings.USE_XGBOOST else "lightgbm"
        
        if not metadata:
            active_model = model_loader.get_active_model()
            return {
                "model_name": model_name,
                "version": "1.0",
                "features_count": len(active_model.feature_names_in_) if hasattr(active_model, 'feature_names_in_') else 64,
                "status": "loaded"
            }
        
        model_info = metadata.get('models', {}).get(model_key, {})
        
        return {
            "model_name": model_name,
            "version": "1.0",
            "features_count": metadata.get('data_info', {}).get('n_features', 64) if settings.USE_XGBOOST else len(model_loader.lgbm_model.feature_name_),
            "threshold": float(model_info.get('threshold', settings.XGBOOST_THRESHOLD if settings.USE_XGBOOST else settings.LIGHTGBM_THRESHOLD)),
            "performance": {
                "roc_auc": float(model_info.get('metrics', {}).get('roc_auc', 0)),
                "f1": float(model_info.get('metrics', {}).get('f1', 0)),
                "precision": float(model_info.get('metrics', {}).get('precision', 0)),
                "recall": float(model_info.get('metrics', {}).get('recall', 0)),
                "balanced_accuracy": float(model_info.get('metrics', {}).get('balanced_accuracy', 0))
            },
            "training_date": metadata.get('training_date', 'N/A')
        }
    except Exception as e:
        from app.core.config import settings
        active_model = model_loader.get_active_model()
        return {
            "error": str(e),
            "model_name": "XGBoost" if settings.USE_XGBOOST else "LightGBM",
            "features_count": len(active_model.feature_names_in_) if hasattr(active_model, 'feature_names_in_') else 64
        }


@router.get("/model/features")
async def get_model_features():
    """
    Get Model Features
    
    Returns list of all features used by the model
    """
    active_model = model_loader.get_active_model()
    feature_names = active_model.feature_names_in_ if hasattr(active_model, 'feature_names_in_') else model_loader.lgbm_model.feature_name_
    return {
        "features": list(feature_names),
        "count": len(feature_names)
    }