"""Routers for accounts operations."""

from fastapi import APIRouter, Depends, HTTPException, status

from app.routers.v1.schemas.accounts import (
    AccountRequest,
    AccountResponse,
    AccountUpdateRequest,
)
from app.routers.v1.schemas.errors import HTTPErrorResponse
from app.routers.v1.services import get_accounts_service
from app.use_cases.accounts import AccountService
from app.use_cases.errors.accounts import AccountNotFoundError

account_router = APIRouter(prefix="/account", tags=["account"])


@account_router.post("/get_or_create", response_model=AccountResponse)
async def get_or_create_account(
    account_name_request: AccountRequest, account_service: AccountService = Depends(get_accounts_service)
) -> AccountResponse:
    """Create or retrieve an account with the given name."""
    account = await account_service.get_or_create_account(account_name=account_name_request.account_name)

    return AccountResponse(id=account.id, account_name=account.account_name)


@account_router.get("/list", response_model=list[AccountResponse])
async def get_all_accounts(
    account_service: AccountService = Depends(get_accounts_service),
) -> list[AccountResponse]:
    """Retrieve all accounts."""
    accounts = await account_service.get_all_accounts()

    return [AccountResponse(id=acc.id, account_name=acc.account_name) for acc in accounts]


@account_router.get(
    "/{account_id}",
    response_model=AccountResponse,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": HTTPErrorResponse,
            "description": "Account not found",
        }
    },
)
async def get_account_by_id(
    account_id: str, account_service: AccountService = Depends(get_accounts_service)
) -> AccountResponse:
    """Retrieve an account by its ID."""
    try:
        account = await account_service.get_account_by_id(account_id=account_id)
    except AccountNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error.message,
        ) from error

    return AccountResponse(id=account.id, account_name=account.account_name)


@account_router.put(
    "/{account_id}",
    response_model=AccountResponse,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": HTTPErrorResponse,
            "description": "Account not found",
        }
    },
)
async def update_account_name(
    account_id: str,
    account_name_update_request: AccountUpdateRequest,
    account_service: AccountService = Depends(get_accounts_service),
) -> AccountResponse:
    """Update an existing account name with the provided data."""
    try:
        account = await account_service.update_account_name(
            account_id=account_id, account_name=account_name_update_request.account_name
        )
    except AccountNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error.message,
        ) from error

    return AccountResponse(id=account.id, account_name=account.account_name)


@account_router.delete(
    "/{account_id}",
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": HTTPErrorResponse,
            "description": "Account not found",
        }
    },
)
async def delete_account(account_id: str, account_service: AccountService = Depends(get_accounts_service)) -> None:
    """Delete an account by its ID."""
    try:
        await account_service.delete_account(account_id=account_id)
    except AccountNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error.message,
        ) from error
