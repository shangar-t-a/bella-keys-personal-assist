"""Schemas for spending account endpoints."""

from pydantic import Field

from app.entities.models.sort import SortOrder
from app.entities.models.spending_entry import SpendingEntrySortField
from app.routers.v1.schemas.base import BaseSchema
from app.routers.v1.schemas.pagination import PaginationResponse


class SpendingEntryBase(BaseSchema):
    """Base schema for spending account entries."""

    account_name: str = Field(..., description="Name of the spending account", examples=["ICICI", "SBI"])
    month: int = Field(..., ge=1, le=12, description="Month of the entry", examples=[1, 2])
    year: int = Field(..., ge=2000, le=2100, description="Year between 2000 and 2100", examples=[2024, 2025])
    starting_balance: float = Field(..., description="Starting balance of the account", examples=[10000.0])
    current_balance: float = Field(..., description="Current balance of the account", examples=[8000.0])
    current_credit: float = Field(..., description="Current credit of the account", examples=[2000.0])


class SpendingEntryRequest(SpendingEntryBase):
    """Schema for spending account entry creation/update requests."""

    pass


class SpendingEntryResponse(SpendingEntryBase):
    """Schema for spending account entry responses."""

    id: str = Field(..., description="Unique identifier for the entry")


class SpendingEntryWithCalcResponse(SpendingEntryResponse):
    """Schema for spending account entry responses with calculated fields."""

    balance_after_credit: float = Field(..., description="Balance after deducting credit", examples=[6000.0])
    total_spent: float = Field(..., description="Total amount spent from the account", examples=[4000.0])


class SpendingEntryWithCalcPageResponse(BaseSchema):
    """Schema for paginated responses of spending account entries with calculated fields."""

    spending_entries: list[SpendingEntryWithCalcResponse] = Field(
        ..., description="List of spending account entries with calculated fields"
    )
    page: PaginationResponse = Field(..., description="Pagination metadata for the current page")


class SpendingEntrySortParams(BaseSchema):
    """Schema for sorting parameters when retrieving spending account entries."""

    sort_by: SpendingEntrySortField = Field(
        SpendingEntrySortField.YEAR,
        description="Field to sort by",
        examples=[SpendingEntrySortField.YEAR, SpendingEntrySortField.MONTH, SpendingEntrySortField.CURRENT_BALANCE],
    )
    sort_order: SortOrder = Field(
        SortOrder.ASC,
        description="Sort order (asc for ascending, desc for descending)",
        examples=[SortOrder.ASC, SortOrder.DESC],
    )


class SpendingEntryFilterParams(BaseSchema):
    """Schema for filtering parameters when retrieving spending account entries."""

    month: int | None = Field(None, ge=1, le=12, description="Filter by month", examples=[1, 2])
    year: int | None = Field(
        None, ge=2000, le=2100, description="Filter by year between 2000 and 2100", examples=[2024, 2025]
    )
    account_name: str | None = Field(None, description="Filter by account name", examples=["ICICI", "SBI"])
