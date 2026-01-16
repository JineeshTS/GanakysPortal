'use client'

import * as React from 'react'
import { PageHeader } from '@/components/layout/page-header'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { DatePicker } from '@/components/forms/date-picker'
import { LoadingSpinner } from '@/components/layout/loading-spinner'
import { EmptyState } from '@/components/layout/empty-state'
import { formatCurrency, formatDate, formatPercentage, getFinancialYear } from '@/lib/format'
import { useApi } from '@/hooks'
import {
  Download,
  FileSpreadsheet,
  FileText,
  Printer,
  RefreshCw,
  TrendingUp,
  TrendingDown,
  Building2,
  Wallet,
  CreditCard,
  Scale,
  ArrowUpRight,
  ArrowDownRight,
  CheckCircle2,
  AlertCircle,
  Loader2,
  ChevronRight,
  ChevronDown
} from 'lucide-react'

// ============================================================================
// Types
// ============================================================================

interface BalanceSheetLineItem {
  id: string
  code: string
  name: string
  current_amount: number
  previous_amount: number
  variance: number
  variance_percent: number
  category: 'current_asset' | 'non_current_asset' | 'current_liability' | 'non_current_liability' | 'equity'
  parent_id?: string
  level: number
  is_total?: boolean
  is_subtotal?: boolean
}

interface BalanceSheetData {
  line_items: BalanceSheetLineItem[]
  summary: {
    total_assets: number
    total_current_assets: number
    total_non_current_assets: number
    total_liabilities: number
    total_current_liabilities: number
    total_non_current_liabilities: number
    total_equity: number
    net_worth: number
    working_capital: number
    current_ratio: number
    debt_to_equity: number
    is_balanced: boolean
  }
  previous_summary: {
    total_assets: number
    total_liabilities: number
    total_equity: number
  }
  as_of_date: string
  previous_as_of_date: string
  generated_at: string
}

// ============================================================================
// Mock Data
// ============================================================================

