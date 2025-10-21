"""v1 routers for the chat application."""

from fastapi import APIRouter

from .chat import router as chat_router

v1_router = APIRouter(prefix="/v1", tags=["v1"])

v1_router.include_router(chat_router)
