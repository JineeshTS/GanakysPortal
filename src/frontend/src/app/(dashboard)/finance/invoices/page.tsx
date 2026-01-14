'use client'

import * as React from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { PageHeader } from '@/components/layout/page-header'
import { DataTable, Column } from '@/components/layout/data-table'
import { Pagination } from '@/components/layout/pagination'
import { StatsGrid } from '@/components/layout/stat-card'
import { SearchInput } from '@/components/forms/search-input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import { formatCurrency, formatDate } from '@/lib/format'
import { useDebounce } from '@/hooks'
import {
  Plus,
  Download,
  Send,
  Eye,
  Edit,
  MoreVertical,
  Receipt,
  TrendingUp,
  AlertCircle,
  CheckCircle,
  Clock,
  FileText,
  IndianRupee,
  Copy,
  Mail,
  Printer,
  Trash2,
  Filter,
  Calendar,
  X
} from 'lucide-react'
import type { Invoice, InvoiceStatus } from '@/types'

// Mock invoice data with comprehensive India GST details
const mockInvoices: Invoice[] = [
  {
    id: '1',
    invoice_number: 'INV-2026-0001',
    company_id: '1',
    customer_id: '1',
    customer_name: 'ABC Technologies Pvt Ltd',
    customer_gstin: '29AABCU9603R1ZM',
    invoice_date: '2026-01-05',
    due_date: '2026-02-04',
    place_of_supply: 'Karnataka',
    supply_type: 'intra_state',
    items: [],
    subtotal: 100000,
    discount: 5000,
    taxable_amount: 95000,
    cgst: 8550,
    sgst: 8550,
    igst: 0,
    cess: 0,
    total_tax: 17100,
    round_off: -0.10,
    total: 112100,
    amount_paid: 0,
    balance_due: 112100,
    status: 'sent',
    irn: 'a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0',
    ack_number: '132400000012345',
    ack_date: '2026-01-05',
    created_at: '2026-01-05T10:00:00Z',
    updated_at: '2026-01-05T10:00:00Z'
  },
  {
    id: '2',
    invoice_number: 'INV-2025-0147',
    company_id: '1',
    customer_id: '2',
    customer_name: 'XYZ Solutions Ltd',
    customer_gstin: '27AABCX1234D1ZP',
    invoice_date: '2025-12-20',
    due_date: '2026-01-19',
    place_of_supply: 'Maharashtra',
    supply_type: 'inter_state',
    items: [],
    subtotal: 75000,
    discount: 0,
    taxable_amount: 75000,
    cgst: 0,
    sgst: 0,
    igst: 13500,
    cess: 0,
    total_tax: 13500,
    round_off: 0,
    total: 88500,
    amount_paid: 88500,
    balance_due: 0,
    status: 'paid',
    irn: 'z9y8x7w6v5u4t3s2r1q0p9o8n7m6l5k4j3i2h1g0',
    ack_number: '132400000012300',
    ack_date: '2025-12-20',
    created_at: '2025-12-20T14:00:00Z',
    updated_at: '2025-12-28T11:00:00Z'
  },
  {
    id: '3',
    invoice_number: 'INV-2025-0145',
    company_id: '1',
    customer_id: '3',
    customer_name: 'PQR Industries',
    customer_gstin: '29AABCP5678E1ZQ',
    invoice_date: '2025-12-15',
    due_date: '2025-12-30',
    place_of_supply: 'Karnataka',
    supply_type: 'intra_state',
    items: [],
    subtotal: 250000,
    discount: 12500,
    taxable_amount: 237500,
    cgst: 21375,
    sgst: 21375,
    igst: 0,
    cess: 0,
    total_tax: 42750,
    round_off: 0,
    total: 280250,
    amount_paid: 100000,
    balance_due: 180250,
    status: 'overdue',
    irn: 'f1e2d3c4b5a6z7y8x9w0v1u2t3s4r5q6p7o8n9m0',
    ack_number: '132400000012280',
    ack_date: '2025-12-15',
    created_at: '2025-12-15T09:00:00Z',
    updated_at: '2025-12-30T00:00:00Z'
  },
  {
    id: '4',
    invoice_number: 'INV-2026-0002',
    company_id: '1',
    customer_id: '4',
    customer_name: 'LMN Enterprises',
    invoice_date: '2026-01-06',
    due_date: '2026-02-05',
    place_of_supply: 'Karnataka',
    supply_type: 'intra_state',
    items: [],
    subtotal: 50000,
    discount: 0,
    taxable_amount: 50000,
    cgst: 4500,
    sgst: 4500,
    igst: 0,
    cess: 0,
    total_tax: 9000,
    round_off: 0,
    total: 59000,
    amount_paid: 0,
    balance_due: 59000,
    status: 'draft',
    created_at: '2026-01-06T11:00:00Z',
    updated_at: '2026-01-06T11:00:00Z'
  },
  {
    id: '5',
    invoice_number: 'INV-2025-0146',
    company_id: '1',
    customer_id: '5',
    customer_name: 'Global Tech Solutions',
    customer_gstin: '33AABCG9876F1ZR',
    invoice_date: '2025-12-18',
    due_date: '2026-01-17',
    place_of_supply: 'Tamil Nadu',
    supply_type: 'inter_state',
    items: [],
    subtotal: 180000,
    discount: 9000,
    taxable_amount: 171000,
    cgst: 0,
    sgst: 0,
    igst: 30780,
    cess: 0,
    total_tax: 30780,
    round_off: 0.20,
    total: 201780,
    amount_paid: 50000,
    balance_due: 151780,
    status: 'partially_paid',
    irn: 'm1n2o3p4q5r6s7t8u9v0w1x2y3z4a5b6c7d8e9f0',
    ack_number: '132400000012290',
    ack_date: '2025-12-18',
    created_at: '2025-12-18T15:00:00Z',
    updated_at: '2026-01-02T10:00:00Z'
  }
]

