'use client'

import * as React from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { PageHeader } from '@/components/layout/page-header'
import { DataTable, Column } from '@/components/layout/data-table'
import { Pagination } from '@/components/layout/pagination'
import { StatsGrid } from '@/components/layout/stat-card'
import { SearchInput } from '@/components/forms/search-input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { formatCurrency, formatDate } from '@/lib/format'
import { useDebounce, useApi } from '@/hooks'
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
  Plus,
  Download,
  Eye,
  Edit,
  Receipt,
  AlertCircle,
  CheckCircle,
  IndianRupee,
  Copy,
  Loader2,
  Trash2,
  AlertTriangle
} from 'lucide-react'
import type { Invoice, InvoiceStatus } from '@/types'

interface InvoiceListResponse {
  data: Invoice[]
  meta: {
    page: number
    page_size: number
    total: number
    total_pages: number
  }
}

interface InvoiceSummary {
  total_invoices: number
  total_amount: number
  total_paid: number
  total_outstanding: number
  overdue_count: number
  overdue_amount: number
}

// Fallback mock data if API fails
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

export default function InvoicesPage() {
  const router = useRouter()
  const [searchQuery, setSearchQuery] = React.useState('')
  const [statusFilter, setStatusFilter] = React.useState<string>('all')
  const [page, setPage] = React.useState(1)
  const [pageSize, setPageSize] = React.useState(20)

  // Delete state
  const [deleteDialogOpen, setDeleteDialogOpen] = React.useState(false)
  const [invoiceToDelete, setInvoiceToDelete] = React.useState<Invoice | null>(null)
  const [isDeleting, setIsDeleting] = React.useState(false)
  const [localInvoices, setLocalInvoices] = React.useState<Invoice[]>([])

  const { data: invoiceData, isLoading, error, get } = useApi<InvoiceListResponse>()
  const { data: summary, get: getSummary } = useApi<InvoiceSummary>()
  const deleteApi = useApi()

  // Delete handlers
  const handleDeleteClick = (invoice: Invoice, e: React.MouseEvent) => {
    e.stopPropagation()
    setInvoiceToDelete(invoice)
    setDeleteDialogOpen(true)
  }

  const handleDeleteConfirm = async () => {
    if (!invoiceToDelete) return
    setIsDeleting(true)
    try {
      await deleteApi.delete(`/invoices/${invoiceToDelete.id}`)
      setLocalInvoices(prev => prev.filter(inv => inv.id !== invoiceToDelete.id))
      setDeleteDialogOpen(false)
      setInvoiceToDelete(null)
    } catch (error) {
      console.error('Failed to delete invoice:', error)
    } finally {
      setIsDeleting(false)
    }
  }

  // Update local invoices when API data changes
  React.useEffect(() => {
    if (invoiceData?.data) {
      setLocalInvoices(invoiceData.data)
    } else {
      setLocalInvoices(mockInvoices)
    }
  }, [invoiceData])

  const debouncedSearch = useDebounce(searchQuery, 300)

  // Fetch invoices on mount and when filters change
  React.useEffect(() => {
    const params = new URLSearchParams({
      page: String(page),
      page_size: String(pageSize)
    })
    if (statusFilter !== 'all') {
      params.set('status', statusFilter)
    }
    if (debouncedSearch) {
      params.set('search', debouncedSearch)
    }
    get(`/invoices?${params.toString()}`)
  }, [page, pageSize, statusFilter, debouncedSearch, get])

  // Fetch summary on mount
  React.useEffect(() => {
    getSummary('/invoices/summary')
  }, [getSummary])

  // Use local invoices (synced with API or mock)
  const totalPages = invoiceData?.meta?.total_pages || 1
  const totalInvoices = invoiceData?.meta?.total || localInvoices.length

  const filteredInvoices = React.useMemo(() => {
    let result = [...localInvoices]

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

    return result
  }, [localInvoices, debouncedSearch, statusFilter])

  const stats = [
    {
      title: 'Total Receivables',
      value: formatCurrency(summary?.total_outstanding || invoiceStats.pendingAmount),
      icon: IndianRupee,
      description: `${summary?.overdue_count || invoiceStats.overdueCount} overdue`,
      valueClassName: 'text-blue-600'
    },
    {
      title: 'Collected This Month',
      value: formatCurrency(summary?.total_paid || invoiceStats.paidAmount),
      icon: CheckCircle,
      description: 'Payments received',
      trend: { value: 12, label: 'vs last month' }
    },
    {
      title: 'Overdue Amount',
      value: formatCurrency(summary?.overdue_amount || invoiceStats.overdueAmount),
      icon: AlertCircle,
      description: `${summary?.overdue_count || invoiceStats.overdueCount} invoices`,
      valueClassName: 'text-red-600'
    },
    {
      title: 'Total Invoices',
      value: String(summary?.total_invoices || invoiceStats.totalInvoices),
      icon: Receipt,
      description: formatCurrency(summary?.total_amount || invoiceStats.totalValue)
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
      header: 'Total',
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
            <Link href={`/dashboard/invoices/${row.id}`}>
              <Eye className="h-4 w-4" />
            </Link>
          </Button>
          {row.status === 'draft' && (
            <>
              <Button variant="ghost" size="icon" asChild>
                <Link href={`/dashboard/invoices/${row.id}/edit`}>
                  <Edit className="h-4 w-4" />
                </Link>
              </Button>
              <Button
                variant="ghost"
                size="icon"
                className="text-red-600 hover:text-red-700 hover:bg-red-50"
                onClick={(e) => handleDeleteClick(row, e)}
              >
                <Trash2 className="h-4 w-4" />
              </Button>
            </>
          )}
          <Button variant="ghost" size="icon">
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
          { label: 'Finance', href: '/dashboard/accounts' },
          { label: 'Invoices' }
        ]}
        actions={
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm">
              <Download className="h-4 w-4 mr-2" />
              Export
            </Button>
            <Button asChild>
              <Link href="/dashboard/invoices/new">
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
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Loading State */}
      {isLoading && (
        <Card className="p-8 flex items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <span className="ml-2">Loading invoices...</span>
        </Card>
      )}

      {/* Error State */}
      {error && (
        <Card className="p-4 bg-red-50 border-red-200">
          <div className="flex items-center gap-2 text-red-600">
            <AlertCircle className="h-5 w-5" />
            <span>Error loading invoices: {error}</span>
          </div>
        </Card>
      )}

      {/* Invoice Table */}
      {!isLoading && (
        <DataTable
          data={filteredInvoices}
          columns={columns}
          keyExtractor={(row) => row.id}
          onRowClick={(row) => router.push(`/dashboard/invoices/${row.id}`)}
          emptyMessage="No invoices found"
        />
      )}

      <Pagination
        page={page}
        pageSize={pageSize}
        total={totalInvoices}
        totalPages={totalPages}
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

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-red-500" />
              Delete Invoice
            </AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete invoice{' '}
              <strong>{invoiceToDelete?.invoice_number}</strong> for{' '}
              <strong>{invoiceToDelete?.customer_name}</strong>?
              This action cannot be undone.
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
