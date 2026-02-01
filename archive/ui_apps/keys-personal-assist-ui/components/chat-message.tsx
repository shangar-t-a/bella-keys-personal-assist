"use client"

import { cn } from "@/lib/utils"
import { MessageCircle, Sparkles } from "lucide-react"
import { MarkdownRenderer } from "./markdown-renderer"

interface ChatMessageProps {
  role: "user" | "assistant"
  content: string
  isStreaming?: boolean
}

export function ChatMessage({ role, content, isStreaming }: ChatMessageProps) {
  const isUser = role === "user"

  return (
    <div className={cn("flex gap-3 mb-4 animate-fade-in", isUser ? "justify-end" : "justify-start")}>
      {!isUser && (
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-emerald-100 dark:bg-emerald-900 flex items-center justify-center">
          <Sparkles className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
        </div>
      )}

      <div
        className={cn(
          "max-w-xs lg:max-w-md xl:max-w-lg px-4 py-3 rounded-lg",
          isUser
            ? "bg-emerald-600 text-white rounded-br-none"
            : cn(
                "bg-muted text-foreground rounded-bl-none border border-border",
                isStreaming && "animate-gradient-glow",
              ),
        )}
      >
        {isUser ? (
          <p className="text-sm leading-relaxed whitespace-pre-wrap break-words">{content}</p>
        ) : (
          <div className="text-sm leading-relaxed">
            <MarkdownRenderer content={content} />
          </div>
        )}
      </div>

      {isUser && (
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-emerald-600 flex items-center justify-center">
          <MessageCircle className="w-4 h-4 text-white" />
        </div>
      )}
    </div>
  )
}
