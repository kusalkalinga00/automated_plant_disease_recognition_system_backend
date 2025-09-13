from fastapi import APIRouter
from .routes_health import router as health_router

api_v1 = APIRouter()
api_v1.include_router(health_router, prefix="")
