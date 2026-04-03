"""Settings for the EMS MCP Server."""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class EMSMCPSettings(BaseSettings):
    """Settings for the EMS MCP Server."""

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent.parent / ".env",
        extra="ignore",
    )

    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8001

    # EMS base URL
    EMS_BASE_URL: str = "http://localhost:8000"

    # Client Settings
    EMS_CLIENT_TIMEOUT_S: int = 30


@lru_cache(maxsize=1)
def get_settings() -> EMSMCPSettings:
    """Get the settings for the EMS MCP Server."""
    return EMSMCPSettings()
