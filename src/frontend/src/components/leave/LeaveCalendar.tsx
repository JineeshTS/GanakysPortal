'use client'

import * as React from 'react'
import { cn } from '@/lib/utils'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import {
  Dialog,
  DialogContent,
  DialogDescription,
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
import { formatDate, getMonthName } from '@/lib/format'
import {
  ChevronLeft,
  ChevronRight,
  Calendar,
  Sun,
  Heart,
  Umbrella,
  Star,
  Users,
  Info
} from 'lucide-react'
import type { LeaveRequest, LeaveStatus } from '@/types'

// ============================================================================
// Types
// ============================================================================

interface Holiday {
  date: string
  name: string
  type: 'national' | 'state' | 'optional' | 'restricted'
}

interface CalendarDay {
  date: Date
  isCurrentMonth: boolean
  isToday: boolean
  isWeekend: boolean
  leaves: LeaveRequest[]
  holiday?: Holiday
}

interface LeaveCalendarProps {
  leaves: LeaveRequest[]
  holidays?: Holiday[]
  teamMembers?: { id: string; name: string }[]
  selectedMember?: string
  onMemberChange?: (memberId: string) => void
  onDateClick?: (date: Date) => void
  onLeaveClick?: (leave: LeaveRequest) => void
  className?: string
}

// ============================================================================
// Constants
// ============================================================================

const DAYS_OF_WEEK = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']

const leaveTypeColors: Record<string, {
  bg: string
  text: string
  border: string
}> = {
  CL: { bg: 'bg-yellow-100', text: 'text-yellow-800', border: 'border-yellow-300' },
  SL: { bg: 'bg-red-100', text: 'text-red-800', border: 'border-red-300' },
  EL: { bg: 'bg-blue-100', text: 'text-blue-800', border: 'border-blue-300' },
  PL: { bg: 'bg-indigo-100', text: 'text-indigo-800', border: 'border-indigo-300' },
  ML: { bg: 'bg-pink-100', text: 'text-pink-800', border: 'border-pink-300' },
  PTL: { bg: 'bg-purple-100', text: 'text-purple-800', border: 'border-purple-300' },
  LWP: { bg: 'bg-gray-100', text: 'text-gray-800', border: 'border-gray-300' },
  default: { bg: 'bg-green-100', text: 'text-green-800', border: 'border-green-300' }
}

const statusColors: Record<LeaveStatus, string> = {
  pending: 'bg-yellow-500',
  approved: 'bg-green-500',
  rejected: 'bg-red-500',
  cancelled: 'bg-gray-500',
  partially_approved: 'bg-blue-500'
}

// ============================================================================
// Helper Functions
// ============================================================================

function getCalendarDays(year: number, month: number, leaves: LeaveRequest[], holidays: Holiday[]): CalendarDay[] {
  const firstDayOfMonth = new Date(year, month, 1)
  const lastDayOfMonth = new Date(year, month + 1, 0)
  const startDate = new Date(firstDayOfMonth)
  startDate.setDate(startDate.getDate() - startDate.getDay()) // Start from Sunday

  const endDate = new Date(lastDayOfMonth)
  const daysToAdd = 6 - endDate.getDay()
  endDate.setDate(endDate.getDate() + daysToAdd) // End on Saturday

  const today = new Date()
  today.setHours(0, 0, 0, 0)

  const days: CalendarDay[] = []
  const currentDate = new Date(startDate)
  const safeLeaves = leaves || []
  const safeHolidays = holidays || []

  while (currentDate <= endDate) {
    const dateStr = currentDate.toISOString().split('T')[0]

    // Find leaves for this date
    const dayLeaves = safeLeaves.filter(leave => {
      const fromDate = new Date(leave.from_date)
      const toDate = new Date(leave.to_date)
      return currentDate >= fromDate && currentDate <= toDate
    })

    // Find holiday for this date
    const holiday = safeHolidays.find(h => h.date === dateStr)

    days.push({
      date: new Date(currentDate),
      isCurrentMonth: currentDate.getMonth() === month,
      isToday: currentDate.getTime() === today.getTime(),
      isWeekend: currentDate.getDay() === 0 || currentDate.getDay() === 6,
      leaves: dayLeaves,
      holiday
    })

    currentDate.setDate(currentDate.getDate() + 1)
  }

  return days
}

function getLeaveTypeIcon(code: string): React.ElementType {
  const icons: Record<string, React.ElementType> = {
    CL: Sun,
    SL: Heart,
    EL: Umbrella,
    default: Calendar
  }
  return icons[code] || icons.default
}

// ============================================================================
// Leave Calendar Component
// ============================================================================

export function LeaveCalendar({
  leaves,
  holidays = [],
  teamMembers,
  selectedMember,
  onMemberChange,
  onDateClick,
  onLeaveClick,
  className
}: LeaveCalendarProps) {
  const [currentDate, setCurrentDate] = React.useState(new Date())
  const [selectedDay, setSelectedDay] = React.useState<CalendarDay | null>(null)
  const [showDayDialog, setShowDayDialog] = React.useState(false)

  const year = currentDate.getFullYear()
  const month = currentDate.getMonth()

  const calendarDays = React.useMemo(() => {
    return getCalendarDays(year, month, leaves, holidays)
  }, [year, month, leaves, holidays])

  const goToPreviousMonth = () => {
    setCurrentDate(new Date(year, month - 1, 1))
  }

  const goToNextMonth = () => {
    setCurrentDate(new Date(year, month + 1, 1))
  }

  const goToToday = () => {
    setCurrentDate(new Date())
  }

  const handleDayClick = (day: CalendarDay) => {
    if (day.leaves.length > 0 || day.holiday) {
      setSelectedDay(day)
      setShowDayDialog(true)
    }
    onDateClick?.(day.date)
  }

  return (
    <>
      <Card className={className}>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <Calendar className="h-5 w-5" />
              Leave Calendar
            </CardTitle>

            {/* Team Member Filter */}
            {teamMembers && teamMembers.length > 0 && (
              <Select value={selectedMember} onValueChange={onMemberChange}>
                <SelectTrigger className="w-[200px]">
                  <Users className="h-4 w-4 mr-2" />
                  <SelectValue placeholder="All Team Members" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Team Members</SelectItem>
                  {teamMembers.map((member) => (
                    <SelectItem key={member.id} value={member.id}>
                      {member.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            )}
          </div>

          {/* Month Navigation */}
          <div className="flex items-center justify-between mt-4">
            <div className="flex items-center gap-2">
              <Button variant="outline" size="icon" onClick={goToPreviousMonth}>
                <ChevronLeft className="h-4 w-4" />
              </Button>
              <h2 className="text-lg font-semibold min-w-[150px] text-center">
                {getMonthName(month + 1)} {year}
              </h2>
              <Button variant="outline" size="icon" onClick={goToNextMonth}>
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
            <Button variant="outline" size="sm" onClick={goToToday}>
              Today
            </Button>
          </div>
        </CardHeader>

        <CardContent>
          {/* Calendar Grid */}
          <div className="border rounded-lg overflow-hidden">
            {/* Days of Week Header */}
            <div className="grid grid-cols-7 bg-muted">
              {DAYS_OF_WEEK.map((day, index) => (
                <div
                  key={day}
                  className={cn(
                    "p-2 text-center text-sm font-medium border-b",
                    (index === 0 || index === 6) && "text-muted-foreground"
                  )}
                >
                  {day}
                </div>
              ))}
            </div>

            {/* Calendar Days */}
            <div className="grid grid-cols-7">
              {calendarDays.map((day, index) => {
                const hasLeaves = day.leaves.length > 0
                const hasHoliday = !!day.holiday
                const colors = day.leaves[0]
                  ? leaveTypeColors[day.leaves[0].leave_type_code] || leaveTypeColors.default
                  : null

                return (
                  <div
                    key={index}
                    className={cn(
                      "min-h-[80px] p-1 border-b border-r cursor-pointer transition-colors",
                      "hover:bg-muted/50",
                      !day.isCurrentMonth && "bg-muted/30 text-muted-foreground",
                      day.isWeekend && day.isCurrentMonth && "bg-gray-50",
                      day.isToday && "ring-2 ring-primary ring-inset",
                      hasHoliday && "bg-orange-50"
                    )}
                    onClick={() => handleDayClick(day)}
                  >
                    {/* Date Number */}
                    <div className={cn(
                      "text-sm font-medium mb-1",
                      day.isToday && "text-primary font-bold"
                    )}>
                      {day.date.getDate()}
                    </div>

                    {/* Holiday Marker */}
                    {hasHoliday && (
                      <div className="mb-1">
                        <Badge
                          variant="outline"
                          className="text-[10px] px-1 py-0 bg-orange-100 text-orange-800 border-orange-300 truncate max-w-full"
                        >
                          <Star className="h-2 w-2 mr-1" />
                          {day.holiday?.name}
                        </Badge>
                      </div>
                    )}

                    {/* Leave Markers */}
                    {hasLeaves && (
                      <div className="space-y-0.5">
                        {day.leaves.slice(0, 2).map((leave, idx) => {
                          const leaveColors = leaveTypeColors[leave.leave_type_code] || leaveTypeColors.default
                          return (
                            <div
                              key={leave.id + idx}
                              className={cn(
                                "text-[10px] px-1 py-0.5 rounded truncate",
                                leaveColors.bg,
                                leaveColors.text,
                                "border",
                                leaveColors.border
                              )}
                              onClick={(e) => {
                                e.stopPropagation()
                                onLeaveClick?.(leave)
                              }}
                            >
                              <div className="flex items-center gap-1">
                                <span
                                  className={cn(
                                    "w-1.5 h-1.5 rounded-full",
                                    statusColors[leave.status]
                                  )}
                                />
                                <span className="truncate">{leave.employee_name}</span>
                              </div>
                            </div>
                          )
                        })}
                        {day.leaves.length > 2 && (
                          <div className="text-[10px] text-muted-foreground px-1">
                            +{day.leaves.length - 2} more
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                )
              })}
            </div>
          </div>

          {/* Legend */}
          <div className="mt-4 flex flex-wrap gap-4 text-sm">
            <div className="flex items-center gap-2">
              <span className="text-xs text-muted-foreground">Leave Types:</span>
            </div>
            {Object.entries(leaveTypeColors).filter(([k]) => k !== 'default').map(([code, colors]) => (
              <div key={code} className="flex items-center gap-1">
                <span className={cn("w-3 h-3 rounded", colors.bg, "border", colors.border)} />
                <span className="text-xs">{code}</span>
              </div>
            ))}
            <div className="flex items-center gap-1">
              <Star className="h-3 w-3 text-orange-500" />
              <span className="text-xs">Holiday</span>
            </div>
          </div>

          {/* Status Legend */}
          <div className="mt-2 flex flex-wrap gap-4 text-sm">
            <div className="flex items-center gap-2">
              <span className="text-xs text-muted-foreground">Status:</span>
            </div>
            {Object.entries(statusColors).map(([status, color]) => (
              <div key={status} className="flex items-center gap-1">
                <span className={cn("w-2 h-2 rounded-full", color)} />
                <span className="text-xs capitalize">{status.replace('_', ' ')}</span>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Day Details Dialog */}
      <Dialog open={showDayDialog} onOpenChange={setShowDayDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Calendar className="h-5 w-5" />
              {selectedDay && formatDate(selectedDay.date, { format: 'long' })}
            </DialogTitle>
            <DialogDescription>
              {selectedDay?.isToday && 'Today - '}
              {selectedDay?.isWeekend ? 'Weekend' : 'Working Day'}
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 py-4">
            {/* Holiday Info */}
            {selectedDay?.holiday && (
              <div className="p-3 bg-orange-50 border border-orange-200 rounded-lg">
                <div className="flex items-center gap-2 text-orange-800">
                  <Star className="h-4 w-4" />
                  <span className="font-medium">{selectedDay.holiday.name}</span>
                </div>
                <p className="text-sm text-orange-600 mt-1 capitalize">
                  {selectedDay.holiday.type} Holiday
                </p>
              </div>
            )}

            {/* Leaves */}
            {selectedDay?.leaves && selectedDay.leaves.length > 0 && (
              <div className="space-y-2">
                <h4 className="text-sm font-medium">Leaves on this day</h4>
                {selectedDay.leaves.map((leave) => {
                  const colors = leaveTypeColors[leave.leave_type_code] || leaveTypeColors.default
                  const Icon = getLeaveTypeIcon(leave.leave_type_code)

                  return (
                    <div
                      key={leave.id}
                      className={cn(
                        "p-3 rounded-lg border",
                        colors.bg,
                        colors.border,
                        "cursor-pointer hover:shadow-sm transition-shadow"
                      )}
                      onClick={() => {
                        onLeaveClick?.(leave)
                        setShowDayDialog(false)
                      }}
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <Icon className={cn("h-4 w-4", colors.text)} />
                          <span className="font-medium">{leave.employee_name}</span>
                        </div>
                        <Badge
                          className={cn(
                            "capitalize",
                            leave.status === 'approved' && "bg-green-500",
                            leave.status === 'pending' && "bg-yellow-500",
                            leave.status === 'rejected' && "bg-red-500"
                          )}
                        >
                          {leave.status}
                        </Badge>
                      </div>
                      <div className="mt-2 text-sm">
                        <p className={colors.text}>
                          {leave.leave_type_name} ({leave.leave_type_code})
                        </p>
                        <p className="text-muted-foreground">
                          {formatDate(leave.from_date)} - {formatDate(leave.to_date)}
                          ({leave.days} day{leave.days !== 1 ? 's' : ''})
                        </p>
                        {leave.half_day && (
                          <Badge variant="outline" className="mt-1">
                            {leave.half_day_type === 'first_half' ? 'First Half' : 'Second Half'}
                          </Badge>
                        )}
                      </div>
                    </div>
                  )
                })}
              </div>
            )}

            {/* No events */}
            {selectedDay && !selectedDay.holiday && selectedDay.leaves.length === 0 && (
              <div className="text-center py-4 text-muted-foreground">
                <Info className="h-8 w-8 mx-auto mb-2 opacity-50" />
                <p>No leaves or holidays on this day</p>
              </div>
            )}
          </div>
        </DialogContent>
      </Dialog>
    </>
  )
}

// ============================================================================
// Mini Leave Calendar Component (for dashboard)
// ============================================================================

interface MiniLeaveCalendarProps {
  leaves: LeaveRequest[]
  holidays?: Holiday[]
  className?: string
}

export function MiniLeaveCalendar({
  leaves,
  holidays = [],
  className
}: MiniLeaveCalendarProps) {
  const today = new Date()
  const year = today.getFullYear()
  const month = today.getMonth()

  const calendarDays = React.useMemo(() => {
    return getCalendarDays(year, month, leaves, holidays)
  }, [year, month, leaves, holidays])

  return (
    <Card className={className}>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium">
          {getMonthName(month + 1)} {year}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-7 gap-1">
          {/* Day Headers */}
          {DAYS_OF_WEEK.map((day) => (
            <div key={day} className="text-[10px] text-center text-muted-foreground font-medium">
              {day[0]}
            </div>
          ))}

          {/* Days */}
          {calendarDays.map((day, index) => {
            const hasLeaves = day.leaves.length > 0
            const hasHoliday = !!day.holiday

            return (
              <div
                key={index}
                className={cn(
                  "aspect-square flex items-center justify-center text-xs rounded",
                  !day.isCurrentMonth && "text-muted-foreground/50",
                  day.isToday && "bg-primary text-primary-foreground font-bold",
                  hasHoliday && !day.isToday && "bg-orange-100",
                  hasLeaves && !day.isToday && "bg-blue-100",
                  day.isWeekend && !hasHoliday && !hasLeaves && !day.isToday && "text-muted-foreground"
                )}
              >
                {day.date.getDate()}
              </div>
            )
          })}
        </div>
      </CardContent>
    </Card>
  )
}

export default LeaveCalendar
