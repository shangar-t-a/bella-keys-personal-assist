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
$$V_{\text{current}} = \begin{cases} \text{Amount of latest REVALUE} & \text{if any REVALUE exists} \\ V_{\text{invested}} & \text{otherwise} \end{cases}$$

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

All outstanding balance calculations share a single simulation engine (`_simulate_amortization`). This section documents its exact mathematical model.

### Parameters

| Symbol | Meaning |
|---|---|
| $P_m$ | Outstanding balance at the close of month $m$ |
| $r$ | Annual nominal interest rate (e.g., $0.1195$ for $11.95\%$) |
| $i$ | Monthly interest rate: $i = r / 12$ |
| $M$ | Scheduled monthly EMI amount |
| $d_{\text{emi}}$ | Optional date when repayments/EMIs officially begin |

### Month 0 — Disbursal

$$P_0 = \sum \text{BORROW}_{\text{month 0}} - \sum \text{REPAY}_{\text{month 0}}$$

If a REVALUE exists in month 0:
$$P_0 = \text{REVALUE}_{\text{amount}},\quad I_{\text{implied}, 0} = \max\left(0,\ \text{REVALUE} - P_0^{\text{pre-reval}}\right)$$

### Months 1 to N — Normal Month (no REVALUE)

$$I_m = P_{m-1} \times i$$
$$\text{auto\_emi}_m = \begin{cases} 0.0 & \text{if } d_{\text{emi}} \text{ is set and month } m < d_{\text{emi}} \\ \min(M,\ P_{m-1} + I_m) & \text{otherwise} \end{cases}$$
$$\text{total\_payment}_m = \text{auto\_emi}_m + \text{REPAY}_m$$
$$P_m = \max\left(0,\ P_{m-1} + I_m + \text{BORROW}_m - \text{total\_payment}_m\right)$$

Cumulative interest: $\text{CumInt} \mathrel{+}= I_m$
Cumulative repaid: $\text{CumRepaid} \mathrel{+}= \text{total\_payment}_m$

### Months 1 to N — REVALUE Month

The bank's statement is the authoritative closing balance. Scheduled EMI is **not** applied separately.

$$P_m = \text{REVALUE}_{\text{amount}}$$
$$I_{\text{implied}, m} = \max\left(0,\ \text{REVALUE} - (P_{m-1} + \text{BORROW}_m)\right)$$

Cumulative interest: $\text{CumInt} \mathrel{+}= I_{\text{implied}, m}$
Cumulative repaid: $\text{CumRepaid} \mathrel{+}= \text{REPAY}_m$ (manual repays only; EMI is already absorbed by REVALUE)

> Note: If $\text{REVALUE} < (P_{m-1} + \text{BORROW}_m)$, the bank has applied a net reduction (EMI and any extra payments reduced the balance). The implied interest is floored at 0 — no negative interest is recorded.

### Zero Balance Propagation

Once $P_m = 0$, all subsequent months record $(0, \text{CumInt}, \text{CumRepaid})$ with no further accumulation.

---

## 3. Current Outstanding (Dashboard Values)

`calculate_current_outstanding` delegates to `_simulate_amortization` and returns the final snapshot.

$$L_{\text{current}} = P_{\text{today}}$$
$$L_{\text{repaid}} = \text{CumRepaid}_{\text{today}}$$
$$L_{\text{interest}} = \text{CumInt}_{\text{today}}$$
$$P_{\text{progress}} = \text{clamp}\left(0,\ \left(1 - \frac{L_{\text{current}}}{L_{\text{original}}}\right) \times 100,\ 100\right)$$

**Non-EMI / Interest-Free Liabilities** (no interest rate or EMI configured):

$$L_{\text{current}} = \max\left(0,\ L_{\text{original}} - L_{\text{repaid}}\right)$$

If a REVALUE exists, it resets the reference point:
$$L_{\text{current}} = \max\left(0,\ V_{\text{latest\_revalue}} + \sum_{t > t_{\text{reval}}} \text{BORROW}_t - \sum_{t > t_{\text{reval}}} \text{REPAY}_t\right)$$

---

## 4. Liability Projection Curves

### A. Ideal Amortization Curve

Simulates from disbursal date with no deviations — pure scheduled EMI only.

For each month $n = 1, 2, \ldots$ until $P_n = 0$:
$$I_n = P_{n-1} \times i$$
$$\text{payment}_n = \begin{cases} 0.0 & \text{if } d_{\text{emi}} \text{ is set and month } n < d_{\text{emi}} \\ \min(M,\ P_{n-1} + I_n) & \text{otherwise} \end{cases}$$
$$P_n = \max\left(0,\ P_{n-1} + I_n - \text{payment}_n\right)$$

- **Ideal tenure $N_{\text{ideal}}$:** Total months until $P_n = 0$.
- **Total ideal interest $I_{\text{ideal}}$:** $\sum_{n=1}^{N_{\text{ideal}}} I_n$

### B. Actual / Projected Curve

**Historical section (start → today):** Directly from `_simulate_amortization` snapshots.

**Future projection section (today → payoff):** Starts from $P_{\text{today}}$, uses scheduled EMI only:

$$P_{\text{proj}, 0} = P_{\text{today}},\quad \text{CumInt}_{\text{proj}, 0} = \text{CumInt}_{\text{today}}$$

For each $k = 1, 2, \ldots$ until $P_{\text{proj}, k} = 0$:
$$I_k = P_{\text{proj}, k-1} \times i$$
$$\text{payment}_k = \begin{cases} 0.0 & \text{if } d_{\text{emi}} \text{ is set and future month } k < d_{\text{emi}} \\ \min(M,\ P_{\text{proj}, k-1} + I_k) & \text{otherwise} \end{cases}$$
$$P_{\text{proj}, k} = \max\left(0,\ P_{\text{proj}, k-1} + I_k - \text{payment}_k\right)$$
$$\text{CumInt}_{\text{proj}, k} = \text{CumInt}_{\text{proj}, k-1} + I_k$$

- **Remaining tenure $K_{\text{projected}}$:** Total future months until $P_{\text{proj}, k} = 0$.

### C. Intelligence Metrics

$$T_{\text{saved}} = N_{\text{ideal}} - (M_{\text{elapsed}} + K_{\text{projected}})$$
$$I_{\text{projected}} = \text{CumInt}_{\text{today}} + \sum_{k=1}^{K_{\text{projected}}} I_k$$
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
