"""Errors related to account operations in the Expense Manager Service use cases."""

from app.use_cases.errors.base import ExpenseManagerUseCaseError


class AccountNotFoundError(ExpenseManagerUseCaseError):
    """Error raised when an account is not found."""

    def __init__(self, account_id: str):
        """Initialize the error with the account ID."""
        super().__init__(f"Account with ID '{account_id}' not found.")
        self.account_id = account_id


class AccountWithNameNotFoundError(ExpenseManagerUseCaseError):
    """Error raised when an account with a specific name is not found."""

    def __init__(self, account_name: str):
        """Initialize the error with the account name."""
        super().__init__(f"Account with name '{account_name}' not found.")
        self.account_name = account_name
