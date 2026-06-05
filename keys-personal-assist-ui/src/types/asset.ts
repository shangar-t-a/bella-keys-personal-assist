export interface AssetCategory {
  id: string;
  name: string;
  code: 'EQUITY' | 'DEBT' | 'REAL_ESTATE' | 'COMMODITIES' | 'CASH_BANK';
  description: string | null;
}

export interface Asset {
  id: string;
  categoryId: string;
  categoryName: string;
  categoryCode: 'EQUITY' | 'DEBT' | 'REAL_ESTATE' | 'COMMODITIES' | 'CASH_BANK';
  name: string;
  subCategory: string | null;
  investedValue: number;
  currentValue: number;
  notes: string | null;
  absoluteReturns: number;
  percentageReturns: number;
  createdAt: string; // ISO datetime
  updatedAt: string; // ISO datetime
}

export interface AssetRequest {
  categoryId: string;
  name: string;
  subCategory?: string | null;
  initialAmount: number;
  units?: number | null;
  pricePerUnit?: number | null;
  notes?: string | null;
}

export interface AssetUpdateRequest {
  categoryId: string;
  name: string;
  subCategory?: string | null;
  notes?: string | null;
}

export interface AssetTransaction {
  id: string;
  assetId: string;
  transactionType: 'BUY' | 'SELL' | 'REVALUE';
  amount: number;
  units: number | null;
  pricePerUnit: number | null;
  transactionDate: string; // ISO datetime
  description: string | null;
}

export interface AssetTransactionRequest {
  transactionType: 'BUY' | 'SELL' | 'REVALUE';
  amount: number;
  units?: number | null;
  pricePerUnit?: number | null;
  transactionDate?: string | null; // ISO datetime
  description?: string | null;
}

export interface AssetCategorySummary {
  categoryId: string;
  categoryName: string;
  categoryCode: 'EQUITY' | 'DEBT' | 'REAL_ESTATE' | 'COMMODITIES' | 'CASH_BANK';
  totalInvested: number;
  totalCurrent: number;
  totalReturns: number;
  percentageReturns: number;
}

export interface AssetSummary {
  totalInvested: number;
  totalCurrent: number;
  totalReturns: number;
  percentageReturns: number;
  categoryBreakdowns: AssetCategorySummary[];
}
