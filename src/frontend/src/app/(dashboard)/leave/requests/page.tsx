'use client'

import * as React from 'react'
import Link from 'next/link'
import { useSearchParams } from 'next/navigation'
import { PageHeader } from '@/components/layout/page-header'
import { DataTable, Column } from '@/components/layout/data-table'
import { SearchInput } from '@/components/forms/search-input'
import { DateRangePicker } from '@/components/forms/date-picker'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle
} from '@/components/ui/dialog'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue
} from '@/components/ui/select'
import { Label } from '@/components/ui/label'
import { formatDate, getFinancialYear } from '@/lib/format'
import { useApi, useToast } from '@/hooks'
import {
  Calendar,
  CheckCircle,
  XCircle,
  Clock,
  Plus,
  Filter,
  Download,
  Eye,
  Sun,
  Heart,
  Umbrella,
  AlertCircle,
  FileText,
  Loader2,
  MoreHorizontal,
  Ban
} from 'lucide-react'
import type { LeaveRequest, LeaveStatus } from '@/types'

// API Response types
interface LeaveRequestApiResponse {
  data: ApiLeaveRequest[]
  total: number
  meta: {
    page: number
    limit: number
    pages: number
  }
}

interface ApiLeaveRequest {
  id: string
  request_number: string
  employee_id: string
  leave_type_id: string
  from_date: string
  to_date: string
  from_day_type: string
  to_day_type: string
  total_days: string
  working_days: string
  reason: string
  status: string
  approver_id: string | null
  approved_at: string | null
  approver_remarks: string | null
  rejected_at: string | null
  rejection_reason: string | null
  cancelled_at: string | null
  cancellation_reason: string | null
  created_at: string
  updated_at: string
  submitted_at: string
  employee?: {
    id: string
    employee_code: string
    full_name: string
  }
  leave_type?: {
    code: string
    name: string
    color_code: string
  }
  approver?: {
    id: string
    employee_code: string
    full_name: string
  }
}

const leaveTypeOptions = [
  { value: 'all', label: 'All Types' },
  { value: 'CL', label: 'Casual Leave' },
  { value: 'SL', label: 'Sick Leave' },
  { value: 'EL', label: 'Earned Leave' },
  { value: 'LWP', label: 'Leave Without Pay' }
]

const statusOptions: { value: string; label: string }[] = [
  { value: 'all', label: 'All Status' },
  { value: 'pending', label: 'Pending' },
  { value: 'approved', label: 'Approved' },
  { value: 'rejected', label: 'Rejected' },
  { value: 'cancelled', label: 'Cancelled' }
]

// ============================================================================
// Leave Requests Page
// ============================================================================

