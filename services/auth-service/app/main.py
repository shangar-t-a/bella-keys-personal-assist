"""Main entrypoint for the Auth Service."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app import __version__
from app.api.routers.auth import router as auth_router
from app.api.routers.oauth import router as oauth_router
from app.core.config import get_settings

app = FastAPI(
    title="Bella Keys Auth Service",
    description="Authentication and Identity Management for Bella Keys",
    version=__version__,
)

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https?://localhost(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, tags=["auth"])
app.include_router(oauth_router, tags=["oauth"])


@app.get("/health")
async def health_check():
    """Service health check endpoint."""
    return {"status": "ok"}


if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=True)
