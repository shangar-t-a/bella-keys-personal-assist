"""Base settings for the expense manager service."""

from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

MODEL_PROVIDERS = Literal["openai", "anthropic", "azure", "google"]
ENV_TYPES = Literal["dev", "prod", "test"]
STORAGE_TYPES = Literal["inmemory", "sqlite"]


class ExpenseManagerBaseSettings(BaseSettings):
    """Base settings for the expense manager service."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Environment
    APP_ENV: ENV_TYPES = "prod"

    # Storage settings
    STORAGE_TYPE: STORAGE_TYPES = "sqlite"

    # Database settings
    DATABASE_URL: str = "sqlite+aiosqlite:///./expense_manager.db"
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

    # AI model settings
    LLM_PROVIDER: MODEL_PROVIDERS = "openai"
    LLM_MODEL: str = "gpt-4o"
    LLM_BASE_URL: str = "https://api.openai.com/v1"
    LLM_API_VERSION: str = "2024-03-15"
    LLM_API_KEY: str = ""
