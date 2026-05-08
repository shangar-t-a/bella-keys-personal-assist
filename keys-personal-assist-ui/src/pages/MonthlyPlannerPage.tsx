import { useState, useEffect, useCallback, useMemo } from 'react';
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
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Chip,
  Checkbox,
  Stack,
  Divider,
  Tab,
  Tabs,
} from '@mui/material';
import { Grid } from '@mui/material';
import {
  Add as Plus,
  Delete as Trash2,
  Refresh as RotateCcw,
  Sync,
  Settings,
  Edit,
} from '@mui/icons-material';
import { toast } from 'sonner';
import { emsClient } from '@/api/clients/ems-client';
import type {
  MonthlyCategory,
  MonthlySummary,
  MonthlyExpenseItem,
  MonthlyExpenseItemRequest,
} from '@/types/api';
import { formatCurrency } from '@/utils/formatters';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip as RechartsTooltip } from 'recharts';

const MONTH_NAMES = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December',
];

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8', '#82ca9d', '#ffc658', '#8dd1e1'];

const CustomTooltip = ({ active, payload }: any) => {
  if (active && payload && payload.length) {
    return (
      <Box sx={{ 
        bgcolor: 'background.paper', 
        p: 1.5, 
        border: 1, 
        borderColor: 'divider', 
        borderRadius: 2,
        boxShadow: 3
      }}>
        <Typography variant="subtitle2" sx={{ fontWeight: 700 }}>{payload[0].name}</Typography>
        <Typography variant="body2" color="primary.main" sx={{ fontWeight: 600 }}>
          {formatCurrency(payload[0].value)}
        </Typography>
      </Box>
    );
  }
  return null;
};

const renderCustomizedLabel = ({ cx, cy, midAngle, innerRadius, outerRadius, percent }: any) => {
  const RADIAN = Math.PI / 180;
  const radius = innerRadius + (outerRadius - innerRadius) * 0.5;
  const x = cx + radius * Math.cos(-midAngle * RADIAN);
  const y = cy + radius * Math.sin(-midAngle * RADIAN);

  if (percent < 0.05) return null;

  return (
    <text x={x} y={y} fill="white" textAnchor="middle" dominantBaseline="central" style={{ fontSize: '12px', fontWeight: 'bold' }}>
      {`${(percent * 100).toFixed(0)}%`}
    </text>
  );
};

