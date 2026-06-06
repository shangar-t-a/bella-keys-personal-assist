"""Savings bucket related entities for the Expense Manager Service."""

from datetime import UTC, datetime

from pydantic import Field

from app.entities.models.base import BaseEntity


class SavingsBucket(BaseEntity):
    """Entity representing a savings bucket (envelope)."""

    account_id: str = Field(description="ID of the parent account")
    name: str = Field(description="Name of the bucket")
    allocated_amount: float = Field(default=0.0, description="Amount allocated to this bucket")
    target_amount: float | None = Field(default=None, description="Optional target savings amount")


class SavingsBucketTransaction(BaseEntity):
    """Entity representing a transaction in a savings bucket (ledger entry)."""

    account_id: str = Field(description="ID of the parent account")
    source_bucket_id: str | None = Field(default=None, description="ID of the source bucket (if applicable)")
    destination_bucket_id: str | None = Field(default=None, description="ID of the destination bucket (if applicable)")
    amount: float = Field(description="Amount of the transaction")
    transaction_type: str = Field(description="Type of transaction (deposit, withdraw, allocate, release, transfer)")
    description: str = Field(description="Audit comment for this transaction")
    transaction_date: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="Date and time of the transaction"
    )
    is_cancelled: bool = Field(default=False, description="Whether the transaction has been cancelled")
    cancellation_reason: str | None = Field(default=None, description="Reason for cancellation if applicable")
