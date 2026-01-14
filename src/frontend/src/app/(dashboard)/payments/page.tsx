'use client'

import * as React from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { PageHeader } from '@/components/layout/page-header'
import { DataTable, Column } from '@/components/layout/data-table'
import { StatsGrid } from '@/components/layout/stat-card'
import { SearchInput } from '@/components/forms/search-input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { formatCurrency, formatDate } from '@/lib/format'
import { useDebounce, useApi } from '@/hooks'
import {
  Plus,
  Download,
  ArrowUpRight,
  ArrowDownLeft,
  CreditCard,
  Building2,
  Wallet,
  CheckCircle,
  Clock,
  XCircle,
  RefreshCw,
  Loader2,
  AlertCircle
} from 'lucide-react'
import type { Payment } from '@/types'

// API Response interfaces
interface PaymentsListResponse {
  payments: PaymentRecord[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

interface PaymentsSummary {
  received_this_month: number
  paid_this_month: number
  pending_receipts: number
  pending_payments: number
  cheques_pending: number
  reconciled_count: number
  by_mode: {
    bank_transfer: { received: number; paid: number }
    cheque: { received: number; paid: number }
    cash: { received: number; paid: number }
    upi: { received: number; paid: number }
    card: { received: number; paid: number }
  }
}

// Extended payment type for UI
interface PaymentRecord {
  id: string
  payment_number: string
  type: 'received' | 'made'
  party_name: string
  party_type: 'customer' | 'vendor'
  amount: number
  payment_mode: 'bank_transfer' | 'cheque' | 'cash' | 'upi' | 'card'
  reference_number?: string
  bank_account?: string
  date: string
  status: 'completed' | 'pending' | 'failed' | 'reconciled'
  invoices?: string[]
  bills?: string[]
  notes?: string
}

// Mock payment data
const mockPayments: PaymentRecord[] = [
  {
    id: '1',
    payment_number: 'PAY-IN-2026-0001',
    type: 'received',
    party_name: 'XYZ Solutions Ltd',
    party_type: 'customer',
    amount: 88500,
    payment_mode: 'bank_transfer',
    reference_number: 'NEFT123456789',
    bank_account: 'HDFC Bank - Current A/c',
    date: '2026-01-05',
    status: 'reconciled',
    invoices: ['INV-2025-0147']
  },
  {
    id: '2',
    payment_number: 'PAY-OUT-2026-0001',
    type: 'made',
    party_name: 'Cloud Services Inc.',
    party_type: 'vendor',
    amount: 162000,
    payment_mode: 'bank_transfer',
    reference_number: 'RTGS987654321',
    bank_account: 'HDFC Bank - Current A/c',
    date: '2026-01-03',
    status: 'completed',
    bills: ['BILL-2025-0089']
  },
  {
    id: '3',
    payment_number: 'PAY-IN-2026-0002',
    type: 'received',
    party_name: 'PQR Industries',
    party_type: 'customer',
    amount: 100000,
    payment_mode: 'cheque',
    reference_number: 'CHQ-456789',
    bank_account: 'HDFC Bank - Current A/c',
    date: '2026-01-04',
    status: 'pending',
    invoices: ['INV-2025-0145'],
    notes: 'Cheque deposited, awaiting clearance'
  },
  {
    id: '4',
    payment_number: 'PAY-OUT-2026-0002',
    type: 'made',
    party_name: 'Premium Office Space',
    party_type: 'vendor',
    amount: 50000,
    payment_mode: 'bank_transfer',
    reference_number: 'NEFT111222333',
    bank_account: 'ICICI Bank - Salary A/c',
    date: '2026-01-06',
    status: 'completed',
    bills: ['BILL-2025-0085']
  },
  {
    id: '5',
    payment_number: 'PAY-IN-2026-0003',
    type: 'received',
    party_name: 'LMN Enterprises',
    party_type: 'customer',
    amount: 25000,
    payment_mode: 'upi',
    reference_number: 'UPI/123456/001',
    date: '2026-01-06',
    status: 'completed',
    notes: 'Advance payment'
  }
]

// Stats
const paymentStats = {
  receivedThisMonth: 213500,
  paidThisMonth: 212000,
  pendingReceipts: 180250,
  pendingPayments: 191650,
  chequesPending: 100000,
  reconciledCount: 45
}

export default function PaymentsPage() {
  const router = useRouter()
  const [searchQuery, setSearchQuery] = React.useState('')
  const [typeFilter, setTypeFilter] = React.useState<string>('all')
  const [statusFilter, setStatusFilter] = React.useState<string>('all')

  const debouncedSearch = useDebounce(searchQuery, 300)

  const { data: paymentsData, isLoading: paymentsLoading, error: paymentsError, get: getPayments } = useApi<PaymentsListResponse>()
  const { data: summaryData, isLoading: summaryLoading, get: getSummary } = useApi<PaymentsSummary>()

  // Fetch payments and summary on mount
  React.useEffect(() => {
    const params = new URLSearchParams()
    if (debouncedSearch) params.set('search', debouncedSearch)
    if (typeFilter !== 'all') params.set('type', typeFilter)
    if (statusFilter !== 'all') params.set('status', statusFilter)

    getPayments(`/payments?${params.toString()}`)
    getSummary('/payments/summary')
  }, [debouncedSearch, typeFilter, statusFilter, getPayments, getSummary])

  const payments = paymentsData?.payments || mockPayments
  const isLoading = paymentsLoading || summaryLoading

  const filteredPayments = React.useMemo(() => {
    let result = [...payments]

    if (debouncedSearch) {
      const query = debouncedSearch.toLowerCase()
      result = result.filter(p =>
        p.payment_number.toLowerCase().includes(query) ||
        p.party_name.toLowerCase().includes(query) ||
        p.reference_number?.toLowerCase().includes(query)
      )
    }

    if (typeFilter !== 'all') {
      result = result.filter(p => p.type === typeFilter)
    }

    if (statusFilter !== 'all') {
      result = result.filter(p => p.status === statusFilter)
    }

    return result
  }, [payments, debouncedSearch, typeFilter, statusFilter])

  // Use API data for stats with fallback to mock
  const statsData = {
    receivedThisMonth: summaryData?.received_this_month ?? paymentStats.receivedThisMonth,
    paidThisMonth: summaryData?.paid_this_month ?? paymentStats.paidThisMonth,
    pendingReceipts: summaryData?.pending_receipts ?? paymentStats.pendingReceipts,
    chequesPending: summaryData?.cheques_pending ?? paymentStats.chequesPending
  }

  const stats = [
    {
      title: 'Received This Month',
      value: formatCurrency(statsData.receivedThisMonth),
      icon: ArrowDownLeft,
      description: 'From customers',
      valueClassName: 'text-green-600'
    },
    {
      title: 'Paid This Month',
      value: formatCurrency(statsData.paidThisMonth),
      icon: ArrowUpRight,
      description: 'To vendors',
      valueClassName: 'text-red-600'
    },
    {
      title: 'Pending Receipts',
      value: formatCurrency(statsData.pendingReceipts),
      icon: Clock,
      description: 'From customers'
    },
    {
      title: 'Cheques Pending',
      value: formatCurrency(statsData.chequesPending),
      icon: CreditCard,
      description: 'Awaiting clearance'
    }
  ]

  const getStatusBadge = (status: string) => {
    const statusConfig: Record<string, { label: string; className: string; icon: React.ElementType }> = {
      completed: { label: 'Completed', className: 'bg-green-100 text-green-800', icon: CheckCircle },
      pending: { label: 'Pending', className: 'bg-yellow-100 text-yellow-800', icon: Clock },
      failed: { label: 'Failed', className: 'bg-red-100 text-red-800', icon: XCircle },
      reconciled: { label: 'Reconciled', className: 'bg-blue-100 text-blue-800', icon: RefreshCw }
    }

    const config = statusConfig[status] || statusConfig.pending
    const Icon = config.icon

    return (
      <Badge className={config.className}>
        <Icon className="h-3 w-3 mr-1" />
        {config.label}
      </Badge>
    )
  }

  const getPaymentModeBadge = (mode: string) => {
    const modeConfig: Record<string, { label: string; className: string }> = {
      bank_transfer: { label: 'Bank Transfer', className: 'bg-blue-50 text-blue-700' },
      cheque: { label: 'Cheque', className: 'bg-purple-50 text-purple-700' },
      cash: { label: 'Cash', className: 'bg-green-50 text-green-700' },
      upi: { label: 'UPI', className: 'bg-orange-50 text-orange-700' },
      card: { label: 'Card', className: 'bg-pink-50 text-pink-700' }
    }

    const config = modeConfig[mode] || modeConfig.bank_transfer
    return <Badge variant="outline" className={config.className}>{config.label}</Badge>
  }

  const columns: Column<PaymentRecord>[] = [
    {
      key: 'payment_number',
      header: 'Payment',
      accessor: (row) => (
        <div className="flex items-center gap-2">
          {row.type === 'received' ? (
            <ArrowDownLeft className="h-4 w-4 text-green-600" />
          ) : (
            <ArrowUpRight className="h-4 w-4 text-red-600" />
          )}
          <div>
            <p className="font-medium font-mono text-sm">{row.payment_number}</p>
            <p className="text-xs text-muted-foreground">{formatDate(row.date)}</p>
          </div>
        </div>
      )
    },
    {
      key: 'party',
      header: 'Party',
      accessor: (row) => (
        <div>
          <p className="font-medium">{row.party_name}</p>
          <p className="text-xs text-muted-foreground capitalize">{row.party_type}</p>
        </div>
      )
    },
    {
      key: 'payment_mode',
      header: 'Mode',
      accessor: (row) => (
        <div className="space-y-1">
          {getPaymentModeBadge(row.payment_mode)}
          {row.reference_number && (
            <p className="text-xs text-muted-foreground font-mono">{row.reference_number}</p>
          )}
        </div>
      )
    },
    {
      key: 'bank_account',
      header: 'Bank',
      accessor: (row) => row.bank_account || '-'
    },
    {
      key: 'amount',
      header: 'Amount',
      className: 'text-right',
      headerClassName: 'text-right',
      accessor: (row) => (
        <span className={`font-semibold ${row.type === 'received' ? 'text-green-600' : 'text-red-600'}`}>
          {row.type === 'received' ? '+' : '-'}{formatCurrency(row.amount)}
        </span>
      )
    },
    {
      key: 'status',
      header: 'Status',
      accessor: (row) => getStatusBadge(row.status)
    },
    {
      key: 'reference',
      header: 'Against',
      accessor: (row) => (
        <div className="text-xs">
          {row.invoices && row.invoices.length > 0 && (
            <p className="text-blue-600">{row.invoices.join(', ')}</p>
          )}
          {row.bills && row.bills.length > 0 && (
            <p className="text-orange-600">{row.bills.join(', ')}</p>
          )}
          {!row.invoices && !row.bills && (
            <span className="text-muted-foreground">Advance</span>
          )}
        </div>
      )
    }
  ]

  return (
    <div className="space-y-6">
      <PageHeader
        title="Payments"
        description="Track money received and paid"
        breadcrumbs={[
          { label: 'Dashboard', href: '/dashboard' },
          { label: 'Finance', href: '/dashboard/accounts' },
          { label: 'Payments' }
        ]}
        actions={
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm">
              <Download className="h-4 w-4 mr-2" />
              Export
            </Button>
            <Button variant="outline" asChild>
              <Link href="/dashboard/payments/receive">
                <ArrowDownLeft className="h-4 w-4 mr-2" />
                Receive Payment
              </Link>
            </Button>
            <Button asChild>
              <Link href="/dashboard/payments/make">
                <ArrowUpRight className="h-4 w-4 mr-2" />
                Make Payment
              </Link>
            </Button>
          </div>
        }
      />

      {/* Loading State */}
      {isLoading && (
        <Card className="p-8 flex items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <span className="ml-2">Loading payments...</span>
        </Card>
      )}

      {/* Error State */}
      {paymentsError && (
        <Card className="p-4 border-red-200 bg-red-50">
          <div className="flex items-center gap-2 text-red-600">
            <AlertCircle className="h-5 w-5" />
            <span>{paymentsError}</span>
          </div>
        </Card>
      )}

      {/* Stats */}
      <StatsGrid stats={stats} columns={4} />

      {/* Tabs for Payment Type */}
      <Tabs defaultValue="all" onValueChange={setTypeFilter}>
        <TabsList>
          <TabsTrigger value="all">All Payments</TabsTrigger>
          <TabsTrigger value="received" className="text-green-600">
            <ArrowDownLeft className="h-4 w-4 mr-1" />
            Received
          </TabsTrigger>
          <TabsTrigger value="made" className="text-red-600">
            <ArrowUpRight className="h-4 w-4 mr-1" />
            Made
          </TabsTrigger>
        </TabsList>

        <TabsContent value="all" className="space-y-4">
          {/* Filters */}
          <Card>
            <CardContent className="pt-6">
              <div className="flex flex-col sm:flex-row gap-4">
                <div className="flex-1 max-w-md">
                  <SearchInput
                    value={searchQuery}
                    onChange={setSearchQuery}
                    placeholder="Search by payment #, party, or reference..."
                  />
                </div>
                <div className="flex gap-2">
                  <Button
                    variant={statusFilter === 'all' ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => setStatusFilter('all')}
                  >
                    All
                  </Button>
                  <Button
                    variant={statusFilter === 'completed' ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => setStatusFilter('completed')}
                  >
                    Completed
                  </Button>
                  <Button
                    variant={statusFilter === 'pending' ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => setStatusFilter('pending')}
                  >
                    Pending
                  </Button>
                  <Button
                    variant={statusFilter === 'reconciled' ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => setStatusFilter('reconciled')}
                  >
                    Reconciled
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Payments Table */}
          <DataTable
            data={filteredPayments}
            columns={columns}
            keyExtractor={(row) => row.id}
            emptyMessage="No payments found"
          />
        </TabsContent>

        <TabsContent value="received" className="space-y-4">
          <DataTable
            data={filteredPayments.filter(p => p.type === 'received')}
            columns={columns}
            keyExtractor={(row) => row.id}
            emptyMessage="No payments received"
          />
        </TabsContent>

        <TabsContent value="made" className="space-y-4">
          <DataTable
            data={filteredPayments.filter(p => p.type === 'made')}
            columns={columns}
            keyExtractor={(row) => row.id}
            emptyMessage="No payments made"
          />
        </TabsContent>
      </Tabs>

      {/* Payment Summary */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm flex items-center gap-2">
              <ArrowDownLeft className="h-4 w-4 text-green-600" />
              Receipts Summary
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Bank Transfer</span>
                <span className="font-medium text-green-600">{formatCurrency(88500)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Cheque</span>
                <span className="font-medium text-green-600">{formatCurrency(100000)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">UPI</span>
                <span className="font-medium text-green-600">{formatCurrency(25000)}</span>
              </div>
              <div className="flex justify-between pt-2 border-t font-semibold">
                <span>Total Received</span>
                <span className="text-green-600">{formatCurrency(213500)}</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm flex items-center gap-2">
              <ArrowUpRight className="h-4 w-4 text-red-600" />
              Payments Summary
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Bank Transfer</span>
                <span className="font-medium text-red-600">{formatCurrency(212000)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Cheque</span>
                <span className="font-medium text-red-600">{formatCurrency(0)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Cash</span>
                <span className="font-medium text-red-600">{formatCurrency(0)}</span>
              </div>
              <div className="flex justify-between pt-2 border-t font-semibold">
                <span>Total Paid</span>
                <span className="text-red-600">{formatCurrency(212000)}</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
