"""Errors related to period operations in the Expense Manager Service use cases."""

from app.use_cases.errors.base import ExpenseManagerUseCaseError


class PeriodNotFoundError(ExpenseManagerUseCaseError):
    """Error raised when a Period is not found."""

    def __init__(self, period_id: str):
        """Initialize the error with the month-year ID."""
        super().__init__(f"Period with ID '{period_id}' not found.")
        self.period_id = period_id


class PeriodWithDetailsNotFoundError(ExpenseManagerUseCaseError):
    """Error raised when a Period with specific details is not found."""

    def __init__(self, month: int, year: int):
        """Initialize the error with the month and year."""
        super().__init__(f"Period with month '{month}' and year '{year}' not found.")
        self.month = month
        self.year = year


class PeriodAlreadyExistsForAccountError(ExpenseManagerUseCaseError):
    """Error raised when a Period already exists for a specific account."""

    def __init__(self, account_name: str, month: int, year: int):
        """Initialize the error with the account name, month, and year."""
        super().__init__(f"Period '{month}-{year}' already exists for account '{account_name}'.")
        self.account_name = account_name
        self.month = month
        self.year = year
