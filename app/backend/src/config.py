"""Application configuration management."""
import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    APP_NAME: str = "Infrastructure Visualization API"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False

    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:3001"]

    # Pulumi
    PULUMI_ACCESS_TOKEN: Optional[str] = None
    INFRA_DIR: Path = Path(__file__).parent.parent.parent.parent / "infra"

    # GCP
    GCP_PROJECT_ID: Optional[str] = None
    GCP_REGION: str = "us-central1"
    GOOGLE_CREDENTIALS: Optional[str] = None

    # WebSocket
    WS_HEARTBEAT_INTERVAL: int = 30
    WS_RECONNECT_INTERVAL: int = 5

    # Logging
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
