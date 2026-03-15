"""Dev settings for the expense manager service."""

from app.settings.base import (
    ENV_TYPES,
    STORAGE_TYPES,
    ExpenseManagerBaseSettings,
)


class ExpenseManagerDevSettings(ExpenseManagerBaseSettings):
    """Development settings for the expense manager service."""

    # Environment
    APP_ENV: ENV_TYPES = "dev"

    # Storage settings
    STORAGE_TYPE: STORAGE_TYPES = "inmemory"

    # Logging settings
    LOG_LEVEL: str = "DEBUG"

    # App Settings
    DEBUG: bool = True
