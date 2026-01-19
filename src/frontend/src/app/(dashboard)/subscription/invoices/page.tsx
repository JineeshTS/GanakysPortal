'use client'

import { useState, useEffect, useCallback } from 'react'
import { PageHeader } from '@/components/layout/page-header'
import { useAuth } from "@/hooks/use-auth"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
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
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import Link from 'next/link'
import {
  Receipt,
  Search,
  Filter,
  Download,
  Eye,
  Send,
  IndianRupee,
  Calendar,
  Building2,
  CheckCircle2,
  Clock,
  AlertTriangle,
  Loader2,
  RefreshCw,
  ArrowLeft,
  ChevronLeft,
  ChevronRight,
  CreditCard,
} from 'lucide-react'

// Types
interface Invoice {
  id: string
  subscription_id: string
  company_id: string
  invoice_number: string
  invoice_date: string
  due_date: string
  period_start: string
  period_end: string
  status: string
  line_items: Array<{
    description: string
    quantity: number
    unit_price: number
    amount: number
  }>
  subtotal: number
  discount_amount: number
  taxable_amount: number
  cgst_amount: number
  sgst_amount: number
  igst_amount: number
  total_tax: number
  total_amount: number
  amount_paid: number
  amount_due: number
  currency: string
  customer_name: string
  customer_email: string | null
  customer_gstin: string | null
  payment_link: string | null
  pdf_url: string | null
}

// Status config
const statusConfig: Record<string, { color: string; icon: React.ReactNode; label: string }> = {
  draft: { color: 'bg-slate-100 text-slate-700', icon: <Clock className="h-3.5 w-3.5" />, label: 'Draft' },
  pending: { color: 'bg-yellow-100 text-yellow-700', icon: <Clock className="h-3.5 w-3.5" />, label: 'Pending' },
  paid: { color: 'bg-green-100 text-green-700', icon: <CheckCircle2 className="h-3.5 w-3.5" />, label: 'Paid' },
  partially_paid: { color: 'bg-blue-100 text-blue-700', icon: <IndianRupee className="h-3.5 w-3.5" />, label: 'Partial' },
  overdue: { color: 'bg-red-100 text-red-700', icon: <AlertTriangle className="h-3.5 w-3.5" />, label: 'Overdue' },
  cancelled: { color: 'bg-gray-100 text-gray-700', icon: <Clock className="h-3.5 w-3.5" />, label: 'Cancelled' },
  refunded: { color: 'bg-purple-100 text-purple-700', icon: <Receipt className="h-3.5 w-3.5" />, label: 'Refunded' },
}

// Format currency
function formatCurrency(amount: number, currency: string = 'INR'): string {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency,
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(amount)
}

