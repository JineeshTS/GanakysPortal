'use client'

import * as React from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { formatCurrency, formatDate } from '@/lib/format'
import {
  CheckCircle,
  XCircle,
  AlertCircle,
  Search,
  Link2,
  Unlink,
  Eye,
  Check,
  X,
  HelpCircle,
  ChevronDown,
  ChevronUp
} from 'lucide-react'

export type ReconciliationStatus =
  | 'matched'
  | 'amount_mismatch'
  | 'tax_mismatch'
  | 'date_mismatch'
  | 'not_in_books'
  | 'not_in_2a'
  | 'not_in_2b'

export interface ReconciliationItem {
  id: string
  supplierGstin: string
  supplierName: string
  invoiceNumber: string
  invoiceDate: string
  booksValue?: number
  booksTax?: number
  gstPortalValue?: number
  gstPortalTax?: number
  difference?: number
  taxDifference?: number
  status: ReconciliationStatus
  reason?: string
}

interface ReconciliationTableProps {
  items: ReconciliationItem[]
  source: '2a' | '2b'
  onMatch?: (id: string) => void
  onUnmatch?: (id: string) => void
  onAcceptPortalValue?: (id: string) => void
  onKeepBooksValue?: (id: string) => void
  onLinkToBill?: (id: string) => void
  onViewDetails?: (id: string) => void
  onContactSupplier?: (id: string) => void
  className?: string
}

