"""Unit tests for SpendingAccount use cases."""

from uuid import uuid4

import pytest

from app.entities.errors.spending_account import (
    SpendingAccountEntryNotFoundError as EntitySpendingAccountEntryNotFoundError,
)
from app.use_cases.accounts import AccountService
from app.use_cases.errors.accounts import (
    AccountNotFoundError,
    AccountWithNameNotFoundError,
    MonthYearAlreadyExistsForAccountError,
)
from app.use_cases.errors.spending_account import SpendingAccountEntryNotFoundError
from app.use_cases.models.spending_account import (
    FlattenedSpendingAccountEntry,
    FlattenedSpendingAccountEntryCreate,
)
from app.use_cases.spending_account import SpendingAccountService


@pytest.fixture(scope="module")
def account_service(account_repo):
    """Provide an instance of AccountService."""
    return AccountService(account_repository=account_repo)


@pytest.fixture(scope="module")
def spending_account_service(account_repo, spending_account_repo):
    """Provide an instance of SpendingAccountService."""
    return SpendingAccountService(
        account_repository=account_repo,
        spending_account_repository=spending_account_repo,
    )


async def add_account(account_service, account_name="Spending Account Test"):
    account = await account_service.account_repository.get_or_create_account(account_name=account_name)
    return account


def get_entry_data(
    account_name="Spending Account Test",
    month="September",
    year=2025,
    starting_balance=1000.0,
    current_balance=1200.0,
    current_credit=200.0,
):
    return {
        "account_name": account_name,
        "month": month,
        "year": year,
        "starting_balance": starting_balance,
        "current_balance": current_balance,
        "current_credit": current_credit,
    }


async def delete_all_entries(spending_account_service):
    """Helper function to delete all entries in the repository."""
    entries = await spending_account_service.spending_account_repository.get_all_entries()
    for entry in entries:
        await spending_account_service.spending_account_repository.delete_entry(entry.id)


async def add_entry(spending_account_service, entry_data):
    entry = FlattenedSpendingAccountEntryCreate(**entry_data)
    return await spending_account_service.add_entry(entry)


class TestAddSpendingAccountEntry:
    @pytest.mark.asyncio
    async def test__add_entry__success(
        self,
        spending_account_service,
    ):
        """Test successfully adding a spending account entry."""
        await add_account(spending_account_service)
        entry_data = get_entry_data()
        entry = FlattenedSpendingAccountEntryCreate(**entry_data)

        result = await spending_account_service.add_entry(entry=entry)

        assert result is not None
        assert result.account_name == entry_data["account_name"].upper()
        assert result.month == entry_data["month"]
        assert result.year == entry_data["year"]
        assert result.starting_balance == entry_data["starting_balance"]
        assert result.current_balance == entry_data["current_balance"]
        assert result.current_credit == entry_data["current_credit"]

    @pytest.mark.asyncio
    async def test__add_entry__account_not_found(
        self,
        spending_account_service,
    ):
        """Test adding entry with non-existent account raises error."""
        await add_account(spending_account_service)
        entry_data = get_entry_data(account_name=f"NonExistent-{uuid4()}")
        entry = FlattenedSpendingAccountEntryCreate(**entry_data)

        with pytest.raises(AccountWithNameNotFoundError):
            await spending_account_service.add_entry(entry=entry)

    @pytest.mark.asyncio
    async def test__add_entry__duplicate_month_year_for_account(
        self,
        spending_account_service,
    ):
        """Test adding entry with duplicate month/year for account raises error."""
        await delete_all_entries(spending_account_service)
        await add_account(spending_account_service)
        entry_data = get_entry_data(account_name="Spending Account Test", month="October", year=2025)
        entry = FlattenedSpendingAccountEntryCreate(**entry_data)

        # Add first entry
        await spending_account_service.add_entry(entry=entry)

        # Try to add duplicate
        with pytest.raises(MonthYearAlreadyExistsForAccountError):
            await spending_account_service.add_entry(entry=entry)

    @pytest.mark.asyncio
    async def test__add_entry__check_response_data(
        self,
        spending_account_service,
    ):
        """Test the response data of adding a spending account entry."""
        await add_account(spending_account_service)
        entry_data = get_entry_data()
        entry = FlattenedSpendingAccountEntryCreate(**entry_data)

        result = await spending_account_service.add_entry(entry=entry)

        assert result is not None
        assert result.id is not None
        assert result.account_name == entry_data["account_name"].upper()
        assert result.month == entry_data["month"]
        assert result.year == entry_data["year"]
        assert result.starting_balance == entry_data["starting_balance"]
        assert result.current_balance == entry_data["current_balance"]
        assert result.current_credit == entry_data["current_credit"]
        assert result.balance_after_credit == entry_data["current_balance"] - entry_data["current_credit"]
        assert (
            result.total_spent
            == (entry_data["starting_balance"] - entry_data["current_balance"]) + entry_data["current_credit"]
        )


