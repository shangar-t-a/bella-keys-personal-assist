import type {
  AccountNameRequest,
  AccountNameResponse,
  AccountUpdateRequest,
  PeriodRequest,
  PeriodResponse,
  SpendingAccountEntryRequest,
  SpendingAccountEntryWithCalculatedFieldsResponse,
  SpendingEntryWithCalcPageResponse,
  SortOrder,
  SpendingEntrySortField,
  MonthlyCategory,
  MonthlySummary,
  MonthlyExpenseItem,
  MonthlyExpenseItemRequest,
  SavingsBucketResponse,
  SavingsBucketCreateRequest,
  SavingsBucketUpdateRequest,
  SavingsBucketTransactionCreateRequest,
  SavingsBucketTransactionResponse,
  SavingsBucketTransactionsPageResponse,
} from '@/types/api';
import { getEmsBase } from '@/api/config';
import { fetchWithAuth } from './fetchClient';

export interface SpendingEntryListParams {
  page?: number;
  size?: number;
  sortBy?: SpendingEntrySortField;
  sortOrder?: SortOrder;
  month?: number | null;
  year?: number | null;
  accountName?: string | null;
}

/**
 * EMS (Expense Management System) Client
 * Handles all account, period, and spending account operations
 *
 * Uses relative paths (/api/ems) that are proxied by nginx in production
 * and by Vite dev server in development to the actual backend services.
 */
class EMSClient {
  private baseURL: string;

  constructor() {
    this.baseURL = getEmsBase();
  }

  // ── Account endpoints ──────────────────────────────────────────────────────

  async getAllAccounts(): Promise<AccountNameResponse[]> {
    const response = await fetchWithAuth(`${this.baseURL}/v1/account/list`);
    if (!response.ok) throw new Error('Failed to fetch accounts');
    return response.json();
  }

