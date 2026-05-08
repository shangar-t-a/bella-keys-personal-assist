"""SQLite repository implementation for the monthly planner."""

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.entities.models.monthly_planner import (
    MonthlyCategory,
    MonthlyExpenseItem,
    MonthlyExpenseItemDetail,
    MonthlySummary,
    MonthlySummaryDetail,
    ExpenseStatus,
)
from app.entities.repositories.monthly_planner import MonthlyPlannerRepositoryInterface
from app.infrastructures.sqlite_db.database import get_async_session
from app.infrastructures.sqlite_db.models.spending_account import PeriodModel  # Period is defined in spending_account for SQLite
from app.infrastructures.sqlite_db.models.monthly_planner import (
    MonthlyCategoryModel,
    MonthlyExpenseItemModel,
    MonthlySummaryModel,
)


class SQLiteMonthlyPlannerRepository(MonthlyPlannerRepositoryInterface):
    """SQLite implementation of the MonthlyPlannerRepositoryInterface."""

    def __init__(self):
        """Initialize the SQLite monthly planner repository."""
        self.session_factory = get_async_session()

    async def _get_session(self) -> AsyncSession:
        """Get a new database session."""
        return self.session_factory()

    # --- Categories ---
    async def list_categories(self) -> list[MonthlyCategory]:
        async with await self._get_session() as session:
            stmt = select(MonthlyCategoryModel).order_by(MonthlyCategoryModel.name)
            result = await session.execute(stmt)
            rows = result.scalars().all()
            return [
                MonthlyCategory(
                    id=r.id,
                    name=r.name,
                    category_l1=r.category_l1,
                )
                for r in rows
            ]

    async def add_category(self, category: MonthlyCategory) -> MonthlyCategory:
        async with await self._get_session() as session:
            new_cat = MonthlyCategoryModel(
                name=category.name,
                category_l1=category.category_l1,
            )
            session.add(new_cat)
            await session.commit()
            await session.refresh(new_cat)
            return MonthlyCategory(
                id=new_cat.id,
                name=new_cat.name,
                category_l1=new_cat.category_l1,
            )

    async def delete_category(self, category_id: str) -> None:
        async with await self._get_session() as session:
            stmt = delete(MonthlyCategoryModel).where(MonthlyCategoryModel.id == category_id)
            await session.execute(stmt)
            await session.commit()

    # --- Summary ---
    async def get_summary(self, period_id: str) -> MonthlySummaryDetail | None:
        async with await self._get_session() as session:
            stmt = (
                select(MonthlySummaryModel, PeriodModel.month, PeriodModel.year)
                .join(PeriodModel, MonthlySummaryModel.period_id == PeriodModel.id)
                .where(MonthlySummaryModel.period_id == period_id)
            )
            result = await session.execute(stmt)
            row = result.one_or_none()
            if not row:
                return None
            
            model, month, year = row
            return MonthlySummaryDetail(
                id=model.id,
                period_id=model.period_id,
                salary=model.salary,
                month=month,
                year=year,
            )

    async def update_summary(self, period_id: str, salary: float) -> MonthlySummaryDetail:
        async with await self._get_session() as session:
            stmt = select(MonthlySummaryModel).where(MonthlySummaryModel.period_id == period_id)
            result = await session.execute(stmt)
            model = result.scalar_one_or_none()

            if model:
                model.salary = salary
            else:
                model = MonthlySummaryModel(period_id=period_id, salary=salary)
                session.add(model)
            
            await session.commit()
            await session.refresh(model)

            # Get period details for the response
            period_stmt = select(PeriodModel).where(PeriodModel.id == period_id)
            period_result = await session.execute(period_stmt)
            period = period_result.scalar_one()

            return MonthlySummaryDetail(
                id=model.id,
                period_id=model.period_id,
                salary=model.salary,
                month=period.month,
                year=period.year,
            )

    # --- Expenses ---
    async def list_expenses(self, period_id: str) -> list[MonthlyExpenseItemDetail]:
        async with await self._get_session() as session:
            stmt = (
                select(MonthlyExpenseItemModel, PeriodModel.month, PeriodModel.year)
                .join(PeriodModel, MonthlyExpenseItemModel.period_id == PeriodModel.id)
                .where(MonthlyExpenseItemModel.period_id == period_id)
                .order_by(MonthlyExpenseItemModel.name)
            )
            result = await session.execute(stmt)
            rows = result.all()
            return [
                MonthlyExpenseItemDetail(
                    id=r.MonthlyExpenseItemModel.id,
                    period_id=r.MonthlyExpenseItemModel.period_id,
                    name=r.MonthlyExpenseItemModel.name,
                    amount=r.MonthlyExpenseItemModel.amount,
                    status=r.MonthlyExpenseItemModel.status,
                    category_l1=r.MonthlyExpenseItemModel.category_l1,
                    category_l2=r.MonthlyExpenseItemModel.category_l2,
                    is_recurring=r.MonthlyExpenseItemModel.is_recurring,
                    month=r.month,
                    year=r.year,
                )
                for r in rows
            ]

    async def add_expense(self, expense: MonthlyExpenseItem) -> MonthlyExpenseItemDetail:
        async with await self._get_session() as session:
            new_item = MonthlyExpenseItemModel(
                period_id=expense.period_id,
                name=expense.name,
                amount=expense.amount,
                status=expense.status,
                category_l1=expense.category_l1,
                category_l2=expense.category_l2,
                is_recurring=expense.is_recurring,
            )
            session.add(new_item)
            await session.commit()
            await session.refresh(new_item)

            period_stmt = select(PeriodModel).where(PeriodModel.id == expense.period_id)
            period = (await session.execute(period_stmt)).scalar_one()

            return MonthlyExpenseItemDetail(
                id=new_item.id,
                period_id=new_item.period_id,
                name=new_item.name,
                amount=new_item.amount,
                status=new_item.status,
                category_l1=new_item.category_l1,
                category_l2=new_item.category_l2,
                is_recurring=new_item.is_recurring,
                month=period.month,
                year=period.year,
            )

    async def update_expense(self, expense_id: str, expense: MonthlyExpenseItem) -> MonthlyExpenseItemDetail:
        async with await self._get_session() as session:
            stmt = select(MonthlyExpenseItemModel).where(MonthlyExpenseItemModel.id == expense_id)
            model = (await session.execute(stmt)).scalar_one()

            model.name = expense.name
            model.amount = expense.amount
            model.status = expense.status
            model.category_l1 = expense.category_l1
            model.category_l2 = expense.category_l2
            model.is_recurring = expense.is_recurring

            await session.commit()
            await session.refresh(model)

            period_stmt = select(PeriodModel).where(PeriodModel.id == model.period_id)
            period = (await session.execute(period_stmt)).scalar_one()

            return MonthlyExpenseItemDetail(
                id=model.id,
                period_id=model.period_id,
                name=model.name,
                amount=model.amount,
                status=model.status,
                category_l1=model.category_l1,
                category_l2=model.category_l2,
                is_recurring=model.is_recurring,
                month=period.month,
                year=period.year,
            )

    async def delete_expense(self, expense_id: str) -> None:
        async with await self._get_session() as session:
            stmt = delete(MonthlyExpenseItemModel).where(MonthlyExpenseItemModel.id == expense_id)
            await session.execute(stmt)
            await session.commit()

    async def reset_statuses(self, period_id: str) -> None:
        async with await self._get_session() as session:
            stmt = (
                update(MonthlyExpenseItemModel)
                .where(MonthlyExpenseItemModel.period_id == period_id)
                .values(status=ExpenseStatus.PENDING)
            )
            await session.execute(stmt)
            await session.commit()

    async def get_previous_period_id(self, current_period_id: str) -> str | None:
        async with await self._get_session() as session:
            # Get current period details
            stmt = select(PeriodModel).where(PeriodModel.id == current_period_id)
            current = (await session.execute(stmt)).scalar_one()

            # Calculate previous month/year
            prev_month = current.month - 1
            prev_year = current.year
            if prev_month == 0:
                prev_month = 12
                prev_year -= 1
            
            # Find period ID
            prev_stmt = select(PeriodModel.id).where(
                PeriodModel.month == prev_month,
                PeriodModel.year == prev_year
            )
            result = await session.execute(prev_stmt)
            return result.scalar_one_or_none()
