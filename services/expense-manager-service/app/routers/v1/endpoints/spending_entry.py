"""Routers for spending account operations."""

from fastapi import APIRouter, Depends, HTTPException, status

from app.routers.v1.mappers.spending_entry import (
    SpendingEntryCreateMapper,
    SpendingEntryMapper,
    SpendingEntryQueryParamsMapper,
    SpendingEntryWithCalcMapper,
)
from app.routers.v1.schemas.errors import HTTPErrorResponse
from app.routers.v1.schemas.pagination import (
    PaginationParams,
    PaginationResponse,
)
from app.routers.v1.schemas.spending_entry import (
    SpendingEntryFilterParams,
    SpendingEntryRequest,
    SpendingEntrySortParams,
    SpendingEntryWithCalcPageResponse,
    SpendingEntryWithCalcResponse,
)
from app.routers.v1.services import get_spending_entry_service
from app.use_cases.errors.account import (
    AccountNotFoundError,
    AccountWithNameNotFoundError,
)
from app.use_cases.errors.period import PeriodAlreadyExistsForAccountError
from app.use_cases.errors.spending_entry import SpendingAccountEntryNotFoundError
from app.use_cases.spending_entry import SpendingEntryService

router = APIRouter(prefix="/spending_account", tags=["spending_account"])


@router.post(
    "",
    response_model=SpendingEntryWithCalcResponse,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": HTTPErrorResponse,
            "description": "Spending account entry not found",
        },
        status.HTTP_400_BAD_REQUEST: {
            "model": HTTPErrorResponse,
            "description": "Account with name not found or month/year already exists for account",
        },
    },
)
async def add_entry(
    request: SpendingEntryRequest,
    spending_account_service: SpendingEntryService = Depends(get_spending_entry_service),
) -> SpendingEntryWithCalcResponse:
    """Add a new entry to the spending account."""
    try:
        entry_dto = SpendingEntryCreateMapper.to_use_case_model(request=request)
        spending_entry_with_calc = await spending_account_service.add_entry(entry=entry_dto)
    except AccountWithNameNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error.message,
        ) from error
    except PeriodAlreadyExistsForAccountError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error.message,
        ) from error
    return SpendingEntryWithCalcMapper.to_response_model(entry=spending_entry_with_calc)


@router.get("/list", response_model=SpendingEntryWithCalcPageResponse)
async def get_all_entries(
    pagination: PaginationParams = Depends(),
    sort: SpendingEntrySortParams = Depends(),
    filters: SpendingEntryFilterParams = Depends(),
    spending_account_service: SpendingEntryService = Depends(get_spending_entry_service),
) -> SpendingEntryWithCalcPageResponse:
    """Retrieve all entries for all spending accounts."""
    # Map request parameters to use case query params model
    filters_model = SpendingEntryQueryParamsMapper.to_filters_model(filters=filters)
    sort_model = SpendingEntryQueryParamsMapper.to_sort_model(sort=sort)

    spending_entry_with_calc_page = await spending_account_service.get_all_entries(
        page=pagination.page, size=pagination.size, filters=filters_model, sort=sort_model
    )
    return SpendingEntryWithCalcPageResponse(
        spending_entries=[
            SpendingEntryWithCalcMapper.to_response_model(entry=entry)
            for entry in spending_entry_with_calc_page.spending_entries
        ],
        page=PaginationResponse(
            number=spending_entry_with_calc_page.page.number,
            size=spending_entry_with_calc_page.page.size,
            total_elements=spending_entry_with_calc_page.page.total_elements,
            total_pages=spending_entry_with_calc_page.page.total_pages,
        ),
    )


@router.get(
    "/{account_id}/list",
    response_model=SpendingEntryWithCalcPageResponse,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": HTTPErrorResponse,
            "description": "Spending account not found",
        }
    },
)
async def get_all_entries_for_account(
    account_id: str,
    pagination: PaginationParams = Depends(),
    sort: SpendingEntrySortParams = Depends(),
    filters: SpendingEntryFilterParams = Depends(),
    spending_account_service: SpendingEntryService = Depends(get_spending_entry_service),
) -> SpendingEntryWithCalcPageResponse:
    """Retrieve all entries for a given spending account."""
    try:
        # Map request parameters to use case query params model
        filters_model = SpendingEntryQueryParamsMapper.to_filters_model(filters=filters)
        sort_model = SpendingEntryQueryParamsMapper.to_sort_model(sort=sort)

        spending_entry_with_calc_page = await spending_account_service.get_all_entries_for_account(
            account_id=account_id, page=pagination.page, size=pagination.size, filters=filters_model, sort=sort_model
        )
    except AccountNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error.message,
        ) from error
    return SpendingEntryWithCalcPageResponse(
        spending_entries=[
            SpendingEntryWithCalcMapper.to_response_model(entry=entry)
            for entry in spending_entry_with_calc_page.spending_entries
        ],
        page=PaginationResponse(
            number=spending_entry_with_calc_page.page.number,
            size=spending_entry_with_calc_page.page.size,
            total_elements=spending_entry_with_calc_page.page.total_elements,
            total_pages=spending_entry_with_calc_page.page.total_pages,
        ),
    )


@router.put(
    "/{entry_id}",
    response_model=SpendingEntryWithCalcResponse,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": HTTPErrorResponse,
            "description": "Spending account entry not found",
        },
        status.HTTP_400_BAD_REQUEST: {
            "model": HTTPErrorResponse,
            "description": "Account with name not found or month/year already exists for account",
        },
    },
)
async def edit_entry(
    entry_id: str,
    request: SpendingEntryRequest,
    spending_account_service: SpendingEntryService = Depends(get_spending_entry_service),
) -> SpendingEntryWithCalcResponse:
    """Edit an existing spending account entry."""
    try:
        spending_entry_with_calc = await spending_account_service.edit_entry(
            entry_id=entry_id,
            entry=SpendingEntryMapper.to_use_case_model(
                entry_id=entry_id,
                request=request,
            ),
        )
    except SpendingAccountEntryNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error.message,
        ) from error
    except AccountWithNameNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error.message,
        ) from error
    except PeriodAlreadyExistsForAccountError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error.message,
        ) from error
    return SpendingEntryWithCalcMapper.to_response_model(entry=spending_entry_with_calc)


@router.delete(
    "/{entry_id}",
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": HTTPErrorResponse,
            "description": "Spending account entry not found",
        }
    },
)
async def delete_entry(
    entry_id: str, spending_account_service: SpendingEntryService = Depends(get_spending_entry_service)
) -> None:
    """Delete a spending account entry by its ID."""
    try:
        await spending_account_service.delete_entry(entry_id=entry_id)
    except SpendingAccountEntryNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error.message,
        ) from error
