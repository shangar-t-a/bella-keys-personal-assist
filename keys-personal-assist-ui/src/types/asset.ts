export type CompoundingFrequency = 'MONTHLY' | 'QUARTERLY' | 'HALF_YEARLY' | 'YEARLY';

export interface AssetSubcategory {
  id: string;
  categoryId: string;
  name: string;
  code: string;
  description: string | null;
  valuationType: 'UNIT_BASED' | 'VALUE_BASED';
  hasInterest: boolean;
  hasMaturity: boolean;
}

export interface AssetCategory {
  id: string;
  name: string;
  code: 'EQUITY' | 'DEBT' | 'REAL_ESTATE' | 'COMMODITIES' | 'CASH_BANK';
  description: string | null;
  subcategories: AssetSubcategory[];
}

export interface AssetInterestDetails {
  interestRate: number;
  compounding: CompoundingFrequency;
  maturityDate?: string | null;
}

export interface AssetUnitDetails {
  units?: number;
  pricePerUnit: number;
}

export interface Asset {
  id: string;
  categoryId: string;
  categoryName: string;
  categoryCode: 'EQUITY' | 'DEBT' | 'REAL_ESTATE' | 'COMMODITIES' | 'CASH_BANK';
  name: string;
  subcategoryId: string | null;
  investedValue: number;
  baseAssetValue?: number;
  additionalSpent?: number;
  totalLoanInterest?: number;
  totalCashOutflow?: number;
  currentValue: number;
  interestRate: number | null;
  interestCompounding: CompoundingFrequency | null;
  maturityDate: string | null;
  notes: string | null;
  absoluteReturns: number;
  percentageReturns: number;
  createdAt: string; // ISO datetime
  updatedAt: string; // ISO datetime
}

export interface AssetRequest {
  categoryId: string;
  name: string;
  subcategoryId?: string | null;
  initialAmount: number;
  unitDetails?: AssetUnitDetails | null;
  interestDetails?: AssetInterestDetails | null;
  notes?: string | null;
}

export interface AssetUpdateRequest {
  categoryId?: string | null;
  name?: string | null;
  subcategoryId?: string | null;
  interestDetails?: AssetInterestDetails | null;
  notes?: string | null;
}

export type AssetTransactionType =
  | 'BUY'
  | 'SELL'
  | 'REVALUE'
  | 'ANCILLARY_FEE'
  | 'CAPITALIZED_INTEREST'
  | 'INTEREST_REDUCTION'
  | 'IMPROVEMENT';

export interface AssetTransaction {
  id: string;
  assetId: string;
  transactionType: AssetTransactionType;
  amount: number;
  units: number | null;
  pricePerUnit: number | null;
  transactionDate: string; // ISO datetime
  description: string | null;
}

export interface AssetTransactionRequest {
  transactionType: AssetTransactionType;
  amount: number;
  unitDetails?: AssetUnitDetails | null;
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
