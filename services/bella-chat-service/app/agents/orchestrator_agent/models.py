"""Models for the orchestrator agent."""

from typing import Annotated

from langgraph.graph.message import add_messages
from pydantic import BaseModel
from typing_extensions import TypedDict


class OrchestratorState(TypedDict):
    """State representation for the orchestrator agent."""

    messages: Annotated[list, add_messages]


class OrchestratorAgentInfo(BaseModel):
    """Orchestrator Agent Info."""

    name: str = "Orchestrator Agent"
    description: str = (
        "ReAct agent that orchestrates EMS MCP tools and a RAG knowledge search "
        "to answer queries about expenses and Keys' personal wiki."
    )
