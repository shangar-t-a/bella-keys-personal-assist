---
id: savings-bucket
title: Savings Buckets & Allocations
sidebar_position: 2
---

# Savings Buckets & Allocations

The Savings Bucket module manages goal-based sub-allocations of funds within an account.

## Concepts

* **Savings Bucket:** A virtual pool of money within a primary account.
* **Root Bucket (`Savings`):** The default bucket in every account holding unallocated general funds.
* **Sub-Buckets:** Custom allocations (e.g., Emergency Fund) for specific saving goals.
* **Transactions:** State changes (allocation, deposit, release) recorded in an append-only ledger.

---

## Design and Fund Flows

### Fund Allocation
Transferring funds from the root `Savings` bucket to a sub-bucket checks balance requirements and logs the allocation.

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant Service as SavingsBucketService
    participant DB as PostgreSQL Database

    User->>Service: Allocate funds from Savings to Sub-Bucket
    Service->>DB: Fetch source & destination buckets
    DB-->>Service: Return bucket states
    Note over Service: Validate: source balance >= allocation amount
    Service->>DB: Deduct amount from Savings
    Service->>DB: Add amount to Sub-Bucket
    Service->>DB: Log transaction (type: 'allocate')
    DB-->>Service: Commit transaction
    Service-->>User: Allocation successful
```

---

### Safe Deletion & Auto-Refund
Deleting a sub-bucket automatically refunds its remaining balance back to the root `Savings` bucket.

```mermaid
stateDiagram-v2
    [*] --> DeletionRequested : Delete bucket
    DeletionRequested --> CheckBalance : Inspect bucket.allocated_amount
    
    state CheckBalance {
        [*] --> Compare
        Compare --> HasFunds : amount > 0.0
        Compare --> Empty : amount == 0.0
    }

    HasFunds --> FindSavingsBucket : Retrieve root 'Savings' bucket
    FindSavingsBucket --> TransferFunds : Refund balance to root Savings
    TransferFunds --> LogCompensatingTx : Log 'release' transaction
    LogCompensatingTx --> DeleteRecord : Remove bucket
    
    Empty --> DeleteRecord : Remove bucket
    DeleteRecord --> [*] : Complete
```

---

### Transaction Cancellation
Ledger entries can be cancelled by specifying a cancellation reason. Cancelling reverses the adjustments. If target sub-buckets are deleted, it falls back to the root `Savings` bucket.

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant Service as SavingsBucketService
    participant DB as PostgreSQL Database

    User->>Service: Cancel transaction (ID, reason)
    Service->>DB: Fetch original transaction
    DB-->>Service: Return transaction details
    Note over Service: Validate: transaction not already cancelled
    Service->>DB: Fetch source & destination buckets
    DB-->>Service: Return bucket states
    Note over Service: Validate: destination balance >= transaction amount (if destination exists)
    Service->>DB: Deduct amount from destination bucket (or root Savings if deleted)
    Service->>DB: Add amount to source bucket (or root Savings if deleted)
    Service->>DB: Update transaction: set is_cancelled = True, cancellation_reason = reason
    DB-->>Service: Commit transaction
    Service-->>User: Cancellation successful
```

---

## Business Invariants

1. **Root Protection:** The primary `Savings` bucket cannot be renamed or deleted.
2. **Transaction Immutability:** Posted transactions cannot be edited or deleted. Reversals must be executed via cancellation.
3. **Balance Validation:** Allocations exceeding the source balance raise an `InsufficientFunds` error and trigger a rollback.
4. **Cross-Account Isolation:** Transactions cannot move funds between buckets belonging to different accounts.
