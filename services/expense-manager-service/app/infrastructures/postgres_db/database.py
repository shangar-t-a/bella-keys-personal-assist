"""Database configuration for PostgreSQL."""

from functools import lru_cache

from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.settings import get_settings


# Create async engine
@lru_cache(maxsize=1)
def get_engine():
    """Get the database engine."""
    postgres_url = get_settings().DATABASE_URL.get_secret_value()
    return create_async_engine(
        postgres_url,
        echo=get_settings().LOG_DB_QUERIES,
    )


# Create async session factory
@lru_cache(maxsize=1)
def get_async_session():
    """Get the async session factory."""
    engine = get_engine()
    return async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""

    pass


async def init_db() -> None:
    """Initialize the database, creating all tables."""
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_db() -> None:
    """Drop all tables in the database."""
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
