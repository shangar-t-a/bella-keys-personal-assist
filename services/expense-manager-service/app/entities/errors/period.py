"""Errors related to period operations."""

from app.entities.errors.base import BaseEntityError


class PeriodNotFoundError(BaseEntityError):
    """Exception raised when a Period record is not found."""

    def __init__(self, period_id: str):
        """Initialize the error with the Period ID."""
        super().__init__(f"Period with ID '{period_id}' not found.")
        self.period_id = period_id
