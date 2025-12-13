'use client';

/**
 * Resource Utilization Report Page
 */

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { DashboardLayout } from '@/components/layout/dashboard-layout';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import projectsApi from '@/lib/api/projects';

interface UtilizationData {
  employee_id: string;
  employee_name: string;
  allocated_hours: number;
  actual_hours: number;
  utilization_rate: number;
  projects: string[];
}

export default function ResourceUtilizationPage() {
  const [data, setData] = useState<UtilizationData[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  // Date range - default to current month
  const now = new Date();
  const firstDay = new Date(now.getFullYear(), now.getMonth(), 1);
  const lastDay = new Date(now.getFullYear(), now.getMonth() + 1, 0);
  const [startDate, setStartDate] = useState(firstDay.toISOString().split('T')[0]);
  const [endDate, setEndDate] = useState(lastDay.toISOString().split('T')[0]);

  const loadData = async () => {
    setIsLoading(true);
    try {
      const result = await projectsApi.getResourceUtilization(startDate, endDate);
      setData(result);
    } catch (error) {
      console.error('Failed to load data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Calculate summary stats
  const stats = {
    totalEmployees: data.length,
    avgUtilization: data.length > 0
      ? Math.round(data.reduce((sum, d) => sum + d.utilization_rate, 0) / data.length)
      : 0,
    underUtilized: data.filter((d) => d.utilization_rate < 80).length,
    overUtilized: data.filter((d) => d.utilization_rate > 100).length,
  };

  const getUtilizationColor = (rate: number) => {
    if (rate > 100) return 'text-red-600 bg-red-50';
    if (rate >= 80) return 'text-green-600 bg-green-50';
    if (rate >= 50) return 'text-yellow-600 bg-yellow-50';
    return 'text-gray-600 bg-gray-50';
  };

  const getUtilizationLabel = (rate: number) => {
    if (rate > 100) return 'Over-utilized';
    if (rate >= 80) return 'Optimal';
    if (rate >= 50) return 'Under-utilized';
    return 'Low';
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center gap-4">
          <Link href="/projects">
            <Button variant="ghost" size="icon">
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
            </Button>
          </Link>
          <div>
            <h1 className="text-2xl font-bold tracking-tight">Resource Utilization</h1>
            <p className="text-muted-foreground">
              Team utilization and capacity analysis
            </p>
          </div>
        </div>

        {/* Date Range */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Report Period</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-end gap-4">
              <div className="space-y-2">
                <Label htmlFor="start_date">From</Label>
                <Input
                  id="start_date"
                  type="date"
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="end_date">To</Label>
                <Input
                  id="end_date"
                  type="date"
                  value={endDate}
                  onChange={(e) => setEndDate(e.target.value)}
                />
              </div>
              <Button onClick={loadData} disabled={isLoading}>
                {isLoading ? 'Loading...' : 'Generate Report'}
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Summary Stats */}
        <div className="grid gap-4 md:grid-cols-4">
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Team Members</CardDescription>
              <CardTitle className="text-2xl">{stats.totalEmployees}</CardTitle>
            </CardHeader>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Avg Utilization</CardDescription>
              <CardTitle className={`text-2xl ${stats.avgUtilization >= 80 ? 'text-green-600' : 'text-yellow-600'}`}>
                {stats.avgUtilization}%
              </CardTitle>
            </CardHeader>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Under-utilized</CardDescription>
              <CardTitle className="text-2xl text-yellow-600">{stats.underUtilized}</CardTitle>
            </CardHeader>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Over-utilized</CardDescription>
              <CardTitle className="text-2xl text-red-600">{stats.overUtilized}</CardTitle>
            </CardHeader>
          </Card>
        </div>

        {/* Utilization Table */}
        <Card>
          <CardHeader>
            <CardTitle>Team Utilization</CardTitle>
            <CardDescription>
              {new Date(startDate).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' })}
              {' - '}
              {new Date(endDate).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' })}
            </CardDescription>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="py-8 text-center">
                <div className="h-8 w-8 mx-auto animate-spin rounded-full border-4 border-primary border-t-transparent" />
                <p className="mt-2 text-muted-foreground">Loading data...</p>
              </div>
            ) : data.length === 0 ? (
              <p className="text-sm text-muted-foreground text-center py-8">No data found for the selected period</p>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Employee</TableHead>
                    <TableHead>Allocated Hours</TableHead>
                    <TableHead>Actual Hours</TableHead>
                    <TableHead>Utilization</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Projects</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {data.map((row) => (
                    <TableRow key={row.employee_id}>
                      <TableCell className="font-medium">{row.employee_name}</TableCell>
                      <TableCell>{row.allocated_hours}h</TableCell>
                      <TableCell>{row.actual_hours}h</TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <div className="w-20 h-2 bg-muted rounded-full overflow-hidden">
                            <div
                              className={`h-full transition-all ${
                                row.utilization_rate > 100 ? 'bg-red-500' :
                                row.utilization_rate >= 80 ? 'bg-green-500' :
                                row.utilization_rate >= 50 ? 'bg-yellow-500' : 'bg-gray-400'
                              }`}
                              style={{ width: `${Math.min(row.utilization_rate, 100)}%` }}
                            />
                          </div>
                          <span className={`text-sm font-medium ${
                            row.utilization_rate > 100 ? 'text-red-600' :
                            row.utilization_rate >= 80 ? 'text-green-600' : 'text-yellow-600'
                          }`}>
                            {row.utilization_rate}%
                          </span>
                        </div>
                      </TableCell>
                      <TableCell>
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getUtilizationColor(row.utilization_rate)}`}>
                          {getUtilizationLabel(row.utilization_rate)}
                        </span>
                      </TableCell>
                      <TableCell>
                        <div className="max-w-[200px] truncate text-sm text-muted-foreground">
                          {row.projects.join(', ') || '—'}
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>

        {/* Legend */}
        <Card>
          <CardContent className="py-4">
            <div className="flex gap-6 text-sm">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-green-500" />
                <span>Optimal (80-100%)</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-yellow-500" />
                <span>Under-utilized (50-80%)</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-gray-400" />
                <span>Low (&lt;50%)</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-red-500" />
                <span>Over-utilized (&gt;100%)</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}
