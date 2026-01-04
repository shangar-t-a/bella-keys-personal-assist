"""Chat endpoints for the chat bot."""

from typing import (
    Annotated,
)

from fastapi import (
    APIRouter,
    Depends,
)
from fastapi.responses import StreamingResponse

from app.agents import (
    RAGAgent,
    SimpleChatAgent,
)
from app.dependencies.agents import (
    get_rag_agent,
    get_simple_chat_agent,
)
from app.routers.v1.models import ChatRequest
from utilities.logger import GetAppLogger

router = APIRouter(prefix="/chat")


@router.post("/")
async def stream_response(
    chat_request: ChatRequest,
    simple_chat_agent: Annotated[SimpleChatAgent, Depends(get_simple_chat_agent)],
    rag_agent: Annotated[RAGAgent, Depends(get_rag_agent)],
) -> StreamingResponse:
    """Send a message to the chat bot and get a response."""
    logger = GetAppLogger().get_logger()

    # Extract and clean the user query
    query = chat_request.message.strip()
    # Get conversation ID
    conversation_id = chat_request.conversation_id

    # Use RAG agent to get context and answer the query
    logger.info(f"RAG Agent processing query: {query}")

    # Generate streaming response from LLM
    response_gen = await rag_agent.run(user_input=query, conversation_id=conversation_id, stream=True)
    return StreamingResponse(response_gen, media_type="text/event-stream")
