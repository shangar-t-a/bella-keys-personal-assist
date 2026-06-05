"""Mappers for converting schemas to use cases and vice versa."""

from datetime import UTC, datetime

from app.entities.models.asset import AssetCategory, AssetTransaction
from app.routers.v1.schemas.asset import (
    AssetCategoryResponse,
    AssetCategorySummaryResponse,
    AssetRequest,
    AssetResponse,
    AssetSummaryResponse,
    AssetTransactionRequest,
    AssetTransactionResponse,
    AssetUpdateRequest,
)
from app.use_cases.models.asset import (
    AssetCategorySummary,
    AssetCreate,
    AssetSummary,
    AssetTransactionCreate,
    AssetUpdate,
    AssetWithCalc,
)


class AssetCreateMapper:
    """Mapper for creating assets."""

    @staticmethod
    def to_use_case_model(request: AssetRequest) -> AssetCreate:
        """Convert request payload to use case create model."""
        return AssetCreate(
            category_id=request.category_id,
            name=request.name,
            sub_category=request.sub_category,
            initial_amount=request.initial_amount,
            units=request.units,
            price_per_unit=request.price_per_unit,
            notes=request.notes,
        )


class AssetUpdateMapper:
    """Mapper for updating assets."""

    @staticmethod
    def to_use_case_model(request: AssetUpdateRequest) -> AssetUpdate:
        """Convert request payload to use case update model."""
        return AssetUpdate(
            category_id=request.category_id,
            name=request.name,
            sub_category=request.sub_category,
            notes=request.notes,
        )


class AssetTransactionCreateMapper:
    """Mapper for creating asset transactions."""

    @staticmethod
    def to_use_case_model(request: AssetTransactionRequest) -> AssetTransactionCreate:
        """Convert request payload to use case transaction create model."""
        tx_date = request.transaction_date or datetime.now(UTC)
        return AssetTransactionCreate(
            transaction_type=request.transaction_type.upper(),
            amount=request.amount,
            units=request.units,
            price_per_unit=request.price_per_unit,
            transaction_date=tx_date,
            description=request.description,
        )


class AssetResponseMapper:
    """Mapper for asset response conversion."""

    @staticmethod
    def to_response_model(asset: AssetWithCalc) -> AssetResponse:
        """Map use case calc model to HTTP response model."""
        return AssetResponse(
            id=asset.id,
            category_id=asset.category_id,
            category_name=asset.category_name,
            category_code=asset.category_code,
            name=asset.name,
            sub_category=asset.sub_category,
            invested_value=asset.invested_value,
            current_value=asset.current_value,
            notes=asset.notes,
            absolute_returns=asset.absolute_returns,
            percentage_returns=asset.percentage_returns,
            created_at=asset.created_at,
            updated_at=asset.updated_at,
        )


class AssetCategoryResponseMapper:
    """Mapper for category list response conversion."""

    @staticmethod
    def to_response_model(category: AssetCategory) -> AssetCategoryResponse:
        """Map domain category model to response model."""
        return AssetCategoryResponse(
            id=category.id,
            name=category.name,
            code=category.code,
            description=category.description,
        )


class AssetTransactionResponseMapper:
    """Mapper for transaction list response conversion."""

    @staticmethod
    def to_response_model(tx: AssetTransaction) -> AssetTransactionResponse:
        """Map transaction model to response model."""
        return AssetTransactionResponse(
            id=tx.id,
            asset_id=tx.asset_id,
            transaction_type=tx.transaction_type,
            amount=tx.amount,
            units=tx.units,
            price_per_unit=tx.price_per_unit,
            transaction_date=tx.transaction_date,
            description=tx.description,
        )


class AssetSummaryResponseMapper:
    """Mapper for asset aggregation dashboard summary conversion."""

    @staticmethod
    def _to_category_summary_response(
        cat_summary: AssetCategorySummary,
    ) -> AssetCategorySummaryResponse:
        return AssetCategorySummaryResponse(
            category_id=cat_summary.category_id,
            category_name=cat_summary.category_name,
            category_code=cat_summary.category_code,
            total_invested=cat_summary.total_invested,
            total_current=cat_summary.total_current,
            total_returns=cat_summary.total_returns,
            percentage_returns=cat_summary.percentage_returns,
        )

    @classmethod
    def to_response_model(cls, summary: AssetSummary) -> AssetSummaryResponse:
        """Map use case summary model to dashboard response model."""
        return AssetSummaryResponse(
            total_invested=summary.total_invested,
            total_current=summary.total_current,
            total_returns=summary.total_returns,
            percentage_returns=summary.percentage_returns,
            category_breakdowns=[cls._to_category_summary_response(cb) for cb in summary.category_breakdowns],
        )
