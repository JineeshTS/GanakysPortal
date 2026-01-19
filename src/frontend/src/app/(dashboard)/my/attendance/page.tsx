'use client'

import { useState, useEffect, useCallback } from 'react'
import { PageHeader } from '@/components/layout/page-header'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Calendar } from '@/components/ui/calendar'
import { Skeleton } from '@/components/ui/skeleton'
import { useApi, useAuthStore, useToast } from '@/hooks'
import {
  Clock,
  LogIn,
  LogOut,
  Timer,
  CalendarDays,
  TrendingUp,
  AlertCircle,
  Loader2
} from 'lucide-react'

interface AttendanceRecord {
  id: string
  employee_id: string
  employee_name?: string
  employee_code?: string
  date: string
  check_in?: string
  check_out?: string
  work_hours: number
  break_hours: number
  overtime_hours: number
  status: string
  source: string
  notes?: string
}

interface AttendanceListResponse {
  success: boolean
  data: AttendanceRecord[]
  meta: {
    page: number
    limit: number
    total: number
  }
}

interface CheckInOutResponse {
  id: string
  check_in?: string
  check_out?: string
  status: string
  message?: string
}

const statusColors: Record<string, string> = {
  present: 'bg-green-100 text-green-800',
  late: 'bg-yellow-100 text-yellow-800',
  absent: 'bg-red-100 text-red-800',
  'early-leave': 'bg-orange-100 text-orange-800',
  'half-day': 'bg-blue-100 text-blue-800',
  'work-from-home': 'bg-purple-100 text-purple-800',
  'on-leave': 'bg-gray-100 text-gray-800',
}

