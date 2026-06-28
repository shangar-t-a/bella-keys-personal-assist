"""Main entrypoint for the Auth Service."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routers.auth import router as auth_router

app = FastAPI(
    title="Bella Keys Auth Service",
    description="Authentication and Identity Management for Bella Keys",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https?://localhost(:\d+)?",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, tags=["auth"])


@app.get("/health")
async def health_check():
    """Service health check endpoint."""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    from app.core.config import get_settings

    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True
    )
