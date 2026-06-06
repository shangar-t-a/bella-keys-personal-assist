"""Schemas for asset API endpoints."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

from app.entities.models.asset import AssetTransactionType, CompoundingFrequency


class BaseSchema(BaseModel):
    """Base schema with camelCase settings."""

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
    )


# Sub-schemas


class AssetInterestDetailsSchema(BaseSchema):
    """Schema for interest-bearing asset fields."""

    interest_rate: float = Field(gt=0, description="Annual interest rate (%)")
    compounding: CompoundingFrequency = Field(description="Compounding frequency")
    maturity_date: datetime | None = Field(default=None, description="Maturity date of the asset")


class AssetUnitDetailsSchema(BaseSchema):
    """Schema for unit-based asset fields."""

    units: float = Field(gt=0, description="Quantity/Weight of units purchased")
    price_per_unit: float = Field(gt=0, description="Price per unit/NAV at time of transaction")


# Request schemas


class AssetRequest(BaseSchema):
    """Schema for adding a new asset."""

    category_id: str = Field(description="ID of the parent category")
    name: str = Field(description="Name of the asset")
    subcategory_id: str | None = Field(default=None, description="ID of the subcategory")
    initial_amount: float = Field(gt=0, description="Amount for the initial BUY transaction (INR)")
    unit_details: AssetUnitDetailsSchema | None = Field(
        default=None, description="Unit-based fields. Required for UNIT_BASED subcategories."
    )
    interest_details: AssetInterestDetailsSchema | None = Field(
        default=None, description="Interest fields. Required for interest-bearing subcategories."
    )
    notes: str | None = Field(default=None, description="Additional notes/remarks")


class AssetUpdateRequest(BaseSchema):
    """Schema for partially updating asset metadata (PATCH)."""

    category_id: str | None = Field(default=None, description="ID of the parent category")
    name: str | None = Field(default=None, description="Name of the asset")
    subcategory_id: str | None = Field(default=None, description="ID of the subcategory")
    interest_details: AssetInterestDetailsSchema | None = Field(
        default=None, description="Updated interest fields. Pass null to clear interest tracking."
    )
    notes: str | None = Field(default=None, description="Additional notes/remarks")


class AssetTransactionRequest(BaseSchema):
    """Schema for logging a new transaction."""

    transaction_type: AssetTransactionType = Field(description="Transaction type: BUY, SELL, or REVALUE")
    amount: float = Field(gt=0, description="Total INR amount of the transaction")
    unit_details: AssetUnitDetailsSchema | None = Field(
        default=None, description="Unit-based fields. Required for BUY/SELL on unit-based assets."
    )
    transaction_date: datetime | None = Field(default=None, description="Transaction timestamp")
    description: str | None = Field(default=None, description="Audit remark")


# Response schemas


class AssetSubcategoryResponse(BaseSchema):
    """Response schema for asset subcategory."""

    id: str
    category_id: str
    name: str
    code: str
    description: str | None = Field(default=None)
    valuation_type: str
    has_interest: bool
    has_maturity: bool


class AssetCategoryResponse(BaseSchema):
    """Response schema for asset category."""

    id: str
    name: str
    code: str
    description: str | None
    subcategories: list[AssetSubcategoryResponse] = Field(default_factory=list)


class AssetResponse(BaseSchema):
    """Response schema for asset details."""

    id: str
    category_id: str
    category_name: str
    category_code: str
    name: str
    subcategory_id: str | None
    invested_value: float
    current_value: float
    interest_rate: float | None
    interest_compounding: CompoundingFrequency | None
    maturity_date: datetime | None
    notes: str | None
    absolute_returns: float
    percentage_returns: float
    created_at: datetime
    updated_at: datetime


class AssetTransactionResponse(BaseSchema):
    """Response schema for asset transaction."""

    id: str
    asset_id: str
    transaction_type: AssetTransactionType
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
