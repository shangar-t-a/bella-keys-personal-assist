# Product Requirements & Design Document (PRD): Wealth Manager - Assets

This document outlines the product requirements, technical design, and architectural specifications for the **Wealth Manager - Assets** module of the personal assistant application.

---

## 1. Product Goals

* **Personal Net Worth Tracking:** Enable users to view, manage, and track all their financial assets in one place.
* **Premium User Experience:** Transition from basic, toy-like interfaces to a modern, high-end, blue-themed UI featuring clean typography, dynamic status chips, and smooth micro-animations.
* **Accuracy & Auditability:** Back all asset values with a transaction ledger to support full historical analysis (buys, sells, revaluations).
* **Scalability & Clean Architecture:** Maintain strict separation of concerns to allow easy integration of liabilities, historical net worth tracking, and portfolio allocation charts in later phases.

---

## 2. Requirements Specifications

### Currency & Scope
* The application runs strictly in Indian Rupees (INR) format (`₹XX,XX,XXX.XX`).
* The initial phase focuses exclusively on **Assets**.

### Supported Categories & Subcategories
Default pre-seeded categories in the database:
1. **EQUITY**: Equity assets (e.g., Stocks, Mutual Funds, ETFs, NPS Equity).
2. **DEBT**: Debt assets (e.g., Fixed Deposits, PPF, Bonds, EPF).
3. **REAL_ESTATE**: Real estate property (e.g., land, residential/commercial properties, REITs).
4. **COMMODITIES**: Commodity holdings (e.g., Physical Gold, Digital Gold, Silver, SGBs).
5. **CASH_BANK**: Liquid cash (e.g., Savings accounts, cash in hand).

Each asset is linked to a top-level **Category** and a specialized **Subcategory**. The subcategory dynamically determines the valuation model, interest parameters, and maturity properties.

### Asset Valuations
Assets are divided into two operational valuation types:
1. **Value-based / Flat Assets (`VALUE_BASED`):** Represents flat-balance accounts (e.g. Bank Savings, PPF). Valuations are updated directly or via basic adjustment transactions.
2. **Unit-based / Quantity Assets (`UNIT_BASED`):** Represents investments tracked by quantity (e.g. Gold in grams, Mutual Funds/Stocks in shares). Valuations are computed dynamically as:
   $$\text{Current Value} = \text{Units Held} \times \text{Price per Unit}$$

---

## 3. Database Schema

The database layout consists of four PostgreSQL tables:

### `asset_category`
Stores the top-level categories.
* `id` (String, Primary Key, UUID)
* `name` (String, e.g., "Equity", "Debt", "Real Estate", "Commodities", "Cash / Bank")
* `code` (String, unique uppercase identifier, e.g., "EQUITY", "DEBT", "REAL_ESTATE", "COMMODITIES", "CASH_BANK")
* `description` (String, nullable)
* `created_at` / `updated_at` (DateTime, timezone-aware)

### `asset_subcategory`
Lookup table for subcategories and their configuration.
* `id` (String, Primary Key, UUID)
* `category_id` (String, ForeignKey to `asset_category.id`, ondelete="CASCADE")
* `name` (String, e.g., "Stock", "Fixed Deposit", "PPF", "Physical Gold / Silver")
* `code` (String, unique uppercase identifier, e.g., "STOCK", "PPF", "FIXED_DEPOSIT", "PHYSICAL_GOLD_SILVER")
* `description` (String, detailed text describing valuation rules and transaction flows)
* `valuation_type` (String, Enum: `UNIT_BASED`, `VALUE_BASED`)
* `has_interest` (Boolean, indicates if interest rate and compounding apply)
* `has_maturity` (Boolean, indicates if maturity date inputs are required)
* `created_at` / `updated_at` (DateTime, timezone-aware)

