"""Errors related to spending account operations."""

from app.entities.errors.base import BaseEntityError


class SpendingAccountEntryNotFoundError(BaseEntityError):
    """Exception raised when a spending account entry is not found."""

    def __init__(self, entry_id: str):
        """Initialize the error with the entry ID."""
        super().__init__(f"Spending account entry with ID '{entry_id}' not found.")
        self.entry_id = entry_id
