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


class MonthYearNotFoundError(ExpenseManagerUseCaseError):
    """Error raised when a MonthYear is not found."""

    def __init__(self, month_year_id: str):
        """Initialize the error with the month-year ID."""
        super().__init__(f"MonthYear with ID '{month_year_id}' not found.")
        self.month_year_id = month_year_id


class MonthYearWithDetailsNotFoundError(ExpenseManagerUseCaseError):
    """Error raised when a MonthYear with specific details is not found."""

    def __init__(self, month: str, year: int):
        """Initialize the error with the month and year."""
        super().__init__(f"MonthYear with month '{month}' and year '{year}' not found.")
        self.month = month
        self.year = year


class MonthYearAlreadyExistsForAccountError(ExpenseManagerUseCaseError):
    """Error raised when a MonthYear already exists for a specific account."""

    def __init__(self, account_name: str, month: str, year: int):
        """Initialize the error with the account name, month, and year."""
        super().__init__(f"MonthYear '{month}-{year}' already exists for account '{account_name}'.")
        self.account_name = account_name
        self.month = month
        self.year = year
