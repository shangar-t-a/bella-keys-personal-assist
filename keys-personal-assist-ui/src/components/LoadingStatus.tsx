import { Box, Paper, Avatar, Typography } from '@mui/material';
import { AutoAwesome as Sparkles } from '@mui/icons-material';

interface LoadingStatusProps {
  message?: string;
  className?: string;
}

/**
 * Loading Status Component
 * Displays intuitive status messages during API calls
 * Supports intermediate steps from streaming API responses
 */
export function LoadingStatus({ message = 'Bella is thinking...', className }: LoadingStatusProps) {
  return (
    <Box
      className={className}
      sx={{
        display: 'flex',
        gap: 1.5,
        mb: 2,
        animation: 'fadeIn 0.3s ease-in',
        '@keyframes fadeIn': {
          '0%': { opacity: 0, transform: 'translateY(10px)' },
          '100%': { opacity: 1, transform: 'translateY(0)' },
        },
      }}
    >
      <Avatar
        sx={{
          width: 32,
          height: 32,
          background: 'linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%)',
          animation: 'spin 2s linear infinite',
          '@keyframes spin': {
            '0%': { transform: 'rotate(0deg)' },
            '100%': { transform: 'rotate(360deg)' },
          },
        }}
      >
        <Sparkles sx={{ fontSize: 18, color: 'white' }} />
      </Avatar>

      <Paper
        elevation={0}
        sx={{
          maxWidth: { xs: '280px', sm: '400px', md: '500px' },
          px: 2,
          py: 1.5,
          borderRadius: 2,
          borderBottomLeftRadius: 0,
          background: 'linear-gradient(135deg, #ecfeff 0%, #dbeafe 100%)',
          border: 1,
          borderColor: 'info.light',
          flex: 1,
        }}
      >
        <Typography
          variant="body2"
          sx={{
            fontSize: '0.875rem',
            lineHeight: 1.6,
            color: 'info.dark',
          }}
        >
          {message}
        </Typography>
      </Paper>
    </Box>
  );
}
