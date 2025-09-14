from fastapi import APIRouter
from .routes_health import router as health_router
from .auth import router as auth_router
from .routes_db import router as db_router
from .scans import router as scans_router
from .admin import router as admin_router


api_v1 = APIRouter()
api_v1.include_router(health_router, prefix="")
api_v1.include_router(auth_router, prefix="")
api_v1.include_router(db_router, prefix="")
api_v1.include_router(scans_router, prefix="")
api_v1.include_router(admin_router, prefix="")
