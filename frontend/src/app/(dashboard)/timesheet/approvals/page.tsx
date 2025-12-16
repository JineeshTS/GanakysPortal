'use client';

/**
 * Timesheet Approvals Page
 */

import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { DashboardLayout } from '@/components/layout/dashboard-layout';
import { Button } from '@/components/ui/button';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Badge } from '@/components/ui/badge';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import timesheetApi from '@/lib/api/timesheet';
import type { Timesheet, TimesheetStatus, TimesheetEntry } from '@/types/timesheet';

const statusColors: Record<TimesheetStatus, string> = {
  draft: 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300',
  submitted: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300',
  approved: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300',
  rejected: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300',
};

export default function TimesheetApprovalsPage() {
  const router = useRouter();
  const [timesheets, setTimesheets] = useState<Timesheet[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [total, setTotal] = useState(0);

  // Filters
  const [statusFilter, setStatusFilter] = useState<string>('submitted');
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 10;

  // Action dialog
  const [actionDialogOpen, setActionDialogOpen] = useState(false);
  const [selectedTimesheet, setSelectedTimesheet] = useState<Timesheet | null>(null);
  const [actionType, setActionType] = useState<'approve' | 'reject'>('approve');
  const [rejectionReason, setRejectionReason] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);

  // Detail dialog
  const [detailDialogOpen, setDetailDialogOpen] = useState(false);
  const [detailTimesheet, setDetailTimesheet] = useState<Timesheet | null>(null);

  const loadTimesheets = useCallback(async () => {
    setIsLoading(true);
    try {
      const response = await timesheetApi.getTeamTimesheets({
        status: (statusFilter as TimesheetStatus) || undefined,
        skip: (currentPage - 1) * pageSize,
        limit: pageSize,
      });
      setTimesheets(response.items);
      setTotal(response.total);
    } catch (error) {
      console.error('Failed to load timesheets:', error);
    } finally {
      setIsLoading(false);
    }
  }, [statusFilter, currentPage]);

  useEffect(() => {
    loadTimesheets();
  }, [loadTimesheets]);

  const formatWeekRange = (start: string, end: string) => {
    const startDate = new Date(start);
    const endDate = new Date(end);
    return `${startDate.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })} - ${endDate.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}`;
  };

  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map((n) => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  const openActionDialog = (timesheet: Timesheet, action: 'approve' | 'reject') => {
    setSelectedTimesheet(timesheet);
    setActionType(action);
    setRejectionReason('');
    setActionDialogOpen(true);
  };

  const openDetailDialog = async (timesheet: Timesheet) => {
    try {
      const fullTimesheet = await timesheetApi.getTimesheet(timesheet.id);
      setDetailTimesheet(fullTimesheet);
      setDetailDialogOpen(true);
    } catch (error) {
      console.error('Failed to load timesheet details:', error);
    }
  };

  const handleProcessAction = async () => {
    if (!selectedTimesheet) return;
    if (actionType === 'reject' && !rejectionReason.trim()) return;

    setIsProcessing(true);
    try {
      await timesheetApi.processApproval(selectedTimesheet.id, {
        action: actionType,
        rejection_reason: actionType === 'reject' ? rejectionReason.trim() : undefined,
      });
      setActionDialogOpen(false);
      loadTimesheets();
    } catch (error) {
      console.error('Failed to process timesheet:', error);
    } finally {
      setIsProcessing(false);
    }
  };

  const groupEntriesByProject = (entries: TimesheetEntry[]) => {
    return entries.reduce((acc, entry) => {
      const key = entry.project_name || 'No Project';
      if (!acc[key]) {
        acc[key] = { hours: 0, billable_hours: 0 };
      }
      acc[key].hours += entry.hours;
      if (entry.is_billable) {
        acc[key].billable_hours += entry.hours;
      }
      return acc;
    }, {} as Record<string, { hours: number; billable_hours: number }>);
  };

  const totalPages = Math.ceil(total / pageSize);

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" onClick={() => router.push('/timesheet')}>
            <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </Button>
          <div>
            <h1 className="text-2xl font-bold tracking-tight">Timesheet Approvals</h1>
            <p className="text-muted-foreground">
              Review and approve team timesheets
            </p>
          </div>
        </div>

        {/* Filters */}
        <div className="flex gap-4">
          <Select value={statusFilter} onValueChange={setStatusFilter}>
            <SelectTrigger className="w-[150px]">
              <SelectValue placeholder="All Status" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="">All Status</SelectItem>
              <SelectItem value="submitted">Submitted</SelectItem>
              <SelectItem value="approved">Approved</SelectItem>
              <SelectItem value="rejected">Rejected</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Table */}
        <div className="rounded-lg border bg-card">
          {isLoading ? (
            <div className="p-8 text-center">
              <div className="h-8 w-8 mx-auto animate-spin rounded-full border-4 border-primary border-t-transparent" />
              <p className="mt-2 text-muted-foreground">Loading timesheets...</p>
            </div>
          ) : timesheets.length === 0 ? (
            <div className="p-8 text-center">
              <svg
                className="mx-auto h-12 w-12 text-muted-foreground"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              <h3 className="mt-2 font-medium">No pending approvals</h3>
              <p className="text-sm text-muted-foreground">
                All caught up! No timesheets waiting for your approval.
              </p>
            </div>
          ) : (
            <>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Employee</TableHead>
                    <TableHead>Week</TableHead>
                    <TableHead>Total Hours</TableHead>
                    <TableHead>Billable</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Submitted</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {timesheets.map((timesheet) => (
                    <TableRow key={timesheet.id}>
                      <TableCell>
                        <div className="flex items-center gap-3">
                          <Avatar>
                            <AvatarFallback>
                              {getInitials(timesheet.employee_name || 'NA')}
                            </AvatarFallback>
                          </Avatar>
                          <div>
                            <div className="font-medium">{timesheet.employee_name}</div>
                            <div className="text-sm text-muted-foreground">
                              {timesheet.employee_code}
                            </div>
                          </div>
                        </div>
                      </TableCell>
                      <TableCell>
                        {formatWeekRange(timesheet.week_start_date, timesheet.week_end_date)}
                      </TableCell>
                      <TableCell className="font-medium">{timesheet.total_hours}h</TableCell>
                      <TableCell className="text-green-600">{timesheet.billable_hours}h</TableCell>
                      <TableCell>
                        <Badge variant="secondary" className={statusColors[timesheet.status]}>
                          {timesheet.status.charAt(0).toUpperCase() + timesheet.status.slice(1)}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        {timesheet.submitted_at
                          ? new Date(timesheet.submitted_at).toLocaleDateString()
                          : '—'}
                      </TableCell>
                      <TableCell className="text-right">
                        <div className="flex justify-end gap-2">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => openDetailDialog(timesheet)}
                          >
                            View
                          </Button>
                          {timesheet.status === 'submitted' && (
                            <>
                              <Button
                                variant="outline"
                                size="sm"
                                className="text-green-600 hover:text-green-700"
                                onClick={() => openActionDialog(timesheet, 'approve')}
                              >
                                Approve
                              </Button>
                              <Button
                                variant="outline"
                                size="sm"
                                className="text-destructive hover:text-destructive"
                                onClick={() => openActionDialog(timesheet, 'reject')}
                              >
                                Reject
                              </Button>
                            </>
                          )}
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>

              {/* Pagination */}
              {totalPages > 1 && (
                <div className="flex items-center justify-between border-t px-4 py-3">
                  <div className="text-sm text-muted-foreground">
                    Showing {(currentPage - 1) * pageSize + 1} to{' '}
                    {Math.min(currentPage * pageSize, total)} of {total} results
                  </div>
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                      disabled={currentPage === 1}
                    >
                      Previous
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
                      disabled={currentPage === totalPages}
                    >
                      Next
                    </Button>
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      </div>

      {/* Action Dialog */}
      <Dialog open={actionDialogOpen} onOpenChange={setActionDialogOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>
              {actionType === 'approve' ? 'Approve Timesheet' : 'Reject Timesheet'}
            </DialogTitle>
            <DialogDescription>
              {actionType === 'approve'
                ? 'Are you sure you want to approve this timesheet?'
                : 'Please provide a reason for rejecting this timesheet.'}
            </DialogDescription>
          </DialogHeader>

          {selectedTimesheet && (
            <div className="space-y-4">
              <div className="rounded-lg bg-muted p-4 space-y-2">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Employee</span>
                  <span className="font-medium">{selectedTimesheet.employee_name}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Week</span>
                  <span className="font-medium">
                    {formatWeekRange(selectedTimesheet.week_start_date, selectedTimesheet.week_end_date)}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Total Hours</span>
                  <span className="font-medium">{selectedTimesheet.total_hours}h</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Billable Hours</span>
                  <span className="font-medium text-green-600">{selectedTimesheet.billable_hours}h</span>
                </div>
              </div>

              {actionType === 'reject' && (
                <div className="space-y-2">
                  <Label htmlFor="rejectionReason">Rejection Reason *</Label>
                  <Textarea
                    id="rejectionReason"
                    placeholder="Please provide a reason for rejecting this timesheet..."
                    value={rejectionReason}
                    onChange={(e) => setRejectionReason(e.target.value)}
                    disabled={isProcessing}
                    rows={3}
                  />
                </div>
              )}
            </div>
          )}

          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setActionDialogOpen(false)}
              disabled={isProcessing}
            >
              Cancel
            </Button>
            <Button
              variant={actionType === 'approve' ? 'default' : 'destructive'}
              onClick={handleProcessAction}
              disabled={isProcessing || (actionType === 'reject' && !rejectionReason.trim())}
            >
              {isProcessing
                ? 'Processing...'
                : actionType === 'approve'
                  ? 'Approve'
                  : 'Reject'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Detail Dialog */}
      <Dialog open={detailDialogOpen} onOpenChange={setDetailDialogOpen}>
        <DialogContent className="sm:max-w-2xl">
          <DialogHeader>
            <DialogTitle>Timesheet Details</DialogTitle>
            <DialogDescription>
              {detailTimesheet && formatWeekRange(detailTimesheet.week_start_date, detailTimesheet.week_end_date)}
            </DialogDescription>
          </DialogHeader>

          {detailTimesheet && (
            <div className="space-y-4 max-h-[60vh] overflow-auto">
              <div className="grid grid-cols-3 gap-4">
                <div className="rounded-lg bg-muted p-3 text-center">
                  <div className="text-2xl font-bold">{detailTimesheet.total_hours}</div>
                  <div className="text-sm text-muted-foreground">Total Hours</div>
                </div>
                <div className="rounded-lg bg-green-50 dark:bg-green-900/20 p-3 text-center">
                  <div className="text-2xl font-bold text-green-600">{detailTimesheet.billable_hours}</div>
                  <div className="text-sm text-muted-foreground">Billable</div>
                </div>
                <div className="rounded-lg bg-muted p-3 text-center">
                  <div className="text-2xl font-bold">{detailTimesheet.total_hours - detailTimesheet.billable_hours}</div>
                  <div className="text-sm text-muted-foreground">Non-Billable</div>
                </div>
              </div>

              <div>
                <h4 className="font-medium mb-2">By Project</h4>
                <div className="space-y-2">
                  {Object.entries(groupEntriesByProject(detailTimesheet.entries)).map(([project, data]) => (
                    <div key={project} className="flex justify-between py-2 border-b last:border-0">
                      <span>{project}</span>
                      <div className="flex gap-4">
                        <span className="font-medium">{data.hours}h</span>
                        <span className="text-green-600">{data.billable_hours}h billable</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {detailTimesheet.entries.length > 0 && (
                <div>
                  <h4 className="font-medium mb-2">All Entries</h4>
                  <div className="space-y-2">
                    {detailTimesheet.entries.map((entry) => (
                      <div key={entry.id} className="flex justify-between items-start py-2 border-b last:border-0">
                        <div>
                          <div className="font-medium">{entry.project_name || 'No Project'}</div>
                          <div className="text-sm text-muted-foreground">
                            {new Date(entry.date).toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' })}
                            {entry.task_name && ` - ${entry.task_name}`}
                          </div>
                          {entry.description && (
                            <div className="text-sm text-muted-foreground mt-1">{entry.description}</div>
                          )}
                        </div>
                        <div className="text-right">
                          <div className="font-medium">{entry.hours}h</div>
                          <Badge variant="secondary" className={entry.is_billable ? 'bg-green-100 text-green-800' : ''}>
                            {entry.is_billable ? 'Billable' : 'Non-billable'}
                          </Badge>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          <DialogFooter>
            <Button onClick={() => setDetailDialogOpen(false)}>Close</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </DashboardLayout>
  );
}
