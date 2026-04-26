import { useState, useEffect, Component } from 'react';
import type { ReactNode, ErrorInfo } from 'react';
import {
    Box,
    Chip,
    Collapse,
    IconButton,
    Typography,
} from '@mui/material';
import {
    Build as ToolIcon,
    CheckCircle as CheckCircleIcon,
    ErrorOutline as ErrorOutlineIcon,
    ExpandLess as ExpandLessIcon,
    ExpandMore as ExpandMoreIcon,
    HourglassEmpty as PendingIcon,
    LibraryBooks as KnowledgeIcon,
    Psychology as ThinkingIcon,
} from '@mui/icons-material';
import type { ThinkingStep } from '@/types/chat';

interface ThinkingStepsProps {
    steps: ThinkingStep[];
    isStreaming: boolean;
}

// ── group adjacent call+result pairs ─────────────────────────────────────────

type ToolGroup = {
    type: 'tool';
    isSubAgent: boolean;
    call: ThinkingStep;
    result: ThinkingStep | null;
};
type ThinkingGroup = { type: 'thinking'; step: ThinkingStep };
type StepGroup = ToolGroup | ThinkingGroup;

function groupSteps(steps: ThinkingStep[]): StepGroup[] {
    const groups: StepGroup[] = [];
    const consumed = new Set<number>();

    for (let i = 0; i < steps.length; i++) {
        if (consumed.has(i)) continue;
        const s = steps[i];

        if (s.kind === 'tool_call') {
            // Look ahead for the matching result by id (primary) or name (fallback).
            // Parallel tool calls produce all calls first then all results, so
            // adjacent-only pairing breaks — forward scan handles both patterns.
            let resultIdx = -1;
            for (let j = i + 1; j < steps.length; j++) {
                if (
                    !consumed.has(j) &&
                    steps[j].kind === 'tool_result' &&
                    (s.id ? steps[j].id === s.id : steps[j].name === s.name)
                ) {
                    resultIdx = j;
                    break;
                }
            }
            if (resultIdx !== -1) consumed.add(resultIdx);
            const result = resultIdx !== -1 ? steps[resultIdx] : null;
            groups.push({ type: 'tool', isSubAgent: !!s.isSubAgent, call: s, result });
        } else if (s.kind === 'tool_result') {
            // Truly orphaned result (no matching call found ahead of it)
            groups.push({
                type: 'tool',
                isSubAgent: !!s.isSubAgent,
                call: { ...s, kind: 'tool_call' },
                result: s,
            });
        } else {
            groups.push({ type: 'thinking', step: s });
        }
    }
    return groups;
}

// ── sub-components ────────────────────────────────────────────────────────────

const TRUNCATE = 280;

function ResultContent({ content, isError }: { content: string; isError?: boolean }) {
    const [expanded, setExpanded] = useState(false);
    // Guard: content may arrive as a non-string if the LLM returns a complex object.
    const safeContent = typeof content === 'string' ? content : JSON.stringify(content);
    const long = safeContent.length > TRUNCATE;
    const shown = !long || expanded ? safeContent : safeContent.slice(0, TRUNCATE) + '…';
    return (
        <Box sx={{ mt: 0.75 }}>
            {isError && (
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 0.5 }}>
                    <ErrorOutlineIcon sx={{ fontSize: 13, color: 'error.main' }} />
                    <Typography variant="caption" sx={{ color: 'error.main', fontWeight: 600 }}>
                        Tool error
                    </Typography>
                </Box>
            )}
            <Typography
                component="pre"
                sx={{
                    m: 0,
                    fontSize: '0.7rem',
                    fontFamily: 'monospace',
                    color: isError ? 'error.main' : 'text.secondary',
                    whiteSpace: 'pre-wrap',
                    wordBreak: 'break-word',
                    lineHeight: 1.5,
                }}
            >
                {shown}
            </Typography>
            {long && (
                <Typography
                    variant="caption"
                    onClick={() => setExpanded((p) => !p)}
                    sx={{
                        cursor: 'pointer',
                        color: 'primary.main',
                        display: 'block',
                        mt: 0.25,
                        '&:hover': { textDecoration: 'underline' },
                    }}
                >
                    {expanded ? 'show less' : 'show more'}
                </Typography>
            )}
        </Box>
    );
}