### `asset`
Tracks assets generally. Has no type-specific or hardcoded columns.
* `id` (String, Primary Key, UUID)
* `category_id` (String, ForeignKey to `asset_category.id`, ondelete="RESTRICT")
* `subcategory_id` (String, ForeignKey to `asset_subcategory.id`, ondelete="RESTRICT", nullable=True)
* `name` (String, indexable asset name)
* `invested_value` (Float, cached total invested cost in INR)
* `current_value` (Float, cached current valuation in INR)
* `interest_rate` (Float, nullable, cached annual interest rate %)
* `interest_compounding` (String, nullable, compounding frequency)
* `maturity_date` (DateTime, timezone-aware, nullable)
* `notes` (String, nullable)
* `created_at` / `updated_at` (DateTime, timezone-aware)

### `asset_transaction`
Maintains buy, sell, or valuation history.
* `id` (String, Primary Key, UUID)
* `asset_id` (String, ForeignKey to `asset.id`, ondelete="CASCADE")
* `transaction_type` (String, Enum: `BUY`, `SELL`, `REVALUE`)
* `amount` (Float, cash flow value in INR)
* `units` (Float, nullable, quantity/weight details for unit-based assets)
* `price_per_unit` (Float, nullable, price/NAV/rate details)
* `transaction_date` (DateTime, timezone-aware)
* `description` (String, nullable)
* `created_at` (DateTime, timezone-aware)

---

## 4. Recalculation Rules

To ensure consistency, whenever a transaction is added, edited, or deleted, the parent `asset` entity's cached fields are updated:

### 1. Value-based / Flat-Value Asset
* **Invested Value**: $\text{invested\_value} = \max\left(0.0, \sum (\text{amount of BUY}) - \sum (\text{amount of SELL})\right)$
* **Current Value**: Resolved from the latest `REVALUE` transaction amount. If no `REVALUE` transactions exist, it defaults to `invested_value`.

### 2. Unit-based / Quantity Asset
* **Total Units**: $\text{total\_units} = \max\left(0.0, \sum (\text{units of BUY}) - \sum (\text{units of SELL})\right)$
* **Invested Value**: Calculated chronologically:
  $$\text{invested\_value} = \max\left(0.0, \sum_{t \in \text{BUY}} (\text{units}_t \times \text{price\_per\_unit}_t) - \sum_{t \in \text{SELL}} (\text{units}_t \times \text{price\_per\_unit}_t)\right)$$
* **Current Value**: $\text{current\_value} = \text{total\_units} \times \text{price\_per\_unit}$
  The `price_per_unit` is resolved using the following order of preference:
  1. Live price from the `PriceResolverService` using the asset name or subcategory code.
  2. The most recent price_per_unit from `BUY` or `REVALUE` transactions if no live price can be resolved.

---

## 5. UI Layout & Design Parameters

### Theme & Styling Parameters
* **Primary Theme:** Sapphire / Deep Blue (`#1e5067`) and Sky Blue (`#108cc6`).
* **Layout Styling:** Premium, tight, ruled standard layout utilizing thin gridlines and borders. Accordion headers summarize totals per category. Heavy margins, floating cards/shadows, and unnecessary whitespace are avoided.
* **Typography:** `Space Grotesk` (clean geometric font for numeric metrics and titles) + `DM Sans` (body text).
* **Currency Display:** All values formatted strictly in Indian Rupees (INR) with standard comma grouping (e.g., `₹XX,XX,XXX.XX`).

### Add / Edit Asset Wizard Form Workflows
* **Step 1: Category & Subcategory Selection**: Choose category and subcategory. The form displays dynamic type-specific instructions and warnings fetched directly from the subcategory model.
* **Step 2: Dynamic Form Fields**:
  * **Unit-based Assets**: Inputs for `Units` and `Price per Unit`. Invested amount is auto-calculated.
  * **Interest-bearing Assets**: Inputs for `Interest Rate` and `Compounding Frequency` (StrEnum: `MONTHLY`, `QUARTERLY`, `HALF_YEARLY`, `YEARLY`).
  * **Maturity-based Assets**: Option to specify a `Maturity Date`.
* **Transaction Log Menu**: A dedicated slide-out dialog to log new events (`BUY`, `SELL`, `REVALUE`), keeping the main asset list clean, dense, and focused.
* Includes "Save" and "Save & Add Another" buttons for rapid data entry.
