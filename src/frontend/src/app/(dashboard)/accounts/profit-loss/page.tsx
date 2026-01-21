'use client'

import * as React from 'react'
import { PageHeader } from '@/components/layout/page-header'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { DateRangePicker } from '@/components/forms/date-picker'
import { LoadingSpinner } from '@/components/layout/loading-spinner'
import { EmptyState } from '@/components/layout/empty-state'
import { formatCurrency, formatDate, formatPercentage, getFinancialYear, getMonthName } from '@/lib/format'
import { useApi } from '@/hooks'
import {
  Download,
  FileSpreadsheet,
  FileText,
  Printer,
  RefreshCw,
  TrendingUp,
  TrendingDown,
  ArrowUpRight,
  ArrowDownRight,
  BarChart3,
  PieChart,
  Loader2,
  IndianRupee
} from 'lucide-react'

// ============================================================================
// Types
// ============================================================================

interface ProfitLossLineItem {
  id: string
  code: string
  name: string
  current_amount: number
  previous_amount: number
  variance: number
  variance_percent: number
  category: 'revenue' | 'direct_expense' | 'operating_expense' | 'other_income' | 'other_expense' | 'tax'
  is_total?: boolean
  is_subtotal?: boolean
}

interface ProfitLossData {
  line_items: ProfitLossLineItem[]
  summary: {
    total_revenue: number
    total_expenses: number
    gross_profit: number
    operating_profit: number
    net_profit: number
    gross_margin: number
    operating_margin: number
    net_margin: number
    previous_net_profit: number
    profit_growth: number
  }
  current_period: { start: string; end: string }
  previous_period: { start: string; end: string }
  generated_at: string
}

// ============================================================================
// Mock Data
// ============================================================================

