"""Routers for the monthly planner."""

from fastapi import APIRouter, Depends, status

from app.routers.v1.schemas.monthly_planner import (
    MonthlyCategoryBase,
    MonthlyCategoryResponse,
    MonthlyExpenseItemRequest,
    MonthlyExpenseItemResponse,
    MonthlySummaryResponse,
    UpdateSalaryRequest,
)
from app.routers.v1.services import get_monthly_planner_service
from app.use_cases.monthly_planner import MonthlyPlannerService

router = APIRouter(prefix="/monthly-planner", tags=["monthly-planner"])


@router.get("/categories", response_model=list[MonthlyCategoryResponse])
async def list_categories(service: MonthlyPlannerService = Depends(get_monthly_planner_service)):
    """List all custom monthly categories."""
    return await service.list_categories()


@router.post("/categories", response_model=MonthlyCategoryResponse)
async def add_category(
    request: MonthlyCategoryBase, service: MonthlyPlannerService = Depends(get_monthly_planner_service)
):
    """Add a new custom monthly category."""
    return await service.add_category(name=request.name, category_l1=request.category_l1)


@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(category_id: str, service: MonthlyPlannerService = Depends(get_monthly_planner_service)):
    """Delete a custom monthly category."""
    await service.delete_category(category_id)


@router.get("/summary/{year}/{month}", response_model=MonthlySummaryResponse)
async def get_summary(year: int, month: int, service: MonthlyPlannerService = Depends(get_monthly_planner_service)):
    """Get the monthly summary (salary, etc.) for a period."""
    return await service.get_summary(month=month, year=year)


@router.put("/summary/{year}/{month}/salary", response_model=MonthlySummaryResponse)
async def update_salary(
    year: int,
    month: int,
    request: UpdateSalaryRequest,
    service: MonthlyPlannerService = Depends(get_monthly_planner_service),
):
    """Update the salary for a specific monthly period."""
    return await service.update_salary(month=month, year=year, salary=request.salary)


@router.get("/expenses/{year}/{month}", response_model=list[MonthlyExpenseItemResponse])
async def list_expenses(year: int, month: int, service: MonthlyPlannerService = Depends(get_monthly_planner_service)):
    """List all expense items for a specific period."""
    return await service.list_expenses(month=month, year=year)


@router.post("/expenses/{year}/{month}", response_model=MonthlyExpenseItemResponse)
async def add_expense(
    year: int,
    month: int,
    request: MonthlyExpenseItemRequest,
    service: MonthlyPlannerService = Depends(get_monthly_planner_service),
):
    """Add a new expense item for a period."""
    return await service.add_expense(
        month=month,
        year=year,
        name=request.name,
        amount=request.amount,
        category_l1=request.category_l1,
        category_l2=request.category_l2,
        is_recurring=request.is_recurring,
    )


@router.put("/expenses/{expense_id}", response_model=MonthlyExpenseItemResponse)
async def update_expense(
    expense_id: str,
    request: MonthlyExpenseItemRequest,
    service: MonthlyPlannerService = Depends(get_monthly_planner_service),
):
    """Update an existing expense item."""
    return await service.update_expense(
        expense_id=expense_id,
        name=request.name,
        amount=request.amount,
        status=request.status,
        category_l1=request.category_l1,
        category_l2=request.category_l2,
        is_recurring=request.is_recurring,
    )


@router.delete("/expenses/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_expense(expense_id: str, service: MonthlyPlannerService = Depends(get_monthly_planner_service)):
    """Delete an expense item."""
    await service.delete_expense(expense_id)


@router.post("/expenses/{year}/{month}/reset", status_code=status.HTTP_204_NO_CONTENT)
async def reset_statuses(year: int, month: int, service: MonthlyPlannerService = Depends(get_monthly_planner_service)):
    """Reset all expense statuses to PENDING for a period."""
    await service.reset_statuses(month=month, year=year)


@router.post("/expenses/{year}/{month}/sync", response_model=list[MonthlyExpenseItemResponse])
async def sync_from_previous_month(
    year: int, month: int, service: MonthlyPlannerService = Depends(get_monthly_planner_service)
):
    """Sync recurring expenses from the previous month."""
    return await service.sync_from_previous_month(month=month, year=year)
