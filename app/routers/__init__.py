from fastapi import APIRouter
from . import brand, vehicle

api_router = APIRouter()

api_router.include_router(brand.router, prefix="/api/v1")
api_router.include_router(vehicle.router, prefix="/api/v1")
