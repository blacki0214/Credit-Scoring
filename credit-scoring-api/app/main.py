from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.api.routes import router as api_router
from app.core.config import settings
from app.core.logging import setup_logging
from app.core.security import get_client_ip
from app.services.student_prediction_service import student_prediction_service
import logging

logger = logging.getLogger(__name__)

# Setup logging
setup_logging()

# Initialize rate limiter
limiter = Limiter(key_func=get_client_ip)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    description="AI-powered Credit Scoring API with secure authentication"
)

# Add rate limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware - Now with restricted origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.API_PREFIX)

@app.get("/")
async def root():
    """Root endpoint - public"""
    return {
        "message": "Credit Scoring API",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "docs": "/docs",
        "security": {
            "authentication": "API Key required for most endpoints",
            "header": "X-API-Key",
            "rate_limiting": "Enabled"
        }
    }

@app.on_event("startup")
async def startup_event():
    """Log startup information"""
    logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"CORS allowed origins: {settings.allowed_origins_list}")
    logger.info(f"API authentication: {'Enabled' if settings.API_KEY else 'Disabled (dev mode)'}")
    logger.info(
        "Student decision policy: %s (manual_review_margin=%.3f)",
        settings.STUDENT_DECISION_POLICY,
        settings.STUDENT_MANUAL_REVIEW_MARGIN,
    )
    strict_student_preflight = settings.STUDENT_STARTUP_STRICT_PREFLIGHT
    student_preflight = student_prediction_service.validate_runtime_assets(
        strict=strict_student_preflight
    )
    if student_preflight["ok"]:
        logger.info("Student model preflight: OK")
    else:
        logger.warning(
            "Student model preflight issues: %s",
            student_preflight["issues"],
        )
    if student_preflight["warnings"]:
        logger.warning(
            "Student model preflight warnings: %s",
            student_preflight["warnings"],
        )
    logger.info(f"Rate limiting: Enabled")