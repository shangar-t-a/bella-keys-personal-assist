"use client"

import type React from "react"

import { useState, useRef, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Send, Loader2 } from "lucide-react"

interface ChatInputProps {
  onSendMessage: (message: string) => void
  isLoading?: boolean
  disabled?: boolean
}

export function ChatInput({ onSendMessage, isLoading, disabled }: ChatInputProps) {
  const [message, setMessage] = useState("")
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto"
      textareaRef.current.style.height = Math.min(textareaRef.current.scrollHeight, 120) + "px"
    }
  }, [message])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (message.trim() && !isLoading && !disabled) {
      const cleanedMessage = stripTerminalLines(message)
      onSendMessage(cleanedMessage)
      setMessage("")
      if (textareaRef.current) {
        textareaRef.current.style.height = "auto"
      }
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e as any)
    }
  }

  const stripTerminalLines = (text: string): string => {
    return text
      .split("\n")
      .filter((line) => {
        const trimmed = line.trim()
        // Remove lines that look like terminal prompts
        return !trimmed.match(/^[$>#%~]\s/) && trimmed.length > 0
      })
      .join("\n")
      .trim()
  }

  return (
    <form onSubmit={handleSubmit} className="flex gap-3 items-end">
      <Textarea
        ref={textareaRef}
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Ask me anything..."
        disabled={isLoading || disabled}
        className="resize-none min-h-12 max-h-32 py-3"
        rows={1}
      />
      <Button
        type="submit"
        disabled={!message.trim() || isLoading || disabled}
        size="icon"
        className="flex-shrink-0 h-12 w-12"
      >
        {isLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
      </Button>
    </form>
  )
}
