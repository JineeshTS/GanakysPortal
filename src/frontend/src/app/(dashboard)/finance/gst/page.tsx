'use client'

import * as React from 'react'
import { useState, useEffect } from 'react'
import Link from 'next/link'
import { useApi } from '@/hooks/use-api'
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
import { formatCurrency, formatDate } from '@/lib/format'
import {
  FileText,
  ArrowRight,
  Clock,
  CheckCircle,
  AlertCircle,
  XCircle,
  Calendar,
  Download,
  Upload,
  RefreshCw,
  Calculator,
  Receipt,
  IndianRupee,
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  ExternalLink,
  Loader2
} from 'lucide-react'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'

// API Response types
interface GSTCalculationResult {
  base_amount: string
  taxable_value: string
  gst_rate: string
  cgst_rate: string
  cgst: string
  sgst_rate: string
  sgst: string
  igst_rate: string
  igst: string
  cess_rate: string
  cess: string
  total_tax: string
  total_amount: string
  is_igst: boolean
}

interface GSTINValidationResult {
  gstin: string
  is_valid: boolean
  state_code: string
  state_name: string
  pan: string
  entity_type_code: string
  entity_type: string
  checksum_valid: boolean
  errors: string[]
}

// Financial Years
const financialYears = [
  { value: '2025-26', label: 'FY 2025-26' },
  { value: '2024-25', label: 'FY 2024-25' },
  { value: '2023-24', label: 'FY 2023-24' },
]

// Periods
const periods = [
  { value: '01-2026', label: 'January 2026' },
  { value: '12-2025', label: 'December 2025' },
  { value: '11-2025', label: 'November 2025' },
  { value: '10-2025', label: 'October 2025' },
  { value: '09-2025', label: 'September 2025' },
]

// GST Returns Data
const gstReturnsData = {
  gstr1: [
    { period: 'January 2026', status: 'pending', dueDate: '2026-02-11', filedDate: null, invoices: 12, value: 567890 },
    { period: 'December 2025', status: 'filed', dueDate: '2026-01-11', filedDate: '2026-01-08', invoices: 15, value: 789000 },
    { period: 'November 2025', status: 'filed', dueDate: '2025-12-11', filedDate: '2025-12-09', invoices: 18, value: 645000 },
  ],
  gstr3b: [
    { period: 'January 2026', status: 'pending', dueDate: '2026-02-20', filedDate: null, liability: 98700 },
    { period: 'December 2025', status: 'filed', dueDate: '2026-01-20', filedDate: '2026-01-18', liability: 124500 },
    { period: 'November 2025', status: 'filed', dueDate: '2025-12-20', filedDate: '2025-12-17', liability: 112300 },
  ],
  gstr9: [
    { period: 'FY 2024-25', status: 'pending', dueDate: '2025-12-31', filedDate: null },
    { period: 'FY 2023-24', status: 'filed', dueDate: '2024-12-31', filedDate: '2024-12-28' },
  ]
}

// ITC Summary
const itcSummary = {
  available: {
    cgst: 234500,
    sgst: 234500,
    igst: 156780,
    cess: 0,
    total: 625780
  },
  utilized: {
    cgst: 123450,
    sgst: 123450,
    igst: 89000,
    cess: 0,
    total: 335900
  },
  balance: {
    cgst: 111050,
    sgst: 111050,
    igst: 67780,
    cess: 0,
    total: 289880
  },
  reversal: {
    rule42: 12340,
    rule43: 5670,
    others: 3450,
    total: 21460
  }
}

// Reconciliation Status
const reconciliationStatus = {
  gstr2aVsBooks: {
    matched: 145,
    mismatched: 12,
    notInBooks: 5,
    notIn2A: 8,
    matchedValue: 5670000,
    mismatchedValue: 234560
  },
  gstr2bVsBooks: {
    matched: 148,
    mismatched: 8,
    notInBooks: 3,
    notIn2B: 6,
    matchedValue: 5890000,
    mismatchedValue: 156780
  }
}

