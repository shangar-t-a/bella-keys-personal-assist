"""Schemas for asset API endpoints."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class BaseSchema(BaseModel):
    """Base schema with camelCase settings."""

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
    )


class AssetRequest(BaseSchema):
    """Schema for adding a new asset."""

    category_id: str = Field(description="ID of the parent category")
    name: str = Field(description="Name of the asset")
    sub_category: str | None = Field(default=None, description="Subcategory type")
    initial_amount: float = Field(description="Initial asset value or transaction amount in INR")
    units: float | None = Field(default=None, description="Quantity/Weight if unit-based")
    price_per_unit: float | None = Field(default=None, description="Price per unit/NAV if unit-based")
    notes: str | None = Field(default=None, description="Notes")


class AssetUpdateRequest(BaseSchema):
    """Schema for updating asset metadata."""

    category_id: str = Field(description="ID of the parent category")
    name: str = Field(description="Name of the asset")
    sub_category: str | None = Field(default=None, description="Subcategory type")
    notes: str | None = Field(default=None, description="Notes")


class AssetTransactionRequest(BaseSchema):
    """Schema for logging a new transaction."""

    transaction_type: str = Field(description="BUY, SELL, REVALUE")
    amount: float = Field(description="Total INR amount of the transaction")
    units: float | None = Field(default=None, description="Quantity/Weight")
    price_per_unit: float | None = Field(default=None, description="Price per unit/NAV")
    transaction_date: datetime | None = Field(default=None, description="Transaction timestamp")
    description: str | None = Field(default=None, description="Audit notes")


class AssetCategoryResponse(BaseSchema):
    """Response schema for asset category."""

    id: str
    name: str
    code: str
    description: str | None


class AssetResponse(BaseSchema):
    """Response schema for asset details."""

    id: str
    category_id: str
    category_name: str
    category_code: str
    name: str
    sub_category: str | None
    invested_value: float
    current_value: float
    notes: str | None
    absolute_returns: float
    percentage_returns: float
    created_at: datetime
    updated_at: datetime


class AssetTransactionResponse(BaseSchema):
    """Response schema for asset transaction."""

    id: str
    asset_id: str
    transaction_type: str
    amount: float
    units: float | None
    price_per_unit: float | None
    transaction_date: datetime
    description: str | None


class AssetCategorySummaryResponse(BaseSchema):
    """Response schema for category aggregate summary."""

    category_id: str
    category_name: str
    category_code: str
    total_invested: float
    total_current: float
    total_returns: float
    percentage_returns: float


class AssetSummaryResponse(BaseSchema):
    """Response schema for full wealth dashboard overview."""

    total_invested: float
    total_current: float
    total_returns: float
    percentage_returns: float
    category_breakdowns: list[AssetCategorySummaryResponse]
