import type { CompoundingFrequency } from './asset';

export interface LiabilitySubcategory {
  id: string;
  categoryId: string;
  name: string;
  code: string;
  description: string | null;
  valuationType: 'VALUE_BASED' | 'UNIT_BASED';
  hasInterest: boolean;
  hasMaturity: boolean;
}

export interface LiabilityCategory {
  id: string;
  name: string;
  code: 'SECURED_LOAN' | 'UNSECURED_LOAN' | 'REVOLVING_CREDIT' | 'OTHER';
  description: string | null;
  subcategories: LiabilitySubcategory[];
}

export interface LiabilityInterestDetails {
  interestRate: number;
  compounding: CompoundingFrequency;
  emiAmount?: number | null;
  maturityDate?: string | null;
}

export interface Liability {
  id: string;
  categoryId: string;
  categoryName: string;
  categoryCode: 'SECURED_LOAN' | 'UNSECURED_LOAN' | 'REVOLVING_CREDIT' | 'OTHER';
  name: string;
  subcategoryId: string | null;
  originalValue: number;
  currentValue: number; // outstanding balance
  interestRate: number | null;
  interestCompounding: CompoundingFrequency | null;
  emiAmount: number | null;
  maturityDate: string | null;
  notes: string | null;
  totalRepaid: number;
  accumulated_interest?: number; // wait, let's match camelCase from API or snake_case
  // Let's check schemas/liability.py: accumulatedInterest is camelCased due to BaseSchema's alias_generator=to_camel
  accumulatedInterest: number;
  progressPct: number;
  createdAt: string; // ISO datetime
  updatedAt: string; // ISO datetime
}

export interface LiabilityRequest {
  categoryId: string;
  name: string;
  subcategoryId?: string | null;
  initialAmount: number;
  initialDate?: string | null;
  interestDetails?: LiabilityInterestDetails | null;
  notes?: string | null;
}

export interface LiabilityUpdateRequest {
  categoryId?: string | null;
  name?: string | null;
  subcategoryId?: string | null;
  interestDetails?: LiabilityInterestDetails | null;
  notes?: string | null;
}

export interface LiabilityTransaction {
  id: string;
  liabilityId: string;
  transactionType: 'BORROW' | 'REPAY' | 'REVALUE';
  amount: number;
  transactionDate: string; // ISO datetime
  description: string | null;
}

export interface LiabilityTransactionRequest {
  transactionType: 'BORROW' | 'REPAY' | 'REVALUE';
  amount: number;
  transactionDate?: string | null; // ISO datetime
  description?: string | null;
}

export interface LiabilityCategorySummary {
  categoryId: string;
  categoryName: string;
  categoryCode: 'SECURED_LOAN' | 'UNSECURED_LOAN' | 'REVOLVING_CREDIT' | 'OTHER';
  totalOriginal: number;
  totalOutstanding: number;
  totalRepaid: number;
  accumulatedInterest: number;
}

export interface LiabilitySummary {
  totalOriginal: number;
  totalOutstanding: number;
  totalRepaid: number;
  accumulatedInterest: number;
  categoryBreakdowns: LiabilityCategorySummary[];
}

export interface LiabilityProjectionPoint {
  date: string;
  idealBalance: number;
  actualBalance: number | null;
  idealInterestPaid: number;
  actualInterestPaid: number | null;
}

export interface LiabilityProjectionMetrics {
  idealTenureMonths: number;
  remainingTenureMonths: number;
  tenureSavedMonths: number;
  totalInterestIdeal: number;
  totalInterestProjected: number;
  interestSaved: number;
  idealEndDate: string | null;
  projectedEndDate: string | null;
}

export interface LiabilityProjections {
  metrics: LiabilityProjectionMetrics;
  projectionPoints: LiabilityProjectionPoint[];
}

