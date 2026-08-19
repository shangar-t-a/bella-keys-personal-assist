import { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Box,
  Typography,
  Grid,
  IconButton,
  Divider,
  Paper,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  CircularProgress,
} from '@mui/material';
import {
  Close as CloseIcon,
  Home as HomeIcon,
  ReceiptLong as ReceiptIcon,
  AccountBalance as BankIcon,
  Payments as PaymentsIcon,
  FormatListBulleted as ListIcon,
  ExpandMore as ExpandMoreIcon,
} from '@mui/icons-material';
import { emsClient } from '@/api/clients/ems-client';
import type { Asset, AssetTransaction } from '@/types/asset';
import { formatCurrency, formatCompactRupees } from '@/utils/formatters';

interface AssetCostBreakdownPopoverProps {
  open: boolean;
  asset: Asset | null;
  onClose: () => void;
  onOpenLedger: (asset: Asset) => void;
}

export default function AssetCostBreakdownPopover({
  open,
  asset,
  onClose,
  onOpenLedger,
}: AssetCostBreakdownPopoverProps) {
  const [loading, setLoading] = useState(false);
  const [transactions, setTransactions] = useState<AssetTransaction[]>([]);

  useEffect(() => {
    if (open && asset) {
      const loadTx = async () => {
        setLoading(true);
        try {
          const data = await emsClient.getTransactionsForAsset(asset.id);
          setTransactions(data);
        } catch (err) {
          console.error('Failed to load breakdown transactions', err);
        } finally {
          setLoading(false);
        }
      };
      loadTx();
    }
  }, [open, asset]);

  if (!asset) return null;

  // Group transactions by category for scalable accordion display
  const baseTxs = transactions.filter((t) => t.transactionType === 'BUY');
  const improvementTxs = transactions.filter((t) => t.transactionType === 'IMPROVEMENT');
  const ancillaryTxs = transactions.filter((t) => t.transactionType === 'ANCILLARY_FEE');
  const interestPaidTxs = transactions.filter((t) => t.transactionType === 'CAPITALIZED_INTEREST');
  const interestRedTxs = transactions.filter((t) => t.transactionType === 'INTEREST_REDUCTION');
  const sellTxs = transactions.filter((t) => t.transactionType === 'SELL');

  const baseSum = baseTxs.reduce((acc, t) => acc + t.amount, 0) + improvementTxs.reduce((acc, t) => acc + t.amount, 0) - sellTxs.reduce((acc, t) => acc + t.amount, 0);
  const baseValue = asset.baseAssetValue ?? Math.max(0, baseSum);

  const feesAndTaxes = asset.additionalSpent ?? ancillaryTxs.reduce((acc, t) => acc + t.amount, 0);

  const netInterestSum = interestPaidTxs.reduce((acc, t) => acc + t.amount, 0) - interestRedTxs.reduce((acc, t) => acc + t.amount, 0);
  const loanInterest = asset.totalLoanInterest ?? netInterestSum;

  const totalOutflow = asset.totalCashOutflow ?? (baseValue + feesAndTaxes + loanInterest);

  const basePct = totalOutflow > 0 ? Math.min(100, Math.max(0, (baseValue / totalOutflow) * 100)) : 0;
  const feesPct = totalOutflow > 0 ? Math.min(100, Math.max(0, (feesAndTaxes / totalOutflow) * 100)) : 0;
  const interestPct = totalOutflow > 0 ? Math.min(100, Math.max(0, (loanInterest / totalOutflow) * 100)) : 0;

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="md"
      fullWidth
      PaperProps={{
        sx: {
          borderRadius: 3,
          backgroundImage: (theme) =>
            theme.palette.mode === 'dark'
              ? 'linear-gradient(135deg, rgba(30, 41, 59, 0.95) 0%, rgba(15, 23, 42, 0.95) 100%)'
              : 'none',
          backdropFilter: 'blur(12px)',
          border: (theme) =>
            theme.palette.mode === 'dark'
              ? '1px solid rgba(56, 189, 248, 0.2)'
              : '1px solid rgba(0, 0, 0, 0.08)',
        },
      }}
    >
      <DialogTitle sx={{ m: 0, p: 2.5, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box>
          <Typography variant="h5" sx={{ fontWeight: 700, fontFamily: '"Space Grotesk", sans-serif' }}>
            Cost & Expenditure Breakdown
          </Typography>
          <Typography variant="subtitle2" color="text.secondary">
            Asset: {asset.name} ({asset.categoryName})
          </Typography>
        </Box>
        <IconButton onClick={onClose} size="small" sx={{ color: 'text.secondary' }}>
          <CloseIcon />
        </IconButton>
      </DialogTitle>

      <Divider />

      <DialogContent sx={{ p: 3 }}>
        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 6 }}>
            <CircularProgress size={36} />
          </Box>
        ) : (
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
            {/* 4 Tile KPI Grid */}
            <Grid container spacing={2}>
              {/* Tile 1: Base Purchase */}
              <Grid size={{ xs: 12, sm: 6, md: 3 }}>
                <Paper
                  elevation={0}
                  sx={{
                    p: 2,
                    borderRadius: 2,
                    border: '1px solid',
                    borderColor: 'success.main',
                    bgcolor: (theme) =>
                      theme.palette.mode === 'dark' ? 'rgba(34, 197, 94, 0.08)' : 'rgba(34, 197, 94, 0.04)',
                  }}
                >
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1, color: 'success.main' }}>
                    <HomeIcon fontSize="small" />
                    <Typography variant="caption" sx={{ fontWeight: 700, textTransform: 'uppercase' }}>
                      Base Purchase
                    </Typography>
                  </Box>
                  <Typography variant="h6" sx={{ fontWeight: 700, fontFamily: '"Space Grotesk", sans-serif' }}>
                    {formatCurrency(baseValue)}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {basePct.toFixed(1)}% of total spent
                  </Typography>
                </Paper>
              </Grid>

              {/* Tile 2: Sunk Fees */}
              <Grid size={{ xs: 12, sm: 6, md: 3 }}>
                <Paper
                  elevation={0}
                  sx={{
                    p: 2,
                    borderRadius: 2,
                    border: '1px solid',
                    borderColor: 'warning.main',
                    bgcolor: (theme) =>
                      theme.palette.mode === 'dark' ? 'rgba(245, 158, 11, 0.08)' : 'rgba(245, 158, 11, 0.04)',
                  }}
                >
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1, color: 'warning.main' }}>
                    <ReceiptIcon fontSize="small" />
                    <Typography variant="caption" sx={{ fontWeight: 700, textTransform: 'uppercase' }}>
                      Sunk Fees & Taxes
                    </Typography>
                  </Box>
                  <Typography variant="h6" sx={{ fontWeight: 700, fontFamily: '"Space Grotesk", sans-serif' }}>
                    {formatCurrency(feesAndTaxes)}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {feesPct.toFixed(1)}% of total spent
                  </Typography>
                </Paper>
              </Grid>

              {/* Tile 3: Net Loan Interest */}
              <Grid size={{ xs: 12, sm: 6, md: 3 }}>
                <Paper
                  elevation={0}
                  sx={{
                    p: 2,
                    borderRadius: 2,
                    border: '1px solid',
                    borderColor: 'secondary.main',
                    bgcolor: (theme) =>
                      theme.palette.mode === 'dark' ? 'rgba(168, 85, 247, 0.08)' : 'rgba(168, 85, 247, 0.04)',
                  }}
                >
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1, color: 'secondary.main' }}>
                    <BankIcon fontSize="small" />
                    <Typography variant="caption" sx={{ fontWeight: 700, textTransform: 'uppercase' }}>
                      Net Loan Interest
                    </Typography>
                  </Box>
                  <Typography variant="h6" sx={{ fontWeight: 700, fontFamily: '"Space Grotesk", sans-serif' }}>
                    {formatCurrency(loanInterest)}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {interestPct.toFixed(1)}% of total spent
                  </Typography>
                </Paper>
              </Grid>

              {/* Tile 4: Total Cash Outflow */}
              <Grid size={{ xs: 12, sm: 6, md: 3 }}>
                <Paper
                  elevation={0}
                  sx={{
                    p: 2,
                    borderRadius: 2,
                    border: '1px solid',
                    borderColor: 'primary.main',
                    bgcolor: (theme) =>
                      theme.palette.mode === 'dark' ? 'rgba(56, 189, 248, 0.12)' : 'rgba(56, 189, 248, 0.06)',
                  }}
                >
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1, color: 'primary.main' }}>
                    <PaymentsIcon fontSize="small" />
                    <Typography variant="caption" sx={{ fontWeight: 700, textTransform: 'uppercase' }}>
                      Total Outflow
                    </Typography>
                  </Box>
                  <Typography variant="h6" sx={{ fontWeight: 700, fontFamily: '"Space Grotesk", sans-serif' }}>
                    {formatCurrency(totalOutflow)}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    True Cost Basis
                  </Typography>
                </Paper>
              </Grid>
            </Grid>

            {/* Visual Composition Progress Bar */}
            <Paper elevation={0} sx={{ p: 2.5, borderRadius: 2, border: '1px solid', borderColor: 'divider' }}>
              <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 1.5, fontFamily: '"Space Grotesk", sans-serif' }}>
                Cost Outflow Composition
              </Typography>

              <Box sx={{ width: '100%', height: 12, borderRadius: 6, bgcolor: 'action.disabledBackground', overflow: 'hidden', display: 'flex', mb: 2 }}>
                <Box sx={{ width: `${basePct}%`, bgcolor: 'success.main', height: '100%' }} />
                <Box sx={{ width: `${feesPct}%`, bgcolor: 'warning.main', height: '100%' }} />
                <Box sx={{ width: `${interestPct}%`, bgcolor: 'secondary.main', height: '100%' }} />
              </Box>

              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 3 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Box sx={{ width: 10, height: 10, borderRadius: '50%', bgcolor: 'success.main' }} />
                  <Typography variant="caption" color="text.secondary">
                    Base Purchase: <strong>{formatCompactRupees(baseValue)}</strong> ({basePct.toFixed(1)}%)
                  </Typography>
                </Box>

                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Box sx={{ width: 10, height: 10, borderRadius: '50%', bgcolor: 'warning.main' }} />
                  <Typography variant="caption" color="text.secondary">
                    Fees & Stamp: <strong>{formatCompactRupees(feesAndTaxes)}</strong> ({feesPct.toFixed(1)}%)
                  </Typography>
                </Box>

                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Box sx={{ width: 10, height: 10, borderRadius: '50%', bgcolor: 'secondary.main' }} />
                  <Typography variant="caption" color="text.secondary">
                    Net Interest: <strong>{formatCompactRupees(loanInterest)}</strong> ({interestPct.toFixed(1)}%)
                  </Typography>
                </Box>
              </Box>
            </Paper>

            {/* Grouped Category Accordions for Scalability */}
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
              <Typography variant="subtitle2" sx={{ fontWeight: 700, fontFamily: '"Space Grotesk", sans-serif' }}>
                Categorized Expenditure Details
              </Typography>

              {/* Group 1: Base Purchase */}
              <Accordion defaultExpanded elevation={0} sx={{ border: '1px solid', borderColor: 'divider', borderRadius: '8px !important' }}>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%', pr: 2 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                      <HomeIcon color="success" fontSize="small" />
                      <Typography variant="body2" sx={{ fontWeight: 700 }}>
                        Base Purchase & Improvements ({baseTxs.length + improvementTxs.length} items)
                      </Typography>
                    </Box>
                    <Typography variant="body2" sx={{ fontWeight: 700, color: 'success.main', fontFamily: '"Space Grotesk", sans-serif' }}>
                      {formatCurrency(baseValue)}
                    </Typography>
                  </Box>
                </AccordionSummary>
                <AccordionDetails sx={{ pt: 0 }}>
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                    {[...baseTxs, ...improvementTxs].map((tx) => (
                      <Box key={tx.id} sx={{ display: 'flex', justifyContent: 'space-between', py: 0.5, px: 1, bgcolor: 'action.hover', borderRadius: 1 }}>
                        <Typography variant="caption">{tx.description || tx.transactionType}</Typography>
                        <Typography variant="caption" sx={{ fontWeight: 700 }}>{formatCurrency(tx.amount)}</Typography>
                      </Box>
                    ))}
                    {[...baseTxs, ...improvementTxs].length === 0 && (
                      <Typography variant="caption" color="text.secondary">No itemized base purchase entries logged.</Typography>
                    )}
                  </Box>
                </AccordionDetails>
              </Accordion>

              {/* Group 2: Ancillary Fees & Taxes */}
              <Accordion elevation={0} sx={{ border: '1px solid', borderColor: 'divider', borderRadius: '8px !important' }}>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%', pr: 2 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                      <ReceiptIcon color="warning" fontSize="small" />
                      <Typography variant="body2" sx={{ fontWeight: 700 }}>
                        Ancillary, Legal & Stamp Fees ({ancillaryTxs.length} items)
                      </Typography>
                    </Box>
                    <Typography variant="body2" sx={{ fontWeight: 700, color: 'warning.main', fontFamily: '"Space Grotesk", sans-serif' }}>
                      {formatCurrency(feesAndTaxes)}
                    </Typography>
                  </Box>
                </AccordionSummary>
                <AccordionDetails sx={{ pt: 0 }}>
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                    {ancillaryTxs.map((tx) => (
                      <Box key={tx.id} sx={{ display: 'flex', justifyContent: 'space-between', py: 0.5, px: 1, bgcolor: 'action.hover', borderRadius: 1 }}>
                        <Typography variant="caption">{tx.description || 'Ancillary Fee'}</Typography>
                        <Typography variant="caption" sx={{ fontWeight: 700 }}>{formatCurrency(tx.amount)}</Typography>
                      </Box>
                    ))}
                    {ancillaryTxs.length === 0 && (
                      <Typography variant="caption" color="text.secondary">No ancillary fees logged.</Typography>
                    )}
                  </Box>
                </AccordionDetails>
              </Accordion>

              {/* Group 3: Loan Interest & Savings */}
              <Accordion elevation={0} sx={{ border: '1px solid', borderColor: 'divider', borderRadius: '8px !important' }}>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%', pr: 2 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                      <BankIcon color="secondary" fontSize="small" />
                      <Typography variant="body2" sx={{ fontWeight: 700 }}>
                        Financing Carrying Costs & Net Interest ({interestPaidTxs.length + interestRedTxs.length} items)
                      </Typography>
                    </Box>
                    <Typography variant="body2" sx={{ fontWeight: 700, color: 'secondary.main', fontFamily: '"Space Grotesk", sans-serif' }}>
                      {formatCurrency(loanInterest)}
                    </Typography>
                  </Box>
                </AccordionSummary>
                <AccordionDetails sx={{ pt: 0 }}>
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                    {interestPaidTxs.map((tx) => (
                      <Box key={tx.id} sx={{ display: 'flex', justifyContent: 'space-between', py: 0.5, px: 1, bgcolor: 'action.hover', borderRadius: 1 }}>
                        <Typography variant="caption">{tx.description || 'Loan Interest Paid'}</Typography>
                        <Typography variant="caption" sx={{ fontWeight: 700, color: 'error.main' }}>+{formatCurrency(tx.amount)}</Typography>
                      </Box>
                    ))}
                    {interestRedTxs.map((tx) => (
                      <Box key={tx.id} sx={{ display: 'flex', justifyContent: 'space-between', py: 0.5, px: 1, bgcolor: 'action.hover', borderRadius: 1 }}>
                        <Typography variant="caption">{tx.description || 'Interest Reduced'}</Typography>
                        <Typography variant="caption" sx={{ fontWeight: 700, color: 'success.main' }}>-{formatCurrency(tx.amount)}</Typography>
                      </Box>
                    ))}
                    {interestPaidTxs.length === 0 && interestRedTxs.length === 0 && (
                      <Typography variant="caption" color="text.secondary">No loan interest entries logged.</Typography>
                    )}
                  </Box>
                </AccordionDetails>
              </Accordion>
            </Box>
          </Box>
        )}
      </DialogContent>

      <Divider />

      <DialogActions sx={{ p: 2.5, justifyContent: 'space-between' }}>
        <Button
          variant="outlined"
          startIcon={<ListIcon />}
          onClick={() => {
            onClose();
            onOpenLedger(asset);
          }}
          sx={{ borderRadius: 2 }}
        >
          Open Full Itemized Ledger ({transactions.length} entries)
        </Button>
        <Button variant="contained" onClick={onClose} sx={{ borderRadius: 2 }}>
          Close
        </Button>
      </DialogActions>
    </Dialog>
  );
}
