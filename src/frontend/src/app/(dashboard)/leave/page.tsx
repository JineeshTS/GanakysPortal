'use client'

import * as React from 'react'
import Link from 'next/link'
import { PageHeader } from '@/components/layout/page-header'
import { DataTable, Column } from '@/components/layout/data-table'
import { StatsGrid } from '@/components/layout/stat-card'
import { LeaveBalanceGrid, MiniLeaveCalendar } from '@/components/leave'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { formatDate, getFinancialYear } from '@/lib/format'
import { useApi } from '@/hooks'
import {
  Calendar,
  CheckCircle,
  XCircle,
  Clock,
  Plus,
  CalendarDays,
  Sun,
  Umbrella,
  Heart,
  Star,
  Users,
  ArrowRight,
  FileText,
  Loader2
} from 'lucide-react'
import type { LeaveRequest, LeaveStatus, LeaveBalance } from '@/types'

// API Response types
interface LeaveBalanceApiResponse {
  employee_id: string
  employee_name: string
  financial_year: string
  balances: {
    leave_type_id: string
    leave_type_code: string
    leave_type_name: string
    color_code: string
    entitled: string
    used: string
    pending: string
    available: string
    is_encashable: boolean
    is_carry_forward: boolean
  }[]
}

interface HolidayApiResponse {
  data: {
    id: string
    name: string
    holiday_date: string
    is_mandatory: boolean
  }[]
  total: number
}

// ============================================================================
// Mock Data
// ============================================================================

// Mock leave requests
const mockLeaveRequests: LeaveRequest[] = [
  {
    id: '1',
    employee_id: '1',
    employee_name: 'Rajesh Kumar',
    leave_type_code: 'CL',
    leave_type_name: 'Casual Leave',
    from_date: '2026-01-10',
    to_date: '2026-01-10',
    days: 1,
    half_day: false,
    reason: 'Personal work',
    status: 'pending',
    applied_on: '2026-01-06T10:30:00Z',
    created_at: '2026-01-06T10:30:00Z',
    updated_at: '2026-01-06T10:30:00Z'
  },
  {
    id: '2',
    employee_id: '2',
    employee_name: 'Priya Sharma',
    leave_type_code: 'SL',
    leave_type_name: 'Sick Leave',
    from_date: '2026-01-08',
    to_date: '2026-01-09',
    days: 2,
    half_day: false,
    reason: 'Not feeling well',
    status: 'approved',
    applied_on: '2026-01-05T09:00:00Z',
    approver_id: 'admin',
    approver_name: 'Admin',
    approved_on: '2026-01-05T14:00:00Z',
    created_at: '2026-01-05T09:00:00Z',
    updated_at: '2026-01-05T14:00:00Z'
  },
  {
    id: '3',
    employee_id: '3',
    employee_name: 'Amit Patel',
    leave_type_code: 'EL',
    leave_type_name: 'Earned Leave',
    from_date: '2026-01-20',
    to_date: '2026-01-24',
    days: 5,
    half_day: false,
    reason: 'Family vacation',
    status: 'pending',
    applied_on: '2026-01-04T11:00:00Z',
    created_at: '2026-01-04T11:00:00Z',
    updated_at: '2026-01-04T11:00:00Z'
  },
  {
    id: '4',
    employee_id: '4',
    employee_name: 'Sneha Reddy',
    leave_type_code: 'CL',
    leave_type_name: 'Casual Leave',
    from_date: '2026-01-03',
    to_date: '2026-01-03',
    days: 0.5,
    half_day: true,
    half_day_type: 'first_half',
    reason: 'Doctor appointment',
    status: 'rejected',
    applied_on: '2026-01-02T16:00:00Z',
    approver_id: 'admin',
    approver_name: 'Admin',
    approved_on: '2026-01-02T17:00:00Z',
    rejection_reason: 'Please provide medical certificate',
    created_at: '2026-01-02T16:00:00Z',
    updated_at: '2026-01-02T17:00:00Z'
  }
]

// Mock leave balances (current user)
const mockLeaveBalances: LeaveBalance[] = [
  { employee_id: '1', leave_type_code: 'CL', leave_type_name: 'Casual Leave', year: 2026, opening_balance: 12, credited: 0, used: 2, lapsed: 0, available: 10, pending_approval: 1 },
  { employee_id: '1', leave_type_code: 'SL', leave_type_name: 'Sick Leave', year: 2026, opening_balance: 12, credited: 0, used: 0, lapsed: 0, available: 12, pending_approval: 0 },
  { employee_id: '1', leave_type_code: 'EL', leave_type_name: 'Earned Leave', year: 2026, opening_balance: 10, credited: 1.25, used: 0, lapsed: 0, available: 11.25, pending_approval: 0 },
  { employee_id: '1', leave_type_code: 'LWP', leave_type_name: 'Leave Without Pay', year: 2026, opening_balance: 0, credited: 0, used: 0, lapsed: 0, available: 0, pending_approval: 0 }
]

