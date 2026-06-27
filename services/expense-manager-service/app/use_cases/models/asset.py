"""Use case models for Assets."""

from datetime import UTC, datetime

from pydantic import Field, model_validator

from app.entities.models.asset import AssetTransactionType, CompoundingFrequency
from app.use_cases.models.base import BaseEntity, BaseInput

# Composable sub-models


class AssetInterestDetails(BaseInput):
    """Grouping for interest-bearing asset fields."""

    interest_rate: float = Field(gt=0, description="Annual interest rate (%)")
    compounding: CompoundingFrequency = Field(description="Compounding frequency")
    maturity_date: datetime | None = Field(default=None, description="Maturity date of the asset")


class AssetUnitDetails(BaseInput):
    """Grouping for unit-based asset fields (stocks, gold, ETFs)."""

    units: float | None = Field(default=None, gt=0, description="Quantity/Weight of units purchased")
    price_per_unit: float = Field(gt=0, description="Price per unit/NAV at time of transaction")


# Input models


class AssetCreate(BaseInput):
    """Model for creating a new asset."""

    category_id: str = Field(description="ID of the parent category")
    name: str = Field(description="Name of the asset")
    subcategory_id: str | None = Field(default=None, description="ID of the subcategory")
    initial_amount: float = Field(gt=0, description="Amount for the initial BUY transaction recorded on creation (INR)")
    unit_details: AssetUnitDetails | None = Field(
        default=None, description="Unit-based fields (units, price_per_unit). Required for UNIT_BASED subcategories."
    )
    interest_details: AssetInterestDetails | None = Field(
        default=None, description="Interest fields. Required for interest-bearing subcategories."
    )
    notes: str | None = Field(default=None, description="Additional notes/remarks")


class AssetUpdate(BaseInput):
    """Model for partially updating an asset's metadata (PATCH semantics).

    All fields are optional. Only supplied fields are applied; the rest
    are preserved from the existing asset record.
    """

    category_id: str | None = Field(default=None, description="ID of the parent category")
    name: str | None = Field(default=None, description="Name of the asset")
    subcategory_id: str | None = Field(default=None, description="ID of the subcategory")
    interest_details: AssetInterestDetails | None = Field(
        default=None, description="Updated interest fields. Pass null to clear interest tracking."
    )
    notes: str | None = Field(default=None, description="Additional notes/remarks")


class AssetTransactionCreate(BaseInput):
    """Model for logging a new transaction for an asset."""

    transaction_type: AssetTransactionType = Field(description="Transaction type: BUY, SELL, or REVALUE")
    amount: float = Field(gt=0, description="Total INR amount of the transaction")
    unit_details: AssetUnitDetails | None = Field(
        default=None,
        description="Unit-based fields. Required for BUY/SELL on unit-based assets.",
    )
    transaction_date: datetime = Field(default_factory=lambda: datetime.now(UTC), description="Date of the transaction")
    description: str | None = Field(default=None, description="Audit remark")

    @model_validator(mode="after")
    def validate_unit_consistency(self) -> "AssetTransactionCreate":
        """Enforce that BUY/SELL transactions provide unit_details if the asset is unit-based.

        This is a soft validation: unit_details is allowed to be None for VALUE_BASED assets.
        If unit_details is provided, both units and price_per_unit must be present.
        """
        if self.transaction_type in (AssetTransactionType.BUY, AssetTransactionType.SELL):
            if self.unit_details is not None and self.unit_details.units is None:
                raise ValueError("Units must be specified for BUY or SELL transactions.")
        return self


# Output models


class AssetWithCalc(BaseEntity):
    """Output model for Asset details including calculated return fields."""

    id: str = Field(description="ID of the asset")
    category_id: str = Field(description="ID of the parent category")
    category_name: str = Field(description="Name of the category")
    category_code: str = Field(description="Code of the category")
    name: str = Field(description="Name of the asset")
    subcategory_id: str | None = Field(default=None, description="ID of the subcategory")
    invested_value: float = Field(description="Total invested value in INR")
    current_value: float = Field(description="Current market value in INR")
    interest_rate: float | None = Field(default=None, description="Annual interest rate (%) of the asset")
    interest_compounding: CompoundingFrequency | None = Field(default=None, description="Compounding frequency")
    maturity_date: datetime | None = Field(default=None, description="Maturity date of the asset")
    notes: str | None = Field(default=None, description="Additional notes/remarks")
    absolute_returns: float = Field(description="Absolute gains/losses in INR (can be negative for losses)")
    percentage_returns: float = Field(description="Return percentage (can be negative for losses)")
    created_at: datetime = Field(description="Time of creation")
    updated_at: datetime = Field(description="Time of last update")


class AssetCategorySummary(BaseEntity):
    """Aggregate stats for a specific asset category."""

    category_id: str = Field(description="ID of the category")
    category_name: str = Field(description="Name of the category")
    category_code: str = Field(description="Code of the category")
    total_invested: float = Field(description="Sum of invested value in INR")
    total_current: float = Field(description="Sum of current value in INR")
    total_returns: float = Field(description="Gains/losses in INR (negative indicates a loss)")
    percentage_returns: float = Field(description="Return percentage (negative indicates a loss)")


class AssetSummary(BaseEntity):
    """Asset summary overview for the dashboard."""

    total_invested: float = Field(description="Total amount invested in INR")
    total_current: float = Field(description="Total current value in INR")
    total_returns: float = Field(description="Total absolute returns in INR (negative indicates a loss)")
    percentage_returns: float = Field(description="Total ROI percentage (negative indicates a loss)")
    category_breakdowns: list[AssetCategorySummary] = Field(description="Per-category breakdown")
