from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Plant Doctor API"
    ENV: str = "local"  # local|dev|prod
    SECRET_KEY: str = "change-me"
    DATABASE_URL: str = "sqlite:///./data/app.db"  # we’ll switch to Postgres later
    UPLOAD_DIR: str = "./uploads"
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    ACCESS_TOKEN_MINUTES: int = 15
    REFRESH_TOKEN_DAYS: int = 14

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)


settings = Settings()


# ensure uploads dir exists
Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