export default function LeaveRequestsPage() {
  const searchParams = useSearchParams()
  const initialStatus = searchParams.get('status') || 'all'

  const [requests, setRequests] = React.useState<LeaveRequest[]>([])
  const [isLoading, setIsLoading] = React.useState(true)
  const [searchTerm, setSearchTerm] = React.useState('')
  const [statusFilter, setStatusFilter] = React.useState(initialStatus)
  const [leaveTypeFilter, setLeaveTypeFilter] = React.useState('all')
  const [dateRange, setDateRange] = React.useState<{ from: string; to: string }>({ from: '', to: '' })

  const [selectedRequest, setSelectedRequest] = React.useState<LeaveRequest | null>(null)
  const [showDetailDialog, setShowDetailDialog] = React.useState(false)
  const [showApproveDialog, setShowApproveDialog] = React.useState(false)
  const [showRejectDialog, setShowRejectDialog] = React.useState(false)
  const [rejectionReason, setRejectionReason] = React.useState('')
  const [isProcessing, setIsProcessing] = React.useState(false)

  const isManager = true // Mock - would come from auth context
  const { showToast } = useToast()
  const requestsApi = useApi<LeaveRequestApiResponse>()
  const approveApi = useApi()
  const rejectApi = useApi()

  // Fetch leave requests from API
  React.useEffect(() => {
    const fetchRequests = async () => {
      setIsLoading(true)
      try {
        const result = await requestsApi.get('/leave/requests?limit=100')
        if (result && result.data) {
          // Map API response to LeaveRequest type
          const mappedRequests: LeaveRequest[] = result.data.map((r: ApiLeaveRequest) => ({
            id: r.id,
            employee_id: r.employee_id,
            employee_name: r.employee?.full_name || 'Unknown',
            leave_type_code: r.leave_type?.code || '',
            leave_type_name: r.leave_type?.name || '',
            from_date: r.from_date,
            to_date: r.to_date,
            days: parseFloat(r.total_days),
            half_day: r.from_day_type !== 'full' || r.to_day_type !== 'full',
            half_day_type: r.from_day_type !== 'full' ? r.from_day_type as 'first_half' | 'second_half' : undefined,
            reason: r.reason,
            status: r.status as LeaveStatus,
            applied_on: r.submitted_at || r.created_at,
            approver_id: r.approver_id || undefined,
            approver_name: r.approver?.full_name,
            approved_on: r.approved_at || undefined,
            rejection_reason: r.rejection_reason || undefined,
            created_at: r.created_at,
            updated_at: r.updated_at
          }))
          setRequests(mappedRequests)
        }
      } catch (error) {
        showToast('error', 'Failed to fetch leave requests')
      } finally {
        setIsLoading(false)
      }
    }

    fetchRequests()
  }, [])

  // Filter requests
  const filteredRequests = React.useMemo(() => {
    return requests.filter(request => {
      // Search filter
      if (searchTerm) {
        const search = searchTerm.toLowerCase()
        if (!request.employee_name.toLowerCase().includes(search) &&
            !request.leave_type_name.toLowerCase().includes(search) &&
            !request.reason.toLowerCase().includes(search)) {
          return false
        }
      }

      // Status filter
      if (statusFilter !== 'all' && request.status !== statusFilter) {
        return false
      }

      // Leave type filter
      if (leaveTypeFilter !== 'all' && request.leave_type_code !== leaveTypeFilter) {
        return false
      }

      // Date range filter
      if (dateRange.from && new Date(request.from_date) < new Date(dateRange.from)) {
        return false
      }
      if (dateRange.to && new Date(request.to_date) > new Date(dateRange.to)) {
        return false
      }

      return true
    })
  }, [requests, searchTerm, statusFilter, leaveTypeFilter, dateRange])

  // Stats
  const stats = React.useMemo(() => ({
    total: requests.length,
    pending: requests.filter(r => r.status === 'pending').length,
    approved: requests.filter(r => r.status === 'approved').length,
    rejected: requests.filter(r => r.status === 'rejected').length
  }), [requests])

  const getStatusBadge = (status: LeaveStatus) => {
    const statusConfig = {
      pending: { label: 'Pending', className: 'bg-yellow-100 text-yellow-800 border-yellow-200' },
      approved: { label: 'Approved', className: 'bg-green-100 text-green-800 border-green-200' },
      rejected: { label: 'Rejected', className: 'bg-red-100 text-red-800 border-red-200' },
      cancelled: { label: 'Cancelled', className: 'bg-gray-100 text-gray-800 border-gray-200' },
      partially_approved: { label: 'Partial', className: 'bg-blue-100 text-blue-800 border-blue-200' }
    }

    const config = statusConfig[status] || statusConfig.pending
    return <Badge variant="outline" className={config.className}>{config.label}</Badge>
  }

  const getLeaveTypeIcon = (code: string) => {
    const icons: Record<string, React.ElementType> = {
      CL: Sun,
      SL: Heart,
      EL: Umbrella,
      default: Calendar
    }
    const Icon = icons[code] || icons.default
    return <Icon className="h-4 w-4" />
  }

  const handleApprove = async () => {
    if (!selectedRequest) return

    setIsProcessing(true)
    try {
      const result = await approveApi.post(`/leave/requests/${selectedRequest.id}/approve`, {
        remarks: 'Approved'
      })

      if (result) {
        setRequests(prev => prev.map(r =>
          r.id === selectedRequest.id
            ? { ...r, status: 'approved' as LeaveStatus, approver_name: 'Admin', approved_on: new Date().toISOString() }
            : r
        ))
        setShowApproveDialog(false)
        setSelectedRequest(null)
      }
    } catch (error) {
      showToast('error', 'Failed to approve leave request')
    } finally {
      setIsProcessing(false)
    }
  }

  const handleReject = async () => {
    if (!selectedRequest || !rejectionReason.trim()) return

    setIsProcessing(true)
    try {
      const result = await rejectApi.post(`/leave/requests/${selectedRequest.id}/reject`, {
        reason: rejectionReason
      })

      if (result) {
        setRequests(prev => prev.map(r =>
          r.id === selectedRequest.id
            ? {
                ...r,
                status: 'rejected' as LeaveStatus,
                approver_name: 'Admin',
                approved_on: new Date().toISOString(),
                rejection_reason: rejectionReason
              }
            : r
        ))
        setShowRejectDialog(false)
        setSelectedRequest(null)
        setRejectionReason('')
      }
    } catch (error) {
      showToast('error', 'Failed to reject leave request')
    } finally {
      setIsProcessing(false)
    }
  }

  const columns: Column<LeaveRequest>[] = [
    {
      key: 'employee',
      header: 'Employee',
      accessor: (row) => (
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-primary/10 rounded-full flex items-center justify-center flex-shrink-0">
            <span className="text-xs font-medium text-primary">
              {row.employee_name.split(' ').map(n => n[0]).join('')}
            </span>
          </div>
          <span className="font-medium">{row.employee_name}</span>
        </div>
      )
    },
    {
      key: 'leave_type',
      header: 'Type',
      accessor: (row) => (
        <div className="flex items-center gap-2">
          {getLeaveTypeIcon(row.leave_type_code)}
          <div>
            <span className="block">{row.leave_type_code}</span>
            <span className="text-xs text-muted-foreground">{row.leave_type_name}</span>
          </div>
        </div>
      )
    },
    {
      key: 'from_date',
      header: 'From',
      accessor: (row) => formatDate(row.from_date)
    },
    {
      key: 'to_date',
      header: 'To',
      accessor: (row) => formatDate(row.to_date)
    },
    {
      key: 'days',
      header: 'Days',
      accessor: (row) => (
        <div className="text-center">
          <span className="font-medium">{row.days}</span>
          {row.half_day && (
            <p className="text-xs text-muted-foreground">
              {row.half_day_type === 'first_half' ? '1st Half' : '2nd Half'}
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
      key: 'applied_on',
      header: 'Applied',
      accessor: (row) => (
        <span className="text-sm text-muted-foreground">
          {formatDate(row.applied_on, { format: 'short' })}
        </span>
      )
    },
    {
      key: 'actions',
      header: '',
      accessor: (row) => (
        <div className="flex items-center gap-1">
          <Button
            variant="ghost"
            size="icon"
            onClick={(e) => {
              e.stopPropagation()
              setSelectedRequest(row)
              setShowDetailDialog(true)
            }}
          >
            <Eye className="h-4 w-4" />
          </Button>

          {isManager && row.status === 'pending' && (
            <>
              <Button
                variant="ghost"
                size="icon"
                className="text-green-600 hover:text-green-700 hover:bg-green-50"
                onClick={(e) => {
                  e.stopPropagation()
                  setSelectedRequest(row)
                  setShowApproveDialog(true)
                }}
              >
                <CheckCircle className="h-4 w-4" />
              </Button>
              <Button
                variant="ghost"
                size="icon"
                className="text-red-600 hover:text-red-700 hover:bg-red-50"
                onClick={(e) => {
                  e.stopPropagation()
                  setSelectedRequest(row)
                  setShowRejectDialog(true)
                }}
              >
                <XCircle className="h-4 w-4" />
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
        title="Leave Requests"
        description={`${getFinancialYear()} - View and manage leave requests`}
        breadcrumbs={[
          { label: 'Dashboard', href: '/' },
          { label: 'Leave', href: '/leave' },
          { label: 'Requests' }
        ]}
        actions={
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm">
              <Download className="h-4 w-4 mr-2" />
              Export
            </Button>
            <Button asChild>
              <Link href="/leave/apply">
                <Plus className="h-4 w-4 mr-2" />
                Apply Leave
              </Link>
            </Button>
          </div>
        }
      />

      {/* Quick Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card className="cursor-pointer hover:bg-muted/50" onClick={() => setStatusFilter('all')}>
          <CardContent className="pt-4 pb-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-2xl font-bold">{stats.total}</p>
                <p className="text-sm text-muted-foreground">Total Requests</p>
              </div>
              <FileText className="h-8 w-8 text-muted-foreground/50" />
            </div>
          </CardContent>
        </Card>
        <Card className="cursor-pointer hover:bg-muted/50" onClick={() => setStatusFilter('pending')}>
          <CardContent className="pt-4 pb-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-2xl font-bold text-yellow-600">{stats.pending}</p>
                <p className="text-sm text-muted-foreground">Pending</p>
              </div>
              <Clock className="h-8 w-8 text-yellow-500/50" />
            </div>
          </CardContent>
        </Card>
        <Card className="cursor-pointer hover:bg-muted/50" onClick={() => setStatusFilter('approved')}>
          <CardContent className="pt-4 pb-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-2xl font-bold text-green-600">{stats.approved}</p>
                <p className="text-sm text-muted-foreground">Approved</p>
              </div>
              <CheckCircle className="h-8 w-8 text-green-500/50" />
            </div>
          </CardContent>
        </Card>
        <Card className="cursor-pointer hover:bg-muted/50" onClick={() => setStatusFilter('rejected')}>
          <CardContent className="pt-4 pb-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-2xl font-bold text-red-600">{stats.rejected}</p>
                <p className="text-sm text-muted-foreground">Rejected</p>
              </div>
              <XCircle className="h-8 w-8 text-red-500/50" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col lg:flex-row gap-4">
            {/* Search */}
            <div className="flex-1">
              <SearchInput
                placeholder="Search by employee name, leave type, or reason..."
                value={searchTerm}
                onChange={setSearchTerm}
              />
            </div>

            {/* Status Filter */}
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-[150px]">
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                {statusOptions.map((option) => (
                  <SelectItem key={option.value} value={option.value}>
                    {option.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            {/* Leave Type Filter */}
            <Select value={leaveTypeFilter} onValueChange={setLeaveTypeFilter}>
              <SelectTrigger className="w-[150px]">
                <SelectValue placeholder="Leave Type" />
              </SelectTrigger>
              <SelectContent>
                {leaveTypeOptions.map((option) => (
                  <SelectItem key={option.value} value={option.value}>
                    {option.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            {/* Date Range */}
            <div className="flex items-center gap-2">
              <input
                type="date"
                value={dateRange.from}
                onChange={(e) => setDateRange(prev => ({ ...prev, from: e.target.value }))}
                className="h-10 rounded-md border border-input bg-background px-3 py-2 text-sm"
                placeholder="From"
              />
              <span className="text-muted-foreground">to</span>
              <input
                type="date"
                value={dateRange.to}
                onChange={(e) => setDateRange(prev => ({ ...prev, to: e.target.value }))}
                className="h-10 rounded-md border border-input bg-background px-3 py-2 text-sm"
                placeholder="To"
              />
            </div>

            {/* Clear Filters */}
            {(searchTerm || statusFilter !== 'all' || leaveTypeFilter !== 'all' || dateRange.from || dateRange.to) && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => {
                  setSearchTerm('')
                  setStatusFilter('all')
                  setLeaveTypeFilter('all')
                  setDateRange({ from: '', to: '' })
                }}
              >
                Clear Filters
              </Button>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Table */}
      {isLoading ? (
        <Card>
          <CardContent className="flex items-center justify-center py-12">
            <div className="flex items-center gap-2 text-muted-foreground">
              <Loader2 className="h-5 w-5 animate-spin" />
              <span>Loading leave requests...</span>
            </div>
          </CardContent>
        </Card>
      ) : (
        <DataTable
          data={filteredRequests}
          columns={columns}
          keyExtractor={(row) => row.id}
          emptyMessage="No leave requests found matching your filters"
          onRowClick={(row) => {
            setSelectedRequest(row)
            setShowDetailDialog(true)
          }}
        />
      )}

      {/* Detail Dialog */}
      <Dialog open={showDetailDialog} onOpenChange={setShowDetailDialog}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              {selectedRequest && getLeaveTypeIcon(selectedRequest.leave_type_code)}
              Leave Request Details
            </DialogTitle>
          </DialogHeader>

          {selectedRequest && (
            <div className="space-y-4">
              {/* Employee Info */}
              <div className="flex items-center gap-3 p-3 bg-muted rounded-lg">
                <div className="w-10 h-10 bg-primary/10 rounded-full flex items-center justify-center">
                  <span className="text-sm font-medium text-primary">
                    {selectedRequest.employee_name.split(' ').map(n => n[0]).join('')}
                  </span>
                </div>
                <div>
                  <p className="font-medium">{selectedRequest.employee_name}</p>
                  <p className="text-sm text-muted-foreground">Employee ID: {selectedRequest.employee_id}</p>
                </div>
                {getStatusBadge(selectedRequest.status)}
              </div>

              {/* Leave Details */}
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="text-muted-foreground">Leave Type</p>
                  <p className="font-medium">{selectedRequest.leave_type_name}</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Duration</p>
                  <p className="font-medium">
                    {selectedRequest.days} day(s)
                    {selectedRequest.half_day && ` (${selectedRequest.half_day_type === 'first_half' ? 'First Half' : 'Second Half'})`}
                  </p>
                </div>
                <div>
                  <p className="text-muted-foreground">From Date</p>
                  <p className="font-medium">{formatDate(selectedRequest.from_date, { format: 'long' })}</p>
                </div>
                <div>
                  <p className="text-muted-foreground">To Date</p>
                  <p className="font-medium">{formatDate(selectedRequest.to_date, { format: 'long' })}</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Applied On</p>
                  <p className="font-medium">{formatDate(selectedRequest.applied_on, { format: 'long', showTime: true })}</p>
                </div>
                {selectedRequest.approved_on && (
                  <div>
                    <p className="text-muted-foreground">
                      {selectedRequest.status === 'approved' ? 'Approved On' : 'Responded On'}
                    </p>
                    <p className="font-medium">{formatDate(selectedRequest.approved_on, { format: 'long', showTime: true })}</p>
                  </div>
                )}
              </div>

              {/* Reason */}
              <div>
                <p className="text-sm text-muted-foreground mb-1">Reason</p>
                <p className="text-sm p-3 bg-muted rounded-lg">{selectedRequest.reason}</p>
              </div>

              {/* Rejection Reason */}
              {selectedRequest.rejection_reason && (
                <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
                  <p className="text-sm text-red-800 font-medium mb-1 flex items-center gap-1">
                    <AlertCircle className="h-4 w-4" />
                    Rejection Reason
                  </p>
                  <p className="text-sm text-red-700">{selectedRequest.rejection_reason}</p>
                </div>
              )}

              {/* Approver Info */}
              {selectedRequest.approver_name && (
                <div className="text-sm">
                  <p className="text-muted-foreground">
                    {selectedRequest.status === 'approved' ? 'Approved' : 'Reviewed'} by
                  </p>
                  <p className="font-medium">{selectedRequest.approver_name}</p>
                </div>
              )}
            </div>
          )}

          <DialogFooter>
            {selectedRequest?.status === 'pending' && isManager && (
              <>
                <Button
                  variant="outline"
                  onClick={() => {
                    setShowDetailDialog(false)
                    setShowRejectDialog(true)
                  }}
                  className="text-red-600 hover:text-red-700"
                >
                  <XCircle className="h-4 w-4 mr-2" />
                  Reject
                </Button>
                <Button
                  onClick={() => {
                    setShowDetailDialog(false)
                    setShowApproveDialog(true)
                  }}
                  className="bg-green-600 hover:bg-green-700"
                >
                  <CheckCircle className="h-4 w-4 mr-2" />
                  Approve
                </Button>
              </>
            )}
            {(!isManager || selectedRequest?.status !== 'pending') && (
              <Button variant="outline" onClick={() => setShowDetailDialog(false)}>
                Close
              </Button>
            )}
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Approve Confirmation Dialog */}
      <Dialog open={showApproveDialog} onOpenChange={setShowApproveDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Approve Leave Request</DialogTitle>
            <DialogDescription>
              Are you sure you want to approve this leave request?
            </DialogDescription>
          </DialogHeader>

          {selectedRequest && (
            <div className="py-4 space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Employee:</span>
                <span className="font-medium">{selectedRequest.employee_name}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Leave Type:</span>
                <span className="font-medium">{selectedRequest.leave_type_name}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Duration:</span>
                <span className="font-medium">
                  {formatDate(selectedRequest.from_date)} - {formatDate(selectedRequest.to_date)}
                  ({selectedRequest.days} days)
                </span>
              </div>
            </div>
          )}

          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setShowApproveDialog(false)}
              disabled={isProcessing}
            >
              Cancel
            </Button>
            <Button
              onClick={handleApprove}
              disabled={isProcessing}
              className="bg-green-600 hover:bg-green-700"
            >
              {isProcessing ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Approving...
                </>
              ) : (
                <>
                  <CheckCircle className="h-4 w-4 mr-2" />
                  Approve
                </>
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Reject Dialog */}
      <Dialog open={showRejectDialog} onOpenChange={setShowRejectDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Reject Leave Request</DialogTitle>
            <DialogDescription>
              Please provide a reason for rejecting this leave request.
            </DialogDescription>
          </DialogHeader>

          {selectedRequest && (
            <div className="space-y-4">
              <div className="py-2 space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Employee:</span>
                  <span className="font-medium">{selectedRequest.employee_name}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Leave Type:</span>
                  <span className="font-medium">{selectedRequest.leave_type_name}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Duration:</span>
                  <span className="font-medium">
                    {formatDate(selectedRequest.from_date)} - {formatDate(selectedRequest.to_date)}
                  </span>
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="rejection_reason">
                  Rejection Reason <span className="text-destructive">*</span>
                </Label>
                <textarea
                  id="rejection_reason"
                  value={rejectionReason}
                  onChange={(e) => setRejectionReason(e.target.value)}
                  placeholder="Please provide a reason for rejection..."
                  rows={3}
                  className="flex w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
                />
              </div>
            </div>
          )}

          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => {
                setShowRejectDialog(false)
                setRejectionReason('')
              }}
              disabled={isProcessing}
            >
              Cancel
            </Button>
            <Button
              onClick={handleReject}
              disabled={isProcessing || !rejectionReason.trim()}
              variant="destructive"
            >
              {isProcessing ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Rejecting...
                </>
              ) : (
                <>
                  <XCircle className="h-4 w-4 mr-2" />
                  Reject
                </>
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
