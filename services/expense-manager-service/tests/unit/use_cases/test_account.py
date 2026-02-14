"""Unit tests for the accounts use case."""

from uuid import uuid4

import pytest

from app.use_cases.account import AccountService
from app.use_cases.errors.account import (
    AccountNotFoundError,
    AccountWithNameNotFoundError,
)


@pytest.fixture(scope="module")
def account_service(account_repo):
    """Provide an instance of AccountService."""
    return AccountService(account_repository=account_repo)


async def add_account(account_service, account_name="Unique Test Account"):
    account = await account_service.account_repository.get_or_create_account(account_name=account_name)
    return account


async def delete_all_accounts(account_service):
    accounts = await account_service.account_repository.get_all_accounts()
    for account in accounts:
        await account_service.account_repository.delete_account(account.id)


class TestGetOrCreateAccount:
    @pytest.mark.parametrize(
        "input_account_name,account_name_stored",
        [
            ("New Account", "NEW ACCOUNT"),
            ("TEST ACCOUNT", "TEST ACCOUNT"),
        ],
    )
    async def test__get_or_create_account__create_new_account(
        self,
        account_service,
        input_account_name,
        account_name_stored,
    ):
        """Test creating a new account."""
        account = await account_service.get_or_create_account(account_name=input_account_name)

        assert account.account_name == account_name_stored

    async def test__get_or_create_account__retrieve_existing_account(
        self,
        account_service,
    ):
        """Test retrieving an existing account."""
        test_account = await add_account(account_service)

        account = await account_service.get_or_create_account(account_name=test_account.account_name)

        assert account.id == test_account.id
        assert account.account_name == test_account.account_name


class TestGetAccountByName:
    async def test__get_account_by_name__existing_account__retrieve_account(
        self,
        account_service,
    ):
        """Test retrieving an existing account by name."""
        test_account = await add_account(account_service)

        account = await account_service.get_account_by_name(account_name=test_account.account_name)

        assert account is not None
        assert account.id == test_account.id
        assert account.account_name == test_account.account_name

    async def test__get_account_by_name__nonexistent_account__raise_error(
        self,
        account_service,
    ):
        """Test retrieving a non-existent account by name."""
        with pytest.raises(AccountWithNameNotFoundError):
            await account_service.get_account_by_name(account_name=f"NonExistent-{uuid4()}")


class TestGetAccountById:
    async def test__get_account_by_id__existing_account__retrieve_account(
        self,
        account_service,
    ):
        """Test retrieving an existing account by ID."""
        test_account = await add_account(account_service)

        account = await account_service.get_account_by_id(account_id=test_account.id)

        assert account is not None
        assert account.id == test_account.id

    async def test__get_account_by_id__nonexistent_account__raise_error(
        self,
        account_service,
    ):
        """Test retrieving a non-existent account by ID."""
        with pytest.raises(AccountNotFoundError):
            await account_service.get_account_by_id(account_id=f"non-existent-id-{uuid4()}")


class TestDeleteAccount:
    async def test__delete_account__delete_existing_account(
        self,
        account_service,
    ):
        """Test deleting an existing account."""
        test_account = await add_account(account_service=account_service, account_name="Account To Delete")

        account = await account_service.get_account_by_name(account_name=test_account.account_name)
        assert account.account_name == "ACCOUNT TO DELETE"
        await account_service.delete_account(account_id=test_account.id)

        with pytest.raises(AccountWithNameNotFoundError):
            await account_service.get_account_by_name(account_name=test_account.account_name)

    async def test__delete_account__nonexistent_account__raise_error(
        self,
        account_service,
    ):
        """Test deleting a non-existent account raises error."""
        with pytest.raises(AccountNotFoundError):
            await account_service.delete_account(account_id=f"non-existent-id-{uuid4()}")


class TestGetAllAccount:
    async def test__get_all_accounts__with_existing_accounts__retrieve_accounts(
        self,
        account_service,
    ):
        """Test retrieving all accounts when accounts exist."""
        await delete_all_accounts(account_service)
        await add_account(account_service=account_service, account_name="Account One")
        await add_account(account_service=account_service, account_name="Account Two")
        num_accounts = 2

        accounts = await account_service.get_all_accounts()

        assert accounts is not None
        assert len(accounts) == num_accounts

    async def test__get_all_accounts__with_no_accounts__retrieve_empty_list(
        self,
        account_service,
    ):
        """Test retrieving all accounts when no accounts exist."""
        await delete_all_accounts(account_service)

        accounts = await account_service.get_all_accounts()

        assert accounts == []


class TestUpdateAccount:
    async def test__update_account_name__existing_account__update_account(
        self,
        account_service,
    ):
        """Test updating the name of an existing account."""
        test_account = await add_account(account_service=account_service, account_name="Old Account Name")

        assert test_account.account_name == "OLD ACCOUNT NAME"
        updated_account = await account_service.update_account_name(
            account_id=test_account.id,
            account_name="Updated Account Name",
        )

        assert updated_account is not None
        assert updated_account.id == test_account.id
        assert updated_account.account_name == "UPDATED ACCOUNT NAME"

    async def test__update_account_name__nonexistent_account__raise_error(
        self,
        account_service,
    ):
        """Test updating the name of a non-existent account."""
        with pytest.raises(AccountNotFoundError):
            await account_service.update_account_name(
                account_id=f"non-existent-id-{uuid4()}",
                account_name="Some Name",
            )