  async getOrCreateAccount(data: AccountNameRequest): Promise<AccountNameResponse> {
    const response = await fetchWithAuth(`${this.baseURL}/v1/account/get_or_create`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error('Failed to get or create account');
    return response.json();
  }

  async updateAccountName(accountId: string, data: AccountUpdateRequest): Promise<AccountNameResponse> {
    const response = await fetchWithAuth(`${this.baseURL}/v1/account/${accountId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error('Failed to update account');
    return response.json();
  }

  async deleteAccount(accountId: string): Promise<void> {
    const response = await fetchWithAuth(`${this.baseURL}/v1/account/${accountId}`, {
      method: 'DELETE',
    });
    if (!response.ok) throw new Error('Failed to delete account');
  }

  // ── Period endpoints ────────────────────────────────────────────────────────

  async getAllPeriods(): Promise<PeriodResponse[]> {
    const response = await fetchWithAuth(`${this.baseURL}/v1/period/list`);
    if (!response.ok) throw new Error('Failed to fetch periods');
    return response.json();
  }

  async getOrCreatePeriod(data: PeriodRequest): Promise<PeriodResponse> {
    const response = await fetchWithAuth(`${this.baseURL}/v1/period/get_or_create`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error('Failed to get or create period');
    return response.json();
  }

  async updatePeriod(periodId: string, data: PeriodRequest): Promise<PeriodResponse> {
    const response = await fetchWithAuth(`${this.baseURL}/v1/period/${periodId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error('Failed to update period');
    return response.json();
  }

  async deletePeriod(periodId: string): Promise<void> {
    const response = await fetchWithAuth(`${this.baseURL}/v1/period/${periodId}`, {
      method: 'DELETE',
    });
    if (!response.ok) throw new Error('Failed to delete period');
  }

  // ── Spending Account endpoints ─────────────────────────────────────────────

  async getAllSpendingAccountEntries(
    params: SpendingEntryListParams = {}
  ): Promise<SpendingEntryWithCalcPageResponse> {
    const qs = new URLSearchParams();
    if (params.page !== undefined) qs.set('page', String(params.page));
    if (params.size !== undefined) qs.set('size', String(params.size));
    if (params.sortBy) qs.set('sortBy', params.sortBy);
    if (params.sortOrder) qs.set('sortOrder', params.sortOrder);
    if (params.month != null) qs.set('month', String(params.month));
    if (params.year != null) qs.set('year', String(params.year));
    if (params.accountName != null) qs.set('accountName', params.accountName);
    const queryString = qs.toString();
    const listUrl = `${this.baseURL}/v1/spending_account/list${queryString ? `?${queryString}` : ''}`;

    const response = await fetchWithAuth(listUrl);
    if (!response.ok) throw new Error('Failed to fetch spending accounts');
    return response.json();
  }

  async getAllSpendingAccountEntriesForAccount(
    accountId: string,
    params: SpendingEntryListParams = {}
  ): Promise<SpendingEntryWithCalcPageResponse> {
    const qs = new URLSearchParams();
    if (params.page !== undefined) qs.set('page', String(params.page));
    if (params.size !== undefined) qs.set('size', String(params.size));
    if (params.sortBy) qs.set('sortBy', params.sortBy);
    if (params.sortOrder) qs.set('sortOrder', params.sortOrder);
    if (params.month != null) qs.set('month', String(params.month));
    if (params.year != null) qs.set('year', String(params.year));
    const queryString = qs.toString();
    const listUrl = `${this.baseURL}/v1/spending_account/${accountId}/list${queryString ? `?${queryString}` : ''}`;

    const response = await fetchWithAuth(listUrl);
    if (!response.ok) throw new Error('Failed to fetch spending account entries');
    return response.json();
  }

  async addSpendingAccountEntry(
    data: SpendingAccountEntryRequest
  ): Promise<SpendingAccountEntryWithCalculatedFieldsResponse> {
    const response = await fetchWithAuth(`${this.baseURL}/v1/spending_account`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error('Failed to add spending account entry');
    return response.json();
  }

  async editSpendingAccountEntry(
    entryId: string,
    data: SpendingAccountEntryRequest
  ): Promise<SpendingAccountEntryWithCalculatedFieldsResponse> {
    const response = await fetchWithAuth(`${this.baseURL}/v1/spending_account/${entryId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error('Failed to edit spending account entry');
    return response.json();
  }

  async deleteSpendingAccountEntry(entryId: string): Promise<void> {
    const response = await fetchWithAuth(`${this.baseURL}/v1/spending_account/${entryId}`, {
      method: 'DELETE',
    });
    if (!response.ok) throw new Error('Failed to delete spending account entry');
  }

  // ── Monthly Planner endpoints ─────────────────────────────────────────────

  async listMonthlyCategories(): Promise<MonthlyCategory[]> {
    const response = await fetchWithAuth(`${this.baseURL}/v1/monthly-planner/categories`);
    if (!response.ok) throw new Error('Failed to fetch categories');
    return response.json();
  }

  async addMonthlyCategory(data: { name: string; category_l1: string }): Promise<MonthlyCategory> {
    const response = await fetchWithAuth(`${this.baseURL}/v1/monthly-planner/categories`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error('Failed to add category');
    return response.json();
  }

  async deleteMonthlyCategory(categoryId: string): Promise<void> {
    const response = await fetchWithAuth(`${this.baseURL}/v1/monthly-planner/categories/${categoryId}`, {
      method: 'DELETE',
    });
    if (!response.ok) throw new Error('Failed to delete category');
  }

  async getMonthlySummary(year: number, month: number): Promise<MonthlySummary> {
    const response = await fetchWithAuth(`${this.baseURL}/v1/monthly-planner/summary/${year}/${month}`);
    if (!response.ok) throw new Error('Failed to fetch summary');
    return response.json();
  }

  async updateMonthlySalary(year: number, month: number, salary: number): Promise<MonthlySummary> {
    const response = await fetchWithAuth(`${this.baseURL}/v1/monthly-planner/summary/${year}/${month}/salary`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ salary }),
    });
    if (!response.ok) throw new Error('Failed to update salary');
    return response.json();
  }

  async listMonthlyExpenses(year: number, month: number): Promise<MonthlyExpenseItem[]> {
    const response = await fetchWithAuth(`${this.baseURL}/v1/monthly-planner/expenses/${year}/${month}`);
    if (!response.ok) throw new Error('Failed to fetch expenses');
    return response.json();
  }

  async addMonthlyExpense(year: number, month: number, data: MonthlyExpenseItemRequest): Promise<MonthlyExpenseItem> {
    const response = await fetchWithAuth(`${this.baseURL}/v1/monthly-planner/expenses/${year}/${month}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error('Failed to add expense');
    return response.json();
  }

  async updateMonthlyExpense(expenseId: string, data: MonthlyExpenseItemRequest): Promise<MonthlyExpenseItem> {
    const response = await fetchWithAuth(`${this.baseURL}/v1/monthly-planner/expenses/${expenseId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error('Failed to update expense');
    return response.json();
  }

  async deleteMonthlyExpense(expenseId: string): Promise<void> {
    const response = await fetchWithAuth(`${this.baseURL}/v1/monthly-planner/expenses/${expenseId}`, {
      method: 'DELETE',
    });
    if (!response.ok) throw new Error('Failed to delete expense');
  }

  async resetMonthlyStatuses(year: number, month: number): Promise<void> {
    const response = await fetchWithAuth(`${this.baseURL}/v1/monthly-planner/expenses/${year}/${month}/reset`, {
      method: 'POST',
    });
    if (!response.ok) throw new Error('Failed to reset statuses');
  }

  async syncMonthlyFromPrevious(year: number, month: number): Promise<MonthlyExpenseItem[]> {
    const response = await fetchWithAuth(`${this.baseURL}/v1/monthly-planner/expenses/${year}/${month}/sync`, {
      method: 'POST',
    });
    if (!response.ok) throw new Error('Failed to sync from previous month');
    return response.json();
  }

  // ── Savings Buckets (V2 Fund Segregation) ───────────────────────────────────

  async getSavingsBuckets(accountId: string): Promise<SavingsBucketResponse[]> {
    const response = await fetchWithAuth(`${this.baseURL}/v1/savings_buckets/list/${accountId}`);
    if (!response.ok) throw new Error('Failed to fetch savings buckets');
    return response.json();
  }

  async createSavingsBucket(accountId: string, data: SavingsBucketCreateRequest): Promise<SavingsBucketResponse> {
    const response = await fetchWithAuth(`${this.baseURL}/v1/savings_buckets/${accountId}/bucket`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!response.ok) {
      const errData = await response.json().catch(() => ({}));
      throw new Error(errData.detail || 'Failed to create savings bucket');
    }
    return response.json();
  }

  async updateSavingsBucket(bucketId: string, data: SavingsBucketUpdateRequest): Promise<SavingsBucketResponse> {
    const response = await fetchWithAuth(`${this.baseURL}/v1/savings_buckets/bucket/${bucketId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!response.ok) {
      const errData = await response.json().catch(() => ({}));
      throw new Error(errData.detail || 'Failed to update savings bucket');
    }
    return response.json();
  }

  async deleteSavingsBucket(bucketId: string): Promise<void> {
    const response = await fetchWithAuth(`${this.baseURL}/v1/savings_buckets/bucket/${bucketId}`, {
      method: 'DELETE',
    });
    if (!response.ok) {
      const errData = await response.json().catch(() => ({}));
      throw new Error(errData.detail || 'Failed to delete savings bucket');
    }
  }

  async createSavingsBucketTransaction(
    accountId: string,
    data: SavingsBucketTransactionCreateRequest
  ): Promise<SavingsBucketTransactionResponse> {
    const response = await fetchWithAuth(`${this.baseURL}/v1/savings_buckets/${accountId}/transaction`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!response.ok) {
      const errData = await response.json().catch(() => ({}));
      throw new Error(errData.detail || 'Failed to create savings bucket transaction');
    }
    return response.json();
  }

  async getSavingsBucketTransactions(
    accountId: string,
    limit: number = 50,
    offset: number = 0
  ): Promise<SavingsBucketTransactionsPageResponse> {
    const response = await fetchWithAuth(`${this.baseURL}/v1/savings_buckets/${accountId}/transactions?limit=${limit}&offset=${offset}`);
    if (!response.ok) throw new Error('Failed to fetch savings bucket transactions');
    return response.json();
  }

  async cancelSavingsBucketTransaction(
    transactionId: string,
    data: { reason: string }
  ): Promise<SavingsBucketTransactionResponse> {
    const response = await fetchWithAuth(`${this.baseURL}/v1/savings_buckets/transaction/${transactionId}/cancel`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!response.ok) {
      const errData = await response.json().catch(() => ({}));
      throw new Error(errData.detail || 'Failed to cancel transaction');
    }
    return response.json();
  }
}

// Export singleton instance
export const emsClient = new EMSClient();
