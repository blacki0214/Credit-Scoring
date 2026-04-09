from pydantic_settings import BaseSettings
from typing import List
from pathlib import Path
import os
import secrets


class Settings(BaseSettings):
    # Project Info
    PROJECT_NAME: str = "Credit Scoring API"
    VERSION: str = "2.0.0"
    ENVIRONMENT: str = "development"
    
    # API Settings
    API_PREFIX: str = "/api"
    
    # Security
    SECRET_KEY: str = secrets.token_urlsafe(32)  # Auto-generate if not in .env
    API_KEY: str = ""  # REQUIRED in .env for production
    DEMO_AUTH_BYPASS_ENABLED: bool = False
    DEMO_AUTH_BYPASS_USER_ID: str = "demo-user"
    DEMO_AUTH_BYPASS_EMAIL: str = "demo@example.com"
    
    # CORS - Restrict to specific origins (NO wildcard in production)
    # Can be comma-separated string in .env: "http://localhost:3000,http://localhost:5173"
    ALLOWED_ORIGINS: str | List[str] = "http://localhost:3000,http://localhost:5173,http://localhost:8080"
    
    @property
    def allowed_origins_list(self) -> List[str]:
        """Parse ALLOWED_ORIGINS into a list"""
        if isinstance(self.ALLOWED_ORIGINS, list):
            return self.ALLOWED_ORIGINS
        # Split comma-separated string
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]
    
    # Model Paths - Use relative paths that work in both Windows and Docker
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    
    @property
    def MODEL_DIR(self) -> Path:
        return self.BASE_DIR / "models"
    
    @property
    def XGB_MODEL_PATH(self) -> Path:
        model_path = os.getenv("XGB_MODEL_PATH", "models/xgboost_final.pkl")
        if Path(model_path).is_absolute():
            return Path(model_path)
        return self.BASE_DIR / model_path
    
    @property
    def LGBM_MODEL_PATH(self) -> Path:
        model_path = os.getenv("LGBM_MODEL_PATH", "models/lgb_model_optimized.pkl")
        if Path(model_path).is_absolute():
            return Path(model_path)
        return self.BASE_DIR / model_path
    
    @property
    def METADATA_PATH(self) -> Path:
        metadata_path = os.getenv("METADATA_PATH", "models/ensemble_comparison_metadata.pkl")
        if Path(metadata_path).is_absolute():
            return Path(metadata_path)
        return self.BASE_DIR / metadata_path
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    # Model Settings
    USE_XGBOOST: bool = True  # Set to False to use LightGBM
    XGBOOST_THRESHOLD: float = 0.86  # Optimized threshold for XGBoost
    LIGHTGBM_THRESHOLD: float = 0.12  # Optimized threshold for LightGBM
    
    # Rate Limiting
    RATE_LIMIT_CALCULATE_LIMIT: int = 10  # requests per minute
    RATE_LIMIT_CALCULATE_TERMS: int = 10
    RATE_LIMIT_APPLY: int = 5
    RATE_LIMIT_BATCH: int = 2

    # Student application logging
    STUDENT_APP_LOGGING_ENABLED: bool = True
    STUDENT_APPLICATIONS_COLLECTION: str = "student_applications"
    STUDENT_DECISION_POLICY: str = "balanced"  # safe | balanced | aggressive
    STUDENT_MANUAL_REVIEW_MARGIN: float = 0.05
    STUDENT_APPROVAL_THRESHOLD_OVERRIDE: float = 0.0  # 0 disables override
    STUDENT_MONITORING_WINDOW_HOURS: int = 24
    STUDENT_SCORING_REFERENCE_LOAN_AMOUNT: int = 5_000_000
    STUDENT_CALIBRATION_ENABLED: bool = True
    STUDENT_CALIBRATOR_FILENAME: str = "student_calibrator_isotonic.pkl"
    STUDENT_STARTUP_STRICT_PREFLIGHT: bool = False

    @property
    def STUDENT_MODEL_PATH(self) -> Path:
        model_path = os.getenv("STUDENT_MODEL_PATH", "")
        if model_path:
            path = Path(model_path)
            return path if path.is_absolute() else self.BASE_DIR / path
        return self.BASE_DIR / "models" / "best_model_phase1.pkl"

    @property
    def STUDENT_THRESHOLD_PATH(self) -> Path:
        threshold_path = os.getenv("STUDENT_THRESHOLD_PATH", "")
        if threshold_path:
            path = Path(threshold_path)
            return path if path.is_absolute() else self.BASE_DIR / path
        return self.BASE_DIR / "models" / "best_threshold_phase1.pkl"

    @property
    def STUDENT_CALIBRATOR_PATH(self) -> Path:
        calibrator_path = os.getenv("STUDENT_CALIBRATOR_PATH", "")
        if calibrator_path:
            path = Path(calibrator_path)
            return path if path.is_absolute() else self.BASE_DIR / path
        return self.BASE_DIR / "models" / self.STUDENT_CALIBRATOR_FILENAME
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "extra": "ignore"  # Ignore extra fields from .env
    }
        
    def validate_security(self):
        """Validate security settings before starting server"""
        if self.ENVIRONMENT == "production":
            if not self.API_KEY:
                raise ValueError(
                    "API_KEY must be set in .env file for production environment"
                )
            # NOTE: CORS wildcard check removed — this is a mobile API.
            # CORS is browser-enforced only; Flutter clients are unaffected by it.


settings = Settings()

# Validate security settings on import
if settings.ENVIRONMENT == "production":
    settings.validate_security()