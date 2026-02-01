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

export interface MonthYearRequest {
  month: string;
  year: number;
}

export interface MonthYearResponse {
  id: string;
  month: string;
  year: number;
}

export interface SpendingAccountEntryRequest {
  accountName: string;
  month: string;
  year: number;
  startingBalance: number;
  currentBalance: number;
  currentCredit: number;
}

export interface SpendingAccountEntryWithCalculatedFieldsResponse {
  accountName: string;
  month: string;
  year: number;
  startingBalance: number;
  currentBalance: number;
  currentCredit: number;
  id: string;
  balanceAfterCredit: number;
  totalSpent: number;
}

export interface HTTPValidationError {
  detail?: ValidationError[];
}

export interface ValidationError {
  loc: (string | number)[];
  msg: string;
  type: string;
}
