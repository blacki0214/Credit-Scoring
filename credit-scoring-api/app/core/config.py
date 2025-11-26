from pydantic_settings import BaseSettings
from typing import List
from pathlib import Path
import os


class Settings(BaseSettings):
    # Project Info
    PROJECT_NAME: str = "Credit Scoring API"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "production"
    
    # API Settings
    API_PREFIX: str = "/api"
    
    # CORS - Add your partner's frontend URLs here
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",  # React default
        "http://localhost:5173",  # Vite default
        "http://localhost:8080",  # Vue default
        "https://your-frontend-domain.com",  # Production URL
        "*"  # Allow all (only for development)
    ]
    
    # Model Paths - Use relative paths that work in both Windows and Docker
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    
    @property
    def MODEL_DIR(self) -> Path:
        return self.BASE_DIR / "models"
    
    @property
    def LGBM_MODEL_PATH(self) -> Path:
        return self.MODEL_DIR / "lgb_model_optimized.pkl"
    
    @property
    def METADATA_PATH(self) -> Path:
        return self.MODEL_DIR / "ensemble_comparison_metadata.pkl"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    # Security 
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()