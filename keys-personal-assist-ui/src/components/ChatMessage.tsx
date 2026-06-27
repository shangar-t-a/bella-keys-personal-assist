import { Box, Paper, Avatar, alpha } from '@mui/material';
import { Chat as MessageCircle, AutoAwesome as Sparkles } from '@mui/icons-material';
import { MarkdownRenderer } from './MarkdownRenderer';
import { ThinkingSteps } from './ThinkingSteps';
import type { ThinkingStep } from '@/types/chat';

interface ChatMessageProps {
  role: 'user' | 'assistant';
  content: string;
  isStreaming?: boolean;
  thinkingSteps?: ThinkingStep[];
}

export function ChatMessage({ role, content, isStreaming, thinkingSteps }: ChatMessageProps) {
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
          px: 2.5,
          py: 1.5,
          borderRadius: 3,
          background: (theme) => isUser
            ? `linear-gradient(135deg, ${theme.palette.primary.main} 0%, ${theme.palette.info.main} 100%)`
            : theme.palette.mode === 'dark'
              ? 'rgba(21, 34, 50, 0.4)'
              : '#ffffff',
          color: isUser ? 'primary.contrastText' : 'text.primary',
          borderBottomRightRadius: isUser ? 2 : undefined,
          borderBottomLeftRadius: !isUser ? 2 : undefined,
          border: '1px solid',
          borderColor: (theme) => isUser ? 'transparent' : theme.palette.divider,
          boxShadow: (theme) => isUser 
            ? `0 4px 14px ${alpha(theme.palette.primary.main, 0.15)}`
            : theme.palette.mode === 'dark'
              ? '0 4px 12px rgba(0, 0, 0, 0.15)'
              : '0 4px 12px rgba(0, 0, 0, 0.02)',
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
            {thinkingSteps && thinkingSteps.length > 0 && (
              <ThinkingSteps steps={thinkingSteps} isStreaming={isStreaming ?? false} />
            )}
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