class TestGetAllSpendingAccountEntries:
    @pytest.mark.asyncio
    async def test__get_all_entries__success(
        self,
        spending_account_service,
    ):
        """Test retrieving all spending account entries."""
        await delete_all_entries(spending_account_service)
        await add_account(spending_account_service)
        entry_data1 = get_entry_data(month="November", year=2025)
        entry_data2 = get_entry_data(month="December", year=2025)
        await add_entry(spending_account_service, entry_data1)
        await add_entry(spending_account_service, entry_data2)
        num_entries = 2

        results = await spending_account_service.get_all_entries()

        assert results is not None
        assert len(results) == num_entries

    @pytest.mark.asyncio
    async def test__get_all_entries__empty(
        self,
        spending_account_service,
    ):
        """Test retrieving all entries when none exist."""
        await delete_all_entries(spending_account_service)

        results = await spending_account_service.get_all_entries()

        assert results == []

    @pytest.mark.asyncio
    async def test__get_all_entries__check_response_data(
        self,
        spending_account_service,
    ):
        """Test the response data of retrieving all spending account entries."""
        await delete_all_entries(spending_account_service)
        await add_account(spending_account_service)
        entry_data = get_entry_data()
        await add_entry(spending_account_service, entry_data)

        results = await spending_account_service.get_all_entries()

        assert results is not None
        assert len(results) == 1
        result = results[0]
        assert result.id is not None
        assert result.account_name == entry_data["account_name"].upper()
        assert result.month == entry_data["month"]
        assert result.year == entry_data["year"]
        assert result.starting_balance == entry_data["starting_balance"]
        assert result.current_balance == entry_data["current_balance"]
        assert result.current_credit == entry_data["current_credit"]
        assert result.balance_after_credit == entry_data["current_balance"] - entry_data["current_credit"]
        assert (
            result.total_spent
            == (entry_data["starting_balance"] - entry_data["current_balance"]) + entry_data["current_credit"]
        )


class TestGetAllEntriesForAccount:
    @pytest.mark.asyncio
    async def test__get_all_entries_for_account__success(
        self,
        spending_account_service,
    ):
        """Test retrieving all entries for a specific account."""
        # Clean up and add account
        await delete_all_entries(spending_account_service)
        account1 = await add_account(spending_account_service, account_name="Account1")
        account2 = await add_account(spending_account_service, account_name="Account2")
        entry_data1 = get_entry_data(account_name=account1.account_name, month="January", year=2025)
        entry_data2 = get_entry_data(account_name=account1.account_name, month="February", year=2025)
        entry_data3 = get_entry_data(account_name=account2.account_name, month="January", year=2025)
        entry_data4 = get_entry_data(account_name=account2.account_name, month="February", year=2025)
        await add_entry(spending_account_service, entry_data1)
        await add_entry(spending_account_service, entry_data2)
        await add_entry(spending_account_service, entry_data3)
        await add_entry(spending_account_service, entry_data4)
        num_entries = 2

        results = await spending_account_service.get_all_entries_for_account(account_id=account1.id)

        assert results is not None
        assert len(results) == num_entries
        for result in results:
            assert result.account_name == account1.account_name.upper()
            assert result.id is not None

    @pytest.mark.asyncio
    async def test__get_all_entries_for_account__empty(
        self,
        spending_account_service,
    ):
        """Test retrieving entries for an account with no entries."""
        await delete_all_entries(spending_account_service)
        account = await add_account(spending_account_service)

        results = await spending_account_service.get_all_entries_for_account(account_id=account.id)

        assert results == []

    @pytest.mark.asyncio
    async def test__get_all_entries_for_account__account_not_found(
        self,
        spending_account_service,
    ):
        """Test retrieving entries for a non-existent account raises error."""
        fake_account_id = f"non-existent-id-{uuid4()}"

        with pytest.raises(AccountNotFoundError):
            await spending_account_service.get_all_entries_for_account(account_id=fake_account_id)