// Stats
const invoiceStats = {
  totalInvoices: 147,
  totalValue: 8567890,
  paidAmount: 6234560,
  pendingAmount: 2333330,
  overdueAmount: 456780,
  overdueCount: 4,
  thisMonthValue: 171100,
  gstCollected: 1542200
}

// Customers for filter
const customers = [
  { id: '1', name: 'ABC Technologies Pvt Ltd' },
  { id: '2', name: 'XYZ Solutions Ltd' },
  { id: '3', name: 'PQR Industries' },
  { id: '4', name: 'LMN Enterprises' },
  { id: '5', name: 'Global Tech Solutions' }
]

export default function InvoicesListPage() {
  const router = useRouter()
  const [invoices, setInvoices] = React.useState(mockInvoices)
  const [searchQuery, setSearchQuery] = React.useState('')
  const [statusFilter, setStatusFilter] = React.useState<string>('all')
  const [customerFilter, setCustomerFilter] = React.useState<string>('all')
  const [dateFrom, setDateFrom] = React.useState('')
  const [dateTo, setDateTo] = React.useState('')
  const [showFilters, setShowFilters] = React.useState(false)
  const [selectedInvoices, setSelectedInvoices] = React.useState<string[]>([])
  const [page, setPage] = React.useState(1)
  const [pageSize, setPageSize] = React.useState(20)

  const debouncedSearch = useDebounce(searchQuery, 300)

  const filteredInvoices = React.useMemo(() => {
    let result = [...invoices]

    if (debouncedSearch) {
      const query = debouncedSearch.toLowerCase()
      result = result.filter(inv =>
        inv.invoice_number.toLowerCase().includes(query) ||
        inv.customer_name.toLowerCase().includes(query) ||
        inv.customer_gstin?.toLowerCase().includes(query)
      )
    }

    if (statusFilter !== 'all') {
      result = result.filter(inv => inv.status === statusFilter)
    }

    if (customerFilter !== 'all') {
      result = result.filter(inv => inv.customer_id === customerFilter)
    }

    if (dateFrom) {
      result = result.filter(inv => inv.invoice_date >= dateFrom)
    }

    if (dateTo) {
      result = result.filter(inv => inv.invoice_date <= dateTo)
    }

    return result
  }, [invoices, debouncedSearch, statusFilter, customerFilter, dateFrom, dateTo])

  const stats = [
    {
      title: 'Total Receivables',
      value: formatCurrency(invoiceStats.pendingAmount),
      icon: IndianRupee,
      description: `${invoiceStats.overdueCount} overdue`,
      valueClassName: 'text-blue-600'
    },
    {
      title: 'Collected This Month',
      value: formatCurrency(invoiceStats.paidAmount),
      icon: CheckCircle,
      description: 'Payments received',
      trend: { value: 12, label: 'vs last month' }
    },
    {
      title: 'Overdue Amount',
      value: formatCurrency(invoiceStats.overdueAmount),
      icon: AlertCircle,
      description: `${invoiceStats.overdueCount} invoices`,
      valueClassName: 'text-red-600'
    },
    {
      title: 'GST Collected',
      value: formatCurrency(invoiceStats.gstCollected),
      icon: Receipt,
      description: 'CGST + SGST + IGST'
    }
  ]

  const getStatusBadge = (status: InvoiceStatus) => {
    const statusConfig = {
      draft: { label: 'Draft', className: 'bg-gray-100 text-gray-800' },
      sent: { label: 'Sent', className: 'bg-blue-100 text-blue-800' },
      viewed: { label: 'Viewed', className: 'bg-purple-100 text-purple-800' },
      partially_paid: { label: 'Partial', className: 'bg-yellow-100 text-yellow-800' },
      paid: { label: 'Paid', className: 'bg-green-100 text-green-800' },
      overdue: { label: 'Overdue', className: 'bg-red-100 text-red-800' },
      cancelled: { label: 'Cancelled', className: 'bg-gray-100 text-gray-800' },
      bad_debt: { label: 'Bad Debt', className: 'bg-red-100 text-red-800' }
    }

    const config = statusConfig[status] || statusConfig.draft
    return <Badge className={config.className}>{config.label}</Badge>
  }

  const getSupplyTypeBadge = (type: string) => {
    const config = {
      intra_state: { label: 'Intra-State', className: 'bg-green-50 text-green-700' },
      inter_state: { label: 'Inter-State', className: 'bg-blue-50 text-blue-700' },
      export: { label: 'Export', className: 'bg-purple-50 text-purple-700' },
      sez: { label: 'SEZ', className: 'bg-orange-50 text-orange-700' }
    }

    const c = config[type as keyof typeof config] || config.intra_state
    return <Badge variant="outline" className={c.className}>{c.label}</Badge>
  }

  const handleSelectAll = (checked: boolean) => {
    if (checked) {
      setSelectedInvoices(filteredInvoices.map(inv => inv.id))
    } else {
      setSelectedInvoices([])
    }
  }

  const handleSelectInvoice = (id: string) => {
    setSelectedInvoices(prev =>
      prev.includes(id) ? prev.filter(i => i !== id) : [...prev, id]
    )
  }

  const clearFilters = () => {
    setStatusFilter('all')
    setCustomerFilter('all')
    setDateFrom('')
    setDateTo('')
    setSearchQuery('')
  }

  const columns: Column<Invoice>[] = [
    {
      key: 'invoice_number',
      header: 'Invoice',
      sortable: true,
      accessor: (row) => (
        <div>
          <p className="font-medium font-mono">{row.invoice_number}</p>
          <p className="text-sm text-muted-foreground">{formatDate(row.invoice_date)}</p>
        </div>
      )
    },
    {
      key: 'customer',
      header: 'Customer',
      accessor: (row) => (
        <div>
          <p className="font-medium">{row.customer_name}</p>
          {row.customer_gstin && (
            <p className="text-xs text-muted-foreground font-mono">{row.customer_gstin}</p>
          )}
        </div>
      )
    },
    {
      key: 'supply_type',
      header: 'Supply',
      accessor: (row) => (
        <div className="space-y-1">
          {getSupplyTypeBadge(row.supply_type)}
          <p className="text-xs text-muted-foreground">{row.place_of_supply}</p>
        </div>
      )
    },
    {
      key: 'tax',
      header: 'GST',
      className: 'text-right',
      headerClassName: 'text-right',
      accessor: (row) => (
        <div className="text-right">
          {row.cgst > 0 && (
            <p className="text-xs">CGST: {formatCurrency(row.cgst)}</p>
          )}
          {row.sgst > 0 && (
            <p className="text-xs">SGST: {formatCurrency(row.sgst)}</p>
          )}
          {row.igst > 0 && (
            <p className="text-xs">IGST: {formatCurrency(row.igst)}</p>
          )}
          <p className="font-medium text-sm">{formatCurrency(row.total_tax)}</p>
        </div>
      )
    },
    {
      key: 'total',
      header: 'Amount',
      sortable: true,
      className: 'text-right',
      headerClassName: 'text-right',
      accessor: (row) => (
        <div className="text-right">
          <p className="font-semibold">{formatCurrency(row.total)}</p>
          {row.balance_due > 0 && row.balance_due < row.total && (
            <p className="text-xs text-muted-foreground">
              Due: {formatCurrency(row.balance_due)}
            </p>
          )}
        </div>
      )
    },
    {
      key: 'status',
      header: 'Status',
      accessor: (row) => (
        <div className="space-y-1">
          {getStatusBadge(row.status)}
          {row.irn && (
            <p className="text-xs text-green-600 flex items-center gap-1">
              <CheckCircle className="h-3 w-3" /> E-Invoice
            </p>
          )}
        </div>
      )
    },
    {
      key: 'due_date',
      header: 'Due Date',
      sortable: true,
      accessor: (row) => {
        const isOverdue = new Date(row.due_date) < new Date() && row.balance_due > 0
        return (
          <span className={isOverdue ? 'text-red-600 font-medium' : ''}>
            {formatDate(row.due_date)}
          </span>
        )
      }
    },
    {
      key: 'actions',
      header: '',
      accessor: (row) => (
        <div className="flex items-center gap-1">
          <Button variant="ghost" size="icon" asChild>
            <Link href={`/finance/invoices/${row.id}`}>
              <Eye className="h-4 w-4" />
            </Link>
          </Button>
          {row.status === 'draft' && (
            <Button variant="ghost" size="icon" asChild>
              <Link href={`/finance/invoices/${row.id}/edit`}>
                <Edit className="h-4 w-4" />
              </Link>
            </Button>
          )}
          <Button variant="ghost" size="icon" title="Download PDF">
            <Download className="h-4 w-4" />
          </Button>
          <Button variant="ghost" size="icon" title="Send Email">
            <Mail className="h-4 w-4" />
          </Button>
          <Button variant="ghost" size="icon" title="Duplicate">
            <Copy className="h-4 w-4" />
          </Button>
        </div>
      )
    }
  ]

  return (
    <div className="space-y-6">
      <PageHeader
        title="Invoices"
        description="Manage sales invoices with GST compliance"
        breadcrumbs={[
          { label: 'Dashboard', href: '/dashboard' },
          { label: 'Finance', href: '/finance' },
          { label: 'Invoices' }
        ]}
        actions={
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm">
              <Download className="h-4 w-4 mr-2" />
              Export
            </Button>
            <Button asChild>
              <Link href="/finance/invoices/create">
                <Plus className="h-4 w-4 mr-2" />
                New Invoice
              </Link>
            </Button>
          </div>
        }
      />

      {/* Stats */}
      <StatsGrid stats={stats} columns={4} />

      {/* Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col gap-4">
            {/* Search and Quick Filters */}
            <div className="flex flex-col sm:flex-row gap-4">
              <div className="flex-1 max-w-md">
                <SearchInput
                  value={searchQuery}
                  onChange={setSearchQuery}
                  placeholder="Search by invoice #, customer, or GSTIN..."
                />
              </div>
              <div className="flex gap-2 flex-wrap">
                <Button
                  variant={statusFilter === 'all' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setStatusFilter('all')}
                >
                  All
                </Button>
                <Button
                  variant={statusFilter === 'draft' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setStatusFilter('draft')}
                >
                  Draft
                </Button>
                <Button
                  variant={statusFilter === 'sent' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setStatusFilter('sent')}
                >
                  Sent
                </Button>
                <Button
                  variant={statusFilter === 'overdue' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setStatusFilter('overdue')}
                  className={statusFilter === 'overdue' ? '' : 'text-red-600'}
                >
                  <AlertCircle className="h-3 w-3 mr-1" />
                  Overdue
                </Button>
                <Button
                  variant={statusFilter === 'paid' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setStatusFilter('paid')}
                >
                  <CheckCircle className="h-3 w-3 mr-1" />
                  Paid
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setShowFilters(!showFilters)}
                >
                  <Filter className="h-4 w-4 mr-1" />
                  More Filters
                </Button>
              </div>
            </div>

            {/* Extended Filters */}
            {showFilters && (
              <div className="grid grid-cols-1 sm:grid-cols-4 gap-4 p-4 bg-muted/50 rounded-lg">
                <div className="space-y-2">
                  <Label>Customer</Label>
                  <Select value={customerFilter} onValueChange={setCustomerFilter}>
                    <SelectTrigger>
                      <SelectValue placeholder="All Customers" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Customers</SelectItem>
                      {customers.map(customer => (
                        <SelectItem key={customer.id} value={customer.id}>
                          {customer.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label>From Date</Label>
                  <Input
                    type="date"
                    value={dateFrom}
                    onChange={(e) => setDateFrom(e.target.value)}
                  />
                </div>
                <div className="space-y-2">
                  <Label>To Date</Label>
                  <Input
                    type="date"
                    value={dateTo}
                    onChange={(e) => setDateTo(e.target.value)}
                  />
                </div>
                <div className="space-y-2">
                  <Label>&nbsp;</Label>
                  <Button variant="outline" className="w-full" onClick={clearFilters}>
                    <X className="h-4 w-4 mr-2" />
                    Clear Filters
                  </Button>
                </div>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Bulk Actions */}
      {selectedInvoices.length > 0 && (
        <Card className="bg-primary/5 border-primary">
          <CardContent className="py-3">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">
                {selectedInvoices.length} invoice(s) selected
              </span>
              <div className="flex items-center gap-2">
                <Button variant="outline" size="sm">
                  <Download className="h-4 w-4 mr-2" />
                  Export Selected
                </Button>
                <Button variant="outline" size="sm">
                  <Mail className="h-4 w-4 mr-2" />
                  Send Reminders
                </Button>
                <Button variant="outline" size="sm">
                  <Printer className="h-4 w-4 mr-2" />
                  Print
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Invoice Table */}
      <DataTable
        data={filteredInvoices}
        columns={columns}
        keyExtractor={(row) => row.id}
        onRowClick={(row) => router.push(`/finance/invoices/${row.id}`)}
        emptyMessage="No invoices found"
      />

      <Pagination
        page={page}
        pageSize={pageSize}
        total={filteredInvoices.length}
        totalPages={Math.ceil(filteredInvoices.length / pageSize)}
        onPageChange={setPage}
        onPageSizeChange={setPageSize}
      />

      {/* GST Summary Card */}
      <Card>
        <CardHeader>
          <CardTitle className="text-sm">GST Summary - January 2026</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4 text-sm">
            <div>
              <p className="text-muted-foreground">Taxable Value</p>
              <p className="font-semibold">{formatCurrency(957500)}</p>
            </div>
            <div>
              <p className="text-muted-foreground">CGST @9%</p>
              <p className="font-semibold">{formatCurrency(34425)}</p>
            </div>
            <div>
              <p className="text-muted-foreground">SGST @9%</p>
              <p className="font-semibold">{formatCurrency(34425)}</p>
            </div>
            <div>
              <p className="text-muted-foreground">IGST @18%</p>
              <p className="font-semibold">{formatCurrency(13500)}</p>
            </div>
            <div>
              <p className="text-muted-foreground">Total GST</p>
              <p className="font-semibold text-primary">{formatCurrency(82350)}</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
