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
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  InputAdornment,
  useTheme,
  alpha,
  Grid,
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  History as HistoryIcon,
  Search as SearchIcon,
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  ShowChart as EquityIcon,
  AccountBalance as DebtIcon,
  HomeWork as RealEstateIcon,
  MonetizationOn as CommoditiesIcon,
  Savings as CashBankIcon,
  InfoOutlined as InfoIcon,
} from '@mui/icons-material';
import { emsClient } from '@/api/clients/ems-client';
import type { Asset, AssetSummary, AssetUpdateRequest, AssetCategory } from '@/types/asset';
import { formatCurrency, formatCompactRupees } from '@/utils/formatters';
import { toast } from 'sonner';
import AddAssetWizard from './AddAssetWizard';
import AssetTransactionsModal from './AssetTransactionsModal';



interface AssetsTabProps {
  onAssetsLoad?: (count: number) => void;
}

export default function AssetsTab({ onAssetsLoad }: AssetsTabProps) {
  const theme = useTheme();
  const mode = theme.palette.mode;
  const isDark = mode === 'dark';

  // Category configurations driven dynamically by the theme palette
  const CATEGORY_META = {
    EQUITY: {
      label: 'Equity',
      color: isDark ? theme.palette.primary.main : theme.palette.secondary.main,
      icon: EquityIcon,
      bg: alpha(isDark ? theme.palette.primary.main : theme.palette.secondary.main, 0.1),
    },
    DEBT: {
      label: 'Debt',
      color: isDark ? theme.palette.secondary.main : theme.palette.primary.main,
      icon: DebtIcon,
      bg: alpha(isDark ? theme.palette.secondary.main : theme.palette.primary.main, 0.15),
    },
    REAL_ESTATE: {
      label: 'Real Estate',
      color: isDark ? theme.palette.warning.dark : theme.palette.warning.main,
      icon: RealEstateIcon,
      bg: alpha(isDark ? theme.palette.warning.dark : theme.palette.warning.main, 0.1),
    },
    COMMODITIES: {
      label: 'Commodities',
      color: isDark ? theme.palette.warning.main : theme.palette.warning.light,
      icon: CommoditiesIcon,
      bg: alpha(isDark ? theme.palette.warning.main : theme.palette.warning.light, 0.1),
    },
    CASH_BANK: {
      label: 'Cash & Bank',
      color: theme.palette.success.main,
      icon: CashBankIcon,
      bg: alpha(theme.palette.success.main, 0.1),
    },
  };

  const [assets, setAssets] = useState<Asset[]>([]);
  const [summary, setSummary] = useState<AssetSummary | null>(null);
  const [loading, setLoading] = useState(true);

  // Modals state
  const [wizardOpen, setWizardOpen] = useState(false);
  const [txModalOpen, setTxModalOpen] = useState(false);
  const [selectedAsset, setSelectedAsset] = useState<Asset | null>(null);

  // Edit Modal State
  const [categories, setCategories] = useState<AssetCategory[]>([]);
  const [editOpen, setEditOpen] = useState(false);
  const [editAssetId, setEditAssetId] = useState('');
  const [editName, setEditName] = useState('');
  const [editNotes, setEditNotes] = useState('');
  const [editCategoryId, setEditCategoryId] = useState('');
  const [editSubcategoryId, setEditSubcategoryId] = useState<string | null>(null);
  const [editInterestRate, setEditInterestRate] = useState<string>('');
  const [editInterestCompounding, setEditInterestCompounding] = useState<string>('YEARLY');
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
    'EQUITY', 'DEBT', 'REAL_ESTATE', 'COMMODITIES', 'CASH_BANK'
  ]);

  // Accordion expanded states
  const [expanded, setExpanded] = useState<Record<string, boolean>>({
    EQUITY: false,
    DEBT: false,
    REAL_ESTATE: false,
    COMMODITIES: false,
    CASH_BANK: false,
  });

  const fetchData = async () => {
    setLoading(true);
    try {
      const [assetsData, summaryData, categoriesData] = await Promise.all([
        emsClient.listAssets(),
        emsClient.getAssetSummary(),
        emsClient.getAllAssetCategories(),
      ]);
      setAssets(assetsData);
      setSummary(summaryData);
      setCategories(categoriesData);
      
      // Update parent component with the count of assets
      if (onAssetsLoad) {
        onAssetsLoad(assetsData.length);
      }
    } catch (err) {
      console.error(err);
      toast.error('Failed to load assets data');
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



  // Edit action
  const handleOpenEdit = (asset: Asset) => {
    setEditAssetId(asset.id);
    setEditName(asset.name);
    setEditNotes(asset.notes || '');
    setEditCategoryId(asset.categoryId);
    setEditSubcategoryId(asset.subcategoryId);
    setEditInterestRate(asset.interestRate != null ? String(asset.interestRate) : '');
    setEditInterestCompounding(asset.interestCompounding || 'YEARLY');
    setEditMaturityDate(asset.maturityDate ? asset.maturityDate.split('T')[0] : '');
    setEditOpen(true);
  };

  const handleUpdateAsset = async () => {
    if (!editName.trim()) {
      toast.error('Asset name is required');
      return;
    }

    const editingAsset = assets.find(a => a.id === editAssetId);
    const editingSubcategory = categories
      .flatMap(c => c.subcategories)
      .find(s => s.id === editingAsset?.subcategoryId);

    if (editingSubcategory?.hasInterest && editInterestRate) {
      const r = parseFloat(editInterestRate);
      if (isNaN(r) || r < 0) {
        toast.error('Interest rate must be a non-negative number');
        return;
      }
    }

    const updateData: AssetUpdateRequest = {
      categoryId: editCategoryId || null,
      name: editName.trim() || null,
      subcategoryId: editSubcategoryId,
      interestDetails:
        editingSubcategory?.hasInterest && editInterestRate
          ? {
              interestRate: parseFloat(editInterestRate),
              compounding: editInterestCompounding as import('@/types/asset').CompoundingFrequency,
              maturityDate:
                editingSubcategory?.hasMaturity && editMaturityDate
                  ? new Date(editMaturityDate).toISOString()
                  : null,
            }
          : null,
      notes: editNotes.trim() || null,
    };

    try {
      await emsClient.updateAsset(editAssetId, updateData);
      toast.success('Asset metadata updated');
      setEditOpen(false);
      fetchData();
    } catch (err: any) {
      console.error(err);
      toast.error(err.message || 'Failed to update asset');
    }
  };

  // Delete action
  const handleDeleteAsset = (asset: Asset) => {
    openConfirm(
      'Delete Asset',
      `Are you sure you want to delete "${asset.name}"? This will delete all its transaction records. This action cannot be undone.`,
      async () => {
        try {
          await emsClient.deleteAsset(asset.id);
          toast.success('Asset deleted');
          fetchData();
        } catch (err) {
          console.error(err);
          toast.error('Failed to delete asset');
        }
      }
    );
  };

  // Open transaction ledger
  const handleOpenLedger = (asset: Asset) => {
    setSelectedAsset(asset);
    setTxModalOpen(true);
  };

  // Filter assets
  const filteredAssets = assets.filter((asset) => {
    const matchesSearch = asset.name.toLowerCase().includes(search.toLowerCase());
    const matchesCategory = selectedCategories.includes(asset.categoryCode);
    return matchesSearch && matchesCategory;
  });

  // Group assets by category code
  const assetsByCategory: Record<string, Asset[]> = {
    EQUITY: [],
    DEBT: [],
    REAL_ESTATE: [],
    COMMODITIES: [],
    CASH_BANK: [],
  };

  filteredAssets.forEach((asset) => {
    if (assetsByCategory[asset.categoryCode]) {
      assetsByCategory[asset.categoryCode].push(asset);
    }
  });

  // Helper for returns color styling
  const renderReturnsText = (absVal: number, pctVal: number) => {
    const isPositive = absVal >= 0;
    return (
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, color: isPositive ? 'success.main' : 'error.main' }}>
        {isPositive ? <TrendingUpIcon fontSize="small" /> : <TrendingDownIcon fontSize="small" />}
        <Typography variant="body2" sx={{ fontWeight: 700, whiteSpace: 'nowrap' }}>
          {isPositive ? '+' : ''}{formatCurrency(absVal)} ({isPositive ? '+' : ''}{pctVal.toFixed(2)}%)
        </Typography>
      </Box>
    );
  };

  if (loading && !summary) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', py: 12 }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>

      {/* Toolbar Card: Search + Category Filters + Add Asset */}
      <Card sx={{ px: 2, py: 1.25, mb: 2.5 }}>
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1.5, justifyContent: 'space-between', alignItems: 'center' }}>
          {/* Left: search + category toggles */}
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, flexGrow: 1, flexWrap: 'wrap' }}>
            <TextField
              size="small"
              placeholder="Search assets..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              sx={{
                width: 200,
                '& .MuiOutlinedInput-root': { borderRadius: 1.5, fontSize: '0.85rem' },
              }}
              InputProps={{ startAdornment: <SearchIcon color="action" sx={{ mr: 0.75, fontSize: 17 }} /> }}
            />
            {/* Category filter toggles — color-coded */}
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
          {/* Right: Add Asset button */}
          <Button
            variant="contained"
            color="primary"
            startIcon={<AddIcon />}
            onClick={() => setWizardOpen(true)}
          >
            Add Asset
          </Button>
        </Box>
      </Card>

      {/* Summary Cards: Prominent Portfolio Metrics */}
      {summary && (
        <Grid container spacing={2} sx={{ mb: 2.5 }}>
          {[
            {
              label: 'Invested',
              value: formatCompactRupees(summary.totalInvested),
              color: theme.palette.text.secondary,
              icon: DebtIcon,
              desc: 'The total amount of principal capital you have contributed to buy or fund your assets.',
            },
            {
              label: 'Current Value',
              value: formatCompactRupees(summary.totalCurrent),
              color: theme.palette.primary.main,
              icon: EquityIcon,
              desc: 'The current market value or appraised value of all your assets.',
            },
            {
              label: 'Total Returns',
              value: renderReturnsText(summary.totalReturns, summary.percentageReturns),
              color: summary.totalReturns >= 0 ? theme.palette.success.main : theme.palette.error.main,
              icon: TrendingUpIcon,
              desc: 'The net absolute return and Percentage Return on Investment (ROI) calculated across your asset portfolio.',
            },
          ].map((metric) => {
            const Icon = metric.icon;
            return (
              <Grid key={metric.label} size={{ xs: 12, md: 4 }}>
                <Card
                  sx={{
                    p: 2.5,
                    height: '100%',
                    background: alpha(metric.color, theme.palette.mode === 'dark' ? 0.08 : 0.04),
                    border: `1px solid ${alpha(metric.color, 0.12)}`,
                    transition: 'transform 200ms ease, box-shadow 200ms ease',
                    '&:hover': {
                      transform: 'translateY(-2px)',
                      boxShadow: `0 6px 20px ${alpha(metric.color, 0.12)}`,
                    },
                  }}
                >
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                      <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 600, textTransform: 'uppercase', letterSpacing: 0.8, fontSize: '0.68rem' }}>
                        {metric.label}
                      </Typography>
                      <Tooltip title={metric.desc} arrow>
                        <InfoIcon sx={{ fontSize: '0.8rem', color: 'text.secondary', cursor: 'pointer' }} />
                      </Tooltip>
                    </Box>
                    <Icon sx={{ color: metric.color, fontSize: 20, opacity: 0.7 }} />
                  </Box>
                  {typeof metric.value === 'string' ? (
                    <Typography variant="h5" sx={{ fontWeight: 700, fontFamily: '"Space Grotesk", sans-serif', color: metric.color === theme.palette.text.secondary ? 'text.primary' : metric.color, fontSize: '1.3rem' }}>
                      {metric.value}
                    </Typography>
                  ) : (
                    <Box sx={{ mt: 0.25 }}>{metric.value}</Box>
                  )}
                </Card>
              </Grid>
            );
          })}
        </Grid>
      )}
      {/* Table Card */}
      <Card sx={{ overflow: 'hidden' }}>
        <TableContainer component={Paper} elevation={0} sx={{ borderRadius: 0, bgcolor: 'transparent' }}>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell sx={{ pl: 3, fontWeight: 700, py: 1.25, fontSize: '0.78rem', textTransform: 'uppercase', letterSpacing: 0.5, color: 'text.secondary' }}>Name</TableCell>
                <TableCell sx={{ fontWeight: 700, py: 1.25, fontSize: '0.78rem', textTransform: 'uppercase', letterSpacing: 0.5, color: 'text.secondary' }}>Type</TableCell>
                <TableCell align="right" sx={{ fontWeight: 700, py: 1.25, fontSize: '0.78rem', textTransform: 'uppercase', letterSpacing: 0.5, color: 'text.secondary' }}>Invested</TableCell>
                <TableCell align="right" sx={{ fontWeight: 700, py: 1.25, fontSize: '0.78rem', textTransform: 'uppercase', letterSpacing: 0.5, color: 'text.secondary' }}>Current Value</TableCell>
                <TableCell sx={{ fontWeight: 700, py: 1.25, fontSize: '0.78rem', textTransform: 'uppercase', letterSpacing: 0.5, color: 'text.secondary' }}>Returns (ROI)</TableCell>
                <TableCell align="center" sx={{ pr: 3, fontWeight: 700, py: 1.25, fontSize: '0.78rem', textTransform: 'uppercase', letterSpacing: 0.5, color: 'text.secondary' }}>Actions</TableCell>
              </TableRow>
            </TableHead>

            <TableBody>
              {Object.entries(CATEGORY_META).map(([code, meta], idx, arr) => {
                const catSummary = summary?.categoryBreakdowns.find((cb) => cb.categoryCode === code);
                const catAssets = assetsByCategory[code];
                if (!selectedCategories.includes(code)) return null;

                const isOpen = expanded[code] !== false;

                const current = catSummary?.totalCurrent ?? 0;
                const returns = catSummary?.totalReturns ?? 0;
                const pctReturns = catSummary?.percentageReturns ?? 0;
                const IconComponent = meta.icon;
                const visibleArr = arr.filter(([c]) => selectedCategories.includes(c));
                const isLast = visibleArr[visibleArr.length - 1][0] === code;

                return [
                  /* Category group-divider row — finboom style */
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
                    {/* LEFT: chevron + icon + name + count */}
                    <TableCell
                      colSpan={4}
                      sx={{
                        py: 1.5,
                        pl: 2,
                        borderBottom: isOpen && catAssets.length > 0 ? '1px solid' : 'none',
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
                          label={catAssets.length}
                          size="small"
                          sx={{
                            height: 18, fontSize: '0.68rem', fontWeight: 700,
                            bgcolor: meta.bg, color: meta.color,
                            '& .MuiChip-label': { px: 0.75 },
                          }}
                        />
                      </Box>
                    </TableCell>

                    {/* RIGHT: current value + returns — right-aligned, spans remaining cols */}
                    <TableCell
                      colSpan={2}
                      align="right"
                      sx={{
                        pr: 3, py: 1.5,
                        borderBottom: 'none',
                        whiteSpace: 'nowrap',
                      }}
                    >
                      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: 2 }}>
                        <Typography variant="body2" sx={{ fontWeight: 700, color: 'primary.main', fontFamily: '"Space Grotesk", sans-serif', fontSize: '0.95rem' }}>
                          {formatCompactRupees(current)}
                        </Typography>
                        {renderReturnsText(returns, pctReturns)}
                      </Box>
                    </TableCell>
                  </TableRow>,

                  /* Asset rows (collapsed/expanded) with zebra striping */
                  ...catAssets.map((asset, assetIdx) => (
                    <TableRow
                      key={asset.id}
                      sx={{
                        display: isOpen ? undefined : 'none',
                        '& td': { py: 1 },
                        bgcolor: assetIdx % 2 === 0
                          ? 'transparent'
                          : (theme) => theme.palette.mode === 'dark' ? 'rgba(255,255,255,0.018)' : 'rgba(0,0,0,0.018)',
                        '&:hover': { bgcolor: 'action.hover' },
                        '&:last-of-type td': { borderBottom: isLast ? 'none' : undefined },
                      }}
                    >
                      <TableCell sx={{ pl: 4 }}>
                        <Typography variant="body2" sx={{ fontWeight: 600 }}>{asset.name}</Typography>
                        {asset.notes && (
                          <Typography variant="caption" color="text.secondary" display="block" sx={{ maxWidth: 220, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                            {asset.notes}
                          </Typography>
                        )}
                      </TableCell>
                      <TableCell>
                        {(() => {
                          const sub = categories
                            .flatMap(c => c.subcategories)
                            .find(s => s.id === asset.subcategoryId);
                          return (
                            <Chip
                              label={sub?.name || asset.categoryCode}
                              size="small"
                              sx={{ fontSize: '0.7rem', fontWeight: 500, height: 20 }}
                            />
                          );
                        })()}
                      </TableCell>
                      <TableCell align="right" sx={{ fontWeight: 500 }}>{formatCurrency(asset.investedValue)}</TableCell>
                      <TableCell align="right" sx={{ fontWeight: 600, color: 'primary.main' }}>{formatCurrency(asset.currentValue)}</TableCell>
                      <TableCell>{renderReturnsText(asset.absoluteReturns, asset.percentageReturns)}</TableCell>
                      <TableCell align="center" sx={{ pr: 3, whiteSpace: 'nowrap' }}>
                        <Tooltip title="Transactions Ledger">
                          <IconButton onClick={() => handleOpenLedger(asset)} size="small" color="primary">
                            <HistoryIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Edit Metadata">
                          <IconButton onClick={() => handleOpenEdit(asset)} size="small" color="secondary">
                            <EditIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Delete Asset">
                          <IconButton onClick={() => handleDeleteAsset(asset)} size="small" color="error">
                            <DeleteIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                      </TableCell>
                    </TableRow>
                  )),

                  /* Empty state row */
                  ...(isOpen && catAssets.length === 0 ? [
                    <TableRow key={`empty-${code}`}>
                      <TableCell colSpan={6} sx={{ textAlign: 'center', py: 2.5, color: 'text.disabled', fontSize: '0.82rem', borderBottom: isLast ? 'none' : '1px solid', borderBottomColor: 'divider' }}>
                        No assets added in {meta.label} yet.
                      </TableCell>
                    </TableRow>
                  ] : []),
                ];
              })}
            </TableBody>
          </Table>
        </TableContainer>
      </Card>

      {/* Dialog Modals */}
      <AddAssetWizard 
        open={wizardOpen} 
        onClose={() => setWizardOpen(false)} 
        onSuccess={fetchData} 
      />

      <AssetTransactionsModal 
        open={txModalOpen} 
        asset={selectedAsset} 
        onClose={() => setTxModalOpen(false)} 
        onSuccess={fetchData} 
      />

      {/* Edit Asset Metadata Dialog */}
      <Dialog 
        open={editOpen} 
        onClose={() => setEditOpen(false)}
        PaperProps={{ sx: { borderRadius: 2, p: 1 } }}
      >
        <DialogTitle sx={{ fontWeight: 700, fontFamily: '"Space Grotesk", sans-serif' }}>
          Edit Asset Details
        </DialogTitle>
        <DialogContent sx={{ minWidth: { sm: 400 } }}>
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2.5, pt: 1.5 }}>
            <TextField
              fullWidth
              label="Asset Name"
              value={editName}
              onChange={(e) => setEditName(e.target.value)}
            />
            
            {/* Conditional Edit Fields for Interest/Compounding */}
            {(() => {
              const editingAsset = assets.find(a => a.id === editAssetId);
              const editingSubcategory = categories
                .flatMap(c => c.subcategories)
                .find(s => s.id === editingAsset?.subcategoryId);

              return (
                <>
                  {editingSubcategory?.hasInterest && (
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
                          <MenuItem value="YEARLY">Yearly</MenuItem>
                          <MenuItem value="QUARTERLY">Quarterly</MenuItem>
                          <MenuItem value="HALF_YEARLY">Half-Yearly</MenuItem>
                          <MenuItem value="MONTHLY">Monthly</MenuItem>
                        </Select>
                      </FormControl>
                    </Box>
                  )}

                  {editingSubcategory?.hasMaturity && (
                    <TextField
                      fullWidth
                      label="Maturity Date"
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
          <Button onClick={handleUpdateAsset} variant="contained" color="primary">
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
