# Wealth Manager: Calculations Reference

This document provides a precise reference of all financial formulas, recalculation logic, and amortization models used in the Wealth Manager module.

For system requirements and schema, see `assets.md` and `liabilities.md`.
For end-user explanations of what each value means, see `docs/user/wealth-manager-guide.md`.

## 1. Asset Valuations

### Value-Based Assets (`VALUE_BASED`)

Flat-balance accounts where value is a direct INR amount (e.g., Bank Savings, PPF).

**Invested Value ($V_{\text{invested}}$):**
$$V_{\text{invested}} = \max\left(0.0,\ \sum \text{Amount}_{\text{BUY}} - \sum \text{Amount}_{\text{SELL}}\right)$$

**Current Value ($V_{\text{current}}$):**
$$V_{\text{current}} = \begin{cases} V_{\text{latest\_revalue}} + \sum_{t > t_{\text{reval}}} \text{Amount}_{\text{BUY}, t} - \sum_{t > t_{\text{reval}}} \text{Amount}_{\text{SELL}, t} & \text{if any REVALUE exists} \\ V_{\text{invested}} & \text{otherwise} \end{cases}$$

### Unit-Based Assets (`UNIT_BASED`)

Investments tracked by quantity (e.g., Stocks, Mutual Funds, Physical Gold).

**Units Held ($U_{\text{held}}$):**
$$U_{\text{held}} = \max\left(0.0,\ \sum \text{Units}_{\text{BUY}} - \sum \text{Units}_{\text{SELL}}\right)$$

**Invested Value ($V_{\text{invested}}$):**
$$V_{\text{invested}} = \max\left(0.0,\ \sum_{t \in \text{BUY}} (\text{Units}_t \times P_t) - \sum_{t \in \text{SELL}} (\text{Units}_t \times P_t)\right)$$

**Current Value ($V_{\text{current}}$):**
$$V_{\text{current}} = U_{\text{held}} \times P_{\text{current}}$$

Where $P_{\text{current}}$ is resolved in priority order:

1. Live price from `PriceResolverService`.
2. Most recent price per unit from a `BUY` or `REVALUE` transaction.

---

## 2. Liability Simulation Engine

All outstanding balance calculations share a single simulation engine (`_simulate_amortization`), which tracks Principal ($P_m$) and Accrued Interest ($I_{\text{acc}, m}$) separately to support compounding frequencies.

### Parameters

| Symbol | Meaning |
|---|---|
| $P_m$ | Principal balance at the close of month $m$ |
| $I_{\text{acc}, m}$ | Accrued uncompounded interest at the close of month $m$ |
| $r$ | Annual nominal interest rate (e.g., $0.1195$ for $11.95\%$) |
| $i$ | Monthly interest rate: $i = r / 12$ |
| $M$ | Scheduled monthly EMI amount (if configured, else resolved dynamically) |
| $d_{\text{emi}}$ | Optional date when repayments/EMIs officially begin |
| $C$ | Compounding frequency interval in months (Monthly = 1, Quarterly = 3, Half-Yearly = 6, Yearly = 12) |

### Month 0 — Disbursal

$$P_0 = \sum \text{BORROW}_{\text{month 0}} - \max\left(0,\ \sum \text{REPAY}_{\text{month 0}}\right)$$
$$I_{\text{acc}, 0} = 0.0$$

If a REVALUE exists in month 0:
$$P_0 = \text{REVALUE}_{\text{amount}},\quad I_{\text{acc}, 0} = 0.0,\quad I_{\text{implied}, 0} = \max\left(0,\ \text{REVALUE} - P_0^{\text{pre-reval}}\right)$$

### Months 1 to N — Normal Month (no REVALUE)

1. **Accrue Interest**:
   $$I_m = P_{m-1} \times i$$
   $$I_{\text{acc}, m}^{\text{pre}} = I_{\text{acc}, m-1} + I_m$$

2. **Determine Scheduled Auto-EMI**:
   $$\text{auto\_emi}_m = \begin{cases} 0.0 & \text{if } d_{\text{emi}} \text{ is set and month } m < d_{\text{emi}} \\ \min(M,\ P_{m-1} + I_{\text{acc}, m}^{\text{pre}}) & \text{otherwise} \end{cases}$$

3. **Repayment Application** (applied to accrued interest first, then principal):
   $$\text{total\_payment}_m = \text{auto\_emi}_m + \text{REPAY}_m$$
   $$B_m = \text{BORROW}_m$$

   If $\text{total\_payment}_m \le I_{\text{acc}, m}^{\text{pre}}$:
   $$I_{\text{acc}, m}^{\text{post}} = I_{\text{acc}, m}^{\text{pre}} - \text{total\_payment}_m$$
   $$P_m^{\text{pre-comp}} = P_{m-1} + B_m$$

   If $\text{total\_payment}_m > I_{\text{acc}, m}^{\text{pre}}$:
   $$\text{rem\_payment}_m = \text{total\_payment}_m - I_{\text{acc}, m}^{\text{pre}}$$
   $$I_{\text{acc}, m}^{\text{post}} = 0.0$$
   $$P_m^{\text{pre-comp}} = \max\left(0.0,\ P_{m-1} + B_m - \text{rem\_payment}_m\right)$$

