/**
 * Chat-related types shared across pages and components (v1 and v2 Deep Agents).
 */

// SSE event payloads (v1 & v2)

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

export interface SubAgentCallEvent {
  type: 'subagent_call';
  id: string;
  name: string;
  label: string;
  args: string;
  node?: string;
}

export interface SubAgentResultEvent {
  type: 'subagent_result';
  id: string;
  name: string;
  label: string;
  content: string;
  node?: string;
}

export interface InterruptEvent {
  type: 'interrupt';
  interrupt_id: string;
  tool_name: string;
  tool_label: string;
  args: Record<string, unknown>;
  description: string;
}

export interface ArtifactCreatedEvent {
  type: 'artifact_created';
  id: string;
  details: string;
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
  | SubAgentCallEvent
  | SubAgentResultEvent
  | InterruptEvent
  | ArtifactCreatedEvent
  | ResponseEvent
  | ErrorEvent
  | DoneEvent;

// Thinking step (for UI display)

export type ThinkingStepKind =
  | 'thinking'
  | 'tool_call'
  | 'tool_result'
  | 'subagent_call'
  | 'subagent_result'
  | 'interrupt'
  | 'artifact_created';

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
  node?: string;
}

export interface PendingInterruptState {
  interruptId: string;
  toolName: string;
  toolLabel: string;
  args: Record<string, unknown>;
  description: string;
}

export interface GeneratedArtifact {
  id: string;
  filename: string;
  details: string;
  url: string;
}

// Chat message

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  isStreaming?: boolean;
  thinkingSteps?: ThinkingStep[];
  pendingInterrupt?: PendingInterruptState;
  artifacts?: GeneratedArtifact[];
}

// Helpers

/**
 * Parse a raw SSE buffer (potentially containing multiple events) into typed
 * SSEEvent objects. Lines that are empty, comments (`:`), or fail JSON parsing
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
