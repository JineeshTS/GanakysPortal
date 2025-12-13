'use client';

/**
 * Holiday Calendar Page
 */

import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { DashboardLayout } from '@/components/layout/dashboard-layout';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import leaveApi from '@/lib/api/leave';
import type { Holiday } from '@/types/leave';

const holidayTypeColors: Record<string, string> = {
  national: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300',
  regional: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300',
  optional: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300',
};

const monthNames = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December'
];

export default function HolidayCalendarPage() {
  const router = useRouter();
  const [holidays, setHolidays] = useState<Holiday[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedYear, setSelectedYear] = useState(new Date().getFullYear());

  const loadHolidays = useCallback(async () => {
    setIsLoading(true);
    try {
      const data = await leaveApi.getHolidays(selectedYear);
      setHolidays(data);
    } catch (error) {
      console.error('Failed to load holidays:', error);
    } finally {
      setIsLoading(false);
    }
  }, [selectedYear]);

  useEffect(() => {
    loadHolidays();
  }, [loadHolidays]);

  const groupedHolidays = holidays.reduce((acc, holiday) => {
    const month = new Date(holiday.date).getMonth();
    if (!acc[month]) {
      acc[month] = [];
    }
    acc[month].push(holiday);
    return acc;
  }, {} as Record<number, Holiday[]>);

  const upcomingHolidays = holidays
    .filter((h) => new Date(h.date) >= new Date())
    .slice(0, 5);

  const years = [
    new Date().getFullYear() - 1,
    new Date().getFullYear(),
    new Date().getFullYear() + 1,
  ];

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="icon" onClick={() => router.push('/leave')}>
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
            </Button>
            <div>
              <h1 className="text-2xl font-bold tracking-tight">Holiday Calendar</h1>
              <p className="text-muted-foreground">
                View company holidays for the year
              </p>
            </div>
          </div>
          <Select
            value={String(selectedYear)}
            onValueChange={(v) => setSelectedYear(parseInt(v))}
          >
            <SelectTrigger className="w-[120px]">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {years.map((year) => (
                <SelectItem key={year} value={String(year)}>
                  {year}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div className="grid gap-6 lg:grid-cols-4">
          {/* Upcoming Holidays */}
          <Card className="lg:col-span-1">
            <CardHeader>
              <CardTitle>Upcoming Holidays</CardTitle>
              <CardDescription>Next public holidays</CardDescription>
            </CardHeader>
            <CardContent>
              {isLoading ? (
                <div className="space-y-3">
                  {[1, 2, 3].map((i) => (
                    <div key={i} className="animate-pulse">
                      <div className="h-4 w-24 bg-muted rounded mb-1" />
                      <div className="h-3 w-32 bg-muted rounded" />
                    </div>
                  ))}
                </div>
              ) : upcomingHolidays.length === 0 ? (
                <p className="text-sm text-muted-foreground">
                  No upcoming holidays this year
                </p>
              ) : (
                <div className="space-y-4">
                  {upcomingHolidays.map((holiday) => {
                    const date = new Date(holiday.date);
                    const isThisWeek = (date.getTime() - new Date().getTime()) < 7 * 24 * 60 * 60 * 1000;

                    return (
                      <div key={holiday.id} className="space-y-1">
                        <div className="flex items-center gap-2">
                          <span className="font-medium">{holiday.name}</span>
                          {isThisWeek && (
                            <Badge variant="secondary" className="text-xs">
                              This week
                            </Badge>
                          )}
                        </div>
                        <div className="text-sm text-muted-foreground">
                          {date.toLocaleDateString('en-US', {
                            weekday: 'short',
                            month: 'short',
                            day: 'numeric',
                          })}
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Full Holiday List */}
          <Card className="lg:col-span-3">
            <CardHeader>
              <CardTitle>All Holidays - {selectedYear}</CardTitle>
              <CardDescription>
                {holidays.length} holidays in total
              </CardDescription>
            </CardHeader>
            <CardContent>
              {isLoading ? (
                <div className="p-8 text-center">
                  <div className="h-8 w-8 mx-auto animate-spin rounded-full border-4 border-primary border-t-transparent" />
                  <p className="mt-2 text-muted-foreground">Loading holidays...</p>
                </div>
              ) : holidays.length === 0 ? (
                <div className="py-8 text-center text-muted-foreground">
                  <svg
                    className="mx-auto h-12 w-12"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
                    />
                  </svg>
                  <p className="mt-2">No holidays found for {selectedYear}</p>
                </div>
              ) : (
                <div className="space-y-6">
                  {Object.entries(groupedHolidays)
                    .sort(([a], [b]) => parseInt(a) - parseInt(b))
                    .map(([month, monthHolidays]) => (
                      <div key={month}>
                        <h3 className="font-semibold text-lg mb-3 pb-2 border-b">
                          {monthNames[parseInt(month)]}
                        </h3>
                        <div className="space-y-3">
                          {monthHolidays.map((holiday) => {
                            const date = new Date(holiday.date);
                            const isPast = date < new Date();

                            return (
                              <div
                                key={holiday.id}
                                className={`flex items-center justify-between py-2 ${
                                  isPast ? 'opacity-60' : ''
                                }`}
                              >
                                <div className="flex items-center gap-4">
                                  <div className="w-12 text-center">
                                    <div className="text-2xl font-bold">
                                      {date.getDate()}
                                    </div>
                                    <div className="text-xs text-muted-foreground uppercase">
                                      {date.toLocaleDateString('en-US', { weekday: 'short' })}
                                    </div>
                                  </div>
                                  <div>
                                    <div className="font-medium">{holiday.name}</div>
                                    {holiday.description && (
                                      <div className="text-sm text-muted-foreground">
                                        {holiday.description}
                                      </div>
                                    )}
                                  </div>
                                </div>
                                <div className="flex items-center gap-2">
                                  <Badge
                                    variant="secondary"
                                    className={holidayTypeColors[holiday.type]}
                                  >
                                    {holiday.type.charAt(0).toUpperCase() + holiday.type.slice(1)}
                                  </Badge>
                                  {holiday.is_optional && (
                                    <Badge variant="outline">Optional</Badge>
                                  )}
                                </div>
                              </div>
                            );
                          })}
                        </div>
                      </div>
                    ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Legend */}
        <Card>
          <CardContent className="py-4">
            <div className="flex flex-wrap gap-6">
              <div className="flex items-center gap-2">
                <Badge variant="secondary" className={holidayTypeColors.national}>
                  National
                </Badge>
                <span className="text-sm text-muted-foreground">
                  Mandatory holidays for all employees
                </span>
              </div>
              <div className="flex items-center gap-2">
                <Badge variant="secondary" className={holidayTypeColors.regional}>
                  Regional
                </Badge>
                <span className="text-sm text-muted-foreground">
                  Based on office location
                </span>
              </div>
              <div className="flex items-center gap-2">
                <Badge variant="secondary" className={holidayTypeColors.optional}>
                  Optional
                </Badge>
                <span className="text-sm text-muted-foreground">
                  Can be chosen from available quota
                </span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}
