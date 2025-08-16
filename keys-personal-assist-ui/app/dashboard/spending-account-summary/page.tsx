"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Label } from "@/components/ui/label"
import {
  Plus,
  Edit,
  Trash2,
  RotateCcw,
  ChevronLeft,
  ChevronRight,
  ChevronsLeft,
  ChevronsRight,
  TrendingUp,
  TrendingDown,
} from "lucide-react"
import { useToast } from "@/hooks/use-toast"
import Header from "@/components/header"

interface SpendingAccountEntry {
  id: string
  accountName: string
  month: string
  year: number
  startingBalance: number
  currentBalance: number
  currentCredit: number
  balanceAfterCredit: number
  totalSpent: number
}

interface AccountResponse {
  id: string
  accountName: string
}

interface FormData {
  accountName: string
  month: string
  year: number
  startingBalance: number
  currentBalance: number
  currentCredit: number
}

const MONTHS = [
  "January",
  "February",
  "March",
  "April",
  "May",
  "June",
  "July",
  "August",
  "September",
  "October",
  "November",
  "December",
]

const PAGE_SIZES = [10, 25, 50, 100]

const getApiBaseUrl = () => {
  // Try to get from window object (set by runtime config)
  if (typeof window !== "undefined" && (window as any).__RUNTIME_CONFIG__?.API_BASE_URL) {
    return (window as any).__RUNTIME_CONFIG__.API_BASE_URL
  }

  // Default fallback for development
  return "http://localhost:8000"
}

