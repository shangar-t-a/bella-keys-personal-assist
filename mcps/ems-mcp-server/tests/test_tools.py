# ruff: noqa: PLR2004, E501
"""Unit tests for EMS MCP Server tools using respx mocks."""

import os
import jwt
from pydantic import SecretStr
import pytest
import respx
from httpx import Response

from app.main import EMSTokenVerifier
from app.settings import get_settings
from app.tools.accounts import (
    delete_account,
    get_account,
    get_or_create_account,
    list_accounts,
    update_account_name,
)
from app.tools.assets import (
    add_asset_transaction,
    create_asset,
    list_asset_categories,
    list_assets,
    update_asset,
)
from app.tools.liabilities import (
    get_liability_projections,
    list_liability_categories,
)
from app.tools.monthly_planner import (
    add_monthly_category,
    get_monthly_summary,
    list_monthly_categories,
)
from app.tools.periods import (
    delete_period,
    get_or_create_period,
    get_period,
    list_periods,
    update_period,
)
from app.tools.savings_buckets import (
    create_savings_bucket_transaction,
    list_savings_buckets,
)
from app.tools.spending_entries import (
    add_spending_entry,
    delete_spending_entry,
    edit_spending_entry,
    list_spending_entries,
    list_spending_entries_for_account,
)
from app.tools.wealth import (
    get_wealth_allocation,
    get_wealth_summary,
)


@pytest.fixture
def ems_url() -> str:
    """Provide the mocked EMS base URL from settings."""
    return get_settings().EMS_BASE_URL


@respx.mock
async def test_error_handling_robustness(ems_url: str) -> None:
    """Verify that backend errors are captured and returned with descriptive ValueErrors."""
    respx.get(f"{ems_url}/v1/account/list").mock(
        return_value=Response(status_code=400, json={"detail": "Bad Request detail"})
    )

    with pytest.raises(ValueError, match="EMS Error \\(400\\): Bad Request detail"):
        await list_accounts()

    respx.get(f"{ems_url}/v1/account/list").mock(
        return_value=Response(status_code=500, content=b"Server crashed text")
    )

    with pytest.raises(ValueError, match="EMS Error \\(500\\): Server crashed text"):
        await list_accounts()


@respx.mock
async def test_accounts_tools(ems_url: str) -> None:
    """Test all account tools CRUD happy paths."""
    # List Accounts
    respx.get(f"{ems_url}/v1/account/list").mock(
        return_value=Response(
            status_code=200, json=[{"id": "acc1", "account_name": "ICICI"}]
        )
    )
    res = await list_accounts()
    assert len(res) == 1
    assert res[0]["account_name"] == "ICICI"

    # Get Account
    respx.get(f"{ems_url}/v1/account/acc1").mock(
        return_value=Response(
            status_code=200, json={"id": "acc1", "account_name": "ICICI"}
        )
    )
    res = await get_account("acc1")
    assert res["account_name"] == "ICICI"

    # Create/Get-or-Create Account
    respx.post(
        f"{ems_url}/v1/account/get_or_create", json={"account_name": "HDFC"}
    ).mock(
        return_value=Response(
            status_code=200, json={"id": "acc2", "account_name": "HDFC"}
        )
    )
    res = await get_or_create_account("HDFC")
    assert res["id"] == "acc2"

    # Update Account Name
    respx.put(
        f"{ems_url}/v1/account/acc1", json={"account_name": "ICICI-Updated"}
    ).mock(
        return_value=Response(
            status_code=200, json={"id": "acc1", "account_name": "ICICI-Updated"}
        )
    )
    res = await update_account_name("acc1", "ICICI-Updated")
    assert res["account_name"] == "ICICI-Updated"

    # Delete Account
    respx.delete(f"{ems_url}/v1/account/acc1").mock(
        return_value=Response(status_code=204)
    )
    res = await delete_account("acc1")
    assert res["status"] == "success"


@respx.mock
async def test_periods_tools(ems_url: str) -> None:
    """Test all period tools CRUD happy paths."""
    # List Periods
    respx.get(f"{ems_url}/v1/period/list").mock(
        return_value=Response(
            status_code=200, json=[{"id": "p1", "month": 6, "year": 2026}]
        )
    )
    res = await list_periods()
    assert len(res) == 1
    assert res[0]["month"] == 6

    # Get Period
    respx.get(f"{ems_url}/v1/period/p1").mock(
        return_value=Response(
            status_code=200, json={"id": "p1", "month": 6, "year": 2026}
        )
    )
    res = await get_period("p1")
    assert res["year"] == 2026

    # Create Period
    respx.post(
        f"{ems_url}/v1/period/get_or_create", json={"month": 7, "year": 2026}
    ).mock(
        return_value=Response(
            status_code=200, json={"id": "p2", "month": 7, "year": 2026}
        )
    )
    res = await get_or_create_period(7, 2026)
    assert res["id"] == "p2"

    # Update Period
    respx.put(f"{ems_url}/v1/period/p1", json={"month": 8, "year": 2026}).mock(
        return_value=Response(
            status_code=200, json={"id": "p1", "month": 8, "year": 2026}
        )
    )
    res = await update_period("p1", 8, 2026)
    assert res["month"] == 8

    # Delete Period
    respx.delete(f"{ems_url}/v1/period/p1").mock(return_value=Response(status_code=204))
    res = await delete_period("p1")
    assert res["status"] == "success"


