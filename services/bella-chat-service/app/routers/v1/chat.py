"""Chat endpoints for the chat bot."""

import json
from typing import Annotated
from uuid import uuid4

from fastapi import (
    APIRouter,
    Depends,
)
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage
from pydantic import (
    BaseModel,
    Field,
)

from app.core.llms.clients import (
    GeminiClient,
    OllamaClient,
)
from app.core.vector_store import (
    CustomQdrantVectorStore,
)
from app.dependencies.ai_dependencies import (
    get_app_synthesis_llm_client,
    get_app_vector_store,
)
from app.routers.v1.prompts import SYNTHESIS_PROMPT_TEMPLATE
from utilities.logger import GetAppLogger

router = APIRouter(prefix="/chat")


class ChatResponse(BaseModel):
    """Response body for chat bot responses."""

    response: str = Field(..., description="The response from the chat bot.")
    sources: list[str] = Field(
        ..., description="List of `source` URLs from the contexts used to generate the response."
    )


class ChatRequest(BaseModel):
    """Request body for sending a message to the chat bot."""

    message: str


async def text_stream(text: str, chunk_size: int = 10):
    """Yields the input text in fixed-size chunks, preserving all formatting."""
    for index in range(0, len(text), chunk_size):
        yield text[index : index + chunk_size]


async def generate_streaming_response(
    llm: GeminiClient | OllamaClient,
    prompt: str,
) -> StreamingResponse:
    """Generate a streaming response from the LLM."""
    # Call LLM with prompt with embedded context and chat response schema
    structured_response: ChatResponse = await llm.aquery_structured(
        messages=[HumanMessage(content=prompt)],
        response_model=ChatResponse,
    )
    # Parse chat response model to string for streaming
    response_str = ""
    if structured_response.response:
        response_str += str(structured_response.response)
        if structured_response.sources:
            response_str += "\n\n## Sources:\n"
            for source in structured_response.sources:
                response_str += f"- {source}\n"
    else:
        response_str += "I'm sorry, I couldn't generate a response with my knowledge."

    return StreamingResponse(
        text_stream(response_str),
        media_type="text/event-stream",
    )


@router.post("/")
async def send_message(
    chat_request: ChatRequest,
    llm: Annotated[GeminiClient | OllamaClient, Depends(get_app_synthesis_llm_client)],
    vector_store: Annotated[CustomQdrantVectorStore, Depends(get_app_vector_store)],
) -> StreamingResponse:
    """Send a message to the chat bot and get a response."""
    logger = GetAppLogger().get_logger()

    # Extract and clean the user query
    query = chat_request.message.strip()

    # Retrieve relevant documents from the vector store
    relevant_docs = vector_store.similarity_search(query=query, k=3)

    # Construct the prompt for the LLM
    context = {}
    for doc, score in relevant_docs:
        context[doc.metadata.get("id", str(uuid4()))] = {
            "page_content": doc.page_content,
            "score": score,
            "source": doc.metadata.get("source", "unknown"),
            "metadata": doc.metadata,
        }
    prompt = SYNTHESIS_PROMPT_TEMPLATE.format(
        context=json.dumps(context, indent=2),
        question=query,
    )

    logger.debug(f"Constructed prompt for LLM: {prompt}")
    # Generate streaming response from LLM
    return await generate_streaming_response(llm=llm, prompt=prompt)
