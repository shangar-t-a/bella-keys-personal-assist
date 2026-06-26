# System Requirements Document: Wealth Manager — Liabilities

This document defines the functional requirements, data model, transaction semantics, and amortization simulation rules for the **Wealth Manager - Liabilities** module. For formula details see `calculations.md`. For end-user guidance see `docs/user/wealth-manager-guide.md`.

## 1. Product Goals

- Enable users to track all outstanding loans and debts with a full chronological ledger.
- Simulate amortization month-by-month using a single shared calculation engine.
- Surface intelligence metrics: tenure saved, interest saved, projected end date.
- Allow late entry of transactions (any past date) without corrupting simulation accuracy.
- Support both EMI-based interest-bearing loans and simple interest-free liabilities.

## 2. Supported Categories and Subcategories

Liabilities are organized under pre-seeded top-level categories and detailed subcategories.

### Categories

| Code | Name | Description |
|---|---|---|
| `SECURED_LOAN` | Secured Loans | Loans backed by collateral (home, vehicle) |
| `UNSECURED_LOAN` | Unsecured Loans | Loans with no collateral (personal, education) |
| `REVOLVING_CREDIT` | Revolving Credit | Credit cards, lines of credit |
| `OTHER` | Other Liabilities | Family loans, hand loans, general debts |

### Subcategory Configuration

| Field | Type | Purpose |
|---|---|---|
| `has_interest` | Boolean | Whether EMI and interest rate fields are applicable |
| `has_maturity` | Boolean | Whether a maturity/end date is relevant |

## 3. Transaction Types and Semantics

The entire liability lifecycle is modelled through four chronological event types logged to a ledger.

| Type | Meaning | Effect on Balance |
|---|---|---|
| `BORROW` | Funds disbursed or additional loan drawn | Increases outstanding balance |
| `REPAY` | Extra manual payment on top of scheduled EMI | Reduces outstanding balance; tracked in total repaid |
| `REVALUE` | Bank's official statement balance for a month | **Authoritative override** — sets closing balance for that month; all interest, EMI, and payments for the month are implicitly absorbed |

### REVALUE Semantics (Critical)

A `REVALUE` transaction represents the bank's official outstanding balance as of that statement month. It is the single source of truth for that month's closing balance.

- The simulation does **not** apply scheduled EMI separately in a REVALUE month (that would double-count).
- The implied interest for the REVALUE month is:
  `implied_interest = max(0, revalue_amount - (prev_balance + borrows_this_month))`
- Any `REPAY` transactions recorded in the same month as a `REVALUE` are credited to `accum_repaid` for tracking purposes, but do not additionally adjust the balance (the REVALUE already accounts for them).
- If `implied_interest < 0` (the REVALUE amount is below the previous balance, meaning the bank applied a net reduction including EMI and payments), the implied interest is floored to 0 — no negative interest is recorded.

## 4. Simulation Engine

All outstanding balance calculations and projection curves are driven by a single shared pure function: `_simulate_amortization()`.

### Inputs

| Parameter | Description |
|---|---|
| `original_value` | Sum of all BORROW transaction amounts |
| `interest_rate` | Annual nominal rate as a percentage (e.g., `11.95` for 11.95%) |
| `emi_amount` | Optional scheduled monthly EMI in INR (or None/0 for irregular/discretionary repayments) |
| `emi_start_date` | Optional date when repayments/EMIs officially begin (moratorium support) |
| `transactions` | Full chronological ledger of all transactions |
| `up_to_date` | Simulate up to and including this date's calendar month |
| `compounding` | Compounding frequency (`MONTHLY`, `QUARTERLY`, `HALF_YEARLY`, `YEARLY`) |

### Compounding Frequency & Payment Semantic (Robust Design)

Rather than assuming monthly compounding, the simulation respects the configured compounding frequency:

- The engine tracks two separate balances: **Principal** (`p`) and **Accrued Interest** (`i_acc`).
- Monthly interest is calculated on the principal: `interest = p × monthly_rate` and added to `i_acc`.
- Compounding events (adding `i_acc` to `p` and resetting `i_acc = 0`) occur at frequency intervals (e.g., every 3 months for `QUARTERLY`, 12 months for `YEARLY`) relative to the disbursal date.
- Repayments (scheduled EMIs and manual prepayments) are applied to **Accrued Interest first**. Any remaining repayment amount is then subtracted from the **Principal**.

### Month-by-Month Logic

**Month 0 (Disbursal Month):**

- Opening principal = sum of all BORROW amounts; accrued interest = 0.0.
- Any extra BORROWs in the same month increase principal.
- Any REPAYs in the same month are applied to accrued interest first (if any), then reduce principal.
- No interest is accrued in the disbursal month.

**Months 1 to N (up_to_date):**

If a `REVALUE` exists in the month:

1. Set principal = REVALUE amount; reset accrued interest `i_acc` = 0.0.
2. Add `max(0, reval_amount - (prev_principal + prev_i_acc + borrows))` to cumulative interest.
3. Credit any manual REPAY amounts to cumulative repaid.

Otherwise (normal month):

1. Accrue interest: `interest_m = principal × monthly_rate`. Add to `i_acc` and cumulative interest.
2. Apply scheduled EMI: if `emi_start_date` is configured and current month is before `emi_start_date`, `auto_emi` is `0.0`. Otherwise, `auto_emi = min(emi, principal + i_acc)`.
3. Apply any extra REPAY: `total_payment = auto_emi + repays`
4. Apply repayment to `i_acc` first, then reduce `principal` with the remainder.
5. Check compounding frequency: if the month index is a multiple of the compounding interval (e.g. `month_idx % 3 == 0` for `QUARTERLY`), add outstanding `i_acc` to `principal` and reset `i_acc = 0.0`.
6. Add `total_payment` to cumulative repaid.

If balance (`principal + i_acc`) reaches 0, all subsequent months are recorded as zero.

### Consumers

| Consumer | Usage |
|---|---|
| `calculate_current_outstanding()` | Takes the last snapshot. Returns `current_value`, `total_repaid`, `accumulated_interest` for the dashboard, respecting the compounding frequency. |
| `get_liability_projections()` | Uses all snapshots for the historical actual curve. Appends a compounding-aware future projection from today's balance. |
| `_calculate_remaining_tenure()` | Dynamic backend tenure estimator. Runs a step-by-step projection simulation (capped at 30 years) using resolved EMI and compounding to determine exactly when the loan will be fully paid off. |

## 5. Projection Curves and Intelligence Metrics

### Curves Generated

| Curve | Description |
|---|---|
| Ideal | Simulates the original loan from disbursal with no deviations — pure scheduled EMI only. If `emi_amount` is missing, resolves the EMI dynamically (from `maturity_date` or elapsed repayments). |
| Actual (Historical) | Month-by-month actual balances from the simulation engine. |
| Projected (Future) | Continuation from today's balance using compounding-aware logic with resolved/fallback EMI until the balance reaches zero. Capped at 30 years or negative amortization checks. |

### Intelligence Metrics

| Metric | Description |
|---|---|
| `ideal_tenure_months` | Number of months the loan would have taken with zero deviations (resolved EMI if none configured). |
| `remaining_tenure_months` | Number of months until full payoff based on today's balance and resolved EMI. Calculated on backend via step-by-step projection simulation; returns `null` if negative amortization occurs. |
| `tenure_saved_months` | `ideal_tenure - (elapsed + remaining)`. Negative means tenure extension. |
| `total_interest_ideal` | Total interest that would have accrued under the ideal schedule. |
| `total_interest_projected` | Historical accumulated interest + projected future interest. |
| `interest_saved` | `total_interest_ideal - total_interest_projected`. Negative means net additional cost. |
| `ideal_end_date` | Date when the loan would have ended under ideal schedule. |
| `projected_end_date` | Date when the loan will end based on current trajectory. |

### Missed Payment Modeling

When no `REPAY` or `REVALUE` is logged for a month, the simulation auto-applies the scheduled EMI. This means:

