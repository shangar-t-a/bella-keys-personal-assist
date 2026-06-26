# ruff: noqa: PLR2004, E501, D102, PLR0913
"""Pure unit tests for the _simulate_amortization engine and calculate_current_outstanding.

These tests are entirely deterministic and do NOT require a database or async context.
They exercise every scenario the simulation engine must handle:

  1. Pure scheduled EMI — balance reduces smoothly month over month
  2. Extra REPAY (prepayment) — reduces outstanding faster than ideal
  3. REVALUE — bank statement override; interest is adjusted to reconcile
  4. REVALUE + same-month REPAY — REPAY is included in the REVALUE reconciliation
  5. Multiple REVALUEs in one month — only the last one counts
  6. Loan fully paid off — no further accumulation after zero balance
  7. Missed payment simulation — when no transactions are logged for a month,
     scheduled EMI is auto-applied (same as the "no transactions" path)
  8. REVALUE after missed payments — correctly absorbs the extra accrued interest
  9. Real-world personal loan walkthrough (₹12L, 11.95%, 3 REPAYs, 1 REVALUE)
"""

from datetime import UTC, datetime
from unittest.mock import MagicMock

from app.entities.models.liability import LiabilityTransaction, LiabilityTransactionType
from app.use_cases.liability import _simulate_amortization, calculate_current_outstanding

# Helpers


def _make_tx(
    tx_type: LiabilityTransactionType,
    amount: float,
    year: int,
    month: int,
    day: int = 1,
    tx_id: str | None = None,
) -> LiabilityTransaction:
    """Build a minimal LiabilityTransaction for simulation testing."""
    m = MagicMock(spec=LiabilityTransaction)
    m.id = tx_id or f"{tx_type.value}_{year}{month:02d}{day:02d}"
    m.transaction_type = tx_type
    m.amount = float(amount)
    m.transaction_date = datetime(year, month, day, tzinfo=UTC)
    m.created_at = m.transaction_date
    m.liability_id = "test-liability-id"
    return m


BORROW = LiabilityTransactionType.BORROW
REPAY = LiabilityTransactionType.REPAY
REVALUE = LiabilityTransactionType.REVALUE


# Scenario 1: Pure EMI — smooth declining balance


class TestPureEMIAmortization:
    """Verify that without any manual transactions the balance decreases monotonically."""

    def test_balance_decreases_each_month(self):
        # ₹5,00,000 @ 12% p.a. (1% per month), EMI ₹15,000
        # Month 1 interest = 500000 * 0.01 = 5000
        # Principal paid month 1 = 15000 - 5000 = 10000  → balance 490000
        principal = 500_000.0
        txs = [_make_tx(BORROW, principal, 2024, 1)]
        up_to = datetime(2024, 7, 1, tzinfo=UTC)

        snaps = _simulate_amortization(
            original_value=principal,
            interest_rate=12.0,
            emi_amount=15_000.0,
            transactions=txs,
            up_to_date=up_to,
        )

        # Month 0 (disbursal) recorded
        assert "2024-01" in snaps
        assert snaps["2024-01"][0] == 500_000.0  # opening balance = principal

        # Months 1-6 should be strictly decreasing
        balances = [snaps.get(f"2024-{m:02d}", (None,))[0] for m in range(2, 8)]
        for i in range(len(balances) - 1):
            assert balances[i] is not None
            assert balances[i + 1] is not None
            assert balances[i] > balances[i + 1], (
                f"Balance should decrease: month {i + 2} {balances[i]} → month {i + 3} {balances[i + 1]}"
            )

    def test_month_1_values_exactly(self):
        """Verify precise arithmetic for month-1 interest, principal, and balance."""
        principal = 500_000.0
        monthly_rate = 12.0 / 100 / 12  # 0.01
        emi = 15_000.0
        interest_m1 = principal * monthly_rate  # 5000.0
        payment_m1 = min(emi, principal + interest_m1)  # 15000
        expected_balance = principal + interest_m1 - payment_m1  # 490000

        txs = [_make_tx(BORROW, principal, 2024, 1)]
        up_to = datetime(2024, 2, 1, tzinfo=UTC)

        snaps = _simulate_amortization(
            original_value=principal,
            interest_rate=12.0,
            emi_amount=emi,
            transactions=txs,
            up_to_date=up_to,
        )

        bal, cum_int, cum_repaid = snaps["2024-02"]
        assert abs(bal - expected_balance) < 0.01, f"Balance mismatch: {bal} vs {expected_balance}"
        assert abs(cum_int - interest_m1) < 0.01, f"Interest mismatch: {cum_int} vs {interest_m1}"
        assert abs(cum_repaid - payment_m1) < 0.01, f"Repaid mismatch: {cum_repaid} vs {payment_m1}"

    def test_cumulative_interest_increases(self):
        """Accumulated interest must be non-decreasing."""
        principal = 300_000.0
        txs = [_make_tx(BORROW, principal, 2024, 1)]
        up_to = datetime(2024, 12, 1, tzinfo=UTC)

        snaps = _simulate_amortization(
            original_value=principal,
            interest_rate=10.0,
            emi_amount=8_000.0,
            transactions=txs,
            up_to_date=up_to,
        )

        prev_int = -1.0
        for key in sorted(snaps.keys()):
            _bal, cum_int, _cum_rep = snaps[key]
            assert cum_int >= prev_int - 0.01  # allow tiny float noise
            prev_int = cum_int


