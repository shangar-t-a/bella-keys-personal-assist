"""MCP tools for spending account operations."""

from typing import Annotated, Any

from app.client import request_ems


async def list_accounts() -> list[dict[str, Any]]:
    """List all spending accounts.

    Returns every account with its id and account_name.
    Use this to discover available accounts before querying entries.
    """
    return await request_ems("GET", "/v1/account/list")


async def get_account(
    account_id: Annotated[str, "The unique ID of the account"],
) -> dict[str, Any]:
    """Get a single spending account by its ID.

    Returns the account's id and account_name.
    Raises an error if the account is not found.
    """
    return await request_ems("GET", f"/v1/account/{account_id}")


async def get_or_create_account(
    account_name: Annotated[str, "The name of the account to retrieve or create"],
) -> dict[str, Any]:
    """Create or retrieve a spending account with the given name."""
    return await request_ems(
        "POST", "/v1/account/get_or_create", json={"account_name": account_name}
    )


async def update_account_name(
    account_id: Annotated[str, "The unique ID of the account to update"],
    account_name: Annotated[str, "The new name for the account"],
) -> dict[str, Any]:
    """Update the name of an existing spending account."""
    return await request_ems(
        "PUT", f"/v1/account/{account_id}", json={"account_name": account_name}
    )


async def delete_account(
    account_id: Annotated[str, "The unique ID of the account to delete"],
) -> dict[str, Any]:
    """Delete a spending account by its ID."""
    return await request_ems("DELETE", f"/v1/account/{account_id}")
