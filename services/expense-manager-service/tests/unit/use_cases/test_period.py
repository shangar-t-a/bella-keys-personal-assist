"""Unit tests for the period use case."""

from uuid import uuid4

import pytest

from app.use_cases.errors.period import (
    PeriodNotFoundError,
    PeriodWithDetailsNotFoundError,
)
from app.use_cases.period import PeriodService


@pytest.fixture(scope="module")
def period_service(period_repo):
    """Provide an instance of PeriodService."""
    return PeriodService(period_repository=period_repo)


async def add_period(period_service, month=9, year=2025):
    period = await period_service.period_repository.get_or_create_period(month=month, year=year)
    return period


async def delete_all_period(period_service):
    all_period = await period_service.period_repository.get_all_period()
    for period in all_period:
        await period_service.period_repository.delete_period(period.id)


class TestGetOrCreatePeriod:
    async def test__get_or_create_period__create_period(
        self,
        period_service,
    ):
        """Test creating a new month-year entry."""
        month = 9
        year = 2025
        period = await period_service.get_or_create_period(month=month, year=year)

        assert period is not None
        assert period.month == month
        assert period.year == year

    async def test__get_or_create_period__retrieve_existing_period(
        self,
        period_service,
    ):
        """Test retrieving an existing month-year entry."""
        test_period = await add_period(period_service)

        period = await period_service.get_or_create_period(month=test_period.month, year=test_period.year)

        assert period.id == test_period.id
        assert period.month == test_period.month
        assert period.year == test_period.year


class TestGetPeriodByValue:
    async def test__get_period_by_value__existing_period__retrieve_period(
        self,
        period_service,
    ):
        """Test retrieving an existing month-year entry by month and year."""
        test_period = await add_period(period_service)

        period = await period_service.get_period_by_value(month=test_period.month, year=test_period.year)

        assert period is not None
        assert period.id == test_period.id
        assert period.month == test_period.month
        assert period.year == test_period.year

    async def test__get_period_by_value__nonexistent_period__raise_error(
        self,
        period_service,
    ):
        """Test retrieving a non-existent month-year entry by month and year."""
        with pytest.raises(PeriodWithDetailsNotFoundError):
            await period_service.get_period_by_value(month=99, year=1999)


class TestGetPeriodById:
    async def test__get_period_by_id__existing_period__retrieve_period(
        self,
        period_service,
    ):
        """Test retrieving an existing month-year entry by ID."""
        test_period = await add_period(period_service)

        period = await period_service.get_period_by_id(period_id=test_period.id)

        assert period is not None
        assert period.id == test_period.id
        assert period.month == test_period.month
        assert period.year == test_period.year

    async def test__get_period_by_id__nonexistent_period__raise_error(
        self,
        period_service,
    ):
        """Test retrieving a non-existent month-year entry by ID."""
        with pytest.raises(PeriodNotFoundError):
            await period_service.get_period_by_id(period_id=f"non-existent-id-{uuid4()}")


class TestDeletePeriod:
    async def test__delete_period__delete_existing_period(
        self,
        period_service,
    ):
        """Test deleting an existing month-year entry."""
        month = 10
        year = 2025
        test_period = await add_period(period_service=period_service, month=month, year=year)

        period = await period_service.get_period_by_id(period_id=test_period.id)
        assert period is not None
        assert period.month == month
        assert period.year == year
        await period_service.delete_period(period_id=test_period.id)

        with pytest.raises(PeriodNotFoundError):
            await period_service.get_period_by_id(period_id=test_period.id)

    async def test__delete_period__nonexistent_period__raise_error(
        self,
        period_service,
    ):
        """Test deleting a non-existent month-year entry raises error."""
        with pytest.raises(PeriodNotFoundError):
            await period_service.delete_period(period_id=f"non-existent-id-{uuid4()}")


class TestGetAllPeriod:
    async def test__get_all_period__with_existing_period__retrieve_period(
        self,
        period_service,
    ):
        """Test retrieving all month-year entries when entries exist."""
        await delete_all_period(period_service)
        await add_period(period_service=period_service, month=1, year=2025)
        await add_period(period_service=period_service, month=2, year=2025)
        num_period = 2

        all_period = await period_service.get_all_period()

        assert all_period is not None
        assert len(all_period) == num_period

    async def test__get_all_period__with_no_period__retrieve_empty_list(
        self,
        period_service,
    ):
        """Test retrieving all month-year entries when no entries exist."""
        await delete_all_period(period_service)

        all_period = await period_service.get_all_period()

        assert all_period == []


class TestUpdatePeriod:
    async def test__update_period__existing_period__update_period(
        self,
        period_service,
    ):
        """Test updating an existing month-year entry."""
        month = 3
        year = 2025
        update_month = 4
        update_year = 2026
        test_period = await add_period(period_service=period_service, month=month, year=year)

        assert test_period.month == month
        assert test_period.year == year
        updated_period = await period_service.update_period(
            period_id=test_period.id,
            month=update_month,
            year=update_year,
        )

        assert updated_period is not None
        assert updated_period.id == test_period.id
        assert updated_period.month == update_month
        assert updated_period.year == update_year

    async def test__update_period__nonexistent_period__raise_error(
        self,
        period_service,
    ):
        """Test updating a non-existent month-year entry."""
        with pytest.raises(PeriodNotFoundError):
            await period_service.update_period(
                period_id=f"non-existent-id-{uuid4()}",
                month=5,
                year=2027,
            )
