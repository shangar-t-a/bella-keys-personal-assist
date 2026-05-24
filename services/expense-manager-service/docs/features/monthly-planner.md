---
id: monthly-planner
title: Monthly Planner & Dashboard
sidebar_position: 5
---

# Monthly Planner & Dashboard

The Monthly Planner helps users plan budgets, categorize expenses, and monitor monthly financial summaries.

## Concepts

* **Expense Item:** Individual planned or actual expenses containing an amount, category, and status (`PENDING` or `COMPLETED`).
* **Custom Categories:** Expense items are classified using structured, two-tier categories (L1 and L2 categories).
* **Summary:** Aggregated dashboard metrics showing total income, total planned expenses, and actual spent.

---

## Key Scenarios

### Syncing Recurring Expenses
To simplify monthly budgeting, users can copy recurring transactions from the previous month.

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant Service as MonthlyPlannerService
    participant DB as PostgreSQL Database

    User->>Service: Sync from previous month (current_period_id)
    Service->>DB: Fetch previous period ID
    Service->>DB: Fetch previous recurring expenses
    Service->>DB: Fetch current expenses (to avoid duplicates)
    Note over Service: Filter out items already in current month
    Service->>DB: Bulk insert new recurring items
    DB-->>Service: Commit transactions
    Service-->>User: Return current month expenses
```
