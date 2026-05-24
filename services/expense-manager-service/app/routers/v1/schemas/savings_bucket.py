"""Schemas for savings buckets and transactions endpoints."""

from datetime import datetime

from pydantic import Field

from app.routers.v1.schemas.base import BaseSchema


class SavingsBucketCreateRequest(BaseSchema):
    """Schema for creating a savings bucket."""

    name: str = Field(..., description="Name of the savings bucket", min_length=1)
    target_amount: float | None = Field(None, description="Optional savings target amount", ge=0.0)


class SavingsBucketUpdateRequest(BaseSchema):
    """Schema for updating a savings bucket."""

    name: str = Field(..., description="Name of the savings bucket", min_length=1)
    target_amount: float | None = Field(None, description="Optional savings target amount", ge=0.0)


class SavingsBucketResponse(BaseSchema):
    """Schema for savings bucket responses."""

    id: str = Field(..., description="Unique identifier of the bucket")
    account_id: str = Field(..., description="Parent account ID")
    name: str = Field(..., description="Name of the bucket")
    allocated_amount: float = Field(..., description="Current allocated amount in the bucket")
    target_amount: float | None = Field(None, description="Optional target savings amount")


class SavingsBucketTransactionCreateRequest(BaseSchema):
    """Schema for creating a savings bucket transaction log."""

    source_bucket_id: str | None = Field(None, description="ID of the source bucket")
    destination_bucket_id: str | None = Field(None, description="ID of the destination bucket")
    amount: float = Field(..., description="Amount to transfer/allocate/withdraw", gt=0.0)
    transaction_type: str = Field(
        ...,
        description="Type of transaction: deposit, withdraw, allocate, release, transfer",
    )
    description: str = Field(..., description="Comment detailing the transaction", min_length=1)
    transaction_date: datetime | None = Field(None, description="Custom transaction date")


class SavingsBucketTransactionResponse(BaseSchema):
    """Schema for savings bucket transaction responses."""

    id: str = Field(..., description="Unique identifier of the transaction")
    account_id: str = Field(..., description="Parent account ID")
    source_bucket_id: str | None = Field(None, description="ID of the source bucket")
    destination_bucket_id: str | None = Field(None, description="ID of the destination bucket")
    amount: float = Field(..., description="Amount of the transaction")
    transaction_type: str = Field(..., description="Type of transaction")
    description: str = Field(..., description="Comment detailing the transaction")
    transaction_date: datetime = Field(..., description="Date and time of the transaction")
    is_cancelled: bool = Field(False, description="Whether the transaction has been cancelled")
    cancellation_reason: str | None = Field(None, description="Reason for cancellation if applicable")


class SavingsBucketTransactionCancelRequest(BaseSchema):
    """Schema for cancelling a savings bucket transaction."""

    reason: str = Field(..., description="Reason for cancelling the transaction", min_length=1)


class SavingsBucketTransactionsPageResponse(BaseSchema):
    """Schema for paginated savings bucket transaction responses."""

    transactions: list[SavingsBucketTransactionResponse] = Field(..., description="List of transactions")
    total_elements: int = Field(..., description="Total number of elements")
    limit: int = Field(..., description="Page limit")
    offset: int = Field(..., description="Page offset")
