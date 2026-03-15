"""Integration tests for the spending entry endpoints.

Endpoints under test:
    POST   /v1/spending_account
    GET    /v1/spending_account/list
    GET    /v1/spending_account/{id}/list
    PUT    /v1/spending_account/{id}
    DELETE /v1/spending_account/{id}
"""

from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import AsyncClient

# ----------------------------------------------- Constants & Helpers ------------------------------------------------ #

BASE_URL = "/v1/spending_account"


def _entry_payload(
    account_name: str,
    month: int,
    year: int,
    starting_balance: float = 10000.0,
    current_balance: float = 8000.0,
    current_credit: float = 2000.0,
) -> dict:
    return {
        "accountName": account_name,
        "month": month,
        "year": year,
        "startingBalance": starting_balance,
        "currentBalance": current_balance,
        "currentCredit": current_credit,
    }


async def _post_entry(client: AsyncClient, payload: dict) -> dict:
    """Ensure the account exists then POST the entry; asserts 200."""
    await client.post("/v1/account/get_or_create", json={"accountName": payload["accountName"]})
    resp = await client.post(BASE_URL, json=payload)
    assert resp.status_code == 200, resp.text
    return resp.json()


async def _delete_all(client: AsyncClient) -> None:
    """Delete every entry visible through the list endpoint."""
    while True:
        resp = await client.get(f"{BASE_URL}/list", params={"size": 100, "page": 0})
        assert resp.status_code == 200
        entries = resp.json()["spendingEntries"]
        if not entries:
            break
        for entry in entries:
            del_resp = await client.delete(f"{BASE_URL}/{entry['id']}")
            assert del_resp.status_code == 200


async def _resolve_account_id(client: AsyncClient, account_name: str) -> str | None:
    """Return the id of the account whose name contains *account_name* (upper-cased)."""
    resp = await client.get("/v1/account/list")
    return next((a["id"] for a in resp.json() if account_name.upper() in a["accountName"]), None)


async def _create_account(client: AsyncClient, prefix: str = "ACC") -> str:
    """Create a uniquely-named account and return its name."""
    name = f"{prefix}-{uuid4().hex[:8]}"
    await client.post("/v1/account/get_or_create", json={"accountName": name})
    return name


# -------------------------------------------- POST /v1/spending_account --------------------------------------------- #


class TestCreateEntry:
    """POST /v1/spending_account -- create a new spending entry."""

    @pytest_asyncio.fixture(autouse=True, scope="class", loop_scope="session")
    async def cleanup(self, client: AsyncClient):
        yield
        await _delete_all(client)

    async def test__success_status_and_shape(self, client: AsyncClient):
        account = await _create_account(client, "CREATE")

        resp = await client.post(BASE_URL, json=_entry_payload(account, month=1, year=2025))

        assert resp.status_code == 200
        data = resp.json()
        for key in (
            "id",
            "accountName",
            "month",
            "year",
            "startingBalance",
            "currentBalance",
            "currentCredit",
            "balanceAfterCredit",
            "totalSpent",
        ):
            assert key in data, f"Missing key: {key}"

    async def test__response_values_match_request(self, client: AsyncClient):
        account = await _create_account(client, "CREATE")

        resp = await client.post(
            BASE_URL,
            json=_entry_payload(
                account, month=2, year=2025, starting_balance=5000.0, current_balance=4000.0, current_credit=500.0
            ),
        )

        assert resp.status_code == 200
        data = resp.json()
        assert data["accountName"] == account.upper()
        assert data["month"] == 2
        assert data["year"] == 2025
        assert data["startingBalance"] == 5000.0
        assert data["currentBalance"] == 4000.0
        assert data["currentCredit"] == 500.0

    async def test__calculated_fields_are_correct(self, client: AsyncClient):
        account = await _create_account(client, "CREATE")

        resp = await client.post(
            BASE_URL,
            json=_entry_payload(
                account, month=3, year=2025, starting_balance=10000.0, current_balance=7000.0, current_credit=1500.0
            ),
        )

        assert resp.status_code == 200
        data = resp.json()
        assert data["balanceAfterCredit"] == pytest.approx(7000.0 - 1500.0)  # currentBalance - currentCredit
        assert data["totalSpent"] == pytest.approx((10000.0 - 7000.0) + 1500.0)  # (start - curr) + credit

    async def test__id_is_assigned(self, client: AsyncClient):
        account = await _create_account(client, "CREATE")

        resp = await client.post(BASE_URL, json=_entry_payload(account, month=4, year=2025))

        assert resp.status_code == 200
        assert resp.json()["id"]

    async def test__unknown_account_returns_400(self, client: AsyncClient):
        resp = await client.post(BASE_URL, json=_entry_payload(f"GHOST-{uuid4().hex}", month=5, year=2025))

        assert resp.status_code == 400

    async def test__duplicate_period_for_same_account_returns_400(self, client: AsyncClient):
        account = await _create_account(client, "CREATE")
        payload = _entry_payload(account, month=6, year=2025)
        await client.post(BASE_URL, json=payload)

        resp = await client.post(BASE_URL, json=payload)

        assert resp.status_code == 400

    async def test__same_period_for_different_accounts_is_allowed(self, client: AsyncClient):
        acc_a = await _create_account(client, "DUPA")
        acc_b = await _create_account(client, "DUPB")

        resp_a = await client.post(BASE_URL, json=_entry_payload(acc_a, month=7, year=2025))
        resp_b = await client.post(BASE_URL, json=_entry_payload(acc_b, month=7, year=2025))

        assert resp_a.status_code == 200
        assert resp_b.status_code == 200