const mockProfitLossData: ProfitLossData = {
  line_items: [
    // Revenue
    { id: 'r1', code: '4100', name: 'Sales Revenue', current_amount: 5500000, previous_amount: 4800000, variance: 700000, variance_percent: 14.58, category: 'revenue' },
    { id: 'r2', code: '4200', name: 'Service Revenue', current_amount: 178900, previous_amount: 150000, variance: 28900, variance_percent: 19.27, category: 'revenue' },
    { id: 'r3', code: '4300', name: 'Commission Income', current_amount: 125000, previous_amount: 98000, variance: 27000, variance_percent: 27.55, category: 'revenue' },
    { id: 'rt', code: '', name: 'Total Revenue', current_amount: 5803900, previous_amount: 5048000, variance: 755900, variance_percent: 14.97, category: 'revenue', is_total: true },

    // Direct Expenses (Cost of Goods Sold)
    { id: 'd1', code: '5010', name: 'Cost of Goods Sold', current_amount: 2750000, previous_amount: 2400000, variance: 350000, variance_percent: 14.58, category: 'direct_expense' },
    { id: 'd2', code: '5020', name: 'Direct Labour', current_amount: 450000, previous_amount: 380000, variance: 70000, variance_percent: 18.42, category: 'direct_expense' },
    { id: 'd3', code: '5030', name: 'Manufacturing Overhead', current_amount: 180000, previous_amount: 165000, variance: 15000, variance_percent: 9.09, category: 'direct_expense' },
    { id: 'dt', code: '', name: 'Total Direct Costs', current_amount: 3380000, previous_amount: 2945000, variance: 435000, variance_percent: 14.77, category: 'direct_expense', is_total: true },

    // Gross Profit (calculated)
    { id: 'gp', code: '', name: 'Gross Profit', current_amount: 2423900, previous_amount: 2103000, variance: 320900, variance_percent: 15.26, category: 'revenue', is_subtotal: true },

    // Operating Expenses
    { id: 'o1', code: '5100', name: 'Salary & Wages', current_amount: 850000, previous_amount: 780000, variance: 70000, variance_percent: 8.97, category: 'operating_expense' },
    { id: 'o2', code: '5200', name: 'Rent Expense', current_amount: 120000, previous_amount: 120000, variance: 0, variance_percent: 0, category: 'operating_expense' },
    { id: 'o3', code: '5300', name: 'Utilities', current_amount: 45000, previous_amount: 42000, variance: 3000, variance_percent: 7.14, category: 'operating_expense' },
    { id: 'o4', code: '5400', name: 'Professional Fees', current_amount: 75000, previous_amount: 68000, variance: 7000, variance_percent: 10.29, category: 'operating_expense' },
    { id: 'o5', code: '5500', name: 'Depreciation', current_amount: 95000, previous_amount: 88000, variance: 7000, variance_percent: 7.95, category: 'operating_expense' },
    { id: 'o6', code: '5600', name: 'Marketing & Advertising', current_amount: 125000, previous_amount: 105000, variance: 20000, variance_percent: 19.05, category: 'operating_expense' },
    { id: 'o7', code: '5700', name: 'Travel & Conveyance', current_amount: 65000, previous_amount: 58000, variance: 7000, variance_percent: 12.07, category: 'operating_expense' },
    { id: 'o8', code: '5800', name: 'Office Supplies', current_amount: 32000, previous_amount: 28000, variance: 4000, variance_percent: 14.29, category: 'operating_expense' },
    { id: 'o9', code: '5900', name: 'Insurance', current_amount: 48000, previous_amount: 45000, variance: 3000, variance_percent: 6.67, category: 'operating_expense' },
    { id: 'o10', code: '5950', name: 'Repairs & Maintenance', current_amount: 38000, previous_amount: 32000, variance: 6000, variance_percent: 18.75, category: 'operating_expense' },
    { id: 'ot', code: '', name: 'Total Operating Expenses', current_amount: 1493000, previous_amount: 1366000, variance: 127000, variance_percent: 9.30, category: 'operating_expense', is_total: true },

    // Operating Profit (calculated)
    { id: 'op', code: '', name: 'Operating Profit (EBITDA)', current_amount: 930900, previous_amount: 737000, variance: 193900, variance_percent: 26.31, category: 'revenue', is_subtotal: true },

    // Other Income
    { id: 'oi1', code: '4500', name: 'Interest Income', current_amount: 45000, previous_amount: 38000, variance: 7000, variance_percent: 18.42, category: 'other_income' },
    { id: 'oi2', code: '4600', name: 'Dividend Income', current_amount: 12000, previous_amount: 10000, variance: 2000, variance_percent: 20.00, category: 'other_income' },
    { id: 'oit', code: '', name: 'Total Other Income', current_amount: 57000, previous_amount: 48000, variance: 9000, variance_percent: 18.75, category: 'other_income', is_total: true },

    // Other Expenses
    { id: 'oe1', code: '5960', name: 'Bank Charges', current_amount: 8500, previous_amount: 7200, variance: 1300, variance_percent: 18.06, category: 'other_expense' },
    { id: 'oe2', code: '5980', name: 'Interest Expense', current_amount: 125000, previous_amount: 138000, variance: -13000, variance_percent: -9.42, category: 'other_expense' },
    { id: 'oet', code: '', name: 'Total Other Expenses', current_amount: 133500, previous_amount: 145200, variance: -11700, variance_percent: -8.06, category: 'other_expense', is_total: true },

    // Profit Before Tax (calculated)
    { id: 'pbt', code: '', name: 'Profit Before Tax', current_amount: 854400, previous_amount: 639800, variance: 214600, variance_percent: 33.54, category: 'revenue', is_subtotal: true },

    // Tax
    { id: 't1', code: '5990', name: 'Income Tax Expense', current_amount: 213600, previous_amount: 159950, variance: 53650, variance_percent: 33.54, category: 'tax' },

    // Net Profit (calculated)
    { id: 'np', code: '', name: 'Net Profit After Tax', current_amount: 640800, previous_amount: 479850, variance: 160950, variance_percent: 33.54, category: 'revenue', is_subtotal: true },
  ],
  summary: {
    total_revenue: 5803900,
    total_expenses: 5163100,
    gross_profit: 2423900,
    operating_profit: 930900,
    net_profit: 640800,
    gross_margin: 41.76,
    operating_margin: 16.04,
    net_margin: 11.04,
    previous_net_profit: 479850,
    profit_growth: 33.54
  },
  current_period: { start: '2024-04-01', end: '2024-12-31' },
  previous_period: { start: '2023-04-01', end: '2023-12-31' },
  generated_at: new Date().toISOString()
}

