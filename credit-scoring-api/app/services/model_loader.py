import joblib
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


class ModelLoader:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.lgbm_model = None
            cls._instance.metadata = None
            cls._instance._load_models()
        return cls._instance
    
    def _load_models(self):
        """Load models from disk"""
        try:
            logger.info(f"Loading LGBM model from {settings.LGBM_MODEL_PATH}")
            self.lgbm_model = joblib.load(settings.LGBM_MODEL_PATH)
            
            logger.info(f"Loading metadata from {settings.METADATA_PATH}")
            self.metadata = joblib.load(settings.METADATA_PATH)
            
            logger.info("Models loaded successfully")
        except Exception as e:
            logger.error(f"Error loading models: {str(e)}")
            raise
    
    def is_loaded(self) -> bool:
        """Check if models are loaded"""
        return self.lgbm_model is not None and self.metadata is not None
    
    def get_metadata(self):
        """Get model metadata"""
        return self.metadata


# Singleton instance
model_loader = ModelLoader()