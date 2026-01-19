'use client'

import { useState, useEffect, useCallback } from 'react'
import Link from 'next/link'
import { PageHeader } from '@/components/layout/page-header'
import { useAuth } from "@/hooks/use-auth"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
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
} from '@/components/ui/dialog'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import {
  ChevronLeft,
  RefreshCw,
  Loader2,
  Clock,
  MapPin,
  Smartphone,
  LogIn,
  LogOut,
  User,
  Calendar,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Search,
  Camera,
  Building,
  Timer,
  TrendingUp,
  Users,
} from 'lucide-react'

interface MobileAttendance {
  id: string
  employee_id: string
  employee_name: string
  employee_code: string
  department: string
  device_name: string
  check_in_time: string | null
  check_out_time: string | null
  check_in_location: { lat: number; lng: number; address: string } | null
  check_out_location: { lat: number; lng: number; address: string } | null
  check_in_photo_url: string | null
  check_out_photo_url: string | null
  is_within_geofence: boolean
  total_hours: number | null
  status: 'checked_in' | 'checked_out' | 'absent' | 'on_leave' | 'half_day'
  verification_method: 'biometric' | 'photo' | 'pin' | 'location'
  date: string
}

const statusConfig: Record<string, { color: string; icon: React.ReactNode; label: string }> = {
  checked_in: { color: 'bg-green-100 text-green-800', icon: <LogIn className="h-4 w-4" />, label: 'Checked In' },
  checked_out: { color: 'bg-blue-100 text-blue-800', icon: <LogOut className="h-4 w-4" />, label: 'Checked Out' },
  absent: { color: 'bg-red-100 text-red-800', icon: <XCircle className="h-4 w-4" />, label: 'Absent' },
  on_leave: { color: 'bg-purple-100 text-purple-800', icon: <Calendar className="h-4 w-4" />, label: 'On Leave' },
  half_day: { color: 'bg-yellow-100 text-yellow-800', icon: <Timer className="h-4 w-4" />, label: 'Half Day' },
}

const verificationConfig: Record<string, { icon: React.ReactNode; label: string }> = {
  biometric: { icon: <User className="h-4 w-4" />, label: 'Biometric' },
  photo: { icon: <Camera className="h-4 w-4" />, label: 'Photo' },
  pin: { icon: <Smartphone className="h-4 w-4" />, label: 'PIN' },
  location: { icon: <MapPin className="h-4 w-4" />, label: 'Location' },
}

function formatDuration(hours: number | null): string {
  if (hours === null) return '-'
  const h = Math.floor(hours)
  const m = Math.round((hours - h) * 60)
  return `${h}h ${m}m`
}

