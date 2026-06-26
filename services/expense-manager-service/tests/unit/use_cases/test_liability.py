# ruff: noqa: PLR2004, E501
"""Unit tests for the wealth manager liabilities service use case."""

from datetime import UTC, datetime, timedelta

import pytest

from app.entities.models.liability import CompoundingFrequency, LiabilityTransactionType
from app.infrastructures.postgres_db.models.liability_category import LiabilityCategoryModel
from app.infrastructures.postgres_db.models.liability_subcategory import LiabilitySubcategoryModel
from app.use_cases.liability import LiabilityService
from app.use_cases.models.liability import (
    LiabilityCreate,
    LiabilityInterestDetails,
    LiabilityTransactionCreate,
    LiabilityUpdate,
)


@pytest.fixture
def liability_service(liability_repo):
    """Provide an instance of LiabilityService."""
    return LiabilityService(liability_repository=liability_repo)


async def get_categories_map(liability_service):
    """Retrieve a lookup map for seeded category codes to category IDs."""
    cats = await liability_service.get_all_categories()
    if not cats:
        # Seed categories if database is empty (standard for fresh test DBs)
        async with await liability_service.liability_repository._get_session() as session:
            session.add_all(
                [
                    LiabilityCategoryModel(
                        id="c1c2c3d4e5f64123a789bcde10111213",
                        name="Secured Loans",
                        code="SECURED_LOAN",
                        description="Loans backed by collateral like home, vehicle",
                    ),
                    LiabilityCategoryModel(
                        id="d1d2d3d4e5f64123a789bcde10111214",
                        name="Unsecured Loans",
                        code="UNSECURED_LOAN",
                        description="Loans with no collateral like personal, education loans",
                    ),
                    LiabilityCategoryModel(
                        id="e1e2e3d4e5f64123a789bcde10111215",
                        name="Revolving Credit",
                        code="REVOLVING_CREDIT",
                        description="Lines of credit like credit cards",
                    ),
                    LiabilityCategoryModel(
                        id="f1f2f3d4e5f64123a789bcde10111216",
                        name="Other Liabilities",
                        code="OTHER",
                        description="Family loans, hand loans, or general liabilities",
                    ),
                    LiabilitySubcategoryModel(
                        id="a1b2c3d4e5f647898b9cdaabcc123456",
                        category_id="c1c2c3d4e5f64123a789bcde10111213",
                        name="Home Loan",
                        code="HOME_LOAN",
                        description="Loan taken to purchase a house",
                        valuation_type="VALUE_BASED",
                        has_interest=True,
                        has_maturity=True,
                    ),
                    LiabilitySubcategoryModel(
                        id="a1b2c3d4e5f647898b9cdaabcc123458",
                        category_id="d1d2d3d4e5f64123a789bcde10111214",
                        name="Personal Loan",
                        code="PERSONAL_LOAN",
                        description="Unsecured personal loan from bank",
                        valuation_type="VALUE_BASED",
                        has_interest=True,
                        has_maturity=True,
                    ),
                ]
            )
            await session.commit()
        cats = await liability_service.get_all_categories()
    return {c.code: c.id for c in cats}


async def get_subcategory_map(liability_service):
    """Retrieve a lookup map for seeded subcategory codes to subcategory IDs."""
    cats = await liability_service.get_all_categories()
    sub_map = {}
    for cat in cats:
        for sub in cat.subcategories:
            sub_map[sub.code] = sub.id
    return sub_map


class TestLiabilityServiceCategories:
    """Tests for liability category retrievals."""

    async def test_get_all_categories(self, liability_service):
        """Verify standard categories are pre-seeded."""
        await get_categories_map(liability_service)
        cats = await liability_service.get_all_categories()
        assert len(cats) >= 4
        codes = [c.code for c in cats]
        assert "SECURED_LOAN" in codes
        assert "UNSECURED_LOAN" in codes
        assert "REVOLVING_CREDIT" in codes
        assert "OTHER" in codes


