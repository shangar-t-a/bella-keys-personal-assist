"""Dev settings for the bella chat application."""

from app.settings.base import (
    ENV_TYPES,
    BellaChatBaseSettings,
)


class BellaChatDevSettings(BellaChatBaseSettings):
    """Development settings for the bella chat application."""

    # Environment
    APP_ENV: ENV_TYPES = "dev"
