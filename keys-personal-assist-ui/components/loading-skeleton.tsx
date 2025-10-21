"use client"

import { cn } from "@/lib/utils"

interface LoadingSkeletonProps {
  className?: string
}

export function LoadingSkeleton({ className }: LoadingSkeletonProps) {
  return (
    <div className={cn("flex gap-3 mb-4 animate-fade-in", className)}>
      <div className="flex-shrink-0 w-8 h-8 rounded-full bg-emerald-100 dark:bg-emerald-900 flex items-center justify-center">
        <div className="w-4 h-4 rounded-full bg-emerald-600 dark:bg-emerald-400 animate-pulse" />
      </div>

      <div className="max-w-xs lg:max-w-md xl:max-w-lg px-4 py-3 rounded-lg bg-muted text-foreground rounded-bl-none border border-border flex-1">
        <div className="space-y-2">
          <div className="h-3 bg-muted-foreground/20 rounded animate-pulse" style={{ width: "90%" }} />
          <div
            className="h-3 bg-muted-foreground/20 rounded animate-pulse"
            style={{ width: "85%", animationDelay: "0.1s" }}
          />
          <div
            className="h-3 bg-muted-foreground/20 rounded animate-pulse"
            style={{ width: "75%", animationDelay: "0.2s" }}
          />
        </div>
      </div>
    </div>
  )
}
