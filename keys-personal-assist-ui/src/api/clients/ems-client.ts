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
} from '@/types/api';
import { getEmsBase } from '@/api/config';

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
    const response = await fetch(`${this.baseURL}/v1/account/list`);
    if (!response.ok) throw new Error('Failed to fetch accounts');
    return response.json();
  }

  async getOrCreateAccount(data: AccountNameRequest): Promise<AccountNameResponse> {
    const response = await fetch(`${this.baseURL}/v1/account/get_or_create`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error('Failed to get or create account');
    return response.json();
  }

  async updateAccountName(accountId: string, data: AccountUpdateRequest): Promise<AccountNameResponse> {
    const response = await fetch(`${this.baseURL}/v1/account/${accountId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error('Failed to update account');
    return response.json();
  }

  async deleteAccount(accountId: string): Promise<void> {
    const response = await fetch(`${this.baseURL}/v1/account/${accountId}`, {
      method: 'DELETE',
    });
    if (!response.ok) throw new Error('Failed to delete account');
  }

  // ── Period endpoints ────────────────────────────────────────────────────────

  async getAllPeriods(): Promise<PeriodResponse[]> {
    const response = await fetch(`${this.baseURL}/v1/period/list`);
    if (!response.ok) throw new Error('Failed to fetch periods');
    return response.json();
  }

  async getOrCreatePeriod(data: PeriodRequest): Promise<PeriodResponse> {
    const response = await fetch(`${this.baseURL}/v1/period/get_or_create`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error('Failed to get or create period');
    return response.json();
  }

  async updatePeriod(periodId: string, data: PeriodRequest): Promise<PeriodResponse> {
    const response = await fetch(`${this.baseURL}/v1/period/${periodId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error('Failed to update period');
    return response.json();
  }

  async deletePeriod(periodId: string): Promise<void> {
    const response = await fetch(`${this.baseURL}/v1/period/${periodId}`, {
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

    const response = await fetch(listUrl);
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

    const response = await fetch(listUrl);
    if (!response.ok) throw new Error('Failed to fetch spending account entries');
    return response.json();
  }

  async addSpendingAccountEntry(
    data: SpendingAccountEntryRequest
  ): Promise<SpendingAccountEntryWithCalculatedFieldsResponse> {
    const response = await fetch(`${this.baseURL}/v1/spending_account`, {
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
    const response = await fetch(`${this.baseURL}/v1/spending_account/${entryId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!response.ok) throw new Error('Failed to edit spending account entry');
    return response.json();
  }

  async deleteSpendingAccountEntry(entryId: string): Promise<void> {
    const response = await fetch(`${this.baseURL}/v1/spending_account/${entryId}`, {
      method: 'DELETE',
    });
    if (!response.ok) throw new Error('Failed to delete spending account entry');
  }
}

// Export singleton instance
export const emsClient = new EMSClient();