# ------------------------------------------ GET /v1/spending_account/list ------------------------------------------- #


class TestListResponseShape:
    """GET /v1/spending_account/list -- response structure and field presence."""

    @pytest_asyncio.fixture(autouse=True, scope="class", loop_scope="session")
    async def seed(self, client: AsyncClient):
        account = f"SHAPE-{uuid4().hex[:8]}"
        await _post_entry(client, _entry_payload(account, month=1, year=2025))
        await _post_entry(client, _entry_payload(account, month=2, year=2025))
        yield
        await _delete_all(client)

    async def test__has_spending_entries_array(self, client: AsyncClient):
        resp = await client.get(f"{BASE_URL}/list")
        assert resp.status_code == 200
        body = resp.json()
        assert "spendingEntries" in body
        assert isinstance(body["spendingEntries"], list)

    async def test__has_page_metadata(self, client: AsyncClient):
        resp = await client.get(f"{BASE_URL}/list")
        assert resp.status_code == 200
        page = resp.json()["page"]
        for key in ("number", "size", "totalElements", "totalPages"):
            assert key in page, f"Missing page key: {key}"

    async def test__entry_has_all_expected_fields(self, client: AsyncClient):
        resp = await client.get(f"{BASE_URL}/list")
        assert resp.status_code == 200
        entry = resp.json()["spendingEntries"][0]
        for key in (
            "id",
            "accountName",
            "month",
            "year",
            "startingBalance",
            "currentBalance",
            "currentCredit",
            "balanceAfterCredit",
            "totalSpent",
        ):
            assert key in entry, f"Missing entry key: {key}"


class TestListCalculatedFields:
    """GET /v1/spending_account/list -- balanceAfterCredit and totalSpent formulas."""

    @pytest_asyncio.fixture(autouse=True, scope="class", loop_scope="session")
    async def seed(self, client: AsyncClient):
        account = f"CALC-{uuid4().hex[:8]}"
        await _post_entry(
            client,
            _entry_payload(
                account, month=1, year=2025, starting_balance=10000.0, current_balance=7000.0, current_credit=1500.0
            ),
        )
        yield
        await _delete_all(client)

    async def test__balance_after_credit_formula(self, client: AsyncClient):
        resp = await client.get(f"{BASE_URL}/list")
        assert resp.status_code == 200
        e = resp.json()["spendingEntries"][0]
        assert e["balanceAfterCredit"] == pytest.approx(e["currentBalance"] - e["currentCredit"])

    async def test__total_spent_formula(self, client: AsyncClient):
        resp = await client.get(f"{BASE_URL}/list")
        assert resp.status_code == 200
        e = resp.json()["spendingEntries"][0]
        assert e["totalSpent"] == pytest.approx((e["startingBalance"] - e["currentBalance"]) + e["currentCredit"])


