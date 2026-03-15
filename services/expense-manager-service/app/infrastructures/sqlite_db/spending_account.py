"""SQLite repository implementation for spending accounts."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.entities.errors.spending_entry import SpendingAccountEntryNotFoundError
from app.entities.models.spending_entry import (
    SpendingEntry,
    SpendingEntryWithCalc,
)
from app.entities.repositories.spending_entry import SpendingEntryRepositoryInterface
from app.infrastructures.sqlite_db.database import get_async_session
from app.infrastructures.sqlite_db.models.spending_account import SpendingEntryModel


class SQLiteSpendingAccountRepository(SpendingEntryRepositoryInterface):
    """SQLite implementation of the SpendingEntryRepositoryInterface."""

    def __init__(self):
        """Initialize the SQLite spending account repository."""
        self.session_factory = get_async_session()

    async def _get_session(self) -> AsyncSession:
        """Get a new database session."""
        return self.session_factory()

    async def add_entry(self, entry: SpendingEntry) -> SpendingEntryWithCalc:
        """Add a new entry to the spending account."""
        async with await self._get_session() as session:
            # Create new entry
            new_entry = SpendingEntryModel(
                account_id=entry.account_id,
                period_id=entry.period_id,
                starting_balance=entry.starting_balance,
                current_balance=entry.current_balance,
                current_credit=entry.current_credit,
            )
            session.add(new_entry)
            await session.commit()

            # Retrieve account and date details
            await session.refresh(new_entry)

            # Convert to domain model with calculated fields
            return SpendingEntryWithCalc(
                id=new_entry.id,
                account_id=new_entry.account_id,
                period_id=new_entry.period_id,
                starting_balance=new_entry.starting_balance,
                current_balance=new_entry.current_balance,
                current_credit=new_entry.current_credit,
            )

    async def get_entry_by_id(self, entry_id: str) -> SpendingEntryWithCalc:
        """Retrieve a spending account entry by its ID."""
        async with await self._get_session() as session:
            stmt = select(SpendingEntryModel).where(SpendingEntryModel.id == entry_id)
            result = await session.execute(stmt)
            entry = result.scalar_one_or_none()

            if entry is None:
                raise SpendingAccountEntryNotFoundError(entry_id=entry_id)

            return SpendingEntryWithCalc(
                id=entry.id,
                account_id=entry.account_id,
                period_id=entry.period_id,
                starting_balance=entry.starting_balance,
                current_balance=entry.current_balance,
                current_credit=entry.current_credit,
            )

    async def get_all_entries(self) -> list[SpendingEntryWithCalc]:
        """Retrieve all entries for all spending accounts."""
        async with await self._get_session() as session:
            stmt = select(SpendingEntryModel)
            result = await session.execute(stmt)
            entries = result.scalars().all()

            return [
                SpendingEntryWithCalc(
                    id=entry.id,
                    account_id=entry.account_id,
                    period_id=entry.period_id,
                    starting_balance=entry.starting_balance,
                    current_balance=entry.current_balance,
                    current_credit=entry.current_credit,
                )
                for entry in entries
            ]

    async def get_all_entries_for_account(self, account_id: str) -> list[SpendingEntryWithCalc]:
        """Retrieve all entries for a given spending account."""
        async with await self._get_session() as session:
            stmt = select(SpendingEntryModel).where(SpendingEntryModel.account_id == account_id)
            result = await session.execute(stmt)
            entries = result.scalars().all()

            return [
                SpendingEntryWithCalc(
                    id=entry.id,
                    account_id=entry.account_id,
                    period_id=entry.period_id,
                    starting_balance=entry.starting_balance,
                    current_balance=entry.current_balance,
                    current_credit=entry.current_credit,
                )
                for entry in entries
            ]

    async def get_entry_by_account_and_period_or_none(
        self,
        account_id: str,
        period_id: str,
    ) -> SpendingEntryWithCalc | None:
        """Retrieve a specific entry for a given account and month-year."""
        async with await self._get_session() as session:
            stmt = select(SpendingEntryModel).where(
                SpendingEntryModel.account_id == account_id,
                SpendingEntryModel.period_id == period_id,
            )
            result = await session.execute(stmt)
            entry = result.scalar_one_or_none()

            if entry is not None:
                return SpendingEntryWithCalc(
                    id=entry.id,
                    account_id=entry.account_id,
                    period_id=entry.period_id,
                    starting_balance=entry.starting_balance,
                    current_balance=entry.current_balance,
                    current_credit=entry.current_credit,
                )

            return None

    async def edit_entry(self, entry_id: str, entry: SpendingEntry) -> SpendingEntryWithCalc:
        """Edit an existing spending account entry."""
        async with await self._get_session() as session:
            # Get entry
            stmt = select(SpendingEntryModel).where(SpendingEntryModel.id == entry_id)
            result = await session.execute(stmt)
            existing_entry = result.scalar_one_or_none()

            if existing_entry is None:
                raise SpendingAccountEntryNotFoundError(entry_id=entry_id)

            # Update entry
            existing_entry.account_id = entry.account_id
            existing_entry.period_id = entry.period_id
            existing_entry.starting_balance = entry.starting_balance
            existing_entry.current_balance = entry.current_balance
            existing_entry.current_credit = entry.current_credit

            await session.commit()

            # Convert to domain model with calculated fields
            return SpendingEntryWithCalc(
                id=existing_entry.id,
                account_id=existing_entry.account_id,
                period_id=existing_entry.period_id,
                starting_balance=existing_entry.starting_balance,
                current_balance=existing_entry.current_balance,
                current_credit=existing_entry.current_credit,
            )

    async def delete_entry(self, entry_id: str) -> None:
        """Delete a spending account entry by its ID."""
        async with await self._get_session() as session:
            # Get entry
            stmt = select(SpendingEntryModel).where(SpendingEntryModel.id == entry_id)
            result = await session.execute(stmt)
            existing_entry = result.scalar_one_or_none()

            if existing_entry is None:
                raise SpendingAccountEntryNotFoundError(entry_id=entry_id)

            # Delete entry
            await session.delete(existing_entry)
            await session.commit()

    # Optimized methods with JOINs - not implemented for SQLite
    async def add_entry_with_details(self, entry):
        raise NotImplementedError("SQLite repository does not support optimized JOIN methods")

    async def get_entry_by_id_with_details(self, entry_id: str):
        raise NotImplementedError("SQLite repository does not support optimized JOIN methods")

    async def get_all_entries_with_details(self, limit: int = 12, offset: int = 0):
        raise NotImplementedError("SQLite repository does not support optimized JOIN methods")

    async def get_all_entries_for_account_with_details(self, account_id: str, limit: int = 12, offset: int = 0):
        raise NotImplementedError("SQLite repository does not support optimized JOIN methods")

    async def edit_entry_with_details(self, entry_id: str, entry):
        raise NotImplementedError("SQLite repository does not support optimized JOIN methods")
