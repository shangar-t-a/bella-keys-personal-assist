import { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CircularProgress,
  LinearProgress,
  useTheme,
  alpha,
  Tooltip,
} from '@mui/material';
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip as RechartsTooltip,
} from 'recharts';
import { emsClient } from '@/api/clients/ems-client';
import type { WealthAllocation } from '@/types/wealth';
import { formatCurrency } from '@/utils/formatters';
import { toast } from 'sonner';
import { InfoOutlined as InfoIcon } from '@mui/icons-material';

export default function AllocationTab() {
  const theme = useTheme();
  const isDark = theme.palette.mode === 'dark';

  const [allocation, setAllocation] = useState<WealthAllocation | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadAllocation() {
      try {
        setLoading(true);
        const res = await emsClient.getWealthAllocation();
        setAllocation(res);
        setError(null);
      } catch (err: any) {
        console.error(err);
        setError('Failed to load portfolio allocations');
        toast.error('Error fetching allocation details');
      } finally {
        setLoading(false);
      }
    }
    loadAllocation();
  }, []);

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', py: 8 }}>
        <CircularProgress size={40} />
      </Box>
    );
  }

  if (error || !allocation) {
    return (
      <Box sx={{ py: 4, textAlign: 'center' }}>
        <Typography color="error">{error || 'Something went wrong.'}</Typography>
      </Box>
    );
  }

  // Filter out zero-value categories for cleaner charts
  const activeAssets = allocation.assets.filter((a) => a.totalValue > 0);
  const activeLiabilities = allocation.liabilities.filter((l) => l.totalValue > 0);

  const {
    totalAssetsValue,
    totalLiabilitiesValue,
    debtToAssetRatio,
    liquidityRatio,
    equityFinancedPct,
    liabilitiesFinancedPct,
    leverageStatusLabel,
    leverageStatusType,
    liquidityStatusLabel,
    liquidityStatusType,
  } = allocation;

  const getStatusColor = (type: 'SUCCESS' | 'WARNING' | 'ERROR') => {
    if (type === 'SUCCESS') return 'success.main';
    if (type === 'WARNING') return 'warning.main';
    return 'error.main';
  };

  // Asset category styling meta matching theme/AssetsTab
  const ASSET_COLOR_MAP: Record<string, string> = {
    EQUITY: isDark ? theme.palette.primary.main : theme.palette.secondary.main,
    DEBT: isDark ? theme.palette.secondary.main : theme.palette.primary.main,
    REAL_ESTATE: isDark ? theme.palette.warning.dark : theme.palette.warning.main,
    COMMODITIES: isDark ? theme.palette.warning.main : theme.palette.warning.light,
    CASH_BANK: theme.palette.success.main,
  };

  // Liability category styling meta
  const LIABILITY_COLOR_MAP: Record<string, string> = {
    SECURED_LOAN: theme.palette.info.main,
    UNSECURED_LOAN: theme.palette.warning.main,
    REVOLVING_CREDIT: theme.palette.error.main,
    OTHER: theme.palette.text.secondary,
  };

  // Standard fallback colors
  const FALLBACK_COLORS = [
    theme.palette.primary.main,
    theme.palette.secondary.main,
    theme.palette.success.main,
    theme.palette.warning.main,
    theme.palette.error.main,
  ];

  const getAssetColor = (code: string, index: number) => {
    return ASSET_COLOR_MAP[code] || FALLBACK_COLORS[index % FALLBACK_COLORS.length];
  };

  const getLiabilityColor = (code: string, index: number) => {
    return LIABILITY_COLOR_MAP[code] || FALLBACK_COLORS[index % FALLBACK_COLORS.length];
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3, mt: 1 }}>
      {/* Allocation Donut Charts */}
      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' },
          gap: 3,
        }}
      >
        {/* Asset Allocation Chart */}
        <Card sx={{ p: 3, borderRadius: 3, border: `1px solid ${theme.palette.divider}`, minHeight: 380 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 1 }}>
            <Typography variant="subtitle1" sx={{ fontWeight: 700, fontFamily: '"Space Grotesk", sans-serif' }}>
              Asset Distribution
            </Typography>
            <Tooltip title="Percentage breakdown of your total assets across different asset classes (e.g. cash, equities, real estate, commodities) to assess diversification." arrow>
              <InfoIcon sx={{ fontSize: '0.9rem', color: 'text.secondary', cursor: 'pointer' }} />
            </Tooltip>
          </Box>
          <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 3, fontWeight: 500 }}>
            Percentage breakdown of your total assets
          </Typography>
          {activeAssets.length > 0 ? (
            <Box sx={{ width: '100%', height: 260, display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
              <ResponsiveContainer width="100%" height="80%">
                <PieChart>
                  <Pie
                    data={activeAssets}
                    cx="50%"
                    cy="50%"
                    innerRadius={55}
                    outerRadius={75}
                    paddingAngle={4}
                    dataKey="totalValue"
                  >
                    {activeAssets.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={getAssetColor(entry.categoryCode, index)} />
                    ))}
                  </Pie>
                  <RechartsTooltip
                    formatter={(value: any) => [formatCurrency(Number(value)), 'Value']}
                    contentStyle={{
                      backgroundColor: theme.palette.background.paper,
                      borderColor: theme.palette.divider,
                      borderRadius: 8,
                      fontSize: '0.78rem',
                      fontFamily: '"Space Grotesk", sans-serif',
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
              
              {/* Custom Grid Legend to match premium style and keep text aligned */}
              <Box
                sx={{
                  display: 'grid',
                  gridTemplateColumns: '1fr 1fr',
                  gap: 1,
                  mt: 1,
                  px: 2,
                }}
              >
                {activeAssets.map((entry, index) => (
                  <Box key={entry.categoryCode} sx={{ display: 'flex', alignItems: 'center' }}>
                    <Box
                      sx={{
                        width: 8,
                        height: 8,
                        borderRadius: '50%',
                        bgcolor: getAssetColor(entry.categoryCode, index),
                        mr: 1,
                      }}
                    />
                    <Typography variant="caption" sx={{ fontWeight: 600, color: 'text.primary', fontSize: '0.7rem' }}>
                      {entry.categoryName}: {entry.percentage.toFixed(1)}%
                    </Typography>
                  </Box>
                ))}
              </Box>
            </Box>
          ) : (
            <Box sx={{ py: 6, textAlign: 'center' }}>
              <Typography variant="body2" color="text.secondary">No assets found to show allocation.</Typography>
            </Box>
          )}
        </Card>

        {/* Liability Allocation Chart */}
        <Card sx={{ p: 3, borderRadius: 3, border: `1px solid ${theme.palette.divider}`, minHeight: 380 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 1 }}>
            <Typography variant="subtitle1" sx={{ fontWeight: 700, fontFamily: '"Space Grotesk", sans-serif' }}>
              Liability Distribution
            </Typography>
            <Tooltip title="Percentage breakdown of outstanding debt across different liability categories to analyze your borrowing profile." arrow>
              <InfoIcon sx={{ fontSize: '0.9rem', color: 'text.secondary', cursor: 'pointer' }} />
            </Tooltip>
          </Box>
          <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 3, fontWeight: 500 }}>
            Percentage breakdown of your outstanding liabilities
          </Typography>
          {activeLiabilities.length > 0 ? (
            <Box sx={{ width: '100%', height: 260, display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
              <ResponsiveContainer width="100%" height="80%">
                <PieChart>
                  <Pie
                    data={activeLiabilities}
                    cx="50%"
                    cy="50%"
                    innerRadius={55}
                    outerRadius={75}
                    paddingAngle={4}
                    dataKey="totalValue"
                  >
                    {activeLiabilities.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={getLiabilityColor(entry.categoryCode, index)} />
                    ))}
                  </Pie>
                  <RechartsTooltip
                    formatter={(value: any) => [formatCurrency(Number(value)), 'Outstanding']}
                    contentStyle={{
                      backgroundColor: theme.palette.background.paper,
                      borderColor: theme.palette.divider,
                      borderRadius: 8,
                      fontSize: '0.78rem',
                      fontFamily: '"Space Grotesk", sans-serif',
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
              
              {/* Custom Grid Legend */}
              <Box
                sx={{
                  display: 'grid',
                  gridTemplateColumns: '1fr 1fr',
                  gap: 1,
                  mt: 1,
                  px: 2,
                }}
              >
                {activeLiabilities.map((entry, index) => (
                  <Box key={entry.categoryCode} sx={{ display: 'flex', alignItems: 'center' }}>
                    <Box
                      sx={{
                        width: 8,
                        height: 8,
                        borderRadius: '50%',
                        bgcolor: getLiabilityColor(entry.categoryCode, index),
                        mr: 1,
                      }}
                    />
                    <Typography variant="caption" sx={{ fontWeight: 600, color: 'text.primary', fontSize: '0.7rem' }}>
                      {entry.categoryName}: {entry.percentage.toFixed(1)}%
                    </Typography>
                  </Box>
                ))}
              </Box>
            </Box>
          ) : (
            <Box sx={{ py: 6, textAlign: 'center' }}>
              <Typography variant="body2" color="text.secondary">No liabilities found to show allocation.</Typography>
            </Box>
          )}
        </Card>
      </Box>

      {/* Leverage Analysis & Financing Bar */}
      <Card sx={{ p: 3, borderRadius: 3, border: `1px solid ${theme.palette.divider}` }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 1 }}>
          <Typography variant="subtitle1" sx={{ fontWeight: 700, fontFamily: '"Space Grotesk", sans-serif' }}>
            Asset Financing Leverage
          </Typography>
          <Tooltip title="Visualizes how much of your total assets are financed using your own wealth (Equity) versus borrowed money (Liabilities). Ideally, self-owned equity should form the majority of your assets." arrow>
            <InfoIcon sx={{ fontSize: '0.9rem', color: 'text.secondary', cursor: 'pointer' }} />
          </Tooltip>
        </Box>
        <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 3.5, fontWeight: 500 }}>
          Visualizing how much of your total assets are self-owned (Equity) vs borrowed debt (Liabilities)
        </Typography>
        
        {totalAssetsValue > 0 ? (
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
            {/* Split Horizontal Bar */}
            <Box
              sx={{
                width: '100%',
                height: 24,
                borderRadius: 1.5,
                overflow: 'hidden',
                display: 'flex',
                bgcolor: 'divider',
              }}
            >
              <Tooltip title={`Equity (Self-Owned): ${equityFinancedPct.toFixed(1)}% - The net portion of your assets owned outright by you (Assets - Liabilities = ${formatCurrency(totalAssetsValue - totalLiabilitiesValue)})`} arrow>
                <Box
                  sx={{
                    width: `${equityFinancedPct}%`,
                    height: '100%',
                    bgcolor: theme.palette.primary.main,
                    transition: 'width 0.5s ease',
                  }}
                />
              </Tooltip>
              <Tooltip title={`Debt (Borrowed): ${liabilitiesFinancedPct.toFixed(1)}% - The portion of assets funded by loans or other outstanding liabilities (Total Liabilities = ${formatCurrency(totalLiabilitiesValue)})`} arrow>
                <Box
                  sx={{
                    width: `${liabilitiesFinancedPct}%`,
                    height: '100%',
                    bgcolor: theme.palette.error.main,
                    transition: 'width 0.5s ease',
                  }}
                />
              </Tooltip>
            </Box>

            {/* Labels */}
            <Box sx={{ display: 'flex', justifyContent: 'space-between', px: 0.5 }}>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <Box sx={{ width: 8, height: 8, borderRadius: '50%', bgcolor: theme.palette.primary.main, mr: 1 }} />
                <Typography variant="caption" sx={{ fontWeight: 700 }}>
                  Equity: {formatCurrency(totalAssetsValue - totalLiabilitiesValue)} ({equityFinancedPct.toFixed(1)}%)
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <Box sx={{ width: 8, height: 8, borderRadius: '50%', bgcolor: theme.palette.error.main, mr: 1 }} />
                <Typography variant="caption" sx={{ fontWeight: 700 }}>
                  Debt: {formatCurrency(totalLiabilitiesValue)} ({liabilitiesFinancedPct.toFixed(1)}%)
                </Typography>
              </Box>
            </Box>
          </Box>
        ) : (
          <Box sx={{ py: 2, textAlign: 'center' }}>
            <Typography variant="body2" color="text.secondary">No portfolio assets to calculate leverage breakdown.</Typography>
          </Box>
        )}
      </Card>

      {/* Health Metrics & Ratios */}
      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' },
          gap: 2.5,
        }}
      >
        {/* Leverage Ratio Card */}
        <Card sx={{ p: 2.5, borderRadius: 3, border: `1px solid ${theme.palette.divider}` }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 1 }}>
            <Typography variant="body2" sx={{ fontWeight: 600, color: 'text.secondary', textTransform: 'uppercase', fontSize: '0.72rem', letterSpacing: 0.8 }}>
              Debt-to-Asset Ratio
            </Typography>
            <Tooltip title="Formula: (Total Liabilities / Total Assets) * 100. Measures the percentage of your portfolio funded by debt. Keeping this ratio low (under 30%) minimizes financial risk." arrow>
              <InfoIcon sx={{ fontSize: '0.85rem', color: 'text.secondary', cursor: 'pointer' }} />
            </Tooltip>
          </Box>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', mb: 1 }}>
            <Typography variant="h5" sx={{ fontWeight: 800, fontFamily: '"Space Grotesk", sans-serif' }}>
              {debtToAssetRatio.toFixed(1)}%
            </Typography>
            <Typography variant="caption" sx={{ fontWeight: 700, color: getStatusColor(leverageStatusType) }}>
              {leverageStatusLabel}
            </Typography>
          </Box>
          <LinearProgress
            variant="determinate"
            value={Math.min(100, debtToAssetRatio)}
            sx={{
              height: 6,
              borderRadius: 3,
              bgcolor: alpha(theme.palette.divider, 0.4),
              '& .MuiLinearProgress-bar': {
                bgcolor: getStatusColor(leverageStatusType),
              },
              mb: 1.5,
            }}
          />
          <Typography variant="caption" color="text.secondary" sx={{ display: 'block', lineHeight: 1.3, fontWeight: 500 }}>
            Calculates total leverage. Healthy limits are under 30%. Over 50% means you are heavily debt-financed.
          </Typography>
        </Card>

        {/* Liquidity Ratio Card */}
        <Card sx={{ p: 2.5, borderRadius: 3, border: `1px solid ${theme.palette.divider}` }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 1 }}>
            <Typography variant="body2" sx={{ fontWeight: 600, color: 'text.secondary', textTransform: 'uppercase', fontSize: '0.72rem', letterSpacing: 0.8 }}>
              Portfolio Liquidity Ratio
            </Typography>
            <Tooltip title="Formula: (Liquid Assets / Total Assets) * 100. Liquid assets include Cash & Bank and Equities, which can be quickly converted to cash. Higher liquidity (15-35%) protects against emergency cash needs." arrow>
              <InfoIcon sx={{ fontSize: '0.85rem', color: 'text.secondary', cursor: 'pointer' }} />
            </Tooltip>
          </Box>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', mb: 1 }}>
            <Typography variant="h5" sx={{ fontWeight: 800, fontFamily: '"Space Grotesk", sans-serif' }}>
              {liquidityRatio.toFixed(1)}%
            </Typography>
            <Typography variant="caption" sx={{ fontWeight: 700, color: getStatusColor(liquidityStatusType) }}>
              {liquidityStatusLabel}
            </Typography>
          </Box>
          <LinearProgress
            variant="determinate"
            value={Math.min(100, liquidityRatio)}
            color={liquidityStatusType === 'SUCCESS' ? 'success' : 'warning'}
            sx={{
              height: 6,
              borderRadius: 3,
              bgcolor: alpha(theme.palette.divider, 0.4),
              mb: 1.5,
            }}
          />
          <Typography variant="caption" color="text.secondary" sx={{ display: 'block', lineHeight: 1.3, fontWeight: 500 }}>
            Represents the proportion of liquid assets (Cash/Bank & Equity) in your portfolio. Ideal targets: 15% to 35%.
          </Typography>
        </Card>
      </Box>
    </Box>
  );
}
