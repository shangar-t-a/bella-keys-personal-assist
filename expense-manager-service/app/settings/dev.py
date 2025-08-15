"""Dev settings for the expense manager service."""

from app.settings.base import ExpenseManagerBaseSettings


class ExpenseManagerDevSettings(ExpenseManagerBaseSettings):
    """Development settings for the expense manager service."""

    # Environment
    APP_ENV: str = "dev"

    # Storage settings
    STORAGE_TYPE: str = "inmemory"

    # Logging settings
    LOG_LEVEL: str = "DEBUG"

    # App Settings
    DEBUG: bool = True
