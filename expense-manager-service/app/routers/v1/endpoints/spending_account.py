"""Routers for spending account operations."""

from fastapi import APIRouter, Depends, HTTPException, status

from app.routers.v1.schemas.errors import HTTPErrorResponse
from app.routers.v1.schemas.spending_account import (
    SpendingAccountEntryRequest,
    SpendingAccountEntryWithCalculatedFieldsResponse,
)
from app.routers.v1.services import get_spending_account_service
from app.use_cases.errors.accounts import (
    AccountNotFoundError,
    AccountWithNameNotFoundError,
    MonthYearAlreadyExistsForAccountError,
)
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
        entry = await spending_account_service.add_entry(request)
    except AccountWithNameNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error.message,
        ) from error
    except MonthYearAlreadyExistsForAccountError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error.message,
        ) from error
    return SpendingAccountEntryWithCalculatedFieldsResponse(
        id=entry.id,
        account_name=entry.account_name,
        month=entry.month,
        year=entry.year,
        starting_balance=entry.starting_balance,
        current_balance=entry.current_balance,
        current_credit=entry.current_credit,
        balance_after_credit=entry.balance_after_credit,
        total_spent=entry.total_spent,
    )


@router.get("/list", response_model=list[SpendingAccountEntryWithCalculatedFieldsResponse])
async def get_all_entries(
    spending_account_service: SpendingAccountService = Depends(get_spending_account_service),
) -> list[SpendingAccountEntryWithCalculatedFieldsResponse]:
    """Retrieve all entries for all spending accounts."""
    entries = await spending_account_service.get_all_entries()
    return [
        SpendingAccountEntryWithCalculatedFieldsResponse(
            id=entry.id,
            account_name=entry.account_name,
            month=entry.month,
            year=entry.year,
            starting_balance=entry.starting_balance,
            current_balance=entry.current_balance,
            current_credit=entry.current_credit,
            balance_after_credit=entry.balance_after_credit,
            total_spent=entry.total_spent,
        )
        for entry in entries
    ]


@router.get(
    "/{account_id}",
    response_model=list[SpendingAccountEntryWithCalculatedFieldsResponse],
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": HTTPErrorResponse,
            "description": "Spending account not found",
        }
    },
)
async def get_all_entries_for_account(
    account_id: str, spending_account_service: SpendingAccountService = Depends(get_spending_account_service)
) -> list[SpendingAccountEntryWithCalculatedFieldsResponse]:
    """Retrieve all entries for a given spending account."""
    try:
        entries = await spending_account_service.get_all_entries_for_account(account_id=account_id)
    except AccountNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error.message,
        ) from error
    return [
        SpendingAccountEntryWithCalculatedFieldsResponse(
            id=entry.id,
            account_name=entry.account_name,
            month=entry.month,
            year=entry.year,
            starting_balance=entry.starting_balance,
            current_balance=entry.current_balance,
            current_credit=entry.current_credit,
            balance_after_credit=entry.balance_after_credit,
            total_spent=entry.total_spent,
        )
        for entry in entries
    ]


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
        entry = await spending_account_service.edit_entry(entry_id=entry_id, entry=request)
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
    except MonthYearAlreadyExistsForAccountError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error.message,
        ) from error
    return SpendingAccountEntryWithCalculatedFieldsResponse(
        id=entry.id,
        account_name=entry.account_name,
        month=entry.month,
        year=entry.year,
        starting_balance=entry.starting_balance,
        current_balance=entry.current_balance,
        current_credit=entry.current_credit,
        balance_after_credit=entry.balance_after_credit,
        total_spent=entry.total_spent,
    )


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
