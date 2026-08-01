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
} from '@mui/icons-material';
import { emsClient } from '@/api/clients/ems-client';
import type { BackupMetadata } from '@/types/api';
import { toast } from 'sonner';

export default function BackupRestoreTab() {
  const theme = useTheme();
  const isDesktop = useMediaQuery(theme.breakpoints.up('sm'));

  const [loading, setLoading] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [restoring, setRestoring] = useState(false);
  const [snapshots, setSnapshots] = useState<BackupMetadata[]>([]);

  // Dialog States
  const [confirmRestoreFilename, setConfirmRestoreFilename] = useState<string | null>(null);
  const [confirmDeleteFilename, setConfirmDeleteFilename] = useState<string | null>(null);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [uploadedMetadata, setUploadedMetadata] = useState<Record<string, any> | null>(null);

  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const loadSnapshots = async () => {
    setLoading(true);
    try {
      const data = await emsClient.listBackups();
      setSnapshots(data);
    } catch {
      toast.error('Failed to load backup snapshots');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSnapshots();
  }, []);

  const handleExportBackup = async () => {
    setExporting(true);
    try {
      const res = await emsClient.exportBackup();
      toast.success(`Backup exported: ${res.filename} (${res.formatted_size})`);
      await loadSnapshots();
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
      toast.success(`Database restored successfully! (${res.restored_records} records)`);
      await loadSnapshots();
    } catch (e: any) {
      toast.error(e.message || 'Restore failed. Original data preserved.');
    } finally {
      setRestoring(false);
    }
  };

  const handleDeleteSnapshot = async () => {
    if (!confirmDeleteFilename) return;
    const targetFile = confirmDeleteFilename;
    setConfirmDeleteFilename(null);
    setLoading(true);

    try {
      await emsClient.deleteBackup(targetFile);
      toast.success(`Snapshot ${targetFile} deleted`);
      await loadSnapshots();
    } catch (e: any) {
      toast.error(e.message || 'Failed to delete snapshot');
    } finally {
      setLoading(false);
    }
  };

  const handleFileSelect = (file: File) => {
    if (!file.name.endsWith('.json')) {
      toast.error('Please select a valid .json backup file');
      return;
    }
    setUploadedFile(file);

    // Pre-flight inspection
    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const json = JSON.parse(e.target?.result as string);
        if (json && json.metadata) {
          setUploadedMetadata(json.metadata);
        } else {
          setUploadedMetadata({ total_records: 'Unknown', version: '1.0' });
        }
      } catch {
        setUploadedMetadata(null);
      }
    };
    reader.readAsText(file);
  };

  const handleConfirmUploadedRestore = async () => {
    if (!uploadedFile) return;
    const fileToRestore = uploadedFile;
    setUploadedFile(null);
    setUploadedMetadata(null);
    setRestoring(true);

    try {
      const res = await emsClient.uploadAndRestoreBackup(fileToRestore);
      toast.success(`External file restored successfully! (${res.restored_records} records)`);
      await loadSnapshots();
    } catch (e: any) {
      toast.error(e.message || 'External restore failed. Original data preserved.');
    } finally {
      setRestoring(false);
    }
  };

  const latestSnapshot = snapshots.length > 0 ? snapshots[0] : null;

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
      {/* Mobile Fallback Warning */}
      {!isDesktop && (
        <Alert severity="info" icon={<Laptop />} sx={{ borderRadius: 2 }}>
          Backup & Restore operations are optimized for Desktop resolution. Full folder management is active.
        </Alert>
      )}

      {/* Card 1: Local Backup Folder Summary */}
      <Card variant="outlined" sx={{ borderRadius: 2, borderColor: 'divider', boxShadow: 'none' }}>
        <CardContent sx={{ p: 3 }}>
          <Stack direction={{ xs: 'column', sm: 'row' }} justifyContent="space-between" alignItems="flex-start" spacing={2}>
            <Box>
              <Stack direction="row" alignItems="center" spacing={1} sx={{ mb: 0.5 }}>
                <FolderZip color="primary" />
                <Typography variant="h6" sx={{ fontWeight: 700, fontFamily: '"Space Grotesk", sans-serif' }}>
                  Local Folder Backups
                </Typography>
                <Chip label="5-File Quota" size="small" color="default" variant="outlined" sx={{ fontWeight: 600, height: 22 }} />
              </Stack>

              <Typography variant="body2" color="text.secondary">
                Storage Directory: <Box component="code" sx={{ bgcolor: 'action.hover', px: 1, py: 0.2, borderRadius: 1 }}>./backups/</Box> (Local Disk)
              </Typography>

              {latestSnapshot ? (
                <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 1, fontWeight: 500 }}>
                  Last Backup: <strong>{new Date(latestSnapshot.created_at).toLocaleString()}</strong> ({latestSnapshot.formatted_size})
                </Typography>
              ) : (
                <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 1, fontWeight: 500 }}>
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
              No snapshots found in local ./backups/ folder. Click "Export Backup File" to create one.
            </Typography>
          ) : (
            <TableContainer sx={{ borderRadius: 1, border: 1, borderColor: 'divider' }}>
              <Table size="small">
                <TableHead sx={{ bgcolor: (theme) => theme.palette.mode === 'dark' ? 'rgba(30, 41, 59, 0.5)' : '#f8fafc' }}>
                  <TableRow>
                    <TableCell sx={{ fontWeight: 700, fontSize: '0.78rem' }}>FILE NAME</TableCell>
                    <TableCell sx={{ fontWeight: 700, fontSize: '0.78rem' }}>TIMESTAMP</TableCell>
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
                                disabled={restoring}
                              >
                                <Restore fontSize="small" />
                              </IconButton>
                            </Tooltip>

                            <Tooltip title="Download file to computer">
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

                            <Tooltip title="Delete snapshot file">
                              <IconButton
                                size="small"
                                color="error"
                                onClick={() => setConfirmDeleteFilename(snap.filename)}
                                disabled={restoring}
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

      {/* Card 3: External File Upload Zone */}
      <Card variant="outlined" sx={{ borderRadius: 2, borderColor: 'divider', boxShadow: 'none' }}>
        <CardContent sx={{ p: 3 }}>
          <Typography variant="h6" sx={{ fontWeight: 700, fontFamily: '"Space Grotesk", sans-serif', mb: 1 }}>
            Restore from External Backup File
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Upload a timestamped <Box component="code">.json</Box> backup file from an external disk or another machine.
          </Typography>

          <input
            type="file"
            accept=".json"
            ref={fileInputRef}
            style={{ display: 'none' }}
            onChange={(e) => {
              if (e.target.files && e.target.files[0]) {
                handleFileSelect(e.target.files[0]);
              }
            }}
          />

          <Box
            onClick={() => fileInputRef.current?.click()}
            sx={{
              border: '2px dashed',
              borderColor: 'divider',
              borderRadius: 2,
              p: 4,
              textAlign: 'center',
              cursor: 'pointer',
              bgcolor: (theme) => theme.palette.mode === 'dark' ? 'rgba(30, 41, 59, 0.2)' : '#fafafa',
              transition: 'all 0.2s',
              '&:hover': {
                borderColor: 'primary.main',
                bgcolor: (theme) => theme.palette.mode === 'dark' ? 'rgba(30, 41, 59, 0.4)' : '#f0f7ff',
              },
            }}
          >
            <UploadFile color="primary" sx={{ fontSize: 40, mb: 1 }} />
            <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
              Click to select or Drag & Drop a .json backup file
            </Typography>
            <Typography variant="caption" color="text.secondary">
              Pre-flight data inspection will be performed before restoring.
            </Typography>
          </Box>
        </CardContent>
      </Card>

      {/* Dialog: Confirm Snapshot Restore */}
      <Dialog
        open={confirmRestoreFilename !== null}
        onClose={() => setConfirmRestoreFilename(null)}
        maxWidth="xs"
      >
        <DialogTitle sx={{ display: 'flex', alignItems: 'center', gap: 1, color: 'warning.main', fontWeight: 700 }}>
          <WarningAmber /> Confirm Restore?
        </DialogTitle>
        <DialogContent>
          <DialogContentText>
            Are you sure you want to restore data from <strong>{confirmRestoreFilename}</strong>?
          </DialogContentText>
          <Alert severity="info" sx={{ mt: 2 }}>
            Current database records will be replaced. A pre-restore safety snapshot will automatically be created before proceeding.
          </Alert>
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 3 }}>
          <Button onClick={() => setConfirmRestoreFilename(null)}>Cancel</Button>
          <Button onClick={handleConfirmRestoreSnapshot} variant="contained" color="warning">
            Restore Snapshot
          </Button>
        </DialogActions>
      </Dialog>

      {/* Dialog: Confirm Snapshot Delete */}
      <Dialog
        open={confirmDeleteFilename !== null}
        onClose={() => setConfirmDeleteFilename(null)}
        maxWidth="xs"
      >
        <DialogTitle sx={{ display: 'flex', alignItems: 'center', gap: 1, color: 'error.main', fontWeight: 700 }}>
          <WarningAmber /> Delete Snapshot File?
        </DialogTitle>
        <DialogContent>
          <DialogContentText>
            Delete <strong>{confirmDeleteFilename}</strong> permanently from local storage?
          </DialogContentText>
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 3 }}>
          <Button onClick={() => setConfirmDeleteFilename(null)}>Cancel</Button>
          <Button onClick={handleDeleteSnapshot} variant="contained" color="error">
            Delete File
          </Button>
        </DialogActions>
      </Dialog>

      {/* Dialog: Pre-flight External Upload Restore Inspection */}
      <Dialog
        open={uploadedFile !== null}
        onClose={() => { setUploadedFile(null); setUploadedMetadata(null); }}
        maxWidth="sm"
        fullWidth
      >
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
            Restoring this file will overwrite existing database records. A pre-restore safety snapshot will automatically be saved to disk first.
          </Alert>
        </DialogContent>
        <DialogActions sx={{ px: 3, pb: 3 }}>
          <Button onClick={() => { setUploadedFile(null); setUploadedMetadata(null); }}>Cancel</Button>
          <Button onClick={handleConfirmUploadedRestore} variant="contained" color="primary">
            Restore External File
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
