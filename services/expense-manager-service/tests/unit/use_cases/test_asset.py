# ruff: noqa: PLR2004, E501
"""Unit tests for the wealth manager assets service use case."""

from datetime import UTC, datetime

import pytest

from app.infrastructures.postgres_db.models.asset_category import AssetCategoryModel
from app.infrastructures.postgres_db.models.asset_subcategory import AssetSubcategoryModel
from app.use_cases.asset import AssetService
from app.use_cases.models.asset import AssetCreate, AssetTransactionCreate, AssetUpdate


@pytest.fixture
def asset_service(asset_repo):
    """Provide an instance of AssetService."""
    return AssetService(asset_repository=asset_repo)


async def get_categories_map(asset_service):
    """Retrieve a lookup map for seeded category codes to category IDs."""
    cats = await asset_service.get_all_categories()
    if not cats:
        # Seed categories if database is empty (standard for fresh test DBs)
        async with await asset_service.asset_repository._get_session() as session:
            session.add_all(
                [
                    AssetCategoryModel(
                        id="5d287bc128794c4fae855f75e7a9e6b1",
                        name="Equity",
                        code="EQUITY",
                        description="Stocks, Mutual Funds, ETFs",
                    ),
                    AssetCategoryModel(
                        id="2f4a47da2f174780a424e7561a09d3b4",
                        name="Debt",
                        code="DEBT",
                        description="Fixed Deposits, PPF, Bonds, EPF",
                    ),
                    AssetCategoryModel(
                        id="e439bb7f10b741008d5b88c426f6e522",
                        name="Real Estate",
                        code="REAL_ESTATE",
                        description="Land, Residential/Commercial Properties",
                    ),
                    AssetCategoryModel(
                        id="a434c382103b417e914e9f7823f6e111",
                        name="Commodities",
                        code="COMMODITIES",
                        description="Physical/Digital Gold, Silver",
                    ),
                    AssetCategoryModel(
                        id="c831c382123b417e914e9f7823f6e222",
                        name="Cash / Bank",
                        code="CASH_BANK",
                        description="Savings accounts, Cash",
                    ),
                    AssetSubcategoryModel(
                        id="b76e3bb81d914dcc8efee7ebaab729e3",
                        category_id="5d287bc128794c4fae855f75e7a9e6b1",
                        name="Stock",
                        code="STOCK",
                        description="Stocks/mutual funds unit-based valuation details",
                        valuation_type="UNIT_BASED",
                        has_interest=False,
                        has_maturity=False,
                    ),
                    AssetSubcategoryModel(
                        id="504bdb52c67c43558f901550cc05fdac",
                        category_id="2f4a47da2f174780a424e7561a09d3b4",
                        name="PPF",
                        code="PPF",
                        description="PPF value-based valuation details with interest",
                        valuation_type="VALUE_BASED",
                        has_interest=True,
                        has_maturity=True,
                    ),
                ]
            )
            await session.commit()
        cats = await asset_service.get_all_categories()
    return {c.code: c.id for c in cats}


class TestAssetServiceCategories:
    """Tests for asset category retrievals."""

    async def test_get_all_categories(self, asset_service):
        """Verify standard categories are pre-seeded."""
        await get_categories_map(asset_service)
        cats = await asset_service.get_all_categories()
        assert len(cats) >= 5
        codes = [c.code for c in cats]
        assert "EQUITY" in codes
        assert "DEBT" in codes
        assert "REAL_ESTATE" in codes
        assert "COMMODITIES" in codes
        assert "CASH_BANK" in codes


