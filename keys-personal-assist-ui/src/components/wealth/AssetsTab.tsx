import { useState, useEffect } from 'react';
import type { SyntheticEvent } from 'react';
import {
  Box,
  Typography,
  Button,
  Grid,
  Card,
  Accordion,
  AccordionSummary,
  AccordionDetails,
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
} from '@mui/icons-material';
import { emsClient } from '@/api/clients/ems-client';
import type { Asset, AssetSummary, AssetUpdateRequest } from '@/types/asset';
import { formatCurrency } from '@/utils/formatters';
import { toast } from 'sonner';
import AddAssetWizard from './AddAssetWizard';
import AssetTransactionsModal from './AssetTransactionsModal';

// Category configurations
const CATEGORY_META = {
  EQUITY: { label: 'Equity', color: '#108cc6', icon: EquityIcon, bg: 'rgba(16, 140, 198, 0.1)' },
  DEBT: { label: 'Debt', color: '#1e5067', icon: DebtIcon, bg: 'rgba(30, 80, 103, 0.1)' },
  REAL_ESTATE: { label: 'Real Estate', color: '#f59e0b', icon: RealEstateIcon, bg: 'rgba(245, 158, 11, 0.1)' },
  COMMODITIES: { label: 'Commodities', color: '#fbbf24', icon: CommoditiesIcon, bg: 'rgba(251, 191, 36, 0.1)' },
  CASH_BANK: { label: 'Cash & Bank', color: '#10b981', icon: CashBankIcon, bg: 'rgba(16, 185, 129, 0.1)' },
};

interface AssetsTabProps {
  onAssetsLoad?: (count: number) => void;
}

// Compact currency formatter for INR
export const formatCompactRupees = (value: number): string => {
  if (value === 0) return '₹0.00';
  const isNegative = value < 0;
  const absVal = Math.abs(value);
  let result = '';

  if (absVal >= 10000000) {
    result = `₹${(absVal / 10000000).toFixed(2)} Cr`;
  } else if (absVal >= 100000) {
    result = `₹${(absVal / 100000).toFixed(2)}L`;
  } else {
    result = formatCurrency(absVal);
    return isNegative ? `-${result}` : result;
  }
  
  return isNegative ? `-${result}` : result;
};

