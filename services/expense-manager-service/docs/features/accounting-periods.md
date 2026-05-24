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

## Flow and Lifecycle

### Automatic Period Creation
When a transaction is registered, the system resolves the target period:
1. Checks if a Period record exists for the given month and year.
2. If it does not exist, the service executes `get_or_create_period` to create it.
3. Associates the transaction with the Period's ID.

### Updates and Deletions
Periods can be modified or deleted via their respective endpoints. Deleting a Period will cascade and delete all associated transactions and summaries for that period.
