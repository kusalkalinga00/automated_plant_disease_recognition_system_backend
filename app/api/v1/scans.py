from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from sqlalchemy.orm import Session
from app.utils.response import api_response
from app.db.deps import get_db
from app.db.models import Scan, User
from app.core.config import settings
from app.core.security import get_current_user
from app.services.storage import save_local_image
from app.services.catalog import get_disease_and_treatments
from app.ml.loader import load_artifacts
from app.ml.inference import preprocess_pil, topk_indices
from PIL import Image
import numpy as np

router = APIRouter(prefix="/scans", tags=["scans"])


@router.post("")
def create_scan(
    file: UploadFile = File(...),
    locale: str | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    try:
        # 1) save original
        path = save_local_image(settings.UPLOAD_DIR, user.id, file)

        # 2) predict
        MODEL, IDX2LABEL, IMG_SIZE, MODEL_VERSION = load_artifacts()
        with Image.open(path) as pil:
            x = preprocess_pil(pil, IMG_SIZE)
        probs = MODEL.predict(x, verbose=0)[0]
        pred_idx = int(np.argmax(probs))
        label = IDX2LABEL[pred_idx]
        confidence = float(probs[pred_idx])
        order = topk_indices(probs, k=5)
        top_k = [{"label": IDX2LABEL[i], "confidence": float(probs[i])} for i in order]

        # 3) hydrate catalog
        disease_payload, treatments = get_disease_and_treatments(db, label, locale)

        # 4) save scan row
        scan = Scan(
            user_id=user.id,
            image_url=path,
            predicted_label=label,
            confidence=confidence,
            top_k=top_k,
            model_version=MODEL_VERSION,
        )
        db.add(scan)
        db.commit()
        db.refresh(scan)

        payload = {
            "scan": {
                "id": scan.id,
                "image_url": scan.image_url,
                "predicted_label": scan.predicted_label,
                "confidence": scan.confidence,
                "top_k": scan.top_k,
                "model_version": scan.model_version,
                "created_at": scan.created_at,
            },
            "disease": disease_payload,  # may be null until you seed
            "treatments": treatments,  # may be []
        }
        return api_response(True, "Scan created", payload, None)

    except HTTPException:
        raise
    except Exception as e:
        return api_response(False, f"Scan failed: {e}", None, None)


@router.get("")
def list_scans(
    page: int = 1,
    page_size: int = 20,
    label: str | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    q = db.query(Scan).filter(Scan.user_id == user.id)
    if label:
        q = q.filter(Scan.predicted_label == label)
    total = q.count()
    items = (
        q.order_by(Scan.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    payload = [
        {
            "id": s.id,
            "image_url": s.image_url,
            "predicted_label": s.predicted_label,
            "confidence": s.confidence,
            "model_version": s.model_version,
            "created_at": s.created_at,
        }
        for s in items
    ]
    meta = {"page": page, "page_size": page_size, "total": total}
    return api_response(True, "Scans retrieved", payload, meta)


@router.get("/{scan_id}")
def get_scan(
    scan_id: str,
    locale: str | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    s = db.query(Scan).filter(Scan.id == scan_id, Scan.user_id == user.id).first()
    if not s:
        return api_response(False, "Scan not found", None, None)
    disease_payload, treatments = get_disease_and_treatments(
        db, s.predicted_label, locale
    )
    payload = {
        "scan": {
            "id": s.id,
            "image_url": s.image_url,
            "predicted_label": s.predicted_label,
            "confidence": s.confidence,
            "top_k": s.top_k,
            "model_version": s.model_version,
            "created_at": s.created_at,
        },
        "disease": disease_payload,
        "treatments": treatments,
    }
    return api_response(True, "Scan details", payload, None)
