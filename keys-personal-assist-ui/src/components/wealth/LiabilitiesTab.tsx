import { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  Card,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  TextField,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Tooltip,
  CircularProgress,
  Divider,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  InputAdornment,
  useTheme,
  alpha,
  LinearProgress,
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  History as HistoryIcon,
  Search as SearchIcon,
  AccountBalance as SecuredIcon,
  CreditCard as CreditCardIcon,
  MoneyOff as UnsecuredIcon,
  MonetizationOn as OtherIcon,
  ShowChart as AnalyticsIcon,
  InfoOutlined as InfoIcon,
} from '@mui/icons-material';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  Legend,
} from 'recharts';
import { emsClient } from '@/api/clients/ems-client';
import type { Liability, LiabilitySummary, LiabilityUpdateRequest, LiabilityCategory, LiabilityProjections } from '@/types/liability';
import { formatCurrency, formatCompactRupees } from '@/utils/formatters';
import { toast } from 'sonner';
import AddLiabilityWizard from './AddLiabilityWizard';
import LiabilityTransactionsModal from './LiabilityTransactionsModal';

const getTicks = (points: { date: string }[]) => {
  if (!points || points.length === 0) return [];
  const len = points.length;
  let step = 3; // Default show every 3 months
  if (len > 72) {
    step = 12; // Show every 12 months (yearly)
  } else if (len > 36) {
    step = 6; // Show every 6 months
  }

  const ticks = [];
  let i = 0;
  for (i = 0; i < len; i += step) {
    ticks.push(points[i].date);
  }
  // Always include the last point's date to show the maturity/end date clearly
  if (ticks[ticks.length - 1] !== points[len - 1].date) {
    ticks.push(points[len - 1].date);
  }
  return ticks;
};

interface LiabilitiesTabProps {
  onLiabilitiesLoad?: (count: number) => void;
}

