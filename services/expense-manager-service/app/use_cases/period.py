"""Service or use case for managing period."""

from app.entities.errors.period import (
    PeriodNotFoundError as EntityPeriodNotFoundError,
)
from app.entities.models.period import (
    Period,
)
from app.entities.repositories.period import PeriodRepositoryInterface
from app.use_cases.errors.period import (
    PeriodNotFoundError,
    PeriodWithDetailsNotFoundError,
)


class PeriodService:
    """Period service to handle business logic."""

    def __init__(self, period_repository: PeriodRepositoryInterface):
        """Initialize the period service with the repository."""
        self.period_repository = period_repository

    async def get_or_create_period(self, month: int, year: int) -> Period:
        """Retrieve an existing Period or create a new one with the provided month and year."""
        period_entity = await self.period_repository.get_or_create_period(month=month, year=year)
        return period_entity

    async def get_period_by_value(self, month: int, year: int) -> Period:
        """Retrieve a Period by its month and year.

        Raises:
            PeriodWithDetailsNotFoundError: If the Period with the provided month and year does not exist.
        """
        period_entity = await self.period_repository.get_period_by_value(month=month, year=year)

        if not period_entity:
            raise PeriodWithDetailsNotFoundError(month=month, year=year)

        return period_entity

    async def get_period_by_id(self, period_id: str) -> Period:
        """Retrieve a Period by its ID.

        Raises:
            PeriodNotFoundError: If the Period with the provided ID does not exist.
        """
        period_entity = await self.period_repository.get_period_by_id(period_id=period_id)

        if not period_entity:
            raise PeriodNotFoundError(period_id=period_id)

        return period_entity

    async def get_all_period(self) -> list[Period]:
        """Retrieve all Periods."""
        period_entities = await self.period_repository.get_all_period()

        if not period_entities:
            return []

        return period_entities

    async def update_period(self, period_id: str, month: int, year: int) -> Period:
        """Update an existing Period with the provided data.

        Raises:
            PeriodNotFoundError: If the Period with the provided ID does not exist.
        """
        try:
            period_entity = await self.period_repository.update_period(period_id=period_id, month=month, year=year)
        except EntityPeriodNotFoundError as error:
            raise PeriodNotFoundError(period_id=error.period_id) from error

        return period_entity

    async def delete_period(self, period_id: str) -> None:
        """Delete a Period by its ID.

        Raises:
            PeriodNotFoundError: If the Period with the provided ID does not exist.
        """
        try:
            await self.period_repository.delete_period(period_id=period_id)
        except EntityPeriodNotFoundError as error:
            raise PeriodNotFoundError(period_id=error.period_id) from error
