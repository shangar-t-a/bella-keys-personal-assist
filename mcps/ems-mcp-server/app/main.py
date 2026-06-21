"""EMS MCP Server entry point.

Exposes Expense Manager Service read operations as MCP tools over streamable-HTTP.
"""

import re

import httpx
import uvicorn
from fastmcp import FastMCP
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.types import ASGIApp

from app.settings import get_settings
from app.tools.accounts import get_account, list_accounts
from app.tools.periods import get_period, list_periods
from app.tools.spending_entries import (
    list_spending_entries,
    list_spending_entries_for_account,
)

mcp = FastMCP(
    name="ems-mcp-server",
    instructions=(
        "Tools for reading data from Expense Manager Service (EMS). "
        "Use list_accounts / list_periods to discover available data. "
        "Use list_spending_entries or list_spending_entries_for_account to fetch "
        "balance and spending data, optionally filtered by month, year, or account name."
    ),
)


HTTP_200_OK = 200


class RemoteAuthMiddleware(BaseHTTPMiddleware):
    """Middleware to validate user JWT by contacting the Auth Service's /me endpoint."""

    def __init__(
        self,
        app: ASGIApp,
        exclude_paths: list[str] | None = None,
        auth_service_url: str | None = None,
    ):
        """Initialize RemoteAuthMiddleware."""
        super().__init__(app)
        self.exclude_paths = exclude_paths or [
            r"^/health$",
            r"^/openapi\.json$",
            r"^/docs$",
            r"^/redoc$",
        ]
        self.auth_service_url = auth_service_url

    async def dispatch(self, request: Request, call_next):
        """Dispatch the request and validate auth token."""
        # Allow GET, DELETE, OPTIONS requests to pass through (SSE stream, connection teardown, CORS)
        if request.method in ("OPTIONS", "GET", "DELETE"):
            return await call_next(request)

        # Check if path is excluded
        path = request.url.path
        for pattern in self.exclude_paths:
            if re.match(pattern, path):
                return await call_next(request)

        # Read request body to check JSON-RPC method
        is_public_method = False
        if request.method == "POST":
            try:
                body = await request.body()
                import json

                data = json.loads(body)
                method = data.get("method")
                if method in ("initialize", "notifications/initialized", "tools/list"):
                    is_public_method = True
            except Exception:
                pass

        if is_public_method:
            return await call_next(request)

        # Extract Authorization Header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=401, content={"detail": "Not authenticated"}
            )

        # Resolve auth service URL dynamically if not set
        auth_url = self.auth_service_url
        if not auth_url:
            settings = get_settings()
            auth_url = settings.AUTH_SERVICE_URL

        # Call auth-service to validate the token
        async with httpx.AsyncClient(timeout=10) as client:
            try:
                response = await client.get(
                    f"{auth_url}/me",
                    headers={"Authorization": auth_header},
                )
                if response.status_code != HTTP_200_OK:
                    return JSONResponse(
                        status_code=401, content={"detail": "Invalid or expired token"}
                    )

                # Attach resolved user info to request state
                request.state.user = response.json()
            except Exception as e:
                return JSONResponse(
                    status_code=500,
                    content={"detail": f"Authentication service unreachable: {str(e)}"},
                )

        return await call_next(request)


# Register all tools
for _fn in [
    list_accounts,
    get_account,
    list_periods,
    get_period,
    list_spending_entries,
    list_spending_entries_for_account,
]:
    mcp.add_tool(_fn)


def run() -> None:
    """Entry point for the EMS MCP Server."""
    settings = get_settings()
    app = mcp.http_app(
        transport="streamable-http",
        middleware=[
            Middleware(
                RemoteAuthMiddleware,
                auth_service_url=settings.AUTH_SERVICE_URL,
            )
        ],
    )
    uvicorn.run(
        app,
        host=settings.HOST,
        port=settings.PORT,
    )


if __name__ == "__main__":
    run()
