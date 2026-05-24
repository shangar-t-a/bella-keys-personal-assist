---
id: monthly-planner
title: Monthly Planner & Dashboard
sidebar_position: 5
---

# Monthly Planner & Dashboard

The Monthly Planner helps users plan budgets, categorize expenses, and monitor monthly financial summaries.

## Concepts

* **Expense Item:** Individual planned or actual expenses containing an amount, category, and status (e.g., `PENDING` or `COMPLETED`).
* **Custom Categories:** Expense items are classified using structured, two-tier categories (L1 and L2 categories).
* **Summary:** Aggregated dashboard metrics showing total income, total planned expenses, and actual spent.

## Key Scenarios

### Syncing Recurring Expenses
To simplify monthly budgeting, users can copy recurring transactions from the previous month:
1. The service identifies the previous active period.
2. It fetches all expense items flagged as `is_recurring`.
3. Filters out items that already exist in the target month to prevent duplicates.
4. Atomically clones the recurring items into the current month.
