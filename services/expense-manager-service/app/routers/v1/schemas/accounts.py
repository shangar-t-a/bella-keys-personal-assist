"""Schemas for accounts endpoints."""

from typing import Literal

from pydantic import Field

from app.routers.v1.schemas.base import BaseSchema

# Type for month literals
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


class AccountNameRequest(BaseSchema):
    """Schema for account name creation/update requests."""

    account_name: str = Field(..., description="Name of the account", examples=["ICICI", "SBI"])


class AccountNameResponse(BaseSchema):
    """Schema for account name responses."""

    id: str = Field(..., description="Unique identifier for the account")
    account_name: str = Field(..., description="Name of the account")


class MonthYearRequest(BaseSchema):
    """Schema for month-year creation requests."""

    month: MonthLiteral = Field(..., description="Name of the month")
    year: int = Field(..., ge=2000, le=2100, description="Year between 2000 and 2100", examples=[2024, 2025])


class MonthYearResponse(BaseSchema):
    """Schema for month-year responses."""

    id: str = Field(..., description="Unique identifier for the month-year combination")
    month: MonthLiteral = Field(..., description="Name of the month")
    year: int = Field(..., description="Year value")


class AccountUpdateRequest(BaseSchema):
    """Schema for account update requests."""

    account_name: str = Field(..., description="New name for the account", examples=["ICICI"])