class TestLiabilityServiceCRUD:
    """Tests for Liability CRUD operations and recalculation workflows."""

    async def test_create_and_recalculate_personal_loan(self, liability_service):
        """Test creating a personal loan with repayments and revaluations."""
        categories_map = await get_categories_map(liability_service)
        subcategory_map = await get_subcategory_map(liability_service)
        unsecured_cat_id = categories_map["UNSECURED_LOAN"]
        personal_sub_id = subcategory_map.get("PERSONAL_LOAN")

        # 1. Create personal loan of 5,00,000 at 12.55%
        liability_in = LiabilityCreate(
            category_id=unsecured_cat_id,
            name="SBI Personal Loan",
            subcategory_id=personal_sub_id,
            initial_amount=500000.00,
            interest_details=LiabilityInterestDetails(
                interest_rate=12.55,
                compounding=CompoundingFrequency.MONTHLY,
                emi_amount=15000.00,
            ),
            notes="Initial borrowing",
        )
        liability = await liability_service.create_liability(liability_in)

        assert liability.name == "SBI Personal Loan"
        assert liability.category_code == "UNSECURED_LOAN"
        assert liability.interest_rate == 12.55
        assert liability.interest_compounding == CompoundingFrequency.MONTHLY
        assert liability.emi_amount == 15000.00
        assert liability.original_value == 500000.00
        assert liability.current_value == 500000.00
        assert liability.total_repaid == 0.00
        assert liability.accumulated_interest == 0.00
        assert liability.progress_pct == 0.00

        # 2. Add two repayments (part-payments/EMIs) of 1,00,000 each
        repay_tx1 = LiabilityTransactionCreate(
            transaction_type=LiabilityTransactionType.REPAY,
            amount=100000.00,
            transaction_date=datetime.now(UTC),
            description="First Part Payment",
        )
        await liability_service.add_transaction(liability.id, repay_tx1)

        repay_tx2 = LiabilityTransactionCreate(
            transaction_type=LiabilityTransactionType.REPAY,
            amount=100000.00,
            transaction_date=datetime.now(UTC),
            description="Second Part Payment",
        )
        await liability_service.add_transaction(liability.id, repay_tx2)

        # Retrieve and verify updated values
        updated = await liability_service.get_liability_by_id(liability.id)
        assert updated.original_value == 500000.00
        assert updated.total_repaid == 200000.00
        assert updated.current_value == 300000.00
        assert updated.progress_pct == 40.00
        assert updated.accumulated_interest == 0.00

        # 3. Bank updates outstanding balance to 3,10,000 (accrued interest added)
        reval_tx = LiabilityTransactionCreate(
            transaction_type=LiabilityTransactionType.REVALUE,
            amount=310000.00,
            transaction_date=datetime.now(UTC),
            description="June Statement Outstanding",
        )
        await liability_service.add_transaction(liability.id, reval_tx)

        # Retrieve and verify updated values (current_value becomes revalued amount)
        revalued = await liability_service.get_liability_by_id(liability.id)
        assert revalued.original_value == 500000.00
        assert revalued.total_repaid == 200000.00
        assert revalued.current_value == 310000.00
        assert revalued.progress_pct == 38.00  # (1 - 310k/500k)*100 = 38%
        assert revalued.accumulated_interest == 10000.00  # 310,000 - 500,000 + 200,000 = 10,000

        # 4. Clean up
        await liability_service.delete_liability(liability.id)
        with pytest.raises(ValueError):
            await liability_service.get_liability_by_id(liability.id)


class TestLiabilityPatchSemantics:
    """Tests for PATCH update behavior on LiabilityUpdate."""

    async def test_patch_preserves_unchanged_fields(self, liability_service):
        """Updating only name should not touch category_id, subcategory_id, notes."""
        categories_map = await get_categories_map(liability_service)
        subcategory_map = await get_subcategory_map(liability_service)
        secured_cat_id = categories_map["SECURED_LOAN"]
        home_sub_id = subcategory_map.get("HOME_LOAN")

        liability_in = LiabilityCreate(
            category_id=secured_cat_id,
            name="HDFC Home Loan Original",
            subcategory_id=home_sub_id,
            initial_amount=2500000.00,
            notes="Original notes",
        )
        created = await liability_service.create_liability(liability_in)

        # PATCH: only update name
        patch = LiabilityUpdate(name="HDFC Home Loan Renamed")
        updated = await liability_service.update_liability(created.id, patch)

        assert updated.name == "HDFC Home Loan Renamed"
        assert updated.category_id == secured_cat_id
        assert updated.subcategory_id == home_sub_id
        assert updated.notes == "Original notes"

        await liability_service.delete_liability(created.id)


