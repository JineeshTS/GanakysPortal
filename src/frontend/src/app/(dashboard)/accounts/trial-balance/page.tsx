'use client'

import * as React from 'react'
import { PageHeader } from '@/components/layout/page-header'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { DateRangePicker } from '@/components/forms/date-picker'
import { LoadingSpinner } from '@/components/layout/loading-spinner'
import { EmptyState } from '@/components/layout/empty-state'
import { formatCurrency, formatDate, getFinancialYear } from '@/lib/format'
import { useApi } from '@/hooks'
import {
  Download,
  FileSpreadsheet,
  FileText,
  Printer,
  RefreshCw,
  TrendingUp,
  TrendingDown,
  Scale,
  AlertCircle,
  CheckCircle2,
  Loader2
} from 'lucide-react'

// ============================================================================
// Types
// ============================================================================

interface TrialBalanceAccount {
  id: string
  code: string
  name: string
  type: 'asset' | 'liability' | 'equity' | 'revenue' | 'expense'
  debit: number
  credit: number
  parent_id?: string
  level: number
}

interface TrialBalanceData {
  accounts: TrialBalanceAccount[]
  total_debit: number
  total_credit: number
  is_balanced: boolean
  as_of_date: string
  generated_at: string
}

// ============================================================================
// Mock Data
// ============================================================================

const mockTrialBalanceData: TrialBalanceData = {
  accounts: [
    // Assets
    { id: '1', code: '1000', name: 'Assets', type: 'asset', debit: 4567890, credit: 0, level: 0 },
    { id: '1-1', code: '1100', name: 'Current Assets', type: 'asset', debit: 3456780, credit: 0, parent_id: '1', level: 1 },
    { id: '1-1-1', code: '1110', name: 'Cash in Hand', type: 'asset', debit: 125000, credit: 0, parent_id: '1-1', level: 2 },
    { id: '1-1-2', code: '1121', name: 'HDFC Bank - Current A/c', type: 'asset', debit: 1845780, credit: 0, parent_id: '1-1', level: 2 },
    { id: '1-1-3', code: '1122', name: 'ICICI Bank - Salary A/c', type: 'asset', debit: 500000, credit: 0, parent_id: '1-1', level: 2 },
    { id: '1-1-4', code: '1130', name: 'Accounts Receivable', type: 'asset', debit: 986000, credit: 0, parent_id: '1-1', level: 2 },
    { id: '1-2', code: '1200', name: 'Fixed Assets', type: 'asset', debit: 1111110, credit: 0, parent_id: '1', level: 1 },
    { id: '1-2-1', code: '1210', name: 'Furniture & Fixtures', type: 'asset', debit: 345000, credit: 0, parent_id: '1-2', level: 2 },
    { id: '1-2-2', code: '1220', name: 'Computer Equipment', type: 'asset', debit: 766110, credit: 0, parent_id: '1-2', level: 2 },

    // Liabilities
    { id: '2', code: '2000', name: 'Liabilities', type: 'liability', debit: 0, credit: 1234560, level: 0 },
    { id: '2-1', code: '2100', name: 'Current Liabilities', type: 'liability', debit: 0, credit: 1234560, parent_id: '2', level: 1 },
    { id: '2-1-1', code: '2110', name: 'Accounts Payable', type: 'liability', debit: 0, credit: 567890, parent_id: '2-1', level: 2 },
    { id: '2-1-2', code: '2121', name: 'GST Payable', type: 'liability', debit: 0, credit: 189000, parent_id: '2-1', level: 2 },
    { id: '2-1-3', code: '2122', name: 'TDS Payable', type: 'liability', debit: 0, credit: 156200, parent_id: '2-1', level: 2 },
    { id: '2-1-4', code: '2123', name: 'PF Payable', type: 'liability', debit: 0, credit: 111470, parent_id: '2-1', level: 2 },
    { id: '2-1-5', code: '2130', name: 'Salary Payable', type: 'liability', debit: 0, credit: 210000, parent_id: '2-1', level: 2 },

    // Equity
    { id: '3', code: '3000', name: 'Equity', type: 'equity', debit: 0, credit: 2500000, level: 0 },
    { id: '3-1', code: '3100', name: 'Share Capital', type: 'equity', debit: 0, credit: 1000000, parent_id: '3', level: 1 },
    { id: '3-2', code: '3200', name: 'Retained Earnings', type: 'equity', debit: 0, credit: 1500000, parent_id: '3', level: 1 },

    // Revenue
    { id: '4', code: '4000', name: 'Revenue', type: 'revenue', debit: 0, credit: 5678900, level: 0 },
    { id: '4-1', code: '4100', name: 'Sales Revenue', type: 'revenue', debit: 0, credit: 5500000, parent_id: '4', level: 1 },
    { id: '4-2', code: '4200', name: 'Service Revenue', type: 'revenue', debit: 0, credit: 178900, parent_id: '4', level: 1 },

    // Expenses
    { id: '5', code: '5000', name: 'Expenses', type: 'expense', debit: 4845570, credit: 0, level: 0 },
    { id: '5-1', code: '5100', name: 'Salary & Wages', type: 'expense', debit: 2100000, credit: 0, parent_id: '5', level: 1 },
    { id: '5-2', code: '5200', name: 'Rent Expense', type: 'expense', debit: 600000, credit: 0, parent_id: '5', level: 1 },
    { id: '5-3', code: '5300', name: 'Utilities', type: 'expense', debit: 156780, credit: 0, parent_id: '5', level: 1 },
    { id: '5-4', code: '5400', name: 'Professional Fees', type: 'expense', debit: 300000, credit: 0, parent_id: '5', level: 1 },
    { id: '5-5', code: '5500', name: 'Depreciation', type: 'expense', debit: 300000, credit: 0, parent_id: '5', level: 1 },
    { id: '5-6', code: '5600', name: 'Marketing Expense', type: 'expense', debit: 456780, credit: 0, parent_id: '5', level: 1 },
    { id: '5-7', code: '5700', name: 'Travel & Conveyance', type: 'expense', debit: 234560, credit: 0, parent_id: '5', level: 1 },
    { id: '5-8', code: '5800', name: 'Office Supplies', type: 'expense', debit: 145230, credit: 0, parent_id: '5', level: 1 },
    { id: '5-9', code: '5900', name: 'Insurance Expense', type: 'expense', debit: 189000, credit: 0, parent_id: '5', level: 1 },
    { id: '5-10', code: '5950', name: 'Bank Charges', type: 'expense', debit: 12450, credit: 0, parent_id: '5', level: 1 },
    { id: '5-11', code: '5980', name: 'Interest Expense', type: 'expense', debit: 350770, credit: 0, parent_id: '5', level: 1 },
  ],
  total_debit: 9413460,
  total_credit: 9413460,
  is_balanced: true,
  as_of_date: '2024-12-31',
  generated_at: new Date().toISOString()
}

