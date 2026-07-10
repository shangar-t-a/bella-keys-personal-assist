"""MCP tools for spending entry operations."""

from typing import Annotated, Any

from app.client import request_ems


async def list_spending_entries(
    page: Annotated[int, "Page number (0-based). Defaults to 0."] = 0,
    size: Annotated[int, "Number of entries per page (1-100). Defaults to 12."] = 12,
    month: Annotated[
        int | None, "Filter by month (1-12). Omit to include all months."
    ] = None,
    year: Annotated[
        int | None, "Filter by year (e.g. 2025). Omit to include all years."
    ] = None,
    account_name: Annotated[
        str | None, "Filter by account name (e.g. 'ICICI'). Omit for all accounts."
    ] = None,
    sort_by: Annotated[
        str,
        "Single field to sort by. Must be exactly one of: 'year', 'month', 'account_name', 'starting_balance', 'current_balance', 'current_credit', 'balance_after_credit', 'total_spent'. Do NOT combine multiple fields.",
    ] = "year",
    sort_order: Annotated[str, "Sort direction: 'asc' or 'desc'."] = "asc",
) -> dict[str, Any]:
    """Retrieve paginated spending entries across all accounts.

    Each entry includes: id, accountName, month, year, startingBalance,
    currentBalance, currentCredit, balanceAfterCredit, totalSpent.
    Also returns pagination metadata (page number, size, totalElements, totalPages).

    Use filters (month, year, accountName) to narrow results.
    Use sort_by / sort_order to control ordering.
    """
    params: dict[str, Any] = {
        "page": page,
        "size": size,
        "sortBy": sort_by,
        "sortOrder": sort_order,
    }
    if month is not None:
        params["month"] = month
    if year is not None:
        params["year"] = year
    if account_name is not None:
        params["accountName"] = account_name

    return await request_ems("GET", "/v1/spending_account/list", params=params)


async def list_spending_entries_for_account(
    account_id: Annotated[str, "The unique ID of the account to query."],
    page: Annotated[int, "Page number (0-based). Defaults to 0."] = 0,
    size: Annotated[int, "Number of entries per page (1-100). Defaults to 12."] = 12,
    month: Annotated[
        int | None, "Filter by month (1-12). Omit to include all months."
    ] = None,
    year: Annotated[
        int | None, "Filter by year (e.g. 2025). Omit to include all years."
    ] = None,
    sort_by: Annotated[
        str,
        "Single field to sort by. Must be exactly one of: 'year', 'month', 'account_name', 'starting_balance', 'current_balance', 'current_credit', 'balance_after_credit', 'total_spent'. Do NOT combine multiple fields.",
    ] = "year",
    sort_order: Annotated[str, "Sort direction: 'asc' or 'desc'."] = "asc",
) -> dict[str, Any]:
    """Retrieve paginated spending entries for a specific account.

    Each entry includes: id, accountName, month, year, startingBalance,
    currentBalance, currentCredit, balanceAfterCredit, totalSpent.
    Also returns pagination metadata.

    Raises an error if the account_id is not found.
    """
    params: dict[str, Any] = {
        "page": page,
        "size": size,
        "sortBy": sort_by,
        "sortOrder": sort_order,
    }
    if month is not None:
        params["month"] = month
    if year is not None:
        params["year"] = year

    return await request_ems(
        "GET", f"/v1/spending_account/{account_id}/list", params=params
    )


async def add_spending_entry(
    account_name: Annotated[str, "Name of the spending account"],
    month: Annotated[int, "Month of the entry (1-12)"],
    year: Annotated[int, "Year of the entry (e.g. 2025)"],
    starting_balance: Annotated[float, "Starting balance of the account"],
    current_balance: Annotated[float, "Current balance of the account"],
    current_credit: Annotated[float, "Current credit of the account"],
) -> dict[str, Any]:
    """Add a new entry to the spending account."""
    json_data = {
        "account_name": account_name,
        "month": month,
        "year": year,
        "starting_balance": starting_balance,
        "current_balance": current_balance,
        "current_credit": current_credit,
    }
    return await request_ems("POST", "/v1/spending_account", json=json_data)


async def edit_spending_entry(
    entry_id: Annotated[str, "The unique ID of the entry to edit"],
    account_name: Annotated[str, "Name of the spending account"],
    month: Annotated[int, "Month of the entry (1-12)"],
    year: Annotated[int, "Year of the entry (e.g. 2025)"],
    starting_balance: Annotated[float, "Starting balance of the account"],
    current_balance: Annotated[float, "Current balance of the account"],
    current_credit: Annotated[float, "Current credit of the account"],
) -> dict[str, Any]:
    """Edit an existing spending account entry."""
    json_data = {
        "account_name": account_name,
        "month": month,
        "year": year,
        "starting_balance": starting_balance,
        "current_balance": current_balance,
        "current_credit": current_credit,
    }
    return await request_ems("PUT", f"/v1/spending_account/{entry_id}", json=json_data)


async def delete_spending_entry(
    entry_id: Annotated[str, "The unique ID of the spending entry to delete"],
) -> dict[str, Any]:
    """Delete a spending account entry by its ID."""
    return await request_ems("DELETE", f"/v1/spending_account/{entry_id}")
