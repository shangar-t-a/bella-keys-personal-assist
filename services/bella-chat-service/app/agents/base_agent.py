"""Base agent module defining common interfaces and utilities for chat agents."""

from collections.abc import AsyncGenerator
from typing import TYPE_CHECKING
from uuid import (
    UUID,
    uuid4,
)

from langgraph.checkpoint.memory import MemorySaver

if TYPE_CHECKING:
    from langchain_core.language_models.chat_models import BaseChatModel
    from langgraph.graph import StateGraph
    from langgraph.graph.state import CompiledStateGraph


class BaseAgent:
    """Base class for chat agents."""

    def __init__(self, model: "BaseChatModel"):
        """Initialize the simple chat agent.

        Args:
            model (BaseChatModel): The chat model to be used by the agent.
        """
        self.model: BaseChatModel = model
        self.graph: StateGraph = None
        self.chain: CompiledStateGraph = None
        self._memory = MemorySaver()
        self._build_agent()

    def _build_agent(self):
        """Build the agent."""
        self._build_graph()
        self._compile()

    def _build_graph(self):
        """Build the state graph for the agent."""
        raise NotImplementedError("This method should be implemented by subclasses.")

    def _compile(self):
        """Compile the agent's model.

        Returns:
            BaseChatModel: The compiled chat model.
        """
        if self.graph:
            self.chain = self.graph.compile(checkpointer=self._memory)

    async def get_response(self, user_input: str, conversation_id: UUID) -> str:
        """Get a response from the agent based on user input and conversation ID.

        Args:
            user_input (str): The input message from the user.
            conversation_id (UUID): The unique identifier for the conversation.

        Returns:
            str: The agent's response.
        """
        result_state = await self.chain.ainvoke(
            input={
                "messages": [{"role": "user", "content": user_input}],
            },
            config={"configurable": {"thread_id": str(conversation_id) if conversation_id else str(uuid4())}},
        )
        return result_state["messages"][-1].content

    async def stream_response(self, user_input: str, conversation_id: UUID) -> AsyncGenerator[str]:
        """Stream a response from the agent for the given user input.

        Args:
            user_input (str): The input message from the user.
            conversation_id (UUID): The unique identifier for the conversation.

        Yields:
            AsyncGenerator[str, None]: An asynchronous generator yielding response chunks.
        """
        # Start the stream
        async for chunk in self.chain.astream(
            input={
                "messages": [{"role": "user", "content": user_input}],
            },
            config={"configurable": {"thread_id": str(conversation_id) if conversation_id else str(uuid4())}},
            stream_mode="messages",  # stream token events
        ):
            # Each chunk is typically (message_chunk, metadata)
            # message_chunk.content may be None or "" for some chunks
            message, metadata = chunk

            # If the chunk has text content, yield it
            content = getattr(message, "content", None)
            if content:
                yield content

    async def run(
        self, user_input: str, conversation_id: UUID | None = None, stream: bool = False
    ) -> AsyncGenerator[str] | str:
        """Run the agent with the given user input and conversation ID.

        Args:
            user_input (str): The input message from the user.
            conversation_id (UUID): The unique identifier for the conversation.
            stream (bool): Whether to stream the response or not.

        Yields:
            AsyncGenerator[str, None] | str: The agent's response, either as a full string or a stream of chunks.
        """
        if not self.chain:
            raise ValueError("The agent's chain is not compiled properly.")
        if not conversation_id:
            conversation_id = uuid4()

        if stream:
            return self.stream_response(user_input, conversation_id)
        else:
            return await self.get_response(user_input, conversation_id)
