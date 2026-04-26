/**
 * Chat-related types shared across pages and components.
 */

// ── SSE event payloads ────────────────────────────────────────────────────────

export interface ThinkingEvent {
    type: 'thinking';
    content: string;
}

export interface ToolCallEvent {
    type: 'tool_call';
    id: string;
    name: string;
    label: string;
    args: string;
    is_sub_agent: boolean;
}

export interface ToolResultEvent {
    type: 'tool_result';
    id: string;
    name: string;
    label: string;
    content: string;
    is_sub_agent: boolean;
}

export interface ResponseEvent {
    type: 'response';
    content: string;
}

export interface ErrorEvent {
    type: 'error';
    content: string;
}

export interface DoneEvent {
    type: 'done';
}

export type SSEEvent =
    | ThinkingEvent
    | ToolCallEvent
    | ToolResultEvent
    | ResponseEvent
    | ErrorEvent
    | DoneEvent;

// ── Thinking step (for UI display) ────────────────────────────────────────────

export type ThinkingStepKind = 'thinking' | 'tool_call' | 'tool_result';

export interface ThinkingStep {
    kind: ThinkingStepKind;
    /** Unique tool-call ID from the backend — primary key for call+result pairing. */
    id?: string;
    /** Tool/sub-agent name — fallback for pairing when id is absent. */
    name?: string;
    label: string;
    detail?: string;
    isSubAgent?: boolean;
    /** True when the tool returned an error (HTTP 4xx/5xx or exception message). */
    isError?: boolean;
}

// ── Chat message ───────────────────────────────────────────────────────────────

export interface ChatMessage {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    isStreaming?: boolean;
    thinkingSteps?: ThinkingStep[];
}

// ── Helpers ───────────────────────────────────────────────────────────────────

/**
 * Parse a raw SSE buffer (potentially containing multiple events) into typed
 * SSEEvent objects.  Lines that are empty, comments (`:`), or fail JSON parsing
 * are silently skipped.
 */
export function parseSseChunk(raw: string): SSEEvent[] {
    const events: SSEEvent[] = [];
    // Events are separated by double newlines; each event is "data: <json>"
    for (const block of raw.split('\n\n')) {
        for (const line of block.split('\n')) {
            const trimmed = line.trim();
            if (!trimmed || trimmed.startsWith(':')) continue;
            const payload = trimmed.startsWith('data: ') ? trimmed.slice(6) : trimmed;
            try {
                const obj = JSON.parse(payload) as SSEEvent;
                if (obj?.type) events.push(obj);
            } catch {
                // ignore malformed lines
            }
        }
    }
    return events;
}
