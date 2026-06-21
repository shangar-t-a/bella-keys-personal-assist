"""Endpoints for liability management operations."""

from fastapi import APIRouter, Depends, HTTPException, status

from app.routers.v1.mappers.liability import (
    LiabilityCategoryResponseMapper,
    LiabilityCreateMapper,
    LiabilityProjectionsMapper,
    LiabilityResponseMapper,
    LiabilitySummaryResponseMapper,
    LiabilityTransactionCreateMapper,
    LiabilityTransactionResponseMapper,
    LiabilityUpdateMapper,
)
from app.routers.v1.schemas.liability import (
    LiabilityCategoryResponse,
    LiabilityProjectionsResponse,
    LiabilityRequest,
    LiabilityResponse,
    LiabilitySummaryResponse,
    LiabilityTransactionRequest,
    LiabilityTransactionResponse,
    LiabilityUpdateRequest,
)
from app.routers.v1.services import get_liability_service
from app.use_cases.liability import LiabilityService

router = APIRouter(prefix="/liabilities", tags=["liabilities"])


@router.get("/categories", response_model=list[LiabilityCategoryResponse])
async def get_all_categories(
    liability_service: LiabilityService = Depends(get_liability_service),
) -> list[LiabilityCategoryResponse]:
    """Retrieve list of all pre-seeded categories."""
    categories = await liability_service.get_all_categories()
    return [LiabilityCategoryResponseMapper.to_response_model(c) for c in categories]


@router.post("", response_model=LiabilityResponse, status_code=status.HTTP_201_CREATED)
async def create_liability(
    request: LiabilityRequest,
    liability_service: LiabilityService = Depends(get_liability_service),
) -> LiabilityResponse:
    """Create a new liability and log its initial balance transaction."""
    try:
        dto = LiabilityCreateMapper.to_use_case_model(request)
        liability_with_calc = await liability_service.create_liability(dto)
        return LiabilityResponseMapper.to_response_model(liability_with_calc)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.get("", response_model=list[LiabilityResponse])
async def list_liabilities(
    category_id: str | None = None,
    search: str | None = None,
    liability_service: LiabilityService = Depends(get_liability_service),
) -> list[LiabilityResponse]:
    """Retrieve list of liabilities, optionally filtered by category or search term."""
    liabilities = await liability_service.list_liabilities(category_id=category_id, search=search)
    return [LiabilityResponseMapper.to_response_model(liab) for liab in liabilities]


@router.get("/summary", response_model=LiabilitySummaryResponse)
async def get_liability_summary(
    liability_service: LiabilityService = Depends(get_liability_service),
) -> LiabilitySummaryResponse:
    """Get aggregate liabilities calculations and category breakdowns."""
    summary = await liability_service.get_liability_summary()
    return LiabilitySummaryResponseMapper.to_response_model(summary)


@router.get("/{id}", response_model=LiabilityResponse)
async def get_liability_by_id(
    id: str,
    liability_service: LiabilityService = Depends(get_liability_service),
) -> LiabilityResponse:
    """Retrieve details of a single liability by its ID."""
    try:
        liability_with_calc = await liability_service.get_liability_by_id(id)
        return LiabilityResponseMapper.to_response_model(liability_with_calc)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e


@router.put("/{id}", response_model=LiabilityResponse)
async def update_liability(
    id: str,
    request: LiabilityUpdateRequest,
    liability_service: LiabilityService = Depends(get_liability_service),
) -> LiabilityResponse:
    """Update metadata fields of an existing liability."""
    try:
        dto = LiabilityUpdateMapper.to_use_case_model(request)
        liability_with_calc = await liability_service.update_liability(id, dto)
        return LiabilityResponseMapper.to_response_model(liability_with_calc)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_liability(
    id: str,
    liability_service: LiabilityService = Depends(get_liability_service),
) -> None:
    """Delete a liability and all its historical transactions."""
    try:
        await liability_service.delete_liability(id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e


@router.get("/{id}/transactions", response_model=list[LiabilityTransactionResponse])
async def get_transactions_for_liability(
    id: str,
    liability_service: LiabilityService = Depends(get_liability_service),
) -> list[LiabilityTransactionResponse]:
    """Retrieve the transaction history ledger for a specific liability."""
    txs = await liability_service.get_transactions_for_liability(id)
    return [LiabilityTransactionResponseMapper.to_response_model(t) for t in txs]


@router.post("/{id}/transactions", response_model=LiabilityTransactionResponse, status_code=status.HTTP_201_CREATED)
async def add_transaction(
    id: str,
    request: LiabilityTransactionRequest,
    liability_service: LiabilityService = Depends(get_liability_service),
) -> LiabilityTransactionResponse:
    """Add a new borrow, repay, or revaluation transaction to the liability's ledger."""
    try:
        dto = LiabilityTransactionCreateMapper.to_use_case_model(request)
        tx = await liability_service.add_transaction(id, dto)
        return LiabilityTransactionResponseMapper.to_response_model(tx)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e


@router.delete("/transactions/{tx_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(
    tx_id: str,
    liability_service: LiabilityService = Depends(get_liability_service),
) -> None:
    """Delete a transaction from the ledger and trigger parent outstanding recalculation."""
    try:
        await liability_service.delete_transaction(tx_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e


@router.get("/{id}/projections", response_model=LiabilityProjectionsResponse)
async def get_liability_projections(
    id: str,
    liability_service: LiabilityService = Depends(get_liability_service),
) -> LiabilityProjectionsResponse:
    """Retrieve ideal and actual amortization projection curves and payoff metrics."""
    try:
        projections = await liability_service.get_liability_projections(id)
        return LiabilityProjectionsMapper.to_response_model(projections)
    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e),
            ) from e
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
