# ruff: noqa: PLR0912, PLR0915, PLR2004
"""Use cases for Liabilities."""

import calendar
import uuid
from datetime import UTC, datetime

from app.entities.models.liability import (
    Liability,
    LiabilityCategory,
    LiabilityFilter,
    LiabilitySort,
    LiabilityTransaction,
    LiabilityTransactionType,
)
from app.entities.repositories.liability import LiabilityRepositoryInterface
from app.use_cases.models.liability import (
    LiabilityCategorySummary,
    LiabilityCreate,
    LiabilityProjectionMetrics,
    LiabilityProjectionPoint,
    LiabilityProjections,
    LiabilitySummary,
    LiabilityTransactionCreate,
    LiabilityUpdate,
    LiabilityWithCalc,
)


def add_months(sourcedate: datetime, months: int) -> datetime:
    """Add a number of months to a datetime, handling end-of-month rollover."""
    month = sourcedate.month - 1 + months
    year = sourcedate.year + month // 12
    month = month % 12 + 1
    day = min(sourcedate.day, calendar.monthrange(year, month)[1])
    return datetime(
        year=year,
        month=month,
        day=day,
        hour=sourcedate.hour,
        minute=sourcedate.minute,
        second=sourcedate.second,
        tzinfo=sourcedate.tzinfo,
    )


