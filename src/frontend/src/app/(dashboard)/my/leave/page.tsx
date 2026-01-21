'use client'

import { useState, useEffect, useCallback } from 'react'
import { PageHeader } from '@/components/layout/page-header'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Skeleton } from '@/components/ui/skeleton'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { useApi, useToast } from '@/hooks'
import {
  Calendar,
  Plus,
  Palmtree,
  Stethoscope,
  Baby,
  Briefcase,
  Clock,
  AlertCircle,
  Loader2
} from 'lucide-react'

interface LeaveBalanceItem {
  leave_type_id: string
  leave_type_name: string
  leave_type_code: string
  entitled: number
  taken: number
  pending: number
  available: number
  carry_forward: number
}

interface LeaveBalanceResponse {
  employee_id: string
  employee_name: string
  year: number
  balances: LeaveBalanceItem[]
  summary: {
    total_entitled: number
    total_taken: number
    total_pending: number
    total_available: number
  }
}

interface LeaveRequest {
  id: string
  leave_type_id: string
  leave_type_name?: string
  from_date: string
  to_date: string
  days: number
  reason: string
  status: string
  applied_on: string
  approved_by?: string
  approved_on?: string
  rejection_reason?: string
}

interface LeaveRequestListResponse {
  data: LeaveRequest[]
  total: number
}

interface LeaveType {
  id: string
  name: string
  code: string
  is_active: boolean
}

interface LeaveTypeListResponse {
  data: LeaveType[]
  total: number
}

interface Holiday {
  id: string
  name: string
  date: string
  type: string
  is_optional: boolean
}

interface HolidayListResponse {
  data: Holiday[]
  total: number
}

const statusColors: Record<string, string> = {
  draft: 'bg-gray-100 text-gray-800',
  pending: 'bg-yellow-100 text-yellow-800',
  approved: 'bg-green-100 text-green-800',
  rejected: 'bg-red-100 text-red-800',
  cancelled: 'bg-gray-100 text-gray-800',
}

const leaveTypeIcons: Record<string, React.ElementType> = {
  EL: Palmtree,
  SL: Stethoscope,
  CL: Calendar,
  WFH: Briefcase,
  ML: Baby,
  PL: Baby,
}