class TestListSort:
    """GET /v1/spending_account/list -- sorting by every supported field.

    Seed: 3 entries with strictly ordered values across all sortable fields so
    that both asc and desc assertions work on the same dataset.

        entry  month  year  startBal  currBal  credit  →  bac   totalSpent
          A      1    2023    1000      900      50    →  850      150
          B      2    2024    3000     2800     100    → 2700      300
          C      3    2025    2000     1800     200    → 1600      400
    """

    @pytest_asyncio.fixture(autouse=True, scope="class", loop_scope="session")
    async def seed(self, client: AsyncClient):
        account = f"SORT-{uuid4().hex[:8]}"
        await _post_entry(
            client,
            _entry_payload(
                account, month=1, year=2023, starting_balance=1000.0, current_balance=900.0, current_credit=50.0
            ),
        )
        await _post_entry(
            client,
            _entry_payload(
                account, month=2, year=2024, starting_balance=3000.0, current_balance=2800.0, current_credit=100.0
            ),
        )
        await _post_entry(
            client,
            _entry_payload(
                account, month=3, year=2025, starting_balance=2000.0, current_balance=1800.0, current_credit=200.0
            ),
        )
        yield
        await _delete_all(client)

    async def test__sort_by_year_asc(self, client: AsyncClient):
        resp = await client.get(f"{BASE_URL}/list", params={"sortBy": "year", "sortOrder": "asc"})
        assert resp.status_code == 200
        values = [e["year"] for e in resp.json()["spendingEntries"]]
        assert values == sorted(values)

    async def test__sort_by_year_desc(self, client: AsyncClient):
        resp = await client.get(f"{BASE_URL}/list", params={"sortBy": "year", "sortOrder": "desc"})
        assert resp.status_code == 200
        values = [e["year"] for e in resp.json()["spendingEntries"]]
        assert values == sorted(values, reverse=True)

    async def test__sort_by_month_asc(self, client: AsyncClient):
        resp = await client.get(f"{BASE_URL}/list", params={"sortBy": "month", "sortOrder": "asc"})
        assert resp.status_code == 200
        values = [e["month"] for e in resp.json()["spendingEntries"]]
        assert values == sorted(values)

    async def test__sort_by_month_desc(self, client: AsyncClient):
        resp = await client.get(f"{BASE_URL}/list", params={"sortBy": "month", "sortOrder": "desc"})
        assert resp.status_code == 200
        values = [e["month"] for e in resp.json()["spendingEntries"]]
        assert values == sorted(values, reverse=True)

    async def test__sort_by_starting_balance_asc(self, client: AsyncClient):
        resp = await client.get(f"{BASE_URL}/list", params={"sortBy": "starting_balance", "sortOrder": "asc"})
        assert resp.status_code == 200
        values = [e["startingBalance"] for e in resp.json()["spendingEntries"]]
        assert values == sorted(values)

    async def test__sort_by_starting_balance_desc(self, client: AsyncClient):
        resp = await client.get(f"{BASE_URL}/list", params={"sortBy": "starting_balance", "sortOrder": "desc"})
        assert resp.status_code == 200
        values = [e["startingBalance"] for e in resp.json()["spendingEntries"]]
        assert values == sorted(values, reverse=True)

    async def test__sort_by_current_balance_asc(self, client: AsyncClient):
        resp = await client.get(f"{BASE_URL}/list", params={"sortBy": "current_balance", "sortOrder": "asc"})
        assert resp.status_code == 200
        values = [e["currentBalance"] for e in resp.json()["spendingEntries"]]
        assert values == sorted(values)

    async def test__sort_by_current_balance_desc(self, client: AsyncClient):
        resp = await client.get(f"{BASE_URL}/list", params={"sortBy": "current_balance", "sortOrder": "desc"})
        assert resp.status_code == 200
        values = [e["currentBalance"] for e in resp.json()["spendingEntries"]]
        assert values == sorted(values, reverse=True)

    async def test__sort_by_balance_after_credit_asc(self, client: AsyncClient):
        resp = await client.get(f"{BASE_URL}/list", params={"sortBy": "balance_after_credit", "sortOrder": "asc"})
        assert resp.status_code == 200
        values = [e["balanceAfterCredit"] for e in resp.json()["spendingEntries"]]
        assert values == sorted(values)

    async def test__sort_by_total_spent_desc(self, client: AsyncClient):
        resp = await client.get(f"{BASE_URL}/list", params={"sortBy": "total_spent", "sortOrder": "desc"})
        assert resp.status_code == 200
        values = [e["totalSpent"] for e in resp.json()["spendingEntries"]]
        assert values == sorted(values, reverse=True)


