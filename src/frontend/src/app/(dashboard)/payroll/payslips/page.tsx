'use client'

import * as React from 'react'
import Link from 'next/link'
import { useSearchParams } from 'next/navigation'
import { PageHeader } from '@/components/layout/page-header'
import { DataTable, Column } from '@/components/layout/data-table'
import { SearchInput } from '@/components/forms/search-input'
import { MonthYearPicker } from '@/components/forms/date-picker'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { formatCurrency, getMonthName } from '@/lib/format'
import {
  Download,
  Mail,
  Eye,
  FileText,
  Users,
  CheckCircle,
  Clock,
  Send,
  Loader2
} from 'lucide-react'

// ============================================================================
// Types
// ============================================================================

interface PayslipListItem {
  id: string
  employee_id: string
  employee_name: string
  employee_code: string
  department: string
  designation: string
  gross_salary: number
  total_deductions: number
  net_salary: number
  status: 'generated' | 'emailed' | 'downloaded'
  generated_at: string
}

// ============================================================================
// Mock Data
// ============================================================================

const mockPayslips: PayslipListItem[] = [
  {
    id: '1',
    employee_id: '1',
    employee_name: 'Rahul Kumar',
    employee_code: 'EMP001',
    department: 'Engineering',
    designation: 'Senior Developer',
    gross_salary: 80000,
    total_deductions: 17200,
    net_salary: 62800,
    status: 'emailed',
    generated_at: '2026-01-02T10:00:00Z'
  },
  {
    id: '2',
    employee_id: '2',
    employee_name: 'Priya Sharma',
    employee_code: 'EMP002',
    department: 'Engineering',
    designation: 'Tech Lead',
    gross_salary: 100000,
    total_deductions: 23500,
    net_salary: 76500,
    status: 'emailed',
    generated_at: '2026-01-02T10:00:00Z'
  },
  {
    id: '3',
    employee_id: '3',
    employee_name: 'Amit Patel',
    employee_code: 'EMP003',
    department: 'Sales',
    designation: 'Sales Executive',
    gross_salary: 50000,
    total_deductions: 9800,
    net_salary: 40200,
    status: 'generated',
    generated_at: '2026-01-02T10:00:00Z'
  },
  {
    id: '4',
    employee_id: '4',
    employee_name: 'Sneha Reddy',
    employee_code: 'EMP004',
    department: 'HR',
    designation: 'HR Manager',
    gross_salary: 70000,
    total_deductions: 14200,
    net_salary: 55800,
    status: 'downloaded',
    generated_at: '2026-01-02T10:00:00Z'
  },
  {
    id: '5',
    employee_id: '5',
    employee_name: 'Vikram Singh',
    employee_code: 'EMP005',
    department: 'Finance',
    designation: 'Accountant',
    gross_salary: 60000,
    total_deductions: 11600,
    net_salary: 48400,
    status: 'generated',
    generated_at: '2026-01-02T10:00:00Z'
  },
  {
    id: '6',
    employee_id: '6',
    employee_name: 'Neha Gupta',
    employee_code: 'EMP006',
    department: 'Engineering',
    designation: 'Developer',
    gross_salary: 65000,
    total_deductions: 12800,
    net_salary: 52200,
    status: 'emailed',
    generated_at: '2026-01-02T10:00:00Z'
  },
  {
    id: '7',
    employee_id: '7',
    employee_name: 'Kiran Desai',
    employee_code: 'EMP007',
    department: 'Marketing',
    designation: 'Marketing Manager',
    gross_salary: 75000,
    total_deductions: 15400,
    net_salary: 59600,
    status: 'generated',
    generated_at: '2026-01-02T10:00:00Z'
  },
  {
    id: '8',
    employee_id: '8',
    employee_name: 'Arjun Mehta',
    employee_code: 'EMP008',
    department: 'Engineering',
    designation: 'Senior Developer',
    gross_salary: 85000,
    total_deductions: 18400,
    net_salary: 66600,
    status: 'downloaded',
    generated_at: '2026-01-02T10:00:00Z'
  }
]

// ============================================================================
// Component
// ============================================================================

