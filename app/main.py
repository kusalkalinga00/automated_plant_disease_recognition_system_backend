from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.logging import setup_logging
from app.api.v1 import api_v1

setup_logging()

app = FastAPI(title=settings.APP_NAME)

# CORS (Next.js dev and later prod domains)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# serve uploaded images locally (read-only HTTP access)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# API
app.include_router(api_v1, prefix="/api/v1")
