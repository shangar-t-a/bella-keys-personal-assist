"""Database configuration for PostgreSQL."""

from functools import lru_cache

from sqlalchemy.ext.asyncio import (AsyncSession,
    async_sessionmaker,
    create_async_engine
)
from sqlalchemy.orm import declarative_base

from app.core.config import get_settings


@lru_cache(maxsize=1)
def get_engine():
    """Get the async database engine."""
    postgres_url = get_settings().DATABASE_URL.get_secret_value()
    return create_async_engine(
        postgres_url,
        echo=get_settings().LOG_DB_QUERIES,
    )


@lru_cache(maxsize=1)
def get_async_session_maker():
    """Get the async session factory."""
    engine = get_engine()
    return async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


Base = declarative_base()


async def get_db():
    """Yield a database session."""
    session_maker = get_async_session_maker()
    async with session_maker() as session:
        yield session
