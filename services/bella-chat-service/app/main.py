"""Bella Chat Application."""

import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime, timedelta

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from openinference.instrumentation.langchain import LangChainInstrumentor
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from app.dependencies.agents import create_orchestrator_agent
from app.dependencies.ai_dependencies import (
    get_app_embedding_client,
    get_app_synthesis_llm_client,
    get_app_vector_db_client,
    get_app_vector_store,
)
from app.routers import app_router
from app.settings import get_settings
from utilities.auth_middleware import JWTAuthMiddleware

# Suppress noisy schema-conversion warnings from the Gemini tool adapter.
# LangChain logs a WARNING for every tool schema field it drops (e.g.
# "additionalProperties"), which floods the console when MCP tools are loaded.
logging.getLogger("langchain_google_genai").setLevel(logging.ERROR)


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

    # Add JWT Auth Middleware for protecting endpoints
    app.add_middleware(
        JWTAuthMiddleware,
        secret_key=settings.JWT_SECRET.get_secret_value() if hasattr(settings, "JWT_SECRET") else None,
    )


def setup_arize_tracing() -> None:
    """Setup Arize tracing if enabled."""
    settings = get_settings()
    if settings.ARIZE_ENABLED:
        resource = Resource(
            attributes={
                "service.name": settings.ARIZE_PROJECT_NAME,
            }
        )
        trace_provider = TracerProvider(resource=resource)

        # Configure standard OTLP HTTP exporter pointing to the Phoenix collector endpoint
        exporter = OTLPSpanExporter(endpoint=settings.ARIZE_TRACES_URL)
        span_processor = BatchSpanProcessor(exporter)
        trace_provider.add_span_processor(span_processor)

        trace.set_tracer_provider(trace_provider)

        LangChainInstrumentor().instrument(tracer_provider=trace_provider)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager."""
    # Set application start time
    app.state.start_time = datetime.now()

    # Initialize orchestrator agent with async resources (Postgres checkpointer, MCP client)
    # These must remain in lifespan as they are async context managers requiring proper cleanup
    async with create_orchestrator_agent() as orchestrator_agent:
        app.state.orchestrator_agent = orchestrator_agent
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

    # Create FastAPI app
    app = FastAPI(
        lifespan=lifespan,
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        debug=settings.DEBUG,
    )

    # Setup Arize tracing if enabled
    setup_arize_tracing()

    # Setup middlewares
    setup_middlewares(app, settings)

    @app.get("/health")
    async def health_check(request: Request) -> dict[str, str]:
        """Health check endpoint."""
        uptime_seconds = (datetime.now() - request.app.state.start_time).total_seconds()
        uptime_str = str(timedelta(seconds=int(uptime_seconds)))
        return {
            "status": "healthy",
            "version": settings.APP_VERSION,
            "start_time": request.app.state.start_time.isoformat(),
            "uptime": uptime_str,
        }

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