# Scenario 2: REPAY (prepayment) reduces balance faster


class TestPrepaymentReducesBalance:
    """Extra REPAY in a month must reduce the balance more than scheduled EMI alone."""

    def test_prepayment_reduces_closing_balance(self):
        """Month with REPAY should yield lower closing balance than without."""
        principal = 500_000.0
        txs_base = [_make_tx(BORROW, principal, 2024, 1)]
        txs_with_prepay = [
            _make_tx(BORROW, principal, 2024, 1),
            _make_tx(REPAY, 50_000.0, 2024, 2),  # extra prepayment in month 2
        ]
        up_to = datetime(2024, 3, 1, tzinfo=UTC)

        snaps_base = _simulate_amortization(principal, 12.0, 15_000.0, txs_base, up_to)
        snaps_prepay = _simulate_amortization(principal, 12.0, 15_000.0, txs_with_prepay, up_to)

        bal_base = snaps_base["2024-03"][0]
        bal_prepay = snaps_prepay["2024-03"][0]

        assert bal_prepay < bal_base, f"Prepayment should reduce balance: prepay={bal_prepay} base={bal_base}"

    def test_prepayment_increases_repaid_total(self):
        """Total repaid must include the extra REPAY amount."""
        principal = 200_000.0
        txs = [
            _make_tx(BORROW, principal, 2024, 1),
            _make_tx(REPAY, 20_000.0, 2024, 2),
        ]
        up_to = datetime(2024, 2, 1, tzinfo=UTC)

        snaps = _simulate_amortization(principal, 12.0, 10_000.0, txs, up_to)
        _bal, _cum_int, cum_repaid = snaps["2024-02"]

        # auto_emi for month 2 = min(10000, 200000 * 1.01) = 10000
        # prepay = 20000 → total repaid in month 2 = 30000
        assert cum_repaid >= 30_000.0 - 0.01


# Scenario 3: REVALUE — bank statement override


