"""MCP tools for monthly budget planning operations."""

from typing import Annotated, Any

from app.client import request_ems


async def list_monthly_categories() -> list[dict[str, Any]]:
    """List all custom monthly categories."""
    return await request_ems("GET", "/v1/monthly-planner/categories")


async def add_monthly_category(
    name: Annotated[str, "Name of the category"],
    category_l1: Annotated[str, "Level 1 category: 'spending' or 'saving'"],
) -> dict[str, Any]:
    """Add a new custom monthly category."""
    json_data = {
        "name": name,
        "category_l1": category_l1,
    }
    return await request_ems("POST", "/v1/monthly-planner/categories", json=json_data)


async def delete_monthly_category(
    category_id: Annotated[
        str, "The unique ID of the custom monthly category to delete"
    ],
) -> dict[str, Any]:
    """Delete a custom monthly category."""
    return await request_ems("DELETE", f"/v1/monthly-planner/categories/{category_id}")


async def get_monthly_summary(
    year: Annotated[int, "Calendar year (e.g. 2025)"],
    month: Annotated[int, "Calendar month (1-12)"],
) -> dict[str, Any]:
    """Get the monthly budget summary (salary, etc.) for a period."""
    return await request_ems("GET", f"/v1/monthly-planner/summary/{year}/{month}")


async def update_monthly_salary(
    year: Annotated[int, "Calendar year (e.g. 2025)"],
    month: Annotated[int, "Calendar month (1-12)"],
    salary: Annotated[float, "Monthly salary/income amount"],
) -> dict[str, Any]:
    """Update the salary for a specific monthly period."""
    json_data = {"salary": salary}
    return await request_ems(
        "PUT", f"/v1/monthly-planner/summary/{year}/{month}/salary", json=json_data
    )


async def list_monthly_expenses(
    year: Annotated[int, "Calendar year (e.g. 2025)"],
    month: Annotated[int, "Calendar month (1-12)"],
) -> list[dict[str, Any]]:
    """List all expense items for a specific period."""
    return await request_ems("GET", f"/v1/monthly-planner/expenses/{year}/{month}")


async def add_monthly_expense(
    year: Annotated[int, "Calendar year (e.g. 2025)"],
    month: Annotated[int, "Calendar month (1-12)"],
    name: Annotated[str, "Name of the expense"],
    amount: Annotated[float, "Amount of the expense"],
    category_l1: Annotated[str, "Level 1 category: 'spending' or 'saving'"],
    category_l2: Annotated[str, "Level 2 category name (custom monthly category)"],
    is_recurring: Annotated[bool, "Whether this expense repeats monthly"] = True,
) -> dict[str, Any]:
    """Add a new expense item for a period."""
    json_data = {
        "name": name,
        "amount": amount,
        "category_l1": category_l1,
        "category_l2": category_l2,
        "is_recurring": is_recurring,
    }
    return await request_ems(
        "POST", f"/v1/monthly-planner/expenses/{year}/{month}", json=json_data
    )


async def update_monthly_expense(
    expense_id: Annotated[str, "The unique ID of the expense item to update"],
    name: Annotated[str, "Name of the expense"],
    amount: Annotated[float, "Amount of the expense"],
    category_l1: Annotated[str, "Level 1 category: 'spending' or 'saving'"],
    category_l2: Annotated[str, "Level 2 category name"],
    is_recurring: Annotated[bool, "Whether this expense repeats monthly"],
    status: Annotated[str, "Status of the expense: 'pending' or 'settled'"] = "pending",
) -> dict[str, Any]:
    """Update an existing expense item."""
    json_data = {
        "name": name,
        "amount": amount,
        "status": status,
        "category_l1": category_l1,
        "category_l2": category_l2,
        "is_recurring": is_recurring,
    }
    return await request_ems(
        "PUT", f"/v1/monthly-planner/expenses/{expense_id}", json=json_data
    )


async def delete_monthly_expense(
    expense_id: Annotated[str, "The unique ID of the expense item to delete"],
) -> dict[str, Any]:
    """Delete an expense item."""
    return await request_ems("DELETE", f"/v1/monthly-planner/expenses/{expense_id}")


async def reset_monthly_expense_statuses(
    year: Annotated[int, "Calendar year (e.g. 2025)"],
    month: Annotated[int, "Calendar month (1-12)"],
) -> dict[str, Any]:
    """Reset all expense statuses to PENDING for a period."""
    return await request_ems(
        "POST", f"/v1/monthly-planner/expenses/{year}/{month}/reset"
    )


async def sync_monthly_expenses_from_previous_month(
    year: Annotated[int, "Calendar year (e.g. 2025)"],
    month: Annotated[int, "Calendar month (1-12)"],
) -> list[dict[str, Any]]:
    """Sync recurring expenses from the previous month."""
    return await request_ems(
        "POST", f"/v1/monthly-planner/expenses/{year}/{month}/sync"
    )
