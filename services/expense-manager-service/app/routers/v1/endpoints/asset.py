"""Endpoints for asset management operations."""

from fastapi import APIRouter, Depends, HTTPException, status

from app.routers.v1.mappers.asset import (
    AssetCategoryResponseMapper,
    AssetCreateMapper,
    AssetResponseMapper,
    AssetSummaryResponseMapper,
    AssetTransactionCreateMapper,
    AssetTransactionResponseMapper,
    AssetUpdateMapper,
)
from app.routers.v1.schemas.asset import (
    AssetCategoryResponse,
    AssetRequest,
    AssetResponse,
    AssetSummaryResponse,
    AssetTransactionRequest,
    AssetTransactionResponse,
    AssetUpdateRequest,
)
from app.routers.v1.services import get_asset_service
from app.use_cases.asset import AssetService

router = APIRouter(prefix="/assets", tags=["assets"])


@router.get("/categories", response_model=list[AssetCategoryResponse])
async def get_all_categories(
    asset_service: AssetService = Depends(get_asset_service),
) -> list[AssetCategoryResponse]:
    """Retrieve list of all pre-seeded categories."""
    categories = await asset_service.get_all_categories()
    return [AssetCategoryResponseMapper.to_response_model(c) for c in categories]


@router.post("", response_model=AssetResponse, status_code=status.HTTP_201_CREATED)
async def create_asset(
    request: AssetRequest,
    asset_service: AssetService = Depends(get_asset_service),
) -> AssetResponse:
    """Create a new asset and log its initial balance transaction."""
    try:
        dto = AssetCreateMapper.to_use_case_model(request)
        asset_with_calc = await asset_service.create_asset(dto)
        return AssetResponseMapper.to_response_model(asset_with_calc)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.get("", response_model=list[AssetResponse])
async def list_assets(
    category_id: str | None = None,
    search: str | None = None,
    asset_service: AssetService = Depends(get_asset_service),
) -> list[AssetResponse]:
    """Retrieve list of assets, optionally filtered by category or search term."""
    assets = await asset_service.list_assets(category_id=category_id, search=search)
    return [AssetResponseMapper.to_response_model(a) for a in assets]


@router.get("/summary", response_model=AssetSummaryResponse)
async def get_asset_summary(
    asset_service: AssetService = Depends(get_asset_service),
) -> AssetSummaryResponse:
    """Get aggregate wealth calculations and category breakdowns."""
    summary = await asset_service.get_asset_summary()
    return AssetSummaryResponseMapper.to_response_model(summary)


@router.get("/{id}", response_model=AssetResponse)
async def get_asset_by_id(
    id: str,
    asset_service: AssetService = Depends(get_asset_service),
) -> AssetResponse:
    """Retrieve details of a single asset by its ID."""
    try:
        asset_with_calc = await asset_service.get_asset_by_id(id)
        return AssetResponseMapper.to_response_model(asset_with_calc)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e


@router.put("/{id}", response_model=AssetResponse)
async def update_asset(
    id: str,
    request: AssetUpdateRequest,
    asset_service: AssetService = Depends(get_asset_service),
) -> AssetResponse:
    """Update metadata fields of an existing asset."""
    try:
        dto = AssetUpdateMapper.to_use_case_model(request)
        asset_with_calc = await asset_service.update_asset(id, dto)
        return AssetResponseMapper.to_response_model(asset_with_calc)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_asset(
    id: str,
    asset_service: AssetService = Depends(get_asset_service),
) -> None:
    """Delete an asset and all its historical transactions."""
    try:
        await asset_service.delete_asset(id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e


@router.get("/{id}/transactions", response_model=list[AssetTransactionResponse])
async def get_transactions_for_asset(
    id: str,
    asset_service: AssetService = Depends(get_asset_service),
) -> list[AssetTransactionResponse]:
    """Retrieve the transaction history ledger for a specific asset."""
    txs = await asset_service.get_transactions_for_asset(id)
    return [AssetTransactionResponseMapper.to_response_model(t) for t in txs]


@router.post("/{id}/transactions", response_model=AssetTransactionResponse, status_code=status.HTTP_201_CREATED)
async def add_transaction(
    id: str,
    request: AssetTransactionRequest,
    asset_service: AssetService = Depends(get_asset_service),
) -> AssetTransactionResponse:
    """Add a new buy, sell, or revaluation transaction to the asset's ledger."""
    try:
        dto = AssetTransactionCreateMapper.to_use_case_model(request)
        tx = await asset_service.add_transaction(id, dto)
        return AssetTransactionResponseMapper.to_response_model(tx)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e


@router.delete("/transactions/{tx_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(
    tx_id: str,
    asset_service: AssetService = Depends(get_asset_service),
) -> None:
    """Delete a transaction from the ledger and trigger parent valuation recalculation."""
    try:
        await asset_service.delete_transaction(tx_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e
