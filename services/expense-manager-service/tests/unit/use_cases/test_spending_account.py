"""Unit tests for SpendingAccount use cases."""

from typing import TYPE_CHECKING
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

if TYPE_CHECKING:
    from app.entities.repositories.accounts import AccountRepositoryInterface
    from app.entities.repositories.spending_account import SpendingAccountRepositoryInterface


@pytest.fixture(scope="module")
def account_service(account_repo: "AccountRepositoryInterface") -> AccountService:
    """Provide an instance of AccountService."""
    return AccountService(account_repository=account_repo)


@pytest.fixture(scope="module")
def spending_account_service(
    account_repo: "AccountRepositoryInterface", spending_account_repo: "SpendingAccountRepositoryInterface"
) -> SpendingAccountService:
    """Provide an instance of SpendingAccountService."""
    return SpendingAccountService(
        account_repository=account_repo,
        spending_account_repository=spending_account_repo,
    )


async def add_account(account_service: AccountService, account_name="Spending Account Test"):
    account = await account_service.account_repository.get_or_create_account(account_name=account_name)
    return account


def get_entry_data(
    account_name="Spending Account Test",
    month=9,
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


async def delete_all_entries(spending_account_service: "SpendingAccountService"):
    """Helper function to delete all entries in the repository."""
    # Keep deleting until no entries remain (handle pagination)
    while True:
        paginated_entries = await spending_account_service.spending_account_repository.get_all_entries(limit=100)
        if not paginated_entries.entries:
            break
        for entry in paginated_entries.entries:
            await spending_account_service.spending_account_repository.delete_entry(entry.id)


async def add_entry(spending_account_service: "SpendingAccountService", entry_data):
    entry = FlattenedSpendingAccountEntryCreate(**entry_data)
    return await spending_account_service.add_entry(entry)


async def create_multiple_entries(
    spending_account_service: "SpendingAccountService",
    account_name: str,
    count: int,
    start_month: int = 1,
    start_year: int = 2024,
):
    """Helper function to create multiple entries for testing pagination."""
    entries = []
    month = start_month
    year = start_year

    for i in range(count):
        entry_data = get_entry_data(
            account_name=account_name,
            month=month,
            year=year,
            starting_balance=1000.0 + (i * 10),
            current_balance=800.0 + (i * 10),
            current_credit=100.0 + (i * 5),
        )
        created_entry = await add_entry(spending_account_service, entry_data)
        entries.append(created_entry)

        # Increment month, handle year rollover
        month += 1
        if month > 12:
            month = 1
            year += 1

    return entries


class TestAddSpendingAccountEntry:
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

    async def test__add_entry__duplicate_month_year_for_account(
        self,
        spending_account_service,
    ):
        """Test adding entry with duplicate month/year for account raises error."""
        await delete_all_entries(spending_account_service)
        await add_account(spending_account_service)
        entry_data = get_entry_data(account_name="Spending Account Test", month=10, year=2025)
        entry = FlattenedSpendingAccountEntryCreate(**entry_data)

        # Add first entry
        await spending_account_service.add_entry(entry=entry)

        # Try to add duplicate
        with pytest.raises(MonthYearAlreadyExistsForAccountError):
            await spending_account_service.add_entry(entry=entry)

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
    async def test__get_all_entries__success(
        self,
        spending_account_service,
    ):
        """Test retrieving all spending account entries."""
        await delete_all_entries(spending_account_service)
        await add_account(spending_account_service)
        entry_data1 = get_entry_data(month=11, year=2025)
        entry_data2 = get_entry_data(month=12, year=2025)
        await add_entry(spending_account_service, entry_data1)
        await add_entry(spending_account_service, entry_data2)
        num_entries = 2

        results = await spending_account_service.get_all_entries()

        assert results is not None
        assert results.total_entries == num_entries
        assert len(results.entries) == num_entries

    async def test__get_all_entries__empty(
        self,
        spending_account_service,
    ):
        """Test retrieving all entries when none exist."""
        await delete_all_entries(spending_account_service)

        results = await spending_account_service.get_all_entries()

        assert results.total_entries == 0
        assert results.entries == []

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
        assert results.total_entries == 1
        assert len(results.entries) == 1
        result = results.entries[0]
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

    async def test__get_all_entries__with_custom_limit_offset(
        self,
        spending_account_service,
    ):
        """Test retrieving entries with custom limit and offset."""
        await delete_all_entries(spending_account_service)
        account = await add_account(spending_account_service, account_name=f"PaginationTest-{uuid4()}")

        # Create 25 entries
        await create_multiple_entries(spending_account_service, account.account_name, 25)

        # First page: limit=10, offset=0
        page1 = await spending_account_service.get_all_entries(limit=10, offset=0)
        assert page1.total_entries == 25
        assert page1.limit == 10
        assert page1.offset == 0
        assert len(page1.entries) == 10

        # Second page: limit=10, offset=10
        page2 = await spending_account_service.get_all_entries(limit=10, offset=10)
        assert page2.total_entries == 25
        assert page2.limit == 10
        assert page2.offset == 10
        assert len(page2.entries) == 10

        # Third page: limit=10, offset=20 (partial page)
        page3 = await spending_account_service.get_all_entries(limit=10, offset=20)
        assert page3.total_entries == 25
        assert page3.limit == 10
        assert page3.offset == 20
        assert len(page3.entries) == 5

    async def test__get_all_entries__offset_beyond_total(
        self,
        spending_account_service,
    ):
        """Test retrieving entries with offset beyond total entries."""
        await delete_all_entries(spending_account_service)
        account = await add_account(spending_account_service, account_name=f"OffsetTest-{uuid4()}")

        # Create 5 entries
        await create_multiple_entries(spending_account_service, account.account_name, 5)

        # Request with offset beyond total
        results = await spending_account_service.get_all_entries(limit=10, offset=10)
        assert results.total_entries == 5
        assert results.limit == 10
        assert results.offset == 10
        assert len(results.entries) == 0

    async def test__get_all_entries__pagination_metadata_accuracy(
        self,
        spending_account_service,
    ):
        """Test pagination metadata accuracy."""
        await delete_all_entries(spending_account_service)
        account = await add_account(spending_account_service, account_name=f"MetadataTest-{uuid4()}")

        # Create 30 entries
        await create_multiple_entries(spending_account_service, account.account_name, 30)

        results = await spending_account_service.get_all_entries(limit=12, offset=0)

        assert results.total_entries == 30
        assert results.limit == 12
        assert results.offset == 0
        assert len(results.entries) == 12
        # Verify all entries have required fields
        for entry in results.entries:
            assert entry.id is not None
            assert entry.account_name is not None
            assert entry.balance_after_credit is not None
            assert entry.total_spent is not None

    async def test__get_all_entries__default_pagination(
        self,
        spending_account_service,
    ):
        """Test default pagination values."""
        await delete_all_entries(spending_account_service)
        account = await add_account(spending_account_service, account_name=f"DefaultTest-{uuid4()}")

        # Create 15 entries
        await create_multiple_entries(spending_account_service, account.account_name, 15)

        # Call without pagination parameters (should use defaults)
        results = await spending_account_service.get_all_entries()

        assert results.total_entries == 15
        assert results.limit == 12  # Default limit
        assert results.offset == 0  # Default offset
        assert len(results.entries) == 12  # Only first 12 returned

    async def test__get_all_entries__last_page_partial_results(
        self,
        spending_account_service,
    ):
        """Test last page returns partial results correctly."""
        await delete_all_entries(spending_account_service)
        account = await add_account(spending_account_service, account_name=f"PartialTest-{uuid4()}")

        # Create 23 entries
        await create_multiple_entries(spending_account_service, account.account_name, 23)

        # Get last page
        results = await spending_account_service.get_all_entries(limit=10, offset=20)

        assert results.total_entries == 23
        assert results.limit == 10
        assert results.offset == 20
        assert len(results.entries) == 3  # Only 3 entries remain


class TestGetAllEntriesForAccount:
    async def test__get_all_entries_for_account__success(
        self,
        spending_account_service,
    ):
        """Test retrieving all entries for a specific account."""
        # Clean up and add account
        await delete_all_entries(spending_account_service)
        account1 = await add_account(spending_account_service, account_name="Account1")
        account2 = await add_account(spending_account_service, account_name="Account2")
        entry_data1 = get_entry_data(account_name=account1.account_name, month=1, year=2025)
        entry_data2 = get_entry_data(account_name=account1.account_name, month=2, year=2025)
        entry_data3 = get_entry_data(account_name=account2.account_name, month=1, year=2025)
        entry_data4 = get_entry_data(account_name=account2.account_name, month=2, year=2025)
        await add_entry(spending_account_service, entry_data1)
        await add_entry(spending_account_service, entry_data2)
        await add_entry(spending_account_service, entry_data3)
        await add_entry(spending_account_service, entry_data4)
        num_entries = 2

        results = await spending_account_service.get_all_entries_for_account(account_id=account1.id)

        assert results is not None
        assert results.total_entries == num_entries
        assert len(results.entries) == num_entries
        for result in results.entries:
            assert result.account_name == account1.account_name.upper()
            assert result.id is not None

    async def test__get_all_entries_for_account__empty(
        self,
        spending_account_service,
    ):
        """Test retrieving entries for an account with no entries."""
        await delete_all_entries(spending_account_service)
        account = await add_account(spending_account_service)

        results = await spending_account_service.get_all_entries_for_account(account_id=account.id)

        assert results.total_entries == 0
        assert results.entries == []

    async def test__get_all_entries_for_account__account_not_found(
        self,
        spending_account_service,
    ):
        """Test retrieving entries for a non-existent account raises error."""
        fake_account_id = f"non-existent-id-{uuid4()}"

        with pytest.raises(AccountNotFoundError):
            await spending_account_service.get_all_entries_for_account(account_id=fake_account_id)

    async def test__get_all_entries_for_account__with_pagination(
        self,
        spending_account_service,
    ):
        """Test account-specific pagination with multiple accounts."""
        await delete_all_entries(spending_account_service)
        account1 = await add_account(spending_account_service, account_name=f"PaginationAccount1-{uuid4()}")
        account2 = await add_account(spending_account_service, account_name=f"PaginationAccount2-{uuid4()}")

        # Create 20 entries for account1, 15 for account2
        await create_multiple_entries(spending_account_service, account1.account_name, 20)
        await create_multiple_entries(spending_account_service, account2.account_name, 15)

        # Get first page for account1
        page1 = await spending_account_service.get_all_entries_for_account(account_id=account1.id, limit=5, offset=0)
        assert page1.total_entries == 20
        assert page1.limit == 5
        assert page1.offset == 0
        assert len(page1.entries) == 5
        # Verify all entries belong to account1
        for entry in page1.entries:
            assert entry.account_name == account1.account_name.upper()

        # Get fourth page for account1
        page4 = await spending_account_service.get_all_entries_for_account(account_id=account1.id, limit=5, offset=15)
        assert page4.total_entries == 20
        assert len(page4.entries) == 5

        # Verify account2 has correct total
        account2_results = await spending_account_service.get_all_entries_for_account(
            account_id=account2.id, limit=10, offset=0
        )
        assert account2_results.total_entries == 15
        assert len(account2_results.entries) == 10

    async def test__get_all_entries_for_account__multiple_pages_navigation(
        self,
        spending_account_service,
    ):
        """Test navigating through multiple pages for one account."""
        await delete_all_entries(spending_account_service)
        account = await add_account(spending_account_service, account_name=f"NavTest-{uuid4()}")

        # Create 18 entries
        created_entries = await create_multiple_entries(spending_account_service, account.account_name, 18)

        # Navigate through pages
        page_size = 5
        all_retrieved_ids = []

        for page_num in range(4):  # 4 pages: 5+5+5+3
            offset = page_num * page_size
            page = await spending_account_service.get_all_entries_for_account(
                account_id=account.id, limit=page_size, offset=offset
            )

            assert page.total_entries == 18
            assert page.limit == page_size
            assert page.offset == offset

            # Collect IDs
            for entry in page.entries:
                all_retrieved_ids.append(entry.id)

        # Verify we got all entries without duplicates
        assert len(all_retrieved_ids) == 18
        assert len(set(all_retrieved_ids)) == 18  # No duplicates

    async def test__get_all_entries_for_account__exact_limit_entries(
        self,
        spending_account_service,
    ):
        """Test account with exactly limit number of entries."""
        await delete_all_entries(spending_account_service)
        account = await add_account(spending_account_service, account_name=f"ExactTest-{uuid4()}")

        # Create exactly 10 entries
        await create_multiple_entries(spending_account_service, account.account_name, 10)

        results = await spending_account_service.get_all_entries_for_account(account_id=account.id, limit=10, offset=0)

        assert results.total_entries == 10
        assert results.limit == 10
        assert results.offset == 0
        assert len(results.entries) == 10

        # Request second page (should be empty)
        page2 = await spending_account_service.get_all_entries_for_account(account_id=account.id, limit=10, offset=10)
        assert page2.total_entries == 10
        assert len(page2.entries) == 0

    async def test__get_all_entries_for_account__default_pagination_parameters(
        self,
        spending_account_service,
    ):
        """Test default pagination parameters for account entries."""
        await delete_all_entries(spending_account_service)
        account = await add_account(spending_account_service, account_name=f"DefaultAccount-{uuid4()}")

        # Create 20 entries
        await create_multiple_entries(spending_account_service, account.account_name, 20)

        # Call without explicit pagination (should use defaults)
        results = await spending_account_service.get_all_entries_for_account(account_id=account.id)

        assert results.total_entries == 20
        assert results.limit == 12  # Default limit
        assert results.offset == 0  # Default offset
        assert len(results.entries) == 12


class TestEditSpendingAccountEntry:
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
            month=4,
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

    async def test__edit_entry__duplicate_month_year_for_account(
        self,
        spending_account_service,
    ):
        """Test editing entry with duplicate month/year for account raises error."""
        await delete_all_entries(spending_account_service)
        account = await add_account(spending_account_service, account_name=f"EditAccount-{uuid4()}")
        entry_data1 = get_entry_data(account_name=account.account_name, month=6, year=2025)
        entry_data2 = get_entry_data(account_name=account.account_name, month=7, year=2025)
        entry1 = await add_entry(spending_account_service, entry_data1)
        entry2 = await add_entry(spending_account_service, entry_data2)

        # Try to edit entry2 to have same month/year as entry1
        edit_entry = FlattenedSpendingAccountEntry(
            id=entry2.id,
            account_name=account.account_name,
            month=6,
            year=2025,
            starting_balance=1500.0,
            current_balance=1400.0,
            current_credit=100.0,
        )

        with pytest.raises(MonthYearAlreadyExistsForAccountError):
            await spending_account_service.edit_entry(entry_id=entry2.id, entry=edit_entry)

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

    async def test__delete_entry__entry_not_found(
        self,
        spending_account_service,
    ):
        """Test deleting a non-existent entry raises error."""
        fake_entry_id = f"non-existent-id-{uuid4()}"

        with pytest.raises(SpendingAccountEntryNotFoundError):
            await spending_account_service.delete_entry(entry_id=fake_entry_id)


class TestPaginationBoundaryConditions:
    """Test boundary conditions for pagination."""

    async def test__pagination__zero_entries(
        self,
        spending_account_service,
    ):
        """Test pagination with zero entries."""
        await delete_all_entries(spending_account_service)

        results = await spending_account_service.get_all_entries(limit=10, offset=0)

        assert results.total_entries == 0
        assert results.limit == 10
        assert results.offset == 0
        assert results.entries == []

    async def test__pagination__single_entry(
        self,
        spending_account_service,
    ):
        """Test pagination with a single entry."""
        await delete_all_entries(spending_account_service)
        account = await add_account(spending_account_service, account_name=f"SingleEntry-{uuid4()}")
        await create_multiple_entries(spending_account_service, account.account_name, 1)

        results = await spending_account_service.get_all_entries(limit=10, offset=0)

        assert results.total_entries == 1
        assert results.limit == 10
        assert results.offset == 0
        assert len(results.entries) == 1

    async def test__pagination__limit_one_with_multiple_entries(
        self,
        spending_account_service,
    ):
        """Test pagination with limit=1 and multiple entries."""
        await delete_all_entries(spending_account_service)
        account = await add_account(spending_account_service, account_name=f"LimitOne-{uuid4()}")
        await create_multiple_entries(spending_account_service, account.account_name, 10)

        results = await spending_account_service.get_all_entries(limit=1, offset=0)

        assert results.total_entries == 10
        assert results.limit == 1
        assert results.offset == 0
        assert len(results.entries) == 1

        # Get second entry
        results2 = await spending_account_service.get_all_entries(limit=1, offset=1)
        assert results2.total_entries == 10
        assert len(results2.entries) == 1
        # Verify different entry
        assert results.entries[0].id != results2.entries[0].id

    async def test__pagination__very_large_limit(
        self,
        spending_account_service,
    ):
        """Test pagination with very large limit value."""
        await delete_all_entries(spending_account_service)
        account = await add_account(spending_account_service, account_name=f"LargeLimit-{uuid4()}")
        await create_multiple_entries(spending_account_service, account.account_name, 10)

        results = await spending_account_service.get_all_entries(limit=1000, offset=0)

        assert results.total_entries == 10
        assert results.limit == 1000
        assert results.offset == 0
        assert len(results.entries) == 10  # Only 10 entries exist

    async def test__pagination__limit_exceeds_total_entries(
        self,
        spending_account_service,
    ):
        """Test pagination where limit exceeds total entries."""
        await delete_all_entries(spending_account_service)
        account = await add_account(spending_account_service, account_name=f"ExceedLimit-{uuid4()}")
        await create_multiple_entries(spending_account_service, account.account_name, 5)

        results = await spending_account_service.get_all_entries(limit=20, offset=0)

        assert results.total_entries == 5
        assert results.limit == 20
        assert results.offset == 0
        assert len(results.entries) == 5

    async def test__pagination__offset_at_last_entry(
        self,
        spending_account_service,
    ):
        """Test pagination with offset at the last entry."""
        await delete_all_entries(spending_account_service)
        account = await add_account(spending_account_service, account_name=f"LastEntry-{uuid4()}")
        await create_multiple_entries(spending_account_service, account.account_name, 10)

        results = await spending_account_service.get_all_entries(limit=5, offset=9)

        assert results.total_entries == 10
        assert results.limit == 5
        assert results.offset == 9
        assert len(results.entries) == 1  # Only last entry

    async def test__pagination__account_specific_zero_entries(
        self,
        spending_account_service,
    ):
        """Test account-specific pagination with zero entries."""
        await delete_all_entries(spending_account_service)
        account1 = await add_account(spending_account_service, account_name=f"EmptyAccount-{uuid4()}")
        account2 = await add_account(spending_account_service, account_name=f"FilledAccount-{uuid4()}")

        # Add entries to account2 only
        await create_multiple_entries(spending_account_service, account2.account_name, 10)

        # Query account1 (no entries)
        results = await spending_account_service.get_all_entries_for_account(account_id=account1.id, limit=10, offset=0)

        assert results.total_entries == 0
        assert results.limit == 10
        assert results.offset == 0
        assert results.entries == []

    async def test__pagination__consecutive_pages_no_gaps(
        self,
        spending_account_service,
    ):
        """Test that consecutive pages have no gaps or overlaps."""
        await delete_all_entries(spending_account_service)
        account = await add_account(spending_account_service, account_name=f"ConsecutiveTest-{uuid4()}")
        created_entries = await create_multiple_entries(spending_account_service, account.account_name, 15)

        # Get all entry IDs from created entries
        created_ids = {entry.id for entry in created_entries}

        # Fetch in pages
        page1 = await spending_account_service.get_all_entries_for_account(account_id=account.id, limit=5, offset=0)
        page2 = await spending_account_service.get_all_entries_for_account(account_id=account.id, limit=5, offset=5)
        page3 = await spending_account_service.get_all_entries_for_account(account_id=account.id, limit=5, offset=10)

        # Collect all retrieved IDs
        page1_ids = {entry.id for entry in page1.entries}
        page2_ids = {entry.id for entry in page2.entries}
        page3_ids = {entry.id for entry in page3.entries}

        # Verify no overlaps
        assert len(page1_ids & page2_ids) == 0  # No overlap between page 1 and 2
        assert len(page2_ids & page3_ids) == 0  # No overlap between page 2 and 3
        assert len(page1_ids & page3_ids) == 0  # No overlap between page 1 and 3

        # Verify all entries retrieved
        all_retrieved_ids = page1_ids | page2_ids | page3_ids
        assert len(all_retrieved_ids) == 15
        assert all_retrieved_ids == created_ids
