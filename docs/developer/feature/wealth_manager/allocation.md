# System Requirements Document: Wealth Manager — Allocation

This document defines the functional requirements, system architecture, and API endpoints for the **Wealth Manager - Allocation** module. For formula details see `calculations.md`. For end-user guidance see `docs/user/wealth-manager-guide.md`.

## 1. Product Goals

- Provide interactive portfolio asset and liability allocation breakdowns using donut charts.
- Visualize asset financing leverage (Equity vs Debt split bar).
- Document and surface key portfolio health ratios (Debt-to-Asset ratio, Portfolio Liquidity ratio) with safety warnings.
- Keep the frontend clean of calculations by relying entirely on the backend as the data and logic provider.

## 2. Supported Categories

Allocations are aggregated by category code:

- **Asset Categories:** `EQUITY`, `DEBT`, `REAL_ESTATE`, `COMMODITIES`, `CASH_BANK`.
- **Liability Categories:** `SECURED_LOAN`, `UNSECURED_LOAN`, `REVOLVING_CREDIT`, `OTHER`.

## 3. Data Flow & API Schema

Calculations are computed dynamically on the backend and exposed via:

### GET `/v1/wealth/allocation`

- **Response Fields:**
  - `assets`: List of Category Allocations
    - `categoryName`: string
    - `categoryCode`: string
    - `totalValue`: float
    - `percentage`: float
  - `liabilities`: List of Category Allocations
  - `totalAssetsValue`: float
  - `totalLiabilitiesValue`: float
  - `debtToAssetRatio`: float (Total liabilities / Total assets × 100)
  - `liquidityRatio`: float (Liquid assets [Equity + Cash/Bank] / Total assets × 100)
  - `equityFinancedPct`: float (Own wealth share of assets)
  - `liabilitiesFinancedPct`: float (Debt-financed share of assets)
  - `leverageStatusLabel`: string ("Low Risk (Healthy)", "Moderate Risk (Watch)", "High Risk (Leveraged)")
  - `leverageStatusType`: string (`SUCCESS`, `WARNING`, `ERROR`)
  - `liquidityStatusLabel`: string ("Healthy Liquidity", "Low Liquidity")
  - `liquidityStatusType`: string (`SUCCESS`, `WARNING`)

## 4. UI Components & Layout (`AllocationTab.tsx`)

- **Diversification donut charts:** Two `<PieChart>` components displaying categories for assets and liabilities.
- **Asset Financing Leverage Split Bar:** A 100% stacked bar showing the self-owned Equity share (primary color) vs borrowed Debt share (error color).
- **Health Metrics Cards:**
  - **Debt-to-Asset Ratio:** Renders a progress bar indicating leverage risk level based on the ratio.
  - **Portfolio Liquidity Ratio:** Renders a progress bar indicating liquid cash cushion health.
- **Informative Tooltips:** All financial headers and jargon labels render interactive hover tooltips explaining terms.
