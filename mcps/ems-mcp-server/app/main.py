"""EMS MCP Server entry point.

Exposes Expense Manager Service read operations as MCP tools over HTTP/SSE.
"""

from contextlib import asynccontextmanager
import logging
import os
from typing import AsyncIterator

from fastmcp import FastMCP
from fastmcp.server.auth import RemoteAuthProvider, TokenVerifier, AccessToken
import jwt
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
import uvicorn

from app.client import close_ems_client
from app.settings import get_settings
import app.tools as tools

logger = logging.getLogger("ems-mcp-server")


class EMSTokenVerifier(TokenVerifier):
    """Custom token verifier for EMS that validates tokens locally using JWT_SECRET."""

    async def verify_token(self, token: str) -> AccessToken | None:
        """Verify the access token and validate target audience."""
        settings = get_settings()
        secret_str = (
            settings.JWT_SECRET.get_secret_value() if settings.JWT_SECRET else None
        )
        if not secret_str:
            logger.error(
                "JWT_SECRET is not configured in the environment of EMS MCP Server"
            )
            return None

        try:
            payload = jwt.decode(
                token, secret_str, algorithms=["HS256"], options={"verify_aud": False}
            )
        except jwt.PyJWTError as e:
            logger.warning(f"JWT signature validation failed: {e}")
            return None

        # Validate target resource audience if present (RFC 8707 / RFC 9728)
        aud = payload.get("aud")
        if aud:
            settings = get_settings()
            norm_aud = str(aud).rstrip("/")
            norm_expected = settings.BASE_URL.rstrip("/")

            if (
                norm_aud != norm_expected
                and norm_aud != f"{norm_expected}/mcp"
                and norm_aud != f"{norm_expected}/sse"
            ):
                logger.warning(
                    f"Token verification failed: Token audience '{aud}' does not match expected '{settings.BASE_URL}'"
                )
                return None

        scopes_raw = payload.get("scope") or payload.get("scopes") or ""
        scopes_list = (
            scopes_raw.split() if isinstance(scopes_raw, str) else list(scopes_raw)
        )

        return AccessToken(
            token=token,
            client_id=payload.get("client_id", "default_client"),
            scopes=scopes_list,
            expires_at=payload.get("exp"),
            claims=payload,
        )


@asynccontextmanager
async def mcp_lifespan(server: FastMCP) -> AsyncIterator[None]:
    """Manage lifecycle resources for the EMS MCP Server."""
    logger.info("Initializing EMS MCP Server resources...")
    yield
    logger.info("Shutting down EMS MCP Server and cleaning up resources...")
    await close_ems_client()


# Setup Auth Providers
settings = get_settings()
verifier = EMSTokenVerifier()
auth_provider = RemoteAuthProvider(
    token_verifier=verifier,
    authorization_servers=[settings.AUTH_SERVICE_URL],
    base_url=settings.BASE_URL,
    resource_name="EMS MCP Server",
)

mcp = FastMCP(
    name="ems-mcp-server",
    instructions=(
        "Tools for reading data from Expense Manager Service (EMS). "
        "Use list_accounts / list_periods to discover available data. "
        "Use list_spending_entries or list_spending_entries_for_account to fetch "
        "balance and spending data, optionally filtered by month, year, or account name."
    ),
    auth=auth_provider,
    lifespan=mcp_lifespan,
)

# Register all tools
for name in tools.__all__:
    mcp.add_tool(getattr(tools, name))


def run() -> None:
    """Entry point for the EMS MCP Server."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    settings = get_settings()
    transport_type = os.environ.get("MCP_TRANSPORT", "streamable-http")
    if transport_type not in ("streamable-http", "sse", "http"):
        transport_type = "streamable-http"

    app = mcp.http_app(
        transport=transport_type,
        middleware=[
            Middleware(
                CORSMiddleware,
                allow_origins=["*"],
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            ),
        ],
    )
    uvicorn.run(
        app,
        host=settings.HOST,
        port=settings.PORT,
    )


if __name__ == "__main__":
    run()
