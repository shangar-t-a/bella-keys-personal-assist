"""MCP tools for liability management operations."""

from typing import Annotated, Any

from app.client import request_ems


async def list_liability_categories() -> list[dict[str, Any]]:
    """Retrieve list of all pre-seeded liability categories and subcategories."""
    return await request_ems("GET", "/v1/liabilities/categories")


async def list_liabilities(
    category_id: Annotated[str | None, "Optional filter by category ID"] = None,
    search: Annotated[str | None, "Optional search term for liability name"] = None,
) -> list[dict[str, Any]]:
    """Retrieve list of liabilities, optionally filtered by category or search term."""
    params: dict[str, Any] = {}
    if category_id is not None:
        params["categoryId"] = category_id
    if search is not None:
        params["search"] = search

    return await request_ems("GET", "/v1/liabilities", params=params)


async def get_liability_by_id(
    liability_id: Annotated[str, "The unique ID of the liability"],
) -> dict[str, Any]:
    """Retrieve details of a single liability by its ID."""
    return await request_ems("GET", f"/v1/liabilities/{liability_id}")


async def create_liability(
    category_id: Annotated[str, "ID of the parent category"],
    name: Annotated[str, "Name of the liability"],
    subcategory_id: Annotated[str | None, "ID of the subcategory"] = None,
    initial_amount: Annotated[
        float, "Amount for the initial BORROW transaction (INR)"
    ] = 0.0,
    initial_date: Annotated[
        str | None, "Timestamp of initial borrowing (ISO format string)"
    ] = None,
    interest_rate: Annotated[
        float | None, "Annual interest rate (%) if interest-bearing"
    ] = None,
    interest_compounding: Annotated[
        str | None, "Compounding frequency (MONTHLY, QUARTERLY, HALF_YEARLY, YEARLY)"
    ] = None,
    emi_amount: Annotated[float | None, "Scheduled monthly EMI amount (INR)"] = None,
    emi_start_date: Annotated[
        str | None, "Date when EMI repayments officially begin (ISO format string)"
    ] = None,
    maturity_date: Annotated[str | None, "Maturity date (ISO format string)"] = None,
    notes: Annotated[str | None, "Additional notes/remarks"] = None,
) -> dict[str, Any]:
    """Create a new liability and log its initial balance transaction."""
    json_data: dict[str, Any] = {
        "categoryId": category_id,
        "name": name,
        "subcategoryId": subcategory_id,
        "initialAmount": initial_amount,
        "initialDate": initial_date,
        "notes": notes,
    }

    if (
        interest_rate is not None
        or interest_compounding is not None
        or emi_amount is not None
        or emi_start_date is not None
        or maturity_date is not None
    ):
        json_data["interestDetails"] = {
            "interestRate": interest_rate or 0.0,
            "compounding": interest_compounding or "YEARLY",
            "emiAmount": emi_amount,
            "emiStartDate": emi_start_date,
            "maturityDate": maturity_date,
        }

    return await request_ems("POST", "/v1/liabilities", json=json_data)


async def update_liability(
    liability_id: Annotated[str, "The unique ID of the liability to update"],
    category_id: Annotated[str | None, "ID of the parent category"] = None,
    name: Annotated[str | None, "Name of the liability"] = None,
    subcategory_id: Annotated[str | None, "ID of the subcategory"] = None,
    interest_rate: Annotated[
        float | None, "Annual interest rate (%) if interest-bearing"
    ] = None,
    interest_compounding: Annotated[
        str | None, "Compounding frequency (MONTHLY, QUARTERLY, HALF_YEARLY, YEARLY)"
    ] = None,
    emi_amount: Annotated[float | None, "Scheduled monthly EMI amount (INR)"] = None,
    emi_start_date: Annotated[
        str | None, "Date when EMI repayments begin (ISO format string)"
    ] = None,
    maturity_date: Annotated[str | None, "Maturity date (ISO format string)"] = None,
    notes: Annotated[str | None, "Additional notes/remarks"] = None,
) -> dict[str, Any]:
    """Update metadata fields of an existing liability."""
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
        or emi_amount is not None
        or emi_start_date is not None
        or maturity_date is not None
    ):
        json_data["interestDetails"] = {
            "interestRate": interest_rate or 0.0,
            "compounding": interest_compounding or "YEARLY",
            "emiAmount": emi_amount,
            "emiStartDate": emi_start_date,
            "maturityDate": maturity_date,
        }

    return await request_ems("PUT", f"/v1/liabilities/{liability_id}", json=json_data)


async def delete_liability(
    liability_id: Annotated[str, "The unique ID of the liability to delete"],
) -> dict[str, Any]:
    """Delete a liability and all its historical transactions."""
    return await request_ems("DELETE", f"/v1/liabilities/{liability_id}")


async def get_liability_summary() -> dict[str, Any]:
    """Get aggregate liabilities calculations and category breakdowns."""
    return await request_ems("GET", "/v1/liabilities/summary")


async def get_transactions_for_liability(
    liability_id: Annotated[str, "The unique ID of the liability"],
) -> list[dict[str, Any]]:
    """Retrieve the transaction history ledger for a specific liability."""
    return await request_ems("GET", f"/v1/liabilities/{liability_id}/transactions")


async def add_liability_transaction(
    liability_id: Annotated[str, "The unique ID of the liability"],
    transaction_type: Annotated[str, "Transaction type: BORROW, REPAY, or REVALUE"],
    amount: Annotated[float, "Total INR amount of the transaction"],
    transaction_date: Annotated[
        str | None, "Transaction timestamp (ISO format string)"
    ] = None,
    description: Annotated[str | None, "Audit remark"] = None,
) -> dict[str, Any]:
    """Add a new borrow, repay, or revaluation transaction to the liability's ledger."""
    json_data = {
        "transactionType": transaction_type,
        "amount": amount,
        "transactionDate": transaction_date,
        "description": description,
    }
    return await request_ems(
        "POST", f"/v1/liabilities/{liability_id}/transactions", json=json_data
    )


async def delete_liability_transaction(
    transaction_id: Annotated[str, "The unique ID of the transaction to delete"],
) -> dict[str, Any]:
    """Delete a transaction from the ledger and trigger parent outstanding recalculation."""
    return await request_ems("DELETE", f"/v1/liabilities/transactions/{transaction_id}")


async def get_liability_projections(
    liability_id: Annotated[str, "The unique ID of the liability"],
) -> dict[str, Any]:
    """Retrieve ideal and actual amortization projection curves and payoff metrics."""
    return await request_ems("GET", f"/v1/liabilities/{liability_id}/projections")
