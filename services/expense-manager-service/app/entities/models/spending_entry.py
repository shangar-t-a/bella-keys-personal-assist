"""Spending Account related entities for the Expense Manager Service."""

from enum import StrEnum

from pydantic import Field, model_validator

from app.entities.models.base import BaseEntity
from app.entities.models.sort import SortOrder


class SpendingEntry(BaseEntity):
    """Entity representing an entry in spending account with basic details."""

    account_id: str = Field(description="ID of the account")
    period_id: str = Field(description="ID of the date detail")
    starting_balance: float = Field(description="Starting balance of the account")
    current_balance: float = Field(description="Current balance of the account")
    current_credit: float = Field(description="Current credit of the account")


class SpendingEntryWithCalc(SpendingEntry):
    """Entity representing an entry in spending account with calculated fields."""

    balance_after_credit: float = Field(default=0, description="Balance after deducting credit")
    total_spent: float = Field(default=0, description="Total amount spent from the account")

    @model_validator(mode="before")
    @classmethod
    def calculate_fields(cls, values) -> "SpendingEntryWithCalc":
        """Calculate balance after credit and total spent."""
        values["balance_after_credit"] = values["current_balance"] - values["current_credit"]
        values["total_spent"] = (values["starting_balance"] - values["current_balance"]) + values["current_credit"]
        return values


class SpendingEntryWithCalcPage(BaseEntity):
    """Entity representing a paginated list of spending account entries with calculated fields."""

    entries: list[SpendingEntryWithCalc] = Field(description="List of spending account entries with calculated fields")
    limit: int = Field(description="Number of entries per page")
    offset: int = Field(description="Offset for pagination")
    total_entries: int = Field(description="Total number of entries available")


class SpendingEntryDetailWithCalc(SpendingEntryWithCalc):
    """Entity representing a spending account entry with joined account and date details.

    This model includes account_name, month, and year from related tables,
    eliminating the need for separate foreign key lookups (N+1 query optimization).
    """

    account_name: str = Field(description="Name of the account")
    month: int = Field(description="Month of the entry")
    year: int = Field(description="Year of the entry")


class SpendingEntryDetailWithCalcPage(BaseEntity):
    """Entity representing a paginated list of spending account entries with details."""

    entries: list[SpendingEntryDetailWithCalc] = Field(
        description="List of spending account entries with account and date details"
    )
    limit: int = Field(description="Number of entries per page")
    offset: int = Field(description="Offset for pagination")
    total_entries: int = Field(description="Total number of entries available")


class SpendingEntrySortField(StrEnum):
    """Sort fields for sorting spending entries."""

    MONTH = "month"
    YEAR = "year"
    ACCOUNT_NAME = "account_name"
    STARTING_BALANCE = "starting_balance"
    CURRENT_BALANCE = "current_balance"
    CURRENT_CREDIT = "current_credit"
    BALANCE_AFTER_CREDIT = "balance_after_credit"
    TOTAL_SPENT = "total_spent"


class SpendingEntrySort(BaseEntity):
    """Entity representing sorting options for spending entries."""

    sort_by: SpendingEntrySortField = Field(default=SpendingEntrySortField.YEAR, description="Field to sort by")
    sort_order: SortOrder = Field(default=SortOrder.ASC, description="Sort order (asc/desc)")


class SpendingEntryFilter(BaseEntity):
    """Entity representing filtering options for spending entries."""

    month: int | None = Field(default=None, description="Filter by month (1-12)")
    year: int | None = Field(default=None, description="Filter by year")
    account_name: str | None = Field(default=None, description="Filter by account name")