export default function MyLeavePage() {
  const [isDialogOpen, setIsDialogOpen] = useState(false)
  const [leaveForm, setLeaveForm] = useState({
    leave_type_id: '',
    from_date: '',
    to_date: '',
    reason: ''
  })
  const { showToast } = useToast()

  // API hooks
  const { data: balanceData, isLoading: isLoadingBalance, get: getBalance } = useApi<LeaveBalanceResponse>()
  const { data: requestsData, isLoading: isLoadingRequests, get: getRequests } = useApi<LeaveRequestListResponse>()
  const { data: leaveTypesData, get: getLeaveTypes } = useApi<LeaveTypeListResponse>()
  const { data: holidaysData, isLoading: isLoadingHolidays, get: getHolidays } = useApi<HolidayListResponse>()
  const { isLoading: isSubmitting, post: submitLeave, error: submitError } = useApi<LeaveRequest>()

  // Fetch all data
  const fetchData = useCallback(() => {
    getBalance('/leave/balance')
    getRequests('/leave/requests?page=1&limit=20')
    getLeaveTypes('/leave/types')
    getHolidays('/leave/holidays')
  }, [getBalance, getRequests, getLeaveTypes, getHolidays])

  useEffect(() => {
    fetchData()
  }, [fetchData])

  const handleSubmitLeave = async () => {
    if (!leaveForm.leave_type_id || !leaveForm.from_date || !leaveForm.to_date || !leaveForm.reason) {
      showToast('error', 'Please fill all required fields')
      return
    }

    const result = await submitLeave('/leave/requests', {
      leave_type_id: leaveForm.leave_type_id,
      from_date: leaveForm.from_date,
      to_date: leaveForm.to_date,
      reason: leaveForm.reason,
      day_type: 'full_day'
    })

    if (result) {
      showToast('success', 'Leave request submitted successfully')
      setIsDialogOpen(false)
      setLeaveForm({ leave_type_id: '', from_date: '', to_date: '', reason: '' })
      fetchData()
    }
  }

  const leaveBalance = balanceData?.balances || []
  const leaveRequests = requestsData?.data || []
  const leaveTypes = leaveTypesData?.data || []
  const holidays = holidaysData?.data || []

  const isLoading = isLoadingBalance || isLoadingRequests

  if (isLoading) {
    return (
      <div className="space-y-6">
        <PageHeader
          title="My Leave"
          description="View balance, apply for leave, and track requests"
          icon={Calendar}
        />
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map(i => (
            <Card key={i}>
              <CardContent className="pt-6">
                <Skeleton className="h-24 w-full" />
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="My Leave"
        description="View balance, apply for leave, and track requests"
        icon={Calendar}
        actions={
          <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="h-4 w-4 mr-2" />
                Apply Leave
              </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-md">
              <DialogHeader>
                <DialogTitle>Apply for Leave</DialogTitle>
                <DialogDescription>
                  Fill in the details to submit your leave request
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4 py-4">
                <div className="space-y-2">
                  <Label htmlFor="leave-type">Leave Type</Label>
                  <Select
                    value={leaveForm.leave_type_id}
                    onValueChange={(value) => setLeaveForm(prev => ({ ...prev, leave_type_id: value }))}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select leave type" />
                    </SelectTrigger>
                    <SelectContent>
                      {leaveTypes.filter(lt => lt.is_active).map(lt => (
                        <SelectItem key={lt.id} value={lt.id}>{lt.name}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="from-date">From Date</Label>
                    <Input
                      id="from-date"
                      type="date"
                      value={leaveForm.from_date}
                      onChange={(e) => setLeaveForm(prev => ({ ...prev, from_date: e.target.value }))}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="to-date">To Date</Label>
                    <Input
                      id="to-date"
                      type="date"
                      value={leaveForm.to_date}
                      onChange={(e) => setLeaveForm(prev => ({ ...prev, to_date: e.target.value }))}
                    />
                  </div>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="reason">Reason</Label>
                  <Textarea
                    id="reason"
                    placeholder="Enter reason for leave..."
                    value={leaveForm.reason}
                    onChange={(e) => setLeaveForm(prev => ({ ...prev, reason: e.target.value }))}
                  />
                </div>
                {submitError && (
                  <p className="text-sm text-red-600">{submitError}</p>
                )}
                <div className="flex justify-end gap-2">
                  <Button variant="outline" onClick={() => setIsDialogOpen(false)}>Cancel</Button>
                  <Button onClick={handleSubmitLeave} disabled={isSubmitting}>
                    {isSubmitting && <Loader2 className="h-4 w-4 mr-2 animate-spin" />}
                    Submit
                  </Button>
                </div>
              </div>
            </DialogContent>
          </Dialog>
        }
      />

      {/* Leave Balance Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {leaveBalance.length > 0 ? (
          leaveBalance.map((leave) => {
            const Icon = leaveTypeIcons[leave.leave_type_code] || Calendar
            const usedPercent = leave.entitled > 0 ? (leave.taken / leave.entitled) * 100 : 0

            return (
              <Card key={leave.leave_type_id}>
                <CardHeader className="pb-2">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-sm font-medium">{leave.leave_type_name}</CardTitle>
                    <div className="p-2 rounded-lg bg-primary/10">
                      <Icon className="h-4 w-4 text-primary" />
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex items-end justify-between">
                      <span className="text-3xl font-bold">{leave.available}</span>
                      <span className="text-sm text-muted-foreground">of {leave.entitled} days</span>
                    </div>
                    <Progress value={usedPercent} className="h-2" />
                    <div className="flex justify-between text-xs text-muted-foreground">
                      <span>Used: {leave.taken}</span>
                      {leave.pending > 0 && <span className="text-yellow-600">Pending: {leave.pending}</span>}
                    </div>
                  </div>
                </CardContent>
              </Card>
            )
          })
        ) : (
          <Card className="col-span-full">
            <CardContent className="pt-6">
              <div className="flex flex-col items-center justify-center py-8 text-center">
                <Calendar className="h-8 w-8 text-muted-foreground mb-2" />
                <p className="text-muted-foreground">No leave balance data available</p>
              </div>
            </CardContent>
          </Card>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Leave Requests */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Leave Requests</CardTitle>
            <CardDescription>Your leave application history</CardDescription>
          </CardHeader>
          <CardContent>
            {leaveRequests.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-8 text-center">
                <Calendar className="h-8 w-8 text-muted-foreground mb-2" />
                <p className="text-muted-foreground">No leave requests found</p>
              </div>
            ) : (
              <div className="border rounded-lg overflow-hidden">
                <table className="w-full">
                  <thead className="bg-muted/50">
                    <tr>
                      <th className="text-left p-3 font-medium">Type</th>
                      <th className="text-left p-3 font-medium">Duration</th>
                      <th className="text-center p-3 font-medium">Days</th>
                      <th className="text-left p-3 font-medium">Reason</th>
                      <th className="text-center p-3 font-medium">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {leaveRequests.map((request) => (
                      <tr key={request.id} className="border-t hover:bg-muted/30">
                        <td className="p-3 font-medium">{request.leave_type_name || 'Leave'}</td>
                        <td className="p-3 text-sm text-muted-foreground">
                          {new Date(request.from_date).toLocaleDateString('en-IN', { day: 'numeric', month: 'short' })}
                          {request.from_date !== request.to_date && (
                            <> - {new Date(request.to_date).toLocaleDateString('en-IN', { day: 'numeric', month: 'short' })}</>
                          )}
                        </td>
                        <td className="p-3 text-center">{request.days}</td>
                        <td className="p-3 text-sm text-muted-foreground max-w-xs truncate">{request.reason}</td>
                        <td className="p-3 text-center">
                          <Badge className={statusColors[request.status]}>{request.status}</Badge>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Upcoming Holidays */}
        <Card>
          <CardHeader>
            <CardTitle>Upcoming Holidays</CardTitle>
            <CardDescription>Public holidays this year</CardDescription>
          </CardHeader>
          <CardContent>
            {isLoadingHolidays ? (
              <div className="space-y-3">
                {[1, 2, 3].map(i => (
                  <Skeleton key={i} className="h-16 w-full" />
                ))}
              </div>
            ) : holidays.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-8 text-center">
                <Calendar className="h-8 w-8 text-muted-foreground mb-2" />
                <p className="text-muted-foreground">No holidays configured</p>
              </div>
            ) : (
              <div className="space-y-3">
                {holidays
                  .filter(h => new Date(h.date) >= new Date())
                  .slice(0, 6)
                  .map((holiday) => {
                    const daysUntil = Math.ceil((new Date(holiday.date).getTime() - new Date().getTime()) / (1000 * 60 * 60 * 24))
                    return (
                      <div key={holiday.id} className="flex items-center justify-between p-3 bg-muted/50 rounded-lg">
                        <div>
                          <p className="font-medium">{holiday.name}</p>
                          <p className="text-sm text-muted-foreground">
                            {new Date(holiday.date).toLocaleDateString('en-IN', { weekday: 'short', day: 'numeric', month: 'short' })}
                          </p>
                        </div>
                        <Badge variant="outline">
                          <Clock className="h-3 w-3 mr-1" />
                          {daysUntil} days
                        </Badge>
                      </div>
                    )
                  })}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