class TestRevalueMonthSemantics:
    """REVALUE snaps the balance to the bank's official value; interest is reconciled."""

    def test_revalue_sets_closing_balance_exactly(self):
        """Balance at end of REVALUE month equals the REVALUE amount."""
        principal = 500_000.0
        reval_amount = 485_000.0
        txs = [
            _make_tx(BORROW, principal, 2024, 1),
            _make_tx(REVALUE, reval_amount, 2024, 2),
        ]
        up_to = datetime(2024, 2, 1, tzinfo=UTC)

        snaps = _simulate_amortization(principal, 12.0, 15_000.0, txs, up_to)
        bal, _cum_int, _cum_rep = snaps["2024-02"]

        assert abs(bal - reval_amount) < 0.01, f"REVALUE: balance should be {reval_amount}, got {bal}"

    def test_revalue_adjusts_interest_correctly(self):
        """Cumulative interest after REVALUE = reval - (prev_balance + borrows), floored at 0.

        REVALUE semantics: the bank's closing balance absorbs everything (interest + EMI + payments).
        We attribute "implied interest" = reval_amount - (prev_balance + borrows).
        """
        # Month 2 opening balance ≈ 500000 (from month 1 disbursal; no EMI in month 0)
        # Month 2 REVALUE = 488000
        # implied_interest = 488000 - 500000 = -12000 → floored to 0
        # (The REVALUE is lower than opening because EMI + interest netted to a reduction)
        principal = 500_000.0
        reval_amount = 488_000.0
        txs = [
            _make_tx(BORROW, principal, 2024, 1),
            _make_tx(REVALUE, reval_amount, 2024, 2),
        ]
        up_to = datetime(2024, 2, 1, tzinfo=UTC)

        snaps = _simulate_amortization(principal, 12.0, 15_000.0, txs, up_to)
        _bal, cum_int, _cum_rep = snaps["2024-02"]

        # implied_interest = 488000 - 500000 = -12000 → floored to 0
        assert cum_int == 0.0, f"Interest floored to 0 (REVALUE < prev balance): {cum_int}"

    def test_revalue_does_not_spike_in_subsequent_months(self):
        """After REVALUE, subsequent months should resume smooth EMI-based decline."""
        principal = 500_000.0
        reval_amount = 490_000.0
        txs = [
            _make_tx(BORROW, principal, 2024, 1),
            _make_tx(REVALUE, reval_amount, 2024, 2),
        ]
        up_to = datetime(2024, 5, 1, tzinfo=UTC)

        snaps = _simulate_amortization(principal, 12.0, 15_000.0, txs, up_to)

        # Months 3, 4, 5 should be strictly below REVALUE amount and declining
        assert snaps["2024-03"][0] < reval_amount
        assert snaps["2024-04"][0] < snaps["2024-03"][0]
        assert snaps["2024-05"][0] < snaps["2024-04"][0]


# Scenario 4: REVALUE + same-month REPAY


class TestRevalueWithSameMonthRepay:
    """REPAY in same month as REVALUE must both be included in the reconciliation."""

    def test_revalue_and_repay_same_month(self):
        """Balance is REVALUE amount; manual REPAY is credited to accum_repaid separately.

        REVALUE semantics: REVALUE is authoritative for the closing balance.
        The manual REPAY is credited to accum_repaid (user's payment tracking)
        but the balance is set to REVALUE, not further adjusted.
        """
        principal = 500_000.0
        reval_amount = 472_000.0
        txs = [
            _make_tx(BORROW, principal, 2024, 1),
            _make_tx(REPAY, 20_000.0, 2024, 2),
            _make_tx(REVALUE, reval_amount, 2024, 2),
        ]
        up_to = datetime(2024, 2, 1, tzinfo=UTC)

        snaps = _simulate_amortization(principal, 12.0, 15_000.0, txs, up_to)
        bal, cum_int, cum_repaid = snaps["2024-02"]

        assert abs(bal - reval_amount) < 0.01, f"Balance should be REVALUE amount: {bal} vs {reval_amount}"
        # Only the manual REPAY (20000) is tracked in accum_repaid for REVALUE months
        assert abs(cum_repaid - 20_000.0) < 0.01, f"Repaid should be the manual REPAY only: {cum_repaid}"

    def test_revalue_and_repay_same_month_positive_interest(self):
        """Verify that implied interest is calculated correctly when it is positive and a repayment exists in the same month."""
        principal = 500_000.0
        reval_amount = 495_000.0
        txs = [
            _make_tx(BORROW, principal, 2024, 1),
            _make_tx(REPAY, 20_000.0, 2024, 2),
            _make_tx(REVALUE, reval_amount, 2024, 2),
        ]
        up_to = datetime(2024, 2, 1, tzinfo=UTC)

        snaps = _simulate_amortization(principal, 12.0, 15_000.0, txs, up_to)
        bal, cum_int, cum_repaid = snaps["2024-02"]

        assert abs(bal - reval_amount) < 0.01
        assert abs(cum_repaid - 20_000.0) < 0.01
        assert abs(cum_int - 15_000.0) < 0.01, f"Expected implied interest to be 15,000, got {cum_int}"


