'use client'

import * as React from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { PageHeader } from '@/components/layout/page-header'
import { LeaveCalendar } from '@/components/leave'
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
import { formatDate, getFinancialYear, getMonthName } from '@/lib/format'
import { useApi, useToast } from '@/hooks'
import {
  Plus,
  Download,
  Star,
  Users,
  Calendar,
  Sun,
  Heart,
  Umbrella,
  Info,
  Loader2
} from 'lucide-react'
import type { LeaveRequest, LeaveStatus } from '@/types'

// API Response types
interface CalendarApiResponse {
  leaves: ApiCalendarLeave[]
  holidays: ApiHoliday[]
  date_range: {
    from: string
    to: string
  }
}

interface ApiCalendarLeave {
  id: string
  request_number: string
  employee_id: string
  employee_name: string
  leave_type_code: string
  leave_type_name: string
  from_date: string
  to_date: string
  total_days: number
  status: string
  color_code: string
}

interface ApiHoliday {
  id: string
  name: string
  holiday_date: string
  holiday_type: string
  is_optional: boolean
}

interface LeaveRequestApiResponse {
  data: ApiLeaveRequest[]
  total: number
}

interface ApiLeaveRequest {
  id: string
  request_number: string
  employee_id: string
  from_date: string
  to_date: string
  from_day_type: string
  to_day_type: string
  total_days: string
  reason: string
  status: string
  approved_at: string | null
  submitted_at: string
  created_at: string
  updated_at: string
  employee?: {
    id: string
    employee_code: string
    full_name: string
  }
  leave_type?: {
    code: string
    name: string
  }
  approver?: {
    id: string
    full_name: string
  }
}

// ============================================================================
// Leave Calendar Page
// ============================================================================

