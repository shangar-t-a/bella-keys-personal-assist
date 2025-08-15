"""Configuration settings for the expense manager service."""

from functools import lru_cache

from app.settings.base import ExpenseManagerBaseSettings
from app.settings.dev import ExpenseManagerDevSettings


@lru_cache
def get_settings() -> ExpenseManagerBaseSettings | ExpenseManagerDevSettings:
    """Get the appropriate settings based on the environment."""
    if ExpenseManagerBaseSettings().APP_ENV == "dev":
        return ExpenseManagerDevSettings()
    else:
        return ExpenseManagerBaseSettings()
