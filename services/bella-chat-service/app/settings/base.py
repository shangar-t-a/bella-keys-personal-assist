"""Base settings for the bella chat application."""

from pathlib import Path
from typing import Literal

from pydantic import SecretStr
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)

MODEL_PROVIDERS = Literal["google", "ollama", "huggingface"]
ENV_TYPES = Literal["dev", "prod", "test"]
LOG_LEVELS = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class BellaChatBaseSettings(BaseSettings):
    """Base settings for the bella chat application."""

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent.parent.parent.joinpath(".env"),
        extra="forbid",
    )

    # Environment
    APP_ENV: ENV_TYPES = "prod"

    # Logging settings
    FASTAPI_LOG_LEVEL: LOG_LEVELS = "INFO"
    CONSOLE_LOG_LEVEL: LOG_LEVELS = "INFO"
    FILE_LOG_LEVEL: LOG_LEVELS = "DEBUG"

    # App Settings
    APP_NAME: str = "Bella"
    APP_VERSION: str = "1.0.0"
    HOST: str = "0.0.0.0"
    PORT: int = 5000
    DEBUG: bool = False
    ALLOWED_HOSTS: list[str] = ["*"]
    ALLOWED_METHODS: list[str] = ["GET", "POST", "PATCH", "PUT", "DELETE"]
    ALLOWED_HEADERS: list[str] = ["*"]

    # CORS settings
    CORS_ORIGINS: list[str] = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_EXPOSE_HEADERS: list[str] = ["*"]

    # AI Settings
    SYNTHESIS_MODEL_PROVIDER: MODEL_PROVIDERS = "ollama"
    SYNTHESIS_MODEL_NAME: str = "qwen2.5vl:7b"
    EMBEDDING_MODEL_PROVIDER: MODEL_PROVIDERS = "ollama"
    EMBEDDING_MODEL_NAME: str = "qwen3-embedding:0.6b"
    EMBEDDING_MODEL_DIMENSION: int = 1024
    GOOGLE_API_KEY: SecretStr = ""

    # QDRANT Settings
    QDRANT_URL: str = "http://localhost:6333"

    # Keys Personal Wiki Agent Settings
    QDRANT_COLLECTION_NAME: str = "keys-personal-wiki"
