"""Schemas for spending account endpoints."""

from pydantic import Field

from app.routers.v1.schemas.base import BaseSchema


class SpendingAccountEntryBase(BaseSchema):
    """Base schema for spending account entries."""

    account_name: str = Field(..., description="Name of the spending account", examples=["ICICI", "SBI"])
    month: str = Field(..., description="Month of the entry", examples=["January", "February"])
    year: int = Field(..., ge=2000, le=2100, description="Year between 2000 and 2100", examples=[2024, 2025])
    starting_balance: float = Field(..., description="Starting balance of the account", examples=[10000.0])
    current_balance: float = Field(..., description="Current balance of the account", examples=[8000.0])
    current_credit: float = Field(..., description="Current credit of the account", examples=[2000.0])


class SpendingAccountEntryRequest(SpendingAccountEntryBase):
    """Schema for spending account entry creation/update requests."""

    pass


class SpendingAccountEntryResponse(SpendingAccountEntryBase):
    """Schema for spending account entry responses."""

    id: str = Field(..., description="Unique identifier for the entry")


class SpendingAccountEntryWithCalculatedFieldsResponse(SpendingAccountEntryResponse):
    """Schema for spending account entry responses with calculated fields."""

    balance_after_credit: float = Field(..., description="Balance after deducting credit", examples=[6000.0])
    total_spent: float = Field(..., description="Total amount spent from the account", examples=[4000.0])
