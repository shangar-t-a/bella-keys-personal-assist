"""Service or use cases for spending account."""

import math
from typing import TYPE_CHECKING

from app.entities.errors.spending_entry import (
    SpendingAccountEntryNotFoundError as EntitySpendingAccountEntryNotFoundError,
)
from app.entities.models.spending_entry import (
    SpendingEntry as SpendingEntryEntity,
)
from app.entities.models.spending_entry import (
    SpendingEntryFilter,
    SpendingEntrySort,
)
from app.use_cases.errors.account import (
    AccountNotFoundError,
    AccountWithNameNotFoundError,
)
from app.use_cases.errors.period import (
    PeriodAlreadyExistsForAccountError,
    PeriodWithDetailsNotFoundError,
)
from app.use_cases.errors.spending_entry import SpendingAccountEntryNotFoundError
from app.use_cases.models.pagination import Page
from app.use_cases.models.spending_entry import (
    SpendingEntryWithCalc,
    SpendingEntryWithCalcPage,
)

if TYPE_CHECKING:
    from app.entities.repositories.account import AccountRepositoryInterface
    from app.entities.repositories.period import PeriodRepositoryInterface
    from app.entities.repositories.spending_entry import SpendingEntryRepositoryInterface
    from app.use_cases.models.spending_entry import (
        SpendingEntry,
        SpendingEntryCreate,
    )