# Scenario 5: Multiple REVALUEs — only latest matters


class TestMultipleRevaluesSameMonth:
    """When multiple REVALUEs exist in a month, only the last (latest) is used."""

    def test_latest_revalue_wins(self):
        principal = 500_000.0
        txs = [
            _make_tx(BORROW, principal, 2024, 1),
            _make_tx(REVALUE, 480_000.0, 2024, 2, day=5, tx_id="reval_early"),
            _make_tx(REVALUE, 475_000.0, 2024, 2, day=10, tx_id="reval_late"),
        ]
        up_to = datetime(2024, 2, 1, tzinfo=UTC)

        snaps = _simulate_amortization(principal, 12.0, 15_000.0, txs, up_to)
        bal, _, _ = snaps["2024-02"]

        # The last REVALUE in sorted order (by date, then created_at) wins
        assert abs(bal - 475_000.0) < 0.01, f"Latest REVALUE should win: {bal}"


# Scenario 6: Loan fully paid off


class TestLoanPaidOff:
    """Once balance hits zero, no further interest or balance changes occur."""

    def test_zero_balance_stays_zero(self):
        # ₹10,000 @ 12% with ₹15,000 EMI — pays off very quickly
        principal = 10_000.0
        txs = [_make_tx(BORROW, principal, 2024, 1)]
        up_to = datetime(2025, 1, 1, tzinfo=UTC)

        snaps = _simulate_amortization(principal, 12.0, 15_000.0, txs, up_to)

        # Find first zero month
        first_zero_month = None
        for key in sorted(snaps.keys()):
            if snaps[key][0] == 0.0:
                first_zero_month = key
                break

        assert first_zero_month is not None, "Loan should have paid off within 12 months"

        # All subsequent months must also be 0
        subsequent = [k for k in sorted(snaps.keys()) if k > first_zero_month]
        for key in subsequent:
            assert snaps[key][0] == 0.0, f"Balance after payoff should stay 0, got {snaps[key][0]} at {key}"


# Scenario 7: Missed payment (no transactions logged)


class TestMissedPayment:
    """When no transactions are logged for a month, scheduled EMI is auto-applied."""

    def test_no_transactions_applies_scheduled_emi(self):
        """Months with no transactions behave exactly like regular scheduled months."""
        principal = 500_000.0
        emi = 15_000.0

        txs = [_make_tx(BORROW, principal, 2024, 1)]
        up_to = datetime(2024, 3, 1, tzinfo=UTC)

        snaps = _simulate_amortization(principal, 12.0, emi, txs, up_to)

        # Month 3 should be below month 2 because auto EMI was applied in month 3
        assert snaps["2024-03"][0] < snaps["2024-02"][0], "Auto EMI must reduce balance in months without transactions"


# Scenario 8: REVALUE after missed payments


class TestRevalueAfterMissedPayments:
    """REVALUE correctly captures higher balance when payments were missed."""

    def test_revalue_after_no_payments_higher_balance(self):
        """If no transactions for 3 months and then REVALUE, the REVALUE amount reflects higher balance.

        When no payments are logged for months 2 and 3, auto-EMI is applied. The REVALUE in month 4
        is still authoritative; interest for that month is reval - (prev_balance + borrows).
        """
        principal = 500_000.0
        # Month 4 REVALUE: say bank shows 492,000 (higher than ideal 3-month EMI schedule)
        reval_amount = 492_000.0
        txs = [
            _make_tx(BORROW, principal, 2024, 1),
            # No payments in months 2, 3
            _make_tx(REVALUE, reval_amount, 2024, 4),
        ]
        up_to = datetime(2024, 4, 1, tzinfo=UTC)

        snaps = _simulate_amortization(principal, 12.0, 15_000.0, txs, up_to)
        bal, cum_int, _ = snaps["2024-04"]

        assert abs(bal - reval_amount) < 0.01, f"Balance should be REVALUE: {bal}"
        # Cumulative interest must be positive
        assert cum_int > 0, f"Interest must be tracked: {cum_int}"