// Invoice Detail Dialog
function InvoiceDetailDialog({
  invoice,
  isOpen,
  onClose,
}: {
  invoice: Invoice | null
  isOpen: boolean
  onClose: () => void
}) {
  if (!invoice) return null

  const status = statusConfig[invoice.status] || statusConfig.pending

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <div className="flex items-center justify-between">
            <DialogTitle>Invoice {invoice.invoice_number}</DialogTitle>
            <Badge className={status.color}>
              {status.icon}
              <span className="ml-1">{status.label}</span>
            </Badge>
          </div>
          <DialogDescription>
            Issued on {new Date(invoice.invoice_date).toLocaleDateString()}
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6 py-4">
          {/* Customer Info */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-muted-foreground">Bill To</p>
              <p className="font-medium">{invoice.customer_name}</p>
              {invoice.customer_email && (
                <p className="text-sm text-muted-foreground">{invoice.customer_email}</p>
              )}
              {invoice.customer_gstin && (
                <p className="text-sm">GSTIN: {invoice.customer_gstin}</p>
              )}
            </div>
            <div className="text-right">
              <p className="text-sm text-muted-foreground">Billing Period</p>
              <p className="font-medium">
                {new Date(invoice.period_start).toLocaleDateString()} -{' '}
                {new Date(invoice.period_end).toLocaleDateString()}
              </p>
              <p className="text-sm text-muted-foreground mt-2">Due Date</p>
              <p className="font-medium">{new Date(invoice.due_date).toLocaleDateString()}</p>
            </div>
          </div>

          {/* Line Items */}
          <div className="border rounded-lg">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Description</TableHead>
                  <TableHead className="text-right">Qty</TableHead>
                  <TableHead className="text-right">Rate</TableHead>
                  <TableHead className="text-right">Amount</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {invoice.line_items.map((item, index) => (
                  <TableRow key={index}>
                    <TableCell>{item.description}</TableCell>
                    <TableCell className="text-right">{item.quantity}</TableCell>
                    <TableCell className="text-right">{formatCurrency(item.unit_price)}</TableCell>
                    <TableCell className="text-right">{formatCurrency(item.amount)}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>

          {/* Totals */}
          <div className="space-y-2 pt-4 border-t">
            <div className="flex justify-between text-sm">
              <span>Subtotal</span>
              <span>{formatCurrency(invoice.subtotal)}</span>
            </div>
            {invoice.discount_amount > 0 && (
              <div className="flex justify-between text-sm text-green-600">
                <span>Discount</span>
                <span>-{formatCurrency(invoice.discount_amount)}</span>
              </div>
            )}
            <div className="flex justify-between text-sm">
              <span>Taxable Amount</span>
              <span>{formatCurrency(invoice.taxable_amount)}</span>
            </div>
            {invoice.cgst_amount > 0 && (
              <div className="flex justify-between text-sm">
                <span>CGST (9%)</span>
                <span>{formatCurrency(invoice.cgst_amount)}</span>
              </div>
            )}
            {invoice.sgst_amount > 0 && (
              <div className="flex justify-between text-sm">
                <span>SGST (9%)</span>
                <span>{formatCurrency(invoice.sgst_amount)}</span>
              </div>
            )}
            {invoice.igst_amount > 0 && (
              <div className="flex justify-between text-sm">
                <span>IGST (18%)</span>
                <span>{formatCurrency(invoice.igst_amount)}</span>
              </div>
            )}
            <div className="flex justify-between font-bold text-lg pt-2 border-t">
              <span>Total</span>
              <span>{formatCurrency(invoice.total_amount)}</span>
            </div>
            {invoice.amount_paid > 0 && (
              <>
                <div className="flex justify-between text-sm text-green-600">
                  <span>Amount Paid</span>
                  <span>{formatCurrency(invoice.amount_paid)}</span>
                </div>
                <div className="flex justify-between font-medium">
                  <span>Amount Due</span>
                  <span>{formatCurrency(invoice.amount_due)}</span>
                </div>
              </>
            )}
          </div>

          {/* Actions */}
          <div className="flex gap-2 pt-4 border-t">
            {invoice.pdf_url && (
              <Button variant="outline" asChild>
                <a href={invoice.pdf_url} target="_blank" rel="noopener noreferrer">
                  <Download className="h-4 w-4 mr-2" />
                  Download PDF
                </a>
              </Button>
            )}
            {invoice.payment_link && invoice.amount_due > 0 && (
              <Button asChild>
                <a href={invoice.payment_link} target="_blank" rel="noopener noreferrer">
                  <CreditCard className="h-4 w-4 mr-2" />
                  Pay Now
                </a>
              </Button>
            )}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  )
}

export default function InvoicesPage() {
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [invoices, setInvoices] = useState<Invoice[]>([])
  const [selectedInvoice, setSelectedInvoice] = useState<Invoice | null>(null)
  const [showDetail, setShowDetail] = useState(false)
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [page, setPage] = useState(0)
  const pageSize = 10

  const fetchInvoices = async () => {
    setIsLoading(true)
    setError(null)
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || '/api/v1'
      const params = new URLSearchParams({
        skip: String(page * pageSize),
        limit: String(pageSize),
      })
      if (statusFilter !== 'all') {
        params.append('status', statusFilter)
      }

      const res = await fetchWithAuth(`${apiUrl}/subscriptions/invoices?${params}`)
      if (res.ok) {
        const data = await res.json()
        setInvoices(data)
      }
    } catch (err) {
      console.error('Failed to fetch invoices:', err)
      setError('Failed to load invoices. Using demo data.')
      // Mock data
      setInvoices([
        {
          id: '1',
          subscription_id: 'sub-1',
          company_id: 'comp-1',
          invoice_number: 'INV-2026-000001',
          invoice_date: '2026-01-01',
          due_date: '2026-01-15',
          period_start: '2026-01-01',
          period_end: '2026-01-31',
          status: 'paid',
          line_items: [
            { description: 'Professional Plan - Base', quantity: 1, unit_price: 2999, amount: 2999 },
            { description: 'Employee licenses (50 employees)', quantity: 50, unit_price: 79, amount: 3950 },
          ],
          subtotal: 6949,
          discount_amount: 0,
          taxable_amount: 6949,
          cgst_amount: 625.41,
          sgst_amount: 625.41,
          igst_amount: 0,
          total_tax: 1250.82,
          total_amount: 8199.82,
          amount_paid: 8199.82,
          amount_due: 0,
          currency: 'INR',
          customer_name: 'Acme Corporation',
          customer_email: 'billing@acme.com',
          customer_gstin: '27AABCU9603R1ZM',
          payment_link: null,
          pdf_url: '/invoices/INV-2026-000001.pdf',
        },
        {
          id: '2',
          subscription_id: 'sub-2',
          company_id: 'comp-2',
          invoice_number: 'INV-2026-000002',
          invoice_date: '2026-01-05',
          due_date: '2026-01-20',
          period_start: '2026-01-01',
          period_end: '2026-01-31',
          status: 'pending',
          line_items: [
            { description: 'Starter Plan - Base', quantity: 1, unit_price: 999, amount: 999 },
            { description: 'Employee licenses (15 employees)', quantity: 15, unit_price: 49, amount: 735 },
          ],
          subtotal: 1734,
          discount_amount: 173.4,
          taxable_amount: 1560.6,
          cgst_amount: 140.45,
          sgst_amount: 140.45,
          igst_amount: 0,
          total_tax: 280.91,
          total_amount: 1841.51,
          amount_paid: 0,
          amount_due: 1841.51,
          currency: 'INR',
          customer_name: 'TechStart Inc',
          customer_email: 'accounts@techstart.io',
          customer_gstin: null,
          payment_link: 'https://rzp.io/i/abc123',
          pdf_url: '/invoices/INV-2026-000002.pdf',
        },
        {
          id: '3',
          subscription_id: 'sub-3',
          company_id: 'comp-3',
          invoice_number: 'INV-2025-000045',
          invoice_date: '2025-12-01',
          due_date: '2025-12-15',
          period_start: '2025-12-01',
          period_end: '2025-12-31',
          status: 'overdue',
          line_items: [
            { description: 'Professional Plan - Base', quantity: 1, unit_price: 2999, amount: 2999 },
            { description: 'Employee licenses (25 employees)', quantity: 25, unit_price: 79, amount: 1975 },
          ],
          subtotal: 4974,
          discount_amount: 0,
          taxable_amount: 4974,
          cgst_amount: 447.66,
          sgst_amount: 447.66,
          igst_amount: 0,
          total_tax: 895.32,
          total_amount: 5869.32,
          amount_paid: 0,
          amount_due: 5869.32,
          currency: 'INR',
          customer_name: 'Global Services Ltd',
          customer_email: 'finance@globalservices.com',
          customer_gstin: '29AABCU9603R1ZN',
          payment_link: 'https://rzp.io/i/xyz789',
          pdf_url: '/invoices/INV-2025-000045.pdf',
        },
      ])
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchInvoices()
  }, [page, statusFilter])

  // Filter invoices by search
  const filteredInvoices = invoices.filter(
    (inv) =>
      inv.invoice_number.toLowerCase().includes(search.toLowerCase()) ||
      inv.customer_name.toLowerCase().includes(search.toLowerCase())
  )

  // Calculate totals
  const totalAmount = invoices.reduce((sum, inv) => sum + inv.total_amount, 0)
  const totalPaid = invoices.reduce((sum, inv) => sum + inv.amount_paid, 0)
  const totalDue = invoices.reduce((sum, inv) => sum + inv.amount_due, 0)

  return (
    <div className="space-y-6">
      <PageHeader
        title="Invoices"
        description="View and manage subscription invoices"
        actions={
          <div className="flex gap-2">
            <Link href="/subscription">
              <Button variant="outline">
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Billing
              </Button>
            </Link>
            <Button variant="outline" onClick={fetchInvoices} disabled={isLoading}>
              <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
          </div>
        }
      />

      {/* Summary Cards */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Total Invoiced</p>
                <p className="text-2xl font-bold">{formatCurrency(totalAmount)}</p>
              </div>
              <Receipt className="h-8 w-8 text-muted-foreground" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Total Collected</p>
                <p className="text-2xl font-bold text-green-600">{formatCurrency(totalPaid)}</p>
              </div>
              <CheckCircle2 className="h-8 w-8 text-green-600" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Outstanding</p>
                <p className="text-2xl font-bold text-orange-600">{formatCurrency(totalDue)}</p>
              </div>
              <AlertTriangle className="h-8 w-8 text-orange-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="pt-4">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search by invoice number or customer..."
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  className="pl-9"
                />
              </div>
            </div>
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-[180px]">
                <Filter className="h-4 w-4 mr-2" />
                <SelectValue placeholder="Filter by status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Statuses</SelectItem>
                <SelectItem value="pending">Pending</SelectItem>
                <SelectItem value="paid">Paid</SelectItem>
                <SelectItem value="partially_paid">Partially Paid</SelectItem>
                <SelectItem value="overdue">Overdue</SelectItem>
                <SelectItem value="cancelled">Cancelled</SelectItem>
              </SelectContent>
            </Select>
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
        <Card className="p-4 border-yellow-200 bg-yellow-50">
          <div className="flex items-center gap-2 text-yellow-700">
            <AlertTriangle className="h-5 w-5" />
            <span>{error}</span>
          </div>
        </Card>
      )}

      {/* Invoices Table */}
      {!isLoading && (
        <Card>
          <CardContent className="pt-4">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Invoice #</TableHead>
                  <TableHead>Customer</TableHead>
                  <TableHead>Date</TableHead>
                  <TableHead>Due Date</TableHead>
                  <TableHead className="text-right">Amount</TableHead>
                  <TableHead className="text-right">Due</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredInvoices.length > 0 ? (
                  filteredInvoices.map((invoice) => {
                    const status = statusConfig[invoice.status] || statusConfig.pending
                    const isOverdue =
                      invoice.amount_due > 0 &&
                      new Date(invoice.due_date) < new Date()

                    return (
                      <TableRow key={invoice.id}>
                        <TableCell className="font-mono font-medium">
                          {invoice.invoice_number}
                        </TableCell>
                        <TableCell>
                          <div>
                            <p className="font-medium">{invoice.customer_name}</p>
                            {invoice.customer_email && (
                              <p className="text-xs text-muted-foreground">
                                {invoice.customer_email}
                              </p>
                            )}
                          </div>
                        </TableCell>
                        <TableCell>
                          {new Date(invoice.invoice_date).toLocaleDateString()}
                        </TableCell>
                        <TableCell className={isOverdue ? 'text-red-600 font-medium' : ''}>
                          {new Date(invoice.due_date).toLocaleDateString()}
                        </TableCell>
                        <TableCell className="text-right font-medium">
                          {formatCurrency(invoice.total_amount)}
                        </TableCell>
                        <TableCell className="text-right">
                          {invoice.amount_due > 0 ? (
                            <span className="text-orange-600 font-medium">
                              {formatCurrency(invoice.amount_due)}
                            </span>
                          ) : (
                            <span className="text-green-600">Paid</span>
                          )}
                        </TableCell>
                        <TableCell>
                          <Badge className={status.color}>
                            {status.icon}
                            <span className="ml-1">{status.label}</span>
                          </Badge>
                        </TableCell>
                        <TableCell className="text-right">
                          <div className="flex justify-end gap-1">
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => {
                                setSelectedInvoice(invoice)
                                setShowDetail(true)
                              }}
                            >
                              <Eye className="h-4 w-4" />
                            </Button>
                            {invoice.pdf_url && (
                              <Button variant="ghost" size="sm" asChild>
                                <a href={invoice.pdf_url} target="_blank" rel="noopener noreferrer">
                                  <Download className="h-4 w-4" />
                                </a>
                              </Button>
                            )}
                          </div>
                        </TableCell>
                      </TableRow>
                    )
                  })
                ) : (
                  <TableRow>
                    <TableCell colSpan={8} className="text-center py-8 text-muted-foreground">
                      No invoices found
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>

            {/* Pagination */}
            <div className="flex items-center justify-between mt-4 pt-4 border-t">
              <p className="text-sm text-muted-foreground">
                Showing {page * pageSize + 1} to {Math.min((page + 1) * pageSize, invoices.length)} of{' '}
                {invoices.length} invoices
              </p>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setPage(Math.max(0, page - 1))}
                  disabled={page === 0}
                >
                  <ChevronLeft className="h-4 w-4" />
                  Previous
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setPage(page + 1)}
                  disabled={invoices.length < pageSize}
                >
                  Next
                  <ChevronRight className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Invoice Detail Dialog */}
      <InvoiceDetailDialog
        invoice={selectedInvoice}
        isOpen={showDetail}
        onClose={() => setShowDetail(false)}
      />
    </div>
  )
}
