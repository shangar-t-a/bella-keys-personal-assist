"""Mappers for spending entry."""

from app.routers.v1.schemas.spending_entry import (
    SpendingEntryRequest,
    SpendingEntryWithCalcResponse,
)
from app.use_cases.models.spending_entry import (
    SpendingEntry,
    SpendingEntryCreate,
    SpendingEntryWithCalc,
)


class SpendingEntryCreateMapper:
    """Mapper for create spending account request to use case model."""

    @staticmethod
    def to_use_case_model(request: SpendingEntryRequest) -> SpendingEntryCreate:
        """Map the request model to the use case model."""
        return SpendingEntryCreate(
            account_name=request.account_name,
            month=request.month,
            year=request.year,
            starting_balance=request.starting_balance,
            current_balance=request.current_balance,
            current_credit=request.current_credit,
        )


class SpendingEntryMapper:
    """Mapper for spending account."""

    @staticmethod
    def to_use_case_model(entry_id: str, request: SpendingEntryRequest) -> SpendingEntry:
        """Map the use case model to the response model."""
        return SpendingEntry(
            id=entry_id,
            account_name=request.account_name,
            month=request.month,
            year=request.year,
            starting_balance=request.starting_balance,
            current_balance=request.current_balance,
            current_credit=request.current_credit,
        )


class SpendingEntryWithCalcMapper:
    """Mapper for spending account with calculated fields."""

    @staticmethod
    def to_response_model(
        entry: SpendingEntryWithCalc,
    ) -> SpendingEntryWithCalcResponse:
        """Map the use case model to the response model."""
        return SpendingEntryWithCalcResponse(
            id=entry.id,
            account_name=entry.account_name,
            month=entry.month,
            year=entry.year,
            starting_balance=entry.starting_balance,
            current_balance=entry.current_balance,
            current_credit=entry.current_credit,
            balance_after_credit=entry.balance_after_credit,
            total_spent=entry.total_spent,
        )
