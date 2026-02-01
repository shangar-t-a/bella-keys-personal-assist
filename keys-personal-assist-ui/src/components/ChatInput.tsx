import { useState, useRef } from 'react';
import { TextField, IconButton, Box } from '@mui/material';
import { Send, RotateRight as Loader2 } from '@mui/icons-material';

interface ChatInputProps {
  onSendMessage: (message: string) => void;
  isLoading?: boolean;
  disabled?: boolean;
}

export function ChatInput({ onSendMessage, isLoading, disabled }: ChatInputProps) {
  const [message, setMessage] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim() && !isLoading && !disabled) {
      const cleanedMessage = stripTerminalLines(message);
      onSendMessage(cleanedMessage);
      setMessage('');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e as any);
    }
  };

  const stripTerminalLines = (text: string): string => {
    return text
      .split('\n')
      .filter((line) => {
        const trimmed = line.trim();
        // Remove lines that look like terminal prompts
        return !trimmed.match(/^[$>#%~]\s/) && trimmed.length > 0;
      })
      .join('\n')
      .trim();
  };

  return (
    <Box component="form" onSubmit={handleSubmit} sx={{ display: 'flex', gap: 2, alignItems: 'flex-end' }}>
      <TextField
        inputRef={textareaRef}
        fullWidth
        multiline
        maxRows={4}
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Ask me anything..."
        disabled={isLoading || disabled}
        variant="outlined"
        sx={{
          '& .MuiOutlinedInput-root': {
            borderRadius: 2,
          },
        }}
      />
      <IconButton
        type="submit"
        disabled={!message.trim() || isLoading || disabled}
        color="primary"
        sx={{
          width: 48,
          height: 48,
          bgcolor: 'primary.main',
          color: 'white',
          '&:hover': {
            bgcolor: 'primary.dark',
          },
          '&:disabled': {
            bgcolor: 'action.disabledBackground',
          },
        }}
      >
        {isLoading ? (
          <Loader2 sx={{ fontSize: 20, animation: 'spin 1s linear infinite', '@keyframes spin': { '0%': { transform: 'rotate(0deg)' }, '100%': { transform: 'rotate(360deg)' } } }} />
        ) : (
          <Send sx={{ fontSize: 20 }} />
        )}
      </IconButton>
    </Box>
  );
}
