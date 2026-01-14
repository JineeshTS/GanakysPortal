'use client'

import * as React from 'react'
import Link from 'next/link'
import { PageHeader } from '@/components/layout/page-header'
import { DataTable, Column } from '@/components/layout/data-table'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
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
import {
  RefreshCw,
  Download,
  Upload,
  CheckCircle,
  XCircle,
  AlertCircle,
  Search,
  FileText,
  Link2,
  Unlink,
  Eye,
  Settings,
  ArrowRight,
  Filter,
  Check,
  X,
  HelpCircle
} from 'lucide-react'

// Periods
const periods = [
  { value: '01-2026', label: 'January 2026' },
  { value: '12-2025', label: 'December 2025' },
  { value: '11-2025', label: 'November 2025' },
]

// Reconciliation Summary
const reconciliationSummary = {
  gstr2a: {
    totalInvoices: 165,
    totalValue: 7890000,
    totalTax: 1420200,
    matched: 145,
    matchedValue: 6890000,
    mismatchAmount: 12,
    mismatchValue: 567000,
    notInBooks: 5,
    notInBooksValue: 233000,
    notIn2A: 8,
    notIn2AValue: 200000
  },
  gstr2b: {
    totalInvoices: 162,
    totalValue: 7650000,
    totalTax: 1377000,
    matched: 148,
    matchedValue: 7100000,
    mismatchAmount: 8,
    mismatchValue: 350000,
    notInBooks: 3,
    notInBooksValue: 100000,
    notIn2B: 6,
    notIn2BValue: 100000
  }
}

// Mock Reconciliation Data - Mismatched Items
const mismatchedItems = [
  {
    id: '1',
    supplierGstin: '29AABCM1234A1Z5',
    supplierName: 'Office Supplies Co.',
    invoiceNumber: 'OS-2025-0456',
    invoiceDate: '2025-12-15',
    booksValue: 45000,
    booksTax: 8100,
    gstr2aValue: 45500,
    gstr2aTax: 8190,
    difference: 500,
    taxDifference: 90,
    status: 'amount_mismatch',
    matchType: 'partial'
  },
  {
    id: '2',
    supplierGstin: '27AABCT5678B1Z9',
    supplierName: 'Tech Hardware Ltd',
    invoiceNumber: 'TH-2025-0789',
    invoiceDate: '2025-12-20',
    booksValue: 125000,
    booksTax: 22500,
    gstr2aValue: 125000,
    gstr2aTax: 15000,
    difference: 0,
    taxDifference: 7500,
    status: 'tax_mismatch',
    matchType: 'partial'
  },
  {
    id: '3',
    supplierGstin: '33AABCS9012C1Z3',
    supplierName: 'Software Solutions Inc',
    invoiceNumber: 'SSI-2025-0234',
    invoiceDate: '2025-12-22',
    booksValue: 78000,
    booksTax: 14040,
    gstr2aValue: 78500,
    gstr2aTax: 14130,
    difference: 500,
    taxDifference: 90,
    status: 'amount_mismatch',
    matchType: 'partial'
  }
]

// Mock Reconciliation Data - Not in Books
const notInBooks = [
  {
    id: '1',
    supplierGstin: '29AABCN1234D1Z7',
    supplierName: 'New Vendor Corp',
    invoiceNumber: 'NV-2025-0567',
    invoiceDate: '2025-12-18',
    gstr2aValue: 56000,
    gstr2aTax: 10080,
    status: 'not_in_books',
    action: 'pending'
  },
  {
    id: '2',
    supplierGstin: '24AABCP7890E1Z1',
    supplierName: 'Premium Parts Ltd',
    invoiceNumber: 'PP-2025-0890',
    invoiceDate: '2025-12-25',
    gstr2aValue: 89000,
    gstr2aTax: 16020,
    status: 'not_in_books',
    action: 'pending'
  }
]

