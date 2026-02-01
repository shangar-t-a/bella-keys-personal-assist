import { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Card,
  CardContent,
  Button,
  TextField,
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
} from '@mui/material';
import Grid from '@mui/material/Grid2';
import {
  Add as Plus,
  Edit,
  Delete as Trash2,
  Refresh as RotateCcw,
} from '@mui/icons-material';
import { toast } from 'sonner';
import ModernHeader from '@/components/ModernHeader';
import { emsClient } from '@/api/clients/ems-client';
import type { SpendingAccountEntryWithCalculatedFieldsResponse } from '@/types/api';
import { formatCurrency } from '@/utils/formatters';

interface SpendingAccountEntry extends SpendingAccountEntryWithCalculatedFieldsResponse { }

interface FormData {
  accountName: string;
  month: string;
  year: number;
  startingBalance: number;
  currentBalance: number;
  currentCredit: number;
}

const MONTHS = [
  'January',
  'February',
  'March',
  'April',
  'May',
  'June',
  'July',
  'August',
  'September',
  'October',
  'November',
  'December',
];

export default function SpendingAccountSummaryPage() {
  const [entries, setEntries] = useState<SpendingAccountEntry[]>([]);
  const [, setLoading] = useState(true);
  const [accounts, setAccounts] = useState<string[]>([]);
  const [availableMonths, setAvailableMonths] = useState<string[]>([]);
  const [availableYears, setAvailableYears] = useState<number[]>([]);

  // Filters
  const [selectedAccount, setSelectedAccount] = useState<string>('');
  const [selectedMonth, setSelectedMonth] = useState<string>('All Months');
  const [selectedYear, setSelectedYear] = useState<string>('All Years');

  // Pagination
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);

  // Modals
  const [isAddModalOpen, setIsAddModalOpen] = useState(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [selectedEntry, setSelectedEntry] = useState<SpendingAccountEntry | null>(null);
  const [formData, setFormData] = useState<FormData>({
    accountName: '',
    month: 'January',
    year: new Date().getFullYear(),
    startingBalance: 0,
    currentBalance: 0,
    currentCredit: 0,
  });

  const fetchAccounts = async () => {
    try {
      const accountData = await emsClient.getAllAccounts();
      const accountNames = accountData.map((account) => account.accountName);
      setAccounts(accountNames);

      if (accountNames.length > 0 && !selectedAccount) {
        setSelectedAccount(accountNames[0]);
      }
    } catch (error) {
      console.error('Error fetching accounts:', error);
      toast.error('Failed to fetch accounts');
    }
  };

  const fetchData = async () => {
    try {
      setLoading(true);
      const data = await emsClient.getAllSpendingAccountEntries();
      setEntries(data);

      // Extract unique months and years
      const months = Array.from(new Set(data.map((entry) => entry.month)));
      const years = Array.from(new Set(data.map((entry) => entry.year))).sort((a, b) => b - a);

      setAvailableMonths(months);
      setAvailableYears(years);
    } catch (error) {
      console.error('Error fetching data:', error);
      toast.error('Failed to fetch spending account data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAccounts();
    fetchData();
  }, []);

  // Filter entries
  const filteredEntries = entries.filter((entry) => {
    if (selectedAccount && entry.accountName !== selectedAccount) return false;
    if (selectedMonth !== 'All Months' && entry.month !== selectedMonth) return false;
    if (selectedYear !== 'All Years' && entry.year !== parseInt(selectedYear)) return false;
    return true;
  });

  // Pagination
  const paginatedEntries = filteredEntries.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage);

  const handleChangePage = (_event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleAddEntry = async () => {
    try {
      await emsClient.addSpendingAccountEntry(formData);
      toast.success('Entry added successfully');
      setIsAddModalOpen(false);
      fetchData();
      resetForm();
    } catch (error) {
      console.error('Error adding entry:', error);
      toast.error('Failed to add entry');
    }
  };

  const handleEditEntry = async () => {
    if (!selectedEntry) return;
    try {
      await emsClient.editSpendingAccountEntry(selectedEntry.id, formData);
      toast.success('Entry updated successfully');
      setIsEditModalOpen(false);
      fetchData();
      resetForm();
    } catch (error) {
      console.error('Error updating entry:', error);
      toast.error('Failed to update entry');
    }
  };

  const handleDeleteEntry = async () => {
    if (!selectedEntry) return;
    try {
      await emsClient.deleteSpendingAccountEntry(selectedEntry.id);
      toast.success('Entry deleted successfully');
      setIsDeleteModalOpen(false);
      fetchData();
      setSelectedEntry(null);
    } catch (error) {
      console.error('Error deleting entry:', error);
      toast.error('Failed to delete entry');
    }
  };

  const resetForm = () => {
    setFormData({
      accountName: '',
      month: 'January',
      year: new Date().getFullYear(),
      startingBalance: 0,
      currentBalance: 0,
      currentCredit: 0,
    });
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

  const openDeleteModal = (entry: SpendingAccountEntry) => {
    setSelectedEntry(entry);
    setIsDeleteModalOpen(true);
  };

  const resetFilters = () => {
    setSelectedMonth('All Months');
    setSelectedYear('All Years');
    if (accounts.length > 0) {
      setSelectedAccount(accounts[0]);
    }
  };

  // Calculate metrics
  const totalSpent = filteredEntries.reduce((sum, entry) => sum + entry.totalSpent, 0);
  const totalCredit = filteredEntries.reduce((sum, entry) => sum + entry.currentCredit, 0);

  // Get last month's data
  const currentDate = new Date();
  const lastMonth = currentDate.getMonth() === 0 ? 11 : currentDate.getMonth() - 1;
  const lastMonthYear = currentDate.getMonth() === 0 ? currentDate.getFullYear() - 1 : currentDate.getFullYear();
  const lastMonthName = MONTHS[lastMonth];

  const lastMonthEntries = entries.filter(
    (entry) => entry.month === lastMonthName && entry.year === lastMonthYear && entry.accountName === selectedAccount
  );

  const lastMonthBalance = lastMonthEntries.reduce((sum, entry) => sum + entry.currentBalance, 0);
  const lastMonthCredit = lastMonthEntries.reduce((sum, entry) => sum + entry.currentCredit, 0);

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: 'background.default' }}>
      <ModernHeader />
      <Container maxWidth="xl" sx={{ py: 4 }}>
        {/* Header */}
        <Box sx={{ mb: 4 }}>
          <Typography
            variant="h4"
            sx={{
              fontWeight: 700,
              fontFamily: '"Space Grotesk", sans-serif',
              mb: 1,
            }}
          >
            Spending Account Summary
          </Typography>
          <Typography variant="body1" color="text.secondary">
            Track and manage your spending accounts
          </Typography>
        </Box>

        {/* Metrics Cards */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid size={{ xs: 12, sm: 6, md: 3 }}>
            <Card>
              <CardContent>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Current Balance (Last Month)
                </Typography>
                <Typography variant="h5" sx={{ fontWeight: 700, color: 'success.main' }}>
                  {formatCurrency(lastMonthBalance)}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid size={{ xs: 12, sm: 6, md: 3 }}>
            <Card>
              <CardContent>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Current Credit (Last Month)
                </Typography>
                <Typography variant="h5" sx={{ fontWeight: 700, color: 'error.main' }}>
                  {formatCurrency(lastMonthCredit)}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid size={{ xs: 12, sm: 6, md: 3 }}>
            <Card>
              <CardContent>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Total Spending (Filtered)
                </Typography>
                <Typography variant="h5" sx={{ fontWeight: 700, color: 'error.main' }}>
                  {formatCurrency(totalSpent)}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  From filtered data
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid size={{ xs: 12, sm: 6, md: 3 }}>
            <Card>
              <CardContent>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  Total Credit (Filtered)
                </Typography>
                <Typography variant="h5" sx={{ fontWeight: 700, color: 'error.main' }}>
                  {formatCurrency(totalCredit)}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  From filtered data
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Filters and Actions */}
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Grid container spacing={2} alignItems="center">
              <Grid size={{ xs: 12, sm: 6, md: 3 }}>
                <FormControl fullWidth size="small">
                  <InputLabel>Account</InputLabel>
                  <Select
                    value={selectedAccount}
                    label="Account"
                    onChange={(e) => setSelectedAccount(e.target.value)}
                  >
                    {accounts.map((account) => (
                      <MenuItem key={account} value={account}>
                        {account}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              <Grid size={{ xs: 12, sm: 6, md: 3 }}>
                <FormControl fullWidth size="small">
                  <InputLabel>Month</InputLabel>
                  <Select
                    value={selectedMonth}
                    label="Month"
                    onChange={(e) => setSelectedMonth(e.target.value)}
                  >
                    <MenuItem value="All Months">All Months</MenuItem>
                    {availableMonths.map((month) => (
                      <MenuItem key={month} value={month}>
                        {month}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              <Grid size={{ xs: 12, sm: 6, md: 3 }}>
                <FormControl fullWidth size="small">
                  <InputLabel>Year</InputLabel>
                  <Select
                    value={selectedYear}
                    label="Year"
                    onChange={(e) => setSelectedYear(e.target.value)}
                  >
                    <MenuItem value="All Years">All Years</MenuItem>
                    {availableYears.map((year) => (
                      <MenuItem key={year} value={year.toString()}>
                        {year}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              <Grid size={{ xs: 12, sm: 6, md: 3 }}>
                <Box sx={{ display: 'flex', gap: 1 }}>
                  <Button
                    variant="outlined"
                    startIcon={<RotateCcw />}
                    onClick={resetFilters}
                    sx={{ flexShrink: 0 }}
                  >
                    Reset Filters
                  </Button>
                  <Button
                    variant="contained"
                    startIcon={<Plus />}
                    onClick={() => setIsAddModalOpen(true)}
                    fullWidth
                  >
                    Add Entry
                  </Button>
                </Box>
              </Grid>
            </Grid>
          </CardContent>
        </Card>

        {/* Table */}
        <Card>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Account</TableCell>
                  <TableCell>Month</TableCell>
                  <TableCell>Year</TableCell>
                  <TableCell align="right">Starting Balance</TableCell>
                  <TableCell align="right">Current Balance</TableCell>
                  <TableCell align="right">Current Credit</TableCell>
                  <TableCell align="right">Balance After Credit</TableCell>
                  <TableCell align="right">Total Spent</TableCell>
                  <TableCell align="center">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {paginatedEntries.map((entry) => (
                  <TableRow key={entry.id} hover>
                    <TableCell>{entry.accountName}</TableCell>
                    <TableCell>{entry.month}</TableCell>
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
                      <IconButton size="small" onClick={() => openDeleteModal(entry)} color="error">
                        <Trash2 fontSize="small" />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
          <TablePagination
            rowsPerPageOptions={[10, 25, 50, 100]}
            component="div"
            count={filteredEntries.length}
            rowsPerPage={rowsPerPage}
            page={page}
            onPageChange={handleChangePage}
            onRowsPerPageChange={handleChangeRowsPerPage}
          />
        </Card>

        {/* Add Modal */}
        <Dialog open={isAddModalOpen} onClose={() => setIsAddModalOpen(false)} maxWidth="sm" fullWidth>
          <DialogTitle>Add New Entry</DialogTitle>
          <DialogContent>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, pt: 2 }}>
              <FormControl fullWidth>
                <InputLabel>Account</InputLabel>
                <Select
                  value={formData.accountName}
                  label="Account"
                  onChange={(e) => setFormData({ ...formData, accountName: e.target.value })}
                >
                  {accounts.map((account) => (
                    <MenuItem key={account} value={account}>
                      {account}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
              <FormControl fullWidth>
                <InputLabel>Month</InputLabel>
                <Select
                  value={formData.month}
                  label="Month"
                  onChange={(e) => setFormData({ ...formData, month: e.target.value })}
                >
                  {MONTHS.map((month) => (
                    <MenuItem key={month} value={month}>
                      {month}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
              <TextField
                fullWidth
                label="Year"
                type="number"
                value={formData.year}
                onChange={(e) => setFormData({ ...formData, year: parseInt(e.target.value) })}
              />
              <TextField
                fullWidth
                label="Starting Balance"
                type="number"
                value={formData.startingBalance}
                onChange={(e) => setFormData({ ...formData, startingBalance: parseFloat(e.target.value) })}
              />
              <TextField
                fullWidth
                label="Current Balance"
                type="number"
                value={formData.currentBalance}
                onChange={(e) => setFormData({ ...formData, currentBalance: parseFloat(e.target.value) })}
              />
              <TextField
                fullWidth
                label="Current Credit"
                type="number"
                value={formData.currentCredit}
                onChange={(e) => setFormData({ ...formData, currentCredit: parseFloat(e.target.value) })}
              />
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setIsAddModalOpen(false)}>Cancel</Button>
            <Button onClick={handleAddEntry} variant="contained">
              Add Entry
            </Button>
          </DialogActions>
        </Dialog>

        {/* Edit Modal */}
        <Dialog open={isEditModalOpen} onClose={() => setIsEditModalOpen(false)} maxWidth="sm" fullWidth>
          <DialogTitle>Edit Entry</DialogTitle>
          <DialogContent>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, pt: 2 }}>
              <FormControl fullWidth>
                <InputLabel>Account</InputLabel>
                <Select
                  value={formData.accountName}
                  label="Account"
                  onChange={(e) => setFormData({ ...formData, accountName: e.target.value })}
                >
                  {accounts.map((account) => (
                    <MenuItem key={account} value={account}>
                      {account}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
              <FormControl fullWidth>
                <InputLabel>Month</InputLabel>
                <Select
                  value={formData.month}
                  label="Month"
                  onChange={(e) => setFormData({ ...formData, month: e.target.value })}
                >
                  {MONTHS.map((month) => (
                    <MenuItem key={month} value={month}>
                      {month}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
              <TextField
                fullWidth
                label="Year"
                type="number"
                value={formData.year}
                onChange={(e) => setFormData({ ...formData, year: parseInt(e.target.value) })}
              />
              <TextField
                fullWidth
                label="Starting Balance"
                type="number"
                value={formData.startingBalance}
                onChange={(e) => setFormData({ ...formData, startingBalance: parseFloat(e.target.value) })}
              />
              <TextField
                fullWidth
                label="Current Balance"
                type="number"
                value={formData.currentBalance}
                onChange={(e) => setFormData({ ...formData, currentBalance: parseFloat(e.target.value) })}
              />
              <TextField
                fullWidth
                label="Current Credit"
                type="number"
                value={formData.currentCredit}
                onChange={(e) => setFormData({ ...formData, currentCredit: parseFloat(e.target.value) })}
              />
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setIsEditModalOpen(false)}>Cancel</Button>
            <Button onClick={handleEditEntry} variant="contained">
              Update Entry
            </Button>
          </DialogActions>
        </Dialog>

        {/* Delete Modal */}
        <Dialog open={isDeleteModalOpen} onClose={() => setIsDeleteModalOpen(false)}>
          <DialogTitle>Delete Entry</DialogTitle>
          <DialogContent>
            <Typography>Are you sure you want to delete this entry? This action cannot be undone.</Typography>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setIsDeleteModalOpen(false)}>Cancel</Button>
            <Button onClick={handleDeleteEntry} variant="contained" color="error">
              Delete
            </Button>
          </DialogActions>
        </Dialog>
      </Container>
    </Box>
  );
}
