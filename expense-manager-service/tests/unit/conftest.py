"""Conftest for expense-manager-service unit testing."""

from unittest.mock import MagicMock

import pytest
import pytest_asyncio

from app import settings
from app.infrastructures.inmemory_db.accounts import AccountRepository
from app.infrastructures.inmemory_db.spending_account import SpendingAccountRepository
from app.infrastructures.sqlite_db import database
from app.infrastructures.sqlite_db.accounts import SQLiteAccountRepository
from app.infrastructures.sqlite_db.spending_account import SQLiteSpendingAccountRepository
from tests.unit.settings import UnitTestSettings


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
    if settings.get_settings().STORAGE_TYPE == "sqlite":
        await database.init_db()

    yield

    # Drop the database after tests
    if settings.get_settings().STORAGE_TYPE == "sqlite":
        await database.drop_db()


@pytest.fixture(scope="session")
def account_repo(patch_settings, init_and_drop_db):
    """Provide an instance of AccountRepository."""
    if settings.get_settings().STORAGE_TYPE == "sqlite":
        return SQLiteAccountRepository()
    elif settings.get_settings().STORAGE_TYPE == "inmemory":
        return AccountRepository()
    raise NotImplementedError("Invalid STORAGE_TYPE")


@pytest.fixture(scope="session")
def spending_account_repo(patch_settings, init_and_drop_db):
    """Provide an instance of SpendingAccountRepository."""
    if settings.get_settings().STORAGE_TYPE == "sqlite":
        return SQLiteSpendingAccountRepository()
    elif settings.get_settings().STORAGE_TYPE == "inmemory":
        return SpendingAccountRepository()
    raise NotImplementedError("Invalid STORAGE_TYPE")
