"""Errors related to account operations."""

from app.entities.errors.base import BaseEntityError


class AccountNotFoundError(BaseEntityError):
    """Exception raised when an account is not found."""

    def __init__(self, account_id: str):
        """Initialize the error with the account ID."""
        super().__init__(f"Account with ID '{account_id}' not found.")
        self.account_id = account_id


class MonthYearNotFoundError(BaseEntityError):
    """Exception raised when a MonthYear record is not found."""

    def __init__(self, month_year_id: str):
        """Initialize the error with the MonthYear ID."""
        super().__init__(f"MonthYear with ID '{month_year_id}' not found.")
        self.month_year_id = month_year_id
