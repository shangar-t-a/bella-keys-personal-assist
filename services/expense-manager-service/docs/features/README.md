---
id: ems-features-index
title: Expense Manager Service Features
sidebar_position: 1
---

# Expense Manager Service Features

This documentation covers the core features of the Expense Manager Service (EMS), a backend utility in the Bella Keys ecosystem that handles financial transactions, accounts, and budget allocations.

The guides in this section map to the capabilities and tabs visible in the user interface.

---

## Core Features

### 1. Savings Buckets & Allocations
Manage sub-savings goals within accounts. Allocate, deposit, and refund money using an audited ledger system.
* **Guide:** [Savings Buckets & Allocations](./savings-bucket.md)
* **Key Scenarios:** Auto-refunds on deletion, root account protection, transaction ledgers.

### 2. Accounting Periods (Coming Soon)
Track financial transactions within discrete monthly or custom periods.
* **Key Scenarios:** Opening balances, period closing locks, active period switches.

### 3. Spending Entries & Ledger (Coming Soon)
Transaction log for daily expenses and income. Supports server-side sorting, filtering, and pagination.
* **Key Scenarios:** Multi-column sorting, pagination boundary checks, category joins.

### 4. Monthly Planner & Dashboard (Coming Soon)
Dashboard displaying summaries, target allocations, and category-wise spending charts.
* **Key Scenarios:** Budget vs. Actual comparisons, monthly rollover calculations.

---

## Design and Extensibility
All feature guides in this directory follow Docusaurus Markdown standards, containing Mermaid diagrams for state transitions and entity structures. They are located inside the microservice directory to maintain separation of concerns.

