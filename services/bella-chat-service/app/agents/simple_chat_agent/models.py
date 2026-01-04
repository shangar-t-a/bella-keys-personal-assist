"""Models for the simple chat agent."""

from typing import Annotated

from langgraph.graph.message import add_messages
from pydantic import BaseModel
from typing_extensions import TypedDict


class State(TypedDict):
    """State representation for the simple chat agent."""

    messages: Annotated[list, add_messages]


class SimpleChatAgentInfo(BaseModel):
    """Simple Chat Agent Info."""

    name: str = "Simple Chat Agent"
    description: str = "A simple chat agent that handles conversational interactions."
