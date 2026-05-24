export interface AccountNameRequest {
  accountName: string;
}

export interface AccountNameResponse {
  id: string;
  accountName: string;
}

export interface AccountUpdateRequest {
  accountName: string;
}

export interface PeriodRequest {
  month: number;
  year: number;
}

export interface PeriodResponse {
  id: string;
  month: number;
  year: number;
}

export interface SpendingAccountEntryRequest {
  accountName: string;
  month: number;
  year: number;
  startingBalance: number;
  currentBalance: number;
  currentCredit: number;
}

export interface SpendingAccountEntryWithCalculatedFieldsResponse {
  accountName: string;
  month: number;
  year: number;
  startingBalance: number;
  currentBalance: number;
  currentCredit: number;
  id: string;
  balanceAfterCredit: number;
  totalSpent: number;
}

export interface PaginationMeta {
  number: number;
  size: number;
  totalElements: number;
  totalPages: number;
}

export interface SpendingEntryWithCalcPageResponse {
  spendingEntries: SpendingAccountEntryWithCalculatedFieldsResponse[];
  page: PaginationMeta;
}

export type SortOrder = 'asc' | 'desc';

export type SpendingEntrySortField = 
  | 'year' 
  | 'month' 
  | 'account_name' 
  | 'starting_balance' 
  | 'current_balance' 
  | 'current_credit' 
  | 'balance_after_credit' 
  | 'total_spent';

export interface HTTPValidationError {
  detail?: ValidationError[];
}

export interface ValidationError {
  loc: (string | number)[];
  msg: string;
  type: string;
}
export interface MonthlyCategory {
  id: string;
  name: string;
  category_l1: 'spending' | 'saving';
}

export interface MonthlySummary {
  id: string;
  period_id: string;
  salary: number;
  month: number;
  year: number;
}

export interface MonthlyExpenseItem {
  id: string;
  period_id: string;
  name: string;
  amount: number;
  status: 'pending' | 'settled';
  category_l1: 'spending' | 'saving';
  category_l2: string;
  is_recurring: boolean;
  month: number;
  year: number;
}

export interface MonthlyExpenseItemRequest {
  name: string;
  amount: number;
  category_l1: 'spending' | 'saving';
  category_l2: string;
  is_recurring: boolean;
  status?: 'pending' | 'settled';
}

// ── Savings Buckets (V2 Fund Segregation) ───────────────────────────────────

export interface SavingsBucketResponse {
  id: string;
  accountId: string;
  name: string;
  allocatedAmount: number;
  targetAmount: number | null;
}

export interface SavingsBucketCreateRequest {
  name: string;
  targetAmount?: number | null;
}

export interface SavingsBucketUpdateRequest {
  name: string;
  targetAmount?: number | null;
}

export interface SavingsBucketTransactionCreateRequest {
  sourceBucketId?: string | null;
  destinationBucketId?: string | null;
  amount: number;
  transactionType: string; // 'deposit', 'withdraw', 'allocate', 'release', 'transfer'
  description: string;
  transactionDate?: string | null; // ISO DateTime
}

export interface SavingsBucketTransactionResponse {
  id: string;
  accountId: string;
  sourceBucketId: string | null;
  destinationBucketId: string | null;
  amount: number;
  transactionType: string;
  description: string;
  transactionDate: string; // ISO DateTime
  isCancelled: boolean;
  cancellationReason: string | null;
}

export interface SavingsBucketTransactionsPageResponse {
  transactions: SavingsBucketTransactionResponse[];
  totalElements: number;
  limit: number;
  offset: number;
}
