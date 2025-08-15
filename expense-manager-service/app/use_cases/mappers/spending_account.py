"""Mappers for spending account."""

from app.entities.models.accounts import (
    AccountName,
    MonthYear,
)
from app.entities.models.spending_account import (
    SpendingAccountEntry,
    SpendingAccountEntryWithCalculatedFields,
)
from app.use_cases.dto.spending_account import (
    SpendingAccountEntryDTO,
    SpendingAccountEntryWithCalculatedFieldsDTO,
)


class SpendingAccountEntryMapper:
    """Mapper for SpendingAccountEntry entity and SpendingAccountEntryDTO."""

    @staticmethod
    def to_entity(dto: SpendingAccountEntryDTO, account_id: str, date_detail_id: str) -> SpendingAccountEntry:
        """Convert SpendingAccountEntryDTO to SpendingAccountEntry entity."""
        return SpendingAccountEntry(
            account_id=account_id,
            date_detail_id=date_detail_id,
            starting_balance=dto.starting_balance,
            current_balance=dto.current_balance,
            current_credit=dto.current_credit,
        )

    @staticmethod
    def to_dto(
        entity: SpendingAccountEntry, account_name: AccountName, date_detail: MonthYear
    ) -> SpendingAccountEntryDTO:
        """Convert SpendingAccountEntry entity to SpendingAccountEntryDTO."""
        return SpendingAccountEntryDTO(
            id=entity.id,
            account_name=account_name.account_name,
            month=date_detail.month,
            year=date_detail.year,
            starting_balance=entity.starting_balance,
            current_balance=entity.current_balance,
            current_credit=entity.current_credit,
        )


class SpendingAccountEntryWithCalculatedFieldsMapper:
    """Mapper for SpendingAccountEntryWithCalculatedFields entity and SpendingAccountEntryWithCalculatedFieldsDTO."""

    @staticmethod
    def to_entity(
        dto: SpendingAccountEntryWithCalculatedFieldsDTO, account_id: str, date_detail_id: str
    ) -> SpendingAccountEntryWithCalculatedFields:
        """Convert SpendingAccountEntryWithCalculatedFieldsDTO to SpendingAccountEntryWithCalculatedFields entity."""
        return SpendingAccountEntryWithCalculatedFields(
            id=dto.id,
            account_id=account_id,
            date_detail_id=date_detail_id,
            starting_balance=dto.starting_balance,
            current_balance=dto.current_balance,
            current_credit=dto.current_credit,
            balance_after_credit=dto.balance_after_credit,
            total_spent=dto.total_spent,
        )

    @staticmethod
    def to_dto(
        entity: SpendingAccountEntryWithCalculatedFields, account_name: AccountName, date_detail: MonthYear
    ) -> SpendingAccountEntryWithCalculatedFieldsDTO:
        """Convert SpendingAccountEntryWithCalculatedFields entity to SpendingAccountEntryWithCalculatedFieldsDTO."""
        return SpendingAccountEntryWithCalculatedFieldsDTO(
            id=entity.id,
            account_name=account_name.account_name,
            month=date_detail.month,
            year=date_detail.year,
            starting_balance=entity.starting_balance,
            current_balance=entity.current_balance,
            current_credit=entity.current_credit,
            balance_after_credit=entity.balance_after_credit,
            total_spent=entity.total_spent,
        )
