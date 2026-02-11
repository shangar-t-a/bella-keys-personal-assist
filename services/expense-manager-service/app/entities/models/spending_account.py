"""Spending Account related entities for the Expense Manager Service."""

from pydantic import Field, model_validator

from app.entities.models.base import BaseEntity


class SpendingAccountEntry(BaseEntity):
    """Entity representing an entry in spending account with basic details."""

    account_id: str = Field(description="ID of the account")
    date_detail_id: str = Field(description="ID of the date detail")
    starting_balance: float = Field(description="Starting balance of the account")
    current_balance: float = Field(description="Current balance of the account")
    current_credit: float = Field(description="Current credit of the account")


class SpendingAccountEntryWithCalculatedFields(SpendingAccountEntry):
    """Entity representing an entry in spending account with calculated fields."""

    balance_after_credit: float = Field(default=0, description="Balance after deducting credit")
    total_spent: float = Field(default=0, description="Total amount spent from the account")

    @model_validator(mode="before")
    @classmethod
    def calculate_fields(cls, values) -> "SpendingAccountEntryWithCalculatedFields":
        """Calculate balance after credit and total spent."""
        values["balance_after_credit"] = values["current_balance"] - values["current_credit"]
        values["total_spent"] = (values["starting_balance"] - values["current_balance"]) + values["current_credit"]
        return values


class SpendingAccountEntryWithCalculatedFieldsPaginated(BaseEntity):
    """Entity representing a paginated list of spending account entries with calculated fields."""

    entries: list[SpendingAccountEntryWithCalculatedFields] = Field(
        description="List of spending account entries with calculated fields"
    )
    limit: int = Field(description="Number of entries per page")
    offset: int = Field(description="Offset for pagination")
    total_entries: int = Field(description="Total number of entries available")
