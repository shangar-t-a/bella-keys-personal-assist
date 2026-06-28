import { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Container,
  Typography,
  Card,
  CardContent,
  Button,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Chip,
  LinearProgress,
  Tooltip as MuiTooltip,
  Paper,
  OutlinedInput,
} from '@mui/material';
import { Grid } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import {
  Add as Plus,
  Edit,
  Delete as Trash2,
  SwapHoriz,
  ArrowUpward,
  ArrowDownward,
  Block,
  Settings,
} from '@mui/icons-material';
import { toast } from 'sonner';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';
import { emsClient } from '@/api/clients/ems-client';
import type {
  AccountNameResponse,
  SavingsBucketResponse,
  SavingsBucketTransactionResponse,
} from '@/types/api';
import { formatCurrency, formatCompactRupees } from '@/utils/formatters';

// Colors for the donut chart — harmonized with the premium palette
const COLORS = ['#1a8fc4', '#48b1e0', '#1a9a6b', '#e29624', '#8b6cc4', '#2ba8a4', '#6366f1', '#d94052'];

export default function SavingsFundSegregatorPage() {
  const navigate = useNavigate();
  // States
  const [accounts, setAccounts] = useState<AccountNameResponse[]>([]);
  const [selectedAccountId, setSelectedAccountId] = useState<string>('');
  const [buckets, setBuckets] = useState<SavingsBucketResponse[]>([]);
  const [transactions, setTransactions] = useState<SavingsBucketTransactionResponse[]>([]);
  const [totalTxs, setTotalTxs] = useState<number>(0);
  const [page, setPage] = useState<number>(0);
  const [rowsPerPage, setRowsPerPage] = useState<number>(10);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  // Modals
  const [isBucketModalOpen, setIsBucketModalOpen] = useState(false);
  const [bucketEditId, setBucketEditId] = useState<string | null>(null);
  const [bucketName, setBucketName] = useState('');
  const [bucketTarget, setBucketTarget] = useState<string>('');
  const [isDeleteBucketModalOpen, setIsDeleteBucketModalOpen] = useState(false);
  const [bucketToDeleteId, setBucketToDeleteId] = useState<string | null>(null);

  const [isTxModalOpen, setIsTxModalOpen] = useState(false);
  const [txType, setTxType] = useState<string>('allocate'); // 'deposit', 'withdraw', 'allocate', 'release', 'transfer'
  const [txSourceId, setTxSourceId] = useState<string>('');
  const [txDestId, setTxDestId] = useState<string>('');
  const [txAmount, setTxAmount] = useState<string>('');
  const [txDescription, setTxDescription] = useState<string>('');
  const [txDate, setTxDate] = useState<string>('');

  // Cancellation States
  const [isCancelModalOpen, setIsCancelModalOpen] = useState(false);
  const [selectedTx, setSelectedTx] = useState<SavingsBucketTransactionResponse | null>(null);
  const [cancelReason, setCancelReason] = useState('');



  // Data Fetching
  const fetchAccounts = async (keepSelection = false) => {
    try {
      const data = await emsClient.getAllAccounts();
      setAccounts(data);
      if (data.length > 0) {
        const exists = data.some(acc => acc.id === selectedAccountId);
        if (keepSelection && selectedAccountId && exists) {
          // Keep current selection
        } else {
          setSelectedAccountId(data[0].id);
        }
      } else {
        setSelectedAccountId('');
      }
    } catch {
      toast.error('Failed to fetch bank accounts');
    }
  };

  const fetchDetails = useCallback(async () => {
    if (!selectedAccountId) return;
    setIsLoading(true);
    try {
      // 1. Fetch Buckets
      const bucketList = await emsClient.getSavingsBuckets(selectedAccountId);
      setBuckets(bucketList);

      // 2. Fetch Ledger Transactions
      const txData = await emsClient.getSavingsBucketTransactions(
        selectedAccountId,
        rowsPerPage,
        page * rowsPerPage
      );
      setTransactions(txData.transactions);
      setTotalTxs(txData.totalElements);
    } catch {
      toast.error('Failed to load fund segregation details');
    } finally {
      setIsLoading(false);
    }
  }, [selectedAccountId, page, rowsPerPage]);

  useEffect(() => {
    fetchAccounts();
  }, []);

  useEffect(() => {
    fetchDetails();
  }, [fetchDetails]);

  // Calculations
  const totalSavings = buckets.reduce((sum, b) => sum + b.allocatedAmount, 0);
  const savingsBucket = buckets.find((b) => b.name === 'Savings');
  const unallocatedSavings = savingsBucket ? savingsBucket.allocatedAmount : 0.0;
  const allocatedFunds = totalSavings - unallocatedSavings;

  // Chart data
  const chartData = buckets
    .filter((b) => b.allocatedAmount > 0)
    .map((b) => ({
      name: b.name,
      value: b.allocatedAmount,
    }));

  // Handlers
  const handleOpenBucketModal = (bucket?: SavingsBucketResponse) => {
    if (bucket) {
      setBucketEditId(bucket.id);
      setBucketName(bucket.name);
      setBucketTarget(bucket.targetAmount ? String(bucket.targetAmount) : '');
    } else {
      setBucketEditId(null);
      setBucketName('');
      setBucketTarget('');
    }
    setIsBucketModalOpen(true);
  };

  const handleSaveBucket = async () => {
    if (!bucketName.trim()) {
      toast.error('Bucket name is required');
      return;
    }
    if (bucketName.trim().toLowerCase() === 'savings' && (!bucketEditId || buckets.find(b => b.id === bucketEditId)?.name !== 'Savings')) {
      toast.error('Cannot create another bucket named Savings');
      return;
    }
    
    const targetVal = bucketTarget ? parseFloat(bucketTarget) : null;
    if (targetVal !== null && (isNaN(targetVal) || targetVal < 0)) {
      toast.error('Target amount must be a positive number');
      return;
    }

    try {
      if (bucketEditId) {
        // Edit
        await emsClient.updateSavingsBucket(bucketEditId, {
          name: bucketName,
          targetAmount: targetVal,
        });
        toast.success('Bucket updated successfully');
      } else {
        // Create
        await emsClient.createSavingsBucket(selectedAccountId, {
          name: bucketName,
          targetAmount: targetVal,
        });
        toast.success('Bucket created successfully');
      }
      setIsBucketModalOpen(false);
      fetchDetails();
    } catch (e: any) {
      toast.error(e.message || 'Failed to save bucket');
    }
  };

  const handleDeleteBucket = (bucketId: string) => {
    setBucketToDeleteId(bucketId);
    setIsDeleteBucketModalOpen(true);
  };

  const handleConfirmDeleteBucket = async () => {
    if (!bucketToDeleteId) return;
    try {
      await emsClient.deleteSavingsBucket(bucketToDeleteId);
      toast.success('Bucket deleted, balance refunded to Savings');
      setIsDeleteBucketModalOpen(false);
      setBucketToDeleteId(null);
      fetchDetails();
    } catch (e: any) {
      toast.error(e.message || 'Failed to delete bucket');
    }
  };

  const handleOpenTxModal = (type: string = 'allocate') => {
    setTxType(type);
    setTxAmount('');
    setTxDescription('');
    setTxDate('');

    // Pre-populate default source/destinations based on type
    const rootBucket = buckets.find(b => b.name === 'Savings');
    if (type === 'allocate') {
      setTxSourceId(rootBucket?.id || '');
      setTxDestId('');
    } else if (type === 'release') {
      setTxSourceId('');
      setTxDestId(rootBucket?.id || '');
    } else if (type === 'deposit') {
      setTxSourceId('');
      setTxDestId(rootBucket?.id || '');
    } else if (type === 'withdraw') {
      setTxSourceId(rootBucket?.id || '');
      setTxDestId('');
    } else {
      setTxSourceId('');
      setTxDestId('');
    }

    setIsTxModalOpen(true);
  };

  const handleSaveTx = async () => {
    const amountVal = parseFloat(txAmount);
    if (isNaN(amountVal) || amountVal <= 0) {
      toast.error('Transaction amount must be a positive number');
      return;
    }
    if (!txDescription.trim()) {
      toast.error('Transaction comment is required for auditing');
      return;
    }

    // Set correct source and destination ids based on type
    let finalSourceId: string | null = txSourceId || null;
    let finalDestId: string | null = txDestId || null;

    if (txType === 'deposit') {
      finalSourceId = null;
    } else if (txType === 'withdraw') {
      finalDestId = null;
    }

    try {
      await emsClient.createSavingsBucketTransaction(selectedAccountId, {
        sourceBucketId: finalSourceId,
        destinationBucketId: finalDestId,
        amount: amountVal,
        transactionType: txType,
        description: txDescription,
        transactionDate: txDate ? new Date(txDate).toISOString() : null,
      });
      toast.success('Transaction logged successfully');
      setIsTxModalOpen(false);
      fetchDetails();
    } catch (e: any) {
      toast.error(e.message || 'Failed to process transaction');
    }
  };

  const handleOpenCancelModal = (tx: SavingsBucketTransactionResponse) => {
    setSelectedTx(tx);
    setCancelReason('');
    setIsCancelModalOpen(true);
  };

  const handleConfirmCancel = async () => {
    if (!selectedTx || !cancelReason.trim()) return;
    try {
      await emsClient.cancelSavingsBucketTransaction(selectedTx.id, { reason: cancelReason });
      toast.success('Transaction cancelled and balances reversed successfully');
      setIsCancelModalOpen(false);
      setCancelReason('');
      setSelectedTx(null);
      fetchDetails();
    } catch (e: any) {
      toast.error(e.message || 'Failed to cancel transaction');
    }
  };

  // Helper Resolvers
  const getBucketNameById = (id: string | null) => {
    if (!id) return '-';
    const b = buckets.find(x => x.id === id);
    return b ? b.name : 'Unknown';
  };

  return (
    <Box
      sx={{
        flexGrow: 1,
        bgcolor: 'background.default',
        py: 2.5,
        px: { xs: 2, md: 4 },
        backgroundImage: (theme) =>
          theme.palette.mode === 'dark'
            ? 'radial-gradient(circle at 10% 20%, rgba(30, 41, 59, 0.4) 0%, rgba(17, 24, 39, 0.95) 90%)'
            : 'none',
        transition: 'background-color 0.3s ease',
        minHeight: '100vh',
      }}
    >
      <Container maxWidth="xl">
        {isLoading && <LinearProgress sx={{ mb: 2, borderRadius: 1 }} />}

        {/* Header Block */}
        <Box sx={{ mb: 2, display: 'flex', flexDirection: { xs: 'column', sm: 'row' }, justifyContent: 'space-between', alignItems: { xs: 'flex-start', sm: 'center' }, gap: 2 }}>
          <Box>
            <Typography
              variant="h5"
              sx={{ fontWeight: 700, fontFamily: '"Space Grotesk", sans-serif', lineHeight: 1.2 }}
            >
              Savings Envelopes
            </Typography>
            <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 500 }}>
              Partition and track allocations in your savings accounts for medical, insurance, and goals.
            </Typography>
          </Box>

          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <FormControl sx={{ minWidth: 200 }} size="small">
              <InputLabel id="bank-account-select-label">Bank Account</InputLabel>
              <Select
                labelId="bank-account-select-label"
                value={selectedAccountId}
                label="Bank Account"
                input={<OutlinedInput label="Bank Account" sx={{ borderRadius: 1.5, fontSize: '0.85rem' }} />}
                onChange={(e) => {
                  setSelectedAccountId(e.target.value);
                  setPage(0);
                }}
              >
                {accounts.map((acc) => (
                  <MenuItem key={acc.id} value={acc.id}>
                    {acc.accountName}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            <MuiTooltip title="Manage Accounts">
              <IconButton
                size="small"
                onClick={() => navigate('/settings?tab=accounts')}
                color="primary"
              >
                <Settings fontSize="small" />
              </IconButton>
            </MuiTooltip>
          </Box>
        </Box>

        {/* Summary Card: Prominent Portfolio Metrics */}
        <Card variant="outlined" sx={{ borderRadius: 2, border: '1px solid', borderColor: 'divider', boxShadow: 'none', mb: 2 }}>
          <Grid container>
            {/* Block 1: Total Savings */}
            <Grid size={{ xs: 12, md: 4 }} sx={{
              p: 2.5,
              borderRight: { xs: 'none', md: '1px solid' },
              borderRightColor: { xs: 'transparent', md: 'divider' },
              borderBottom: { xs: '1px solid', md: 'none' },
              borderBottomColor: { xs: 'divider', md: 'transparent' },
            }}>
              <Typography variant="caption" color="text.disabled" sx={{ fontWeight: 600, textTransform: 'uppercase', letterSpacing: 0.8, fontSize: '0.68rem', display: 'block', mb: 0.5 }}>
                Total Savings
              </Typography>
              <Typography variant="h5" sx={{ fontWeight: 700, fontFamily: '"Space Grotesk", sans-serif', color: 'text.primary', fontSize: '1.3rem' }}>
                {formatCompactRupees(totalSavings)}
              </Typography>
            </Grid>

            {/* Block 2: Allocated Envelopes */}
            <Grid size={{ xs: 12, md: 4 }} sx={{
              p: 2.5,
              borderRight: { xs: 'none', md: '1px solid' },
              borderRightColor: { xs: 'transparent', md: 'divider' },
              borderBottom: { xs: '1px solid', md: 'none' },
              borderBottomColor: { xs: 'divider', md: 'transparent' },
            }}>
              <Typography variant="caption" color="text.disabled" sx={{ fontWeight: 600, textTransform: 'uppercase', letterSpacing: 0.8, fontSize: '0.68rem', display: 'block', mb: 0.5 }}>
                Allocated Envelopes
              </Typography>
              <Typography variant="h5" sx={{ fontWeight: 700, fontFamily: '"Space Grotesk", sans-serif', color: 'primary.main', fontSize: '1.3rem' }}>
                {formatCompactRupees(allocatedFunds)}
              </Typography>
            </Grid>

            {/* Block 3: Free Savings */}
            <Grid size={{ xs: 12, md: 4 }} sx={{ p: 2.5 }}>
              <Typography variant="caption" color="text.disabled" sx={{ fontWeight: 600, textTransform: 'uppercase', letterSpacing: 0.8, fontSize: '0.68rem', display: 'block', mb: 0.5 }}>
                Free Savings (Unallocated)
              </Typography>
              <Typography variant="h5" sx={{ fontWeight: 700, fontFamily: '"Space Grotesk", sans-serif', color: 'success.main', fontSize: '1.3rem' }}>
                {formatCompactRupees(unallocatedSavings)}
              </Typography>
            </Grid>
          </Grid>
        </Card>

        {/* Main Layout: Visual Chart & Bucket List */}
        <Grid container spacing={3} sx={{ mb: 2 }}>
          {/* Visual Donut Chart */}
          <Grid size={{ xs: 12, lg: 4 }}>
            <Card variant="outlined" sx={{ height: '100%', borderRadius: 2, border: '1px solid', borderColor: 'divider', boxShadow: 'none' }}>
              <CardContent sx={{ p: 3, display: 'flex', flexDirection: 'column', height: '100%' }}>
                <Typography variant="body2" sx={{ fontWeight: 700, fontFamily: '"Space Grotesk", sans-serif', textTransform: 'uppercase', letterSpacing: 0.5, color: 'text.secondary', mb: 2 }}>
                  Allocation Split
                </Typography>
                {chartData.length === 0 ? (
                  <Box sx={{ display: 'flex', flexGrow: 1, alignItems: 'center', justifyContent: 'center', height: 260, color: 'text.secondary' }}>
                    No funds allocated yet
                  </Box>
                ) : (
                  <Box sx={{ width: '100%', height: 280, position: 'relative' }}>
                    <ResponsiveContainer width="100%" height="100%" minWidth={0} minHeight={0}>
                      <PieChart>
                        <Pie
                          data={chartData}
                          cx="50%"
                          cy="50%"
                          innerRadius={60}
                          outerRadius={90}
                          paddingAngle={3}
                          dataKey="value"
                        >
                          {chartData.map((_entry, index) => (
                            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                          ))}
                        </Pie>
                        <Tooltip formatter={(value) => formatCurrency(Number(value))} />
                      </PieChart>
                    </ResponsiveContainer>
                    {/* Dynamic legend split */}
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1.5, justifyContent: 'center', mt: 2 }}>
                      {chartData.map((entry, idx) => {
                        const pct = ((entry.value / totalSavings) * 100).toFixed(1);
                        return (
                          <Box key={entry.name} sx={{ display: 'flex', alignItems: 'center', gap: 0.75 }}>
                            <Box sx={{ width: 8, height: 8, borderRadius: '50%', bgcolor: COLORS[idx % COLORS.length] }} />
                            <Typography variant="caption" sx={{ fontWeight: 600 }}>
                              {entry.name} ({pct}%)
                            </Typography>
                          </Box>
                        );
                      })}
                    </Box>
                  </Box>
                )}
              </CardContent>
            </Card>
          </Grid>

          {/* Envelopes list */}
          <Grid size={{ xs: 12, lg: 8 }}>
            <Card variant="outlined" sx={{ height: '100%', borderRadius: 2, border: '1px solid', borderColor: 'divider', boxShadow: 'none' }}>
              <CardContent sx={{ p: 3 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
                  <Typography variant="body2" sx={{ fontWeight: 700, fontFamily: '"Space Grotesk", sans-serif', textTransform: 'uppercase', letterSpacing: 0.5, color: 'text.secondary' }}>
                    My Envelopes
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 1.5 }}>
                    <Button
                      variant="outlined"
                      color="inherit"
                      size="small"
                      startIcon={<Plus />}
                      onClick={() => handleOpenBucketModal()}
                      sx={{ py: 0.6, px: 2, fontWeight: 600, textTransform: 'none', borderRadius: 1.5, fontSize: '0.85rem' }}
                    >
                      Create Bucket
                    </Button>
                    <Button
                      variant="contained"
                      color="primary"
                      size="small"
                      startIcon={<SwapHoriz />}
                      onClick={() => handleOpenTxModal('allocate')}
                      sx={{ py: 0.6, px: 2, fontWeight: 600, textTransform: 'none', borderRadius: 1.5, fontSize: '0.85rem' }}
                    >
                      Move Money
                    </Button>
                  </Box>
                </Box>

                <Grid container spacing={2}>
                  {buckets.map((b) => {
                    const isRoot = b.name === 'Savings';
                    const targetPercent = b.targetAmount ? Math.min((b.allocatedAmount / b.targetAmount) * 100, 100) : 0;

                    return (
                      <Grid size={{ xs: 12, sm: 6 }} key={b.id}>
                        <Card variant="outlined" sx={{ borderRadius: 2, p: 2, position: 'relative', borderLeft: `4px solid ${isRoot ? '#10b981' : '#6366f1'}`, boxShadow: 'none' }}>
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                            <Box>
                              <Typography variant="body2" sx={{ fontWeight: 700 }}>
                                {b.name}
                              </Typography>
                              <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, display: 'block' }}>
                                {isRoot ? 'General Cash Pool' : 'Special Bucket'}
                              </Typography>
                            </Box>
                            
                            {!isRoot && (
                              <Box sx={{ display: 'flex', gap: 0.5 }}>
                                <MuiTooltip title="Edit">
                                  <IconButton size="small" color="secondary" onClick={() => handleOpenBucketModal(b)}>
                                    <Edit fontSize="small" />
                                  </IconButton>
                                </MuiTooltip>
                                <MuiTooltip title="Delete">
                                  <IconButton size="small" color="error" onClick={() => handleDeleteBucket(b.id)}>
                                    <Trash2 fontSize="small" />
                                  </IconButton>
                                </MuiTooltip>
                              </Box>
                            )}
                          </Box>

                          <Box sx={{ my: 1.5 }}>
                            <Typography variant="h6" sx={{ fontWeight: 800, fontFamily: '"Space Grotesk", sans-serif' }}>
                              {formatCurrency(b.allocatedAmount)}
                            </Typography>
                            {b.targetAmount && (
                              <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 0.5 }}>
                                Target: {formatCurrency(b.targetAmount)} ({targetPercent.toFixed(0)}%)
                              </Typography>
                            )}
                          </Box>

                          {b.targetAmount && (
                            <Box sx={{ mt: 1 }}>
                              <LinearProgress
                                variant="determinate"
                                value={targetPercent}
                                sx={{
                                  height: 4,
                                  borderRadius: 2,
                                  bgcolor: 'rgba(99, 102, 241, 0.1)',
                                  '& .MuiLinearProgress-bar': {
                                    bgcolor: '#6366f1',
                                    borderRadius: 2,
                                  },
                                }}
                              />
                            </Box>
                          )}
                        </Card>
                      </Grid>
                    );
                  })}
                </Grid>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Transaction Ledger Block */}
        <Card variant="outlined" sx={{ borderRadius: 2, overflow: 'hidden', border: '1px solid', borderColor: 'divider', boxShadow: 'none', mb: 2 }}>
          <Box sx={{ p: 2, display: 'flex', flexDirection: { xs: 'column', sm: 'row' }, justifyContent: 'space-between', alignItems: { xs: 'flex-start', sm: 'center' }, gap: 2, borderBottom: '1px solid', borderColor: 'divider' }}>
            <Box>
              <Typography variant="body2" sx={{ fontWeight: 700, fontFamily: '"Space Grotesk", sans-serif', textTransform: 'uppercase', letterSpacing: 0.5, color: 'text.secondary' }}>
                Allocation Ledger
              </Typography>
              <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 500 }}>
                Complete history of allocations, releases, deposits, and transfers.
              </Typography>
            </Box>
            <Box sx={{ display: 'flex', gap: 1.5 }}>
              <Button
                variant="outlined"
                color="success"
                size="small"
                startIcon={<ArrowUpward />}
                onClick={() => handleOpenTxModal('deposit')}
                sx={{ py: 0.6, px: 2, fontWeight: 600, textTransform: 'none', borderRadius: 1.5, fontSize: '0.85rem' }}
              >
                Deposit
              </Button>
              <Button
                variant="outlined"
                color="error"
                size="small"
                startIcon={<ArrowDownward />}
                onClick={() => handleOpenTxModal('withdraw')}
                sx={{ py: 0.6, px: 2, fontWeight: 600, textTransform: 'none', borderRadius: 1.5, fontSize: '0.85rem' }}
              >
                Withdraw
              </Button>
            </Box>
          </Box>

          <TableContainer component={Paper} elevation={0} sx={{ borderRadius: 0, bgcolor: 'transparent' }}>
            <Table size="small">
              <TableHead sx={{ bgcolor: (theme) => theme.palette.mode === 'dark' ? 'rgba(30, 41, 59, 0.5)' : '#f1f5f9' }}>
                <TableRow>
                  <TableCell sx={{ pl: 3, fontWeight: 700, py: 1.25, fontSize: '0.78rem', textTransform: 'uppercase', letterSpacing: 0.5, color: 'text.secondary' }}>Date</TableCell>
                  <TableCell sx={{ fontWeight: 700, py: 1.25, fontSize: '0.78rem', textTransform: 'uppercase', letterSpacing: 0.5, color: 'text.secondary' }}>Type</TableCell>
                  <TableCell sx={{ fontWeight: 700, py: 1.25, fontSize: '0.78rem', textTransform: 'uppercase', letterSpacing: 0.5, color: 'text.secondary' }}>Source Envelope</TableCell>
                  <TableCell sx={{ fontWeight: 700, py: 1.25, fontSize: '0.78rem', textTransform: 'uppercase', letterSpacing: 0.5, color: 'text.secondary' }}>Destination Envelope</TableCell>
                  <TableCell align="right" sx={{ fontWeight: 700, py: 1.25, fontSize: '0.78rem', textTransform: 'uppercase', letterSpacing: 0.5, color: 'text.secondary' }}>Amount</TableCell>
                  <TableCell sx={{ fontWeight: 700, py: 1.25, fontSize: '0.78rem', textTransform: 'uppercase', letterSpacing: 0.5, color: 'text.secondary' }}>Comment</TableCell>
                  <TableCell align="center" sx={{ pr: 3, fontWeight: 700, py: 1.25, fontSize: '0.78rem', textTransform: 'uppercase', letterSpacing: 0.5, color: 'text.secondary' }}>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {transactions.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={7} align="center" sx={{ py: 6, color: 'text.secondary' }}>
                      No transactions logged yet
                    </TableCell>
                  </TableRow>
                ) : (
                  transactions.map((t, idx) => {
                    let typeLabel = t.transactionType.toUpperCase();
                    let typeColor: 'success' | 'error' | 'warning' | 'primary' | 'info' | 'default' = 'primary';
                    let amountPrefix = '';
                    let amountColor = 'text.primary';

                    if (t.transactionType === 'deposit') {
                      typeColor = 'success';
                      amountPrefix = '+';
                      amountColor = 'success.main';
                    } else if (t.transactionType === 'withdraw') {
                      typeColor = 'error';
                      amountPrefix = '-';
                      amountColor = 'error.main';
                    } else if (t.transactionType === 'allocate') {
                      typeColor = 'warning';
                      amountColor = 'text.secondary';
                    } else if (t.transactionType === 'release') {
                      typeColor = 'info';
                      amountColor = 'text.secondary';
                    }

                    if (t.isCancelled) {
                      typeColor = 'default';
                    }

                    return (
                      <TableRow
                        key={t.id}
                        sx={{
                          '& td': { py: 1 },
                          bgcolor: idx % 2 === 0
                            ? 'transparent'
                            : (theme) => theme.palette.mode === 'dark' ? 'rgba(255,255,255,0.018)' : 'rgba(0,0,0,0.018)',
                          '&:hover': { bgcolor: 'action.hover' },
                        }}
                      >
                        <TableCell sx={{ pl: 3, fontWeight: 500, color: t.isCancelled ? 'text.disabled' : 'text.primary' }}>
                          {new Date(t.transactionDate).toLocaleDateString('en-IN', {
                            day: '2-digit',
                            month: 'short',
                            year: 'numeric',
                            hour: '2-digit',
                            minute: '2-digit',
                          })}
                        </TableCell>
                        <TableCell>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Chip label={typeLabel} size="small" color={typeColor} variant="outlined" sx={{ fontWeight: 700, fontSize: '0.68rem', height: 20 }} />
                            {t.isCancelled && (
                              <Chip label="CANCELLED" size="small" color="error" variant="filled" sx={{ fontWeight: 700, fontSize: '0.625rem', height: 18 }} />
                            )}
                          </Box>
                        </TableCell>
                        <TableCell sx={{ fontWeight: 500, color: t.isCancelled ? 'text.disabled' : 'text.primary' }}>{getBucketNameById(t.sourceBucketId)}</TableCell>
                        <TableCell sx={{ fontWeight: 500, color: t.isCancelled ? 'text.disabled' : 'text.primary' }}>{getBucketNameById(t.destinationBucketId)}</TableCell>
                        <TableCell align="right" sx={{ fontWeight: 700, color: t.isCancelled ? 'text.disabled' : amountColor, textDecoration: t.isCancelled ? 'line-through' : 'none' }}>
                          {amountPrefix}{formatCurrency(t.amount)}
                        </TableCell>
                        <TableCell sx={{ color: t.isCancelled ? 'text.disabled' : 'text.secondary', maxWidth: 300, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                          <span style={{ textDecoration: t.isCancelled ? 'line-through' : 'none' }}>{t.description}</span>
                          {t.isCancelled && (
                            <Typography variant="caption" display="block" color="error" sx={{ fontWeight: 600 }}>
                              Reason: {t.cancellationReason}
                            </Typography>
                          )}
                        </TableCell>
                        <TableCell align="center" sx={{ pr: 3 }}>
                          {!t.isCancelled && (
                            <MuiTooltip title="Cancel Transaction">
                              <IconButton
                                size="small"
                                color="error"
                                onClick={() => handleOpenCancelModal(t)}
                              >
                                <Block fontSize="small" />
                              </IconButton>
                            </MuiTooltip>
                          )}
                        </TableCell>
                      </TableRow>
                    );
                  })
                )}
              </TableBody>
            </Table>
          </TableContainer>
          <TablePagination
            rowsPerPageOptions={[10, 25, 50]}
            component="div"
            count={totalTxs}
            rowsPerPage={rowsPerPage}
            page={page}
            onPageChange={(_e, newPage) => setPage(newPage)}
            onRowsPerPageChange={(e) => {
              setRowsPerPage(parseInt(e.target.value, 10));
              setPage(0);
            }}
            sx={{ borderTop: '1px solid', borderColor: 'divider' }}
          />
        </Card>

        {/* Add/Edit Bucket Dialog */}
        <Dialog open={isBucketModalOpen} onClose={() => setIsBucketModalOpen(false)} maxWidth="xs" fullWidth PaperProps={{ sx: { borderRadius: 2, p: 1 } }}>
          <DialogTitle sx={{ fontWeight: 700, fontFamily: '"Space Grotesk", sans-serif' }}>
            {bucketEditId ? 'Edit Envelope Details' : 'Create New Envelope'}
          </DialogTitle>
          <DialogContent>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2.5, pt: 1.5 }}>
              <TextField
                fullWidth
                label="Envelope Name"
                value={bucketName}
                onChange={(e) => setBucketName(e.target.value)}
                placeholder="e.g. LIC, Medical Insurance, Safety net"
                disabled={bucketEditId !== null && buckets.find(b => b.id === bucketEditId)?.name === 'Savings'}
              />
              <TextField
                fullWidth
                label="Target Amount (Optional)"
                type="number"
                value={bucketTarget}
                onChange={(e) => setBucketTarget(e.target.value)}
                placeholder="e.g. 20000"
              />
            </Box>
          </DialogContent>
          <DialogActions sx={{ p: 2 }}>
            <Button onClick={() => setIsBucketModalOpen(false)} variant="text" color="inherit">Cancel</Button>
            <Button onClick={handleSaveBucket} variant="contained" color="primary">
              {bucketEditId ? 'Save Changes' : 'Create'}
            </Button>
          </DialogActions>
        </Dialog>

        {/* Transaction Move Money Dialog */}
        <Dialog open={isTxModalOpen} onClose={() => setIsTxModalOpen(false)} maxWidth="sm" fullWidth PaperProps={{ sx: { borderRadius: 2, p: 1 } }}>
          <DialogTitle sx={{ fontWeight: 700, fontFamily: '"Space Grotesk", sans-serif' }}>Log Transaction Entry</DialogTitle>
          <DialogContent>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2.5, pt: 1.5 }}>
              <FormControl fullWidth>
                <InputLabel id="tx-action-type-label">Action Type</InputLabel>
                <Select
                  labelId="tx-action-type-label"
                  value={txType}
                  label="Action Type"
                  onChange={(e) => {
                    const val = e.target.value;
                    setTxType(val);
                    // Reset sources / destinations
                    const root = buckets.find(b => b.name === 'Savings');
                    if (val === 'allocate') {
                      setTxSourceId(root?.id || '');
                      setTxDestId('');
                    } else if (val === 'release') {
                      setTxSourceId('');
                      setTxDestId(root?.id || '');
                    } else if (val === 'deposit') {
                      setTxSourceId('');
                      setTxDestId(root?.id || '');
                    } else if (val === 'withdraw') {
                      setTxSourceId(root?.id || '');
                      setTxDestId('');
                    } else {
                      setTxSourceId('');
                      setTxDestId('');
                    }
                  }}
                >
                  <MenuItem value="deposit">Deposit (New cash into bucket)</MenuItem>
                  <MenuItem value="withdraw">Withdrawal (Spend cash from bucket)</MenuItem>
                  <MenuItem value="allocate">Allocate (Savings → Custom Envelope)</MenuItem>
                  <MenuItem value="release">Release (Custom Envelope → Savings)</MenuItem>
                  <MenuItem value="transfer">Transfer (Envelope A → Envelope B)</MenuItem>
                </Select>
              </FormControl>

              {/* Source Selector */}
              {txType !== 'deposit' && (
                <FormControl fullWidth>
                  <InputLabel id="tx-source-envelope-label">Source Envelope</InputLabel>
                  <Select
                    labelId="tx-source-envelope-label"
                    value={txSourceId}
                    label="Source Envelope"
                    onChange={(e) => setTxSourceId(e.target.value)}
                  >
                    {buckets
                      .filter((b) => b.id !== txDestId)
                      .map((b) => (
                        <MenuItem key={b.id} value={b.id}>
                          {b.name} (Available: {formatCurrency(b.allocatedAmount)})
                        </MenuItem>
                      ))}
                  </Select>
                </FormControl>
              )}

              {/* Destination Selector */}
              {txType !== 'withdraw' && (
                <FormControl fullWidth>
                  <InputLabel id="tx-dest-envelope-label">Destination Envelope</InputLabel>
                  <Select
                    labelId="tx-dest-envelope-label"
                    value={txDestId}
                    label="Destination Envelope"
                    onChange={(e) => setTxDestId(e.target.value)}
                  >
                    {buckets
                      .filter((b) => b.id !== txSourceId)
                      .map((b) => (
                        <MenuItem key={b.id} value={b.id}>
                          {b.name} (Available: {formatCurrency(b.allocatedAmount)})
                        </MenuItem>
                      ))}
                  </Select>
                </FormControl>
              )}

              <TextField
                fullWidth
                label="Amount (in ₹)"
                type="number"
                value={txAmount}
                onChange={(e) => setTxAmount(e.target.value)}
                placeholder="e.g. 5000"
              />

              <TextField
                fullWidth
                label="Transaction Date"
                type="date"
                value={txDate}
                onChange={(e) => setTxDate(e.target.value)}
                InputLabelProps={{ shrink: true }}
                helperText="Optional. Leave blank to use current date."
              />

              <TextField
                fullWidth
                label="Audit Comment / Description"
                value={txDescription}
                onChange={(e) => setTxDescription(e.target.value)}
                placeholder="e.g. Monthly LIC premium allocation"
                multiline
                rows={2}
                helperText="Required. Explain the purpose of this transaction."
              />
            </Box>
          </DialogContent>
          <DialogActions sx={{ p: 2 }}>
            <Button onClick={() => setIsTxModalOpen(false)} variant="text" color="inherit">Cancel</Button>
            <Button onClick={handleSaveTx} variant="contained" color="primary">
              Submit Transaction
            </Button>
          </DialogActions>
        </Dialog>

        {/* Cancel Transaction Dialog */}
        <Dialog open={isCancelModalOpen} onClose={() => setIsCancelModalOpen(false)} maxWidth="xs" fullWidth PaperProps={{ sx: { borderRadius: 2, p: 1 } }}>
          <DialogTitle sx={{ fontWeight: 700, fontFamily: '"Space Grotesk", sans-serif' }}>Cancel Transaction</DialogTitle>
          <DialogContent>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2.5, pt: 1.5 }}>
              <Typography variant="body2" color="text.secondary">
                Are you sure you want to cancel this transaction? This will reverse the balance adjustments in the respective envelopes.
              </Typography>
              <TextField
                fullWidth
                label="Cancellation Reason"
                value={cancelReason}
                onChange={(e) => setCancelReason(e.target.value)}
                placeholder="e.g. Entered incorrect amount"
                multiline
                rows={2}
                helperText="Required. Provide a reason for this cancellation."
              />
            </Box>
          </DialogContent>
          <DialogActions sx={{ p: 2 }}>
            <Button onClick={() => setIsCancelModalOpen(false)} variant="text" color="inherit">Cancel</Button>
            <Button onClick={handleConfirmCancel} variant="contained" color="error" disabled={!cancelReason.trim()}>
              Confirm Cancellation
            </Button>
          </DialogActions>
        </Dialog>

        {/* Delete Bucket Confirmation Dialog */}
        <Dialog open={isDeleteBucketModalOpen} onClose={() => setIsDeleteBucketModalOpen(false)} maxWidth="xs" fullWidth PaperProps={{ sx: { borderRadius: 2, p: 1 } }}>
          <DialogTitle sx={{ fontWeight: 700, fontFamily: '"Space Grotesk", sans-serif' }}>Delete Envelope</DialogTitle>
          <DialogContent>
            <Typography variant="body2" color="text.secondary">
              Are you sure you want to delete this envelope? Any remaining balance will be automatically refunded back to your main Savings pool.
            </Typography>
          </DialogContent>
          <DialogActions sx={{ p: 2 }}>
            <Button onClick={() => setIsDeleteBucketModalOpen(false)} variant="outlined" color="inherit">Cancel</Button>
            <Button onClick={handleConfirmDeleteBucket} variant="contained" color="error">
              Delete Envelope
            </Button>
          </DialogActions>
        </Dialog>
      </Container>
    </Box>
  );
}
