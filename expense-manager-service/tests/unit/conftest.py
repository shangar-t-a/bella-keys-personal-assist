"""Conftest for expense-manager-service unit testing."""

from unittest.mock import MagicMock

import pytest
import pytest_asyncio
from pytest_asyncio import is_async_test

from app import settings
from app.infrastructures.postgres_db import database
from app.infrastructures.postgres_db.accounts import PostgresAccountRepository
from app.infrastructures.postgres_db.spending_account import PostgresSpendingAccountRepository
from tests.unit.settings import UnitTestSettings

# --------------------------------------------------- Pytest Hooks --------------------------------------------------- #


def pytest_collection_modifyitems(items):
    """Modify collected test items to add session scope to async tests."""
    pytest_asyncio_tests = (item for item in items if is_async_test(item))
    session_scope_marker = pytest.mark.asyncio(loop_scope="session")
    for async_test in pytest_asyncio_tests:
        async_test.add_marker(session_scope_marker, append=False)


# ----------------------------------------------- End of Pytest Hooks ------------------------------------------------ #

# ----------------------------------------------------- Fixtures ----------------------------------------------------- #


@pytest_asyncio.fixture(autouse=True, scope="session")
async def patch_settings():
    """Patch settings for unit tests."""
    settings.get_settings = MagicMock()
    settings.get_settings.return_value = UnitTestSettings()
    database.get_settings = MagicMock()
    database.get_settings.return_value = UnitTestSettings()
    yield


@pytest_asyncio.fixture(autouse=True, scope="session")
async def init_and_drop_db(patch_settings):
    """Initialize and drop the database for unit tests."""
    # Initialize the database before tests
    await database.init_db()

    yield

    # Drop the database after tests
    await database.drop_db()


@pytest.fixture(scope="session")
def account_repo(patch_settings, init_and_drop_db):
    """Provide an instance of AccountRepository."""
    if settings.get_settings().STORAGE_TYPE == "postgresql":
        return PostgresAccountRepository()
    raise NotImplementedError("Invalid STORAGE_TYPE")


@pytest.fixture(scope="session")
def spending_account_repo(patch_settings, init_and_drop_db):
    """Provide an instance of SpendingAccountRepository."""
    if settings.get_settings().STORAGE_TYPE == "postgresql":
        return PostgresSpendingAccountRepository()
    raise NotImplementedError("Invalid STORAGE_TYPE")


# ------------------------------------------------- End of Fixtures -------------------------------------------------- #
