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
  Grid,
  Card,
  CardActionArea,
  IconButton,
  InputAdornment,
  Divider,
  ToggleButtonGroup,
  ToggleButton,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material';
import {
  Close as CloseIcon,
  ShowChart as EquityIcon,
  AccountBalance as DebtIcon,
  HomeWork as RealEstateIcon,
  MonetizationOn as CommoditiesIcon,
  Savings as CashBankIcon,
  ArrowBack as ArrowBackIcon,
  ExpandMore as ExpandMoreIcon,
} from '@mui/icons-material';
import { emsClient } from '@/api/clients/ems-client';
import type { AssetCategory, AssetRequest } from '@/types/asset';
import { toast } from 'sonner';

interface AddAssetWizardProps {
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export default function AddAssetWizard({ open, onClose, onSuccess }: AddAssetWizardProps) {
  const [step, setStep] = useState<1 | 2>(1);
  const [categories, setCategories] = useState<AssetCategory[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<AssetCategory | null>(null);
  const [selectedSubtype, setSelectedSubtype] = useState<string>('');

  // Step 2 Form States
  const [name, setName] = useState('');
  const [notes, setNotes] = useState('');
  // Specific toggles
  const [metalType, setMetalType] = useState<'Gold' | 'Silver'>('Gold');
  const [purity, setPurity] = useState<'24K' | '22K'>('24K');
  const [equityType, setEquityType] = useState<'Stock' | 'Mutual Fund' | 'ETF'>('Stock');

  // Input value states
  const [units, setUnits] = useState<string>('');
  const [pricePerUnit, setPricePerUnit] = useState<string>('');
  const [currentValueInput, setCurrentValueInput] = useState<string>('');
  const [totalInvestedInput, setTotalInvestedInput] = useState<string>('');

  // Fetch categories on mount
  useEffect(() => {
    if (open) {
      emsClient.getAllAssetCategories()
        .then((cats) => {
          setCategories(cats);
          // Auto select first category (Equity) by default in Step 1
          const firstCat = cats.find(c => c.code === 'EQUITY');
          if (firstCat) setSelectedCategory(firstCat);
        })
        .catch((err) => {
          console.error(err);
          toast.error('Failed to load asset categories');
        });
      resetWizard();
    }
  }, [open]);

  const resetWizard = () => {
    setStep(1);
    setSelectedSubtype('');
    setName('');
    setNotes('');
    setUnits('');
    setPricePerUnit('');
    setCurrentValueInput('');
    setTotalInvestedInput('');
    setMetalType('Gold');
    setPurity('24K');
    setEquityType('Stock');
  };

  const getSubtypesForCategory = (code: string) => {
    switch (code) {
      case 'EQUITY':
        return ['Stock', 'Mutual Fund', 'ETF', 'NPS', 'Other Equity'];
      case 'DEBT':
        return ['PPF', 'EPF / VPF', 'NPS', 'SSY', 'Govt. Savings Scheme', 'Fixed Deposit', 'Bonds', 'Other Debt'];
      case 'REAL_ESTATE':
        return ['Residential Property', 'Commercial Property', 'Plot', 'REIT', 'Other Property'];
      case 'COMMODITIES':
        return ['Physical Gold / Silver', 'Digital (ETF / SGB / MF)'];
      case 'CASH_BANK':
        return ['Savings Account', 'Current Account', 'Cash in Hand', 'Other Cash'];
      default:
        return [];
    }
  };

  const isUnitBased = selectedCategory?.code === 'EQUITY' || selectedCategory?.code === 'COMMODITIES';

  // Dynamic automatic calculation triggers
  useEffect(() => {
    if (isUnitBased && units && pricePerUnit) {
      const u = parseFloat(units);
      const p = parseFloat(pricePerUnit);
      if (!isNaN(u) && !isNaN(p)) {
        const calcVal = (u * p).toFixed(2);
        setTotalInvestedInput(calcVal);
        // Default current value to invested value if not modified
        if (!currentValueInput) {
          setCurrentValueInput(calcVal);
        }
      }
    }
  }, [units, pricePerUnit, isUnitBased]);

  const handleSubtypeSelect = (subtype: string) => {
    setSelectedSubtype(subtype);
    // Setup defaults
    if (selectedCategory?.code === 'COMMODITIES' && subtype === 'Physical Gold / Silver') {
      setName('Gold Jewelry');
    } else {
      setName(subtype);
    }
    setStep(2);
  };

  const validateForm = (): boolean => {
    if (!name.trim()) {
      toast.error('Asset name is required');
      return false;
    }

    if (isUnitBased) {
      const u = parseFloat(units);
      const p = parseFloat(pricePerUnit);
      if (isNaN(u) || u <= 0) {
        toast.error('Quantity/Units must be a positive number');
        return false;
      }
      if (isNaN(p) || p <= 0) {
        toast.error('Price per unit must be a positive number');
        return false;
      }
    } else {
      const cur = parseFloat(currentValueInput);
      const inv = parseFloat(totalInvestedInput);
      if (isNaN(cur) || cur < 0) {
        toast.error('Current Value must be a non-negative number');
        return false;
      }
      if (isNaN(inv) || inv < 0) {
        toast.error('Total Invested must be a non-negative number');
        return false;
      }
    }
    return true;
  };

  const handleSave = async (addAnother = false) => {
    if (!validateForm()) return;

    let finalInvested = parseFloat(totalInvestedInput);
    let finalCurrent = parseFloat(currentValueInput);

    if (isUnitBased) {
      finalInvested = parseFloat(units) * parseFloat(pricePerUnit);
    }

    const reqData: AssetRequest = {
      categoryId: selectedCategory!.id,
      name: name.trim(),
      subCategory: selectedSubtype,
      initialAmount: finalInvested,
      units: isUnitBased ? parseFloat(units) : null,
      pricePerUnit: isUnitBased ? parseFloat(pricePerUnit) : null,
      notes: notes.trim() || null,
    };

    try {
      // Create asset - this automatically logs a BUY transaction with finalInvested
      const createdAsset = await emsClient.createAsset(reqData);

      // If current value is different from invested value (for flat assets or overrides), log a REVALUE transaction
      if (finalCurrent !== finalInvested) {
        await emsClient.addTransactionToAsset(createdAsset.id, {
          transactionType: 'REVALUE',
          amount: finalCurrent,
          pricePerUnit: isUnitBased ? (finalCurrent / parseFloat(units)) : null,
          description: 'Initial valuation adjustment',
        });
      }

      toast.success(`Asset "${name}" logged successfully`);

      if (addAnother) {
        // Reset states keeping Category / Subtype for quick entry
        setName(selectedSubtype);
        setUnits('');
        setPricePerUnit('');
        setCurrentValueInput('');
        setTotalInvestedInput('');
        setNotes('');
        setNotes('');
        setStep(2);
      } else {
        onSuccess();
        onClose();
      }
    } catch (err: any) {
      console.error(err);
      toast.error(err.message || 'Failed to create asset');
    }
  };

  const getCategoryIcon = (code: string) => {
    switch (code) {
      case 'EQUITY': return <EquityIcon />;
      case 'DEBT': return <DebtIcon />;
      case 'REAL_ESTATE': return <RealEstateIcon />;
      case 'COMMODITIES': return <CommoditiesIcon />;
      case 'CASH_BANK': return <CashBankIcon />;
      default: return <EquityIcon />;
    }
  };

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth="md"
      fullWidth
      PaperProps={{
        sx: {
          borderRadius: 3,
          p: 1,
          bgcolor: 'background.paper',
        }
      }}
    >
      <DialogTitle sx={{ m: 0, p: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box>
          <Typography variant="h5" sx={{ fontWeight: 700, fontFamily: '"Space Grotesk", sans-serif' }}>
            Add Asset
          </Typography>
          <Typography variant="caption" color="text.secondary">
            Step {step} of 2: {step === 1 ? 'Select asset type' : selectedSubtype}
          </Typography>
        </Box>
        <IconButton onClick={onClose} size="small" sx={{ color: 'text.secondary' }}>
          <CloseIcon />
        </IconButton>
      </DialogTitle>

      <Divider />

      <DialogContent sx={{ p: 3, minHeight: 400 }}>
        {step === 1 ? (
          /* Step 1: Select Type */
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3.5 }}>
            {/* Asset / Liability toggle */}
            <Box>
              <ToggleButtonGroup
                value="ASSET"
                exclusive
                size="small"
                sx={{ width: 300 }}
              >
                <ToggleButton value="ASSET" sx={{ width: '50%', fontWeight: 600 }}>Asset</ToggleButton>
                <ToggleButton value="LIABILITY" disabled sx={{ width: '50%', fontWeight: 600 }}>Liability</ToggleButton>
              </ToggleButtonGroup>
            </Box>

            {/* Category tabs */}
            <Card variant="outlined" sx={{ borderRadius: 2 }}>
              <Box sx={{ display: 'flex', borderBottom: 1, borderColor: 'divider', bgcolor: (theme) => theme.palette.mode === 'dark' ? 'rgba(255,255,255,0.02)' : '#fcfdfe' }}>
                {categories.map((cat) => (
                  <Button
                    key={cat.id}
                    onClick={() => setSelectedCategory(cat)}
                    variant={selectedCategory?.id === cat.id ? 'contained' : 'text'}
                    color={selectedCategory?.id === cat.id ? 'primary' : 'inherit'}
                    startIcon={getCategoryIcon(cat.code)}
                    sx={{
                      borderRadius: 0,
                      py: 1.5,
                      px: 3,
                      flexGrow: 1,
                      textTransform: 'none',
                      fontWeight: 600,
                      boxShadow: 'none',
                      '&:hover': { boxShadow: 'none' }
                    }}
                  >
                    {cat.name}
                  </Button>
                ))}
              </Box>

              {/* Subtype tiles */}
              <Box sx={{ p: 3 }}>
                <Typography variant="subtitle2" sx={{ mb: 2, color: 'text.secondary', fontWeight: 600, textTransform: 'uppercase', letterSpacing: 0.5 }}>
                  Select Sub Type
                </Typography>
                <Grid container spacing={2}>
                  {selectedCategory && getSubtypesForCategory(selectedCategory.code).map((sub) => (
                    <Grid size={{ xs: 12, sm: 6, md: 4 }} key={sub}>
                      <Card
                        variant="outlined"
                        sx={{
                          borderRadius: 2,
                          transition: 'all 0.15s ease',
                          borderColor: 'divider',
                          '&:hover': {
                            borderColor: 'primary.main',
                            bgcolor: (theme) => theme.palette.mode === 'dark' ? 'rgba(56, 189, 248, 0.04)' : 'rgba(30, 80, 103, 0.02)',
                            transform: 'translateY(-2px)'
                          }
                        }}
                      >
                        <CardActionArea onClick={() => handleSubtypeSelect(sub)} sx={{ p: 2.5, textAlign: 'center' }}>
                          <Typography variant="body2" sx={{ fontWeight: 600 }}>
                            {sub}
                          </Typography>
                        </CardActionArea>
                      </Card>
                    </Grid>
                  ))}
                </Grid>
              </Box>
            </Card>
          </Box>
        ) : (
          /* Step 2: Details Form */
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3.5 }}>
            {/* Header info card */}
            <Card variant="outlined" sx={{ p: 2.5, display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderRadius: 2 }}>
              <Box>
                <Typography variant="caption" color="text.secondary" display="block" sx={{ fontWeight: 600, textTransform: 'uppercase' }}>
                  Select Asset Type
                </Typography>
                <Typography variant="subtitle1" sx={{ fontWeight: 700, color: 'primary.main' }}>
                  {selectedCategory?.name} &gt; {selectedSubtype}
                </Typography>
              </Box>
              <Button 
                startIcon={<ArrowBackIcon />} 
                onClick={() => setStep(1)} 
                variant="text" 
                size="small"
                sx={{ textTransform: 'none', fontWeight: 600 }}
              >
                Change type
              </Button>
            </Card>

            {/* Step 2 form configurations */}
            <Grid container spacing={4}>
              <Grid size={{ xs: 12, md: 7 }}>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2.5 }}>
                  <Typography variant="subtitle2" sx={{ fontWeight: 700, color: 'text.secondary', textTransform: 'uppercase', letterSpacing: 0.5 }}>
                    Asset Details
                  </Typography>

