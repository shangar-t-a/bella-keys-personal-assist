export interface WealthSummary {
  totalAssets: number;
  totalInvestedAssets: number;
  totalReturnsAssets: number;
  percentageReturnsAssets: number;
  totalLiabilities: number;
  totalOriginalLiabilities: number;
  totalRepaidLiabilities: number;
  accumulatedInterestLiabilities: number;
  netWorth: number;
}

export interface HistoricalNetWorthPoint {
  date: string; // Format: YYYY-MM
  totalAssets: number;
  totalLiabilities: number;
  netWorth: number;
}

export interface WealthCategoryAllocation {
  categoryName: string;
  categoryCode: string;
  totalValue: number;
  percentage: number;
}

export interface WealthAllocation {
  assets: WealthCategoryAllocation[];
  liabilities: WealthCategoryAllocation[];
  totalAssetsValue: number;
  totalLiabilitiesValue: number;
  debtToAssetRatio: number;
  liquidityRatio: number;
  equityFinancedPct: number;
  liabilitiesFinancedPct: number;
  leverageStatusLabel: string;
  leverageStatusType: 'SUCCESS' | 'WARNING' | 'ERROR';
  liquidityStatusLabel: string;
  liquidityStatusType: 'SUCCESS' | 'WARNING';
}
