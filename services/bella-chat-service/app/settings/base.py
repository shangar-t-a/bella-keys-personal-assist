"""Base settings for the bella chat application."""

from pathlib import Path
from typing import Literal

from pydantic import SecretStr
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)

MODEL_PROVIDERS = Literal["google", "ollama", "huggingface"]
ENV_TYPES = Literal["dev", "prod", "test"]
LOG_LEVELS = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class BellaChatBaseSettings(BaseSettings):
    """Base settings for the bella chat application."""

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent.parent.parent.joinpath(".env"),
        extra="ignore",
    )

    # Environment
    APP_ENV: ENV_TYPES = "prod"

    # Logging settings
    FASTAPI_LOG_LEVEL: LOG_LEVELS = "INFO"
    CONSOLE_LOG_LEVEL: LOG_LEVELS = "INFO"
    FILE_LOG_LEVEL: LOG_LEVELS = "DEBUG"

    # App Settings
    APP_NAME: str = "Bella"
    APP_VERSION: str = "1.0.0"
    HOST: str = "0.0.0.0"
    PORT: int = 5000
    DEBUG: bool = False
    ALLOWED_HOSTS: list[str] = ["*"]
    ALLOWED_METHODS: list[str] = ["GET", "POST", "PATCH", "PUT", "DELETE"]
    ALLOWED_HEADERS: list[str] = ["*"]

    # CORS settings
    CORS_ORIGINS: list[str] = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_EXPOSE_HEADERS: list[str] = ["*"]

    # AI Settings
    SYNTHESIS_MODEL_PROVIDER: MODEL_PROVIDERS = "ollama"
    SYNTHESIS_MODEL_NAME: str = "qwen2.5vl:7b"
    SYNTHESIS_MODEL_CTX_LENGTH: int = 32000
    EMBEDDING_MODEL_PROVIDER: MODEL_PROVIDERS = "ollama"
    EMBEDDING_MODEL_NAME: str = "qwen3-embedding:0.6b"
    EMBEDDING_MODEL_DIMENSION: int = 1024
    GOOGLE_API_KEY: SecretStr = ""

    # Ollama Settings
    OLLAMA_URL: str = "http://localhost:11434"

    # QDRANT Settings
    QDRANT_URL: str = "http://localhost:6333"

    # Arize Settings
    ARIZE_ENABLED: bool = True
    ARIZE_TRACES_URL: str = "http://localhost:6006/v1/traces"
    ARIZE_PROJECT_NAME: str = "bella-chat-service"
    ARIZE_PG_DB_USER: str = "bella_chat_user"
    ARIZE_PG_DB_PASSWORD: SecretStr = SecretStr("")
    ARIZE_PG_DB_HOST: str = "localhost"
    ARIZE_PG_DB_NAME: str = "bella_chat_arize_data"

    # Keys Personal Wiki Agent Settings
    QDRANT_COLLECTION_NAME: str = "keys-personal-wiki"

    # EMS MCP Server Settings
    EMS_MCP_SERVER_URL: str = "http://localhost:8001/mcp"

    # Orchestrator Settings — LangGraph Postgres checkpointer
    LANGGRAPH_PG_DB_USER: str = "bella_chat_user"
    LANGGRAPH_PG_DB_PASSWORD: SecretStr = SecretStr("")
    LANGGRAPH_PG_DB_HOST: str = "localhost"
    LANGGRAPH_PG_DB_NAME: str = "bella_chat_checkpoints"
    ORCHESTRATOR_MAX_ITERATIONS: int = 10

    @property
    def arize_pg_db_dsn(self) -> str:
        """Construct the Arize Postgres DSN from individual credentials."""
        password = self.ARIZE_PG_DB_PASSWORD.get_secret_value()
        return f"postgresql://{self.ARIZE_PG_DB_USER}:{password}@{self.ARIZE_PG_DB_HOST}:5432/{self.ARIZE_PG_DB_NAME}"

    @property
    def langgraph_pg_db_dsn(self) -> str:
        """Construct the LangGraph Postgres DSN from individual credentials."""
        password = self.LANGGRAPH_PG_DB_PASSWORD.get_secret_value()
        return (
            f"postgresql://{self.LANGGRAPH_PG_DB_USER}:{password}"
            f"@{self.LANGGRAPH_PG_DB_HOST}:5432/{self.LANGGRAPH_PG_DB_NAME}"
        )
