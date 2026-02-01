import { Box, Paper, Avatar } from '@mui/material';
import { Chat as MessageCircle, AutoAwesome as Sparkles } from '@mui/icons-material';
import { MarkdownRenderer } from './MarkdownRenderer';

interface ChatMessageProps {
  role: 'user' | 'assistant';
  content: string;
  isStreaming?: boolean;
}

export function ChatMessage({ role, content, isStreaming }: ChatMessageProps) {
  const isUser = role === 'user';

  return (
    <Box
      sx={{
        display: 'flex',
        gap: 1.5,
        mb: 2,
        justifyContent: isUser ? 'flex-end' : 'flex-start',
        animation: 'fadeIn 0.3s ease-in',
        '@keyframes fadeIn': {
          '0%': { opacity: 0, transform: 'translateY(10px)' },
          '100%': { opacity: 1, transform: 'translateY(0)' },
        },
      }}
    >
      {!isUser && (
        <Avatar
          sx={{
            width: 32,
            height: 32,
            bgcolor: 'primary.light',
            color: 'primary.dark',
          }}
        >
          <Sparkles sx={{ fontSize: 18 }} />
        </Avatar>
      )}

      <Paper
        elevation={0}
        sx={{
          maxWidth: { xs: '280px', sm: '400px', md: '500px' },
          px: 2,
          py: 1.5,
          borderRadius: 2,
          bgcolor: isUser ? 'primary.main' : 'background.paper',
          color: isUser ? 'primary.contrastText' : 'text.primary',
          borderBottomRightRadius: isUser ? 0 : undefined,
          borderBottomLeftRadius: !isUser ? 0 : undefined,
          border: !isUser ? 1 : 0,
          borderColor: 'divider',
          ...(isStreaming && {
            animation: 'pulse 2s ease-in-out infinite',
            '@keyframes pulse': {
              '0%, 100%': { opacity: 1 },
              '50%': { opacity: 0.8 },
            },
          }),
        }}
      >
        {isUser ? (
          <Box
            component="p"
            sx={{
              fontSize: '0.875rem',
              lineHeight: 1.6,
              whiteSpace: 'pre-wrap',
              wordBreak: 'break-word',
              m: 0,
            }}
          >
            {content}
          </Box>
        ) : (
          <Box sx={{ fontSize: '0.875rem', lineHeight: 1.6 }}>
            <MarkdownRenderer content={content} />
          </Box>
        )}
      </Paper>

      {isUser && (
        <Avatar
          sx={{
            width: 32,
            height: 32,
            bgcolor: 'primary.main',
            color: 'white',
          }}
        >
          <MessageCircle sx={{ fontSize: 18 }} />
        </Avatar>
      )}
    </Box>
  );
}
