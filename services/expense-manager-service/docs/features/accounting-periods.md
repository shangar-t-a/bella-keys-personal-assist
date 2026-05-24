---
id: accounting-periods
title: Accounting Periods
sidebar_position: 3
---

# Accounting Periods

Accounting Periods isolate financial tracking records into discrete, monthly buckets.

## Concepts

* **Period:** A unique combination of a specific month and year (e.g., May 2026).
* **ID Isolation:** All transactions and budgets are associated with a `period_id` to ensure monthly isolation.

---

## Flow and Lifecycle

### Automatic Period Resolution
When transactions are registered, the system resolves the target period dynamically:

```mermaid
sequenceDiagram
    autonumber
    participant API as Transaction API
    participant Period as Period Service
    participant DB as PostgreSQL Database

    API->>Period: Get or Create Period (month, year)
    Period->>DB: Query Period by month and year
    alt Period Exists
        DB-->>Period: Return existing Period ID
    else Period Does Not Exist
        Period->>DB: Insert new Period record
        DB-->>Period: Return new Period ID
    end
    Period-->>API: Return Period ID
```

---

## Updates and Deletions
Periods can be modified or deleted via their respective endpoints. Deleting a Period cascades and removes all associated transactions and summaries for that period.
