from fastapi import FastAPI
from app.api.routes import router as api_router
from app.services.model_loader import model_loader
from datetime import datetime

app = FastAPI()

app.include_router(api_router, prefix="/api")


@app.get("/health")
async def health_check():
    """
    🏥 Health Check Endpoint

    Check if API and models are running correctly
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "models_loaded": True,
        "lgbm_features": len(model_loader.lgbm_model.feature_name_),
        "threshold": model_loader.metadata['models']['lightgbm']['threshold']
    }


@app.get("/ping")
async def ping():
    """
    🏓 Simple Ping Endpoint
    """
    return {"message": "pong"}