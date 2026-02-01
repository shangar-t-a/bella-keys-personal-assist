import { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Box, Typography, Container, IconButton, Paper } from '@mui/material';
import { ArrowBack as ArrowLeft, Delete as Trash2, Chat as ChatIcon } from '@mui/icons-material';
import { ChatMessage } from '@/components/ChatMessage';
import { ChatInput } from '@/components/ChatInput';
import { LoadingStatus } from '@/components/LoadingStatus';
import ModernHeader from '@/components/ModernHeader';
import { bellaChatClient } from '@/api/clients/bella-chat-client';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  isStreaming?: boolean;
}

export default function ChatPage() {
  const navigate = useNavigate();
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [loadingStatus, setLoadingStatus] = useState('Bella is thinking...');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const messagesContainerRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = async (message: string) => {
    const cleanedMessage = message
      .split('\n')
      .filter((line) => !line.match(/^[$>#%]\s/))
      .join('\n')
      .trim();

    if (!cleanedMessage) return;

    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: cleanedMessage,
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);
    setLoadingStatus('Bella is thinking...');

    try {
      const response = await bellaChatClient.sendMessage(cleanedMessage);

      if (!response.ok) {
        throw new Error('Failed to get response');
      }

      // Handle streaming response
      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error('No response body');
      }

      let assistantMessage = '';
      const assistantId = (Date.now() + 1).toString();

      setMessages((prev) => [
        ...prev,
        {
          id: assistantId,
          role: 'assistant',
          content: '',
          isStreaming: true,
        },
      ]);

      const decoder = new TextDecoder();
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        assistantMessage += chunk;

        setMessages((prev) =>
          prev.map((msg) => (msg.id === assistantId ? { ...msg, content: assistantMessage, isStreaming: true } : msg))
        );
      }

      setMessages((prev) => prev.map((msg) => (msg.id === assistantId ? { ...msg, isStreaming: false } : msg)));
    } catch (error) {
      console.error('Error sending message:', error);
      setMessages((prev) => [
        ...prev,
        {
          id: (Date.now() + 2).toString(),
          role: 'assistant',
          content: 'Sorry, I encountered an error. Please try again.',
          isStreaming: false,
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleClearChat = () => {
    setMessages([]);
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
        background: (theme) =>
          theme.palette.mode === 'light'
            ? 'linear-gradient(135deg, #ffffff 0%, #f0fdf4 100%)'
            : 'linear-gradient(135deg, #1f2937 0%, #064e3b 100%)',
      }}
    >
      <ModernHeader />

      <Container
        maxWidth="md"
        sx={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          py: 3,
          overflow: 'hidden',
        }}
      >
        {/* Header */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3, flexShrink: 0 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <IconButton onClick={() => navigate(-1)} sx={{ '&:hover': { bgcolor: 'action.hover' } }}>
              <ArrowLeft />
            </IconButton>
            <Box>
              <Typography variant="h5" sx={{ fontWeight: 700, fontFamily: '"Space Grotesk", sans-serif' }}>
                Chat with Bella
              </Typography>
              <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                Ask me anything
              </Typography>
            </Box>
          </Box>
          {messages.length > 0 && (
            <IconButton
              onClick={handleClearChat}
              sx={{
                '&:hover': { bgcolor: 'error.light', color: 'error.main' },
              }}
            >
              <Trash2 />
            </IconButton>
          )}
        </Box>

        {/* Messages Container - scrollable */}
        <Paper
          elevation={0}
          sx={{
            flex: 1,
            mb: 2,
            p: 3,
            overflowY: 'auto',
            bgcolor: 'background.paper',
            borderRadius: 2,
            border: 1,
            borderColor: 'divider',
          }}
        >
          <Box ref={messagesContainerRef}>
            {messages.length === 0 ? (
              <Box
                sx={{
                  height: '100%',
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  justifyContent: 'center',
                  textAlign: 'center',
                  py: 12,
                }}
              >
                <Box
                  sx={{
                    width: 64,
                    height: 64,
                    borderRadius: '50%',
                    bgcolor: 'primary.light',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    mb: 2,
                  }}
                >
                  <ChatIcon sx={{ fontSize: 32, color: 'primary.main' }} />
                </Box>
                <Typography variant="h6" sx={{ fontWeight: 600, mb: 1 }}>
                  Start a conversation
                </Typography>
                <Typography variant="body2" sx={{ color: 'text.secondary', maxWidth: '300px' }}>
                  Ask me questions, get help with tasks, or just chat. I'm here to help!
                </Typography>
              </Box>
            ) : (
              <>
                {messages.map((msg) => (
                  <ChatMessage key={msg.id} role={msg.role} content={msg.content} isStreaming={msg.isStreaming} />
                ))}
                {isLoading && <LoadingStatus message={loadingStatus} />}
                <div ref={messagesEndRef} />
              </>
            )}
          </Box>
        </Paper>

        {/* Input Area - fixed at bottom */}
        <Box sx={{ flexShrink: 0, bgcolor: 'background.default', pt: 2 }}>
          <ChatInput onSendMessage={handleSendMessage} isLoading={isLoading} />
          <Typography variant="caption" sx={{ display: 'block', textAlign: 'center', color: 'text.secondary', mt: 1.5 }}>
            Press Enter to send, Shift+Enter for new line
          </Typography>
        </Box>
      </Container>
    </Box>
  );
}
