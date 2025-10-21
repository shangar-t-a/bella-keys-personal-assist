"""Bella Chat Application."""

import os
from contextlib import asynccontextmanager
from datetime import datetime

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.dependencies.ai_dependencies import (
    get_app_embedding_client,
    get_app_synthesis_llm_client,
    get_app_vector_db_client,
    get_app_vector_store,
)
from app.routers import app_router
from app.settings import get_settings


def setup_middlewares(app: FastAPI, settings) -> None:
    """Setup middleware for the application."""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=settings.ALLOWED_METHODS,
        allow_headers=settings.ALLOWED_HEADERS,
        expose_headers=settings.CORS_EXPOSE_HEADERS,
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager."""
    # Set application start time
    app.state.start_time = datetime.now()

    yield


def create_ai_dependencies(settings):
    """Create and configure AI dependencies."""
    # Initialize AI clients

    # 1. Synthesis LLM Client
    get_app_synthesis_llm_client()

    # 2. Embedding Client
    get_app_embedding_client()

    # 3. Vector DB Client and Vector Store
    get_app_vector_db_client()

    # 4. Vector Store
    get_app_vector_store()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    # Get settings
    settings = get_settings()

    # Set APP_NAME environment variable if not set
    if os.getenv("APP_NAME", None) is None:
        os.environ["APP_NAME"] = settings.APP_NAME

    # Initialize AI clients
    create_ai_dependencies(settings)

    app = FastAPI(
        lifespan=lifespan,
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        debug=settings.DEBUG,
    )

    # Setup middlewares
    setup_middlewares(app, settings)

    return app


app = create_app()
app.include_router(app_router)

if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.FASTAPI_LOG_LEVEL.lower(),
    )
