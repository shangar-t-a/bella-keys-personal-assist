import { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import {
  Box,
  Container,
  Typography,
  Card,
  CardContent,
  Tab,
  Tabs,
  TextField,
  Button,
  List,
  ListItem,
  IconButton,
  Divider,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Stack,
  Grid,
} from '@mui/material';
import {
  Add as Plus,
  Edit,
  Check,
  Close,
  Delete as Trash2,
  WarningAmber,
  AccountBalance,
  Category as CategoryIcon,
} from '@mui/icons-material';
import { emsClient } from '@/api/clients/ems-client';
import type { AccountNameResponse, MonthlyCategory } from '@/types/api';
import { toast } from 'sonner';

export default function SettingsPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const activeTabParam = searchParams.get('tab') === 'categories' ? 1 : 0;
  
  const [activeTab, setActiveTab] = useState(activeTabParam);
  const [loading, setLoading] = useState(false);

  // --- Accounts States ---
  const [accounts, setAccounts] = useState<AccountNameResponse[]>([]);
  const [newAccountName, setNewAccountName] = useState('');
  const [editingAccountId, setEditingAccountId] = useState<string | null>(null);
  const [editingAccountName, setEditingAccountName] = useState('');
  const [deleteAccountConfirmId, setDeleteAccountConfirmId] = useState<string | null>(null);

  // --- Categories States ---
  const [categories, setCategories] = useState<MonthlyCategory[]>([]);
  const [newCategoryName, setNewCategoryName] = useState('');
  const [newCategoryL1, setNewCategoryL1] = useState<'spending' | 'saving'>('spending');
  const [deleteCategoryConfirmId, setDeleteCategoryConfirmId] = useState<string | null>(null);

  // Sync tab with URL search parameter
  useEffect(() => {
    setActiveTab(activeTabParam);
  }, [activeTabParam]);

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
    setSearchParams({ tab: newValue === 1 ? 'categories' : 'accounts' });
  };

  // --- Load Data ---
  const loadData = async () => {
    setLoading(true);
    try {
      const [accData, catData] = await Promise.all([
        emsClient.getAllAccounts(),
        emsClient.listMonthlyCategories(),
      ]);
      setAccounts(accData);
      setCategories(catData);
    } catch {
      toast.error('Failed to load settings data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  // ── Account Handlers ────────────────────────────────────────────────────────
  const handleCreateAccount = async () => {
    if (!newAccountName.trim()) {
      toast.error('Account name cannot be empty');
      return;
    }
    setLoading(true);
    try {
      await emsClient.getOrCreateAccount({ accountName: newAccountName.trim() });
      toast.success(`Account "${newAccountName.trim()}" created successfully`);
      setNewAccountName('');
      await loadData();
    } catch (e: any) {
      toast.error(e.message || 'Failed to create account');
    } finally {
      setLoading(false);
    }
  };

  const handleStartEditAccount = (id: string, name: string) => {
    setEditingAccountId(id);
    setEditingAccountName(name);
  };

  const handleCancelEditAccount = () => {
    setEditingAccountId(null);
    setEditingAccountName('');
  };

  const handleSaveEditAccount = async (id: string) => {
    if (!editingAccountName.trim()) {
      toast.error('Account name cannot be empty');
      return;
    }
    setLoading(true);
    try {
      await emsClient.updateAccountName(id, { accountName: editingAccountName.trim() });
      toast.success('Account renamed successfully');
      setEditingAccountId(null);
      await loadData();
    } catch (e: any) {
      toast.error(e.message || 'Failed to update account');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteAccount = async () => {
    if (!deleteAccountConfirmId) return;
    setLoading(true);
    try {
      await emsClient.deleteAccount(deleteAccountConfirmId);
      toast.success('Account and all associated entries deleted successfully');
      setDeleteAccountConfirmId(null);
      await loadData();
    } catch (e: any) {
      toast.error(e.message || 'Failed to delete account');
    } finally {
      setLoading(false);
    }
  };

  // ── Category Handlers ───────────────────────────────────────────────────────
  const handleCreateCategory = async () => {
    if (!newCategoryName.trim()) {
      toast.error('Category name cannot be empty');
      return;
    }
    setLoading(true);
    try {
      await emsClient.addMonthlyCategory({
        name: newCategoryName.trim(),
        category_l1: newCategoryL1,
      });
      toast.success(`Category "${newCategoryName.trim()}" added successfully`);
      setNewCategoryName('');
      await loadData();
    } catch (e: any) {
      toast.error(e.message || 'Failed to create category');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteCategory = async () => {
    if (!deleteCategoryConfirmId) return;
    setLoading(true);
    try {
      await emsClient.deleteMonthlyCategory(deleteCategoryConfirmId);
      toast.success('Category deleted successfully');
      setDeleteCategoryConfirmId(null);
      await loadData();
    } catch (e: any) {
      toast.error(e.message || 'Failed to delete category');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: 'background.default', py: 6 }}>
      <Container maxWidth="md">
        <Typography
          variant="h3"
          sx={{
            fontWeight: 700,
            fontFamily: '"Space Grotesk", sans-serif',
            mb: 1,
            background: 'linear-gradient(135deg, #10b981 0%, #06b6d4 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
          }}
        >
          System Settings
        </Typography>
        <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
          Centralized configuration panel to manage bank accounts and budget categories
        </Typography>

        <Card sx={{ borderRadius: 3, boxShadow: 3 }}>
          <Tabs
            value={activeTab}
            onChange={handleTabChange}
            variant="fullWidth"
            indicatorColor="primary"
            textColor="primary"
            sx={{ borderBottom: 1, borderColor: 'divider' }}
          >
            <Tab icon={<AccountBalance />} iconPosition="start" label="Bank Accounts" />
            <Tab icon={<CategoryIcon />} iconPosition="start" label="Budget Categories" />
          </Tabs>

          <CardContent sx={{ p: 4 }}>
            {/* TAB 1: ACCOUNTS */}
            {activeTab === 0 && (
              <Box>
                <Typography variant="h6" sx={{ fontWeight: 700, mb: 1 }}>
                  Manage Accounts
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 4 }}>
                  Add, rename, or remove your checking, savings, credit cards, or cash accounts.
                </Typography>

                {/* Account Creator Form */}
                <Box sx={{ display: 'flex', gap: 2, mb: 4 }}>
                  <TextField
                    fullWidth
                    size="small"
                    label="Account Name"
                    placeholder="e.g. Chase Bank, Wallet Cash"
                    value={newAccountName}
                    onChange={(e) => setNewAccountName(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') {
                        e.preventDefault();
                        handleCreateAccount();
                      }
                    }}
                    disabled={loading}
                  />
                  <Button
                    variant="contained"
                    startIcon={<Plus />}
                    onClick={handleCreateAccount}
                    disabled={loading || !newAccountName.trim()}
                    sx={{ px: 3, borderRadius: 2 }}
                  >
                    Create
                  </Button>
                </Box>

                <Divider sx={{ my: 3 }} />

                <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 1, color: 'text.secondary' }}>
                  Registered Accounts ({accounts.length})
                </Typography>

                {loading && accounts.length === 0 ? (
                  <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
                    <CircularProgress size={24} />
                  </Box>
                ) : accounts.length === 0 ? (
                  <Typography variant="body2" color="text.secondary" sx={{ py: 3, textAlign: 'center' }}>
                    No accounts registered yet.
                  </Typography>
                ) : (
                  <List sx={{ bgcolor: 'action.hover', borderRadius: 2, p: 0 }}>
                    {accounts.map((account) => {
                      const isEditing = editingAccountId === account.id;
                      return (
                        <ListItem
                          key={account.id}
                          divider
                          secondaryAction={
                            isEditing ? (
                              <Stack direction="row" spacing={0.5}>
                                <IconButton
                                  size="small"
                                  color="success"
                                  onClick={() => handleSaveEditAccount(account.id)}
                                  disabled={loading || !editingAccountName.trim()}
                                >
                                  <Check fontSize="small" />
                                </IconButton>
                                <IconButton
                                  size="small"
                                  color="error"
                                  onClick={handleCancelEditAccount}
                                  disabled={loading}
                                >
                                  <Close fontSize="small" />
                                </IconButton>
                              </Stack>
                            ) : (
                              <Stack direction="row" spacing={0.5}>
                                <IconButton
                                  size="small"
                                  color="primary"
                                  onClick={() => handleStartEditAccount(account.id, account.accountName)}
                                  disabled={loading}
                                >
                                  <Edit fontSize="small" />
                                </IconButton>
                                <IconButton
                                  size="small"
                                  color="error"
                                  onClick={() => setDeleteAccountConfirmId(account.id)}
                                  disabled={loading}
                                >
                                  <Trash2 fontSize="small" />
                                </IconButton>
                              </Stack>
                            )
                          }
                          sx={{ py: 1.5, px: 2 }}
                        >
                          {isEditing ? (
                            <TextField
                              fullWidth
                              size="small"
                              value={editingAccountName}
                              onChange={(e) => setEditingAccountName(e.target.value)}
                              onKeyDown={(e) => {
                                if (e.key === 'Enter') {
                                  e.preventDefault();
                                  handleSaveEditAccount(account.id);
                                }
                              }}
                              autoFocus
                            />
                          ) : (
                            <Typography variant="body1" sx={{ fontWeight: 600 }}>
                              {account.accountName}
                            </Typography>
                          )}
                        </ListItem>
                      );
                    })}
                  </List>
                )}
              </Box>
            )}

            {/* TAB 2: CATEGORIES */}
            {activeTab === 1 && (
              <Box>
                <Typography variant="h6" sx={{ fontWeight: 700, mb: 1 }}>
                  Manage Budget Categories
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 4 }}>
                  Add or remove categories utilized in your monthly budget planner checklists.
                </Typography>

                {/* Category Creator Form */}
                <Box sx={{ display: 'flex', gap: 2, mb: 4, flexDirection: { xs: 'column', sm: 'row' } }}>
                  <TextField
                    fullWidth
                    size="small"
                    label="Category Name"
                    placeholder="e.g. Groceries, Fuel, Insurance"
                    value={newCategoryName}
                    onChange={(e) => setNewCategoryName(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') {
                        e.preventDefault();
                        handleCreateCategory();
                      }
                    }}
                    disabled={loading}
                  />
                  <FormControl size="small" sx={{ minWidth: 140 }}>
                    <InputLabel>Type</InputLabel>
                    <Select
                      value={newCategoryL1}
                      label="Type"
                      onChange={(e) => setNewCategoryL1(e.target.value as any)}
                      disabled={loading}
                    >
                      <MenuItem value="spending">Spending</MenuItem>
                      <MenuItem value="saving">Saving</MenuItem>
                    </Select>
                  </FormControl>
                  <Button
                    variant="contained"
                    startIcon={<Plus />}
                    onClick={handleCreateCategory}
                    disabled={loading || !newCategoryName.trim()}
                    sx={{ px: 3, borderRadius: 2 }}
                  >
                    Add
                  </Button>
                </Box>

                <Divider sx={{ my: 3 }} />

                <Grid container spacing={3}>
                  {/* Spending Category Group */}
                  <Grid size={{ xs: 12, sm: 6 }}>
                    <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 2, color: 'error.main' }}>
                      Spending Categories ({categories.filter(c => c.category_l1 === 'spending').length})
                    </Typography>
                    {loading && categories.length === 0 ? (
                      <CircularProgress size={20} />
                    ) : (
                      <Stack direction="row" spacing={1} useFlexGap flexWrap="wrap">
                        {categories
                          .filter(c => c.category_l1 === 'spending')
                          .map((cat) => (
                            <Chip
                              key={cat.id}
                              label={cat.name}
                              onDelete={() => setDeleteCategoryConfirmId(cat.id)}
                              color="error"
                              variant="outlined"
                              sx={{ fontWeight: 500 }}
                            />
                          ))}
                        {categories.filter(c => c.category_l1 === 'spending').length === 0 && (
                          <Typography variant="body2" color="text.secondary">None configured.</Typography>
                        )}
                      </Stack>
                    )}
                  </Grid>

                  {/* Saving Category Group */}
                  <Grid size={{ xs: 12, sm: 6 }}>
                    <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 2, color: 'success.main' }}>
                      Saving/Investment Categories ({categories.filter(c => c.category_l1 === 'saving').length})
                    </Typography>
                    {loading && categories.length === 0 ? (
                      <CircularProgress size={20} />
                    ) : (
                      <Stack direction="row" spacing={1} useFlexGap flexWrap="wrap">
                        {categories
                          .filter(c => c.category_l1 === 'saving')
                          .map((cat) => (
                            <Chip
                              key={cat.id}
                              label={cat.name}
                              onDelete={() => setDeleteCategoryConfirmId(cat.id)}
                              color="success"
                              variant="outlined"
                              sx={{ fontWeight: 500 }}
                            />
                          ))}
                        {categories.filter(c => c.category_l1 === 'saving').length === 0 && (
                          <Typography variant="body2" color="text.secondary">None configured.</Typography>
                        )}
                      </Stack>
                    )}
                  </Grid>
                </Grid>
              </Box>
            )}
          </CardContent>
        </Card>
      </Container>

      {/* Account Deletion Confirmation Dialog */}
      <Dialog
        open={deleteAccountConfirmId !== null}
        onClose={() => setDeleteAccountConfirmId(null)}
        maxWidth="xs"
      >
        <DialogTitle sx={{ display: 'flex', alignItems: 'center', gap: 1, color: 'error.main', fontWeight: 700 }}>
          <WarningAmber /> Warning: Delete Account?
        </DialogTitle>
        <DialogContent>
          <DialogContentText>
            Deleting this account will permanently delete all associated ledger entries, monthly budget items, and savings envelopes. This action is irreversible.
          </DialogContentText>
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 3 }}>
          <Button onClick={() => setDeleteAccountConfirmId(null)}>Cancel</Button>
          <Button onClick={handleDeleteAccount} variant="contained" color="error">
            Delete Irreversibly
          </Button>
        </DialogActions>
      </Dialog>

      {/* Category Deletion Confirmation Dialog */}
      <Dialog
        open={deleteCategoryConfirmId !== null}
        onClose={() => setDeleteCategoryConfirmId(null)}
        maxWidth="xs"
      >
        <DialogTitle sx={{ display: 'flex', alignItems: 'center', gap: 1, color: 'error.main', fontWeight: 700 }}>
          <WarningAmber /> Delete Budget Category?
        </DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to delete this category? Any existing monthly budget items mapped to it will lose their subcategory association.
          </DialogContentText>
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 3 }}>
          <Button onClick={() => setDeleteCategoryConfirmId(null)}>Cancel</Button>
          <Button onClick={handleDeleteCategory} variant="contained" color="error">
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