# Scenario 9: calculate_current_outstanding delegates to simulation


class TestCalculateCurrentOutstanding:
    """Verify calculate_current_outstanding returns consistent values."""

    def test_pure_borrow_no_payments_same_month(self):
        """Loan created today: no elapsed months, balance = principal."""
        principal = 5_00_000.0
        txs = [_make_tx(BORROW, principal, 2024, 6)]
        today = datetime(2024, 6, 15, tzinfo=UTC)

        result = calculate_current_outstanding(
            original_value=principal,
            interest_rate=12.0,
            emi_amount=15_000.0,
            transactions=txs,
            today=today,
        )

        assert result["current_value"] == principal
        assert result["accumulated_interest"] == 0.0
        assert result["total_repaid"] == 0.0

    def test_interest_accrues_after_first_month(self):
        """After 1 full month, interest must be > 0."""
        principal = 500_000.0
        txs = [_make_tx(BORROW, principal, 2024, 1)]
        today = datetime(2024, 3, 1, tzinfo=UTC)

        result = calculate_current_outstanding(
            original_value=principal,
            interest_rate=12.0,
            emi_amount=15_000.0,
            transactions=txs,
            today=today,
        )

        assert result["accumulated_interest"] > 0, "Interest must accrue after one month"
        assert result["current_value"] < principal, "Balance must decrease with EMI payments"

    def test_revalue_sets_current_value(self):
        """REVALUE in current month must snap current_value to that amount."""
        principal = 500_000.0
        reval = 485_000.0
        txs = [
            _make_tx(BORROW, principal, 2024, 1),
            _make_tx(REVALUE, reval, 2024, 3),
        ]
        today = datetime(2024, 3, 15, tzinfo=UTC)

        result = calculate_current_outstanding(
            original_value=principal,
            interest_rate=12.0,
            emi_amount=15_000.0,
            transactions=txs,
            today=today,
        )

        assert abs(result["current_value"] - reval) < 0.01

    def test_no_transactions_returns_zeros(self):
        result = calculate_current_outstanding(
            original_value=0.0,
            interest_rate=12.0,
            emi_amount=15_000.0,
            transactions=[],
            today=datetime(2024, 6, 1, tzinfo=UTC),
        )
        assert result == {"current_value": 0.0, "total_repaid": 0.0, "accumulated_interest": 0.0}

    def test_no_interest_rate_simple_loan(self):
        """Non-EMI loan: balance = principal - repayments."""
        principal = 100_000.0
        txs = [
            _make_tx(BORROW, principal, 2024, 1),
            _make_tx(REPAY, 30_000.0, 2024, 3),
        ]
        today = datetime(2024, 6, 1, tzinfo=UTC)

        result = calculate_current_outstanding(
            original_value=principal,
            interest_rate=None,
            emi_amount=None,
            transactions=txs,
            today=today,
        )

        assert result["current_value"] == 70_000.0
        assert result["total_repaid"] == 30_000.0
        assert result["accumulated_interest"] == 0.0


# Scenario 10: Real-world personal loan walkthrough


