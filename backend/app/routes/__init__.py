"""
Routes package initialization
"""
from fastapi import APIRouter
from app.routes import (
	climate,
	land_health,
	predictions,
	recommendations,
	locations,
)


router = APIRouter()

router.include_router(climate.router)
router.include_router(land_health.router)
router.include_router(predictions.router)
router.include_router(recommendations.router)
router.include_router(locations.router)

__all__ = ["router"]