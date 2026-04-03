"""MCP tools for spending entry operations."""

from typing import Annotated, Any

from app.client import get_ems_client


async def list_spending_entries(
    page: Annotated[int, "Page number (0-based). Defaults to 0."] = 0,
    size: Annotated[int, "Number of entries per page (1-100). Defaults to 12."] = 12,
    month: Annotated[int | None, "Filter by month (1-12). Omit to include all months."] = None,
    year: Annotated[int | None, "Filter by year (e.g. 2025). Omit to include all years."] = None,
    account_name: Annotated[str | None, "Filter by account name (e.g. 'ICICI'). Omit for all accounts."] = None,
    sort_by: Annotated[str, "Field to sort by: 'year', 'month', 'currentBalance', etc."] = "year",
    sort_order: Annotated[str, "Sort direction: 'asc' or 'desc'."] = "asc",
) -> dict[str, Any]:
    """Retrieve paginated spending entries across all accounts.

    Each entry includes: id, accountName, month, year, startingBalance,
    currentBalance, currentCredit, balanceAfterCredit, totalSpent.
    Also returns pagination metadata (page number, size, totalElements, totalPages).

    Use filters (month, year, accountName) to narrow results.
    Use sort_by / sort_order to control ordering.
    """
    client = get_ems_client()
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

    response = await client.get("/v1/spending_account/list", params=params)
    response.raise_for_status()
    return response.json()


async def list_spending_entries_for_account(
    account_id: Annotated[str, "The unique ID of the account to query."],
    page: Annotated[int, "Page number (0-based). Defaults to 0."] = 0,
    size: Annotated[int, "Number of entries per page (1-100). Defaults to 12."] = 12,
    month: Annotated[int | None, "Filter by month (1-12). Omit to include all months."] = None,
    year: Annotated[int | None, "Filter by year (e.g. 2025). Omit to include all years."] = None,
    sort_by: Annotated[str, "Field to sort by: 'year', 'month', 'currentBalance', etc."] = "year",
    sort_order: Annotated[str, "Sort direction: 'asc' or 'desc'."] = "asc",
) -> dict[str, Any]:
    """Retrieve paginated spending entries for a specific account.

    Each entry includes: id, accountName, month, year, startingBalance,
    currentBalance, currentCredit, balanceAfterCredit, totalSpent.
    Also returns pagination metadata.

    Raises an error if the account_id is not found.
    """
    client = get_ems_client()
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

    response = await client.get(f"/v1/spending_account/{account_id}/list", params=params)
    response.raise_for_status()
    return response.json()
