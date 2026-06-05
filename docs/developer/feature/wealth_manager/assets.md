# Product Requirements Document (PRD): Wealth Manager - Assets

This document outlines the product requirements and technical design for the **Wealth Manager - Assets** module of the personal assistant application.

---

## 1. Product Goals
* **Personal Net Worth Tracking:** Enable users to view, manage, and track all their financial assets in one place.
* **Premium User Experience:** Transition from basic, toy-like interfaces to a modern, high-end, blue-themed UI featuring glassmorphism, clean typography, and smooth micro-animations.
* **Accuracy & Auditability:** Back all asset values with a transaction ledger to support full historical analysis (buys, sells, revaluations).
* **Scalability & Clean Architecture:** Maintain strict separation of concerns to allow easy integration of liabilities, historical net worth tracking, and portfolio allocation charts in later phases.

---

## 2. Requirements Specifications

### Currency & Scope
* The application runs strictly in Indian Rupees (INR) format (`₹XX,XX,XXX.XX`).
* The initial phase focuses exclusively on **Assets**.

### Supported Categories
Default pre-seeded categories in the database:
1. **EQUITY**: Equity assets (e.g. Stocks, Mutual Funds, ETFs).
2. **DEBT**: Debt assets (e.g. Fixed Deposits, PPF, Bonds, EPF).
3. **REAL_ESTATE**: Real estate property (e.g. land, residential/commercial properties).
4. **COMMODITIES**: Commodity holdings (e.g. Physical Gold, Digital Gold, Silver).
5. **CASH_BANK**: Liquid cash (e.g. Savings accounts, cash in hand).

### Asset Valuations
Assets are divided into two operational types:
1. **Simple / Flat Assets:** Represents flat-balance accounts (e.g. Bank Savings, PPF). Valuations are updated directly or via basic adjustment transactions.
2. **Unit-based / Quantity Assets:** Represents investments tracked by quantity (e.g. Gold in grams, Mutual Funds/Stocks in shares). Valuations are computed dynamically as:
   $$\text{Current Value} = \text{Units Held} \times \text{Latest Price per Unit}$$

---

## 3. Database Schema

We define three Postgres tables:

### `asset_category`
Stores the top-level categories.
* `id` (String, Primary Key, UUID)
* `name` (String, e.g., "Equity", "Debt", "Real Estate", "Commodities", "Cash / Bank")
* `code` (String, unique uppercase identifier, e.g., "EQUITY", "DEBT", "REAL_ESTATE", "COMMODITIES", "CASH_BANK")
* `description` (String, nullable)
* `created_at` / `updated_at` (DateTime)

### `asset`
Tracks assets generally. Has no type-specific or hardcoded columns.
* `id` (String, Primary Key, UUID)
* `category_id` (String, ForeignKey to `asset_category.id`)
* `name` (String, e.g., "Gold Jewelry")
* `sub_category` (String, nullable, e.g. "Physical Gold", "PPF", "NPS", "Mutual Fund", "Stock")
* `invested_value` (Float, cached total invested cost in INR)
* `current_value` (Float, cached current valuation in INR)
* `notes` (String, nullable)
* `created_at` / `updated_at` (DateTime)

### `asset_transaction`
Maintains buy, sell, or valuation history.
* `id` (String, Primary Key, UUID)
* `asset_id` (String, ForeignKey to `asset.id`, ondelete="CASCADE")
* `transaction_type` (String, Enum: `BUY`, `SELL`, `REVALUE`)
* `amount` (Float, cash flow value in INR)
* `units` (Float, nullable, quantity/weight details)
* `price_per_unit` (Float, nullable, price/NAV/rate details)
* `transaction_date` (DateTime)
* `description` (String, nullable)
* `created_at` (DateTime)

---

## 4. Recalculation Rules

To ensure consistency, whenever a transaction is added, edited, or deleted, the parent `asset` entity's cached fields are updated:

### 1. Simple / Flat-Value Asset
* $\text{invested\_value} = \sum (\text{amount of BUY}) - \sum (\text{amount of SELL})$
* $\text{current\_value} = \text{amount of the latest REVALUE transaction}$ (if none exist, defaults to `invested_value`).

### 2. Unit-based Asset
* $\text{total\_units} = \sum (\text{units of BUY}) - \sum (\text{units of SELL})$
* $\text{invested\_value} = \sum (\text{units} \times \text{price\_per\_unit of BUY}) - \sum (\text{units} \times \text{price\_per\_unit of SELL})$
* $\text{current\_value} = \text{total\_units} \times \text{latest\_price\_per\_unit}$ (resolved from the most recent transaction of type `REVALUE` or `BUY`).

---

### Theme & Layout Parameters
* **Primary Theme:** Sapphire / Deep Blue (`#1e5067`) and Sky Blue (`#108cc6`).
* **Layout Styling:** Premium, tight, ruled standard layout utilizing thin gridlines and borders. Heavy margins, floating cards/shadows, and unnecessary whitespace are avoided in favor of a clean, structured list/grid.
* **Typography:** `Space Grotesk` (clean geometric font for numeric metrics and titles) + `DM Sans` (body text).

### Form Workflows
* **Step 1: Type Selection:** Choose Category (Equity, Debt, Real Estate, Commodities, Cash/Bank) and Sub-type (PPF, EPF, Gold, Stocks).
* **Step 2: Dynamic Form Fields:**
  * For commodities (Gold/Silver): Inputs for Purity (24K, 22K), Weight (grams), Price per gram. Invested amount is auto-calculated.
  * For PPF/Savings: Inputs for Name, Balance.
  * Note: The form runs strictly in INR; no currency selector or alternative classification box is displayed next to the Name.
  * Includes "Save" and "Save & Add Another" buttons for rapid data entry.
* **Transaction Log Menu:** A dedicated slide-out drawer or overlay modal to log events (e.g. buying more units, selling shares, or recording a new revaluation price), keeping the main table clean and focused.
