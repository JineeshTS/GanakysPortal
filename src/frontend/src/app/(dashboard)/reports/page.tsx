'use client'

import { useState } from 'react'
import { useApi } from '@/hooks/use-api'
import { PageHeader } from '@/components/layout/page-header'
import { StatCard } from '@/components/layout/stat-card'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { formatCurrency, formatDate, getFinancialYear, getMonthName } from '@/lib/format'
import {
  FileText,
  Download,
  TrendingUp,
  TrendingDown,
  DollarSign,
  FileSpreadsheet,
  BarChart3,
  PieChart,
  Calendar,
  Building2,
  Receipt,
  CreditCard,
  Banknote,
  Calculator,
  FileCheck,
  FileClock,
  RefreshCw,
  Loader2,
} from 'lucide-react'

// Map report IDs to API endpoints
const reportApiEndpoints: Record<string, { endpoint: string; method: 'get' | 'post'; needsParams?: boolean }> = {
  // Financial Reports
  'profit-loss': { endpoint: '/reports/finance/profit-loss', method: 'get', needsParams: true },
  'balance-sheet': { endpoint: '/reports/finance/balance-sheet', method: 'get', needsParams: true },
  'cash-flow': { endpoint: '/reports/finance/cash-flow', method: 'get', needsParams: true },
  'trial-balance': { endpoint: '/reports/finance/trial-balance', method: 'get', needsParams: true },
  'receivables-aging': { endpoint: '/reports/finance/receivables-aging', method: 'get', needsParams: true },
  'payables-aging': { endpoint: '/reports/finance/payables-aging', method: 'get', needsParams: true },
  // GST Reports
  'gstr-1': { endpoint: '/reports/compliance/gstr1', method: 'get', needsParams: true },
  'gstr-3b': { endpoint: '/reports/compliance/gstr3b', method: 'get', needsParams: true },
  'hsn-summary': { endpoint: '/gst/hsn-summary', method: 'get', needsParams: true },
  // TDS Reports
  'form-24q': { endpoint: '/reports/compliance/form24q', method: 'get', needsParams: true },
  // HR Reports
  'pf-ecr': { endpoint: '/reports/compliance/pf-ecr', method: 'get', needsParams: true },
  'esi-return': { endpoint: '/reports/compliance/esi-monthly', method: 'get', needsParams: true },
  'pt-return': { endpoint: '/reports/compliance/pt-monthly', method: 'get', needsParams: true },
  'payroll-register': { endpoint: '/reports/payroll/register', method: 'get', needsParams: true },
  'attendance-summary': { endpoint: '/reports/hr/attendance-summary', method: 'get', needsParams: true },
  'leave-balance': { endpoint: '/reports/hr/leave-summary', method: 'get', needsParams: true },
}

// Report types for Indian compliance
interface ReportCard {
  id: string
  name: string
  description: string
  category: 'financial' | 'statutory' | 'hr' | 'gst' | 'tds' | 'analytics'
  icon: React.ReactNode
  frequency: 'daily' | 'monthly' | 'quarterly' | 'annual'
  lastGenerated?: string
  status?: 'ready' | 'generating' | 'scheduled'
}

