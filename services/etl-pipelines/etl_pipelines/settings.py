"""Configs for ETL pipelines."""

from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class ETLPipelineSettings(BaseSettings):
    """Settings for ETL pipelines."""

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent.parent / ".env",
        env_file_encoding="utf-8",
        extra="forbid",
    )

    GIT_PAT: SecretStr = ""


class ETLSourceTypes:
    """Supported ETL source types."""

    GITHUB = "github"


settings = ETLPipelineSettings()
