# System Requirements Document: Wealth Manager — Net Worth

This document defines the functional requirements, system architecture, and API endpoints for the **Wealth Manager - Net Worth** module. For calculation formulas see `calculations.md`. For end-user guidance see `docs/user/wealth-manager-guide.md`.

## 1. Product Goals

- Surface a high-level current portfolio valuation consisting of Current Net Worth, Total Assets, and Total Liabilities.
- Show historical portfolio trajectory over the last 12 months with composed area/line charts (Assets, Liabilities, Net Worth).
- Display a detailed Month-over-Month historical ledger with percentage changes.

## 2. API Endpoints

The Net Worth module is powered by the following FastAPI endpoints:

### GET `/v1/wealth/summary`

Returns a high-level summary of current portfolio values.

- **Response Schema:**
  - `totalAssets`: float (Current market value of all assets)
  - `totalInvestedAssets`: float (Total cost of assets purchased)
  - `totalReturnsAssets`: float (Absolute gains across assets)
  - `percentageReturnsAssets`: float (Asset ROI %)
  - `totalLiabilities`: float (Current outstanding liability balance)
  - `totalOriginalLiabilities`: float (Total principal borrowed)
  - `totalRepaidLiabilities`: float (Total repayments made)
  - `accumulatedInterestLiabilities`: float (Total interest accrued)
  - `netWorth`: float (`totalAssets - totalLiabilities`)

### GET `/v1/wealth/history?months=12`

Returns a chronological timeline of portfolio snapshots.

- **Response Schema:** List of:
  - `date`: string (Format: `YYYY-MM`)
  - `totalAssets`: float (Historical asset value at month-end)
  - `totalLiabilities`: float (Historical liability balance at month-end)
  - `netWorth`: float (Historical net worth at month-end)

## 3. UI Components & Layout (`NetWorthTab.tsx`)

- **Metric Summary Cards:** Renders three prominent cards (Current Net Worth, Total Assets, Total Liabilities) showing total values and MoM deltas.
- **Historical Portfolio Trajectory Composed Chart:** Uses Recharts `<ComposedChart>` to overlay:
  - `<Area>` for Total Assets (success color)
  - `<Area>` for Total Liabilities (error color)
  - `<Line>` for Net Worth (primary color)
- **Net Worth Ledger:** A sticky-header small table listing row entries chronologically descending, displaying monthly valuations and MoM changes.
