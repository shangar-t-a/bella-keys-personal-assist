"""Use case models for Wealth/Portfolio analytics."""

from app.use_cases.models.base import BaseInput


class WealthSummary(BaseInput):
    """Model for high-level current wealth aggregation."""

    total_assets: float
    total_invested_assets: float
    total_returns_assets: float
    percentage_returns_assets: float
    total_liabilities: float
    total_original_liabilities: float
    total_repaid_liabilities: float
    accumulated_interest_liabilities: float
    net_worth: float


class HistoricalNetWorthPoint(BaseInput):
    """Model for monthly historical net worth timeline point."""

    date: str  # Format: YYYY-MM
    total_assets: float
    total_liabilities: float
    net_worth: float


class WealthCategoryAllocation(BaseInput):
    """Model for allocation breakdown by category."""

    category_name: str
    category_code: str
    total_value: float
    percentage: float


class WealthAllocation(BaseInput):
    """Model for complete portfolio allocation breakdown."""

    assets: list[WealthCategoryAllocation]
    liabilities: list[WealthCategoryAllocation]
    total_assets_value: float
    total_liabilities_value: float
    debt_to_asset_ratio: float
    liquidity_ratio: float
    equity_financed_pct: float
    liabilities_financed_pct: float
    leverage_status_label: str
    leverage_status_type: str
    liquidity_status_label: str
    liquidity_status_type: str
