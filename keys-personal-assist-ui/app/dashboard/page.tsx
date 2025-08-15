"use client"

import Link from "next/link"
import { TrendingUp, ArrowRight } from "lucide-react"
import Header from "@/components/header"

export default function DashboardPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-50">
      <Header />

      <main className="container mx-auto px-4 py-12">
        {/* Header Section */}
        <div className="text-center max-w-3xl mx-auto mb-16">
          <h1 className="font-display text-4xl md:text-5xl font-bold text-slate-900 mb-6">
            Your
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-600 to-cyan-600">
              {" "}
              Dashboards
            </span>
          </h1>
          <p className="text-xl text-slate-600 leading-relaxed">Access your personal management tools and insights.</p>
        </div>

        {/* Dashboard Grid */}
        <div className="grid md:grid-cols-2 gap-8 max-w-6xl mx-auto">
          {/* Active Dashboard */}
          <div className="group relative bg-white rounded-2xl shadow-lg border border-slate-100 hover:shadow-2xl transition-all duration-300 overflow-hidden">
            <div className="p-8">
              {/* Icon and Title */}
              <div className="flex items-start gap-4 mb-6">
                <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-emerald-500 to-emerald-600 hover:from-emerald-600 hover:to-emerald-700 flex items-center justify-center shadow-lg">
                  <TrendingUp className="w-7 h-7 text-white" />
                </div>
                <div className="flex-1">
                  <h3 className="font-display text-xl font-bold text-slate-900 mb-2">Spending Account Summary</h3>
                  <p className="text-slate-600 leading-relaxed">
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

          {/* Future Slot */}
          <div className="group relative bg-white/50 rounded-2xl shadow-lg border border-slate-200 border-dashed transition-all duration-300 overflow-hidden">
            <div className="p-8 text-center">
              <div className="w-14 h-14 rounded-2xl bg-slate-100 flex items-center justify-center mx-auto mb-6">
                <div className="w-6 h-6 bg-slate-300 rounded"></div>
              </div>
              <h3 className="font-display text-xl font-bold text-slate-400 mb-2">Future Dashboard</h3>
              <p className="text-slate-400 leading-relaxed mb-6">
                More dashboards coming soon to help you manage different aspects of your life.
              </p>

              <button
                disabled
                className="w-full flex items-center justify-center gap-2 bg-slate-100 text-slate-400 px-6 py-3 rounded-xl font-semibold cursor-not-allowed"
              >
                Coming Soon
              </button>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