class TestEditSpendingAccountEntry:
    @pytest.mark.asyncio
    async def test__edit_entry__success(
        self,
        spending_account_service,
    ):
        """Test successfully editing a spending account entry."""
        account = await add_account(spending_account_service, account_name=f"EditAccount-{uuid4()}")
        entry_data = get_entry_data(account_name=account.account_name)
        created_entry = await add_entry(spending_account_service, entry_data)

        # Edit entry: change month/year and balances
        edit_data = get_entry_data(
            account_name=account.account_name,
            month="April",
            year=2026,
            starting_balance=2000.0,
            current_balance=1800.0,
            current_credit=100.0,
        )
        edit_entry = FlattenedSpendingAccountEntry(id=created_entry.id, **edit_data)
        result = await spending_account_service.edit_entry(entry_id=created_entry.id, entry=edit_entry)

        assert result is not None
        assert result.id == created_entry.id
        assert result.account_name == edit_data["account_name"].upper()
        assert result.month == edit_data["month"]
        assert result.year == edit_data["year"]
        assert result.starting_balance == edit_data["starting_balance"]
        assert result.current_balance == edit_data["current_balance"]
        assert result.current_credit == edit_data["current_credit"]

    @pytest.mark.asyncio
    async def test__edit_entry__check_response_data(
        self,
        spending_account_service,
    ):
        """Test the response data of editing a spending account entry."""
        account = await add_account(spending_account_service, account_name=f"EditAccount-{uuid4()}")
        entry_data = get_entry_data(account_name=account.account_name)
        created_entry = await add_entry(spending_account_service, entry_data)

        # Edit entry: change month/year and balances
        edit_data = get_entry_data(account_name=account.account_name)
        edit_entry = FlattenedSpendingAccountEntry(id=created_entry.id, **edit_data)
        result = await spending_account_service.edit_entry(entry_id=created_entry.id, entry=edit_entry)

        assert result is not None
        assert result.id == created_entry.id
        assert result.account_name == edit_data["account_name"].upper()
        assert result.month == edit_data["month"]
        assert result.year == edit_data["year"]
        assert result.starting_balance == edit_data["starting_balance"]
        assert result.current_balance == edit_data["current_balance"]
        assert result.current_credit == edit_data["current_credit"]
        assert result.balance_after_credit == edit_data["current_balance"] - edit_data["current_credit"]
        assert (
            result.total_spent
            == (edit_data["starting_balance"] - edit_data["current_balance"]) + edit_data["current_credit"]
        )

    @pytest.mark.asyncio
    async def test__edit_entry__account_not_found(
        self,
        spending_account_service,
    ):
        """Test editing entry with non-existent account raises error."""
        account = await add_account(spending_account_service, account_name=f"EditAccount-{uuid4()}")
        entry_data = get_entry_data(account_name=account.account_name)
        created_entry = await add_entry(spending_account_service, entry_data)

        # Try to edit with a non-existent account name
        edit_data = get_entry_data(account_name=f"NonExistent-{uuid4()}")
        edit_entry = FlattenedSpendingAccountEntry(id=created_entry.id, **edit_data)

        with pytest.raises(AccountWithNameNotFoundError):
            await spending_account_service.edit_entry(entry_id=created_entry.id, entry=edit_entry)

    @pytest.mark.asyncio
    async def test__edit_entry__duplicate_month_year_for_account(
        self,
        spending_account_service,
    ):
        """Test editing entry with duplicate month/year for account raises error."""
        await delete_all_entries(spending_account_service)
        account = await add_account(spending_account_service, account_name=f"EditAccount-{uuid4()}")
        entry_data1 = get_entry_data(account_name=account.account_name, month="June", year=2025)
        entry_data2 = get_entry_data(account_name=account.account_name, month="July", year=2025)
        entry1 = await add_entry(spending_account_service, entry_data1)
        entry2 = await add_entry(spending_account_service, entry_data2)

        # Try to edit entry2 to have same month/year as entry1
        edit_entry = FlattenedSpendingAccountEntry(
            id=entry2.id,
            account_name=account.account_name,
            month="June",
            year=2025,
            starting_balance=1500.0,
            current_balance=1400.0,
            current_credit=100.0,
        )

        with pytest.raises(MonthYearAlreadyExistsForAccountError):
            await spending_account_service.edit_entry(entry_id=entry2.id, entry=edit_entry)

    @pytest.mark.asyncio
    async def test__edit_entry__entry_not_found(
        self,
        spending_account_service,
    ):
        """Test editing a non-existent entry raises error."""
        await delete_all_entries(spending_account_service)
        account = await add_account(spending_account_service)

        edit_data = get_entry_data(account_name=account.account_name)
        edit_entry = FlattenedSpendingAccountEntry(id=f"non-existent-id-{uuid4()}", **edit_data)

        with pytest.raises(SpendingAccountEntryNotFoundError):
            await spending_account_service.edit_entry(entry_id=edit_entry.id, entry=edit_entry)


class TestDeleteSpendingAccountEntry:
    @pytest.mark.asyncio
    async def test__delete_entry__success(
        self,
        spending_account_service,
    ):
        """Test successfully deleting a spending account entry."""
        account = await add_account(spending_account_service, account_name=f"DeleteAccount-{uuid4()}")
        entry_data = get_entry_data(account_name=account.account_name)
        created_entry = await add_entry(spending_account_service, entry_data)

        # Delete the entry
        await spending_account_service.delete_entry(entry_id=created_entry.id)

        # Verify deletion
        with pytest.raises(EntitySpendingAccountEntryNotFoundError):
            await spending_account_service.spending_account_repository.get_entry_by_id(created_entry.id)

    @pytest.mark.asyncio
    async def test__delete_entry__entry_not_found(
        self,
        spending_account_service,
    ):
        """Test deleting a non-existent entry raises error."""
        fake_entry_id = f"non-existent-id-{uuid4()}"

        with pytest.raises(SpendingAccountEntryNotFoundError):
            await spending_account_service.delete_entry(entry_id=fake_entry_id)
