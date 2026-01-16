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
  Upload,
  Eye,
  Edit,
  Receipt,
  TrendingDown,
  AlertCircle,
  CheckCircle,
  Clock,
  IndianRupee,
  FileText,
  Loader2,
  Trash2,
  AlertTriangle
} from 'lucide-react'
import type { Bill, BillStatus, TDSSection } from '@/types'

// Mock bill data
const mockBills: Bill[] = [
  {
    id: '1',
    bill_number: 'BILL-2026-0001',
    company_id: '1',
    vendor_id: '1',
    vendor_name: 'Office Supplies Co.',
    vendor_gstin: '29AABCO1234A1ZP',
    vendor_pan: 'AABCO1234A',
    bill_date: '2026-01-05',
    due_date: '2026-02-04',
    place_of_supply: 'Karnataka',
    supply_type: 'intra_state',
    items: [],
    subtotal: 45000,
    discount: 0,
    taxable_amount: 45000,
    cgst: 4050,
    sgst: 4050,
    igst: 0,
    cess: 0,
    total_tax: 8100,
    tds_section: '194C',
    tds_rate: 1,
    tds_amount: 450,
    round_off: 0,
    total: 53100,
    net_payable: 52650,
    amount_paid: 0,
    balance_due: 52650,
    status: 'approved',
    created_at: '2026-01-05T10:00:00Z',
    updated_at: '2026-01-05T14:00:00Z'
  },
  {
    id: '2',
    bill_number: 'BILL-2025-0089',
    company_id: '1',
    vendor_id: '2',
    vendor_name: 'Cloud Services Inc.',
    vendor_gstin: '07AABCC5678B1ZQ',
    vendor_pan: 'AABCC5678B',
    bill_date: '2025-12-28',
    due_date: '2026-01-27',
    place_of_supply: 'Delhi',
    supply_type: 'inter_state',
    items: [],
    subtotal: 150000,
    discount: 0,
    taxable_amount: 150000,
    cgst: 0,
    sgst: 0,
    igst: 27000,
    cess: 0,
    total_tax: 27000,
    tds_section: '194J',
    tds_rate: 10,
    tds_amount: 15000,
    round_off: 0,
    total: 177000,
    net_payable: 162000,
    amount_paid: 162000,
    balance_due: 0,
    status: 'paid',
    created_at: '2025-12-28T11:00:00Z',
    updated_at: '2026-01-03T09:00:00Z'
  },
  {
    id: '3',
    bill_number: 'BILL-2025-0085',
    company_id: '1',
    vendor_id: '3',
    vendor_name: 'Premium Office Space',
    vendor_gstin: '29AABCP9012C1ZR',
    vendor_pan: 'AABCP9012C',
    bill_date: '2025-12-01',
    due_date: '2025-12-10',
    place_of_supply: 'Karnataka',
    supply_type: 'intra_state',
    items: [],
    subtotal: 100000,
    discount: 0,
    taxable_amount: 100000,
    cgst: 9000,
    sgst: 9000,
    igst: 0,
    cess: 0,
    total_tax: 18000,
    tds_section: '194I',
    tds_rate: 10,
    tds_amount: 10000,
    round_off: 0,
    total: 118000,
    net_payable: 108000,
    amount_paid: 50000,
    balance_due: 58000,
    status: 'overdue',
    created_at: '2025-12-01T10:00:00Z',
    updated_at: '2025-12-20T00:00:00Z'
  },
  {
    id: '4',
    bill_number: 'BILL-2026-0002',
    company_id: '1',
    vendor_id: '4',
    vendor_name: 'Legal Advisors LLP',
    vendor_pan: 'AABFL3456D',
    bill_date: '2026-01-06',
    due_date: '2026-02-05',
    place_of_supply: 'Karnataka',
    supply_type: 'intra_state',
    items: [],
    subtotal: 75000,
    discount: 0,
    taxable_amount: 75000,
    cgst: 6750,
    sgst: 6750,
    igst: 0,
    cess: 0,
    total_tax: 13500,
    tds_section: '194J',
    tds_rate: 10,
    tds_amount: 7500,
    round_off: 0,
    total: 88500,
    net_payable: 81000,
    amount_paid: 0,
    balance_due: 81000,
    status: 'draft',
    created_at: '2026-01-06T15:00:00Z',
    updated_at: '2026-01-06T15:00:00Z'
  }
]

