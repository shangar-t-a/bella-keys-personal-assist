"use client"

import { cn } from "@/lib/utils"
import { Sparkles } from "lucide-react"

interface LoadingStatusProps {
  message?: string
  className?: string
}

/**
 * Loading Status Component
 * Displays intuitive status messages during API calls
 * Supports intermediate steps from streaming API responses
 */
export function LoadingStatus({ message = "Bella is thinking...", className }: LoadingStatusProps) {
  return (
    <div className={cn("flex gap-3 mb-4 animate-fade-in", className)}>
      <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-cyan-400 to-blue-500 flex items-center justify-center">
        <Sparkles className="w-4 h-4 text-white animate-spin" />
      </div>

      <div className="max-w-xs lg:max-w-md xl:max-w-lg px-4 py-3 rounded-lg bg-gradient-to-r from-cyan-50 to-blue-50 dark:from-cyan-950 dark:to-blue-950 text-foreground rounded-bl-none border border-cyan-200 dark:border-cyan-800 flex-1">
        <p className="text-sm leading-relaxed text-cyan-900 dark:text-cyan-100">{message}</p>
      </div>
    </div>
  )
}
