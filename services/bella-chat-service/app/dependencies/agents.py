"""Agents dependencies for Bella Chat Service.

These dependencies should not be used inside agents to avoid circular imports.
"""

from contextlib import asynccontextmanager
from functools import lru_cache
from http import HTTPStatus
from typing import Any

import httpx
from langchain_core.tools import BaseTool
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from app.agents import (
    RAGAgent,
    SimpleChatAgent,
)
from app.agents.v2.deep_orchestrator import create_deep_orchestrator_agent
from app.dependencies.ai_dependencies import get_app_synthesis_llm_client
from app.settings import get_settings
from utilities.logger import GetAppLogger

_logger = GetAppLogger().get_logger()


async def exchange_token_for_ems(auth_header: str | None) -> str | None:
    """Exchange the user's bearer token for an EMS-MCP-scoped token via RFC 8693.

    Returns the raw access token string (no 'Bearer ' prefix) or None if the
    exchange fails, in which case the caller should fall back to the original token.
    """
    if not auth_header:
        return None

    raw_token = auth_header.removeprefix("Bearer ").strip()
    settings = get_settings()
    auth_service_url = settings.AUTH_SERVICE_URL.rstrip("/")
    ems_mcp_url = settings.EMS_MCP_SERVER_URL.split("/mcp")[0]  # base URL only

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.post(
                f"{auth_service_url}/oauth/token",
                data={
                    "grant_type": "urn:ietf:params:oauth:grant-type:token-exchange",
                    "subject_token": raw_token,
                    "subject_token_type": "urn:ietf:params:oauth:token-type:access_token",
                    "client_id": "bella-chat-service",
                    "resource": ems_mcp_url,
                },
            )
            if resp.status_code == HTTPStatus.OK:
                exchanged = resp.json().get("access_token")
                if exchanged:
                    _logger.debug("OBO token exchange succeeded for EMS MCP")
                    return exchanged
            _logger.warning(
                f"OBO token exchange returned {resp.status_code}, "
                "falling back to original token"
            )
    except Exception as exc:
        _logger.warning(f"OBO token exchange failed: {exc!r}, falling back to original token")

    # Fallback: pass the original token through directly
    return raw_token


async def get_mcp_tools(auth_header: str | None) -> list[BaseTool]:
    """Load EMS MCP tools for the current request.

    Performs an OBO token exchange so the forwarded token is scoped to the
    EMS MCP server, then creates a fresh MCP session with that token injected
    as a static Authorization header.  langchain-mcp-adapters opens a new
    HTTP session per tool call, so the header is picked up on every invocation.
    """
    settings = get_settings()
    token = await exchange_token_for_ems(auth_header)
    headers: dict[str, Any] = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        mcp_client = MultiServerMCPClient(
            {
                "ems": {
                    "url": settings.EMS_MCP_SERVER_URL,
                    "transport": "streamable_http",
                    "headers": headers,
                }
            }
        )
        return await mcp_client.get_tools()
    except Exception as exc:
        _logger.warning(f"Failed to load MCP tools: {exc!r}")
        return []


def build_agent(
    mcp_tools: list[BaseTool],
    checkpointer: AsyncPostgresSaver,
) -> Any:
    """Assemble the deep orchestrator agent for a single request lifecycle."""
    model = get_app_synthesis_llm_client()
    return create_deep_orchestrator_agent(
        model=model,
        mcp_tools=mcp_tools,
        checkpointer=checkpointer,
    )


@lru_cache(maxsize=1)
def get_simple_chat_agent() -> SimpleChatAgent:
    """Get the simple chat agent."""
    llm_client = get_app_synthesis_llm_client()
    return SimpleChatAgent(model=llm_client)


@lru_cache(maxsize=1)
def get_rag_agent() -> RAGAgent:
    """Get the RAG agent."""
    llm_client = get_app_synthesis_llm_client()
    return RAGAgent(model=llm_client)


@asynccontextmanager
async def create_checkpointer():
    """Async context manager that initialises and yields the LangGraph Postgres checkpointer.

    The checkpointer is a long-lived resource shared across all requests.
    MCP tool loading and agent construction happen per-request in the router.
    """
    settings = get_settings()

    _logger.info("Connecting LangGraph Postgres checkpointer...")
    async with AsyncPostgresSaver.from_conn_string(settings.langgraph_pg_db_dsn) as checkpointer:
        await checkpointer.setup()  # Idempotent — creates tables on first run
        _logger.info("LangGraph Postgres checkpointer initialised.")
        yield checkpointer
