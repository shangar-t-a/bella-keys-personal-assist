import { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Box, Typography, Container, IconButton, Paper, Chip } from '@mui/material';
import { ArrowBack as ArrowLeft, Delete as Trash2, Chat as ChatIcon, AutoAwesome as SparklesIcon } from '@mui/icons-material';
import { ChatMessage } from '@/components/ChatMessage';
import { ChatInput } from '@/components/ChatInput';
import { LoadingStatus } from '@/components/LoadingStatus';
import { HitlApprovalCard } from '@/components/HitlApprovalCard';
import { TaskExecutionTree } from '@/components/TaskExecutionTree';
import { ArtifactPreviewDrawer } from '@/components/ArtifactPreviewDrawer';
import { bellaChatClient } from '@/api/clients/bella-chat-client';
import { parseSseChunk } from '@/types/chat';
import type { ChatMessage as ChatMessageType, ThinkingStep, PendingInterruptState, GeneratedArtifact } from '@/types/chat';

export default function ChatPage() {
  const navigate = useNavigate();
  const [messages, setMessages] = useState<ChatMessageType[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [loadingStatus, setLoadingStatus] = useState('Bella v2 Deep Agent reasoning…');
  const [conversationId] = useState(() => crypto.randomUUID());
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const messagesContainerRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const processStreamReader = async (reader: ReadableStreamDefaultReader<Uint8Array>, assistantId: string) => {
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });

      const boundary = buffer.lastIndexOf('\n\n');
      if (boundary === -1) continue;

      const toProcess = buffer.slice(0, boundary + 2);
      buffer = buffer.slice(boundary + 2);

      const events = parseSseChunk(toProcess);

      for (const event of events) {
        if (event.type === 'thinking') {
          const step: ThinkingStep = {
            kind: 'thinking',
            label: event.content,
          };
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === assistantId ? { ...msg, thinkingSteps: [...(msg.thinkingSteps ?? []), step] } : msg
            )
          );
        } else if (event.type === 'tool_call' || event.type === 'subagent_call') {
          setLoadingStatus(`Delegating to ${event.label}…`);
          const step: ThinkingStep = {
            kind: event.type,
            id: event.id,
            name: event.name,
            label: event.label,
            detail: event.args || undefined,
            isSubAgent: event.type === 'subagent_call' || ('is_sub_agent' in event && event.is_sub_agent),
            node: 'node' in event ? (event.node as string) : undefined,
          };
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === assistantId ? { ...msg, thinkingSteps: [...(msg.thinkingSteps ?? []), step] } : msg
            )
          );
        } else if (event.type === 'tool_result' || event.type === 'subagent_result') {
          const isError =
            event.content.startsWith('Error') ||
            /\b(4\d\d|5\d\d)\b/.test(event.content) ||
            event.content.toLowerCase().includes('error calling tool');
          const step: ThinkingStep = {
            kind: event.type,
            id: event.id,
            name: event.name,
            label: event.label,
            detail: event.content,
            isSubAgent: event.type === 'subagent_result' || ('is_sub_agent' in event && event.is_sub_agent),
            isError,
            node: 'node' in event ? (event.node as string) : undefined,
          };
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === assistantId ? { ...msg, thinkingSteps: [...(msg.thinkingSteps ?? []), step] } : msg
            )
          );
        } else if (event.type === 'interrupt') {
          const pendingInterrupt: PendingInterruptState = {
            interruptId: event.interrupt_id,
            toolName: event.tool_name,
            toolLabel: event.tool_label,
            args: event.args,
            description: event.description,
          };
          setMessages((prev) =>
            prev.map((msg) => (msg.id === assistantId ? { ...msg, pendingInterrupt } : msg))
          );
          setIsLoading(false);
          return;
        } else if (event.type === 'artifact_created') {
          const artifact: GeneratedArtifact = {
            id: event.id,
            filename: `Artifact_${event.id.slice(0, 8)}`,
            details: event.details,
            url: bellaChatClient.getArtifactUrl(conversationId, event.id),
          };
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === assistantId ? { ...msg, artifacts: [...(msg.artifacts ?? []), artifact] } : msg
            )
          );
        } else if (event.type === 'response') {
          setIsLoading(false);
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === assistantId ? { ...msg, content: msg.content + event.content } : msg
            )
          );
        } else if (event.type === 'error') {
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === assistantId ? { ...msg, content: `Error: ${event.content}`, isStreaming: false } : msg
            )
          );
        } else if (event.type === 'done') {
          setMessages((prev) =>
            prev.map((msg) => (msg.id === assistantId ? { ...msg, isStreaming: false } : msg))
          );
        }
      }
    }
  };

  const handleSendMessage = async (message: string) => {
    const cleanedMessage = message
      .split('\n')
      .filter((line) => !line.match(/^[$>#%]\s/))
      .join('\n')
      .trim();

    if (!cleanedMessage) return;

    const userMessage: ChatMessageType = {
      id: Date.now().toString(),
      role: 'user',
      content: cleanedMessage,
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);
    setLoadingStatus('Bella v2 Deep Agent reasoning…');

    try {
      const response = await bellaChatClient.sendV2Message(cleanedMessage, conversationId);

      if (!response.ok) {
        throw new Error('Failed to get response');
      }

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error('No response body');
      }

      const assistantId = (Date.now() + 1).toString();
      setMessages((prev) => [
        ...prev,
        {
          id: assistantId,
          role: 'assistant',
          content: '',
          isStreaming: true,
          thinkingSteps: [],
        },
      ]);

      await processStreamReader(reader, assistantId);
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

  const handleHitlDecision = async (
    assistantId: string,
    interruptId: string,
    decision: 'approve' | 'edit' | 'reject',
    editedArgs?: Record<string, unknown>
  ) => {
    // Clear pending interrupt state
    setMessages((prev) =>
      prev.map((msg) => (msg.id === assistantId ? { ...msg, pendingInterrupt: undefined, isStreaming: true } : msg))
    );
    setIsLoading(true);
    setLoadingStatus(`Resuming action with decision '${decision}'…`);

    try {
      const response = await bellaChatClient.resumeInterruptedAction(conversationId, interruptId, decision, editedArgs);
      if (!response.ok) throw new Error('Failed to resume interrupted action');

      const reader = response.body?.getReader();
      if (!reader) throw new Error('No response body');

      await processStreamReader(reader, assistantId);
    } catch (err) {
      console.error('Error resuming HITL action:', err);
      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === assistantId
            ? { ...msg, content: msg.content + '\n\n[Error resuming action]', isStreaming: false }
            : msg
        )
      );
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
            ? 'linear-gradient(135deg, #f5f8fa 0%, #e0eef7 100%)'
            : 'linear-gradient(135deg, #111827 0%, #0b2d47 100%)',
      }}
    >
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
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Typography variant="h5" sx={{ fontWeight: 700, fontFamily: '"Space Grotesk", sans-serif' }}>
                  Chat with Bella
                </Typography>
                <Chip icon={<SparklesIcon />} label="v2 Deep Agent" color="primary" size="small" variant="filled" />
              </Box>
              <Typography variant="body2" sx={{ color: 'text.secondary' }}>
                Powered by Sub-Agents, HITL Review & Virtual Filesystem
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

        {/* Messages Container */}
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
                  Welcome to Bella v2
                </Typography>
                <Typography variant="body2" sx={{ color: 'text.secondary', maxWidth: '360px' }}>
                  Ask questions, request financial summaries, generate report documents, or trigger sub-agent tasks.
                </Typography>
              </Box>
            ) : (
              <>
                {messages.map((msg) => (
                  <Box key={msg.id} sx={{ mb: 2 }}>
                    <ChatMessage
                      role={msg.role}
                      content={msg.content}
                      isStreaming={msg.isStreaming}
                      thinkingSteps={msg.thinkingSteps}
                    />

                    {msg.thinkingSteps && msg.thinkingSteps.length > 0 && (
                      <TaskExecutionTree steps={msg.thinkingSteps} />
                    )}

                    {msg.artifacts && msg.artifacts.length > 0 && (
                      <ArtifactPreviewDrawer artifacts={msg.artifacts} />
                    )}

                    {msg.pendingInterrupt && (
                      <HitlApprovalCard
                        interrupt={msg.pendingInterrupt}
                        onDecision={(decision, editedArgs) =>
                          handleHitlDecision(msg.id, msg.pendingInterrupt!.interruptId, decision, editedArgs)
                        }
                        isLoading={isLoading}
                      />
                    )}
                  </Box>
                ))}
                {isLoading && <LoadingStatus message={loadingStatus} />}
                <div ref={messagesEndRef} />
              </>
            )}
          </Box>
        </Paper>

        {/* Input Area */}
        <Box sx={{ flexShrink: 0, pt: 2 }}>
          <ChatInput onSendMessage={handleSendMessage} isLoading={isLoading} />
          <Typography variant="caption" sx={{ display: 'block', textAlign: 'center', color: 'text.secondary', mt: 1.5 }}>
            Press Enter to send, Shift+Enter for new line
          </Typography>
        </Box>
      </Container>
    </Box>
  );
}
