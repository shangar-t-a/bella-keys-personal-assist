/**
 * Bella Chat Client
 * Handles chat message streaming and AI responses
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
   * Send a message and get a streaming SSE response.
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
}

// Export singleton instance
export const bellaChatClient = new BellaChatClient();
