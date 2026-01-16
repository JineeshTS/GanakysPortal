'use client'

import * as React from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { PageHeader } from '@/components/layout/page-header'
import { DataTable, Column } from '@/components/layout/data-table'
import { StatsGrid } from '@/components/layout/stat-card'
import { MonthYearPicker } from '@/components/forms/date-picker'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { formatCurrency, formatCurrencySmart, getMonthName, formatDate } from '@/lib/format'
import { useApi } from '@/hooks/use-api'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog"
import {
  Play,
  Download,
  FileText,
  CheckCircle,
  Clock,
  AlertCircle,
  Users,
  Wallet,
  Receipt,
  TrendingUp,
  Calculator,
  Send,
  FileSpreadsheet,
  Building,
  CreditCard,
  ArrowUpRight,
  Eye,
  BarChart3,
  Bell,
  Trash2,
  AlertTriangle,
  Loader2
} from 'lucide-react'
import type { PayrollRun, PayrollStatus } from '@/types'

// ============================================================================
// Default/Fallback Data
// ============================================================================

const defaultPayrollRuns: PayrollRun[] = [
  {
    id: '1',
    company_id: '1',
    month: 12,
    year: 2025,
    status: 'paid',
    total_employees: 45,
    total_gross: 1847500,
    total_deductions: 442300,
    total_net: 1405200,
    total_employer_cost: 2142800,
    processed_by: 'admin',
    processed_at: '2025-12-28T10:00:00Z',
    approved_by: 'cfo',
    approved_at: '2025-12-29T14:00:00Z',
    paid_at: '2025-12-30T11:00:00Z',
    created_at: '2025-12-25T00:00:00Z',
    updated_at: '2025-12-30T11:00:00Z'
  },
  {
    id: '2',
    company_id: '1',
    month: 11,
    year: 2025,
    status: 'paid',
    total_employees: 44,
    total_gross: 1792000,
    total_deductions: 429100,
    total_net: 1362900,
    total_employer_cost: 2078400,
    processed_by: 'admin',
    processed_at: '2025-11-28T10:00:00Z',
    approved_by: 'cfo',
    approved_at: '2025-11-29T14:00:00Z',
    paid_at: '2025-11-30T11:00:00Z',
    created_at: '2025-11-25T00:00:00Z',
    updated_at: '2025-11-30T11:00:00Z'
  },
  {
    id: '3',
    company_id: '1',
    month: 1,
    year: 2026,
    status: 'draft',
    total_employees: 47,
    total_gross: 0,
    total_deductions: 0,
    total_net: 0,
    total_employer_cost: 0,
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z'
  }
]

// Default stats when no API data
const defaultStats = {
  totalEmployees: 47,
  grossSalary: 1895000,
  pfContribution: 227400,
  esiContribution: 75800,
  ptDeduction: 9400,
  tdsDeduction: 156200,
  totalDeductions: 468800,
  netPayable: 1426200,
  employerPF: 227400,
  employerESI: 61587,
  totalCTC: 2183987
}

// Quick stats for dashboard cards
const defaultQuickStats = {
  pendingApprovals: 2,
  pendingReimbursements: 15,
  taxDeclarationsDue: 8,
  salaryRevisionsDue: 3
}

// Upcoming compliance dates
const defaultComplianceDates = [
  { title: 'PF Payment Due', date: '2026-01-15', type: 'pf', amount: 454800 },
  { title: 'ESI Payment Due', date: '2026-01-15', type: 'esi', amount: 75800 },
  { title: 'TDS Payment Due', date: '2026-01-07', type: 'tds', amount: 156200 },
  { title: 'PT Payment Due', date: '2026-01-15', type: 'pt', amount: 9400 }
]

// API Response interface
interface PayrollRunsResponse {
  items: PayrollRun[]
  total: number
  page: number
  page_size: number
}

// ============================================================================
// Component
// ============================================================================