// Stats
const billStats = {
  totalPayables: 1890000,
  paidThisMonth: 562000,
  pendingAmount: 1328000,
  overdueAmount: 234500,
  overdueCount: 3,
  tdsDeducted: 156700,
  gstCredit: 245600
}

// TDS Section descriptions
const tdsDescriptions: Record<TDSSection, string> = {
  '194A': 'Interest',
  '194C': 'Contractor',
  '194H': 'Commission',
  '194I': 'Rent',
  '194J': 'Professional',
  '194Q': 'Purchase'
}

interface BillListResponse {
  bills: Bill[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

interface BillSummaryResponse {
  total_bills: number
  total_amount: number
  total_paid: number
  total_pending: number
  total_overdue: number
  overdue_count: number
  tds_deducted: number
  gst_input_credit: number
  by_status: {
    draft: number
    approved: number
    partially_paid: number
    paid: number
    overdue: number
    cancelled: number
  }
}

export default function BillsPage() {
  const router = useRouter()
  const [searchQuery, setSearchQuery] = React.useState('')
  const [statusFilter, setStatusFilter] = React.useState<string>('all')
  const [page, setPage] = React.useState(1)
  const [pageSize, setPageSize] = React.useState(20)

  // Delete state
  const [deleteDialogOpen, setDeleteDialogOpen] = React.useState(false)
  const [billToDelete, setBillToDelete] = React.useState<Bill | null>(null)
  const [isDeleting, setIsDeleting] = React.useState(false)
  const [localBills, setLocalBills] = React.useState<Bill[]>(mockBills)

  const { data: billsData, isLoading: billsLoading, error: billsError, get: getBills } = useApi<BillListResponse>()
  const { data: summaryData, isLoading: summaryLoading, get: getSummary } = useApi<BillSummaryResponse>()
  const deleteApi = useApi()

  // Delete handlers
  const handleDeleteClick = (bill: Bill, e: React.MouseEvent) => {
    e.stopPropagation()
    setBillToDelete(bill)
    setDeleteDialogOpen(true)
  }

  const handleDeleteConfirm = async () => {
    if (!billToDelete) return
    setIsDeleting(true)
    try {
      await deleteApi.delete(`/bills/${billToDelete.id}`)
      setLocalBills(prev => prev.filter(b => b.id !== billToDelete.id))
      setDeleteDialogOpen(false)
      setBillToDelete(null)
    } catch (error) {
      console.error('Failed to delete bill:', error)
    } finally {
      setIsDeleting(false)
    }
  }

  // Update local bills when API data changes
  React.useEffect(() => {
    if (billsData?.bills) {
      setLocalBills(billsData.bills)
    }
  }, [billsData])

  const debouncedSearch = useDebounce(searchQuery, 300)

  // Fetch bills and summary on mount and when filters change
  React.useEffect(() => {
    const params = new URLSearchParams()
    params.set('page', String(page))
    params.set('page_size', String(pageSize))
    if (statusFilter !== 'all') params.set('status', statusFilter)
    if (debouncedSearch) params.set('search', debouncedSearch)

    getBills(`/bills?${params.toString()}`)
    getSummary('/bills/summary')
  }, [page, pageSize, statusFilter, debouncedSearch, getBills, getSummary])

  const isLoading = billsLoading || summaryLoading

  const filteredBills = React.useMemo(() => {
    let result = [...localBills]

    if (debouncedSearch) {
      const query = debouncedSearch.toLowerCase()
      result = result.filter(bill =>
        bill.bill_number.toLowerCase().includes(query) ||
        bill.vendor_name.toLowerCase().includes(query) ||
        bill.vendor_gstin?.toLowerCase().includes(query) ||
        bill.vendor_pan?.toLowerCase().includes(query)
      )
    }

    if (statusFilter !== 'all') {
      result = result.filter(bill => bill.status === statusFilter)
    }

    return result
  }, [localBills, debouncedSearch, statusFilter])

  const stats = [
    {
      title: 'Total Payables',
      value: formatCurrency(summaryData?.total_pending || billStats.pendingAmount),
      icon: TrendingDown,
      description: `${summaryData?.overdue_count || billStats.overdueCount} overdue`,
      valueClassName: 'text-red-600'
    },
    {
      title: 'Paid This Month',
      value: formatCurrency(summaryData?.total_paid || billStats.paidThisMonth),
      icon: CheckCircle,
      description: 'Payments made',
      trend: { value: 8, label: 'vs last month' }
    },
    {
      title: 'TDS Deducted',
      value: formatCurrency(summaryData?.tds_deducted || billStats.tdsDeducted),
      icon: FileText,
      description: 'To be deposited'
    },
    {
      title: 'GST Input Credit',
      value: formatCurrency(summaryData?.gst_input_credit || billStats.gstCredit),
      icon: Receipt,
      description: 'Available for set-off'
    }
  ]

  const getStatusBadge = (status: BillStatus) => {
    const statusConfig = {
      draft: { label: 'Draft', className: 'bg-gray-100 text-gray-800' },
      approved: { label: 'Approved', className: 'bg-blue-100 text-blue-800' },
      partially_paid: { label: 'Partial', className: 'bg-yellow-100 text-yellow-800' },
      paid: { label: 'Paid', className: 'bg-green-100 text-green-800' },
      overdue: { label: 'Overdue', className: 'bg-red-100 text-red-800' },
      cancelled: { label: 'Cancelled', className: 'bg-gray-100 text-gray-800' }
    }

    const config = statusConfig[status] || statusConfig.draft
    return <Badge className={config.className}>{config.label}</Badge>
  }

  const getTDSBadge = (section?: TDSSection, amount?: number) => {
    if (!section || !amount) return null

    return (
      <div className="text-xs">
        <Badge variant="outline" className="bg-orange-50 text-orange-700">
          {section} - {tdsDescriptions[section]}
        </Badge>
        <p className="text-muted-foreground mt-1">TDS: {formatCurrency(amount)}</p>
      </div>
    )
  }

  const columns: Column<Bill>[] = [
    {
      key: 'bill_number',
      header: 'Bill',
      sortable: true,
      accessor: (row) => (
        <div>
          <p className="font-medium font-mono">{row.bill_number}</p>
          <p className="text-sm text-muted-foreground">{formatDate(row.bill_date)}</p>
        </div>
      )
    },
    {
      key: 'vendor',
      header: 'Vendor',
      accessor: (row) => (
        <div>
          <p className="font-medium">{row.vendor_name}</p>
          <div className="text-xs text-muted-foreground font-mono">
            {row.vendor_gstin && <p>GSTIN: {row.vendor_gstin}</p>}
            {row.vendor_pan && <p>PAN: {row.vendor_pan}</p>}
          </div>
        </div>
      )
    },
    {
      key: 'gst',
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
      key: 'tds',
      header: 'TDS',
      accessor: (row) => getTDSBadge(row.tds_section, row.tds_amount)
    },
    {
      key: 'total',
      header: 'Amount',
      sortable: true,
      className: 'text-right',
      headerClassName: 'text-right',
      accessor: (row) => (
        <div className="text-right">
          <p className="text-xs text-muted-foreground">Total: {formatCurrency(row.total)}</p>
          <p className="font-semibold">Net: {formatCurrency(row.net_payable)}</p>
          {row.balance_due > 0 && row.balance_due < row.net_payable && (
            <p className="text-xs text-red-600">
              Due: {formatCurrency(row.balance_due)}
            </p>
          )}
        </div>
      )
    },
    {
      key: 'status',
      header: 'Status',
      accessor: (row) => getStatusBadge(row.status)
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
            <Link href={`/dashboard/bills/${row.id}`}>
              <Eye className="h-4 w-4" />
            </Link>
          </Button>
          {row.status === 'draft' && (
            <>
              <Button variant="ghost" size="icon" asChild>
                <Link href={`/dashboard/bills/${row.id}/edit`}>
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
        </div>
      )
    }
  ]

  return (
    <div className="space-y-6">
      <PageHeader
        title="Bills"
        description="Manage purchase bills with TDS compliance"
        breadcrumbs={[
          { label: 'Dashboard', href: '/dashboard' },
          { label: 'Finance', href: '/dashboard/accounts' },
          { label: 'Bills' }
        ]}
        actions={
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm">
              <Upload className="h-4 w-4 mr-2" />
              Import
            </Button>
            <Button variant="outline" size="sm">
              <Download className="h-4 w-4 mr-2" />
              Export
            </Button>
            <Button asChild>
              <Link href="/dashboard/bills/new">
                <Plus className="h-4 w-4 mr-2" />
                New Bill
              </Link>
            </Button>
          </div>
        }
      />

      {/* Loading State */}
      {isLoading && (
        <Card className="p-8 flex items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <span className="ml-2">Loading bills...</span>
        </Card>
      )}

      {/* Error State */}
      {billsError && (
        <Card className="p-4 border-red-200 bg-red-50">
          <div className="flex items-center gap-2 text-red-600">
            <AlertCircle className="h-5 w-5" />
            <span>{billsError}</span>
          </div>
        </Card>
      )}

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
                placeholder="Search by bill #, vendor, GSTIN, or PAN..."
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
                variant={statusFilter === 'approved' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setStatusFilter('approved')}
              >
                Approved
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

      {/* Bills Table */}
      <DataTable
        data={filteredBills}
        columns={columns}
        keyExtractor={(row) => row.id}
        onRowClick={(row) => router.push(`/dashboard/bills/${row.id}`)}
        emptyMessage="No bills found"
      />

      <Pagination
        page={billsData?.page || page}
        pageSize={billsData?.page_size || pageSize}
        total={billsData?.total || filteredBills.length}
        totalPages={billsData?.total_pages || Math.ceil(filteredBills.length / pageSize)}
        onPageChange={setPage}
        onPageSizeChange={setPageSize}
      />

      {/* TDS Summary */}
      <Card>
        <CardHeader>
          <CardTitle className="text-sm">TDS Summary - January 2026</CardTitle>
          <CardDescription>Section-wise TDS deducted</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-6 gap-4 text-sm">
            <div>
              <p className="text-muted-foreground">194C - Contractor</p>
              <p className="font-semibold">{formatCurrency(450)}</p>
            </div>
            <div>
              <p className="text-muted-foreground">194I - Rent</p>
              <p className="font-semibold">{formatCurrency(10000)}</p>
            </div>
            <div>
              <p className="text-muted-foreground">194J - Professional</p>
              <p className="font-semibold">{formatCurrency(22500)}</p>
            </div>
            <div>
              <p className="text-muted-foreground">194A - Interest</p>
              <p className="font-semibold">{formatCurrency(0)}</p>
            </div>
            <div>
              <p className="text-muted-foreground">194H - Commission</p>
              <p className="font-semibold">{formatCurrency(0)}</p>
            </div>
            <div>
              <p className="text-muted-foreground font-medium">Total TDS</p>
              <p className="font-bold text-primary">{formatCurrency(32950)}</p>
            </div>
          </div>
          <p className="text-xs text-muted-foreground mt-4">
            TDS to be deposited by 7th of next month (7th Feb 2026)
          </p>
        </CardContent>
      </Card>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-red-500" />
              Delete Bill
            </AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete bill{' '}
              <strong>{billToDelete?.bill_number}</strong> from{' '}
              <strong>{billToDelete?.vendor_name}</strong>?
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
