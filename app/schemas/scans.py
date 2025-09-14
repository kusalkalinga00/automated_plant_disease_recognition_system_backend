from pydantic import BaseModel
from datetime import datetime


class TopKItem(BaseModel):
    label: str
    confidence: float


class ScanOut(BaseModel):
    id: str
    image_url: str
    predicted_label: str
    confidence: float
    top_k: list[TopKItem]
    model_version: str | None
    created_at: datetime
