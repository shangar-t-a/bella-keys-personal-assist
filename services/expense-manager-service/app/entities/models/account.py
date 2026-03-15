"""Account related entities for the Expense Manager Service."""

from pydantic import Field, model_validator

from app.entities.models.base import BaseEntity


class Account(BaseEntity):
    """Entity representing an account name."""

    account_name: str = Field(description="Name of the account")

    @model_validator(mode="before")
    @classmethod
    def make_account_name_uppercase(cls, values) -> "Account":
        """Ensure the account name is stored in uppercase."""
        values["account_name"] = values["account_name"].upper()
        return values
