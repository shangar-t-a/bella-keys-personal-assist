"""Chat endpoints for the chat bot (v1 Legacy)."""

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from app.agents.v2.deep_orchestrator import stream_deep_agent
from app.dependencies.agents import build_agent, get_mcp_tools
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

    _logger.info(f"Deep agent (v1 compat) query: {query}")

    mcp_tools = await get_mcp_tools(auth_header)
    agent = build_agent(mcp_tools=mcp_tools, checkpointer=request.app.state.checkpointer)

    response_gen = stream_deep_agent(
        agent=agent, user_input=query, conversation_id=conversation_id
    )
    return StreamingResponse(response_gen, media_type="text/event-stream")