class TestRealWorldPersonalLoan:
    """Simulate the actual personal loan data: ₹12,00,000 @ 11.95%, EMI ₹26,743.

    Transactions:
      - BORROW ₹12,00,000 on 2025-04-08
      - REPAY  ₹96,581   on 2025-05-26  (extra prepayment in May 2025)
      - REPAY  ₹1,44,871 on 2025-07-11  (extra prepayment in Jul 2025)
      - REVALUE ₹6,35,563.92 on 2026-06-21 (bank statement Jun 2026)

    This verifies the simulation produces a smooth curve with no spikes.
    """

    def _build_txs(self):
        return [
            _make_tx(BORROW, 1_200_000.0, 2025, 4, day=8),
            _make_tx(REPAY, 96_581.0, 2025, 5, day=26),
            _make_tx(REPAY, 144_871.0, 2025, 7, day=11),
            _make_tx(REVALUE, 635_563.92, 2026, 6, day=21),
        ]

    def test_balance_after_revalue_is_correct(self):
        txs = self._build_txs()
        up_to = datetime(2026, 6, 21, tzinfo=UTC)

        snaps = _simulate_amortization(
            original_value=1_200_000.0,
            interest_rate=11.95,
            emi_amount=26_743.0,
            transactions=txs,
            up_to_date=up_to,
        )

        bal, _, _ = snaps["2026-06"]
        assert abs(bal - 635_563.92) < 0.01, f"Balance after REVALUE should be 635563.92, got {bal}"

    def test_balance_monotonically_declined_before_revalue(self):
        """Verify months Apr2025 → May2025 → Jun2025 → Jul2025 each drop."""
        txs = self._build_txs()
        up_to = datetime(2026, 6, 21, tzinfo=UTC)

        snaps = _simulate_amortization(
            original_value=1_200_000.0,
            interest_rate=11.95,
            emi_amount=26_743.0,
            transactions=txs,
            up_to_date=up_to,
        )

        # months with large prepayments should show significant drops
        assert snaps["2025-05"][0] < snaps["2025-04"][0], "May should be lower than Apr"
        assert snaps["2025-07"][0] < snaps["2025-06"][0], "Jul should be lower than Jun (large prepayment)"

    def test_no_negative_interest(self):
        """Cumulative interest must never be negative."""
        txs = self._build_txs()
        up_to = datetime(2026, 6, 21, tzinfo=UTC)

        snaps = _simulate_amortization(
            original_value=1_200_000.0,
            interest_rate=11.95,
            emi_amount=26_743.0,
            transactions=txs,
            up_to_date=up_to,
        )

        for key in snaps:
            _, cum_int, _ = snaps[key]
            assert cum_int >= 0.0, f"Cumulative interest negative at {key}: {cum_int}"

    def test_calculate_current_outstanding_matches_revalue(self):
        """calculate_current_outstanding must return the REVALUE amount as current_value."""
        txs = self._build_txs()
        today = datetime(2026, 6, 21, tzinfo=UTC)

        result = calculate_current_outstanding(
            original_value=1_200_000.0,
            interest_rate=11.95,
            emi_amount=26_743.0,
            transactions=txs,
            today=today,
        )

        assert abs(result["current_value"] - 635_563.92) < 0.01
        assert result["accumulated_interest"] >= 0.0

    def test_interest_curve_has_no_spikes(self):
        """Cumulative interest must be monotonically non-decreasing across all months."""
        txs = self._build_txs()
        up_to = datetime(2026, 6, 21, tzinfo=UTC)

        snaps = _simulate_amortization(
            original_value=1_200_000.0,
            interest_rate=11.95,
            emi_amount=26_743.0,
            transactions=txs,
            up_to_date=up_to,
        )

        sorted_keys = sorted(snaps.keys())
        for i in range(1, len(sorted_keys)):
            prev_int = snaps[sorted_keys[i - 1]][1]
            curr_int = snaps[sorted_keys[i]][1]
            assert curr_int >= prev_int - 0.01, f"Interest spike at {sorted_keys[i]}: {prev_int:.2f} → {curr_int:.2f}"


