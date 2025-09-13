from fastapi import APIRouter
from datetime import datetime, timezone
from app.core.config import settings
from app.utils.response import api_response

router = APIRouter()


@router.get("/health", tags=["system"])
def health():
    info = {
        "service": settings.APP_NAME,
        "env": settings.ENV,
        "time_utc": datetime.now(timezone.utc).isoformat(),
        "model_loaded": False,  # we’ll flip to True when we wire the .keras model
    }
    return api_response(True, "OK", info, meta=None)
