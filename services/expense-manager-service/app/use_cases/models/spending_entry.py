"""Models for use cases."""

from pydantic import Field

from app.use_cases.models.base import BaseEntity
from app.use_cases.models.pagination import Page


class SpendingEntryCreate(BaseEntity):
    """Model for creating a spending account entry with flattened details."""

    account_name: str = Field(description="Name of the account")
    month: int = Field(description="Month of the entry")
    year: int = Field(description="Year of the entry")
    starting_balance: float = Field(description="Starting balance of the account")
    current_balance: float = Field(description="Current balance of the account")
    current_credit: float = Field(description="Current credit of the account")


class SpendingEntry(SpendingEntryCreate):
    """Flattened output model for SpendingEntry with related details."""

    id: str = Field(description="ID of the spending account entry")


class SpendingEntryWithCalc(SpendingEntry):
    """Flattened output model for SpendingEntry with related details and calculated fields."""

    balance_after_credit: float = Field(description="Balance after applying current credit")
    total_spent: float = Field(description="Total amount spent from starting balance to current balance")


class SpendingEntryWithCalcPage(BaseEntity):
    """Model for paginated response of flattened spending account entries with calculated fields."""

    spending_entries: list[SpendingEntryWithCalc] = Field(
        description="List of flattened spending account entries with calculated fields"
    )
    page: Page = Field(description="Pagination metadata for the current page")