class TestAssetServiceCRUD:
    """Tests for Asset CRUD operations and recalculation workflows."""

    async def test_create_and_recalculate_flat_asset(self, asset_service):
        """Test creating a simple flat asset and verifying calculations."""
        categories_map = await get_categories_map(asset_service)
        debt_cat_id = categories_map["DEBT"]
        asset_in = AssetCreate(
            category_id=debt_cat_id,
            name="PPF Account",
            sub_category="PPF",
            initial_amount=50000.00,
            notes="Self PPF account",
        )
        asset = await asset_service.create_asset(asset_in)

        assert asset.name == "PPF Account"
        assert asset.category_code == "DEBT"
        assert asset.sub_category == "PPF"
        assert asset.invested_value == 50000.00
        assert asset.current_value == 50000.00  # Default to invested if no revaluation
        assert asset.absolute_returns == 0.00
        assert asset.percentage_returns == 0.00

        # Revalue the asset
        reval_tx = AssetTransactionCreate(
            transaction_type="REVALUE",
            amount=55000.00,
            transaction_date=datetime.now(UTC),
            description="Interest credited FY2026",
        )
        await asset_service.add_transaction(asset.id, reval_tx)

        # Retrieve and verify updated values
        updated = await asset_service.get_asset_by_id(asset.id)
        assert updated.invested_value == 50000.00
        assert updated.current_value == 55000.00
        assert updated.absolute_returns == 5000.00
        assert updated.percentage_returns == 10.00

        # Clean up
        await asset_service.delete_asset(asset.id)
        with pytest.raises(ValueError):
            await asset_service.get_asset_by_id(asset.id)

    async def test_create_and_recalculate_unit_based_asset(self, asset_service):
        """Test creating a unit-based asset (Commodity Gold) and verifying live calculations."""
        categories_map = await get_categories_map(asset_service)
        comm_cat_id = categories_map["COMMODITIES"]
        asset_in = AssetCreate(
            category_id=comm_cat_id,
            name="Gold Jewelry",
            sub_category="GOLD_24K",  # Resolves mock live price (15863.18)
            initial_amount=909000.00,
            units=250.00,  # 250 grams
            price_per_unit=3636.00,  # ₹3636 per gram
            notes="Wedding gold",
        )
        asset = await asset_service.create_asset(asset_in)

        # Invested cash flow: 250 units * ₹3636 PPU = 909,000.00
        assert asset.invested_value == 909000.00
        # Current valuation: 250 units * ₹15,863.18 mock live price = ₹3,965,795.00
        assert asset.current_value == 250.00 * 15863.18
        assert asset.absolute_returns == (250.00 * 15863.18) - 909000.00
        assert asset.percentage_returns > 300.00  # ROI returns > 300%

        # Update metadata
        update_in = AssetUpdate(
            category_id=comm_cat_id,
            name="Gold Jewelry Renamed",
            sub_category="GOLD_24K",
            notes="Updated notes",
        )
        edited = await asset_service.update_asset(asset.id, update_in)
        assert edited.name == "Gold Jewelry Renamed"

        # Log a BUY transaction of 50 more grams at ₹5000 per gram
        buy_tx = AssetTransactionCreate(
            transaction_type="BUY",
            amount=250000.00,
            units=50.00,
            price_per_unit=5000.00,
            description="Bought extra gold coin",
        )
        await asset_service.add_transaction(asset.id, buy_tx)

        # Recalculated state:
        # Total units: 250 + 50 = 300 grams
        # Total invested: 909,000 + 250,000 = 1,159,000
        # Current Value: 300 * 15,863.18 = 4,758,954
        recalced = await asset_service.get_asset_by_id(asset.id)
        assert recalced.invested_value == 1159000.00
        assert recalced.current_value == 300.00 * 15863.18

        # Log a SELL transaction of 20 grams
        sell_tx = AssetTransactionCreate(
            transaction_type="SELL",
            amount=317263.60,
            units=20.00,
            price_per_unit=15863.18,
            description="Sold 20 grams coin",
        )
        await asset_service.add_transaction(asset.id, sell_tx)

        # Recalculated state:
        # Total units: 300 - 20 = 280 grams
        # Total invested cost (reduced prorated/cashflow): 1,159,000 - (20 * 5000 approx base cost or transactional cashflow deduction)
        # Note: Recalculator tracks Cash flow base: buys_invested - sells_invested = (909000 + 250000) - (20 * 15863.18) = 841,736.4
        recalced_sell = await asset_service.get_asset_by_id(asset.id)
        assert recalced_sell.invested_value == 841736.4
        assert recalced_sell.current_value == 280.00 * 15863.18

        # Verify transaction log
        txs = await asset_service.get_transactions_for_asset(asset.id)
        assert len(txs) == 3
        # First in list is latest due to DESC sort
        assert txs[0].transaction_type == "SELL"

        # Delete transaction (roll back the sell)
        await asset_service.delete_transaction(txs[0].id)
        recalced_rollback = await asset_service.get_asset_by_id(asset.id)
        # Units should return to 300
        assert recalced_rollback.current_value == 300.00 * 15863.18

        # Clean up
        await asset_service.delete_asset(asset.id)


class TestAssetServiceSummary:
    """Tests for portfolio summaries aggregates."""

    async def test_get_asset_summary(self, asset_service):
        """Create multiple assets and verify portfolio summary aggregation metrics."""
        categories_map = await get_categories_map(asset_service)
        # Clean existing assets
        existing_assets = await asset_service.list_assets()
        for a in existing_assets:
            await asset_service.delete_asset(a.id)

        # Add Asset 1: Flat cash balance
        cb_cat_id = categories_map["CASH_BANK"]
        asset_in1 = AssetCreate(
            category_id=cb_cat_id,
            name="SBI Savings",
            sub_category="Savings",
            initial_amount=10000.00,
        )
        a1 = await asset_service.create_asset(asset_in1)

        # Add Asset 2: Equity fund
        eq_cat_id = categories_map["EQUITY"]
        asset_in2 = AssetCreate(
            category_id=eq_cat_id,
            name="Mutual Fund",
            sub_category="MF",
            initial_amount=20000.00,
        )
        a2 = await asset_service.create_asset(asset_in2)

        # Revalue Mutual Fund to 25000
        reval_tx = AssetTransactionCreate(
            transaction_type="REVALUE",
            amount=25000.00,
        )
        await asset_service.add_transaction(a2.id, reval_tx)

        # Retrieve summary
        summary = await asset_service.get_asset_summary()
        # Total invested: 10,000 + 20,000 = 30,000
        assert summary.total_invested == 30000.00
        # Total current: 10,000 + 25,000 = 35,000
        assert summary.total_current == 35000.00
        # Total returns: 35,000 - 30,000 = 5,000
        assert summary.total_returns == 5000.00
        assert round(summary.percentage_returns, 2) == 16.67

        # Check category breakdowns
        breakdowns = {b.category_code: b for b in summary.category_breakdowns}
        assert breakdowns["CASH_BANK"].total_current == 10000.00
        assert breakdowns["EQUITY"].total_current == 25000.00
        assert breakdowns["EQUITY"].percentage_returns == 25.00

        # Clean up
        await asset_service.delete_asset(a1.id)
        await asset_service.delete_asset(a2.id)
