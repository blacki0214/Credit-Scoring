from fastapi import APIRouter

router = APIRouter()

# Import route modules
from app.api.routes import health, prediction, model_info

# Include all routers without prefix (main.py already adds /api)
router.include_router(health.router, tags=["Health"])
router.include_router(prediction.router, tags=["Prediction"])
router.include_router(model_info.router, tags=["Model Info"])