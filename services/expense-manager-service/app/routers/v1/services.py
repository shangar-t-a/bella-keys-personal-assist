"""Services for Expense Manager Service."""

from enum import Enum
from functools import lru_cache

from app.entities.repositories.accounts import AccountRepositoryInterface
from app.entities.repositories.spending_account import SpendingAccountRepositoryInterface
from app.infrastructures.inmemory_db.accounts import AccountRepository as InMemoryAccountRepository
from app.infrastructures.inmemory_db.spending_account import (
    SpendingAccountRepository as InMemorySpendingAccountRepository,
)
from app.infrastructures.postgres_db.accounts import PostgresAccountRepository
from app.infrastructures.postgres_db.spending_account import PostgresSpendingAccountRepository
from app.infrastructures.sqlite_db.accounts import SQLiteAccountRepository
from app.infrastructures.sqlite_db.spending_account import SQLiteSpendingAccountRepository
from app.settings import get_settings
from app.use_cases.accounts import AccountService
from app.use_cases.spending_account import SpendingAccountService


class StorageType(str, Enum):
    """Storage type enum."""

    INMEMORY = "inmemory"
    SQLITE = "sqlite"
    POSTGRES = "postgresql"


def get_account_repository() -> AccountRepositoryInterface:
    """Get the appropriate account repository based on settings."""
    settings = get_settings()
    storage_type = StorageType(settings.STORAGE_TYPE)

    if storage_type == StorageType.SQLITE:
        return SQLiteAccountRepository()
    elif storage_type == StorageType.POSTGRES:
        return PostgresAccountRepository()
    return InMemoryAccountRepository()


def get_spending_account_repository() -> SpendingAccountRepositoryInterface:
    """Get the appropriate spending account repository based on settings."""
    settings = get_settings()
    storage_type = StorageType(settings.STORAGE_TYPE)

    if storage_type == StorageType.SQLITE:
        return SQLiteSpendingAccountRepository()
    elif storage_type == StorageType.POSTGRES:
        return PostgresSpendingAccountRepository()
    return InMemorySpendingAccountRepository()


@lru_cache
def get_spending_account_service() -> SpendingAccountService:
    """Get the Spending Account Service."""
    account_repository = get_account_repository()
    spending_account_repository = get_spending_account_repository()
    return SpendingAccountService(
        account_repository=account_repository, spending_account_repository=spending_account_repository
    )


@lru_cache
def get_accounts_service() -> AccountService:
    """Get the Accounts Service."""
    account_repository = get_account_repository()
    return AccountService(account_repository=account_repository)
