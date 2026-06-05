import { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box,
  TextField,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Chip,
  Grid,
  MenuItem,
  Divider,
  InputAdornment,
  CircularProgress,
} from '@mui/material';
import {
  Close as CloseIcon,
  Delete as DeleteIcon,
  Add as AddIcon,
} from '@mui/icons-material';
import { emsClient } from '@/api/clients/ems-client';
import type { Asset, AssetTransaction, AssetTransactionRequest } from '@/types/asset';
import { formatCurrency } from '@/utils/formatters';
import { toast } from 'sonner';

interface AssetTransactionsModalProps {
  open: boolean;
  asset: Asset | null;
  onClose: () => void;
  onSuccess: () => void;
}

export default function AssetTransactionsModal({ open, asset, onClose, onSuccess }: AssetTransactionsModalProps) {
  const [transactions, setTransactions] = useState<AssetTransaction[]>([]);
  const [loading, setLoading] = useState(false);

  // Form State
  const [transactionType, setTransactionType] = useState<'BUY' | 'SELL' | 'REVALUE'>('BUY');
  const [amount, setAmount] = useState<string>('');
  const [units, setUnits] = useState<string>('');
  const [pricePerUnit, setPricePerUnit] = useState<string>('');
  const [description, setDescription] = useState<string>('');
  const [transactionDate, setTransactionDate] = useState<string>(
    new Date().toISOString().substring(0, 16) // Format: YYYY-MM-DDThh:mm
  );

  const isUnitBased = asset?.categoryCode === 'EQUITY' || asset?.categoryCode === 'COMMODITIES';

  // Load transactions for the asset
  const fetchTransactions = async () => {
    if (!asset) return;
    setLoading(true);
    try {
      const data = await emsClient.getTransactionsForAsset(asset.id);
      // Sort by date descending
      setTransactions(data.sort((a, b) => new Date(b.transactionDate).getTime() - new Date(a.transactionDate).getTime()));
    } catch (err) {
      console.error(err);
      toast.error('Failed to load transaction ledger');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (open && asset) {
      fetchTransactions();
      resetForm();
    }
  }, [open, asset]);

  const resetForm = () => {
    setTransactionType('BUY');
    setAmount('');
    setUnits('');
    setPricePerUnit('');
    setDescription('');
    setTransactionDate(new Date().toISOString().substring(0, 16));
  };

  // Auto calculation for units/prices in unit-based transactions
  useEffect(() => {
    if (isUnitBased && (transactionType === 'BUY' || transactionType === 'SELL') && units && pricePerUnit) {
      const u = parseFloat(units);
      const p = parseFloat(pricePerUnit);
      if (!isNaN(u) && !isNaN(p)) {
        setAmount((u * p).toFixed(2));
      }
    }
  }, [units, pricePerUnit, transactionType, isUnitBased]);

  const validateTransactionForm = (): boolean => {
    if (!asset) return false;
    
    if (isUnitBased) {
      if (transactionType === 'BUY' || transactionType === 'SELL') {
        const u = parseFloat(units);
        const p = parseFloat(pricePerUnit);
        if (isNaN(u) || u <= 0) {
          toast.error('Units/Quantity must be a positive number');
          return false;
        }
        if (isNaN(p) || p <= 0) {
          toast.error('Price per unit must be a positive number');
          return false;
        }
      } else if (transactionType === 'REVALUE') {
        const p = parseFloat(pricePerUnit);
        if (isNaN(p) || p <= 0) {
          toast.error('New Price per unit must be a positive number');
          return false;
        }
      }
    } else {
      const amt = parseFloat(amount);
      if (isNaN(amt) || amt < 0) {
        toast.error('Amount must be a non-negative number');
        return false;
      }
    }

    if (!transactionDate) {
      toast.error('Transaction date is required');
      return false;
    }

    return true;
  };

  const handleAddTransaction = async () => {
    if (!asset || !validateTransactionForm()) return;

    let finalAmount = parseFloat(amount);
    
    // For unit-based revaluation, amount can be computed as total units * new price.
    // However, on the backend, price_per_unit is the key field for REVALUE, amount represents new valuation.
    // Let's compute amount if not entered:
    if (isUnitBased && transactionType === 'REVALUE') {
      const p = parseFloat(pricePerUnit);
      // Calculate amount based on current units or previous units. The backend does this, but let's supply it.
      // Sum units of BUY - SELL to get total units.
      const totalUnits = transactions.reduce((sum, tx) => {
        if (tx.transactionType === 'BUY') return sum + (tx.units || 0);
        if (tx.transactionType === 'SELL') return sum - (tx.units || 0);
        return sum;
      }, 0);
      finalAmount = totalUnits * p;
    }

    const reqData: AssetTransactionRequest = {
      transactionType,
      amount: finalAmount,
      units: isUnitBased && transactionType !== 'REVALUE' ? parseFloat(units) : null,
      pricePerUnit: isUnitBased ? parseFloat(pricePerUnit) : null,
      transactionDate: new Date(transactionDate).toISOString(),
      description: description.trim() || null,
    };

    try {
      await emsClient.addTransactionToAsset(asset.id, reqData);
      toast.success('Transaction logged successfully');
      resetForm();
      fetchTransactions();
      onSuccess(); // Trigger reload of parent page
    } catch (err: any) {
      console.error(err);
      toast.error(err.message || 'Failed to record transaction');
    }
  };

  const handleDeleteTransaction = async (txId: string) => {
    if (!window.confirm('Are you sure you want to delete this transaction? This will revert the valuation calculations.')) {
      return;
    }
    try {
      await emsClient.deleteAssetTransaction(txId);
      toast.success('Transaction deleted');
      fetchTransactions();
      onSuccess(); // Trigger reload of parent page
    } catch (err) {
      console.error(err);
      toast.error('Failed to delete transaction');
    }
  };

  const getBadgeColor = (type: string) => {
    switch (type) {
      case 'BUY': return 'success';
      case 'SELL': return 'error';
      case 'REVALUE': return 'info';
      default: return 'default';
    }
  };

  const formatTxDate = (dateStr: string) => {
    const d = new Date(dateStr);
    return d.toLocaleDateString('en-IN', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <Dialog 
      open={open} 
      onClose={onClose} 
      maxWidth="lg" 
      fullWidth
      PaperProps={{
        sx: {
          borderRadius: 3,
          backgroundImage: (theme) => 
            theme.palette.mode === 'dark' 
              ? 'linear-gradient(135deg, rgba(30, 41, 59, 0.9) 0%, rgba(17, 24, 39, 0.9) 100%)'
              : 'none',
          backdropFilter: 'blur(10px)',
          border: (theme) => 
            theme.palette.mode === 'dark' 
              ? '1px solid rgba(56, 189, 248, 0.15)'
              : 'none',
        }
      }}
    >
      <DialogTitle sx={{ m: 0, p: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box>
          <Typography variant="h5" sx={{ fontWeight: 700, fontFamily: '"Space Grotesk", sans-serif' }}>
            Transaction Ledger
          </Typography>
          <Typography variant="subtitle2" color="text.secondary">
            Asset: {asset?.name} ({asset?.subCategory || asset?.categoryName})
          </Typography>
        </Box>
        <IconButton onClick={onClose} size="small" sx={{ color: 'text.secondary' }}>
          <CloseIcon />
        </IconButton>
      </DialogTitle>

      <Divider />

      <DialogContent sx={{ p: 3 }}>
        <Grid container spacing={4}>
          {/* Left Column: Form to log a new transaction */}
          <Grid size={{ xs: 12, md: 4 }}>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2.5, p: 2.5, borderRadius: 2, border: '1px solid', borderColor: 'divider', bgcolor: (theme) => theme.palette.mode === 'dark' ? 'rgba(30, 41, 59, 0.2)' : '#fcfdfe' }}>
              <Typography variant="h6" sx={{ fontWeight: 700, fontFamily: '"Space Grotesk", sans-serif', mb: 1 }}>
                Log Transaction
              </Typography>

              <TextField
                select
                fullWidth
                label="Transaction Type"
                value={transactionType}
                onChange={(e) => {
                  setTransactionType(e.target.value as any);
                  setAmount('');
                  setUnits('');
                  setPricePerUnit('');
                }}
              >
                <MenuItem value="BUY">BUY (Add Value/Units)</MenuItem>
                <MenuItem value="SELL">SELL (Reduce Value/Units)</MenuItem>
                <MenuItem value="REVALUE">REVALUE (Update Price/Balance)</MenuItem>
              </TextField>

              <TextField
                fullWidth
                required
                type="datetime-local"
                label="Transaction Date & Time"
                value={transactionDate}
                onChange={(e) => setTransactionDate(e.target.value)}
                InputLabelProps={{ shrink: true }}
              />

              {isUnitBased ? (
                <>
                  {transactionType !== 'REVALUE' && (
                    <TextField
                      fullWidth
                      required
                      type="number"
                      label="Quantity / Units"
                      placeholder="e.g. 5.5"
                      value={units}
                      onChange={(e) => setUnits(e.target.value)}
                      inputProps={{ step: 'any', min: '0' }}
                    />
                  )}

                  <TextField
                    fullWidth
                    required
                    type="number"
                    label={transactionType === 'REVALUE' ? 'New Price per Unit (INR)' : 'Price per Unit (INR)'}
                    placeholder="e.g. 7850.00"
                    value={pricePerUnit}
                    onChange={(e) => setPricePerUnit(e.target.value)}
                    inputProps={{ step: 'any', min: '0' }}
                    InputProps={{
                      startAdornment: <InputAdornment position="start">₹</InputAdornment>,
                    }}
                  />

                  {transactionType !== 'REVALUE' && (
                    <TextField
                      fullWidth
                      disabled
                      label="Total Amount (INR)"
                      value={amount}
                      InputProps={{
                        startAdornment: <InputAdornment position="start">₹</InputAdornment>,
                      }}
                    />
                  )}
                </>
              ) : (
                <TextField
                  fullWidth
                  required
                  type="number"
                  label={transactionType === 'REVALUE' ? 'New Current Balance (INR)' : 'Cash Amount (INR)'}
                  placeholder="e.g. 10000.00"
                  value={amount}
                  onChange={(e) => setAmount(e.target.value)}
                  inputProps={{ step: 'any', min: '0' }}
                  InputProps={{
                    startAdornment: <InputAdornment position="start">₹</InputAdornment>,
                  }}
                />
              )}

              <TextField
                fullWidth
                multiline
                rows={2}
                label="Description / Audit Notes"
                placeholder="Why was this logged? e.g. quarterly interest, monthly SIP"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
              />

              <Button
                fullWidth
                variant="contained"
                color="primary"
                startIcon={<AddIcon />}
                onClick={handleAddTransaction}
                sx={{ mt: 1 }}
              >
                Add Transaction
              </Button>
            </Box>
          </Grid>

          {/* Right Column: Ledger Table */}
          <Grid size={{ xs: 12, md: 8 }}>
            <Typography variant="h6" sx={{ fontWeight: 700, fontFamily: '"Space Grotesk", sans-serif', mb: 2 }}>
              Transaction History
            </Typography>

            {loading ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
                <CircularProgress />
              </Box>
            ) : transactions.length === 0 ? (
              <Box sx={{ p: 4, textAlign: 'center', border: '1px dashed', borderColor: 'divider', borderRadius: 2 }}>
                <Typography color="text.secondary">No transactions logged yet.</Typography>
              </Box>
            ) : (
              <TableContainer component={Paper} variant="outlined" sx={{ maxHeight: 440, borderRadius: 2 }}>
                <Table stickyHeader size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Date</TableCell>
                      <TableCell>Type</TableCell>
                      <TableCell align="right">Amount</TableCell>
                      {isUnitBased && (
                        <>
                          <TableCell align="right">Units</TableCell>
                          <TableCell align="right">Price/Unit</TableCell>
                        </>
                      )}
                      <TableCell>Notes</TableCell>
                      <TableCell align="center">Action</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {transactions.map((tx) => (
                      <TableRow key={tx.id} hover>
                        <TableCell sx={{ whiteSpace: 'nowrap' }}>{formatTxDate(tx.transactionDate)}</TableCell>
                        <TableCell>
                          <Chip 
                            label={tx.transactionType} 
                            color={getBadgeColor(tx.transactionType)} 
                            size="small"
                            sx={{ fontWeight: 600, fontSize: '0.7rem' }}
                          />
                        </TableCell>
                        <TableCell align="right" sx={{ fontWeight: 600 }}>{formatCurrency(tx.amount)}</TableCell>
                        {isUnitBased && (
                          <>
                            <TableCell align="right">{tx.units !== null ? tx.units.toLocaleString('en-IN') : '-'}</TableCell>
                            <TableCell align="right">{tx.pricePerUnit !== null ? formatCurrency(tx.pricePerUnit) : '-'}</TableCell>
                          </>
                        )}
                        <TableCell sx={{ maxWidth: 150, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                          {tx.description || <Typography variant="caption" color="text.disabled">No details</Typography>}
                        </TableCell>
                        <TableCell align="center">
                          {transactions.length === 1 ? (
                            /* Don't allow deleting the only transaction, as assets must have at least one initial txn */
                            <IconButton disabled size="small" title="Cannot delete initial transaction. Delete the asset instead.">
                              <DeleteIcon fontSize="small" />
                            </IconButton>
                          ) : (
                            <IconButton 
                              onClick={() => handleDeleteTransaction(tx.id)} 
                              size="small" 
                              color="error"
                            >
                              <DeleteIcon fontSize="small" />
                            </IconButton>
                          )}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            )}
          </Grid>
        </Grid>
      </DialogContent>
      
      <Divider />

      <DialogActions sx={{ p: 2, px: 3 }}>
        <Button onClick={onClose} variant="contained" color="secondary">
          Close Ledger
        </Button>
      </DialogActions>
    </Dialog>
  );
}