class TestLiabilityServiceSummary:
    """Tests for portfolio summary calculations for liabilities."""

    async def test_get_liability_summary(self, liability_service):
        """Create multiple liabilities and verify summary aggregations."""
        categories_map = await get_categories_map(liability_service)

        # Clean existing liabilities
        existing = await liability_service.list_liabilities()
        for liab in existing:
            await liability_service.delete_liability(liab.id)

        # Add Secured Loan
        sec_cat_id = categories_map["SECURED_LOAN"]
        l1_in = LiabilityCreate(
            category_id=sec_cat_id,
            name="Car Loan",
            initial_amount=800000.00,
        )
        l1 = await liability_service.create_liability(l1_in)

        # Add Unsecured Loan
        unsec_cat_id = categories_map["UNSECURED_LOAN"]
        l2_in = LiabilityCreate(
            category_id=unsec_cat_id,
            name="Personal Loan",
            initial_amount=200000.00,
        )
        l2 = await liability_service.create_liability(l2_in)

        # Repay 50,000 on Personal Loan
        repay_tx = LiabilityTransactionCreate(
            transaction_type=LiabilityTransactionType.REPAY,
            amount=50000.00,
            transaction_date=datetime.now(UTC),
        )
        await liability_service.add_transaction(l2.id, repay_tx)

        # Get summary
        summary = await liability_service.get_liability_summary()

        # Total original: 8,00,000 + 2,00,000 = 10,00,000
        assert summary.total_original == 1000000.00
        # Total outstanding: 8,00,000 + (2,00,000 - 50,000) = 9,50,000
        assert summary.total_outstanding == 950000.00
        # Total repaid: 50,000
        assert summary.total_repaid == 50000.00
        assert summary.accumulated_interest == 0.00

        # Clean up
        await liability_service.delete_liability(l1.id)
        await liability_service.delete_liability(l2.id)


class TestLiabilityProjections:
    """Tests for liability payoff projection curves and intelligence metrics."""

    async def test_projections_generation_and_savings(self, liability_service):
        """Verify that projections calculate ideal/actual payoff curves and savings metrics correctly."""
        categories_map = await get_categories_map(liability_service)
        subcategory_map = await get_subcategory_map(liability_service)
        unsecured_cat_id = categories_map["UNSECURED_LOAN"]
        personal_sub_id = subcategory_map.get("PERSONAL_LOAN")

        # Create a liability with ₹5,00,000 borrowed at 12.00% annual interest with ₹15,000 EMI
        # Disbursal date set to 6 months ago to verify historical ledger actual curve mapping
        disbursal_date = datetime.now(UTC) - timedelta(days=180)

        liability_in = LiabilityCreate(
            category_id=unsecured_cat_id,
            name="Personal Loan Projections Test",
            subcategory_id=personal_sub_id,
            initial_amount=500000.00,
            initial_date=disbursal_date,
            interest_details=LiabilityInterestDetails(
                interest_rate=12.00,
                compounding=CompoundingFrequency.MONTHLY,
                emi_amount=15000.00,
            ),
        )
        liability = await liability_service.create_liability(liability_in)

        # Before any repayments, fetch projections
        proj_init = await liability_service.get_liability_projections(liability.id)
        assert proj_init.metrics.ideal_tenure_months > 0
        assert proj_init.metrics.remaining_tenure_months > 0
        # Since disbursal was in the past and no payments were logged, scheduled payments are assumed to have occurred.
        # So tenure saved starts at 0.
        assert proj_init.metrics.tenure_saved_months == 0
        assert len(proj_init.projection_points) > 0

        # Add repayments (prepayments) of ₹1,00,000 today to simulate early payoff
        repay_tx = LiabilityTransactionCreate(
            transaction_type=LiabilityTransactionType.REPAY,
            amount=100000.00,
            transaction_date=datetime.now(UTC),
            description="Large Prepayment",
        )
        await liability_service.add_transaction(liability.id, repay_tx)

        # Retrieve projections after prepayment
        proj_after = await liability_service.get_liability_projections(liability.id)

        # Outstanding is smaller, so remaining projected tenure must be shorter than ideal remaining tenure
        assert proj_after.metrics.remaining_tenure_months < proj_init.metrics.remaining_tenure_months
        assert proj_after.metrics.tenure_saved_months > 0
        assert proj_after.metrics.interest_saved > 0
        assert proj_after.metrics.total_interest_projected < proj_after.metrics.total_interest_ideal

        # Clean up
        await liability_service.delete_liability(liability.id)

    async def test_projections_missing_config_raises(self, liability_service):
        """Verify get_liability_projections raises ValueError if interest parameters are missing."""
        categories_map = await get_categories_map(liability_service)
        sec_cat_id = categories_map["SECURED_LOAN"]

        # Create a liability without interestDetails
        liability_in = LiabilityCreate(
            category_id=sec_cat_id,
            name="No Interest Loan",
            initial_amount=100000.00,
        )
        liability = await liability_service.create_liability(liability_in)

        with pytest.raises(ValueError) as exc:
            await liability_service.get_liability_projections(liability.id)
        assert "missing interest rate" in str(exc.value)

        # Clean up
        await liability_service.delete_liability(liability.id)