export default function SpendingAccountSummaryPage() {
  const [mounted, setMounted] = useState(false)
  const [entries, setEntries] = useState<SpendingAccountEntry[]>([])
  const [loading, setLoading] = useState(true)
  const [accounts, setAccounts] = useState<string[]>([])
  const [availableMonths, setAvailableMonths] = useState<string[]>([])
  const [availableYears, setAvailableYears] = useState<number[]>([])

  // Filters
  const [selectedAccount, setSelectedAccount] = useState<string>("")
  const [selectedMonth, setSelectedMonth] = useState<string>("All Months")
  const [selectedYear, setSelectedYear] = useState<string>("All Years")

  // Pagination
  const [currentPage, setCurrentPage] = useState(1)
  const [pageSize, setPageSize] = useState(10)

  // Sorting
  const [sortConfig, setSortConfig] = useState<{ key: keyof SpendingAccountEntry; direction: "asc" | "desc" }[]>([
    { key: "year", direction: "desc" },
    { key: "month", direction: "desc" },
  ])

  // Modals
  const [isAddModalOpen, setIsAddModalOpen] = useState(false)
  const [isEditModalOpen, setIsEditModalOpen] = useState(false)
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false)
  const [selectedEntry, setSelectedEntry] = useState<SpendingAccountEntry | null>(null)
  const [formData, setFormData] = useState<FormData>({
    accountName: "",
    month: "January",
    year: new Date().getFullYear(),
    startingBalance: 0,
    currentBalance: 0,
    currentCredit: 0,
  })

  const { toast } = useToast()

  const fetchAccounts = async () => {
    try {
      const apiBaseUrl = getApiBaseUrl()
      console.log("[v0] API Base URL:", apiBaseUrl)
      console.log(
        "[v0] Runtime config:",
        typeof window !== "undefined" ? (window as any).__RUNTIME_CONFIG__ : "server-side",
      )

      const response = await fetch(`${apiBaseUrl}/v1/account/list`)

      if (response.ok) {
        const accountData: AccountResponse[] = await response.json()
        const accountNames = accountData.map((account) => account.accountName)
        setAccounts(accountNames)

        // Set default account if none selected
        if (accountNames.length > 0 && !selectedAccount) {
          setSelectedAccount(accountNames[0])
        }
      } else {
        console.error("Failed to fetch accounts")
      }
    } catch (error) {
      console.error("Error fetching accounts:", error)
    }
  }

  const fetchData = async () => {
    try {
      setLoading(true)
      const apiBaseUrl = getApiBaseUrl()
      console.log("[v0] Fetching data from:", `${apiBaseUrl}/v1/spending_account/list`)

      const response = await fetch(`${apiBaseUrl}/v1/spending_account/list`)

      if (response.ok) {
        const data: SpendingAccountEntry[] = await response.json()
        setEntries(data)

        // Extract unique months and years from entries
        const uniqueMonths = [...new Set(data.map((entry) => entry.month))]
        const uniqueYears = [...new Set(data.map((entry) => entry.year))].sort((a, b) => b - a)

        setAvailableMonths(uniqueMonths)
        setAvailableYears(uniqueYears)
      } else {
        toast({
          title: "Error",
          description: "Failed to fetch data from server",
          variant: "destructive",
        })
      }
    } catch (error) {
      console.error("Error fetching data:", error)
      toast({
        title: "Error",
        description: "Unable to connect to server",
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchAccounts()
    fetchData()
    setMounted(true)
  }, [])

  const filteredEntries = entries.filter((entry) => {
    const accountMatch = selectedAccount === "" || entry.accountName === selectedAccount
    const monthMatch = selectedMonth === "All Months" || entry.month === selectedMonth
    const yearMatch = selectedYear === "All Years" || entry.year.toString() === selectedYear
    return accountMatch && monthMatch && yearMatch
  })

  const sortedEntries = [...filteredEntries].sort((a, b) => {
    for (const { key, direction } of sortConfig) {
      let aVal = a[key]
      let bVal = b[key]

      // Special handling for month sorting
      if (key === "month") {
        aVal = MONTHS.indexOf(a.month as string)
        bVal = MONTHS.indexOf(b.month as string)
      }

      if (aVal < bVal) return direction === "asc" ? -1 : 1
      if (aVal > bVal) return direction === "asc" ? 1 : -1
    }
    return 0
  })

  const totalPages = Math.ceil(sortedEntries.length / pageSize)
  const paginatedEntries = sortedEntries.slice((currentPage - 1) * pageSize, currentPage * pageSize)

  const currentBalanceMetric = filteredEntries.length > 0 ? filteredEntries[0].currentBalance : 0
  const currentCreditMetric = filteredEntries.length > 0 ? filteredEntries[0].currentCredit : 0
  const totalSpendingMetric = filteredEntries.reduce((sum, entry) => sum + entry.totalSpent, 0)
  const totalCreditMetric = filteredEntries.reduce((sum, entry) => sum + entry.currentCredit, 0)

  const calculateTrend = (current: number, previous: number) => {
    if (previous === 0) return null
    const change = ((current - previous) / previous) * 100
    return { change, isPositive: change > 0 }
  }

  const calculateTrendIndicators = () => {
    if (filteredEntries.length < 2) return { balanceTrend: null, creditTrend: null }

    // Sort entries by year and month to get chronological order
    const sortedByDate = [...filteredEntries].sort((a, b) => {
      if (a.year !== b.year) return a.year - b.year
      return MONTHS.indexOf(a.month) - MONTHS.indexOf(b.month)
    })

    const latest = sortedByDate[sortedByDate.length - 1]
    const previous = sortedByDate[sortedByDate.length - 2]

    const balanceTrend = calculateTrend(latest.currentBalance, previous.currentBalance)
    const creditTrend = calculateTrend(latest.currentCredit, previous.currentCredit)

    return { balanceTrend, creditTrend }
  }

  const { balanceTrend, creditTrend } = calculateTrendIndicators()

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat("en-IN", {
      style: "currency",
      currency: "INR",
      minimumFractionDigits: 2,
    }).format(amount)
  }

  const getValueColorClass = (amount: number) => {
    return amount >= 0 ? "text-emerald-600" : "text-red-600"
  }

  const handleSubmit = async (isEdit: boolean) => {
    try {
      const apiBaseUrl = getApiBaseUrl()

      const url = isEdit
        ? `${apiBaseUrl}/v1/spending_account/${selectedEntry?.id}`
        : `${apiBaseUrl}/v1/spending_account`
      const method = isEdit ? "PUT" : "POST"

      const response = await fetch(url, {
        method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      })

      if (response.ok) {
        toast({
          title: "Success",
          description: `Entry ${isEdit ? "updated" : "created"} successfully`,
        })
        fetchData()
        setIsAddModalOpen(false)
        setIsEditModalOpen(false)
        resetForm()
      } else {
        const error = await response.json()
        toast({
          title: "Error",
          description: error.detail || `Failed to ${isEdit ? "update" : "create"} entry`,
          variant: "destructive",
        })
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Network error occurred",
        variant: "destructive",
      })
    }
  }

  const handleDelete = async () => {
    if (!selectedEntry) return

    try {
      const apiBaseUrl = getApiBaseUrl()
      const response = await fetch(`${apiBaseUrl}/v1/spending_account/${selectedEntry.id}`, {
        method: "DELETE",
      })

      if (response.ok) {
        toast({
          title: "Success",
          description: "Entry deleted successfully",
        })
        fetchData()
        setIsDeleteModalOpen(false)
        setSelectedEntry(null)
      } else {
        toast({
          title: "Error",
          description: "Failed to delete entry",
          variant: "destructive",
        })
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Network error occurred",
        variant: "destructive",
      })
    }
  }

  const resetForm = () => {
    setFormData({
      accountName: "",
      month: "January",
      year: new Date().getFullYear(),
      startingBalance: 0,
      currentBalance: 0,
      currentCredit: 0,
    })
  }

  const resetFilters = () => {
    setSelectedAccount(accounts[0] || "")
    setSelectedMonth("All Months")
    setSelectedYear("All Years")
    setCurrentPage(1)
  }

  if (!mounted) return null

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-background via-background to-muted/20">
        <Header />
        <main className="container mx-auto px-4 py-8">
          <div className="max-w-7xl mx-auto">
            <div className="text-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-600 mx-auto"></div>
              <p className="mt-4 text-muted-foreground">Loading your data...</p>
            </div>
          </div>
        </main>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-background via-background to-muted/20">
      <Header />

      <main className="container mx-auto px-4 py-8">
        <div className="max-w-7xl mx-auto">
          {/* Header */}
          <div className="mb-8 animate-slide-in">
            <h1 className="text-3xl font-bold mb-2">Spending Account Summary</h1>
            <p className="text-muted-foreground">
              Track your income, expenses, credits and account balance with detailed insights
            </p>
          </div>

          {/* Dashboard Metrics */}
          <div className="grid md:grid-cols-4 gap-6 mb-8 animate-fade-in">
            <Card className="border-0 bg-card/50 backdrop-blur-sm">
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  Current Balance (Last Month)
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className={`text-2xl font-bold ${getValueColorClass(currentBalanceMetric)}`}>
                  {formatCurrency(currentBalanceMetric)}
                </div>
                {balanceTrend && (
                  <div
                    className={`flex items-center text-sm mt-1 ${balanceTrend.isPositive ? "text-emerald-600" : "text-red-600"}`}
                  >
                    {balanceTrend.isPositive ? (
                      <TrendingUp className="w-4 h-4 mr-1" />
                    ) : (
                      <TrendingDown className="w-4 h-4 mr-1" />
                    )}
                    {Math.abs(balanceTrend.change).toFixed(1)}% from last month
                  </div>
                )}
                {!balanceTrend && (
                  <div className="flex items-center text-sm text-muted-foreground mt-1">Latest month data</div>
                )}
              </CardContent>
            </Card>

            <Card className="border-0 bg-card/50 backdrop-blur-sm">
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium text-muted-foreground">Current Credit (Last Month)</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-red-600">{formatCurrency(currentCreditMetric)}</div>
                {creditTrend && (
                  <div
                    className={`flex items-center text-sm mt-1 ${creditTrend.isPositive ? "text-red-600" : "text-emerald-600"}`}
                  >
                    {creditTrend.isPositive ? (
                      <TrendingUp className="w-4 h-4 mr-1" />
                    ) : (
                      <TrendingDown className="w-4 h-4 mr-1" />
                    )}
                    {Math.abs(creditTrend.change).toFixed(1)}% from last month
                  </div>
                )}
                {!creditTrend && (
                  <div className="flex items-center text-sm text-muted-foreground mt-1">Latest month data</div>
                )}
              </CardContent>
            </Card>

            <Card className="border-0 bg-card/50 backdrop-blur-sm">
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium text-muted-foreground">Total Spending (Filtered)</CardTitle>
              </CardHeader>
              <CardContent>
                <div className={`text-2xl font-bold ${getValueColorClass(totalSpendingMetric)}`}>
                  {formatCurrency(totalSpendingMetric)}
                </div>
                <div className="flex items-center text-sm text-muted-foreground mt-1">From filtered data</div>
              </CardContent>
            </Card>

            <Card className="border-0 bg-card/50 backdrop-blur-sm">
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium text-muted-foreground">Total Credit (Filtered)</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-red-600">{formatCurrency(totalCreditMetric)}</div>
                <div className="flex items-center text-sm text-muted-foreground mt-1">From filtered data</div>
              </CardContent>
            </Card>
          </div>

          {/* Filters */}
          <Card className="mb-6 border-0 bg-card/50 backdrop-blur-sm animate-fade-in">
            <CardContent className="p-4 sm:p-6">
              <div className="flex flex-col gap-4">
                {/* Filter controls */}
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
                  <Select value={selectedAccount} onValueChange={setSelectedAccount}>
                    <SelectTrigger className="w-full">
                      <SelectValue placeholder="Select Account" />
                    </SelectTrigger>
                    <SelectContent>
                      {accounts.map((account) => (
                        <SelectItem key={account} value={account}>
                          {account}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>

                  <Select value={selectedMonth} onValueChange={setSelectedMonth}>
                    <SelectTrigger className="w-full">
                      <SelectValue placeholder="Select Month" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="All Months">All Months</SelectItem>
                      {MONTHS.map((month) => (
                        <SelectItem key={month} value={month}>
                          {month}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>

                  <Select value={selectedYear} onValueChange={setSelectedYear}>
                    <SelectTrigger className="w-full">
                      <SelectValue placeholder="Select Year" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="All Years">All Years</SelectItem>
                      {availableYears.map((year) => (
                        <SelectItem key={year} value={year.toString()}>
                          {year}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>

                  <Button variant="outline" onClick={resetFilters} className="w-full bg-transparent">
                    <RotateCcw className="w-4 h-4 mr-2" />
                    Reset Filters
                  </Button>
                </div>

                {/* Add Entry button - separate row on mobile */}
                <div className="flex justify-center sm:justify-end">
                  <Dialog open={isAddModalOpen} onOpenChange={setIsAddModalOpen}>
                    <DialogTrigger asChild>
                      <Button className="gap-2 w-full sm:w-auto">
                        <Plus className="w-4 h-4" />
                        Add Entry
                      </Button>
                    </DialogTrigger>
                    <DialogContent>
                      <DialogHeader>
                        <DialogTitle>Add New Entry</DialogTitle>
                        <DialogDescription>Create a new spending account entry</DialogDescription>
                      </DialogHeader>
                      <div className="grid gap-4 py-4">
                        <div className="grid grid-cols-4 items-center gap-4">
                          <Label htmlFor="accountName" className="text-right">
                            Account
                          </Label>
                          <Select
                            value={formData.accountName}
                            onValueChange={(value) => setFormData({ ...formData, accountName: value })}
                          >
                            <SelectTrigger className="col-span-3">
                              <SelectValue placeholder="Select Account" />
                            </SelectTrigger>
                            <SelectContent>
                              {accounts.map((account) => (
                                <SelectItem key={account} value={account}>
                                  {account}
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                        </div>
                        <div className="grid grid-cols-4 items-center gap-4">
                          <Label htmlFor="month" className="text-right">
                            Month
                          </Label>
                          <Select
                            value={formData.month}
                            onValueChange={(value) => setFormData({ ...formData, month: value })}
                          >
                            <SelectTrigger className="col-span-3">
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              {MONTHS.map((month) => (
                                <SelectItem key={month} value={month}>
                                  {month}
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                        </div>
                        <div className="grid grid-cols-4 items-center gap-4">
                          <Label htmlFor="year" className="text-right">
                            Year
                          </Label>
                          <Input
                            id="year"
                            type="number"
                            value={formData.year}
                            onChange={(e) => setFormData({ ...formData, year: Number.parseInt(e.target.value) })}
                            className="col-span-3"
                          />
                        </div>
                        <div className="grid grid-cols-4 items-center gap-4">
                          <Label htmlFor="startingBalance" className="text-right">
                            Starting Balance
                          </Label>
                          <Input
                            id="startingBalance"
                            type="number"
                            step="0.01"
                            value={formData.startingBalance}
                            onChange={(e) =>
                              setFormData({ ...formData, startingBalance: Number.parseFloat(e.target.value) })
                            }
                            className="col-span-3"
                          />
                        </div>
                        <div className="grid grid-cols-4 items-center gap-4">
                          <Label htmlFor="currentBalance" className="text-right">
                            Current Balance
                          </Label>
                          <Input
                            id="currentBalance"
                            type="number"
                            step="0.01"
                            value={formData.currentBalance}
                            onChange={(e) =>
                              setFormData({ ...formData, currentBalance: Number.parseFloat(e.target.value) })
                            }
                            className="col-span-3"
                          />
                        </div>
                        <div className="grid grid-cols-4 items-center gap-4">
                          <Label htmlFor="currentCredit" className="text-right">
                            Current Credit
                          </Label>
                          <Input
                            id="currentCredit"
                            type="number"
                            step="0.01"
                            value={formData.currentCredit}
                            onChange={(e) =>
                              setFormData({ ...formData, currentCredit: Number.parseFloat(e.target.value) })
                            }
                            className="col-span-3"
                          />
                        </div>
                      </div>
                      <DialogFooter>
                        <Button onClick={() => handleSubmit(false)}>Save Entry</Button>
                      </DialogFooter>
                    </DialogContent>
                  </Dialog>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Account Summary Table */}
          <Card className="border-0 bg-card/50 backdrop-blur-sm animate-fade-in">
            <CardHeader>
              <CardTitle>Account Summary</CardTitle>
              <CardDescription>Monthly account balance and spending summary</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead className="cursor-pointer min-w-[100px]">Month</TableHead>
                      <TableHead className="cursor-pointer min-w-[80px]">Year</TableHead>
                      <TableHead className="cursor-pointer text-right min-w-[120px]">Starting Balance</TableHead>
                      <TableHead className="cursor-pointer text-right min-w-[120px]">Current Balance</TableHead>
                      <TableHead className="cursor-pointer text-right min-w-[120px]">Current Credit</TableHead>
                      <TableHead className="cursor-pointer text-right min-w-[140px]">Balance After Credit</TableHead>
                      <TableHead className="cursor-pointer text-right min-w-[120px]">Total Spent</TableHead>
                      <TableHead className="text-right min-w-[100px]">Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {paginatedEntries.map((entry) => (
                      <TableRow key={entry.id}>
                        <TableCell className="font-medium">{entry.month}</TableCell>
                        <TableCell>{entry.year}</TableCell>
                        <TableCell className="text-right font-medium">
                          {formatCurrency(entry.startingBalance)}
                        </TableCell>
                        <TableCell className={`text-right font-medium ${getValueColorClass(entry.currentBalance)}`}>
                          {formatCurrency(entry.currentBalance)}
                        </TableCell>
                        <TableCell className="text-right font-medium text-red-600">
                          {formatCurrency(entry.currentCredit)}
                        </TableCell>
                        <TableCell className={`text-right font-medium ${getValueColorClass(entry.balanceAfterCredit)}`}>
                          {formatCurrency(entry.balanceAfterCredit)}
                        </TableCell>
                        <TableCell className={`text-right font-medium ${getValueColorClass(entry.totalSpent)}`}>
                          {formatCurrency(entry.totalSpent)}
                        </TableCell>
                        <TableCell className="text-right">
                          <div className="flex justify-end gap-2">
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => {
                                setSelectedEntry(entry)
                                setFormData({
                                  accountName: entry.accountName,
                                  month: entry.month,
                                  year: entry.year,
                                  startingBalance: entry.startingBalance,
                                  currentBalance: entry.currentBalance,
                                  currentCredit: entry.currentCredit,
                                })
                                setIsEditModalOpen(true)
                              }}
                            >
                              <Edit className="w-4 h-4" />
                            </Button>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => {
                                setSelectedEntry(entry)
                                setIsDeleteModalOpen(true)
                              }}
                            >
                              <Trash2 className="w-4 h-4" />
                            </Button>
                          </div>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>

              {/* Pagination */}
              <div className="flex flex-col sm:flex-row items-center justify-between space-y-4 sm:space-y-0 sm:space-x-2 py-4">
                <div className="flex items-center space-x-2">
                  <p className="text-sm font-medium">Rows per page</p>
                  <Select
                    value={pageSize.toString()}
                    onValueChange={(value) => {
                      setPageSize(Number.parseInt(value))
                      setCurrentPage(1)
                    }}
                  >
                    <SelectTrigger className="h-8 w-[70px]">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent side="top">
                      {PAGE_SIZES.map((size) => (
                        <SelectItem key={size} value={size.toString()}>
                          {size}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="flex items-center space-x-6 lg:space-x-8">
                  <div className="flex w-[100px] items-center justify-center text-sm font-medium">
                    Page {currentPage} of {totalPages}
                  </div>
                  <div className="flex items-center space-x-2">
                    <Button
                      variant="outline"
                      className="hidden h-8 w-8 p-0 lg:flex bg-transparent"
                      onClick={() => setCurrentPage(1)}
                      disabled={currentPage === 1}
                    >
                      <ChevronsLeft className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="outline"
                      className="h-8 w-8 p-0 bg-transparent"
                      onClick={() => setCurrentPage(currentPage - 1)}
                      disabled={currentPage === 1}
                    >
                      <ChevronLeft className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="outline"
                      className="h-8 w-8 p-0 bg-transparent"
                      onClick={() => setCurrentPage(currentPage + 1)}
                      disabled={currentPage === totalPages}
                    >
                      <ChevronRight className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="outline"
                      className="hidden h-8 w-8 p-0 lg:flex bg-transparent"
                      onClick={() => setCurrentPage(totalPages)}
                      disabled={currentPage === totalPages}
                    >
                      <ChevronsRight className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </main>

      {/* Edit Modal */}
      <Dialog open={isEditModalOpen} onOpenChange={setIsEditModalOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Edit Entry</DialogTitle>
            <DialogDescription>Update the spending account entry</DialogDescription>
          </DialogHeader>
          {/* Same form fields as Add Modal */}
          <div className="grid gap-4 py-4">
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="accountName" className="text-right">
                Account
              </Label>
              <Select
                value={formData.accountName}
                onValueChange={(value) => setFormData({ ...formData, accountName: value })}
              >
                <SelectTrigger className="col-span-3">
                  <SelectValue placeholder="Select Account" />
                </SelectTrigger>
                <SelectContent>
                  {accounts.map((account) => (
                    <SelectItem key={account} value={account}>
                      {account}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="month" className="text-right">
                Month
              </Label>
              <Select value={formData.month} onValueChange={(value) => setFormData({ ...formData, month: value })}>
                <SelectTrigger className="col-span-3">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {MONTHS.map((month) => (
                    <SelectItem key={month} value={month}>
                      {month}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="year" className="text-right">
                Year
              </Label>
              <Input
                id="year"
                type="number"
                value={formData.year}
                onChange={(e) => setFormData({ ...formData, year: Number.parseInt(e.target.value) })}
                className="col-span-3"
              />
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="startingBalance" className="text-right">
                Starting Balance
              </Label>
              <Input
                id="startingBalance"
                type="number"
                step="0.01"
                value={formData.startingBalance}
                onChange={(e) => setFormData({ ...formData, startingBalance: Number.parseFloat(e.target.value) })}
                className="col-span-3"
              />
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="currentBalance" className="text-right">
                Current Balance
              </Label>
              <Input
                id="currentBalance"
                type="number"
                step="0.01"
                value={formData.currentBalance}
                onChange={(e) => setFormData({ ...formData, currentBalance: Number.parseFloat(e.target.value) })}
                className="col-span-3"
              />
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="currentCredit" className="text-right">
                Current Credit
              </Label>
              <Input
                id="currentCredit"
                type="number"
                step="0.01"
                value={formData.currentCredit}
                onChange={(e) => setFormData({ ...formData, currentCredit: Number.parseFloat(e.target.value) })}
                className="col-span-3"
              />
            </div>
          </div>
          <DialogFooter>
            <Button onClick={() => handleSubmit(true)}>Update Entry</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Modal */}
      <Dialog open={isDeleteModalOpen} onOpenChange={setIsDeleteModalOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete Entry</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete this entry? This action cannot be undone.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsDeleteModalOpen(false)}>
              Cancel
            </Button>
            <Button variant="destructive" onClick={handleDelete}>
              Delete
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
