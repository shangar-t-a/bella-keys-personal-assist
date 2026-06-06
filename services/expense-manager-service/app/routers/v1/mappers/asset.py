"""Mappers for converting schemas to use cases and vice versa."""

from datetime import UTC, datetime

from app.entities.models.asset import (
    AssetCategory,
    AssetSubcategory,
    AssetTransaction,
)
from app.routers.v1.schemas.asset import (
    AssetCategoryResponse,
    AssetCategorySummaryResponse,
    AssetRequest,
    AssetResponse,
    AssetSubcategoryResponse,
    AssetSummaryResponse,
    AssetTransactionRequest,
    AssetTransactionResponse,
    AssetUpdateRequest,
)
from app.use_cases.models.asset import (
    AssetCategorySummary,
    AssetCreate,
    AssetInterestDetails,
    AssetSummary,
    AssetTransactionCreate,
    AssetUnitDetails,
    AssetUpdate,
    AssetWithCalc,
)


class AssetCreateMapper:
    """Mapper for creating assets."""

    @staticmethod
    def to_use_case_model(request: AssetRequest) -> AssetCreate:
        """Convert request payload to use case create model."""
        interest_details = None
        if request.interest_details:
            interest_details = AssetInterestDetails(
                interest_rate=request.interest_details.interest_rate,
                compounding=request.interest_details.compounding,
                maturity_date=request.interest_details.maturity_date,
            )

        unit_details = None
        if request.unit_details:
            unit_details = AssetUnitDetails(
                units=request.unit_details.units,
                price_per_unit=request.unit_details.price_per_unit,
            )

        return AssetCreate(
            category_id=request.category_id,
            name=request.name,
            subcategory_id=request.subcategory_id,
            initial_amount=request.initial_amount,
            unit_details=unit_details,
            interest_details=interest_details,
            notes=request.notes,
        )


class AssetUpdateMapper:
    """Mapper for updating assets."""

    @staticmethod
    def to_use_case_model(request: AssetUpdateRequest) -> AssetUpdate:
        """Convert request payload to use case update model."""
        interest_details = None
        if request.interest_details:
            interest_details = AssetInterestDetails(
                interest_rate=request.interest_details.interest_rate,
                compounding=request.interest_details.compounding,
                maturity_date=request.interest_details.maturity_date,
            )

        return AssetUpdate(
            category_id=request.category_id,
            name=request.name,
            subcategory_id=request.subcategory_id,
            interest_details=interest_details,
            notes=request.notes,
        )


class AssetTransactionCreateMapper:
    """Mapper for creating asset transactions."""

    @staticmethod
    def to_use_case_model(request: AssetTransactionRequest) -> AssetTransactionCreate:
        """Convert request payload to use case transaction create model."""
        unit_details = None
        if request.unit_details:
            unit_details = AssetUnitDetails(
                units=request.unit_details.units,
                price_per_unit=request.unit_details.price_per_unit,
            )

        return AssetTransactionCreate(
            transaction_type=request.transaction_type,
            amount=request.amount,
            unit_details=unit_details,
            transaction_date=request.transaction_date or datetime.now(UTC),
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
            subcategory_id=asset.subcategory_id,
            invested_value=asset.invested_value,
            current_value=asset.current_value,
            interest_rate=asset.interest_rate,
            interest_compounding=asset.interest_compounding,
            maturity_date=asset.maturity_date,
            notes=asset.notes,
            absolute_returns=asset.absolute_returns,
            percentage_returns=asset.percentage_returns,
            created_at=asset.created_at,
            updated_at=asset.updated_at,
        )


class AssetCategoryResponseMapper:
    """Mapper for category list response conversion."""

    @staticmethod
    def _to_subcategory_response(sub: AssetSubcategory) -> AssetSubcategoryResponse:
        """Map domain subcategory model to response model."""
        return AssetSubcategoryResponse(
            id=sub.id,
            category_id=sub.category_id,
            name=sub.name,
            code=sub.code,
            description=sub.description,
            valuation_type=sub.valuation_type,
            has_interest=sub.has_interest,
            has_maturity=sub.has_maturity,
        )

    @staticmethod
    def to_response_model(category: AssetCategory) -> AssetCategoryResponse:
        """Map domain category model to response model."""
        subcategories = [
            AssetCategoryResponseMapper._to_subcategory_response(sub)
            for sub in category.subcategories
        ]
        return AssetCategoryResponse(
            id=category.id,
            name=category.name,
            code=category.code,
            description=category.description,
            subcategories=subcategories,
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
