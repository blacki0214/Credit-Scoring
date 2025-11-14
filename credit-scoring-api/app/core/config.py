from pydantic_settings import BaseSettings
from typing import List
from pathlib import Path


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
    
    # Model Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    MODEL_DIR: Path = BASE_DIR / "models"
    LGBM_MODEL_PATH: Path = MODEL_DIR / "lgbm_model_optimized.pkl"
    METADATA_PATH: Path = MODEL_DIR / "ensemble_comparison_metadata.pkl"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    # Security (if needed)
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()