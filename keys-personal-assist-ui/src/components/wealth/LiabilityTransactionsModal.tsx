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
import type { Liability, LiabilityTransaction, LiabilityTransactionRequest } from '@/types/liability';
import { formatCurrency } from '@/utils/formatters';
import { toast } from 'sonner';

interface LiabilityTransactionsModalProps {
  open: boolean;
  liability: Liability | null;
  onClose: () => void;
  onSuccess: () => void;
}

export default function LiabilityTransactionsModal({ open, liability, onClose, onSuccess }: LiabilityTransactionsModalProps) {
  const [transactions, setTransactions] = useState<LiabilityTransaction[]>([]);
  const [loading, setLoading] = useState(false);

  // Form State
  const [transactionType, setTransactionType] = useState<'BORROW' | 'REPAY' | 'REVALUE'>('REPAY');
  const [amount, setAmount] = useState<string>('');
  const [description, setDescription] = useState<string>('');
  const [transactionDate, setTransactionDate] = useState<string>(
    new Date().toISOString().substring(0, 16)
  );

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

  const fetchTransactions = async () => {
    if (!liability) return;
    setLoading(true);
    try {
      const data = await emsClient.getTransactionsForLiability(liability.id);
      setTransactions(data.sort((a, b) => new Date(b.transactionDate).getTime() - new Date(a.transactionDate).getTime()));
    } catch (err) {
      console.error(err);
      toast.error('Failed to load liability ledger');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (open && liability) {
      fetchTransactions();
      resetForm();
    }
  }, [open, liability]);

  const resetForm = () => {
    setTransactionType('REPAY');
    setAmount('');
    setDescription('');
    setTransactionDate(new Date().toISOString().substring(0, 16));
  };

  const validateTransactionForm = (): boolean => {
    if (!liability) return false;

    const amt = parseFloat(amount);
    if (isNaN(amt) || amt <= 0) {
      toast.error('Amount must be a positive number');
      return false;
    }

    if (!transactionDate) {
      toast.error('Transaction date is required');
      return false;
    }

    return true;
  };

  const handleAddTransaction = async () => {
    if (!liability || !validateTransactionForm()) return;

    const reqData: LiabilityTransactionRequest = {
      transactionType,
      amount: parseFloat(amount),
      transactionDate: new Date(transactionDate).toISOString(),
      description: description.trim() || null,
    };

    try {
      await emsClient.addTransactionToLiability(liability.id, reqData);
      toast.success('Transaction logged successfully');
      resetForm();
      fetchTransactions();
      onSuccess();
    } catch (err: any) {
      console.error(err);
      toast.error(err.message || 'Failed to record transaction');
    }
  };

  const handleDeleteTransaction = (txId: string) => {
    openConfirm(
      'Delete Transaction',
      'Are you sure you want to delete this transaction? This will revert the outstanding balance calculations. This action cannot be undone.',
      async () => {
        try {
          await emsClient.deleteLiabilityTransaction(txId);
          toast.success('Transaction deleted');
          fetchTransactions();
          onSuccess();
        } catch (err) {
          console.error(err);
          toast.error('Failed to delete transaction');
        }
      }
    );
  };

  const getBadgeColor = (type: string) => {
    switch (type) {
      case 'BORROW': return 'error';
      case 'REPAY': return 'success';
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
    <>
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
                ? '1px solid rgba(244, 63, 94, 0.15)'
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
              Liability: {liability?.name} ({liability?.categoryName})
            </Typography>
          </Box>
          <IconButton onClick={onClose} size="small" sx={{ color: 'text.secondary' }}>
            <CloseIcon />
          </IconButton>
        </DialogTitle>

        <Divider />

        <DialogContent sx={{ p: 3 }}>
          <Grid container spacing={4}>
            {/* Left Column: Form */}
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
                  }}
                >
                  <MenuItem value="REPAY">REPAY (Log Repayment/EMI)</MenuItem>
                  <MenuItem value="BORROW">BORROW (Add Principal/Charges)</MenuItem>
                  <MenuItem value="REVALUE">REVALUE (Update Balance from Statement)</MenuItem>
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

                <TextField
                  fullWidth
                  required
                  type="number"
                  label={
                    transactionType === 'REVALUE'
                      ? 'New Statement Balance (INR)'
                      : transactionType === 'BORROW'
                      ? 'Borrowing / Fee Amount (INR)'
                      : 'Repayment Amount (INR)'
                  }
                  placeholder="e.g. 15000.00"
                  value={amount}
                  onChange={(e) => setAmount(e.target.value)}
                  inputProps={{ step: 'any', min: '0' }}
                  InputProps={{
                    startAdornment: <InputAdornment position="start">₹</InputAdornment>,
                  }}
                />

                <TextField
                  fullWidth
                  multiline
                  rows={2}
                  label="Description / Audit Notes"
                  placeholder="e.g. monthly EMI payment, part-payment, bank interest charge"
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

            {/* Right Column: Table */}
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
                          <TableCell sx={{ maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                            {tx.description || <Typography variant="caption" color="text.disabled">No details</Typography>}
                          </TableCell>
                          <TableCell align="center">
                            {transactions.length === 1 ? (
                              <IconButton disabled size="small" title="Cannot delete initial transaction. Delete the liability instead.">
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
    </>
  );
}
