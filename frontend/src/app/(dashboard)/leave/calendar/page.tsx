'use client';

/**
 * Team Leave Calendar Page
 */

import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { DashboardLayout } from '@/components/layout/dashboard-layout';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import leaveApi from '@/lib/api/leave';
import type { TeamLeaveCalendarEntry, LeaveStatus } from '@/types/leave';

const statusColors: Record<LeaveStatus, string> = {
  pending: 'bg-yellow-200 border-yellow-400',
  approved: 'bg-green-200 border-green-400',
  rejected: 'bg-red-200 border-red-400',
  cancelled: 'bg-gray-200 border-gray-400',
};

const daysOfWeek = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
const monthNames = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December'
];

export default function TeamLeaveCalendarPage() {
  const router = useRouter();
  const [currentDate, setCurrentDate] = useState(new Date());
  const [calendarEntries, setCalendarEntries] = useState<TeamLeaveCalendarEntry[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const loadCalendarData = useCallback(async () => {
    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();
    const startDate = new Date(year, month, 1).toISOString().split('T')[0];
    const endDate = new Date(year, month + 1, 0).toISOString().split('T')[0];

    setIsLoading(true);
    try {
      const data = await leaveApi.getTeamCalendar(startDate, endDate);
      setCalendarEntries(data);
    } catch (error) {
      console.error('Failed to load calendar data:', error);
    } finally {
      setIsLoading(false);
    }
  }, [currentDate]);

  useEffect(() => {
    loadCalendarData();
  }, [loadCalendarData]);

  const getCalendarDays = () => {
    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const daysInMonth = lastDay.getDate();
    const startPadding = firstDay.getDay();

    const days: (number | null)[] = [];

    // Add empty cells for days before the first of the month
    for (let i = 0; i < startPadding; i++) {
      days.push(null);
    }

    // Add days of the month
    for (let i = 1; i <= daysInMonth; i++) {
      days.push(i);
    }

    return days;
  };

  const getEntriesForDate = (day: number) => {
    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();
    const dateStr = new Date(year, month, day).toISOString().split('T')[0];

    return calendarEntries.filter((entry) => {
      const start = new Date(entry.start_date);
      const end = new Date(entry.end_date);
      const current = new Date(dateStr);
      return current >= start && current <= end && entry.status !== 'rejected' && entry.status !== 'cancelled';
    });
  };

  const navigateMonth = (direction: -1 | 1) => {
    const newDate = new Date(currentDate);
    newDate.setMonth(newDate.getMonth() + direction);
    setCurrentDate(newDate);
  };

  const goToToday = () => {
    setCurrentDate(new Date());
  };

  const isToday = (day: number) => {
    const today = new Date();
    return (
      day === today.getDate() &&
      currentDate.getMonth() === today.getMonth() &&
      currentDate.getFullYear() === today.getFullYear()
    );
  };

  const calendarDays = getCalendarDays();

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" onClick={() => router.push('/leave')}>
            <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </Button>
          <div>
            <h1 className="text-2xl font-bold tracking-tight">Team Leave Calendar</h1>
            <p className="text-muted-foreground">
              View team members who are on leave
            </p>
          </div>
        </div>

        {/* Calendar */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>
                {monthNames[currentDate.getMonth()]} {currentDate.getFullYear()}
              </CardTitle>
              <div className="flex items-center gap-2">
                <Button variant="outline" size="sm" onClick={goToToday}>
                  Today
                </Button>
                <Button variant="outline" size="icon" onClick={() => navigateMonth(-1)}>
                  <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                  </svg>
                </Button>
                <Button variant="outline" size="icon" onClick={() => navigateMonth(1)}>
                  <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </Button>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="p-8 text-center">
                <div className="h-8 w-8 mx-auto animate-spin rounded-full border-4 border-primary border-t-transparent" />
                <p className="mt-2 text-muted-foreground">Loading calendar...</p>
              </div>
            ) : (
              <>
                {/* Days of week header */}
                <div className="grid grid-cols-7 gap-px bg-muted mb-px">
                  {daysOfWeek.map((day) => (
                    <div
                      key={day}
                      className="bg-background p-2 text-center text-sm font-medium text-muted-foreground"
                    >
                      {day}
                    </div>
                  ))}
                </div>

                {/* Calendar grid */}
                <div className="grid grid-cols-7 gap-px bg-muted">
                  {calendarDays.map((day, index) => {
                    const entries = day ? getEntriesForDate(day) : [];

                    return (
                      <div
                        key={index}
                        className={`bg-background min-h-[100px] p-2 ${
                          day === null ? 'bg-muted/50' : ''
                        }`}
                      >
                        {day !== null && (
                          <>
                            <div
                              className={`text-sm font-medium mb-1 ${
                                isToday(day)
                                  ? 'bg-primary text-primary-foreground rounded-full w-7 h-7 flex items-center justify-center'
                                  : ''
                              }`}
                            >
                              {day}
                            </div>
                            <div className="space-y-1">
                              {entries.slice(0, 3).map((entry, i) => (
                                <div
                                  key={i}
                                  className={`text-xs px-1 py-0.5 rounded truncate border-l-2 ${
                                    statusColors[entry.status]
                                  }`}
                                  title={`${entry.employee_name} - ${entry.leave_type}`}
                                >
                                  {entry.employee_name.split(' ')[0]}
                                </div>
                              ))}
                              {entries.length > 3 && (
                                <div className="text-xs text-muted-foreground">
                                  +{entries.length - 3} more
                                </div>
                              )}
                            </div>
                          </>
                        )}
                      </div>
                    );
                  })}
                </div>

                {/* Legend */}
                <div className="flex gap-4 mt-4 pt-4 border-t">
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded bg-green-200 border-l-2 border-green-400" />
                    <span className="text-sm text-muted-foreground">Approved</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded bg-yellow-200 border-l-2 border-yellow-400" />
                    <span className="text-sm text-muted-foreground">Pending</span>
                  </div>
                </div>
              </>
            )}
          </CardContent>
        </Card>

        {/* Team on Leave Today */}
        <Card>
          <CardHeader>
            <CardTitle>Team on Leave Today</CardTitle>
          </CardHeader>
          <CardContent>
            {(() => {
              const today = new Date().toISOString().split('T')[0];
              const onLeaveToday = calendarEntries.filter((entry) => {
                const start = new Date(entry.start_date);
                const end = new Date(entry.end_date);
                const current = new Date(today);
                return current >= start && current <= end && entry.status === 'approved';
              });

              if (onLeaveToday.length === 0) {
                return (
                  <p className="text-sm text-muted-foreground">
                    No team members on leave today
                  </p>
                );
              }

              return (
                <div className="flex flex-wrap gap-2">
                  {onLeaveToday.map((entry, i) => (
                    <Badge key={i} variant="secondary">
                      {entry.employee_name} - {entry.leave_type}
                    </Badge>
                  ))}
                </div>
              );
            })()}
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}
