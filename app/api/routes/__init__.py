from fastapi import APIRouter

from app.api.routes import storage_routes, wine_routes

# Main router that includes all sub-routers
router = APIRouter()

# Include all routes
router.include_router(storage_routes.router)
router.include_router(wine_routes.router)