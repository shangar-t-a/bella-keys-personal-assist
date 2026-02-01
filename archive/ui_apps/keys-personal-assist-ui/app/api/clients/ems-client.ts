import type {
  AccountNameRequest,
  AccountNameResponse,
  AccountUpdateRequest,
  MonthYearRequest,
  MonthYearResponse,
  SpendingAccountEntryRequest,
  SpendingAccountEntryWithCalculatedFieldsResponse,
} from "@/types/api"

const EMS_API_URL = process.env.NEXT_PUBLIC_EMS_API_URL || "http://localhost:8000"

/**
 * EMS (Expense Management System) Client
 * Handles all account, month-year, and spending account operations
 */
class EMSClient {
  private baseURL: string

  constructor() {
    this.baseURL = EMS_API_URL
  }

  // Account endpoints
  async getAllAccounts(): Promise<AccountNameResponse[]> {
    const response = await fetch(`${this.baseURL}/v1/account/list`)
    if (!response.ok) throw new Error("Failed to fetch accounts")
    return response.json()
  }

  async getOrCreateAccount(data: AccountNameRequest): Promise<AccountNameResponse> {
    const response = await fetch(`${this.baseURL}/v1/account/get_or_create`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    })
    if (!response.ok) throw new Error("Failed to get or create account")
    return response.json()
  }

  async updateAccountName(accountId: string, data: AccountUpdateRequest): Promise<AccountNameResponse> {
    const response = await fetch(`${this.baseURL}/v1/account/${accountId}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    })
    if (!response.ok) throw new Error("Failed to update account")
    return response.json()
  }

  async deleteAccount(accountId: string): Promise<void> {
    const response = await fetch(`${this.baseURL}/v1/account/${accountId}`, {
      method: "DELETE",
    })
    if (!response.ok) throw new Error("Failed to delete account")
  }

  // Month Year endpoints
  async getAllMonthYears(): Promise<MonthYearResponse[]> {
    const response = await fetch(`${this.baseURL}/v1/month_year/list`)
    if (!response.ok) throw new Error("Failed to fetch month years")
    return response.json()
  }

  async getOrCreateMonthYear(data: MonthYearRequest): Promise<MonthYearResponse> {
    const response = await fetch(`${this.baseURL}/v1/month_year/get_or_create`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    })
    if (!response.ok) throw new Error("Failed to get or create month year")
    return response.json()
  }

  async updateMonthYear(monthYearId: string, data: MonthYearRequest): Promise<MonthYearResponse> {
    const response = await fetch(`${this.baseURL}/v1/month_year/${monthYearId}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    })
    if (!response.ok) throw new Error("Failed to update month year")
    return response.json()
  }

  async deleteMonthYear(monthYearId: string): Promise<void> {
    const response = await fetch(`${this.baseURL}/v1/month_year/${monthYearId}`, {
      method: "DELETE",
    })
    if (!response.ok) throw new Error("Failed to delete month year")
  }

  // Spending Account endpoints
  async getAllSpendingAccountEntries(): Promise<SpendingAccountEntryWithCalculatedFieldsResponse[]> {
    const response = await fetch(`${this.baseURL}/v1/spending_account/list`)
    if (!response.ok) throw new Error("Failed to fetch spending accounts")
    return response.json()
  }

  async getAllSpendingAccountEntriesForAccount(
    accountId: string,
  ): Promise<SpendingAccountEntryWithCalculatedFieldsResponse[]> {
    const response = await fetch(`${this.baseURL}/v1/spending_account/${accountId}`)
    if (!response.ok) throw new Error("Failed to fetch spending account entries")
    return response.json()
  }

  async addSpendingAccountEntry(
    data: SpendingAccountEntryRequest,
  ): Promise<SpendingAccountEntryWithCalculatedFieldsResponse> {
    const response = await fetch(`${this.baseURL}/v1/spending_account`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    })
    if (!response.ok) throw new Error("Failed to add spending account entry")
    return response.json()
  }

  async editSpendingAccountEntry(
    entryId: string,
    data: SpendingAccountEntryRequest,
  ): Promise<SpendingAccountEntryWithCalculatedFieldsResponse> {
    const response = await fetch(`${this.baseURL}/v1/spending_account/${entryId}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    })
    if (!response.ok) throw new Error("Failed to edit spending account entry")
    return response.json()
  }

  async deleteSpendingAccountEntry(entryId: string): Promise<void> {
    const response = await fetch(`${this.baseURL}/v1/spending_account/${entryId}`, {
      method: "DELETE",
    })
    if (!response.ok) throw new Error("Failed to delete spending account entry")
  }
}

// Export singleton instance
export const emsClient = new EMSClient()
