# ruff: noqa: PLR2004, E501
"""Unit tests for the wealth manager portfolio/wealth service use case."""

from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import delete, select

from app.entities.models.asset import AssetTransactionType, CompoundingFrequency
from app.infrastructures.postgres_db.models.asset import AssetModel
from app.infrastructures.postgres_db.models.asset_category import AssetCategoryModel
from app.infrastructures.postgres_db.models.asset_subcategory import AssetSubcategoryModel
from app.infrastructures.postgres_db.models.asset_transaction import AssetTransactionModel
from app.infrastructures.postgres_db.models.liability import LiabilityModel
from app.infrastructures.postgres_db.models.liability_category import LiabilityCategoryModel
from app.infrastructures.postgres_db.models.liability_subcategory import LiabilitySubcategoryModel
from app.infrastructures.postgres_db.models.liability_transaction import LiabilityTransactionModel
from app.use_cases.asset import AssetService
from app.use_cases.liability import LiabilityService
from app.use_cases.models.asset import AssetCreate, AssetTransactionCreate
from app.use_cases.models.liability import LiabilityCreate, LiabilityInterestDetails
from app.use_cases.wealth import WealthService


@pytest.fixture
def asset_service(asset_repo):
    """Provide an instance of AssetService."""
    return AssetService(asset_repository=asset_repo)


@pytest.fixture
def liability_service(liability_repo):
    """Provide an instance of LiabilityService."""
    return LiabilityService(liability_repository=liability_repo)


@pytest.fixture
def wealth_service(asset_repo, liability_repo):
    """Provide an instance of WealthService."""
    return WealthService(asset_repository=asset_repo, liability_repository=liability_repo)


async def seed_categories(wealth_service):
    """Seed asset and liability categories/subcategories if they do not exist."""
    asset_repo = wealth_service.asset_repository
    liability_repo = wealth_service.liability_repository

    async with await asset_repo._get_session() as session:
        # Seed Asset Categories
        cats_to_seed = {
            "EQUITY": ("Equity", "Stocks, Mutual Funds, ETFs"),
            "DEBT": ("Debt", "Fixed Deposits, PPF, Bonds, EPF"),
        }
        cats_map = {}
        for code, (name, desc) in cats_to_seed.items():
            stmt = select(AssetCategoryModel).where(AssetCategoryModel.code == code)
            res = await session.execute(stmt)
            cat = res.scalar_one_or_none()
            if not cat:
                cat = AssetCategoryModel(name=name, code=code, description=desc)
                session.add(cat)
                await session.flush()
            cats_map[code] = cat.id

        # Seed Asset Subcategories
        subs_to_seed = {
            "STOCK": ("Stock", cats_map["EQUITY"], "UNIT_BASED", False, False),
            "FD": ("Fixed Deposit", cats_map["DEBT"], "VALUE_BASED", True, True),
        }
        for code, (name, cat_id, val_type, has_int, has_mat) in subs_to_seed.items():
            stmt = select(AssetSubcategoryModel).where(AssetSubcategoryModel.code == code)
            res = await session.execute(stmt)
            sub = res.scalar_one_or_none()
            if not sub:
                sub = AssetSubcategoryModel(
                    category_id=cat_id,
                    name=name,
                    code=code,
                    valuation_type=val_type,
                    has_interest=has_int,
                    has_maturity=has_mat,
                )
                session.add(sub)
        await session.commit()

    async with await liability_repo._get_session() as session:
        # Seed Liability Categories
        liab_cats_to_seed = {
            "SECURED_LOAN": ("Secured Loans", "Loans backed by collateral like home, vehicle"),
            "UNSECURED_LOAN": ("Unsecured Loans", "Loans with no collateral"),
        }
        liab_cats_map = {}
        for code, (name, desc) in liab_cats_to_seed.items():
            stmt = select(LiabilityCategoryModel).where(LiabilityCategoryModel.code == code)
            res = await session.execute(stmt)
            cat = res.scalar_one_or_none()
            if not cat:
                cat = LiabilityCategoryModel(name=name, code=code, description=desc)
                session.add(cat)
                await session.flush()
            liab_cats_map[code] = cat.id

        # Seed Liability Subcategories
        liab_subs_to_seed = {
            "HOME_LOAN": ("Home Loan", liab_cats_map["SECURED_LOAN"], "VALUE_BASED", True, True),
        }
        for code, (name, cat_id, val_type, has_int, has_mat) in liab_subs_to_seed.items():
            stmt = select(LiabilitySubcategoryModel).where(LiabilitySubcategoryModel.code == code)
            res = await session.execute(stmt)
            sub = res.scalar_one_or_none()
            if not sub:
                sub = LiabilitySubcategoryModel(
                    category_id=cat_id,
                    name=name,
                    code=code,
                    valuation_type=val_type,
                    has_interest=has_int,
                    has_maturity=has_mat,
                )
                session.add(sub)
        await session.commit()


