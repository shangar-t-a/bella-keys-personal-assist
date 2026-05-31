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
    GOOGLE_API_KEY: SecretStr = ""

    # Embedding settings
    EMBEDDING_MODEL_PROVIDER: str = "google"
    EMBEDDING_MODEL_NAME: str = "gemini-embedding-2"
    EMBEDDING_MODEL_DIMENSION: int = 1536
    OLLAMA_URL: str = "http://localhost:11434"
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_COLLECTION_NAME: str = "keys-personal-wiki"


class ETLSourceTypes:
    """Supported ETL source types."""

    GITHUB = "github"


settings = ETLPipelineSettings()