const mockBalanceSheetData: BalanceSheetData = {
  line_items: [
    // Current Assets
    { id: 'ca', code: '1100', name: 'Current Assets', current_amount: 3956780, previous_amount: 3245000, variance: 711780, variance_percent: 21.93, category: 'current_asset', level: 0, is_subtotal: true },
    { id: 'ca1', code: '1110', name: 'Cash and Cash Equivalents', current_amount: 125000, previous_amount: 95000, variance: 30000, variance_percent: 31.58, category: 'current_asset', parent_id: 'ca', level: 1 },
    { id: 'ca2', code: '1120', name: 'Bank Accounts', current_amount: 2345780, previous_amount: 1850000, variance: 495780, variance_percent: 26.80, category: 'current_asset', parent_id: 'ca', level: 1 },
    { id: 'ca2-1', code: '1121', name: 'HDFC Bank - Current A/c', current_amount: 1845780, previous_amount: 1450000, variance: 395780, variance_percent: 27.30, category: 'current_asset', parent_id: 'ca2', level: 2 },
    { id: 'ca2-2', code: '1122', name: 'ICICI Bank - Salary A/c', current_amount: 500000, previous_amount: 400000, variance: 100000, variance_percent: 25.00, category: 'current_asset', parent_id: 'ca2', level: 2 },
    { id: 'ca3', code: '1130', name: 'Accounts Receivable', current_amount: 986000, previous_amount: 850000, variance: 136000, variance_percent: 16.00, category: 'current_asset', parent_id: 'ca', level: 1 },
    { id: 'ca4', code: '1140', name: 'Inventory', current_amount: 350000, previous_amount: 320000, variance: 30000, variance_percent: 9.38, category: 'current_asset', parent_id: 'ca', level: 1 },
    { id: 'ca5', code: '1150', name: 'Prepaid Expenses', current_amount: 150000, previous_amount: 130000, variance: 20000, variance_percent: 15.38, category: 'current_asset', parent_id: 'ca', level: 1 },

    // Non-Current Assets
    { id: 'nca', code: '1200', name: 'Non-Current Assets', current_amount: 1611110, previous_amount: 1450000, variance: 161110, variance_percent: 11.11, category: 'non_current_asset', level: 0, is_subtotal: true },
    { id: 'nca1', code: '1210', name: 'Property, Plant & Equipment', current_amount: 1111110, previous_amount: 1050000, variance: 61110, variance_percent: 5.82, category: 'non_current_asset', parent_id: 'nca', level: 1 },
    { id: 'nca1-1', code: '1211', name: 'Furniture & Fixtures', current_amount: 345000, previous_amount: 320000, variance: 25000, variance_percent: 7.81, category: 'non_current_asset', parent_id: 'nca1', level: 2 },
    { id: 'nca1-2', code: '1212', name: 'Computer Equipment', current_amount: 766110, previous_amount: 730000, variance: 36110, variance_percent: 4.95, category: 'non_current_asset', parent_id: 'nca1', level: 2 },
    { id: 'nca2', code: '1220', name: 'Intangible Assets', current_amount: 250000, previous_amount: 200000, variance: 50000, variance_percent: 25.00, category: 'non_current_asset', parent_id: 'nca', level: 1 },
    { id: 'nca3', code: '1230', name: 'Long-term Investments', current_amount: 250000, previous_amount: 200000, variance: 50000, variance_percent: 25.00, category: 'non_current_asset', parent_id: 'nca', level: 1 },

    // Total Assets
    { id: 'ta', code: '', name: 'Total Assets', current_amount: 5567890, previous_amount: 4695000, variance: 872890, variance_percent: 18.59, category: 'current_asset', level: 0, is_total: true },

    // Current Liabilities
    { id: 'cl', code: '2100', name: 'Current Liabilities', current_amount: 1234560, previous_amount: 1050000, variance: 184560, variance_percent: 17.58, category: 'current_liability', level: 0, is_subtotal: true },
    { id: 'cl1', code: '2110', name: 'Accounts Payable', current_amount: 567890, previous_amount: 480000, variance: 87890, variance_percent: 18.31, category: 'current_liability', parent_id: 'cl', level: 1 },
    { id: 'cl2', code: '2120', name: 'Statutory Dues', current_amount: 456670, previous_amount: 380000, variance: 76670, variance_percent: 20.18, category: 'current_liability', parent_id: 'cl', level: 1 },
    { id: 'cl2-1', code: '2121', name: 'GST Payable', current_amount: 189000, previous_amount: 150000, variance: 39000, variance_percent: 26.00, category: 'current_liability', parent_id: 'cl2', level: 2 },
    { id: 'cl2-2', code: '2122', name: 'TDS Payable', current_amount: 156200, previous_amount: 130000, variance: 26200, variance_percent: 20.15, category: 'current_liability', parent_id: 'cl2', level: 2 },
    { id: 'cl2-3', code: '2123', name: 'PF Payable', current_amount: 111470, previous_amount: 100000, variance: 11470, variance_percent: 11.47, category: 'current_liability', parent_id: 'cl2', level: 2 },
    { id: 'cl3', code: '2130', name: 'Salary Payable', current_amount: 210000, previous_amount: 190000, variance: 20000, variance_percent: 10.53, category: 'current_liability', parent_id: 'cl', level: 1 },

    // Non-Current Liabilities
    { id: 'ncl', code: '2200', name: 'Non-Current Liabilities', current_amount: 500000, previous_amount: 600000, variance: -100000, variance_percent: -16.67, category: 'non_current_liability', level: 0, is_subtotal: true },
    { id: 'ncl1', code: '2210', name: 'Long-term Loans', current_amount: 350000, previous_amount: 450000, variance: -100000, variance_percent: -22.22, category: 'non_current_liability', parent_id: 'ncl', level: 1 },
    { id: 'ncl2', code: '2220', name: 'Deferred Tax Liability', current_amount: 150000, previous_amount: 150000, variance: 0, variance_percent: 0, category: 'non_current_liability', parent_id: 'ncl', level: 1 },

    // Total Liabilities
    { id: 'tl', code: '', name: 'Total Liabilities', current_amount: 1734560, previous_amount: 1650000, variance: 84560, variance_percent: 5.13, category: 'current_liability', level: 0, is_total: true },

    // Equity
    { id: 'eq', code: '3000', name: "Shareholders' Equity", current_amount: 3833330, previous_amount: 3045000, variance: 788330, variance_percent: 25.89, category: 'equity', level: 0, is_subtotal: true },
    { id: 'eq1', code: '3100', name: 'Share Capital', current_amount: 1000000, previous_amount: 1000000, variance: 0, variance_percent: 0, category: 'equity', parent_id: 'eq', level: 1 },
    { id: 'eq1-1', code: '3110', name: 'Authorized Capital', current_amount: 2000000, previous_amount: 2000000, variance: 0, variance_percent: 0, category: 'equity', parent_id: 'eq1', level: 2 },
    { id: 'eq1-2', code: '3120', name: 'Paid-up Capital', current_amount: 1000000, previous_amount: 1000000, variance: 0, variance_percent: 0, category: 'equity', parent_id: 'eq1', level: 2 },
    { id: 'eq2', code: '3200', name: 'Reserves & Surplus', current_amount: 2833330, previous_amount: 2045000, variance: 788330, variance_percent: 38.55, category: 'equity', parent_id: 'eq', level: 1 },
    { id: 'eq2-1', code: '3210', name: 'Retained Earnings', current_amount: 2192530, previous_amount: 1565150, variance: 627380, variance_percent: 40.08, category: 'equity', parent_id: 'eq2', level: 2 },
    { id: 'eq2-2', code: '3220', name: 'Current Year Profit', current_amount: 640800, previous_amount: 479850, variance: 160950, variance_percent: 33.54, category: 'equity', parent_id: 'eq2', level: 2 },

    // Total Equity
    { id: 'te', code: '', name: 'Total Equity', current_amount: 3833330, previous_amount: 3045000, variance: 788330, variance_percent: 25.89, category: 'equity', level: 0, is_total: true },

    // Total Liabilities & Equity
    { id: 'tle', code: '', name: 'Total Liabilities & Equity', current_amount: 5567890, previous_amount: 4695000, variance: 872890, variance_percent: 18.59, category: 'equity', level: 0, is_total: true },
  ],
  summary: {
    total_assets: 5567890,
    total_current_assets: 3956780,
    total_non_current_assets: 1611110,
    total_liabilities: 1734560,
    total_current_liabilities: 1234560,
    total_non_current_liabilities: 500000,
    total_equity: 3833330,
    net_worth: 3833330,
    working_capital: 2722220, // Current Assets - Current Liabilities
    current_ratio: 3.21, // Current Assets / Current Liabilities
    debt_to_equity: 0.45, // Total Liabilities / Total Equity
    is_balanced: true
  },
  previous_summary: {
    total_assets: 4695000,
    total_liabilities: 1650000,
    total_equity: 3045000
  },
  as_of_date: '2024-12-31',
  previous_as_of_date: '2023-12-31',
  generated_at: new Date().toISOString()
}

