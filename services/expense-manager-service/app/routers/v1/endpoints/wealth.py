"""Endpoints for wealth and portfolio analytics operations."""

from fastapi import APIRouter, Depends

from app.routers.v1.mappers.wealth import (
    HistoricalNetWorthResponseMapper,
    WealthAllocationResponseMapper,
    WealthSummaryResponseMapper,
)
from app.routers.v1.schemas.wealth import (
    HistoricalNetWorthPointResponse,
    WealthAllocationResponse,
    WealthSummaryResponse,
)
from app.routers.v1.services import get_wealth_service
from app.use_cases.wealth import WealthService

router = APIRouter(prefix="/wealth", tags=["wealth"])


@router.get("/summary", response_model=WealthSummaryResponse)
async def get_wealth_summary(
    wealth_service: WealthService = Depends(get_wealth_service),
) -> WealthSummaryResponse:
    """Retrieve current wealth summary (total assets, liabilities, and net worth)."""
    summary = await wealth_service.get_wealth_summary()
    return WealthSummaryResponseMapper.to_response_model(summary)


@router.get("/history", response_model=list[HistoricalNetWorthPointResponse])
async def get_historical_net_worth(
    months: int = 12,
    wealth_service: WealthService = Depends(get_wealth_service),
) -> list[HistoricalNetWorthPointResponse]:
    """Retrieve historical net worth trend for the past N months."""
    history = await wealth_service.get_historical_net_worth(months=months)
    return [HistoricalNetWorthResponseMapper.to_response_model(p) for p in history]


@router.get("/allocation", response_model=WealthAllocationResponse)
async def get_wealth_allocation(
    wealth_service: WealthService = Depends(get_wealth_service),
) -> WealthAllocationResponse:
    """Retrieve asset and liability category allocation percentages."""
    allocation = await wealth_service.get_portfolio_allocation()
    return WealthAllocationResponseMapper.to_response_model(allocation)