class TestEMIStartDate:
    """Verify that emi_start_date is respected during simulation and calculations."""

    def test_emi_not_applied_before_start_date(self):
        # Borrow ₹1,00,000 in month 1, emi_start_date in month 5, EMI ₹5,000
        # Balance should accrue interest but NOT decrease from Month 1 to Month 4
        principal = 100_000.0
        txs = [_make_tx(BORROW, principal, 2024, 1)]
        up_to = datetime(2024, 4, 1, tzinfo=UTC)
        emi_start = datetime(2024, 5, 1, tzinfo=UTC)

        snaps = _simulate_amortization(
            original_value=principal,
            interest_rate=12.0,  # 1% per month
            emi_amount=5_000.0,
            transactions=txs,
            up_to_date=up_to,
            emi_start_date=emi_start,
        )

        # In 2024-01, balance = 100,000
        # In 2024-02, balance = 100,000 + 1,000 (interest) = 101,000
        # In 2024-03, balance = 101,000 + 1,010 = 102,010
        # In 2024-04, balance = 102,010 + 1,020.10 = 103,030.10
        assert snaps["2024-01"][0] == 100_000.0
        assert abs(snaps["2024-02"][0] - 101_000.0) < 0.01
        assert abs(snaps["2024-03"][0] - 102_010.0) < 0.01
        assert abs(snaps["2024-04"][0] - 103_030.10) < 0.01

    def test_emi_applied_on_and_after_start_date(self):
        # Borrow ₹1,00,000 in month 1, emi_start_date in month 3
        # Month 2: balance = 100k + 1k = 101k (no EMI applied)
        # Month 3: balance = 101k + 1.01k (interest) - 5k (EMI) = 97.01k
        principal = 100_000.0
        txs = [_make_tx(BORROW, principal, 2024, 1)]
        up_to = datetime(2024, 3, 1, tzinfo=UTC)
        emi_start = datetime(2024, 3, 1, tzinfo=UTC)

        snaps = _simulate_amortization(
            original_value=principal,
            interest_rate=12.0,
            emi_amount=5_000.0,
            transactions=txs,
            up_to_date=up_to,
            emi_start_date=emi_start,
        )

        assert abs(snaps["2024-02"][0] - 101_000.0) < 0.01
        assert abs(snaps["2024-03"][0] - 97_010.0) < 0.01


class TestMultiBorrowOutstanding:
    """Verify that multi-disbursal loans correctly handle opening balance and future borrows."""

    def test_opening_balance_starts_with_first_borrow_only(self):
        # Total borrows = 34k + 34k = 68k.
        # Month 0 (2024-01) should start with 34k only, not 68k.
        txs = [
            _make_tx(BORROW, 34_000.0, 2024, 1),
            _make_tx(BORROW, 34_000.0, 2024, 3),
        ]
        up_to = datetime(2024, 3, 1, tzinfo=UTC)

        snaps = _simulate_amortization(
            original_value=68_000.0,
            interest_rate=12.0,
            emi_amount=5_000.0,
            transactions=txs,
            up_to_date=up_to,
        )

        # Month 0: 34,000
        assert snaps["2024-01"][0] == 34_000.0


class TestPaidOffSkipRevival:
    """Verify that new borrows or revalues revive a loan even if the simulated balance hit 0.0."""

    def test_borrow_revives_paid_off_loan(self):
        # Borrow ₹5,000 in month 1, EMI ₹6,000.
        # Month 2: balance goes to 0.0.
        # Month 3: BORROW ₹10,000 happens. Balance must become 10,000, not stay 0.0.
        txs = [
            _make_tx(BORROW, 5_000.0, 2024, 1),
            _make_tx(BORROW, 10_000.0, 2024, 3),
        ]
        up_to = datetime(2024, 3, 1, tzinfo=UTC)

        snaps = _simulate_amortization(
            original_value=15_000.0,
            interest_rate=12.0,
            emi_amount=6_000.0,
            transactions=txs,
            up_to_date=up_to,
        )

        assert snaps["2024-01"][0] == 5_000.0
        # Month 2: balance 0.0
        assert snaps["2024-02"][0] == 0.0
        # Month 3: balance should be 10,000.0 (plus some minor interest or repayments depending on order)
        assert snaps["2024-03"][0] > 0.0
        assert abs(snaps["2024-03"][0] - 10_000.0) < 100.0

