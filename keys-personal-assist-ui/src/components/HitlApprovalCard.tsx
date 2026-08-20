import React, { useState } from 'react';
import { Box, Typography, Button, Paper, TextField, Collapse } from '@mui/material';
import {
  ShieldOutlined as ShieldIcon,
  Check as CheckIcon,
  Close as CloseIcon,
  EditOutlined as EditIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
} from '@mui/icons-material';
import type { PendingInterruptState } from '@/types/chat';

interface HitlApprovalCardProps {
  interrupt: PendingInterruptState;
  onDecision: (decision: 'approve' | 'edit' | 'reject', editedArgs?: Record<string, unknown>) => void;
  isLoading?: boolean;
}

export const HitlApprovalCard: React.FC<HitlApprovalCardProps> = ({ interrupt, onDecision, isLoading = false }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [showArgs, setShowArgs] = useState(true);
  const [jsonArgsText, setJsonArgsText] = useState(() => JSON.stringify(interrupt.args || {}, null, 2));
  const [parseError, setParseError] = useState<string | null>(null);

  const toolName = interrupt.toolName || 'Unknown Tool';
  const toolLabel = interrupt.toolLabel || toolName;

  const handleApprove = () => {
    onDecision('approve');
  };

  const handleReject = () => {
    onDecision('reject');
  };

  const handleSaveEdit = () => {
    try {
      const parsed = JSON.parse(jsonArgsText) as Record<string, unknown>;
      setParseError(null);
      onDecision('edit', parsed);
    } catch {
      setParseError('Invalid JSON format.');
    }
  };

  return (
    <Paper
      elevation={0}
      sx={{
        p: 2,
        my: 1.5,
        borderRadius: 2,
        border: '1px solid',
        borderColor: (theme) => (theme.palette.mode === 'light' ? '#ffe58f' : '#433403'),
        bgcolor: (theme) => (theme.palette.mode === 'light' ? '#fffbe6' : '#1f1a08'),
      }}
    >
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <ShieldIcon sx={{ fontSize: 20, color: '#d48806' }} />
          <Typography variant="subtitle2" sx={{ fontWeight: 600, color: (theme) => (theme.palette.mode === 'light' ? '#8c6800' : '#ffd591') }}>
            Action Pending Approval
          </Typography>
        </Box>
        <Button
          size="small"
          onClick={() => setShowArgs(!showArgs)}
          endIcon={showArgs ? <ExpandLessIcon /> : <ExpandMoreIcon />}
          sx={{ textTransform: 'none', color: 'text.secondary', fontSize: '0.75rem' }}
        >
          {showArgs ? 'Hide Details' : 'Show Details'}
        </Button>
      </Box>

      <Typography variant="body2" sx={{ mb: 1, fontWeight: 500, color: 'text.primary' }}>
        Tool: <Box component="span" sx={{ fontFamily: 'monospace', px: 0.8, py: 0.2, bgcolor: (theme) => (theme.palette.mode === 'light' ? 'rgba(0,0,0,0.06)' : 'rgba(255,255,255,0.08)'), borderRadius: 1 }}>{toolLabel} ({toolName})</Box>
      </Typography>

      <Collapse in={showArgs}>
        {isEditing ? (
          <Box sx={{ mt: 1, mb: 1.5 }}>
            <TextField
              multiline
              rows={4}
              fullWidth
              size="small"
              value={jsonArgsText}
              onChange={(e) => setJsonArgsText(e.target.value)}
              error={Boolean(parseError)}
              helperText={parseError}
              sx={{ fontFamily: 'monospace', fontSize: '0.8rem' }}
            />
          </Box>
        ) : (
          <Paper
            variant="outlined"
            sx={{
              p: 1.25,
              my: 1,
              bgcolor: (theme) => (theme.palette.mode === 'light' ? '#fafafa' : '#141414'),
              fontFamily: 'monospace',
              fontSize: '0.8rem',
              whiteSpace: 'pre-wrap',
              overflowX: 'auto',
              borderRadius: 1,
            }}
          >
            {Object.keys(interrupt.args || {}).length === 0 ? '{}' : JSON.stringify(interrupt.args, null, 2)}
          </Paper>
        )}
      </Collapse>

      <Box sx={{ display: 'flex', gap: 1, justifyContent: 'flex-end', mt: 1.5 }}>
        {isEditing ? (
          <>
            <Button size="small" variant="text" onClick={() => setIsEditing(false)} disabled={isLoading}>
              Cancel
            </Button>
            <Button size="small" variant="contained" color="warning" onClick={handleSaveEdit} disabled={isLoading}>
              Submit Edit
            </Button>
          </>
        ) : (
          <>
            <Button
              size="small"
              variant="outlined"
              color="error"
              startIcon={<CloseIcon />}
              onClick={handleReject}
              disabled={isLoading}
              sx={{ textTransform: 'none' }}
            >
              Reject
            </Button>
            <Button
              size="small"
              variant="outlined"
              color="inherit"
              startIcon={<EditIcon />}
              onClick={() => setIsEditing(true)}
              disabled={isLoading}
              sx={{ textTransform: 'none' }}
            >
              Edit Params
            </Button>
            <Button
              size="small"
              variant="contained"
              color="success"
              startIcon={<CheckIcon />}
              onClick={handleApprove}
              disabled={isLoading}
              sx={{ textTransform: 'none', fontWeight: 600 }}
            >
              Approve
            </Button>
          </>
        )}
      </Box>
    </Paper>
  );
};
