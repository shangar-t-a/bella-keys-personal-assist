"""Models for the v2 chat router supporting Deep Agents & HITL."""

from typing import Any, Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class ChatRequestV2(BaseModel):
    """Request body for v2 chat endpoint."""

    message: str = Field(..., description="User prompt or question.")
    conversation_id: UUID = Field(
        default_factory=uuid4,
        description="Unique identifier for the conversation thread.",
    )
    enable_hitl: bool = Field(
        default=True,
        description="Whether to pause for human approval on high-impact tool calls.",
    )


class ResumeDecision(BaseModel):
    """Payload for human-in-the-loop decision."""

    type: Literal["approve", "edit", "reject"] = Field(
        ...,
        description="Approval type: 'approve' to run tool, 'edit' to modify args, 'reject' to cancel.",
    )
    edited_args: dict[str, Any] | None = Field(
        default=None,
        description="Modified tool arguments if decision type is 'edit'.",
    )


class ResumeRequest(BaseModel):
    """Request body for resuming an interrupted conversation."""

    conversation_id: UUID = Field(..., description="Unique conversation thread ID.")
    interrupt_id: str = Field(..., description="Interrupt identifier emitted in the SSE interrupt event.")
    decision: ResumeDecision = Field(..., description="Decision payload.")


class ArtifactResponse(BaseModel):
    """Metadata response for a virtual filesystem artifact."""

    artifact_id: str
    conversation_id: str
    filename: str
    mime_type: str
    size_bytes: int
    metadata: dict[str, Any] = Field(default_factory=dict)
