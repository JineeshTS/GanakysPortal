'use client'

import * as React from 'react'
import { PageHeader } from '@/components/layout/page-header'
import { DataTable, Column } from '@/components/layout/data-table'
import { StatsGrid } from '@/components/layout/stat-card'
import { DatePicker } from '@/components/forms/date-picker'
import { SearchInput } from '@/components/forms/search-input'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { formatDate, formatTime } from '@/lib/format'
import { useApi } from '@/hooks'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog"
import {
  Users,
  Clock,
  CheckCircle,
  XCircle,
  Calendar,
  Download,
  Upload,
  MapPin,
  Loader2,
  Trash2,
  Edit,
  AlertTriangle
} from 'lucide-react'
import type { AttendanceLog, AttendanceStatus } from '@/types'

// API Response types
interface AttendanceApiResponse {
  success: boolean
  data: ApiAttendanceLog[]
  meta: { page: number; limit: number; total: number; date: string }
}

interface ApiAttendanceLog {
  id: string
  employee_id: string
  employee_name: string | null
  employee_code: string | null
  date: string
  check_in: string | null
  check_out: string | null
  work_hours: number
  break_hours: number
  overtime_hours: number
  status: string
  source: string
  location: { latitude: number; longitude: number; address?: string } | null
  notes: string | null
}

interface AttendanceSummaryResponse {
  date: string
  total_employees: number
  present: number
  absent: number
  on_leave: number
  half_day: number
  work_from_home: number
  late_arrivals: number
  early_departures: number
  avg_check_in: string | null
  avg_check_out: string | null
  avg_work_hours: number
  total_overtime_hours: number
}

// Mock attendance data
const mockAttendance: AttendanceLog[] = [
  {
    id: '1',
    employee_id: '1',
    date: '2026-01-06',
    check_in: '2026-01-06T09:05:00',
    check_out: '2026-01-06T18:30:00',
    work_hours: 8.5,
    break_hours: 1,
    overtime_hours: 0.5,
    status: 'present',
    source: 'biometric',
    created_at: '2026-01-06T09:05:00Z',
    updated_at: '2026-01-06T18:30:00Z'
  },
  {
    id: '2',
    employee_id: '2',
    date: '2026-01-06',
    check_in: '2026-01-06T09:45:00',
    check_out: '2026-01-06T18:00:00',
    work_hours: 7.25,
    break_hours: 1,
    overtime_hours: 0,
    status: 'present',
    source: 'mobile',
    location: { latitude: 12.9716, longitude: 77.5946, accuracy: 10, address: 'Bangalore, KA' },
    created_at: '2026-01-06T09:45:00Z',
    updated_at: '2026-01-06T18:00:00Z'
  },
  {
    id: '3',
    employee_id: '3',
    date: '2026-01-06',
    status: 'on_leave',
    work_hours: 0,
    break_hours: 0,
    overtime_hours: 0,
    source: 'system',
    notes: 'Approved EL',
    created_at: '2026-01-06T00:00:00Z',
    updated_at: '2026-01-06T00:00:00Z'
  },
  {
    id: '4',
    employee_id: '4',
    date: '2026-01-06',
    check_in: '2026-01-06T10:30:00',
    work_hours: 0,
    break_hours: 0,
    overtime_hours: 0,
    status: 'half_day',
    source: 'biometric',
    created_at: '2026-01-06T10:30:00Z',
    updated_at: '2026-01-06T10:30:00Z'
  }
]

// Employee names mapping
const employeeNames: Record<string, string> = {
  '1': 'Rajesh Kumar',
  '2': 'Priya Sharma',
  '3': 'Amit Patel',
  '4': 'Sneha Reddy'
}

// Today's stats
const todayStats = {
  totalEmployees: 47,
  present: 42,
  absent: 2,
  onLeave: 3,
  workFromHome: 5,
  late: 4
}

