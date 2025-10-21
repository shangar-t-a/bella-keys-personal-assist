"""SQLite repository implementation for accounts."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.entities.errors.accounts import AccountNotFoundError, MonthYearNotFoundError
from app.entities.models.accounts import AccountName, MonthYear
from app.entities.repositories.accounts import AccountRepositoryInterface
from app.infrastructures.sqlite_db.database import get_async_session
from app.infrastructures.sqlite_db.models.accounts import AccountModel, MonthYearModel


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

    async def get_or_create_month_year(self, month: str, year: int) -> MonthYear:
        """Retrieve an existing MonthYear or create a new one with the provided month and year."""
        async with await self._get_session() as session:
            # Check if month-year exists
            stmt = select(MonthYearModel).where(MonthYearModel.month == month, MonthYearModel.year == year)
            result = await session.execute(stmt)
            month_year = result.scalar_one_or_none()

            if month_year is None:
                # Create new month-year
                month_year = MonthYearModel(month=month, year=year)
                session.add(month_year)
                await session.commit()

            return MonthYear(id=month_year.id, month=month_year.month, year=month_year.year)

    async def get_month_year_by_value(self, month, year) -> MonthYear | None:
        """Retrieve a MonthYear by its month and year."""
        async with await self._get_session() as session:
            stmt = select(MonthYearModel).where(MonthYearModel.month == month, MonthYearModel.year == year)
            result = await session.execute(stmt)
            month_year = result.scalar_one_or_none()
            return MonthYear(id=month_year.id, month=month_year.month, year=month_year.year) if month_year else None

    async def get_month_year_by_id(self, month_year_id: str) -> MonthYear | None:
        """Retrieve a MonthYear by its ID."""
        async with await self._get_session() as session:
            stmt = select(MonthYearModel).where(MonthYearModel.id == month_year_id)
            result = await session.execute(stmt)
            month_year = result.scalar_one_or_none()
            return MonthYear(id=month_year.id, month=month_year.month, year=month_year.year) if month_year else None

    async def get_all_month_years(self) -> list[MonthYear]:
        """Retrieve all month-year records."""
        async with await self._get_session() as session:
            stmt = select(MonthYearModel)
            result = await session.execute(stmt)
            month_years = result.scalars().all()
            return [MonthYear(id=my.id, month=my.month, year=my.year) for my in month_years]

    async def update_month_year(self, month_year_id: str, month: str, year: int) -> MonthYear:
        """Update an existing MonthYear with the provided month and year."""
        async with await self._get_session() as session:
            # Get month-year
            stmt = select(MonthYearModel).where(MonthYearModel.id == month_year_id)
            result = await session.execute(stmt)
            month_year = result.scalar_one_or_none()

            if month_year is None:
                raise MonthYearNotFoundError(month_year_id=month_year_id)

            # Update month-year
            month_year.month = month
            month_year.year = year
            await session.commit()

            return MonthYear(id=month_year.id, month=month_year.month, year=month_year.year)

    async def delete_month_year(self, month_year_id: str) -> None:
        """Delete a MonthYear by its ID."""
        async with await self._get_session() as session:
            # Get month-year
            stmt = select(MonthYearModel).where(MonthYearModel.id == month_year_id)
            result = await session.execute(stmt)
            month_year = result.scalar_one_or_none()

            if month_year is None:
                raise MonthYearNotFoundError(month_year_id=month_year_id)

            # Delete month-year
            await session.delete(month_year)
            await session.commit()
