import { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CircularProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Divider,
  useTheme,
  alpha,
  Tooltip,
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  TrendingFlat as TrendingFlatIcon,
  AccountBalanceWallet as NetWorthIcon,
  ArrowUpward as AssetsIcon,
  ArrowDownward as LiabilitiesIcon,
  InfoOutlined as InfoIcon,
} from '@mui/icons-material';
import {
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
  Legend,
  Line,
  ComposedChart,
} from 'recharts';
import { emsClient } from '@/api/clients/ems-client';
import type { WealthSummary, HistoricalNetWorthPoint } from '@/types/wealth';
import { formatCurrency, formatCompactRupees } from '@/utils/formatters';
import { toast } from 'sonner';

export default function NetWorthTab() {
  const theme = useTheme();
  const isDark = theme.palette.mode === 'dark';

  const [summary, setSummary] = useState<WealthSummary | null>(null);
  const [history, setHistory] = useState<HistoricalNetWorthPoint[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadWealthData() {
      try {
        setLoading(true);
        const [sumRes, histRes] = await Promise.all([
          emsClient.getWealthSummary(),
          emsClient.getHistoricalNetWorth(12),
        ]);
        setSummary(sumRes);
        setHistory(histRes);
        setError(null);
      } catch (err: any) {
        console.error(err);
        setError('Failed to load wealth data');
        toast.error('Error fetching net worth details');
      } finally {
        setLoading(false);
      }
    }
    loadWealthData();
  }, []);

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', py: 8 }}>
        <CircularProgress size={40} />
      </Box>
    );
  }

  if (error || !summary) {
    return (
      <Box sx={{ py: 4, textAlgin: 'center' }}>
        <Typography color="error">{error || 'Something went wrong.'}</Typography>
      </Box>
    );
  }

  // Calculate MoM net worth change
  let nwChangePercent = 0;
  let nwChangeAmount = 0;
  if (history.length >= 2) {
    const current = history[history.length - 1].netWorth;
    const previous = history[history.length - 2].netWorth;
    nwChangeAmount = current - previous;
    if (previous !== 0) {
      nwChangePercent = (nwChangeAmount / Math.abs(previous)) * 100;
    }
  }

  const getMoMIcon = (val: number) => {
    if (val > 0) return <TrendingUpIcon sx={{ color: 'success.main', fontSize: '1.2rem', mr: 0.5 }} />;
    if (val < 0) return <TrendingDownIcon sx={{ color: 'error.main', fontSize: '1.2rem', mr: 0.5 }} />;
    return <TrendingFlatIcon sx={{ color: 'text.secondary', fontSize: '1.2rem', mr: 0.5 }} />;
  };

  const getMoMColor = (val: number) => {
    if (val > 0) return 'success.main';
    if (val < 0) return 'error.main';
    return 'text.secondary';
  };

  // Process ticks for XAxis
  const getTicks = (points: HistoricalNetWorthPoint[]) => {
    if (points.length <= 6) return points.map((p) => p.date);
    return points.filter((_, idx) => idx % 2 === 0).map((p) => p.date);
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3, mt: 1 }}>
      {/* Summary Cards */}
      {/* Summary Cards */}
      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: { xs: '1fr', md: '1fr 1fr 1fr' },
          gap: 2.5,
        }}
      >
        {/* Net Worth Card */}
        <Card
          sx={{
            p: 2.5,
            borderRadius: 3,
            position: 'relative',
            overflow: 'hidden',
            background: isDark
              ? `linear-gradient(135deg, ${alpha(theme.palette.primary.main, 0.15)} 0%, ${alpha(theme.palette.background.paper, 0.4)} 100%)`
              : `linear-gradient(135deg, ${alpha(theme.palette.primary.main, 0.05)} 0%, ${theme.palette.background.paper} 100%)`,
            border: `1px solid ${alpha(theme.palette.primary.main, 0.2)}`,
            boxShadow: isDark ? `0 4px 20px ${alpha(theme.palette.common.black, 0.5)}` : 'none',
          }}
        >
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
              <Typography variant="body2" sx={{ fontWeight: 600, color: 'text.secondary', textTransform: 'uppercase', fontSize: '0.72rem', letterSpacing: 0.8 }}>
                Current Net Worth
              </Typography>
              <Tooltip title="Formula: Total Assets - Total Liabilities. The net measure of your overall financial wealth." arrow>
                <InfoIcon sx={{ fontSize: '0.8rem', color: 'text.secondary', cursor: 'pointer' }} />
              </Tooltip>
            </Box>
            <NetWorthIcon sx={{ color: theme.palette.primary.main, opacity: 0.8 }} />
          </Box>
          <Typography variant="h4" sx={{ fontWeight: 800, fontFamily: '"Space Grotesk", sans-serif', mb: 1, color: theme.palette.primary.main }}>
            {formatCurrency(summary.netWorth)}
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            {getMoMIcon(nwChangeAmount)}
            <Typography variant="caption" sx={{ fontWeight: 600, color: getMoMColor(nwChangeAmount) }}>
              {nwChangeAmount >= 0 ? '+' : ''}
              {formatCurrency(nwChangeAmount)} ({nwChangePercent.toFixed(1)}% MoM)
            </Typography>
          </Box>
        </Card>

        {/* Total Assets Card */}
        <Card
          sx={{
            p: 2.5,
            borderRadius: 3,
            background: theme.palette.background.paper,
            border: `1px solid ${theme.palette.divider}`,
          }}
        >
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
              <Typography variant="body2" sx={{ fontWeight: 600, color: 'text.secondary', textTransform: 'uppercase', fontSize: '0.72rem', letterSpacing: 0.8 }}>
                Total Assets
              </Typography>
              <Tooltip title="The sum of all your self-owned property and investments (e.g. Cash, Bank Accounts, Equities, Real Estate, Commodities)." arrow>
                <InfoIcon sx={{ fontSize: '0.8rem', color: 'text.secondary', cursor: 'pointer' }} />
              </Tooltip>
            </Box>
            <AssetsIcon sx={{ color: theme.palette.success.main, opacity: 0.8 }} />
          </Box>
          <Typography variant="h4" sx={{ fontWeight: 800, fontFamily: '"Space Grotesk", sans-serif', mb: 1 }}>
            {formatCurrency(summary.totalAssets)}
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 500 }}>
              Invested: {formatCurrency(summary.totalInvestedAssets)} | Returns:{' '}
              <Box component="span" sx={{ color: summary.totalReturnsAssets >= 0 ? 'success.main' : 'error.main', fontWeight: 600 }}>
                {summary.totalReturnsAssets >= 0 ? '+' : ''}
                {summary.percentageReturnsAssets.toFixed(1)}%
              </Box>
            </Typography>
          </Box>
        </Card>

        {/* Total Liabilities Card */}
        <Card
          sx={{
            p: 2.5,
            borderRadius: 3,
            background: theme.palette.background.paper,
            border: `1px solid ${theme.palette.divider}`,
          }}
        >
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
              <Typography variant="body2" sx={{ fontWeight: 600, color: 'text.secondary', textTransform: 'uppercase', fontSize: '0.72rem', letterSpacing: 0.8 }}>
                Total Liabilities
              </Typography>
              <Tooltip title="The sum of all your outstanding borrowed funds and financial obligations (e.g. Secured Loans, Unsecured Loans, Credit Cards)." arrow>
                <InfoIcon sx={{ fontSize: '0.8rem', color: 'text.secondary', cursor: 'pointer' }} />
              </Tooltip>
            </Box>
            <LiabilitiesIcon sx={{ color: theme.palette.error.main, opacity: 0.8 }} />
          </Box>
          <Typography variant="h4" sx={{ fontWeight: 800, fontFamily: '"Space Grotesk", sans-serif', mb: 1 }}>
            {formatCurrency(summary.totalLiabilities)}
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 500 }}>
              Repaid: {formatCurrency(summary.totalRepaidLiabilities)} | Interest Accrued: {formatCurrency(summary.accumulatedInterestLiabilities)}
            </Typography>
          </Box>
        </Card>
      </Box>

      {/* Chart Panel */}
      <Card sx={{ p: 3, borderRadius: 3, border: `1px solid ${theme.palette.divider}` }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 2.5 }}>
          <Typography variant="subtitle1" sx={{ fontWeight: 700, fontFamily: '"Space Grotesk", sans-serif' }}>
            Historical Portfolio Trajectory
          </Typography>
          <Tooltip title="Visualizes the month-over-month trends of your total assets, outstanding liabilities, and net worth over the last 12 months." arrow>
            <InfoIcon sx={{ fontSize: '0.9rem', color: 'text.secondary', cursor: 'pointer' }} />
          </Tooltip>
        </Box>
        {history.length > 0 ? (
          <Box sx={{ width: '100%', height: 350 }}>
            <ResponsiveContainer width="100%" height="100%">
              <ComposedChart data={history} margin={{ top: 15, right: 10, left: 10, bottom: 5 }}>
                <defs>
                  <linearGradient id="colorAssets" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor={theme.palette.success.main} stopOpacity={0.2} />
                    <stop offset="95%" stopColor={theme.palette.success.main} stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="colorLiabilities" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor={theme.palette.error.main} stopOpacity={0.2} />
                    <stop offset="95%" stopColor={theme.palette.error.main} stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke={theme.palette.divider} />
                <XAxis
                  dataKey="date"
                  stroke={theme.palette.text.secondary}
                  style={{ fontSize: '0.75rem', fontFamily: '"Space Grotesk", sans-serif', fontWeight: 500 }}
                  ticks={getTicks(history)}
                  tickMargin={8}
                  tickFormatter={(dateStr) => {
                    if (!dateStr) return '';
                    const parts = dateStr.split('-');
                    if (parts.length < 2) return dateStr;
                    const [y, m] = parts;
                    const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
                    return `${months[parseInt(m, 10) - 1]} '${y.slice(2)}`;
                  }}
                />
                <YAxis
                  stroke={theme.palette.text.secondary}
                  style={{ fontSize: '0.75rem', fontFamily: '"Space Grotesk", sans-serif', fontWeight: 500 }}
                  tickFormatter={(val) => formatCompactRupees(val)}
                  width={75}
                  tickMargin={8}
                />
                <RechartsTooltip
                  formatter={(value: any, name: any) => [formatCurrency(Number(value)), name]}
                  contentStyle={{
                    backgroundColor: theme.palette.background.paper,
                    borderColor: theme.palette.divider,
                    borderRadius: 8,
                    color: theme.palette.text.primary,
                    fontFamily: '"Space Grotesk", sans-serif',
                    fontSize: '0.78rem',
                  }}
                />
                <Legend wrapperStyle={{ fontSize: '0.78rem', fontFamily: '"Space Grotesk", sans-serif', fontWeight: 500, paddingTop: 10 }} />
                <Area
                  name="Total Assets"
                  type="monotone"
                  dataKey="totalAssets"
                  stroke={theme.palette.success.main}
                  strokeWidth={2}
                  fillOpacity={1}
                  fill="url(#colorAssets)"
                />
                <Area
                  name="Total Liabilities"
                  type="monotone"
                  dataKey="totalLiabilities"
                  stroke={theme.palette.error.main}
                  strokeWidth={2}
                  fillOpacity={1}
                  fill="url(#colorLiabilities)"
                />
                <Line
                  name="Net Worth"
                  type="monotone"
                  dataKey="netWorth"
                  stroke={theme.palette.primary.main}
                  strokeWidth={3}
                  dot={{ r: 4, strokeWidth: 1 }}
                  activeDot={{ r: 6 }}
                />
              </ComposedChart>
            </ResponsiveContainer>
          </Box>
        ) : (
          <Box sx={{ py: 6, textAlign: 'center' }}>
            <Typography variant="body2" color="text.secondary">
              Not enough historical data to display trajectory chart.
            </Typography>
          </Box>
        )}
      </Card>

      {/* Ledger History Table */}
      <Card sx={{ borderRadius: 3, border: `1px solid ${theme.palette.divider}`, overflow: 'hidden' }}>
        <Box sx={{ p: 2.5, display: 'flex', alignItems: 'center', gap: 0.5 }}>
          <Typography variant="subtitle1" sx={{ fontWeight: 700, fontFamily: '"Space Grotesk", sans-serif' }}>
            Historical Net Worth Ledger
          </Typography>
          <Tooltip title="A detailed table showing month-over-month values of your assets, liabilities, net worth, and percentage change." arrow>
            <InfoIcon sx={{ fontSize: '0.9rem', color: 'text.secondary', cursor: 'pointer' }} />
          </Tooltip>
        </Box>
        <Divider />
        <TableContainer component={Paper} elevation={0} sx={{ maxHeight: 350, bgcolor: 'transparent' }}>
          <Table stickyHeader size="small">
            <TableHead>
              <TableRow>
                <TableCell sx={{ fontWeight: 700, bgcolor: 'background.paper' }}>Month</TableCell>
                <TableCell align="right" sx={{ fontWeight: 700, bgcolor: 'background.paper' }}>Total Assets</TableCell>
                <TableCell align="right" sx={{ fontWeight: 700, bgcolor: 'background.paper' }}>Total Liabilities</TableCell>
                <TableCell align="right" sx={{ fontWeight: 700, bgcolor: 'background.paper' }}>Net Worth</TableCell>
                <TableCell align="right" sx={{ fontWeight: 700, bgcolor: 'background.paper' }}>Change (MoM)</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {[...history].reverse().map((row, idx, arr) => {
                let changePct = 0;
                let changeAmt = 0;
                if (idx < arr.length - 1) {
                  const prev = arr[idx + 1].netWorth;
                  changeAmt = row.netWorth - prev;
                  if (prev !== 0) {
                    changePct = (changeAmt / Math.abs(prev)) * 100;
                  }
                }
                const parts = row.date.split('-');
                const monthNames = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
                const displayMonth = parts.length === 2 ? `${monthNames[parseInt(parts[1], 10) - 1]} ${parts[0]}` : row.date;

                return (
                  <TableRow key={row.date} sx={{ '&:last-child td, &:last-child th': { border: 0 } }}>
                    <TableCell sx={{ fontWeight: 600 }}>{displayMonth}</TableCell>
                    <TableCell align="right">{formatCurrency(row.totalAssets)}</TableCell>
                    <TableCell align="right" sx={{ color: 'error.main' }}>{formatCurrency(row.totalLiabilities)}</TableCell>
                    <TableCell align="right" sx={{ fontWeight: 700, color: theme.palette.primary.main }}>
                      {formatCurrency(row.netWorth)}
                    </TableCell>
                    <TableCell align="right">
                      {idx < arr.length - 1 ? (
                        <Box sx={{ display: 'inline-flex', alignItems: 'center', fontWeight: 600, color: getMoMColor(changeAmt) }}>
                          {changeAmt > 0 ? '+' : ''}
                          {changePct.toFixed(1)}%
                        </Box>
                      ) : (
                        <Typography variant="body2" color="text.secondary">—</Typography>
                      )}
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </TableContainer>
      </Card>
    </Box>
  );
}
