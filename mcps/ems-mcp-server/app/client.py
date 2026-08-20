"""HTTP client for communicating with the Expense Manager Service."""

import logging
from typing import Any

import httpx
from fastmcp.server.dependencies import get_access_token, get_http_request

from app.constants import BEARER_PREFIX
from app.settings import get_settings

logger = logging.getLogger("ems-mcp-server")
_client: httpx.AsyncClient | None = None


def clean_params(**kwargs: Any) -> dict[str, Any]:
    """Filter out None values from query parameters dictionary."""
    return {k: v for k, v in kwargs.items() if v is not None}


def get_ems_client() -> httpx.AsyncClient:
    """Return a shared async HTTP client pointing at the EMS base URL."""
    global _client
    if _client is None:
        settings = get_settings()
        _client = httpx.AsyncClient(
            base_url=settings.EMS_BASE_URL, timeout=settings.EMS_CLIENT_TIMEOUT_S
        )
    return _client


async def close_ems_client() -> None:
    """Close the shared async HTTP client if it was initialized."""
    global _client
    if _client is not None:
        await _client.aclose()
        _client = None
        logger.info("Shared EMS HTTP client closed successfully.")


def get_auth_headers() -> dict[str, str]:
    """Extract Authorization header from FastMCP auth context or incoming HTTP request."""
    access_token = get_access_token()
    if access_token and access_token.token:
        token = access_token.token
        if not token.startswith(BEARER_PREFIX):
            token = f"{BEARER_PREFIX}{token}"
        return {"Authorization": token}

    try:
        req = get_http_request()
        auth = req.headers.get("authorization")
        if auth:
            return {"Authorization": auth}
    except Exception as exc:
        logger.debug(f"Could not retrieve HTTP request auth header: {exc}")

    logger.warning("No access token in FastMCP context — forwarding no Authorization header to EMS")
    return {}


async def request_ems(method: str, path: str, **kwargs: Any) -> Any:
    """Send an HTTP request to EMS and handle errors robustly."""
    client = get_ems_client()
    headers = kwargs.pop("headers", {})
    headers.update(get_auth_headers())
    try:
        response = await client.request(method, path, headers=headers, **kwargs)
        if response.is_error:
            try:
                detail = response.json().get("detail", response.text)
            except Exception:
                detail = response.text
            raise ValueError(f"EMS Error ({response.status_code}): {detail}")
        if response.status_code == 204 or not response.content:
            return {"status": "success"}
        return response.json()
    except httpx.RequestError as exc:
        logger.exception(f"HTTP request to EMS failed: {exc}")
        raise ValueError(f"Failed to communicate with EMS backend: {exc}") from exc
