"""Account related entities for the Expense Manager Service."""

from typing import Literal

from pydantic import Field, model_validator

from app.entities.models.base import BaseEntity

MonthLiteral = Literal[
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
]


class AccountName(BaseEntity):
    """Entity representing an account name."""

    account_name: str

    @model_validator(mode="before")
    @classmethod
    def make_account_name_uppercase(cls, values) -> "AccountName":
        """Ensure the account name is stored in uppercase."""
        values["account_name"] = values["account_name"].upper()
        return values


class MonthYear(BaseEntity):
    """Entity representing date details with month and year."""

    month: MonthLiteral
    year: int = Field(ge=2000, le=2100)
