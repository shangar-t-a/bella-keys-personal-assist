"""Routers for spending account operations."""

from fastapi import APIRouter, Depends, HTTPException, status

from app.routers.v1.mappers.spending_account import (
    CreateSpendingAccountMapper,
    SpendingAccountMapper,
    SpendingAccountWithCalculatedFieldsMapper,
)
from app.routers.v1.schemas.errors import HTTPErrorResponse
from app.routers.v1.schemas.pagination import PaginationParams
from app.routers.v1.schemas.spending_account import (
    SpendingAccountEntryRequest,
    SpendingAccountEntryWithCalculatedFieldsPaginatedResponse,
    SpendingAccountEntryWithCalculatedFieldsResponse,
)
from app.routers.v1.services import get_spending_account_service
from app.use_cases.errors.accounts import (
    AccountNotFoundError,
    AccountWithNameNotFoundError,
)
from app.use_cases.errors.period import PeriodAlreadyExistsForAccountError
from app.use_cases.errors.spending_account import SpendingAccountEntryNotFoundError
from app.use_cases.spending_account import SpendingAccountService

router = APIRouter(prefix="/spending_account", tags=["spending_account"])


@router.post(
    "",
    response_model=SpendingAccountEntryWithCalculatedFieldsResponse,
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
    request: SpendingAccountEntryRequest,
    spending_account_service: SpendingAccountService = Depends(get_spending_account_service),
) -> SpendingAccountEntryWithCalculatedFieldsResponse:
    """Add a new entry to the spending account."""
    try:
        entry_dto = CreateSpendingAccountMapper.to_use_case_model(request=request)
        flattened_entry = await spending_account_service.add_entry(entry=entry_dto)
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
    return SpendingAccountWithCalculatedFieldsMapper.to_response_model(entry=flattened_entry)


@router.get("/list", response_model=SpendingAccountEntryWithCalculatedFieldsPaginatedResponse)
async def get_all_entries(
    pagination: PaginationParams = Depends(),
    spending_account_service: SpendingAccountService = Depends(get_spending_account_service),
) -> SpendingAccountEntryWithCalculatedFieldsPaginatedResponse:
    """Retrieve all entries for all spending accounts."""
    flattened_entries_with_calculated_fields_paginated = await spending_account_service.get_all_entries(
        limit=pagination.limit, offset=pagination.offset
    )
    return SpendingAccountEntryWithCalculatedFieldsPaginatedResponse(
        entries=[
            SpendingAccountWithCalculatedFieldsMapper.to_response_model(entry=entry)
            for entry in flattened_entries_with_calculated_fields_paginated.entries
        ],
        limit=flattened_entries_with_calculated_fields_paginated.limit,
        offset=flattened_entries_with_calculated_fields_paginated.offset,
        total_entries=flattened_entries_with_calculated_fields_paginated.total_entries,
    )


@router.get(
    "/{account_id}/list",
    response_model=SpendingAccountEntryWithCalculatedFieldsPaginatedResponse,
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
    spending_account_service: SpendingAccountService = Depends(get_spending_account_service),
) -> SpendingAccountEntryWithCalculatedFieldsPaginatedResponse:
    """Retrieve all entries for a given spending account."""
    try:
        flattened_entries_with_calculated_fields_paginated = await spending_account_service.get_all_entries_for_account(
            account_id=account_id, limit=pagination.limit, offset=pagination.offset
        )
    except AccountNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error.message,
        ) from error
    return SpendingAccountEntryWithCalculatedFieldsPaginatedResponse(
        entries=[
            SpendingAccountWithCalculatedFieldsMapper.to_response_model(entry=entry)
            for entry in flattened_entries_with_calculated_fields_paginated.entries
        ],
        limit=flattened_entries_with_calculated_fields_paginated.limit,
        offset=flattened_entries_with_calculated_fields_paginated.offset,
        total_entries=flattened_entries_with_calculated_fields_paginated.total_entries,
    )


@router.put(
    "/{entry_id}",
    response_model=SpendingAccountEntryWithCalculatedFieldsResponse,
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
    request: SpendingAccountEntryRequest,
    spending_account_service: SpendingAccountService = Depends(get_spending_account_service),
) -> SpendingAccountEntryWithCalculatedFieldsResponse:
    """Edit an existing spending account entry."""
    try:
        flattened_entry = await spending_account_service.edit_entry(
            entry_id=entry_id,
            entry=SpendingAccountMapper.to_use_case_model(
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
    return SpendingAccountWithCalculatedFieldsMapper.to_response_model(entry=flattened_entry)


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
    entry_id: str, spending_account_service: SpendingAccountService = Depends(get_spending_account_service)
) -> None:
    """Delete a spending account entry by its ID."""
    try:
        await spending_account_service.delete_entry(entry_id=entry_id)
    except SpendingAccountEntryNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error.message,
        ) from error
