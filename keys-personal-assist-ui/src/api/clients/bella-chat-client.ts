/**
 * Bella Chat Client
 * Handles chat message streaming, AI responses, Human-In-The-Loop resumes, and artifacts.
 *
 * Uses relative paths (/api/bella-chat) that are proxied by nginx in production
 * and by Vite dev server in development to the actual backend services.
 */
import { getBellaChatBase } from '@/api/config';
import { fetchWithAuth } from './fetchClient';

class BellaChatClient {
  private baseURL: string;

  constructor() {
    this.baseURL = getBellaChatBase();
  }

  /**
   * Send a message and get a streaming SSE response (v1 Legacy).
   * @param message - The user message to send
   * @param conversationId - UUID that groups messages into a conversation
   * @returns Raw fetch Response whose body is a text/event-stream
   */
  async sendMessage(message: string, conversationId: string): Promise<Response> {
    return fetchWithAuth(`${this.baseURL}/v1/chat/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message, conversation_id: conversationId }),
    });
  }

  /**
   * Send a message to Bella v2 Deep Agent engine and get streaming SSE events.
   * @param message - User query or instruction
   * @param conversationId - UUID grouping messages
   * @param enableHitl - Whether Human-In-The-Loop interrupts are enabled
   */
  async sendV2Message(message: string, conversationId: string, enableHitl = true): Promise<Response> {
    return fetchWithAuth(`${this.baseURL}/v2/chat/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message,
        conversation_id: conversationId,
        enable_hitl: enableHitl,
      }),
    });
  }

  /**
   * Resume an interrupted conversation with a human approval decision.
   */
  async resumeInterruptedAction(
    conversationId: string,
    interruptId: string,
    decision: 'approve' | 'edit' | 'reject',
    editedArgs?: Record<string, unknown>
  ): Promise<Response> {
    return fetchWithAuth(`${this.baseURL}/v2/chat/resume`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        conversation_id: conversationId,
        interrupt_id: interruptId,
        decision: {
          type: decision,
          edited_args: editedArgs || null,
        },
      }),
    });
  }

  /**
   * Get the download URL for a virtual filesystem artifact.
   */
  getArtifactUrl(conversationId: string, artifactId: string): string {
    return `${this.baseURL}/v2/chat/artifacts/${conversationId}/${artifactId}`;
  }
}

// Export singleton instance
export const bellaChatClient = new BellaChatClient();