const financialReports: ReportCard[] = [
  {
    id: 'profit-loss',
    name: 'Profit & Loss Statement',
    description: 'Income, expenses, and net profit for the period',
    category: 'financial',
    icon: <TrendingUp className="h-5 w-5" />,
    frequency: 'monthly',
    lastGenerated: '2026-01-01T10:30:00',
    status: 'ready',
  },
  {
    id: 'balance-sheet',
    name: 'Balance Sheet',
    description: 'Assets, liabilities, and equity position',
    category: 'financial',
    icon: <FileSpreadsheet className="h-5 w-5" />,
    frequency: 'monthly',
    lastGenerated: '2026-01-01T10:30:00',
    status: 'ready',
  },
  {
    id: 'cash-flow',
    name: 'Cash Flow Statement',
    description: 'Operating, investing, and financing activities',
    category: 'financial',
    icon: <Banknote className="h-5 w-5" />,
    frequency: 'monthly',
    lastGenerated: '2026-01-01T10:30:00',
    status: 'ready',
  },
  {
    id: 'trial-balance',
    name: 'Trial Balance',
    description: 'All account balances with debit/credit totals',
    category: 'financial',
    icon: <Calculator className="h-5 w-5" />,
    frequency: 'monthly',
    lastGenerated: '2026-01-01T10:30:00',
    status: 'ready',
  },
  {
    id: 'receivables-aging',
    name: 'Receivables Aging',
    description: 'Outstanding customer invoices by age',
    category: 'financial',
    icon: <FileClock className="h-5 w-5" />,
    frequency: 'daily',
    lastGenerated: '2026-01-06T08:00:00',
    status: 'ready',
  },
  {
    id: 'payables-aging',
    name: 'Payables Aging',
    description: 'Outstanding vendor bills by age',
    category: 'financial',
    icon: <CreditCard className="h-5 w-5" />,
    frequency: 'daily',
    lastGenerated: '2026-01-06T08:00:00',
    status: 'ready',
  },
]

const gstReports: ReportCard[] = [
  {
    id: 'gstr-1',
    name: 'GSTR-1 (Sales Register)',
    description: 'Outward supplies - B2B, B2C, exports, amendments',
    category: 'gst',
    icon: <Receipt className="h-5 w-5" />,
    frequency: 'monthly',
    lastGenerated: '2026-01-10T15:00:00',
    status: 'ready',
  },
  {
    id: 'gstr-2a',
    name: 'GSTR-2A Reconciliation',
    description: 'Auto-populated inward supplies vs books',
    category: 'gst',
    icon: <FileCheck className="h-5 w-5" />,
    frequency: 'monthly',
    lastGenerated: '2026-01-05T12:00:00',
    status: 'ready',
  },
  {
    id: 'gstr-3b',
    name: 'GSTR-3B Summary',
    description: 'Monthly summary return - tax liability',
    category: 'gst',
    icon: <FileSpreadsheet className="h-5 w-5" />,
    frequency: 'monthly',
    status: 'scheduled',
  },
  {
    id: 'gstr-9',
    name: 'GSTR-9 Annual Return',
    description: 'Annual return with reconciliation',
    category: 'gst',
    icon: <FileText className="h-5 w-5" />,
    frequency: 'annual',
    status: 'scheduled',
  },
  {
    id: 'hsn-summary',
    name: 'HSN-wise Summary',
    description: 'Sales and purchases grouped by HSN/SAC code',
    category: 'gst',
    icon: <BarChart3 className="h-5 w-5" />,
    frequency: 'monthly',
    lastGenerated: '2026-01-05T12:00:00',
    status: 'ready',
  },
  {
    id: 'itc-register',
    name: 'ITC Register',
    description: 'Input Tax Credit claimed and utilized',
    category: 'gst',
    icon: <DollarSign className="h-5 w-5" />,
    frequency: 'monthly',
    lastGenerated: '2026-01-05T12:00:00',
    status: 'ready',
  },
]

const tdsReports: ReportCard[] = [
  {
    id: 'form-26q',
    name: 'Form 26Q (Quarterly TDS)',
    description: 'TDS on payments other than salary',
    category: 'tds',
    icon: <FileText className="h-5 w-5" />,
    frequency: 'quarterly',
    lastGenerated: '2026-01-07T10:00:00',
    status: 'ready',
  },
  {
    id: 'form-24q',
    name: 'Form 24Q (Salary TDS)',
    description: 'TDS on salary payments - Q3',
    category: 'tds',
    icon: <FileText className="h-5 w-5" />,
    frequency: 'quarterly',
    lastGenerated: '2026-01-07T10:00:00',
    status: 'ready',
  },
  {
    id: 'form-16',
    name: 'Form 16 Generation',
    description: 'Annual salary certificate for employees',
    category: 'tds',
    icon: <FileCheck className="h-5 w-5" />,
    frequency: 'annual',
    status: 'scheduled',
  },
  {
    id: 'form-16a',
    name: 'Form 16A Generation',
    description: 'TDS certificate for vendors',
    category: 'tds',
    icon: <FileCheck className="h-5 w-5" />,
    frequency: 'quarterly',
    status: 'ready',
  },
  {
    id: 'tds-section-summary',
    name: 'TDS Section-wise Summary',
    description: '194A/C/H/I/J/Q breakdown',
    category: 'tds',
    icon: <PieChart className="h-5 w-5" />,
    frequency: 'monthly',
    lastGenerated: '2026-01-05T12:00:00',
    status: 'ready',
  },
  {
    id: 'tds-challan',
    name: 'TDS Challan Status',
    description: 'Track challan payments and acknowledgments',
    category: 'tds',
    icon: <Receipt className="h-5 w-5" />,
    frequency: 'monthly',
    lastGenerated: '2026-01-05T12:00:00',
    status: 'ready',
  },
]