export default function AttendancePage() {
  const [selectedDate, setSelectedDate] = React.useState(
    new Date().toISOString().split('T')[0]
  )
  const [searchQuery, setSearchQuery] = React.useState('')
  const [attendance, setAttendance] = React.useState<AttendanceLog[]>([])
  const [summary, setSummary] = React.useState<AttendanceSummaryResponse | null>(null)
  const [isLoading, setIsLoading] = React.useState(true)

  // Delete state
  const [deleteDialogOpen, setDeleteDialogOpen] = React.useState(false)
  const [recordToDelete, setRecordToDelete] = React.useState<AttendanceLog | null>(null)
  const [isDeleting, setIsDeleting] = React.useState(false)

  const attendanceApi = useApi<AttendanceApiResponse>()
  const summaryApi = useApi<AttendanceSummaryResponse>()
  const deleteApi = useApi()

  // Delete handlers
  const handleDeleteClick = (record: AttendanceLog, e: React.MouseEvent) => {
    e.stopPropagation()
    setRecordToDelete(record)
    setDeleteDialogOpen(true)
  }

  const handleDeleteConfirm = async () => {
    if (!recordToDelete) return
    setIsDeleting(true)
    try {
      await deleteApi.delete(`/attendance/${recordToDelete.id}`)
      setAttendance(attendance.filter(a => a.id !== recordToDelete.id))
      setDeleteDialogOpen(false)
      setRecordToDelete(null)
    } catch (error) {
      console.error('Failed to delete attendance record:', error)
    } finally {
      setIsDeleting(false)
    }
  }

  // Fetch attendance data
  React.useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true)
      try {
        // Fetch attendance records
        const attendanceResult = await attendanceApi.get(`/attendance?log_date=${selectedDate}`)
        if (attendanceResult && attendanceResult.data) {
          const mappedAttendance: AttendanceLog[] = attendanceResult.data.map((a: ApiAttendanceLog) => ({
            id: a.id,
            employee_id: a.employee_id,
            date: a.date,
            check_in: a.check_in || undefined,
            check_out: a.check_out || undefined,
            work_hours: a.work_hours,
            break_hours: a.break_hours,
            overtime_hours: a.overtime_hours,
            status: a.status as AttendanceStatus,
            source: a.source as 'biometric' | 'manual' | 'mobile' | 'system',
            location: a.location ? {
              latitude: a.location.latitude,
              longitude: a.location.longitude,
              accuracy: 0,
              address: a.location.address
            } : undefined,
            notes: a.notes || undefined,
            created_at: a.date,
            updated_at: a.date,
            _employee_name: a.employee_name
          }))
          setAttendance(mappedAttendance)
        }

        // Fetch summary
        const summaryResult = await summaryApi.get(`/attendance/summary?log_date=${selectedDate}`)
        if (summaryResult) {
          setSummary(summaryResult)
        }
      } catch (error) {
        console.error('Failed to fetch attendance:', error)
      } finally {
        setIsLoading(false)
      }
    }
    fetchData()
  }, [selectedDate])

  const stats = [
    {
      title: 'Total Employees',
      value: summary?.total_employees || 0,
      icon: Users,
      description: 'Headcount'
    },
    {
      title: 'Present Today',
      value: summary?.present || 0,
      icon: CheckCircle,
      description: summary?.total_employees
        ? `${Math.round(((summary?.present || 0) / summary.total_employees) * 100)}% attendance`
        : '0% attendance',
      valueClassName: 'text-green-600'
    },
    {
      title: 'On Leave',
      value: summary?.on_leave || 0,
      icon: Calendar,
      description: 'Approved leave'
    },
    {
      title: 'Late Arrivals',
      value: summary?.late_arrivals || 0,
      icon: Clock,
      description: 'After 9:30 AM',
      valueClassName: 'text-yellow-600'
    }
  ]

  // Build employee names map from attendance data
  const employeeNames: Record<string, string> = {}
  attendance.forEach(a => {
    if ((a as AttendanceLog & { _employee_name?: string })._employee_name) {
      employeeNames[a.employee_id] = (a as AttendanceLog & { _employee_name?: string })._employee_name!
    }
  })

  const getStatusBadge = (status: AttendanceStatus) => {
    const statusConfig = {
      present: { label: 'Present', className: 'bg-green-100 text-green-800' },
      absent: { label: 'Absent', className: 'bg-red-100 text-red-800' },
      half_day: { label: 'Half Day', className: 'bg-yellow-100 text-yellow-800' },
      on_leave: { label: 'On Leave', className: 'bg-blue-100 text-blue-800' },
      holiday: { label: 'Holiday', className: 'bg-purple-100 text-purple-800' },
      week_off: { label: 'Week Off', className: 'bg-gray-100 text-gray-800' },
      work_from_home: { label: 'WFH', className: 'bg-teal-100 text-teal-800' },
      on_duty: { label: 'On Duty', className: 'bg-orange-100 text-orange-800' },
      pending: { label: 'Pending', className: 'bg-gray-100 text-gray-800' }
    }

    const config = statusConfig[status] || statusConfig.pending
    return <Badge className={config.className}>{config.label}</Badge>
  }

  const getSourceBadge = (source: string) => {
    const sourceConfig: Record<string, { label: string; className: string }> = {
      biometric: { label: 'Biometric', className: 'bg-blue-50 text-blue-700' },
      manual: { label: 'Manual', className: 'bg-gray-50 text-gray-700' },
      mobile: { label: 'Mobile', className: 'bg-green-50 text-green-700' },
      system: { label: 'System', className: 'bg-purple-50 text-purple-700' }
    }

    const config = sourceConfig[source] || sourceConfig.manual
    return <Badge variant="outline" className={config.className}>{config.label}</Badge>
  }

  const columns: Column<AttendanceLog>[] = [
    {
      key: 'employee',
      header: 'Employee',
      accessor: (row) => (
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-primary/10 rounded-full flex items-center justify-center">
            <span className="text-xs font-medium text-primary">
              {employeeNames[row.employee_id]?.split(' ').map(n => n[0]).join('') || '??'}
            </span>
          </div>
          <span className="font-medium">{employeeNames[row.employee_id] || 'Unknown'}</span>
        </div>
      )
    },
    {
      key: 'check_in',
      header: 'Check In',
      accessor: (row) => row.check_in ? (
        <div>
          <p className="font-medium">{formatTime(row.check_in)}</p>
          {row.location && (
            <p className="text-xs text-muted-foreground flex items-center gap-1">
              <MapPin className="h-3 w-3" />
              {row.location.address}
            </p>
          )}
        </div>
      ) : '-'
    },
    {
      key: 'check_out',
      header: 'Check Out',
      accessor: (row) => row.check_out ? formatTime(row.check_out) : '-'
    },
    {
      key: 'work_hours',
      header: 'Work Hours',
      accessor: (row) => row.work_hours > 0 ? `${row.work_hours.toFixed(1)} hrs` : '-'
    },
    {
      key: 'overtime',
      header: 'Overtime',
      accessor: (row) => row.overtime_hours > 0 ? (
        <span className="text-green-600 font-medium">+{row.overtime_hours.toFixed(1)} hrs</span>
      ) : '-'
    },
    {
      key: 'status',
      header: 'Status',
      accessor: (row) => getStatusBadge(row.status)
    },
    {
      key: 'source',
      header: 'Source',
      accessor: (row) => getSourceBadge(row.source)
    },
    {
      key: 'actions',
      header: '',
      accessor: (row) => row.source === 'manual' || row.source === 'mobile' ? (
        <div className="flex items-center gap-1">
          <Button
            variant="ghost"
            size="icon"
            className="text-gray-600 hover:text-red-700 hover:bg-red-50"
            onClick={(e) => handleDeleteClick(row, e)}
            title="Delete Record"
          >
            <Trash2 className="h-4 w-4" />
          </Button>
        </div>
      ) : null
    }
  ]

  return (
    <div className="space-y-6">
      <PageHeader
        title="Attendance"
        description="Track daily attendance and work hours"
        breadcrumbs={[
          { label: 'Dashboard', href: '/dashboard' },
          { label: 'Attendance' }
        ]}
        actions={
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm">
              <Upload className="h-4 w-4 mr-2" />
              Import
            </Button>
            <Button variant="outline" size="sm">
              <Download className="h-4 w-4 mr-2" />
              Export
            </Button>
          </div>
        }
      />

      {/* Stats */}
      <StatsGrid stats={stats} columns={4} />

      {/* Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col sm:flex-row gap-4">
            <DatePicker
              label="Select Date"
              name="attendance-date"
              value={selectedDate}
              onChange={(date) => setSelectedDate(date)}
              max={new Date().toISOString().split('T')[0]}
              containerClassName="flex-1 max-w-xs"
            />
            <div className="flex-1">
              <SearchInput
                value={searchQuery}
                onChange={setSearchQuery}
                placeholder="Search employee..."
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Attendance Table */}
      <Card>
        <CardHeader>
          <CardTitle>Attendance Log</CardTitle>
          <CardDescription>
            {formatDate(selectedDate, { format: 'long' })}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="h-6 w-6 animate-spin text-primary mr-2" />
              <span className="text-muted-foreground">Loading attendance...</span>
            </div>
          ) : (
            <DataTable
              data={attendance}
              columns={columns}
              keyExtractor={(row) => row.id}
              emptyMessage="No attendance records found"
            />
          )}
        </CardContent>
      </Card>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Attendance Summary</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Present</span>
                <span className="text-green-600 font-medium">{summary?.present || 0}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Absent</span>
                <span className="text-red-600 font-medium">{summary?.absent || 0}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">On Leave</span>
                <span className="text-blue-600 font-medium">{summary?.on_leave || 0}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Work From Home</span>
                <span className="text-teal-600 font-medium">{summary?.work_from_home || 0}</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Time Summary</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Avg Check-in</span>
                <span className="font-medium">{summary?.avg_check_in || '-'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Avg Check-out</span>
                <span className="font-medium">{summary?.avg_check_out || '-'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Avg Work Hours</span>
                <span className="font-medium">{summary?.avg_work_hours?.toFixed(1) || '0'} hrs</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Total Overtime</span>
                <span className="text-green-600 font-medium">{summary?.total_overtime_hours?.toFixed(1) || '0'} hrs</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Regularization Requests</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Pending</span>
                <span className="text-yellow-600 font-medium">0</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Approved Today</span>
                <span className="text-green-600 font-medium">0</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Rejected Today</span>
                <span className="text-red-600 font-medium">0</span>
              </div>
            </div>
            <Button variant="link" size="sm" className="mt-2 p-0 h-auto">
              View All Requests →
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-red-500" />
              Delete Attendance Record
            </AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete the attendance record for{' '}
              <strong>
                {recordToDelete ? employeeNames[recordToDelete.employee_id] || 'Unknown Employee' : ''}
              </strong>
              {' '}on {recordToDelete ? formatDate(recordToDelete.date) : ''}?
              This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={isDeleting}>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDeleteConfirm}
              disabled={isDeleting}
              className="bg-red-600 hover:bg-red-700 focus:ring-red-600"
            >
              {isDeleting ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Deleting...
                </>
              ) : (
                'Delete'
              )}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
}
