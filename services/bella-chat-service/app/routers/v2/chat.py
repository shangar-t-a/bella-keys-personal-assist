"""Next-Gen Chat Endpoints for Bella v2 powered by native deepagents harness."""

from uuid import UUID

from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.responses import StreamingResponse

from app.agents.v2.deep_orchestrator import resume_deep_agent, stream_deep_agent
from app.core.artifacts import artifact_manager
from app.dependencies.agents import build_agent, get_mcp_tools
from app.routers.v2.models import ChatRequestV2, ResumeRequest
from utilities.logger import GetAppLogger

router = APIRouter(prefix="/chat", tags=["v2-chat"])
_logger = GetAppLogger().get_logger()


@router.post("/")
async def stream_response_v2(
    chat_request: ChatRequestV2,
    request: Request,
) -> StreamingResponse:
    """Send a message to Bella v2 Deep Agent and stream responses."""
    query = chat_request.message.strip()
    conversation_id = chat_request.conversation_id
    auth_header = request.headers.get("Authorization")

    _logger.info(f"Deep Agent v2 processing query: {query}")

    mcp_tools = await get_mcp_tools(auth_header)
    agent = build_agent(mcp_tools=mcp_tools, checkpointer=request.app.state.checkpointer)

    response_gen = stream_deep_agent(
        agent=agent,
        user_input=query,
        conversation_id=conversation_id,
    )
    return StreamingResponse(response_gen, media_type="text/event-stream")


@router.post("/resume")
async def resume_response_v2(
    resume_request: ResumeRequest,
    request: Request,
) -> StreamingResponse:
    """Resume an interrupted conversation thread with human approval decision."""
    conversation_id = resume_request.conversation_id
    decision_type = resume_request.decision.type
    edited_args = resume_request.decision.edited_args
    auth_header = request.headers.get("Authorization")

    _logger.info(f"Resuming deep agent thread {conversation_id} with decision: {decision_type}")

    mcp_tools = await get_mcp_tools(auth_header)
    agent = build_agent(mcp_tools=mcp_tools, checkpointer=request.app.state.checkpointer)

    response_gen = resume_deep_agent(
        agent=agent,
        conversation_id=conversation_id,
        decision=decision_type,
        edited_args=edited_args,
    )
    return StreamingResponse(response_gen, media_type="text/event-stream")


@router.get("/artifacts/{conversation_id}/{artifact_id}")
async def get_artifact(
    conversation_id: UUID,
    artifact_id: str,
) -> Response:
    """Download or view a generated virtual filesystem artifact."""
    result = artifact_manager.read_artifact_content(conversation_id, artifact_id)
    if not result:
        raise HTTPException(status_code=404, detail="Artifact not found")

    content, mime_type = result
    return Response(content=content, media_type=mime_type)
