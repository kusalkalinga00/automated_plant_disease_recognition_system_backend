from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, Boolean
from sqlalchemy.sql import func
from app.db.base import Base
import uuid
import datetime
from sqlalchemy import String, DateTime, Float, Text, JSON, Boolean, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship


def _uuid() -> str:
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String)
    full_name: Mapped[str | None] = mapped_column(String, nullable=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[str] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )


class Scan(Base):
    __tablename__ = "scans"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"))
    image_url: Mapped[str] = mapped_column(String)
    predicted_label: Mapped[str] = mapped_column(String)
    confidence: Mapped[float] = mapped_column(Float)
    top_k: Mapped[dict | None] = mapped_column(JSON)
    model_version: Mapped[str | None] = mapped_column(String)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    user: Mapped["User"] = relationship(backref="scans")


class Disease(Base):
    __tablename__ = "diseases"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    label: Mapped[str] = mapped_column(
        String, unique=True, index=True
    )  # must match model class name
    display_name: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class Treatment(Base):
    __tablename__ = "treatments"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    disease_id: Mapped[str] = mapped_column(String, ForeignKey("diseases.id"))
    type: Mapped[str] = mapped_column(String)  # "organic" | "chemical"
    title: Mapped[str] = mapped_column(String)
    instructions: Mapped[str] = mapped_column(Text)
    dosage: Mapped[str | None] = mapped_column(String, nullable=True)
    locale: Mapped[str] = mapped_column(String)  # "en" | "si" | "ta"
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
