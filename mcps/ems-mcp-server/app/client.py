"""HTTP client for communicating with the Expense Manager Service."""

import httpx
from fastmcp.server.dependencies import get_http_request

from app.settings import get_settings

_client: httpx.AsyncClient | None = None


def get_ems_client() -> httpx.AsyncClient:
    """Return a shared async HTTP client pointing at the EMS base URL."""
    global _client
    if _client is None:
        settings = get_settings()
        _client = httpx.AsyncClient(
            base_url=settings.EMS_BASE_URL, timeout=settings.EMS_CLIENT_TIMEOUT_S
        )
    return _client


def get_auth_headers() -> dict[str, str]:
    """Extract Authorization header from the current request to propagate to EMS backend."""
    try:
        req = get_http_request()
        auth_header = req.headers.get("Authorization")
        if auth_header:
            return {"Authorization": auth_header}
    except Exception:
        pass
    return {}
