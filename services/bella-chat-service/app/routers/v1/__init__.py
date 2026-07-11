"""v1 routers for the chat application."""

from fastapi import APIRouter

from utilities.scope_guard import require_scope

from .chat import router as chat_router

v1_router = APIRouter(prefix="/v1", tags=["v1"])

# The chat endpoint (POST /chat/) sends messages on behalf of the user and requires write access.
# bella-chat:read would gate any future read-only endpoints (e.g. listing chat history).
v1_router.include_router(chat_router, dependencies=[require_scope("bella-chat:write")])

