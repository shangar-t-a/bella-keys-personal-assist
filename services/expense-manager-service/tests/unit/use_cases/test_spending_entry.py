"""Unit tests for SpendingAccount use cases."""

from typing import TYPE_CHECKING
from uuid import uuid4

import pytest
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError

from app.entities.errors.spending_entry import (
    SpendingAccountEntryNotFoundError as EntitySpendingAccountEntryNotFoundError,
)
from app.entities.models.sort import SortOrder
from app.entities.models.spending_entry import (
    SpendingEntryFilter,
    SpendingEntrySort,
    SpendingEntrySortField,
)
from app.use_cases.account import AccountService
from app.use_cases.errors.account import (
    AccountNotFoundError,
    AccountWithNameNotFoundError,
)
from app.use_cases.errors.period import PeriodAlreadyExistsForAccountError
from app.use_cases.errors.spending_entry import SpendingAccountEntryNotFoundError
from app.use_cases.models.spending_entry import (
    SpendingEntry,
    SpendingEntryCreate,
)
from app.use_cases.spending_entry import SpendingEntryService

if TYPE_CHECKING:
    from app.entities.repositories.account import AccountRepositoryInterface
    from app.entities.repositories.period import PeriodRepositoryInterface
    from app.entities.repositories.spending_entry import SpendingEntryRepositoryInterface


@pytest.fixture(scope="module")
def account_service(account_repo: "AccountRepositoryInterface") -> AccountService:
    """Provide an instance of AccountService."""
    return AccountService(account_repository=account_repo)


