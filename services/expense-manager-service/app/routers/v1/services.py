"""Services for Expense Manager Service."""

from enum import Enum
from functools import lru_cache

from app.entities.repositories.accounts import AccountRepositoryInterface
from app.entities.repositories.period import PeriodRepositoryInterface
from app.entities.repositories.spending_account import SpendingAccountRepositoryInterface
from app.infrastructures.postgres_db.accounts import PostgresAccountRepository
from app.infrastructures.postgres_db.period import PostgresPeriodRepository
from app.infrastructures.postgres_db.spending_account import PostgresSpendingAccountRepository
from app.settings import get_settings
from app.use_cases.accounts import AccountService
from app.use_cases.period import PeriodService
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

    if storage_type in (StorageType.INMEMORY, StorageType.SQLITE):
        raise ValueError(f"Storage type {storage_type} is deprecated and not supported as of February 2026.")
    if storage_type == StorageType.POSTGRES:
        return PostgresAccountRepository()
    raise ValueError(f"Unsupported storage type: {storage_type}. Supported types: [{StorageType.POSTGRES}]")


def get_period_repository() -> PeriodRepositoryInterface:
    """Get the appropriate period repository based on settings."""
    settings = get_settings()
    storage_type = StorageType(settings.STORAGE_TYPE)

    if storage_type in (StorageType.INMEMORY, StorageType.SQLITE):
        raise ValueError(f"Storage type {storage_type} is deprecated and not supported as of February 2026.")
    if storage_type == StorageType.POSTGRES:
        return PostgresPeriodRepository()
    raise ValueError(f"Unsupported storage type: {storage_type}. Supported types: [{StorageType.POSTGRES}]")


def get_spending_account_repository() -> SpendingAccountRepositoryInterface:
    """Get the appropriate spending account repository based on settings."""
    settings = get_settings()
    storage_type = StorageType(settings.STORAGE_TYPE)

    if storage_type in (StorageType.INMEMORY, StorageType.SQLITE):
        raise ValueError(f"Storage type {storage_type} is deprecated and not supported as of February 2026.")
    if storage_type == StorageType.POSTGRES:
        return PostgresSpendingAccountRepository()
    raise ValueError(f"Unsupported storage type: {storage_type}. Supported types: [{StorageType.POSTGRES}]")


@lru_cache
def get_accounts_service() -> AccountService:
    """Get the Accounts Service."""
    account_repository = get_account_repository()
    return AccountService(account_repository=account_repository)


@lru_cache
def get_period_service() -> PeriodService:
    """Get the Period Service."""
    period_repository = get_period_repository()
    return PeriodService(period_repository=period_repository)


@lru_cache
def get_spending_account_service() -> SpendingAccountService:
    """Get the Spending Account Service."""
    account_repository = get_account_repository()
    period_repository = get_period_repository()
    spending_account_repository = get_spending_account_repository()
    return SpendingAccountService(
        account_repository=account_repository,
        period_repository=period_repository,
        spending_account_repository=spending_account_repository,
    )
