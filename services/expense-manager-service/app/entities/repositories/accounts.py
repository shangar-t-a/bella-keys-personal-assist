"""Repository interface for accounts."""

from abc import ABC, abstractmethod

from app.entities.models.accounts import (
    AccountName,
)


class AccountRepositoryInterface(ABC):
    """Interface for account repository."""

    @abstractmethod
    async def get_or_create_account(self, account_name: str) -> AccountName:
        """Retrieve an existing account or create a new one with the provided name."""
        pass

    @abstractmethod
    async def get_account_by_name(self, account_name: str) -> AccountName | None:
        """Retrieve an account by its name."""
        pass

    @abstractmethod
    async def get_account_by_id(self, account_id: str) -> AccountName | None:
        """Retrieve an account by its ID."""
        pass

    @abstractmethod
    async def get_all_accounts(self) -> list[AccountName]:
        """Retrieve all accounts."""
        pass

    @abstractmethod
    async def update_account_name(self, account_id: str, account_name: str) -> AccountName:
        """Update an existing account name with the provided data."""
        pass

    @abstractmethod
    async def delete_account(self, account_id: str) -> None:
        """Delete an account by its ID."""
        pass
