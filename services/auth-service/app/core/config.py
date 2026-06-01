"""Configuration settings for the Auth Service."""

from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class AuthSettings(BaseSettings):
    """Auth settings containing secrets and environment variables."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    HOST: str = "0.0.0.0"
    PORT: int = 8002

    JWT_SECRET: SecretStr = SecretStr("super_secret_dev_key_change_me_in_prod")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    DATABASE_URL: SecretStr = SecretStr("postgresql+asyncpg://postgres:postgres@localhost:5432/bella_keys")
    LOG_DB_QUERIES: bool = False


@lru_cache(maxsize=1)
def get_settings() -> AuthSettings:
    """Get cached settings instance."""
    return AuthSettings()
