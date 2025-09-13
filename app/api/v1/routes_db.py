from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.deps import get_db
from app.utils.response import api_response

router = APIRouter()


@router.get("/db/health", tags=["system"])
def db_health(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return api_response(True, "DB connection OK", {"engine": "postgres"}, None)
