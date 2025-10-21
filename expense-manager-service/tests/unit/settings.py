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
    PG_DB_HOST: str = "localhost"
    PG_DB_PORT: int = 5432
    PG_DB_USER: str = "ems_test_user"
    PG_DB_PASSWORD: SecretStr = "test123"
    PG_DB_NAME: str = "expense_manager_test"
