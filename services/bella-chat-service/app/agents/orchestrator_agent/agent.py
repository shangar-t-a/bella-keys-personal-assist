r"""LangGraph-native orchestrator agent with v2 streaming and Postgres-backed memory.

Architecture:
  - Uses create_agent from langchain.agents for tool dispatch
  - MCP tools passed through directly
  - RAG search wrapped as a @tool that calls the RAGAgent's compiled graph
  - AsyncPostgresSaver checkpointer for persistent conversation memory
  - Streams via LangGraph v2 StreamPart format, mapped to SSE events

SSE event format (one per line, double-newline terminated):
    data: {"type": "<event_type>", ...fields}\n\n

Event types
-----------
thinking        - reasoning text the model emitted before a tool call fields: content (str)
tool_call       - a tool is about to be called fields: name (str), args (dict)
tool_result     - the result returned by a tool fields: name (str), content (str)
response        - a token of the final synthesized answer fields: content (str)
error           - an unrecoverable error occurred fields: content (str)
done            - stream finished (always the last event)
"""

from __future__ import annotations

import contextlib
import json
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from langchain.agents import create_agent
from langchain_core.messages import AIMessageChunk
from langchain_core.tools import tool

from app.agents.orchestrator_agent.prompts import ORCHESTRATOR_SYSTEM_PROMPT
from app.core.context import current_auth_header
from utilities.logger import GetAppLogger

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from langchain_core.language_models.chat_models import BaseChatModel
    from langchain_core.tools import BaseTool
    from langgraph.checkpoint.base import BaseCheckpointSaver
    from langgraph.graph.state import CompiledStateGraph

    from app.agents.rag_agent.agent import RAGAgent

_logger = GetAppLogger().get_logger()

# LangGraph counts every node traversal, not just tool-call rounds.
# Each round is roughly 3 steps (agent → tool → agent), so multiply
# max_iterations by this factor to keep the graph budget aligned.
_RECURSION_LIMIT_MULTIPLIER = 3

# Maximum length of content to log for tool results
_LOG_CONTENT_MAX_LENGTH = 120


def _tool_label(name: str) -> str:
    """Convert snake_case tool name to a human-readable Title Case label."""
    return " ".join(word.capitalize() for word in name.split("_"))


def _sse(event_type: str, **fields: object) -> str:
    """Serialize a single SSE data frame."""
    return f"data: {json.dumps({'type': event_type, **fields})}\n\n"


