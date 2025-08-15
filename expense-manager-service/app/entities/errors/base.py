"""Base exception class for the Expense Manager Service entities."""


class BaseEntityError(Exception):
    """Base class for all entity-related exceptions in the Expense Manager Service."""

    def __init__(self, message: str):
        """Initialize the base entity error with a message."""
        super().__init__(message)
        self.message = message
