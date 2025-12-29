"""Settings for expense-manager-service unit testing."""

from pydantic import SecretStr

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
    STORAGE_TYPE: STORAGE_TYPES = "postgresql"

    # Database settings
    DATABASE_URL: SecretStr = "postgresql+asyncpg://ems_test_user:test123@localhost:5432/expense_manager_test"
