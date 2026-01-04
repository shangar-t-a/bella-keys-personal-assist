"""Models for the v1 chat router."""

from uuid import (
    UUID,
    uuid4,
)

from pydantic import (
    BaseModel,
    Field,
)


class ChatRequest(BaseModel):
    """Request body for sending a message to the chat bot."""

    message: str
    conversation_id: UUID = Field(
        default_factory=uuid4,
        description="Unique identifier for the conversation.",
    )
