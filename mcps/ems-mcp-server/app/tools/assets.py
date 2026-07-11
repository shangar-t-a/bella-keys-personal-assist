"""MCP tools for asset management operations."""

from typing import Annotated, Any

from app.client import request_ems


async def list_asset_categories() -> list[dict[str, Any]]:
    """Retrieve list of all pre-seeded asset categories and subcategories."""
    return await request_ems("GET", "/v1/assets/categories")


async def list_assets(
    category_id: Annotated[str | None, "Optional filter by category ID"] = None,
    search: Annotated[str | None, "Optional search term for asset name"] = None,
) -> list[dict[str, Any]]:
    """Retrieve list of assets, optionally filtered by category or search term."""
    params: dict[str, Any] = {}
    if category_id is not None:
        params["categoryId"] = category_id
    if search is not None:
        params["search"] = search

    return await request_ems("GET", "/v1/assets", params=params)


async def get_asset_by_id(
    asset_id: Annotated[str, "The unique ID of the asset"],
) -> dict[str, Any]:
    """Retrieve details of a single asset by its ID."""
    return await request_ems("GET", f"/v1/assets/{asset_id}")


async def create_asset(
    category_id: Annotated[str, "ID of the parent category"],
    name: Annotated[str, "Name of the asset"],
    subcategory_id: Annotated[str | None, "ID of the subcategory"] = None,
    initial_amount: Annotated[
        float, "Amount for the initial BUY transaction (INR)"
    ] = 0.0,
    interest_rate: Annotated[
        float | None, "Annual interest rate (%) if interest-bearing"
    ] = None,
    interest_compounding: Annotated[
        str | None, "Compounding frequency (MONTHLY, QUARTERLY, HALF_YEARLY, YEARLY)"
    ] = None,
    maturity_date: Annotated[
        str | None, "Maturity date (ISO format string: YYYY-MM-DDTHH:MM:SS)"
    ] = None,
    units: Annotated[float | None, "Quantity/Weight of units purchased"] = None,
    price_per_unit: Annotated[
        float | None, "Price per unit/NAV at time of transaction"
    ] = None,
    notes: Annotated[str | None, "Additional notes/remarks"] = None,
) -> dict[str, Any]:
    """Create a new asset and log its initial balance transaction."""
    json_data: dict[str, Any] = {
        "categoryId": category_id,
        "name": name,
        "subcategoryId": subcategory_id,
        "initialAmount": initial_amount,
        "notes": notes,
    }

    if (
        interest_rate is not None
        or interest_compounding is not None
        or maturity_date is not None
    ):
        json_data["interestDetails"] = {
            "interestRate": interest_rate or 0.0,
            "compounding": interest_compounding or "YEARLY",
            "maturityDate": maturity_date,
        }

    if units is not None or price_per_unit is not None:
        json_data["unitDetails"] = {
            "units": units,
            "pricePerUnit": price_per_unit or 0.0,
        }

    return await request_ems("POST", "/v1/assets", json=json_data)


async def update_asset(
    asset_id: Annotated[str, "The unique ID of the asset to update"],
    category_id: Annotated[str | None, "ID of the parent category"] = None,
    name: Annotated[str | None, "Name of the asset"] = None,
    subcategory_id: Annotated[str | None, "ID of the subcategory"] = None,
    interest_rate: Annotated[
        float | None, "Annual interest rate (%) if interest-bearing"
    ] = None,
    interest_compounding: Annotated[
        str | None, "Compounding frequency (MONTHLY, QUARTERLY, HALF_YEARLY, YEARLY)"
    ] = None,
    maturity_date: Annotated[str | None, "Maturity date (ISO format string)"] = None,
    notes: Annotated[str | None, "Additional notes/remarks"] = None,
) -> dict[str, Any]:
    """Update metadata fields of an existing asset."""
    json_data: dict[str, Any] = {}
    if category_id is not None:
        json_data["categoryId"] = category_id
    if name is not None:
        json_data["name"] = name
    if subcategory_id is not None:
        json_data["subcategoryId"] = subcategory_id
    if notes is not None:
        json_data["notes"] = notes

    if (
        interest_rate is not None
        or interest_compounding is not None
        or maturity_date is not None
    ):
        json_data["interestDetails"] = {
            "interestRate": interest_rate or 0.0,
            "compounding": interest_compounding or "YEARLY",
            "maturityDate": maturity_date,
        }

    return await request_ems("PUT", f"/v1/assets/{asset_id}", json=json_data)


async def delete_asset(
    asset_id: Annotated[str, "The unique ID of the asset to delete"],
) -> dict[str, Any]:
    """Delete an asset and all its historical transactions."""
    return await request_ems("DELETE", f"/v1/assets/{asset_id}")


async def get_asset_summary() -> dict[str, Any]:
    """Get aggregate wealth calculations and category breakdowns for assets."""
    return await request_ems("GET", "/v1/assets/summary")


async def get_transactions_for_asset(
    asset_id: Annotated[str, "The unique ID of the asset"],
) -> list[dict[str, Any]]:
    """Retrieve the transaction history ledger for a specific asset."""
    return await request_ems("GET", f"/v1/assets/{asset_id}/transactions")


async def add_asset_transaction(
    asset_id: Annotated[str, "The unique ID of the asset"],
    transaction_type: Annotated[str, "Transaction type: BUY, SELL, or REVALUE"],
    amount: Annotated[float, "Total INR amount of the transaction"],
    units: Annotated[
        float | None,
        "Quantity/Weight of units purchased (required for BUY/SELL on unit assets)",
    ] = None,
    price_per_unit: Annotated[
        float | None, "Price per unit/NAV at time of transaction"
    ] = None,
    transaction_date: Annotated[
        str | None, "Transaction timestamp (ISO format string)"
    ] = None,
    description: Annotated[str | None, "Audit remark"] = None,
) -> dict[str, Any]:
    """Add a new buy, sell, or revaluation transaction to the asset's ledger."""
    json_data: dict[str, Any] = {
        "transactionType": transaction_type,
        "amount": amount,
        "transactionDate": transaction_date,
        "description": description,
    }

    if units is not None or price_per_unit is not None:
        json_data["unitDetails"] = {
            "units": units,
            "pricePerUnit": price_per_unit or 0.0,
        }

    return await request_ems(
        "POST", f"/v1/assets/{asset_id}/transactions", json=json_data
    )


async def delete_asset_transaction(
    transaction_id: Annotated[str, "The unique ID of the transaction to delete"],
) -> dict[str, Any]:
    """Delete a transaction from the ledger and trigger parent valuation recalculation."""
    return await request_ems("DELETE", f"/v1/assets/transactions/{transaction_id}")
