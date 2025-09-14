from sqlalchemy.orm import Session
from app.db.models import Disease, Treatment


def get_disease_and_treatments(db: Session, label: str, locale: str | None):
    disease = db.query(Disease).filter(Disease.label == label).first()
    disease_payload = None
    if disease:
        disease_payload = {
            "label": disease.label,
            "display_name": disease.display_name,
            "description": disease.description,
        }
    q = (
        db.query(Treatment)
        .join(Disease, Disease.id == Treatment.disease_id)
        .filter(Disease.label == label)
    )
    items = q.filter(Treatment.locale.in_([locale, "en"])).all() if locale else q.all()
    treatments = [
        {
            "id": t.id,
            "type": t.type,
            "title": t.title,
            "instructions": t.instructions,
            "dosage": t.dosage,
            "locale": t.locale,
        }
        for t in items
    ]
    return disease_payload, treatments
