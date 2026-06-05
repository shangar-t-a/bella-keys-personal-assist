"""Domain models for Assets."""

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field

from app.entities.models.base import BaseEntity
from app.entities.models.sort import SortOrder


class AssetCategory(BaseEntity):
    """Domain model for asset category."""

    name: str = Field(description="Name of the category")
    code: str = Field(description="Unique code code of the category")
    description: str | None = Field(default=None, description="Description of the category")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Time of creation")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Time of last update")


class Asset(BaseEntity):
    """Domain model for asset."""

    category_id: str = Field(description="ID of the parent category")
    name: str = Field(description="Name of the asset")
    sub_category: str | None = Field(default=None, description="Type/Sub-type of the asset")
    invested_value: float = Field(default=0.0, description="Total invested value in INR")
    current_value: float = Field(default=0.0, description="Current market value in INR")
    notes: str | None = Field(default=None, description="Additional notes/remarks")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Time of creation")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Time of last update")


class AssetTransaction(BaseEntity):
    """Domain model for asset transaction."""

    asset_id: str = Field(description="ID of the parent asset")
    transaction_type: str = Field(description="Type: BUY, SELL, REVALUE")
    amount: float = Field(description="Cash flow amount in INR")
    units: float | None = Field(default=None, description="Generic quantity/weight")
    price_per_unit: float | None = Field(default=None, description="Generic price per unit/gram")
    transaction_date: datetime = Field(default_factory=datetime.utcnow, description="Date of the transaction")
    description: str | None = Field(default=None, description="Audit remark")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Time of creation")


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
