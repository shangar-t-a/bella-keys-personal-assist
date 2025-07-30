"""Base error for the expense manager service use cases."""


class ExpenseManagerUseCaseError(Exception):
    """Base class for all use case errors."""

    def __init__(self, message: str):
        """Initialize the error with a message."""
        super().__init__(message)
        self.message = message
