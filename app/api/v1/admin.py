from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.utils.response import api_response
from app.db.deps import get_db
from app.db.models import Disease, Treatment
from app.core.security import admin_required
from app.schemas.catalog import DiseaseIn, DiseaseUpdate, TreatmentIn, TreatmentUpdate

router = APIRouter(prefix="/admin", tags=["admin"])


# ---------- Diseases ----------
@router.post("/diseases")
def create_disease(
    data: DiseaseIn, _: str = Depends(admin_required), db: Session = Depends(get_db)
):
    exists = db.query(Disease).filter(Disease.label == data.label).first()
    if exists:
        return api_response(False, "Disease label already exists", None, None)
    d = Disease(
        label=data.label, display_name=data.display_name, description=data.description
    )
    db.add(d)
    db.commit()
    db.refresh(d)
    payload = {
        "id": d.id,
        "label": d.label,
        "display_name": d.display_name,
        "description": d.description,
    }
    return api_response(True, "Disease created", payload, None)


@router.put("/diseases/{disease_id}")
def update_disease(
    disease_id: str,
    data: DiseaseUpdate,
    _: str = Depends(admin_required),
    db: Session = Depends(get_db),
):
    d = db.query(Disease).filter(Disease.id == disease_id).first()
    if not d:
        return api_response(False, "Disease not found", None, None)
    if data.display_name is not None:
        d.display_name = data.display_name
    if data.description is not None:
        d.description = data.description
    db.commit()
    db.refresh(d)
    payload = {
        "id": d.id,
        "label": d.label,
        "display_name": d.display_name,
        "description": d.description,
    }
    return api_response(True, "Disease updated", payload, None)


@router.delete("/diseases/{disease_id}")
def delete_disease(
    disease_id: str, _: str = Depends(admin_required), db: Session = Depends(get_db)
):
    d = db.query(Disease).filter(Disease.id == disease_id).first()
    if not d:
        return api_response(False, "Disease not found", None, None)
    # prevent delete if treatments exist
    t_count = (
        db.query(func.count(Treatment.id)).filter(Treatment.disease_id == d.id).scalar()
        or 0
    )
    if t_count > 0:
        return api_response(
            False,
            "Cannot delete: treatments exist (delete them first)",
            None,
            {"treatments": t_count},
        )
    db.delete(d)
    db.commit()
    return api_response(True, "Disease deleted", None, None)


@router.get("/diseases")
def list_diseases(
    page: int = 1,
    page_size: int = 50,
    search: str | None = None,
    _: str = Depends(admin_required),
    db: Session = Depends(get_db),
):
    q = db.query(Disease)
    if search:
        q = q.filter(
            (Disease.label.ilike(f"%{search}%"))
            | (Disease.display_name.ilike(f"%{search}%"))
        )
    total = q.count()
    items = (
        q.order_by(Disease.display_name.asc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    payload = [
        {
            "id": d.id,
            "label": d.label,
            "display_name": d.display_name,
            "description": d.description,
        }
        for d in items
    ]
    return api_response(
        True,
        "Diseases retrieved",
        payload,
        {"page": page, "page_size": page_size, "total": total},
    )


# ---------- Treatments ----------
@router.post("/treatments")
def create_treatment(
    data: TreatmentIn, _: str = Depends(admin_required), db: Session = Depends(get_db)
):
    disease = db.query(Disease).filter(Disease.label == data.disease_label).first()
    if not disease:
        return api_response(False, "Disease not found", None, None)
    t = Treatment(
        disease_id=disease.id,
        type=data.type,
        title=data.title,
        instructions=data.instructions,
        dosage=data.dosage,
        locale=data.locale,
    )
    db.add(t)
    db.commit()
    db.refresh(t)
    payload = {
        "id": t.id,
        "disease_id": t.disease_id,
        "type": t.type,
        "title": t.title,
        "instructions": t.instructions,
        "dosage": t.dosage,
        "locale": t.locale,
    }
    return api_response(True, "Treatment created", payload, None)


@router.put("/treatments/{treatment_id}")
def update_treatment(
    treatment_id: str,
    data: TreatmentUpdate,
    _: str = Depends(admin_required),
    db: Session = Depends(get_db),
):
    t = db.query(Treatment).filter(Treatment.id == treatment_id).first()
    if not t:
        return api_response(False, "Treatment not found", None, None)
    if data.type is not None:
        t.type = data.type
    if data.title is not None:
        t.title = data.title
    if data.instructions is not None:
        t.instructions = data.instructions
    if data.dosage is not None:
        t.dosage = data.dosage
    if data.locale is not None:
        t.locale = data.locale
    db.commit()
    db.refresh(t)
    payload = {
        "id": t.id,
        "disease_id": t.disease_id,
        "type": t.type,
        "title": t.title,
        "instructions": t.instructions,
        "dosage": t.dosage,
        "locale": t.locale,
    }
    return api_response(True, "Treatment updated", payload, None)


@router.delete("/treatments/{treatment_id}")
def delete_treatment(
    treatment_id: str, _: str = Depends(admin_required), db: Session = Depends(get_db)
):
    t = db.query(Treatment).filter(Treatment.id == treatment_id).first()
    if not t:
        return api_response(False, "Treatment not found", None, None)
    db.delete(t)
    db.commit()
    return api_response(True, "Treatment deleted", None, None)


@router.get("/treatments")
def list_treatments(
    page: int = 1,
    page_size: int = 50,
    disease_label: str | None = None,
    locale: str | None = None,
    type: str | None = None,
    _: str = Depends(admin_required),
    db: Session = Depends(get_db),
):
    q = db.query(Treatment).join(Disease, Disease.id == Treatment.disease_id)
    if disease_label:
        q = q.filter(Disease.label == disease_label)
    if locale:
        q = q.filter(Treatment.locale == locale)
    if type:
        q = q.filter(Treatment.type == type)
    total = q.count()
    items = (
        q.order_by(Treatment.title.asc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    payload = [
        {
            "id": t.id,
            "disease_id": t.disease_id,
            "type": t.type,
            "title": t.title,
            "instructions": t.instructions,
            "dosage": t.dosage,
            "locale": t.locale,
        }
        for t in items
    ]
    return api_response(
        True,
        "Treatments retrieved",
        payload,
        {"page": page, "page_size": page_size, "total": total},
    )
