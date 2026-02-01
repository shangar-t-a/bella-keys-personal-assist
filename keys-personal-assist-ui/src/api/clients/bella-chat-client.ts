/**
 * Bella Chat Client
 * Handles chat message streaming and AI responses
 * 
 * Uses relative paths (/api/bella-chat) that are proxied by nginx in production
 * and by Vite dev server in development to the actual backend services.
 */
class BellaChatClient {
  private baseURL: string;

  constructor() {
    // Use relative path - nginx/Vite proxy handles routing to backend
    this.baseURL = '/api/bella-chat';
  }

  /**
   * Send a message and get a streaming response
   * @param message - The user message to send
   * @returns Response stream for reading chunks
   */
  async sendMessage(message: string): Promise<Response> {
    return fetch(`${this.baseURL}/v1/chat/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message }),
    });
  }
}

// Export singleton instance
export const bellaChatClient = new BellaChatClient();