// ============================================================================
// Component
// ============================================================================

export default function BalanceSheetPage() {
  const api = useApi<BalanceSheetData>()
  const [data, setData] = React.useState<BalanceSheetData | null>(null)
  const [isLoading, setIsLoading] = React.useState(false)
  const [isExporting, setIsExporting] = React.useState(false)
  const [viewMode, setViewMode] = React.useState<'detailed' | 'summary'>('detailed')
  const [expandedSections, setExpandedSections] = React.useState<Set<string>>(
    new Set(['ca', 'nca', 'cl', 'ncl', 'eq'])
  )

  // Date state
  const currentDate = new Date()
  const [asOfDate, setAsOfDate] = React.useState(
    currentDate.toISOString().split('T')[0]
  )

  // Toggle section expansion
  const toggleSection = (id: string) => {
    setExpandedSections(prev => {
      const next = new Set(prev)
      if (next.has(id)) {
        next.delete(id)
      } else {
        next.add(id)
      }
      return next
    })
  }

  // Fetch balance sheet data
  const fetchBalanceSheet = React.useCallback(async () => {
    setIsLoading(true)
    try {
      // In production, this would call the API
      // await api.get(`/accounts/balance-sheet?as_of_date=${asOfDate}`)

      // Using mock data for now
      await new Promise(resolve => setTimeout(resolve, 1000))
      setData(mockBalanceSheetData)
    } catch (error) {
      console.error('Failed to fetch balance sheet:', error)
    } finally {
      setIsLoading(false)
    }
  }, [asOfDate])

  // Initial fetch
  React.useEffect(() => {
    fetchBalanceSheet()
  }, [])

  // Export handlers
  const handleExport = async (format: 'xlsx' | 'pdf') => {
    setIsExporting(true)
    try {
      // In production, this would call the API
      // await api.get(`/accounts/balance-sheet/export?format=${format}&as_of_date=${asOfDate}`)
      await new Promise(resolve => setTimeout(resolve, 1500))
      // Download would be triggered here
    } catch (error) {
      console.error('Export failed:', error)
    } finally {
      setIsExporting(false)
    }
  }

  // Get category icon
  const getCategoryIcon = (category: string) => {
    const icons: Record<string, React.ElementType> = {
      current_asset: Wallet,
      non_current_asset: Building2,
      current_liability: CreditCard,
      non_current_liability: CreditCard,
      equity: Scale
    }
    return icons[category] || Building2
  }

  // Get category color
  const getCategoryColor = (category: string) => {
    const colors: Record<string, string> = {
      current_asset: 'text-blue-600',
      non_current_asset: 'text-indigo-600',
      current_liability: 'text-red-600',
      non_current_liability: 'text-red-500',
      equity: 'text-purple-600'
    }
    return colors[category] || 'text-gray-600'
  }

  // Get variance indicator
  const getVarianceIndicator = (item: BalanceSheetLineItem) => {
    const isLiability = ['current_liability', 'non_current_liability'].includes(item.category)
    const isPositive = item.variance > 0

    // For assets/equity, positive variance is good; for liabilities, negative is good
    const isGood = isLiability ? !isPositive : isPositive

    if (item.variance === 0) return null

    return (
      <span className={`flex items-center gap-1 text-xs ${isGood ? 'text-green-600' : 'text-red-600'}`}>
        {isPositive ? <ArrowUpRight className="h-3 w-3" /> : <ArrowDownRight className="h-3 w-3" />}
        {formatPercentage(Math.abs(item.variance_percent))}
      </span>
    )
  }

  // Filter items by category
  const getItemsByCategory = (category: string) => {
    return data?.line_items.filter(
      item => item.category === category && !item.is_total && !item.is_subtotal
    ) || []
  }

  const getCategorySubtotal = (category: string) => {
    return data?.line_items.find(item => item.category === category && item.is_subtotal)
  }

  // Check if an item should be visible based on expansion state
  const isItemVisible = (item: BalanceSheetLineItem) => {
    if (item.level === 0) return true
    if (item.level === 1) {
      // Check if parent (level 0) is expanded
      const parent = data?.line_items.find(i => i.is_subtotal && i.category === item.category)
      return parent ? expandedSections.has(parent.id) : true
    }
    if (item.level === 2) {
      // Check if parent (level 1) is expanded
      const parent = data?.line_items.find(i => i.id === item.parent_id)
      return parent ? expandedSections.has(parent.id) : true
    }
    return true
  }

  // Render a section of the balance sheet
  const renderSection = (
    title: string,
    category: string | string[],
    bgColor: string,
    textColor: string
  ) => {
    const categories = Array.isArray(category) ? category : [category]
    const items = data?.line_items.filter(
      item => categories.includes(item.category) && !item.is_total
    ) || []

    return (
      <>
        <tr className={bgColor}>
          <td colSpan={5} className={`py-2 px-4 font-semibold ${textColor}`}>
            {title}
          </td>
        </tr>
        {items.filter(isItemVisible).map((item) => {
          const hasChildren = data?.line_items.some(i => i.parent_id === item.id)
          const isExpanded = expandedSections.has(item.id)

          return (
            <tr
              key={item.id}
              className={`border-b hover:bg-muted/30 ${item.is_subtotal ? 'font-semibold bg-muted/50' : ''}`}
            >
              <td className="py-3 px-4">
                <div
                  className="flex items-center gap-2 cursor-pointer"
                  style={{ paddingLeft: `${item.level * 20}px` }}
                  onClick={() => hasChildren && toggleSection(item.id)}
                >
                  {hasChildren && (
                    <span className="text-muted-foreground">
                      {isExpanded ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
                    </span>
                  )}
                  {item.code && <span className="font-mono text-xs text-muted-foreground">{item.code}</span>}
                  <span>{item.name}</span>
                </div>
              </td>
              <td className="py-3 px-4 text-right font-mono">
                {formatCurrency(item.current_amount)}
              </td>
              <td className="py-3 px-4 text-right font-mono text-muted-foreground">
                {formatCurrency(item.previous_amount)}
              </td>
              <td className="py-3 px-4 text-right font-mono">
                <span className={item.variance >= 0 ? 'text-green-600' : 'text-red-600'}>
                  {item.variance >= 0 ? '+' : ''}{formatCurrency(item.variance)}
                </span>
              </td>
              <td className="py-3 px-4 text-center">
                {getVarianceIndicator(item)}
              </td>
            </tr>
          )
        })}
      </>
    )
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <PageHeader
        title="Balance Sheet"
        description="Assets, liabilities, and equity position"
        breadcrumbs={[
          { label: 'Dashboard', href: '/dashboard' },
          { label: 'Accounts', href: '/accounts' },
          { label: 'Balance Sheet' }
        ]}
        actions={
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={() => fetchBalanceSheet()} disabled={isLoading}>
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

      {/* Date Selection */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col md:flex-row md:items-end md:justify-between gap-4">
            <DatePicker
              label="As of Date"
              name="balance-sheet-date"
              value={asOfDate}
              onChange={setAsOfDate}
            />
            <div className="flex items-center gap-4">
              <div className="text-right">
                <p className="text-sm text-muted-foreground">Financial Year</p>
                <p className="font-semibold">{getFinancialYear(new Date(asOfDate))}</p>
              </div>
              <Button onClick={fetchBalanceSheet} disabled={isLoading}>
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
                <TrendingUp className="h-4 w-4 text-blue-600" />
                <p className="text-sm text-muted-foreground">Total Assets</p>
              </div>
              <p className="text-xl font-bold text-blue-600">{formatCurrency(data.summary.total_assets)}</p>
              <div className="flex items-center gap-1 mt-1">
                <ArrowUpRight className="h-3 w-3 text-green-600" />
                <p className="text-xs text-green-600">
                  +{formatPercentage(((data.summary.total_assets - data.previous_summary.total_assets) / data.previous_summary.total_assets) * 100)} vs prev
                </p>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-4">
              <div className="flex items-center gap-2 mb-1">
                <TrendingDown className="h-4 w-4 text-red-600" />
                <p className="text-sm text-muted-foreground">Total Liabilities</p>
              </div>
              <p className="text-xl font-bold text-red-600">{formatCurrency(data.summary.total_liabilities)}</p>
              <div className="flex items-center gap-1 mt-1">
                <ArrowUpRight className="h-3 w-3 text-red-600" />
                <p className="text-xs text-red-600">
                  +{formatPercentage(((data.summary.total_liabilities - data.previous_summary.total_liabilities) / data.previous_summary.total_liabilities) * 100)} vs prev
                </p>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-4">
              <div className="flex items-center gap-2 mb-1">
                <Scale className="h-4 w-4 text-purple-600" />
                <p className="text-sm text-muted-foreground">Total Equity</p>
              </div>
              <p className="text-xl font-bold text-purple-600">{formatCurrency(data.summary.total_equity)}</p>
              <div className="flex items-center gap-1 mt-1">
                <ArrowUpRight className="h-3 w-3 text-green-600" />
                <p className="text-xs text-green-600">
                  +{formatPercentage(((data.summary.total_equity - data.previous_summary.total_equity) / data.previous_summary.total_equity) * 100)} vs prev
                </p>
              </div>
            </CardContent>
          </Card>
          <Card className="bg-green-50 border-green-200">
            <CardContent className="pt-4">
              <div className="flex items-center gap-2 mb-1">
                <Wallet className="h-4 w-4 text-green-600" />
                <p className="text-sm text-muted-foreground">Working Capital</p>
              </div>
              <p className="text-xl font-bold text-green-600">{formatCurrency(data.summary.working_capital)}</p>
              <p className="text-xs text-muted-foreground mt-1">
                Current Ratio: {data.summary.current_ratio.toFixed(2)}x
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Financial Ratios */}
      {data && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card>
            <CardContent className="pt-4">
              <div className="flex justify-between items-center">
                <div>
                  <p className="text-sm text-muted-foreground">Current Ratio</p>
                  <p className="text-2xl font-bold">{data.summary.current_ratio.toFixed(2)}x</p>
                </div>
                <Badge variant={data.summary.current_ratio >= 1.5 ? 'default' : 'destructive'} className={data.summary.current_ratio >= 1.5 ? 'bg-green-100 text-green-800' : ''}>
                  {data.summary.current_ratio >= 1.5 ? 'Healthy' : 'Low'}
                </Badge>
              </div>
              <p className="text-xs text-muted-foreground mt-2">
                Current Assets / Current Liabilities
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="pt-4">
              <div className="flex justify-between items-center">
                <div>
                  <p className="text-sm text-muted-foreground">Debt to Equity</p>
                  <p className="text-2xl font-bold">{data.summary.debt_to_equity.toFixed(2)}x</p>
                </div>
                <Badge variant={data.summary.debt_to_equity <= 1 ? 'default' : 'destructive'} className={data.summary.debt_to_equity <= 1 ? 'bg-green-100 text-green-800' : ''}>
                  {data.summary.debt_to_equity <= 1 ? 'Conservative' : 'High Leverage'}
                </Badge>
              </div>
              <p className="text-xs text-muted-foreground mt-2">
                Total Liabilities / Total Equity
              </p>
            </CardContent>
          </Card>
          <Card className={data.summary.is_balanced ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'}>
            <CardContent className="pt-4">
              <div className="flex items-center gap-3">
                {data.summary.is_balanced ? (
                  <CheckCircle2 className="h-8 w-8 text-green-600" />
                ) : (
                  <AlertCircle className="h-8 w-8 text-red-600" />
                )}
                <div>
                  <p className={`font-semibold ${data.summary.is_balanced ? 'text-green-800' : 'text-red-800'}`}>
                    {data.summary.is_balanced ? 'Balance Sheet is Balanced' : 'Balance Sheet is Not Balanced'}
                  </p>
                  <p className={`text-sm ${data.summary.is_balanced ? 'text-green-600' : 'text-red-600'}`}>
                    Assets = Liabilities + Equity
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Balance Sheet Table */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Balance Sheet</CardTitle>
              <CardDescription>
                As of {formatDate(asOfDate, { format: 'long' })} | Compared to {data ? formatDate(data.previous_as_of_date, { format: 'long' }) : '-'}
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
              description="Select a date and generate the report to view the balance sheet."
            />
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b bg-muted/50">
                    <th className="text-left py-3 px-4 font-medium text-muted-foreground">Particulars</th>
                    <th className="text-right py-3 px-4 font-medium text-muted-foreground">
                      As of {formatDate(data.as_of_date)}
                    </th>
                    <th className="text-right py-3 px-4 font-medium text-muted-foreground">
                      As of {formatDate(data.previous_as_of_date)}
                    </th>
                    <th className="text-right py-3 px-4 font-medium text-muted-foreground">Variance</th>
                    <th className="text-center py-3 px-4 font-medium text-muted-foreground">Change</th>
                  </tr>
                </thead>
                <tbody>
                  {/* ASSETS SECTION */}
                  <tr className="bg-blue-100 border-y-2 border-blue-300">
                    <td colSpan={5} className="py-3 px-4 font-bold text-blue-800 text-lg">
                      ASSETS
                    </td>
                  </tr>

                  {/* Current Assets */}
                  {renderSection('Current Assets', 'current_asset', 'bg-blue-50', 'text-blue-700')}

                  {/* Non-Current Assets */}
                  {renderSection('Non-Current Assets', 'non_current_asset', 'bg-indigo-50', 'text-indigo-700')}

                  {/* Total Assets */}
                  {data.line_items.find(i => i.id === 'ta') && (
                    <tr className="bg-blue-200 font-bold border-y-2 border-blue-400">
                      <td className="py-4 px-4 text-blue-800">Total Assets</td>
                      <td className="py-4 px-4 text-right font-mono text-blue-800">{formatCurrency(data.summary.total_assets)}</td>
                      <td className="py-4 px-4 text-right font-mono text-muted-foreground">{formatCurrency(data.previous_summary.total_assets)}</td>
                      <td className="py-4 px-4 text-right font-mono">
                        <span className="text-green-600">+{formatCurrency(data.summary.total_assets - data.previous_summary.total_assets)}</span>
                      </td>
                      <td className="py-4 px-4 text-center">
                        <span className="flex items-center justify-center gap-1 text-xs text-green-600">
                          <ArrowUpRight className="h-3 w-3" />
                          {formatPercentage(((data.summary.total_assets - data.previous_summary.total_assets) / data.previous_summary.total_assets) * 100)}
                        </span>
                      </td>
                    </tr>
                  )}

                  {/* LIABILITIES SECTION */}
                  <tr className="bg-red-100 border-y-2 border-red-300">
                    <td colSpan={5} className="py-3 px-4 font-bold text-red-800 text-lg">
                      LIABILITIES
                    </td>
                  </tr>

                  {/* Current Liabilities */}
                  {renderSection('Current Liabilities', 'current_liability', 'bg-red-50', 'text-red-700')}

                  {/* Non-Current Liabilities */}
                  {renderSection('Non-Current Liabilities', 'non_current_liability', 'bg-red-50/50', 'text-red-600')}

                  {/* Total Liabilities */}
                  {data.line_items.find(i => i.id === 'tl') && (
                    <tr className="bg-red-200 font-bold border-y-2 border-red-400">
                      <td className="py-4 px-4 text-red-800">Total Liabilities</td>
                      <td className="py-4 px-4 text-right font-mono text-red-800">{formatCurrency(data.summary.total_liabilities)}</td>
                      <td className="py-4 px-4 text-right font-mono text-muted-foreground">{formatCurrency(data.previous_summary.total_liabilities)}</td>
                      <td className="py-4 px-4 text-right font-mono">
                        <span className="text-red-600">+{formatCurrency(data.summary.total_liabilities - data.previous_summary.total_liabilities)}</span>
                      </td>
                      <td className="py-4 px-4 text-center">
                        <span className="flex items-center justify-center gap-1 text-xs text-red-600">
                          <ArrowUpRight className="h-3 w-3" />
                          {formatPercentage(((data.summary.total_liabilities - data.previous_summary.total_liabilities) / data.previous_summary.total_liabilities) * 100)}
                        </span>
                      </td>
                    </tr>
                  )}

                  {/* EQUITY SECTION */}
                  <tr className="bg-purple-100 border-y-2 border-purple-300">
                    <td colSpan={5} className="py-3 px-4 font-bold text-purple-800 text-lg">
                      SHAREHOLDERS' EQUITY
                    </td>
                  </tr>

                  {/* Equity Items */}
                  {renderSection("Shareholders' Equity", 'equity', 'bg-purple-50', 'text-purple-700')}

                  {/* Total Equity */}
                  {data.line_items.find(i => i.id === 'te') && (
                    <tr className="bg-purple-200 font-bold border-y-2 border-purple-400">
                      <td className="py-4 px-4 text-purple-800">Total Equity</td>
                      <td className="py-4 px-4 text-right font-mono text-purple-800">{formatCurrency(data.summary.total_equity)}</td>
                      <td className="py-4 px-4 text-right font-mono text-muted-foreground">{formatCurrency(data.previous_summary.total_equity)}</td>
                      <td className="py-4 px-4 text-right font-mono">
                        <span className="text-green-600">+{formatCurrency(data.summary.total_equity - data.previous_summary.total_equity)}</span>
                      </td>
                      <td className="py-4 px-4 text-center">
                        <span className="flex items-center justify-center gap-1 text-xs text-green-600">
                          <ArrowUpRight className="h-3 w-3" />
                          {formatPercentage(((data.summary.total_equity - data.previous_summary.total_equity) / data.previous_summary.total_equity) * 100)}
                        </span>
                      </td>
                    </tr>
                  )}

                  {/* Total Liabilities & Equity */}
                  <tr className="bg-primary/10 font-bold border-t-4 border-primary">
                    <td className="py-4 px-4 text-lg">Total Liabilities & Equity</td>
                    <td className="py-4 px-4 text-right font-mono text-lg">{formatCurrency(data.summary.total_liabilities + data.summary.total_equity)}</td>
                    <td className="py-4 px-4 text-right font-mono text-muted-foreground">{formatCurrency(data.previous_summary.total_liabilities + data.previous_summary.total_equity)}</td>
                    <td className="py-4 px-4 text-right font-mono">
                      <span className="text-green-600">+{formatCurrency((data.summary.total_liabilities + data.summary.total_equity) - (data.previous_summary.total_liabilities + data.previous_summary.total_equity))}</span>
                    </td>
                    <td className="py-4 px-4 text-center">
                      <Badge variant="outline" className="text-primary">
                        {data.summary.is_balanced ? 'Balanced' : 'Unbalanced'}
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
