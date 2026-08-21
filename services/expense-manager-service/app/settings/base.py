"""Base settings for the expense manager service."""

import os
from typing import Literal

from pydantic import SecretStr
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)

from app import __version__ as _app_version

ENV_TYPES = Literal["dev", "prod", "test"]
STORAGE_TYPES = Literal["inmemory", "sqlite", "postgresql"]


def get_default_user_backup_dir() -> str:
    """Get default user home directory for desktop backups."""
    bella_dir = os.path.join(os.path.expanduser("~"), ".bella", "backups")
    legacy_dir = os.path.join(os.path.expanduser("~"), ".bella-keys", "backups")
    if not os.path.exists(bella_dir) and os.path.exists(legacy_dir):
        return legacy_dir
    return bella_dir


class ExpenseManagerBaseSettings(BaseSettings):
    """Base settings for the expense manager service."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Environment
    APP_ENV: ENV_TYPES = "prod"

    # Authentication
    JWT_SECRET: SecretStr | None = None

    # Storage settings
    STORAGE_TYPE: STORAGE_TYPES = "postgresql"

    # Database settings
    DATABASE_URL: SecretStr = SecretStr("")
    PG_DB_HOST: str = "localhost"
    LOG_DB_QUERIES: bool = False
    BACKUP_DIR: str = get_default_user_backup_dir()

    # Logging settings
    LOG_LEVEL: str = "INFO"

    # App Settings
    APP_NAME: str = "Expense Manager Service"
    APP_VERSION: str = _app_version
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
