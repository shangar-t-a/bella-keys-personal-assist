"""Postgres repository implementation for accounts."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.entities.errors.accounts import AccountNotFoundError
from app.entities.models.accounts import Account
from app.entities.repositories.accounts import AccountRepositoryInterface
from app.infrastructures.postgres_db.database import get_async_session
from app.infrastructures.postgres_db.models.accounts import AccountModel


class PostgresAccountRepository(AccountRepositoryInterface):
    """Postgres implementation of the AccountRepositoryInterface."""

    def __init__(self):
        """Initialize the Postgres account repository."""
        self.session_factory = get_async_session()

    async def _get_session(self) -> AsyncSession:
        """Get a new database session."""
        return self.session_factory()

    async def get_or_create_account(self, account_name: str) -> Account:
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

            return Account(id=account.id, account_name=account.account_name)

    async def get_account_by_name(self, account_name: str) -> Account | None:
        """Retrieve an account by its name."""
        async with await self._get_session() as session:
            stmt = select(AccountModel).where(AccountModel.account_name == account_name.upper())
            result = await session.execute(stmt)
            account = result.scalar_one_or_none()
            return Account(id=account.id, account_name=account.account_name) if account else None

    async def get_account_by_id(self, account_id: str) -> Account | None:
        """Retrieve an account by its ID."""
        async with await self._get_session() as session:
            stmt = select(AccountModel).where(AccountModel.id == account_id)
            result = await session.execute(stmt)
            account = result.scalar_one_or_none()
            return Account(id=account.id, account_name=account.account_name) if account else None

    async def get_all_accounts(self) -> list[Account]:
        """Retrieve all accounts."""
        async with await self._get_session() as session:
            stmt = select(AccountModel)
            result = await session.execute(stmt)
            accounts = result.scalars().all()
            return [Account(id=acc.id, account_name=acc.account_name) for acc in accounts]

    async def update_account_name(self, account_id: str, account_name: str) -> Account:
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

            return Account(id=account.id, account_name=account.account_name)

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
