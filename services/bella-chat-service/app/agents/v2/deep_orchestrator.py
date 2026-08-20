"""Bella v2 Deep Agent Orchestrator built using native deepagents harness."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from deepagents import create_deep_agent
from langchain_core.messages import AIMessage, AIMessageChunk
from langgraph.types import Command

from app.agents.v2.tools.retrieval import get_personal_wiki_retriever_tool
from utilities.logger import GetAppLogger

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    from langchain_core.language_models.chat_models import BaseChatModel
    from langchain_core.tools import BaseTool
    from langgraph.checkpoint.base import BaseCheckpointSaver

_logger = GetAppLogger().get_logger()

DEEP_ORCHESTRATOR_PROMPT = """You are Bella v2, an advanced AI Personal Assistant.
Coordinate tasks using specialized sub-agents (expense_analyst, knowledge_wiki) and tools to help the user.
"""


def _sse(event_type: str, **fields: object) -> str:
    """Format an SSE frame."""
    return f"data: {json.dumps({'type': event_type, **fields})}\n\n"


def create_deep_orchestrator_agent(
    model: BaseChatModel,
    mcp_tools: list[BaseTool],
    checkpointer: BaseCheckpointSaver,
):
    """Create a native Deep Agent using deepagents.create_deep_agent."""
    retriever_tool = get_personal_wiki_retriever_tool()

    subagents = [
        {
            "name": "expense_analyst",
            "description": "Queries financial records, expense summaries, and budget entries.",
            "system_prompt": "You analyze user expense queries and financial data.",
            "tools": mcp_tools,
        },
        {
            "name": "knowledge_wiki",
            "description": "Searches personal notes, wiki facts, and document archives.",
            "system_prompt": "You retrieve answers from personal notes and wiki facts.",
            "tools": [retriever_tool],
        },
    ]

    all_tools = [retriever_tool] + list(mcp_tools)

    return create_deep_agent(
        model=model,
        tools=all_tools,
        system_prompt=DEEP_ORCHESTRATOR_PROMPT,
        subagents=subagents,
        checkpointer=checkpointer,
        name="bella_deep_agent",
    )


def _extract_text(content: object) -> str:
    """Extract plain text from AIMessage content (handles strings, lists, and dict blocks)."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = [
            item if isinstance(item, str) else str(item.get("text", ""))
            for item in content
            if isinstance(item, (str, dict))
        ]
        return "".join(parts)
    if isinstance(content, dict) and "text" in content:
        return str(content["text"])
    return str(content) if content is not None else ""


def _extract_interrupt_events(state: object) -> list[str]:
    """Extract interrupt SSE frames from paused graph state."""
    frames = []
    if not getattr(state, "next", None):
        return frames

    for task in getattr(state, "tasks", []):
        for intr in getattr(task, "interrupts", []):
            intr_val = getattr(intr, "value", intr)
            tool_name = ""
            args: dict[str, object] = {}
            description = "Human-in-the-Loop review requested."

            if isinstance(intr_val, dict) and "action_requests" in intr_val:
                reqs = intr_val["action_requests"]
                if isinstance(reqs, list) and reqs:
                    req = reqs[0]
                    if isinstance(req, dict):
                        tool_name = str(req.get("name", ""))
                        raw_args = req.get("arguments", req.get("args", {}))
                        if isinstance(raw_args, dict):
                            args = raw_args
                        description = str(req.get("description", description))

            frames.append(
                _sse(
                    "interrupt",
                    interrupt_id=str(uuid4()),
                    tool_name=tool_name,
                    tool_label=tool_name.replace("_", " ").title(),
                    args=args,
                    description=description,
                )
            )
    return frames


def _process_stream_item(item: object) -> tuple[list[str], bool]:
    """Process a single astream item tuple and return list of SSE frames and text flag."""
    frames = []
    has_text = False
    if not isinstance(item, (tuple, list)):
        return frames, has_text

    mode = item[0]
    data = item[1] if len(item) > 1 else None

    if mode == "messages" and data is not None:
        msg = data[0] if isinstance(data, (tuple, list)) else data
        if isinstance(msg, AIMessageChunk) and msg.content:
            text = _extract_text(msg.content)
            if text:
                has_text = True
                frames.append(_sse("response", content=text))
    elif mode == "updates" and isinstance(data, dict):
        for node_name, node_state in data.items():
            if node_name in ("expense_analyst", "knowledge_wiki", "bella_deep_agent"):
                frames.append(
                    _sse(
                        "subagent_call",
                        subagent=node_name,
                        status="running",
                        details=f"Executing node task: {node_name}",
                    )
                )
            if isinstance(node_state, dict) and "messages" in node_state:
                msgs = node_state["messages"]
                if isinstance(msgs, list):
                    for msg in msgs:
                        if isinstance(msg, (AIMessage, AIMessageChunk)) and msg.content:
                            text = _extract_text(msg.content)
                            if text:
                                has_text = True
                                frames.append(_sse("response", content=text))
    return frames, has_text


async def stream_deep_agent(
    agent,
    user_input: str,
    conversation_id: UUID,
) -> AsyncGenerator[str]:
    """Stream events from the deep agent formatted as SSE."""
    thread_id = str(conversation_id) if conversation_id else str(uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    inputs = {"messages": [{"role": "user", "content": user_input}]}

    try:
        has_response = False
        async for item in agent.astream(
            inputs, config, stream_mode=["messages", "updates"], version="v2"
        ):
            frames, text_found = _process_stream_item(item)
            if text_found:
                has_response = True
            for frame in frames:
                yield frame

        state = await agent.aget_state(config)
        for intr_sse in _extract_interrupt_events(state):
            yield intr_sse

        if not has_response and hasattr(state, "values") and isinstance(state.values, dict):
            msgs = state.values.get("messages", [])
            if isinstance(msgs, list) and msgs:
                last_msg = msgs[-1]
                if isinstance(last_msg, (AIMessage, AIMessageChunk)) and last_msg.content:
                    text = _extract_text(last_msg.content)
                    if text:
                        yield _sse("response", content=text)
    except Exception as exc:
        _logger.exception(f"Deep agent stream error for thread {thread_id}")
        yield _sse("error", content=str(exc))

    yield _sse("done")


async def resume_deep_agent(
    agent,
    conversation_id: UUID,
    decision: str = "approve",
    edited_args: dict[str, object] | None = None,
) -> AsyncGenerator[str]:
    """Resume execution of a deep agent thread paused by an interrupt."""
    thread_id = str(conversation_id) if conversation_id else str(uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    decision_payload: dict[str, object] = {"type": decision}
    if decision == "edit" and edited_args is not None:
        decision_payload["edited_args"] = edited_args

    command = Command(resume={"decisions": [decision_payload]})

    try:
        has_response = False
        async for item in agent.astream(
            command, config, stream_mode=["messages", "updates"], version="v2"
        ):
            frames, text_found = _process_stream_item(item)
            if text_found:
                has_response = True
            for frame in frames:
                yield frame

        # Fallback to state check if streaming didn't produce text
        state = await agent.aget_state(config)
        if not has_response and hasattr(state, "values") and isinstance(state.values, dict):
            msgs = state.values.get("messages", [])
            if isinstance(msgs, list) and msgs:
                last_msg = msgs[-1]
                if isinstance(last_msg, (AIMessage, AIMessageChunk)) and last_msg.content:
                    text = _extract_text(last_msg.content)
                    if text:
                        yield _sse("response", content=text)
    except Exception as exc:
        _logger.exception(f"Deep agent resume error for thread {thread_id}")
        yield _sse("error", content=str(exc))

    yield _sse("done")