async def get_asset_maps(wealth_service):
    """Retrieve maps of category and subcategory codes to IDs."""
    asset_repo = wealth_service.asset_repository
    async with await asset_repo._get_session() as session:
        cat_res = await session.execute(select(AssetCategoryModel))
        cats = cat_res.scalars().all()
        cats_map = {c.code: c.id for c in cats}

        sub_res = await session.execute(select(AssetSubcategoryModel))
        subs = sub_res.scalars().all()
        subs_map = {s.code: s.id for s in subs}
        return cats_map, subs_map


async def get_liability_maps(wealth_service):
    """Retrieve maps of liability category and subcategory codes to IDs."""
    liability_repo = wealth_service.liability_repository
    async with await liability_repo._get_session() as session:
        cat_res = await session.execute(select(LiabilityCategoryModel))
        cats = cat_res.scalars().all()
        cats_map = {c.code: c.id for c in cats}

        sub_res = await session.execute(select(LiabilitySubcategoryModel))
        subs = sub_res.scalars().all()
        subs_map = {s.code: s.id for s in subs}
        return cats_map, subs_map


async def cleanup_db(asset_repo, liability_repo):
    """Remove created assets and liabilities records."""
    async with await asset_repo._get_session() as session:
        await session.execute(delete(AssetTransactionModel))
        await session.execute(delete(AssetModel))
        await session.commit()

    async with await liability_repo._get_session() as session:
        await session.execute(delete(LiabilityTransactionModel))
        await session.execute(delete(LiabilityModel))
        await session.commit()


@pytest.mark.asyncio
async def test_wealth_summary_empty(wealth_service, asset_repo, liability_repo):
    """Test wealth summary with an empty database."""
    await cleanup_db(asset_repo, liability_repo)
    await seed_categories(wealth_service)

    summary = await wealth_service.get_wealth_summary()
    assert summary.total_assets == 0.0
    assert summary.total_liabilities == 0.0
    assert summary.net_worth == 0.0


@pytest.mark.asyncio
async def test_wealth_summary_with_data(wealth_service, asset_service, liability_service, asset_repo, liability_repo):
    """Test wealth summary calculation with active assets and liabilities."""
    await cleanup_db(asset_repo, liability_repo)
    await seed_categories(wealth_service)

    asset_cats, asset_subs = await get_asset_maps(wealth_service)
    liab_cats, liab_subs = await get_liability_maps(wealth_service)

    # 1. Create a cash asset (flat balance)
    await asset_service.create_asset(
        AssetCreate(
            category_id=asset_cats["DEBT"],
            name="Emergency Savings Account",
            subcategory_id=asset_subs["FD"],
            initial_amount=150000.0,
        )
    )

    # 2. Create an interest-bearing liability (Secured Loan)
    today = datetime.now(UTC)
    await liability_service.create_liability(
        LiabilityCreate(
            category_id=liab_cats["SECURED_LOAN"],
            name="Home Mortgage",
            subcategory_id=liab_subs["HOME_LOAN"],
            initial_amount=100000.0,
            initial_date=today - timedelta(days=60),
            interest_details=LiabilityInterestDetails(
                interest_rate=12.0,
                compounding=CompoundingFrequency.MONTHLY,
                emi_amount=10000.0,
                emi_start_date=today - timedelta(days=30),
                maturity_date=today + timedelta(days=365),
            ),
        )
    )

    # Calculate summary
    summary = await wealth_service.get_wealth_summary()
    assert summary.total_assets == 150000.0
    # Liabilities outstanding balance should decrease due to EMI/repayment simulation
    assert summary.total_liabilities < 100000.0
    assert summary.net_worth == round(summary.total_assets - summary.total_liabilities, 2)


