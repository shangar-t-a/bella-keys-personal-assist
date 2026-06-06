import { useState, useEffect, useCallback, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import {  Box,
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
  Tab,
  Tabs,
  Paper,
  OutlinedInput,
  Tooltip,
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
import { formatCurrency, formatCompactRupees } from '@/utils/formatters';
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
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState(0);
  const [selectedMonth, setSelectedMonth] = useState(new Date().getMonth() + 1);
  const [selectedYear, setSelectedYear] = useState(new Date().getFullYear());
  
  const [summary, setSummary] = useState<MonthlySummary | null>(null);
  const [expenses, setExpenses] = useState<MonthlyExpenseItem[]>([]);
  const [categories, setCategories] = useState<MonthlyCategory[]>([]);
  const [isEditingSalary, setIsEditingSalary] = useState(false);
  const [salaryInputVal, setSalaryInputVal] = useState('');
  
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

  const handleSaveSalary = () => {
    setIsEditingSalary(false);
    handleUpdateSalary(salaryInputVal);
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
        {/* Header */}
        <Stack direction={{ xs: 'column', md: 'row' }} justifyContent="space-between" alignItems={{ md: 'center' }} spacing={2} sx={{ mb: 2 }}>
          <Box>
            <Typography variant="h5" sx={{ fontWeight: 700, fontFamily: '"Space Grotesk", sans-serif', lineHeight: 1.2 }}>
              Monthly Budget
            </Typography>
            <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 500 }}>
              Track your monthly budget and expenses checklist.
            </Typography>
          </Box>
          
          <Stack direction="row" spacing={2} alignItems="center">
            <FormControl size="small" sx={{ minWidth: 120 }}>
              <InputLabel id="budget-month-label">Month</InputLabel>
              <Select
                labelId="budget-month-label"
                value={selectedMonth}
                label="Month"
                input={<OutlinedInput label="Month" sx={{ borderRadius: 1.5, fontSize: '0.85rem' }} />}
                onChange={(e) => setSelectedMonth(Number(e.target.value))}
              >
                {MONTH_NAMES.map((name, i) => <MenuItem key={i} value={i + 1}>{name}</MenuItem>)}
              </Select>
            </FormControl>
            <TextField
              size="small"
              label="Year"
              type="number"
              value={selectedYear}
              onChange={(e) => setSelectedYear(Number(e.target.value))}
              sx={{ width: 100, '& .MuiOutlinedInput-root': { borderRadius: 1.5, fontSize: '0.85rem' } }}
            />
            <Button
              variant="outlined"
              color="inherit"
              size="small"
              startIcon={<Settings />}
              onClick={() => navigate('/settings?tab=categories')}
              sx={{ py: 0.6, px: 2, fontWeight: 600, textTransform: 'none', borderRadius: 1.5, fontSize: '0.85rem' }}
            >
              Categories
            </Button>
          </Stack>
        </Stack>

        {/* ── Summary Card: Prominent Portfolio Metrics ────────────────────────── */}
        <Card variant="outlined" sx={{ borderRadius: 2, border: '1px solid', borderColor: 'divider', boxShadow: 'none', mb: 2 }}>
          <Grid container>
            {/* Block 1: Current Salary (Interactive) */}
            <Grid size={{ xs: 6, md: 3 }} sx={{
              p: 2.5,
              borderRight: '1px solid',
              borderRightColor: 'divider',
              borderBottom: { xs: '1px solid', md: 'none' },
              borderBottomColor: { xs: 'divider', md: 'transparent' },
            }}>
              <Typography variant="caption" color="text.disabled" sx={{ fontWeight: 600, textTransform: 'uppercase', letterSpacing: 0.8, fontSize: '0.68rem', display: 'block', mb: 0.5 }}>
                Current Salary
              </Typography>
              {isEditingSalary ? (
                <TextField
                  size="small"
                  type="number"
                  autoFocus
                  value={salaryInputVal}
                  onChange={(e) => setSalaryInputVal(e.target.value)}
                  onBlur={handleSaveSalary}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') handleSaveSalary();
                    if (e.key === 'Escape') setIsEditingSalary(false);
                  }}
                  sx={{
                    width: '100%',
                    '& .MuiOutlinedInput-root': { borderRadius: 1.5, fontSize: '1rem', fontWeight: 700 }
                  }}
                />
              ) : (
                <Box
                  sx={{ display: 'flex', alignItems: 'center', gap: 1, cursor: 'pointer' }}
                  onClick={() => { setSalaryInputVal(String(summary?.salary || 0)); setIsEditingSalary(true); }}
                >
                  <Typography variant="h5" sx={{ fontWeight: 700, fontFamily: '"Space Grotesk", sans-serif', color: 'primary.main', fontSize: '1.3rem' }}>
                    {formatCompactRupees(summary?.salary || 0)}
                  </Typography>
                  <Edit sx={{ fontSize: 16, color: 'text.secondary', opacity: 0.6, '&:hover': { opacity: 1 } }} />
                </Box>
              )}
            </Grid>

            {/* Block 2: Total Spending */}
            <Grid size={{ xs: 6, md: 3 }} sx={{
              p: 2.5,
              borderRight: { xs: 'none', md: '1px solid' },
              borderRightColor: { xs: 'transparent', md: 'divider' },
              borderBottom: { xs: '1px solid', md: 'none' },
              borderBottomColor: { xs: 'divider', md: 'transparent' },
            }}>
              <Typography variant="caption" color="text.disabled" sx={{ fontWeight: 600, textTransform: 'uppercase', letterSpacing: 0.8, fontSize: '0.68rem', display: 'block', mb: 0.5 }}>
                Total Spending
              </Typography>
              <Typography variant="h5" sx={{ fontWeight: 700, fontFamily: '"Space Grotesk", sans-serif', color: 'error.main', fontSize: '1.3rem' }}>
                {formatCompactRupees(totals.totalSpending)}
              </Typography>
            </Grid>

            {/* Block 3: Total Saving */}
            <Grid size={{ xs: 6, md: 3 }} sx={{
              p: 2.5,
              borderRight: '1px solid',
              borderRightColor: 'divider',
            }}>
              <Typography variant="caption" color="text.disabled" sx={{ fontWeight: 600, textTransform: 'uppercase', letterSpacing: 0.8, fontSize: '0.68rem', display: 'block', mb: 0.5 }}>
                Total Saving
              </Typography>
              <Typography variant="h5" sx={{ fontWeight: 700, fontFamily: '"Space Grotesk", sans-serif', color: 'success.main', fontSize: '1.3rem' }}>
                {formatCompactRupees(totals.totalSaving)}
              </Typography>
            </Grid>

            {/* Block 4: Remaining Balance */}
            <Grid size={{ xs: 6, md: 3 }} sx={{ p: 2.5 }}>
              <Typography variant="caption" color="text.disabled" sx={{ fontWeight: 600, textTransform: 'uppercase', letterSpacing: 0.8, fontSize: '0.68rem', display: 'block', mb: 0.5 }}>
                Remaining Balance
              </Typography>
              <Typography variant="h5" sx={{ fontWeight: 700, fontFamily: '"Space Grotesk", sans-serif', color: totals.balance >= 0 ? 'primary.main' : 'error.main', fontSize: '1.3rem' }}>
                {formatCompactRupees(totals.balance)}
              </Typography>
            </Grid>
          </Grid>
        </Card>

        {/* Tabs for View */}
        <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
          <Tabs
            value={activeTab}
            onChange={(_, v) => setActiveTab(v)}
            sx={{
              minHeight: 36,
              '& .MuiTab-root': {
                fontFamily: '"Space Grotesk", sans-serif',
                fontWeight: 600,
                fontSize: '0.875rem',
                textTransform: 'none',
                minHeight: 36,
                px: 0,
                mr: 3,
                py: 0.5,
              },
            }}
          >
            <Tab label="Checklist" />
            <Tab label="Visuals" />
          </Tabs>
        </Box>

        {activeTab === 0 && (
          <>
            {/* Checklist Toolbar Card */}
            <Card variant="outlined" sx={{ borderRadius: 2, border: '1px solid', borderColor: 'divider', boxShadow: 'none', px: 2, py: 1.25, mb: 2 }}>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1.5, justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography variant="body2" sx={{ fontWeight: 700, fontFamily: '"Space Grotesk", sans-serif', textTransform: 'uppercase', letterSpacing: 0.5, color: 'text.secondary' }}>
                  Expense Checklist
                </Typography>
                <Stack direction="row" spacing={1.5}>
                  <Button
                    variant="outlined"
                    color="inherit"
                    size="small"
                    startIcon={<Sync />}
                    onClick={handleSync}
                    sx={{ py: 0.6, px: 2, fontWeight: 600, textTransform: 'none', borderRadius: 1.5, fontSize: '0.85rem' }}
                  >
                    Sync Previous
                  </Button>
                  <Button
                    variant="outlined"
                    color="warning"
                    size="small"
                    startIcon={<RotateCcw />}
                    onClick={handleReset}
                    sx={{ py: 0.6, px: 2, fontWeight: 600, textTransform: 'none', borderRadius: 1.5, fontSize: '0.85rem' }}
                  >
                    Reset All
                  </Button>
                  <Button
                    variant="contained"
                    color="primary"
                    size="small"
                    startIcon={<Plus />}
                    onClick={openAddExpense}
                    sx={{ py: 0.6, px: 2, fontWeight: 600, textTransform: 'none', borderRadius: 1.5, fontSize: '0.85rem' }}
                  >
                    Add Item
                  </Button>
                </Stack>
              </Box>
            </Card>

            {/* Checklist Table Card */}
            <Card variant="outlined" sx={{ borderRadius: 2, overflow: 'hidden', border: '1px solid', borderColor: 'divider', boxShadow: 'none', mb: 2 }}>
              <TableContainer component={Paper} elevation={0} sx={{ borderRadius: 0, bgcolor: 'transparent' }}>
                <Table size="small">
                  <TableHead sx={{ bgcolor: (theme) => theme.palette.mode === 'dark' ? 'rgba(30, 41, 59, 0.5)' : '#f1f5f9' }}>
                    <TableRow>
                      <TableCell padding="checkbox" sx={{ pl: 3 }}>Status</TableCell>
                      <TableCell sx={{ fontWeight: 700, py: 1.25, fontSize: '0.78rem', textTransform: 'uppercase', letterSpacing: 0.5, color: 'text.secondary' }}>Name</TableCell>
                      <TableCell sx={{ fontWeight: 700, py: 1.25, fontSize: '0.78rem', textTransform: 'uppercase', letterSpacing: 0.5, color: 'text.secondary' }}>Type</TableCell>
                      <TableCell sx={{ fontWeight: 700, py: 1.25, fontSize: '0.78rem', textTransform: 'uppercase', letterSpacing: 0.5, color: 'text.secondary' }}>Category</TableCell>
                      <TableCell align="right" sx={{ fontWeight: 700, py: 1.25, fontSize: '0.78rem', textTransform: 'uppercase', letterSpacing: 0.5, color: 'text.secondary' }}>Amount</TableCell>
                      <TableCell align="center" sx={{ fontWeight: 700, py: 1.25, fontSize: '0.78rem', textTransform: 'uppercase', letterSpacing: 0.5, color: 'text.secondary' }}>Recurring</TableCell>
                      <TableCell align="right" sx={{ pr: 3, fontWeight: 700, py: 1.25, fontSize: '0.78rem', textTransform: 'uppercase', letterSpacing: 0.5, color: 'text.secondary' }}>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {expenses.length === 0 ? (
                      <TableRow>
                        <TableCell colSpan={7} align="center" sx={{ py: 4, color: 'text.secondary' }}>
                          No items found for this month.
                        </TableCell>
                      </TableRow>
                    ) : (
                      expenses.map((exp, idx) => (
                        <TableRow
                          key={exp.id}
                          hover
                          sx={{
                            opacity: exp.status === 'settled' ? 0.45 : 1,
                            transition: 'opacity 0.2s ease',
                            '& td': { py: 1 },
                            bgcolor: idx % 2 === 0
                              ? 'transparent'
                              : (theme) => theme.palette.mode === 'dark' ? 'rgba(255,255,255,0.018)' : 'rgba(0,0,0,0.018)',
                            '&:hover': { bgcolor: 'action.hover' },
                          }}
                        >
                          <TableCell padding="checkbox" sx={{ pl: 3 }}>
                            <Checkbox
                              checked={exp.status === 'settled'}
                              onChange={() => handleToggleStatus(exp)}
                              size="small"
                            />
                          </TableCell>
                          <TableCell sx={{ fontWeight: 600 }}>{exp.name}</TableCell>
                          <TableCell>
                            <Chip
                              label={exp.category_l1 === 'spending' ? 'Spending' : 'Saving'}
                              size="small"
                              color={exp.category_l1 === 'spending' ? 'error' : 'success'}
                              variant="outlined"
                              sx={{ fontWeight: 700, fontSize: '0.68rem', height: 20 }}
                            />
                          </TableCell>
                          <TableCell>{exp.category_l2}</TableCell>
                          <TableCell align="right" sx={{ fontWeight: 700 }}>{formatCurrency(exp.amount)}</TableCell>
                          <TableCell align="center">
                            {exp.is_recurring ? <Typography color="primary.main" variant="body2" sx={{ fontWeight: 600 }}>Yes</Typography> : '-'}
                          </TableCell>
                          <TableCell align="right" sx={{ pr: 3, whiteSpace: 'nowrap' }}>
                            <Tooltip title="Edit">
                              <IconButton size="small" color="secondary" onClick={() => openEditExpense(exp)}>
                                <Edit sx={{ fontSize: 18 }} />
                              </IconButton>
                            </Tooltip>
                            <Tooltip title="Delete">
                              <IconButton size="small" color="error" onClick={() => handleDeleteExpense(exp.id)}>
                                <Trash2 sx={{ fontSize: 18 }} />
                              </IconButton>
                            </Tooltip>
                          </TableCell>
                        </TableRow>
                      ))
                    )}
                  </TableBody>
                </Table>
              </TableContainer>
            </Card>
          </>
        )}

        {activeTab === 1 && (
          <Grid container spacing={3}>
            <Grid size={{ xs: 12, md: 6 }}>
              <Card variant="outlined" sx={{ height: 400, borderRadius: 2, border: '1px solid', borderColor: 'divider', boxShadow: 'none' }}>
                <CardContent sx={{ height: '100%', p: 3 }}>
                  <Typography variant="body2" sx={{ fontWeight: 700, fontFamily: '"Space Grotesk", sans-serif', textTransform: 'uppercase', letterSpacing: 0.5, color: 'text.secondary', mb: 2 }}>
                    Allocation Type
                  </Typography>
                  <ResponsiveContainer width="100%" height="85%">
                    <PieChart>
                      <Pie
                        data={chartDataL1}
                        cx="50%"
                        cy="50%"
                        innerRadius={60}
                        outerRadius={90}
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
              <Card variant="outlined" sx={{ height: 400, borderRadius: 2, border: '1px solid', borderColor: 'divider', boxShadow: 'none' }}>
                <CardContent sx={{ height: '100%', p: 3 }}>
                  <Typography variant="body2" sx={{ fontWeight: 700, fontFamily: '"Space Grotesk", sans-serif', textTransform: 'uppercase', letterSpacing: 0.5, color: 'text.secondary', mb: 2 }}>
                    Category Breakdown
                  </Typography>
                  <ResponsiveContainer width="100%" height="85%">
                    <PieChart>
                      <Pie
                        data={chartDataL2}
                        cx="50%"
                        cy="50%"
                        innerRadius={60}
                        outerRadius={90}
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

        {/* --- Expense Form Modal --- */}
        <Dialog open={isExpenseModalOpen} onClose={() => setIsExpenseModalOpen(false)} maxWidth="xs" fullWidth PaperProps={{ sx: { borderRadius: 2, p: 1 } }}>
          <DialogTitle sx={{ fontWeight: 700, fontFamily: '"Space Grotesk", sans-serif' }}>
            {editingExpense ? 'Edit Expense' : 'Add Expense'}
          </DialogTitle>
          <DialogContent>
            <Stack spacing={2.5} sx={{ pt: 1.5 }}>
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
                <InputLabel id="expense-type-label">Type</InputLabel>
                <Select
                  labelId="expense-type-label"
                  value={expenseForm.category_l1}
                  label="Type"
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
                <InputLabel id="expense-category-label">Category (Optional)</InputLabel>
                <Select
                  labelId="expense-category-label"
                  value={expenseForm.category_l2}
                  label="Category (Optional)"
                  onChange={(e) => setExpenseForm({ ...expenseForm, category_l2: e.target.value })}
                >
                  <MenuItem value=""><em>None (Defaults to Type)</em></MenuItem>
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
                <Typography variant="body2">Recurring every month</Typography>
              </Stack>
            </Stack>
          </DialogContent>
          <DialogActions sx={{ p: 2 }}>
            <Button onClick={() => setIsExpenseModalOpen(false)} variant="text" color="inherit">Cancel</Button>
            <Button onClick={handleSaveExpense} variant="contained" color="primary">Save</Button>
          </DialogActions>
        </Dialog>

        {/* --- Confirm Dialog --- */}
        <Dialog open={confirmDialog.open} onClose={closeConfirm} maxWidth="xs" fullWidth PaperProps={{ sx: { borderRadius: 2, p: 1 } }}>
          <DialogTitle sx={{ fontWeight: 700, fontFamily: '"Space Grotesk", sans-serif' }}>{confirmDialog.title}</DialogTitle>
          <DialogContent>
            <Typography variant="body2">{confirmDialog.message}</Typography>
          </DialogContent>
          <DialogActions sx={{ p: 2 }}>
            <Button onClick={closeConfirm} variant="outlined" color="inherit">Cancel</Button>
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