export default function PayrollPage() {
  const router = useRouter()
  const currentDate = new Date()
  const [selectedMonth, setSelectedMonth] = React.useState(currentDate.getMonth() + 1)
  const [selectedYear, setSelectedYear] = React.useState(currentDate.getFullYear())
  const [payrollRuns, setPayrollRuns] = React.useState<PayrollRun[]>(defaultPayrollRuns)
  const [isLoading, setIsLoading] = React.useState(true)
  const [currentMonthStats, setCurrentMonthStats] = React.useState(defaultStats)
  const [quickStats, setQuickStats] = React.useState(defaultQuickStats)
  const [complianceDates, setComplianceDates] = React.useState(defaultComplianceDates)

  // Delete state
  const [deleteDialogOpen, setDeleteDialogOpen] = React.useState(false)
  const [runToDelete, setRunToDelete] = React.useState<PayrollRun | null>(null)
  const [isDeleting, setIsDeleting] = React.useState(false)

  // API hooks
  const api = useApi<PayrollRunsResponse>()
  const deleteApi = useApi()

  // Fetch payroll runs from API
  React.useEffect(() => {
    const fetchPayrollRuns = async () => {
      setIsLoading(true)
      try {
        const companyId = '00000000-0000-0000-0000-000000000001' // Default company ID
        const response = await api.get(`/payroll/runs?company_id=${companyId}`)
        if (response && response.items && response.items.length > 0) {
          setPayrollRuns(response.items)
        }
        // If API returns empty, keep default data for demo
      } catch (error) {
        console.error('Failed to fetch payroll runs:', error)
        // Keep default data on error
      } finally {
        setIsLoading(false)
      }
    }
    fetchPayrollRuns()
  }, [])

  const currentRun = payrollRuns.find(
    run => run.month === selectedMonth && run.year === selectedYear
  )

  // Delete handlers
  const handleDeleteClick = (run: PayrollRun, e: React.MouseEvent) => {
    e.stopPropagation()
    setRunToDelete(run)
    setDeleteDialogOpen(true)
  }

  const handleDeleteConfirm = async () => {
    if (!runToDelete) return
    setIsDeleting(true)
    try {
      await deleteApi.delete(`/payroll/runs/${runToDelete.id}`)
      setPayrollRuns(payrollRuns.filter(run => run.id !== runToDelete.id))
      setDeleteDialogOpen(false)
      setRunToDelete(null)
    } catch (error) {
      console.error('Failed to delete payroll run:', error)
    } finally {
      setIsDeleting(false)
    }
  }

  // Dashboard Stats
  const stats = [
    {
      title: 'Total Employees',
      value: currentMonthStats.totalEmployees,
      icon: Users,
      description: 'For payroll processing',
      trend: { value: 4.5, label: 'vs last month' }
    },
    {
      title: 'Total CTC',
      value: formatCurrencySmart(currentMonthStats.totalCTC),
      icon: Wallet,
      description: 'Monthly cost to company',
      trend: { value: 2.8, label: 'vs last month' }
    },
    {
      title: 'Total Deductions',
      value: formatCurrencySmart(currentMonthStats.totalDeductions),
      icon: Calculator,
      description: 'PF + ESI + PT + TDS',
      trend: { value: 1.2, label: 'vs last month', type: 'neutral' as const }
    },
    {
      title: 'Net Payable',
      value: formatCurrencySmart(currentMonthStats.netPayable),
      icon: Receipt,
      description: 'After all deductions',
      valueClassName: 'text-green-600'
    }
  ]

  // Status badge helper
  const getStatusBadge = (status: PayrollStatus) => {
    const statusConfig = {
      draft: { label: 'Draft', className: 'bg-gray-100 text-gray-800', icon: FileText },
      processing: { label: 'Processing', className: 'bg-blue-100 text-blue-800', icon: Clock },
      calculated: { label: 'Calculated', className: 'bg-purple-100 text-purple-800', icon: Calculator },
      pending_approval: { label: 'Pending Approval', className: 'bg-yellow-100 text-yellow-800', icon: AlertCircle },
      approved: { label: 'Approved', className: 'bg-green-100 text-green-800', icon: CheckCircle },
      paid: { label: 'Paid', className: 'bg-green-100 text-green-800', icon: CheckCircle },
      cancelled: { label: 'Cancelled', className: 'bg-red-100 text-red-800', icon: AlertCircle }
    }

    const config = statusConfig[status] || statusConfig.draft
    const Icon = config.icon

    return (
      <Badge className={config.className}>
        <Icon className="h-3 w-3 mr-1" />
        {config.label}
      </Badge>
    )
  }

  // Table columns
  const columns: Column<PayrollRun>[] = [
    {
      key: 'month',
      header: 'Period',
      accessor: (row) => `${getMonthName(row.month)} ${row.year}`
    },
    {
      key: 'status',
      header: 'Status',
      accessor: (row) => getStatusBadge(row.status)
    },
    {
      key: 'total_employees',
      header: 'Employees',
      accessor: (row) => row.total_employees
    },
    {
      key: 'total_gross',
      header: 'Gross Salary',
      className: 'text-right',
      headerClassName: 'text-right',
      accessor: (row) => formatCurrency(row.total_gross)
    },
    {
      key: 'total_deductions',
      header: 'Deductions',
      className: 'text-right',
      headerClassName: 'text-right',
      accessor: (row) => formatCurrency(row.total_deductions)
    },
    {
      key: 'total_net',
      header: 'Net Payable',
      className: 'text-right font-medium',
      headerClassName: 'text-right',
      accessor: (row) => formatCurrency(row.total_net)
    },
    {
      key: 'actions',
      header: '',
      accessor: (row) => (
        <div className="flex items-center gap-2">
          <Button variant="ghost" size="sm" asChild>
            <Link href={`/payroll/payslips?month=${row.month}&year=${row.year}`}>
              <Eye className="h-4 w-4" />
            </Link>
          </Button>
          {row.status === 'draft' && (
            <Button
              variant="ghost"
              size="sm"
              className="text-red-600 hover:text-red-700 hover:bg-red-50"
              onClick={(e) => handleDeleteClick(row, e)}
            >
              <Trash2 className="h-4 w-4" />
            </Button>
          )}
        </div>
      )
    }
  ]

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <PageHeader
        title="Payroll"
        description="Process and manage employee salaries"
        breadcrumbs={[
          { label: 'Dashboard', href: '/dashboard' },
          { label: 'Payroll' }
        ]}
        actions={
          <div className="flex items-center gap-2">
            <Button variant="outline" asChild>
              <Link href="/payroll/reports">
                <BarChart3 className="h-4 w-4 mr-2" />
                Reports
              </Link>
            </Button>
            <Button asChild>
              <Link href="/payroll/run">
                <Play className="h-4 w-4 mr-2" />
                Run Payroll
              </Link>
            </Button>
          </div>
        }
      />

      {/* Month Selector & Current Status */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <MonthYearPicker
              label="Select Period"
              name="payroll-period"
              month={selectedMonth}
              year={selectedYear}
              onMonthChange={setSelectedMonth}
              onYearChange={setSelectedYear}
            />
            <div className="flex items-center gap-2">
              {currentRun && getStatusBadge(currentRun.status)}
              {currentRun?.status === 'draft' && (
                <Button asChild>
                  <Link href="/payroll/run">
                    <Play className="h-4 w-4 mr-2" />
                    Run Payroll
                  </Link>
                </Button>
              )}
              {currentRun?.status === 'calculated' && (
                <Button>
                  <Send className="h-4 w-4 mr-2" />
                  Submit for Approval
                </Button>
              )}
              {currentRun?.status === 'paid' && (
                <>
                  <Button variant="outline" asChild>
                    <Link href={`/payroll/payslips?month=${selectedMonth}&year=${selectedYear}`}>
                      <FileText className="h-4 w-4 mr-2" />
                      View Payslips
                    </Link>
                  </Button>
                  <Button variant="outline">
                    <Download className="h-4 w-4 mr-2" />
                    Download Report
                  </Button>
                </>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Stats Grid */}
      <StatsGrid stats={stats} columns={4} />

      {/* Quick Actions & Alerts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Quick Actions */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-base">Quick Actions</CardTitle>
          </CardHeader>
          <CardContent className="grid grid-cols-2 gap-2">
            <Button variant="outline" size="sm" className="justify-start" asChild>
              <Link href="/payroll/run">
                <Play className="h-4 w-4 mr-2" />
                Run Payroll
              </Link>
            </Button>
            <Button variant="outline" size="sm" className="justify-start" asChild>
              <Link href="/payroll/payslips">
                <FileText className="h-4 w-4 mr-2" />
                Payslips
              </Link>
            </Button>
            <Button variant="outline" size="sm" className="justify-start" asChild>
              <Link href="/payroll/reports">
                <FileSpreadsheet className="h-4 w-4 mr-2" />
                Reports
              </Link>
            </Button>
            <Button variant="outline" size="sm" className="justify-start">
              <CreditCard className="h-4 w-4 mr-2" />
              Bank File
            </Button>
          </CardContent>
        </Card>

        {/* Pending Items */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-base flex items-center gap-2">
              <Bell className="h-4 w-4" />
              Pending Items
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <div className="flex items-center justify-between py-2 border-b">
              <span className="text-sm">Pending Approvals</span>
              <Badge>{quickStats.pendingApprovals}</Badge>
            </div>
            <div className="flex items-center justify-between py-2 border-b">
              <span className="text-sm">Reimbursement Claims</span>
              <Badge variant="secondary">{quickStats.pendingReimbursements}</Badge>
            </div>
            <div className="flex items-center justify-between py-2 border-b">
              <span className="text-sm">Tax Declarations Due</span>
              <Badge variant="outline">{quickStats.taxDeclarationsDue}</Badge>
            </div>
            <div className="flex items-center justify-between py-2">
              <span className="text-sm">Salary Revisions</span>
              <Badge variant="outline">{quickStats.salaryRevisionsDue}</Badge>
            </div>
          </CardContent>
        </Card>

        {/* Compliance Due Dates */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-base flex items-center gap-2">
              <AlertCircle className="h-4 w-4 text-yellow-500" />
              Compliance Due Dates
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            {complianceDates.map((item, index) => (
              <div key={index} className="flex items-center justify-between py-2 border-b last:border-0">
                <div>
                  <span className="text-sm font-medium">{item.title}</span>
                  <p className="text-xs text-muted-foreground">{formatDate(item.date)}</p>
                </div>
                <span className="text-sm font-medium">{formatCurrency(item.amount)}</span>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>

      {/* Payroll Details Tabs */}
      <Tabs defaultValue="summary" className="space-y-4">
        <TabsList>
          <TabsTrigger value="summary">Summary</TabsTrigger>
          <TabsTrigger value="statutory">Statutory Breakup</TabsTrigger>
          <TabsTrigger value="history">History</TabsTrigger>
        </TabsList>

        <TabsContent value="summary" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Earnings Breakup */}
            <Card>
              <CardHeader>
                <CardTitle>Earnings Breakup</CardTitle>
                <CardDescription>{getMonthName(selectedMonth)} {selectedYear}</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex justify-between py-2 border-b">
                    <span>Basic Salary</span>
                    <span className="font-medium">{formatCurrency(947500)}</span>
                  </div>
                  <div className="flex justify-between py-2 border-b">
                    <span>House Rent Allowance (HRA)</span>
                    <span className="font-medium">{formatCurrency(473750)}</span>
                  </div>
                  <div className="flex justify-between py-2 border-b">
                    <span>Special Allowance</span>
                    <span className="font-medium">{formatCurrency(378750)}</span>
                  </div>
                  <div className="flex justify-between py-2 border-b">
                    <span>Other Allowances</span>
                    <span className="font-medium">{formatCurrency(95000)}</span>
                  </div>
                  <div className="flex justify-between py-2 font-semibold text-lg">
                    <span>Total Gross</span>
                    <span className="text-primary">{formatCurrency(currentMonthStats.grossSalary)}</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Deductions Breakup */}
            <Card>
              <CardHeader>
                <CardTitle>Deductions Breakup</CardTitle>
                <CardDescription>{getMonthName(selectedMonth)} {selectedYear}</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex justify-between py-2 border-b">
                    <span>Provident Fund (Employee 12%)</span>
                    <span className="font-medium text-red-600">-{formatCurrency(currentMonthStats.pfContribution)}</span>
                  </div>
                  <div className="flex justify-between py-2 border-b">
                    <span>ESI (Employee 0.75%)</span>
                    <span className="font-medium text-red-600">-{formatCurrency(14213)}</span>
                  </div>
                  <div className="flex justify-between py-2 border-b">
                    <span>Professional Tax</span>
                    <span className="font-medium text-red-600">-{formatCurrency(currentMonthStats.ptDeduction)}</span>
                  </div>
                  <div className="flex justify-between py-2 border-b">
                    <span>TDS (Income Tax)</span>
                    <span className="font-medium text-red-600">-{formatCurrency(currentMonthStats.tdsDeduction)}</span>
                  </div>
                  <div className="flex justify-between py-2 border-b">
                    <span>Other Deductions</span>
                    <span className="font-medium text-red-600">-{formatCurrency(61587)}</span>
                  </div>
                  <div className="flex justify-between py-2 font-semibold text-lg">
                    <span>Total Deductions</span>
                    <span className="text-red-600">-{formatCurrency(currentMonthStats.totalDeductions)}</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Net Payable Summary */}
          <Card className="bg-primary/5 border-primary/20">
            <CardContent className="pt-6">
              <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                <div>
                  <p className="text-sm text-muted-foreground">Net Payable Amount</p>
                  <p className="text-3xl font-bold text-primary">{formatCurrency(currentMonthStats.netPayable)}</p>
                  <p className="text-sm text-muted-foreground mt-1">
                    For {currentMonthStats.totalEmployees} employees
                  </p>
                </div>
                <div className="space-y-2">
                  <div className="flex items-center gap-2 text-sm">
                    <span className="text-muted-foreground">Employer PF Contribution:</span>
                    <span className="font-medium">{formatCurrency(currentMonthStats.employerPF)}</span>
                  </div>
                  <div className="flex items-center gap-2 text-sm">
                    <span className="text-muted-foreground">Employer ESI Contribution:</span>
                    <span className="font-medium">{formatCurrency(currentMonthStats.employerESI)}</span>
                  </div>
                  <div className="flex items-center gap-2 text-sm font-semibold">
                    <span className="text-muted-foreground">Total CTC:</span>
                    <span>{formatCurrency(currentMonthStats.totalCTC)}</span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="statutory" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* PF Summary */}
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Provident Fund</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Employee (12%)</span>
                    <span>{formatCurrency(currentMonthStats.pfContribution)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Employer EPS (8.33%)</span>
                    <span>{formatCurrency(157000)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Employer EPF (3.67%)</span>
                    <span>{formatCurrency(70400)}</span>
                  </div>
                  <div className="flex justify-between font-semibold pt-2 border-t">
                    <span>Total PF</span>
                    <span>{formatCurrency(454800)}</span>
                  </div>
                </div>
                <p className="text-xs text-muted-foreground mt-2">Due: 15th of next month</p>
              </CardContent>
            </Card>

            {/* ESI Summary */}
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">ESI</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Employee (0.75%)</span>
                    <span>{formatCurrency(14213)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Employer (3.25%)</span>
                    <span>{formatCurrency(61587)}</span>
                  </div>
                  <div className="flex justify-between font-semibold pt-2 border-t">
                    <span>Total ESI</span>
                    <span>{formatCurrency(75800)}</span>
                  </div>
                </div>
                <p className="text-xs text-muted-foreground mt-2">Applicable: Gross &lt;= Rs.21,000</p>
              </CardContent>
            </Card>

            {/* PT Summary */}
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">Professional Tax</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Karnataka PT</span>
                    <span>{formatCurrency(currentMonthStats.ptDeduction)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Employees liable</span>
                    <span>47</span>
                  </div>
                  <div className="flex justify-between font-semibold pt-2 border-t">
                    <span>Total PT</span>
                    <span>{formatCurrency(currentMonthStats.ptDeduction)}</span>
                  </div>
                </div>
                <p className="text-xs text-muted-foreground mt-2">Rs.200/month (Rs.300 in Feb)</p>
              </CardContent>
            </Card>

            {/* TDS Summary */}
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium">TDS (Income Tax)</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">New Regime</span>
                    <span>{formatCurrency(98000)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Old Regime</span>
                    <span>{formatCurrency(58200)}</span>
                  </div>
                  <div className="flex justify-between font-semibold pt-2 border-t">
                    <span>Total TDS</span>
                    <span>{formatCurrency(currentMonthStats.tdsDeduction)}</span>
                  </div>
                </div>
                <p className="text-xs text-muted-foreground mt-2">Due: 7th of next month</p>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="history">
          <Card>
            <CardHeader>
              <CardTitle>Payroll History</CardTitle>
              <CardDescription>Previous payroll runs</CardDescription>
            </CardHeader>
            <CardContent>
              {isLoading ? (
                <div className="flex items-center justify-center py-8">
                  <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
                </div>
              ) : (
                <DataTable
                  data={payrollRuns}
                  columns={columns}
                  keyExtractor={(row) => row.id}
                />
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-red-500" />
              Delete Payroll Run
            </AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete the payroll run for{' '}
              <strong>
                {runToDelete ? `${getMonthName(runToDelete.month)} ${runToDelete.year}` : ''}
              </strong>
              ? This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={isDeleting}>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDeleteConfirm}
              disabled={isDeleting}
              className="bg-red-600 hover:bg-red-700 focus:ring-red-600"
            >
              {isDeleting ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Deleting...
                </>
              ) : (
                'Delete'
              )}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
}
