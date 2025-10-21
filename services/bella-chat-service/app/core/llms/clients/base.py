"""Base client for LLM engines."""

from abc import ABC, abstractmethod

from langchain_core.messages.base import BaseMessage
from pydantic import BaseModel


class LLMClientInterface(ABC):
    """Base class for LLM clients."""

    @abstractmethod
    def query(self, messages: list[BaseMessage]) -> str:
        """Query the LLM with a list of messages and return the response as a string."""
        pass

    @abstractmethod
    def query_structured(self, messages: list[BaseMessage], response_model: BaseModel) -> BaseModel:
        """Query the LLM and return the response as a structured pydantic model."""
        pass

    @abstractmethod
    def stream_query(self, messages: list[BaseMessage]):
        """Stream the LLM response for a list of messages."""
        pass

    @abstractmethod
    async def aquery(self, messages: list[BaseMessage]) -> str:
        """Asynchronously query the LLM with a list of messages and return the response as a string."""
        pass

    @abstractmethod
    async def aquery_structured(self, messages: list[BaseMessage], response_model: BaseModel) -> BaseModel:
        """Query the LLM asynchronously and return the response as a structured pydantic model."""
        pass

    @abstractmethod
    async def astream_query(self, messages: list[BaseMessage]):
        """Asynchronously stream the LLM response for a list of messages."""
        pass
