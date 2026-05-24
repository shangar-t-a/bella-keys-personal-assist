"""Router for savings buckets and transactions endpoints."""


from fastapi import APIRouter, Depends, HTTPException, status

from app.routers.v1.schemas.savings_bucket import (
    SavingsBucketCreateRequest,
    SavingsBucketResponse,
    SavingsBucketTransactionCreateRequest,
    SavingsBucketTransactionResponse,
    SavingsBucketTransactionsPageResponse,
    SavingsBucketUpdateRequest,
)
from app.routers.v1.services import get_savings_bucket_service
from app.use_cases.errors.savings_bucket import (
    SavingsBucketDuplicateNameError,
    SavingsBucketInsufficientFundsError,
    SavingsBucketNotFoundError,
    SavingsBucketProtectedError,
)
from app.use_cases.savings_bucket import SavingsBucketService

router = APIRouter(prefix="/savings_buckets", tags=["savings_buckets"])


@router.get("/list/{account_id}", response_model=list[SavingsBucketResponse])
async def get_buckets(
    account_id: str,
    service: SavingsBucketService = Depends(get_savings_bucket_service),
) -> list[SavingsBucketResponse]:
    """Retrieve all savings buckets for a given account. Auto-seeds defaults if empty."""
    buckets = await service.get_buckets_for_account(account_id=account_id)
    return [
        SavingsBucketResponse(
            id=b.id,
            account_id=b.account_id,
            name=b.name,
            allocated_amount=b.allocated_amount,
            target_amount=b.target_amount,
        )
        for b in buckets
    ]


@router.post("/{account_id}/bucket", response_model=SavingsBucketResponse, status_code=status.HTTP_201_CREATED)
async def create_bucket(
    account_id: str,
    request: SavingsBucketCreateRequest,
    service: SavingsBucketService = Depends(get_savings_bucket_service),
) -> SavingsBucketResponse:
    """Create a new savings bucket for an account."""
    try:
        b = await service.create_bucket(account_id=account_id, name=request.name, target_amount=request.target_amount)
        return SavingsBucketResponse(
            id=b.id,
            account_id=b.account_id,
            name=b.name,
            allocated_amount=b.allocated_amount,
            target_amount=b.target_amount,
        )
    except SavingsBucketDuplicateNameError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error.message) from error


@router.put("/bucket/{bucket_id}", response_model=SavingsBucketResponse)
async def update_bucket(
    bucket_id: str,
    request: SavingsBucketUpdateRequest,
    service: SavingsBucketService = Depends(get_savings_bucket_service),
) -> SavingsBucketResponse:
    """Update an existing savings bucket's details."""
    try:
        b = await service.edit_bucket(bucket_id=bucket_id, name=request.name, target_amount=request.target_amount)
        return SavingsBucketResponse(
            id=b.id,
            account_id=b.account_id,
            name=b.name,
            allocated_amount=b.allocated_amount,
            target_amount=b.target_amount,
        )
    except SavingsBucketNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error.message) from error
    except SavingsBucketDuplicateNameError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error.message) from error
    except SavingsBucketProtectedError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error.message) from error


@router.delete("/bucket/{bucket_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_bucket(
    bucket_id: str,
    service: SavingsBucketService = Depends(get_savings_bucket_service),
) -> None:
    """Delete a savings bucket, safely returning any remaining funds to root Savings."""
    try:
        await service.delete_bucket(bucket_id=bucket_id)
    except SavingsBucketNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error.message) from error
    except SavingsBucketProtectedError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error.message) from error


@router.post(
    "/{account_id}/transaction",
    response_model=SavingsBucketTransactionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_transaction(
    account_id: str,
    request: SavingsBucketTransactionCreateRequest,
    service: SavingsBucketService = Depends(get_savings_bucket_service),
) -> SavingsBucketTransactionResponse:
    """Create a transaction to deposit, withdraw, allocate, release or transfer savings funds."""
    try:
        tx = await service.add_transaction(
            account_id=account_id,
            source_bucket_id=request.source_bucket_id,
            destination_bucket_id=request.destination_bucket_id,
            amount=request.amount,
            transaction_type=request.transaction_type,
            description=request.description,
            transaction_date=request.transaction_date,
        )
        return SavingsBucketTransactionResponse(
            id=tx.id,
            account_id=tx.account_id,
            source_bucket_id=tx.source_bucket_id,
            destination_bucket_id=tx.destination_bucket_id,
            amount=tx.amount,
            transaction_type=tx.transaction_type,
            description=tx.description,
            transaction_date=tx.transaction_date,
        )
    except SavingsBucketNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error.message) from error
    except SavingsBucketInsufficientFundsError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error.message) from error
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error


@router.get("/{account_id}/transactions", response_model=SavingsBucketTransactionsPageResponse)
async def get_transactions(
    account_id: str,
    limit: int = 50,
    offset: int = 0,
    service: SavingsBucketService = Depends(get_savings_bucket_service),
) -> SavingsBucketTransactionsPageResponse:
    """Retrieve transaction history for a given savings account."""
    txs = await service.get_transactions_for_account(account_id=account_id, limit=limit, offset=offset)
    total = await service.get_transactions_count_for_account(account_id=account_id)
    return SavingsBucketTransactionsPageResponse(
        transactions=[
            SavingsBucketTransactionResponse(
                id=t.id,
                account_id=t.account_id,
                source_bucket_id=t.source_bucket_id,
                destination_bucket_id=t.destination_bucket_id,
                amount=t.amount,
                transaction_type=t.transaction_type,
                description=t.description,
                transaction_date=t.transaction_date,
            )
            for t in txs
        ],
        total_elements=total,
        limit=limit,
        offset=offset,
    )