// Mock Reconciliation Data - Not in GSTR-2A
const notInGstr2a = [
  {
    id: '1',
    supplierGstin: '29AABCE3456F1Z5',
    supplierName: 'Equipment Services',
    invoiceNumber: 'ES-2025-0123',
    invoiceDate: '2025-12-10',
    booksValue: 67000,
    booksTax: 12060,
    status: 'not_in_2a',
    reason: 'Supplier not filed GSTR-1'
  },
  {
    id: '2',
    supplierGstin: '27AABCF6789G1Z9',
    supplierName: 'Facility Management Co',
    invoiceNumber: 'FM-2025-0456',
    invoiceDate: '2025-12-12',
    booksValue: 45000,
    booksTax: 8100,
    status: 'not_in_2a',
    reason: 'Invoice date mismatch'
  }
]

// Matched Items (sample)
const matchedItems = [
  {
    id: '1',
    supplierGstin: '29AABCG1234H1Z3',
    supplierName: 'ABC Technologies',
    invoiceNumber: 'ABC-2025-0789',
    invoiceDate: '2025-12-05',
    value: 234000,
    tax: 42120,
    status: 'matched'
  },
  {
    id: '2',
    supplierGstin: '33AABCH5678I1Z7',
    supplierName: 'Chennai IT Services',
    invoiceNumber: 'CIT-2025-0456',
    invoiceDate: '2025-12-08',
    value: 156000,
    tax: 28080,
    status: 'matched'
  },
  {
    id: '3',
    supplierGstin: '27AABCI9012J1Z1',
    supplierName: 'Mumbai Marketing',
    invoiceNumber: 'MM-2025-0123',
    invoiceDate: '2025-12-10',
    value: 89000,
    tax: 16020,
    status: 'matched'
  }
]