export default function LeaveCalendarPage() {
  const router = useRouter()
  const [selectedMember, setSelectedMember] = React.useState<string>('all')
  const [selectedLeave, setSelectedLeave] = React.useState<LeaveRequest | null>(null)
  const [showLeaveDialog, setShowLeaveDialog] = React.useState(false)
  const [isLoading, setIsLoading] = React.useState(true)
  const [leaveRequests, setLeaveRequests] = React.useState<LeaveRequest[]>([])
  const [holidays, setHolidays] = React.useState<{date: string, name: string, type: 'national' | 'optional' | 'state'}[]>([])
  const [teamMembers, setTeamMembers] = React.useState<{id: string, name: string}[]>([])

  const isManager = true // Mock - would come from auth context
  const { showToast } = useToast()
  const requestsApi = useApi<LeaveRequestApiResponse>()
  const holidaysApi = useApi()

  // Fetch leave requests and holidays from API
  React.useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true)
      try {
        // Fetch leave requests
        const requestsResult = await requestsApi.get('/leave/requests?limit=100')
        if (requestsResult && requestsResult.data) {
          const mappedRequests: LeaveRequest[] = requestsResult.data.map((r: ApiLeaveRequest) => ({
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
            approver_id: r.approver?.id,
            approver_name: r.approver?.full_name,
            approved_on: r.approved_at || undefined,
            created_at: r.created_at,
            updated_at: r.updated_at
          }))
          setLeaveRequests(mappedRequests)

          // Extract unique team members from leave requests
          const members = new Map<string, string>()
          requestsResult.data.forEach((r: ApiLeaveRequest) => {
            if (r.employee && r.employee.id) {
              members.set(r.employee.id, r.employee.full_name)
            }
          })
          setTeamMembers(Array.from(members).map(([id, name]) => ({ id, name })))
        }

        // Fetch holidays for current year
        const holidaysResult = await holidaysApi.get('/leave/holidays?year=2026')
        if (holidaysResult && holidaysResult.data) {
          const mappedHolidays = holidaysResult.data.map((h: ApiHoliday) => ({
            date: h.holiday_date,
            name: h.name,
            type: h.is_optional ? 'optional' as const : 'national' as const
          }))
          setHolidays(mappedHolidays)
        }
      } catch (error) {
        showToast('error', 'Failed to fetch calendar data')
      } finally {
        setIsLoading(false)
      }
    }

    fetchData()
  }, [])

  // Filter leaves by selected member
  const filteredLeaves = React.useMemo(() => {
    if (selectedMember === 'all') {
      return leaveRequests.filter(r => r.status === 'approved' || r.status === 'pending')
    }
    return leaveRequests.filter(
      r => r.employee_id === selectedMember && (r.status === 'approved' || r.status === 'pending')
    )
  }, [selectedMember, leaveRequests])

  const handleLeaveClick = (leave: LeaveRequest) => {
    setSelectedLeave(leave)
    setShowLeaveDialog(true)
  }

  const handleDateClick = (date: Date) => {
    // Navigate to leave application page with the selected date pre-filled
    const formattedDate = date.toISOString().split('T')[0]
    router.push(`/leave/apply?from_date=${formattedDate}&to_date=${formattedDate}`)
  }

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

  // Group holidays by month for the sidebar
  const upcomingHolidays = React.useMemo(() => {
    const today = new Date()
    return holidays
      .filter(h => new Date(h.date) >= today)
      .slice(0, 6)
  }, [holidays])

  // Get leaves for today and upcoming week
  const leavesToday = React.useMemo(() => {
    const today = new Date().toISOString().split('T')[0]
    return filteredLeaves.filter(l => l.from_date <= today && l.to_date >= today && l.status === 'approved')
  }, [filteredLeaves])

  return (
    <div className="space-y-6">
      <PageHeader
        title="Leave Calendar"
        description={`${getFinancialYear()} - Team leave overview and holidays`}
        breadcrumbs={[
          { label: 'Dashboard', href: '/' },
          { label: 'Leave', href: '/leave' },
          { label: 'Calendar' }
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

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Main Calendar */}
        <div className="lg:col-span-3">
          {isLoading ? (
            <Card>
              <CardContent className="flex items-center justify-center py-24">
                <div className="flex items-center gap-2 text-muted-foreground">
                  <Loader2 className="h-5 w-5 animate-spin" />
                  <span>Loading calendar data...</span>
                </div>
              </CardContent>
            </Card>
          ) : (
            <LeaveCalendar
              leaves={filteredLeaves}
              holidays={holidays}
              teamMembers={isManager ? teamMembers : undefined}
              selectedMember={selectedMember}
              onMemberChange={setSelectedMember}
              onDateClick={handleDateClick}
              onLeaveClick={handleLeaveClick}
            />
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* On Leave Today */}
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <Users className="h-4 w-4 text-blue-500" />
                On Leave Today
              </CardTitle>
            </CardHeader>
            <CardContent>
              {leavesToday.length > 0 ? (
                <div className="space-y-2">
                  {leavesToday.map((leave) => (
                    <div
                      key={leave.id}
                      className="flex items-center justify-between p-2 rounded bg-blue-50 border border-blue-100 cursor-pointer hover:bg-blue-100"
                      onClick={() => handleLeaveClick(leave)}
                    >
                      <div className="flex items-center gap-2">
                        <div className="w-6 h-6 bg-blue-200 rounded-full flex items-center justify-center">
                          <span className="text-xs font-medium text-blue-800">
                            {leave.employee_name.split(' ').map(n => n[0]).join('')}
                          </span>
                        </div>
                        <span className="text-sm font-medium">{leave.employee_name}</span>
                      </div>
                      <Badge variant="outline" className="bg-white text-xs">
                        {leave.leave_type_code}
                      </Badge>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-muted-foreground text-center py-4">
                  No team members on leave today
                </p>
              )}
            </CardContent>
          </Card>

          {/* Upcoming Holidays */}
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <Star className="h-4 w-4 text-orange-500" />
                Upcoming Holidays
              </CardTitle>
              <CardDescription>National & Optional Holidays</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {upcomingHolidays.map((holiday, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between p-2 rounded bg-orange-50 border border-orange-100"
                  >
                    <div>
                      <p className="text-sm font-medium">{holiday.name}</p>
                      <p className="text-xs text-muted-foreground capitalize">{holiday.type}</p>
                    </div>
                    <Badge variant="outline" className="bg-white text-xs">
                      {formatDate(holiday.date)}
                    </Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Leave Type Legend */}
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <Info className="h-4 w-4 text-gray-500" />
                Legend
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 rounded bg-yellow-100 border border-yellow-300" />
                  <span className="text-sm">Casual Leave (CL)</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 rounded bg-red-100 border border-red-300" />
                  <span className="text-sm">Sick Leave (SL)</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 rounded bg-blue-100 border border-blue-300" />
                  <span className="text-sm">Earned Leave (EL)</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 rounded bg-orange-100 border border-orange-300" />
                  <span className="text-sm">Holiday</span>
                </div>

                <div className="pt-2 border-t mt-2">
                  <p className="text-xs text-muted-foreground mb-2">Status Indicators:</p>
                  <div className="flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-green-500" />
                    <span className="text-xs">Approved</span>
                  </div>
                  <div className="flex items-center gap-2 mt-1">
                    <span className="w-2 h-2 rounded-full bg-yellow-500" />
                    <span className="text-xs">Pending</span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Quick Stats */}
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium">This Month</CardTitle>
              <CardDescription>{getMonthName(new Date().getMonth() + 1)} 2026</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Total Leaves</span>
                  <span className="font-medium">{filteredLeaves.length}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Approved</span>
                  <span className="font-medium text-green-600">
                    {filteredLeaves.filter(l => l.status === 'approved').length}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Pending</span>
                  <span className="font-medium text-yellow-600">
                    {filteredLeaves.filter(l => l.status === 'pending').length}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Holidays</span>
                  <span className="font-medium text-orange-600">
                    {holidays.filter(h => {
                      const d = new Date(h.date)
                      const now = new Date()
                      return d.getMonth() === now.getMonth() && d.getFullYear() === now.getFullYear()
                    }).length}
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Leave Detail Dialog */}
      <Dialog open={showLeaveDialog} onOpenChange={setShowLeaveDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              {selectedLeave && getLeaveTypeIcon(selectedLeave.leave_type_code)}
              Leave Details
            </DialogTitle>
          </DialogHeader>

          {selectedLeave && (
            <div className="space-y-4">
              {/* Employee Info */}
              <div className="flex items-center gap-3 p-3 bg-muted rounded-lg">
                <div className="w-10 h-10 bg-primary/10 rounded-full flex items-center justify-center">
                  <span className="text-sm font-medium text-primary">
                    {selectedLeave.employee_name.split(' ').map(n => n[0]).join('')}
                  </span>
                </div>
                <div className="flex-1">
                  <p className="font-medium">{selectedLeave.employee_name}</p>
                  <p className="text-sm text-muted-foreground">{selectedLeave.leave_type_name}</p>
                </div>
                {getStatusBadge(selectedLeave.status)}
              </div>

              {/* Leave Details */}
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="text-muted-foreground">From Date</p>
                  <p className="font-medium">{formatDate(selectedLeave.from_date, { format: 'long' })}</p>
                </div>
                <div>
                  <p className="text-muted-foreground">To Date</p>
                  <p className="font-medium">{formatDate(selectedLeave.to_date, { format: 'long' })}</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Duration</p>
                  <p className="font-medium">
                    {selectedLeave.days} day(s)
                    {selectedLeave.half_day && ` (${selectedLeave.half_day_type === 'first_half' ? 'First Half' : 'Second Half'})`}
                  </p>
                </div>
                <div>
                  <p className="text-muted-foreground">Applied On</p>
                  <p className="font-medium">{formatDate(selectedLeave.applied_on, { format: 'short' })}</p>
                </div>
              </div>

              {/* Reason */}
              <div>
                <p className="text-sm text-muted-foreground mb-1">Reason</p>
                <p className="text-sm p-3 bg-muted rounded-lg">{selectedLeave.reason}</p>
              </div>

              {/* Approver Info */}
              {selectedLeave.approver_name && (
                <div className="text-sm p-3 bg-green-50 border border-green-200 rounded-lg">
                  <p className="text-green-800">
                    {selectedLeave.status === 'approved' ? 'Approved' : 'Reviewed'} by{' '}
                    <span className="font-medium">{selectedLeave.approver_name}</span>
                  </p>
                  {selectedLeave.approved_on && (
                    <p className="text-green-600 text-xs mt-1">
                      on {formatDate(selectedLeave.approved_on, { format: 'long', showTime: true })}
                    </p>
                  )}
                </div>
              )}
            </div>
          )}

          <DialogFooter>
            <Button variant="outline" onClick={() => setShowLeaveDialog(false)}>
              Close
            </Button>
            <Button variant="outline" asChild>
              <Link href={`/leave/requests`}>
                View All Requests
              </Link>
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
