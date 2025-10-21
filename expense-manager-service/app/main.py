"""Main entry point for the Expense Manager Service."""

from contextlib import asynccontextmanager
from datetime import datetime, timedelta

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.infrastructures.postgres_db.database import init_db
from app.routers.v1 import router as v1_router
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

    # Initialize database
    await init_db()

    yield


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()

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
app.include_router(v1_router)


@app.get("/")
async def read_root() -> dict[str, str]:
    """Root endpoint."""
    return {"message": "Welcome to the Expense Manager Service!"}


@app.get("/health")
async def health_check(request: Request) -> dict[str, str]:
    """Health check endpoint.

    Returns:
        Dict containing service health information including:
        - status: Current service status
        - version: Application version
        - start_time: Service start time in ISO format
        - uptime: Service uptime in hh:mm:ss format
    """
    uptime_seconds = (datetime.now() - request.app.state.start_time).total_seconds()
    uptime_str = str(timedelta(seconds=int(uptime_seconds)))
    return {
        "status": "healthy",
        "version": request.app.version,
        "start_time": request.app.state.start_time.isoformat(),
        "uptime": uptime_str,
    }


if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