def _extract_text(content: str | list) -> str:
    """Normalize LLM content that is either a plain string or a Gemini list payload."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        try:
            return "".join(part.get("text", "") for part in content if isinstance(part, dict))
        except Exception:
            pass
    return str(content)


class OrchestratorAgent:
    """LangGraph-native orchestrator with create_agent and v2 streaming.

    Uses:
      - create_agent for tool dispatch loop (handles retries, max iterations)
      - AsyncPostgresSaver checkpointer for persistent memory across restarts
      - LangGraph v2 stream format for type-safe SSE events

    Create instances via ``OrchestratorAgent.create()``.
    """

    def __init__(self, agent: CompiledStateGraph, max_iterations: int = 10) -> None:
        """Initialize the orchestrator with a compiled LangGraph agent."""
        self._agent = agent
        self._max_iter = max_iterations

    @classmethod
    def create(
        cls,
        model: BaseChatModel,
        mcp_tools: list[BaseTool],
        rag_agent: RAGAgent,
        checkpointer: BaseCheckpointSaver,
        max_iterations: int = 10,
    ) -> OrchestratorAgent:
        """Build a ready-to-use OrchestratorAgent.

        Args:
            model: An initialized LangChain chat model (Gemini or Ollama).
            mcp_tools: Tools to be added to the agent's toolkit (e.g. web search, calculator).
            rag_agent: The RAGAgent instance - will be called via a @tool wrapper that invokes its compiled graph.
            checkpointer: An initialized AsyncPostgresSaver (or any BaseCheckpointSaver).
            max_iterations: Safety cap on the tool-call loop.
        """

        @tool
        async def rag_search(query: str) -> str:
            """Retrieve relevant information from the RAGAgent's knowledge base.

            Args:
                query: Natural-language question or search phrase.

            Returns:
                Relevant text snippets with source references, or a not-found message.
            """
            try:
                # Per-invocation pattern: no checkpointer, inherits from parent
                result_state = await rag_agent.chain.ainvoke({"messages": [{"role": "user", "content": query}]})
                content = result_state["messages"][-1].content
                return _extract_text(content)
            except Exception as exc:
                _logger.error(f"RAG sub-agent failed: {exc}")
                return f"Error from knowledge base: {exc}"

        all_tools: list = [rag_search] + list(mcp_tools)

        agent = create_agent(
            model=model,
            tools=all_tools,
            name="orchestrator_agent",
            system_prompt=ORCHESTRATOR_SYSTEM_PROMPT,
            checkpointer=checkpointer,
        )

        return cls(agent=agent, max_iterations=max_iterations)

    async def get_response(self, user_input: str, conversation_id: UUID, auth_header: str | None = None) -> str:
        """Non-streaming invoke — call the agent directly and return the final message."""
        token_t = current_auth_header.set(auth_header)
        try:
            conv_id = str(conversation_id) if conversation_id else str(uuid4())
            config = {
                "configurable": {"thread_id": conv_id},
                "recursion_limit": self._max_iter * _RECURSION_LIMIT_MULTIPLIER,
            }
            inputs = {"messages": [{"role": "user", "content": user_input}]}
            result = await self._agent.ainvoke(inputs, config)
            return _extract_text(result["messages"][-1].content)
        finally:
            current_auth_header.reset(token_t)

    async def stream_response(
        self, user_input: str, conversation_id: UUID, auth_header: str | None = None
    ) -> AsyncGenerator[str]:
        r"""Stream all orchestration steps as SSE events.

        Uses LangGraph v2 streaming with stream_mode=["messages", "updates"] and maps each StreamPart to the
        appropriate SSE event type.
        """
        token_t = current_auth_header.set(auth_header)
        try:
            conv_id = str(conversation_id) if conversation_id else str(uuid4())
            _logger.info(f"Orchestrator: conversation={conv_id}, query={user_input!r}")

            config = {
                "configurable": {"thread_id": conv_id},
                "recursion_limit": self._max_iter * _RECURSION_LIMIT_MULTIPLIER,
            }
            inputs = {"messages": [{"role": "user", "content": user_input}]}

            # Separate sets: tool_call IDs already emitted vs tool_result IDs
            # already emitted. Must be kept separate — a tool_call ID is added
            # when the call event fires; if we re-used it for results the result
            # would always be suppressed (same ID, already in the set).
            emitted_tool_calls: set[str] = set()
            emitted_tool_results: set[str] = set()

            async for part in self._agent.astream(
                inputs,
                config,
                stream_mode=["messages", "updates"],
                version="v2",
            ):
                sse_events = self._map_stream_part(part, emitted_tool_calls, emitted_tool_results)
                for event in sse_events:
                    yield event

        except Exception as exc:
            _logger.exception(f"Orchestrator error for conversation {conv_id}")
            yield _sse("error", content=str(exc))
        finally:
            current_auth_header.reset(token_t)

        yield _sse("done")

    @staticmethod
    def _map_stream_part(
        part: dict,
        emitted_tool_calls: set[str],
        emitted_tool_results: set[str],
    ) -> list[str]:
        """Convert a single LangGraph v2 StreamPart to zero or more SSE frames."""
        part_type = part.get("type")
        if part_type == "messages":
            return OrchestratorAgent._handle_messages_part(part)
        if part_type == "updates":
            return OrchestratorAgent._handle_updates_part(part, emitted_tool_calls, emitted_tool_results)
        return []

    @staticmethod
    def _handle_messages_part(part: dict) -> list[str]:
        """Map a ``messages`` StreamPart to SSE frames (thinking / response)."""
        msg_chunk, _metadata = part["data"]
        if not isinstance(msg_chunk, AIMessageChunk):
            return []

        content = _extract_text(msg_chunk.content) if msg_chunk.content else ""
        tool_call_chunks = getattr(msg_chunk, "tool_call_chunks", [])

        if tool_call_chunks:
            # Reasoning text emitted before / alongside tool calls
            return [_sse("thinking", content=content)] if content else []
        # No tool calls → final response token
        return [_sse("response", content=content)] if content else []

    @staticmethod
    def _handle_updates_part(
        part: dict,
        emitted_tool_calls: set[str],
        emitted_tool_results: set[str],
    ) -> list[str]:
        """Map an ``updates`` StreamPart to SSE frames (tool_call / tool_result).

        Iterates all nodes in the update rather than looking for hardcoded node names
        ("agent" / "tools"), because create_agent(name=...) names the agent node after
        the supplied name, not "agent".
        """
        update_data = part.get("data", {})
        events: list[str] = []
        for _, node_data in update_data.items():
            if not isinstance(node_data, dict):
                continue
            messages = node_data.get("messages", [])
            if not messages:
                continue
            first = messages[0]
            # ToolMessage has tool_call_id → results; AIMessage has tool_calls → calls
            if getattr(first, "tool_call_id", None):
                events.extend(OrchestratorAgent._collect_tool_results(messages, emitted_tool_results))
            elif getattr(first, "tool_calls", []):
                events.extend(OrchestratorAgent._collect_tool_calls(messages, emitted_tool_calls))
        return events

    @staticmethod
    def _collect_tool_results(messages: list, emitted: set[str]) -> list[str]:
        """Emit ``tool_result`` SSE frames for each unseen ToolMessage."""
        events: list[str] = []
        for msg in messages:
            tool_call_id = getattr(msg, "tool_call_id", "")
            if tool_call_id and tool_call_id not in emitted:
                emitted.add(tool_call_id)
                name = getattr(msg, "name", "unknown")
                content = _extract_text(msg.content) if hasattr(msg, "content") else ""
                # Pretty-print if the tool returned a JSON string
                with contextlib.suppress(json.JSONDecodeError, TypeError):
                    content = json.dumps(json.loads(content), indent=2)
                _logger.info(
                    f"tool_result: name={name!r} is_sub_agent={name == 'rag_search'} "
                    f"content={content[:_LOG_CONTENT_MAX_LENGTH]!r}"
                    f"{'...' if len(content) > _LOG_CONTENT_MAX_LENGTH else ''}"
                )
                events.append(
                    _sse(
                        "tool_result",
                        id=tool_call_id,
                        name=name,
                        label=_tool_label(name),
                        content=content,
                        is_sub_agent=name == "rag_search",
                    )
                )
        return events

    @staticmethod
    def _collect_tool_calls(messages: list, emitted: set[str]) -> list[str]:
        """Emit ``tool_call`` SSE frames for each unseen tool call in an AIMessage."""
        events: list[str] = []
        for msg in messages:
            for tc in getattr(msg, "tool_calls", []):
                tc_id = tc.get("id", "")
                if tc_id and tc_id not in emitted:
                    emitted.add(tc_id)
                    name = tc.get("name", "unknown")
                    args = tc.get("args", {})
                    args_str = json.dumps(args, indent=2)
                    is_sub_agent = name == "rag_search"
                    _logger.info(f"tool_call: name={name!r} is_sub_agent={is_sub_agent} args={args_str}")
                    events.append(
                        _sse(
                            "tool_call",
                            id=tc_id,
                            name=name,
                            label=_tool_label(name),
                            args=args_str,
                            is_sub_agent=is_sub_agent,
                        )
                    )
        return events