@pytest.mark.asyncio
async def test_wealth_allocation(wealth_service, asset_service, liability_service, asset_repo, liability_repo):
    """Test category and subcategory allocation calculations."""
    await cleanup_db(asset_repo, liability_repo)
    await seed_categories(wealth_service)

    asset_cats, asset_subs = await get_asset_maps(wealth_service)
    liab_cats, liab_subs = await get_liability_maps(wealth_service)

    # Create an asset in DEBT category
    await asset_service.create_asset(
        AssetCreate(
            category_id=asset_cats["DEBT"],
            name="Emergency Cash",
            subcategory_id=asset_subs["FD"],
            initial_amount=100000.0,
        )
    )

    # Create an asset in EQUITY category
    await asset_service.create_asset(
        AssetCreate(
            category_id=asset_cats["EQUITY"],
            name="Index Fund",
            subcategory_id=asset_subs["STOCK"],
            initial_amount=300000.0,
        )
    )

    # Create a liability
    await liability_service.create_liability(
        LiabilityCreate(
            category_id=liab_cats["SECURED_LOAN"],
            name="Car Mortgage",
            subcategory_id=liab_subs["HOME_LOAN"],
            initial_amount=200000.0,
        )
    )

    allocation = await wealth_service.get_portfolio_allocation()

    # Check assets allocations
    assert len(allocation.assets) > 0
    debt_alloc = next(c for c in allocation.assets if c.category_code == "DEBT")
    equity_alloc = next(c for c in allocation.assets if c.category_code == "EQUITY")
    assert debt_alloc.total_value == 100000.0
    assert equity_alloc.total_value == 300000.0
    assert debt_alloc.percentage == 25.0
    assert equity_alloc.percentage == 75.0

    # Check liabilities allocations
    assert len(allocation.liabilities) > 0
    secured_alloc = next(c for c in allocation.liabilities if c.category_code == "SECURED_LOAN")
    assert secured_alloc.total_value == 200000.0
    assert secured_alloc.percentage == 100.0

    # Check calculated totals and ratios
    assert allocation.total_assets_value == 400000.0
    assert allocation.total_liabilities_value == 200000.0
    assert allocation.debt_to_asset_ratio == 50.0
    assert allocation.liquidity_ratio == 75.0
    assert allocation.equity_financed_pct == 50.0
    assert allocation.liabilities_financed_pct == 50.0
    assert allocation.leverage_status_label == "Moderate Risk (Watch)"
    assert allocation.leverage_status_type == "WARNING"
    assert allocation.liquidity_status_label == "Healthy Liquidity"
    assert allocation.liquidity_status_type == "SUCCESS"



@pytest.mark.asyncio
async def test_wealth_historical_net_worth(wealth_service, asset_service, liability_service, asset_repo, liability_repo):
    """Test historical timeline net worth points calculation."""
    await cleanup_db(asset_repo, liability_repo)
    await seed_categories(wealth_service)

    asset_cats, asset_subs = await get_asset_maps(wealth_service)

    today = datetime.now(UTC)

    # 1. Create an asset starting 2 months ago
    asset = await asset_service.create_asset(
        AssetCreate(
            category_id=asset_cats["DEBT"],
            name="Historical Bank",
            subcategory_id=asset_subs["FD"],
            initial_amount=50000.0,
        )
    )
    # Edit initial transaction date in database directly
    async with await asset_repo._get_session() as session:
        stmt = select(AssetTransactionModel).where(AssetTransactionModel.asset_id == asset.id)
        res = await session.execute(stmt)
        tx = res.scalar_one()
        tx.transaction_date = today - timedelta(days=60)
        await session.commit()

    # 2. Add an asset transaction in the current month
    await asset_service.add_transaction(
        asset.id,
        AssetTransactionCreate(
            transaction_type=AssetTransactionType.BUY,
            amount=25000.0,
            transaction_date=today,
        )
    )

    history = await wealth_service.get_historical_net_worth(months=3)
    assert len(history) == 3
    # Check that values grow historically
    # Point 0 (2 months ago): should have asset value ~ 50000
    # Point 2 (current month): should have asset value ~ 75000
    assert history[0].total_assets == 50000.0
    assert history[2].total_assets == 75000.0
    assert history[2].net_worth == 75000.0
