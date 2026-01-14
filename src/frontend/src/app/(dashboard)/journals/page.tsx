'use client'

import * as React from 'react'
import Link from 'next/link'
import { PageHeader } from '@/components/layout/page-header'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { formatCurrency, formatDate } from '@/lib/format'
import { useApi } from '@/hooks'
import {
  Plus,
  Search,
  FileText,
  Download,
  Filter,
  Calendar,
  ArrowUpRight,
  ArrowDownRight,
  Loader2,
  Eye
} from 'lucide-react'

interface JournalEntry {
  id: string
  entry_number: string
  date: string
  reference: string
  narration: string
  total_debit: number
  total_credit: number
  status: 'draft' | 'posted' | 'reversed'
  created_by: string
  created_at: string
}

// Mock journal entries
const mockJournalEntries: JournalEntry[] = [
  {
    id: '1',
    entry_number: 'JV-2026-001',
    date: '2026-01-10',
    reference: 'SAL-JAN-2026',
    narration: 'Salary provision for January 2026',
    total_debit: 2500000,
    total_credit: 2500000,
    status: 'posted',
    created_by: 'Admin',
    created_at: '2026-01-10T10:00:00Z'
  },
  {
    id: '2',
    entry_number: 'JV-2026-002',
    date: '2026-01-08',
    reference: 'DEP-JAN-2026',
    narration: 'Depreciation entry for January 2026',
    total_debit: 125000,
    total_credit: 125000,
    status: 'posted',
    created_by: 'Admin',
    created_at: '2026-01-08T14:30:00Z'
  },
  {
    id: '3',
    entry_number: 'JV-2026-003',
    date: '2026-01-05',
    reference: 'ADJ-001',
    narration: 'Year-end adjustment entry',
    total_debit: 45000,
    total_credit: 45000,
    status: 'draft',
    created_by: 'Accountant',
    created_at: '2026-01-05T09:15:00Z'
  },
  {
    id: '4',
    entry_number: 'JV-2025-156',
    date: '2025-12-31',
    reference: 'PROV-DEC-2025',
    narration: 'Provisions for December 2025',
    total_debit: 350000,
    total_credit: 350000,
    status: 'posted',
    created_by: 'Admin',
    created_at: '2025-12-31T18:00:00Z'
  },
  {
    id: '5',
    entry_number: 'JV-2025-155',
    date: '2025-12-28',
    reference: 'REV-001',
    narration: 'Reversal of incorrect entry',
    total_debit: 75000,
    total_credit: 75000,
    status: 'reversed',
    created_by: 'Admin',
    created_at: '2025-12-28T11:30:00Z'
  },
]

