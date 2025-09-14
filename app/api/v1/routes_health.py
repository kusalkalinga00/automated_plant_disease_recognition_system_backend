from fastapi import APIRouter
from datetime import datetime, timezone
from app.core.config import settings
from app.utils.response import api_response
from app.ml.loader import load_artifacts

router = APIRouter()


@router.get("/health", tags=["system"])
def health():
    info = {
        "service": settings.APP_NAME,
        "env": settings.ENV,
        "time_utc": datetime.now(timezone.utc).isoformat(),
        "model_loaded": False,
        "num_classes": None,
        "img_size": None,
        "model_version": None,
    }
    try:
        _, idx2label, img_size, version = load_artifacts()
        info["model_loaded"] = True
        info["num_classes"] = len(idx2label)
        info["img_size"] = list(img_size)
        info["model_version"] = version
        return api_response(True, "OK", info, None)
    except Exception as e:
        # still return 200 with success=false so your frontend can show a helpful state
        return api_response(False, f"Health check: {e}", info, None)


@router.get("/labels", tags=["system"])
def labels():
    try:
        _, idx2label, _, _ = load_artifacts()
        # return as strings to be stable over JSON
        payload = {str(k): v for k, v in idx2label.items()}
        return api_response(True, "Labels retrieved", payload, None)
    except Exception as e:
        return api_response(False, f"Failed to load labels: {e}", None, None)
