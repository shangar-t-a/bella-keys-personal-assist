"""Mappers for converting schemas to use cases and vice versa for liabilities."""

from datetime import UTC, datetime

from app.entities.models.liability import (
    LiabilityCategory,
    LiabilitySubcategory,
    LiabilityTransaction,
)
from app.routers.v1.schemas.liability import (
    LiabilityCategoryResponse,
    LiabilityCategorySummaryResponse,
    LiabilityProjectionMetricsResponse,
    LiabilityProjectionPointResponse,
    LiabilityProjectionsResponse,
    LiabilityRequest,
    LiabilityResponse,
    LiabilitySubcategoryResponse,
    LiabilitySummaryResponse,
    LiabilityTransactionRequest,
    LiabilityTransactionResponse,
    LiabilityUpdateRequest,
)
from app.use_cases.models.liability import (
    LiabilityCategorySummary,
    LiabilityCreate,
    LiabilityInterestDetails,
    LiabilityProjections,
    LiabilitySummary,
    LiabilityTransactionCreate,
    LiabilityUpdate,
    LiabilityWithCalc,
)


class LiabilityCreateMapper:
    """Mapper for creating liabilities."""

    @staticmethod
    def to_use_case_model(request: LiabilityRequest) -> LiabilityCreate:
        """Convert request payload to use case create model."""
        interest_details = None
        if request.interest_details:
            interest_details = LiabilityInterestDetails(
                interest_rate=request.interest_details.interest_rate,
                compounding=request.interest_details.compounding,
                emi_amount=request.interest_details.emi_amount,
                emi_start_date=request.interest_details.emi_start_date,
                maturity_date=request.interest_details.maturity_date,
            )

        return LiabilityCreate(
            category_id=request.category_id,
            name=request.name,
            subcategory_id=request.subcategory_id,
            initial_amount=request.initial_amount,
            initial_date=request.initial_date,
            interest_details=interest_details,
            notes=request.notes,
        )


class LiabilityUpdateMapper:
    """Mapper for updating liabilities."""

    @staticmethod
    def to_use_case_model(request: LiabilityUpdateRequest) -> LiabilityUpdate:
        """Convert request payload to use case update model."""
        interest_details = None
        if request.interest_details:
            interest_details = LiabilityInterestDetails(
                interest_rate=request.interest_details.interest_rate,
                compounding=request.interest_details.compounding,
                emi_amount=request.interest_details.emi_amount,
                emi_start_date=request.interest_details.emi_start_date,
                maturity_date=request.interest_details.maturity_date,
            )

        return LiabilityUpdate(
            category_id=request.category_id,
            name=request.name,
            subcategory_id=request.subcategory_id,
            interest_details=interest_details,
            notes=request.notes,
        )


class LiabilityTransactionCreateMapper:
    """Mapper for creating liability transactions."""

    @staticmethod
    def to_use_case_model(request: LiabilityTransactionRequest) -> LiabilityTransactionCreate:
        """Convert request payload to use case transaction create model."""
        return LiabilityTransactionCreate(
            transaction_type=request.transaction_type,
            amount=request.amount,
            transaction_date=request.transaction_date or datetime.now(UTC),
            description=request.description,
        )


class LiabilityResponseMapper:
    """Mapper for liability response conversion."""

    @staticmethod
    def to_response_model(liability: LiabilityWithCalc) -> LiabilityResponse:
        """Map use case calc model to HTTP response model."""
        return LiabilityResponse(
            id=liability.id,
            category_id=liability.category_id,
            category_name=liability.category_name,
            category_code=liability.category_code,
            name=liability.name,
            subcategory_id=liability.subcategory_id,
            original_value=liability.original_value,
            current_value=liability.current_value,
            interest_rate=liability.interest_rate,
            interest_compounding=liability.interest_compounding,
            emi_amount=liability.emi_amount,
            emi_start_date=liability.emi_start_date,
            maturity_date=liability.maturity_date,
            notes=liability.notes,
            total_repaid=liability.total_repaid,
            accumulated_interest=liability.accumulated_interest,
            progress_pct=liability.progress_pct,
            created_at=liability.created_at,
            updated_at=liability.updated_at,
        )


