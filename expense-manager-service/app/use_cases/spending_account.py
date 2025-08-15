"""Service or use cases for spending account."""

from app.entities.errors.spending_account import (
    SpendingAccountEntryNotFoundError as EntitySpendingAccountEntryNotFoundError,
)
from app.entities.repositories.accounts import AccountRepositoryInterface
from app.entities.repositories.spending_account import SpendingAccountRepositoryInterface
from app.use_cases.dto.spending_account import (
    SpendingAccountEntryDTO,
    SpendingAccountEntryWithCalculatedFieldsDTO,
)
from app.use_cases.errors.accounts import (
    AccountNotFoundError,
    AccountWithNameNotFoundError,
    MonthYearAlreadyExistsForAccountError,
)
from app.use_cases.errors.spending_account import SpendingAccountEntryNotFoundError
from app.use_cases.mappers.spending_account import (
    SpendingAccountEntryMapper,
    SpendingAccountEntryWithCalculatedFieldsMapper,
)


class SpendingAccountService:
    """Spending account service to handle business logic."""

    async def _retrieve_account_and_date_details_and_convert_to_dto(
        self, entry: SpendingAccountEntryWithCalculatedFieldsDTO
    ) -> SpendingAccountEntryWithCalculatedFieldsDTO:
        """Retrieve account and date details for a spending account entry."""
        retrieved_account = await self.account_repository.get_account_by_id(account_id=entry.account_id)
        retrieved_date_detail = await self.account_repository.get_month_year_by_id(month_year_id=entry.date_detail_id)

        return SpendingAccountEntryWithCalculatedFieldsMapper.to_dto(entry, retrieved_account, retrieved_date_detail)

    def __init__(
        self,
        account_repository: AccountRepositoryInterface,
        spending_account_repository: SpendingAccountRepositoryInterface,
    ):
        """Initialize the SpendingAccountService with repositories."""
        self.account_repository = account_repository
        self.spending_account_repository = spending_account_repository

    async def add_entry(self, entry: SpendingAccountEntryDTO) -> SpendingAccountEntryWithCalculatedFieldsDTO:
        """Add a new entry to the spending account.

        Raises:
            AccountWithNameNotFoundError: If the account with the provided name does not exist.
            MonthYearAlreadyExistsForAccountError: If the month and year already exist for the account.
        """
        # Account must exist
        account = await self.account_repository.get_account_by_name(account_name=entry.account_name)
        if not account:
            raise AccountWithNameNotFoundError(account_name=entry.account_name)

        # Duplicate MonthYear should not exist
        date_detail = await self.account_repository.get_month_year_by_value(month=entry.month, year=entry.year)
        if date_detail:
            # Check if the entry already exists for the account and month/year
            entry_with_selected_account_and_month_year = (
                await self.spending_account_repository.get_entry_by_account_and_month_year_or_none(
                    account_id=account.id,
                    month_year_id=date_detail.id,
                )
            )

            if entry_with_selected_account_and_month_year:
                raise MonthYearAlreadyExistsForAccountError(
                    account_name=account.account_name, month=entry.month, year=entry.year
                )

        # Create MonthYear if it does not exist
        if not date_detail:
            date_detail = await self.account_repository.get_or_create_month_year(month=entry.month, year=entry.year)

        # Convert DTO to entity
        spending_account_entry_entity = SpendingAccountEntryMapper.to_entity(
            dto=entry, account_id=account.id, date_detail_id=date_detail.id
        )

        # Add entry in repository
        spending_account_entry_entity = await self.spending_account_repository.add_entry(
            entry=spending_account_entry_entity
        )

        return await self._retrieve_account_and_date_details_and_convert_to_dto(spending_account_entry_entity)

    async def get_all_entries(self) -> list[SpendingAccountEntryWithCalculatedFieldsDTO]:
        """Retrieve all entries for all spending accounts."""
        spending_account_entry_entities = await self.spending_account_repository.get_all_entries()
        spending_account_entry_entities_with_retrieved_details = []
        # Retrieve account and date details for each entry
        for entry in spending_account_entry_entities:
            spending_account_entry_entities_with_retrieved_details.append(
                await self._retrieve_account_and_date_details_and_convert_to_dto(entry)
            )

        return spending_account_entry_entities_with_retrieved_details

    async def get_all_entries_for_account(self, account_id: str) -> list[SpendingAccountEntryWithCalculatedFieldsDTO]:
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
        spending_account_entry_entities_with_retrieved_details = []
        for entry in spending_account_entry_entities:
            spending_account_entry_entities_with_retrieved_details.append(
                await self._retrieve_account_and_date_details_and_convert_to_dto(entry)
            )

        return spending_account_entry_entities_with_retrieved_details

    async def edit_entry(
        self, entry_id: str, entry: SpendingAccountEntryDTO
    ) -> SpendingAccountEntryWithCalculatedFieldsDTO:
        """Edit an existing spending account entry.

        Raises:
            AccountWithNameNotFoundError: If the account with the provided name does not exist.
            MonthYearAlreadyExistsForAccountError: If the month and year already exist for the account.
            SpendingAccountEntryNotFoundError: If the spending account entry with the provided ID does not exist.
        """
        # Check if entry exists
        try:
            await self.spending_account_repository.get_entry_by_id(entry_id=entry_id)
        except EntitySpendingAccountEntryNotFoundError as error:
            raise SpendingAccountEntryNotFoundError(entry_id=error.entry_id) from error

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

        # Convert DTO to entity
        spending_account_entry_entity = SpendingAccountEntryMapper.to_entity(
            dto=entry, account_id=account.id, date_detail_id=date_detail.id
        )

        # Edit entry in repository
        updated_spending_account_entry_entity = await self.spending_account_repository.edit_entry(
            entry_id=entry_id, entry=spending_account_entry_entity
        )

        return await self._retrieve_account_and_date_details_and_convert_to_dto(updated_spending_account_entry_entity)

    async def delete_entry(self, entry_id: str) -> None:
        """Delete a spending account entry by its ID.

        Raises:
            SpendingAccountEntryNotFoundError: If the spending account entry with the provided ID does not exist.
        """
        try:
            await self.spending_account_repository.delete_entry(entry_id=entry_id)
        except EntitySpendingAccountEntryNotFoundError as error:
            raise SpendingAccountEntryNotFoundError(entry_id=error.entry_id) from error