// Mock holidays for current month
const mockHolidays = [
  { date: '2026-01-14', name: 'Makar Sankranti', type: 'national' as const },
  { date: '2026-01-26', name: 'Republic Day', type: 'national' as const }
]

// Team members on leave today
const mockTeamOnLeave = [
  { id: '2', name: 'Priya Sharma', leave_type: 'SL', from: '2026-01-08', to: '2026-01-09' },
  { id: '5', name: 'Vikram Singh', leave_type: 'EL', from: '2026-01-06', to: '2026-01-08' }
]

// Stats
const leaveStats = {
  pendingRequests: 5,
  onLeaveToday: 3,
  upcomingLeaves: 8,
  approvedThisMonth: 12
}

// ============================================================================
// Leave Dashboard Page
// ============================================================================

export default function LeavePage() {
  const [requests, setRequests] = React.useState(mockLeaveRequests)
  const [statusFilter, setStatusFilter] = React.useState<string>('all')
  const [leaveBalances, setLeaveBalances] = React.useState<LeaveBalance[]>(mockLeaveBalances)
  const [holidays, setHolidays] = React.useState(mockHolidays)
  const [isLoading, setIsLoading] = React.useState(true)
  const isManager = true // Mock - would come from auth context

  const balanceApi = useApi<LeaveBalanceApiResponse>()
  const holidayApi = useApi<HolidayApiResponse>()

  // Fetch data from API
  React.useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true)
      try {
        // Fetch leave balance
        const balanceResult = await balanceApi.get('/leave/balance')
        if (balanceResult && balanceResult.balances) {
          const mappedBalances: LeaveBalance[] = balanceResult.balances.map(b => ({
            employee_id: balanceResult.employee_id,
            leave_type_code: b.leave_type_code,
            leave_type_name: b.leave_type_name,
            year: parseInt(balanceResult.financial_year.split('-')[0]),
            opening_balance: parseFloat(b.entitled),
            credited: 0,
            used: parseFloat(b.used),
            lapsed: 0,
            available: parseFloat(b.available),
            pending_approval: parseFloat(b.pending)
          }))
          setLeaveBalances(mappedBalances)
        }

        // Fetch holidays
        const holidayResult = await holidayApi.get('/leave/holidays')
        if (holidayResult && holidayResult.data) {
          const mappedHolidays = holidayResult.data.map(h => ({
            date: h.holiday_date,
            name: h.name,
            type: h.is_mandatory ? 'national' as const : 'optional' as const
          }))
          setHolidays(mappedHolidays)
        }
      } catch (error) {
        console.error('Failed to fetch leave data:', error)
      } finally {
        setIsLoading(false)
      }
    }

    fetchData()
  }, [])

  const filteredRequests = React.useMemo(() => {
    if (statusFilter === 'all') return requests
    return requests.filter(r => r.status === statusFilter)
  }, [requests, statusFilter])

  const recentRequests = React.useMemo(() => {
    return [...requests]
      .sort((a, b) => new Date(b.applied_on).getTime() - new Date(a.applied_on).getTime())
      .slice(0, 5)
  }, [requests])

  const stats = [
    {
      title: 'Pending Requests',
      value: leaveStats.pendingRequests,
      icon: Clock,
      description: 'Awaiting approval',
      valueClassName: 'text-yellow-600'
    },
    {
      title: 'On Leave Today',
      value: leaveStats.onLeaveToday,
      icon: CalendarDays,
      description: 'Team members'
    },
    {
      title: 'Upcoming Leaves',
      value: leaveStats.upcomingLeaves,
      icon: Calendar,
      description: 'Next 7 days'
    },
    {
      title: 'Approved This Month',
      value: leaveStats.approvedThisMonth,
      icon: CheckCircle,
      description: 'January 2026',
      valueClassName: 'text-green-600'
    }
  ]

  const getStatusBadge = (status: LeaveStatus) => {
    const statusConfig = {
      pending: { label: 'Pending', className: 'bg-yellow-100 text-yellow-800' },
      approved: { label: 'Approved', className: 'bg-green-100 text-green-800' },
      rejected: { label: 'Rejected', className: 'bg-red-100 text-red-800' },
      cancelled: { label: 'Cancelled', className: 'bg-gray-100 text-gray-800' },
      partially_approved: { label: 'Partial', className: 'bg-blue-100 text-blue-800' }
    }

    const config = statusConfig[status] || statusConfig.pending
    return <Badge className={config.className}>{config.label}</Badge>
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

  const handleApprove = (id: string) => {
    setRequests(prev => prev.map(r =>
      r.id === id ? { ...r, status: 'approved' as LeaveStatus } : r
    ))
  }

  const handleReject = (id: string) => {
    setRequests(prev => prev.map(r =>
      r.id === id ? { ...r, status: 'rejected' as LeaveStatus } : r
    ))
  }

  const columns: Column<LeaveRequest>[] = [
    {
      key: 'employee',
      header: 'Employee',
      accessor: (row) => (
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-primary/10 rounded-full flex items-center justify-center">
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
      header: 'Leave Type',
      accessor: (row) => (
        <div className="flex items-center gap-2">
          {getLeaveTypeIcon(row.leave_type_code)}
          <span>{row.leave_type_name}</span>
        </div>
      )
    },
    {
      key: 'duration',
      header: 'Duration',
      accessor: (row) => (
        <div>
          <p>{formatDate(row.from_date)} - {formatDate(row.to_date)}</p>
          <p className="text-sm text-muted-foreground">
            {row.days} day{row.days !== 1 ? 's' : ''}
            {row.half_day && ` (${row.half_day_type === 'first_half' ? 'First Half' : 'Second Half'})`}
          </p>
        </div>
      )
    },
    {
      key: 'reason',
      header: 'Reason',
      accessor: (row) => (
        <p className="max-w-[200px] truncate" title={row.reason}>
          {row.reason}
        </p>
      )
    },
    {
      key: 'status',
      header: 'Status',
      accessor: (row) => getStatusBadge(row.status)
    },
    {
      key: 'applied_on',
      header: 'Applied On',
      accessor: (row) => formatDate(row.applied_on, { format: 'long' })
    },
    {
      key: 'actions',
      header: '',
      accessor: (row) => row.status === 'pending' ? (
        <div className="flex items-center gap-1">
          <Button
            variant="ghost"
            size="icon"
            className="text-green-600 hover:text-green-700 hover:bg-green-50"
            onClick={(e) => {
              e.stopPropagation()
              handleApprove(row.id)
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
              handleReject(row.id)
            }}
          >
            <XCircle className="h-4 w-4" />
          </Button>
        </div>
      ) : null
    }
  ]

  return (
    <div className="space-y-6">
      <PageHeader
        title="Leave Management"
        description={`${getFinancialYear()} - Manage leave requests and balances`}
        breadcrumbs={[
          { label: 'Dashboard', href: '/' },
          { label: 'Leave' }
        ]}
        actions={
          <div className="flex items-center gap-2">
            <Button variant="outline" asChild>
              <Link href="/leave/requests">
                <FileText className="h-4 w-4 mr-2" />
                View All Requests
              </Link>
            </Button>
            <Button variant="outline" asChild>
              <Link href="/leave/calendar">
                <CalendarDays className="h-4 w-4 mr-2" />
                Calendar
              </Link>
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

      {/* Stats */}
      <StatsGrid stats={stats} columns={4} />

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Leave Balances & Recent Requests */}
        <div className="lg:col-span-2 space-y-6">
          {/* Leave Balances */}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle className="text-lg">My Leave Balance</CardTitle>
                <CardDescription>{getFinancialYear()}</CardDescription>
              </div>
              <Button variant="ghost" size="sm" asChild>
                <Link href="/leave/balance">
                  View Details
                  <ArrowRight className="h-4 w-4 ml-1" />
                </Link>
              </Button>
            </CardHeader>
            <CardContent>
              <LeaveBalanceGrid
                balances={leaveBalances}
                compact
                columns={2}
              />
            </CardContent>
          </Card>

          {/* Recent Leave Requests */}
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle className="text-lg">Recent Leave Requests</CardTitle>
                <CardDescription>Latest leave applications</CardDescription>
              </div>
              <Button variant="ghost" size="sm" asChild>
                <Link href="/leave/requests">
                  View All
                  <ArrowRight className="h-4 w-4 ml-1" />
                </Link>
              </Button>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {recentRequests.map((request) => (
                  <div
                    key={request.id}
                    className="flex items-center justify-between p-3 rounded-lg border bg-card hover:bg-muted/50 transition-colors"
                  >
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 bg-primary/10 rounded-full flex items-center justify-center">
                        {getLeaveTypeIcon(request.leave_type_code)}
                      </div>
                      <div>
                        <p className="font-medium">{request.employee_name}</p>
                        <p className="text-sm text-muted-foreground">
                          {request.leave_type_name} - {request.days} day(s)
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      {getStatusBadge(request.status)}
                      <p className="text-xs text-muted-foreground mt-1">
                        {formatDate(request.from_date)}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Right Column - Calendar & Team on Leave */}
        <div className="space-y-6">
          {/* Mini Calendar */}
          <MiniLeaveCalendar
            leaves={mockLeaveRequests.filter(r => r.status === 'approved')}
            holidays={holidays}
          />

          {/* Upcoming Holidays */}
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <Star className="h-4 w-4 text-orange-500" />
                Upcoming Holidays
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {holidays.slice(0, 5).map((holiday, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between p-2 rounded bg-orange-50 border border-orange-100"
                  >
                    <div>
                      <p className="text-sm font-medium">{holiday.name}</p>
                      <p className="text-xs text-muted-foreground capitalize">{holiday.type}</p>
                    </div>
                    <Badge variant="outline" className="bg-white">
                      {formatDate(holiday.date)}
                    </Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Team on Leave Today (Manager View) */}
          {isManager && (
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium flex items-center gap-2">
                  <Users className="h-4 w-4 text-blue-500" />
                  Team on Leave Today
                </CardTitle>
              </CardHeader>
              <CardContent>
                {mockTeamOnLeave.length > 0 ? (
                  <div className="space-y-2">
                    {mockTeamOnLeave.map((member) => (
                      <div
                        key={member.id}
                        className="flex items-center justify-between p-2 rounded bg-blue-50 border border-blue-100"
                      >
                        <div className="flex items-center gap-2">
                          <div className="w-6 h-6 bg-blue-200 rounded-full flex items-center justify-center">
                            <span className="text-xs font-medium text-blue-800">
                              {member.name.split(' ').map(n => n[0]).join('')}
                            </span>
                          </div>
                          <span className="text-sm font-medium">{member.name}</span>
                        </div>
                        <Badge variant="outline" className="bg-white text-xs">
                          {member.leave_type}
                        </Badge>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-muted-foreground text-center py-2">
                    No team members on leave today
                  </p>
                )}
              </CardContent>
            </Card>
          )}
        </div>
      </div>

      {/* Leave Requests Table */}
      <Tabs defaultValue="requests" className="space-y-4">
        <TabsList>
          <TabsTrigger value="requests">Leave Requests</TabsTrigger>
          <TabsTrigger value="policies">Leave Policies</TabsTrigger>
        </TabsList>

        <TabsContent value="requests" className="space-y-4">
          {/* Filters */}
          <Card>
            <CardContent className="pt-6">
              <div className="flex flex-col sm:flex-row gap-4">
                <div className="flex gap-2 flex-wrap">
                  <Button
                    variant={statusFilter === 'all' ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => setStatusFilter('all')}
                  >
                    All
                  </Button>
                  <Button
                    variant={statusFilter === 'pending' ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => setStatusFilter('pending')}
                  >
                    <Clock className="h-3 w-3 mr-1" />
                    Pending ({requests.filter(r => r.status === 'pending').length})
                  </Button>
                  <Button
                    variant={statusFilter === 'approved' ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => setStatusFilter('approved')}
                  >
                    <CheckCircle className="h-3 w-3 mr-1" />
                    Approved
                  </Button>
                  <Button
                    variant={statusFilter === 'rejected' ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => setStatusFilter('rejected')}
                  >
                    <XCircle className="h-3 w-3 mr-1" />
                    Rejected
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Requests Table */}
          <DataTable
            data={filteredRequests}
            columns={columns}
            keyExtractor={(row) => row.id}
            emptyMessage="No leave requests found"
          />
        </TabsContent>

        <TabsContent value="policies" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {/* Casual Leave */}
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="flex items-center gap-2 text-base">
                  <Sun className="h-4 w-4 text-yellow-500" />
                  Casual Leave (CL)
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Annual Quota</span>
                    <span>12 days</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Carry Forward</span>
                    <span>None</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Max Continuous</span>
                    <span>3 days</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Notice Required</span>
                    <span>1 day</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Sick Leave */}
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="flex items-center gap-2 text-base">
                  <Heart className="h-4 w-4 text-red-500" />
                  Sick Leave (SL)
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Annual Quota</span>
                    <span>12 days</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Carry Forward</span>
                    <span>6 days</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Medical Cert</span>
                    <span>After 2 days</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Notice Required</span>
                    <span>None</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Earned Leave */}
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="flex items-center gap-2 text-base">
                  <Umbrella className="h-4 w-4 text-blue-500" />
                  Earned Leave (EL)
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Annual Quota</span>
                    <span>15 days</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Carry Forward</span>
                    <span>30 days max</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Encashment</span>
                    <span>Allowed</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">Notice Required</span>
                    <span>7 days</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}
