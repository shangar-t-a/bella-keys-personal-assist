"""Repository interface for the monthly planner."""

from abc import ABC, abstractmethod

from app.entities.models.monthly_planner import (
    MonthlyCategory,
    MonthlyExpenseItem,
    MonthlyExpenseItemDetail,
    MonthlySummaryDetail,
)


class MonthlyPlannerRepositoryInterface(ABC):
    """Interface for monthly planner repository."""

    @abstractmethod
    async def list_categories(self) -> list[MonthlyCategory]:
        """List all custom categories."""
        pass

    @abstractmethod
    async def add_category(self, category: MonthlyCategory) -> MonthlyCategory:
        """Add a new custom category."""
        pass

    @abstractmethod
    async def delete_category(self, category_id: str) -> None:
        """Delete a custom category."""
        pass

    @abstractmethod
    async def get_summary(self, period_id: str) -> MonthlySummaryDetail | None:
        """Get monthly summary for a period."""
        pass

    @abstractmethod
    async def update_summary(self, period_id: str, salary: float) -> MonthlySummaryDetail:
        """Update or create monthly summary."""
        pass

    @abstractmethod
    async def list_expenses(self, period_id: str) -> list[MonthlyExpenseItemDetail]:
        """List all expenses for a period."""
        pass

    @abstractmethod
    async def add_expense(self, expense: MonthlyExpenseItem) -> MonthlyExpenseItemDetail:
        """Add a new expense item."""
        pass

    @abstractmethod
    async def update_expense(self, expense_id: str, expense: MonthlyExpenseItem) -> MonthlyExpenseItemDetail:
        """Update an existing expense item."""
        pass

    @abstractmethod
    async def delete_expense(self, expense_id: str) -> None:
        """Delete an expense item."""
        pass

    @abstractmethod
    async def reset_statuses(self, period_id: str) -> None:
        """Reset all expense statuses to PENDING for a period."""
        pass

    @abstractmethod
    async def get_previous_period_id(self, current_period_id: str) -> str | None:
        """Get the ID of the previous period."""
        pass