@respx.mock
async def test_spending_entries_tools(ems_url: str) -> None:
    """Test spending entries tools happy paths."""
    # List Entries
    respx.get(
        f"{ems_url}/v1/spending_account/list?page=0&size=12&sortBy=year&sortOrder=asc"
    ).mock(
        return_value=Response(
            status_code=200, json={"spending_entries": [], "page": {}}
        )
    )
    res = await list_spending_entries()
    assert "spending_entries" in res

    # List Entries for Account
    respx.get(
        f"{ems_url}/v1/spending_account/acc1/list?page=0&size=12&sortBy=year&sortOrder=asc"
    ).mock(
        return_value=Response(
            status_code=200, json={"spending_entries": [], "page": {}}
        )
    )
    res = await list_spending_entries_for_account("acc1")
    assert "spending_entries" in res

    # Add Entry
    json_payload = {
        "account_name": "ICICI",
        "month": 6,
        "year": 2026,
        "starting_balance": 1000.0,
        "current_balance": 800.0,
        "current_credit": 200.0,
    }
    respx.post(f"{ems_url}/v1/spending_account", json=json_payload).mock(
        return_value=Response(status_code=200, json={"id": "entry1", **json_payload})
    )
    res = await add_spending_entry("ICICI", 6, 2026, 1000.0, 800.0, 200.0)
    assert res["id"] == "entry1"

    # Edit Entry
    respx.put(f"{ems_url}/v1/spending_account/entry1", json=json_payload).mock(
        return_value=Response(status_code=200, json={"id": "entry1", **json_payload})
    )
    res = await edit_spending_entry("entry1", "ICICI", 6, 2026, 1000.0, 800.0, 200.0)
    assert res["current_balance"] == 800.0

    # Delete Entry
    respx.delete(f"{ems_url}/v1/spending_account/entry1").mock(
        return_value=Response(status_code=204)
    )
    res = await delete_spending_entry("entry1")
    assert res["status"] == "success"


@respx.mock
async def test_assets_tools(ems_url: str) -> None:
    """Test asset tools happy paths and parameter nesting."""
    # List Categories
    respx.get(f"{ems_url}/v1/assets/categories").mock(
        return_value=Response(
            status_code=200, json=[{"id": "cat1", "name": "Mutual Funds"}]
        )
    )
    res = await list_asset_categories()
    assert len(res) == 1

    # List Assets
    respx.get(f"{ems_url}/v1/assets?categoryId=cat1&search=HDFC").mock(
        return_value=Response(status_code=200, json=[])
    )
    res = await list_assets(category_id="cat1", search="HDFC")
    assert isinstance(res, list)

    # Create Asset (with interest & unit nesting)
    json_payload = {
        "categoryId": "cat1",
        "name": "Nippon Liquid",
        "subcategoryId": "sub1",
        "initialAmount": 5000.0,
        "notes": "My savings asset",
        "interestDetails": {
            "interestRate": 6.5,
            "compounding": "MONTHLY",
            "maturityDate": "2027-06-30T00:00:00",
        },
        "unitDetails": {
            "units": 100.0,
            "pricePerUnit": 50.0,
        },
    }
    respx.post(f"{ems_url}/v1/assets", json=json_payload).mock(
        return_value=Response(
            status_code=201, json={"id": "asset1", "name": "Nippon Liquid"}
        )
    )
    res = await create_asset(
        category_id="cat1",
        name="Nippon Liquid",
        subcategory_id="sub1",
        initial_amount=5000.0,
        interest_rate=6.5,
        interest_compounding="MONTHLY",
        maturity_date="2027-06-30T00:00:00",
        units=100.0,
        price_per_unit=50.0,
        notes="My savings asset",
    )
    assert res["id"] == "asset1"

    # Update Asset
    respx.put(
        f"{ems_url}/v1/assets/asset1",
        json={"notes": "Updated notes"},
    ).mock(
        return_value=Response(
            status_code=200, json={"id": "asset1", "notes": "Updated notes"}
        )
    )
    res = await update_asset("asset1", notes="Updated notes")
    assert res["notes"] == "Updated notes"

    # Add Transaction
    respx.post(
        f"{ems_url}/v1/assets/asset1/transactions",
        json={
            "transactionType": "BUY",
            "amount": 2000.0,
            "transactionDate": None,
            "description": "Top-up",
            "unitDetails": {
                "units": 40.0,
                "pricePerUnit": 50.0,
            },
        },
    ).mock(return_value=Response(status_code=201, json={"id": "t1"}))
    res = await add_asset_transaction(
        asset_id="asset1",
        transaction_type="BUY",
        amount=2000.0,
        units=40.0,
        price_per_unit=50.0,
        description="Top-up",
    )
    assert res["id"] == "t1"