class TestListFilter:
    """GET /v1/spending_account/list -- filtering by month, year, account name, and combinations.

    Seed: 4 entries across 2 accounts to isolate every filter scenario.
        ACC1: month=3/year=2024, month=3/year=2025, month=7/year=2025
        ACC2: month=1/year=2025
    """

    account_1: str = ""
    account_2: str = ""

    @pytest_asyncio.fixture(autouse=True, scope="class", loop_scope="session")
    async def seed(self, client: AsyncClient):
        suffix = uuid4().hex[:8]
        TestListFilter.account_1 = f"ACC1-{suffix}"
        TestListFilter.account_2 = f"ACC2-{suffix}"
        await _post_entry(client, _entry_payload(TestListFilter.account_1, month=3, year=2024))
        await _post_entry(client, _entry_payload(TestListFilter.account_1, month=3, year=2025))
        await _post_entry(client, _entry_payload(TestListFilter.account_1, month=7, year=2025))
        await _post_entry(client, _entry_payload(TestListFilter.account_2, month=1, year=2025))
        yield
        await _delete_all(client)

    async def test__filter_by_month_returns_matching_entries(self, client: AsyncClient):
        resp = await client.get(f"{BASE_URL}/list", params={"month": 3})
        assert resp.status_code == 200
        data = resp.json()
        assert data["page"]["totalElements"] == 2
        assert all(e["month"] == 3 for e in data["spendingEntries"])

    async def test__filter_by_month_single_result(self, client: AsyncClient):
        resp = await client.get(f"{BASE_URL}/list", params={"month": 7})
        assert resp.status_code == 200
        data = resp.json()
        assert data["page"]["totalElements"] == 1
        assert data["spendingEntries"][0]["month"] == 7

    async def test__filter_by_year_returns_matching_entries(self, client: AsyncClient):
        resp = await client.get(f"{BASE_URL}/list", params={"year": 2024})
        assert resp.status_code == 200
        data = resp.json()
        assert data["page"]["totalElements"] == 1
        assert data["spendingEntries"][0]["year"] == 2024

    async def test__filter_by_month_and_year_and_combination(self, client: AsyncClient):
        resp = await client.get(f"{BASE_URL}/list", params={"month": 3, "year": 2025})
        assert resp.status_code == 200
        data = resp.json()
        assert data["page"]["totalElements"] == 1
        assert data["spendingEntries"][0]["month"] == 3
        assert data["spendingEntries"][0]["year"] == 2025

    async def test__filter_by_account_name_exact_match(self, client: AsyncClient):
        resp = await client.get(f"{BASE_URL}/list", params={"accountName": self.account_1.upper()})
        assert resp.status_code == 200
        data = resp.json()
        assert data["page"]["totalElements"] == 3
        assert all(e["accountName"] == self.account_1.upper() for e in data["spendingEntries"])

    async def test__filter_by_account_name_no_match_returns_empty(self, client: AsyncClient):
        resp = await client.get(f"{BASE_URL}/list", params={"accountName": f"NOMATCH-{uuid4().hex}"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["page"]["totalElements"] == 0
        assert data["spendingEntries"] == []

    async def test__unmatched_filter_returns_empty(self, client: AsyncClient):
        resp = await client.get(f"{BASE_URL}/list", params={"year": 2099})
        assert resp.status_code == 200
        data = resp.json()
        assert data["page"]["totalElements"] == 0
        assert data["spendingEntries"] == []


class TestListFilterAndSort:
    """GET /v1/spending_account/list -- filter and sort applied simultaneously."""

    account_a: str = ""

    @pytest_asyncio.fixture(autouse=True, scope="class", loop_scope="session")
    async def seed(self, client: AsyncClient):
        suffix = uuid4().hex[:8]
        TestListFilterAndSort.account_a = f"COMBA-{suffix}"
        account_b = f"COMB-B-{suffix}"
        await _post_entry(
            client, _entry_payload(TestListFilterAndSort.account_a, month=1, year=2025, current_balance=500.0)
        )
        await _post_entry(
            client, _entry_payload(TestListFilterAndSort.account_a, month=2, year=2025, current_balance=300.0)
        )
        await _post_entry(
            client, _entry_payload(TestListFilterAndSort.account_a, month=3, year=2025, current_balance=700.0)
        )
        await _post_entry(client, _entry_payload(account_b, month=1, year=2025, current_balance=999.0))
        yield
        await _delete_all(client)

    async def test__filter_by_account_name_and_sort_by_current_balance_asc(self, client: AsyncClient):
        resp = await client.get(
            f"{BASE_URL}/list",
            params={"accountName": self.account_a.upper(), "sortBy": "current_balance", "sortOrder": "asc"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["page"]["totalElements"] == 3
        balances = [e["currentBalance"] for e in data["spendingEntries"]]
        assert balances == sorted(balances)
        assert all(e["accountName"] == self.account_a.upper() for e in data["spendingEntries"])

    async def test__filter_by_year_and_sort_by_month_desc(self, client: AsyncClient):
        resp = await client.get(
            f"{BASE_URL}/list",
            params={"year": 2025, "sortBy": "month", "sortOrder": "desc"},
        )
        assert resp.status_code == 200
        months = [e["month"] for e in resp.json()["spendingEntries"]]
        assert months == sorted(months, reverse=True)


class TestListPagination:
    """GET /v1/spending_account/list -- page/size, last page, and beyond-bounds behaviour."""

    @pytest_asyncio.fixture(autouse=True, scope="class", loop_scope="session")
    async def seed(self, client: AsyncClient):
        account = f"PAGE-{uuid4().hex[:8]}"
        for month in range(1, 6):  # 5 entries
            await _post_entry(client, _entry_payload(account, month=month, year=2025))
        yield
        await _delete_all(client)

    async def test__second_page_returns_correct_entries(self, client: AsyncClient):
        resp = await client.get(f"{BASE_URL}/list", params={"page": 1, "size": 2})
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["spendingEntries"]) == 2
        assert data["page"]["totalElements"] == 5
        assert data["page"]["number"] == 1
        assert data["page"]["size"] == 2

    async def test__total_elements_consistent_across_page_sizes(self, client: AsyncClient):
        total = (await client.get(f"{BASE_URL}/list", params={"page": 0, "size": 100})).json()["page"]["totalElements"]
        paged = (await client.get(f"{BASE_URL}/list", params={"page": 0, "size": 2})).json()["page"]["totalElements"]
        assert total == paged

    async def test__last_page_has_remaining_entries(self, client: AsyncClient):
        # 5 entries, size=2 → pages 0 and 1 full; page 2 has 1
        resp = await client.get(f"{BASE_URL}/list", params={"page": 2, "size": 2})
        assert resp.status_code == 200
        data = resp.json()
        assert data["page"]["totalElements"] == 5
        assert data["page"]["totalPages"] == 3
        assert len(data["spendingEntries"]) == 1

    async def test__beyond_last_page_returns_empty(self, client: AsyncClient):
        resp = await client.get(f"{BASE_URL}/list", params={"page": 99, "size": 2})
        assert resp.status_code == 200
        data = resp.json()
        assert data["page"]["totalElements"] == 5
        assert data["page"]["number"] == 99
        assert len(data["spendingEntries"]) == 0


# ---------------------------------------- GET /v1/spending_account/{id}/list ---------------------------------------- #


class TestPerAccountListAccountNotFound:
    """GET /v1/spending_account/{id}/list -- non-existent account_id returns 400."""

    async def test__unknown_account_id_returns_400(self, client: AsyncClient):
        resp = await client.get(f"{BASE_URL}/{uuid4()}/list")
        assert resp.status_code == 400


class TestPerAccountListSortAndFilter:
    """GET /v1/spending_account/{id}/list -- sort, filter, and combined filter+sort.

    Seed: 3 entries for one account.
        month=1, year=2025, currentBalance=800
        month=2, year=2025, currentBalance=400
        month=3, year=2024, currentBalance=600
    """

    account_id: str | None = None

    @pytest_asyncio.fixture(autouse=True, scope="class", loop_scope="session")
    async def seed(self, client: AsyncClient):
        account = f"PASFILT-{uuid4().hex[:8]}"
        await _post_entry(client, _entry_payload(account, month=1, year=2025, current_balance=800.0))
        await _post_entry(client, _entry_payload(account, month=2, year=2025, current_balance=400.0))
        await _post_entry(client, _entry_payload(account, month=3, year=2024, current_balance=600.0))
        TestPerAccountListSortAndFilter.account_id = await _resolve_account_id(client, account)
        yield
        await _delete_all(client)

    async def test__sort_by_current_balance_asc(self, client: AsyncClient):
        if not self.account_id:
            pytest.skip("Could not resolve account id")
        resp = await client.get(
            f"{BASE_URL}/{self.account_id}/list", params={"sortBy": "current_balance", "sortOrder": "asc"}
        )
        assert resp.status_code == 200
        balances = [e["currentBalance"] for e in resp.json()["spendingEntries"]]
        assert balances == sorted(balances)

    async def test__sort_by_current_balance_desc(self, client: AsyncClient):
        if not self.account_id:
            pytest.skip("Could not resolve account id")
        resp = await client.get(
            f"{BASE_URL}/{self.account_id}/list", params={"sortBy": "current_balance", "sortOrder": "desc"}
        )
        assert resp.status_code == 200
        balances = [e["currentBalance"] for e in resp.json()["spendingEntries"]]
        assert balances == sorted(balances, reverse=True)

    async def test__filter_by_year(self, client: AsyncClient):
        if not self.account_id:
            pytest.skip("Could not resolve account id")
        resp = await client.get(f"{BASE_URL}/{self.account_id}/list", params={"year": 2025})
        assert resp.status_code == 200
        data = resp.json()
        assert data["page"]["totalElements"] == 2
        assert all(e["year"] == 2025 for e in data["spendingEntries"])

    async def test__filter_by_month(self, client: AsyncClient):
        if not self.account_id:
            pytest.skip("Could not resolve account id")
        resp = await client.get(f"{BASE_URL}/{self.account_id}/list", params={"month": 1})
        assert resp.status_code == 200
        data = resp.json()
        assert data["page"]["totalElements"] == 1
        assert data["spendingEntries"][0]["month"] == 1

    async def test__filter_and_sort_combined(self, client: AsyncClient):
        if not self.account_id:
            pytest.skip("Could not resolve account id")
        resp = await client.get(
            f"{BASE_URL}/{self.account_id}/list",
            params={"year": 2025, "sortBy": "current_balance", "sortOrder": "asc"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["page"]["totalElements"] == 2
        balances = [e["currentBalance"] for e in data["spendingEntries"]]
        assert balances == sorted(balances)


class TestPerAccountListPagination:
    """GET /v1/spending_account/{id}/list -- pagination behaviour."""

    account_id: str | None = None

    @pytest_asyncio.fixture(autouse=True, scope="class", loop_scope="session")
    async def seed(self, client: AsyncClient):
        account = f"PAPAG-{uuid4().hex[:8]}"
        for month in range(1, 8):  # 7 entries
            await _post_entry(client, _entry_payload(account, month=month, year=2025))
        TestPerAccountListPagination.account_id = await _resolve_account_id(client, account)
        yield
        await _delete_all(client)

    async def test__first_page_returns_correct_count(self, client: AsyncClient):
        if not self.account_id:
            pytest.skip("Could not resolve account id")
        resp = await client.get(f"{BASE_URL}/{self.account_id}/list", params={"page": 0, "size": 3})
        assert resp.status_code == 200
        data = resp.json()
        assert data["page"]["totalElements"] == 7
        assert data["page"]["size"] == 3
        assert data["page"]["number"] == 0
        assert len(data["spendingEntries"]) == 3

    async def test__last_page_has_remaining_entries(self, client: AsyncClient):
        if not self.account_id:
            pytest.skip("Could not resolve account id")
        # 7 entries, size=3 → page 2 has 1
        resp = await client.get(f"{BASE_URL}/{self.account_id}/list", params={"page": 2, "size": 3})
        assert resp.status_code == 200
        data = resp.json()
        assert data["page"]["totalElements"] == 7
        assert data["page"]["totalPages"] == 3
        assert len(data["spendingEntries"]) == 1

    async def test__beyond_last_page_returns_empty(self, client: AsyncClient):
        if not self.account_id:
            pytest.skip("Could not resolve account id")
        resp = await client.get(f"{BASE_URL}/{self.account_id}/list", params={"page": 99, "size": 3})
        assert resp.status_code == 200
        data = resp.json()
        assert data["page"]["totalElements"] == 7
        assert len(data["spendingEntries"]) == 0

    async def test__no_overlap_between_pages(self, client: AsyncClient):
        if not self.account_id:
            pytest.skip("Could not resolve account id")
        page0 = await client.get(f"{BASE_URL}/{self.account_id}/list", params={"page": 0, "size": 3})
        page1 = await client.get(f"{BASE_URL}/{self.account_id}/list", params={"page": 1, "size": 3})
        ids_0 = {e["id"] for e in page0.json()["spendingEntries"]}
        ids_1 = {e["id"] for e in page1.json()["spendingEntries"]}
        assert ids_0.isdisjoint(ids_1)


# ------------------------------------------ PUT /v1/spending_account/{id} ------------------------------------------- #


class TestEditEntry:
    """PUT /v1/spending_account/{id} -- edit an existing entry."""

    @pytest_asyncio.fixture(autouse=True, scope="class", loop_scope="session")
    async def cleanup(self, client: AsyncClient):
        yield
        await _delete_all(client)

    async def _create(self, client: AsyncClient, account: str, month: int = 1, year: int = 2025) -> dict:
        return await _post_entry(client, _entry_payload(account, month=month, year=year))

    async def test__success_returns_updated_values(self, client: AsyncClient):
        account = f"EDIT-{uuid4().hex[:8]}"
        entry = await self._create(client, account, month=1, year=2025)

        resp = await client.put(
            f"{BASE_URL}/{entry['id']}",
            json=_entry_payload(
                account, month=2, year=2025, starting_balance=9000.0, current_balance=7500.0, current_credit=800.0
            ),
        )

        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == entry["id"]
        assert data["month"] == 2
        assert data["year"] == 2025
        assert data["startingBalance"] == 9000.0
        assert data["currentBalance"] == 7500.0
        assert data["currentCredit"] == 800.0

    async def test__calculated_fields_are_recalculated(self, client: AsyncClient):
        account = f"EDIT-{uuid4().hex[:8]}"
        entry = await self._create(client, account, month=3, year=2025)

        resp = await client.put(
            f"{BASE_URL}/{entry['id']}",
            json=_entry_payload(
                account, month=3, year=2025, starting_balance=6000.0, current_balance=4000.0, current_credit=1000.0
            ),
        )

        assert resp.status_code == 200
        data = resp.json()
        assert data["balanceAfterCredit"] == pytest.approx(4000.0 - 1000.0)
        assert data["totalSpent"] == pytest.approx((6000.0 - 4000.0) + 1000.0)

    async def test__same_period_same_entry_allowed(self, client: AsyncClient):
        """Re-saving with the same month/year must not trigger a duplicate-period error."""
        account = f"EDIT-{uuid4().hex[:8]}"
        entry = await self._create(client, account, month=4, year=2025)

        resp = await client.put(
            f"{BASE_URL}/{entry['id']}",
            json=_entry_payload(
                account, month=4, year=2025, starting_balance=3000.0, current_balance=2000.0, current_credit=500.0
            ),
        )

        assert resp.status_code == 200
        assert resp.json()["startingBalance"] == 3000.0

    async def test__not_found_returns_404(self, client: AsyncClient):
        account = await _create_account(client, "EDIT")

        resp = await client.put(f"{BASE_URL}/{uuid4()}", json=_entry_payload(account, month=5, year=2025))

        assert resp.status_code == 404

    async def test__unknown_account_returns_400(self, client: AsyncClient):
        account = f"EDIT-{uuid4().hex[:8]}"
        entry = await self._create(client, account, month=6, year=2025)

        resp = await client.put(
            f"{BASE_URL}/{entry['id']}", json=_entry_payload(f"GHOST-{uuid4().hex}", month=6, year=2025)
        )

        assert resp.status_code == 400

    async def test__duplicate_period_for_same_account_returns_400(self, client: AsyncClient):
        account = f"EDIT-{uuid4().hex[:8]}"
        entry1 = await self._create(client, account, month=7, year=2025)
        entry2 = await self._create(client, account, month=8, year=2025)

        # Move entry2 onto entry1's period — should conflict
        resp = await client.put(f"{BASE_URL}/{entry2['id']}", json=_entry_payload(account, month=7, year=2025))

        assert resp.status_code == 400


# ----------------------------------------- DELETE /v1/spending_account/{id} ----------------------------------------- #


class TestDeleteEntry:
    """DELETE /v1/spending_account/{id} -- delete an entry."""

    @pytest_asyncio.fixture(autouse=True, scope="class", loop_scope="session")
    async def cleanup(self, client: AsyncClient):
        yield
        await _delete_all(client)

    async def test__success_returns_200(self, client: AsyncClient):
        account = f"DEL-{uuid4().hex[:8]}"
        entry = await _post_entry(client, _entry_payload(account, month=1, year=2025))

        resp = await client.delete(f"{BASE_URL}/{entry['id']}")

        assert resp.status_code == 200

    async def test__entry_no_longer_in_list(self, client: AsyncClient):
        account = f"DEL-{uuid4().hex[:8]}"
        entry = await _post_entry(client, _entry_payload(account, month=2, year=2025))
        await client.delete(f"{BASE_URL}/{entry['id']}")

        resp = await client.get(f"{BASE_URL}/list", params={"accountName": account.upper(), "size": 100})

        assert entry["id"] not in [e["id"] for e in resp.json()["spendingEntries"]]

    async def test__not_found_returns_404(self, client: AsyncClient):
        resp = await client.delete(f"{BASE_URL}/{uuid4()}")

        assert resp.status_code == 404

    async def test__second_delete_returns_404(self, client: AsyncClient):
        account = f"DEL-{uuid4().hex[:8]}"
        entry = await _post_entry(client, _entry_payload(account, month=3, year=2025))
        await client.delete(f"{BASE_URL}/{entry['id']}")

        resp = await client.delete(f"{BASE_URL}/{entry['id']}")

        assert resp.status_code == 404


# ---------------------------------------------- Input Validation (422) ---------------------------------------------- #


class TestInputValidation:
    """FastAPI/Pydantic field validation -- expects 422 Unprocessable Entity."""

    async def test__create_missing_required_field_returns_422(self, client: AsyncClient):
        # 'month' deliberately omitted
        payload = {
            "accountName": "VALID",
            "year": 2025,
            "startingBalance": 1000.0,
            "currentBalance": 800.0,
            "currentCredit": 100.0,
        }
        resp = await client.post(BASE_URL, json=payload)
        assert resp.status_code == 422

    async def test__create_month_zero_returns_422(self, client: AsyncClient):
        resp = await client.post(BASE_URL, json=_entry_payload("VALID", month=0, year=2025))
        assert resp.status_code == 422

    async def test__create_month_thirteen_returns_422(self, client: AsyncClient):
        resp = await client.post(BASE_URL, json=_entry_payload("VALID", month=13, year=2025))
        assert resp.status_code == 422

    async def test__create_year_below_minimum_returns_422(self, client: AsyncClient):
        resp = await client.post(BASE_URL, json=_entry_payload("VALID", month=1, year=1999))
        assert resp.status_code == 422

    async def test__create_year_above_maximum_returns_422(self, client: AsyncClient):
        resp = await client.post(BASE_URL, json=_entry_payload("VALID", month=1, year=2101))
        assert resp.status_code == 422

    async def test__list_invalid_sort_field_returns_422(self, client: AsyncClient):
        resp = await client.get(f"{BASE_URL}/list", params={"sortBy": "not_a_real_field"})
        assert resp.status_code == 422

    async def test__list_month_filter_below_minimum_returns_422(self, client: AsyncClient):
        resp = await client.get(f"{BASE_URL}/list", params={"month": 0})
        assert resp.status_code == 422

    async def test__list_month_filter_above_maximum_returns_422(self, client: AsyncClient):
        resp = await client.get(f"{BASE_URL}/list", params={"month": 13})
        assert resp.status_code == 422
