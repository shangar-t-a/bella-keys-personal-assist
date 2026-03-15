"""Repository interface for period."""

from abc import ABC, abstractmethod

from app.entities.models.period import (
    Period,
)


class PeriodRepositoryInterface(ABC):
    """Interface for period repository."""

    @abstractmethod
    async def get_or_create_period(self, month: int, year: int) -> Period:
        """Retrieve an existing Period or create a new one with the provided month and year."""
        pass

    @abstractmethod
    async def get_period_by_value(self, month: int, year: int) -> Period | None:
        """Retrieve a Period by its month and year."""
        pass

    @abstractmethod
    async def get_period_by_id(self, period_id: str) -> Period | None:
        """Retrieve a Period by its ID."""
        pass

    @abstractmethod
    async def get_all_period(self) -> list[Period]:
        """Retrieve all month-year records."""
        pass

    @abstractmethod
    async def update_period(self, period_id: str, month: int, year: int) -> Period:
        """Update an existing Period with the provided month and year."""
        pass

    @abstractmethod
    async def delete_period(self, period_id: str) -> None:
        """Delete a Period by its ID."""
        pass
