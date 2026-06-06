"""Service or use cases for the monthly planner."""

from typing import TYPE_CHECKING

from app.entities.models.monthly_planner import (
    ExpenseStatus,
    MonthlyCategory,
    MonthlyExpenseItem,
    MonthlyExpenseItemDetail,
    MonthlySummaryDetail,
)

if TYPE_CHECKING:
    from app.entities.repositories.monthly_planner import MonthlyPlannerRepositoryInterface
    from app.entities.repositories.period import PeriodRepositoryInterface


class MonthlyPlannerService:
    """Monthly planner service to handle business logic."""

    def __init__(
        self,
        monthly_planner_repository: "MonthlyPlannerRepositoryInterface",
        period_repository: "PeriodRepositoryInterface",
    ):
        """Initialize the MonthlyPlannerService with repositories."""
        self.repo = monthly_planner_repository
        self.period_repo = period_repository

    async def list_categories(self) -> list[MonthlyCategory]:
        """List all custom categories."""
        return await self.repo.list_categories()

    async def add_category(self, name: str, category_l1: str) -> MonthlyCategory:
        """Create and add a new custom category."""
        return await self.repo.add_category(MonthlyCategory(name=name, category_l1=category_l1))

    async def delete_category(self, category_id: str) -> None:
        """Delete a custom category by ID."""
        await self.repo.delete_category(category_id)

    async def get_summary(self, month: int, year: int) -> MonthlySummaryDetail:
        """Retrieve the monthly summary for a specific month and year."""
        period = await self.period_repo.get_or_create_period(month=month, year=year)
        summary = await self.repo.get_summary(period.id)
        if not summary:
            # Return a default summary if not found
            return MonthlySummaryDetail(id="", salary=0.0, month=month, year=year)
        return summary

    async def update_salary(self, month: int, year: int, salary: float) -> MonthlySummaryDetail:
        """Update the salary for a specific month and year."""
        period = await self.period_repo.get_or_create_period(month=month, year=year)
        return await self.repo.update_summary(period.id, salary)

    async def list_expenses(self, month: int, year: int) -> list[MonthlyExpenseItemDetail]:
        """List all expenses for a specific month and year."""
        period = await self.period_repo.get_or_create_period(month=month, year=year)
        return await self.repo.list_expenses(period.id)

    async def add_expense(  # noqa: PLR0913
        self,
        month: int,
        year: int,
        name: str,
        amount: float,
        category_l1: str,
        category_l2: str,
        is_recurring: bool = True,
    ) -> MonthlyExpenseItemDetail:
        """Add a new expense item for the given month and year."""
        period = await self.period_repo.get_or_create_period(month=month, year=year)
        item = MonthlyExpenseItem(
            period_id=period.id,
            name=name,
            amount=amount,
            status=ExpenseStatus.PENDING,
            category_l1=category_l1,
            category_l2=category_l2,
            is_recurring=is_recurring,
        )
        return await self.repo.add_expense(item)

    async def update_expense(  # noqa: PLR0913
        self,
        expense_id: str,
        name: str,
        amount: float,
        status: str,
        category_l1: str,
        category_l2: str,
        is_recurring: bool,
    ) -> MonthlyExpenseItemDetail:
        """Update an existing expense item's details."""
        item = MonthlyExpenseItem(
            period_id="",
            name=name,
            amount=amount,
            status=status,
            category_l1=category_l1,
            category_l2=category_l2,
            is_recurring=is_recurring,
        )
        return await self.repo.update_expense(expense_id, item)

    async def delete_expense(self, expense_id: str) -> None:
        """Delete an expense item by ID."""
        await self.repo.delete_expense(expense_id)

    async def reset_statuses(self, month: int, year: int) -> None:
        """Reset all expense statuses to PENDING for the given month."""
        period = await self.period_repo.get_or_create_period(month=month, year=year)
        await self.repo.reset_statuses(period.id)

    async def sync_from_previous_month(self, month: int, year: int) -> list[MonthlyExpenseItemDetail]:
        """Sync recurring expenses from the previous month to the current one."""
        current_period = await self.period_repo.get_or_create_period(month=month, year=year)
        prev_period_id = await self.repo.get_previous_period_id(current_period.id)

        if not prev_period_id:
            return await self.list_expenses(month, year)

        prev_expenses = await self.repo.list_expenses(prev_period_id)
        current_expenses = await self.repo.list_expenses(current_period.id)
        current_names = {e.name for e in current_expenses}

        new_items = []
        for prev in prev_expenses:
            if prev.is_recurring and prev.name not in current_names:
                item = MonthlyExpenseItem(
                    period_id=current_period.id,
                    name=prev.name,
                    amount=prev.amount,
                    status=ExpenseStatus.PENDING,
                    category_l1=prev.category_l1,
                    category_l2=prev.category_l2,
                    is_recurring=prev.is_recurring,
                )
                new_item = await self.repo.add_expense(item)
                new_items.append(new_item)

        return await self.list_expenses(month, year)
