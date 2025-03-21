from fastapi import APIRouter
from app.api.storage import router as storage_router
from app.api.wine import router as wine_router

# Create main API router and include sub-routers
router = APIRouter()
router.include_router(storage_router)
router.include_router(wine_router)