"""Unit tests for the accounts use case."""

from uuid import uuid4

import pytest

from app.use_cases.accounts import AccountService
from app.use_cases.errors.accounts import (
    AccountNotFoundError,
    AccountWithNameNotFoundError,
    MonthYearNotFoundError,
    MonthYearWithDetailsNotFoundError,
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


async def add_month_year(account_service, month="September", year=2025):
    month_year = await account_service.account_repository.get_or_create_month_year(month=month, year=year)
    return month_year


async def delete_all_month_years(account_service):
    month_years = await account_service.account_repository.get_all_month_years()
    for month_year in month_years:
        await account_service.account_repository.delete_month_year(month_year.id)


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


class TestGetAllAccounts:
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


class TestUpdateAccountName:
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


class TestGetOrCreateMonthYear:
    async def test__get_or_create_month_year__create_month_year(
        self,
        account_service,
    ):
        """Test creating a new month-year entry."""
        month = "September"
        year = 2025
        month_year = await account_service.get_or_create_month_year(month=month, year=year)

        assert month_year is not None
        assert month_year.month == month
        assert month_year.year == year

    async def test__get_or_create_month_year__retrieve_existing_month_year(
        self,
        account_service,
    ):
        """Test retrieving an existing month-year entry."""
        test_month_year = await add_month_year(account_service)

        month_year = await account_service.get_or_create_month_year(
            month=test_month_year.month, year=test_month_year.year
        )

        assert month_year.id == test_month_year.id
        assert month_year.month == test_month_year.month
        assert month_year.year == test_month_year.year


class TestGetMonthYearByValue:
    async def test__get_month_year_by_value__existing_month_year__retrieve_month_year(
        self,
        account_service,
    ):
        """Test retrieving an existing month-year entry by month and year."""
        test_month_year = await add_month_year(account_service)

        month_year = await account_service.get_month_year_by_value(
            month=test_month_year.month, year=test_month_year.year
        )

        assert month_year is not None
        assert month_year.id == test_month_year.id
        assert month_year.month == test_month_year.month
        assert month_year.year == test_month_year.year

    async def test__get_month_year_by_value__nonexistent_month_year__raise_error(
        self,
        account_service,
    ):
        """Test retrieving a non-existent month-year entry by month and year."""
        with pytest.raises(MonthYearWithDetailsNotFoundError):
            await account_service.get_month_year_by_value(month=f"NonExistentMonth-{uuid4()}", year=1999)


class TestGetMonthYearById:
    async def test__get_month_year_by_id__existing_month_year__retrieve_month_year(
        self,
        account_service,
    ):
        """Test retrieving an existing month-year entry by ID."""
        test_month_year = await add_month_year(account_service)

        month_year = await account_service.get_month_year_by_id(month_year_id=test_month_year.id)

        assert month_year is not None
        assert month_year.id == test_month_year.id
        assert month_year.month == test_month_year.month
        assert month_year.year == test_month_year.year

    async def test__get_month_year_by_id__nonexistent_month_year__raise_error(
        self,
        account_service,
    ):
        """Test retrieving a non-existent month-year entry by ID."""
        with pytest.raises(MonthYearNotFoundError):
            await account_service.get_month_year_by_id(month_year_id=f"non-existent-id-{uuid4()}")


class TestDeleteMonthYear:
    async def test__delete_month_year__delete_existing_month_year(
        self,
        account_service,
    ):
        """Test deleting an existing month-year entry."""
        month = "October"
        year = 2025
        test_month_year = await add_month_year(account_service=account_service, month=month, year=year)

        month_year = await account_service.get_month_year_by_id(month_year_id=test_month_year.id)
        assert month_year is not None
        assert month_year.month == month
        assert month_year.year == year
        await account_service.delete_month_year(month_year_id=test_month_year.id)

        with pytest.raises(MonthYearNotFoundError):
            await account_service.get_month_year_by_id(month_year_id=test_month_year.id)

    async def test__delete_month_year__nonexistent_month_year__raise_error(
        self,
        account_service,
    ):
        """Test deleting a non-existent month-year entry raises error."""
        with pytest.raises(MonthYearNotFoundError):
            await account_service.delete_month_year(month_year_id=f"non-existent-id-{uuid4()}")


class TestGetAllMonthYears:
    async def test__get_all_month_years__with_existing_month_years__retrieve_month_years(
        self,
        account_service,
    ):
        """Test retrieving all month-year entries when entries exist."""
        await delete_all_month_years(account_service)
        await add_month_year(account_service=account_service, month="January", year=2025)
        await add_month_year(account_service=account_service, month="February", year=2025)
        num_month_years = 2

        month_years = await account_service.get_all_month_years()

        assert month_years is not None
        assert len(month_years) == num_month_years

    async def test__get_all_month_years__with_no_month_years__retrieve_empty_list(
        self,
        account_service,
    ):
        """Test retrieving all month-year entries when no entries exist."""
        await delete_all_month_years(account_service)

        month_years = await account_service.get_all_month_years()

        assert month_years == []


class TestUpdateMonthYear:
    async def test__update_month_year__existing_month_year__update_month_year(
        self,
        account_service,
    ):
        """Test updating an existing month-year entry."""
        month = "March"
        year = 2025
        update_month = "April"
        update_year = 2026
        test_month_year = await add_month_year(account_service=account_service, month=month, year=year)

        assert test_month_year.month == month
        assert test_month_year.year == year
        updated_month_year = await account_service.update_month_year(
            month_year_id=test_month_year.id,
            month=update_month,
            year=update_year,
        )

        assert updated_month_year is not None
        assert updated_month_year.id == test_month_year.id
        assert updated_month_year.month == update_month
        assert updated_month_year.year == update_year

    async def test__update_month_year__nonexistent_month_year__raise_error(
        self,
        account_service,
    ):
        """Test updating a non-existent month-year entry."""
        with pytest.raises(MonthYearNotFoundError):
            await account_service.update_month_year(
                month_year_id=f"non-existent-id-{uuid4()}",
                month="May",
                year=2027,
            )
