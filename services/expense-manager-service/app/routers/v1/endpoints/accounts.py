"""Routers for accounts operations."""

from fastapi import APIRouter, Depends, HTTPException, status

from app.routers.v1.schemas.accounts import (
    AccountNameRequest,
    AccountNameResponse,
    AccountUpdateRequest,
    MonthYearRequest,
    MonthYearResponse,
)
from app.routers.v1.schemas.errors import HTTPErrorResponse
from app.routers.v1.services import get_accounts_service
from app.use_cases.accounts import AccountService
from app.use_cases.errors.accounts import AccountNotFoundError, MonthYearNotFoundError

account_router = APIRouter(prefix="/account", tags=["account"])
month_year_router = APIRouter(prefix="/month_year", tags=["month_year"])


@account_router.post("/get_or_create", response_model=AccountNameResponse)
async def get_or_create_account(
    account_name_request: AccountNameRequest, account_service: AccountService = Depends(get_accounts_service)
) -> AccountNameResponse:
    """Create or retrieve an account with the given name."""
    account = await account_service.get_or_create_account(account_name=account_name_request.account_name)

    return AccountNameResponse(id=account.id, account_name=account.account_name)


@account_router.get("/list", response_model=list[AccountNameResponse])
async def get_all_accounts(
    account_service: AccountService = Depends(get_accounts_service),
) -> list[AccountNameResponse]:
    """Retrieve all accounts."""
    accounts = await account_service.get_all_accounts()

    return [AccountNameResponse(id=acc.id, account_name=acc.account_name) for acc in accounts]


@account_router.get(
    "/{account_id}",
    response_model=AccountNameResponse,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": HTTPErrorResponse,
            "description": "Account not found",
        }
    },
)
async def get_account_by_id(
    account_id: str, account_service: AccountService = Depends(get_accounts_service)
) -> AccountNameResponse:
    """Retrieve an account by its ID."""
    try:
        account = await account_service.get_account_by_id(account_id=account_id)
    except AccountNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error.message,
        ) from error

    return AccountNameResponse(id=account.id, account_name=account.account_name)


@account_router.put(
    "/{account_id}",
    response_model=AccountNameResponse,
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
) -> AccountNameResponse:
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

    return AccountNameResponse(id=account.id, account_name=account.account_name)


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


@month_year_router.post("/get_or_create", response_model=MonthYearResponse)
async def get_or_create_month_year(
    month_year_request: MonthYearRequest, account_service: AccountService = Depends(get_accounts_service)
) -> MonthYearResponse:
    """Retrieve an existing MonthYear or create a new one with the provided month and year."""
    month_year = await account_service.get_or_create_month_year(
        month=month_year_request.month, year=month_year_request.year
    )

    return MonthYearResponse(id=month_year.id, month=month_year.month, year=month_year.year)


@month_year_router.get("/list", response_model=list[MonthYearResponse])
async def get_all_month_years(
    account_service: AccountService = Depends(get_accounts_service),
) -> list[MonthYearResponse]:
    """Retrieve all MonthYears."""
    month_years = await account_service.get_all_month_years()

    return [MonthYearResponse(id=my.id, month=my.month, year=my.year) for my in month_years]


@month_year_router.get(
    "/{month_year_id}",
    response_model=MonthYearResponse,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": HTTPErrorResponse,
            "description": "MonthYear not found",
        }
    },
)
async def get_month_year_by_id(
    month_year_id: str, account_service: AccountService = Depends(get_accounts_service)
) -> MonthYearResponse:
    """Retrieve a MonthYear by its ID."""
    try:
        month_year = await account_service.get_month_year_by_id(month_year_id=month_year_id)
    except MonthYearNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error.message,
        ) from error

    return MonthYearResponse(id=month_year.id, month=month_year.month, year=month_year.year)


@month_year_router.put(
    "/{month_year_id}",
    response_model=MonthYearResponse,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": HTTPErrorResponse,
            "description": "MonthYear not found",
        }
    },
)
async def update_month_year(
    month_year_id: str,
    month_year_update_request: MonthYearRequest,
    account_service: AccountService = Depends(get_accounts_service),
) -> MonthYearResponse:
    """Update an existing MonthYear with the provided data."""
    try:
        month_year = await account_service.update_month_year(
            month_year_id=month_year_id, month=month_year_update_request.month, year=month_year_update_request.year
        )
    except MonthYearNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error.message,
        ) from error

    return MonthYearResponse(id=month_year.id, month=month_year.month, year=month_year.year)


@month_year_router.delete(
    "/{month_year_id}",
    responses={
        status.HTTP_404_NOT_FOUND: {
            "model": HTTPErrorResponse,
            "description": "MonthYear not found",
        }
    },
)
async def delete_month_year(
    month_year_id: str, account_service: AccountService = Depends(get_accounts_service)
) -> None:
    """Delete a MonthYear by its ID."""
    try:
        await account_service.delete_month_year(month_year_id=month_year_id)
    except MonthYearNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error.message,
        ) from error
