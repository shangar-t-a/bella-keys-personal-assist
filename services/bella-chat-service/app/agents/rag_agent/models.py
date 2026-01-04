"""Models for RAG agent."""

from typing import Annotated

from langgraph.graph.message import add_messages
from pydantic import BaseModel
from typing_extensions import TypedDict


class State(TypedDict):
    """State representation for the RAG agent."""

    messages: Annotated[list, add_messages]
    context: list


class RAGAgentInfo(BaseModel):
    """RAG Agent Info."""

    name: str = "RAG Agent"
    description: str = "Retrieval Agent that uses external knowledge sources."
