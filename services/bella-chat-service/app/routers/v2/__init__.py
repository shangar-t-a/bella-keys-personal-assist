"""v2 routers for the chat application."""

from fastapi import APIRouter

from utilities.scope_guard import require_scope

from .chat import router as chat_router

v2_router = APIRouter(prefix="/v2", tags=["v2"])
v2_router.include_router(chat_router, dependencies=[require_scope("bella-chat:write")])
