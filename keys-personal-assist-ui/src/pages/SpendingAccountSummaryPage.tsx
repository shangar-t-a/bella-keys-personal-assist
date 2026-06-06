import { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Container,
  Typography,
  Card,
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
  TableSortLabel,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  OutlinedInput,
  Tooltip,
  Paper,
  Grid,
} from '@mui/material';
import {
  Add as Plus,
  Edit,
  Delete as Trash2,
  Refresh as RotateCcw,
  Settings,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { toast } from 'sonner';
import { emsClient } from '@/api/clients/ems-client';
import type {
  SpendingAccountEntryWithCalculatedFieldsResponse,
  SpendingEntryWithCalcPageResponse,
  PaginationMeta,
  SortOrder,
  SpendingEntrySortField,
} from '@/types/api';
import { formatCurrency, formatCompactRupees } from '@/utils/formatters';

type SpendingAccountEntry = SpendingAccountEntryWithCalculatedFieldsResponse;

interface FormData {
  accountName: string;
  month: number;
  year: number;
  startingBalance: number;
  currentBalance: number;
  currentCredit: number;
}

// ── Constants ────────────────────────────────────────────────────────────────

export const MONTH_NAMES = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December',
];


const DEFAULT_FORM: FormData = {
  accountName: '',
  month: new Date().getMonth() + 1,
  year: new Date().getFullYear(),
  startingBalance: 0,
  currentBalance: 0,
  currentCredit: 0,
};

// ── Entry form — defined OUTSIDE the page so it is never re-mounted ──────────
// (Defining it inside the page would cause focus loss on every state change.)

interface EntryFormFieldsProps {
  formData: FormData;
  accounts: string[];
  onChange: (next: FormData) => void;
  onAddAccountClick: () => void;
}

function EntryFormFields({ formData, accounts, onChange, onAddAccountClick }: EntryFormFieldsProps) {
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, pt: 2 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <FormControl fullWidth>
          <InputLabel>Account</InputLabel>
          <Select
            value={formData.accountName}
            label="Account"
            onChange={(e) => onChange({ ...formData, accountName: e.target.value })}
          >
            {accounts.map((a) => (
              <MenuItem key={a} value={a}>{a}</MenuItem>
            ))}
          </Select>
        </FormControl>
        <Tooltip title="Add New Account">
          <IconButton onClick={onAddAccountClick} color="primary">
            <Plus />
          </IconButton>
        </Tooltip>
      </Box>

      <FormControl fullWidth>
        <InputLabel>Month</InputLabel>
        <Select
          value={formData.month}
          label="Month"
          onChange={(e) => onChange({ ...formData, month: Number(e.target.value) })}
        >
          {MONTH_NAMES.map((name, i) => (
            <MenuItem key={name} value={i + 1}>{name}</MenuItem>
          ))}
        </Select>
      </FormControl>

      <TextField
        fullWidth
        label="Year"
        type="number"
        value={formData.year}
        onChange={(e) => onChange({ ...formData, year: parseInt(e.target.value) })}
      />
      <TextField
        fullWidth
        label="Starting Balance"
        type="number"
        value={formData.startingBalance}
        onChange={(e) => onChange({ ...formData, startingBalance: parseFloat(e.target.value) })}
      />
      <TextField
        fullWidth
        label="Current Balance"
        type="number"
        value={formData.currentBalance}
        onChange={(e) => onChange({ ...formData, currentBalance: parseFloat(e.target.value) })}
      />
      <TextField
        fullWidth
        label="Current Credit"
        type="number"
        value={formData.currentCredit}
        onChange={(e) => onChange({ ...formData, currentCredit: parseFloat(e.target.value) })}
      />
    </Box>
  );
}

// ── Page component ────────────────────────────────────────────────────────────