// ============================================================================
// Component
// ============================================================================

export default function TrialBalancePage() {
  const api = useApi<TrialBalanceData>()
  const [data, setData] = React.useState<TrialBalanceData | null>(null)
  const [isLoading, setIsLoading] = React.useState(false)
  const [isExporting, setIsExporting] = React.useState(false)

  // Date range state
  const currentDate = new Date()
  const financialYearStart = currentDate.getMonth() >= 3
    ? new Date(currentDate.getFullYear(), 3, 1)
    : new Date(currentDate.getFullYear() - 1, 3, 1)

  const [startDate, setStartDate] = React.useState(
    financialYearStart.toISOString().split('T')[0]
  )
  const [endDate, setEndDate] = React.useState(
    currentDate.toISOString().split('T')[0]
  )

  // Fetch trial balance data
  const fetchTrialBalance = React.useCallback(async () => {
    setIsLoading(true)
    try {
      // In production, this would call the API
      // await api.get(`/accounts/trial-balance?start_date=${startDate}&end_date=${endDate}`)

      // Using mock data for now
      await new Promise(resolve => setTimeout(resolve, 1000))
      setData(mockTrialBalanceData)
    } catch (error) {
      console.error('Failed to fetch trial balance:', error)
    } finally {
      setIsLoading(false)
    }
  }, [startDate, endDate])

  // Initial fetch
  React.useEffect(() => {
    fetchTrialBalance()
  }, [])

  // Export handlers
  const handleExport = async (format: 'xlsx' | 'pdf') => {
    setIsExporting(true)
    try {
      // In production, this would call the API
      // await api.get(`/accounts/trial-balance/export?format=${format}&start_date=${startDate}&end_date=${endDate}`)
      await new Promise(resolve => setTimeout(resolve, 1500))
      // Download would be triggered here
    } catch (error) {
      console.error('Export failed:', error)
    } finally {
      setIsExporting(false)
    }
  }

  // Get type color for row styling
  const getTypeColor = (type: string) => {
    const colors: Record<string, string> = {
      asset: 'text-blue-600',
      liability: 'text-red-600',
      equity: 'text-purple-600',
      revenue: 'text-green-600',
      expense: 'text-orange-600'
    }
    return colors[type] || 'text-gray-600'
  }

  // Calculate running totals by type
  const getTypeTotals = () => {
    if (!data) return { assets: 0, liabilities: 0, equity: 0, revenue: 0, expenses: 0 }

    const topLevelAccounts = data.accounts.filter(a => a.level === 0)
    return {
      assets: topLevelAccounts.find(a => a.type === 'asset')?.debit || 0,
      liabilities: topLevelAccounts.find(a => a.type === 'liability')?.credit || 0,
      equity: topLevelAccounts.find(a => a.type === 'equity')?.credit || 0,
      revenue: topLevelAccounts.find(a => a.type === 'revenue')?.credit || 0,
      expenses: topLevelAccounts.find(a => a.type === 'expense')?.debit || 0
    }
  }

  const typeTotals = getTypeTotals()

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <PageHeader
        title="Trial Balance"
        description="View debit and credit balances for all accounts"
        breadcrumbs={[
          { label: 'Dashboard', href: '/dashboard' },
          { label: 'Accounts', href: '/accounts' },
          { label: 'Trial Balance' }
        ]}
        actions={
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={() => fetchTrialBalance()} disabled={isLoading}>
              <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
            <Button variant="outline" size="sm" onClick={() => handleExport('xlsx')} disabled={isExporting}>
              {isExporting ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : <FileSpreadsheet className="h-4 w-4 mr-2" />}
              Excel
            </Button>
            <Button variant="outline" size="sm" onClick={() => handleExport('pdf')} disabled={isExporting}>
              <FileText className="h-4 w-4 mr-2" />
              PDF
            </Button>
            <Button variant="outline" size="sm">
              <Printer className="h-4 w-4 mr-2" />
              Print
            </Button>
          </div>
        }
      />

      {/* Date Range Selection */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col md:flex-row md:items-end md:justify-between gap-4">
            <DateRangePicker
              label="Report Period"
              name="trial-balance-period"
              startValue={startDate}
              endValue={endDate}
              onStartChange={setStartDate}
              onEndChange={setEndDate}
            />
            <div className="flex items-center gap-4">
              <div className="text-right">
                <p className="text-sm text-muted-foreground">Financial Year</p>
                <p className="font-semibold">{getFinancialYear(new Date(endDate))}</p>
              </div>
              <Button onClick={fetchTrialBalance} disabled={isLoading}>
                {isLoading ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : null}
                Generate Report
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Summary Cards */}
      {data && (
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          <Card>
            <CardContent className="pt-4">
              <div className="flex items-center gap-2 mb-1">
                <TrendingUp className="h-4 w-4 text-blue-600" />
                <p className="text-sm text-muted-foreground">Total Assets</p>
              </div>
              <p className="text-xl font-bold text-blue-600">{formatCurrency(typeTotals.assets)}</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-4">
              <div className="flex items-center gap-2 mb-1">
                <TrendingDown className="h-4 w-4 text-red-600" />
                <p className="text-sm text-muted-foreground">Total Liabilities</p>
              </div>
              <p className="text-xl font-bold text-red-600">{formatCurrency(typeTotals.liabilities)}</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-4">
              <div className="flex items-center gap-2 mb-1">
                <Scale className="h-4 w-4 text-purple-600" />
                <p className="text-sm text-muted-foreground">Total Equity</p>
              </div>
              <p className="text-xl font-bold text-purple-600">{formatCurrency(typeTotals.equity)}</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-4">
              <div className="flex items-center gap-2 mb-1">
                <TrendingUp className="h-4 w-4 text-green-600" />
                <p className="text-sm text-muted-foreground">Total Revenue</p>
              </div>
              <p className="text-xl font-bold text-green-600">{formatCurrency(typeTotals.revenue)}</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-4">
              <div className="flex items-center gap-2 mb-1">
                <TrendingDown className="h-4 w-4 text-orange-600" />
                <p className="text-sm text-muted-foreground">Total Expenses</p>
              </div>
              <p className="text-xl font-bold text-orange-600">{formatCurrency(typeTotals.expenses)}</p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Balance Status */}
      {data && (
        <Card className={data.is_balanced ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'}>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                {data.is_balanced ? (
                  <CheckCircle2 className="h-6 w-6 text-green-600" />
                ) : (
                  <AlertCircle className="h-6 w-6 text-red-600" />
                )}
                <div>
                  <p className={`font-semibold ${data.is_balanced ? 'text-green-800' : 'text-red-800'}`}>
                    {data.is_balanced ? 'Trial Balance is Balanced' : 'Trial Balance is Not Balanced'}
                  </p>
                  <p className={`text-sm ${data.is_balanced ? 'text-green-600' : 'text-red-600'}`}>
                    {data.is_balanced
                      ? 'Total debits equal total credits'
                      : `Difference: ${formatCurrency(Math.abs(data.total_debit - data.total_credit))}`
                    }
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-8">
                <div className="text-right">
                  <p className="text-sm text-muted-foreground">Total Debit</p>
                  <p className="text-2xl font-bold">{formatCurrency(data.total_debit)}</p>
                </div>
                <div className="text-right">
                  <p className="text-sm text-muted-foreground">Total Credit</p>
                  <p className="text-2xl font-bold">{formatCurrency(data.total_credit)}</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Trial Balance Table */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Trial Balance Report</CardTitle>
              <CardDescription>
                As of {formatDate(endDate, { format: 'long' })} | Generated: {data ? formatDate(data.generated_at, { format: 'long', showTime: true }) : '-'}
              </CardDescription>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <LoadingSpinner size="lg" />
            </div>
          ) : !data ? (
            <EmptyState
              title="No data available"
              description="Select a date range and generate the report to view the trial balance."
            />
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b bg-muted/50">
                    <th className="text-left py-3 px-4 font-medium text-muted-foreground">Code</th>
                    <th className="text-left py-3 px-4 font-medium text-muted-foreground">Account Name</th>
                    <th className="text-center py-3 px-4 font-medium text-muted-foreground">Type</th>
                    <th className="text-right py-3 px-4 font-medium text-muted-foreground">Debit (Dr.)</th>
                    <th className="text-right py-3 px-4 font-medium text-muted-foreground">Credit (Cr.)</th>
                  </tr>
                </thead>
                <tbody>
                  {data.accounts.map((account) => (
                    <tr
                      key={account.id}
                      className={`border-b hover:bg-muted/30 ${account.level === 0 ? 'bg-muted/20 font-semibold' : ''}`}
                    >
                      <td className="py-3 px-4">
                        <span className="font-mono text-sm text-muted-foreground">{account.code}</span>
                      </td>
                      <td className="py-3 px-4">
                        <span style={{ paddingLeft: `${account.level * 20}px` }}>
                          {account.name}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-center">
                        <Badge variant="outline" className={`capitalize ${getTypeColor(account.type)}`}>
                          {account.type}
                        </Badge>
                      </td>
                      <td className="py-3 px-4 text-right font-mono">
                        {account.debit > 0 ? formatCurrency(account.debit) : '-'}
                      </td>
                      <td className="py-3 px-4 text-right font-mono">
                        {account.credit > 0 ? formatCurrency(account.credit) : '-'}
                      </td>
                    </tr>
                  ))}
                </tbody>
                <tfoot>
                  <tr className="border-t-2 border-primary bg-primary/5">
                    <td colSpan={3} className="py-4 px-4 font-bold text-lg">
                      Total
                    </td>
                    <td className="py-4 px-4 text-right font-mono font-bold text-lg">
                      {formatCurrency(data.total_debit)}
                    </td>
                    <td className="py-4 px-4 text-right font-mono font-bold text-lg">
                      {formatCurrency(data.total_credit)}
                    </td>
                  </tr>
                </tfoot>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