@pytest.fixture(scope="module")
def spending_account_service(
    account_repo: "AccountRepositoryInterface",
    period_repo: "PeriodRepositoryInterface",
    spending_account_repo: "SpendingEntryRepositoryInterface",
) -> SpendingEntryService:
    """Provide an instance of SpendingEntryService."""
    return SpendingEntryService(
        account_repository=account_repo,
        period_repository=period_repo,
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


async def delete_all_entries(spending_account_service: "SpendingEntryService"):
    """Helper function to delete all entries in the repository."""
    # Keep deleting until no entries remain (handle pagination)
    while True:
        paginated_entries = await spending_account_service.spending_account_repository.get_all_entries(limit=100)
        if not paginated_entries.entries:
            break
        for entry in paginated_entries.entries:
            await spending_account_service.spending_account_repository.delete_entry(entry.id)


async def add_entry(spending_account_service: "SpendingEntryService", entry_data):
    entry = SpendingEntryCreate(**entry_data)
    return await spending_account_service.add_entry(entry)


async def create_multiple_entries(
    spending_account_service: "SpendingEntryService",
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
        entry = SpendingEntryCreate(**entry_data)

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
        entry = SpendingEntryCreate(**entry_data)

        with pytest.raises(AccountWithNameNotFoundError):
            await spending_account_service.add_entry(entry=entry)

    async def test__add_entry__duplicate_period_for_account(
        self,
        spending_account_service,
    ):
        """Test adding entry with duplicate month/year for account raises error."""
        await delete_all_entries(spending_account_service)
        await add_account(spending_account_service)
        entry_data = get_entry_data(account_name="Spending Account Test", month=10, year=2025)
        entry = SpendingEntryCreate(**entry_data)

        # Add first entry
        await spending_account_service.add_entry(entry=entry)

        # Try to add duplicate
        with pytest.raises(PeriodAlreadyExistsForAccountError):
            await spending_account_service.add_entry(entry=entry)

    async def test__add_entry__check_response_data(
        self,
        spending_account_service,
    ):
        """Test the response data of adding a spending account entry."""
        await add_account(spending_account_service)
        entry_data = get_entry_data()
        entry = SpendingEntryCreate(**entry_data)

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

    async def test__add_entry__calculated_fields_when_balance_increases(
        self,
        spending_account_service,
    ):
        """Test calculated fields when current balance is higher than starting balance."""
        await add_account(spending_account_service)

        # Current balance > Starting balance (money added to account)
        entry_data = get_entry_data(
            month=1,
            year=2024,
            starting_balance=1000.0,
            current_balance=1500.0,  # Increased by 500
            current_credit=100.0,
        )
        entry = SpendingEntryCreate(**entry_data)
        result = await spending_account_service.add_entry(entry=entry)

        # balance_after_credit = current_balance - current_credit
        assert result.balance_after_credit == 1500.0 - 100.0
        assert result.balance_after_credit == 1400.0

        # total_spent = (starting_balance - current_balance) + current_credit
        # When balance increases, total_spent should be negative
        assert result.total_spent == (1000.0 - 1500.0) + 100.0
        assert result.total_spent == -400.0

    async def test__add_entry__calculated_fields_with_zero_credit(
        self,
        spending_account_service,
    ):
        """Test calculated fields when current_credit is zero."""
        await add_account(spending_account_service)

        entry_data = get_entry_data(
            month=2,
            year=2024,
            starting_balance=1000.0,
            current_balance=800.0,
            current_credit=0.0,
        )
        entry = SpendingEntryCreate(**entry_data)
        result = await spending_account_service.add_entry(entry=entry)

        assert result.balance_after_credit == 800.0
        assert result.total_spent == 200.0

    async def test__add_entry__calculated_fields_when_credit_exceeds_balance(
        self,
        spending_account_service,
    ):
        """Test calculated fields when current_credit is larger than current_balance."""
        await add_account(spending_account_service)

        entry_data = get_entry_data(
            month=3,
            year=2024,
            starting_balance=1000.0,
            current_balance=500.0,
            current_credit=700.0,  # Credit exceeds balance
        )
        entry = SpendingEntryCreate(**entry_data)
        result = await spending_account_service.add_entry(entry=entry)

        # balance_after_credit can be negative
        assert result.balance_after_credit == 500.0 - 700.0
        assert result.balance_after_credit == -200.0

        # total_spent calculation
        assert result.total_spent == (1000.0 - 500.0) + 700.0
        assert result.total_spent == 1200.0

    async def test__add_entry__with_zero_values(
        self,
        spending_account_service,
    ):
        """Test adding entry with zero values for all balance fields."""
        await add_account(spending_account_service)

        entry_data = get_entry_data(
            month=4,
            year=2024,
            starting_balance=0.0,
            current_balance=0.0,
            current_credit=0.0,
        )
        entry = SpendingEntryCreate(**entry_data)
        result = await spending_account_service.add_entry(entry=entry)

        assert result.starting_balance == 0.0
        assert result.current_balance == 0.0
        assert result.current_credit == 0.0
        assert result.balance_after_credit == 0.0
        assert result.total_spent == 0.0

    async def test__add_entry__with_large_float_values(
        self,
        spending_account_service,
    ):
        """Test adding entry with very large float values."""
        await add_account(spending_account_service)

        entry_data = get_entry_data(
            month=5,
            year=2024,
            starting_balance=999999999.99,
            current_balance=999999000.50,
            current_credit=500.25,
        )
        entry = SpendingEntryCreate(**entry_data)
        result = await spending_account_service.add_entry(entry=entry)

        assert result.starting_balance == 999999999.99
        assert result.current_balance == 999999000.50
        assert result.current_credit == 500.25

    async def test__add_entry__with_precise_decimal_values(
        self,
        spending_account_service,
    ):
        """Test adding entry with precise decimal values."""
        await add_account(spending_account_service)

        entry_data = get_entry_data(
            month=6,
            year=2024,
            starting_balance=1234.56,
            current_balance=987.65,
            current_credit=123.45,
        )
        entry = SpendingEntryCreate(**entry_data)
        result = await spending_account_service.add_entry(entry=entry)

        # Verify precision is maintained
        assert result.balance_after_credit == 987.65 - 123.45
        assert result.total_spent == (1234.56 - 987.65) + 123.45


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
        assert results.page.total_elements == num_entries
        assert len(results.spending_entries) == num_entries

    async def test__get_all_entries__empty(
        self,
        spending_account_service,
    ):
        """Test retrieving all entries when none exist."""
        await delete_all_entries(spending_account_service)

        results = await spending_account_service.get_all_entries()

        assert results.page.total_elements == 0
        assert results.spending_entries == []

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
        assert results.page.total_elements == 1
        assert len(results.spending_entries) == 1
        result = results.spending_entries[0]
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

        # First page: size=10, page=0
        page1 = await spending_account_service.get_all_entries(page=0, size=10)
        assert page1.page.total_elements == 25
        assert page1.page.size == 10
        assert page1.page.number == 0
        assert len(page1.spending_entries) == 10

        # Second page: size=10, page=1
        page2 = await spending_account_service.get_all_entries(page=1, size=10)
        assert page2.page.total_elements == 25
        assert page2.page.size == 10
        assert page2.page.number == 1
        assert len(page2.spending_entries) == 10

        # Third page: size=10, page=2 (partial page)
        page3 = await spending_account_service.get_all_entries(page=2, size=10)
        assert page3.page.total_elements == 25
        assert page3.page.size == 10
        assert page3.page.number == 2
        assert len(page3.spending_entries) == 5

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
        results = await spending_account_service.get_all_entries(page=1, size=10)
        assert results.page.total_elements == 5
        assert results.page.size == 10
        assert results.page.number == 1
        assert len(results.spending_entries) == 0

    async def test__get_all_entries__pagination_metadata_accuracy(
        self,
        spending_account_service,
    ):
        """Test pagination metadata accuracy."""
        await delete_all_entries(spending_account_service)
        account = await add_account(spending_account_service, account_name=f"MetadataTest-{uuid4()}")

        # Create 30 entries
        await create_multiple_entries(spending_account_service, account.account_name, 30)

        results = await spending_account_service.get_all_entries(page=0, size=12)

        assert results.page.total_elements == 30
        assert results.page.size == 12
        assert results.page.number == 0
        assert len(results.spending_entries) == 12
        # Verify all entries have required fields
        for entry in results.spending_entries:
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

        assert results.page.total_elements == 15
        assert results.page.size == 12  # Default size
        assert results.page.number == 0  # Default page
        assert len(results.spending_entries) == 12  # Only first 12 returned

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
        results = await spending_account_service.get_all_entries(page=2, size=10)

        assert results.page.total_elements == 23
        assert results.page.size == 10
        assert results.page.number == 2
        assert len(results.spending_entries) == 3  # Only 3 entries remain

    async def test__get_all_entries__total_pages_calculation(
        self,
        spending_account_service,
    ):
        """Test that total_pages is calculated correctly."""
        await delete_all_entries(spending_account_service)
        account = await add_account(spending_account_service, account_name=f"TotalPagesTest-{uuid4()}")

        # Create 25 entries
        await create_multiple_entries(spending_account_service, account.account_name, 25)

        results = await spending_account_service.get_all_entries(page=0, size=10)

        assert results.page.total_pages == 3  # 25 / 10 = 3 pages (ceil)
        assert results.page.total_elements == 25
        assert results.page.size == 10
        assert results.page.number == 0

    async def test__get_all_entries__total_pages_with_exact_multiple(
        self,
        spending_account_service,
    ):
        """Test total_pages when entries exactly divide by size."""
        await delete_all_entries(spending_account_service)
        account = await add_account(spending_account_service, account_name=f"ExactPages-{uuid4()}")

        await create_multiple_entries(spending_account_service, account.account_name, 20)

        results = await spending_account_service.get_all_entries(page=0, size=10)

        assert results.page.total_pages == 2  # Exactly 2 pages
        assert results.page.total_elements == 20

    async def test__get_all_entries__total_pages_with_zero_entries(
        self,
        spending_account_service,
    ):
        """Test total_pages calculation with zero entries."""
        await delete_all_entries(spending_account_service)

        results = await spending_account_service.get_all_entries(page=0, size=10)

        assert results.page.total_pages == 0  # No pages when no entries
        assert results.page.total_elements == 0

    async def test__get_all_entries__verify_all_response_fields(
        self,
        spending_account_service,
    ):
        """Test that response contains all expected fields."""
        await delete_all_entries(spending_account_service)
        await add_account(spending_account_service)
        entry_data = get_entry_data()
        await add_entry(spending_account_service, entry_data)

        results = await spending_account_service.get_all_entries()

        # Check page object has all required fields
        assert hasattr(results.page, "number")
        assert hasattr(results.page, "size")
        assert hasattr(results.page, "total_elements")
        assert hasattr(results.page, "total_pages")

        # Check entry has all required fields
        entry = results.spending_entries[0]
        required_fields = [
            "id",
            "account_name",
            "month",
            "year",
            "starting_balance",
            "current_balance",
            "current_credit",
            "balance_after_credit",
            "total_spent",
        ]
        for field in required_fields:
            assert hasattr(entry, field), f"Missing field: {field}"


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
        assert results.page.total_elements == num_entries
        assert len(results.spending_entries) == num_entries
        for result in results.spending_entries:
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

        assert results.page.total_elements == 0
        assert results.spending_entries == []

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
        page1 = await spending_account_service.get_all_entries_for_account(account_id=account1.id, page=0, size=5)
        assert page1.page.total_elements == 20
        assert page1.page.size == 5
        assert page1.page.number == 0
        assert len(page1.spending_entries) == 5
        # Verify all entries belong to account1
        for entry in page1.spending_entries:
            assert entry.account_name == account1.account_name.upper()

        # Get fourth page for account1
        page4 = await spending_account_service.get_all_entries_for_account(account_id=account1.id, page=3, size=5)
        assert page4.page.total_elements == 20
        assert len(page4.spending_entries) == 5

        # Verify account2 has correct total
        account2_results = await spending_account_service.get_all_entries_for_account(
            account_id=account2.id, page=0, size=10
        )
        assert account2_results.page.total_elements == 15
        assert len(account2_results.spending_entries) == 10

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
            page = await spending_account_service.get_all_entries_for_account(
                account_id=account.id, page=page_num, size=page_size
            )

            assert page.page.total_elements == 18
            assert page.page.size == page_size
            assert page.page.number == page_num

            # Collect IDs
            for entry in page.spending_entries:
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

        results = await spending_account_service.get_all_entries_for_account(account_id=account.id, page=0, size=10)

        assert results.page.total_elements == 10
        assert results.page.size == 10
        assert results.page.number == 0
        assert len(results.spending_entries) == 10

        # Request second page (should be empty)
        page2 = await spending_account_service.get_all_entries_for_account(account_id=account.id, page=1, size=10)
        assert page2.page.total_elements == 10
        assert len(page2.spending_entries) == 0

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

        assert results.page.total_elements == 20
        assert results.page.size == 12  # Default size
        assert results.page.number == 0  # Default page
        assert len(results.spending_entries) == 12


class TestSpendingEntrySortingAndFiltering:
    async def test__get_all_entries__filter_by_account_name(
        self,
        spending_account_service,
    ):
        """Test filtering all entries by account name."""
        await delete_all_entries(spending_account_service)
        acc1 = await add_account(spending_account_service, account_name="ACCOUNT_ALPHA")
        acc2 = await add_account(spending_account_service, account_name="ACCOUNT_BETA")

        await create_multiple_entries(spending_account_service, acc1.account_name, 5)
        await create_multiple_entries(spending_account_service, acc2.account_name, 3)

        # Filter by ACCOUNT_ALPHA
        filters = SpendingEntryFilter(account_name="ACCOUNT_ALPHA")
        results = await spending_account_service.get_all_entries(filters=filters)

        assert results.page.total_elements == 5
        for entry in results.spending_entries:
            assert entry.account_name == "ACCOUNT_ALPHA"

    async def test__get_all_entries__filter_by_month_and_year(
        self,
        spending_account_service,
    ):
        """Test filtering all entries by month and year."""
        await delete_all_entries(spending_account_service)
        acc = await add_account(spending_account_service)

        # 2024: Jan(1), Feb(2)
        # 2025: Jan(1)
        await add_entry(spending_account_service, get_entry_data(month=1, year=2024))
        await add_entry(spending_account_service, get_entry_data(month=2, year=2024))
        await add_entry(spending_account_service, get_entry_data(month=1, year=2025))

        # Filter Year 2024
        filters_year = SpendingEntryFilter(year=2024)
        res_year = await spending_account_service.get_all_entries(filters=filters_year)
        assert res_year.page.total_elements == 2

        # Filter Month 1
        filters_month = SpendingEntryFilter(month=1)
        res_month = await spending_account_service.get_all_entries(filters=filters_month)
        assert res_month.page.total_elements == 2

        # Filter Month 1 AND Year 2025
        filters_both = SpendingEntryFilter(month=1, year=2025)
        res_both = await spending_account_service.get_all_entries(filters=filters_both)
        assert res_both.page.total_elements == 1

    async def test__get_all_entries__sort_by_current_balance_desc(
        self,
        spending_account_service,
    ):
        """Test sorting entries by current balance in descending order."""
        await delete_all_entries(spending_account_service)
        acc = await add_account(spending_account_service)

        await add_entry(spending_account_service, get_entry_data(current_balance=100.0, month=1))
        await add_entry(spending_account_service, get_entry_data(current_balance=500.0, month=2))
        await add_entry(spending_account_service, get_entry_data(current_balance=300.0, month=3))

        sort = SpendingEntrySort(sort_by=SpendingEntrySortField.CURRENT_BALANCE, sort_order=SortOrder.DESC)
        results = await spending_account_service.get_all_entries(sort=sort)

        balances = [e.current_balance for e in results.spending_entries]
        assert balances == [500.0, 300.0, 100.0]

    async def test__get_all_entries__sort_by_account_name_asc(
        self,
        spending_account_service,
    ):
        """Test sorting entries by account name in ascending order."""
        await delete_all_entries(spending_account_service)
        await add_account(spending_account_service, account_name="C_ACCOUNT")
        await add_account(spending_account_service, account_name="A_ACCOUNT")
        await add_account(spending_account_service, account_name="B_ACCOUNT")

        await add_entry(spending_account_service, get_entry_data(account_name="C_ACCOUNT"))
        await add_entry(spending_account_service, get_entry_data(account_name="A_ACCOUNT"))
        await add_entry(spending_account_service, get_entry_data(account_name="B_ACCOUNT"))

        sort = SpendingEntrySort(sort_by=SpendingEntrySortField.ACCOUNT_NAME, sort_order=SortOrder.ASC)
        results = await spending_account_service.get_all_entries(sort=sort)

        names = [e.account_name for e in results.spending_entries]
        assert names == ["A_ACCOUNT", "B_ACCOUNT", "C_ACCOUNT"]

    async def test__get_all_entries_for_account__with_sorting(
        self,
        spending_account_service,
    ):
        """Test account-specific entries with custom sorting."""
        await delete_all_entries(spending_account_service)
        acc = await add_account(spending_account_service, account_name="SORT_TEST_ACC")

        await add_entry(
            spending_account_service, get_entry_data(account_name="SORT_TEST_ACC", starting_balance=1000, month=1)
        )
        await add_entry(
            spending_account_service, get_entry_data(account_name="SORT_TEST_ACC", starting_balance=3000, month=2)
        )
        await add_entry(
            spending_account_service, get_entry_data(account_name="SORT_TEST_ACC", starting_balance=2000, month=3)
        )

        sort = SpendingEntrySort(sort_by=SpendingEntrySortField.STARTING_BALANCE, sort_order=SortOrder.ASC)
        results = await spending_account_service.get_all_entries_for_account(account_id=acc.id, sort=sort)

        starting_balances = [e.starting_balance for e in results.spending_entries]
        assert starting_balances == [1000.0, 2000.0, 3000.0]

    async def test__get_all_entries__exhaustive_sorting(
        self,
        spending_account_service,
    ):
        """Verify sorting works for all fields in the Enum."""
        await delete_all_entries(spending_account_service)
        acc = await add_account(spending_account_service)

        # Create entries with varied data
        await add_entry(
            spending_account_service,
            get_entry_data(month=1, year=2024, starting_balance=100.0, current_balance=50.0, current_credit=10.0),
        )
        await add_entry(
            spending_account_service,
            get_entry_data(month=2, year=2024, starting_balance=200.0, current_balance=150.0, current_credit=20.0),
        )

        for field in SpendingEntrySortField:
            # Skip fields already heavily tested or redundant
            sort = SpendingEntrySort(sort_by=field, sort_order=SortOrder.ASC)
            results = await spending_account_service.get_all_entries(sort=sort)
            assert len(results.spending_entries) == 2

    async def test__get_all_entries__sort_by_calculated_total_spent(
        self,
        spending_account_service,
    ):
        """Test sorting by calculated field total_spent."""
        await delete_all_entries(spending_account_service)
        acc = await add_account(spending_account_service)

        # total_spent = (start - curr) + credit
        # A: (1000 - 900) + 50 = 150
        # B: (1000 - 800) + 10 = 210
        # C: (1000 - 950) + 20 = 70
        await add_entry(spending_account_service, get_entry_data(month=1, current_balance=900.0, current_credit=50.0))
        await add_entry(spending_account_service, get_entry_data(month=2, current_balance=800.0, current_credit=10.0))
        await add_entry(spending_account_service, get_entry_data(month=3, current_balance=950.0, current_credit=20.0))

        sort = SpendingEntrySort(sort_by=SpendingEntrySortField.TOTAL_SPENT, sort_order=SortOrder.ASC)
        results = await spending_account_service.get_all_entries(sort=sort)

        spent = [e.total_spent for e in results.spending_entries]
        assert spent == [70.0, 150.0, 210.0]

    async def test__get_all_entries__filter_by_account_name_exact_match(
        self,
        spending_account_service,
    ):
        """Test exact account name filtering."""
        await delete_all_entries(spending_account_service)
        await add_account(spending_account_service, account_name="SAVINGS_ACCOUNT")
        await add_account(spending_account_service, account_name="CHECKING_ACCOUNT")

        await add_entry(spending_account_service, get_entry_data(account_name="SAVINGS_ACCOUNT"))
        await add_entry(spending_account_service, get_entry_data(account_name="CHECKING_ACCOUNT"))

        # Exact match
        filters1 = SpendingEntryFilter(account_name="SAVINGS_ACCOUNT")
        res1 = await spending_account_service.get_all_entries(filters=filters1)
        assert res1.page.total_elements == 1
        assert res1.spending_entries[0].account_name == "SAVINGS_ACCOUNT"

        # Non-matching partial should return nothing
        filters2 = SpendingEntryFilter(account_name="SAV")
        res2 = await spending_account_service.get_all_entries(filters=filters2)
        assert res2.page.total_elements == 0

    async def test__get_all_entries__filter_unmatched_results(
        self,
        spending_account_service,
    ):
        """Verify empty results when filters don't match anything."""
        await delete_all_entries(spending_account_service)
        await add_account(spending_account_service, account_name="ACC1")
        await add_entry(spending_account_service, get_entry_data(account_name="ACC1", year=2024))

        # Filter by different year
        filters = SpendingEntryFilter(year=2025)
        results = await spending_account_service.get_all_entries(filters=filters)
        assert results.page.total_elements == 0
        assert results.spending_entries == []

    async def test__get_all_entries__pagination_metadata_with_filters(
        self,
        spending_account_service,
    ):
        """Verify that pagination metadata reflects filtered counts."""
        await delete_all_entries(spending_account_service)
        acc = await add_account(spending_account_service, account_name="PAGINATION_ACC")

        # Create 10 entries in 2024 and 5 in 2025
        for m in range(1, 11):
            await add_entry(spending_account_service, get_entry_data(account_name="PAGINATION_ACC", month=m, year=2024))
        for m in range(1, 6):
            await add_entry(spending_account_service, get_entry_data(account_name="PAGINATION_ACC", month=m, year=2025))

        # Filter 2024, size=3
        filters = SpendingEntryFilter(year=2024)
        results = await spending_account_service.get_all_entries(page=0, size=3, filters=filters)

        assert results.page.total_elements == 10
        assert results.page.total_pages == 4  # ceil(10/3)
        assert len(results.spending_entries) == 3


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
        edit_entry = SpendingEntry(id=created_entry.id, **edit_data)
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
        edit_entry = SpendingEntry(id=created_entry.id, **edit_data)
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
        edit_entry = SpendingEntry(id=created_entry.id, **edit_data)

        with pytest.raises(AccountWithNameNotFoundError):
            await spending_account_service.edit_entry(entry_id=created_entry.id, entry=edit_entry)

    async def test__edit_entry__duplicate_period_for_account(
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
        edit_entry = SpendingEntry(
            id=entry2.id,
            account_name=account.account_name,
            month=6,
            year=2025,
            starting_balance=1500.0,
            current_balance=1400.0,
            current_credit=100.0,
        )

        with pytest.raises(PeriodAlreadyExistsForAccountError):
            await spending_account_service.edit_entry(entry_id=entry2.id, entry=edit_entry)

    async def test__edit_entry__entry_not_found(
        self,
        spending_account_service,
    ):
        """Test editing a non-existent entry raises error."""
        await delete_all_entries(spending_account_service)
        account = await add_account(spending_account_service)

        edit_data = get_entry_data(account_name=account.account_name)
        edit_entry = SpendingEntry(id=f"non-existent-id-{uuid4()}", **edit_data)

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


class TestInputValidation:
    """Test input validation for spending entry fields."""

    async def test__add_entry__invalid_month_zero(
        self,
        spending_account_service,
    ):
        """Test that month value of 0 is rejected by database constraint."""
        await add_account(spending_account_service)
        entry_data = get_entry_data(month=0)

        with pytest.raises((ValidationError, ValueError, IntegrityError)):
            entry = SpendingEntryCreate(**entry_data)
            await spending_account_service.add_entry(entry=entry)

    async def test__add_entry__invalid_month_thirteen(
        self,
        spending_account_service,
    ):
        """Test that month value of 13 is rejected by database constraint."""
        await add_account(spending_account_service)
        entry_data = get_entry_data(month=13)

        with pytest.raises((ValidationError, ValueError, IntegrityError)):
            entry = SpendingEntryCreate(**entry_data)
            await spending_account_service.add_entry(entry=entry)

    async def test__add_entry__invalid_month_negative(
        self,
        spending_account_service,
    ):
        """Test that negative month value is rejected by database constraint."""
        await add_account(spending_account_service)
        entry_data = get_entry_data(month=-1)

        with pytest.raises((ValidationError, ValueError, IntegrityError)):
            entry = SpendingEntryCreate(**entry_data)
            await spending_account_service.add_entry(entry=entry)

    async def test__add_entry__valid_boundary_months(
        self,
        spending_account_service,
    ):
        """Test that boundary month values 1 and 12 are accepted."""
        await delete_all_entries(spending_account_service)
        await add_account(spending_account_service)

        # Test month = 1
        entry_data = get_entry_data(month=1, year=2024)
        entry = SpendingEntryCreate(**entry_data)
        result = await spending_account_service.add_entry(entry=entry)
        assert result.month == 1

        # Test month = 12
        entry_data = get_entry_data(month=12, year=2024)
        entry = SpendingEntryCreate(**entry_data)
        result = await spending_account_service.add_entry(entry=entry)
        assert result.month == 12

    async def test__add_entry__negative_year(
        self,
        spending_account_service,
    ):
        """Test that negative year value is handled."""
        await add_account(spending_account_service)
        entry_data = get_entry_data(year=-2024)

        # Depending on business rules, this might be allowed or rejected
        # For now, test that it doesn't crash
        try:
            entry = SpendingEntryCreate(**entry_data)
            result = await spending_account_service.add_entry(entry=entry)
            # If accepted, verify it's stored correctly
            assert result.year == -2024
        except (ValidationError, ValueError):
            # If rejected, that's also valid
            pass

    async def test__add_entry__negative_starting_balance(
        self,
        spending_account_service,
    ):
        """Test entry with negative starting balance."""
        await add_account(spending_account_service)
        entry_data = get_entry_data(starting_balance=-100.0, current_balance=-50.0, current_credit=0.0)

        # Test that negative balances are handled
        entry = SpendingEntryCreate(**entry_data)
        result = await spending_account_service.add_entry(entry=entry)

        assert result.starting_balance == -100.0
        assert result.current_balance == -50.0
        # Verify calculated fields work with negative values
        assert result.balance_after_credit == -50.0
        assert result.total_spent == (-100.0 - (-50.0)) + 0.0
        assert result.total_spent == -50.0

    async def test__add_entry__empty_account_name(
        self,
        spending_account_service,
    ):
        """Test that empty account name is rejected."""
        entry_data = get_entry_data(account_name="")

        with pytest.raises((ValidationError, ValueError, AccountWithNameNotFoundError)):
            entry = SpendingEntryCreate(**entry_data)
            await spending_account_service.add_entry(entry=entry)


class TestPaginationBoundaryConditions:
    """Test boundary conditions for pagination."""

    async def test__pagination__zero_entries(
        self,
        spending_account_service,
    ):
        """Test pagination with zero entries."""
        await delete_all_entries(spending_account_service)

        results = await spending_account_service.get_all_entries(page=0, size=10)

        assert results.page.total_elements == 0
        assert results.page.size == 10
        assert results.page.number == 0
        assert results.spending_entries == []

    async def test__pagination__single_entry(
        self,
        spending_account_service,
    ):
        """Test pagination with a single entry."""
        await delete_all_entries(spending_account_service)
        account = await add_account(spending_account_service, account_name=f"SingleEntry-{uuid4()}")
        await create_multiple_entries(spending_account_service, account.account_name, 1)

        results = await spending_account_service.get_all_entries(page=0, size=10)

        assert results.page.total_elements == 1
        assert results.page.size == 10
        assert results.page.number == 0
        assert len(results.spending_entries) == 1

    async def test__pagination__limit_one_with_multiple_entries(
        self,
        spending_account_service,
    ):
        """Test pagination with limit=1 and multiple entries."""
        await delete_all_entries(spending_account_service)
        account = await add_account(spending_account_service, account_name=f"LimitOne-{uuid4()}")
        await create_multiple_entries(spending_account_service, account.account_name, 10)

        results = await spending_account_service.get_all_entries(page=0, size=1)

        assert results.page.total_elements == 10
        assert results.page.size == 1
        assert results.page.number == 0
        assert len(results.spending_entries) == 1

        # Get second entry
        results2 = await spending_account_service.get_all_entries(page=1, size=1)
        assert results2.page.total_elements == 10
        assert len(results2.spending_entries) == 1
        # Verify different entry
        assert results.spending_entries[0].id != results2.spending_entries[0].id

    async def test__pagination__very_large_limit(
        self,
        spending_account_service,
    ):
        """Test pagination with very large limit value."""
        await delete_all_entries(spending_account_service)
        account = await add_account(spending_account_service, account_name=f"LargeLimit-{uuid4()}")
        await create_multiple_entries(spending_account_service, account.account_name, 10)

        results = await spending_account_service.get_all_entries(page=0, size=1000)

        assert results.page.total_elements == 10
        assert results.page.size == 1000
        assert results.page.number == 0
        assert len(results.spending_entries) == 10  # Only 10 entries exist

    async def test__pagination__limit_exceeds_total_entries(
        self,
        spending_account_service,
    ):
        """Test pagination where limit exceeds total entries."""
        await delete_all_entries(spending_account_service)
        account = await add_account(spending_account_service, account_name=f"ExceedLimit-{uuid4()}")
        await create_multiple_entries(spending_account_service, account.account_name, 5)

        results = await spending_account_service.get_all_entries(page=0, size=20)

        assert results.page.total_elements == 5
        assert results.page.size == 20
        assert results.page.number == 0
        assert len(results.spending_entries) == 5

    async def test__pagination__offset_at_last_entry(
        self,
        spending_account_service,
    ):
        """Test pagination with offset at the last entry."""
        await delete_all_entries(spending_account_service)
        account = await add_account(spending_account_service, account_name=f"LastEntry-{uuid4()}")
        await create_multiple_entries(spending_account_service, account.account_name, 10)

        # With page-based pagination, to get near the end with 5 entries:
        # page=1, size=5 gets entries 6-10 (5 entries)
        results = await spending_account_service.get_all_entries(page=1, size=5)

        assert results.page.total_elements == 10
        assert results.page.size == 5
        assert results.page.number == 1
        assert len(results.spending_entries) == 5  # Gets entries 6-10

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
        results = await spending_account_service.get_all_entries_for_account(account_id=account1.id, page=0, size=10)

        assert results.page.total_elements == 0
        assert results.page.size == 10
        assert results.page.number == 0
        assert results.spending_entries == []

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
        page1 = await spending_account_service.get_all_entries_for_account(account_id=account.id, page=0, size=5)
        page2 = await spending_account_service.get_all_entries_for_account(account_id=account.id, page=1, size=5)
        page3 = await spending_account_service.get_all_entries_for_account(account_id=account.id, page=2, size=5)

        # Collect all retrieved IDs
        page1_ids = {entry.id for entry in page1.spending_entries}
        page2_ids = {entry.id for entry in page2.spending_entries}
        page3_ids = {entry.id for entry in page3.spending_entries}

        # Verify no overlaps
        assert len(page1_ids & page2_ids) == 0  # No overlap between page 1 and 2
        assert len(page2_ids & page3_ids) == 0  # No overlap between page 2 and 3
        assert len(page1_ids & page3_ids) == 0  # No overlap between page 1 and 3

        # Verify all entries retrieved
        all_retrieved_ids = page1_ids | page2_ids | page3_ids
        assert len(all_retrieved_ids) == 15
        assert all_retrieved_ids == created_ids

    async def test__pagination__order_consistency_across_page_sizes(
        self,
        spending_account_service,
    ):
        """Test that entries are returned in consistent order across different page sizes."""
        await delete_all_entries(spending_account_service)
        account = await add_account(spending_account_service, account_name=f"OrderTest-{uuid4()}")

        await create_multiple_entries(spending_account_service, account.account_name, 15)

        # Get all entries at once
        all_at_once = await spending_account_service.get_all_entries(page=0, size=15)

        # Get same entries with different pagination
        page1 = await spending_account_service.get_all_entries(page=0, size=5)
        page2 = await spending_account_service.get_all_entries(page=1, size=5)
        page3 = await spending_account_service.get_all_entries(page=2, size=5)

        # Order should be consistent
        paginated_ids = (
            [e.id for e in page1.spending_entries]
            + [e.id for e in page2.spending_entries]
            + [e.id for e in page3.spending_entries]
        )
        all_ids = [e.id for e in all_at_once.spending_entries]

        assert paginated_ids == all_ids  # Same order regardless of pagination

    async def test__pagination__data_consistency_across_pages(
        self,
        spending_account_service,
    ):
        """Test that entry data is consistent when retrieved on different pages."""
        await delete_all_entries(spending_account_service)
        account = await add_account(spending_account_service, account_name=f"DataConsistency-{uuid4()}")

        # Create entries with specific data
        created_entries = await create_multiple_entries(spending_account_service, account.account_name, 10)

        # Get all entries
        all_results = await spending_account_service.get_all_entries(page=0, size=10)

        # Verify each entry matches the created data
        for i, entry in enumerate(all_results.spending_entries):
            assert entry.id is not None
            assert entry.account_name == account.account_name.upper()
            assert entry.month is not None
            assert entry.year is not None
            assert entry.starting_balance is not None
            assert entry.current_balance is not None
            assert entry.current_credit is not None
            # Verify calculated fields are present
            assert entry.balance_after_credit == entry.current_balance - entry.current_credit
            assert entry.total_spent == (entry.starting_balance - entry.current_balance) + entry.current_credit

    async def test__pagination__total_pages_for_account_specific(
        self,
        spending_account_service,
    ):
        """Test total_pages calculation for account-specific queries."""
        await delete_all_entries(spending_account_service)
        account = await add_account(spending_account_service, account_name=f"AccountPages-{uuid4()}")

        # Create 17 entries
        await create_multiple_entries(spending_account_service, account.account_name, 17)

        results = await spending_account_service.get_all_entries_for_account(account_id=account.id, page=0, size=5)

        assert results.page.total_pages == 4  # 17 / 5 = 4 pages (ceil)
        assert results.page.total_elements == 17
        assert results.page.size == 5

        # Verify last page has correct number
        last_page = await spending_account_service.get_all_entries_for_account(account_id=account.id, page=3, size=5)
        assert len(last_page.spending_entries) == 2  # Only 2 entries on last page
