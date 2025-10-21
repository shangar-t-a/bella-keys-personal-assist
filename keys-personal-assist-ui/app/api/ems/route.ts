import { type NextRequest, NextResponse } from "next/server"
import { emsClient } from "@/app/api/clients/ems-client"

/**
 * EMS API Route Handler
 * Proxies requests to the EMS backend
 * Supports: GET /api/ems?endpoint=...&method=...
 */
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const endpoint = searchParams.get("endpoint")

    if (!endpoint) {
      return NextResponse.json({ error: "Endpoint parameter is required" }, { status: 400 })
    }

    // Route to appropriate EMS client method
    let result
    switch (endpoint) {
      case "accounts":
        result = await emsClient.getAllAccounts()
        break
      case "month-years":
        result = await emsClient.getAllMonthYears()
        break
      case "spending-accounts":
        result = await emsClient.getAllSpendingAccountEntries()
        break
      default:
        return NextResponse.json({ error: "Unknown endpoint" }, { status: 400 })
    }

    return NextResponse.json(result)
  } catch (error) {
    console.error("EMS API error:", error)
    return NextResponse.json({ error: "Internal server error" }, { status: 500 })
  }
}