export default function PayslipsPage() {
  const searchParams = useSearchParams()
  const currentDate = new Date()

  // Get month/year from URL params or use current
  const initialMonth = searchParams.get('month') ? parseInt(searchParams.get('month')!) : currentDate.getMonth() + 1
  const initialYear = searchParams.get('year') ? parseInt(searchParams.get('year')!) : currentDate.getFullYear()

  const [selectedMonth, setSelectedMonth] = React.useState(initialMonth)
  const [selectedYear, setSelectedYear] = React.useState(initialYear)
  const [searchQuery, setSearchQuery] = React.useState('')
  const [selectedPayslips, setSelectedPayslips] = React.useState<string[]>([])
  const [isEmailDialogOpen, setIsEmailDialogOpen] = React.useState(false)
  const [isSendingEmails, setIsSendingEmails] = React.useState(false)
  const [isDownloading, setIsDownloading] = React.useState(false)

  // Filter payslips
  const filteredPayslips = mockPayslips.filter(payslip =>
    payslip.employee_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    payslip.employee_code.toLowerCase().includes(searchQuery.toLowerCase()) ||
    payslip.department.toLowerCase().includes(searchQuery.toLowerCase())
  )

  // Calculate stats
  const stats = {
    total: filteredPayslips.length,
    emailed: filteredPayslips.filter(p => p.status === 'emailed').length,
    downloaded: filteredPayslips.filter(p => p.status === 'downloaded').length,
    pending: filteredPayslips.filter(p => p.status === 'generated').length
  }

  // Handle select all
  const handleSelectAll = () => {
    if (selectedPayslips.length === filteredPayslips.length) {
      setSelectedPayslips([])
    } else {
      setSelectedPayslips(filteredPayslips.map(p => p.id))
    }
  }

  // Handle individual select
  const handleSelect = (id: string) => {
    if (selectedPayslips.includes(id)) {
      setSelectedPayslips(selectedPayslips.filter(p => p !== id))
    } else {
      setSelectedPayslips([...selectedPayslips, id])
    }
  }

  // Handle bulk email
  const handleBulkEmail = async () => {
    setIsSendingEmails(true)
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 2000))
    setIsSendingEmails(false)
    setIsEmailDialogOpen(false)
    setSelectedPayslips([])
  }

  // Handle bulk download
  const handleBulkDownload = async () => {
    setIsDownloading(true)
    // Simulate download
    await new Promise(resolve => setTimeout(resolve, 1500))
    setIsDownloading(false)
  }

  // Status badge helper
  const getStatusBadge = (status: PayslipListItem['status']) => {
    const config = {
      generated: { label: 'Generated', className: 'bg-blue-100 text-blue-800', icon: FileText },
      emailed: { label: 'Emailed', className: 'bg-green-100 text-green-800', icon: CheckCircle },
      downloaded: { label: 'Downloaded', className: 'bg-purple-100 text-purple-800', icon: Download }
    }

    const { label, className, icon: Icon } = config[status]

    return (
      <Badge className={className}>
        <Icon className="h-3 w-3 mr-1" />
        {label}
      </Badge>
    )
  }

  // Table columns
  const columns: Column<PayslipListItem>[] = [
    {
      key: 'select',
      header: () => (
        <input
          type="checkbox"
          checked={selectedPayslips.length === filteredPayslips.length && filteredPayslips.length > 0}
          onChange={handleSelectAll}
          className="h-4 w-4 rounded border-gray-300"
        />
      ),
      accessor: (row) => (
        <input
          type="checkbox"
          checked={selectedPayslips.includes(row.id)}
          onChange={() => handleSelect(row.id)}
          className="h-4 w-4 rounded border-gray-300"
        />
      )
    },
    {
      key: 'employee',
      header: 'Employee',
      accessor: (row) => (
        <div>
          <p className="font-medium">{row.employee_name}</p>
          <p className="text-sm text-muted-foreground">{row.employee_code}</p>
        </div>
      )
    },
    {
      key: 'department',
      header: 'Department',
      accessor: (row) => (
        <div>
          <p>{row.department}</p>
          <p className="text-sm text-muted-foreground">{row.designation}</p>
        </div>
      )
    },
    {
      key: 'gross',
      header: 'Gross',
      className: 'text-right',
      headerClassName: 'text-right',
      accessor: (row) => formatCurrency(row.gross_salary)
    },
    {
      key: 'deductions',
      header: 'Deductions',
      className: 'text-right',
      headerClassName: 'text-right',
      accessor: (row) => (
        <span className="text-red-600">-{formatCurrency(row.total_deductions)}</span>
      )
    },
    {
      key: 'net',
      header: 'Net Pay',
      className: 'text-right font-medium',
      headerClassName: 'text-right',
      accessor: (row) => (
        <span className="text-green-600">{formatCurrency(row.net_salary)}</span>
      )
    },
    {
      key: 'status',
      header: 'Status',
      accessor: (row) => getStatusBadge(row.status)
    },
    {
      key: 'actions',
      header: '',
      accessor: (row) => (
        <div className="flex items-center gap-1">
          <Button variant="ghost" size="sm" asChild>
            <Link href={`/payroll/payslips/${row.id}`}>
              <Eye className="h-4 w-4" />
            </Link>
          </Button>
          <Button variant="ghost" size="sm">
            <Download className="h-4 w-4" />
          </Button>
          <Button variant="ghost" size="sm">
            <Mail className="h-4 w-4" />
          </Button>
        </div>
      )
    }
  ]

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <PageHeader
        title="Payslips"
        description="View and manage employee payslips"
        breadcrumbs={[
          { label: 'Dashboard', href: '/dashboard' },
          { label: 'Payroll', href: '/payroll' },
          { label: 'Payslips' }
        ]}
        actions={
          <div className="flex items-center gap-2">
            {selectedPayslips.length > 0 && (
              <>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleBulkDownload}
                  disabled={isDownloading}
                >
                  {isDownloading ? (
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  ) : (
                    <Download className="h-4 w-4 mr-2" />
                  )}
                  Download ({selectedPayslips.length})
                </Button>
                <Button
                  size="sm"
                  onClick={() => setIsEmailDialogOpen(true)}
                >
                  <Send className="h-4 w-4 mr-2" />
                  Email ({selectedPayslips.length})
                </Button>
              </>
            )}
          </div>
        }
      />

      {/* Filters & Stats */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
        {/* Period Selector */}
        <Card className="lg:col-span-2">
          <CardContent className="pt-4">
            <MonthYearPicker
              label="Select Period"
              name="payslip-period"
              month={selectedMonth}
              year={selectedYear}
              onMonthChange={setSelectedMonth}
              onYearChange={setSelectedYear}
            />
          </CardContent>
        </Card>

        {/* Stats */}
        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-full bg-blue-100 flex items-center justify-center">
                <Users className="h-5 w-5 text-blue-600" />
              </div>
              <div>
                <p className="text-2xl font-bold">{stats.total}</p>
                <p className="text-sm text-muted-foreground">Total Payslips</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <CheckCircle className="h-4 w-4 text-green-500" />
                <span className="text-sm">Emailed: {stats.emailed}</span>
              </div>
              <div className="flex items-center gap-2">
                <Clock className="h-4 w-4 text-yellow-500" />
                <span className="text-sm">Pending: {stats.pending}</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Search & Table */}
      <Card>
        <CardHeader>
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div>
              <CardTitle>Payslips - {getMonthName(selectedMonth)} {selectedYear}</CardTitle>
              <CardDescription>
                {stats.total} payslips generated
              </CardDescription>
            </div>
            <SearchInput
              placeholder="Search employees..."
              value={searchQuery}
              onChange={setSearchQuery}
              className="w-full md:w-64"
            />
          </div>
        </CardHeader>
        <CardContent>
          <DataTable
            data={filteredPayslips}
            columns={columns}
            keyExtractor={(row) => row.id}
          />
        </CardContent>
      </Card>

      {/* Email Confirmation Dialog */}
      <Dialog open={isEmailDialogOpen} onOpenChange={setIsEmailDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Email Payslips</DialogTitle>
            <DialogDescription>
              Are you sure you want to email payslips to {selectedPayslips.length} employees?
            </DialogDescription>
          </DialogHeader>
          <div className="py-4">
            <p className="text-sm text-muted-foreground">
              Payslips will be sent to the registered email addresses of the selected employees.
            </p>
          </div>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setIsEmailDialogOpen(false)}
              disabled={isSendingEmails}
            >
              Cancel
            </Button>
            <Button
              onClick={handleBulkEmail}
              disabled={isSendingEmails}
            >
              {isSendingEmails ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Sending...
                </>
              ) : (
                <>
                  <Send className="h-4 w-4 mr-2" />
                  Send Emails
                </>
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
