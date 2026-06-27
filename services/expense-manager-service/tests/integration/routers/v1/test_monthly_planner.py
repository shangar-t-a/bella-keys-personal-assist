"""Integration tests for the monthly planner endpoints.

Endpoints under test:
    GET    /v1/monthly-planner/categories
    POST   /v1/monthly-planner/categories
    DELETE /v1/monthly-planner/categories/{category_id}
    GET    /v1/monthly-planner/summary/{year}/{month}
    PUT    /v1/monthly-planner/summary/{year}/{month}/salary
    GET    /v1/monthly-planner/expenses/{year}/{month}
    POST   /v1/monthly-planner/expenses/{year}/{month}
    PUT    /v1/monthly-planner/expenses/{expense_id}
    DELETE /v1/monthly-planner/expenses/{expense_id}
    POST   /v1/monthly-planner/expenses/{year}/{month}/reset
    POST   /v1/monthly-planner/expenses/{year}/{month}/sync
"""

from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import AsyncClient

# Constants & Helpers

BASE_URL = "/v1/monthly-planner"


async def _post_category(client: AsyncClient, name: str, category_l1: str = "spending") -> dict:
    """Helper to create a category."""
    resp = await client.post(f"{BASE_URL}/categories", json={"name": name, "category_l1": category_l1})
    assert resp.status_code == 200, resp.text
    return resp.json()


async def _post_expense(client: AsyncClient, year: int, month: int, payload: dict) -> dict:
    """Helper to create an expense."""
    resp = await client.post(f"{BASE_URL}/expenses/{year}/{month}", json=payload)
    assert resp.status_code == 200, resp.text
    return resp.json()


# Categories


class TestCategoriesEndpoints:
    """Tests for Category endpoints."""

    @pytest_asyncio.fixture(autouse=True, scope="class", loop_scope="session")
    async def cleanup(self, client: AsyncClient):
        yield
        resp = await client.get(f"{BASE_URL}/categories")
        if resp.status_code == 200:
            for cat in resp.json():
                await client.delete(f"{BASE_URL}/categories/{cat['id']}")

    async def test__add_and_list_category(self, client: AsyncClient):
        # Add category
        name = f"TestCat-{uuid4().hex[:8]}"
        cat = await _post_category(client, name)
        assert cat["name"] == name
        assert cat["category_l1"] == "spending"
        assert "id" in cat

        # List categories
        resp = await client.get(f"{BASE_URL}/categories")
        assert resp.status_code == 200
        cats = resp.json()
        assert any(c["id"] == cat["id"] for c in cats)

    async def test__delete_category(self, client: AsyncClient):
        name = f"DelCat-{uuid4().hex[:8]}"
        cat = await _post_category(client, name)

        resp = await client.delete(f"{BASE_URL}/categories/{cat['id']}")
        assert resp.status_code == 204

        resp_list = await client.get(f"{BASE_URL}/categories")
        assert not any(c["id"] == cat["id"] for c in resp_list.json())


# Summary


class TestSummaryEndpoints:
    """Tests for Summary endpoints."""

    async def test__get_summary_creates_default(self, client: AsyncClient):
        year = 2026
        month = 1
        resp = await client.get(f"{BASE_URL}/summary/{year}/{month}")
        assert resp.status_code == 200
        data = resp.json()
        assert data["month"] == month
        assert data["year"] == year
        assert data["salary"] == 0.0

    async def test__update_salary(self, client: AsyncClient):
        year = 2026
        month = 2
        resp = await client.put(f"{BASE_URL}/summary/{year}/{month}/salary", json={"salary": 8500.0})
        assert resp.status_code == 200
        data = resp.json()
        assert data["salary"] == 8500.0

        # Verify persistence
        get_resp = await client.get(f"{BASE_URL}/summary/{year}/{month}")
        assert get_resp.json()["salary"] == 8500.0


# Expenses


class TestExpensesEndpoints:
    """Tests for Expenses endpoints."""

    async def test__crud_expenses(self, client: AsyncClient):
        year = 2026
        month = 5

        # Create
        payload = {
            "name": "Test Expense",
            "amount": 100.0,
            "category_l1": "spending",
            "category_l2": "General",
            "is_recurring": True,
        }
        expense = await _post_expense(client, year, month, payload)
        assert expense["name"] == "Test Expense"
        assert expense["status"] == "pending"

        # List
        resp = await client.get(f"{BASE_URL}/expenses/{year}/{month}")
        assert resp.status_code == 200
        assert any(e["id"] == expense["id"] for e in resp.json())

        # Update
        update_payload = {
            "name": "Updated Expense",
            "amount": 150.0,
            "status": "settled",
            "category_l1": "spending",
            "category_l2": "General",
            "is_recurring": True,
        }
        put_resp = await client.put(f"{BASE_URL}/expenses/{expense['id']}", json=update_payload)
        assert put_resp.status_code == 200
        assert put_resp.json()["name"] == "Updated Expense"
        assert put_resp.json()["status"] == "settled"

        # Delete
        del_resp = await client.delete(f"{BASE_URL}/expenses/{expense['id']}")
        assert del_resp.status_code == 204

        # Verify deletion
        list_after = await client.get(f"{BASE_URL}/expenses/{year}/{month}")
        assert not any(e["id"] == expense["id"] for e in list_after.json())

    async def test__reset_statuses(self, client: AsyncClient):
        year = 2026
        month = 6

        # Create two expenses
        payload1 = {"name": "Exp 1", "amount": 10.0, "category_l1": "spending", "category_l2": "Misc", "is_recurring": False}
        payload2 = {"name": "Exp 2", "amount": 20.0, "category_l1": "spending", "category_l2": "Misc", "is_recurring": False}
        e1 = await _post_expense(client, year, month, payload1)
        e2 = await _post_expense(client, year, month, payload2)

        # Settle one
        await client.put(f"{BASE_URL}/expenses/{e1['id']}", json={**payload1, "status": "settled"})

        # Reset all
        reset_resp = await client.post(f"{BASE_URL}/expenses/{year}/{month}/reset")
        assert reset_resp.status_code == 204

        # Verify both are pending
        list_resp = await client.get(f"{BASE_URL}/expenses/{year}/{month}")
        expenses = list_resp.json()
        assert all(e["status"] == "pending" for e in expenses if e["id"] in (e1["id"], e2["id"]))

    async def test__sync_from_previous_month(self, client: AsyncClient):
        # Prev month: March 2026
        year_prev = 2026
        month_prev = 3
        
        # Add recurring expense
        await _post_expense(client, year_prev, month_prev, {
            "name": "Recurring Sub", "amount": 15.0, "category_l1": "spending", "category_l2": "Subs", "is_recurring": True
        })
        # Add non-recurring
        await _post_expense(client, year_prev, month_prev, {
            "name": "One Time", "amount": 100.0, "category_l1": "spending", "category_l2": "Misc", "is_recurring": False
        })

        # Sync to April 2026
        sync_resp = await client.post(f"{BASE_URL}/expenses/{year_prev}/{month_prev + 1}/sync")
        assert sync_resp.status_code == 200
        synced_expenses = sync_resp.json()

        # Verify only recurring is synced
        assert any(e["name"] == "Recurring Sub" for e in synced_expenses)
        assert not any(e["name"] == "One Time" for e in synced_expenses)
