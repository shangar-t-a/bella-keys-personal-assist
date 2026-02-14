"""Data access layer for spending account."""

from typing import ClassVar

from app.entities.errors.accounts import AccountNotFoundError
from app.entities.errors.period import PeriodNotFoundError
from app.entities.models.accounts import Account
from app.entities.models.period import Period
from app.entities.repositories.accounts import AccountRepositoryInterface


class AccountRepository(AccountRepositoryInterface):
    """Implementation of the AccountRepositoryInterface."""

    accounts: ClassVar[dict[str, dict]] = {}
    periods: ClassVar[dict[str, dict]] = {}

    def __init__(self):
        """Initialize the in-memory account repository."""
        pass

    async def get_or_create_account(self, account_name: str) -> Account:
        """Retrieve an existing account or create a new one with the provided name."""
        new_account = Account(account_name=account_name)
        new_account_data = new_account.model_dump()
        for account in self.accounts.values():
            if account["account_name"] == new_account.account_name:
                return Account(**account)
        self.accounts[new_account_data["id"]] = new_account_data
        return new_account

    async def get_account_by_name(self, account_name: str) -> Account | None:
        """Retrieve an account by its name."""
        for account in self.accounts.values():
            if account["account_name"] == account_name:
                return Account(**account)
        return None

    async def get_account_by_id(self, account_id: str) -> Account | None:
        """Retrieve an account by its ID."""
        account = self.accounts.get(account_id)
        if account:
            return Account(**account)
        return None

    async def get_all_accounts(self) -> list[Account]:
        """Retrieve all accounts."""
        return [Account(**account) for account in self.accounts.values()]

    async def update_account_name(self, account_id: str, account_name: str) -> Account:
        """Update an existing account name with the provided data."""
        account = self.accounts.get(account_id)
        if not account:
            raise AccountNotFoundError(account_id=account_id)
        account["account_name"] = account_name
        return Account(**account)

    async def delete_account(self, account_id: str) -> None:
        """Delete an account by its ID."""
        if account_id in self.accounts:
            del self.accounts[account_id]
        else:
            raise AccountNotFoundError(account_id=account_id)

    async def get_or_create_period(self, month: str, year: int) -> Period:
        """Retrieve an existing Period or create a new one with the provided month and year."""
        for period in self.periods.values():
            if period["month"] == month and period["year"] == year:
                return Period(**period)
        new_period = Period(month=month, year=year)
        self.periods[new_period.id] = new_period.model_dump()
        return new_period

    async def get_period_by_value(self, month: str, year: int) -> Period | None:
        """Retrieve a Period by its month and year."""
        for period in self.periods.values():
            if period["month"] == month and period["year"] == year:
                return Period(**period)
        return None

    async def get_period_by_id(self, period_id: str) -> Period | None:
        """Retrieve a Period by its ID."""
        period = self.periods.get(period_id)
        if period:
            return Period(**period)
        return None

    async def get_all_period(self) -> list[Period]:
        """Retrieve all month-year records."""
        return [Period(**period) for period in self.periods.values()]

    async def update_period(self, period_id: str, month: str, year: int) -> Period:
        """Update an existing Period with the provided month and year."""
        period = self.periods.get(period_id)
        if not period:
            raise PeriodNotFoundError(period_id=period_id)
        period["month"] = month
        period["year"] = year
        return Period(**period)

    async def delete_period(self, period_id: str) -> None:
        """Delete a Period by its ID."""
        if period_id in self.periods:
            del self.periods[period_id]
        else:
            raise PeriodNotFoundError(period_id=period_id)
