"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Card, CardHeader, CardTitle } from "@/components/ui/card"
import { ArrowRight, Calendar, MessageCircle, BarChart3 } from "lucide-react"
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

        {/* Simple Features Grid */}
        <div className="grid md:grid-cols-3 gap-6 mt-20 animate-fade-in">
          <Card className="group hover:shadow-lg transition-all duration-300 border-0 bg-card/50 backdrop-blur-sm">
            <CardHeader className="text-center pb-4">
              <div className="w-12 h-12 bg-emerald-100 dark:bg-emerald-900 rounded-xl flex items-center justify-center mx-auto mb-4 group-hover:bg-emerald-200 dark:group-hover:bg-emerald-800 transition-colors">
                <BarChart3 className="w-6 h-6 text-emerald-600 dark:text-emerald-400" />
              </div>
              <CardTitle>Dashboard</CardTitle>
            </CardHeader>
          </Card>

          <Card className="group hover:shadow-lg transition-all duration-300 border-0 bg-card/50 backdrop-blur-sm">
            <CardHeader className="text-center pb-4">
              <div className="w-12 h-12 bg-emerald-100 dark:bg-emerald-900 rounded-xl flex items-center justify-center mx-auto mb-4 group-hover:bg-emerald-200 dark:group-hover:bg-emerald-800 transition-colors">
                <Calendar className="w-6 h-6 text-emerald-600 dark:text-emerald-400" />
              </div>
              <CardTitle>Organization</CardTitle>
            </CardHeader>
          </Card>

          <Card className="group hover:shadow-lg transition-all duration-300 border-0 bg-card/50 backdrop-blur-sm">
            <CardHeader className="text-center pb-4">
              <div className="w-12 h-12 bg-emerald-100 dark:bg-emerald-900 rounded-xl flex items-center justify-center mx-auto mb-4 group-hover:bg-emerald-200 dark:group-hover:bg-emerald-800 transition-colors">
                <MessageCircle className="w-6 h-6 text-emerald-600 dark:text-emerald-400" />
              </div>
              <CardTitle>Questions</CardTitle>
            </CardHeader>
          </Card>
        </div>
      </main>
    </div>
  )
}
