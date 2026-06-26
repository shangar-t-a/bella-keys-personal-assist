"""Schemas for wealth API endpoints."""

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class BaseSchema(BaseModel):
    """Base schema with camelCase settings."""

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
    )


class WealthSummaryResponse(BaseSchema):
    """Response schema for high-level current wealth aggregation."""

    total_assets: float
    total_invested_assets: float
    total_returns_assets: float
    percentage_returns_assets: float
    total_liabilities: float
    total_original_liabilities: float
    total_repaid_liabilities: float
    accumulated_interest_liabilities: float
    net_worth: float


class HistoricalNetWorthPointResponse(BaseSchema):
    """Response schema for monthly historical net worth timeline point."""

    date: str
    total_assets: float
    total_liabilities: float
    net_worth: float


class WealthCategoryAllocationResponse(BaseSchema):
    """Response schema for allocation breakdown by category."""

    category_name: str
    category_code: str
    total_value: float
    percentage: float


class WealthAllocationResponse(BaseSchema):
    """Response schema for complete portfolio allocation breakdown."""

    assets: list[WealthCategoryAllocationResponse]
    liabilities: list[WealthCategoryAllocationResponse]
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