function ToolCard({ group, isLast, isStreaming }: { group: ToolGroup; isLast: boolean; isStreaming: boolean }) {
    const [argsExpanded, setArgsExpanded] = useState(false);
    const [resultExpanded, setResultExpanded] = useState(false);
    const pending = isLast && isStreaming && group.result === null;
    const { call, result, isSubAgent } = group;
    const hasArgs = !!call.detail;
    const hasResult = !!result?.detail;

    const accentColor = isSubAgent ? '#7c3aed' : '#108cc6';
    const accentBg = isSubAgent ? 'rgba(124,58,237,0.07)' : 'rgba(16,140,198,0.07)';

    return (
        <Box
            sx={{
                border: '1px solid',
                borderColor: 'divider',
                borderRadius: 1.5,
                overflow: 'hidden',
                bgcolor: 'background.paper',
            }}
        >
            {/* ── Header row ── */}
            <Box
                sx={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 1,
                    px: 1.25,
                    py: 0.75,
                    bgcolor: accentBg,
                    borderBottom: (argsExpanded && hasArgs) || (resultExpanded && hasResult) ? '1px solid' : 'none',
                    borderColor: 'divider',
                }}
            >
                {isSubAgent ? (
                    <KnowledgeIcon sx={{ fontSize: 14, color: accentColor, flexShrink: 0 }} />
                ) : (
                    <ToolIcon sx={{ fontSize: 14, color: accentColor, flexShrink: 0 }} />
                )}
                <Typography
                    variant="caption"
                    sx={{ fontWeight: 600, color: accentColor, fontFamily: 'monospace', flexGrow: 1 }}
                >
                    {call.label}
                </Typography>
                {pending ? (
                    <PendingIcon
                        sx={{
                            fontSize: 14,
                            color: accentColor,
                            animation: 'spin 1.5s linear infinite',
                            '@keyframes spin': { '100%': { transform: 'rotate(360deg)' } },
                        }}
                    />
                ) : (
                    <CheckCircleIcon sx={{ fontSize: 14, color: '#059669' }} />
                )}
                {hasArgs && (
                    <Chip
                        label="args"
                        size="small"
                        onClick={() => setArgsExpanded((p) => !p)}
                        sx={{
                            height: 16,
                            fontSize: '0.6rem',
                            cursor: 'pointer',
                            bgcolor: argsExpanded ? 'action.selected' : 'action.hover',
                        }}
                    />
                )}
                {hasResult && (
                    <Chip
                        label="result"
                        size="small"
                        onClick={() => setResultExpanded((p) => !p)}
                        sx={{
                            height: 16,
                            fontSize: '0.6rem',
                            cursor: 'pointer',
                            bgcolor: result?.isError
                                ? resultExpanded ? 'rgba(211,47,47,0.18)' : 'rgba(211,47,47,0.09)'
                                : resultExpanded ? 'action.selected' : 'action.hover',
                            color: result?.isError ? 'error.main' : undefined,
                            borderColor: result?.isError ? 'error.main' : undefined,
                            border: result?.isError ? '1px solid' : undefined,
                        }}
                    />
                )}
            </Box>

            {/* ── Args (collapsible) ── */}
            {hasArgs && (
                <Collapse in={argsExpanded}>
                    <Box sx={{ px: 1.25, py: 0.75, borderBottom: resultExpanded && hasResult ? '1px solid' : 'none', borderColor: 'divider' }}>
                        <Typography
                            component="pre"
                            sx={{
                                m: 0,
                                fontSize: '0.7rem',
                                fontFamily: 'monospace',
                                color: 'text.secondary',
                                whiteSpace: 'pre-wrap',
                                wordBreak: 'break-word',
                            }}
                        >
                            {call.detail}
                        </Typography>
                    </Box>
                </Collapse>
            )}

            {/* ── Result (collapsible) ── */}
            {hasResult && (
                <Collapse in={resultExpanded}>
                    <Box sx={{ px: 1.25, pb: 0.75, pt: 0.5 }}>
                        <ResultContent content={result!.detail!} isError={result?.isError} />
                    </Box>
                </Collapse>
            )}
        </Box>
    );
}

