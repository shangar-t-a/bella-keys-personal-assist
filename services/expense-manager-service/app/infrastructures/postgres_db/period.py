"""Postgres repository implementation for period."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.entities.errors.period import PeriodNotFoundError
from app.entities.models.period import Period
from app.entities.repositories.period import PeriodRepositoryInterface
from app.infrastructures.postgres_db.database import get_async_session
from app.infrastructures.postgres_db.models.period import PeriodModel


class PostgresPeriodRepository(PeriodRepositoryInterface):
    """Postgres implementation of the PeriodRepositoryInterface."""

    def __init__(self):
        """Initialize the Postgres period repository."""
        self.session_factory = get_async_session()

    async def _get_session(self) -> AsyncSession:
        """Get a new database session."""
        return self.session_factory()

    async def get_or_create_period(self, month: int, year: int) -> Period:
        """Retrieve an existing Period or create a new one with the provided month and year."""
        async with await self._get_session() as session:
            # Check if month-year exists
            stmt = select(PeriodModel).where(PeriodModel.month == month, PeriodModel.year == year)
            result = await session.execute(stmt)
            period = result.scalar_one_or_none()

            if period is None:
                # Create new month-year
                period = PeriodModel(month=month, year=year)
                session.add(period)
                await session.commit()

            return Period(id=period.id, month=period.month, year=period.year)

    async def get_period_by_value(self, month: int, year: int) -> Period | None:
        """Retrieve a Period by its month and year."""
        async with await self._get_session() as session:
            stmt = select(PeriodModel).where(PeriodModel.month == month, PeriodModel.year == year)
            result = await session.execute(stmt)
            period = result.scalar_one_or_none()
            return Period(id=period.id, month=period.month, year=period.year) if period else None

    async def get_period_by_id(self, period_id: str) -> Period | None:
        """Retrieve a Period by its ID."""
        async with await self._get_session() as session:
            stmt = select(PeriodModel).where(PeriodModel.id == period_id)
            result = await session.execute(stmt)
            period = result.scalar_one_or_none()
            return Period(id=period.id, month=period.month, year=period.year) if period else None

    async def get_all_period(self) -> list[Period]:
        """Retrieve all month-year records."""
        async with await self._get_session() as session:
            stmt = select(PeriodModel)
            result = await session.execute(stmt)
            all_period = result.scalars().all()
            return [Period(id=period.id, month=period.month, year=period.year) for period in all_period]

    async def update_period(self, period_id: str, month: int, year: int) -> Period:
        """Update an existing Period with the provided month and year."""
        async with await self._get_session() as session:
            # Get month-year
            stmt = select(PeriodModel).where(PeriodModel.id == period_id)
            result = await session.execute(stmt)
            period = result.scalar_one_or_none()

            if period is None:
                raise PeriodNotFoundError(period_id=period_id)

            # Update month-year
            period.month = month
            period.year = year
            await session.commit()

            return Period(id=period.id, month=period.month, year=period.year)

    async def delete_period(self, period_id: str) -> None:
        """Delete a Period by its ID."""
        async with await self._get_session() as session:
            # Get month-year
            stmt = select(PeriodModel).where(PeriodModel.id == period_id)
            result = await session.execute(stmt)
            period = result.scalar_one_or_none()

            if period is None:
                raise PeriodNotFoundError(period_id=period_id)

            # Delete month-year
            await session.delete(period)
            await session.commit()
