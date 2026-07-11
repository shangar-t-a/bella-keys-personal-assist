"""MCP tools for period (month/year) operations."""

from typing import Annotated, Any

from app.client import request_ems


async def list_periods() -> list[dict[str, Any]]:
    """List all budget periods (month + year combinations).

    Returns every period with its id, month (1-12), and year.
    Use this to discover available periods before querying entries.
    """
    return await request_ems("GET", "/v1/period/list")


async def get_period(
    period_id: Annotated[str, "The unique ID of the period"],
) -> dict[str, Any]:
    """Get a single budget period by its ID.

    Returns the period's id, month, and year.
    Raises an error if the period is not found.
    """
    return await request_ems("GET", f"/v1/period/{period_id}")


async def get_or_create_period(
    month: Annotated[int, "The month of the period (1-12)"],
    year: Annotated[int, "The year of the period (e.g. 2025)"],
) -> dict[str, Any]:
    """Retrieve an existing budget period or create a new one with the provided month and year."""
    return await request_ems(
        "POST", "/v1/period/get_or_create", json={"month": month, "year": year}
    )


async def update_period(
    period_id: Annotated[str, "The unique ID of the period to update"],
    month: Annotated[int, "The new month (1-12)"],
    year: Annotated[int, "The new year (e.g. 2025)"],
) -> dict[str, Any]:
    """Update an existing budget period with the provided month and year."""
    return await request_ems(
        "PUT", f"/v1/period/{period_id}", json={"month": month, "year": year}
    )


async def delete_period(
    period_id: Annotated[str, "The unique ID of the period to delete"],
) -> dict[str, Any]:
    """Delete a budget period by its ID."""
    return await request_ems("DELETE", f"/v1/period/{period_id}")
