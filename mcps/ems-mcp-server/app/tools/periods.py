"""MCP tools for period (month/year) operations."""

from typing import Annotated, Any

from app.client import get_ems_client


async def list_periods() -> list[dict[str, Any]]:
    """List all budget periods (month + year combinations).

    Returns every period with its id, month (1-12), and year.
    Use this to discover available periods before querying entries.
    """
    client = get_ems_client()
    response = await client.get("/v1/period/list")
    response.raise_for_status()
    return response.json()


async def get_period(period_id: Annotated[str, "The unique ID of the period"]) -> dict[str, Any]:
    """Get a single budget period by its ID.

    Returns the period's id, month, and year.
    Raises an error if the period is not found.
    """
    client = get_ems_client()
    response = await client.get(f"/v1/period/{period_id}")
    response.raise_for_status()
    return response.json()
