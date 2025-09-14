"""Settings for expense-manager-service unit testing."""

from app.settings.base import (
    ENV_TYPES,
    STORAGE_TYPES,
    ExpenseManagerBaseSettings,
)


class UnitTestSettings(ExpenseManagerBaseSettings):
    """Settings for unit testing."""

    # Environment
    APP_ENV: ENV_TYPES = "test"

    # Storage settings
    STORAGE_TYPE: STORAGE_TYPES = "sqlite"

    # Database settings
    DATABASE_URL: str = "sqlite+aiosqlite:///./test_expense_manager.db"
