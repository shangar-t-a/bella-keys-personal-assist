"""Service or use cases for spending account."""

from app.entities.errors.spending_account import (
    SpendingAccountEntryNotFoundError as EntitySpendingAccountEntryNotFoundError,
)
from app.entities.models.spending_account import (
    SpendingAccountEntry,
    SpendingAccountEntryWithCalculatedFields,
)
from app.entities.repositories.accounts import AccountRepositoryInterface
from app.entities.repositories.period import PeriodRepositoryInterface
from app.entities.repositories.spending_account import SpendingAccountRepositoryInterface
from app.use_cases.errors.accounts import (
    AccountNotFoundError,
    AccountWithNameNotFoundError,
)
from app.use_cases.errors.period import PeriodAlreadyExistsForAccountError
from app.use_cases.errors.spending_account import SpendingAccountEntryNotFoundError
from app.use_cases.models.spending_account import (
    FlattenedSpendingAccountEntry,
    FlattenedSpendingAccountEntryCreate,
    FlattenedSpendingAccountEntryWithCalculatedFields,
    FlattenedSpendingAccountEntryWithCalculatedFieldsPaginatedResponse,
)


class SpendingAccountService:
    """Spending account service to handle business logic."""

    def __init__(
        self,
        account_repository: AccountRepositoryInterface,
        period_repository: PeriodRepositoryInterface,
        spending_account_repository: SpendingAccountRepositoryInterface,
    ):
        """Initialize the SpendingAccountService with repositories."""
        self.account_repository = account_repository
        self.period_repository = period_repository
        self.spending_account_repository = spending_account_repository

    async def _retrieve_foreign_key_values_in_spending_account(
        self, entry: SpendingAccountEntryWithCalculatedFields
    ) -> FlattenedSpendingAccountEntryWithCalculatedFields:
        """Retrieve foreign key details for a spending account entry."""
        account = await self.account_repository.get_account_by_id(account_id=entry.account_id)
        date_detail = await self.period_repository.get_period_by_id(period_id=entry.period_id)

        return FlattenedSpendingAccountEntryWithCalculatedFields(
            id=entry.id,
            account_name=account.account_name,
            month=date_detail.month,
            year=date_detail.year,
            starting_balance=entry.starting_balance,
            current_balance=entry.current_balance,
            current_credit=entry.current_credit,
            balance_after_credit=entry.balance_after_credit,
            total_spent=entry.total_spent,
        )

    async def _convert_flattened_spending_account_entry_to_entity(
        self, entry: FlattenedSpendingAccountEntry
    ) -> SpendingAccountEntry:
        """Convert a flattened spending account entry to entity."""
        # Retrieve account and month year details
        account = await self.account_repository.get_account_by_name(account_name=entry.account_name)
        date_detail = await self.period_repository.get_period_by_value(month=entry.month, year=entry.year)

        return SpendingAccountEntry(
            id=entry.id,
            account_id=account.id,
            period_id=date_detail.id,
            starting_balance=entry.starting_balance,
            current_balance=entry.current_balance,
            current_credit=entry.current_credit,
        )

    async def add_entry(
        self, entry: FlattenedSpendingAccountEntryCreate
    ) -> FlattenedSpendingAccountEntryWithCalculatedFields:
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
            entry=SpendingAccountEntry(
                account_id=retrieved_account.id,
                period_id=retrieved_date_detail.id,
                starting_balance=entry.starting_balance,
                current_balance=entry.current_balance,
                current_credit=entry.current_credit,
            )
        )

        return FlattenedSpendingAccountEntryWithCalculatedFields(
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
        self, limit: int = 12, offset: int = 0
    ) -> FlattenedSpendingAccountEntryWithCalculatedFieldsPaginatedResponse:
        """Retrieve all entries for all spending accounts."""
        # Get all entries with details using optimized repository method with JOIN to eliminate N+1 queries
        spending_account_entry_with_details_paginated = (
            await self.spending_account_repository.get_all_entries_with_details(limit=limit, offset=offset)
        )

        # Convert to flattened response (account_name, month, year already included)
        spending_account_entry_entities_with_retrieved_details = [
            FlattenedSpendingAccountEntryWithCalculatedFields(
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
            for entry in spending_account_entry_with_details_paginated.entries
        ]

        return FlattenedSpendingAccountEntryWithCalculatedFieldsPaginatedResponse(
            entries=spending_account_entry_entities_with_retrieved_details,
            limit=spending_account_entry_with_details_paginated.limit,
            offset=spending_account_entry_with_details_paginated.offset,
            total_entries=spending_account_entry_with_details_paginated.total_entries,
        )

    async def get_all_entries_for_account(
        self, account_id: str, limit: int = 12, offset: int = 0
    ) -> FlattenedSpendingAccountEntryWithCalculatedFieldsPaginatedResponse:
        """Retrieve all entries for a given spending account.

        Raises:
            AccountNotFoundError: If the account with the provided ID does not exist.
        """
        # Check if account exists
        account = await self.account_repository.get_account_by_id(account_id=account_id)
        if not account:
            raise AccountNotFoundError(account_id=account_id)

        # Get all entries for account with details using optimized repository method with JOIN to eliminate N+1 queries
        spending_account_entry_with_details_paginated = (
            await self.spending_account_repository.get_all_entries_for_account_with_details(
                account_id=account_id, limit=limit, offset=offset
            )
        )

        # Convert to flattened response (account_name, month, year already included)
        spending_account_entry_entities_with_retrieved_details = [
            FlattenedSpendingAccountEntryWithCalculatedFields(
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
            for entry in spending_account_entry_with_details_paginated.entries
        ]

        return FlattenedSpendingAccountEntryWithCalculatedFieldsPaginatedResponse(
            entries=spending_account_entry_entities_with_retrieved_details,
            limit=spending_account_entry_with_details_paginated.limit,
            offset=spending_account_entry_with_details_paginated.offset,
            total_entries=spending_account_entry_with_details_paginated.total_entries,
        )

    async def edit_entry(
        self, entry_id: str, entry: FlattenedSpendingAccountEntry
    ) -> FlattenedSpendingAccountEntryWithCalculatedFields:
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

        return FlattenedSpendingAccountEntryWithCalculatedFields(
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
