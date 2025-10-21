"""Repository interface for accounts."""

from abc import ABC, abstractmethod

from app.entities.models.accounts import AccountName, MonthLiteral, MonthYear


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

    @abstractmethod
    async def get_or_create_month_year(self, month: MonthLiteral, year: int) -> MonthYear:
        """Retrieve an existing MonthYear or create a new one with the provided month and year."""
        pass

    @abstractmethod
    async def get_month_year_by_value(self, month: MonthLiteral, year: int) -> MonthYear | None:
        """Retrieve a MonthYear by its month and year."""
        pass

    @abstractmethod
    async def get_month_year_by_id(self, month_year_id: str) -> MonthYear | None:
        """Retrieve a MonthYear by its ID."""
        pass

    @abstractmethod
    async def get_all_month_years(self) -> list[MonthYear]:
        """Retrieve all month-year records."""
        pass

    @abstractmethod
    async def update_month_year(self, month_year_id: str, month: MonthLiteral, year: int) -> MonthYear:
        """Update an existing MonthYear with the provided month and year."""
        pass

    @abstractmethod
    async def delete_month_year(self, month_year_id: str) -> None:
        """Delete a MonthYear by its ID."""
        pass
