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
  TableSortLabel,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Chip,
  OutlinedInput,
} from '@mui/material';
import { Grid } from '@mui/material';
import {
  Add as Plus,
  Edit,
  Delete as Trash2,
  Refresh as RotateCcw,
  TrendingDown,
  AccountBalance,
  CreditCard,
  Payments,
} from '@mui/icons-material';
import { toast } from 'sonner';
import ModernHeader from '@/components/ModernHeader';
import { emsClient } from '@/api/clients/ems-client';
import type {
  SpendingAccountEntryWithCalculatedFieldsResponse,
  SpendingEntryWithCalcPageResponse,
  PaginationMeta,
  SortOrder,
  SpendingEntrySortField,
} from '@/types/api';
import { formatCurrency } from '@/utils/formatters';

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

const SORT_FIELD_LABELS: Record<SpendingEntrySortField, string> = {
  year: 'Year',
  month: 'Month',
  account_name: 'Account',
  starting_balance: 'Starting Balance',
  current_balance: 'Current Balance',
  current_credit: 'Current Credit',
  balance_after_credit: 'Balance After Credit',
  total_spent: 'Total Spent',
};

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
}

function EntryFormFields({ formData, accounts, onChange }: EntryFormFieldsProps) {
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, pt: 2 }}>
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

  // ── Derived values for metric cards ─────────────────────────────────────────
  const now = new Date();
  const prevMonth = now.getMonth() === 0 ? 12 : now.getMonth(); // 1-12
  const prevMonthYear = now.getMonth() === 0 ? now.getFullYear() - 1 : now.getFullYear();

  // Aggregate the currently loaded page (after server filtering)
  const totalSpent = entries.reduce((s, e) => s + e.totalSpent, 0);
  const totalBalanceAfterCredit = entries.reduce((s, e) => s + e.balanceAfterCredit, 0);

  // Prev-month rows in the current result set (server-filtered)
  const prevMonthEntries = entries.filter(
    (e) => e.month === prevMonth && e.year === prevMonthYear,
  );
  const prevMonthBalance = prevMonthEntries.reduce((s, e) => s + e.currentBalance, 0);
  const prevMonthCredit = prevMonthEntries.reduce((s, e) => s + e.currentCredit, 0);

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
    <TableCell align={align} sortDirection={sortBy === field ? sortOrder : false}>
      <TableSortLabel
        active={sortBy === field}
        direction={sortBy === field ? sortOrder : 'asc'}
        onClick={() => handleSort(field)}
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

  const prevMonthLabel = `${MONTH_NAMES[prevMonth - 1]} ${prevMonthYear}`;

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: 'background.default' }}>
      <ModernHeader />
      <Container maxWidth="xl" sx={{ py: 4 }}>
        {/* Header */}
        <Box sx={{ mb: 4, display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
          <Box>
            <Typography
              variant="h4"
              sx={{ fontWeight: 700, fontFamily: '"Space Grotesk", sans-serif', mb: 0.5 }}
            >
              Spending Account Summary
            </Typography>
            <Typography variant="body1" color="text.secondary">
              {contextLabel} · {paginationMeta.totalElements} entries
            </Typography>
          </Box>
        </Box>

        {/* ── Metric Cards ─────────────────────────────────────────────────────── */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          {/* Card 1 — Balance last month */}
          <Grid size={{ xs: 12, sm: 6, md: 3 }}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                  <AccountBalance fontSize="small" color="success" />
                  <Typography variant="body2" color="text.secondary">
                    Balance · {prevMonthLabel}
                  </Typography>
                </Box>
                <Typography variant="h5" sx={{ fontWeight: 700, color: 'success.main' }}>
                  {formatCurrency(prevMonthBalance)}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Money left in account after spending
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          {/* Card 2 — Credit last month */}
          <Grid size={{ xs: 12, sm: 6, md: 3 }}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                  <CreditCard fontSize="small" color="warning" />
                  <Typography variant="body2" color="text.secondary">
                    Credit Used · {prevMonthLabel}
                  </Typography>
                </Box>
                <Typography variant="h5" sx={{ fontWeight: 700, color: 'warning.main' }}>
                  {formatCurrency(prevMonthCredit)}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Outstanding credit card spend
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          {/* Card 3 — Total spent across current page */}
          <Grid size={{ xs: 12, sm: 6, md: 3 }}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                  <TrendingDown fontSize="small" color="error" />
                  <Typography variant="body2" color="text.secondary">
                    Total Spent · filtered view
                  </Typography>
                </Box>
                <Typography variant="h5" sx={{ fontWeight: 700, color: 'error.main' }}>
                  {formatCurrency(totalSpent)}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Starting − current balance
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          {/* Card 4 — Net balance after credit */}
          <Grid size={{ xs: 12, sm: 6, md: 3 }}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                  <Payments fontSize="small" color="info" />
                  <Typography variant="body2" color="text.secondary">
                    Net Balance · filtered view
                  </Typography>
                </Box>
                <Typography variant="h5" sx={{ fontWeight: 700, color: 'info.main' }}>
                  {formatCurrency(totalBalanceAfterCredit)}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Balance minus outstanding credit
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* ── Filter bar ───────────────────────────────────────────────────────── */}
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Grid container spacing={2} alignItems="center">
              {/* Account filter */}
              <Grid size={{ xs: 12, sm: 6, md: 3 }}>
                <FormControl fullWidth size="small">
                  <InputLabel shrink>Account</InputLabel>
                  <Select
                    value={filterAccount}
                    displayEmpty
                    input={<OutlinedInput notched label="Account" />}
                    onChange={(e) => { setFilterAccount(e.target.value); setPage(0); }}
                    renderValue={(v: string) => v || <em style={{ color: '#9e9e9e' }}>All Accounts</em>}
                  >
                    <MenuItem value="">All Accounts</MenuItem>
                    {accounts.map((a) => (
                      <MenuItem key={a} value={a}>{a}</MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>

              {/* Month filter */}
              <Grid size={{ xs: 12, sm: 6, md: 2 }}>
                <FormControl fullWidth size="small">
                  <InputLabel shrink>Month</InputLabel>
                  <Select
                    value={filterMonth}
                    displayEmpty
                    input={<OutlinedInput notched label="Month" />}
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
              </Grid>

              {/* Year filter */}
              <Grid size={{ xs: 12, sm: 6, md: 2 }}>
                <FormControl fullWidth size="small">
                  <InputLabel shrink>Year</InputLabel>
                  <Select
                    value={filterYear}
                    displayEmpty
                    input={<OutlinedInput notched label="Year" />}
                    onChange={(e) => { setFilterYear(e.target.value); setPage(0); }}
                    renderValue={(v: string) => v || <em style={{ color: '#9e9e9e' }}>All Years</em>}
                  >
                    <MenuItem value="">All Years</MenuItem>
                    {Array.from({ length: 10 }, (_, i) => String(now.getFullYear() - i)).map((y) => (
                      <MenuItem key={y} value={y}>{y}</MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>

              {/* Sort by */}
              <Grid size={{ xs: 12, sm: 6, md: 2 }}>
                <FormControl fullWidth size="small">
                  <InputLabel>Sort By</InputLabel>
                  <Select
                    value={sortBy}
                    label="Sort By"
                    onChange={(e) => { setSortBy(e.target.value as SpendingEntrySortField); setPage(0); }}
                  >
                    {(Object.keys(SORT_FIELD_LABELS) as SpendingEntrySortField[]).map((f) => (
                      <MenuItem key={f} value={f}>{SORT_FIELD_LABELS[f]}</MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>

              {/* Sort order toggle */}
              <Grid size={{ xs: 6, sm: 3, md: 1 }}>
                <Chip
                  label={sortOrder.toUpperCase()}
                  onClick={() => { setSortOrder((p) => (p === 'asc' ? 'desc' : 'asc')); setPage(0); }}
                  color="primary"
                  variant="outlined"
                  sx={{ width: '100%', cursor: 'pointer', fontWeight: 700 }}
                />
              </Grid>

              {/* Actions */}
              <Grid size={{ xs: 6, sm: 3, md: 2 }}>
                <Box sx={{ display: 'flex', gap: 1 }}>
                  <Button
                    variant="outlined"
                    startIcon={<RotateCcw />}
                    onClick={resetFilters}
                    disabled={activeFilterCount === 0}
                    sx={{ flexShrink: 0 }}
                  >
                    Reset
                  </Button>
                  <Button
                    variant="contained"
                    startIcon={<Plus />}
                    onClick={() => { setFormData(DEFAULT_FORM); setIsAddModalOpen(true); }}
                    fullWidth
                  >
                    Add
                  </Button>
                </Box>
              </Grid>
            </Grid>
          </CardContent>
        </Card>

        {/* ── Table ───────────────────────────────────────────────────────────── */}
        <Card>
          <TableContainer>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <SortableCell field="account_name">Account</SortableCell>
                  <SortableCell field="month">Month</SortableCell>
                  <SortableCell field="year">Year</SortableCell>
                  <SortableCell field="starting_balance" align="right">Starting Bal.</SortableCell>
                  <SortableCell field="current_balance" align="right">Current Bal.</SortableCell>
                  <SortableCell field="current_credit" align="right">Credit Used</SortableCell>
                  <SortableCell field="balance_after_credit" align="right">Net Balance</SortableCell>
                  <SortableCell field="total_spent" align="right">Total Spent</SortableCell>
                  <TableCell align="center">Actions</TableCell>
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
                  entries.map((entry) => (
                    <TableRow key={entry.id} hover>
                      <TableCell>{entry.accountName}</TableCell>
                      <TableCell>{MONTH_NAMES[entry.month - 1]}</TableCell>
                      <TableCell>{entry.year}</TableCell>
                      <TableCell align="right">{formatCurrency(entry.startingBalance)}</TableCell>
                      <TableCell align="right">{formatCurrency(entry.currentBalance)}</TableCell>
                      <TableCell align="right">{formatCurrency(entry.currentCredit)}</TableCell>
                      <TableCell align="right">{formatCurrency(entry.balanceAfterCredit)}</TableCell>
                      <TableCell align="right">{formatCurrency(entry.totalSpent)}</TableCell>
                      <TableCell align="center">
                        <IconButton size="small" onClick={() => openEditModal(entry)} color="primary">
                          <Edit fontSize="small" />
                        </IconButton>
                        <IconButton
                          size="small"
                          onClick={() => { setSelectedEntry(entry); setIsDeleteModalOpen(true); }}
                          color="error"
                        >
                          <Trash2 fontSize="small" />
                        </IconButton>
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
          />
        </Card>

        {/* ── Add Modal ────────────────────────────────────────────────────────── */}
        <Dialog open={isAddModalOpen} onClose={() => setIsAddModalOpen(false)} maxWidth="sm" fullWidth>
          <DialogTitle>Add New Entry</DialogTitle>
          <DialogContent>
            <EntryFormFields formData={formData} accounts={accounts} onChange={setFormData} />
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setIsAddModalOpen(false)}>Cancel</Button>
            <Button onClick={handleAddEntry} variant="contained">Add Entry</Button>
          </DialogActions>
        </Dialog>

        {/* ── Edit Modal ───────────────────────────────────────────────────────── */}
        <Dialog open={isEditModalOpen} onClose={() => setIsEditModalOpen(false)} maxWidth="sm" fullWidth>
          <DialogTitle>Edit Entry</DialogTitle>
          <DialogContent>
            <EntryFormFields formData={formData} accounts={accounts} onChange={setFormData} />
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setIsEditModalOpen(false)}>Cancel</Button>
            <Button onClick={handleEditEntry} variant="contained">Update Entry</Button>
          </DialogActions>
        </Dialog>

        {/* ── Delete Modal ─────────────────────────────────────────────────────── */}
        <Dialog open={isDeleteModalOpen} onClose={() => setIsDeleteModalOpen(false)}>
          <DialogTitle>Delete Entry</DialogTitle>
          <DialogContent>
            <Typography>
              Are you sure you want to delete this entry? This action cannot be undone.
            </Typography>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setIsDeleteModalOpen(false)}>Cancel</Button>
            <Button onClick={handleDeleteEntry} variant="contained" color="error">Delete</Button>
          </DialogActions>
        </Dialog>
      </Container>
    </Box>
  );
}
