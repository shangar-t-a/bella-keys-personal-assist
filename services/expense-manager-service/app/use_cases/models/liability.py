"""Use case models for Liabilities."""

from datetime import datetime

from pydantic import BaseModel, Field

from app.entities.models.liability import CompoundingFrequency, LiabilityTransactionType


class BaseInput(BaseModel):
    """Base pydantic model with default configuration."""

    pass


class LiabilityInterestDetails(BaseInput):
    """Grouping for interest-bearing liability fields."""

    interest_rate: float = Field(gt=0, description="Annual interest rate (%) of the liability")
    compounding: CompoundingFrequency = Field(description="Compounding frequency")
    emi_amount: float | None = Field(default=None, gt=0, description="Scheduled monthly EMI amount (INR)")
    maturity_date: datetime | None = Field(default=None, description="Maturity date of the liability")


class LiabilityCreate(BaseInput):
    """Model for creating a new liability."""

    category_id: str = Field(description="ID of the parent category")
    name: str = Field(description="Name of the liability")
    subcategory_id: str | None = Field(default=None, description="ID of the subcategory")
    initial_amount: float = Field(gt=0, description="Amount of the initial BORROW transaction (INR)")
    initial_date: datetime | None = Field(
        default=None, description="Disbursal/start date of the initial BORROW transaction"
    )
    interest_details: LiabilityInterestDetails | None = Field(
        default=None, description="Interest fields. Required if subcategory has_interest is True."
    )
    notes: str | None = Field(default=None, description="Additional notes/remarks")


class LiabilityUpdate(BaseInput):
    """Model for partially updating a liability's metadata."""

    category_id: str | None = Field(default=None, description="ID of the parent category")
    name: str | None = Field(default=None, description="Name of the liability")
    subcategory_id: str | None = Field(default=None, description="ID of the subcategory")
    interest_details: LiabilityInterestDetails | None = Field(
        default=None, description="Updated interest details. Pass None if clearing interest tracking."
    )
    notes: str | None = Field(default=None, description="Additional notes/remarks")


class LiabilityTransactionCreate(BaseInput):
    """Model for logging a new transaction for a liability."""

    transaction_type: LiabilityTransactionType = Field(description="Transaction type: BORROW, REPAY, or REVALUE")
    amount: float = Field(gt=0, description="Amount of the transaction in INR")
    transaction_date: datetime = Field(description="Date of the transaction")
    description: str | None = Field(default=None, description="Audit remark")


class BaseEntity(BaseModel):
    """Base response model."""

    pass


class LiabilityWithCalc(BaseEntity):
    """Output model for Liability details including calculated values."""

    id: str = Field(description="ID of the liability")
    category_id: str = Field(description="Category ID")
    category_name: str = Field(description="Name of the category")
    category_code: str = Field(description="Unique code of the category")
    name: str = Field(description="Name of the liability")
    subcategory_id: str | None = Field(default=None, description="Subcategory ID")
    original_value: float = Field(description="Original borrowed value in INR")
    current_value: float = Field(description="Current outstanding balance in INR")
    interest_rate: float | None = Field(default=None, description="Annual interest rate (%)")
    interest_compounding: CompoundingFrequency | None = Field(default=None, description="Compounding frequency")
    emi_amount: float | None = Field(default=None, description="Scheduled monthly EMI amount (INR)")
    maturity_date: datetime | None = Field(default=None, description="Maturity date of the liability")
    notes: str | None = Field(default=None, description="Additional notes")
    total_repaid: float = Field(default=0.0, description="Total amount repaid so far")
    accumulated_interest: float = Field(default=0.0, description="Accumulated interest/charges")
    progress_pct: float = Field(default=0.0, description="Repayment progress percentage")
    created_at: datetime
    updated_at: datetime


class LiabilityCategorySummary(BaseEntity):
    """Aggregate stats for a specific liability category."""

    category_id: str
    category_name: str
    category_code: str
    total_original: float
    total_outstanding: float
    total_repaid: float
    accumulated_interest: float


class LiabilitySummary(BaseEntity):
    """Liabilities summary overview for the wealth dashboard."""

    total_original: float
    total_outstanding: float
    total_repaid: float
    accumulated_interest: float
    category_breakdowns: list[LiabilityCategorySummary]


class LiabilityProjectionPoint(BaseModel):
    """A single monthly data point in a liability projection."""

    date: str = Field(description="Month in YYYY-MM format")
    ideal_balance: float = Field(description="Expected outstanding balance in INR")
    actual_balance: float | None = Field(default=None, description="Actual/projected outstanding balance in INR")
    ideal_interest_paid: float = Field(default=0.0, description="Ideal accumulated interest paid in INR")
    actual_interest_paid: float | None = Field(default=None, description="Actual/projected accumulated interest paid in INR")


class LiabilityProjectionMetrics(BaseModel):
    """Calculated metrics for liability payoff comparisons."""

    ideal_tenure_months: int = Field(description="Total months in ideal schedule")
    remaining_tenure_months: int = Field(description="Remaining months under projected path")
    tenure_saved_months: int = Field(description="Months saved by prepayments/revaluations")
    total_interest_ideal: float = Field(description="Total interest expected under scheduled plan")
    total_interest_projected: float = Field(description="Total interest expected under current trajectory")
    interest_saved: float = Field(description="Interest savings generated (INR)")
    ideal_end_date: datetime | None = Field(default=None, description="Projected end date under scheduled plan")
    projected_end_date: datetime | None = Field(default=None, description="Projected end date under current trajectory")


class LiabilityProjections(BaseEntity):
    """Complete projections response."""

    metrics: LiabilityProjectionMetrics
    projection_points: list[LiabilityProjectionPoint]