- Balance reduces as if the payment was made on time.
- If the user subsequently records a `REVALUE` from their bank statement, the correct real-world balance (which may be higher due to missed EMIs) is reconciled automatically.
- The difference between the expected-simulated balance and the REVALUE amount is attributed to implied interest charges.

## 6. Database Schema

### `liability_category`

| Column | Type | Notes |
|---|---|---|
| `id` | String (UUID) | Primary key |
| `name` | String | Display name |
| `code` | String | Unique uppercase identifier |
| `description` | String (nullable) | |
| `created_at` / `updated_at` | DateTime (tz-aware) | Audit timestamps |

### `liability_subcategory`

| Column | Type | Notes |
|---|---|---|
| `id` | String (UUID) | Primary key |
| `category_id` | String (FK) | References `liability_category.id`, CASCADE delete |
| `name` | String | Display name |
| `code` | String | Unique uppercase identifier |
| `description` | String (nullable) | |
| `valuation_type` | String | `VALUE_BASED` (all liabilities are value-based) |
| `has_interest` | Boolean | EMI and interest rate applicable flag |
| `has_maturity` | Boolean | Maturity date required flag |
| `created_at` / `updated_at` | DateTime (tz-aware) | Audit timestamps |

### `liability`

| Column | Type | Notes |
|---|---|---|
| `id` | String (UUID) | Primary key |
| `category_id` | String (FK) | References `liability_category.id` |
| `subcategory_id` | String (FK, nullable) | References `liability_subcategory.id` |
| `name` | String | Loan or liability name |
| `original_value` | Float | Cached sum of all BORROW amounts |
| `current_value` | Float | Cached outstanding balance as of today |
| `interest_rate` | Float (nullable) | Annual interest rate % |
| `interest_compounding` | String (nullable) | `MONTHLY`, `QUARTERLY`, `HALF_YEARLY`, `YEARLY` |
| `emi_amount` | Float (nullable) | Scheduled monthly EMI |
| `emi_start_date` | DateTime (tz-aware, nullable) | Date when repayments/EMIs officially begin |
| `maturity_date` | DateTime (tz-aware, nullable) | Contracted end date if applicable |
| `notes` | String (nullable) | Free text notes |
| `created_at` / `updated_at` | DateTime (tz-aware) | Audit timestamps |

### `liability_transaction`

| Column | Type | Notes |
|---|---|---|
| `id` | String (UUID) | Primary key |
| `liability_id` | String (FK) | References `liability.id`, CASCADE delete |
| `transaction_type` | Enum | `BORROW`, `REPAY`, `REVALUE` |
| `amount` | Float | Amount in INR |
| `transaction_date` | DateTime (tz-aware) | Date of the event (may be backdated for delayed entry) |
| `description` | String (nullable) | Optional description |
| `created_at` | DateTime (tz-aware) | Audit timestamp |

## 7. Recalculation Trigger

Whenever a transaction is added or deleted on a liability, the parent `liability` entity's cached fields (`original_value`, `current_value`) are recalculated in full from the complete transaction ledger.

## 8. UI Interaction Requirements

### Add Liability Wizard

- **Step 1:** Category and subcategory selection.
- **Step 2:** Core fields — name, loan amount, start date (used as the BORROW transaction date for backdated entry).
- **Step 3:** Interest details (only for subcategories with `has_interest = true`) — interest rate, compounding frequency, EMI amount, EMI start date, maturity date.

### Dashboard Display (per Liability)

- Current outstanding balance, original loan amount, repayment progress %.
- EMI amount, disbursal date, EMI start date, projected end date.
- Accumulated interest paid, total repaid.
- Pending EMIs / remaining tenure.

### Projections Graph

- Dual Y-axis chart: principal balance (left axis, INR), cumulative interest (right axis, INR).
- Three data series: Ideal balance, Actual/Projected balance, Ideal interest, Actual/Projected interest.
- Months with REVALUE data shown as authoritative anchor points on the actual curve.

### Transaction Log

A dedicated slide-out dialog for logging BORROW, REPAY, and REVALUE events with a date picker that supports any past date.
