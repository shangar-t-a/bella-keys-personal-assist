"""Service or use case for managing accounts."""

from app.entities.errors.account import (
    AccountNotFoundError as EntityAccountNotFoundError,
)
from app.entities.models.account import (
    Account,
)
from app.entities.repositories.account import AccountRepositoryInterface
from app.use_cases.errors.account import (
    AccountNotFoundError,
    AccountWithNameNotFoundError,
)


class AccountService:
    """Account service to handle business logic."""

    def __init__(self, account_repository: AccountRepositoryInterface):
        """Initialize the account service with the repository."""
        self.account_repository = account_repository

    async def get_or_create_account(self, account_name: str) -> Account:
        """Retrieve an existing account or create a new one with the provided name."""
        account_name_entity = await self.account_repository.get_or_create_account(account_name=account_name)

        return account_name_entity

    async def get_account_by_name(self, account_name: str) -> Account:
        """Retrieve an account by its name.

        Raises:
            AccountWithNameNotFoundError: If the account with the provided name does not exist.
        """
        account_name_entity = await self.account_repository.get_account_by_name(account_name=account_name)

        if not account_name_entity:
            raise AccountWithNameNotFoundError(account_name=account_name)

        return account_name_entity

    async def get_account_by_id(self, account_id: str) -> Account:
        """Retrieve an account by its ID.

        Raises:
            AccountNotFoundError: If the account with the provided ID does not exist.
        """
        account_name_entity = await self.account_repository.get_account_by_id(account_id=account_id)

        if not account_name_entity:
            raise AccountNotFoundError(account_id=account_id)

        return account_name_entity

    async def get_all_accounts(self) -> list[Account]:
        """Retrieve all accounts."""
        account_name_entities = await self.account_repository.get_all_accounts()

        if not account_name_entities:
            return []

        return account_name_entities

    async def update_account_name(self, account_id: str, account_name: str) -> Account:
        """Update an existing account name with the provided data.

        Raises:
            AccountNotFoundError: If the account with the provided ID does not exist.
        """
        try:
            account_name_entity = await self.account_repository.update_account_name(
                account_id=account_id, account_name=account_name
            )
        except EntityAccountNotFoundError as error:
            raise AccountNotFoundError(account_id=error.account_id) from error

        return account_name_entity

    async def delete_account(self, account_id: str) -> None:
        """Delete an account by its ID.

        Raises:
            AccountNotFoundError: If the account with the provided ID does not exist.
        """
        try:
            await self.account_repository.delete_account(account_id=account_id)
        except EntityAccountNotFoundError as error:
            raise AccountNotFoundError(account_id=error.account_id) from error
