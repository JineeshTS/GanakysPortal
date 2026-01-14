'use client'

import * as React from 'react'
import Link from 'next/link'
import { PageHeader } from '@/components/layout/page-header'
import { StatsGrid } from '@/components/layout/stat-card'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { formatCurrency, formatCurrencySmart, formatDate } from '@/lib/format'
import {
  IndianRupee,
  TrendingUp,
  TrendingDown,
  Receipt,
  FileText,
  CreditCard,
  Building2,
  Calculator,
  AlertCircle,
  CheckCircle,
  Clock,
  ArrowRight,
  Plus,
  Download,
  Eye,
  BarChart3,
  PieChart,
  Wallet,
  Banknote,
  RefreshCw
} from 'lucide-react'

// Indian State Codes for GST
const indianStates = [
  { code: '01', name: 'Jammu and Kashmir' },
  { code: '02', name: 'Himachal Pradesh' },
  { code: '03', name: 'Punjab' },
  { code: '04', name: 'Chandigarh' },
  { code: '05', name: 'Uttarakhand' },
  { code: '06', name: 'Haryana' },
  { code: '07', name: 'Delhi' },
  { code: '08', name: 'Rajasthan' },
  { code: '09', name: 'Uttar Pradesh' },
  { code: '10', name: 'Bihar' },
  { code: '11', name: 'Sikkim' },
  { code: '12', name: 'Arunachal Pradesh' },
  { code: '13', name: 'Nagaland' },
  { code: '14', name: 'Manipur' },
  { code: '15', name: 'Mizoram' },
  { code: '16', name: 'Tripura' },
  { code: '17', name: 'Meghalaya' },
  { code: '18', name: 'Assam' },
  { code: '19', name: 'West Bengal' },
  { code: '20', name: 'Jharkhand' },
  { code: '21', name: 'Odisha' },
  { code: '22', name: 'Chhattisgarh' },
  { code: '23', name: 'Madhya Pradesh' },
  { code: '24', name: 'Gujarat' },
  { code: '27', name: 'Maharashtra' },
  { code: '29', name: 'Karnataka' },
  { code: '30', name: 'Goa' },
  { code: '32', name: 'Kerala' },
  { code: '33', name: 'Tamil Nadu' },
  { code: '36', name: 'Telangana' },
  { code: '37', name: 'Andhra Pradesh' },
]

// Financial Year options
const financialYears = [
  { value: '2025-26', label: 'FY 2025-26' },
  { value: '2024-25', label: 'FY 2024-25' },
  { value: '2023-24', label: 'FY 2023-24' },
]

// Mock dashboard data
const dashboardData = {
  revenue: {
    current: 4567890,
    previous: 3890000,
    growth: 17.4
  },
  expenses: {
    current: 2890000,
    previous: 2650000,
    growth: 9.1
  },
  profit: {
    current: 1677890,
    previous: 1240000,
    growth: 35.3
  },
  cashBalance: {
    current: 3450000,
    previous: 2890000,
    growth: 19.4
  },
  receivables: {
    total: 2345670,
    current: 890000,
    days30: 567890,
    days60: 456780,
    days90: 231000,
    overdue: 200000
  },
  payables: {
    total: 1234560,
    current: 567890,
    days30: 345670,
    days60: 189000,
    days90: 98000,
    overdue: 34000
  },
  gstLiability: {
    cgst: 123450,
    sgst: 123450,
    igst: 89000,
    total: 335900,
    dueDate: '2026-01-20'
  },
  tdsLiability: {
    section194C: 45670,
    section194J: 34560,
    section194I: 23450,
    total: 103680,
    dueDate: '2026-01-07'
  }
}

// GST Returns Status
const gstReturns = [
  {
    type: 'GSTR-1',
    period: 'December 2025',
    status: 'filed',
    dueDate: '2026-01-11',
    filedDate: '2026-01-08'
  },
  {
    type: 'GSTR-3B',
    period: 'December 2025',
    status: 'pending',
    dueDate: '2026-01-20',
    filedDate: null
  },
  {
    type: 'GSTR-1',
    period: 'January 2026',
    status: 'draft',
    dueDate: '2026-02-11',
    filedDate: null
  },
  {
    type: 'GSTR-3B',
    period: 'January 2026',
    status: 'upcoming',
    dueDate: '2026-02-20',
    filedDate: null
  }
]