class SpendingEntryService:
    """Spending account service to handle business logic."""

    def __init__(
        self,
        account_repository: "AccountRepositoryInterface",
        period_repository: "PeriodRepositoryInterface",
        spending_account_repository: "SpendingEntryRepositoryInterface",
    ):
        """Initialize the SpendingEntryService with repositories."""
        self.account_repository = account_repository
        self.period_repository = period_repository
        self.spending_account_repository = spending_account_repository

    async def _convert_flattened_spending_account_entry_to_entity(self, entry: "SpendingEntry") -> SpendingEntryEntity:
        """Convert a flattened spending account entry to entity."""
        # Retrieve account and month year details
        account = await self.account_repository.get_account_by_name(account_name=entry.account_name)
        if not account:
            raise AccountWithNameNotFoundError(account_name=entry.account_name)
        date_detail = await self.period_repository.get_period_by_value(month=entry.month, year=entry.year)
        if not date_detail:
            raise PeriodWithDetailsNotFoundError(month=entry.month, year=entry.year)

        return SpendingEntryEntity(
            id=entry.id,
            account_id=account.id,
            period_id=date_detail.id,
            starting_balance=entry.starting_balance,
            current_balance=entry.current_balance,
            current_credit=entry.current_credit,
        )

    async def add_entry(self, entry: "SpendingEntryCreate") -> SpendingEntryWithCalc:
        """Add a new entry to the spending account.

        Raises:
            AccountWithNameNotFoundError: If the account with the provided name does not exist.
            PeriodAlreadyExistsForAccountError: If the month and year already exist for the account.
        """
        # Retrieve account and month year details
        retrieved_account = await self.account_repository.get_account_by_name(account_name=entry.account_name)

        # Account must exist
        if not retrieved_account:
            raise AccountWithNameNotFoundError(account_name=entry.account_name)

        # Retrieve Period if it exists
        retrieved_date_detail = await self.period_repository.get_period_by_value(month=entry.month, year=entry.year)

        # Duplicate Period should not exist
        if retrieved_date_detail:
            # Check if the entry already exists for the account and month/year
            entry_with_selected_account_and_period = (
                await self.spending_account_repository.get_entry_by_account_and_period_or_none(
                    account_id=retrieved_account.id,
                    period_id=retrieved_date_detail.id,
                )
            )

            if entry_with_selected_account_and_period:
                raise PeriodAlreadyExistsForAccountError(
                    account_name=retrieved_account.account_name,
                    month=retrieved_date_detail.month,
                    year=retrieved_date_detail.year,
                )

        # Create Period if it does not exist
        if not retrieved_date_detail:
            retrieved_date_detail = await self.period_repository.get_or_create_period(
                month=entry.month, year=entry.year
            )

        # Add entry with details to avoid extra query for foreign keys
        spending_account_entry_entity_with_details = await self.spending_account_repository.add_entry_with_details(
            entry=SpendingEntryEntity(
                account_id=retrieved_account.id,
                period_id=retrieved_date_detail.id,
                starting_balance=entry.starting_balance,
                current_balance=entry.current_balance,
                current_credit=entry.current_credit,
            )
        )

        return SpendingEntryWithCalc(
            id=spending_account_entry_entity_with_details.id,
            account_name=spending_account_entry_entity_with_details.account_name,
            month=spending_account_entry_entity_with_details.month,
            year=spending_account_entry_entity_with_details.year,
            starting_balance=spending_account_entry_entity_with_details.starting_balance,
            current_balance=spending_account_entry_entity_with_details.current_balance,
            current_credit=spending_account_entry_entity_with_details.current_credit,
            balance_after_credit=spending_account_entry_entity_with_details.balance_after_credit,
            total_spent=spending_account_entry_entity_with_details.total_spent,
        )

    async def get_all_entries(
        self,
        page: int = 0,
        size: int = 12,
        filters: SpendingEntryFilter | None = None,
        sort: SpendingEntrySort | None = None,
    ) -> SpendingEntryWithCalcPage:
        """Retrieve all entries for all spending accounts."""
        # Get all entries with details using optimized repository method with JOIN to eliminate N+1 queries
        spending_entry_detail_with_calc_page = await self.spending_account_repository.get_all_entries_with_details(
            limit=size, offset=page * size, filters=filters, sort=sort
        )

        # Convert to flattened response (account_name, month, year already included)
        spending_account_entry_entities_with_retrieved_details = [
            SpendingEntryWithCalc(
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
            for entry in spending_entry_detail_with_calc_page.entries
        ]

        return SpendingEntryWithCalcPage(
            spending_entries=spending_account_entry_entities_with_retrieved_details,
            page=Page(
                number=page,
                size=size,
                total_elements=spending_entry_detail_with_calc_page.total_entries,
                total_pages=math.ceil(spending_entry_detail_with_calc_page.total_entries / size),
            ),
        )

    async def get_all_entries_for_account(
        self,
        account_id: str,
        page: int = 0,
        size: int = 12,
        filters: SpendingEntryFilter | None = None,
        sort: SpendingEntrySort | None = None,
    ) -> SpendingEntryWithCalcPage:
        """Retrieve all entries for a given spending account.

        Raises:
            AccountNotFoundError: If the account with the provided ID does not exist.
        """
        # Check if account exists
        account = await self.account_repository.get_account_by_id(account_id=account_id)
        if not account:
            raise AccountNotFoundError(account_id=account_id)

        # Get all entries for account with details using optimized repository method with JOIN to eliminate N+1 queries
        spending_entry_detail_with_calc_page = (
            await self.spending_account_repository.get_all_entries_for_account_with_details(
                account_id=account_id, limit=size, offset=page * size, filters=filters, sort=sort
            )
        )

        # Convert to flattened response (account_name, month, year already included)
        spending_account_entry_entities_with_retrieved_details = [
            SpendingEntryWithCalc(
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
            for entry in spending_entry_detail_with_calc_page.entries
        ]

        return SpendingEntryWithCalcPage(
            spending_entries=spending_account_entry_entities_with_retrieved_details,
            page=Page(
                number=page,
                size=size,
                total_elements=spending_entry_detail_with_calc_page.total_entries,
                total_pages=math.ceil(spending_entry_detail_with_calc_page.total_entries / size),
            ),
        )

    async def edit_entry(self, entry_id: str, entry: "SpendingEntry") -> SpendingEntryWithCalc:
        """Edit an existing spending account entry.

        Raises:
            AccountWithNameNotFoundError: If the account with the provided name does not exist.
            PeriodAlreadyExistsForAccountError: If the month and year already exist for the account.
            SpendingAccountEntryNotFoundError: If the spending account entry with the provided ID does not exist.
        """
        # Account must exist. If exists, retrieve the account to get its ID
        account = await self.account_repository.get_account_by_name(account_name=entry.account_name)
        if not account:
            raise AccountWithNameNotFoundError(account_name=entry.account_name)

        # Period must be unique for the account
        # Retrieve or Create Period
        date_detail = await self.period_repository.get_or_create_period(month=entry.month, year=entry.year)
        entry_with_selected_account_and_period = (
            await self.spending_account_repository.get_entry_by_account_and_period_or_none(
                account_id=account.id,
                period_id=date_detail.id,
            )
        )
        if entry_with_selected_account_and_period and entry_with_selected_account_and_period.id != entry_id:
            raise PeriodAlreadyExistsForAccountError(
                account_name=account.account_name, month=entry.month, year=entry.year
            )

        # Convert flattened entry to entity
        spending_account_entry_entity = await self._convert_flattened_spending_account_entry_to_entity(entry=entry)

        # Edit entry with details to avoid extra query for foreign keys
        try:
            updated_spending_account_entry_entity_with_details = (
                await self.spending_account_repository.edit_entry_with_details(
                    entry_id=entry_id, entry=spending_account_entry_entity
                )
            )
        except EntitySpendingAccountEntryNotFoundError as error:
            raise SpendingAccountEntryNotFoundError(entry_id=error.entry_id) from error

        return SpendingEntryWithCalc(
            id=updated_spending_account_entry_entity_with_details.id,
            account_name=updated_spending_account_entry_entity_with_details.account_name,
            month=updated_spending_account_entry_entity_with_details.month,
            year=updated_spending_account_entry_entity_with_details.year,
            starting_balance=updated_spending_account_entry_entity_with_details.starting_balance,
            current_balance=updated_spending_account_entry_entity_with_details.current_balance,
            current_credit=updated_spending_account_entry_entity_with_details.current_credit,
            balance_after_credit=updated_spending_account_entry_entity_with_details.balance_after_credit,
            total_spent=updated_spending_account_entry_entity_with_details.total_spent,
        )

    async def delete_entry(self, entry_id: str) -> None:
        """Delete a spending account entry by its ID.

        Raises:
            SpendingAccountEntryNotFoundError: If the spending account entry with the provided ID does not exist.
        """
        try:
            await self.spending_account_repository.delete_entry(entry_id=entry_id)
        except EntitySpendingAccountEntryNotFoundError as error:
            raise SpendingAccountEntryNotFoundError(entry_id=error.entry_id) from error
