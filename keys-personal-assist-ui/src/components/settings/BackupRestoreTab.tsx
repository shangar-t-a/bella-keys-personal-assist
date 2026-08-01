import { useState, useEffect, useRef } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Button,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  IconButton,
  CircularProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
  Alert,
  Tooltip,
  useMediaQuery,
  useTheme,
  TextField,
} from '@mui/material';
import {
  CloudDownload,
  FolderZip,
  Restore,
  Delete as Trash2,
  UploadFile,
  Download,
  Shield,
  WarningAmber,
  CheckCircle,
  Laptop,
  FolderOpen,
} from '@mui/icons-material';
import { emsClient } from '@/api/clients/ems-client';
import type { BackupConfigResponse, BackupMetadata } from '@/types/api';
import { toast } from 'sonner';

export default function BackupRestoreTab() {
  const theme = useTheme();
  const isDesktop = useMediaQuery(theme.breakpoints.up('sm'));

  const [loading, setLoading] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [restoring, setRestoring] = useState(false);
  const [snapshots, setSnapshots] = useState<BackupMetadata[]>([]);
  const [backupConfig, setBackupConfig] = useState<BackupConfigResponse | null>(null);

  // Dialog States
  const [confirmRestoreFilename, setConfirmRestoreFilename] = useState<string | null>(null);
  const [confirmDeleteFilename, setConfirmDeleteFilename] = useState<string | null>(null);
  const [changeFolderOpen, setChangeFolderOpen] = useState(false);
  const [customFolderPath, setCustomFolderPath] = useState('');
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [uploadedMetadata, setUploadedMetadata] = useState<Record<string, any> | null>(null);

  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const loadData = async () => {
    setLoading(true);
    try {
      const [snapData, cfgData] = await Promise.all([
        emsClient.listBackups(),
        emsClient.getBackupConfig().catch(() => null),
      ]);
      setSnapshots(snapData);
      if (cfgData) {
        setBackupConfig(cfgData);
        setCustomFolderPath(cfgData.backup_dir);
      }
    } catch {
      toast.error('Failed to load backup snapshots');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleChangeFolder = async () => {
    // If running in Desktop Electron environment, use native OS folder picker dialog
    if (window.electronAPI?.selectDirectory) {
      try {
        const selected = await window.electronAPI.selectDirectory();
        if (selected) {
          const updated = await emsClient.updateBackupConfig(selected);
          setBackupConfig(updated);
          setCustomFolderPath(updated.backup_dir);
          toast.success(`Backup folder updated to: ${updated.absolute_backup_dir}`);
          await loadData();
        }
      } catch (e: any) {
        toast.error(e.message || 'Failed to select directory');
      }
      return;
    }

    // Otherwise, open input dialog for web mode
    setCustomFolderPath(backupConfig?.backup_dir || '');
    setChangeFolderOpen(true);
  };

  const handleSaveCustomFolder = async () => {
    if (!customFolderPath.trim()) return;
    try {
      const updated = await emsClient.updateBackupConfig(customFolderPath.trim());
      setBackupConfig(updated);
      setChangeFolderOpen(false);
      toast.success(`Backup folder updated to: ${updated.absolute_backup_dir}`);
      await loadData();
    } catch (e: any) {
      toast.error(e.message || 'Failed to update backup folder location');
    }
  };

  const handleExportBackup = async () => {
    setExporting(true);
    try {
      const res = await emsClient.exportBackup();
      toast.success(`Backup exported: ${res.filename} (${res.formatted_size})`);
      await loadData();
    } catch (e: any) {
      toast.error(e.message || 'Failed to export backup');
    } finally {
      setExporting(false);
    }
  };

  const handleRestoreLatest = async () => {
    if (snapshots.length === 0) {
      toast.error('No backup snapshots available');
      return;
    }
    setConfirmRestoreFilename(snapshots[0].filename);
  };

  const handleConfirmRestoreSnapshot = async () => {
    if (!confirmRestoreFilename) return;
    const targetFile = confirmRestoreFilename;
    setConfirmRestoreFilename(null);
    setRestoring(true);
    try {
      const res = await emsClient.restoreSnapshot(targetFile);
      toast.success(`Database restored successfully! (${res.restored_records} records restored)`);
      await loadData();
    } catch (e: any) {
      toast.error(e.message || 'Failed to restore snapshot');
    } finally {
      setRestoring(false);
    }
  };

  const handleDeleteSnapshot = async () => {
    if (!confirmDeleteFilename) return;
    const targetFile = confirmDeleteFilename;
    setConfirmDeleteFilename(null);
    try {
      await emsClient.deleteBackup(targetFile);
      toast.success(`Deleted snapshot: ${targetFile}`);
      await loadData();
    } catch (e: any) {
      toast.error(e.message || 'Failed to delete snapshot');
    }
  };

  const handleFileDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      processSelectedFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      processSelectedFile(e.target.files[0]);
    }
  };

  const processSelectedFile = (file: File) => {
    if (!file.name.endsWith('.json')) {
      toast.error('Please select a valid JSON backup file.');
      return;
    }

    const reader = new FileReader();
    reader.onload = (event) => {
      try {
        const json = JSON.parse(event.target?.result as string);
        if (!json || typeof json !== 'object' || !json.tables) {
          toast.error('Invalid backup file structure: missing tables envelope.');
          return;
        }
        setUploadedFile(file);
        setUploadedMetadata(json.metadata || {});
      } catch {
        toast.error('Selected file is not valid JSON.');
      }
    };
    reader.readAsText(file);
  };

  const handleConfirmUploadRestore = async () => {
    if (!uploadedFile) return;
    const fileToRestore = uploadedFile;
    setUploadedFile(null);
    setUploadedMetadata(null);
    setRestoring(true);

    try {
      const res = await emsClient.uploadAndRestoreBackup(fileToRestore);
      toast.success(`Restored from uploaded file! (${res.restored_records} records restored)`);
      await loadData();
    } catch (e: any) {
      toast.error(e.message || 'Failed to restore uploaded file');
    } finally {
      setRestoring(false);
    }
  };

  const latestSnapshot = snapshots.length > 0 ? snapshots[0] : null;

  return (
    <Stack spacing={3}>
      {!isDesktop && (
        <Alert severity="info" icon={<Laptop />} sx={{ borderRadius: 2 }}>
          Backup & Restore operations are optimized for Desktop resolution. Full folder management is active.
        </Alert>
      )}

      {/* Card 1: Local Backup Folder Summary */}
      <Card variant="outlined" sx={{ borderRadius: 2, borderColor: 'divider', boxShadow: 'none' }}>
        <CardContent sx={{ p: 3 }}>
          <Stack direction={{ xs: 'column', sm: 'row' }} justifyContent="space-between" alignItems="flex-start" spacing={2}>
            <Box sx={{ flex: 1 }}>
              <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 0.5 }}>
                <FolderZip color="primary" />
                <Typography variant="h6" sx={{ fontWeight: 700, fontFamily: '"Space Grotesk", sans-serif' }}>
                  Local Folder Backups
                </Typography>
                <Chip label="5-File Quota" size="small" color="default" variant="outlined" sx={{ fontWeight: 600, height: 22 }} />
              </Stack>

              <Stack direction="row" alignItems="center" spacing={1} sx={{ mt: 1, mb: 1, flexWrap: 'wrap' }}>
                <Typography variant="body2" color="text.secondary">
                  Target Backup Location:
                </Typography>
                <Box
                  component="code"
                  sx={{
                    bgcolor: 'action.hover',
                    px: 1,
                    py: 0.3,
                    borderRadius: 1,
                    fontSize: '0.82rem',
                    fontWeight: 600,
                    wordBreak: 'break-all',
                  }}
                >
                  {backupConfig?.absolute_backup_dir || './backups/'}
                </Box>
                <Button
                  size="small"
                  variant="outlined"
                  startIcon={<FolderOpen fontSize="small" />}
                  onClick={handleChangeFolder}
                  sx={{ py: 0.2, px: 1.2, height: 26, fontSize: '0.75rem', fontWeight: 600 }}
                >
                  Change Folder
                </Button>
              </Stack>

              {latestSnapshot ? (
                <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 0.5, fontWeight: 500 }}>
                  Last Backup: <strong>{new Date(latestSnapshot.created_at).toLocaleString()}</strong> ({latestSnapshot.formatted_size})
                </Typography>
              ) : (
                <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 0.5, fontWeight: 500 }}>
                  No local backup files created yet.
                </Typography>
              )}
            </Box>

            <Stack direction="row" spacing={1.5} sx={{ width: { xs: '100%', sm: 'auto' } }}>
              <Button
                variant="contained"
                startIcon={exporting ? <CircularProgress size={18} color="inherit" /> : <CloudDownload />}
                onClick={handleExportBackup}
                disabled={exporting || restoring}
                fullWidth={!isDesktop}
              >
                Export Backup File
              </Button>

              <Button
                variant="outlined"
                color="secondary"
                startIcon={restoring ? <CircularProgress size={18} color="inherit" /> : <Restore />}
                onClick={handleRestoreLatest}
                disabled={exporting || restoring || snapshots.length === 0}
                fullWidth={!isDesktop}
              >
                Restore Latest
              </Button>
            </Stack>
          </Stack>

          <Box sx={{ mt: 2, pt: 2, borderTop: 1, borderColor: 'divider', display: 'flex', alignItems: 'center', gap: 1 }}>
            <Shield fontSize="small" color="success" />
            <Typography variant="caption" color="text.secondary">
              <strong>Pre-Restore Safety Guarantee:</strong> Before restoring any backup file, a pre-restore snapshot is automatically saved to disk.
            </Typography>
          </Box>
        </CardContent>
      </Card>

      {/* Card 2: Local Folder Snapshot Stream */}
      <Card variant="outlined" sx={{ borderRadius: 2, borderColor: 'divider', boxShadow: 'none' }}>
        <CardContent sx={{ p: 3 }}>
          <Typography variant="h6" sx={{ fontWeight: 700, fontFamily: '"Space Grotesk", sans-serif', mb: 2 }}>
            Local Snapshot Stream ({snapshots.length})
          </Typography>

          {loading && snapshots.length === 0 ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
              <CircularProgress size={24} />
            </Box>
          ) : snapshots.length === 0 ? (
            <Typography variant="body2" color="text.secondary" sx={{ py: 3, textAlign: 'center' }}>
              No snapshots found in backup folder. Click "Export Backup File" to create one.
            </Typography>
          ) : (
            <TableContainer>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell sx={{ fontWeight: 700, fontSize: '0.78rem' }}>SNAPSHOT FILE</TableCell>
                    <TableCell sx={{ fontWeight: 700, fontSize: '0.78rem' }}>CREATED AT</TableCell>
                    <TableCell sx={{ fontWeight: 700, fontSize: '0.78rem' }}>TYPE</TableCell>
                    <TableCell sx={{ fontWeight: 700, fontSize: '0.78rem' }}>SIZE</TableCell>
                    <TableCell sx={{ fontWeight: 700, fontSize: '0.78rem', textAlign: 'right' }}>ACTIONS</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {snapshots.map((snap) => {
                    const isPreRestore = snap.type === 'pre_restore';
                    return (
                      <TableRow key={snap.filename} hover sx={{ '&:nth-of-type(even)': { bgcolor: 'action.hover' } }}>
                        <TableCell sx={{ fontWeight: 600, fontFamily: 'monospace', fontSize: '0.82rem' }}>
                          {snap.filename}
                        </TableCell>
                        <TableCell variant="body">
                          {new Date(snap.created_at).toLocaleString()}
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={isPreRestore ? 'Safety Net' : 'Manual Export'}
                            color={isPreRestore ? 'warning' : 'primary'}
                            size="small"
                            variant="outlined"
                            sx={{ fontWeight: 600, height: 20, fontSize: '0.68rem' }}
                          />
                        </TableCell>
                        <TableCell variant="body">{snap.formatted_size}</TableCell>
                        <TableCell align="right">
                          <Stack direction="row" spacing={0.5} justifyContent="flex-end">
                            <Tooltip title="Restore this snapshot">
                              <IconButton
                                size="small"
                                color="primary"
                                onClick={() => setConfirmRestoreFilename(snap.filename)}
                                disabled={restoring || exporting}
                              >
                                <Restore fontSize="small" />
                              </IconButton>
                            </Tooltip>
                            <Tooltip title="Download snapshot JSON">
                              <IconButton
                                size="small"
                                color="info"
                                component="a"
                                href={emsClient.getBackupDownloadUrl(snap.filename)}
                                download={snap.filename}
                              >
                                <Download fontSize="small" />
                              </IconButton>
                            </Tooltip>
                            <Tooltip title="Delete snapshot">
                              <IconButton
                                size="small"
                                color="error"
                                onClick={() => setConfirmDeleteFilename(snap.filename)}
                                disabled={restoring || exporting}
                              >
                                <Trash2 fontSize="small" />
                              </IconButton>
                            </Tooltip>
                          </Stack>
                        </TableCell>
                      </TableRow>
                    );
                  })}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </CardContent>
      </Card>

      {/* Card 3: External Backup File Upload Restore */}
      <Card variant="outlined" sx={{ borderRadius: 2, borderColor: 'divider', boxShadow: 'none' }}>
        <CardContent sx={{ p: 3 }}>
          <Typography variant="h6" sx={{ fontWeight: 700, fontFamily: '"Space Grotesk", sans-serif', mb: 1 }}>
            Restore External Backup File
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            Drag and drop an external JSON backup file or choose a file from your computer to inspect and restore.
          </Typography>

          <Box
            onDragOver={(e) => e.preventDefault()}
            onDrop={handleFileDrop}
            onClick={() => fileInputRef.current?.click()}
            sx={{
              border: '2px dashed',
              borderColor: 'primary.main',
              borderRadius: 2,
              p: 4,
              textAlign: 'center',
              cursor: 'pointer',
              bgcolor: 'action.hover',
              transition: 'background-color 0.2s',
              '&:hover': { bgcolor: 'action.selected' },
            }}
          >
            <input
              type="file"
              accept=".json"
              ref={fileInputRef}
              onChange={handleFileInputChange}
              style={{ display: 'none' }}
            />
            <UploadFile sx={{ fontSize: 40, color: 'primary.main', mb: 1 }} />
            <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
              Click or drag a `.json` backup file here to inspect & restore
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Only valid `.json` export envelopes from Expense Manager are supported.
            </Typography>
          </Box>
        </CardContent>
      </Card>

      {/* Dialog 1: Change Backup Folder */}
      <Dialog open={changeFolderOpen} onClose={() => setChangeFolderOpen(false)} maxWidth="xs" fullWidth>
        <DialogTitle sx={{ fontWeight: 700 }}>Configure Backup Storage Folder</DialogTitle>
        <DialogContent>
          <DialogContentText sx={{ mb: 2 }}>
            Specify the folder path on your computer where database backups should be stored:
          </DialogContentText>
          <TextField
            fullWidth
            size="small"
            label="Folder Path"
            value={customFolderPath}
            onChange={(e) => setCustomFolderPath(e.target.value)}
            placeholder="e.g. C:\Users\Username\BellaKeys\backups"
          />
        </DialogContent>
        <DialogActions sx={{ p: 2 }}>
          <Button onClick={() => setChangeFolderOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleSaveCustomFolder}>
            Save Location
          </Button>
        </DialogActions>
      </Dialog>

      {/* Dialog 2: Snapshot Restore Confirmation */}
      <Dialog open={confirmRestoreFilename !== null} onClose={() => setConfirmRestoreFilename(null)} maxWidth="xs">
        <DialogTitle sx={{ display: 'flex', alignItems: 'center', gap: 1, color: 'warning.main', fontWeight: 700 }}>
          <WarningAmber /> Confirm Database Restore
        </DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to restore database state from snapshot <strong>{confirmRestoreFilename}</strong>?
            <br /><br />
            Current database tables will be cleared and replaced with this snapshot data. A safety snapshot will be created automatically before restoring.
          </DialogContentText>
        </DialogContent>
        <DialogActions sx={{ p: 2 }}>
          <Button onClick={() => setConfirmRestoreFilename(null)}>Cancel</Button>
          <Button variant="contained" color="warning" onClick={handleConfirmRestoreSnapshot} disabled={restoring}>
            {restoring ? <CircularProgress size={18} color="inherit" /> : 'Confirm & Restore'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Dialog 3: Delete Snapshot Confirmation */}
      <Dialog open={confirmDeleteFilename !== null} onClose={() => setConfirmDeleteFilename(null)} maxWidth="xs">
        <DialogTitle sx={{ display: 'flex', alignItems: 'center', gap: 1, color: 'error.main', fontWeight: 700 }}>
          <WarningAmber /> Delete Snapshot File
        </DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to permanently delete snapshot file <strong>{confirmDeleteFilename}</strong>?
          </DialogContentText>
        </DialogContent>
        <DialogActions sx={{ p: 2 }}>
          <Button onClick={() => setConfirmDeleteFilename(null)}>Cancel</Button>
          <Button variant="contained" color="error" onClick={handleDeleteSnapshot}>
            Delete File
          </Button>
        </DialogActions>
      </Dialog>

      {/* Dialog 4: Uploaded External File Inspection Dialog */}
      <Dialog open={uploadedFile !== null} onClose={() => setUploadedFile(null)} maxWidth="sm" fullWidth>
        <DialogTitle sx={{ display: 'flex', alignItems: 'center', gap: 1, color: 'primary.main', fontWeight: 700 }}>
          <CheckCircle color="success" /> External Backup File Inspected
        </DialogTitle>
        <DialogContent>
          <DialogContentText sx={{ mb: 2 }}>
            Selected File: <strong>{uploadedFile?.name}</strong> ({(uploadedFile?.size ? (uploadedFile.size / 1024).toFixed(1) : 0)} KB)
          </DialogContentText>

          {uploadedMetadata && (
            <Card variant="outlined" sx={{ p: 2, bgcolor: 'action.hover', mb: 2 }}>
              <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 700, display: 'block', mb: 1, textTransform: 'uppercase' }}>
                Backup File Payload Inspection
              </Typography>
              <Typography variant="body2">
                Exported At: <strong>{uploadedMetadata.exported_at ? new Date(uploadedMetadata.exported_at).toLocaleString() : 'N/A'}</strong>
              </Typography>
              <Typography variant="body2">
                Total Records: <strong>{uploadedMetadata.total_records || 'Unknown'}</strong>
              </Typography>
            </Card>
          )}

          <Alert severity="warning">
            Restoring from this file will replace current database state. An automatic safety snapshot will be created first.
          </Alert>
        </DialogContent>
        <DialogActions sx={{ p: 2 }}>
          <Button onClick={() => setUploadedFile(null)}>Cancel</Button>
          <Button variant="contained" color="warning" onClick={handleConfirmUploadRestore} disabled={restoring}>
            {restoring ? <CircularProgress size={18} color="inherit" /> : 'Confirm & Restore Upload'}
          </Button>
        </DialogActions>
      </Dialog>
    </Stack>
  );
}
