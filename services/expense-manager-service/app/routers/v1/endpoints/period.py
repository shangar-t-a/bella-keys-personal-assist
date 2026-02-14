"""Routers for period operations."""

from fastapi import APIRouter, Depends, HTTPException, status

from app.routers.v1.schemas.errors import HTTPErrorResponse
from app.routers.v1.schemas.period import (
    PeriodRequest,
    PeriodResponse,
)
from app.routers.v1.services import get_period_service
from app.use_cases.errors.period import PeriodNotFoundError
from app.use_cases.period import PeriodService

period_router = APIRouter(prefix="/period", tags=["period"])


@period_router.post("/get_or_create", response_model=PeriodResponse)
async def get_or_create_period(
    period_request: PeriodRequest, period_service: PeriodService = Depends(get_period_service)
) -> PeriodResponse:
    """Retrieve an existing Period or create a new one with the provided month and year."""
    period = await period_service.get_or_create_period(month=period_request.month, year=period_request.year)

    return PeriodResponse(id=period.id, month=period.month, year=period.year)


@period_router.get("/list", response_model=list[PeriodResponse])
async def get_all_period(
    period_service: PeriodService = Depends(get_period_service),
) -> list[PeriodResponse]:
    """Retrieve all Periods."""
    all_period = await period_service.get_all_period()

    return [PeriodResponse(id=period.id, month=period.month, year=period.year) for period in all_period]


@period_router.get(
    "/{period_id}",
    response_model=PeriodResponse,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": HTTPErrorResponse,
            "description": "Period not found",
        }
    },
)
async def get_period_by_id(
    period_id: str, period_service: PeriodService = Depends(get_period_service)
) -> PeriodResponse:
    """Retrieve a Period by its ID."""
    try:
        period = await period_service.get_period_by_id(period_id=period_id)
    except PeriodNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error.message,
        ) from error

    return PeriodResponse(id=period.id, month=period.month, year=period.year)


@period_router.put(
    "/{period_id}",
    response_model=PeriodResponse,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": HTTPErrorResponse,
            "description": "Period not found",
        }
    },
)
async def update_period(
    period_id: str,
    period_update_request: PeriodRequest,
    period_service: PeriodService = Depends(get_period_service),
) -> PeriodResponse:
    """Update an existing Period with the provided data."""
    try:
        period = await period_service.update_period(
            period_id=period_id, month=period_update_request.month, year=period_update_request.year
        )
    except PeriodNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error.message,
        ) from error

    return PeriodResponse(id=period.id, month=period.month, year=period.year)


@period_router.delete(
    "/{period_id}",
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": HTTPErrorResponse,
            "description": "Period not found",
        }
    },
)
async def delete_period(period_id: str, period_service: PeriodService = Depends(get_period_service)) -> None:
    """Delete a Period by its ID."""
    try:
        await period_service.delete_period(period_id=period_id)
    except PeriodNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error.message,
        ) from error