@respx.mock
async def test_liabilities_tools(ems_url: str) -> None:
    """Test liability tools happy paths and nested parameters."""
    # List categories
    respx.get(f"{ems_url}/v1/liabilities/categories").mock(
        return_value=Response(status_code=200, json=[])
    )
    res = await list_liability_categories()
    assert isinstance(res, list)

    # Get projections
    respx.get(f"{ems_url}/v1/liabilities/liab1/projections").mock(
        return_value=Response(
            status_code=200, json={"metrics": {}, "projectionPoints": []}
        )
    )
    res = await get_liability_projections("liab1")
    assert "metrics" in res


@respx.mock
async def test_monthly_planner_tools(ems_url: str) -> None:
    """Test monthly planner tools happy paths."""
    # List custom categories
    respx.get(f"{ems_url}/v1/monthly-planner/categories").mock(
        return_value=Response(status_code=200, json=[])
    )
    res = await list_monthly_categories()
    assert isinstance(res, list)

    # Add category
    respx.post(
        f"{ems_url}/v1/monthly-planner/categories",
        json={"name": "Groceries", "category_l1": "spending"},
    ).mock(
        return_value=Response(status_code=200, json={"id": "mc1", "name": "Groceries"})
    )
    res = await add_monthly_category("Groceries", "spending")
    assert res["id"] == "mc1"

    # Get monthly summary
    respx.get(f"{ems_url}/v1/monthly-planner/summary/2026/6").mock(
        return_value=Response(
            status_code=200, json={"salary": 50000.0, "month": 6, "year": 2026}
        )
    )
    res = await get_monthly_summary(2026, 6)
    assert res["salary"] == 50000.0


@respx.mock
async def test_savings_buckets_tools(ems_url: str) -> None:
    """Test savings buckets tools happy paths."""
    # List buckets
    respx.get(f"{ems_url}/v1/savings_buckets/list/acc1").mock(
        return_value=Response(status_code=200, json=[])
    )
    res = await list_savings_buckets("acc1")
    assert isinstance(res, list)

    # Create savings bucket transaction
    respx.post(
        f"{ems_url}/v1/savings_buckets/acc1/transaction",
        json={
            "sourceBucketId": "b1",
            "destinationBucketId": "b2",
            "amount": 500.0,
            "transactionType": "transfer",
            "description": "Moved funds",
            "transactionDate": None,
        },
    ).mock(return_value=Response(status_code=201, json={"id": "tx99"}))
    res = await create_savings_bucket_transaction(
        account_id="acc1",
        amount=500.0,
        transaction_type="transfer",
        description="Moved funds",
        source_bucket_id="b1",
        destination_bucket_id="b2",
    )
    assert res["id"] == "tx99"


@respx.mock
async def test_wealth_tools(ems_url: str) -> None:
    """Test wealth summary and allocations."""
    # Get wealth summary
    respx.get(f"{ems_url}/v1/wealth/summary").mock(
        return_value=Response(status_code=200, json={"netWorth": 100000.0})
    )
    res = await get_wealth_summary()
    assert res["netWorth"] == 100000.0

    # Get allocation
    respx.get(f"{ems_url}/v1/wealth/allocation").mock(
        return_value=Response(status_code=200, json={"assetAllocation": {}})
    )
    res = await get_wealth_allocation()
    assert "assetAllocation" in res


async def test_ems_token_verifier() -> None:
    """Test EMSTokenVerifier signature and audience validation."""
    verifier = EMSTokenVerifier()

    # Configure test env
    settings = get_settings()
    old_secret = os.environ.get("JWT_SECRET")
    os.environ["JWT_SECRET"] = "test_mcp_secret"
    old_settings_secret = settings.JWT_SECRET
    settings.JWT_SECRET = SecretStr("test_mcp_secret")

    # 1. Invalid signature
    res = await verifier.verify_token("invalid.jwt.token")
    assert res is None

    # 3. Valid token, invalid audience
    token_invalid_aud = jwt.encode(
        {"sub": "shangar", "role": "admin", "aud": "http://wrong-audience"},
        "test_mcp_secret",
        algorithm="HS256",
    )
    res = await verifier.verify_token(token_invalid_aud)
    assert res is None

    # 4. Valid token, valid audience
    token_valid_aud = jwt.encode(
        {"sub": "shangar", "role": "admin", "aud": "http://localhost:8001/mcp"},
        "test_mcp_secret",
        algorithm="HS256",
    )
    res = await verifier.verify_token(token_valid_aud)
    assert res is not None
    assert res.claims["sub"] == "shangar"
    assert res.claims["role"] == "admin"

    # Clean up test env
    settings.JWT_SECRET = old_settings_secret
    if old_secret is not None:
        os.environ["JWT_SECRET"] = old_secret
    else:
        os.environ.pop("JWT_SECRET", None)
