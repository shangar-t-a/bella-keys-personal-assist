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