export default function SpendingAccountSummaryPage() {
  const navigate = useNavigate();
  // ── Server data ─────────────────────────────────────────────────────────────
  const [entries, setEntries] = useState<SpendingAccountEntry[]>([]);
  const [paginationMeta, setPaginationMeta] = useState<PaginationMeta>({
    number: 0,
    size: 12,
    totalElements: 0,
    totalPages: 0,
  });
  const [accounts, setAccounts] = useState<string[]>([]);

  // ── Filter / sort / pagination state ────────────────────────────────────────
  const [filterAccount, setFilterAccount] = useState<string>('');
  const [filterMonth, setFilterMonth] = useState<string>('');
  const [filterYear, setFilterYear] = useState<string>('');
  const [sortBy, setSortBy] = useState<SpendingEntrySortField>('year');
  const [sortOrder, setSortOrder] = useState<SortOrder>('desc');
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(12);

  // ── Modal state ─────────────────────────────────────────────────────────────
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [selectedEntry, setSelectedEntry] = useState<SpendingAccountEntry | null>(null);
  const [formData, setFormData] = useState<FormData>(DEFAULT_FORM);

  const [isQuickAddAccountOpen, setIsQuickAddAccountOpen] = useState(false);
  const [quickAddAccountName, setQuickAddAccountName] = useState('');
  const [quickAddLoading, setQuickAddLoading] = useState(false);

  // ── Derived values for metric cards ─────────────────────────────────────────
  const now = new Date();

  // Aggregate the currently loaded page (after server filtering)
  const totalStartingBalance = entries.reduce((s, e) => s + e.startingBalance, 0);
  const totalSpent = entries.reduce((s, e) => s + e.totalSpent, 0);
  const totalCurrentBalance = entries.reduce((s, e) => s + e.currentBalance, 0);
  const totalCurrentCredit = entries.reduce((s, e) => s + e.currentCredit, 0);
  const totalBalanceAfterCredit = entries.reduce((s, e) => s + e.balanceAfterCredit, 0);

  // ── Data fetching ────────────────────────────────────────────────────────────
  const fetchAccounts = async () => {
    try {
      const data = await emsClient.getAllAccounts();
      setAccounts(data.map((a) => a.accountName));
    } catch {
      toast.error('Failed to fetch accounts');
    }
  };

  const fetchEntries = useCallback(async () => {
    try {
      const result: SpendingEntryWithCalcPageResponse =
        await emsClient.getAllSpendingAccountEntries({
          page,
          size: rowsPerPage,
          sortBy,
          sortOrder,
          month: filterMonth !== '' ? parseInt(filterMonth, 10) : null,
          year: filterYear !== '' ? parseInt(filterYear, 10) : null,
          accountName: filterAccount || null,
        });
      setEntries(result.spendingEntries);
      setPaginationMeta(result.page);
    } catch {
      toast.error('Failed to fetch spending account data');
    }
  }, [page, rowsPerPage, sortBy, sortOrder, filterMonth, filterYear, filterAccount]);

  useEffect(() => { fetchAccounts(); }, []);
  useEffect(() => { fetchEntries(); }, [fetchEntries]);

  // ── Sort handler ─────────────────────────────────────────────────────────────
  const handleSort = (field: SpendingEntrySortField) => {
    if (sortBy === field) {
      setSortOrder((prev) => (prev === 'asc' ? 'desc' : 'asc'));
    } else {
      setSortBy(field);
      setSortOrder('asc');
    }
    setPage(0);
  };

  const resetFilters = () => {
    setFilterAccount('');
    setFilterMonth('');
    setFilterYear('');
    setPage(0);
  };

  // ── CRUD handlers ────────────────────────────────────────────────────────────
  const handleAddEntry = async () => {
    try {
      await emsClient.addSpendingAccountEntry(formData);
      toast.success('Entry added successfully');
      setIsAddModalOpen(false);
      setFormData(DEFAULT_FORM);
      fetchEntries();
    } catch {
      toast.error('Failed to add entry');
    }
  };

  const handleEditEntry = async () => {
    if (!selectedEntry) return;
    try {
      await emsClient.editSpendingAccountEntry(selectedEntry.id, formData);
      toast.success('Entry updated successfully');
      setIsEditModalOpen(false);
      setFormData(DEFAULT_FORM);
      fetchEntries();
    } catch {
      toast.error('Failed to update entry');
    }
  };

  const handleDeleteEntry = async () => {
    if (!selectedEntry) return;
    try {
      await emsClient.deleteSpendingAccountEntry(selectedEntry.id);
      toast.success('Entry deleted successfully');
      setIsDeleteModalOpen(false);
      setSelectedEntry(null);
      fetchEntries();
    } catch {
      toast.error('Failed to delete entry');
    }
  };

  const handleQuickAddAccount = async () => {
    if (!quickAddAccountName.trim()) {
      toast.error('Account name cannot be empty');
      return;
    }
    setQuickAddLoading(true);
    try {
      await emsClient.getOrCreateAccount({ accountName: quickAddAccountName.trim() });
      toast.success(`Account "${quickAddAccountName.trim()}" created successfully`);
      setFormData(prev => ({ ...prev, accountName: quickAddAccountName.trim() }));
      setQuickAddAccountName('');
      setIsQuickAddAccountOpen(false);
      await fetchAccounts();
    } catch (e: any) {
      toast.error(e.message || 'Failed to create account');
    } finally {
      setQuickAddLoading(false);
    }
  };

  const openEditModal = (entry: SpendingAccountEntry) => {
    setSelectedEntry(entry);
    setFormData({
      accountName: entry.accountName,
      month: entry.month,
      year: entry.year,
      startingBalance: entry.startingBalance,
      currentBalance: entry.currentBalance,
      currentCredit: entry.currentCredit,
    });
    setIsEditModalOpen(true);
  };

  // ── Sortable column header ───────────────────────────────────────────────────
  // ── Sortable column header ───────────────────────────────────────────────────
  const SortableCell = ({
    field,
    align = 'left',
    children,
  }: {
    field: SpendingEntrySortField;
    align?: 'left' | 'right' | 'center';
    children: React.ReactNode;
  }) => (
    <TableCell
      align={align}
      sortDirection={sortBy === field ? sortOrder : false}
      sx={{
        pl: align === 'left' ? 3 : undefined,
        fontWeight: 700,
        py: 1.25,
        fontSize: '0.78rem',
        textTransform: 'uppercase',
        letterSpacing: 0.5,
        color: 'text.secondary',
      }}
    >
      <TableSortLabel
        active={sortBy === field}
        direction={sortBy === field ? sortOrder : 'asc'}
        onClick={() => handleSort(field)}
        sx={{
          '&.MuiTableSortLabel-active': {
            color: 'text.primary',
          },
        }}
      >
        {children}
      </TableSortLabel>
    </TableCell>
  );

  // ── Render ───────────────────────────────────────────────────────────────────
  const activeFilterCount =
    (filterAccount ? 1 : 0) + (filterMonth !== '' ? 1 : 0) + (filterYear !== '' ? 1 : 0);

  const contextLabel = filterAccount
    ? filterAccount
    : 'All Accounts';

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
        {/* Header */}
        <Box sx={{ mb: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
          <Box>
            <Typography
              variant="h5"
              sx={{ fontWeight: 700, fontFamily: '"Space Grotesk", sans-serif', lineHeight: 1.2 }}
            >
              Spending Accounts
            </Typography>
            <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 500 }}>
              {contextLabel} · {paginationMeta.totalElements} entries
            </Typography>
          </Box>
        </Box>

        {/* ── Summary Card: Prominent Portfolio Metrics ────────────────────────── */}
        <Card variant="outlined" sx={{ borderRadius: 2, border: '1px solid', borderColor: 'divider', boxShadow: 'none', mb: 2 }}>
          <Grid container>
            {/* Block 1: Starting Balance */}
            <Grid size={{ xs: 6, md: 3 }} sx={{
              p: 2.5,
              borderRight: '1px solid',
              borderRightColor: 'divider',
              borderBottom: { xs: '1px solid', md: 'none' },
              borderBottomColor: { xs: 'divider', md: 'transparent' },
            }}>
              <Typography variant="caption" color="text.disabled" sx={{ fontWeight: 600, textTransform: 'uppercase', letterSpacing: 0.8, fontSize: '0.68rem', display: 'block', mb: 0.5 }}>
                Starting Balance
              </Typography>
              <Typography variant="h5" sx={{ fontWeight: 700, fontFamily: '"Space Grotesk", sans-serif', color: 'success.main', fontSize: '1.3rem' }}>
                {formatCompactRupees(totalStartingBalance)}
              </Typography>
            </Grid>
            
            {/* Block 2: Total Spent */}
            <Grid size={{ xs: 6, md: 3 }} sx={{
              p: 2.5,
              borderRight: { xs: 'none', md: '1px solid' },
              borderRightColor: { xs: 'transparent', md: 'divider' },
              borderBottom: { xs: '1px solid', md: 'none' },
              borderBottomColor: { xs: 'divider', md: 'transparent' },
            }}>
              <Typography variant="caption" color="text.disabled" sx={{ fontWeight: 600, textTransform: 'uppercase', letterSpacing: 0.8, fontSize: '0.68rem', display: 'block', mb: 0.5 }}>
                Total Spent
              </Typography>
              <Typography variant="h5" sx={{ fontWeight: 700, fontFamily: '"Space Grotesk", sans-serif', color: 'error.main', fontSize: '1.3rem' }}>
                {formatCompactRupees(totalSpent)}
              </Typography>
            </Grid>
            
            {/* Block 3: Current Cash */}
            <Grid size={{ xs: 6, md: 3 }} sx={{
              p: 2.5,
              borderRight: '1px solid',
              borderRightColor: 'divider',
            }}>
              <Typography variant="caption" color="text.disabled" sx={{ fontWeight: 600, textTransform: 'uppercase', letterSpacing: 0.8, fontSize: '0.68rem', display: 'block', mb: 0.5 }}>
                Current Cash
              </Typography>
              <Typography variant="h5" sx={{ fontWeight: 700, fontFamily: '"Space Grotesk", sans-serif', color: 'info.main', fontSize: '1.3rem' }}>
                {formatCompactRupees(totalCurrentBalance)}
              </Typography>
            </Grid>
            
            {/* Block 4: Credit CC Debt & Net */}
            <Grid size={{ xs: 6, md: 3 }} sx={{ p: 2.5 }}>
              <Typography variant="caption" color="text.disabled" sx={{ fontWeight: 600, textTransform: 'uppercase', letterSpacing: 0.8, fontSize: '0.68rem', display: 'block', mb: 0.5 }}>
                Credit Card Debt
              </Typography>
              <Typography variant="h5" sx={{ fontWeight: 700, fontFamily: '"Space Grotesk", sans-serif', color: 'warning.main', fontSize: '1.3rem', mb: 0.5 }}>
                {formatCompactRupees(totalCurrentCredit)}
              </Typography>
              <Typography variant="caption" sx={{ color: 'text.secondary', fontWeight: 600 }}>
                Net: {formatCompactRupees(totalBalanceAfterCredit)}
              </Typography>
            </Grid>
          </Grid>
        </Card>

        {/* ── Toolbar Card: Filters + Actions ─────────────────────────────────── */}
        <Card variant="outlined" sx={{ borderRadius: 2, border: '1px solid', borderColor: 'divider', boxShadow: 'none', px: 2, py: 1.25, mb: 2 }}>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1.5, justifyContent: 'space-between', alignItems: 'center' }}>
            {/* Left: Filters */}
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, flexGrow: 1, flexWrap: 'wrap' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <FormControl size="small" sx={{ width: 180 }}>
                  <InputLabel id="filter-account-label" shrink>Account</InputLabel>
                  <Select
                    labelId="filter-account-label"
                    value={filterAccount}
                    displayEmpty
                    input={<OutlinedInput notched label="Account" sx={{ borderRadius: 1.5, fontSize: '0.85rem' }} />}
                    onChange={(e) => { setFilterAccount(e.target.value); setPage(0); }}
                    renderValue={(v: string) => v || <em style={{ color: '#9e9e9e' }}>All Accounts</em>}
                  >
                    <MenuItem value="">All Accounts</MenuItem>
                    {accounts.map((a) => (
                      <MenuItem key={a} value={a}>{a}</MenuItem>
                    ))}
                  </Select>
                </FormControl>
                <Tooltip title="Manage Accounts">
                  <IconButton
                    size="small"
                    onClick={() => navigate('/settings?tab=accounts')}
                    color="primary"
                  >
                    <Settings fontSize="small" />
                  </IconButton>
                </Tooltip>
              </Box>

              <FormControl size="small" sx={{ width: 140 }}>
                <InputLabel id="filter-month-label" shrink>Month</InputLabel>
                <Select
                  labelId="filter-month-label"
                  value={filterMonth}
                  displayEmpty
                  input={<OutlinedInput notched label="Month" sx={{ borderRadius: 1.5, fontSize: '0.85rem' }} />}
                  onChange={(e) => { setFilterMonth(e.target.value); setPage(0); }}
                  renderValue={(v: string) =>
                    v !== '' ? MONTH_NAMES[parseInt(v, 10) - 1] : <em style={{ color: '#9e9e9e' }}>All Months</em>
                  }
                >
                  <MenuItem value="">All Months</MenuItem>
                  {MONTH_NAMES.map((name, i) => (
                    <MenuItem key={name} value={String(i + 1)}>{name}</MenuItem>
                  ))}
                </Select>
              </FormControl>

              <FormControl size="small" sx={{ width: 120 }}>
                <InputLabel id="filter-year-label" shrink>Year</InputLabel>
                <Select
                  labelId="filter-year-label"
                  value={filterYear}
                  displayEmpty
                  input={<OutlinedInput notched label="Year" sx={{ borderRadius: 1.5, fontSize: '0.85rem' }} />}
                  onChange={(e) => { setFilterYear(e.target.value); setPage(0); }}
                  renderValue={(v: string) => v || <em style={{ color: '#9e9e9e' }}>All Years</em>}
                >
                  <MenuItem value="">All Years</MenuItem>
                  {Array.from({ length: 10 }, (_, i) => String(now.getFullYear() - i)).map((y) => (
                    <MenuItem key={y} value={y}>{y}</MenuItem>
                  ))}
                </Select>
              </FormControl>

              <Button
                variant="outlined"
                color="inherit"
                size="small"
                startIcon={<RotateCcw />}
                onClick={resetFilters}
                disabled={activeFilterCount === 0}
                sx={{ py: 0.6, px: 2, fontWeight: 600, textTransform: 'none', borderRadius: 1.5, fontSize: '0.85rem' }}
              >
                Reset
              </Button>
            </Box>

            {/* Right: Add CTA */}
            <Button
              variant="contained"
              color="primary"
              startIcon={<Plus />}
              onClick={() => { setFormData(DEFAULT_FORM); setIsAddModalOpen(true); }}
              sx={{ py: 0.6, px: 2, fontWeight: 600, textTransform: 'none', borderRadius: 1.5, fontSize: '0.85rem', flexShrink: 0 }}
            >
              Add Entry
            </Button>
          </Box>
        </Card>

        {/* ── Table Card ──────────────────────────────────────────────────────── */}
        <Card variant="outlined" sx={{ borderRadius: 2, overflow: 'hidden', border: '1px solid', borderColor: 'divider', boxShadow: 'none' }}>
          <TableContainer component={Paper} elevation={0} sx={{ borderRadius: 0, bgcolor: 'transparent' }}>
            <Table size="small">
              <TableHead sx={{ bgcolor: (theme) => theme.palette.mode === 'dark' ? 'rgba(30, 41, 59, 0.5)' : '#f1f5f9' }}>
                <TableRow>
                  <SortableCell field="account_name">Account</SortableCell>
                  <SortableCell field="month">Month</SortableCell>
                  <SortableCell field="year">Year</SortableCell>
                  <SortableCell field="starting_balance" align="right">Starting Bal.</SortableCell>
                  <SortableCell field="current_balance" align="right">Current Bal.</SortableCell>
                  <SortableCell field="current_credit" align="right">Credit Used</SortableCell>
                  <SortableCell field="balance_after_credit" align="right">Net Balance</SortableCell>
                  <SortableCell field="total_spent" align="right">Total Spent</SortableCell>
                  <TableCell align="center" sx={{ fontWeight: 700, py: 1.25, fontSize: '0.78rem', textTransform: 'uppercase', letterSpacing: 0.5, color: 'text.secondary' }}>Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {entries.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={9} align="center" sx={{ py: 6, color: 'text.secondary' }}>
                      No entries found
                    </TableCell>
                  </TableRow>
                ) : (
                  entries.map((entry, idx) => (
                    <TableRow
                      key={entry.id}
                      sx={{
                        '& td': { py: 1 },
                        bgcolor: idx % 2 === 0
                          ? 'transparent'
                          : (theme) => theme.palette.mode === 'dark' ? 'rgba(255,255,255,0.018)' : 'rgba(0,0,0,0.018)',
                        '&:hover': { bgcolor: 'action.hover' },
                      }}
                    >
                      <TableCell sx={{ fontWeight: 600 }}>{entry.accountName}</TableCell>
                      <TableCell>{MONTH_NAMES[entry.month - 1]}</TableCell>
                      <TableCell>{entry.year}</TableCell>
                      <TableCell align="right" sx={{ fontWeight: 500 }}>{formatCurrency(entry.startingBalance)}</TableCell>
                      <TableCell align="right" sx={{ fontWeight: 600, color: 'primary.main' }}>{formatCurrency(entry.currentBalance)}</TableCell>
                      <TableCell align="right" sx={{ fontWeight: 500, color: 'warning.main' }}>{formatCurrency(entry.currentCredit)}</TableCell>
                      <TableCell align="right" sx={{ fontWeight: 600 }}>{formatCurrency(entry.balanceAfterCredit)}</TableCell>
                      <TableCell align="right" sx={{ fontWeight: 600, color: 'error.main' }}>{formatCurrency(entry.totalSpent)}</TableCell>
                      <TableCell align="center" sx={{ whiteSpace: 'nowrap' }}>
                        <Tooltip title="Edit">
                          <IconButton size="small" onClick={() => openEditModal(entry)} color="secondary">
                            <Edit fontSize="small" />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Delete">
                          <IconButton
                            size="small"
                            onClick={() => { setSelectedEntry(entry); setIsDeleteModalOpen(true); }}
                            color="error"
                          >
                            <Trash2 fontSize="small" />
                          </IconButton>
                        </Tooltip>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </TableContainer>
          <TablePagination
            rowsPerPageOptions={[12, 25, 50, 100]}
            component="div"
            count={paginationMeta.totalElements}
            rowsPerPage={rowsPerPage}
            page={page}
            onPageChange={(_e, newPage) => setPage(newPage)}
            onRowsPerPageChange={(e) => { setRowsPerPage(parseInt(e.target.value, 10)); setPage(0); }}
            sx={{ borderTop: '1px solid', borderColor: 'divider' }}
          />
        </Card>

        {/* ── Add Modal ────────────────────────────────────────────────────────── */}
        <Dialog open={isAddModalOpen} onClose={() => setIsAddModalOpen(false)} maxWidth="sm" fullWidth PaperProps={{ sx: { borderRadius: 2, p: 1 } }}>
          <DialogTitle sx={{ fontWeight: 700, fontFamily: '"Space Grotesk", sans-serif' }}>Add New Entry</DialogTitle>
          <DialogContent>
            <EntryFormFields formData={formData} accounts={accounts} onChange={setFormData} onAddAccountClick={() => setIsQuickAddAccountOpen(true)} />
          </DialogContent>
          <DialogActions sx={{ p: 2 }}>
            <Button onClick={() => setIsAddModalOpen(false)} variant="text" color="inherit">Cancel</Button>
            <Button onClick={handleAddEntry} variant="contained" color="primary">Add Entry</Button>
          </DialogActions>
        </Dialog>

        {/* ── Edit Modal ───────────────────────────────────────────────────────── */}
        <Dialog open={isEditModalOpen} onClose={() => setIsEditModalOpen(false)} maxWidth="sm" fullWidth PaperProps={{ sx: { borderRadius: 2, p: 1 } }}>
          <DialogTitle sx={{ fontWeight: 700, fontFamily: '"Space Grotesk", sans-serif' }}>Edit Entry</DialogTitle>
          <DialogContent>
            <EntryFormFields formData={formData} accounts={accounts} onChange={setFormData} onAddAccountClick={() => setIsQuickAddAccountOpen(true)} />
          </DialogContent>
          <DialogActions sx={{ p: 2 }}>
            <Button onClick={() => setIsEditModalOpen(false)} variant="text" color="inherit">Cancel</Button>
            <Button onClick={handleEditEntry} variant="contained" color="primary">Update Entry</Button>
          </DialogActions>
        </Dialog>

        {/* ── Delete Modal ─────────────────────────────────────────────────────── */}
        <Dialog open={isDeleteModalOpen} onClose={() => setIsDeleteModalOpen(false)} maxWidth="xs" fullWidth PaperProps={{ sx: { borderRadius: 2, p: 1 } }}>
          <DialogTitle sx={{ fontWeight: 700, fontFamily: '"Space Grotesk", sans-serif' }}>Delete Entry</DialogTitle>
          <DialogContent>
            <Typography variant="body2">
              Are you sure you want to delete this entry? This action cannot be undone.
            </Typography>
          </DialogContent>
          <DialogActions sx={{ p: 2 }}>
            <Button onClick={() => setIsDeleteModalOpen(false)} variant="outlined" color="inherit">Cancel</Button>
            <Button onClick={handleDeleteEntry} variant="contained" color="error">Delete</Button>
          </DialogActions>
        </Dialog>

        {/* Inline Quick-Add Account Dialog */}
        <Dialog
          open={isQuickAddAccountOpen}
          onClose={() => setIsQuickAddAccountOpen(false)}
          maxWidth="xs"
          fullWidth
          PaperProps={{ sx: { borderRadius: 2, p: 1 } }}
        >
          <DialogTitle sx={{ fontWeight: 700, fontFamily: '"Space Grotesk", sans-serif' }}>Quick Add Account</DialogTitle>
          <DialogContent>
            <TextField
              fullWidth
              size="small"
              label="Account Name"
              placeholder="e.g. Citi Bank"
              value={quickAddAccountName}
              onChange={(e) => setQuickAddAccountName(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  e.preventDefault();
                  handleQuickAddAccount();
                }
              }}
              disabled={quickAddLoading}
              sx={{ mt: 1 }}
            />
          </DialogContent>
          <DialogActions sx={{ p: 2 }}>
            <Button onClick={() => setIsQuickAddAccountOpen(false)} variant="text" color="inherit">Cancel</Button>
            <Button
              onClick={handleQuickAddAccount}
              variant="contained"
              color="primary"
              disabled={quickAddLoading || !quickAddAccountName.trim()}
            >
              Create
            </Button>
          </DialogActions>
        </Dialog>
      </Container>
    </Box>
  );
}
