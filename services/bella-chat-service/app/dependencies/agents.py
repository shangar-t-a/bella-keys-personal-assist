"""Agents dependencies for Bella Chat Service.

These dependencies should not be used inside agents to avoid circular imports.
"""

from contextlib import asynccontextmanager
from functools import lru_cache

from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from app.agents import (
    OrchestratorAgent,
    RAGAgent,
    SimpleChatAgent,
)
from app.dependencies.ai_dependencies import get_app_synthesis_llm_client
from app.settings import get_settings
from utilities.logger import GetAppLogger

_logger = GetAppLogger().get_logger()


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
    """Async context manager that builds and yields an OrchestratorAgent.

    Manages the MCP client and Postgres checkpointer lifecycles: both are
    kept open for the full duration of the context (i.e. the FastAPI app's lifespan).
    """
    settings = get_settings()
    llm_client = get_app_synthesis_llm_client()
    rag_agent = get_rag_agent()

    _logger.info("Connecting LangGraph Postgres checkpointer...")
    async with AsyncPostgresSaver.from_conn_string(settings.langgraph_pg_db_dsn) as checkpointer:
        await checkpointer.setup()  # Idempotent — creates tables on first run
        _logger.info("LangGraph Postgres checkpointer initialised.")

        mcp_client = MultiServerMCPClient(
            {
                "ems": {
                    "url": settings.EMS_MCP_SERVER_URL,
                    "transport": "streamable_http",
                }
            }
        )
        mcp_tools = await mcp_client.get_tools()

        agent = OrchestratorAgent.create(
            model=llm_client,
            mcp_tools=mcp_tools,
            rag_agent=rag_agent,
            checkpointer=checkpointer,
            max_iterations=settings.ORCHESTRATOR_MAX_ITERATIONS,
        )
        yield agent
