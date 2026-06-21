"""Services for Expense Manager Service."""

from enum import StrEnum
from functools import lru_cache

from app.entities.repositories.account import AccountRepositoryInterface
from app.entities.repositories.asset import AssetRepositoryInterface
from app.entities.repositories.liability import LiabilityRepositoryInterface
from app.entities.repositories.monthly_planner import MonthlyPlannerRepositoryInterface
from app.entities.repositories.period import PeriodRepositoryInterface
from app.entities.repositories.savings_bucket import SavingsBucketRepositoryInterface
from app.entities.repositories.spending_entry import SpendingEntryRepositoryInterface
from app.infrastructures.postgres_db.account import PostgresAccountRepository
from app.infrastructures.postgres_db.asset import PostgresAssetRepository
from app.infrastructures.postgres_db.liability import PostgresLiabilityRepository
from app.infrastructures.postgres_db.monthly_planner import PostgresMonthlyPlannerRepository
from app.infrastructures.postgres_db.period import PostgresPeriodRepository
from app.infrastructures.postgres_db.savings_bucket import PostgresSavingsBucketRepository
from app.infrastructures.postgres_db.spending_entry import PostgresSpendingEntryRepository
from app.settings import get_settings
from app.use_cases.account import AccountService
from app.use_cases.asset import AssetService
from app.use_cases.liability import LiabilityService
from app.use_cases.monthly_planner import MonthlyPlannerService
from app.use_cases.period import PeriodService
from app.use_cases.savings_bucket import SavingsBucketService
from app.use_cases.spending_entry import SpendingEntryService


class StorageType(StrEnum):
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


def get_spending_entry_repository() -> SpendingEntryRepositoryInterface:
    """Get the appropriate spending account repository based on settings."""
    settings = get_settings()
    storage_type = StorageType(settings.STORAGE_TYPE)

    if storage_type in (StorageType.INMEMORY, StorageType.SQLITE):
        raise ValueError(f"Storage type {storage_type} is deprecated and not supported as of February 2026.")
    if storage_type == StorageType.POSTGRES:
        return PostgresSpendingEntryRepository()
    raise ValueError(f"Unsupported storage type: {storage_type}. Supported types: [{StorageType.POSTGRES}]")


def get_monthly_planner_repository() -> MonthlyPlannerRepositoryInterface:
    """Get the appropriate monthly planner repository based on settings."""
    settings = get_settings()
    storage_type = StorageType(settings.STORAGE_TYPE)

    if storage_type in (StorageType.INMEMORY, StorageType.SQLITE):
        raise ValueError(f"Storage type {storage_type} is deprecated and not supported as of February 2026.")
    if storage_type == StorageType.POSTGRES:
        return PostgresMonthlyPlannerRepository()
    raise ValueError(f"Unsupported storage type: {storage_type}. Supported types: [{StorageType.POSTGRES}]")


def get_savings_bucket_repository() -> SavingsBucketRepositoryInterface:
    """Get the appropriate savings bucket repository based on settings."""
    settings = get_settings()
    storage_type = StorageType(settings.STORAGE_TYPE)

    if storage_type in (StorageType.INMEMORY, StorageType.SQLITE):
        raise ValueError(f"Storage type {storage_type} is deprecated and not supported as of February 2026.")
    if storage_type == StorageType.POSTGRES:
        return PostgresSavingsBucketRepository()
    raise ValueError(f"Unsupported storage type: {storage_type}. Supported types: [{StorageType.POSTGRES}]")


def get_asset_repository() -> AssetRepositoryInterface:
    """Get the appropriate asset repository based on settings."""
    settings = get_settings()
    storage_type = StorageType(settings.STORAGE_TYPE)

    if storage_type in (StorageType.INMEMORY, StorageType.SQLITE):
        raise ValueError(f"Storage type {storage_type} is deprecated and not supported as of February 2026.")
    if storage_type == StorageType.POSTGRES:
        return PostgresAssetRepository()
    raise ValueError(f"Unsupported storage type: {storage_type}. Supported types: [{StorageType.POSTGRES}]")


def get_liability_repository() -> LiabilityRepositoryInterface:
    """Get the appropriate liability repository based on settings."""
    settings = get_settings()
    storage_type = StorageType(settings.STORAGE_TYPE)

    if storage_type in (StorageType.INMEMORY, StorageType.SQLITE):
        raise ValueError(f"Storage type {storage_type} is deprecated and not supported as of February 2026.")
    if storage_type == StorageType.POSTGRES:
        return PostgresLiabilityRepository()
    raise ValueError(f"Unsupported storage type: {storage_type}. Supported types: [{StorageType.POSTGRES}]")


@lru_cache
def get_account_service() -> AccountService:
    """Get the Accounts Service."""
    account_repository = get_account_repository()
    return AccountService(account_repository=account_repository)


@lru_cache
def get_period_service() -> PeriodService:
    """Get the Period Service."""
    period_repository = get_period_repository()
    return PeriodService(period_repository=period_repository)


@lru_cache
def get_spending_entry_service() -> SpendingEntryService:
    """Get the Spending Account Service."""
    account_repository = get_account_repository()
    period_repository = get_period_repository()
    spending_account_repository = get_spending_entry_repository()
    return SpendingEntryService(
        account_repository=account_repository,
        period_repository=period_repository,
        spending_account_repository=spending_account_repository,
    )


@lru_cache
def get_monthly_planner_service() -> MonthlyPlannerService:
    """Get the Monthly Planner Service."""
    monthly_planner_repository = get_monthly_planner_repository()
    period_repository = get_period_repository()
    return MonthlyPlannerService(
        monthly_planner_repository=monthly_planner_repository,
        period_repository=period_repository,
    )


@lru_cache
def get_savings_bucket_service() -> SavingsBucketService:
    """Get the Savings Bucket Service."""
    savings_bucket_repository = get_savings_bucket_repository()
    return SavingsBucketService(savings_bucket_repository=savings_bucket_repository)


@lru_cache
def get_asset_service() -> AssetService:
    """Get the Asset Service."""
    asset_repository = get_asset_repository()
    return AssetService(asset_repository=asset_repository)


@lru_cache
def get_liability_service() -> LiabilityService:
    """Get the Liability Service."""
    liability_repository = get_liability_repository()
    return LiabilityService(liability_repository=liability_repository)