const hrReports: ReportCard[] = [
  {
    id: 'pf-ecr',
    name: 'PF ECR (Electronic Challan)',
    description: 'Monthly PF contribution return',
    category: 'hr',
    icon: <FileSpreadsheet className="h-5 w-5" />,
    frequency: 'monthly',
    lastGenerated: '2026-01-10T10:00:00',
    status: 'ready',
  },
  {
    id: 'esi-return',
    name: 'ESI Half-Yearly Return',
    description: 'Employee State Insurance contribution',
    category: 'hr',
    icon: <FileText className="h-5 w-5" />,
    frequency: 'quarterly',
    status: 'scheduled',
  },
  {
    id: 'pt-return',
    name: 'Professional Tax Return',
    description: 'State-wise PT deduction summary',
    category: 'hr',
    icon: <Building2 className="h-5 w-5" />,
    frequency: 'monthly',
    lastGenerated: '2026-01-05T12:00:00',
    status: 'ready',
  },
  {
    id: 'payroll-register',
    name: 'Payroll Register',
    description: 'Complete salary breakup for all employees',
    category: 'hr',
    icon: <FileSpreadsheet className="h-5 w-5" />,
    frequency: 'monthly',
    lastGenerated: '2026-01-02T10:00:00',
    status: 'ready',
  },
  {
    id: 'attendance-summary',
    name: 'Attendance Summary',
    description: 'Monthly attendance, leave, and work hours',
    category: 'hr',
    icon: <Calendar className="h-5 w-5" />,
    frequency: 'monthly',
    lastGenerated: '2026-01-02T10:00:00',
    status: 'ready',
  },
  {
    id: 'leave-balance',
    name: 'Leave Balance Report',
    description: 'Employee-wise leave balances and utilization',
    category: 'hr',
    icon: <Calendar className="h-5 w-5" />,
    frequency: 'monthly',
    lastGenerated: '2026-01-02T10:00:00',
    status: 'ready',
  },
]

// Summary statistics
const reportStats = {
  totalReports: 24,
  generatedToday: 4,
  scheduled: 5,
  pendingFilings: 3,
  gstLiability: 847500,
  tdsLiability: 156200,
}

// GST Summary for current month
const gstSummary = {
  month: 12,
  year: 2025,
  outputCGST: 425000,
  outputSGST: 425000,
  outputIGST: 850000,
  inputCGST: 180000,
  inputSGST: 180000,
  inputIGST: 492500,
  netLiability: 847500,
}

// TDS Summary by section
const tdsSummary = [
  { section: '194A', description: 'Interest', deducted: 24500, deposited: 24500 },
  { section: '194C', description: 'Contractor', deducted: 48200, deposited: 48200 },
  { section: '194H', description: 'Commission', deducted: 12800, deposited: 12800 },
  { section: '194I', description: 'Rent', deducted: 35000, deposited: 35000 },
  { section: '194J', description: 'Professional', deducted: 28500, deposited: 28500 },
  { section: '194Q', description: 'Purchase', deducted: 7200, deposited: 0 },
]

