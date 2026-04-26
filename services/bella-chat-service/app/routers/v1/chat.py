"""Chat endpoints for the chat bot."""

from typing import TYPE_CHECKING

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from app.routers.v1.models import ChatRequest
from utilities.logger import GetAppLogger

if TYPE_CHECKING:
    from app.agents.orchestrator_agent.agent import OrchestratorAgent

router = APIRouter(prefix="/chat")

_logger = GetAppLogger().get_logger()


@router.post("/")
async def stream_response(
    chat_request: ChatRequest,
    request: Request,
) -> StreamingResponse:
    """Send a message to Bella and get a streamed response.

    The orchestrator agent routes the query to EMS MCP tools (for expense data)
    or the RAG knowledge search (for personal wiki), then synthesises a reply.
    """
    query = chat_request.message.strip()
    conversation_id = chat_request.conversation_id

    orchestrator_agent: OrchestratorAgent = request.app.state.orchestrator_agent
    _logger.info(f"Orchestrator processing query: {query}")

    response_gen = orchestrator_agent.stream_response(user_input=query, conversation_id=conversation_id)
    return StreamingResponse(response_gen, media_type="text/event-stream")
