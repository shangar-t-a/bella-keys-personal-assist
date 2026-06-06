"""Use case models for Assets."""

from datetime import UTC, datetime

from pydantic import Field

from app.entities.models.asset import AssetTransactionType
from app.use_cases.models.base import BaseEntity


class AssetCreate(BaseEntity):
    """Model for creating a new asset."""

    category_id: str = Field(description="ID of the parent category")
    name: str = Field(description="Name of the asset")
    sub_category: str | None = Field(default=None, description="Legacy subcategory type")
    subcategory_id: str | None = Field(default=None, description="ID of the subcategory")
    initial_amount: float = Field(description="Initial asset value or transaction amount in INR")
    units: float | None = Field(default=None, description="Quantity/Weight if unit-based")
    price_per_unit: float | None = Field(default=None, description="Price per unit/NAV if unit-based")
    interest_rate: float | None = Field(default=None, description="Actual interest rate (%) of the asset")
    interest_compounding: str | None = Field(default=None, description="Compounding frequency (e.g. YEARLY)")
    maturity_date: datetime | None = Field(default=None, description="Maturity date of the asset")
    notes: str | None = Field(default=None, description="Notes")


class AssetUpdate(BaseEntity):
    """Model for updating an asset's metadata."""

    category_id: str = Field(description="ID of the parent category")
    name: str = Field(description="Name of the asset")
    sub_category: str | None = Field(default=None, description="Legacy subcategory type")
    subcategory_id: str | None = Field(default=None, description="ID of the subcategory")
    interest_rate: float | None = Field(default=None, description="Actual interest rate (%) of the asset")
    interest_compounding: str | None = Field(default=None, description="Compounding frequency (e.g. YEARLY)")
    maturity_date: datetime | None = Field(default=None, description="Maturity date of the asset")
    notes: str | None = Field(default=None, description="Notes")


class AssetTransactionCreate(BaseEntity):
    """Model for logging a new transaction for an asset."""

    transaction_type: AssetTransactionType = Field(description="BUY, SELL, REVALUE")
    amount: float = Field(description="Total INR amount of the transaction")
    units: float | None = Field(default=None, description="Quantity/Weight")
    price_per_unit: float | None = Field(default=None, description="Price per unit/NAV")
    transaction_date: datetime = Field(default_factory=lambda: datetime.now(UTC), description="Transaction timestamp")
    description: str | None = Field(default=None, description="Audit notes")


class AssetWithCalc(BaseEntity):
    """Output model for Asset details including calculated fields."""

    id: str = Field(description="ID of the asset")
    category_id: str = Field(description="ID of the parent category")
    category_name: str = Field(description="Name of the category")
    category_code: str = Field(description="Code of the category")
    name: str = Field(description="Name of the asset")
    sub_category: str | None = Field(default=None, description="Legacy subcategory type")
    subcategory_id: str | None = Field(default=None, description="ID of the subcategory")
    invested_value: float = Field(description="Invested value in INR")
    current_value: float = Field(description="Current value in INR")
    interest_rate: float | None = Field(default=None, description="Actual interest rate (%) of the asset")
    interest_compounding: str | None = Field(default=None, description="Compounding frequency (e.g. YEARLY)")
    maturity_date: datetime | None = Field(default=None, description="Maturity date of the asset")
    notes: str | None = Field(default=None, description="Notes")
    absolute_returns: float = Field(description="Absolute gains/losses in INR")
    percentage_returns: float = Field(description="Return percentage")
    created_at: datetime
    updated_at: datetime


class AssetCategorySummary(BaseEntity):
    """Aggregate stats for a specific asset category."""

    category_id: str = Field(description="ID of the category")
    category_name: str = Field(description="Name of the category")
    category_code: str = Field(description="Code of the category")
    total_invested: float = Field(description="Sum of invested value in INR")
    total_current: float = Field(description="Sum of current value in INR")
    total_returns: float = Field(description="Gains/losses in INR")
    percentage_returns: float = Field(description="Return percentage")


class AssetSummary(BaseEntity):
    """Asset summary overview for the dashboard."""

    total_invested: float = Field(description="Total amount invested in INR")
    total_current: float = Field(description="Total current value in INR")
    total_returns: float = Field(description="Total absolute returns in INR")
    percentage_returns: float = Field(description="Total ROI percentage")
    category_breakdowns: list[AssetCategorySummary] = Field(description="Breakdown by category code")