// Recent Transactions
const recentTransactions = [
  {
    id: '1',
    type: 'invoice',
    number: 'INV-2026-0001',
    party: 'ABC Technologies Pvt Ltd',
    amount: 112100,
    date: '2026-01-05',
    status: 'sent'
  },
  {
    id: '2',
    type: 'payment',
    number: 'PAY-2026-0001',
    party: 'XYZ Solutions Ltd',
    amount: 88500,
    date: '2026-01-04',
    status: 'received'
  },
  {
    id: '3',
    type: 'bill',
    number: 'BILL-2026-0001',
    party: 'Office Supplies Co',
    amount: 23450,
    date: '2026-01-03',
    status: 'approved'
  },
  {
    id: '4',
    type: 'invoice',
    number: 'INV-2025-0148',
    party: 'PQR Industries',
    amount: 280250,
    date: '2025-12-28',
    status: 'overdue'
  }
]

export default function FinanceDashboardPage() {
  const [selectedFY, setSelectedFY] = React.useState('2025-26')

  const stats = [
    {
      title: 'Total Revenue',
      value: formatCurrencySmart(dashboardData.revenue.current),
      icon: TrendingUp,
      description: 'This financial year',
      trend: { value: dashboardData.revenue.growth, label: 'vs last year' },
      valueClassName: 'text-green-600'
    },
    {
      title: 'Total Expenses',
      value: formatCurrencySmart(dashboardData.expenses.current),
      icon: TrendingDown,
      description: 'This financial year',
      trend: { value: dashboardData.expenses.growth, label: 'vs last year', type: 'decrease' as const },
      valueClassName: 'text-red-600'
    },
    {
      title: 'Net Profit',
      value: formatCurrencySmart(dashboardData.profit.current),
      icon: IndianRupee,
      description: 'This financial year',
      trend: { value: dashboardData.profit.growth, label: 'vs last year' }
    },
    {
      title: 'Cash Balance',
      value: formatCurrencySmart(dashboardData.cashBalance.current),
      icon: Wallet,
      description: 'As of today',
      trend: { value: dashboardData.cashBalance.growth, label: 'vs last month' }
    }
  ]

  const getStatusBadge = (status: string) => {
    const config: Record<string, { label: string; className: string }> = {
      filed: { label: 'Filed', className: 'bg-green-100 text-green-800' },
      pending: { label: 'Pending', className: 'bg-yellow-100 text-yellow-800' },
      draft: { label: 'Draft', className: 'bg-gray-100 text-gray-800' },
      upcoming: { label: 'Upcoming', className: 'bg-blue-100 text-blue-800' },
      overdue: { label: 'Overdue', className: 'bg-red-100 text-red-800' },
      sent: { label: 'Sent', className: 'bg-blue-100 text-blue-800' },
      received: { label: 'Received', className: 'bg-green-100 text-green-800' },
      approved: { label: 'Approved', className: 'bg-purple-100 text-purple-800' }
    }
    const c = config[status] || config.pending
    return <Badge className={c.className}>{c.label}</Badge>
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Finance Dashboard"
        description="Financial overview and GST compliance"
        breadcrumbs={[
          { label: 'Dashboard', href: '/dashboard' },
          { label: 'Finance' }
        ]}
        actions={
          <div className="flex items-center gap-3">
            <Select value={selectedFY} onValueChange={setSelectedFY}>
              <SelectTrigger className="w-[140px]">
                <SelectValue placeholder="Select FY" />
              </SelectTrigger>
              <SelectContent>
                {financialYears.map(fy => (
                  <SelectItem key={fy.value} value={fy.value}>
                    {fy.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Button variant="outline" size="sm">
              <Download className="h-4 w-4 mr-2" />
              Export
            </Button>
            <Button variant="outline" size="sm">
              <RefreshCw className="h-4 w-4 mr-2" />
              Refresh
            </Button>
          </div>
        }
      />

      {/* Key Metrics */}
      <StatsGrid stats={stats} columns={4} />

      {/* Receivables & Payables Aging + GST/TDS Summary */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Receivables Aging */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle className="text-lg">Receivables Aging</CardTitle>
              <CardDescription>Outstanding customer invoices</CardDescription>
            </div>
            <Button variant="ghost" size="sm" asChild>
              <Link href="/finance/invoices">
                View All <ArrowRight className="h-4 w-4 ml-1" />
              </Link>
            </Button>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between text-2xl font-bold">
                <span>Total Receivables</span>
                <span className="text-blue-600">{formatCurrency(dashboardData.receivables.total)}</span>
              </div>

              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Current (0-30 days)</span>
                  <span className="font-medium">{formatCurrency(dashboardData.receivables.current)}</span>
                </div>
                <div className="h-2 bg-green-100 rounded-full">
                  <div
                    className="h-2 bg-green-500 rounded-full"
                    style={{ width: `${(dashboardData.receivables.current / dashboardData.receivables.total) * 100}%` }}
                  />
                </div>

                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">31-60 days</span>
                  <span className="font-medium">{formatCurrency(dashboardData.receivables.days30)}</span>
                </div>
                <div className="h-2 bg-yellow-100 rounded-full">
                  <div
                    className="h-2 bg-yellow-500 rounded-full"
                    style={{ width: `${(dashboardData.receivables.days30 / dashboardData.receivables.total) * 100}%` }}
                  />
                </div>

                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">61-90 days</span>
                  <span className="font-medium">{formatCurrency(dashboardData.receivables.days60)}</span>
                </div>
                <div className="h-2 bg-orange-100 rounded-full">
                  <div
                    className="h-2 bg-orange-500 rounded-full"
                    style={{ width: `${(dashboardData.receivables.days60 / dashboardData.receivables.total) * 100}%` }}
                  />
                </div>

                <div className="flex items-center justify-between">
                  <span className="text-sm text-red-600">90+ days (Overdue)</span>
                  <span className="font-medium text-red-600">{formatCurrency(dashboardData.receivables.days90 + dashboardData.receivables.overdue)}</span>
                </div>
                <div className="h-2 bg-red-100 rounded-full">
                  <div
                    className="h-2 bg-red-500 rounded-full"
                    style={{ width: `${((dashboardData.receivables.days90 + dashboardData.receivables.overdue) / dashboardData.receivables.total) * 100}%` }}
                  />
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Payables Aging */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle className="text-lg">Payables Aging</CardTitle>
              <CardDescription>Outstanding vendor bills</CardDescription>
            </div>
            <Button variant="ghost" size="sm" asChild>
              <Link href="/bills">
                View All <ArrowRight className="h-4 w-4 ml-1" />
              </Link>
            </Button>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between text-2xl font-bold">
                <span>Total Payables</span>
                <span className="text-red-600">{formatCurrency(dashboardData.payables.total)}</span>
              </div>

              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Current (0-30 days)</span>
                  <span className="font-medium">{formatCurrency(dashboardData.payables.current)}</span>
                </div>
                <div className="h-2 bg-green-100 rounded-full">
                  <div
                    className="h-2 bg-green-500 rounded-full"
                    style={{ width: `${(dashboardData.payables.current / dashboardData.payables.total) * 100}%` }}
                  />
                </div>

                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">31-60 days</span>
                  <span className="font-medium">{formatCurrency(dashboardData.payables.days30)}</span>
                </div>
                <div className="h-2 bg-yellow-100 rounded-full">
                  <div
                    className="h-2 bg-yellow-500 rounded-full"
                    style={{ width: `${(dashboardData.payables.days30 / dashboardData.payables.total) * 100}%` }}
                  />
                </div>

                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">61-90 days</span>
                  <span className="font-medium">{formatCurrency(dashboardData.payables.days60)}</span>
                </div>
                <div className="h-2 bg-orange-100 rounded-full">
                  <div
                    className="h-2 bg-orange-500 rounded-full"
                    style={{ width: `${(dashboardData.payables.days60 / dashboardData.payables.total) * 100}%` }}
                  />
                </div>

                <div className="flex items-center justify-between">
                  <span className="text-sm text-red-600">90+ days (Overdue)</span>
                  <span className="font-medium text-red-600">{formatCurrency(dashboardData.payables.days90 + dashboardData.payables.overdue)}</span>
                </div>
                <div className="h-2 bg-red-100 rounded-full">
                  <div
                    className="h-2 bg-red-500 rounded-full"
                    style={{ width: `${((dashboardData.payables.days90 + dashboardData.payables.overdue) / dashboardData.payables.total) * 100}%` }}
                  />
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* GST & TDS Liability */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* GST Liability Summary */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle className="text-lg flex items-center gap-2">
                <Receipt className="h-5 w-5" />
                GST Liability
              </CardTitle>
              <CardDescription>For December 2025</CardDescription>
            </div>
            <Button variant="ghost" size="sm" asChild>
              <Link href="/finance/gst">
                View Details <ArrowRight className="h-4 w-4 ml-1" />
              </Link>
            </Button>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between text-2xl font-bold">
                <span>Total GST Payable</span>
                <span className="text-primary">{formatCurrency(dashboardData.gstLiability.total)}</span>
              </div>

              <div className="grid grid-cols-3 gap-4 text-center">
                <div className="p-3 bg-muted/50 rounded-lg">
                  <p className="text-sm text-muted-foreground">CGST</p>
                  <p className="font-semibold">{formatCurrency(dashboardData.gstLiability.cgst)}</p>
                </div>
                <div className="p-3 bg-muted/50 rounded-lg">
                  <p className="text-sm text-muted-foreground">SGST</p>
                  <p className="font-semibold">{formatCurrency(dashboardData.gstLiability.sgst)}</p>
                </div>
                <div className="p-3 bg-muted/50 rounded-lg">
                  <p className="text-sm text-muted-foreground">IGST</p>
                  <p className="font-semibold">{formatCurrency(dashboardData.gstLiability.igst)}</p>
                </div>
              </div>

              <div className="flex items-center justify-between p-3 bg-yellow-50 rounded-lg border border-yellow-200">
                <div className="flex items-center gap-2">
                  <Clock className="h-4 w-4 text-yellow-600" />
                  <span className="text-sm">GSTR-3B Due Date</span>
                </div>
                <span className="font-medium text-yellow-700">{formatDate(dashboardData.gstLiability.dueDate)}</span>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* TDS Liability Summary */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle className="text-lg flex items-center gap-2">
                <Calculator className="h-5 w-5" />
                TDS Liability
              </CardTitle>
              <CardDescription>For December 2025</CardDescription>
            </div>
            <Button variant="ghost" size="sm" asChild>
              <Link href="/finance/tds">
                View Details <ArrowRight className="h-4 w-4 ml-1" />
              </Link>
            </Button>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between text-2xl font-bold">
                <span>Total TDS Payable</span>
                <span className="text-primary">{formatCurrency(dashboardData.tdsLiability.total)}</span>
              </div>

              <div className="space-y-2">
                <div className="flex items-center justify-between p-2 bg-muted/50 rounded">
                  <span className="text-sm">194C - Contractor</span>
                  <span className="font-medium">{formatCurrency(dashboardData.tdsLiability.section194C)}</span>
                </div>
                <div className="flex items-center justify-between p-2 bg-muted/50 rounded">
                  <span className="text-sm">194J - Professional Fees</span>
                  <span className="font-medium">{formatCurrency(dashboardData.tdsLiability.section194J)}</span>
                </div>
                <div className="flex items-center justify-between p-2 bg-muted/50 rounded">
                  <span className="text-sm">194I - Rent</span>
                  <span className="font-medium">{formatCurrency(dashboardData.tdsLiability.section194I)}</span>
                </div>
              </div>

              <div className="flex items-center justify-between p-3 bg-red-50 rounded-lg border border-red-200">
                <div className="flex items-center gap-2">
                  <AlertCircle className="h-4 w-4 text-red-600" />
                  <span className="text-sm">TDS Payment Due</span>
                </div>
                <span className="font-medium text-red-700">{formatDate(dashboardData.tdsLiability.dueDate)}</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* GST Returns Status & Quick Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* GST Returns Status */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="text-lg">GST Returns Status</CardTitle>
            <CardDescription>Filing status for recent periods</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {gstReturns.map((ret, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between p-3 border rounded-lg hover:bg-muted/50 transition-colors"
                >
                  <div className="flex items-center gap-4">
                    <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center">
                      <FileText className="h-5 w-5 text-primary" />
                    </div>
                    <div>
                      <p className="font-medium">{ret.type}</p>
                      <p className="text-sm text-muted-foreground">{ret.period}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <div className="text-right">
                      <p className="text-sm">Due: {formatDate(ret.dueDate)}</p>
                      {ret.filedDate && (
                        <p className="text-xs text-green-600">Filed: {formatDate(ret.filedDate)}</p>
                      )}
                    </div>
                    {getStatusBadge(ret.status)}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Quick Actions */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Quick Actions</CardTitle>
            <CardDescription>Common finance operations</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <Button className="w-full justify-start" variant="outline" asChild>
                <Link href="/finance/invoices/create">
                  <Plus className="h-4 w-4 mr-2" />
                  Create Invoice
                </Link>
              </Button>
              <Button className="w-full justify-start" variant="outline" asChild>
                <Link href="/bills/create">
                  <Plus className="h-4 w-4 mr-2" />
                  Record Bill
                </Link>
              </Button>
              <Button className="w-full justify-start" variant="outline" asChild>
                <Link href="/payments/create">
                  <CreditCard className="h-4 w-4 mr-2" />
                  Record Payment
                </Link>
              </Button>
              <Button className="w-full justify-start" variant="outline" asChild>
                <Link href="/finance/gst/gstr1">
                  <FileText className="h-4 w-4 mr-2" />
                  Prepare GSTR-1
                </Link>
              </Button>
              <Button className="w-full justify-start" variant="outline" asChild>
                <Link href="/finance/gst/gstr3b">
                  <FileText className="h-4 w-4 mr-2" />
                  File GSTR-3B
                </Link>
              </Button>
              <Button className="w-full justify-start" variant="outline" asChild>
                <Link href="/finance/gst/reconciliation">
                  <RefreshCw className="h-4 w-4 mr-2" />
                  GST Reconciliation
                </Link>
              </Button>
              <Button className="w-full justify-start" variant="outline" asChild>
                <Link href="/reports/profit-loss">
                  <BarChart3 className="h-4 w-4 mr-2" />
                  P&L Report
                </Link>
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent Transactions */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle className="text-lg">Recent Transactions</CardTitle>
            <CardDescription>Latest financial activities</CardDescription>
          </div>
          <Button variant="ghost" size="sm">
            View All <ArrowRight className="h-4 w-4 ml-1" />
          </Button>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {recentTransactions.map((txn) => (
              <div
                key={txn.id}
                className="flex items-center justify-between p-3 border rounded-lg hover:bg-muted/50 transition-colors cursor-pointer"
              >
                <div className="flex items-center gap-4">
                  <div className={`h-10 w-10 rounded-lg flex items-center justify-center ${
                    txn.type === 'invoice' ? 'bg-blue-100' :
                    txn.type === 'payment' ? 'bg-green-100' : 'bg-orange-100'
                  }`}>
                    {txn.type === 'invoice' ? <FileText className="h-5 w-5 text-blue-600" /> :
                     txn.type === 'payment' ? <Banknote className="h-5 w-5 text-green-600" /> :
                     <Receipt className="h-5 w-5 text-orange-600" />}
                  </div>
                  <div>
                    <p className="font-medium">{txn.number}</p>
                    <p className="text-sm text-muted-foreground">{txn.party}</p>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <div className="text-right">
                    <p className={`font-semibold ${
                      txn.type === 'payment' ? 'text-green-600' :
                      txn.type === 'bill' ? 'text-red-600' : ''
                    }`}>
                      {txn.type === 'payment' ? '+' : ''}{formatCurrency(txn.amount)}
                    </p>
                    <p className="text-xs text-muted-foreground">{formatDate(txn.date)}</p>
                  </div>
                  {getStatusBadge(txn.status)}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
