---
id: savings-bucket
title: Savings Buckets & Allocations
sidebar_position: 2
---

# Savings Buckets & Allocations

The Savings Bucket module manages goal-based sub-allocations of funds within an account. It supports allocating, depositing, and releasing money while maintaining an audited transaction ledger.

---

## Concepts

* **Savings Bucket**: A virtual pool of money within a primary account.
* **Root Bucket (`Savings`)**: The default bucket in every account. It holds all unallocated general funds.
* **Sub-Buckets**: Custom allocations (e.g., `Emergency Fund`, `LIC`) for specific saving goals.
* **Transactions**: State changes (allocation, deposit, release) are recorded in an append-only ledger.

---

## Design and Fund Flows

### 1. Account & Bucket Hierarchy
Each account owns one or more buckets, with the `Savings` bucket acting as the root pool.

```mermaid
classDiagram
    class Account {
        +String id
        +String name
        +Float balance
    }
    class SavingsBucket {
        +String id
        +String account_id
        +String name
        +Float allocated_amount
        +Float target_amount
    }
    class SavingsBucketTransaction {
        +String id
        +String account_id
        +String source_bucket_id
        +String destination_bucket_id
        +Float amount
        +String transaction_type
        +String description
        +DateTime transaction_date
    }

    Account "1" --> "many" SavingsBucket : owns
    SavingsBucket "1" --> "many" SavingsBucketTransaction : participates
```

---

### 2. Fund Allocation Sequence
When transferring funds from the root `Savings` bucket to a sub-bucket, the service checks balance requirements and records the transaction atomically.

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant Service as SavingsBucketService
    participant DB as PostgreSQL Database

    User->>Service: Allocate funds from Savings to LIC
    Service->>DB: Fetch source & destination buckets
    DB-->>Service: Return bucket states
    Note over Service: Validate: source balance >= allocation amount
    Service->>DB: Deduct amount from Savings
    Service->>DB: Add amount to LIC
    Service->>DB: Log transaction (type: 'allocate')
    DB-->>Service: Commit transaction
    Service-->>User: Allocation successful
```

---

### 3. Safe Deletion & Auto-Refund
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

## Business Rules & Invariants

1. **Root Protection**: The primary `Savings` bucket cannot be renamed or deleted.
2. **Transaction Immutability**: Posted transactions are append-only. There is no edit or delete capability for transaction records.
3. **Double Spend Guard**: Balance modifications are atomic. Allocations exceeding the source bucket balance raise an `InsufficientFunds` error and trigger a rollback.
4. **Cross-Account Isolation**: Transactions cannot move funds between buckets belonging to different accounts.