class LiabilityCategoryResponseMapper:
    """Mapper for category list response conversion."""

    @staticmethod
    def _to_subcategory_response(sub: LiabilitySubcategory) -> LiabilitySubcategoryResponse:
        """Map domain subcategory model to response model."""
        return LiabilitySubcategoryResponse(
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
    def to_response_model(category: LiabilityCategory) -> LiabilityCategoryResponse:
        """Map domain category model to response model."""
        subcategories = [
            LiabilityCategoryResponseMapper._to_subcategory_response(sub) for sub in category.subcategories
        ]
        return LiabilityCategoryResponse(
            id=category.id,
            name=category.name,
            code=category.code,
            description=category.description,
            subcategories=subcategories,
        )


class LiabilityTransactionResponseMapper:
    """Mapper for transaction list response conversion."""

    @staticmethod
    def to_response_model(tx: LiabilityTransaction) -> LiabilityTransactionResponse:
        """Map transaction model to response model."""
        return LiabilityTransactionResponse(
            id=tx.id,
            liability_id=tx.liability_id,
            transaction_type=tx.transaction_type,
            amount=tx.amount,
            transaction_date=tx.transaction_date,
            description=tx.description,
        )


class LiabilitySummaryResponseMapper:
    """Mapper for liability aggregation dashboard summary conversion."""

    @staticmethod
    def _to_category_summary_response(
        cat_summary: LiabilityCategorySummary,
    ) -> LiabilityCategorySummaryResponse:
        return LiabilityCategorySummaryResponse(
            category_id=cat_summary.category_id,
            category_name=cat_summary.category_name,
            category_code=cat_summary.category_code,
            total_original=cat_summary.total_original,
            total_outstanding=cat_summary.total_outstanding,
            total_repaid=cat_summary.total_repaid,
            accumulated_interest=cat_summary.accumulated_interest,
        )

    @classmethod
    def to_response_model(cls, summary: LiabilitySummary) -> LiabilitySummaryResponse:
        """Map use case summary model to dashboard response model."""
        return LiabilitySummaryResponse(
            total_original=summary.total_original,
            total_outstanding=summary.total_outstanding,
            total_repaid=summary.total_repaid,
            accumulated_interest=summary.accumulated_interest,
            category_breakdowns=[cls._to_category_summary_response(cb) for cb in summary.category_breakdowns],
        )


class LiabilityProjectionsMapper:
    """Mapper for converting liability projections to API response models."""

    @staticmethod
    def to_response_model(proj: LiabilityProjections) -> LiabilityProjectionsResponse:
        """Convert a LiabilityProjections use case model to API response model."""
        points = [
            LiabilityProjectionPointResponse(
                date=pt.date,
                ideal_balance=pt.ideal_balance,
                actual_balance=pt.actual_balance,
                ideal_interest_paid=pt.ideal_interest_paid,
                actual_interest_paid=pt.actual_interest_paid,
            )
            for pt in proj.projection_points
        ]

        metrics = LiabilityProjectionMetricsResponse(
            ideal_tenure_months=proj.metrics.ideal_tenure_months,
            remaining_tenure_months=proj.metrics.remaining_tenure_months,
            tenure_saved_months=proj.metrics.tenure_saved_months,
            total_interest_ideal=proj.metrics.total_interest_ideal,
            total_interest_projected=proj.metrics.total_interest_projected,
            interest_saved=proj.metrics.interest_saved,
            ideal_end_date=proj.metrics.ideal_end_date,
            projected_end_date=proj.metrics.projected_end_date,
        )

        return LiabilityProjectionsResponse(metrics=metrics, projection_points=points)
