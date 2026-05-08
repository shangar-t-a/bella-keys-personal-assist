"""Unit tests for the monthly planner use case."""

import pytest

from app.entities.models.monthly_planner import CategoryL1, ExpenseStatus
from app.use_cases.monthly_planner import MonthlyPlannerService


@pytest.fixture(scope="module")
def monthly_planner_service(monthly_planner_repo, period_repo):
    """Provide an instance of MonthlyPlannerService."""
    return MonthlyPlannerService(
        monthly_planner_repository=monthly_planner_repo,
        period_repository=period_repo,
    )


class TestMonthlyPlannerCategories:
    async def test__add_and_list_categories(self, monthly_planner_service):
        """Test adding and listing custom categories."""
        # Add a category
        cat = await monthly_planner_service.add_category(name="Groceries", category_l1=CategoryL1.SPENDING)
        assert cat.name == "Groceries"
        assert cat.category_l1 == CategoryL1.SPENDING
        
        # List categories
        categories = await monthly_planner_service.list_categories()
        assert any(c.id == cat.id for c in categories)
        
        # Clean up
        await monthly_planner_service.delete_category(cat.id)
        categories_after = await monthly_planner_service.list_categories()
        assert not any(c.id == cat.id for c in categories_after)


class TestMonthlyPlannerSummary:
    async def test__get_and_update_summary(self, monthly_planner_service):
        """Test getting and updating the monthly summary."""
        # Get initial summary (should create default if not exists)
        summary = await monthly_planner_service.get_summary(month=1, year=2026)
        assert summary.month == 1
        assert summary.year == 2026
        
        # Update salary
        updated_summary = await monthly_planner_service.update_salary(month=1, year=2026, salary=5000.0)
        assert updated_summary.salary == 5000.0
        assert updated_summary.month == 1
        assert updated_summary.year == 2026
        
        # Verify it persists
        retrieved_summary = await monthly_planner_service.get_summary(month=1, year=2026)
        assert retrieved_summary.salary == 5000.0


class TestMonthlyPlannerExpenses:
    async def test__crud_expenses(self, monthly_planner_service):
        """Test creating, reading, updating, and deleting expenses."""
        month = 2
        year = 2026
        
        # Add expense
        expense = await monthly_planner_service.add_expense(
            month=month,
            year=year,
            name="Internet Bill",
            amount=60.0,
            category_l1=CategoryL1.SPENDING,
            category_l2="Utilities",
            is_recurring=True,
        )
        assert expense.name == "Internet Bill"
        assert expense.amount == 60.0
        assert expense.status == ExpenseStatus.PENDING
        
        # List expenses
        expenses = await monthly_planner_service.list_expenses(month=month, year=year)
        assert len(expenses) >= 1
        assert any(e.id == expense.id for e in expenses)
        
        # Update expense
        updated_expense = await monthly_planner_service.update_expense(
            expense_id=expense.id,
            name="Internet Bill",
            amount=65.0,
            status=ExpenseStatus.SETTLED,
            category_l1=CategoryL1.SPENDING,
            category_l2="Utilities",
            is_recurring=True,
        )
        assert updated_expense.amount == 65.0
        assert updated_expense.status == ExpenseStatus.SETTLED
        
        # Reset statuses
        await monthly_planner_service.reset_statuses(month=month, year=year)
        expenses_after_reset = await monthly_planner_service.list_expenses(month=month, year=year)
        target_expense = next((e for e in expenses_after_reset if e.id == expense.id), None)
        assert target_expense is not None
        assert target_expense.status == ExpenseStatus.PENDING
        
        # Delete expense
        await monthly_planner_service.delete_expense(expense.id)
        expenses_after_delete = await monthly_planner_service.list_expenses(month=month, year=year)
        assert not any(e.id == expense.id for e in expenses_after_delete)

    async def test__sync_from_previous_month(self, monthly_planner_service):
        """Test syncing recurring expenses from the previous month."""
        # Setup previous month (March 2026)
        prev_expense = await monthly_planner_service.add_expense(
            month=3,
            year=2026,
            name="Gym Membership",
            amount=50.0,
            category_l1=CategoryL1.SPENDING,
            category_l2="Health",
            is_recurring=True,
        )
        
        # Add a non-recurring expense
        await monthly_planner_service.add_expense(
            month=3,
            year=2026,
            name="One-time equipment",
            amount=200.0,
            category_l1=CategoryL1.SPENDING,
            category_l2="Health",
            is_recurring=False,
        )
        
        # Sync to current month (April 2026)
        synced_expenses = await monthly_planner_service.sync_from_previous_month(month=4, year=2026)
        
        # Verify sync
        assert any(e.name == "Gym Membership" and e.amount == 50.0 for e in synced_expenses)
        assert not any(e.name == "One-time equipment" for e in synced_expenses)
        
        # Clean up
        for e in synced_expenses:
            await monthly_planner_service.delete_expense(e.id)
        await monthly_planner_service.delete_expense(prev_expense.id)
