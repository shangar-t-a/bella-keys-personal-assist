import { type NextRequest, NextResponse } from "next/server"
import { bellaChatClient } from "@/app/api/clients/bella-chat-client"

export async function POST(request: NextRequest) {
  try {
    const { message } = await request.json()

    if (!message || typeof message !== "string") {
      return NextResponse.json({ error: "Message is required" }, { status: 400 })
    }

    const response = await bellaChatClient.sendMessage(message)

    if (!response.ok) {
      const error = await response.text()
      return NextResponse.json({ error: `API Error: ${error}` }, { status: response.status })
    }

    // Handle streaming response
    const reader = response.body?.getReader()
    if (!reader) {
      return NextResponse.json({ error: "No response body" }, { status: 500 })
    }

    const encoder = new TextEncoder()
    const stream = new ReadableStream({
      async start(controller) {
        try {
          while (true) {
            const { done, value } = await reader.read()
            if (done) break

            const chunk = new TextDecoder().decode(value)
            controller.enqueue(encoder.encode(chunk))
          }
          controller.close()
        } catch (error) {
          controller.error(error)
        }
      },
    })

    return new NextResponse(stream, {
      headers: {
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache",
        Connection: "keep-alive",
      },
    })
  } catch (error) {
    console.error("Chat API error:", error)
    return NextResponse.json({ error: "Internal server error" }, { status: 500 })
  }
}
