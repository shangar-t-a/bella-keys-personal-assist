"""Domain models for Assets."""

from datetime import UTC, datetime
from enum import StrEnum

from pydantic import BaseModel, Field

from app.entities.models.base import BaseEntity
from app.entities.models.sort import SortOrder


class ValuationType(StrEnum):
    """Supported valuation models."""

    UNIT_BASED = "UNIT_BASED"
    VALUE_BASED = "VALUE_BASED"


class AssetTransactionType(StrEnum):
    """Types of asset transactions."""

    BUY = "BUY"
    SELL = "SELL"
    REVALUE = "REVALUE"


class AssetSubcategory(BaseEntity):
    """Domain model for asset subcategory."""

    category_id: str = Field(description="ID of the parent category")
    name: str = Field(description="Name of the subcategory")
    code: str = Field(description="Unique code of the subcategory")
    description: str | None = Field(
        default=None, description="Description/hints of valuation details for the subcategory"
    )
    valuation_type: ValuationType = Field(description="Valuation model (UNIT_BASED, VALUE_BASED)")
    has_interest: bool = Field(default=False, description="Whether interest tracking is supported")
    has_maturity: bool = Field(default=False, description="Whether maturity date tracking is supported")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC), description="Time of creation")
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC), description="Time of last update")


class AssetCategory(BaseEntity):
    """Domain model for asset category."""

    name: str = Field(description="Name of the category")
    code: str = Field(description="Unique code of the category")
    description: str | None = Field(default=None, description="Description of the category")
    subcategories: list[AssetSubcategory] = Field(default_factory=list, description="Subcategories for the category")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC), description="Time of creation")
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC), description="Time of last update")


class Asset(BaseEntity):
    """Domain model for asset."""

    category_id: str = Field(description="ID of the parent category")
    name: str = Field(description="Name of the asset")
    sub_category: str | None = Field(default=None, description="Type/Sub-type of the asset")
    subcategory_id: str | None = Field(default=None, description="ID of the subcategory")
    invested_value: float = Field(default=0.0, description="Total invested value in INR")
    current_value: float = Field(default=0.0, description="Current market value in INR")
    interest_rate: float | None = Field(default=None, description="Actual interest rate (%) of the asset")
    interest_compounding: str | None = Field(default=None, description="Compounding frequency (e.g. YEARLY)")
    maturity_date: datetime | None = Field(default=None, description="Maturity date of the asset")
    notes: str | None = Field(default=None, description="Additional notes/remarks")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC), description="Time of creation")
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC), description="Time of last update")


class AssetTransaction(BaseEntity):
    """Domain model for asset transaction."""

    asset_id: str = Field(description="ID of the parent asset")
    transaction_type: AssetTransactionType = Field(description="Type: BUY, SELL, REVALUE")
    amount: float = Field(description="Cash flow amount in INR")
    units: float | None = Field(default=None, description="Generic quantity/weight")
    price_per_unit: float | None = Field(default=None, description="Generic price per unit/gram")
    transaction_date: datetime = Field(default_factory=lambda: datetime.now(UTC), description="Date of the transaction")
    description: str | None = Field(default=None, description="Audit remark")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC), description="Time of creation")


class AssetFilter(BaseModel):
    """Filters for assets query."""

    category_id: str | None = None
    search: str | None = None


class AssetSortField(StrEnum):
    """Valid fields for sorting assets."""

    NAME = "name"
    INVESTED_VALUE = "invested_value"
    CURRENT_VALUE = "current_value"
    CREATED_AT = "created_at"


class AssetSort(BaseModel):
    """Sorting configuration for assets."""

    sort_by: AssetSortField = AssetSortField.NAME
    sort_order: SortOrder = SortOrder.ASC
