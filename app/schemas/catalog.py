from typing import Literal
from pydantic import BaseModel


class DiseaseIn(BaseModel):
    label: str
    display_name: str
    description: str


class DiseaseUpdate(BaseModel):
    display_name: str | None = None
    description: str | None = None


class TreatmentIn(BaseModel):
    disease_label: str
    type: Literal["organic", "chemical"]
    title: str
    instructions: str
    dosage: str | None = None
    locale: Literal["en", "si", "ta"] = "en"

class TreatmentUpdate(BaseModel):
    type: Literal["organic", "chemical"] | None = None
    title: str | None = None
    instructions: str | None = None
    dosage: str | None = None
    locale: Literal["en", "si", "ta"] | None = None