// ============================================================================
// Component
// ============================================================================

export default function ProfitLossPage() {
  const api = useApi<ProfitLossData>()
  const [data, setData] = React.useState<ProfitLossData | null>(null)
  const [isLoading, setIsLoading] = React.useState(false)
  const [isExporting, setIsExporting] = React.useState(false)
  const [viewMode, setViewMode] = React.useState<'detailed' | 'summary'>('detailed')

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

  // Fetch P&L data
  const fetchProfitLoss = React.useCallback(async () => {
    setIsLoading(true)
    try {
      // In production, this would call the API
      // await api.get(`/accounts/profit-loss?start_date=${startDate}&end_date=${endDate}`)

      // Using mock data for now
      await new Promise(resolve => setTimeout(resolve, 1000))
      setData(mockProfitLossData)
    } catch (error) {
      console.error('Failed to fetch profit & loss:', error)
    } finally {
      setIsLoading(false)
    }
  }, [startDate, endDate])

  // Initial fetch
  React.useEffect(() => {
    fetchProfitLoss()
  }, [])

  // Export handlers
  const handleExport = async (format: 'xlsx' | 'pdf') => {
    setIsExporting(true)
    try {
      // In production, this would call the API
      // await api.get(`/accounts/profit-loss/export?format=${format}&start_date=${startDate}&end_date=${endDate}`)
      await new Promise(resolve => setTimeout(resolve, 1500))
      // Download would be triggered here
    } catch (error) {
      console.error('Export failed:', error)
    } finally {
      setIsExporting(false)
    }
  }

  // Get category color
  const getCategoryColor = (category: string) => {
    const colors: Record<string, string> = {
      revenue: 'text-green-600',
      direct_expense: 'text-red-600',
      operating_expense: 'text-orange-600',
      other_income: 'text-blue-600',
      other_expense: 'text-red-500',
      tax: 'text-purple-600'
    }
    return colors[category] || 'text-gray-600'
  }

  // Get variance indicator
  const getVarianceIndicator = (item: ProfitLossLineItem) => {
    const isExpense = ['direct_expense', 'operating_expense', 'other_expense', 'tax'].includes(item.category)
    const isPositive = item.variance > 0

    // For expenses, positive variance is bad; for revenue/profit, positive is good
    const isGood = isExpense ? !isPositive : isPositive

    if (item.variance === 0) return null

    return (
      <span className={`flex items-center gap-1 text-xs ${isGood ? 'text-green-600' : 'text-red-600'}`}>
        {isPositive ? <ArrowUpRight className="h-3 w-3" /> : <ArrowDownRight className="h-3 w-3" />}
        {formatPercentage(Math.abs(item.variance_percent))}
      </span>
    )
  }

  // Get row items by category
  const getItemsByCategory = (category: string) => {
    return data?.line_items.filter(item => item.category === category && !item.is_total && !item.is_subtotal) || []
  }

  const getCategoryTotal = (category: string) => {
    return data?.line_items.find(item => item.category === category && item.is_total)
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <PageHeader
        title="Profit & Loss Statement"
        description="Revenue, expenses, and profitability analysis"
        breadcrumbs={[
          { label: 'Dashboard', href: '/dashboard' },
          { label: 'Accounts', href: '/accounts' },
          { label: 'Profit & Loss' }
        ]}
        actions={
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={() => fetchProfitLoss()} disabled={isLoading}>
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
              name="pnl-period"
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
              <Button onClick={fetchProfitLoss} disabled={isLoading}>
                {isLoading ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : null}
                Generate Report
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Key Metrics */}
      {data && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Card>
            <CardContent className="pt-4">
              <div className="flex items-center gap-2 mb-1">
                <TrendingUp className="h-4 w-4 text-green-600" />
                <p className="text-sm text-muted-foreground">Total Revenue</p>
              </div>
              <p className="text-xl font-bold text-green-600">{formatCurrency(data.summary.total_revenue)}</p>
              <p className="text-xs text-muted-foreground mt-1">
                vs {formatCurrency(mockProfitLossData.current_period.start === mockProfitLossData.previous_period.start ? 0 : 5048000)} prev
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-4">
              <div className="flex items-center gap-2 mb-1">
                <BarChart3 className="h-4 w-4 text-blue-600" />
                <p className="text-sm text-muted-foreground">Gross Profit</p>
              </div>
              <p className="text-xl font-bold text-blue-600">{formatCurrency(data.summary.gross_profit)}</p>
              <p className="text-xs text-muted-foreground mt-1">
                Margin: {formatPercentage(data.summary.gross_margin)}
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-4">
              <div className="flex items-center gap-2 mb-1">
                <PieChart className="h-4 w-4 text-purple-600" />
                <p className="text-sm text-muted-foreground">Operating Profit</p>
              </div>
              <p className="text-xl font-bold text-purple-600">{formatCurrency(data.summary.operating_profit)}</p>
              <p className="text-xs text-muted-foreground mt-1">
                Margin: {formatPercentage(data.summary.operating_margin)}
              </p>
            </CardContent>
          </Card>
          <Card className={data.summary.net_profit >= 0 ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'}>
            <CardContent className="pt-4">
              <div className="flex items-center gap-2 mb-1">
                <IndianRupee className={`h-4 w-4 ${data.summary.net_profit >= 0 ? 'text-green-600' : 'text-red-600'}`} />
                <p className="text-sm text-muted-foreground">Net Profit</p>
              </div>
              <p className={`text-xl font-bold ${data.summary.net_profit >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {formatCurrency(data.summary.net_profit)}
              </p>
              <div className="flex items-center gap-1 mt-1">
                {data.summary.profit_growth >= 0 ? (
                  <ArrowUpRight className="h-3 w-3 text-green-600" />
                ) : (
                  <ArrowDownRight className="h-3 w-3 text-red-600" />
                )}
                <p className={`text-xs ${data.summary.profit_growth >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {formatPercentage(Math.abs(data.summary.profit_growth))} vs prev
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* P&L Statement */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Profit & Loss Statement</CardTitle>
              <CardDescription>
                Period: {formatDate(startDate, { format: 'long' })} to {formatDate(endDate, { format: 'long' })}
              </CardDescription>
            </div>
            <Tabs value={viewMode} onValueChange={(v) => setViewMode(v as 'detailed' | 'summary')}>
              <TabsList>
                <TabsTrigger value="detailed">Detailed</TabsTrigger>
                <TabsTrigger value="summary">Summary</TabsTrigger>
              </TabsList>
            </Tabs>
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
              description="Select a date range and generate the report to view the profit & loss statement."
            />
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b bg-muted/50">
                    <th className="text-left py-3 px-4 font-medium text-muted-foreground">Particulars</th>
                    <th className="text-right py-3 px-4 font-medium text-muted-foreground">
                      Current Period
                      <span className="block text-xs font-normal">
                        {formatDate(data.current_period.start)} - {formatDate(data.current_period.end)}
                      </span>
                    </th>
                    <th className="text-right py-3 px-4 font-medium text-muted-foreground">
                      Previous Period
                      <span className="block text-xs font-normal">
                        {formatDate(data.previous_period.start)} - {formatDate(data.previous_period.end)}
                      </span>
                    </th>
                    <th className="text-right py-3 px-4 font-medium text-muted-foreground">Variance</th>
                    <th className="text-center py-3 px-4 font-medium text-muted-foreground">Change</th>
                  </tr>
                </thead>
                <tbody>
                  {/* Revenue Section */}
                  <tr className="bg-green-50">
                    <td colSpan={5} className="py-2 px-4 font-semibold text-green-800">
                      Revenue
                    </td>
                  </tr>
                  {getItemsByCategory('revenue').map((item) => (
                    <tr key={item.id} className="border-b hover:bg-muted/30">
                      <td className="py-3 px-4 pl-8">{item.name}</td>
                      <td className="py-3 px-4 text-right font-mono">{formatCurrency(item.current_amount)}</td>
                      <td className="py-3 px-4 text-right font-mono text-muted-foreground">{formatCurrency(item.previous_amount)}</td>
                      <td className="py-3 px-4 text-right font-mono">
                        <span className={item.variance >= 0 ? 'text-green-600' : 'text-red-600'}>
                          {item.variance >= 0 ? '+' : ''}{formatCurrency(item.variance)}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-center">{getVarianceIndicator(item)}</td>
                    </tr>
                  ))}
                  {getCategoryTotal('revenue') && (
                    <tr className="border-b bg-green-100 font-semibold">
                      <td className="py-3 px-4">{getCategoryTotal('revenue')?.name}</td>
                      <td className="py-3 px-4 text-right font-mono">{formatCurrency(getCategoryTotal('revenue')?.current_amount || 0)}</td>
                      <td className="py-3 px-4 text-right font-mono text-muted-foreground">{formatCurrency(getCategoryTotal('revenue')?.previous_amount || 0)}</td>
                      <td className="py-3 px-4 text-right font-mono">
                        <span className={(getCategoryTotal('revenue')?.variance || 0) >= 0 ? 'text-green-600' : 'text-red-600'}>
                          {(getCategoryTotal('revenue')?.variance || 0) >= 0 ? '+' : ''}{formatCurrency(getCategoryTotal('revenue')?.variance || 0)}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-center">{getCategoryTotal('revenue') && getVarianceIndicator(getCategoryTotal('revenue')!)}</td>
                    </tr>
                  )}

                  {/* Direct Costs Section */}
                  <tr className="bg-red-50">
                    <td colSpan={5} className="py-2 px-4 font-semibold text-red-800">
                      Less: Cost of Goods Sold
                    </td>
                  </tr>
                  {getItemsByCategory('direct_expense').map((item) => (
                    <tr key={item.id} className="border-b hover:bg-muted/30">
                      <td className="py-3 px-4 pl-8">{item.name}</td>
                      <td className="py-3 px-4 text-right font-mono">{formatCurrency(item.current_amount)}</td>
                      <td className="py-3 px-4 text-right font-mono text-muted-foreground">{formatCurrency(item.previous_amount)}</td>
                      <td className="py-3 px-4 text-right font-mono">
                        <span className={item.variance <= 0 ? 'text-green-600' : 'text-red-600'}>
                          {item.variance >= 0 ? '+' : ''}{formatCurrency(item.variance)}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-center">{getVarianceIndicator(item)}</td>
                    </tr>
                  ))}
                  {getCategoryTotal('direct_expense') && (
                    <tr className="border-b bg-red-100 font-semibold">
                      <td className="py-3 px-4">{getCategoryTotal('direct_expense')?.name}</td>
                      <td className="py-3 px-4 text-right font-mono">{formatCurrency(getCategoryTotal('direct_expense')?.current_amount || 0)}</td>
                      <td className="py-3 px-4 text-right font-mono text-muted-foreground">{formatCurrency(getCategoryTotal('direct_expense')?.previous_amount || 0)}</td>
                      <td className="py-3 px-4 text-right font-mono">
                        <span className={(getCategoryTotal('direct_expense')?.variance || 0) <= 0 ? 'text-green-600' : 'text-red-600'}>
                          {(getCategoryTotal('direct_expense')?.variance || 0) >= 0 ? '+' : ''}{formatCurrency(getCategoryTotal('direct_expense')?.variance || 0)}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-center">{getCategoryTotal('direct_expense') && getVarianceIndicator(getCategoryTotal('direct_expense')!)}</td>
                    </tr>
                  )}

                  {/* Gross Profit */}
                  {data.line_items.find(i => i.id === 'gp') && (
                    <tr className="bg-blue-100 font-bold border-y-2 border-blue-300">
                      <td className="py-4 px-4">Gross Profit</td>
                      <td className="py-4 px-4 text-right font-mono text-blue-700">{formatCurrency(data.summary.gross_profit)}</td>
                      <td className="py-4 px-4 text-right font-mono text-muted-foreground">{formatCurrency(data.line_items.find(i => i.id === 'gp')?.previous_amount || 0)}</td>
                      <td className="py-4 px-4 text-right font-mono">
                        <span className="text-green-600">+{formatCurrency(data.line_items.find(i => i.id === 'gp')?.variance || 0)}</span>
                      </td>
                      <td className="py-4 px-4 text-center">
                        <Badge variant="outline" className="text-blue-600">
                          {formatPercentage(data.summary.gross_margin)} margin
                        </Badge>
                      </td>
                    </tr>
                  )}

                  {/* Operating Expenses Section */}
                  <tr className="bg-orange-50">
                    <td colSpan={5} className="py-2 px-4 font-semibold text-orange-800">
                      Less: Operating Expenses
                    </td>
                  </tr>
                  {viewMode === 'detailed' && getItemsByCategory('operating_expense').map((item) => (
                    <tr key={item.id} className="border-b hover:bg-muted/30">
                      <td className="py-3 px-4 pl-8">{item.name}</td>
                      <td className="py-3 px-4 text-right font-mono">{formatCurrency(item.current_amount)}</td>
                      <td className="py-3 px-4 text-right font-mono text-muted-foreground">{formatCurrency(item.previous_amount)}</td>
                      <td className="py-3 px-4 text-right font-mono">
                        <span className={item.variance <= 0 ? 'text-green-600' : 'text-red-600'}>
                          {item.variance >= 0 ? '+' : ''}{formatCurrency(item.variance)}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-center">{getVarianceIndicator(item)}</td>
                    </tr>
                  ))}
                  {getCategoryTotal('operating_expense') && (
                    <tr className="border-b bg-orange-100 font-semibold">
                      <td className="py-3 px-4">{getCategoryTotal('operating_expense')?.name}</td>
                      <td className="py-3 px-4 text-right font-mono">{formatCurrency(getCategoryTotal('operating_expense')?.current_amount || 0)}</td>
                      <td className="py-3 px-4 text-right font-mono text-muted-foreground">{formatCurrency(getCategoryTotal('operating_expense')?.previous_amount || 0)}</td>
                      <td className="py-3 px-4 text-right font-mono">
                        <span className={(getCategoryTotal('operating_expense')?.variance || 0) <= 0 ? 'text-green-600' : 'text-red-600'}>
                          {(getCategoryTotal('operating_expense')?.variance || 0) >= 0 ? '+' : ''}{formatCurrency(getCategoryTotal('operating_expense')?.variance || 0)}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-center">{getCategoryTotal('operating_expense') && getVarianceIndicator(getCategoryTotal('operating_expense')!)}</td>
                    </tr>
                  )}

                  {/* Operating Profit */}
                  {data.line_items.find(i => i.id === 'op') && (
                    <tr className="bg-purple-100 font-bold border-y-2 border-purple-300">
                      <td className="py-4 px-4">Operating Profit (EBITDA)</td>
                      <td className="py-4 px-4 text-right font-mono text-purple-700">{formatCurrency(data.summary.operating_profit)}</td>
                      <td className="py-4 px-4 text-right font-mono text-muted-foreground">{formatCurrency(data.line_items.find(i => i.id === 'op')?.previous_amount || 0)}</td>
                      <td className="py-4 px-4 text-right font-mono">
                        <span className="text-green-600">+{formatCurrency(data.line_items.find(i => i.id === 'op')?.variance || 0)}</span>
                      </td>
                      <td className="py-4 px-4 text-center">
                        <Badge variant="outline" className="text-purple-600">
                          {formatPercentage(data.summary.operating_margin)} margin
                        </Badge>
                      </td>
                    </tr>
                  )}

                  {/* Other Income */}
                  <tr className="bg-blue-50">
                    <td colSpan={5} className="py-2 px-4 font-semibold text-blue-800">
                      Add: Other Income
                    </td>
                  </tr>
                  {viewMode === 'detailed' && getItemsByCategory('other_income').map((item) => (
                    <tr key={item.id} className="border-b hover:bg-muted/30">
                      <td className="py-3 px-4 pl-8">{item.name}</td>
                      <td className="py-3 px-4 text-right font-mono">{formatCurrency(item.current_amount)}</td>
                      <td className="py-3 px-4 text-right font-mono text-muted-foreground">{formatCurrency(item.previous_amount)}</td>
                      <td className="py-3 px-4 text-right font-mono">
                        <span className={item.variance >= 0 ? 'text-green-600' : 'text-red-600'}>
                          {item.variance >= 0 ? '+' : ''}{formatCurrency(item.variance)}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-center">{getVarianceIndicator(item)}</td>
                    </tr>
                  ))}
                  {getCategoryTotal('other_income') && (
                    <tr className="border-b bg-blue-100 font-semibold">
                      <td className="py-3 px-4">{getCategoryTotal('other_income')?.name}</td>
                      <td className="py-3 px-4 text-right font-mono">{formatCurrency(getCategoryTotal('other_income')?.current_amount || 0)}</td>
                      <td className="py-3 px-4 text-right font-mono text-muted-foreground">{formatCurrency(getCategoryTotal('other_income')?.previous_amount || 0)}</td>
                      <td className="py-3 px-4 text-right font-mono">
                        <span className={(getCategoryTotal('other_income')?.variance || 0) >= 0 ? 'text-green-600' : 'text-red-600'}>
                          {(getCategoryTotal('other_income')?.variance || 0) >= 0 ? '+' : ''}{formatCurrency(getCategoryTotal('other_income')?.variance || 0)}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-center">{getCategoryTotal('other_income') && getVarianceIndicator(getCategoryTotal('other_income')!)}</td>
                    </tr>
                  )}

                  {/* Other Expenses */}
                  <tr className="bg-red-50">
                    <td colSpan={5} className="py-2 px-4 font-semibold text-red-800">
                      Less: Other Expenses
                    </td>
                  </tr>
                  {viewMode === 'detailed' && getItemsByCategory('other_expense').map((item) => (
                    <tr key={item.id} className="border-b hover:bg-muted/30">
                      <td className="py-3 px-4 pl-8">{item.name}</td>
                      <td className="py-3 px-4 text-right font-mono">{formatCurrency(item.current_amount)}</td>
                      <td className="py-3 px-4 text-right font-mono text-muted-foreground">{formatCurrency(item.previous_amount)}</td>
                      <td className="py-3 px-4 text-right font-mono">
                        <span className={item.variance <= 0 ? 'text-green-600' : 'text-red-600'}>
                          {item.variance >= 0 ? '+' : ''}{formatCurrency(item.variance)}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-center">{getVarianceIndicator(item)}</td>
                    </tr>
                  ))}
                  {getCategoryTotal('other_expense') && (
                    <tr className="border-b bg-red-100 font-semibold">
                      <td className="py-3 px-4">{getCategoryTotal('other_expense')?.name}</td>
                      <td className="py-3 px-4 text-right font-mono">{formatCurrency(getCategoryTotal('other_expense')?.current_amount || 0)}</td>
                      <td className="py-3 px-4 text-right font-mono text-muted-foreground">{formatCurrency(getCategoryTotal('other_expense')?.previous_amount || 0)}</td>
                      <td className="py-3 px-4 text-right font-mono">
                        <span className={(getCategoryTotal('other_expense')?.variance || 0) <= 0 ? 'text-green-600' : 'text-red-600'}>
                          {(getCategoryTotal('other_expense')?.variance || 0) >= 0 ? '+' : ''}{formatCurrency(getCategoryTotal('other_expense')?.variance || 0)}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-center">{getCategoryTotal('other_expense') && getVarianceIndicator(getCategoryTotal('other_expense')!)}</td>
                    </tr>
                  )}

                  {/* Profit Before Tax */}
                  {data.line_items.find(i => i.id === 'pbt') && (
                    <tr className="bg-amber-100 font-bold border-y-2 border-amber-300">
                      <td className="py-4 px-4">Profit Before Tax</td>
                      <td className="py-4 px-4 text-right font-mono text-amber-700">{formatCurrency(data.line_items.find(i => i.id === 'pbt')?.current_amount || 0)}</td>
                      <td className="py-4 px-4 text-right font-mono text-muted-foreground">{formatCurrency(data.line_items.find(i => i.id === 'pbt')?.previous_amount || 0)}</td>
                      <td className="py-4 px-4 text-right font-mono">
                        <span className="text-green-600">+{formatCurrency(data.line_items.find(i => i.id === 'pbt')?.variance || 0)}</span>
                      </td>
                      <td className="py-4 px-4 text-center">
                        {getVarianceIndicator(data.line_items.find(i => i.id === 'pbt')!)}
                      </td>
                    </tr>
                  )}

                  {/* Tax */}
                  <tr className="bg-purple-50">
                    <td colSpan={5} className="py-2 px-4 font-semibold text-purple-800">
                      Less: Income Tax
                    </td>
                  </tr>
                  {getItemsByCategory('tax').map((item) => (
                    <tr key={item.id} className="border-b hover:bg-muted/30">
                      <td className="py-3 px-4 pl-8">{item.name}</td>
                      <td className="py-3 px-4 text-right font-mono">{formatCurrency(item.current_amount)}</td>
                      <td className="py-3 px-4 text-right font-mono text-muted-foreground">{formatCurrency(item.previous_amount)}</td>
                      <td className="py-3 px-4 text-right font-mono">
                        <span className={item.variance <= 0 ? 'text-green-600' : 'text-red-600'}>
                          {item.variance >= 0 ? '+' : ''}{formatCurrency(item.variance)}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-center">{getVarianceIndicator(item)}</td>
                    </tr>
                  ))}

                  {/* Net Profit */}
                  <tr className={`font-bold border-t-4 ${data.summary.net_profit >= 0 ? 'bg-green-200 border-green-400' : 'bg-red-200 border-red-400'}`}>
                    <td className="py-4 px-4 text-lg">Net Profit After Tax</td>
                    <td className={`py-4 px-4 text-right font-mono text-lg ${data.summary.net_profit >= 0 ? 'text-green-700' : 'text-red-700'}`}>
                      {formatCurrency(data.summary.net_profit)}
                    </td>
                    <td className="py-4 px-4 text-right font-mono text-muted-foreground">{formatCurrency(data.summary.previous_net_profit)}</td>
                    <td className="py-4 px-4 text-right font-mono">
                      <span className={data.summary.net_profit - data.summary.previous_net_profit >= 0 ? 'text-green-600' : 'text-red-600'}>
                        {data.summary.net_profit - data.summary.previous_net_profit >= 0 ? '+' : ''}
                        {formatCurrency(data.summary.net_profit - data.summary.previous_net_profit)}
                      </span>
                    </td>
                    <td className="py-4 px-4 text-center">
                      <Badge variant="outline" className={data.summary.net_profit >= 0 ? 'text-green-600' : 'text-red-600'}>
                        {formatPercentage(data.summary.net_margin)} margin
                      </Badge>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
