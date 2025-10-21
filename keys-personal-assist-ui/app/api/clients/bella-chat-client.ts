const BELLA_CHAT_API_URL = process.env.NEXT_PUBLIC_BELLA_CHAT_API_URL || "http://localhost:5000"

/**
 * Bella Chat Client
 * Handles chat message streaming and AI responses
 */
class BellaChatClient {
  private baseURL: string

  constructor() {
    this.baseURL = BELLA_CHAT_API_URL
  }

  /**
   * Send a message and get a streaming response
   * @param message - The user message to send
   * @returns Response stream for reading chunks
   */
  async sendMessage(message: string): Promise<Response> {
    return fetch(`${this.baseURL}/v1/chat/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ message }),
    })
  }
}

// Export singleton instance
export const bellaChatClient = new BellaChatClient()