function ReportCardComponent({ report, onGenerate, onDownload, isGenerating }: {
  report: ReportCard
  onGenerate: () => void
  onDownload: () => void
  isGenerating?: boolean
}) {
  const statusColors = {
    ready: 'bg-green-100 text-green-800',
    generating: 'bg-yellow-100 text-yellow-800',
    scheduled: 'bg-blue-100 text-blue-800',
  }

  const frequencyLabels = {
    daily: 'Daily',
    monthly: 'Monthly',
    quarterly: 'Quarterly',
    annual: 'Annual',
  }

  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardHeader className="pb-2">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-primary/10 rounded-lg">
              {report.icon}
            </div>
            <div>
              <CardTitle className="text-base">{report.name}</CardTitle>
              <CardDescription className="text-xs mt-1">
                {report.description}
              </CardDescription>
            </div>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="flex items-center justify-between mt-2">
          <div className="flex items-center gap-2">
            <Badge variant="outline" className="text-xs">
              {frequencyLabels[report.frequency]}
            </Badge>
            {(report.status || isGenerating) && (
              <Badge className={`text-xs ${isGenerating ? statusColors.generating : statusColors[report.status || 'ready']}`}>
                {isGenerating ? 'Generating...' : report.status === 'ready' ? 'Ready' : report.status === 'generating' ? 'Generating...' : 'Scheduled'}
              </Badge>
            )}
          </div>
          {report.lastGenerated && (
            <span className="text-xs text-muted-foreground">
              {formatDate(report.lastGenerated)}
            </span>
          )}
        </div>
        <div className="flex gap-2 mt-4">
          <Button
            size="sm"
            variant="outline"
            className="flex-1"
            onClick={onGenerate}
            disabled={isGenerating}
          >
            {isGenerating ? (
              <Loader2 className="h-3.5 w-3.5 mr-1 animate-spin" />
            ) : (
              <RefreshCw className="h-3.5 w-3.5 mr-1" />
            )}
            {isGenerating ? 'Generating...' : 'Generate'}
          </Button>
          <Button
            size="sm"
            className="flex-1"
            onClick={onDownload}
            disabled={report.status !== 'ready' || isGenerating}
          >
            <Download className="h-3.5 w-3.5 mr-1" />
            Download
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}

