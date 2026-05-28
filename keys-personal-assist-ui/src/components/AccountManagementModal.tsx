import { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  IconButton,
  List,
  ListItem,
  Typography,
  Box,
  Divider,
  CircularProgress,
  DialogContentText,
} from '@mui/material';
import {
  Delete as Trash2,
  Edit,
  Check,
  Close,
  Add as Plus,
  WarningAmber,
} from '@mui/icons-material';
import { emsClient } from '@/api/clients/ems-client';
import type { AccountNameResponse } from '@/types/api';
import { toast } from 'sonner';

interface AccountManagementModalProps {
  open: boolean;
  onClose: (hasChanges: boolean) => void;
}

export default function AccountManagementModal({ open, onClose }: AccountManagementModalProps) {
  const [accounts, setAccounts] = useState<AccountNameResponse[]>([]);
  const [loading, setLoading] = useState(false);
  const [newAccountName, setNewAccountName] = useState('');
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editingName, setEditingName] = useState('');
  
  // Deletion Confirmation States
  const [deleteConfirmId, setDeleteConfirmId] = useState<string | null>(null);
  const [hasChanges, setHasChanges] = useState(false);

  const fetchAccounts = async () => {
    setLoading(true);
    try {
      const data = await emsClient.getAllAccounts();
      setAccounts(data);
    } catch {
      toast.error('Failed to load accounts');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (open) {
      fetchAccounts();
      setHasChanges(false);
      setNewAccountName('');
      setEditingId(null);
      setDeleteConfirmId(null);
    }
  }, [open]);

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
      setHasChanges(true);
      await fetchAccounts();
    } catch (e: any) {
      toast.error(e.message || 'Failed to create account');
    } finally {
      setLoading(false);
    }
  };

  const handleStartEdit = (id: string, currentName: string) => {
    setEditingId(id);
    setEditingName(currentName);
  };

  const handleCancelEdit = () => {
    setEditingId(null);
    setEditingName('');
  };

  const handleSaveEdit = async (id: string) => {
    if (!editingName.trim()) {
      toast.error('Account name cannot be empty');
      return;
    }
    setLoading(true);
    try {
      await emsClient.updateAccountName(id, { accountName: editingName.trim() });
      toast.success('Account renamed successfully');
      setEditingId(null);
      setHasChanges(true);
      await fetchAccounts();
    } catch (e: any) {
      toast.error(e.message || 'Failed to update account');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteAccount = async () => {
    if (!deleteConfirmId) return;
    setLoading(true);
    try {
      await emsClient.deleteAccount(deleteConfirmId);
      toast.success('Account and all associated entries deleted successfully');
      setDeleteConfirmId(null);
      setHasChanges(true);
      await fetchAccounts();
    } catch (e: any) {
      toast.error(e.message || 'Failed to delete account');
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Dialog open={open} onClose={() => onClose(hasChanges)} maxWidth="sm" fullWidth>
        <DialogTitle sx={{ fontWeight: 700, fontFamily: '"Space Grotesk", sans-serif' }}>
          Manage Bank Accounts
        </DialogTitle>
        <DialogContent dividers>
          {/* New Account Creation Form */}
          <Box sx={{ display: 'flex', gap: 2, mb: 3, mt: 1 }}>
            <TextField
              fullWidth
              size="small"
              label="New Account Name"
              placeholder="e.g. Chase Bank, HDFC Savings, Cash Wallet"
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
              sx={{ px: 3 }}
            >
              Add
            </Button>
          </Box>

          <Divider sx={{ my: 2 }} />

          <Typography variant="subtitle2" sx={{ fontWeight: 700, mb: 1, color: 'text.secondary' }}>
            Existing Accounts ({accounts.length})
          </Typography>

          {loading && accounts.length === 0 ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
              <CircularProgress size={24} />
            </Box>
          ) : accounts.length === 0 ? (
            <Typography variant="body2" color="text.secondary" sx={{ py: 3, textAlign: 'center' }}>
              No accounts registered. Create one above to get started.
            </Typography>
          ) : (
            <List sx={{ width: '100%', bgcolor: 'background.paper', borderRadius: 1 }}>
              {accounts.map((account) => {
                const isEditing = editingId === account.id;
                return (
                  <ListItem
                    key={account.id}
                    divider
                    secondaryAction={
                      isEditing ? (
                        <Box sx={{ display: 'flex', gap: 0.5 }}>
                          <IconButton
                            edge="end"
                            size="small"
                            color="success"
                            onClick={() => handleSaveEdit(account.id)}
                            disabled={loading || !editingName.trim()}
                          >
                            <Check fontSize="small" />
                          </IconButton>
                          <IconButton
                            edge="end"
                            size="small"
                            color="error"
                            onClick={handleCancelEdit}
                            disabled={loading}
                          >
                            <Close fontSize="small" />
                          </IconButton>
                        </Box>
                      ) : (
                        <Box sx={{ display: 'flex', gap: 0.5 }}>
                          <IconButton
                            edge="end"
                            size="small"
                            color="primary"
                            onClick={() => handleStartEdit(account.id, account.accountName)}
                            disabled={loading}
                          >
                            <Edit fontSize="small" />
                          </IconButton>
                          <IconButton
                            edge="end"
                            size="small"
                            color="error"
                            onClick={() => setDeleteConfirmId(account.id)}
                            disabled={loading}
                          >
                            <Trash2 fontSize="small" />
                          </IconButton>
                        </Box>
                      )
                    }
                    sx={{ py: 1.5 }}
                  >
                    {isEditing ? (
                      <TextField
                        fullWidth
                        size="small"
                        value={editingName}
                        onChange={(e) => setEditingName(e.target.value)}
                        onKeyDown={(e) => {
                          if (e.key === 'Enter') {
                            e.preventDefault();
                            handleSaveEdit(account.id);
                          }
                        }}
                        autoFocus
                      />
                    ) : (
                      <Typography variant="body1" sx={{ fontWeight: 500 }}>
                        {account.accountName}
                      </Typography>
                    )}
                  </ListItem>
                );
              })}
            </List>
          )}
        </DialogContent>
        <DialogActions sx={{ px: 3, py: 2 }}>
          <Button onClick={() => onClose(hasChanges)} variant="outlined">
            Close
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog
        open={deleteConfirmId !== null}
        onClose={() => setDeleteConfirmId(null)}
        maxWidth="xs"
      >
        <DialogTitle sx={{ display: 'flex', alignItems: 'center', gap: 1, color: 'error.main', fontWeight: 700 }}>
          <WarningAmber /> Warning: Delete Account?
        </DialogTitle>
        <DialogContent>
          <DialogContentText>
            Deleting this account will permanently delete all associated ledger entries, monthly expenses, and savings buckets. This action is irreversible.
          </DialogContentText>
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 3 }}>
          <Button onClick={() => setDeleteConfirmId(null)}>Cancel</Button>
          <Button onClick={handleDeleteAccount} variant="contained" color="error">
            Delete Irreversibly
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
}
