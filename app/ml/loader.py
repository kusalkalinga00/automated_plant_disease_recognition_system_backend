import os, json, datetime, threading
from tensorflow.keras.models import load_model
from app.core.config import settings


_MODEL = None
_IDX2LABEL = None
_IMG_SIZE = (224, 224)
_MODEL_VERSION = None
_LOCK = threading.Lock()


def load_artifacts():
    """
    Lazy load and cache (model, labels, img_size, version).
    Safe to call from any endpoint; loads exactly once per process.
    """
    global _MODEL, _IDX2LABEL, _IMG_SIZE, _MODEL_VERSION
    if _MODEL is not None:
        return _MODEL, _IDX2LABEL, _IMG_SIZE, _MODEL_VERSION

    with _LOCK:
        if _MODEL is None:
            if not os.path.exists(settings.MODEL_PATH):
                raise RuntimeError(f"Model not found at {settings.MODEL_PATH}")
            _MODEL = load_model(settings.MODEL_PATH)

            # version from filename + mtime
            mtime = datetime.datetime.fromtimestamp(
                os.path.getmtime(settings.MODEL_PATH)
            ).isoformat()
            _MODEL_VERSION = f"{os.path.basename(settings.MODEL_PATH)}@{mtime}"

            # labels
            with open(settings.LABELS_PATH, "r") as f:
                # labels.json is { "0": "Tomato___Early_blight", ... }
                _IDX2LABEL = {int(k): v for k, v in json.load(f).items()}

            # meta
            with open(settings.META_PATH, "r") as f:
                meta = json.load(f)
                s = int(meta.get("img_size", 224))
                _IMG_SIZE = (s, s)

    return _MODEL, _IDX2LABEL, _IMG_SIZE, _MODEL_VERSION