export function ReconciliationTable({
  items,
  source,
  onMatch,
  onUnmatch,
  onAcceptPortalValue,
  onKeepBooksValue,
  onLinkToBill,
  onViewDetails,
  onContactSupplier,
  className
}: ReconciliationTableProps) {
  const [searchQuery, setSearchQuery] = React.useState('')
  const [sortField, setSortField] = React.useState<keyof ReconciliationItem>('invoiceDate')
  const [sortOrder, setSortOrder] = React.useState<'asc' | 'desc'>('desc')
  const [expandedRows, setExpandedRows] = React.useState<Set<string>>(new Set())

  const toggleRowExpansion = (id: string) => {
    setExpandedRows(prev => {
      const newSet = new Set(prev)
      if (newSet.has(id)) {
        newSet.delete(id)
      } else {
        newSet.add(id)
      }
      return newSet
    })
  }

  const handleSort = (field: keyof ReconciliationItem) => {
    if (sortField === field) {
      setSortOrder(prev => prev === 'asc' ? 'desc' : 'asc')
    } else {
      setSortField(field)
      setSortOrder('asc')
    }
  }

  const getStatusConfig = (status: ReconciliationStatus) => {
    const config: Record<ReconciliationStatus, { label: string; className: string; icon: React.ReactNode }> = {
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
      date_mismatch: {
        label: 'Date Mismatch',
        className: 'bg-purple-100 text-purple-800',
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
        icon: <Unlink className="h-3 w-3" />
      },
      not_in_2b: {
        label: 'Not in GSTR-2B',
        className: 'bg-purple-100 text-purple-800',
        icon: <Unlink className="h-3 w-3" />
      }
    }
    return config[status]
  }

  const filteredItems = React.useMemo(() => {
    let result = [...items]

    if (searchQuery) {
      const query = searchQuery.toLowerCase()
      result = result.filter(item =>
        item.supplierGstin.toLowerCase().includes(query) ||
        item.supplierName.toLowerCase().includes(query) ||
        item.invoiceNumber.toLowerCase().includes(query)
      )
    }

    result.sort((a, b) => {
      const aValue = a[sortField]
      const bValue = b[sortField]
      if (aValue === undefined || bValue === undefined) return 0
      if (typeof aValue === 'string' && typeof bValue === 'string') {
        return sortOrder === 'asc'
          ? aValue.localeCompare(bValue)
          : bValue.localeCompare(aValue)
      }
      if (typeof aValue === 'number' && typeof bValue === 'number') {
        return sortOrder === 'asc' ? aValue - bValue : bValue - aValue
      }
      return 0
    })

    return result
  }, [items, searchQuery, sortField, sortOrder])

  const renderSortIcon = (field: keyof ReconciliationItem) => {
    if (sortField !== field) return null
    return sortOrder === 'asc' ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />
  }

  const renderActions = (item: ReconciliationItem) => {
    switch (item.status) {
      case 'matched':
        return (
          <div className="flex items-center gap-1">
            {onViewDetails && (
              <Button variant="ghost" size="icon" onClick={() => onViewDetails(item.id)} title="View Details">
                <Eye className="h-4 w-4" />
              </Button>
            )}
            {onUnmatch && (
              <Button variant="ghost" size="icon" onClick={() => onUnmatch(item.id)} title="Unmatch">
                <Unlink className="h-4 w-4" />
              </Button>
            )}
          </div>
        )

      case 'amount_mismatch':
      case 'tax_mismatch':
      case 'date_mismatch':
        return (
          <div className="flex items-center gap-1">
            {onAcceptPortalValue && (
              <Button
                variant="ghost"
                size="icon"
                onClick={() => onAcceptPortalValue(item.id)}
                title="Accept Portal Value"
              >
                <Check className="h-4 w-4 text-green-600" />
              </Button>
            )}
            {onKeepBooksValue && (
              <Button
                variant="ghost"
                size="icon"
                onClick={() => onKeepBooksValue(item.id)}
                title="Keep Books Value"
              >
                <X className="h-4 w-4 text-red-600" />
              </Button>
            )}
            {onViewDetails && (
              <Button variant="ghost" size="icon" onClick={() => onViewDetails(item.id)} title="View Details">
                <Eye className="h-4 w-4" />
              </Button>
            )}
          </div>
        )

      case 'not_in_books':
        return (
          <div className="flex items-center gap-1">
            {onLinkToBill && (
              <Button variant="outline" size="sm" onClick={() => onLinkToBill(item.id)}>
                <Link2 className="h-3 w-3 mr-1" />
                Link to Bill
              </Button>
            )}
          </div>
        )

      case 'not_in_2a':
      case 'not_in_2b':
        return (
          <div className="flex items-center gap-1">
            {onContactSupplier && (
              <Button variant="outline" size="sm" onClick={() => onContactSupplier(item.id)}>
                Contact Supplier
              </Button>
            )}
          </div>
        )

      default:
        return null
    }
  }

  return (
    <div className={className}>
      {/* Search */}
      <div className="mb-4 flex items-center gap-4">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search by GSTIN, supplier, or invoice..."
            className="pl-10"
          />
        </div>
        <span className="text-sm text-muted-foreground">
          {filteredItems.length} of {items.length} items
        </span>
      </div>

      {/* Table */}
      <div className="border rounded-lg overflow-hidden">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-[40px]"></TableHead>
              <TableHead
                className="cursor-pointer"
                onClick={() => handleSort('supplierGstin')}
              >
                <div className="flex items-center gap-1">
                  Supplier {renderSortIcon('supplierGstin')}
                </div>
              </TableHead>
              <TableHead
                className="cursor-pointer"
                onClick={() => handleSort('invoiceNumber')}
              >
                <div className="flex items-center gap-1">
                  Invoice {renderSortIcon('invoiceNumber')}
                </div>
              </TableHead>
              <TableHead className="text-right">Books</TableHead>
              <TableHead className="text-right">GSTR-{source.toUpperCase()}</TableHead>
              <TableHead className="text-right">Difference</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filteredItems.map((item) => {
              const statusConfig = getStatusConfig(item.status)
              const isExpanded = expandedRows.has(item.id)

              return (
                <React.Fragment key={item.id}>
                  <TableRow>
                    <TableCell>
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-6 w-6"
                        onClick={() => toggleRowExpansion(item.id)}
                      >
                        {isExpanded ? (
                          <ChevronUp className="h-4 w-4" />
                        ) : (
                          <ChevronDown className="h-4 w-4" />
                        )}
                      </Button>
                    </TableCell>
                    <TableCell>
                      <div>
                        <p className="font-mono text-sm">{item.supplierGstin}</p>
                        <p className="text-xs text-muted-foreground">{item.supplierName}</p>
                      </div>
                    </TableCell>
                    <TableCell>
                      <div>
                        <p className="font-mono font-medium">{item.invoiceNumber}</p>
                        <p className="text-xs text-muted-foreground">{formatDate(item.invoiceDate)}</p>
                      </div>
                    </TableCell>
                    <TableCell className="text-right">
                      {item.booksValue !== undefined ? (
                        <div>
                          <p>{formatCurrency(item.booksValue)}</p>
                          <p className="text-xs text-muted-foreground">
                            Tax: {formatCurrency(item.booksTax || 0)}
                          </p>
                        </div>
                      ) : (
                        <span className="text-muted-foreground">-</span>
                      )}
                    </TableCell>
                    <TableCell className="text-right">
                      {item.gstPortalValue !== undefined ? (
                        <div>
                          <p>{formatCurrency(item.gstPortalValue)}</p>
                          <p className="text-xs text-muted-foreground">
                            Tax: {formatCurrency(item.gstPortalTax || 0)}
                          </p>
                        </div>
                      ) : (
                        <span className="text-muted-foreground">-</span>
                      )}
                    </TableCell>
                    <TableCell className="text-right">
                      {item.difference !== undefined && item.difference !== 0 ? (
                        <div>
                          <p className="text-red-600 font-medium">
                            {formatCurrency(item.difference)}
                          </p>
                          {item.taxDifference !== undefined && item.taxDifference !== 0 && (
                            <p className="text-xs text-red-600">
                              Tax: {formatCurrency(item.taxDifference)}
                            </p>
                          )}
                        </div>
                      ) : item.status === 'matched' ? (
                        <CheckCircle className="h-4 w-4 text-green-600 ml-auto" />
                      ) : (
                        <span className="text-muted-foreground">-</span>
                      )}
                    </TableCell>
                    <TableCell>
                      <Badge className={`${statusConfig.className} flex items-center gap-1 w-fit`}>
                        {statusConfig.icon}
                        {statusConfig.label}
                      </Badge>
                    </TableCell>
                    <TableCell>{renderActions(item)}</TableCell>
                  </TableRow>

                  {/* Expanded Row Details */}
                  {isExpanded && (
                    <TableRow className="bg-muted/50">
                      <TableCell colSpan={8} className="p-4">
                        <div className="grid grid-cols-3 gap-4 text-sm">
                          <div>
                            <h4 className="font-medium mb-2">Supplier Details</h4>
                            <p><span className="text-muted-foreground">GSTIN:</span> {item.supplierGstin}</p>
                            <p><span className="text-muted-foreground">Name:</span> {item.supplierName}</p>
                          </div>
                          <div>
                            <h4 className="font-medium mb-2">Invoice Details</h4>
                            <p><span className="text-muted-foreground">Number:</span> {item.invoiceNumber}</p>
                            <p><span className="text-muted-foreground">Date:</span> {formatDate(item.invoiceDate)}</p>
                          </div>
                          <div>
                            <h4 className="font-medium mb-2">Comparison</h4>
                            <div className="grid grid-cols-2 gap-2">
                              <div>
                                <p className="text-muted-foreground">Books Value</p>
                                <p className="font-medium">{formatCurrency(item.booksValue || 0)}</p>
                              </div>
                              <div>
                                <p className="text-muted-foreground">Portal Value</p>
                                <p className="font-medium">{formatCurrency(item.gstPortalValue || 0)}</p>
                              </div>
                            </div>
                          </div>
                        </div>
                        {item.reason && (
                          <div className="mt-4 flex items-start gap-2 p-3 bg-yellow-50 rounded-lg">
                            <HelpCircle className="h-4 w-4 text-yellow-600 mt-0.5" />
                            <div>
                              <p className="font-medium text-yellow-800">Possible Reason</p>
                              <p className="text-yellow-700">{item.reason}</p>
                            </div>
                          </div>
                        )}
                      </TableCell>
                    </TableRow>
                  )}
                </React.Fragment>
              )
            })}

            {filteredItems.length === 0 && (
              <TableRow>
                <TableCell colSpan={8} className="text-center py-8 text-muted-foreground">
                  No items found
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>
    </div>
  )
}

// Summary component for reconciliation statistics
interface ReconciliationSummaryProps {
  matched: number
  matchedValue: number
  mismatched: number
  mismatchedValue: number
  notInBooks: number
  notInBooksValue: number
  notInPortal: number
  notInPortalValue: number
  source: '2a' | '2b'
}

export function ReconciliationSummary({
  matched,
  matchedValue,
  mismatched,
  mismatchedValue,
  notInBooks,
  notInBooksValue,
  notInPortal,
  notInPortalValue,
  source
}: ReconciliationSummaryProps) {
  const total = matched + mismatched + notInBooks + notInPortal

  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
      <Card className="bg-green-50 border-green-200">
        <CardContent className="pt-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-green-600">Matched</p>
              <p className="text-2xl font-bold text-green-700">{matched}</p>
              <p className="text-xs text-green-600">{formatCurrency(matchedValue)}</p>
            </div>
            <CheckCircle className="h-8 w-8 text-green-500" />
          </div>
          <div className="mt-2 h-1 bg-green-200 rounded-full">
            <div
              className="h-1 bg-green-500 rounded-full"
              style={{ width: `${(matched / total) * 100}%` }}
            />
          </div>
        </CardContent>
      </Card>

      <Card className="bg-yellow-50 border-yellow-200">
        <CardContent className="pt-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-yellow-600">Mismatched</p>
              <p className="text-2xl font-bold text-yellow-700">{mismatched}</p>
              <p className="text-xs text-yellow-600">{formatCurrency(mismatchedValue)}</p>
            </div>
            <AlertCircle className="h-8 w-8 text-yellow-500" />
          </div>
          <div className="mt-2 h-1 bg-yellow-200 rounded-full">
            <div
              className="h-1 bg-yellow-500 rounded-full"
              style={{ width: `${(mismatched / total) * 100}%` }}
            />
          </div>
        </CardContent>
      </Card>

      <Card className="bg-red-50 border-red-200">
        <CardContent className="pt-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-red-600">Not in Books</p>
              <p className="text-2xl font-bold text-red-700">{notInBooks}</p>
              <p className="text-xs text-red-600">{formatCurrency(notInBooksValue)}</p>
            </div>
            <XCircle className="h-8 w-8 text-red-500" />
          </div>
          <div className="mt-2 h-1 bg-red-200 rounded-full">
            <div
              className="h-1 bg-red-500 rounded-full"
              style={{ width: `${(notInBooks / total) * 100}%` }}
            />
          </div>
        </CardContent>
      </Card>

      <Card className="bg-purple-50 border-purple-200">
        <CardContent className="pt-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-purple-600">Not in GSTR-{source.toUpperCase()}</p>
              <p className="text-2xl font-bold text-purple-700">{notInPortal}</p>
              <p className="text-xs text-purple-600">{formatCurrency(notInPortalValue)}</p>
            </div>
            <Unlink className="h-8 w-8 text-purple-500" />
          </div>
          <div className="mt-2 h-1 bg-purple-200 rounded-full">
            <div
              className="h-1 bg-purple-500 rounded-full"
              style={{ width: `${(notInPortal / total) * 100}%` }}
            />
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default ReconciliationTable
