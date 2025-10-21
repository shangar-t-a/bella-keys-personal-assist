"""Configuration settings for the expense manager service."""

from functools import lru_cache

from app.settings.base import BellaChatBaseSettings
from app.settings.dev import BellaChatDevSettings


@lru_cache(maxsize=1)
def get_settings() -> BellaChatBaseSettings | BellaChatDevSettings:
    """Get the appropriate settings based on the environment."""
    if BellaChatBaseSettings().APP_ENV == "dev":
        return BellaChatDevSettings()
    else:
        return BellaChatBaseSettings()
