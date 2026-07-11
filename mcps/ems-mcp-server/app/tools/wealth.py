"""MCP tools for wealth and portfolio analytics operations."""

from typing import Annotated, Any

from app.client import request_ems


async def get_wealth_summary() -> dict[str, Any]:
    """Retrieve current wealth summary (total assets, liabilities, and net worth)."""
    return await request_ems("GET", "/v1/wealth/summary")


async def get_historical_net_worth(
    months: Annotated[
        int, "Number of past months of trend data to retrieve. Defaults to 12."
    ] = 12,
) -> list[dict[str, Any]]:
    """Retrieve historical net worth trend for the past N months."""
    params = {"months": months}
    return await request_ems("GET", "/v1/wealth/history", params=params)


async def get_wealth_allocation() -> dict[str, Any]:
    """Retrieve asset and liability category allocation percentages."""
    return await request_ems("GET", "/v1/wealth/allocation")
