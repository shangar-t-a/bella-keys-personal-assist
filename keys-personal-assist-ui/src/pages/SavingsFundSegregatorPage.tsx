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
} from '@mui/material';
import { Grid } from '@mui/material';
import {
  Add as Plus,
  Edit,
  Delete as Trash2,
  AccountBalance,
  AccountBalanceWallet,
  FolderShared,
  SwapHoriz,
  ArrowUpward,
  ArrowDownward,
  Block,
} from '@mui/icons-material';
import { toast } from 'sonner';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';
import { emsClient } from '@/api/clients/ems-client';
import type {
  AccountNameResponse,
  SavingsBucketResponse,
  SavingsBucketTransactionResponse,
} from '@/types/api';
import { formatCurrency } from '@/utils/formatters';

// Colors for the donut chart
const COLORS = ['#3b82f6', '#0ea5e9', '#10b981', '#f59e0b', '#8b5cf6', '#06b6d4', '#6366f1', '#ef4444'];

export default function SavingsFundSegregatorPage() {
  // ── States ──────────────────────────────────────────────────────────────────
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

  // ── Data Fetching ────────────────────────────────────────────────────────────
  const fetchAccounts = async () => {
    try {
      const data = await emsClient.getAllAccounts();
      setAccounts(data);
      if (data.length > 0) {
        setSelectedAccountId(data[0].id);
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

  // ── Calculations ─────────────────────────────────────────────────────────────
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

  // ── Handlers ─────────────────────────────────────────────────────────────────
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

  // ── Helper Resolvers ─────────────────────────────────────────────────────────
  const getBucketNameById = (id: string | null) => {
    if (!id) return '-';
    const b = buckets.find(x => x.id === id);
    return b ? b.name : 'Unknown';
  };

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: 'background.default', py: 6 }}>
      <Container maxWidth="xl">
        {isLoading && <LinearProgress sx={{ mb: 3, borderRadius: 1 }} />}
        {/* Header Block */}
        <Box sx={{ mb: 6, display: 'flex', flexDirection: { xs: 'column', md: 'row' }, justifyContent: 'space-between', alignItems: { xs: 'flex-start', md: 'center' }, gap: 3 }}>
          <Box>
            <Typography
              variant="h3"
              sx={{ fontWeight: 700, fontFamily: '"Space Grotesk", sans-serif', mb: 1, background: 'linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}
            >
              Savings Fund Segregator
            </Typography>
            <Typography variant="body1" color="text.secondary">
              Partition and track allocations in your savings accounts for medical, LIC, targets, and goals.
            </Typography>
          </Box>

          <FormControl sx={{ minWidth: 240 }} size="small">
            <InputLabel>Bank Account</InputLabel>
            <Select
              value={selectedAccountId}
              label="Bank Account"
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
        </Box>

        {/* ── Metric Cards ── */}
        <Grid container spacing={3} sx={{ mb: 6 }}>
          {/* Card 1: Total Savings */}
          <Grid size={{ xs: 12, md: 4 }}>
            <Card sx={{ height: '100%', borderRadius: 3, boxShadow: 3, background: 'linear-gradient(135deg, #f3e8ff 0%, #e9d5ff 100%)', color: '#6b21a8' }}>
              <CardContent sx={{ p: 4, display: 'flex', alignItems: 'center', gap: 3 }}>
                <Box sx={{ width: 56, height: 56, borderRadius: 2, bgcolor: 'rgba(107, 33, 168, 0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <AccountBalance sx={{ fontSize: 32 }} />
                </Box>
                <Box>
                  <Typography variant="body2" sx={{ fontWeight: 600, textTransform: 'uppercase', letterSpacing: 0.5, opacity: 0.8 }}>
                    Total Savings
                  </Typography>
                  <Typography variant="h4" sx={{ fontWeight: 700, my: 0.5 }}>
                    {formatCurrency(totalSavings)}
                  </Typography>
                  <Typography variant="caption" sx={{ opacity: 0.7 }}>
                    Sum of all envelopes
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* Card 2: Allocated Funds */}
          <Grid size={{ xs: 12, md: 4 }}>
            <Card sx={{ height: '100%', borderRadius: 3, boxShadow: 3, background: 'linear-gradient(135deg, #e0f2fe 0%, #bae6fd 100%)', color: '#0369a1' }}>
              <CardContent sx={{ p: 4, display: 'flex', alignItems: 'center', gap: 3 }}>
                <Box sx={{ width: 56, height: 56, borderRadius: 2, bgcolor: 'rgba(3, 105, 161, 0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <FolderShared sx={{ fontSize: 32 }} />
                </Box>
                <Box>
                  <Typography variant="body2" sx={{ fontWeight: 600, textTransform: 'uppercase', letterSpacing: 0.5, opacity: 0.8 }}>
                    Allocated Envelopes
                  </Typography>
                  <Typography variant="h4" sx={{ fontWeight: 700, my: 0.5 }}>
                    {formatCurrency(allocatedFunds)}
                  </Typography>
                  <Typography variant="caption" sx={{ opacity: 0.7 }}>
                    LIC, Medical, Targets
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* Card 3: Savings (Unallocated Pool) */}
          <Grid size={{ xs: 12, md: 4 }}>
            <Card sx={{ height: '100%', borderRadius: 3, boxShadow: 3, background: 'linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%)', color: '#065f46' }}>
              <CardContent sx={{ p: 4, display: 'flex', alignItems: 'center', gap: 3 }}>
                <Box sx={{ width: 56, height: 56, borderRadius: 2, bgcolor: 'rgba(6, 95, 70, 0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <AccountBalanceWallet sx={{ fontSize: 32 }} />
                </Box>
                <Box>
                  <Typography variant="body2" sx={{ fontWeight: 600, textTransform: 'uppercase', letterSpacing: 0.5, opacity: 0.8 }}>
                    Free Savings (Unallocated)
                  </Typography>
                  <Typography variant="h4" sx={{ fontWeight: 700, my: 0.5 }}>
                    {formatCurrency(unallocatedSavings)}
                  </Typography>
                  <Typography variant="caption" sx={{ opacity: 0.7 }}>
                    Primary cash pool
                  </Typography>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* ── Main Layout: Visual Chart & Bucket List ── */}
        <Grid container spacing={4} sx={{ mb: 6 }}>
          {/* Visual Donut Chart */}
          <Grid size={{ xs: 12, lg: 4 }}>
            <Card sx={{ height: '100%', borderRadius: 3, boxShadow: 2 }}>
              <CardContent sx={{ p: 4, display: 'flex', flexDirection: 'column', height: '100%' }}>
                <Typography variant="h6" sx={{ fontWeight: 700, mb: 3 }}>
                  Allocation Split
                </Typography>
                {chartData.length === 0 ? (
                  <Box sx={{ display: 'flex', flexGrow: 1, alignItems: 'center', justifyContent: 'center', height: 260, color: 'text.secondary' }}>
                    No funds allocated yet
                  </Box>
                ) : (
                  <Box sx={{ width: '100%', height: 280, position: 'relative' }}>
                    <ResponsiveContainer width="100%" height="100%">
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
                            <Box sx={{ width: 10, height: 10, borderRadius: '50%', bgcolor: COLORS[idx % COLORS.length] }} />
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
            <Card sx={{ height: '100%', borderRadius: 3, boxShadow: 2 }}>
              <CardContent sx={{ p: 4 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 4 }}>
                  <Typography variant="h6" sx={{ fontWeight: 700 }}>
                    My Envelopes
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 1.5 }}>
                    <Button variant="outlined" startIcon={<Plus />} size="small" onClick={() => handleOpenBucketModal()} sx={{ borderRadius: 2 }}>
                      Create Bucket
                    </Button>
                    <Button variant="contained" startIcon={<SwapHoriz />} size="small" onClick={() => handleOpenTxModal('allocate')} sx={{ borderRadius: 2, background: 'linear-gradient(135deg, #ec4899 0%, #db2777 100%)', '&:hover': { background: 'linear-gradient(135deg, #db2777 0%, #be185d 100%)' } }}>
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
                        <Card variant="outlined" sx={{ borderRadius: 2, p: 2.5, position: 'relative', borderLeft: `5px solid ${isRoot ? '#10b981' : '#6366f1'}` }}>
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                            <Box>
                              <Typography variant="subtitle1" sx={{ fontWeight: 700 }}>
                                {b.name}
                              </Typography>
                              <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                                {isRoot ? 'General Cash Pool' : 'Special Bucket'}
                              </Typography>
                            </Box>
                            
                            {!isRoot && (
                              <Box sx={{ display: 'flex', gap: 0.5 }}>
                                <IconButton size="small" color="primary" onClick={() => handleOpenBucketModal(b)}>
                                  <Edit fontSize="small" />
                                </IconButton>
                                <IconButton size="small" color="error" onClick={() => handleDeleteBucket(b.id)}>
                                  <Trash2 fontSize="small" />
                                </IconButton>
                              </Box>
                            )}
                          </Box>

                          <Box sx={{ my: 2 }}>
                            <Typography variant="h5" sx={{ fontWeight: 800 }}>
                              {formatCurrency(b.allocatedAmount)}
                            </Typography>
                            {b.targetAmount && (
                              <Typography variant="caption" color="text.secondary">
                                Target: {formatCurrency(b.targetAmount)} ({targetPercent.toFixed(0)}%)
                              </Typography>
                            )}
                          </Box>

                          {b.targetAmount && (
                            <Box sx={{ mt: 1.5 }}>
                              <LinearProgress
                                variant="determinate"
                                value={targetPercent}
                                sx={{
                                  height: 6,
                                  borderRadius: 3,
                                  bgcolor: 'rgba(99, 102, 241, 0.1)',
                                  '& .MuiLinearProgress-bar': {
                                    bgcolor: '#6366f1',
                                    borderRadius: 3,
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

        {/* ── Transaction Ledger Block ── */}
        <Card sx={{ borderRadius: 3, boxShadow: 3 }}>
          <CardContent sx={{ p: 4 }}>
            <Box sx={{ display: 'flex', flexDirection: { xs: 'column', sm: 'row' }, justifyContent: 'space-between', alignItems: { xs: 'flex-start', sm: 'center' }, gap: 2, mb: 4 }}>
              <Box>
                <Typography variant="h6" sx={{ fontWeight: 700 }}>
                  Allocation Ledger
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Complete history of allocations, releases, deposits, and transfers.
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', gap: 1.5 }}>
                <Button variant="outlined" size="small" startIcon={<ArrowUpward />} onClick={() => handleOpenTxModal('deposit')} color="success" sx={{ borderRadius: 2 }}>
                  Deposit
                </Button>
                <Button variant="outlined" size="small" startIcon={<ArrowDownward />} onClick={() => handleOpenTxModal('withdraw')} color="error" sx={{ borderRadius: 2 }}>
                  Withdrawal
                </Button>
              </Box>
            </Box>

            <TableContainer>
              <Table size="medium">
                <TableHead>
                  <TableRow sx={{ bgcolor: 'action.hover' }}>
                    <TableCell sx={{ fontWeight: 700 }}>Date</TableCell>
                    <TableCell sx={{ fontWeight: 700 }}>Type</TableCell>
                    <TableCell sx={{ fontWeight: 700 }}>Source envelope</TableCell>
                    <TableCell sx={{ fontWeight: 700 }}>Destination envelope</TableCell>
                    <TableCell sx={{ fontWeight: 700 }} align="right">Amount</TableCell>
                    <TableCell sx={{ fontWeight: 700 }}>Comment / Description</TableCell>
                    <TableCell sx={{ fontWeight: 700 }} align="center">Actions</TableCell>
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
                    transactions.map((t) => {
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
                        <TableRow key={t.id} hover>
                          <TableCell sx={{ fontWeight: 500, color: t.isCancelled ? 'text.disabled' : 'text.primary' }}>
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
                              <Chip label={typeLabel} size="small" color={typeColor} variant="outlined" sx={{ fontWeight: 700 }} />
                              {t.isCancelled && (
                                <Chip label="CANCELLED" size="small" color="error" variant="filled" sx={{ fontWeight: 700, fontSize: '0.65rem', height: 20 }} />
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
                          <TableCell align="center">
                            {!t.isCancelled && (
                              <IconButton
                                size="small"
                                color="error"
                                onClick={() => handleOpenCancelModal(t)}
                                title="Cancel Transaction"
                              >
                                <Block fontSize="small" />
                              </IconButton>
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
            />
          </CardContent>
        </Card>

        {/* ── Add/Edit Bucket Dialog ── */}
        <Dialog open={isBucketModalOpen} onClose={() => setIsBucketModalOpen(false)} maxWidth="xs" fullWidth>
          <DialogTitle sx={{ fontWeight: 700 }}>
            {bucketEditId ? 'Edit Envelope Details' : 'Create New Envelope'}
          </DialogTitle>
          <DialogContent>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2.5, pt: 2 }}>
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
          <DialogActions sx={{ px: 3, pb: 3 }}>
            <Button onClick={() => setIsBucketModalOpen(false)}>Cancel</Button>
            <Button onClick={handleSaveBucket} variant="contained">
              {bucketEditId ? 'Save Changes' : 'Create'}
            </Button>
          </DialogActions>
        </Dialog>

        {/* ── Transaction Move Money Dialog ── */}
        <Dialog open={isTxModalOpen} onClose={() => setIsTxModalOpen(false)} maxWidth="sm" fullWidth>
          <DialogTitle sx={{ fontWeight: 700 }}>Log Transaction Entry</DialogTitle>
          <DialogContent>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2.5, pt: 2 }}>
              <FormControl fullWidth>
                <InputLabel>Action Type</InputLabel>
                <Select
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
                  <InputLabel>Source Envelope</InputLabel>
                  <Select
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
                  <InputLabel>Destination Envelope</InputLabel>
                  <Select
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
          <DialogActions sx={{ px: 3, pb: 3 }}>
            <Button onClick={() => setIsTxModalOpen(false)}>Cancel</Button>
            <Button onClick={handleSaveTx} variant="contained">
              Submit Transaction
            </Button>
          </DialogActions>
        </Dialog>

        {/* ── Cancel Transaction Dialog ── */}
        <Dialog open={isCancelModalOpen} onClose={() => setIsCancelModalOpen(false)} maxWidth="xs" fullWidth>
          <DialogTitle sx={{ fontWeight: 700 }}>Cancel Transaction</DialogTitle>
          <DialogContent>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2.5, pt: 1 }}>
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
          <DialogActions sx={{ px: 3, pb: 3 }}>
            <Button onClick={() => setIsCancelModalOpen(false)}>Cancel</Button>
            <Button onClick={handleConfirmCancel} variant="contained" color="error" disabled={!cancelReason.trim()}>
              Confirm Cancellation
            </Button>
          </DialogActions>
        </Dialog>

        {/* ── Delete Bucket Confirmation Dialog ── */}
        <Dialog open={isDeleteBucketModalOpen} onClose={() => setIsDeleteBucketModalOpen(false)} maxWidth="xs" fullWidth>
          <DialogTitle sx={{ fontWeight: 700 }}>Delete Envelope</DialogTitle>
          <DialogContent>
            <Typography variant="body2" color="text.secondary">
              Are you sure you want to delete this envelope? Any remaining balance will be automatically refunded back to your main Savings pool.
            </Typography>
          </DialogContent>
          <DialogActions sx={{ px: 3, pb: 3 }}>
            <Button onClick={() => setIsDeleteBucketModalOpen(false)}>Cancel</Button>
            <Button onClick={handleConfirmDeleteBucket} variant="contained" color="error">
              Delete Envelope
            </Button>
          </DialogActions>
        </Dialog>
      </Container>
    </Box>
  );
}