export default function AssetsTab({ onAssetsLoad }: AssetsTabProps) {
  const [assets, setAssets] = useState<Asset[]>([]);
  const [summary, setSummary] = useState<AssetSummary | null>(null);
  const [loading, setLoading] = useState(true);

  // Modals state
  const [wizardOpen, setWizardOpen] = useState(false);
  const [txModalOpen, setTxModalOpen] = useState(false);
  const [selectedAsset, setSelectedAsset] = useState<Asset | null>(null);

  // Edit Modal State
  const [editOpen, setEditOpen] = useState(false);
  const [editAssetId, setEditAssetId] = useState('');
  const [editName, setEditName] = useState('');
  const [editSubCategory, setEditSubCategory] = useState('');
  const [editNotes, setEditNotes] = useState('');
  const [editCategoryId, setEditCategoryId] = useState('');

  // Filtering state
  const [search, setSearch] = useState('');
  const [selectedCategories, setSelectedCategories] = useState<string[]>([
    'EQUITY', 'DEBT', 'REAL_ESTATE', 'COMMODITIES', 'CASH_BANK'
  ]);

  // Accordion expanded states
  const [expanded, setExpanded] = useState<Record<string, boolean>>({
    EQUITY: true,
    DEBT: true,
    REAL_ESTATE: true,
    COMMODITIES: true,
    CASH_BANK: true,
  });

  const fetchData = async () => {
    setLoading(true);
    try {
      const [assetsData, summaryData] = await Promise.all([
        emsClient.listAssets(),
        emsClient.getAssetSummary(),
      ]);
      setAssets(assetsData);
      setSummary(summaryData);
      
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

  const handleAccordionChange = (panel: string) => (_event: SyntheticEvent, isExpanded: boolean) => {
    setExpanded((prev) => ({ ...prev, [panel]: isExpanded }));
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
    setEditSubCategory(asset.subCategory || '');
    setEditNotes(asset.notes || '');
    setEditCategoryId(asset.categoryId);
    setEditOpen(true);
  };

  const handleUpdateAsset = async () => {
    if (!editName.trim()) {
      toast.error('Asset name is required');
      return;
    }
    const updateData: AssetUpdateRequest = {
      categoryId: editCategoryId,
      name: editName.trim(),
      subCategory: editSubCategory.trim() || null,
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
  const handleDeleteAsset = async (asset: Asset) => {
    if (!window.confirm(`Are you sure you want to delete "${asset.name}"? This will delete all its transaction records.`)) {
      return;
    }
    try {
      await emsClient.deleteAsset(asset.id);
      toast.success('Asset deleted');
      fetchData();
    } catch (err) {
      console.error(err);
      toast.error('Failed to delete asset');
    }
  };

  // Open transaction ledger
  const handleOpenLedger = (asset: Asset) => {
    setSelectedAsset(asset);
    setTxModalOpen(true);
  };

  // Filter assets
  const filteredAssets = assets.filter((asset) => {
    const matchesSearch = asset.name.toLowerCase().includes(search.toLowerCase()) || 
                          (asset.subCategory && asset.subCategory.toLowerCase().includes(search.toLowerCase()));
    
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
        <Typography variant="body2" sx={{ fontWeight: 700 }}>
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
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3.5 }}>
      
      {/* ── Toolbar Search, Filter Chips & Add Button ────────────────────────── */}
      <Box 
        sx={{ 
          display: 'flex', 
          flexWrap: 'wrap', 
          gap: 2, 
          justifyContent: 'space-between', 
          alignItems: 'center',
          pb: 0.5
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, flexGrow: 1, flexWrap: 'wrap' }}>
          <TextField
            size="small"
            placeholder="Search assets..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            sx={{ width: 220, bgcolor: 'background.paper' }}
            InputProps={{
              startAdornment: <SearchIcon color="action" sx={{ mr: 1, fontSize: 18 }} />,
            }}
          />
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            {Object.entries(CATEGORY_META).map(([code, meta]) => {
              const isActive = selectedCategories.includes(code);
              return (
                <Chip
                  key={code}
                  label={meta.label}
                  variant={isActive ? 'filled' : 'outlined'}
                  onClick={() => handleToggleCategoryFilter(code)}
                  color={isActive ? 'primary' : 'default'}
                  size="small"
                  sx={{ 
                    fontWeight: 600,
                    fontSize: '0.75rem',
                    height: 28,
                    ...(isActive ? {} : { borderColor: 'divider', color: 'text.secondary' })
                  }}
                />
              );
            })}
          </Box>
        </Box>

        <Button
          variant="contained"
          color="primary"
          startIcon={<AddIcon />}
          onClick={() => setWizardOpen(true)}
          sx={{ py: 0.75, px: 2, fontWeight: 600, textTransform: 'none', borderRadius: 1 }}
        >
          Add Asset
        </Button>
      </Box>

      {/* ── Consolidated Metrics Bar ────────────────────────────────────────── */}
      {summary && (
        <Box 
          sx={{ 
            display: 'flex', 
            justifyContent: 'space-between', 
            alignItems: 'center', 
            p: 2, 
            bgcolor: (theme) => theme.palette.mode === 'dark' ? 'rgba(30, 41, 59, 0.15)' : '#f9fafb',
            border: '1px solid',
            borderColor: 'divider',
            borderRadius: 1,
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 4, width: '100%' }}>
            <Box sx={{ minWidth: 120 }}>
              <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 600, textTransform: 'uppercase', display: 'block', mb: 0.5, fontSize: '0.7rem', letterSpacing: 0.5 }}>
                Invested
              </Typography>
              <Typography variant="h6" sx={{ fontWeight: 700, fontFamily: '"Space Grotesk", sans-serif', color: 'text.primary', fontSize: '1.1rem' }}>
                {formatCurrency(summary.totalInvested)}
              </Typography>
            </Box>
            <Divider orientation="vertical" flexItem sx={{ borderColor: 'divider' }} />
            <Box sx={{ minWidth: 120 }}>
              <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 600, textTransform: 'uppercase', display: 'block', mb: 0.5, fontSize: '0.7rem', letterSpacing: 0.5 }}>
                Current Value
              </Typography>
              <Typography variant="h6" sx={{ fontWeight: 700, color: 'primary.main', fontFamily: '"Space Grotesk", sans-serif', fontSize: '1.1rem' }}>
                {formatCurrency(summary.totalCurrent)}
              </Typography>
            </Box>
            <Divider orientation="vertical" flexItem sx={{ borderColor: 'divider' }} />
            <Box>
              <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 600, textTransform: 'uppercase', display: 'block', mb: 0.5, fontSize: '0.7rem', letterSpacing: 0.5 }}>
                Total Returns
              </Typography>
              {renderReturnsText(summary.totalReturns, summary.percentageReturns)}
            </Box>
          </Box>
        </Box>
      )}

      {/* ── Asset Accordion Group Container ───────────────────────────────────── */}
      <Card variant="outlined" sx={{ borderRadius: 2, overflow: 'hidden', border: '1px solid', borderColor: 'divider', boxShadow: 'none' }}>
        {Object.entries(CATEGORY_META).map(([code, meta], _index, array) => {
          const catSummary = summary?.categoryBreakdowns.find((cb) => cb.categoryCode === code);
          const catAssets = assetsByCategory[code];

          // Skip if category is filtered out
          if (!selectedCategories.includes(code)) return null;

          const hasAssets = catAssets.length > 0;
          const invested = catSummary?.totalInvested ?? 0;
          const current = catSummary?.totalCurrent ?? 0;
          const returns = catSummary?.totalReturns ?? 0;
          const pctReturns = catSummary?.percentageReturns ?? 0;
          const IconComponent = meta.icon;

          // Find if this is the last visible item to omit the bottom border
          const visibleCategories = array.filter(([c]) => selectedCategories.includes(c));
          const isLastVisible = visibleCategories[visibleCategories.length - 1][0] === code;

          return (
            <Accordion
              key={code}
              expanded={expanded[code] !== false}
              onChange={handleAccordionChange(code)}
              sx={{
                borderRadius: '0px !important',
                border: 'none',
                borderBottom: isLastVisible ? 'none' : '1px solid',
                borderBottomColor: 'divider',
                backgroundImage: 'none',
                bgcolor: 'background.paper',
                boxShadow: 'none',
                '&::before': { display: 'none' },
                '&.Mui-expanded': { margin: '0' },
              }}
            >
              <AccordionSummary
                expandIcon={<ExpandMoreIcon sx={{ color: 'text.secondary' }} />}
                sx={{
                  px: 3,
                  py: 1.5,
                  borderBottom: expanded[code] !== false && hasAssets ? '1px solid' : 'none',
                  borderColor: 'divider',
                }}
              >
                <Grid container alignItems="center" spacing={2}>
                  {/* Category Title & Badge */}
                  <Grid size={{ xs: 12, md: 4 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                      <Box 
                        sx={{ 
                          width: 32, 
                          height: 32, 
                          borderRadius: '50%', 
                          bgcolor: meta.bg, 
                          color: meta.color,
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center'
                        }}
                      >
                        <IconComponent sx={{ fontSize: 16 }} />
                      </Box>
                      <Box>
                        <Typography variant="subtitle2" sx={{ fontWeight: 700, fontFamily: '"Space Grotesk", sans-serif' }}>
                          {meta.label}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {catAssets.length} assets
                        </Typography>
                      </Box>
                    </Box>
                  </Grid>

                  {/* Invested */}
                  <Grid size={{ xs: 4, md: 2.5 }} sx={{ display: 'flex', flexDirection: 'column' }}>
                    <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 500, fontSize: '0.72rem' }}>Invested</Typography>
                    <Typography variant="body2" sx={{ fontWeight: 600, color: 'text.primary', fontFamily: '"Space Grotesk", sans-serif' }}>
                      {formatCurrency(invested)}
                    </Typography>
                  </Grid>

                  {/* Current Value */}
                  <Grid size={{ xs: 4, md: 2.5 }} sx={{ display: 'flex', flexDirection: 'column' }}>
                    <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 500, fontSize: '0.72rem' }}>Current Value</Typography>
                    <Typography variant="body2" sx={{ fontWeight: 700, color: 'primary.main', fontFamily: '"Space Grotesk", sans-serif' }}>
                      {formatCurrency(current)}
                    </Typography>
                  </Grid>

                  {/* Returns */}
                  <Grid size={{ xs: 4, md: 3 }} sx={{ display: 'flex', flexDirection: 'column', alignItems: { xs: 'flex-start', md: 'flex-end' }, pr: 2 }}>
                    <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 500, fontSize: '0.72rem', width: '100%', textAlign: { xs: 'left', md: 'right' } }}>Returns</Typography>
                    <Box sx={{ width: '100%', display: 'flex', justifyContent: { xs: 'flex-start', md: 'flex-end' } }}>
                      {renderReturnsText(returns, pctReturns)}
                    </Box>
                  </Grid>
                </Grid>
              </AccordionSummary>

              <AccordionDetails sx={{ p: 0 }}>
                {!hasAssets ? (
                  <Box sx={{ p: 4, textAlign: 'center' }}>
                    <Typography color="text.secondary" variant="body2">
                      No assets added in {meta.label} yet.
                    </Typography>
                  </Box>
                ) : (
                  <TableContainer component={Paper} elevation={0} sx={{ borderRadius: 0, bgcolor: 'transparent' }}>
                    <Table size="small">
                      <TableHead sx={{ bgcolor: (theme) => theme.palette.mode === 'dark' ? 'rgba(30, 41, 59, 0.4)' : '#f9fafb' }}>
                        <TableRow>
                          <TableCell sx={{ pl: 3, fontWeight: 700, py: 1 }}>Name</TableCell>
                          <TableCell sx={{ fontWeight: 700, py: 1 }}>Type</TableCell>
                          <TableCell align="right" sx={{ fontWeight: 700, py: 1 }}>Invested</TableCell>
                          <TableCell align="right" sx={{ fontWeight: 700, py: 1 }}>Current Value</TableCell>
                          <TableCell sx={{ fontWeight: 700, py: 1 }}>Returns (ROI)</TableCell>
                          <TableCell align="center" sx={{ pr: 3, fontWeight: 700, py: 1 }}>Actions</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {catAssets.map((asset) => (
                          <TableRow key={asset.id} hover sx={{ '& td': { py: 1 } }}>
                            <TableCell sx={{ pl: 3 }}>
                              <Typography variant="body2" sx={{ fontWeight: 600 }}>{asset.name}</Typography>
                              {asset.notes && (
                                <Typography variant="caption" color="text.secondary" display="block" sx={{ maxWidth: 220, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                                  {asset.notes}
                                </Typography>
                              )}
                            </TableCell>
                            <TableCell>
                              <Chip label={asset.subCategory || 'General'} size="small" sx={{ fontSize: '0.7rem', fontWeight: 500, height: 20 }} />
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
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                )}
              </AccordionDetails>
            </Accordion>
          );
        })}
      </Card>

      {/* ── Dialog Modals ────────────────────────────────────────────────────── */}
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
        <DialogContent sx={{ display: 'flex', flexDirection: 'column', gap: 2.5, minWidth: { sm: 400 }, pt: 2 }}>
          <TextField
            fullWidth
            required
            label="Asset Name"
            value={editName}
            onChange={(e) => setEditName(e.target.value)}
          />
          <TextField
            fullWidth
            label="Subcategory / Type"
            value={editSubCategory}
            onChange={(e) => setEditSubCategory(e.target.value)}
          />
          <TextField
            fullWidth
            multiline
            rows={3}
            label="Notes"
            value={editNotes}
            onChange={(e) => setEditNotes(e.target.value)}
          />
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
    </Box>
  );
}
