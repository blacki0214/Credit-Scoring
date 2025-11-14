import joblib
from pathlib import Path
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class ModelLoader:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelLoader, cls).__new__(cls)
            cls._instance._load_models()
        return cls._instance
    
    def _load_models(self):
        """Load ML models on initialization"""
        try:
            logger.info("📦 Loading LightGBM model...")
            self.lgbm_model = joblib.load(settings.LGBM_MODEL_PATH)
            logger.info("✅ LightGBM model loaded successfully")
            
            logger.info("📦 Loading metadata...")
            self.metadata = joblib.load(settings.METADATA_PATH)
            logger.info("✅ Metadata loaded successfully")
            
            # Log model info
            logger.info(f"📊 Model features: {len(self.lgbm_model.feature_name_)}")
            logger.info(f"🎯 Threshold: {self.metadata['models']['lightgbm']['threshold']:.3f}")
            
        except Exception as e:
            logger.error(f"❌ Error loading models: {e}")
            raise


# Create singleton instance
model_loader = ModelLoader()