                  {/* Commodities Toggles */}
                  {selectedCategory?.code === 'COMMODITIES' && selectedSubtype === 'Physical Gold / Silver' && (
                    <Box sx={{ display: 'flex', gap: 3, mb: 1 }}>
                      <Box sx={{ flexGrow: 1 }}>
                        <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 600, display: 'block', mb: 1 }}>
                          Metal Type
                        </Typography>
                        <ToggleButtonGroup
                          value={metalType}
                          exclusive
                          onChange={(_e, v) => v && setMetalType(v)}
                          size="small"
                          fullWidth
                        >
                          <ToggleButton value="Gold" sx={{ fontWeight: 600 }}>Gold</ToggleButton>
                          <ToggleButton value="Silver" sx={{ fontWeight: 600 }}>Silver</ToggleButton>
                        </ToggleButtonGroup>
                      </Box>

                      {metalType === 'Gold' && (
                        <Box sx={{ flexGrow: 1 }}>
                          <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 600, display: 'block', mb: 1 }}>
                            Purity
                          </Typography>
                          <ToggleButtonGroup
                            value={purity}
                            exclusive
                            onChange={(_e, v) => v && setPurity(v)}
                            size="small"
                            fullWidth
                          >
                            <ToggleButton value="24K" sx={{ fontWeight: 600 }}>24K</ToggleButton>
                            <ToggleButton value="22K" sx={{ fontWeight: 600 }}>22K</ToggleButton>
                          </ToggleButtonGroup>
                        </Box>
                      )}
                    </Box>
                  )}

                  {/* Equity type segment toggles */}
                  {selectedCategory?.code === 'EQUITY' && (
                    <Box sx={{ mb: 1 }}>
                      <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 600, display: 'block', mb: 1 }}>
                        Asset Type
                      </Typography>
                      <ToggleButtonGroup
                        value={equityType}
                        exclusive
                        onChange={(_e, v) => v && setEquityType(v)}
                        size="small"
                        fullWidth
                      >
                        <ToggleButton value="Stock" sx={{ fontWeight: 600 }}>Stock</ToggleButton>
                        <ToggleButton value="Mutual Fund" sx={{ fontWeight: 600 }}>Mutual Fund</ToggleButton>
                        <ToggleButton value="ETF" sx={{ fontWeight: 600 }}>ETF</ToggleButton>
                      </ToggleButtonGroup>
                    </Box>
                  )}

                  {/* Name input */}
                  <TextField
                    fullWidth
                    required
                    label="Name *"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                  />

                  {/* Quantity inputs if unit-based */}
                  {isUnitBased && (
                    <Box sx={{ display: 'flex', gap: 2 }}>
                      <TextField
                        fullWidth
                        required
                        label={selectedCategory?.code === 'COMMODITIES' ? 'Weight (grams) *' : 'Quantity / Units *'}
                        type="number"
                        value={units}
                        onChange={(e) => setUnits(e.target.value)}
                        inputProps={{ step: 'any', min: '0' }}
                      />
                      <TextField
                        fullWidth
                        required
                        label={selectedCategory?.code === 'COMMODITIES' ? 'Price per Gram (INR) *' : 'Price per Unit (INR) *'}
                        type="number"
                        value={pricePerUnit}
                        onChange={(e) => setPricePerUnit(e.target.value)}
                        inputProps={{ step: 'any', min: '0' }}
                        InputProps={{
                          startAdornment: <InputAdornment position="start">₹</InputAdornment>,
                        }}
                      />
                    </Box>
                  )}

                  {/* Aligned Balances inputs */}
                  <Box sx={{ display: 'flex', gap: 2 }}>
                    <TextField
                      fullWidth
                      required
                      label="Current Value *"
                      type="number"
                      value={currentValueInput}
                      onChange={(e) => setCurrentValueInput(e.target.value)}
                      inputProps={{ step: 'any', min: '0' }}
                      InputProps={{
                        startAdornment: <InputAdornment position="start">₹</InputAdornment>,
                      }}
                    />
                    <TextField
                      fullWidth
                      required
                      disabled={isUnitBased} // Units calculation handles this
                      label="Total Invested *"
                      type="number"
                      value={totalInvestedInput}
                      onChange={(e) => setTotalInvestedInput(e.target.value)}
                      inputProps={{ step: 'any', min: '0' }}
                      InputProps={{
                        startAdornment: <InputAdornment position="start">₹</InputAdornment>,
                      }}
                    />
                  </Box>

                  {/* Collapsible notes section */}
                  <Accordion variant="outlined" sx={{ borderRadius: '6px !important', mt: 1 }}>
                    <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                      <Typography variant="body2" sx={{ fontWeight: 600 }}>
                        Add notes
                      </Typography>
                    </AccordionSummary>
                    <AccordionDetails sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                      <TextField
                        fullWidth
                        multiline
                        rows={2}
                        label="Notes"
                        placeholder="Additional tracking notes..."
                        value={notes}
                        onChange={(e) => setNotes(e.target.value)}
                      />
                    </AccordionDetails>
                  </Accordion>
                </Box>
              </Grid>

              {/* Step 2 Right Column: Informative Tips card */}
              <Grid size={{ xs: 12, md: 5 }}>
                <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
                  <Card 
                    variant="outlined" 
                    sx={{ 
                      p: 3, 
                      borderRadius: 2, 
                      bgcolor: (theme) => theme.palette.mode === 'dark' ? 'rgba(30, 41, 59, 0.3)' : '#fcfdfe',
                      borderStyle: 'dashed',
                      borderColor: 'primary.light',
                      height: '100%',
                      display: 'flex',
                      flexDirection: 'column',
                      justifyContent: 'center'
                    }}
                  >
                    <Typography variant="subtitle2" color="primary.main" sx={{ fontWeight: 700, mb: 1.5 }}>
                      Valuation Method Details
                    </Typography>
                    
                    <Typography variant="body2" color="text.secondary" paragraph>
                      {isUnitBased 
                        ? 'This category calculates assets dynamically based on quantity/weight held. The initial invested value will be computed automatically as (Units × Price per unit).' 
                        : 'This category tracks flat balance accounts (e.g. Bank Accounts, PPF). You supply the initial invested value and current value directly.'}
                    </Typography>

                    <Typography variant="body2" color="text.secondary">
                      Logging different Invested and Current Values will record a revaluation adjustments history transaction in the ledger.
                    </Typography>
                  </Card>
                </Box>
              </Grid>
            </Grid>
          </Box>
        )}
      </DialogContent>

      <Divider />

      <DialogActions sx={{ p: 2, px: 3, justifyContent: 'space-between' }}>
        {step === 2 ? (
          <Button
            startIcon={<ArrowBackIcon />}
            onClick={() => setStep(1)}
            variant="outlined"
            size="small"
          >
            Back to Categories
          </Button>
        ) : (
          <Box />
        )}

        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button onClick={onClose} variant="text" color="inherit">
            Cancel
          </Button>
          {step === 2 && (
            <>
              <Button
                onClick={() => handleSave(true)}
                variant="outlined"
                color="secondary"
              >
                Save & Add Another
              </Button>
              <Button
                onClick={() => handleSave(false)}
                variant="contained"
                color="primary"
              >
                Save
              </Button>
            </>
          )}
        </Box>
      </DialogActions>
    </Dialog>
  );
}
