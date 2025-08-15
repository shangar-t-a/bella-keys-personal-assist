import axios from 'axios';
import {
  AccountNameRequest,
  AccountNameResponse,
  AccountUpdateRequest,
  MonthYearRequest,
  MonthYearResponse,
  SpendingAccountEntryRequest,
  SpendingAccountEntryWithCalculatedFieldsResponse,
} from '../types/api';

const API_BASE_URL = import.meta.env.VITE_BACKEND_BASE_URL;

// Log the API_BASE_URL to the console for debugging
console.log('API_BASE_URL from .env:', API_BASE_URL);

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const getAllAccounts = async (): Promise<AccountNameResponse[]> => {
  const response = await apiClient.get<AccountNameResponse[]>('/v1/account/list');
  return response.data;
};

export const getOrCreateAccount = async (
  data: AccountNameRequest
): Promise<AccountNameResponse> => {
  const response = await apiClient.post<AccountNameResponse>('/v1/account/get_or_create', data);
  return response.data;
};

export const updateAccountName = async (
  accountId: string,
  data: AccountUpdateRequest
): Promise<AccountNameResponse> => {
  const response = await apiClient.put<AccountNameResponse>(`/v1/account/${accountId}`, data);
  return response.data;
};

export const deleteAccount = async (accountId: string): Promise<void> => {
  await apiClient.delete(`/v1/account/${accountId}`);
};

export const getAllMonthYears = async (): Promise<MonthYearResponse[]> => {
  const response = await apiClient.get<MonthYearResponse[]>('/v1/month_year/list');
  return response.data;
};

export const getOrCreateMonthYear = async (
  data: MonthYearRequest
): Promise<MonthYearResponse> => {
  const response = await apiClient.post<MonthYearResponse>('/v1/month_year/get_or_create', data);
  return response.data;
};

export const updateMonthYear = async (
  monthYearId: string,
  data: MonthYearRequest
): Promise<MonthYearResponse> => {
  const response = await apiClient.put<MonthYearResponse>(`/v1/month_year/${monthYearId}`, data);
  return response.data;
};

export const deleteMonthYear = async (monthYearId: string): Promise<void> => {
  await apiClient.delete(`/v1/month_year/${monthYearId}`);
};

export const getAllSpendingAccountEntries = async (): Promise<
  SpendingAccountEntryWithCalculatedFieldsResponse[]
> => {
  const response = await apiClient.get<SpendingAccountEntryWithCalculatedFieldsResponse[]>(
    '/v1/spending_account/list'
  );
  return response.data;
};

export const getAllSpendingAccountEntriesForAccount = async (
  accountId: string
): Promise<SpendingAccountEntryWithCalculatedFieldsResponse[]> => {
  const response = await apiClient.get<SpendingAccountEntryWithCalculatedFieldsResponse[]>(
    `/v1/spending_account/${accountId}`
  );
  return response.data;
};

export const addSpendingAccountEntry = async (
  data: SpendingAccountEntryRequest
): Promise<SpendingAccountEntryWithCalculatedFieldsResponse> => {
  const response = await apiClient.post<SpendingAccountEntryWithCalculatedFieldsResponse>(
    '/v1/spending_account',
    data
  );
  return response.data;
};

export const editSpendingAccountEntry = async (
  entryId: string,
  data: SpendingAccountEntryRequest
): Promise<SpendingAccountEntryWithCalculatedFieldsResponse> => {
  const response = await apiClient.put<SpendingAccountEntryWithCalculatedFieldsResponse>(
    `/v1/spending_account/${entryId}`,
    data
  );
  return response.data;
};

export const deleteSpendingAccountEntry = async (entryId: string): Promise<void> => {
  await apiClient.delete(`/v1/spending_account/${entryId}`);
};
