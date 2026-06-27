# ruff: noqa: PLR2004, E501
"""Unit tests for the wealth manager assets service use case."""

from datetime import UTC, datetime

import pytest

from app.infrastructures.postgres_db.models.asset_category import AssetCategoryModel
from app.infrastructures.postgres_db.models.asset_subcategory import AssetSubcategoryModel
from app.entities.models.asset import AssetTransactionType, CompoundingFrequency
from app.use_cases.asset import AssetService
from app.use_cases.models.asset import (
    AssetCreate,
    AssetInterestDetails,
    AssetTransactionCreate,
    AssetUnitDetails,
    AssetUpdate,
)


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
                    AssetSubcategoryModel(
                        id="c91d4bb83e914acc9fcee8ebcbc840f4",
                        category_id="a434c382103b417e914e9f7823f6e111",
                        name="Physical Gold / Silver",
                        code="GOLD_24K",
                        description="Unit-based valuation for gold/silver",
                        valuation_type="UNIT_BASED",
                        has_interest=False,
                        has_maturity=False,
                    ),
                ]
            )
            await session.commit()
        cats = await asset_service.get_all_categories()
    return {c.code: c.id for c in cats}


async def get_subcategory_map(asset_service):
    """Retrieve a lookup map for seeded subcategory codes to subcategory IDs."""
    cats = await asset_service.get_all_categories()
    sub_map = {}
    for cat in cats:
        for sub in cat.subcategories:
            sub_map[sub.code] = sub.id
    return sub_map


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
        subcategory_map = await get_subcategory_map(asset_service)
        debt_cat_id = categories_map["DEBT"]
        ppf_sub_id = subcategory_map.get("PPF")

        asset_in = AssetCreate(
            category_id=debt_cat_id,
            name="PPF Account",
            subcategory_id=ppf_sub_id,
            initial_amount=50000.00,
            interest_details=AssetInterestDetails(
                interest_rate=7.1,
                compounding=CompoundingFrequency.YEARLY,
            ),
            notes="Self PPF account",
        )
        asset = await asset_service.create_asset(asset_in)

        assert asset.name == "PPF Account"
        assert asset.category_code == "DEBT"
        assert asset.interest_rate == 7.1
        assert asset.interest_compounding == CompoundingFrequency.YEARLY
        assert asset.invested_value == 50000.00
        assert asset.current_value == 50000.00  # Default to invested if no revaluation
        assert asset.absolute_returns == 0.00
        assert asset.percentage_returns == 0.00

        # Revalue the asset
        reval_tx = AssetTransactionCreate(
            transaction_type=AssetTransactionType.REVALUE,
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
        subcategory_map = await get_subcategory_map(asset_service)
        comm_cat_id = categories_map["COMMODITIES"]
        gold_sub_id = subcategory_map.get("GOLD_24K")  # Resolves mock live price (15863.18)

        asset_in = AssetCreate(
            category_id=comm_cat_id,
            name="Gold Jewelry",
            subcategory_id=gold_sub_id,
            initial_amount=909000.00,
            unit_details=AssetUnitDetails(
                units=250.00,  # 250 grams
                price_per_unit=3636.00,  # ₹3636 per gram
            ),
            notes="Wedding gold",
        )
        asset = await asset_service.create_asset(asset_in)

        # Invested cash flow: 250 units * ₹3636 PPU = 909,000.00
        assert asset.invested_value == 909000.00
        # Current valuation: 250 units * ₹15,863.18 mock live price = ₹3,965,795.00
        assert asset.current_value == 250.00 * 15863.18
        assert asset.absolute_returns == (250.00 * 15863.18) - 909000.00
        assert asset.percentage_returns > 300.00  # ROI returns > 300%

        # Update metadata (PATCH — only name changes)
        update_in = AssetUpdate(
            name="Gold Jewelry Renamed",
        )
        edited = await asset_service.update_asset(asset.id, update_in)
        assert edited.name == "Gold Jewelry Renamed"
        # Verify PATCH preserved subcategory_id and notes
        assert edited.subcategory_id == gold_sub_id
        assert edited.notes == "Wedding gold"

        # Log a BUY transaction of 50 more grams at ₹5000 per gram
        buy_tx = AssetTransactionCreate(
            transaction_type=AssetTransactionType.BUY,
            amount=250000.00,
            unit_details=AssetUnitDetails(units=50.00, price_per_unit=5000.00),
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
            transaction_type=AssetTransactionType.SELL,
            amount=317263.60,
            unit_details=AssetUnitDetails(units=20.00, price_per_unit=15863.18),
            description="Sold 20 grams coin",
        )
        await asset_service.add_transaction(asset.id, sell_tx)

        recalced_sell = await asset_service.get_asset_by_id(asset.id)
        assert recalced_sell.invested_value == 841736.4
        assert recalced_sell.current_value == 280.00 * 15863.18

        # Verify transaction log
        txs = await asset_service.get_transactions_for_asset(asset.id)
        assert len(txs) == 3
        # First in list is latest due to DESC sort
        assert txs[0].transaction_type == AssetTransactionType.SELL

        # Delete transaction (roll back the sell)
        await asset_service.delete_transaction(txs[0].id)
        recalced_rollback = await asset_service.get_asset_by_id(asset.id)
        # Units should return to 300
        assert recalced_rollback.current_value == 300.00 * 15863.18

        # Clean up
        await asset_service.delete_asset(asset.id)

    async def test_revalue_unit_based_asset_calculations(self, asset_service):
        """Test revaluing a unit-based asset (like a Mutual Fund or ETF) without units in the transaction."""
        categories_map = await get_categories_map(asset_service)
        subcategory_map = await get_subcategory_map(asset_service)
        eq_cat_id = categories_map["EQUITY"]
        stock_sub_id = subcategory_map.get("STOCK")

        asset_in = AssetCreate(
            category_id=eq_cat_id,
            name="MUTUAL_FUND_XYZ",
            subcategory_id=stock_sub_id,
            initial_amount=100000.00,
            unit_details=AssetUnitDetails(
                units=100.00,
                price_per_unit=1000.00,
            ),
            notes="Equity mutual fund",
        )
        asset = await asset_service.create_asset(asset_in)

        assert asset.invested_value == 100000.00
        assert asset.current_value == 100000.00

        # Log a REVALUE transaction with new price per unit (NAV) = ₹1100, but no units specified.
        reval_tx = AssetTransactionCreate(
            transaction_type=AssetTransactionType.REVALUE,
            amount=110000.00,
            unit_details=AssetUnitDetails(price_per_unit=1100.00),
            description="End of month revaluation",
        )
        await asset_service.add_transaction(asset.id, reval_tx)

        # Retrieve and verify updated values
        updated = await asset_service.get_asset_by_id(asset.id)
        assert updated.invested_value == 100000.00
        assert updated.current_value == 110000.00
        assert updated.absolute_returns == 10000.00
        assert updated.percentage_returns == 10.00

        # Clean up
        await asset_service.delete_asset(asset.id)


class TestAssetTransactionValidation:
    """Tests for AssetTransactionCreate validation rules."""

    def test_amount_must_be_positive(self):
        """Reject transactions with amount <= 0."""
        with pytest.raises(Exception):
            AssetTransactionCreate(
                transaction_type=AssetTransactionType.BUY,
                amount=0.0,
            )

    def test_amount_negative_rejected(self):
        """Reject transactions with negative amount."""
        with pytest.raises(Exception):
            AssetTransactionCreate(
                transaction_type=AssetTransactionType.BUY,
                amount=-100.0,
            )

    def test_unit_details_units_must_be_positive(self):
        """Reject unit_details with zero units."""
        with pytest.raises(Exception):
            AssetUnitDetails(units=0.0, price_per_unit=100.0)

    def test_unit_details_price_per_unit_must_be_positive(self):
        """Reject unit_details with zero price_per_unit."""
        with pytest.raises(Exception):
            AssetUnitDetails(units=10.0, price_per_unit=0.0)

    def test_valid_transaction_no_units(self):
        """Value-based transactions (no unit_details) should be accepted."""
        tx = AssetTransactionCreate(
            transaction_type=AssetTransactionType.REVALUE,
            amount=55000.00,
        )
        assert tx.amount == 55000.00
        assert tx.unit_details is None

    def test_valid_transaction_with_units(self):
        """Unit-based transactions with full unit_details should be accepted."""
        tx = AssetTransactionCreate(
            transaction_type=AssetTransactionType.BUY,
            amount=250000.00,
            unit_details=AssetUnitDetails(units=50.0, price_per_unit=5000.0),
        )
        assert tx.unit_details.units == 50.0
        assert tx.unit_details.price_per_unit == 5000.0

    def test_revalue_unit_details_units_optional(self):
        """Verify AssetTransactionCreate accepts REVALUE with unit_details having only price_per_unit."""
        tx = AssetTransactionCreate(
            transaction_type=AssetTransactionType.REVALUE,
            amount=250000.00,
            unit_details=AssetUnitDetails(price_per_unit=5000.0),
        )
        assert tx.unit_details.units is None
        assert tx.unit_details.price_per_unit == 5000.0

    def test_buy_sell_unit_details_units_required(self):
        """Verify AssetTransactionCreate rejects BUY or SELL with unit_details if units is omitted."""
        with pytest.raises(Exception):
            AssetTransactionCreate(
                transaction_type=AssetTransactionType.BUY,
                amount=250000.00,
                unit_details=AssetUnitDetails(price_per_unit=5000.0),
            )
        with pytest.raises(Exception):
            AssetTransactionCreate(
                transaction_type=AssetTransactionType.SELL,
                amount=250000.00,
                unit_details=AssetUnitDetails(price_per_unit=5000.0),
            )


class TestAssetPatchSemantics:
    """Tests for PATCH update behaviour on AssetUpdate."""

    async def test_patch_preserves_unchanged_fields(self, asset_service):
        """Updating only name should not touch category_id, subcategory_id, notes."""
        categories_map = await get_categories_map(asset_service)
        subcategory_map = await get_subcategory_map(asset_service)
        debt_cat_id = categories_map["DEBT"]
        ppf_sub_id = subcategory_map.get("PPF")

        asset_in = AssetCreate(
            category_id=debt_cat_id,
            name="PPF Original",
            subcategory_id=ppf_sub_id,
            initial_amount=10000.00,
            notes="Original notes",
        )
        created = await asset_service.create_asset(asset_in)

        # PATCH: only update name
        patch = AssetUpdate(name="PPF Renamed")
        updated = await asset_service.update_asset(created.id, patch)

        assert updated.name == "PPF Renamed"
        assert updated.category_id == debt_cat_id
        assert updated.subcategory_id == ppf_sub_id
        assert updated.notes == "Original notes"

        await asset_service.delete_asset(created.id)


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
            initial_amount=10000.00,
        )
        a1 = await asset_service.create_asset(asset_in1)

        # Add Asset 2: Equity fund
        eq_cat_id = categories_map["EQUITY"]
        asset_in2 = AssetCreate(
            category_id=eq_cat_id,
            name="Mutual Fund",
            initial_amount=20000.00,
        )
        a2 = await asset_service.create_asset(asset_in2)

        # Revalue Mutual Fund to 25000
        reval_tx = AssetTransactionCreate(
            transaction_type=AssetTransactionType.REVALUE,
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


class TestAssetPostRevaluation:
    """Verify that flat-asset current valuations accurately combine revaluations with subsequent buy and sell transactions."""

    async def test_revalue_followed_by_buy_sell(self, asset_service):
        categories_map = await get_categories_map(asset_service)
        cb_cat_id = categories_map["CASH_BANK"]

        # Create a simple flat cash asset
        asset_in = AssetCreate(
            category_id=cb_cat_id,
            name="Emergency Fund",
            initial_amount=100000.00,
        )
        asset = await asset_service.create_asset(asset_in)

        assert asset.invested_value == 100000.00
        assert asset.current_value == 100000.00

        # 1. Revalue to 110,000
        reval_tx = AssetTransactionCreate(
            transaction_type=AssetTransactionType.REVALUE,
            amount=110000.00,
            transaction_date=datetime.now(UTC),
        )
        await asset_service.add_transaction(asset.id, reval_tx)

        updated1 = await asset_service.get_asset_by_id(asset.id)
        assert updated1.invested_value == 100000.00
        assert updated1.current_value == 110000.00

        # 2. Log subsequent BUY of 50,000
        buy_tx = AssetTransactionCreate(
            transaction_type=AssetTransactionType.BUY,
            amount=50000.00,
            transaction_date=datetime.now(UTC),
        )
        await asset_service.add_transaction(asset.id, buy_tx)

        updated2 = await asset_service.get_asset_by_id(asset.id)
        assert updated2.invested_value == 150000.00
        # Expected current value = 110k + 50k = 160k
        assert updated2.current_value == 160000.00

        # 3. Log subsequent SELL of 20,000
        sell_tx = AssetTransactionCreate(
            transaction_type=AssetTransactionType.SELL,
            amount=20000.00,
            transaction_date=datetime.now(UTC),
        )
        await asset_service.add_transaction(asset.id, sell_tx)

        updated3 = await asset_service.get_asset_by_id(asset.id)
        assert updated3.invested_value == 130000.00
        # Expected current value = 160k - 20k = 140k
        assert updated3.current_value == 140000.00

        await asset_service.delete_asset(asset.id)

