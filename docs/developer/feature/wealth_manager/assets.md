# System Requirements Document: Wealth Manager — Assets

This document defines the functional requirements, data model, and recalculation rules for the **Wealth Manager - Assets** module. For formula details see `calculations.md`. For end-user guidance see `docs/user/wealth-manager-guide.md`.

## 1. Product Goals

- Enable users to track all financial assets in one place with full transaction history.
- Support both flat-balance and quantity-based asset types under a single unified ledger model.
- Back all current values with auditable transactions (buys, sells, revaluations).
- Maintain clean separation of concerns so liabilities and net worth tracking can be added incrementally.

## 2. Supported Categories and Subcategories

Assets are organized under pre-seeded top-level categories and detailed subcategories.

### Categories

| Code | Name | Description |
| --- | --- | --- |
| `EQUITY` | Equity | Stocks, Mutual Funds, ETFs, NPS Equity |
| `DEBT` | Debt | Fixed Deposits, PPF, Bonds, EPF |
| `REAL_ESTATE` | Real Estate | Land, residential/commercial properties, REITs |
| `COMMODITIES` | Commodities | Physical Gold, Digital Gold, Silver, SGBs |
| `CASH_BANK` | Cash / Bank | Savings accounts, cash in hand |

### Subcategory Configuration

Each subcategory defines the operational rules for its assets:

| Field | Type | Purpose |
| --- | --- | --- |
| `valuation_type` | Enum | `VALUE_BASED` or `UNIT_BASED` — drives the recalculation path |
| `has_interest` | Boolean | Whether interest rate and compounding apply |
| `has_maturity` | Boolean | Whether a maturity date is required |

## 3. Valuation Types

### VALUE_BASED (Flat / Balance Assets)

Represents account balances where value is a direct INR amount (e.g., Bank Savings, PPF, Fixed Deposit).

- Invested value = sum of BUY amounts minus sum of SELL amounts.
- Current value = amount of the latest `REVALUE` transaction. Defaults to invested value if no REVALUE exists.

### UNIT_BASED (Quantity / Market Assets)

Represents investments tracked by units held (e.g., Stocks, Mutual Funds, Gold in grams).

- Units held = sum of BUY units minus sum of SELL units.
- Invested value = sum of (BUY units × price per unit) minus sum of (SELL units × price per unit).
- Current value = units held × current price per unit, where the price is resolved in priority order:
  1. Live price from the `PriceResolverService` using the asset name or subcategory code.
  2. Most recent price per unit from a `BUY` or `REVALUE` transaction if no live price is available.

## 4. Transaction Types

| Type | Applies To | Effect |
| --- | --- | --- |
| `BUY` | All | Increases invested value and units held |
| `SELL` | All | Decreases invested value and units held |
| `REVALUE` | All | Sets the current market value without changing invested cost |

## 5. Database Schema

### `asset_category`

| Column | Type | Notes |
| --- | --- | --- |
| `id` | String (UUID) | Primary key |
| `name` | String | Display name |
| `code` | String | Unique uppercase identifier |
| `description` | String | Nullable |
| `created_at` / `updated_at` | DateTime (tz-aware) | Audit timestamps |

### `asset_subcategory`

| Column | Type | Notes |
| --- | --- | --- |
| `id` | String (UUID) | Primary key |
| `category_id` | String (FK) | References `asset_category.id`, CASCADE delete |
| `name` | String | Display name |
| `code` | String | Unique uppercase identifier |
| `description` | String | Detailed valuation rules description |
| `valuation_type` | Enum | `UNIT_BASED` or `VALUE_BASED` |
| `has_interest` | Boolean | Interest rate / compounding flag |
| `has_maturity` | Boolean | Maturity date required flag |
| `created_at` / `updated_at` | DateTime (tz-aware) | Audit timestamps |

### `asset`

| Column | Type | Notes |
| --- | --- | --- |
| `id` | String (UUID) | Primary key |
| `category_id` | String (FK) | References `asset_category.id`, RESTRICT delete |
| `subcategory_id` | String (FK, nullable) | References `asset_subcategory.id`, RESTRICT delete |
| `name` | String | Asset name |
| `invested_value` | Float | Cached total invested cost in INR |
| `current_value` | Float | Cached current valuation in INR |
| `interest_rate` | Float (nullable) | Annual interest rate % |
| `interest_compounding` | String (nullable) | Compounding frequency: `MONTHLY`, `QUARTERLY`, `HALF_YEARLY`, `YEARLY` |
| `maturity_date` | DateTime (tz-aware, nullable) | Maturity date if applicable |
| `notes` | String (nullable) | Free text notes |
| `created_at` / `updated_at` | DateTime (tz-aware) | Audit timestamps |

### `asset_transaction`

| Column | Type | Notes |
| --- | --- | --- |
| `id` | String (UUID) | Primary key |
| `asset_id` | String (FK) | References `asset.id`, CASCADE delete |
| `transaction_type` | Enum | `BUY`, `SELL`, `REVALUE` |
| `amount` | Float | Cash flow value in INR |
| `units` | Float (nullable) | Quantity / weight for unit-based assets |
| `price_per_unit` | Float (nullable) | Price / NAV / rate per unit |
| `transaction_date` | DateTime (tz-aware) | Date of the transaction |
| `description` | String (nullable) | Optional description |
| `created_at` | DateTime (tz-aware) | Audit timestamp |

## 6. Recalculation Trigger

Whenever a transaction is added, edited, or deleted on an asset, the parent `asset` entity's cached fields (`invested_value`, `current_value`) are recalculated in full from the complete transaction ledger to ensure consistency.

## 7. UI Interaction Requirements

### Add / Edit Asset Wizard

- **Step 1:** Category and subcategory selection. Dynamic type-specific instructions surface from the subcategory model.
- **Step 2:** Dynamic form fields based on subcategory type:
  - Unit-based: `Units` and `Price per Unit` inputs. Invested amount is auto-calculated.
  - Interest-bearing: `Interest Rate` and `Compounding Frequency` inputs.
  - Maturity-based: Optional `Maturity Date` input.
- **Transaction Log:** A dedicated slide-out dialog for logging new events (`BUY`, `SELL`, `REVALUE`), keeping the main asset list uncluttered.
- **Bulk Entry:** "Save & Add Another" button for rapid sequential data entry.

### Theme and Display Standards

- Primary theme: Sapphire / Deep Blue (`#1e5067`) + Sky Blue (`#108cc6`).
- Typography: `Space Grotesk` for numeric metrics and titles, `DM Sans` for body text.
- All monetary values displayed in Indian Rupees with standard comma grouping (e.g., `₹12,50,000.00`).
