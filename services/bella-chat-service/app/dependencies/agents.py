"""Agents dependencies for Bella Chat Service.

These dependencies should not be used inside agents to avoid circular imports.
"""

from functools import lru_cache

from app.agents import (
    RAGAgent,
    SimpleChatAgent,
)
from app.dependencies.ai_dependencies import get_app_synthesis_llm_client


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
