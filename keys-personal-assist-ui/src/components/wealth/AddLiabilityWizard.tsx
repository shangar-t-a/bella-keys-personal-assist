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
  Select,
  MenuItem,
  FormControl,
  InputLabel,
} from '@mui/material';
import {
  Close as CloseIcon,
  AccountBalance as SecuredIcon,
  CreditCard as CreditCardIcon,
  MoneyOff as UnsecuredIcon,
  MonetizationOn as OtherIcon,
  ArrowBack as ArrowBackIcon,
  ExpandMore as ExpandMoreIcon,
} from '@mui/icons-material';
import { emsClient } from '@/api/clients/ems-client';
import type { LiabilityCategory, LiabilitySubcategory, LiabilityRequest } from '@/types/liability';
import { toast } from 'sonner';

interface AddLiabilityWizardProps {
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export default function AddLiabilityWizard({ open, onClose, onSuccess }: AddLiabilityWizardProps) {
  const [step, setStep] = useState<1 | 2>(1);
  const [categories, setCategories] = useState<LiabilityCategory[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<LiabilityCategory | null>(null);
  const [selectedSubcategory, setSelectedSubcategory] = useState<LiabilitySubcategory | null>(null);

  // Step 2 Form States
  const [name, setName] = useState('');
  const [notes, setNotes] = useState('');
  const [interestRate, setInterestRate] = useState<string>('');
  const [interestCompounding, setInterestCompounding] = useState<string>('MONTHLY');
  const [emiAmount, setEmiAmount] = useState<string>('');
  const [maturityDate, setMaturityDate] = useState<string>('');
  const [initialDate, setInitialDate] = useState<string>(new Date().toISOString().split('T')[0]);

  // Input value states
  const [outstandingBalance, setOutstandingBalance] = useState<string>('');
  const [originalBorrowed, setOriginalBorrowed] = useState<string>('');

  // Fetch categories on mount
  useEffect(() => {
    if (open) {
      emsClient.getAllLiabilityCategories()
        .then((cats) => {
          setCategories(cats);
          // Auto select first category (Secured Loan) by default in Step 1
          const firstCat = cats.find(c => c.code === 'SECURED_LOAN');
          if (firstCat) setSelectedCategory(firstCat);
        })
        .catch((err) => {
          console.error(err);
          toast.error('Failed to load liability categories');
        });
      resetWizard();
    }
  }, [open]);

  const resetWizard = () => {
    setStep(1);
    setSelectedSubcategory(null);
    setName('');
    setNotes('');
    setOutstandingBalance('');
    setOriginalBorrowed('');
    setInterestRate('');
    setInterestCompounding('MONTHLY');
    setEmiAmount('');
    setMaturityDate('');
    setInitialDate(new Date().toISOString().split('T')[0]);
  };

  const handleSubcategorySelect = (subcategory: LiabilitySubcategory) => {
    setSelectedSubcategory(subcategory);
    setName(subcategory.name);
    setStep(2);
  };

  const validateForm = (): boolean => {
    if (!name.trim()) {
      toast.error('Liability name is required');
      return false;
    }

    const cur = parseFloat(outstandingBalance);
    const orig = parseFloat(originalBorrowed || outstandingBalance);

    if (isNaN(cur) || cur < 0) {
      toast.error('Outstanding balance must be a non-negative number');
      return false;
    }
    if (isNaN(orig) || orig < 0) {
      toast.error('Original borrowed amount must be a non-negative number');
      return false;
    }

    if (selectedSubcategory?.hasInterest) {
      if (!interestRate) {
        toast.error('Interest rate is required for this liability type');
        return false;
      }
      const r = parseFloat(interestRate);
      if (isNaN(r) || r <= 0) {
        toast.error('Interest rate must be a positive number');
        return false;
      }
      if (emiAmount) {
        const emi = parseFloat(emiAmount);
        if (isNaN(emi) || emi <= 0) {
          toast.error('EMI amount must be a positive number');
          return false;
        }
      }
    }

    return true;
  };

  const handleSave = async (addAnother = false) => {
    if (!validateForm()) return;

    const finalOutstanding = parseFloat(outstandingBalance);
    const finalOriginal = parseFloat(originalBorrowed) || finalOutstanding;

    const reqData: LiabilityRequest = {
      categoryId: selectedCategory!.id,
      name: name.trim(),
      subcategoryId: selectedSubcategory?.id || null,
      initialAmount: finalOriginal,
      initialDate: initialDate ? new Date(initialDate).toISOString() : null,
      interestDetails:
        selectedSubcategory?.hasInterest
          ? {
              interestRate: parseFloat(interestRate),
              compounding: interestCompounding as import('@/types/asset').CompoundingFrequency,
              emiAmount: emiAmount ? parseFloat(emiAmount) : null,
              maturityDate:
                selectedSubcategory?.hasMaturity && maturityDate
                  ? new Date(maturityDate).toISOString()
                  : null,
            }
          : null,
      notes: notes.trim() || null,
    };

    try {
      // Create liability - logs a BORROW transaction with finalOriginal amount
      const createdLiability = await emsClient.createLiability(reqData);

      // If outstanding balance is different from original borrowed, log a REVALUE transaction
      if (finalOutstanding !== finalOriginal) {
        await emsClient.addTransactionToLiability(createdLiability.id, {
          transactionType: 'REVALUE',
          amount: finalOutstanding,
          transactionDate: initialDate ? new Date(initialDate).toISOString() : null,
          description: 'Reconciled current outstanding balance',
        });
      }

      toast.success(`Liability "${name}" logged successfully`);

      if (addAnother) {
        setName(selectedSubcategory?.name || '');
        setOutstandingBalance('');
        setOriginalBorrowed('');
        setInterestRate('');
        setInterestCompounding('MONTHLY');
        setEmiAmount('');
        setMaturityDate('');
        setInitialDate(new Date().toISOString().split('T')[0]);
        setNotes('');
        setStep(2);
      } else {
        onSuccess();
        onClose();
      }
    } catch (err: any) {
      console.error(err);
      toast.error(err.message || 'Failed to create liability');
    }
  };

  const getCategoryIcon = (code: string) => {
    switch (code) {
      case 'SECURED_LOAN': return <SecuredIcon />;
      case 'UNSECURED_LOAN': return <UnsecuredIcon />;
      case 'REVOLVING_CREDIT': return <CreditCardIcon />;
      case 'OTHER': return <OtherIcon />;
      default: return <SecuredIcon />;
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
            Add Liability
          </Typography>
          <Typography variant="caption" color="text.secondary">
            Step {step} of 2: {step === 1 ? 'Select liability category' : selectedSubcategory?.name || ''}
          </Typography>
        </Box>
        <IconButton onClick={onClose} size="small" sx={{ color: 'text.secondary' }}>
          <CloseIcon />
        </IconButton>
      </DialogTitle>

      <Divider />

      <DialogContent sx={{ p: 3, minHeight: 400 }}>
        {step === 1 ? (
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3.5 }}>
            <Box>
              <ToggleButtonGroup
                value="LIABILITY"
                exclusive
                size="small"
                sx={{ width: 300 }}
              >
                <ToggleButton value="ASSET" disabled sx={{ width: '50%', fontWeight: 600 }}>Asset</ToggleButton>
                <ToggleButton value="LIABILITY" sx={{ width: '50%', fontWeight: 600 }}>Liability</ToggleButton>
              </ToggleButtonGroup>
            </Box>

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

              <Box sx={{ p: 3 }}>
                <Typography variant="subtitle2" sx={{ mb: 2, color: 'text.secondary', fontWeight: 600, textTransform: 'uppercase', letterSpacing: 0.5 }}>
                  Select Subtype
                </Typography>
                <Grid container spacing={2}>
                  {selectedCategory && (selectedCategory.subcategories || []).map((sub) => (
                    <Grid size={{ xs: 12, sm: 6, md: 4 }} key={sub.id}>
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
                        <CardActionArea onClick={() => handleSubcategorySelect(sub)} sx={{ p: 2.5, textAlign: 'center' }}>
                          <Typography variant="body2" sx={{ fontWeight: 600 }}>
                            {sub.name}
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
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3.5 }}>
            <Card variant="outlined" sx={{ p: 2.5, display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderRadius: 2 }}>
              <Box>
                <Typography variant="caption" color="text.secondary" display="block" sx={{ fontWeight: 600, textTransform: 'uppercase' }}>
                  Select Liability Type
                </Typography>
                <Typography variant="subtitle1" sx={{ fontWeight: 700, color: 'primary.main' }}>
                  {selectedCategory?.name} &gt; {selectedSubcategory?.name || ''}
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

            <Grid container spacing={4}>
              <Grid size={{ xs: 12, md: 7 }}>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2.5 }}>
                  <Typography variant="subtitle2" sx={{ fontWeight: 700, color: 'text.secondary', textTransform: 'uppercase', letterSpacing: 0.5 }}>
                    Liability Details
                  </Typography>

                  <TextField
                    fullWidth
                    required
                    label="Name / Lender"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="e.g. HDFC Home Loan, SBI Card"
                  />

                  <TextField
                    fullWidth
                    required
                    label="Start Date / Disbursal Date"
                    type="date"
                    value={initialDate}
                    onChange={(e) => setInitialDate(e.target.value)}
                    InputLabelProps={{ shrink: true }}
                    helperText="Select the date this borrowing or loan was originally created"
                  />

                  <Box sx={{ display: 'flex', gap: 2 }}>
                    <TextField
                      fullWidth
                      required
                      label="Original Borrowed Amount"
                      type="number"
                      value={originalBorrowed}
                      onChange={(e) => setOriginalBorrowed(e.target.value)}
                      inputProps={{ step: 'any', min: '0' }}
                      InputProps={{
                        startAdornment: <InputAdornment position="start">₹</InputAdornment>,
                      }}
                      placeholder="Principal loan limit"
                    />
                    <TextField
                      fullWidth
                      required
                      label="Current Outstanding Balance"
                      type="number"
                      value={outstandingBalance}
                      onChange={(e) => setOutstandingBalance(e.target.value)}
                      inputProps={{ step: 'any', min: '0' }}
                      InputProps={{
                        startAdornment: <InputAdornment position="start">₹</InputAdornment>,
                      }}
                      placeholder="Statement outstanding"
                    />
                  </Box>

                  {/* Interest Fields */}
                  {selectedSubcategory?.hasInterest && (
                    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2.5 }}>
                      <Box sx={{ display: 'flex', gap: 2 }}>
                        <TextField
                          fullWidth
                          required
                          label="Interest Rate (%)"
                          type="number"
                          value={interestRate}
                          onChange={(e) => setInterestRate(e.target.value)}
                          inputProps={{ step: 'any', min: '0' }}
                          InputProps={{
                            endAdornment: <InputAdornment position="end">%</InputAdornment>,
                          }}
                        />
                        <FormControl fullWidth>
                          <InputLabel id="interest-compounding-label">Compounding Frequency</InputLabel>
                          <Select
                            labelId="interest-compounding-label"
                            value={interestCompounding}
                            label="Compounding Frequency"
                            onChange={(e) => setInterestCompounding(e.target.value)}
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
                        value={emiAmount}
                        onChange={(e) => setEmiAmount(e.target.value)}
                        inputProps={{ step: 'any', min: '0' }}
                        InputProps={{
                          startAdornment: <InputAdornment position="start">₹</InputAdornment>,
                        }}
                        placeholder="Scheduled monthly payment"
                      />
                    </Box>
                  )}

                  {/* Maturity Field */}
                  {selectedSubcategory?.hasMaturity && (
                    <TextField
                      fullWidth
                      label="Closure / Maturity Date"
                      type="date"
                      value={maturityDate}
                      onChange={(e) => setMaturityDate(e.target.value)}
                      InputLabelProps={{ shrink: true }}
                    />
                  )}

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
                        placeholder="Additional loan/credit terms..."
                        value={notes}
                        onChange={(e) => setNotes(e.target.value)}
                      />
                    </AccordionDetails>
                  </Accordion>
                </Box>
              </Grid>

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
                    
                    {(selectedSubcategory?.description || '').split('\n\n').map((paragraph, idx) => (
                      <Typography
                        key={idx}
                        variant="body2"
                        color="text.secondary"
                        sx={{ mb: idx === 0 ? 1.5 : 0 }}
                      >
                        {paragraph}
                      </Typography>
                    ))}
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
