"""MCP tools for spending account operations."""

from typing import Annotated, Any

from app.client import get_ems_client


async def list_accounts() -> list[dict[str, Any]]:
    """List all spending accounts.

    Returns every account with its id and account_name.
    Use this to discover available accounts before querying entries.
    """
    client = get_ems_client()
    response = await client.get("/v1/account/list")
    response.raise_for_status()
    return response.json()


async def get_account(account_id: Annotated[str, "The unique ID of the account"]) -> dict[str, Any]:
    """Get a single spending account by its ID.

    Returns the account's id and account_name.
    Raises an error if the account is not found.
    """
    client = get_ems_client()
    response = await client.get(f"/v1/account/{account_id}")
    response.raise_for_status()
    return response.json()
