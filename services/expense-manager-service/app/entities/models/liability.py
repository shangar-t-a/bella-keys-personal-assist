"""Domain models for Liabilities."""

from datetime import UTC, datetime
from enum import StrEnum

from pydantic import BaseModel, Field

from app.entities.models.base import BaseEntity
from app.entities.models.sort import SortOrder


class ValuationType(StrEnum):
    """Supported valuation models."""

    UNIT_BASED = "UNIT_BASED"
    VALUE_BASED = "VALUE_BASED"


class CompoundingFrequency(StrEnum):
    """Supported interest compounding frequencies."""

    MONTHLY = "MONTHLY"
    QUARTERLY = "QUARTERLY"
    HALF_YEARLY = "HALF_YEARLY"
    YEARLY = "YEARLY"


class LiabilityTransactionType(StrEnum):
    """Types of liability transactions."""

    BORROW = "BORROW"
    REPAY = "REPAY"
    REVALUE = "REVALUE"


class LiabilitySubcategory(BaseEntity):
    """Domain model for liability subcategory."""

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


class LiabilityCategory(BaseEntity):
    """Domain model for liability category."""

    name: str = Field(description="Name of the category")
    code: str = Field(description="Unique code of the category")
    description: str | None = Field(default=None, description="Description of the category")
    subcategories: list[LiabilitySubcategory] = Field(
        default_factory=list, description="Subcategories for the category"
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC), description="Time of creation")
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC), description="Time of last update")


class Liability(BaseEntity):
    """Domain model for liability."""

    category_id: str = Field(description="ID of the parent category")
    name: str = Field(description="Name of the liability")
    subcategory_id: str | None = Field(default=None, description="ID of the subcategory")
    original_value: float = Field(default=0.0, description="Total borrowed amount in INR")
    current_value: float = Field(default=0.0, description="Outstanding liability balance in INR")
    interest_rate: float | None = Field(default=None, description="Annual interest rate (%) of the liability")
    interest_compounding: CompoundingFrequency | None = Field(default=None, description="Compounding frequency")
    emi_amount: float | None = Field(default=None, description="Scheduled monthly EMI amount in INR")
    maturity_date: datetime | None = Field(default=None, description="Maturity/Closure date of the liability")
    notes: str | None = Field(default=None, description="Additional notes/remarks")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC), description="Time of creation")
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC), description="Time of last update")


class LiabilityTransaction(BaseEntity):
    """Domain model for liability transaction."""

    liability_id: str = Field(description="ID of the parent liability")
    transaction_type: LiabilityTransactionType = Field(description="Type: BORROW, REPAY, REVALUE")
    amount: float = Field(description="Transaction amount in INR")
    transaction_date: datetime = Field(default_factory=lambda: datetime.now(UTC), description="Date of the transaction")
    description: str | None = Field(default=None, description="Audit remark")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC), description="Time of creation")


class LiabilityFilter(BaseModel):
    """Filters for liabilities query."""

    category_id: str | None = None
    search: str | None = None


class LiabilitySortField(StrEnum):
    """Valid fields for sorting liabilities."""

    NAME = "name"
    ORIGINAL_VALUE = "original_value"
    CURRENT_VALUE = "current_value"
    CREATED_AT = "created_at"


class LiabilitySort(BaseModel):
    """Sorting configuration for liabilities."""

    sort_by: LiabilitySortField = LiabilitySortField.NAME
    sort_order: SortOrder = SortOrder.ASC
