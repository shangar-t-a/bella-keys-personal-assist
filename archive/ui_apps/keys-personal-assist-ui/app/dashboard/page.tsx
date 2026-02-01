"use client"

import Link from "next/link"
import { TrendingUp, ArrowRight } from "lucide-react"
import Header from "@/components/header"

export default function DashboardPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-muted/20">
      <Header />

      <main className="container mx-auto px-4 py-12">
        {/* Header Section */}
        <div className="text-center max-w-3xl mx-auto mb-16">
          <h1 className="font-display text-4xl md:text-5xl font-bold text-foreground mb-6">
            Your
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-600 to-cyan-600">
              {" "}
              Dashboards
            </span>
          </h1>
          <p className="text-xl text-muted-foreground leading-relaxed">
            Access your personal management tools and insights.
          </p>
        </div>

        {/* Dashboard Grid */}
        <div className="max-w-2xl mx-auto">
          {/* Spending Account Dashboard */}
          <div className="group relative bg-card rounded-2xl shadow-lg border border-border hover:shadow-2xl transition-all duration-300 overflow-hidden hover:-translate-y-1">
            <div className="p-8">
              {/* Icon and Title */}
              <div className="flex items-start gap-4 mb-6">
                <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-emerald-500 to-emerald-600 hover:from-emerald-600 hover:to-emerald-700 flex items-center justify-center shadow-lg">
                  <TrendingUp className="w-7 h-7 text-white" />
                </div>
                <div className="flex-1">
                  <h3 className="font-display text-xl font-bold text-foreground mb-2">Spending Account Summary</h3>
                  <p className="text-muted-foreground leading-relaxed">
                    Track your expenses, view spending patterns, and manage your budget with detailed analytics.
                  </p>
                </div>
              </div>

              {/* Action Button */}
              <Link
                href="/dashboard/spending-account-summary"
                className="w-full flex items-center justify-center gap-2 bg-gradient-to-r from-emerald-500 to-emerald-600 hover:from-emerald-600 hover:to-emerald-700 text-white px-6 py-3 rounded-xl font-semibold transition-all duration-200 shadow-lg hover:shadow-xl transform group-hover:-translate-y-0.5"
              >
                Open Dashboard
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </Link>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
