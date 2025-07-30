"""Data access layer for spending account."""

from typing import ClassVar

from app.entities.errors.accounts import AccountNotFoundError, MonthYearNotFoundError
from app.entities.models.accounts import AccountName, MonthYear
from app.entities.repositories.accounts import AccountRepositoryInterface


class AccountRepository(AccountRepositoryInterface):
    """Implementation of the AccountRepositoryInterface."""

    accounts: ClassVar[dict[str, dict]] = {}
    month_years: ClassVar[dict[str, dict]] = {}

    def __init__(self):
        """Initialize the in-memory account repository."""
        pass

    async def get_or_create_account(self, account_name: str) -> AccountName:
        """Retrieve an existing account or create a new one with the provided name."""
        new_account = AccountName(account_name=account_name)
        new_account_data = new_account.model_dump()
        for account in self.accounts.values():
            if account["account_name"] == new_account.account_name:
                return AccountName(**account)
        self.accounts[new_account_data["id"]] = new_account_data
        return new_account

    async def get_account_by_name(self, account_name: str) -> AccountName | None:
        """Retrieve an account by its name."""
        for account in self.accounts.values():
            if account["account_name"] == account_name:
                return AccountName(**account)
        return None

    async def get_account_by_id(self, account_id: str) -> AccountName | None:
        """Retrieve an account by its ID."""
        account = self.accounts.get(account_id)
        if account:
            return AccountName(**account)
        return None

    async def get_all_accounts(self) -> list[AccountName]:
        """Retrieve all accounts."""
        return [AccountName(**account) for account in self.accounts.values()]

    async def update_account_name(self, account_id: str, account_name: str) -> AccountName:
        """Update an existing account name with the provided data."""
        account = self.accounts.get(account_id)
        if not account:
            raise AccountNotFoundError(account_id=account_id)
        account["account_name"] = account_name
        return AccountName(**account)

    async def delete_account(self, account_id: str) -> None:
        """Delete an account by its ID."""
        if account_id in self.accounts:
            del self.accounts[account_id]
        else:
            raise AccountNotFoundError(account_id=account_id)

    async def get_or_create_month_year(self, month: str, year: int) -> MonthYear:
        """Retrieve an existing MonthYear or create a new one with the provided month and year."""
        for month_year in self.month_years.values():
            if month_year["month"] == month and month_year["year"] == year:
                return MonthYear(**month_year)
        new_month_year = MonthYear(month=month, year=year)
        self.month_years[new_month_year.id] = new_month_year.model_dump()
        return new_month_year

    async def get_month_year_by_value(self, month: str, year: int) -> MonthYear | None:
        """Retrieve a MonthYear by its month and year."""
        for month_year in self.month_years.values():
            if month_year["month"] == month and month_year["year"] == year:
                return MonthYear(**month_year)
        return None

    async def get_month_year_by_id(self, month_year_id: str) -> MonthYear | None:
        """Retrieve a MonthYear by its ID."""
        month_year = self.month_years.get(month_year_id)
        if month_year:
            return MonthYear(**month_year)
        return None

    async def get_all_month_years(self) -> list[MonthYear]:
        """Retrieve all month-year records."""
        return [MonthYear(**month_year) for month_year in self.month_years.values()]

    async def update_month_year(self, month_year_id: str, month: str, year: int) -> MonthYear:
        """Update an existing MonthYear with the provided month and year."""
        month_year = self.month_years.get(month_year_id)
        if not month_year:
            raise MonthYearNotFoundError(month_year_id=month_year_id)
        month_year["month"] = month
        month_year["year"] = year
        return MonthYear(**month_year)

    async def delete_month_year(self, month_year_id: str) -> None:
        """Delete a MonthYear by its ID."""
        if month_year_id in self.month_years:
            del self.month_years[month_year_id]
        else:
            raise MonthYearNotFoundError(month_year_id=month_year_id)
