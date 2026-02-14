"""SQLite repository implementation for accounts."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.entities.errors.accounts import AccountNotFoundError, PeriodNotFoundError
from app.entities.models.accounts import AccountName, Period
from app.entities.repositories.accounts import AccountRepositoryInterface
from app.infrastructures.sqlite_db.database import get_async_session
from app.infrastructures.sqlite_db.models.accounts import AccountModel, PeriodModel


class SQLiteAccountRepository(AccountRepositoryInterface):
    """SQLite implementation of the AccountRepositoryInterface."""

    def __init__(self):
        """Initialize the SQLite account repository."""
        self.session_factory = get_async_session()

    async def _get_session(self) -> AsyncSession:
        """Get a new database session."""
        return self.session_factory()

    async def get_or_create_account(self, account_name: str) -> AccountName:
        """Retrieve an existing account or create a new one with the provided name."""
        async with await self._get_session() as session:
            # Check if account exists
            stmt = select(AccountModel).where(AccountModel.account_name == account_name.upper())
            result = await session.execute(stmt)
            account = result.scalar_one_or_none()

            if account is None:
                # Create new account
                account = AccountModel(account_name=account_name.upper())
                session.add(account)
                await session.commit()

            return AccountName(id=account.id, account_name=account.account_name)

    async def get_account_by_name(self, account_name: str) -> AccountName | None:
        """Retrieve an account by its name."""
        async with await self._get_session() as session:
            stmt = select(AccountModel).where(AccountModel.account_name == account_name.upper())
            result = await session.execute(stmt)
            account = result.scalar_one_or_none()
            return AccountName(id=account.id, account_name=account.account_name) if account else None

    async def get_account_by_id(self, account_id: str) -> AccountName | None:
        """Retrieve an account by its ID."""
        async with await self._get_session() as session:
            stmt = select(AccountModel).where(AccountModel.id == account_id)
            result = await session.execute(stmt)
            account = result.scalar_one_or_none()
            return AccountName(id=account.id, account_name=account.account_name) if account else None

    async def get_all_accounts(self) -> list[AccountName]:
        """Retrieve all accounts."""
        async with await self._get_session() as session:
            stmt = select(AccountModel)
            result = await session.execute(stmt)
            accounts = result.scalars().all()
            return [AccountName(id=acc.id, account_name=acc.account_name) for acc in accounts]

    async def update_account_name(self, account_id: str, account_name: str) -> AccountName:
        """Update an existing account name with the provided data."""
        async with await self._get_session() as session:
            # Get account
            stmt = select(AccountModel).where(AccountModel.id == account_id)
            result = await session.execute(stmt)
            account = result.scalar_one_or_none()

            if account is None:
                raise AccountNotFoundError(account_id=account_id)

            # Update account
            account.account_name = account_name.upper()
            await session.commit()

            return AccountName(id=account.id, account_name=account.account_name)

    async def delete_account(self, account_id: str) -> None:
        """Delete an account by its ID."""
        async with await self._get_session() as session:
            # Get account
            stmt = select(AccountModel).where(AccountModel.id == account_id)
            result = await session.execute(stmt)
            account = result.scalar_one_or_none()

            if account is None:
                raise AccountNotFoundError(account_id=account_id)

            # Delete account
            await session.delete(account)
            await session.commit()

    async def get_or_create_period(self, month: str, year: int) -> Period:
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

    async def get_period_by_value(self, month, year) -> Period | None:
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

    async def update_period(self, period_id: str, month: str, year: int) -> Period:
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