export default function MonthlyPlannerPage() {
  const [activeTab, setActiveTab] = useState(0);
  const [selectedMonth, setSelectedMonth] = useState(new Date().getMonth() + 1);
  const [selectedYear, setSelectedYear] = useState(new Date().getFullYear());
  
  const [summary, setSummary] = useState<MonthlySummary | null>(null);
  const [expenses, setExpenses] = useState<MonthlyExpenseItem[]>([]);
  const [categories, setCategories] = useState<MonthlyCategory[]>([]);
  
  const [isCategoryModalOpen, setIsCategoryModalOpen] = useState(false);
  const [newCategoryName, setNewCategoryName] = useState('');
  const [newCategoryL1, setNewCategoryL1] = useState<'spending' | 'saving'>('spending');
  
  const [isExpenseModalOpen, setIsExpenseModalOpen] = useState(false);
  const [editingExpense, setEditingExpense] = useState<MonthlyExpenseItem | null>(null);
  const [expenseForm, setExpenseForm] = useState<MonthlyExpenseItemRequest>({
    name: '',
    amount: 0,
    category_l1: 'spending',
    category_l2: '',
    is_recurring: true,
  });

  const [confirmDialog, setConfirmDialog] = useState<{
    open: boolean;
    title: string;
    message: string;
    onConfirm: () => void;
  }>({ open: false, title: '', message: '', onConfirm: () => {} });

  const openConfirm = (title: string, message: string, onConfirm: () => void) => {
    setConfirmDialog({ open: true, title, message, onConfirm });
  };

  const closeConfirm = () => {
    setConfirmDialog(prev => ({ ...prev, open: false }));
  };

  // --- Data Fetching ---
  const fetchData = useCallback(async () => {
    try {
      const [sum, exp, cat] = await Promise.all([
        emsClient.getMonthlySummary(selectedYear, selectedMonth),
        emsClient.listMonthlyExpenses(selectedYear, selectedMonth),
        emsClient.listMonthlyCategories(),
      ]);
      setSummary(sum);
      setExpenses(exp);
      setCategories(cat);
    } catch (err) {
      console.error(err);
      toast.error('Failed to fetch monthly planner data');
    }
  }, [selectedMonth, selectedYear]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // --- Calculations ---
  const totals = useMemo(() => {
    const totalSpending = expenses
      .filter(e => e.category_l1 === 'spending')
      .reduce((sum, e) => sum + e.amount, 0);
    const totalSaving = expenses
      .filter(e => e.category_l1 === 'saving')
      .reduce((sum, e) => sum + e.amount, 0);
    const balance = (summary?.salary || 0) - totalSpending - totalSaving;
    
    return { totalSpending, totalSaving, balance };
  }, [expenses, summary]);

  const chartDataL1 = useMemo(() => [
    { name: 'Spending', value: totals.totalSpending },
    { name: 'Saving', value: totals.totalSaving },
    { name: 'Leftover', value: Math.max(0, totals.balance) },
  ], [totals]);

  const chartDataL2 = useMemo(() => {
    const l2Map: Record<string, number> = {};
    expenses.forEach(e => {
      l2Map[e.category_l2] = (l2Map[e.category_l2] || 0) + e.amount;
    });
    return Object.entries(l2Map).map(([name, value]) => ({ name, value }));
  }, [expenses]);

  // --- Handlers ---
  const handleUpdateSalary = async (val: string) => {
    const salary = parseFloat(val) || 0;
    try {
      const updated = await emsClient.updateMonthlySalary(selectedYear, selectedMonth, salary);
      setSummary(updated);
      toast.success('Salary updated');
    } catch {
      toast.error('Failed to update salary');
    }
  };

  const handleToggleStatus = async (expense: MonthlyExpenseItem) => {
    try {
      const newStatus = expense.status === 'pending' ? 'settled' : 'pending';
      await emsClient.updateMonthlyExpense(expense.id, {
        name: expense.name,
        amount: expense.amount,
        category_l1: expense.category_l1,
        category_l2: expense.category_l2,
        is_recurring: expense.is_recurring,
        status: newStatus,
      });
      fetchData();
    } catch {
      toast.error('Failed to update status');
    }
  };

  const handleReset = async () => {
    openConfirm(
      'Reset All Statuses',
      'Are you sure you want to reset all statuses to PENDING? This cannot be undone.',
      async () => {
        try {
          await emsClient.resetMonthlyStatuses(selectedYear, selectedMonth);
          toast.success('Statuses reset');
          fetchData();
        } catch {
          toast.error('Failed to reset statuses');
        }
      }
    );
  };

  const handleSync = async () => {
    try {
      await emsClient.syncMonthlyFromPrevious(selectedYear, selectedMonth);
      toast.success('Synced from previous month');
      fetchData();
    } catch {
      toast.error('Failed to sync. Make sure previous month has recurring expenses.');
    }
  };

  const handleAddCategory = async () => {
    if (!newCategoryName) {
      toast.error('Category name is mandatory');
      return;
    }
    try {
      await emsClient.addMonthlyCategory({ name: newCategoryName, category_l1: newCategoryL1 });
      setNewCategoryName('');
      toast.success('Category added');
      fetchData();
    } catch {
      toast.error('Failed to add category');
    }
  };

  const handleDeleteCategory = async (id: string) => {
    try {
      await emsClient.deleteMonthlyCategory(id);
      toast.success('Category deleted');
      fetchData();
    } catch {
      toast.error('Failed to delete category');
    }
  };

  const handleSaveExpense = async () => {
    if (!expenseForm.name || expenseForm.amount <= 0) {
      toast.error('Name and Amount are mandatory');
      return;
    }
    
    // Default category_l2 to capitalized L1 if empty
    const finalForm = {
      ...expenseForm,
      category_l2: expenseForm.category_l2 || (expenseForm.category_l1.charAt(0).toUpperCase() + expenseForm.category_l1.slice(1))
    };

    try {
      if (editingExpense) {
        await emsClient.updateMonthlyExpense(editingExpense.id, finalForm);
        toast.success('Expense updated');
      } else {
        await emsClient.addMonthlyExpense(selectedYear, selectedMonth, finalForm);
        toast.success('Expense added');
      }
      setIsExpenseModalOpen(false);
      setEditingExpense(null);
      fetchData();
    } catch {
      toast.error('Failed to save expense');
    }
  };

  const handleDeleteExpense = async (id: string) => {
    openConfirm(
      'Delete Expense',
      'Are you sure you want to delete this expense? This cannot be undone.',
      async () => {
        try {
          await emsClient.deleteMonthlyExpense(id);
          toast.success('Expense deleted');
          fetchData();
        } catch {
          toast.error('Failed to delete expense');
        }
      }
    );
  };

  const openAddExpense = () => {
    setEditingExpense(null);
    setExpenseForm({
      name: '',
      amount: 0,
      category_l1: 'spending',
      category_l2: categories.length > 0 ? categories[0].name : '',
      is_recurring: true,
      status: 'pending',
    });
    setIsExpenseModalOpen(true);
  };

  const openEditExpense = (exp: MonthlyExpenseItem) => {
    setEditingExpense(exp);
    setExpenseForm({
      name: exp.name,
      amount: exp.amount,
      category_l1: exp.category_l1,
      category_l2: exp.category_l2,
      is_recurring: exp.is_recurring,
      status: exp.status,
    });
    setIsExpenseModalOpen(true);
  };

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: 'background.default', pb: 8 }}>
      <Container maxWidth="xl" sx={{ py: 4 }}>
        {/* Header */}
        <Stack direction={{ xs: 'column', md: 'row' }} justifyContent="space-between" alignItems={{ md: 'flex-end' }} spacing={2} sx={{ mb: 4 }}>
          <Box>
            <Typography variant="h4" sx={{ fontWeight: 700, fontFamily: '"Space Grotesk", sans-serif' }}>
              Monthly Planner
            </Typography>
            <Typography variant="body1" color="text.secondary">
              Track your monthly budget and expenses checklist
            </Typography>
          </Box>
          
          <Stack direction="row" spacing={2} alignItems="center">
            <FormControl size="small" sx={{ minWidth: 120 }}>
              <InputLabel>Month</InputLabel>
              <Select value={selectedMonth} label="Month" onChange={(e) => setSelectedMonth(Number(e.target.value))}>
                {MONTH_NAMES.map((name, i) => <MenuItem key={i} value={i + 1}>{name}</MenuItem>)}
              </Select>
            </FormControl>
            <TextField
              size="small"
              label="Year"
              type="number"
              value={selectedYear}
              onChange={(e) => setSelectedYear(Number(e.target.value))}
              sx={{ width: 100 }}
            />
            <Button variant="outlined" startIcon={<Settings />} onClick={() => setIsCategoryModalOpen(true)}>
              Categories
            </Button>
          </Stack>
        </Stack>

        {/* Overview Cards */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid size={{ xs: 12, md: 3 }}>
            <Card>
              <CardContent>
                <Stack direction="row" justifyContent="space-between" alignItems="center">
                  <Typography variant="overline" color="text.secondary">Current Salary</Typography>
                  <Typography variant="h6" sx={{ color: 'primary.main', fontWeight: 600 }}>
                    {formatCurrency(summary?.salary || 0)}
                  </Typography>
                </Stack>
                <TextField
                  fullWidth
                  required
                  variant="standard"
                  type="number"
                  placeholder="Enter amount..."
                  value={summary?.salary || 0}
                  onChange={(e) => setSummary(s => s ? { ...s, salary: parseFloat(e.target.value) || 0 } : null)}
                  onBlur={(e) => handleUpdateSalary(e.target.value)}
                  slotProps={{ input: { style: { fontSize: '1.2rem', fontWeight: 700, textAlign: 'left' } } }}
                />
                <Typography variant="caption" color="text.secondary">Net monthly income (auto-formatted above)</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid size={{ xs: 12, md: 3 }}>
            <Card>
              <CardContent>
                <Typography variant="overline" color="text.secondary">Total Spending</Typography>
                <Typography variant="h5" sx={{ fontWeight: 700, color: 'error.main' }}>
                  {formatCurrency(totals.totalSpending)}
                </Typography>
                <Typography variant="caption" color="text.secondary">Sum of all spending items</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid size={{ xs: 12, md: 3 }}>
            <Card>
              <CardContent>
                <Typography variant="overline" color="text.secondary">Total Saving</Typography>
                <Typography variant="h5" sx={{ fontWeight: 700, color: 'success.main' }}>
                  {formatCurrency(totals.totalSaving)}
                </Typography>
                <Typography variant="caption" color="text.secondary">Investments and savings</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid size={{ xs: 12, md: 3 }}>
            <Card>
              <CardContent>
                <Typography variant="overline" color="text.secondary">Remaining Balance</Typography>
                <Typography variant="h5" sx={{ fontWeight: 700, color: totals.balance >= 0 ? 'primary.main' : 'error.main' }}>
                  {formatCurrency(totals.balance)}
                </Typography>
                <Typography variant="caption" color="text.secondary">Unallocated funds</Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Tabs for View */}
        <Tabs value={activeTab} onChange={(_, v) => setActiveTab(v)} sx={{ mb: 3 }}>
          <Tab label="Checklist" />
          <Tab label="Visuals" />
        </Tabs>

        {activeTab === 0 && (
          <Card>
            <Box sx={{ p: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: 1, borderColor: 'divider' }}>
              <Typography variant="h6" sx={{ fontWeight: 600 }}>Expense Checklist</Typography>
              <Stack direction="row" spacing={1}>
                <Button size="small" variant="outlined" startIcon={<Sync />} onClick={handleSync}>Sync Previous</Button>
                <Button size="small" variant="outlined" color="warning" startIcon={<RotateCcw />} onClick={handleReset}>Reset All</Button>
                <Button size="small" variant="contained" startIcon={<Plus />} onClick={openAddExpense}>Add Item</Button>
              </Stack>
            </Box>
            <TableContainer>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell padding="checkbox">Status</TableCell>
                    <TableCell>Name</TableCell>
                    <TableCell>Category L1</TableCell>
                    <TableCell>Category L2</TableCell>
                    <TableCell align="right">Amount</TableCell>
                    <TableCell align="center">Recurring</TableCell>
                    <TableCell align="right">Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {expenses.length === 0 ? (
                    <TableRow><TableCell colSpan={7} align="center" sx={{ py: 4 }}>No items found for this month.</TableCell></TableRow>
                  ) : (
                    expenses.map((exp) => (
                      <TableRow
                        key={exp.id}
                        hover
                        sx={{
                          opacity: exp.status === 'settled' ? 0.4 : 1,
                          transition: 'opacity 0.3s ease',
                        }}
                      >
                        <TableCell padding="checkbox">
                          <Checkbox
                            checked={exp.status === 'settled'}
                            onChange={() => handleToggleStatus(exp)}
                          />
                        </TableCell>
                        <TableCell>{exp.name}</TableCell>
                        <TableCell>
                          <Chip label={exp.category_l1} size="small" color={exp.category_l1 === 'spending' ? 'error' : 'success'} variant="outlined" />
                        </TableCell>
                        <TableCell>{exp.category_l2}</TableCell>
                        <TableCell align="right" sx={{ fontWeight: 600 }}>{formatCurrency(exp.amount)}</TableCell>
                        <TableCell align="center">
                          {exp.is_recurring ? <Typography color="primary" variant="body2">Yes</Typography> : '-'}
                        </TableCell>
                        <TableCell align="right">
                          <IconButton size="small" onClick={() => openEditExpense(exp)}><Edit sx={{ fontSize: 18 }} /></IconButton>
                          <IconButton size="small" color="error" onClick={() => handleDeleteExpense(exp.id)}><Trash2 sx={{ fontSize: 18 }} /></IconButton>
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </TableContainer>
          </Card>
        )}

        {activeTab === 1 && (
          <Grid container spacing={3}>
            <Grid size={{ xs: 12, md: 6 }}>
              <Card sx={{ height: 400 }}>
                <CardContent sx={{ height: '100%' }}>
                  <Typography variant="h6" gutterBottom>Allocation (L1)</Typography>
                  <ResponsiveContainer width="100%" height="90%">
                      <PieChart>
                        <Pie
                          data={chartDataL1}
                          cx="50%"
                          cy="50%"
                          innerRadius={60}
                          outerRadius={100}
                          paddingAngle={5}
                          dataKey="value"
                          labelLine={false}
                          label={renderCustomizedLabel}
                        >
                          {chartDataL1.map((_, index) => (
                            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                          ))}
                        </Pie>
                        <RechartsTooltip content={<CustomTooltip />} />
                        <Legend />
                      </PieChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </Grid>
            <Grid size={{ xs: 12, md: 6 }}>
              <Card sx={{ height: 400 }}>
                <CardContent sx={{ height: '100%' }}>
                  <Typography variant="h6" gutterBottom>Category Breakdown (L2)</Typography>
                  <ResponsiveContainer width="100%" height="90%">
                      <PieChart>
                        <Pie
                          data={chartDataL2}
                          cx="50%"
                          cy="50%"
                          innerRadius={60}
                          outerRadius={100}
                          paddingAngle={2}
                          dataKey="value"
                          labelLine={false}
                          label={renderCustomizedLabel}
                        >
                          {chartDataL2.map((_, index) => (
                            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                          ))}
                        </Pie>
                        <RechartsTooltip content={<CustomTooltip />} />
                        <Legend />
                      </PieChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        )}

        {/* --- Category Management Modal --- */}
        <Dialog open={isCategoryModalOpen} onClose={() => setIsCategoryModalOpen(false)} maxWidth="sm" fullWidth>
          <DialogTitle>Manage Categories</DialogTitle>
          <DialogContent>
            <Box sx={{ mb: 3, pt: 1 }}>
              <Typography variant="subtitle2" gutterBottom>Add New Category</Typography>
              <Stack direction="row" spacing={1}>
                <TextField 
                  size="small" 
                  fullWidth 
                  required
                  placeholder="Category Name" 
                  value={newCategoryName}
                  onChange={(e) => setNewCategoryName(e.target.value)}
                />
                <Select
                  size="small"
                  required
                  value={newCategoryL1}
                  onChange={(e) => setNewCategoryL1(e.target.value as any)}
                  sx={{ minWidth: 120 }}
                >
                  <MenuItem value="spending">Spending</MenuItem>
                  <MenuItem value="saving">Saving</MenuItem>
                </Select>
                <Button variant="contained" onClick={handleAddCategory}>Add</Button>
              </Stack>
            </Box>
            <Divider sx={{ my: 2 }} />
            <Typography variant="subtitle2" gutterBottom>Existing Categories</Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
              {categories.map((cat) => (
                <Chip
                  key={cat.id}
                  label={`${cat.name} (${cat.category_l1})`}
                  onDelete={() => handleDeleteCategory(cat.id)}
                  color={cat.category_l1 === 'spending' ? 'error' : 'success'}
                  variant="outlined"
                />
              ))}
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setIsCategoryModalOpen(false)}>Close</Button>
          </DialogActions>
        </Dialog>

        {/* --- Expense Form Modal --- */}
        <Dialog open={isExpenseModalOpen} onClose={() => setIsExpenseModalOpen(false)} maxWidth="xs" fullWidth>
          <DialogTitle>{editingExpense ? 'Edit Expense' : 'Add Expense'}</DialogTitle>
          <DialogContent>
            <Stack spacing={2} sx={{ pt: 1 }}>
              <TextField 
                fullWidth label="Name" required
                value={expenseForm.name} 
                onChange={(e) => setExpenseForm({ ...expenseForm, name: e.target.value })} 
              />
              <TextField 
                fullWidth label="Amount" required type="number" 
                value={expenseForm.amount} 
                onChange={(e) => setExpenseForm({ ...expenseForm, amount: parseFloat(e.target.value) || 0 })} 
              />
              <FormControl fullWidth required>
                <InputLabel>Category L1</InputLabel>
                <Select
                  value={expenseForm.category_l1}
                  label="Category L1"
                  onChange={(e) => {
                    const newL1 = e.target.value as any;
                    const filtered = categories.filter(c => c.category_l1 === newL1);
                    setExpenseForm({ 
                      ...expenseForm, 
                      category_l1: newL1,
                      category_l2: filtered.length > 0 ? filtered[0].name : ''
                    });
                  }}
                >
                  <MenuItem value="spending">Spending</MenuItem>
                  <MenuItem value="saving">Saving</MenuItem>
                </Select>
              </FormControl>
              <FormControl fullWidth>
                <InputLabel>Category L2 (Optional)</InputLabel>
                <Select
                  value={expenseForm.category_l2}
                  label="Category L2 (Optional)"
                  onChange={(e) => setExpenseForm({ ...expenseForm, category_l2: e.target.value })}
                >
                  <MenuItem value=""><em>None (Defaults to L1)</em></MenuItem>
                  {categories
                    .filter(c => c.category_l1 === expenseForm.category_l1)
                    .map(c => <MenuItem key={c.id} value={c.name}>{c.name}</MenuItem>)
                  }
                  {categories.filter(c => c.category_l1 === expenseForm.category_l1).length === 0 && (
                    <MenuItem disabled>No categories for this type</MenuItem>
                  )}
                </Select>
              </FormControl>
              <Stack direction="row" alignItems="center">
                <Checkbox 
                  checked={expenseForm.is_recurring} 
                  onChange={(e) => setExpenseForm({ ...expenseForm, is_recurring: e.target.checked })} 
                />
                <Typography>Recurring every month</Typography>
              </Stack>
            </Stack>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setIsExpenseModalOpen(false)}>Cancel</Button>
            <Button onClick={handleSaveExpense} variant="contained">Save</Button>
          </DialogActions>
        </Dialog>

        {/* --- Confirm Dialog --- */}
        <Dialog open={confirmDialog.open} onClose={closeConfirm} maxWidth="xs" fullWidth>
          <DialogTitle sx={{ fontWeight: 700 }}>{confirmDialog.title}</DialogTitle>
          <DialogContent>
            <Typography>{confirmDialog.message}</Typography>
          </DialogContent>
          <DialogActions>
            <Button onClick={closeConfirm}>Cancel</Button>
            <Button
              variant="contained"
              color="error"
              onClick={() => { confirmDialog.onConfirm(); closeConfirm(); }}
            >
              Confirm
            </Button>
          </DialogActions>
        </Dialog>
      </Container>
    </Box>
  );
}
