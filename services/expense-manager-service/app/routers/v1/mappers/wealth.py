"""Mappers for converting wealth use cases to schemas."""

from app.routers.v1.schemas.wealth import (
    HistoricalNetWorthPointResponse,
    WealthAllocationResponse,
    WealthCategoryAllocationResponse,
    WealthSummaryResponse,
)
from app.use_cases.models.wealth import (
    HistoricalNetWorthPoint,
    WealthAllocation,
    WealthSummary,
)


class WealthSummaryResponseMapper:
    """Mapper for wealth summaries."""

    @staticmethod
    def to_response_model(model: WealthSummary) -> WealthSummaryResponse:
        """Convert wealth summary to response model."""
        return WealthSummaryResponse(
            total_assets=model.total_assets,
            total_invested_assets=model.total_invested_assets,
            total_returns_assets=model.total_returns_assets,
            percentage_returns_assets=model.percentage_returns_assets,
            total_liabilities=model.total_liabilities,
            total_original_liabilities=model.total_original_liabilities,
            total_repaid_liabilities=model.total_repaid_liabilities,
            accumulated_interest_liabilities=model.accumulated_interest_liabilities,
            net_worth=model.net_worth,
        )


class HistoricalNetWorthResponseMapper:
    """Mapper for historical net worth points."""

    @staticmethod
    def to_response_model(model: HistoricalNetWorthPoint) -> HistoricalNetWorthPointResponse:
        """Convert historical point to response model."""
        return HistoricalNetWorthPointResponse(
            date=model.date,
            total_assets=model.total_assets,
            total_liabilities=model.total_liabilities,
            net_worth=model.net_worth,
        )


class WealthAllocationResponseMapper:
    """Mapper for wealth allocations."""

    @staticmethod
    def to_response_model(model: WealthAllocation) -> WealthAllocationResponse:
        """Convert wealth allocation to response model."""
        assets = [
            WealthCategoryAllocationResponse(
                category_name=c.category_name,
                category_code=c.category_code,
                total_value=c.total_value,
                percentage=c.percentage,
            )
            for c in model.assets
        ]
        liabilities = [
            WealthCategoryAllocationResponse(
                category_name=c.category_name,
                category_code=c.category_code,
                total_value=c.total_value,
                percentage=c.percentage,
            )
            for c in model.liabilities
        ]
        return WealthAllocationResponse(
            assets=assets,
            liabilities=liabilities,
            total_assets_value=model.total_assets_value,
            total_liabilities_value=model.total_liabilities_value,
            debt_to_asset_ratio=model.debt_to_asset_ratio,
            liquidity_ratio=model.liquidity_ratio,
            equity_financed_pct=model.equity_financed_pct,
            liabilities_financed_pct=model.liabilities_financed_pct,
            leverage_status_label=model.leverage_status_label,
            leverage_status_type=model.leverage_status_type,
            liquidity_status_label=model.liquidity_status_label,
            liquidity_status_type=model.liquidity_status_type,
        )
