"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { ArrowRight } from "lucide-react"
import ModernHeader from "@/components/modern-header"

export default function HomePage() {
  const router = useRouter()
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  const handleGetStarted = () => {
    router.push("/dashboard")
  }

  if (!mounted) return null

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-muted/20">
      <ModernHeader />

      {/* Hero Section */}
      <main className="container mx-auto px-4 py-12">
        <div className="max-w-4xl mx-auto text-center space-y-8 animate-slide-in">
          <div className="space-y-4">
            <h1 className="text-4xl md:text-6xl font-bold bg-gradient-to-r from-emerald-600 to-cyan-600 bg-clip-text text-transparent leading-tight">
              Bella
            </h1>

            <h2 className="text-2xl md:text-3xl font-semibold text-foreground">Keys' Personal Assistant</h2>

            <p className="text-xl text-muted-foreground max-w-2xl mx-auto leading-relaxed">
              Manage your day, ask questions and more with your personal assistant.
            </p>
          </div>

          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <Button onClick={handleGetStarted} size="lg" className="px-8 py-6 text-lg font-semibold group">
              Get Started
              <ArrowRight className="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" />
            </Button>
          </div>
        </div>
      </main>
    </div>
  )
}