function ThinkingCard({ step }: { step: ThinkingStep }) {
    return (
        <Box sx={{ display: 'flex', gap: 0.75, alignItems: 'flex-start' }}>
            <ThinkingIcon sx={{ fontSize: 14, color: 'text.disabled', mt: 0.25, flexShrink: 0 }} />
            <Typography
                variant="caption"
                sx={{ color: 'text.secondary', fontStyle: 'italic', lineHeight: 1.5 }}
            >
                {step.label}
            </Typography>
        </Box>
    );
}

// ── Error boundary so a render crash doesn't blank the whole chat ────────────

class StepsErrorBoundary extends Component<{ children: ReactNode }, { failed: boolean }> {
    state = { failed: false };
    static getDerivedStateFromError(): { failed: boolean } {
        return { failed: true };
    }
    componentDidCatch(err: Error, info: ErrorInfo) {
        console.error('ThinkingSteps render error', err, info);
    }
    render() {
        if (this.state.failed) {
            return (
                <Typography variant="caption" sx={{ color: 'text.disabled', fontStyle: 'italic' }}>
                    (could not render reasoning steps)
                </Typography>
            );
        }
        return this.props.children;
    }
}

// ── Main component ────────────────────────────────────────────────────────────

export function ThinkingSteps({ steps, isStreaming }: ThinkingStepsProps) {
    const [expanded, setExpanded] = useState(true);

    useEffect(() => {
        if (!isStreaming) setExpanded(false);
    }, [isStreaming]);

    if (steps.length === 0) return null;

    const groups = groupSteps(steps);
    const toolCount = groups.filter((g) => g.type === 'tool').length;
    const label = isStreaming
        ? 'Thinking…'
        : toolCount > 0
            ? `${toolCount} tool call${toolCount !== 1 ? 's' : ''}`
            : 'Reasoning';

    return (
        <StepsErrorBoundary>
            <Box sx={{ mb: 1.5 }}>
                {/* Toggle header */}
                <Box
                    sx={{ display: 'flex', alignItems: 'center', gap: 0.25, cursor: 'pointer', userSelect: 'none', width: 'fit-content' }}
                    onClick={() => setExpanded((p) => !p)}
                >
                    <Typography variant="caption" sx={{ color: 'text.secondary', fontStyle: 'italic' }}>
                        {label}
                    </Typography>
                    <IconButton size="small" sx={{ p: 0.25, color: 'text.secondary' }}>
                        {expanded ? <ExpandLessIcon sx={{ fontSize: 15 }} /> : <ExpandMoreIcon sx={{ fontSize: 15 }} />}
                    </IconButton>
                </Box>

                <Collapse in={expanded} timeout="auto" unmountOnExit={false}>
                    <Box sx={{ mt: 0.75, display: 'flex', flexDirection: 'column', gap: 0.75 }}>
                        {groups.map((group, idx) =>
                            group.type === 'tool' ? (
                                <ToolCard
                                    key={idx}
                                    group={group}
                                    isLast={idx === groups.length - 1}
                                    isStreaming={isStreaming}
                                />
                            ) : (
                                <ThinkingCard key={idx} step={group.step} />
                            )
                        )}
                        {isStreaming && (
                            <Typography variant="caption" sx={{ color: 'text.disabled', fontStyle: 'italic', pl: 0.25 }}>
                                …
                            </Typography>
                        )}
                    </Box>
                </Collapse>
            </Box>
        </StepsErrorBoundary>
    );
}