// Dashboard stats
const gstStats = {
  totalOutputTax: 456780,
  totalInputTax: 335900,
  netLiability: 120880,
  cashLedger: 234500,
  creditLedger: 289880,
  liabilityLedger: 120880
}

// GST Calculator Dialog Component
function GSTCalculatorDialog({
  open,
  onOpenChange
}: {
  open: boolean
  onOpenChange: (open: boolean) => void
}) {
  const api = useApi()
  const [amount, setAmount] = useState('')
  const [gstRate, setGstRate] = useState('18')
  const [isIGST, setIsIGST] = useState(false)
  const [isInclusive, setIsInclusive] = useState(false)
  const [result, setResult] = useState<GSTCalculationResult | null>(null)
  const [calculating, setCalculating] = useState(false)

  const handleCalculate = async () => {
    if (!amount || isNaN(parseFloat(amount))) return

    setCalculating(true)
    try {
      const response = await api.post('/gst/calculate', {
        amount: parseFloat(amount),
        gst_rate: parseInt(gstRate),
        is_igst: isIGST,
        is_inclusive: isInclusive,
        cess_rate: 0
      }) as GSTCalculationResult

      setResult(response)
    } catch (error) {
      console.error('GST calculation failed:', error)
    } finally {
      setCalculating(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>GST Calculator</DialogTitle>
          <DialogDescription>
            Calculate GST on any amount with different rates
          </DialogDescription>
        </DialogHeader>

        <div className="grid gap-4 py-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="amount">Amount (₹)</Label>
              <Input
                id="amount"
                type="number"
                placeholder="10000"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="rate">GST Rate</Label>
              <Select value={gstRate} onValueChange={setGstRate}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="0">0% (Exempt)</SelectItem>
                  <SelectItem value="5">5%</SelectItem>
                  <SelectItem value="12">12%</SelectItem>
                  <SelectItem value="18">18%</SelectItem>
                  <SelectItem value="28">28%</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="flex gap-4">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={isIGST}
                onChange={(e) => setIsIGST(e.target.checked)}
                className="rounded"
              />
              <span className="text-sm">Inter-state (IGST)</span>
            </label>
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={isInclusive}
                onChange={(e) => setIsInclusive(e.target.checked)}
                className="rounded"
              />
              <span className="text-sm">GST Inclusive</span>
            </label>
          </div>

          <Button onClick={handleCalculate} disabled={calculating || !amount}>
            {calculating ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Calculating...
              </>
            ) : (
              <>
                <Calculator className="h-4 w-4 mr-2" />
                Calculate
              </>
            )}
          </Button>

          {result && (
            <div className="mt-4 p-4 bg-muted rounded-lg space-y-3">
              <div className="grid grid-cols-2 gap-2 text-sm">
                <span className="text-muted-foreground">Taxable Value:</span>
                <span className="font-medium text-right">{formatCurrency(parseFloat(result.taxable_value))}</span>

                {result.is_igst ? (
                  <>
                    <span className="text-muted-foreground">IGST ({result.igst_rate}%):</span>
                    <span className="font-medium text-right">{formatCurrency(parseFloat(result.igst))}</span>
                  </>
                ) : (
                  <>
                    <span className="text-muted-foreground">CGST ({result.cgst_rate}%):</span>
                    <span className="font-medium text-right">{formatCurrency(parseFloat(result.cgst))}</span>
                    <span className="text-muted-foreground">SGST ({result.sgst_rate}%):</span>
                    <span className="font-medium text-right">{formatCurrency(parseFloat(result.sgst))}</span>
                  </>
                )}

                <span className="text-muted-foreground">Total Tax:</span>
                <span className="font-medium text-right text-blue-600">{formatCurrency(parseFloat(result.total_tax))}</span>

                <span className="text-muted-foreground font-semibold">Total Amount:</span>
                <span className="font-bold text-right text-primary">{formatCurrency(parseFloat(result.total_amount))}</span>
              </div>
            </div>
          )}
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Close
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

export default function GSTCompliancePage() {
  const [selectedFY, setSelectedFY] = useState('2025-26')
  const [selectedPeriod, setSelectedPeriod] = useState('01-2026')
  const [calculatorOpen, setCalculatorOpen] = useState(false)

  const stats = [
    {
      title: 'Output Tax Liability',
      value: formatCurrency(gstStats.totalOutputTax),
      icon: TrendingUp,
      description: 'Current period',
      valueClassName: 'text-red-600'
    },
    {
      title: 'Input Tax Credit',
      value: formatCurrency(gstStats.totalInputTax),
      icon: TrendingDown,
      description: 'Available ITC',
      valueClassName: 'text-green-600'
    },
    {
      title: 'Net GST Payable',
      value: formatCurrency(gstStats.netLiability),
      icon: IndianRupee,
      description: 'After ITC utilization'
    },
    {
      title: 'Credit Ledger Balance',
      value: formatCurrency(gstStats.creditLedger),
      icon: Receipt,
      description: 'Available balance'
    }
  ]

  const getStatusBadge = (status: string) => {
    const config: Record<string, { label: string; className: string; icon: React.ReactNode }> = {
      filed: {
        label: 'Filed',
        className: 'bg-green-100 text-green-800',
        icon: <CheckCircle className="h-3 w-3" />
      },
      pending: {
        label: 'Pending',
        className: 'bg-yellow-100 text-yellow-800',
        icon: <Clock className="h-3 w-3" />
      },
      overdue: {
        label: 'Overdue',
        className: 'bg-red-100 text-red-800',
        icon: <AlertCircle className="h-3 w-3" />
      },
      draft: {
        label: 'Draft',
        className: 'bg-gray-100 text-gray-800',
        icon: <FileText className="h-3 w-3" />
      }
    }
    const c = config[status] || config.pending
    return (
      <Badge className={`${c.className} flex items-center gap-1`}>
        {c.icon}
        {c.label}
      </Badge>
    )
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="GST Compliance"
        description="GST returns filing and ITC management"
        breadcrumbs={[
          { label: 'Dashboard', href: '/dashboard' },
          { label: 'Finance', href: '/finance' },
          { label: 'GST Compliance' }
        ]}
        actions={
          <div className="flex items-center gap-3">
            <Select value={selectedFY} onValueChange={setSelectedFY}>
              <SelectTrigger className="w-[140px]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {financialYears.map(fy => (
                  <SelectItem key={fy.value} value={fy.value}>
                    {fy.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Button variant="outline" size="sm" onClick={() => setCalculatorOpen(true)}>
              <Calculator className="h-4 w-4 mr-2" />
              GST Calculator
            </Button>
            <Button variant="outline" size="sm">
              <RefreshCw className="h-4 w-4 mr-2" />
              Sync with GST Portal
            </Button>
          </div>
        }
      />

      {/* Stats */}
      <StatsGrid stats={stats} columns={4} />

      {/* GST Returns Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* GSTR-1 Card */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <div>
              <CardTitle className="text-lg">GSTR-1</CardTitle>
              <CardDescription>Outward Supplies</CardDescription>
            </div>
            <div className="h-10 w-10 rounded-lg bg-blue-100 flex items-center justify-center">
              <FileText className="h-5 w-5 text-blue-600" />
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            {gstReturnsData.gstr1.slice(0, 2).map((ret, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-muted/50 rounded-lg">
                <div>
                  <p className="font-medium text-sm">{ret.period}</p>
                  <p className="text-xs text-muted-foreground">Due: {formatDate(ret.dueDate)}</p>
                </div>
                <div className="text-right">
                  {getStatusBadge(ret.status)}
                  {ret.filedDate && (
                    <p className="text-xs text-green-600 mt-1">Filed: {formatDate(ret.filedDate)}</p>
                  )}
                </div>
              </div>
            ))}

            <div className="pt-2">
              <Button className="w-full" variant="outline" asChild>
                <Link href="/finance/gst/gstr1">
                  View GSTR-1 Details <ArrowRight className="h-4 w-4 ml-2" />
                </Link>
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* GSTR-3B Card */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <div>
              <CardTitle className="text-lg">GSTR-3B</CardTitle>
              <CardDescription>Summary Return</CardDescription>
            </div>
            <div className="h-10 w-10 rounded-lg bg-purple-100 flex items-center justify-center">
              <Calculator className="h-5 w-5 text-purple-600" />
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            {gstReturnsData.gstr3b.slice(0, 2).map((ret, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-muted/50 rounded-lg">
                <div>
                  <p className="font-medium text-sm">{ret.period}</p>
                  <p className="text-xs text-muted-foreground">Due: {formatDate(ret.dueDate)}</p>
                </div>
                <div className="text-right">
                  {getStatusBadge(ret.status)}
                  <p className="text-xs font-medium mt-1">{formatCurrency(ret.liability)}</p>
                </div>
              </div>
            ))}

            <div className="pt-2">
              <Button className="w-full" variant="outline" asChild>
                <Link href="/finance/gst/gstr3b">
                  View GSTR-3B Details <ArrowRight className="h-4 w-4 ml-2" />
                </Link>
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* GSTR-9 Card */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <div>
              <CardTitle className="text-lg">GSTR-9</CardTitle>
              <CardDescription>Annual Return</CardDescription>
            </div>
            <div className="h-10 w-10 rounded-lg bg-orange-100 flex items-center justify-center">
              <Calendar className="h-5 w-5 text-orange-600" />
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            {gstReturnsData.gstr9.map((ret, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-muted/50 rounded-lg">
                <div>
                  <p className="font-medium text-sm">{ret.period}</p>
                  <p className="text-xs text-muted-foreground">Due: {formatDate(ret.dueDate)}</p>
                </div>
                <div className="text-right">
                  {getStatusBadge(ret.status)}
                  {ret.filedDate && (
                    <p className="text-xs text-green-600 mt-1">Filed: {formatDate(ret.filedDate)}</p>
                  )}
                </div>
              </div>
            ))}

            <div className="pt-2">
              <Button className="w-full" variant="outline" disabled>
                Prepare GSTR-9 <ArrowRight className="h-4 w-4 ml-2" />
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* ITC Summary & Reconciliation */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* ITC Summary */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <Receipt className="h-5 w-5" />
              Input Tax Credit Summary
            </CardTitle>
            <CardDescription>ITC available, utilized and balance</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-2 font-medium">Tax Type</th>
                    <th className="text-right py-2 font-medium">Available</th>
                    <th className="text-right py-2 font-medium">Utilized</th>
                    <th className="text-right py-2 font-medium">Balance</th>
                  </tr>
                </thead>
                <tbody>
                  <tr className="border-b">
                    <td className="py-2">CGST</td>
                    <td className="text-right py-2">{formatCurrency(itcSummary.available.cgst)}</td>
                    <td className="text-right py-2">{formatCurrency(itcSummary.utilized.cgst)}</td>
                    <td className="text-right py-2 font-medium">{formatCurrency(itcSummary.balance.cgst)}</td>
                  </tr>
                  <tr className="border-b">
                    <td className="py-2">SGST</td>
                    <td className="text-right py-2">{formatCurrency(itcSummary.available.sgst)}</td>
                    <td className="text-right py-2">{formatCurrency(itcSummary.utilized.sgst)}</td>
                    <td className="text-right py-2 font-medium">{formatCurrency(itcSummary.balance.sgst)}</td>
                  </tr>
                  <tr className="border-b">
                    <td className="py-2">IGST</td>
                    <td className="text-right py-2">{formatCurrency(itcSummary.available.igst)}</td>
                    <td className="text-right py-2">{formatCurrency(itcSummary.utilized.igst)}</td>
                    <td className="text-right py-2 font-medium">{formatCurrency(itcSummary.balance.igst)}</td>
                  </tr>
                  <tr className="font-semibold bg-muted/50">
                    <td className="py-2">Total</td>
                    <td className="text-right py-2">{formatCurrency(itcSummary.available.total)}</td>
                    <td className="text-right py-2">{formatCurrency(itcSummary.utilized.total)}</td>
                    <td className="text-right py-2 text-primary">{formatCurrency(itcSummary.balance.total)}</td>
                  </tr>
                </tbody>
              </table>
            </div>

            <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
              <div className="flex items-start gap-2">
                <AlertTriangle className="h-4 w-4 text-yellow-600 mt-0.5" />
                <div className="text-sm">
                  <p className="font-medium text-yellow-800">ITC Reversal Required</p>
                  <p className="text-yellow-600">
                    Rule 42/43 reversal: {formatCurrency(itcSummary.reversal.total)}
                  </p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Reconciliation Status */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle className="text-lg flex items-center gap-2">
                <RefreshCw className="h-5 w-5" />
                Reconciliation Status
              </CardTitle>
              <CardDescription>GSTR-2A/2B vs Books comparison</CardDescription>
            </div>
            <Button variant="outline" size="sm" asChild>
              <Link href="/finance/gst/reconciliation">
                View Details <ArrowRight className="h-4 w-4 ml-1" />
              </Link>
            </Button>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* GSTR-2A Reconciliation */}
            <div>
              <h4 className="font-medium mb-3">GSTR-2A vs Books</h4>
              <div className="grid grid-cols-2 gap-4">
                <div className="p-3 bg-green-50 rounded-lg">
                  <div className="flex items-center gap-2">
                    <CheckCircle className="h-4 w-4 text-green-600" />
                    <span className="text-sm text-green-700">Matched</span>
                  </div>
                  <p className="text-2xl font-bold text-green-700 mt-1">
                    {reconciliationStatus.gstr2aVsBooks.matched}
                  </p>
                  <p className="text-xs text-green-600">
                    {formatCurrency(reconciliationStatus.gstr2aVsBooks.matchedValue)}
                  </p>
                </div>
                <div className="p-3 bg-red-50 rounded-lg">
                  <div className="flex items-center gap-2">
                    <XCircle className="h-4 w-4 text-red-600" />
                    <span className="text-sm text-red-700">Mismatched</span>
                  </div>
                  <p className="text-2xl font-bold text-red-700 mt-1">
                    {reconciliationStatus.gstr2aVsBooks.mismatched}
                  </p>
                  <p className="text-xs text-red-600">
                    {formatCurrency(reconciliationStatus.gstr2aVsBooks.mismatchedValue)}
                  </p>
                </div>
              </div>
              <div className="flex gap-4 mt-3 text-sm">
                <span className="text-muted-foreground">
                  Not in Books: <span className="font-medium text-foreground">{reconciliationStatus.gstr2aVsBooks.notInBooks}</span>
                </span>
                <span className="text-muted-foreground">
                  Not in 2A: <span className="font-medium text-foreground">{reconciliationStatus.gstr2aVsBooks.notIn2A}</span>
                </span>
              </div>
            </div>

            {/* GSTR-2B Reconciliation */}
            <div>
              <h4 className="font-medium mb-3">GSTR-2B vs Books</h4>
              <div className="grid grid-cols-2 gap-4">
                <div className="p-3 bg-green-50 rounded-lg">
                  <div className="flex items-center gap-2">
                    <CheckCircle className="h-4 w-4 text-green-600" />
                    <span className="text-sm text-green-700">Matched</span>
                  </div>
                  <p className="text-2xl font-bold text-green-700 mt-1">
                    {reconciliationStatus.gstr2bVsBooks.matched}
                  </p>
                  <p className="text-xs text-green-600">
                    {formatCurrency(reconciliationStatus.gstr2bVsBooks.matchedValue)}
                  </p>
                </div>
                <div className="p-3 bg-red-50 rounded-lg">
                  <div className="flex items-center gap-2">
                    <XCircle className="h-4 w-4 text-red-600" />
                    <span className="text-sm text-red-700">Mismatched</span>
                  </div>
                  <p className="text-2xl font-bold text-red-700 mt-1">
                    {reconciliationStatus.gstr2bVsBooks.mismatched}
                  </p>
                  <p className="text-xs text-red-600">
                    {formatCurrency(reconciliationStatus.gstr2bVsBooks.mismatchedValue)}
                  </p>
                </div>
              </div>
              <div className="flex gap-4 mt-3 text-sm">
                <span className="text-muted-foreground">
                  Not in Books: <span className="font-medium text-foreground">{reconciliationStatus.gstr2bVsBooks.notInBooks}</span>
                </span>
                <span className="text-muted-foreground">
                  Not in 2B: <span className="font-medium text-foreground">{reconciliationStatus.gstr2bVsBooks.notIn2B}</span>
                </span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Pending Actions & Due Dates */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Upcoming Due Dates & Actions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="p-4 border rounded-lg bg-yellow-50 border-yellow-200">
              <div className="flex items-center gap-2 text-yellow-800">
                <Clock className="h-4 w-4" />
                <span className="font-medium">GSTR-3B - Jan 2026</span>
              </div>
              <p className="text-sm text-yellow-600 mt-1">Due: 20 Feb 2026</p>
              <p className="text-lg font-bold text-yellow-800 mt-2">{formatCurrency(98700)}</p>
              <Button size="sm" className="mt-3 w-full" variant="outline" asChild>
                <Link href="/finance/gst/gstr3b">Prepare Now</Link>
              </Button>
            </div>

            <div className="p-4 border rounded-lg bg-blue-50 border-blue-200">
              <div className="flex items-center gap-2 text-blue-800">
                <FileText className="h-4 w-4" />
                <span className="font-medium">GSTR-1 - Jan 2026</span>
              </div>
              <p className="text-sm text-blue-600 mt-1">Due: 11 Feb 2026</p>
              <p className="text-lg font-bold text-blue-800 mt-2">12 Invoices</p>
              <Button size="sm" className="mt-3 w-full" variant="outline" asChild>
                <Link href="/finance/gst/gstr1">Prepare Now</Link>
              </Button>
            </div>

            <div className="p-4 border rounded-lg bg-green-50 border-green-200">
              <div className="flex items-center gap-2 text-green-800">
                <RefreshCw className="h-4 w-4" />
                <span className="font-medium">ITC Reconciliation</span>
              </div>
              <p className="text-sm text-green-600 mt-1">12 items need attention</p>
              <p className="text-lg font-bold text-green-800 mt-2">{formatCurrency(234560)}</p>
              <Button size="sm" className="mt-3 w-full" variant="outline" asChild>
                <Link href="/finance/gst/reconciliation">Reconcile Now</Link>
              </Button>
            </div>

            <div className="p-4 border rounded-lg">
              <div className="flex items-center gap-2 text-muted-foreground">
                <ExternalLink className="h-4 w-4" />
                <span className="font-medium">GST Portal</span>
              </div>
              <p className="text-sm text-muted-foreground mt-1">Quick access</p>
              <div className="mt-4 space-y-2">
                <Button size="sm" className="w-full" variant="outline" asChild>
                  <a href="https://gst.gov.in" target="_blank" rel="noopener noreferrer">
                    Open GST Portal <ExternalLink className="h-3 w-3 ml-1" />
                  </a>
                </Button>
                <Button size="sm" className="w-full" variant="outline" asChild>
                  <a href="https://einvoice.gst.gov.in" target="_blank" rel="noopener noreferrer">
                    E-Invoice Portal <ExternalLink className="h-3 w-3 ml-1" />
                  </a>
                </Button>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* GST Calculator Dialog */}
      <GSTCalculatorDialog open={calculatorOpen} onOpenChange={setCalculatorOpen} />
    </div>
  )
}