export default function MyAttendancePage() {
  const [date, setDate] = useState<Date | undefined>(new Date())
  const { user } = useAuthStore()
  const { showToast } = useToast()

  // API hooks
  const { data: attendanceData, isLoading, error, get } = useApi<AttendanceListResponse>()
  const { data: checkInData, isLoading: isCheckingIn, post: checkIn } = useApi<CheckInOutResponse>()
  const { data: checkOutData, isLoading: isCheckingOut, post: checkOut } = useApi<CheckInOutResponse>()

  // Fetch attendance records
  const fetchAttendance = useCallback(() => {
    const today = new Date().toISOString().split('T')[0]
    get(`/attendance?page=1&limit=30`)
  }, [get])

  useEffect(() => {
    fetchAttendance()
  }, [fetchAttendance])

  const currentTime = new Date().toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' })

  // Find today's attendance
  const today = new Date().toISOString().split('T')[0]
  const todayAttendance = attendanceData?.data?.find(record => record.date === today)
  const isCheckedIn = !!todayAttendance?.check_in && !todayAttendance?.check_out
  const hasCheckedOut = !!todayAttendance?.check_out

  const handleCheckIn = async () => {
    const result = await checkIn('/attendance/check-in', {
      source: 'web',
      notes: 'Checked in via web portal'
    })
    if (result) {
      showToast('success', 'Checked in successfully')
      fetchAttendance()
    }
  }

  const handleCheckOut = async () => {
    const result = await checkOut('/attendance/check-out', {
      notes: 'Checked out via web portal'
    })
    if (result) {
      showToast('success', 'Checked out successfully')
      fetchAttendance()
    }
  }

  // Calculate stats from attendance data
  const attendanceRecords = attendanceData?.data || []
  const stats = {
    presentDays: attendanceRecords.filter(r => r.status === 'present' || r.status === 'late').length,
    lateDays: attendanceRecords.filter(r => r.status === 'late').length,
    absentDays: attendanceRecords.filter(r => r.status === 'absent').length,
    avgHours: attendanceRecords.length > 0
      ? `${Math.floor(attendanceRecords.reduce((sum, r) => sum + r.work_hours, 0) / attendanceRecords.length)}h ${Math.round((attendanceRecords.reduce((sum, r) => sum + r.work_hours, 0) / attendanceRecords.length % 1) * 60)}m`
      : '0h 0m',
  }

  const formatTime = (timeStr?: string) => {
    if (!timeStr) return '-'
    const date = new Date(timeStr)
    return date.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' })
  }

  const formatWorkHours = (hours: number) => {
    const h = Math.floor(hours)
    const m = Math.round((hours % 1) * 60)
    return `${h}h ${m}m`
  }

  if (isLoading) {
    return (
      <div className="space-y-6">
        <PageHeader
          title="My Attendance"
          description="Track your daily attendance and working hours"
          icon={Clock}
        />
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <Skeleton className="h-16 w-48" />
              <Skeleton className="h-12 w-32" />
            </div>
          </CardContent>
        </Card>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map(i => (
            <Card key={i}>
              <CardContent className="pt-6">
                <Skeleton className="h-16 w-full" />
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
        title="My Attendance"
        description="Track your daily attendance and working hours"
        icon={Clock}
      />

      {/* Quick Actions */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-primary/10 rounded-full">
                <Clock className="h-8 w-8 text-primary" />
              </div>
              <div>
                <p className="text-3xl font-bold">{currentTime}</p>
                <p className="text-muted-foreground">
                  {new Date().toLocaleDateString('en-IN', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-4">
              {todayAttendance?.check_in && (
                <div className="text-right mr-4">
                  <p className="text-sm text-muted-foreground">Checked in at</p>
                  <p className="text-lg font-semibold text-green-600">{formatTime(todayAttendance.check_in)}</p>
                  {todayAttendance?.check_out && (
                    <>
                      <p className="text-sm text-muted-foreground mt-1">Checked out at</p>
                      <p className="text-lg font-semibold text-red-600">{formatTime(todayAttendance.check_out)}</p>
                    </>
                  )}
                </div>
              )}
              {!hasCheckedOut && (
                <Button
                  size="lg"
                  variant={isCheckedIn ? "destructive" : "default"}
                  onClick={isCheckedIn ? handleCheckOut : handleCheckIn}
                  disabled={isCheckingIn || isCheckingOut}
                >
                  {(isCheckingIn || isCheckingOut) ? (
                    <Loader2 className="h-5 w-5 mr-2 animate-spin" />
                  ) : isCheckedIn ? (
                    <LogOut className="h-5 w-5 mr-2" />
                  ) : (
                    <LogIn className="h-5 w-5 mr-2" />
                  )}
                  {isCheckedIn ? 'Check Out' : 'Check In'}
                </Button>
              )}
              {hasCheckedOut && (
                <Badge className="bg-green-100 text-green-800 text-lg py-2 px-4">
                  Day Completed
                </Badge>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-green-100 rounded-lg">
                <CalendarDays className="h-5 w-5 text-green-600" />
              </div>
              <div>
                <p className="text-2xl font-bold">{stats.presentDays}</p>
                <p className="text-sm text-muted-foreground">Present Days</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-yellow-100 rounded-lg">
                <AlertCircle className="h-5 w-5 text-yellow-600" />
              </div>
              <div>
                <p className="text-2xl font-bold">{stats.lateDays}</p>
                <p className="text-sm text-muted-foreground">Late Days</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-red-100 rounded-lg">
                <CalendarDays className="h-5 w-5 text-red-600" />
              </div>
              <div>
                <p className="text-2xl font-bold">{stats.absentDays}</p>
                <p className="text-sm text-muted-foreground">Absent Days</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-100 rounded-lg">
                <TrendingUp className="h-5 w-5 text-blue-600" />
              </div>
              <div>
                <p className="text-2xl font-bold">{stats.avgHours}</p>
                <p className="text-sm text-muted-foreground">Avg. Daily Hours</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Calendar */}
        <Card>
          <CardHeader>
            <CardTitle>Calendar</CardTitle>
            <CardDescription>Select a date to view details</CardDescription>
          </CardHeader>
          <CardContent>
            <Calendar
              mode="single"
              selected={date}
              onSelect={setDate}
              className="rounded-md border"
            />
          </CardContent>
        </Card>

        {/* Recent Attendance */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Recent Attendance</CardTitle>
            <CardDescription>Your attendance for this month</CardDescription>
          </CardHeader>
          <CardContent>
            {error ? (
              <div className="flex flex-col items-center justify-center py-8 text-center">
                <AlertCircle className="h-8 w-8 text-muted-foreground mb-2" />
                <p className="text-muted-foreground">{error}</p>
                <Button variant="outline" onClick={fetchAttendance} className="mt-4">
                  Try Again
                </Button>
              </div>
            ) : attendanceRecords.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-8 text-center">
                <CalendarDays className="h-8 w-8 text-muted-foreground mb-2" />
                <p className="text-muted-foreground">No attendance records found</p>
              </div>
            ) : (
              <div className="border rounded-lg overflow-hidden">
                <table className="w-full">
                  <thead className="bg-muted/50">
                    <tr>
                      <th className="text-left p-3 font-medium">Date</th>
                      <th className="text-center p-3 font-medium">Check In</th>
                      <th className="text-center p-3 font-medium">Check Out</th>
                      <th className="text-center p-3 font-medium">Hours</th>
                      <th className="text-center p-3 font-medium">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {attendanceRecords.slice(0, 10).map((record) => (
                      <tr key={record.id} className="border-t hover:bg-muted/30">
                        <td className="p-3">
                          {new Date(record.date).toLocaleDateString('en-IN', { weekday: 'short', day: 'numeric', month: 'short' })}
                        </td>
                        <td className="p-3 text-center">
                          {record.check_in ? (
                            <span className="flex items-center justify-center gap-1">
                              <LogIn className="h-3 w-3 text-green-600" />
                              {formatTime(record.check_in)}
                            </span>
                          ) : (
                            <span className="text-muted-foreground">-</span>
                          )}
                        </td>
                        <td className="p-3 text-center">
                          {record.check_out ? (
                            <span className="flex items-center justify-center gap-1">
                              <LogOut className="h-3 w-3 text-red-600" />
                              {formatTime(record.check_out)}
                            </span>
                          ) : (
                            <span className="text-muted-foreground">-</span>
                          )}
                        </td>
                        <td className="p-3 text-center font-medium">{formatWorkHours(record.work_hours)}</td>
                        <td className="p-3 text-center">
                          <Badge className={statusColors[record.status] || 'bg-gray-100 text-gray-800'}>
                            {record.status}
                          </Badge>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
