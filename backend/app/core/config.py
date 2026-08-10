import os
from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Edge ANPR & Vehicle Trip Management Platform"
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:1234@localhost:5432/anpr_db")

    DETECTION_RETENTION_DAYS: int = 90
    PLATE_PREDICTION_RETENTION_DAYS: int = 90
    ALERT_RETENTION_DAYS: int = 60
    AUDIT_LOG_RETENTION_DAYS: int = 180
    CAMERA_HEALTH_RETENTION_DAYS: int = 30
    RETENTION_DRY_RUN: bool = False

    model_config = ConfigDict(case_sensitive=True, env_file=".env", extra="ignore")


settings = Settings()