export default function GSTReconciliationPage() {
  const [selectedPeriod, setSelectedPeriod] = React.useState('12-2025')
  const [selectedSource, setSelectedSource] = React.useState<'2a' | '2b'>('2a')
  const [selectedItems, setSelectedItems] = React.useState<string[]>([])

  const getStatusBadge = (status: string) => {
    const config: Record<string, { label: string; className: string; icon: React.ReactNode }> = {
      matched: {
        label: 'Matched',
        className: 'bg-green-100 text-green-800',
        icon: <CheckCircle className="h-3 w-3" />
      },
      amount_mismatch: {
        label: 'Amount Mismatch',
        className: 'bg-yellow-100 text-yellow-800',
        icon: <AlertCircle className="h-3 w-3" />
      },
      tax_mismatch: {
        label: 'Tax Mismatch',
        className: 'bg-orange-100 text-orange-800',
        icon: <AlertCircle className="h-3 w-3" />
      },
      not_in_books: {
        label: 'Not in Books',
        className: 'bg-red-100 text-red-800',
        icon: <XCircle className="h-3 w-3" />
      },
      not_in_2a: {
        label: 'Not in GSTR-2A',
        className: 'bg-purple-100 text-purple-800',
        icon: <XCircle className="h-3 w-3" />
      }
    }
    const c = config[status] || config.matched
    return (
      <Badge className={`${c.className} flex items-center gap-1`}>
        {c.icon}
        {c.label}
      </Badge>
    )
  }

  const mismatchColumns: Column<typeof mismatchedItems[0]>[] = [
    {
      key: 'supplier',
      header: 'Supplier',
      accessor: (row) => (
        <div>
          <p className="font-mono text-sm">{row.supplierGstin}</p>
          <p className="text-xs text-muted-foreground">{row.supplierName}</p>
        </div>
      )
    },
    {
      key: 'invoice',
      header: 'Invoice',
      accessor: (row) => (
        <div>
          <p className="font-mono font-medium">{row.invoiceNumber}</p>
          <p className="text-xs text-muted-foreground">{formatDate(row.invoiceDate)}</p>
        </div>
      )
    },
    {
      key: 'books',
      header: 'As per Books',
      className: 'text-right',
      headerClassName: 'text-right',
      accessor: (row) => (
        <div className="text-right">
          <p>{formatCurrency(row.booksValue)}</p>
          <p className="text-xs text-muted-foreground">Tax: {formatCurrency(row.booksTax)}</p>
        </div>
      )
    },
    {
      key: 'gstr2a',
      header: 'As per GSTR-2A',
      className: 'text-right',
      headerClassName: 'text-right',
      accessor: (row) => (
        <div className="text-right">
          <p>{formatCurrency(row.gstr2aValue)}</p>
          <p className="text-xs text-muted-foreground">Tax: {formatCurrency(row.gstr2aTax)}</p>
        </div>
      )
    },
    {
      key: 'difference',
      header: 'Difference',
      className: 'text-right',
      headerClassName: 'text-right',
      accessor: (row) => (
        <div className="text-right">
          <p className={row.difference !== 0 ? 'text-red-600 font-medium' : ''}>
            {formatCurrency(row.difference)}
          </p>
          <p className={`text-xs ${row.taxDifference !== 0 ? 'text-red-600' : 'text-muted-foreground'}`}>
            Tax: {formatCurrency(row.taxDifference)}
          </p>
        </div>
      )
    },
    {
      key: 'status',
      header: 'Status',
      accessor: (row) => getStatusBadge(row.status)
    },
    {
      key: 'actions',
      header: 'Action',
      accessor: (row) => (
        <div className="flex items-center gap-1">
          <Button variant="ghost" size="icon" title="Accept Supplier Value">
            <Check className="h-4 w-4 text-green-600" />
          </Button>
          <Button variant="ghost" size="icon" title="Keep Books Value">
            <X className="h-4 w-4 text-red-600" />
          </Button>
          <Button variant="ghost" size="icon" title="View Details">
            <Eye className="h-4 w-4" />
          </Button>
        </div>
      )
    }
  ]

  const notInBooksColumns: Column<typeof notInBooks[0]>[] = [
    {
      key: 'supplier',
      header: 'Supplier',
      accessor: (row) => (
        <div>
          <p className="font-mono text-sm">{row.supplierGstin}</p>
          <p className="text-xs text-muted-foreground">{row.supplierName}</p>
        </div>
      )
    },
    {
      key: 'invoice',
      header: 'Invoice',
      accessor: (row) => (
        <div>
          <p className="font-mono font-medium">{row.invoiceNumber}</p>
          <p className="text-xs text-muted-foreground">{formatDate(row.invoiceDate)}</p>
        </div>
      )
    },
    {
      key: 'value',
      header: 'Value',
      className: 'text-right',
      headerClassName: 'text-right',
      accessor: (row) => (
        <div className="text-right">
          <p className="font-medium">{formatCurrency(row.gstr2aValue)}</p>
          <p className="text-xs text-muted-foreground">Tax: {formatCurrency(row.gstr2aTax)}</p>
        </div>
      )
    },
    {
      key: 'status',
      header: 'Status',
      accessor: (row) => getStatusBadge(row.status)
    },
    {
      key: 'actions',
      header: 'Action',
      accessor: (row) => (
        <div className="flex items-center gap-1">
          <Button variant="outline" size="sm">
            <Link2 className="h-3 w-3 mr-1" />
            Link to Bill
          </Button>
          <Button variant="ghost" size="sm">
            Add to Books
          </Button>
        </div>
      )
    }
  ]

  const notIn2aColumns: Column<typeof notInGstr2a[0]>[] = [
    {
      key: 'supplier',
      header: 'Supplier',
      accessor: (row) => (
        <div>
          <p className="font-mono text-sm">{row.supplierGstin}</p>
          <p className="text-xs text-muted-foreground">{row.supplierName}</p>
        </div>
      )
    },
    {
      key: 'invoice',
      header: 'Invoice (Books)',
      accessor: (row) => (
        <div>
          <p className="font-mono font-medium">{row.invoiceNumber}</p>
          <p className="text-xs text-muted-foreground">{formatDate(row.invoiceDate)}</p>
        </div>
      )
    },
    {
      key: 'value',
      header: 'Value',
      className: 'text-right',
      headerClassName: 'text-right',
      accessor: (row) => (
        <div className="text-right">
          <p className="font-medium">{formatCurrency(row.booksValue)}</p>
          <p className="text-xs text-muted-foreground">Tax: {formatCurrency(row.booksTax)}</p>
        </div>
      )
    },
    {
      key: 'reason',
      header: 'Possible Reason',
      accessor: (row) => (
        <div className="flex items-center gap-1">
          <HelpCircle className="h-3 w-3 text-muted-foreground" />
          <span className="text-sm text-muted-foreground">{row.reason}</span>
        </div>
      )
    },
    {
      key: 'status',
      header: 'Status',
      accessor: (row) => getStatusBadge(row.status)
    },
    {
      key: 'actions',
      header: 'Action',
      accessor: (row) => (
        <div className="flex items-center gap-1">
          <Button variant="outline" size="sm">
            Contact Supplier
          </Button>
        </div>
      )
    }
  ]

  const summary = selectedSource === '2a' ? reconciliationSummary.gstr2a : reconciliationSummary.gstr2b

  return (
    <div className="space-y-6">
      <PageHeader
        title="GST Reconciliation"
        description="Reconcile purchase register with GSTR-2A/2B"
        breadcrumbs={[
          { label: 'Dashboard', href: '/dashboard' },
          { label: 'Finance', href: '/finance' },
          { label: 'GST', href: '/finance/gst' },
          { label: 'Reconciliation' }
        ]}
        actions={
          <div className="flex items-center gap-2">
            <Select value={selectedPeriod} onValueChange={setSelectedPeriod}>
              <SelectTrigger className="w-[180px]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {periods.map(period => (
                  <SelectItem key={period.value} value={period.value}>
                    {period.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Button variant="outline" size="sm">
              <Upload className="h-4 w-4 mr-2" />
              Import GSTR-2A/2B
            </Button>
            <Button variant="outline" size="sm">
              <RefreshCw className="h-4 w-4 mr-2" />
              Auto-Match
            </Button>
            <Button variant="outline" size="sm">
              <Download className="h-4 w-4 mr-2" />
              Export Report
            </Button>
          </div>
        }
      />

      {/* Source Selection */}
      <div className="flex items-center gap-4">
        <Label>Reconcile with:</Label>
        <div className="flex gap-2">
          <Button
            variant={selectedSource === '2a' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setSelectedSource('2a')}
          >
            GSTR-2A
          </Button>
          <Button
            variant={selectedSource === '2b' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setSelectedSource('2b')}
          >
            GSTR-2B
          </Button>
        </div>
        <span className="text-sm text-muted-foreground">
          {selectedSource === '2a'
            ? '(Dynamic statement - updated as suppliers file)'
            : '(Static statement - generated on 14th of each month)'
          }
        </span>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Total Invoices</p>
                <p className="text-2xl font-bold">{summary.totalInvoices}</p>
                <p className="text-xs text-muted-foreground mt-1">
                  {formatCurrency(summary.totalValue)}
                </p>
              </div>
              <FileText className="h-8 w-8 text-muted-foreground" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-green-50 border-green-200">
          <CardContent className="pt-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-green-600">Matched</p>
                <p className="text-2xl font-bold text-green-700">{summary.matched}</p>
                <p className="text-xs text-green-600 mt-1">
                  {formatCurrency(summary.matchedValue)}
                </p>
              </div>
              <CheckCircle className="h-8 w-8 text-green-500" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-yellow-50 border-yellow-200">
          <CardContent className="pt-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-yellow-600">Mismatched</p>
                <p className="text-2xl font-bold text-yellow-700">{summary.mismatchAmount}</p>
                <p className="text-xs text-yellow-600 mt-1">
                  {formatCurrency(summary.mismatchValue)}
                </p>
              </div>
              <AlertCircle className="h-8 w-8 text-yellow-500" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-red-50 border-red-200">
          <CardContent className="pt-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-red-600">Not in Books</p>
                <p className="text-2xl font-bold text-red-700">{summary.notInBooks}</p>
                <p className="text-xs text-red-600 mt-1">
                  {formatCurrency(summary.notInBooksValue)}
                </p>
              </div>
              <Unlink className="h-8 w-8 text-red-500" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-purple-50 border-purple-200">
          <CardContent className="pt-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-purple-600">Not in {selectedSource.toUpperCase()}</p>
                <p className="text-2xl font-bold text-purple-700">
                  {selectedSource === '2a' ? summary.notIn2A : summary.notIn2B}
                </p>
                <p className="text-xs text-purple-600 mt-1">
                  {formatCurrency(selectedSource === '2a' ? summary.notIn2AValue : summary.notIn2BValue)}
                </p>
              </div>
              <Unlink className="h-8 w-8 text-purple-500" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Match Summary Progress */}
      <Card>
        <CardContent className="py-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium">Reconciliation Progress</span>
            <span className="text-sm text-muted-foreground">
              {Math.round((summary.matched / summary.totalInvoices) * 100)}% matched
            </span>
          </div>
          <div className="h-3 bg-muted rounded-full overflow-hidden flex">
            <div
              className="h-full bg-green-500"
              style={{ width: `${(summary.matched / summary.totalInvoices) * 100}%` }}
            />
            <div
              className="h-full bg-yellow-500"
              style={{ width: `${(summary.mismatchAmount / summary.totalInvoices) * 100}%` }}
            />
            <div
              className="h-full bg-red-500"
              style={{ width: `${(summary.notInBooks / summary.totalInvoices) * 100}%` }}
            />
            <div
              className="h-full bg-purple-500"
              style={{ width: `${((selectedSource === '2a' ? summary.notIn2A : summary.notIn2B) / summary.totalInvoices) * 100}%` }}
            />
          </div>
          <div className="flex gap-4 mt-2 text-xs">
            <span className="flex items-center gap-1">
              <span className="h-2 w-2 rounded-full bg-green-500" /> Matched
            </span>
            <span className="flex items-center gap-1">
              <span className="h-2 w-2 rounded-full bg-yellow-500" /> Mismatched
            </span>
            <span className="flex items-center gap-1">
              <span className="h-2 w-2 rounded-full bg-red-500" /> Not in Books
            </span>
            <span className="flex items-center gap-1">
              <span className="h-2 w-2 rounded-full bg-purple-500" /> Not in {selectedSource.toUpperCase()}
            </span>
          </div>
        </CardContent>
      </Card>

      {/* Tabbed Content */}
      <Tabs defaultValue="mismatched" className="space-y-4">
        <TabsList>
          <TabsTrigger value="matched" className="gap-2">
            <CheckCircle className="h-4 w-4" />
            Matched ({summary.matched})
          </TabsTrigger>
          <TabsTrigger value="mismatched" className="gap-2">
            <AlertCircle className="h-4 w-4" />
            Mismatched ({summary.mismatchAmount})
          </TabsTrigger>
          <TabsTrigger value="not-in-books" className="gap-2">
            <XCircle className="h-4 w-4" />
            Not in Books ({summary.notInBooks})
          </TabsTrigger>
          <TabsTrigger value="not-in-2a" className="gap-2">
            <Unlink className="h-4 w-4" />
            Not in {selectedSource.toUpperCase()} ({selectedSource === '2a' ? summary.notIn2A : summary.notIn2B})
          </TabsTrigger>
        </TabsList>

        {/* Matched Tab */}
        <TabsContent value="matched">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Matched Invoices</CardTitle>
              <CardDescription>
                Invoices that match between your books and GSTR-{selectedSource.toUpperCase()}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <DataTable
                data={matchedItems}
                columns={[
                  {
                    key: 'supplier',
                    header: 'Supplier',
                    accessor: (row) => (
                      <div>
                        <p className="font-mono text-sm">{row.supplierGstin}</p>
                        <p className="text-xs text-muted-foreground">{row.supplierName}</p>
                      </div>
                    )
                  },
                  {
                    key: 'invoice',
                    header: 'Invoice',
                    accessor: (row) => (
                      <div>
                        <p className="font-mono font-medium">{row.invoiceNumber}</p>
                        <p className="text-xs text-muted-foreground">{formatDate(row.invoiceDate)}</p>
                      </div>
                    )
                  },
                  {
                    key: 'value',
                    header: 'Value',
                    className: 'text-right',
                    headerClassName: 'text-right',
                    accessor: (row) => (
                      <div className="text-right">
                        <p className="font-medium">{formatCurrency(row.value)}</p>
                        <p className="text-xs text-muted-foreground">Tax: {formatCurrency(row.tax)}</p>
                      </div>
                    )
                  },
                  {
                    key: 'status',
                    header: 'Status',
                    accessor: (row) => getStatusBadge(row.status)
                  }
                ]}
                keyExtractor={(row) => row.id}
                emptyMessage="No matched invoices"
              />
            </CardContent>
          </Card>
        </TabsContent>

        {/* Mismatched Tab */}
        <TabsContent value="mismatched">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle className="text-lg">Mismatched Invoices</CardTitle>
                <CardDescription>
                  Invoices with amount or tax discrepancies between books and GSTR-{selectedSource.toUpperCase()}
                </CardDescription>
              </div>
              <div className="flex items-center gap-2">
                <Button variant="outline" size="sm">
                  <Check className="h-4 w-4 mr-2" />
                  Accept All Supplier Values
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <DataTable
                data={mismatchedItems}
                columns={mismatchColumns}
                keyExtractor={(row) => row.id}
                emptyMessage="No mismatched invoices"
              />
            </CardContent>
          </Card>
        </TabsContent>

        {/* Not in Books Tab */}
        <TabsContent value="not-in-books">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle className="text-lg">Not in Books</CardTitle>
                <CardDescription>
                  Invoices appearing in GSTR-{selectedSource.toUpperCase()} but not recorded in your purchase register
                </CardDescription>
              </div>
              <Button variant="outline" size="sm">
                <Settings className="h-4 w-4 mr-2" />
                Matching Settings
              </Button>
            </CardHeader>
            <CardContent>
              <DataTable
                data={notInBooks}
                columns={notInBooksColumns}
                keyExtractor={(row) => row.id}
                emptyMessage="No unmatched invoices from GSTR-2A"
              />

              <div className="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                <div className="flex items-start gap-2">
                  <AlertCircle className="h-4 w-4 text-yellow-600 mt-0.5" />
                  <div className="text-sm">
                    <p className="font-medium text-yellow-800">ITC at Risk</p>
                    <p className="text-yellow-600">
                      These invoices are in GSTR-{selectedSource.toUpperCase()} but not in your books.
                      You may be missing eligible ITC of {formatCurrency(summary.notInBooksValue * 0.18)}.
                    </p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Not in GSTR-2A Tab */}
        <TabsContent value="not-in-2a">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Not in GSTR-{selectedSource.toUpperCase()}</CardTitle>
              <CardDescription>
                Invoices recorded in your books but not appearing in GSTR-{selectedSource.toUpperCase()}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <DataTable
                data={notInGstr2a}
                columns={notIn2aColumns}
                keyExtractor={(row) => row.id}
                emptyMessage={`No invoices missing from GSTR-${selectedSource.toUpperCase()}`}
              />

              <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
                <div className="flex items-start gap-2">
                  <XCircle className="h-4 w-4 text-red-600 mt-0.5" />
                  <div className="text-sm">
                    <p className="font-medium text-red-800">Action Required</p>
                    <p className="text-red-600">
                      ITC for these invoices cannot be claimed until they appear in GSTR-{selectedSource.toUpperCase()}.
                      Contact your suppliers to ensure they file their GSTR-1.
                    </p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