4. **Periodic Compounding**:
   If month index $m$ is a multiple of compounding interval $C$ ($m \pmod C == 0$):
   $$P_m = P_m^{\text{pre-comp}} + I_{\text{acc}, m}^{\text{post}}$$
   $$I_{\text{acc}, m} = 0.0$$

   Otherwise:
   $$P_m = P_m^{\text{pre-comp}}$$
   $$I_{\text{acc}, m} = I_{\text{acc}, m}^{\text{post}}$$

*Note: Total outstanding balance shown on the UI is $P_m + I_{\text{acc}, m}$.*

Cumulative interest: $\text{CumInt} \mathrel{+}= I_m$
Cumulative repaid: $\text{CumRepaid} \mathrel{+}= \text{total\_payment}_m$

### Months 1 to N — REVALUE Month

The bank's statement is the authoritative closing balance (compounding boundary). Scheduled EMI is **not** applied separately.

$$P_m = \text{REVALUE}_{\text{amount}}$$
$$I_{\text{acc}, m} = 0.0$$
$$I_{\text{implied}, m} = \max\left(0,\ \text{REVALUE} - (P_{m-1} + I_{\text{acc}, m-1} + \text{BORROW}_m - \text{REPAY}_m)\right)$$

Cumulative interest: $\text{CumInt} \mathrel{+}= I_{\text{implied}, m}$
Cumulative repaid: $\text{CumRepaid} \mathrel{+}= \text{REPAY}_m$ (manual repays only)

### Zero Balance Propagation

Once $P_m = 0$ and $I_{\text{acc}, m} = 0$, all subsequent months record $(0, \text{CumInt}, \text{CumRepaid})$ with no further accumulation.

---

## 3. Current Outstanding (Dashboard Values)

`calculate_current_outstanding` delegates to `_simulate_amortization` and returns the final snapshot.

$$L_{\text{current}} = P_{\text{today}} + I_{\text{acc}, \text{today}}$$
$$L_{\text{repaid}} = \text{CumRepaid}_{\text{today}}$$
$$L_{\text{interest}} = \text{CumInt}_{\text{today}}$$
$$P_{\text{progress}} = \text{clamp}\left(0,\ \left(1 - \frac{L_{\text{current}}}{L_{\text{original}}}\right) \times 100,\ 100\right)$$

**Interest-Free Liabilities** (no interest rate configured):

$$L_{\text{current}} = \max\left(0,\ L_{\text{original}} - L_{\text{repaid}}\right)$$

If a REVALUE exists, it resets the reference point:
$$L_{\text{current}} = \max\left(0,\ V_{\text{latest\_revalue}} + \sum_{t > t_{\text{reval}}} \text{BORROW}_t - \sum_{t > t_{\text{reval}}} \text{REPAY}_t\right)$$

---

## 4. Liability Projection Curves & Dynamic EMI

For loans where scheduled `emi_amount` is not configured, a dynamic EMI ($M$) is resolved:

1. **With Maturity Date ($d_{\text{maturity}}$)**: Calculates the mathematically ideal amortizing payment to clear disbursal balance by maturity at nominal interest rate:
   $$M = \frac{P \times i \times (1 + i)^n}{(1 + i)^n - 1}$$
   where $n$ is months between disbursal and maturity. If $i = 0$, $M = P / n$.
2. **Without Maturity Date**: Falls back to average past monthly repayments:
   $$M = \max\left(1000.0,\ \frac{L_{\text{repaid}}}{\text{elapsed\_months}}\right)$$
   If no repayments have occurred yet, defaults to a 5-year repayment schedule: $M = \max(1000.0, P / 60)$.

### A. Ideal Amortization Curve

Simulates from disbursal date using resolved/configured EMI, with no prepayments.
Calculations follow the compounding-aware simulation engine loop.

### B. Actual / Projected Curve

**Historical section (start → today):** Directly from `_simulate_amortization` snapshots.

**Future projection section (today → payoff):** Starts from $P_{\text{today}}$ and $I_{\text{acc}, \text{today}} = 0.0$, running the compounding-aware simulation loop with resolved/configured EMI $M$ until balance reaches zero (capped at 30 years).

- **Remaining tenure $K_{\text{projected}}$**: Count of months in future projection.

### C. Intelligence Metrics

$$T_{\text{saved}} = N_{\text{ideal}} - (M_{\text{elapsed}} + K_{\text{projected}})$$
$$I_{\text{projected}} = \text{CumInt}_{\text{today}} + \sum_{\text{future}} I_k$$
$$I_{\text{saved}} = I_{\text{ideal}} - I_{\text{projected}}$$

> $T_{\text{saved}} < 0$: Tenure extended (e.g., due to missed payments or penalties).
> $I_{\text{saved}} < 0$: Net additional interest cost incurred.

---

## 5. Deviation Modeling

### Missed Payment

When no `REPAY` or `REVALUE` is logged for a month, the simulation auto-applies the scheduled EMI. The outstanding balance decreases as if the payment was made. If the actual bank balance is higher (real missed payment), the next `REVALUE` will reconcile this difference, attributing the gap as implied interest.

### Late Fees and Penalties

Log as either:

- A `BORROW` transaction (increases principal), or
- A `REVALUE` transaction with a higher-than-expected balance.

Both correctly propagate to higher future interest accrual.

### Trajectory Shift

All projections start from the actual current balance. Any missed payments or penalties that increased the balance automatically extend the projected tenure and increase projected interest, making $T_{\text{saved}} < 0$ and $I_{\text{saved}} < 0$ when the user is behind schedule.