export default function ReportsPage() {
  const api = useApi()
  const [selectedPeriod, setSelectedPeriod] = useState('dec-2025')
  const [activeTab, setActiveTab] = useState('financial')
  const [generatingReport, setGeneratingReport] = useState<string | null>(null)
  const [reportData, setReportData] = useState<Record<string, any>>({})

  // Parse selected period into year and month
  const getPeriodParams = () => {
    const periodMap: Record<string, { year: number; month?: number; quarter?: number; financial_year?: string }> = {
      'jan-2026': { year: 2026, month: 1 },
      'dec-2025': { year: 2025, month: 12 },
      'nov-2025': { year: 2025, month: 11 },
      'q3-2025': { year: 2025, quarter: 3, financial_year: '2025-26' },
      'fy-2025-26': { year: 2025, financial_year: '2025-26' },
    }
    return periodMap[selectedPeriod] || { year: 2025, month: 12 }
  }

  const handleGenerate = async (reportId: string) => {
    const apiConfig = reportApiEndpoints[reportId]
    if (!apiConfig) {
      console.log('No API endpoint configured for:', reportId)
      return
    }

    setGeneratingReport(reportId)
    try {
      const params = getPeriodParams()
      // Build query string
      const queryParams = new URLSearchParams()
      queryParams.append('company_id', '27958f6c-7c88-4340-ac3b-3bcc3070f9a2') // Demo company ID
      if (params.year) queryParams.append('year', params.year.toString())
      if (params.month) queryParams.append('month', params.month.toString())
      if (params.quarter) queryParams.append('quarter', params.quarter.toString())
      if (params.financial_year) queryParams.append('financial_year', params.financial_year)

      const response = await api.get(`${apiConfig.endpoint}?${queryParams.toString()}`)

      if (response) {
        setReportData(prev => ({ ...prev, [reportId]: response }))
        console.log(`Report ${reportId} generated:`, response)
      }
    } catch (error) {
      console.error(`Failed to generate report ${reportId}:`, error)
    } finally {
      setGeneratingReport(null)
    }
  }

  const handleDownload = async (reportId: string) => {
    const apiConfig = reportApiEndpoints[reportId]
    if (!apiConfig) {
      console.log('No API endpoint configured for:', reportId)
      return
    }

    try {
      const params = getPeriodParams()
      const queryParams = new URLSearchParams()
      queryParams.append('company_id', '27958f6c-7c88-4340-ac3b-3bcc3070f9a2')
      if (params.year) queryParams.append('year', params.year.toString())
      if (params.month) queryParams.append('month', params.month.toString())
      queryParams.append('output_format', 'excel')

      // For download, we'd normally trigger a file download
      // For now, generate the report in JSON and log it
      const response = await api.get(`${apiConfig.endpoint}?${queryParams.toString()}`)
      console.log(`Download report ${reportId}:`, response)

      // In production, this would be:
      // window.open(`/api/v1${apiConfig.endpoint}?${queryParams.toString()}&output_format=excel`, '_blank')
    } catch (error) {
      console.error(`Failed to download report ${reportId}:`, error)
    }
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Reports & Compliance"
        description={`Financial, statutory, and analytical reports - ${getFinancialYear()}`}
        actions={
          <div className="flex gap-2">
            <Select value={selectedPeriod} onValueChange={setSelectedPeriod}>
              <SelectTrigger className="w-[160px]">
                <SelectValue placeholder="Select period" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="jan-2026">January 2026</SelectItem>
                <SelectItem value="dec-2025">December 2025</SelectItem>
                <SelectItem value="nov-2025">November 2025</SelectItem>
                <SelectItem value="q3-2025">Q3 FY 25-26</SelectItem>
                <SelectItem value="fy-2025-26">FY 2025-26</SelectItem>
              </SelectContent>
            </Select>
          </div>
        }
      />

      {/* Summary Stats */}
      <div className="grid gap-4 md:grid-cols-4">
        <StatCard
          title="Total Reports"
          value={reportStats.totalReports}
          icon={<FileText className="h-4 w-4" />}
          description="Available reports"
        />
        <StatCard
          title="Pending Filings"
          value={reportStats.pendingFilings}
          icon={<FileClock className="h-4 w-4" />}
          description="Due this month"
          trend="up"
          trendValue="3 due"
        />
        <StatCard
          title="GST Liability"
          value={formatCurrency(reportStats.gstLiability)}
          icon={<Receipt className="h-4 w-4" />}
          description="Dec 2025"
        />
        <StatCard
          title="TDS Liability"
          value={formatCurrency(reportStats.tdsLiability)}
          icon={<Calculator className="h-4 w-4" />}
          description="Q3 FY 25-26"
        />
      </div>

      {/* GST and TDS Summary Cards */}
      <div className="grid gap-4 md:grid-cols-2">
        {/* GST Summary */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <Receipt className="h-5 w-5" />
              GST Summary - {getMonthName(gstSummary.month)} {gstSummary.year}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <p className="text-sm text-muted-foreground mb-2">Output Tax (Sales)</p>
                <div className="grid grid-cols-3 gap-2 text-sm">
                  <div className="bg-muted/50 p-2 rounded">
                    <p className="text-xs text-muted-foreground">CGST</p>
                    <p className="font-medium">{formatCurrency(gstSummary.outputCGST)}</p>
                  </div>
                  <div className="bg-muted/50 p-2 rounded">
                    <p className="text-xs text-muted-foreground">SGST</p>
                    <p className="font-medium">{formatCurrency(gstSummary.outputSGST)}</p>
                  </div>
                  <div className="bg-muted/50 p-2 rounded">
                    <p className="text-xs text-muted-foreground">IGST</p>
                    <p className="font-medium">{formatCurrency(gstSummary.outputIGST)}</p>
                  </div>
                </div>
              </div>
              <div>
                <p className="text-sm text-muted-foreground mb-2">Input Tax Credit (ITC)</p>
                <div className="grid grid-cols-3 gap-2 text-sm">
                  <div className="bg-green-50 p-2 rounded">
                    <p className="text-xs text-muted-foreground">CGST</p>
                    <p className="font-medium text-green-700">{formatCurrency(gstSummary.inputCGST)}</p>
                  </div>
                  <div className="bg-green-50 p-2 rounded">
                    <p className="text-xs text-muted-foreground">SGST</p>
                    <p className="font-medium text-green-700">{formatCurrency(gstSummary.inputSGST)}</p>
                  </div>
                  <div className="bg-green-50 p-2 rounded">
                    <p className="text-xs text-muted-foreground">IGST</p>
                    <p className="font-medium text-green-700">{formatCurrency(gstSummary.inputIGST)}</p>
                  </div>
                </div>
              </div>
              <div className="border-t pt-3">
                <div className="flex justify-between items-center">
                  <span className="font-medium">Net GST Liability</span>
                  <span className="text-lg font-bold text-primary">
                    {formatCurrency(gstSummary.netLiability)}
                  </span>
                </div>
                <p className="text-xs text-muted-foreground mt-1">
                  Due by 20th {getMonthName(gstSummary.month + 1 > 12 ? 1 : gstSummary.month + 1)} {gstSummary.month === 12 ? gstSummary.year + 1 : gstSummary.year}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* TDS Summary */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <Calculator className="h-5 w-5" />
              TDS Summary - Q3 FY 25-26
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="grid grid-cols-4 text-xs font-medium text-muted-foreground border-b pb-2">
                <span>Section</span>
                <span>Nature</span>
                <span className="text-right">Deducted</span>
                <span className="text-right">Deposited</span>
              </div>
              {tdsSummary.map((item) => (
                <div key={item.section} className="grid grid-cols-4 text-sm py-1.5 border-b border-dashed last:border-0">
                  <span className="font-medium">{item.section}</span>
                  <span className="text-muted-foreground">{item.description}</span>
                  <span className="text-right">{formatCurrency(item.deducted)}</span>
                  <span className={`text-right ${item.deposited < item.deducted ? 'text-red-600' : 'text-green-600'}`}>
                    {formatCurrency(item.deposited)}
                  </span>
                </div>
              ))}
              <div className="border-t pt-3 mt-2">
                <div className="flex justify-between items-center">
                  <span className="font-medium">Total TDS</span>
                  <div className="text-right">
                    <span className="text-lg font-bold text-primary">
                      {formatCurrency(tdsSummary.reduce((sum, t) => sum + t.deducted, 0))}
                    </span>
                    <p className="text-xs text-muted-foreground">
                      Pending: {formatCurrency(tdsSummary.reduce((sum, t) => sum + (t.deducted - t.deposited), 0))}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Reports by Category */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="financial">Financial</TabsTrigger>
          <TabsTrigger value="gst">GST Returns</TabsTrigger>
          <TabsTrigger value="tds">TDS/Income Tax</TabsTrigger>
          <TabsTrigger value="hr">HR & Payroll</TabsTrigger>
        </TabsList>

        <TabsContent value="financial" className="mt-4">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {financialReports.map((report) => (
              <ReportCardComponent
                key={report.id}
                report={report}
                onGenerate={() => handleGenerate(report.id)}
                onDownload={() => handleDownload(report.id)}
                isGenerating={generatingReport === report.id}
              />
            ))}
          </div>
        </TabsContent>

        <TabsContent value="gst" className="mt-4">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {gstReports.map((report) => (
              <ReportCardComponent
                key={report.id}
                report={report}
                onGenerate={() => handleGenerate(report.id)}
                onDownload={() => handleDownload(report.id)}
                isGenerating={generatingReport === report.id}
              />
            ))}
          </div>
        </TabsContent>

        <TabsContent value="tds" className="mt-4">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {tdsReports.map((report) => (
              <ReportCardComponent
                key={report.id}
                report={report}
                onGenerate={() => handleGenerate(report.id)}
                onDownload={() => handleDownload(report.id)}
                isGenerating={generatingReport === report.id}
              />
            ))}
          </div>
        </TabsContent>

        <TabsContent value="hr" className="mt-4">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {hrReports.map((report) => (
              <ReportCardComponent
                key={report.id}
                report={report}
                onGenerate={() => handleGenerate(report.id)}
                onDownload={() => handleDownload(report.id)}
                isGenerating={generatingReport === report.id}
              />
            ))}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}