def _simulate_amortization(
    original_value: float,
    interest_rate: float,
    emi_amount: float,
    transactions: list[LiabilityTransaction],
    up_to_date: datetime,
) -> dict[str, tuple[float, float, float]]:
    """Core amortization simulation engine (single source of truth).

    Simulates month-by-month amortization from the first BORROW date up to ``up_to_date``,
    honouring scheduled EMI, manual REPAY prepayments, additional BORROWs, and REVALUE
    bank statement overrides.

    REVALUE semantics: A REVALUE transaction represents the bank's official outstanding
    balance for that month. It implicitly absorbs the interest accrued, the scheduled EMI
    applied, and any extra repayments made. The difference between the REVALUE amount and
    the expected balance (after applying interest, EMI, borrows, repays) is treated as an
    interest adjustment (positive = extra interest charged, negative = interest relief/waiver).

    Args:
        original_value: Sum of all BORROW transaction amounts.
        interest_rate: Annual interest rate as a percentage (e.g. 11.95 for 11.95%).
        emi_amount: Scheduled monthly EMI in INR.
        transactions: Full chronological ledger of transactions.
        up_to_date: Simulate up to (and including) this date's month.

    Returns:
        Dict of ``"YYYY-MM"`` → ``(balance, cumulative_interest, cumulative_repaid)`` at
        the *closing* of each simulated month. Month 0 (disbursal month) is also included.
    """
    monthly_rate = (interest_rate / 100.0) / 12.0
    emi = emi_amount

    sorted_txs = sorted(transactions, key=lambda t: (t.transaction_date, t.created_at or datetime.min))
    borrow_txs = [t for t in sorted_txs if t.transaction_type == LiabilityTransactionType.BORROW]
    if not borrow_txs:
        return {}

    first_borrow = borrow_txs[0]
    start_date = first_borrow.transaction_date
    if start_date.tzinfo is None:
        start_date = start_date.replace(tzinfo=UTC)
    if up_to_date.tzinfo is None:
        up_to_date = up_to_date.replace(tzinfo=UTC)

    # Group all transactions by YYYY-MM
    txs_by_month: dict[str, list[LiabilityTransaction]] = {}
    for t in sorted_txs:
        tx_date = t.transaction_date
        if tx_date.tzinfo is None:
            tx_date = tx_date.replace(tzinfo=UTC)
        key = tx_date.strftime("%Y-%m")
        txs_by_month.setdefault(key, []).append(t)

    snapshots: dict[str, tuple[float, float, float]] = {}

    # Month 0: Disbursal month
    p = original_value  # opening balance after all borrows
    accum_interest = 0.0
    accum_repaid = 0.0

    m0_str = start_date.strftime("%Y-%m")
    m0_other = [t for t in txs_by_month.get(m0_str, []) if t.id != first_borrow.id]

    # Extra borrows in disbursal month
    extra_borrows_0 = sum(t.amount for t in m0_other if t.transaction_type == LiabilityTransactionType.BORROW)
    repays_0 = sum(t.amount for t in m0_other if t.transaction_type == LiabilityTransactionType.REPAY)
    revals_0 = [t for t in m0_other if t.transaction_type == LiabilityTransactionType.REVALUE]

    p += extra_borrows_0
    p -= repays_0
    accum_repaid += repays_0

    if revals_0:
        # REVALUE in disbursal month: snap to official balance, attribute difference as interest
        reval_amount = revals_0[-1].amount
        interest_adj = reval_amount - p
        accum_interest += interest_adj
        p = reval_amount

    p = max(0.0, p)
    snapshots[m0_str] = (round(p, 2), round(accum_interest, 2), round(accum_repaid, 2))

    # Months 1 … N (up_to_date)
    elapsed = max(0, (up_to_date.year - start_date.year) * 12 + (up_to_date.month - start_date.month))

    for m in range(1, elapsed + 1):
        date_m = add_months(start_date, m)
        m_str = date_m.strftime("%Y-%m")

        if p <= 0.0:
            # Loan already paid off — record zero balance going forward
            snapshots[m_str] = (0.0, round(accum_interest, 2), round(accum_repaid, 2))
            continue

        # Step 1 — Gather any manual transactions in this month
        month_txs = txs_by_month.get(m_str, [])
        borrows_m = sum(t.amount for t in month_txs if t.transaction_type == LiabilityTransactionType.BORROW)
        repays_m = sum(t.amount for t in month_txs if t.transaction_type == LiabilityTransactionType.REPAY)
        revals_m = [t for t in month_txs if t.transaction_type == LiabilityTransactionType.REVALUE]

        if revals_m:
            # REVALUE month: the bank's official closing balance is the authoritative truth.
            # It already reflects all interest accrued, EMI payments, and any extra repayments
            # the bank processed. We do NOT apply auto-EMI separately — that would double-count.
            #
            # Interest attribution for this month:
            #   The balance moved from p_prev → reval_amount.
            #   The "effective interest" is the difference: reval - (p_prev + borrows).
            #   This is naturally ≥ 0 for a normal interest-bearing month, but can be slightly
            #   negative if the bank applied relief/waivers — we floor at 0 for display.
            reval_amount = revals_m[-1].amount
            implied_interest = reval_amount - (p + borrows_m)
            accum_interest += max(0.0, implied_interest)
            # Manual REPAY entries in same month are additional repayments the user tracked;
            # they are credited separately (the REVALUE already incorporated them into the balance).
            accum_repaid += repays_m
            p = max(0.0, reval_amount)
        else:
            # Normal month: accrue interest, apply scheduled EMI + any manual repayments
            interest_m = p * monthly_rate
            auto_emi = min(emi, p + interest_m)
            total_repayment = auto_emi + repays_m
            p = max(0.0, p + interest_m + borrows_m - total_repayment)
            accum_interest += interest_m
            accum_repaid += total_repayment

        snapshots[m_str] = (round(p, 2), round(accum_interest, 2), round(accum_repaid, 2))

    return snapshots