export default function LiabilitiesTab({ onLiabilitiesLoad }: LiabilitiesTabProps) {
  const theme = useTheme();

  const CATEGORY_META = {
    SECURED_LOAN: {
      label: 'Secured Loans',
      color: theme.palette.primary.main,
      icon: SecuredIcon,
      bg: alpha(theme.palette.primary.main, 0.1),
    },
    UNSECURED_LOAN: {
      label: 'Unsecured Loans',
      color: theme.palette.secondary.main,
      icon: UnsecuredIcon,
      bg: alpha(theme.palette.secondary.main, 0.1),
    },
    REVOLVING_CREDIT: {
      label: 'Revolving Credit',
      color: theme.palette.warning.main,
      icon: CreditCardIcon,
      bg: alpha(theme.palette.warning.main, 0.1),
    },
    OTHER: {
      label: 'Other Liabilities',
      color: theme.palette.success.main,
      icon: OtherIcon,
      bg: alpha(theme.palette.success.main, 0.1),
    },
  };

  const [liabilities, setLiabilities] = useState<Liability[]>([]);
  const [summary, setSummary] = useState<LiabilitySummary | null>(null);
  const [loading, setLoading] = useState(true);

  // Modals state
  const [wizardOpen, setWizardOpen] = useState(false);
  const [txModalOpen, setTxModalOpen] = useState(false);
  const [selectedLiability, setSelectedLiability] = useState<Liability | null>(null);

  // Projections & Analytics panel state
  const [expandedLiabilityId, setExpandedLiabilityId] = useState<string | null>(null);
  const [projections, setProjections] = useState<LiabilityProjections | null>(null);
  const [projectionsLoading, setProjectionsLoading] = useState(false);

  const handleToggleProjections = async (id: string) => {
    if (expandedLiabilityId === id) {
      setExpandedLiabilityId(null);
      setProjections(null);
    } else {
      setExpandedLiabilityId(id);
      setProjections(null);
      setProjectionsLoading(true);
      try {
        const data = await emsClient.getLiabilityProjections(id);
        setProjections(data);
      } catch (err: any) {
        console.error(err);
        toast.error(err.message || 'Failed to fetch projections');
        setExpandedLiabilityId(null);
      } finally {
        setProjectionsLoading(false);
      }
    }
  };

  // Edit Modal State
  const [categories, setCategories] = useState<LiabilityCategory[]>([]);
  const [editOpen, setEditOpen] = useState(false);
  const [editLiabilityId, setEditLiabilityId] = useState('');
  const [editName, setEditName] = useState('');
  const [editNotes, setEditNotes] = useState('');
  const [editCategoryId, setEditCategoryId] = useState('');
  const [editSubcategoryId, setEditSubcategoryId] = useState<string | null>(null);
  const [editInterestRate, setEditInterestRate] = useState<string>('');
  const [editInterestCompounding, setEditInterestCompounding] = useState<string>('MONTHLY');
  const [editEmiAmount, setEditEmiAmount] = useState<string>('');
  const [editEmiStartDate, setEditEmiStartDate] = useState<string>('');
  const [editMaturityDate, setEditMaturityDate] = useState<string>('');

  // Custom Confirm Dialog State
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
    setConfirmDialog((prev) => ({ ...prev, open: false }));
  };

  // Filtering state
  const [search, setSearch] = useState('');
  const [selectedCategories, setSelectedCategories] = useState<string[]>([
    'SECURED_LOAN', 'UNSECURED_LOAN', 'REVOLVING_CREDIT', 'OTHER'
  ]);

  // Accordion expanded states
  const [expanded, setExpanded] = useState<Record<string, boolean>>({
    SECURED_LOAN: true,
    UNSECURED_LOAN: true,
    REVOLVING_CREDIT: true,
    OTHER: true,
  });

  const fetchData = async () => {
    setLoading(true);
    try {
      const [liabilitiesData, summaryData, categoriesData] = await Promise.all([
        emsClient.listLiabilities(),
        emsClient.getLiabilitySummary(),
        emsClient.getAllLiabilityCategories(),
      ]);
      setLiabilities(liabilitiesData);
      setSummary(summaryData);
      setCategories(categoriesData);
      
      if (onLiabilitiesLoad) {
        onLiabilitiesLoad(liabilitiesData.length);
      }
    } catch (err) {
      console.error(err);
      toast.error('Failed to load liabilities data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleToggleCategory = (code: string) => {
    setExpanded((prev) => ({ ...prev, [code]: !prev[code] }));
  };

  const handleToggleCategoryFilter = (code: string) => {
    setSelectedCategories((prev) =>
      prev.includes(code)
        ? prev.filter((c) => c !== code)
        : [...prev, code]
    );
  };

  const handleOpenEdit = (liability: Liability) => {
    setEditLiabilityId(liability.id);
    setEditName(liability.name);
    setEditNotes(liability.notes || '');
    setEditCategoryId(liability.categoryId);
    setEditSubcategoryId(liability.subcategoryId);
    setEditInterestRate(liability.interestRate != null ? String(liability.interestRate) : '');
    setEditInterestCompounding(liability.interestCompounding || 'MONTHLY');
    setEditEmiAmount(liability.emiAmount != null ? String(liability.emiAmount) : '');
    setEditEmiStartDate(liability.emiStartDate ? liability.emiStartDate.split('T')[0] : '');
    setEditMaturityDate(liability.maturityDate ? liability.maturityDate.split('T')[0] : '');
    setEditOpen(true);
  };

  const handleUpdateLiability = async () => {
    if (!editName.trim()) {
      toast.error('Liability name is required');
      return;
    }

    const editingLiability = liabilities.find(l => l.id === editLiabilityId);
    const editingSubcategory = categories
      .flatMap(c => c.subcategories)
      .find(s => s.id === editingLiability?.subcategoryId);

    if (editingSubcategory?.hasInterest) {
      if (editInterestRate) {
        const r = parseFloat(editInterestRate);
        if (isNaN(r) || r < 0) {
          toast.error('Interest rate must be a non-negative number');
          return;
        }
      }
      if (editEmiAmount) {
        const emi = parseFloat(editEmiAmount);
        if (isNaN(emi) || emi < 0) {
          toast.error('EMI amount must be a non-negative number');
          return;
        }
      }
    }

    const updateData: LiabilityUpdateRequest = {
      categoryId: editCategoryId || null,
      name: editName.trim() || null,
      subcategoryId: editSubcategoryId,
      interestDetails:
        editingSubcategory?.hasInterest
          ? {
              interestRate: editInterestRate ? parseFloat(editInterestRate) : 0,
              compounding: editInterestCompounding as import('@/types/asset').CompoundingFrequency,
              emiAmount: editEmiAmount ? parseFloat(editEmiAmount) : null,
              emiStartDate: editEmiStartDate ? new Date(editEmiStartDate).toISOString() : null,
              maturityDate:
                editingSubcategory?.hasMaturity && editMaturityDate
                  ? new Date(editMaturityDate).toISOString()
                  : null,
            }
          : null,
      notes: editNotes.trim() || null,
    };

    try {
      await emsClient.updateLiability(editLiabilityId, updateData);
      toast.success('Liability details updated');
      setEditOpen(false);
      fetchData();
    } catch (err: any) {
      console.error(err);
      toast.error(err.message || 'Failed to update liability');
    }
  };

  const handleDeleteLiability = (liability: Liability) => {
    openConfirm(
      'Delete Liability',
      `Are you sure you want to delete "${liability.name}"? This will delete all its transaction ledger records. This action cannot be undone.`,
      async () => {
        try {
          await emsClient.deleteLiability(liability.id);
          toast.success('Liability deleted');
          fetchData();
        } catch (err) {
          console.error(err);
          toast.error('Failed to delete liability');
        }
      }
    );
  };

  const handleOpenLedger = (liability: Liability) => {
    setSelectedLiability(liability);
    setTxModalOpen(true);
  };

  // Remaining Tenure Projection Helper
  const getRemainingTenureText = (liability: Liability) => {
    if (liability.currentValue <= 0) return 'Paid Off';
    if (liability.remainingTenureMonths == null) return 'No End Date';
    
    const months = liability.remainingTenureMonths;
    const prefix = liability.maturityDate ? '' : '~';
    const yrs = Math.floor(months / 12);
    const remainingMonths = months % 12;
    
    return yrs > 0 
      ? `${prefix}${yrs}y ${remainingMonths}m` 
      : `${prefix}${months}m`;
  };

  // Filter
  const filteredLiabilities = liabilities.filter((l) => {
    const matchesSearch = l.name.toLowerCase().includes(search.toLowerCase());
    const matchesCategory = selectedCategories.includes(l.categoryCode);
    return matchesSearch && matchesCategory;
  });

  // Group
  const liabilitiesByCategory: Record<string, Liability[]> = {
    SECURED_LOAN: [],
    UNSECURED_LOAN: [],
    REVOLVING_CREDIT: [],
    OTHER: [],
  };

  filteredLiabilities.forEach((l) => {
    if (liabilitiesByCategory[l.categoryCode]) {
      liabilitiesByCategory[l.categoryCode].push(l);
    }
  });

  if (loading && !summary) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', py: 12 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>

      {/* ── Toolbar Card ────────────────────────────────────────────────────── */}
      <Card variant="outlined" sx={{ borderRadius: 2, border: '1px solid', borderColor: 'divider', boxShadow: 'none', px: 2, py: 1.25 }}>
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1.5, justifyContent: 'space-between', alignItems: 'center' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, flexGrow: 1, flexWrap: 'wrap' }}>
            <TextField
              size="small"
              placeholder="Search liabilities..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              sx={{
                width: 200,
                '& .MuiOutlinedInput-root': { borderRadius: 1.5, fontSize: '0.85rem' },
              }}
              InputProps={{ startAdornment: <SearchIcon color="action" sx={{ mr: 0.75, fontSize: 17 }} /> }}
            />
            
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.75, flexWrap: 'wrap' }}>
              {Object.entries(CATEGORY_META).map(([code, meta]) => {
                const isActive = selectedCategories.includes(code);
                const IconComponent = meta.icon;
                return (
                  <Box
                    key={code}
                    onClick={() => handleToggleCategoryFilter(code)}
                    sx={{
                      display: 'flex', alignItems: 'center', gap: 0.5,
                      px: 1.25, py: 0.4,
                      borderRadius: '20px',
                      border: '1.5px solid',
                      borderColor: isActive ? meta.color : 'divider',
                      bgcolor: isActive ? meta.bg : 'transparent',
                      color: isActive ? meta.color : 'text.disabled',
                      cursor: 'pointer',
                      userSelect: 'none',
                      transition: 'all 0.15s ease',
                      '&:hover': { borderColor: meta.color, bgcolor: meta.bg, color: meta.color },
                    }}
                  >
                    <IconComponent sx={{ fontSize: 12 }} />
                    <Typography sx={{ fontSize: '0.72rem', fontWeight: 700, lineHeight: 1 }}>
                      {meta.label}
                    </Typography>
                  </Box>
                );
              })}
            </Box>
          </Box>

          <Button
            variant="contained"
            color="primary"
            startIcon={<AddIcon />}
            onClick={() => setWizardOpen(true)}
            sx={{ py: 0.6, px: 2, fontWeight: 600, textTransform: 'none', borderRadius: 1.5, fontSize: '0.85rem', flexShrink: 0 }}
          >
            Add Liability
          </Button>
        </Box>
      </Card>

      {/* ── Summary Card ────────────────────────────────────────────────────── */}
      {summary && (
        <Card variant="outlined" sx={{ borderRadius: 2, border: '1px solid', borderColor: 'divider', boxShadow: 'none' }}>
          <Box sx={{ display: 'flex' }}>
            <Box sx={{ flex: 1, px: 3, py: 2 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 0.5 }}>
                <Typography variant="caption" color="text.disabled" sx={{ fontWeight: 600, textTransform: 'uppercase', letterSpacing: 0.8, fontSize: '0.68rem', display: 'block' }}>
                  Total Borrowed
                </Typography>
                <Tooltip title="The total original amount of principal money borrowed across all active liabilities." arrow>
                  <InfoIcon sx={{ fontSize: '0.8rem', color: 'text.secondary', cursor: 'pointer' }} />
                </Tooltip>
              </Box>
              <Typography variant="h5" sx={{ fontWeight: 700, fontFamily: '"Space Grotesk", sans-serif', color: 'text.primary', fontSize: '1.3rem' }}>
                {formatCompactRupees(summary.totalOriginal)}
              </Typography>
            </Box>
            <Divider orientation="vertical" flexItem />
            
            <Box sx={{ flex: 1, px: 3, py: 2 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 0.5 }}>
                <Typography variant="caption" color="text.disabled" sx={{ fontWeight: 600, textTransform: 'uppercase', letterSpacing: 0.8, fontSize: '0.68rem', display: 'block' }}>
                  Outstanding Balance
                </Typography>
                <Tooltip title="The current unpaid balance remaining on your liabilities." arrow>
                  <InfoIcon sx={{ fontSize: '0.8rem', color: 'text.secondary', cursor: 'pointer' }} />
                </Tooltip>
              </Box>
              <Typography variant="h5" sx={{ fontWeight: 700, fontFamily: '"Space Grotesk", sans-serif', color: 'error.main', fontSize: '1.3rem' }}>
                {formatCompactRupees(summary.totalOutstanding)}
              </Typography>
            </Box>
            <Divider orientation="vertical" flexItem />

            <Box sx={{ flex: 1, px: 3, py: 2 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 0.5 }}>
                <Typography variant="caption" color="text.disabled" sx={{ fontWeight: 600, textTransform: 'uppercase', letterSpacing: 0.8, fontSize: '0.68rem', display: 'block' }}>
                  Total Repaid
                </Typography>
                <Tooltip title="The total amount of principal and interest you have successfully paid back." arrow>
                  <InfoIcon sx={{ fontSize: '0.8rem', color: 'text.secondary', cursor: 'pointer' }} />
                </Tooltip>
              </Box>
              <Typography variant="h5" sx={{ fontWeight: 700, fontFamily: '"Space Grotesk", sans-serif', color: 'success.main', fontSize: '1.3rem' }}>
                {formatCompactRupees(summary.totalRepaid)}
              </Typography>
            </Box>
            <Divider orientation="vertical" flexItem />

            <Box sx={{ flex: 1, px: 3, py: 2 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 0.5 }}>
                <Typography variant="caption" color="text.disabled" sx={{ fontWeight: 600, textTransform: 'uppercase', letterSpacing: 0.8, fontSize: '0.68rem', display: 'block' }}>
                  Interest Accrued
                </Typography>
                <Tooltip title="The total interest that has accumulated on your interest-bearing liabilities since inception." arrow>
                  <InfoIcon sx={{ fontSize: '0.8rem', color: 'text.secondary', cursor: 'pointer' }} />
                </Tooltip>
              </Box>
              <Typography variant="h5" sx={{ fontWeight: 700, fontFamily: '"Space Grotesk", sans-serif', color: 'warning.main', fontSize: '1.3rem' }}>
                {formatCompactRupees(summary.accumulatedInterest)}
              </Typography>
            </Box>
          </Box>
        </Card>
      )}

      {/* ── Table Card ──────────────────────────────────────────────────────── */}
      <Card variant="outlined" sx={{ borderRadius: 2, overflow: 'hidden', border: '1px solid', borderColor: 'divider', boxShadow: 'none' }}>
        <TableContainer component={Paper} elevation={0} sx={{ borderRadius: 0, bgcolor: 'transparent' }}>
          <Table size="small">
            <TableHead sx={{ bgcolor: (theme) => theme.palette.mode === 'dark' ? 'rgba(30, 41, 59, 0.5)' : '#f1f5f9' }}>
              <TableRow>
                <TableCell sx={{ pl: 3, fontWeight: 700, py: 1.25, fontSize: '0.78rem', textTransform: 'uppercase', letterSpacing: 0.5, color: 'text.secondary' }}>Name / Lender</TableCell>
                <TableCell sx={{ fontWeight: 700, py: 1.25, fontSize: '0.78rem', textTransform: 'uppercase', letterSpacing: 0.5, color: 'text.secondary' }}>Subtype</TableCell>
                <TableCell align="right" sx={{ fontWeight: 700, py: 1.25, fontSize: '0.78rem', textTransform: 'uppercase', letterSpacing: 0.5, color: 'text.secondary' }}>Original Limit</TableCell>
                <TableCell align="right" sx={{ fontWeight: 700, py: 1.25, fontSize: '0.78rem', textTransform: 'uppercase', letterSpacing: 0.5, color: 'text.secondary' }}>Outstanding</TableCell>
                <TableCell sx={{ fontWeight: 700, py: 1.25, fontSize: '0.78rem', textTransform: 'uppercase', letterSpacing: 0.5, color: 'text.secondary', width: '20%' }}>Payoff Progress</TableCell>
                <TableCell sx={{ fontWeight: 700, py: 1.25, fontSize: '0.78rem', textTransform: 'uppercase', letterSpacing: 0.5, color: 'text.secondary' }}>Tenure Left</TableCell>
                <TableCell align="center" sx={{ pr: 3, fontWeight: 700, py: 1.25, fontSize: '0.78rem', textTransform: 'uppercase', letterSpacing: 0.5, color: 'text.secondary' }}>Actions</TableCell>
              </TableRow>
            </TableHead>

            <TableBody>
              {Object.entries(CATEGORY_META).map(([code, meta], idx, arr) => {
                const catSummary = summary?.categoryBreakdowns.find((cb) => cb.categoryCode === code);
                const catLiabilities = liabilitiesByCategory[code];
                if (!selectedCategories.includes(code)) return null;

                const isOpen = expanded[code] !== false;

                const original = catSummary?.totalOriginal ?? 0;
                const outstanding = catSummary?.totalOutstanding ?? 0;
                const IconComponent = meta.icon;
                const visibleArr = arr.filter(([c]) => selectedCategories.includes(c));
                const isLast = visibleArr[visibleArr.length - 1][0] === code;

                return [
                  /* Category Row Group */
                  <TableRow
                    key={`cat-${code}`}
                    onClick={() => handleToggleCategory(code)}
                    sx={{
                      cursor: 'pointer',
                      bgcolor: (theme) => theme.palette.mode === 'dark' ? 'rgba(30, 41, 59, 0.3)' : '#f8fafc',
                      borderLeft: `3px solid ${meta.color}`,
                      '&:hover': { bgcolor: (theme) => theme.palette.mode === 'dark' ? 'rgba(30, 41, 59, 0.5)' : '#f1f5f9' },
                      borderTop: idx === 0 ? 'none' : '1px solid',
                      borderTopColor: 'divider',
                    }}
                  >
                    <TableCell
                      colSpan={4}
                      sx={{
                        py: 1.5,
                        pl: 2,
                        borderBottom: isOpen && catLiabilities.length > 0 ? '1px solid' : 'none',
                        borderBottomColor: 'divider',
                      }}
                    >
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.25 }}>
                        <Box sx={{
                          color: 'text.secondary',
                          display: 'flex', alignItems: 'center',
                          transition: 'transform 0.2s',
                          transform: isOpen ? 'rotate(0deg)' : 'rotate(-90deg)',
                        }}>
                          <ExpandMoreIcon sx={{ fontSize: 18 }} />
                        </Box>
                        <Box sx={{
                          width: 28, height: 28, borderRadius: '50%',
                          bgcolor: meta.bg, color: meta.color,
                          display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0,
                        }}>
                          <IconComponent sx={{ fontSize: 15 }} />
                        </Box>
                        <Typography variant="body2" sx={{ fontWeight: 700, fontFamily: '"Space Grotesk", sans-serif' }}>
                          {meta.label}
                        </Typography>
                        <Chip
                          label={catLiabilities.length}
                          size="small"
                          sx={{
                            height: 18, fontSize: '0.68rem', fontWeight: 700,
                            bgcolor: meta.bg, color: meta.color,
                            '& .MuiChip-label': { px: 0.75 },
                          }}
                        />
                      </Box>
                    </TableCell>

                    <TableCell
                      colSpan={3}
                      align="right"
                      sx={{
                        pr: 3, py: 1.5,
                        borderBottom: 'none',
                        whiteSpace: 'nowrap',
                      }}
                    >
                      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: 3.5 }}>
                        <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 600 }}>
                          Borrowed: {formatCompactRupees(original)}
                        </Typography>
                        <Typography variant="body2" sx={{ fontWeight: 700, color: 'error.main', fontFamily: '"Space Grotesk", sans-serif', fontSize: '0.95rem' }}>
                          Outstanding: {formatCompactRupees(outstanding)}
                        </Typography>
                      </Box>
                    </TableCell>
                  </TableRow>,

                  /* Individual Liability rows */
                  ...catLiabilities.flatMap((liability, lIdx) => {
                    const sub = categories
                      .flatMap(c => c.subcategories)
                      .find(s => s.id === liability.subcategoryId);
                    const canShowProjections = !!(sub?.hasInterest && liability.interestRate != null);
                    const isExpanded = expandedLiabilityId === liability.id;

                    const row1 = (
                      <TableRow
                        key={`row-${liability.id}`}
                        sx={{
                          display: isOpen ? undefined : 'none',
                          '& td': { py: 1 },
                          bgcolor: lIdx % 2 === 0
                            ? 'transparent'
                            : (theme) => theme.palette.mode === 'dark' ? 'rgba(255,255,255,0.018)' : 'rgba(0,0,0,0.018)',
                          '&:hover': { bgcolor: 'action.hover' },
                          '&:last-of-type td': { borderBottom: isLast && !isExpanded ? 'none' : undefined },
                        }}
                      >
                        <TableCell sx={{ pl: 4 }}>
                          <Typography variant="body2" sx={{ fontWeight: 600 }}>{liability.name}</Typography>
                          {liability.notes && (
                            <Typography variant="caption" color="text.secondary" display="block" sx={{ maxWidth: 220, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                              {liability.notes}
                            </Typography>
                          )}
                        </TableCell>
                        
                        <TableCell>
                          <Chip
                            label={sub?.name || liability.categoryCode}
                            size="small"
                            sx={{ fontSize: '0.7rem', fontWeight: 500, height: 20 }}
                          />
                        </TableCell>

                        <TableCell align="right" sx={{ fontWeight: 500 }}>{formatCurrency(liability.originalValue)}</TableCell>
                        <TableCell align="right" sx={{ fontWeight: 600, color: 'error.main' }}>{formatCurrency(liability.currentValue)}</TableCell>
                        
                        <TableCell>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                            <Box sx={{ flexGrow: 1 }}>
                              <LinearProgress
                                variant="determinate"
                                value={liability.progressPct}
                                color={liability.progressPct > 75 ? 'success' : liability.progressPct > 35 ? 'primary' : 'warning'}
                                sx={{ height: 6, borderRadius: 3 }}
                              />
                            </Box>
                            <Typography variant="caption" sx={{ fontWeight: 700, width: '40px', textAlign: 'right' }}>
                              {liability.progressPct}%
                            </Typography>
                          </Box>
                        </TableCell>

                        <TableCell>
                          <Typography variant="body2" sx={{ fontWeight: 600 }}>
                            {getRemainingTenureText(liability)}
                          </Typography>
                          {liability.interestRate && (
                            <Typography variant="caption" color="text.secondary">
                              @{liability.interestRate}% Int.
                            </Typography>
                          )}
                        </TableCell>

                        <TableCell align="center" sx={{ pr: 3, whiteSpace: 'nowrap' }}>
                          {canShowProjections && (
                            <Tooltip title="Toggle Payoff Projections">
                              <IconButton
                                onClick={() => handleToggleProjections(liability.id)}
                                size="small"
                                color={isExpanded ? 'warning' : 'info'}
                                sx={{ mr: 0.5 }}
                              >
                                <AnalyticsIcon fontSize="small" />
                              </IconButton>
                            </Tooltip>
                          )}
                          <Tooltip title="Transactions Ledger">
                            <IconButton onClick={() => handleOpenLedger(liability)} size="small" color="primary">
                              <HistoryIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Edit Metadata">
                            <IconButton onClick={() => handleOpenEdit(liability)} size="small" color="secondary">
                              <EditIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Delete Liability">
                            <IconButton onClick={() => handleDeleteLiability(liability)} size="small" color="error">
                              <DeleteIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        </TableCell>
                      </TableRow>
                    );

                    if (!isExpanded || !isOpen) {
                      return [row1];
                    }

                    const row2 = (
                      <TableRow
                        key={`expanded-${liability.id}`}
                        sx={{
                          display: isOpen ? undefined : 'none',
                          bgcolor: (theme) => theme.palette.mode === 'dark' ? 'rgba(30, 41, 59, 0.12)' : 'rgba(15, 23, 42, 0.02)',
                          '& td': { borderBottom: isLast ? 'none' : undefined }
                        }}
                      >
                        <TableCell colSpan={7} sx={{ p: 3 }}>
                          {projectionsLoading ? (
                            <Box sx={{ display: 'flex', justifyContent: 'center', py: 4, gap: 1.5, alignItems: 'center' }}>
                              <CircularProgress size={24} />
                              <Typography variant="body2" color="text.secondary">Computing projections...</Typography>
                            </Box>
                          ) : projections ? (
                            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3.5 }}>
                              
                              {/* Projections Stats Grid */}
                              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2.5 }}>
                                {/* Dates Card */}
                                <Card variant="outlined" sx={{ flex: '1 1 220px', p: 2, borderRadius: 2, bgcolor: 'background.paper', boxShadow: 'none' }}>
                                  <Typography variant="caption" color="text.disabled" sx={{ fontWeight: 600, textTransform: 'uppercase', letterSpacing: 0.5, fontSize: '0.625rem' }}>
                                    Loan Timeline
                                  </Typography>
                                  <Box sx={{ mt: 1 }}>
                                    <Typography variant="body2" sx={{ fontWeight: 600 }}>
                                      Ideal End: <span style={{ fontFamily: '"Space Grotesk", sans-serif' }}>
                                        {projections.metrics.idealEndDate ? new Date(projections.metrics.idealEndDate).toLocaleDateString('en-IN', { month: 'short', year: 'numeric' }) : '-'}
                                      </span>
                                    </Typography>
                                    <Typography variant="body2" sx={{ fontWeight: 600, color: projections.metrics.tenureSavedMonths >= 0 ? 'success.main' : 'error.main', mt: 0.5 }}>
                                      Projected End: <span style={{ fontFamily: '"Space Grotesk", sans-serif' }}>
                                        {projections.metrics.projectedEndDate ? new Date(projections.metrics.projectedEndDate).toLocaleDateString('en-IN', { month: 'short', year: 'numeric' }) : '-'}
                                      </span>
                                    </Typography>
                                  </Box>
                                </Card>

                                {/* Tenure Card */}
                                <Card variant="outlined" sx={{ flex: '1 1 220px', p: 2, borderRadius: 2, bgcolor: 'background.paper', boxShadow: 'none' }}>
                                  <Typography variant="caption" color="text.disabled" sx={{ fontWeight: 600, textTransform: 'uppercase', letterSpacing: 0.5, fontSize: '0.625rem' }}>
                                    Tenure Impact
                                  </Typography>
                                  <Box sx={{ mt: 1 }}>
                                    <Typography variant="h6" sx={{ fontWeight: 700, color: projections.metrics.tenureSavedMonths >= 0 ? 'success.main' : 'error.main', fontFamily: '"Space Grotesk", sans-serif' }}>
                                      {projections.metrics.tenureSavedMonths >= 0 
                                        ? `${projections.metrics.tenureSavedMonths} months saved`
                                        : `${Math.abs(projections.metrics.tenureSavedMonths)} months delayed`}
                                    </Typography>
                                    <Typography variant="caption" color="text.secondary">
                                      Remaining: {projections.metrics.remainingTenureMonths}m (Ideal: {projections.metrics.idealTenureMonths}m)
                                    </Typography>
                                  </Box>
                                </Card>

                                {/* Interest Saved Card */}
                                <Card variant="outlined" sx={{ flex: '1 1 220px', p: 2, borderRadius: 2, bgcolor: 'background.paper', boxShadow: 'none' }}>
                                  <Typography variant="caption" color="text.disabled" sx={{ fontWeight: 600, textTransform: 'uppercase', letterSpacing: 0.5, fontSize: '0.625rem' }}>
                                    Interest Impact
                                  </Typography>
                                  <Box sx={{ mt: 1 }}>
                                    <Typography variant="h6" sx={{ fontWeight: 700, color: projections.metrics.interestSaved >= 0 ? 'success.main' : 'error.main', fontFamily: '"Space Grotesk", sans-serif' }}>
                                      {projections.metrics.interestSaved >= 0
                                        ? `Saved ${formatCompactRupees(projections.metrics.interestSaved)}`
                                        : `Extra ${formatCompactRupees(Math.abs(projections.metrics.interestSaved))} interest`}
                                    </Typography>
                                    <Typography variant="caption" color="text.secondary">
                                      Projected Int: {formatCompactRupees(projections.metrics.totalInterestProjected)} (Ideal: {formatCompactRupees(projections.metrics.totalInterestIdeal)})
                                    </Typography>
                                  </Box>
                                </Card>
                              </Box>

                              {/* Chart Panel */}
                              <Box sx={{ width: '100%', height: 280, pr: 2 }}>
                                <Typography variant="body2" sx={{ fontWeight: 700, color: 'text.secondary', mb: 2, fontSize: '0.72rem', textTransform: 'uppercase', letterSpacing: 0.5 }}>
                                  Payoff Curves: Ideal vs Actual & Future Trajectory
                                </Typography>
                                <ResponsiveContainer width="100%" height="100%">
                                  <LineChart data={projections.projectionPoints} margin={{ top: 15, right: 10, left: 10, bottom: 15 }}>
                                    <CartesianGrid strokeDasharray="3 3" stroke={theme.palette.divider} />
                                    <XAxis 
                                      dataKey="date" 
                                      stroke={theme.palette.text.secondary} 
                                      style={{ fontSize: '0.7rem' }} 
                                      minTickGap={45}
                                      ticks={getTicks(projections.projectionPoints)}
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
                                      yAxisId="left"
                                      stroke={theme.palette.text.secondary} 
                                      style={{ fontSize: '0.7rem' }} 
                                      tickFormatter={(val) => formatCompactRupees(val)}
                                      width={75}
                                      tickMargin={8}
                                    />
                                    <YAxis 
                                      yAxisId="right"
                                      orientation="right"
                                      stroke={theme.palette.warning.main} 
                                      style={{ fontSize: '0.7rem' }} 
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
                                        fontSize: '0.78rem'
                                      }}
                                    />
                                    <Legend wrapperStyle={{ fontSize: '0.75rem', paddingTop: 10 }} />
                                    <Line 
                                      yAxisId="left"
                                      name="Ideal Amortization Curve" 
                                      type="monotone" 
                                      dataKey="idealBalance" 
                                      stroke={theme.palette.text.disabled} 
                                      strokeDasharray="4 4"
                                      strokeWidth={1.5} 
                                      dot={false}
                                    />
                                    <Line 
                                      yAxisId="left"
                                      name="Actual / Projected Curve" 
                                      type="monotone" 
                                      dataKey="actualBalance" 
                                      stroke={theme.palette.info.main} 
                                      strokeWidth={2.5} 
                                      dot={false}
                                    />
                                    <Line 
                                      yAxisId="right"
                                      name="Ideal Interest Accrued" 
                                      type="monotone" 
                                      dataKey="idealInterestPaid" 
                                      stroke={alpha(theme.palette.warning.main, 0.4)} 
                                      strokeDasharray="4 4"
                                      strokeWidth={1.5} 
                                      dot={false}
                                    />
                                    <Line 
                                      yAxisId="right"
                                      name="Actual / Projected Interest Accrued" 
                                      type="monotone" 
                                      dataKey="actualInterestPaid" 
                                      stroke={theme.palette.warning.main} 
                                      strokeWidth={2.5} 
                                      dot={false}
                                    />
                                  </LineChart>
                                </ResponsiveContainer>
                              </Box>
                            </Box>
                          ) : (
                            <Typography variant="body2" color="error" align="center">Failed to load projections.</Typography>
                          )}
                        </TableCell>
                      </TableRow>
                    );

                    return [row1, row2];
                  }),

                  /* Empty state */
                  ...(isOpen && catLiabilities.length === 0 ? [
                    <TableRow key={`empty-${code}`}>
                      <TableCell colSpan={7} sx={{ textAlign: 'center', py: 2.5, color: 'text.disabled', fontSize: '0.82rem', borderBottom: isLast ? 'none' : '1px solid', borderBottomColor: 'divider' }}>
                        No liabilities logged under {meta.label} yet.
                      </TableCell>
                    </TableRow>
                  ] : []),
                ];
              })}
            </TableBody>
          </Table>
        </TableContainer>
      </Card>

      {/* ── Dialog Modals ────────────────────────────────────────────────────── */}
      <AddLiabilityWizard 
        open={wizardOpen} 
        onClose={() => setWizardOpen(false)} 
        onSuccess={fetchData} 
      />

      <LiabilityTransactionsModal 
        open={txModalOpen} 
        liability={selectedLiability} 
        onClose={() => setTxModalOpen(false)} 
        onSuccess={fetchData} 
      />

      {/* Edit Dialog */}
      <Dialog 
        open={editOpen} 
        onClose={() => setEditOpen(false)}
        PaperProps={{ sx: { borderRadius: 2, p: 1 } }}
      >
        <DialogTitle sx={{ fontWeight: 700, fontFamily: '"Space Grotesk", sans-serif' }}>
          Edit Liability Details
        </DialogTitle>
        <DialogContent sx={{ minWidth: { sm: 400 } }}>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2.5, pt: 1.5 }}>
            <TextField
              fullWidth
              label="Liability Name"
              value={editName}
              onChange={(e) => setEditName(e.target.value)}
            />
            
            {(() => {
              const editingLiability = liabilities.find(l => l.id === editLiabilityId);
              const editingSubcategory = categories
                .flatMap(c => c.subcategories)
                .find(s => s.id === editingLiability?.subcategoryId);

              return (
                <>
                  {editingSubcategory?.hasInterest && (
                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                      <Box sx={{ display: 'flex', gap: 2 }}>
                        <TextField
                          fullWidth
                          label="Interest Rate (%)"
                          type="number"
                          value={editInterestRate}
                          onChange={(e) => setEditInterestRate(e.target.value)}
                          inputProps={{ step: 'any', min: '0' }}
                          InputProps={{
                            endAdornment: <InputAdornment position="end">%</InputAdornment>,
                          }}
                        />
                        <FormControl fullWidth>
                          <InputLabel id="edit-interest-compounding-label">Compounding Frequency</InputLabel>
                          <Select
                            labelId="edit-interest-compounding-label"
                            value={editInterestCompounding}
                            label="Compounding Frequency"
                            onChange={(e) => setEditInterestCompounding(e.target.value)}
                          >
                            <MenuItem value="MONTHLY">Monthly</MenuItem>
                            <MenuItem value="QUARTERLY">Quarterly</MenuItem>
                            <MenuItem value="HALF_YEARLY">Half-Yearly</MenuItem>
                            <MenuItem value="YEARLY">Yearly</MenuItem>
                          </Select>
                        </FormControl>
                      </Box>
                      <TextField
                        fullWidth
                        label="Monthly EMI Amount"
                        type="number"
                        value={editEmiAmount}
                        onChange={(e) => setEditEmiAmount(e.target.value)}
                        inputProps={{ step: 'any', min: '0' }}
                        InputProps={{
                          startAdornment: <InputAdornment position="start">₹</InputAdornment>,
                        }}
                        placeholder="Scheduled monthly payment"
                      />
                      <TextField
                        fullWidth
                        label="EMI Start Date"
                        type="date"
                        value={editEmiStartDate}
                        onChange={(e) => setEditEmiStartDate(e.target.value)}
                        InputLabelProps={{ shrink: true }}
                        helperText="The date when EMI payments officially began/begins"
                      />
                    </Box>
                  )}

                  {editingSubcategory?.hasMaturity && (
                    <TextField
                      fullWidth
                      label="Maturity / Closure Date"
                      type="date"
                      value={editMaturityDate}
                      onChange={(e) => setEditMaturityDate(e.target.value)}
                      InputLabelProps={{ shrink: true }}
                    />
                  )}
                </>
              );
            })()}

            <TextField
              fullWidth
              multiline
              rows={3}
              label="Notes"
              value={editNotes}
              onChange={(e) => setEditNotes(e.target.value)}
            />
          </Box>
        </DialogContent>
        <DialogActions sx={{ p: 2 }}>
          <Button onClick={() => setEditOpen(false)} variant="text" color="inherit">
            Cancel
          </Button>
          <Button onClick={handleUpdateLiability} variant="contained" color="primary">
            Save Changes
          </Button>
        </DialogActions>
      </Dialog>

      {/* Custom Confirm Dialog */}
      <Dialog open={confirmDialog.open} onClose={closeConfirm} maxWidth="xs" fullWidth>
        <DialogTitle sx={{ fontWeight: 700, fontFamily: '"Space Grotesk", sans-serif' }}>{confirmDialog.title}</DialogTitle>
        <DialogContent>
          <Typography variant="body2">{confirmDialog.message}</Typography>
        </DialogContent>
        <DialogActions sx={{ p: 2 }}>
          <Button onClick={closeConfirm} variant="text" color="inherit">Cancel</Button>
          <Button
            variant="contained"
            color="error"
            onClick={() => { confirmDialog.onConfirm(); closeConfirm(); }}
          >
            Confirm
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
