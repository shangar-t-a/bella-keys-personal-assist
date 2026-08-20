"""Chat endpoints for the chat bot (v1 Legacy)."""

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from app.agents.v2.deep_orchestrator import stream_deep_agent
from app.routers.v1.models import ChatRequest
from utilities.logger import GetAppLogger

router = APIRouter(prefix="/chat")
_logger = GetAppLogger().get_logger()


@router.post("/", deprecated=True)
async def stream_response(
    chat_request: ChatRequest,
    request: Request,
) -> StreamingResponse:
    """Send a message to Bella and get a streamed response (v1 Deprecated API)."""
    query = chat_request.message.strip()
    conversation_id = chat_request.conversation_id
    auth_header = request.headers.get("Authorization")

    agent = request.app.state.orchestrator_agent
    _logger.info(f"Deep agent (v1 compat) query: {query}")

    response_gen = stream_deep_agent(
        agent=agent, user_input=query, conversation_id=conversation_id, auth_header=auth_header
    )
    return StreamingResponse(response_gen, media_type="text/event-stream")


