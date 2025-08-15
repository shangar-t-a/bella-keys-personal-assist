"""Errors related to account operations in the Expense Manager Service use cases."""

from app.use_cases.errors.base import ExpenseManagerUseCaseError


class SpendingAccountEntryNotFoundError(ExpenseManagerUseCaseError):
    """Error raised when a spending account entry is not found."""

    def __init__(self, entry_id: str):
        """Initialize the error with the entry ID."""
        super().__init__(f"Spending account entry with ID '{entry_id}' not found.")
        self.entry_id = entry_id
