"""HTTP client for communicating with the Expense Manager Service."""

import httpx

from app.settings import get_settings

_client: httpx.AsyncClient | None = None


def get_ems_client() -> httpx.AsyncClient:
    """Return a shared async HTTP client pointing at the EMS base URL."""
    global _client
    if _client is None:
        settings = get_settings()
        _client = httpx.AsyncClient(base_url=settings.EMS_BASE_URL, timeout=settings.EMS_CLIENT_TIMEOUT_S)
    return _client
