"""Service or use cases for spending account."""

from app.entities.errors.spending_account import (
    SpendingAccountEntryNotFoundError as EntitySpendingAccountEntryNotFoundError,
)
from app.entities.models.spending_account import (
    SpendingAccountEntry,
    SpendingAccountEntryWithCalculatedFields,
)
from app.entities.repositories.accounts import AccountRepositoryInterface
from app.entities.repositories.spending_account import SpendingAccountRepositoryInterface
from app.use_cases.errors.accounts import (
    AccountNotFoundError,
    AccountWithNameNotFoundError,
    MonthYearAlreadyExistsForAccountError,
)
from app.use_cases.errors.spending_account import SpendingAccountEntryNotFoundError
from app.use_cases.models.spending_account import (
    FlattenedSpendingAccountEntry,
    FlattenedSpendingAccountEntryCreate,
    FlattenedSpendingAccountEntryWithCalculatedFields,
)


class SpendingAccountService:
    """Spending account service to handle business logic."""

    def __init__(
        self,
        account_repository: AccountRepositoryInterface,
        spending_account_repository: SpendingAccountRepositoryInterface,
    ):
        """Initialize the SpendingAccountService with repositories."""
        self.account_repository = account_repository
        self.spending_account_repository = spending_account_repository

    async def _retrieve_foreign_key_values_in_spending_account(
        self, entry: SpendingAccountEntryWithCalculatedFields
    ) -> FlattenedSpendingAccountEntryWithCalculatedFields:
        """Retrieve foreign key details for a spending account entry."""
        account = await self.account_repository.get_account_by_id(account_id=entry.account_id)
        date_detail = await self.account_repository.get_month_year_by_id(month_year_id=entry.date_detail_id)

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
        date_detail = await self.account_repository.get_month_year_by_value(month=entry.month, year=entry.year)

        return SpendingAccountEntry(
            id=entry.id,
            account_id=account.id,
            date_detail_id=date_detail.id,
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
            MonthYearAlreadyExistsForAccountError: If the month and year already exist for the account.
        """
        # Retrieve account and month year details
        retrieved_account = await self.account_repository.get_account_by_name(account_name=entry.account_name)

        # Account must exist
        if not retrieved_account:
            raise AccountWithNameNotFoundError(account_name=entry.account_name)

        # Retrieve MonthYear if it exists
        retrieved_date_detail = await self.account_repository.get_month_year_by_value(
            month=entry.month, year=entry.year
        )

        # Duplicate MonthYear should not exist
        if retrieved_date_detail:
            # Check if the entry already exists for the account and month/year
            entry_with_selected_account_and_month_year = (
                await self.spending_account_repository.get_entry_by_account_and_month_year_or_none(
                    account_id=retrieved_account.id,
                    month_year_id=retrieved_date_detail.id,
                )
            )

            if entry_with_selected_account_and_month_year:
                raise MonthYearAlreadyExistsForAccountError(
                    account_name=retrieved_account.account_name,
                    month=retrieved_date_detail.month,
                    year=retrieved_date_detail.year,
                )

        # Create MonthYear if it does not exist
        if not retrieved_date_detail:
            retrieved_date_detail = await self.account_repository.get_or_create_month_year(
                month=entry.month, year=entry.year
            )

        # Add entry in repository
        spending_account_entry_entity = await self.spending_account_repository.add_entry(
            entry=SpendingAccountEntry(
                account_id=retrieved_account.id,
                date_detail_id=retrieved_date_detail.id,
                starting_balance=entry.starting_balance,
                current_balance=entry.current_balance,
                current_credit=entry.current_credit,
            )
        )

        # Retrieve foreign key details for the new entry
        spending_account_entry_entity_with_details = await self._retrieve_foreign_key_values_in_spending_account(
            spending_account_entry_entity
        )

        return spending_account_entry_entity_with_details

    async def get_all_entries(self) -> list[FlattenedSpendingAccountEntryWithCalculatedFields]:
        """Retrieve all entries for all spending accounts."""
        spending_account_entry_entities = await self.spending_account_repository.get_all_entries()
        # Apply calculated fields for each entry
        spending_account_entry_entities_with_calculated_fields = [
            SpendingAccountEntryWithCalculatedFields(
                id=entry.id,
                account_id=entry.account_id,
                date_detail_id=entry.date_detail_id,
                starting_balance=entry.starting_balance,
                current_balance=entry.current_balance,
                current_credit=entry.current_credit,
            )
            for entry in spending_account_entry_entities
        ]
        # Retrieve foreign key details for each entry
        spending_account_entry_entities_with_retrieved_details = [
            await self._retrieve_foreign_key_values_in_spending_account(entry)
            for entry in spending_account_entry_entities_with_calculated_fields
        ]

        return spending_account_entry_entities_with_retrieved_details

    async def get_all_entries_for_account(
        self, account_id: str
    ) -> list[FlattenedSpendingAccountEntryWithCalculatedFields]:
        """Retrieve all entries for a given spending account.

        Raises:
            AccountNotFoundError: If the account with the provided ID does not exist.
        """
        # Check if account exists
        account = await self.account_repository.get_account_by_id(account_id=account_id)
        if not account:
            raise AccountNotFoundError(account_id=account_id)

        # Retrieve all entries for the account
        spending_account_entry_entities = await self.spending_account_repository.get_all_entries_for_account(
            account_id=account_id
        )
        # Apply calculated fields for each entry
        spending_account_entry_entities_with_calculated_fields = [
            SpendingAccountEntryWithCalculatedFields(
                id=entry.id,
                account_id=entry.account_id,
                date_detail_id=entry.date_detail_id,
                starting_balance=entry.starting_balance,
                current_balance=entry.current_balance,
                current_credit=entry.current_credit,
            )
            for entry in spending_account_entry_entities
        ]
        # Retrieve foreign key details for each entry
        spending_account_entry_entities_with_retrieved_details = [
            await self._retrieve_foreign_key_values_in_spending_account(entry)
            for entry in spending_account_entry_entities_with_calculated_fields
        ]

        return spending_account_entry_entities_with_retrieved_details

    async def edit_entry(
        self, entry_id: str, entry: FlattenedSpendingAccountEntry
    ) -> FlattenedSpendingAccountEntryWithCalculatedFields:
        """Edit an existing spending account entry.

        Raises:
            AccountWithNameNotFoundError: If the account with the provided name does not exist.
            MonthYearAlreadyExistsForAccountError: If the month and year already exist for the account.
            SpendingAccountEntryNotFoundError: If the spending account entry with the provided ID does not exist.
        """
        # Account must exist. If exists, retrieve the account to get its ID
        account = await self.account_repository.get_account_by_name(account_name=entry.account_name)
        if not account:
            raise AccountWithNameNotFoundError(account_name=entry.account_name)

        # MonthYear must be unique for the account
        # Retrieve or Create MonthYear
        date_detail = await self.account_repository.get_or_create_month_year(month=entry.month, year=entry.year)
        entry_with_selected_account_and_month_year = (
            await self.spending_account_repository.get_entry_by_account_and_month_year_or_none(
                account_id=account.id,
                month_year_id=date_detail.id,
            )
        )
        if entry_with_selected_account_and_month_year and entry_with_selected_account_and_month_year.id != entry_id:
            raise MonthYearAlreadyExistsForAccountError(
                account_name=account.account_name, month=entry.month, year=entry.year
            )

        # Convert flattened entry to entity
        spending_account_entry_entity = await self._convert_flattened_spending_account_entry_to_entity(entry=entry)

        # Edit entry in repository
        try:
            updated_spending_account_entry_entity = await self.spending_account_repository.edit_entry(
                entry_id=entry_id, entry=spending_account_entry_entity
            )
        except EntitySpendingAccountEntryNotFoundError as error:
            raise SpendingAccountEntryNotFoundError(entry_id=error.entry_id) from error

        # Retrieve foreign key details for the updated entry
        updated_spending_account_entry_entity_with_details = (
            await self._retrieve_foreign_key_values_in_spending_account(updated_spending_account_entry_entity)
        )

        return updated_spending_account_entry_entity_with_details

    async def delete_entry(self, entry_id: str) -> None:
        """Delete a spending account entry by its ID.

        Raises:
            SpendingAccountEntryNotFoundError: If the spending account entry with the provided ID does not exist.
        """
        try:
            await self.spending_account_repository.delete_entry(entry_id=entry_id)
        except EntitySpendingAccountEntryNotFoundError as error:
            raise SpendingAccountEntryNotFoundError(entry_id=error.entry_id) from error
