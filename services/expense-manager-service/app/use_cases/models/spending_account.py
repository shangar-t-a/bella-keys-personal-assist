"""Models for use cases."""

from pydantic import Field

from app.entities.models.accounts import MonthLiteral
from app.use_cases.models.base import BaseEntity


class FlattenedSpendingAccountEntryCreate(BaseEntity):
    """Model for creating a spending account entry with flattened details."""

    account_name: str = Field(description="Name of the account")
    month: MonthLiteral = Field(description="Month of the entry")
    year: int = Field(description="Year of the entry")
    starting_balance: float = Field(description="Starting balance of the account")
    current_balance: float = Field(description="Current balance of the account")
    current_credit: float = Field(description="Current credit of the account")


class FlattenedSpendingAccountEntry(FlattenedSpendingAccountEntryCreate):
    """Flattened output model for SpendingAccountEntry with related details."""

    id: str = Field(description="ID of the spending account entry")


class FlattenedSpendingAccountEntryWithCalculatedFields(FlattenedSpendingAccountEntry):
    """Flattened output model for SpendingAccountEntry with related details and calculated fields."""

    balance_after_credit: float = Field(description="Balance after applying current credit")
    total_spent: float = Field(description="Total amount spent from starting balance to current balance")