def calculate_current_outstanding(
    original_value: float,
    interest_rate: float | None,
    emi_amount: float | None,
    transactions: list[LiabilityTransaction],
    today: datetime | None = None,
) -> dict[str, float]:
    """Calculate the dynamic outstanding balance, total repaid, and accumulated interest as of today.

    Delegates to ``_simulate_amortization`` for interest-bearing EMI loans.
    Provides a simplified path for non-EMI or interest-free loans.
    """
    if today is None:
        today = datetime.now(UTC)

    if not transactions:
        return {"current_value": 0.0, "total_repaid": 0.0, "accumulated_interest": 0.0}

    sorted_txs = sorted(transactions, key=lambda t: (t.transaction_date, t.created_at or datetime.min))
    borrow_txs = [t for t in sorted_txs if t.transaction_type == LiabilityTransactionType.BORROW]
    if not borrow_txs:
        return {"current_value": 0.0, "total_repaid": 0.0, "accumulated_interest": 0.0}

    total_borrowed = sum(t.amount for t in borrow_txs)

    # Non-EMI / interest-free loans
    if not interest_rate or not emi_amount:
        repayments = sum(t.amount for t in sorted_txs if t.transaction_type == LiabilityTransactionType.REPAY)
        revalue_txs = [t for t in sorted_txs if t.transaction_type == LiabilityTransactionType.REVALUE]
        if revalue_txs:
            latest_revalue = revalue_txs[-1]
            revalue_index = sorted_txs.index(latest_revalue)
            current_val = latest_revalue.amount
            for t in sorted_txs[revalue_index + 1 :]:
                if t.transaction_type == LiabilityTransactionType.BORROW:
                    current_val += t.amount
                elif t.transaction_type == LiabilityTransactionType.REPAY:
                    current_val -= t.amount
            current_val = max(0.0, current_val)
            acc_interest = max(0.0, current_val - total_borrowed + repayments)
            return {
                "current_value": round(current_val, 2),
                "total_repaid": round(repayments, 2),
                "accumulated_interest": round(acc_interest, 2),
            }
        else:
            current_val = max(0.0, total_borrowed - repayments)
            return {
                "current_value": round(current_val, 2),
                "total_repaid": round(repayments, 2),
                "accumulated_interest": 0.0,
            }

    # EMI / interest-bearing loans — delegate to simulation engine
    snapshots = _simulate_amortization(
        original_value=total_borrowed,
        interest_rate=interest_rate,
        emi_amount=emi_amount,
        transactions=transactions,
        up_to_date=today,
    )

    if not snapshots:
        return {"current_value": 0.0, "total_repaid": 0.0, "accumulated_interest": 0.0}

    # The last snapshot key (sorted by date) is "today"
    last_key = sorted(snapshots.keys())[-1]
    balance, cum_interest, cum_repaid = snapshots[last_key]

    return {
        "current_value": round(balance, 2),
        "total_repaid": round(cum_repaid, 2),
        "accumulated_interest": round(max(0.0, cum_interest), 2),
    }