class TestLiabilitySimulationAndCompounding:
    """Unit tests for compounding frequency and irregular repayments simulation."""

    async def test_interest_bearing_loan_no_emi(self, liability_service):
        """Verify interest-bearing loan with emi_amount=None accrues interest without auto-EMI."""
        categories_map = await get_categories_map(liability_service)
        subcategory_map = await get_subcategory_map(liability_service)
        unsecured_cat_id = categories_map["UNSECURED_LOAN"]
        personal_sub_id = subcategory_map.get("PERSONAL_LOAN")

        disbursal_date = datetime.now(UTC) - timedelta(days=90)  # ~3 months ago

        # 1. Create a loan of 100,000 at 12% interest, no EMI
        liability_in = LiabilityCreate(
            category_id=unsecured_cat_id,
            name="No-EMI Personal Loan",
            subcategory_id=personal_sub_id,
            initial_amount=100000.00,
            initial_date=disbursal_date,
            interest_details=LiabilityInterestDetails(
                interest_rate=12.00,
                compounding=CompoundingFrequency.MONTHLY,
                emi_amount=None,  # No scheduled EMI
            ),
        )
        liability = await liability_service.create_liability(liability_in)

        # Since there is no EMI, outstanding balance should grow month-by-month with interest.
        # ~3 months elapsed. At 1% per month, balance should grow from 100,000 to ~103,030.10
        updated = await liability_service.get_liability_by_id(liability.id)
        assert updated.current_value > 100000.00
        assert updated.accumulated_interest > 0.00
        assert updated.total_repaid == 0.00
        assert updated.remaining_tenure_months is not None  # Amortizes via fallback EMI (100k/60 = 1666.67 > 1000.00 monthly interest)

        # Now get projections. Projections should be generated successfully.
        projections = await liability_service.get_liability_projections(liability.id)
        assert len(projections.projection_points) > 0

        # Cleanup
        await liability_service.delete_liability(liability.id)

        # 2. Test negative amortization where interest > fallback EMI
        liability_in_high_int = LiabilityCreate(
            category_id=unsecured_cat_id,
            name="Negative Amortization Personal Loan",
            subcategory_id=personal_sub_id,
            initial_amount=100000.00,
            initial_date=disbursal_date,
            interest_details=LiabilityInterestDetails(
                interest_rate=24.00,  # 2% monthly = 2000 interest. Fallback EMI is 1666.67
                compounding=CompoundingFrequency.MONTHLY,
                emi_amount=None,
            ),
        )
        liability_high = await liability_service.create_liability(liability_in_high_int)
        updated_high = await liability_service.get_liability_by_id(liability_high.id)
        assert updated_high.remaining_tenure_months is None  # Growing balance (interest > EMI), so no end date

        # Cleanup
        await liability_service.delete_liability(liability_high.id)

    async def test_compounding_frequencies(self, liability_service):
        """Verify interest calculations reflect monthly vs yearly compounding."""
        categories_map = await get_categories_map(liability_service)
        subcategory_map = await get_subcategory_map(liability_service)
        unsecured_cat_id = categories_map["UNSECURED_LOAN"]
        personal_sub_id = subcategory_map.get("PERSONAL_LOAN")

        disbursal_date = datetime.now(UTC) - timedelta(days=365)  # 1 year ago

        # Loan A: Monthly Compounding
        loan_a_in = LiabilityCreate(
            category_id=unsecured_cat_id,
            name="Monthly Compounding Loan",
            subcategory_id=personal_sub_id,
            initial_amount=100000.00,
            initial_date=disbursal_date,
            interest_details=LiabilityInterestDetails(
                interest_rate=12.00,
                compounding=CompoundingFrequency.MONTHLY,
                emi_amount=None,
            ),
        )
        loan_a = await liability_service.create_liability(loan_a_in)

        # Loan B: Yearly Compounding (compounds only at month 12)
        loan_b_in = LiabilityCreate(
            category_id=unsecured_cat_id,
            name="Yearly Compounding Loan",
            subcategory_id=personal_sub_id,
            initial_amount=100000.00,
            initial_date=disbursal_date,
            interest_details=LiabilityInterestDetails(
                interest_rate=12.00,
                compounding=CompoundingFrequency.YEARLY,
                emi_amount=None,
            ),
        )
        loan_b = await liability_service.create_liability(loan_b_in)

        val_a = await liability_service.get_liability_by_id(loan_a.id)
        val_b = await liability_service.get_liability_by_id(loan_b.id)

        # Monthly compounding compounding principal grows faster.
        assert val_a.current_value >= val_b.current_value
        assert val_a.accumulated_interest >= val_b.accumulated_interest

        # Cleanup
        await liability_service.delete_liability(loan_a.id)
        await liability_service.delete_liability(loan_b.id)
