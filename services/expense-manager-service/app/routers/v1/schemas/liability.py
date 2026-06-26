"""Schemas for liability API endpoints."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

from app.entities.models.liability import CompoundingFrequency, LiabilityTransactionType


class BaseSchema(BaseModel):
    """Base schema with camelCase settings."""

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
    )


# Sub-schemas


class LiabilityInterestDetailsSchema(BaseSchema):
    """Schema for interest-bearing liability fields."""

    interest_rate: float = Field(gt=0, description="Annual interest rate (%)")
    compounding: CompoundingFrequency = Field(description="Compounding frequency")
    emi_amount: float | None = Field(default=None, gt=0, description="Scheduled monthly EMI amount (INR)")
    emi_start_date: datetime | None = Field(default=None, description="Date when EMI repayments officially begin")
    maturity_date: datetime | None = Field(default=None, description="Maturity date of the liability")


# Request schemas


class LiabilityRequest(BaseSchema):
    """Schema for adding a new liability."""

    category_id: str = Field(description="ID of the parent category")
    name: str = Field(description="Name of the liability")
    subcategory_id: str | None = Field(default=None, description="ID of the subcategory")
    initial_amount: float = Field(gt=0, description="Amount for the initial BORROW transaction (INR)")
    initial_date: datetime | None = Field(default=None, description="Timestamp of initial borrowing")
    interest_details: LiabilityInterestDetailsSchema | None = Field(
        default=None, description="Interest fields. Required for interest-bearing subcategories."
    )
    notes: str | None = Field(default=None, description="Additional notes/remarks")


class LiabilityUpdateRequest(BaseSchema):
    """Schema for partially updating liability metadata (PATCH)."""

    category_id: str | None = Field(default=None, description="ID of the parent category")
    name: str | None = Field(default=None, description="Name of the liability")
    subcategory_id: str | None = Field(default=None, description="ID of the subcategory")
    interest_details: LiabilityInterestDetailsSchema | None = Field(
        default=None, description="Updated interest fields. Pass null to clear interest tracking."
    )
    notes: str | None = Field(default=None, description="Additional notes/remarks")


class LiabilityTransactionRequest(BaseSchema):
    """Schema for logging a new transaction."""

    transaction_type: LiabilityTransactionType = Field(description="Transaction type: BORROW, REPAY, or REVALUE")
    amount: float = Field(gt=0, description="Total INR amount of the transaction")
    transaction_date: datetime | None = Field(default=None, description="Transaction timestamp")
    description: str | None = Field(default=None, description="Audit remark")


# Response schemas


class LiabilitySubcategoryResponse(BaseSchema):
    """Response schema for liability subcategory."""

    id: str
    category_id: str
    name: str
    code: str
    description: str | None = Field(default=None)
    valuation_type: str
    has_interest: bool
    has_maturity: bool


class LiabilityCategoryResponse(BaseSchema):
    """Response schema for liability category."""

    id: str
    name: str
    code: str
    description: str | None
    subcategories: list[LiabilitySubcategoryResponse] = Field(default_factory=list)


class LiabilityResponse(BaseSchema):
    """Response schema for liability details."""

    id: str
    category_id: str
    category_name: str
    category_code: str
    name: str
    subcategory_id: str | None
    original_value: float
    current_value: float
    interest_rate: float | None
    interest_compounding: CompoundingFrequency | None
    emi_amount: float | None
    emi_start_date: datetime | None
    maturity_date: datetime | None
    notes: str | None
    total_repaid: float
    accumulated_interest: float
    progress_pct: float
    remaining_tenure_months: int | None = Field(default=None, description="Estimated remaining tenure in months")
    created_at: datetime
    updated_at: datetime


class LiabilityTransactionResponse(BaseSchema):
    """Response schema for liability transaction."""

    id: str
    liability_id: str
    transaction_type: LiabilityTransactionType
    amount: float
    transaction_date: datetime
    description: str | None


class LiabilityCategorySummaryResponse(BaseSchema):
    """Response schema for category aggregate summary."""

    category_id: str
    category_name: str
    category_code: str
    total_original: float
    total_outstanding: float
    total_repaid: float
    accumulated_interest: float


class LiabilitySummaryResponse(BaseSchema):
    """Response schema for full liabilities dashboard overview."""

    total_original: float
    total_outstanding: float
    total_repaid: float
    accumulated_interest: float
    category_breakdowns: list[LiabilityCategorySummaryResponse]


class LiabilityProjectionPointResponse(BaseSchema):
    """API response schema for a single projection monthly data point."""

    date: str
    ideal_balance: float
    actual_balance: float | None = None
    ideal_interest_paid: float
    actual_interest_paid: float | None = None


class LiabilityProjectionMetricsResponse(BaseSchema):
    """API response schema for liability payoff projection metrics."""

    ideal_tenure_months: int
    remaining_tenure_months: int | None = None
    tenure_saved_months: int | None = None
    total_interest_ideal: float
    total_interest_projected: float
    interest_saved: float
    ideal_end_date: datetime | None = None
    projected_end_date: datetime | None = None


class LiabilityProjectionsResponse(BaseSchema):
    """API response schema for complete liability projections."""

    metrics: LiabilityProjectionMetricsResponse
    projection_points: list[LiabilityProjectionPointResponse]
