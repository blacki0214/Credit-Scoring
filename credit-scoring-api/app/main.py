from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import prediction, health, model_info
from app.core.config import settings
from app.core.logging import setup_logging
import logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="AI-Powered Credit Scoring API for Loan Approval Prediction",
    version=settings.VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# CORS Middleware - Allow your partner's frontend to call API
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(model_info.router, prefix="/api", tags=["Model Info"])
app.include_router(prediction.router, prefix="/api", tags=["Predictions"])


@app.on_event("startup")
async def startup_event():
    """Load models on startup"""
    logger.info("🚀 Starting Credit Scoring API...")
    logger.info(f"📦 Version: {settings.VERSION}")
    logger.info(f"🔧 Environment: {settings.ENVIRONMENT}")
    

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("👋 Shutting down Credit Scoring API...")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Credit Scoring API",
        "version": settings.VERSION,
        "docs": "/api/docs",
        "health": "/api/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True if settings.ENVIRONMENT == "development" else False
    )