export default function JournalEntriesPage() {
  const [entries, setEntries] = React.useState<JournalEntry[]>(mockJournalEntries)
  const [searchQuery, setSearchQuery] = React.useState('')
  const [statusFilter, setStatusFilter] = React.useState<string>('all')
  const [isLoading, setIsLoading] = React.useState(false)
  const api = useApi()

  const filteredEntries = React.useMemo(() => {
    return entries.filter(entry => {
      const matchesSearch = !searchQuery ||
        entry.entry_number.toLowerCase().includes(searchQuery.toLowerCase()) ||
        entry.narration.toLowerCase().includes(searchQuery.toLowerCase()) ||
        entry.reference.toLowerCase().includes(searchQuery.toLowerCase())

      const matchesStatus = statusFilter === 'all' || entry.status === statusFilter

      return matchesSearch && matchesStatus
    })
  }, [entries, searchQuery, statusFilter])

  const getStatusBadge = (status: string) => {
    const statusConfig: Record<string, { label: string; className: string }> = {
      draft: { label: 'Draft', className: 'bg-yellow-100 text-yellow-800' },
      posted: { label: 'Posted', className: 'bg-green-100 text-green-800' },
      reversed: { label: 'Reversed', className: 'bg-red-100 text-red-800' }
    }
    const config = statusConfig[status] || statusConfig.draft
    return <Badge className={config.className}>{config.label}</Badge>
  }

  const totalDebit = filteredEntries.reduce((sum, e) => sum + e.total_debit, 0)
  const totalCredit = filteredEntries.reduce((sum, e) => sum + e.total_credit, 0)

  return (
    <div className="space-y-6">
      <PageHeader
        title="Journal Entries"
        description="Create and manage accounting journal entries"
        breadcrumbs={[
          { label: 'Dashboard', href: '/' },
          { label: 'Finance', href: '/accounts' },
          { label: 'Journal Entries' }
        ]}
        actions={
          <div className="flex items-center gap-2">
            <Button variant="outline">
              <Download className="h-4 w-4 mr-2" />
              Export
            </Button>
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              New Entry
            </Button>
          </div>
        }
      />

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-blue-100 rounded-full">
                <FileText className="h-6 w-6 text-blue-600" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Total Entries</p>
                <p className="text-2xl font-bold">{entries.length}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-green-100 rounded-full">
                <ArrowUpRight className="h-6 w-6 text-green-600" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Total Debit</p>
                <p className="text-2xl font-bold text-green-600">{formatCurrency(totalDebit)}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-red-100 rounded-full">
                <ArrowDownRight className="h-6 w-6 text-red-600" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Total Credit</p>
                <p className="text-2xl font-bold text-red-600">{formatCurrency(totalCredit)}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-yellow-100 rounded-full">
                <Calendar className="h-6 w-6 text-yellow-600" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Draft Entries</p>
                <p className="text-2xl font-bold text-yellow-600">
                  {entries.filter(e => e.status === 'draft').length}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col sm:flex-row gap-4 items-center justify-between">
            <div className="relative w-full sm:w-64">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search entries..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
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
                variant={statusFilter === 'draft' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setStatusFilter('draft')}
              >
                Draft
              </Button>
              <Button
                variant={statusFilter === 'posted' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setStatusFilter('posted')}
              >
                Posted
              </Button>
              <Button
                variant={statusFilter === 'reversed' ? 'default' : 'outline'}
                size="sm"
                onClick={() => setStatusFilter('reversed')}
              >
                Reversed
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Journal Entries Table */}
      <Card>
        <CardHeader>
          <CardTitle>Journal Entries</CardTitle>
          <CardDescription>
            {filteredEntries.length} entries found
          </CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex items-center justify-center h-64">
              <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b">
                    <th className="text-left py-3 px-4 font-medium text-muted-foreground">Entry #</th>
                    <th className="text-left py-3 px-4 font-medium text-muted-foreground">Date</th>
                    <th className="text-left py-3 px-4 font-medium text-muted-foreground">Reference</th>
                    <th className="text-left py-3 px-4 font-medium text-muted-foreground">Narration</th>
                    <th className="text-right py-3 px-4 font-medium text-muted-foreground">Debit</th>
                    <th className="text-right py-3 px-4 font-medium text-muted-foreground">Credit</th>
                    <th className="text-center py-3 px-4 font-medium text-muted-foreground">Status</th>
                    <th className="text-center py-3 px-4 font-medium text-muted-foreground">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredEntries.map((entry) => (
                    <tr key={entry.id} className="border-b hover:bg-muted/50">
                      <td className="py-3 px-4">
                        <span className="font-mono text-sm font-medium">{entry.entry_number}</span>
                      </td>
                      <td className="py-3 px-4 text-sm">
                        {formatDate(entry.date)}
                      </td>
                      <td className="py-3 px-4 text-sm text-muted-foreground">
                        {entry.reference}
                      </td>
                      <td className="py-3 px-4 text-sm max-w-[300px] truncate">
                        {entry.narration}
                      </td>
                      <td className="py-3 px-4 text-right font-mono text-sm">
                        {formatCurrency(entry.total_debit)}
                      </td>
                      <td className="py-3 px-4 text-right font-mono text-sm">
                        {formatCurrency(entry.total_credit)}
                      </td>
                      <td className="py-3 px-4 text-center">
                        {getStatusBadge(entry.status)}
                      </td>
                      <td className="py-3 px-4 text-center">
                        <Button variant="ghost" size="icon">
                          <Eye className="h-4 w-4" />
                        </Button>
                      </td>
                    </tr>
                  ))}
                  {filteredEntries.length === 0 && (
                    <tr>
                      <td colSpan={8} className="py-8 text-center text-muted-foreground">
                        No journal entries found
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
