"""Conftest for expense-manager-service integration tests."""

from unittest.mock import MagicMock

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from pytest_asyncio import is_async_test

from app import settings
from app.infrastructures.postgres_db import database
from app.main import app
from tests.unit.settings import UnitTestSettings

# --------------------------------------------------- Pytest Hooks --------------------------------------------------- #


def pytest_collection_modifyitems(items):
    """Modify collected test items to add session scope to async tests and apply unit/integration markers."""
    session_scope_marker = pytest.mark.asyncio(loop_scope="session")
    integration_marker = pytest.mark.integration
    unit_marker = pytest.mark.unit
    for item in items:
        node_path = str(item.fspath)
        if "/integration/" in node_path or "\\integration\\" in node_path:
            item.add_marker(integration_marker)
        elif "/unit/" in node_path or "\\unit\\" in node_path:
            item.add_marker(unit_marker)
        if is_async_test(item):
            item.add_marker(session_scope_marker, append=False)


# ----------------------------------------------- End of Pytest Hooks ------------------------------------------------ #

# ----------------------------------------------------- Fixtures ----------------------------------------------------- #


@pytest_asyncio.fixture(autouse=True, scope="session")
async def patch_settings():
    """Patch settings for integration tests."""
    unit_test_settings = UnitTestSettings(
        APP_ENV="test",
        STORAGE_TYPE="postgresql",
        DATABASE_URL="postgresql+asyncpg://ems_test_user:test123@localhost:5432/expense_manager_test",
    )
    settings.get_settings = MagicMock()
    settings.get_settings.return_value = unit_test_settings
    database.get_settings = MagicMock()
    database.get_settings.return_value = unit_test_settings
    yield


@pytest_asyncio.fixture(autouse=True, scope="session")
async def init_and_drop_db(patch_settings):
    """Initialize and drop the database for unit tests."""
    # Initialize the database before tests
    await database.init_db()

    yield

    # Drop the database after tests
    await database.drop_db()


@pytest_asyncio.fixture(scope="session")
async def client(patch_settings, init_and_drop_db) -> AsyncClient:
    """Provide an httpx AsyncClient wired to the FastAPI app."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


# ------------------------------------------------- End of Fixtures -------------------------------------------------- #
