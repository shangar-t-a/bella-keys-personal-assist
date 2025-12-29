"""Base settings for the expense manager service."""

from typing import Literal

from pydantic import SecretStr
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)

ENV_TYPES = Literal["dev", "prod", "test"]
STORAGE_TYPES = Literal["inmemory", "sqlite", "postgresql"]


class ExpenseManagerBaseSettings(BaseSettings):
    """Base settings for the expense manager service."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Environment
    APP_ENV: ENV_TYPES = "prod"

    # Storage settings
    STORAGE_TYPE: STORAGE_TYPES = "postgresql"

    # Database settings
    DATABASE_URL: SecretStr = ""
    LOG_DB_QUERIES: bool = False

    # Logging settings
    LOG_LEVEL: str = "INFO"

    # App Settings
    APP_NAME: str = "Expense Manager Service"
    APP_VERSION: str = "1.0.0"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False
    ALLOWED_HOSTS: list[str] = ["*"]
    ALLOWED_METHODS: list[str] = ["GET", "POST", "PATCH", "PUT", "DELETE"]
    ALLOWED_HEADERS: list[str] = ["*"]

    # CORS settings
    CORS_ORIGINS: list[str] = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_EXPOSE_HEADERS: list[str] = ["*"]
