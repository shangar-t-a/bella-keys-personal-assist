---
id: spending-ledger
title: Spending Entries & Ledger
sidebar_position: 4
---

# Spending Entries & Ledger

The Spending Entries and Ledger module tracks transaction inputs, manages account balance calculations, and displays paginated logs.

## Concepts

* **Starting Balance:** The initial balance of the account at the start of the period.
* **Current Balance:** The remaining balance after all expenses.
* **Current Credit:** The total incoming funds or salary credited during the period.
* **Balance After Credit:** Calculated as `current_balance + current_credit`.
* **Total Spent:** Calculated as `starting_balance - current_balance`.

---

## DB-Level Pagination, Sorting, and Filtering

To ensure optimal performance and avoid loading massive datasets into memory, sorting, filtering, and pagination are executed directly in PostgreSQL.

```mermaid
sequenceDiagram
    autonumber
    actor UI as Desktop UI
    participant API as Spending API
    participant DB as PostgreSQL Database

    UI->>API: GET /spending_account/list?page=0&size=12&sort_by=year&account_name=Main
    API->>DB: Query with filters, ORDER BY, LIMIT 12 OFFSET 0
    DB-->>API: Return matched entries & total count
    API->>API: Calculate page metadata (total elements, pages)
    API-->>UI: Return PaginationResponse
```

### Pagination
List requests accept `page` (0-indexed) and `size` parameters. The service translates these into SQL `LIMIT` and `OFFSET` queries.

### Sorting
Transactions can be sorted by fields such as `month`, `year`, or `account_name` in either ascending (`asc`) or descending (`desc`) order.

### Filtering
Queries support filtering by account name, specific month, and specific year.
