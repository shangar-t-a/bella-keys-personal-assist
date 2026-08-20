"""Agents dependencies for Bella Chat Service.

These dependencies should not be used inside agents to avoid circular imports.
"""

from contextlib import asynccontextmanager
from functools import lru_cache
from typing import Any

import httpx
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from app.agents import (
    RAGAgent,
    SimpleChatAgent,
)
from app.agents.v2.deep_orchestrator import create_deep_orchestrator_agent
from app.core.context import current_auth_header
from app.dependencies.ai_dependencies import get_app_synthesis_llm_client
from app.settings import get_settings
from utilities.logger import GetAppLogger

_logger = GetAppLogger().get_logger()


class OBOTokenAuth(httpx.Auth):
    """httpx Auth handler performing RFC 8693 OAuth 2.0 Token Exchange for MCP calls."""

    def __init__(self, target_resource: str | None = None) -> None:
        self.target_resource = target_resource
        self._token_cache: dict[str, str] = {}

    def auth_flow(self, request: httpx.Request):
        """Inject target-bounded access token via RFC 8693 token exchange."""
        token = current_auth_header.get()
        if not token:
            yield request
            return

        raw_token = token.replace("Bearer ", "").strip()
        settings = get_settings()
        resource = self.target_resource or str(request.url).split("?")[0]

        # Check cache for previously exchanged token
        cache_key = f"{raw_token}:{resource}"
        if cache_key in self._token_cache:
            request.headers["Authorization"] = f"Bearer {self._token_cache[cache_key]}"
            yield request
            return

        # Synchronously attempt token exchange at Auth Service
        auth_service_url = getattr(settings, "AUTH_SERVICE_URL", None) or "http://auth-service:8002"
        token_endpoint = f"{auth_service_url.rstrip('/')}/oauth/token"

        try:
            with httpx.Client(timeout=3.0) as sync_client:
                resp = sync_client.post(
                    token_endpoint,
                    data={
                        "grant_type": "urn:ietf:params:oauth:grant-type:token-exchange",
                        "subject_token": raw_token,
                        "subject_token_type": "urn:ietf:params:oauth:token-type:access_token",
                        "client_id": "bella-chat-service",
                        "resource": resource,
                    },
                )
                if resp.status_code == 200:
                    exchanged_token = resp.json().get("access_token")
                    if exchanged_token:
                        self._token_cache[cache_key] = exchanged_token
                        request.headers["Authorization"] = f"Bearer {exchanged_token}"
                        yield request
                        return
        except Exception as exc:
            _logger.warning(f"OBO Token Exchange failed, falling back to original token: {exc}")

        # Fallback to direct token if exchange fails or is unsupported
        request.headers["Authorization"] = token if token.startswith("Bearer ") else f"Bearer {token}"
        yield request


def make_http_client(
    headers: dict[str, str] | None = None,
    timeout: Any = None,
    auth: Any = None,
) -> httpx.AsyncClient:
    """Create an httpx.AsyncClient with RFC 8693 OBO Token Exchange auth handler."""
    return httpx.AsyncClient(headers=headers, timeout=timeout, auth=OBOTokenAuth())


@lru_cache(maxsize=1)
def get_simple_chat_agent() -> SimpleChatAgent:
    """Get the simple chat agent."""
    llm_client = get_app_synthesis_llm_client()
    chat_agent = SimpleChatAgent(model=llm_client)
    return chat_agent


@lru_cache(maxsize=1)
def get_rag_agent() -> RAGAgent:
    """Get the RAG agent."""
    llm_client = get_app_synthesis_llm_client()
    rag_agent = RAGAgent(model=llm_client)
    return rag_agent


@asynccontextmanager
async def create_orchestrator_agent():
    """Async context manager that builds and yields a native Deep Agent graph.

    Manages the MCP client and Postgres checkpointer lifecycles: both are
    kept open for the full duration of the context (i.e. the FastAPI app's lifespan).
    """
    settings = get_settings()
    llm_client = get_app_synthesis_llm_client()

    _logger.info("Connecting LangGraph Postgres checkpointer...")
    async with AsyncPostgresSaver.from_conn_string(settings.langgraph_pg_db_dsn) as checkpointer:
        await checkpointer.setup()  # Idempotent — creates tables on first run
        _logger.info("LangGraph Postgres checkpointer initialised.")

        mcp_tools = []
        try:
            mcp_client = MultiServerMCPClient(
                {
                    "ems": {
                        "url": settings.EMS_MCP_SERVER_URL,
                        "transport": "streamable_http",
                        "httpx_client_factory": make_http_client,
                    }
                }
            )
            mcp_tools = await mcp_client.get_tools()
        except Exception as exc:
            _logger.warning(f"Failed to load MCP client tools during initialization: {exc}")

        agent = create_deep_orchestrator_agent(
            model=llm_client,
            mcp_tools=mcp_tools,
            checkpointer=checkpointer,
        )
        yield agent