export default function MobileAttendancePage() {
  const [isLoading, setIsLoading] = useState(true)
  const [attendanceRecords, setAttendanceRecords] = useState<MobileAttendance[]>([])
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [dateFilter, setDateFilter] = useState<string>(new Date().toISOString().split('T')[0])
  const [detailDialogOpen, setDetailDialogOpen] = useState(false)
  const [selectedRecord, setSelectedRecord] = useState<MobileAttendance | null>(null)

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || '/api/v1'

  const fetchAttendance = useCallback(async () => {
    setIsLoading(true)
    try {
      const params = new URLSearchParams()
      params.set('date', dateFilter)
      if (statusFilter !== 'all') params.set('status', statusFilter)

      const res = await fetchWithAuth(`${apiUrl}/mobile/attendance?${params.toString()}`)
      if (res.ok) {
        const data = await res.json()
        setAttendanceRecords(data.data || [])
      }
    } catch (err) {
      console.error('Failed to fetch attendance:', err)
    } finally {
      setIsLoading(false)
    }
  }, [apiUrl, dateFilter, statusFilter])

  useEffect(() => {
    fetchAttendance()
  }, [fetchAttendance])

  // Mock data for demo
  const mockRecords: MobileAttendance[] = [
    { id: '1', employee_id: 'e1', employee_name: 'Rahul Sharma', employee_code: 'EMP001', department: 'Engineering', device_name: 'iPhone 15 Pro', check_in_time: '2026-01-17T09:02:00Z', check_out_time: '2026-01-17T18:15:00Z', check_in_location: { lat: 28.6139, lng: 77.209, address: 'Connaught Place, New Delhi' }, check_out_location: { lat: 28.6139, lng: 77.209, address: 'Connaught Place, New Delhi' }, check_in_photo_url: null, check_out_photo_url: null, is_within_geofence: true, total_hours: 9.22, status: 'checked_out', verification_method: 'biometric', date: '2026-01-17' },
    { id: '2', employee_id: 'e2', employee_name: 'Priya Patel', employee_code: 'EMP002', department: 'Finance', device_name: 'Samsung Galaxy S24', check_in_time: '2026-01-17T08:55:00Z', check_out_time: null, check_in_location: { lat: 28.6129, lng: 77.2295, address: 'India Gate, New Delhi' }, check_out_location: null, check_in_photo_url: '/photos/priya-checkin.jpg', check_out_photo_url: null, is_within_geofence: true, total_hours: null, status: 'checked_in', verification_method: 'photo', date: '2026-01-17' },
    { id: '3', employee_id: 'e3', employee_name: 'Amit Kumar', employee_code: 'EMP003', department: 'HR', device_name: 'iPad Pro', check_in_time: '2026-01-17T09:30:00Z', check_out_time: '2026-01-17T13:00:00Z', check_in_location: { lat: 28.5535, lng: 77.2588, address: 'Nehru Place, New Delhi' }, check_out_location: { lat: 28.5535, lng: 77.2588, address: 'Nehru Place, New Delhi' }, check_in_photo_url: null, check_out_photo_url: null, is_within_geofence: true, total_hours: 3.5, status: 'half_day', verification_method: 'pin', date: '2026-01-17' },
    { id: '4', employee_id: 'e4', employee_name: 'Neha Singh', employee_code: 'EMP004', department: 'Sales', device_name: 'OnePlus 12', check_in_time: null, check_out_time: null, check_in_location: null, check_out_location: null, check_in_photo_url: null, check_out_photo_url: null, is_within_geofence: false, total_hours: null, status: 'on_leave', verification_method: 'location', date: '2026-01-17' },
    { id: '5', employee_id: 'e5', employee_name: 'Vikram Rao', employee_code: 'EMP005', department: 'Operations', device_name: 'Pixel 8 Pro', check_in_time: '2026-01-17T08:45:00Z', check_out_time: '2026-01-17T17:30:00Z', check_in_location: { lat: 28.4595, lng: 77.0266, address: 'Gurgaon, Haryana' }, check_out_location: { lat: 28.4595, lng: 77.0266, address: 'Gurgaon, Haryana' }, check_in_photo_url: null, check_out_photo_url: null, is_within_geofence: false, total_hours: 8.75, status: 'checked_out', verification_method: 'biometric', date: '2026-01-17' },
    { id: '6', employee_id: 'e6', employee_name: 'Sunita Gupta', employee_code: 'EMP006', department: 'Marketing', device_name: 'iPhone 14', check_in_time: null, check_out_time: null, check_in_location: null, check_out_location: null, check_in_photo_url: null, check_out_photo_url: null, is_within_geofence: false, total_hours: null, status: 'absent', verification_method: 'location', date: '2026-01-17' },
  ]

  const displayRecords = attendanceRecords.length > 0 ? attendanceRecords : mockRecords
  const filteredRecords = displayRecords.filter(r =>
    r.employee_name.toLowerCase().includes(search.toLowerCase()) ||
    r.employee_code.toLowerCase().includes(search.toLowerCase()) ||
    r.department.toLowerCase().includes(search.toLowerCase())
  )

  // Stats
  const checkedIn = mockRecords.filter(r => r.status === 'checked_in').length
  const checkedOut = mockRecords.filter(r => r.status === 'checked_out').length
  const onLeave = mockRecords.filter(r => r.status === 'on_leave').length
  const absent = mockRecords.filter(r => r.status === 'absent').length
  const withinGeofence = mockRecords.filter(r => r.is_within_geofence).length
  const avgHours = mockRecords.filter(r => r.total_hours).reduce((sum, r) => sum + (r.total_hours || 0), 0) / mockRecords.filter(r => r.total_hours).length || 0

  return (
    <div className="space-y-6">
      <PageHeader
        title="Mobile Attendance"
        description="Track employee attendance from mobile devices"
        actions={
          <div className="flex gap-2">
            <Link href="/mobile">
              <Button variant="outline">
                <ChevronLeft className="h-4 w-4 mr-1" />
                Back
              </Button>
            </Link>
            <Button onClick={fetchAttendance} disabled={isLoading}>
              <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
          </div>
        }
      />

      {/* Stats */}
      <div className="grid gap-4 md:grid-cols-6">
        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-green-100">
                <LogIn className="h-5 w-5 text-green-600" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Checked In</p>
                <p className="text-2xl font-bold">{checkedIn}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-blue-100">
                <LogOut className="h-5 w-5 text-blue-600" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Checked Out</p>
                <p className="text-2xl font-bold">{checkedOut}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-purple-100">
                <Calendar className="h-5 w-5 text-purple-600" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">On Leave</p>
                <p className="text-2xl font-bold">{onLeave}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-red-100">
                <XCircle className="h-5 w-5 text-red-600" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Absent</p>
                <p className="text-2xl font-bold">{absent}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-teal-100">
                <MapPin className="h-5 w-5 text-teal-600" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">In Geofence</p>
                <p className="text-2xl font-bold">{withinGeofence}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-orange-100">
                <TrendingUp className="h-5 w-5 text-orange-600" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Avg Hours</p>
                <p className="text-2xl font-bold">{avgHours.toFixed(1)}h</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="pt-4">
          <div className="flex flex-wrap gap-4">
            <div className="flex-1 min-w-[200px]">
              <div className="relative">
                <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search employees..."
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  className="pl-8"
                />
              </div>
            </div>
            <div>
              <Input
                type="date"
                value={dateFilter}
                onChange={(e) => setDateFilter(e.target.value)}
                className="w-[160px]"
              />
            </div>
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-[150px]">
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="checked_in">Checked In</SelectItem>
                <SelectItem value="checked_out">Checked Out</SelectItem>
                <SelectItem value="on_leave">On Leave</SelectItem>
                <SelectItem value="absent">Absent</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Loading */}
      {isLoading && (
        <Card className="p-8 flex items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <span className="ml-2">Loading attendance records...</span>
        </Card>
      )}

      {/* Attendance Table */}
      {!isLoading && (
        <Card>
          <CardContent className="p-0">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Employee</TableHead>
                  <TableHead>Department</TableHead>
                  <TableHead>Check In</TableHead>
                  <TableHead>Check Out</TableHead>
                  <TableHead>Hours</TableHead>
                  <TableHead>Geofence</TableHead>
                  <TableHead>Verification</TableHead>
                  <TableHead>Status</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredRecords.map((record) => {
                  const status = statusConfig[record.status] || statusConfig.absent
                  const verification = verificationConfig[record.verification_method] || verificationConfig.location

                  return (
                    <TableRow
                      key={record.id}
                      className="cursor-pointer hover:bg-muted/50"
                      onClick={() => { setSelectedRecord(record); setDetailDialogOpen(true); }}
                    >
                      <TableCell>
                        <div className="flex items-center gap-3">
                          <Avatar className="h-8 w-8">
                            <AvatarFallback className="text-xs">
                              {record.employee_name.split(' ').map(n => n[0]).join('')}
                            </AvatarFallback>
                          </Avatar>
                          <div>
                            <p className="font-medium">{record.employee_name}</p>
                            <p className="text-xs text-muted-foreground">{record.employee_code}</p>
                          </div>
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-1 text-sm">
                          <Building className="h-3 w-3 text-muted-foreground" />
                          {record.department}
                        </div>
                      </TableCell>
                      <TableCell>
                        {record.check_in_time ? (
                          <div className="text-sm">
                            <p className="font-medium">{new Date(record.check_in_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</p>
                            {record.check_in_location && (
                              <p className="text-xs text-muted-foreground truncate max-w-[150px]">{record.check_in_location.address}</p>
                            )}
                          </div>
                        ) : (
                          <span className="text-muted-foreground">-</span>
                        )}
                      </TableCell>
                      <TableCell>
                        {record.check_out_time ? (
                          <div className="text-sm">
                            <p className="font-medium">{new Date(record.check_out_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</p>
                          </div>
                        ) : (
                          <span className="text-muted-foreground">-</span>
                        )}
                      </TableCell>
                      <TableCell>
                        <span className="font-medium">{formatDuration(record.total_hours)}</span>
                      </TableCell>
                      <TableCell>
                        {record.is_within_geofence ? (
                          <Badge variant="outline" className="text-green-700 border-green-300">
                            <CheckCircle className="h-3 w-3 mr-1" />
                            Yes
                          </Badge>
                        ) : (
                          <Badge variant="outline" className="text-red-700 border-red-300">
                            <AlertTriangle className="h-3 w-3 mr-1" />
                            No
                          </Badge>
                        )}
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-1 text-sm">
                          {verification.icon}
                          <span>{verification.label}</span>
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge className={status.color}>
                          {status.icon}
                          <span className="ml-1">{status.label}</span>
                        </Badge>
                      </TableCell>
                    </TableRow>
                  )
                })}
              </TableBody>
            </Table>

            {filteredRecords.length === 0 && (
              <div className="text-center py-12">
                <Users className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                <p className="text-muted-foreground">No attendance records found</p>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Detail Dialog */}
      <Dialog open={detailDialogOpen} onOpenChange={setDetailDialogOpen}>
        <DialogContent className="sm:max-w-[500px]">
          <DialogHeader>
            <DialogTitle>Attendance Details</DialogTitle>
            <DialogDescription>
              {selectedRecord?.date && new Date(selectedRecord.date).toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
            </DialogDescription>
          </DialogHeader>
          {selectedRecord && (
            <div className="space-y-4 py-4">
              {/* Employee Info */}
              <div className="flex items-center gap-4 pb-4 border-b">
                <Avatar className="h-12 w-12">
                  <AvatarFallback>
                    {selectedRecord.employee_name.split(' ').map(n => n[0]).join('')}
                  </AvatarFallback>
                </Avatar>
                <div>
                  <p className="font-medium text-lg">{selectedRecord.employee_name}</p>
                  <p className="text-sm text-muted-foreground">{selectedRecord.employee_code} | {selectedRecord.department}</p>
                </div>
              </div>

              {/* Times */}
              <div className="grid grid-cols-2 gap-4">
                <div className="p-3 rounded-lg bg-green-50 border border-green-200">
                  <div className="flex items-center gap-2 mb-1">
                    <LogIn className="h-4 w-4 text-green-600" />
                    <span className="text-sm font-medium text-green-800">Check In</span>
                  </div>
                  {selectedRecord.check_in_time ? (
                    <>
                      <p className="text-xl font-bold text-green-900">
                        {new Date(selectedRecord.check_in_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </p>
                      {selectedRecord.check_in_location && (
                        <p className="text-xs text-green-700 mt-1 truncate">
                          {selectedRecord.check_in_location.address}
                        </p>
                      )}
                    </>
                  ) : (
                    <p className="text-muted-foreground">Not checked in</p>
                  )}
                </div>
                <div className="p-3 rounded-lg bg-blue-50 border border-blue-200">
                  <div className="flex items-center gap-2 mb-1">
                    <LogOut className="h-4 w-4 text-blue-600" />
                    <span className="text-sm font-medium text-blue-800">Check Out</span>
                  </div>
                  {selectedRecord.check_out_time ? (
                    <>
                      <p className="text-xl font-bold text-blue-900">
                        {new Date(selectedRecord.check_out_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </p>
                      {selectedRecord.check_out_location && (
                        <p className="text-xs text-blue-700 mt-1 truncate">
                          {selectedRecord.check_out_location.address}
                        </p>
                      )}
                    </>
                  ) : (
                    <p className="text-muted-foreground">Not checked out</p>
                  )}
                </div>
              </div>

              {/* Details */}
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="text-muted-foreground">Total Hours</p>
                  <p className="font-medium text-lg">{formatDuration(selectedRecord.total_hours)}</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Device</p>
                  <p className="font-medium">{selectedRecord.device_name}</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Verification</p>
                  <div className="flex items-center gap-1">
                    {verificationConfig[selectedRecord.verification_method]?.icon}
                    <span className="font-medium">{verificationConfig[selectedRecord.verification_method]?.label}</span>
                  </div>
                </div>
                <div>
                  <p className="text-muted-foreground">Geofence</p>
                  {selectedRecord.is_within_geofence ? (
                    <span className="text-green-600 font-medium">Within office area</span>
                  ) : (
                    <span className="text-red-600 font-medium">Outside office area</span>
                  )}
                </div>
              </div>

              {/* Status */}
              <div className="flex items-center justify-between pt-4 border-t">
                <span className="text-muted-foreground">Status</span>
                <Badge className={statusConfig[selectedRecord.status]?.color + ' text-sm'}>
                  {statusConfig[selectedRecord.status]?.icon}
                  <span className="ml-1">{statusConfig[selectedRecord.status]?.label}</span>
                </Badge>
              </div>
            </div>
          )}
          <DialogFooter>
            <Button variant="outline" onClick={() => setDetailDialogOpen(false)}>
              Close
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Info Card */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2">
            <Smartphone className="h-4 w-4 text-primary" />
            Mobile Attendance Features
          </CardTitle>
        </CardHeader>
        <CardContent className="text-sm text-muted-foreground space-y-2">
          <p>
            <strong>Geofencing</strong> verifies that employees check in/out from designated office locations,
            helping ensure accurate attendance tracking.
          </p>
          <p>
            <strong>Multiple verification methods</strong> are supported including biometric (Face ID/Fingerprint),
            photo capture, PIN, and location-based verification.
          </p>
          <p>
            <strong>Offline support</strong> allows employees to mark attendance even without internet.
            Records are synced automatically when connectivity is restored.
          </p>
        </CardContent>
      </Card>
    </div>
  )
}
