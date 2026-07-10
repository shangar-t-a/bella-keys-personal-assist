"""MCP tools for savings buckets and transactions operations."""

from typing import Annotated, Any

from app.client import request_ems


async def list_savings_buckets(
    account_id: Annotated[str, "The unique ID of the savings account"],
) -> list[dict[str, Any]]:
    """Retrieve all savings buckets for a given account. Auto-seeds defaults if empty."""
    return await request_ems("GET", f"/v1/savings_buckets/list/{account_id}")


async def create_savings_bucket(
    account_id: Annotated[str, "The unique ID of the savings account"],
    name: Annotated[str, "Name of the savings bucket"],
    target_amount: Annotated[
        float | None, "Optional savings target amount (INR)"
    ] = None,
) -> dict[str, Any]:
    """Create a new savings bucket for an account."""
    json_data = {
        "name": name,
        "targetAmount": target_amount,
    }
    return await request_ems(
        "POST", f"/v1/savings_buckets/{account_id}/bucket", json=json_data
    )


async def update_savings_bucket(
    bucket_id: Annotated[str, "The unique ID of the savings bucket to update"],
    name: Annotated[str, "Name of the savings bucket"],
    target_amount: Annotated[
        float | None, "Optional savings target amount (INR)"
    ] = None,
) -> dict[str, Any]:
    """Update an existing savings bucket's details."""
    json_data = {
        "name": name,
        "targetAmount": target_amount,
    }
    return await request_ems(
        "PUT", f"/v1/savings_buckets/bucket/{bucket_id}", json=json_data
    )


async def delete_savings_bucket(
    bucket_id: Annotated[str, "The unique ID of the savings bucket to delete"],
) -> dict[str, Any]:
    """Delete a savings bucket, safely returning any remaining funds to root Savings."""
    return await request_ems("DELETE", f"/v1/savings_buckets/bucket/{bucket_id}")


async def create_savings_bucket_transaction(
    account_id: Annotated[str, "The unique ID of the savings account"],
    amount: Annotated[float, "Amount to transfer/allocate/withdraw/deposit"],
    transaction_type: Annotated[
        str, "Type of transaction: deposit, withdraw, allocate, release, transfer"
    ],
    description: Annotated[str, "Comment detailing the transaction"],
    source_bucket_id: Annotated[
        str | None, "ID of the source bucket (required for transfer/release/withdraw)"
    ] = None,
    destination_bucket_id: Annotated[
        str | None,
        "ID of the destination bucket (required for transfer/allocate/deposit)",
    ] = None,
    transaction_date: Annotated[
        str | None, "Custom transaction date (ISO format string)"
    ] = None,
) -> dict[str, Any]:
    """Create a transaction to deposit, withdraw, allocate, release or transfer savings funds."""
    json_data = {
        "sourceBucketId": source_bucket_id,
        "destinationBucketId": destination_bucket_id,
        "amount": amount,
        "transactionType": transaction_type,
        "description": description,
        "transactionDate": transaction_date,
    }
    return await request_ems(
        "POST", f"/v1/savings_buckets/{account_id}/transaction", json=json_data
    )


async def list_savings_bucket_transactions(
    account_id: Annotated[str, "The unique ID of the savings account"],
    limit: Annotated[int, "Page size limit"] = 50,
    offset: Annotated[int, "Page offset"] = 0,
) -> dict[str, Any]:
    """Retrieve transaction history for a given savings account."""
    params = {
        "limit": limit,
        "offset": offset,
    }
    return await request_ems(
        "GET", f"/v1/savings_buckets/{account_id}/transactions", params=params
    )


async def cancel_savings_bucket_transaction(
    transaction_id: Annotated[str, "The unique ID of the transaction to cancel"],
    reason: Annotated[str, "Reason for cancelling the transaction"],
) -> dict[str, Any]:
    """Cancel a transaction and reverse its balance changes atomically."""
    json_data = {
        "reason": reason,
    }
    return await request_ems(
        "POST",
        f"/v1/savings_buckets/transaction/{transaction_id}/cancel",
        json=json_data,
    )
