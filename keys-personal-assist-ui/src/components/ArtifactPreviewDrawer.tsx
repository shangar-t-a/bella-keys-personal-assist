import React from 'react';
import { Box, Typography, Button, Paper, Stack } from '@mui/material';
import { InsertDriveFile as FileIcon, Download as DownloadIcon } from '@mui/icons-material';
import type { GeneratedArtifact } from '@/types/chat';

interface ArtifactPreviewDrawerProps {
  artifacts: GeneratedArtifact[];
}

export const ArtifactPreviewDrawer: React.FC<ArtifactPreviewDrawerProps> = ({ artifacts }) => {
  if (!artifacts || artifacts.length === 0) return null;

  return (
    <Box sx={{ mt: 2, mb: 1 }}>
      <Typography variant="caption" sx={{ fontWeight: 700, textTransform: 'uppercase', color: 'text.secondary', mb: 1, display: 'block' }}>
        Generated Virtual Filesystem Artifacts ({artifacts.length})
      </Typography>
      <Stack spacing={1}>
        {artifacts.map((art) => (
          <Paper
            key={art.id}
            variant="outlined"
            sx={{
              p: 1.5,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              borderRadius: 2,
              bgcolor: (theme) => (theme.palette.mode === 'light' ? '#f8fafc' : '#0f172a'),
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
              <FileIcon color="primary" />
              <Box>
                <Typography variant="body2" sx={{ fontWeight: 600 }}>
                  {art.filename}
                </Typography>
                <Typography variant="caption" sx={{ color: 'text.secondary', display: 'block' }}>
                  {art.details}
                </Typography>
              </Box>
            </Box>
            <Button
              size="small"
              variant="outlined"
              startIcon={<DownloadIcon />}
              href={art.url}
              target="_blank"
              rel="noopener noreferrer"
            >
              Download
            </Button>
          </Paper>
        ))}
      </Stack>
    </Box>
  );
};