class LiabilityService:
    """Service handling liability orchestration and financial calculations."""

    def __init__(self, liability_repository: LiabilityRepositoryInterface):
        """Initialize the LiabilityService with repository."""
        self.liability_repository = liability_repository

    async def get_all_categories(self) -> list[LiabilityCategory]:
        """Retrieve all liability categories."""
        return await self.liability_repository.get_all_categories()

    async def _to_calc_model(self, liability: Liability) -> LiabilityWithCalc:
        """Add calculated fields and category information to liability model."""
        category = await self.liability_repository.get_category_by_id(liability.category_id)
        category_name = category.name if category else "Unknown"
        category_code = category.code if category else "UNKNOWN"

        transactions = await self.liability_repository.get_transactions_for_liability(liability.id)

        # Dynamic outstanding calculations as of today
        calcs = calculate_current_outstanding(
            original_value=liability.original_value,
            interest_rate=liability.interest_rate,
            emi_amount=liability.emi_amount,
            transactions=transactions,
            today=datetime.now(UTC),
        )
        dynamic_current_value = calcs["current_value"]
        total_repaid = calcs["total_repaid"]
        accumulated_interest = calcs["accumulated_interest"]

        progress_pct = 0.0
        if liability.original_value > 0:
            # Clamped between 0 and 100
            progress_pct = max(0.0, min(100.0, (1 - dynamic_current_value / liability.original_value) * 100))

        return LiabilityWithCalc(
            id=liability.id,
            category_id=liability.category_id,
            category_name=category_name,
            category_code=category_code,
            name=liability.name,
            subcategory_id=liability.subcategory_id,
            original_value=liability.original_value,
            current_value=dynamic_current_value,
            interest_rate=liability.interest_rate,
            interest_compounding=liability.interest_compounding,
            emi_amount=liability.emi_amount,
            maturity_date=liability.maturity_date,
            notes=liability.notes,
            total_repaid=round(total_repaid, 2),
            accumulated_interest=round(accumulated_interest, 2),
            progress_pct=round(progress_pct, 2),
            created_at=liability.created_at,
            updated_at=liability.updated_at,
        )

    async def create_liability(self, liability_create: LiabilityCreate) -> LiabilityWithCalc:
        """Create a new liability and log its initial BORROW transaction."""
        liability_id = uuid.uuid4().hex

        interest_rate = liability_create.interest_details.interest_rate if liability_create.interest_details else None
        interest_compounding = (
            liability_create.interest_details.compounding if liability_create.interest_details else None
        )
        emi_amount = liability_create.interest_details.emi_amount if liability_create.interest_details else None
        maturity_date = liability_create.interest_details.maturity_date if liability_create.interest_details else None

        liability = Liability(
            id=liability_id,
            category_id=liability_create.category_id,
            name=liability_create.name,
            subcategory_id=liability_create.subcategory_id,
            original_value=0.0,
            current_value=0.0,
            interest_rate=interest_rate,
            interest_compounding=interest_compounding,
            emi_amount=emi_amount,
            maturity_date=maturity_date,
            notes=liability_create.notes,
        )
        created_liability = await self.liability_repository.add_liability(liability)

        # Log the initial BORROW transaction representing disbursal
        tx = LiabilityTransaction(
            id=uuid.uuid4().hex,
            liability_id=liability_id,
            transaction_type=LiabilityTransactionType.BORROW,
            amount=liability_create.initial_amount,
            transaction_date=liability_create.initial_date or datetime.now(UTC),
            description="Initial disbursal/borrowing",
        )
        await self.liability_repository.add_transaction(tx)

        # Recalculate valuations
        await self._recalculate_liability_values(liability_id)

        updated_liability = await self.liability_repository.get_liability_by_id(liability_id)
        if not updated_liability:
            return await self._to_calc_model(created_liability)
        return await self._to_calc_model(updated_liability)

    async def update_liability(self, liability_id: str, liability_update: LiabilityUpdate) -> LiabilityWithCalc:
        """Partially update liability metadata."""
        existing_liability = await self.liability_repository.get_liability_by_id(liability_id)
        if not existing_liability:
            raise ValueError(f"Liability with ID {liability_id} not found.")

        updated_liability = Liability(
            id=existing_liability.id,
            category_id=liability_update.category_id or existing_liability.category_id,
            name=liability_update.name or existing_liability.name,
            subcategory_id=(
                liability_update.subcategory_id
                if liability_update.subcategory_id is not None
                else existing_liability.subcategory_id
            ),
            original_value=existing_liability.original_value,
            current_value=existing_liability.current_value,
            interest_rate=(
                liability_update.interest_details.interest_rate
                if liability_update.interest_details
                else existing_liability.interest_rate
            ),
            interest_compounding=(
                liability_update.interest_details.compounding
                if liability_update.interest_details
                else existing_liability.interest_compounding
            ),
            emi_amount=(
                liability_update.interest_details.emi_amount
                if liability_update.interest_details
                else existing_liability.emi_amount
            ),
            maturity_date=(
                liability_update.interest_details.maturity_date
                if liability_update.interest_details
                else existing_liability.maturity_date
            ),
            notes=liability_update.notes if liability_update.notes is not None else existing_liability.notes,
            created_at=existing_liability.created_at,
        )

        saved_liability = await self.liability_repository.edit_liability(liability_id, updated_liability)
        await self._recalculate_liability_values(liability_id)
        final_liability = await self.liability_repository.get_liability_by_id(liability_id)
        return await self._to_calc_model(final_liability or saved_liability)

    async def delete_liability(self, liability_id: str) -> None:
        """Delete a liability."""
        await self.liability_repository.delete_liability(liability_id)

    async def get_liability_by_id(self, liability_id: str) -> LiabilityWithCalc:
        """Retrieve a liability by ID with calculations."""
        liability = await self.liability_repository.get_liability_by_id(liability_id)
        if not liability:
            raise ValueError(f"Liability with ID {liability_id} not found.")
        return await self._to_calc_model(liability)

    async def list_liabilities(
        self, category_id: str | None = None, search: str | None = None
    ) -> list[LiabilityWithCalc]:
        """List liabilities matching criteria."""
        filters = LiabilityFilter(category_id=category_id, search=search)
        sort = LiabilitySort(sort_by="name", sort_order="asc")
        liabilities = await self.liability_repository.get_all_liabilities(filters=filters, sort=sort)
        return [await self._to_calc_model(liab) for liab in liabilities]

    async def get_liability_summary(self) -> LiabilitySummary:
        """Calculate total summary and category breakdowns for all liabilities."""
        liabilities = await self.liability_repository.get_all_liabilities()
        categories = await self.liability_repository.get_all_categories()

        total_original = 0.0
        total_outstanding = 0.0
        total_repaid_all = 0.0
        total_interest_all = 0.0

        category_breakdowns = []
        liab_calcs = {}

        # Precompute dynamic values for all liabilities
        for liab in liabilities:
            txs = await self.liability_repository.get_transactions_for_liability(liab.id)
            calcs = calculate_current_outstanding(
                original_value=liab.original_value,
                interest_rate=liab.interest_rate,
                emi_amount=liab.emi_amount,
                transactions=txs,
                today=datetime.now(UTC),
            )
            liab_calcs[liab.id] = calcs
            total_original += liab.original_value
            total_outstanding += calcs["current_value"]
            total_repaid_all += calcs["total_repaid"]
            total_interest_all += calcs["accumulated_interest"]

        for cat in categories:
            cat_liabilities = [liab for liab in liabilities if liab.category_id == cat.id]
            cat_original = sum(liab.original_value for liab in cat_liabilities)
            cat_outstanding = sum(liab_calcs[liab.id]["current_value"] for liab in cat_liabilities)
            cat_repaid = sum(liab_calcs[liab.id]["total_repaid"] for liab in cat_liabilities)
            cat_interest = sum(liab_calcs[liab.id]["accumulated_interest"] for liab in cat_liabilities)

            category_breakdowns.append(
                LiabilityCategorySummary(
                    category_id=cat.id,
                    category_name=cat.name,
                    category_code=cat.code,
                    total_original=round(cat_original, 2),
                    total_outstanding=round(cat_outstanding, 2),
                    total_repaid=round(cat_repaid, 2),
                    accumulated_interest=round(cat_interest, 2),
                )
            )

        return LiabilitySummary(
            total_original=round(total_original, 2),
            total_outstanding=round(total_outstanding, 2),
            total_repaid=round(total_repaid_all, 2),
            accumulated_interest=round(total_interest_all, 2),
            category_breakdowns=category_breakdowns,
        )

    async def add_transaction(self, liability_id: str, tx_create: LiabilityTransactionCreate) -> LiabilityTransaction:
        """Log a new transaction and update outstanding balance on the parent liability."""
        liability = await self.liability_repository.get_liability_by_id(liability_id)
        if not liability:
            raise ValueError(f"Liability with ID {liability_id} not found.")

        tx = LiabilityTransaction(
            id=uuid.uuid4().hex,
            liability_id=liability_id,
            transaction_type=tx_create.transaction_type,
            amount=tx_create.amount,
            transaction_date=tx_create.transaction_date,
            description=tx_create.description,
        )
        created_tx = await self.liability_repository.add_transaction(tx)
        await self._recalculate_liability_values(liability_id)
        return created_tx

    async def get_transactions_for_liability(self, liability_id: str) -> list[LiabilityTransaction]:
        """Fetch transactions list for a single liability."""
        return await self.liability_repository.get_transactions_for_liability(liability_id)

    async def delete_transaction(self, transaction_id: str) -> None:
        """Remove a transaction and recalculate parent liability outstanding."""
        tx = await self.liability_repository.get_transaction_by_id(transaction_id)
        if not tx:
            raise ValueError(f"Transaction with ID {transaction_id} not found.")

        await self.liability_repository.delete_transaction(transaction_id)
        await self._recalculate_liability_values(tx.liability_id)

    async def _recalculate_liability_values(self, liability_id: str) -> None:
        """Run calculations across all transactions to refresh original and outstanding values."""
        liability = await self.liability_repository.get_liability_by_id(liability_id)
        if not liability:
            return

        transactions = await self.liability_repository.get_transactions_for_liability(liability_id)
        if not transactions:
            updated = Liability(
                id=liability.id,
                category_id=liability.category_id,
                name=liability.name,
                subcategory_id=liability.subcategory_id,
                original_value=0.0,
                current_value=0.0,
                interest_rate=liability.interest_rate,
                interest_compounding=liability.interest_compounding,
                emi_amount=liability.emi_amount,
                maturity_date=liability.maturity_date,
                notes=liability.notes,
                created_at=liability.created_at,
            )
            await self.liability_repository.edit_liability(liability_id, updated)
            return

        # Sort transactions chronologically (oldest first) to accurately process REVALUE
        sorted_txs = sorted(transactions, key=lambda t: (t.transaction_date, t.created_at or datetime.min))

        # 1. Total Borrowed (Original loan amount) is the sum of all BORROW transactions
        original_value = sum(t.amount for t in sorted_txs if t.transaction_type == LiabilityTransactionType.BORROW)

        # 2. Outstanding Balance calculation via shared engine
        calcs = calculate_current_outstanding(
            original_value=original_value,
            interest_rate=liability.interest_rate,
            emi_amount=liability.emi_amount,
            transactions=transactions,
            today=datetime.now(UTC),
        )
        current_value = calcs["current_value"]

        # Save recalculations, preserving all metadata
        updated = Liability(
            id=liability.id,
            category_id=liability.category_id,
            name=liability.name,
            subcategory_id=liability.subcategory_id,
            original_value=round(max(0.0, original_value), 2),
            current_value=round(max(0.0, current_value), 2),
            interest_rate=liability.interest_rate,
            interest_compounding=liability.interest_compounding,
            emi_amount=liability.emi_amount,
            maturity_date=liability.maturity_date,
            notes=liability.notes,
            created_at=liability.created_at,
        )
        await self.liability_repository.edit_liability(liability_id, updated)

    async def get_liability_projections(self, liability_id: str) -> LiabilityProjections:
        """Compute ideal and actual/projected amortization curves and financial metrics.

        Args:
            liability_id: The ID of the liability to calculate projections for.

        Returns:
            LiabilityProjections containing comparative metrics and data points.

        Raises:
            ValueError: If the liability doesn't exist, is missing interest/EMI configs,
                        or has no transaction history.
        """
        liability = await self.liability_repository.get_liability_by_id(liability_id)
        if not liability:
            raise ValueError(f"Liability with ID {liability_id} not found.")

        if not liability.interest_rate or not liability.emi_amount:
            raise ValueError(
                f"Liability '{liability.name}' is missing interest rate or scheduled EMI amount configuration."
            )

        transactions = await self.liability_repository.get_transactions_for_liability(liability_id)
        if not transactions:
            raise ValueError(f"Liability '{liability.name}' has no transactions in the ledger.")

        sorted_txs = sorted(transactions, key=lambda t: (t.transaction_date, t.created_at or datetime.min))
        borrow_txs = [t for t in sorted_txs if t.transaction_type == LiabilityTransactionType.BORROW]
        if not borrow_txs:
            raise ValueError(f"Liability '{liability.name}' has no disbursal/BORROW transactions.")

        first_borrow = borrow_txs[0]
        start_date = first_borrow.transaction_date
        if start_date.tzinfo is None:
            start_date = start_date.replace(tzinfo=UTC)

        original_value = sum(t.amount for t in borrow_txs)

        monthly_rate = (liability.interest_rate / 100.0) / 12.0
        emi = liability.emi_amount
        today = datetime.now(UTC)

        # A. Ideal Curve (no prepayments, pure scheduled amortization)
        ideal_points: dict[str, float] = {}
        ideal_interest_points: dict[str, float] = {}
        ideal_points[start_date.strftime("%Y-%m")] = original_value
        ideal_interest_points[start_date.strftime("%Y-%m")] = 0.0

        p_ideal = original_value
        n_ideal = 0
        total_interest_ideal = 0.0

        while p_ideal > 0 and n_ideal < 360:
            n_ideal += 1
            interest_m = p_ideal * monthly_rate
            payment = min(emi, p_ideal + interest_m)
            p_ideal = max(0.0, p_ideal + interest_m - payment)
            total_interest_ideal += interest_m

            n_str = add_months(start_date, n_ideal).strftime("%Y-%m")
            ideal_points[n_str] = round(p_ideal, 2)
            ideal_interest_points[n_str] = round(total_interest_ideal, 2)
            if p_ideal <= 0:
                break

        ideal_end_date = add_months(start_date, n_ideal)

        # B. Actual Historical Curve — uses the shared simulation engine
        # _simulate_amortization returns one snapshot per month from month 0 → today
        historical_snapshots = _simulate_amortization(
            original_value=original_value,
            interest_rate=liability.interest_rate,
            emi_amount=liability.emi_amount,
            transactions=transactions,
            up_to_date=today,
        )

        actual_points: dict[str, float] = {}
        actual_interest_points: dict[str, float] = {}
        for m_str, (bal, cum_int, _cum_repaid) in historical_snapshots.items():
            actual_points[m_str] = round(bal, 2)
            actual_interest_points[m_str] = round(max(0.0, cum_int), 2)

        # Today's closing values from the simulation
        today_str = today.strftime("%Y-%m")
        today_snap = historical_snapshots.get(today_str)
        if today_snap:
            p_today, interest_today, _repaid_today = today_snap
        else:
            # Fallback: use the last available snapshot
            last_snap_key = sorted(historical_snapshots.keys())[-1] if historical_snapshots else None
            if last_snap_key:
                p_today, interest_today, _repaid_today = historical_snapshots[last_snap_key]
            else:
                p_today, interest_today = 0.0, 0.0

        p_today = max(0.0, p_today)
        total_interest_historical = max(0.0, interest_today)

        # C. Future Projection (from today, scheduled EMI only)
        k_projected = 0
        total_interest_projected_future = 0.0
        projected_future_points: dict[str, float] = {}
        projected_future_interest_points: dict[str, float] = {}

        if p_today > 0:
            p_proj = p_today
            cum_int_proj = total_interest_historical
            while p_proj > 0 and k_projected < 360:
                k_projected += 1
                interest_m = p_proj * monthly_rate
                payment = min(emi, p_proj + interest_m)
                p_proj = max(0.0, p_proj + interest_m - payment)
                total_interest_projected_future += interest_m
                cum_int_proj += interest_m

                k_str = add_months(today, k_projected).strftime("%Y-%m")
                projected_future_points[k_str] = round(p_proj, 2)
                projected_future_interest_points[k_str] = round(cum_int_proj, 2)
                if p_proj <= 0:
                    break

        projected_end_date = add_months(today, k_projected) if p_today > 0 else today

        # D. Derived Metrics
        elapsed_months = max(0, (today.year - start_date.year) * 12 + (today.month - start_date.month))
        total_interest_projected = total_interest_historical + total_interest_projected_future
        tenure_saved = n_ideal - (elapsed_months + k_projected)
        interest_saved = total_interest_ideal - total_interest_projected

        # E. Combine into projection point list
        max_end_date = max(ideal_end_date, projected_end_date)
        total_span = max(0, (max_end_date.year - start_date.year) * 12 + (max_end_date.month - start_date.month))

        projection_points_list: list[LiabilityProjectionPoint] = []
        for step in range(total_span + 1):
            date_step = add_months(start_date, step)
            step_str = date_step.strftime("%Y-%m")

            ideal_bal = ideal_points.get(step_str, 0.0)
            ideal_int = ideal_interest_points.get(step_str, 0.0)

            if date_step <= today:
                actual_bal = actual_points.get(step_str, 0.0)
                actual_int = actual_interest_points.get(step_str, 0.0)
            else:
                actual_bal = projected_future_points.get(step_str, 0.0)
                actual_int = projected_future_interest_points.get(step_str, 0.0)

            projection_points_list.append(
                LiabilityProjectionPoint(
                    date=step_str,
                    ideal_balance=round(ideal_bal, 2),
                    actual_balance=round(actual_bal, 2),
                    ideal_interest_paid=round(ideal_int, 2),
                    actual_interest_paid=round(max(0.0, actual_int), 2),
                )
            )

        metrics = LiabilityProjectionMetrics(
            ideal_tenure_months=n_ideal,
            remaining_tenure_months=k_projected,
            tenure_saved_months=tenure_saved,
            total_interest_ideal=round(max(0.0, total_interest_ideal), 2),
            total_interest_projected=round(max(0.0, total_interest_projected), 2),
            interest_saved=round(interest_saved, 2),
            ideal_end_date=ideal_end_date,
            projected_end_date=projected_end_date,
        )

        return LiabilityProjections(metrics=metrics, projection_points=projection_points_list)
