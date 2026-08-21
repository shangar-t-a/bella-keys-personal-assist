"""Constants and configuration defaults for the bella-deploy package."""

from pathlib import Path

# Package Metadata
PACKAGE_NAME = "bella-deploy-manager"
CLI_COMMAND = "bella-deploy"

# Default Paths & File Names
DEFAULT_DIR_NAME = ".bella"
COMPOSE_FILENAME = "docker-compose.prod.yaml"
ENV_FILENAME = ".env"
ENV_EXAMPLE_FILENAME = ".env.example"
SQL_INIT_FILENAME = "init-db-prod.sql"

# Repository Remote URLs
REPO_BASE_RAW_URL = (
    "https://raw.githubusercontent.com/shangar-t-a/bella-keys-personal-assist/main"
)
REPO_COMPOSE_URL = f"{REPO_BASE_RAW_URL}/docker/{COMPOSE_FILENAME}"
REPO_ENV_URL = f"{REPO_BASE_RAW_URL}/docker/.env.prod.example"
REPO_SQL_URL = f"{REPO_BASE_RAW_URL}/scripts/database/{SQL_INIT_FILENAME}"
REPO_PYPROJECT_URL = f"{REPO_BASE_RAW_URL}/tools/deploy-manager/pyproject.toml"

# Docker Profiles
PROFILE_AI_CHAT = "ai-chat"
PROFILE_MONITOR = "monitor"
PROFILE_UI = "ui"
PROFILE_UI_EMS = "ui-ems"

# Service Labels
LABEL_EMS_ONLY = "EMS only (auth, ems)"
LABEL_AI_CHAT = "AI Chat (auth, ems, bella-chat, ems-mcp, qdrant)"
LABEL_AI_CHAT_MONITOR = "AI Chat + Monitor (auth, ems, bella-chat, ems-mcp, qdrant, phoenix)"
LABEL_UI_EMS = " + Web UI (EMS only)"
LABEL_UI_FULL = " + Web UI (EMS + AI Chat)"
