'use client';

/**
 * My Leave Requests Page
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
import leaveApi from '@/lib/api/leave';
import type { LeaveRequest, LeaveStatus, LeaveTypeConfig } from '@/types/leave';

const statusColors: Record<LeaveStatus, string> = {
  pending: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300',
  approved: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300',
  rejected: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300',
  cancelled: 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300',
};

const statusLabels: Record<LeaveStatus, string> = {
  pending: 'Pending',
  approved: 'Approved',
  rejected: 'Rejected',
  cancelled: 'Cancelled',
};

export default function MyLeaveRequestsPage() {
  const router = useRouter();
  const [requests, setRequests] = useState<LeaveRequest[]>([]);
  const [leaveTypes, setLeaveTypes] = useState<LeaveTypeConfig[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [total, setTotal] = useState(0);

  // Filters
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [leaveTypeFilter, setLeaveTypeFilter] = useState<string>('');
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 10;

  // Cancel dialog
  const [cancelDialogOpen, setCancelDialogOpen] = useState(false);
  const [selectedRequest, setSelectedRequest] = useState<LeaveRequest | null>(null);
  const [cancelReason, setCancelReason] = useState('');
  const [isCancelling, setIsCancelling] = useState(false);

  // Detail dialog
  const [detailDialogOpen, setDetailDialogOpen] = useState(false);
  const [detailRequest, setDetailRequest] = useState<LeaveRequest | null>(null);

  const loadRequests = useCallback(async () => {
    setIsLoading(true);
    try {
      const response = await leaveApi.getMyRequests({
        status: (statusFilter as LeaveStatus) || undefined,
        leave_type_id: leaveTypeFilter || undefined,
        skip: (currentPage - 1) * pageSize,
        limit: pageSize,
      });
      setRequests(response.items);
      setTotal(response.total);
    } catch (error) {
      console.error('Failed to load requests:', error);
    } finally {
      setIsLoading(false);
    }
  }, [statusFilter, leaveTypeFilter, currentPage]);

  const loadLeaveTypes = useCallback(async () => {
    try {
      const types = await leaveApi.getLeaveTypes();
      setLeaveTypes(types);
    } catch (error) {
      console.error('Failed to load leave types:', error);
    }
  }, []);

  useEffect(() => {
    loadLeaveTypes();
  }, [loadLeaveTypes]);

  useEffect(() => {
    loadRequests();
  }, [loadRequests]);

  const openCancelDialog = (request: LeaveRequest) => {
    setSelectedRequest(request);
    setCancelReason('');
    setCancelDialogOpen(true);
  };

  const handleCancelRequest = async () => {
    if (!selectedRequest || !cancelReason.trim()) return;

    setIsCancelling(true);
    try {
      await leaveApi.cancelRequest(selectedRequest.id, cancelReason.trim());
      setCancelDialogOpen(false);
      loadRequests();
    } catch (error) {
      console.error('Failed to cancel request:', error);
    } finally {
      setIsCancelling(false);
    }
  };

  const openDetailDialog = (request: LeaveRequest) => {
    setDetailRequest(request);
    setDetailDialogOpen(true);
  };

  const formatDateRange = (start: string, end: string) => {
    const startDate = new Date(start);
    const endDate = new Date(end);
    if (start === end) {
      return startDate.toLocaleDateString();
    }
    return `${startDate.toLocaleDateString()} - ${endDate.toLocaleDateString()}`;
  };

  const totalPages = Math.ceil(total / pageSize);

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
              <h1 className="text-2xl font-bold tracking-tight">My Leave Requests</h1>
              <p className="text-muted-foreground">
                View and manage your leave applications
              </p>
            </div>
          </div>
          <Button onClick={() => router.push('/leave/apply')}>
            <svg className="mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            Apply Leave
          </Button>
        </div>

        {/* Filters */}
        <div className="flex gap-4">
          <Select value={statusFilter} onValueChange={setStatusFilter}>
            <SelectTrigger className="w-[150px]">
              <SelectValue placeholder="All Status" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="">All Status</SelectItem>
              {Object.entries(statusLabels).map(([value, label]) => (
                <SelectItem key={value} value={value}>
                  {label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          <Select value={leaveTypeFilter} onValueChange={setLeaveTypeFilter}>
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder="All Leave Types" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="">All Leave Types</SelectItem>
              {leaveTypes.map((type) => (
                <SelectItem key={type.id} value={type.id}>
                  {type.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Table */}
        <div className="rounded-lg border bg-card">
          {isLoading ? (
            <div className="p-8 text-center">
              <div className="h-8 w-8 mx-auto animate-spin rounded-full border-4 border-primary border-t-transparent" />
              <p className="mt-2 text-muted-foreground">Loading requests...</p>
            </div>
          ) : requests.length === 0 ? (
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
                  d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
                />
              </svg>
              <h3 className="mt-2 font-medium">No leave requests found</h3>
              <p className="text-sm text-muted-foreground">
                {statusFilter || leaveTypeFilter
                  ? 'Try adjusting your filters'
                  : 'Get started by applying for leave'}
              </p>
            </div>
          ) : (
            <>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Leave Type</TableHead>
                    <TableHead>Dates</TableHead>
                    <TableHead>Days</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Applied</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {requests.map((request) => (
                    <TableRow key={request.id}>
                      <TableCell className="font-medium">
                        {request.leave_type_name}
                      </TableCell>
                      <TableCell>
                        {formatDateRange(request.start_date, request.end_date)}
                      </TableCell>
                      <TableCell>{request.total_days}</TableCell>
                      <TableCell>
                        <Badge variant="secondary" className={statusColors[request.status]}>
                          {statusLabels[request.status]}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        {new Date(request.applied_at).toLocaleDateString()}
                      </TableCell>
                      <TableCell className="text-right">
                        <div className="flex justify-end gap-2">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => openDetailDialog(request)}
                          >
                            View
                          </Button>
                          {request.status === 'pending' && (
                            <Button
                              variant="ghost"
                              size="sm"
                              className="text-destructive hover:text-destructive"
                              onClick={() => openCancelDialog(request)}
                            >
                              Cancel
                            </Button>
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

      {/* Cancel Dialog */}
      <Dialog open={cancelDialogOpen} onOpenChange={setCancelDialogOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Cancel Leave Request</DialogTitle>
            <DialogDescription>
              Please provide a reason for cancelling this leave request.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="cancelReason">Reason for cancellation *</Label>
              <Textarea
                id="cancelReason"
                placeholder="Enter the reason..."
                value={cancelReason}
                onChange={(e) => setCancelReason(e.target.value)}
                disabled={isCancelling}
                rows={3}
              />
            </div>
          </div>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setCancelDialogOpen(false)}
              disabled={isCancelling}
            >
              Close
            </Button>
            <Button
              variant="destructive"
              onClick={handleCancelRequest}
              disabled={!cancelReason.trim() || isCancelling}
            >
              {isCancelling ? 'Cancelling...' : 'Cancel Request'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Detail Dialog */}
      <Dialog open={detailDialogOpen} onOpenChange={setDetailDialogOpen}>
        <DialogContent className="sm:max-w-lg">
          <DialogHeader>
            <DialogTitle>Leave Request Details</DialogTitle>
          </DialogHeader>
          {detailRequest && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <dt className="text-sm text-muted-foreground">Leave Type</dt>
                  <dd className="font-medium">{detailRequest.leave_type_name}</dd>
                </div>
                <div>
                  <dt className="text-sm text-muted-foreground">Status</dt>
                  <dd>
                    <Badge variant="secondary" className={statusColors[detailRequest.status]}>
                      {statusLabels[detailRequest.status]}
                    </Badge>
                  </dd>
                </div>
                <div>
                  <dt className="text-sm text-muted-foreground">Start Date</dt>
                  <dd className="font-medium">
                    {new Date(detailRequest.start_date).toLocaleDateString()}
                    {detailRequest.start_day_type !== 'full' && (
                      <span className="ml-1 text-muted-foreground">
                        ({detailRequest.start_day_type.replace('_', ' ')})
                      </span>
                    )}
                  </dd>
                </div>
                <div>
                  <dt className="text-sm text-muted-foreground">End Date</dt>
                  <dd className="font-medium">
                    {new Date(detailRequest.end_date).toLocaleDateString()}
                    {detailRequest.end_day_type !== 'full' && (
                      <span className="ml-1 text-muted-foreground">
                        ({detailRequest.end_day_type.replace('_', ' ')})
                      </span>
                    )}
                  </dd>
                </div>
                <div>
                  <dt className="text-sm text-muted-foreground">Total Days</dt>
                  <dd className="font-medium">{detailRequest.total_days}</dd>
                </div>
                <div>
                  <dt className="text-sm text-muted-foreground">Applied On</dt>
                  <dd className="font-medium">
                    {new Date(detailRequest.applied_at).toLocaleString()}
                  </dd>
                </div>
              </div>

              <div>
                <dt className="text-sm text-muted-foreground">Reason</dt>
                <dd className="mt-1 p-3 rounded-lg bg-muted">{detailRequest.reason}</dd>
              </div>

              {detailRequest.status === 'approved' && detailRequest.approver_name && (
                <div>
                  <dt className="text-sm text-muted-foreground">Approved By</dt>
                  <dd className="font-medium">
                    {detailRequest.approver_name}
                    {detailRequest.approved_at && (
                      <span className="ml-2 text-muted-foreground text-sm">
                        on {new Date(detailRequest.approved_at).toLocaleString()}
                      </span>
                    )}
                  </dd>
                </div>
              )}

              {detailRequest.status === 'rejected' && (
                <div>
                  <dt className="text-sm text-muted-foreground">Rejection Reason</dt>
                  <dd className="mt-1 p-3 rounded-lg bg-destructive/10 text-destructive">
                    {detailRequest.rejection_reason || 'No reason provided'}
                  </dd>
                </div>
              )}

              {detailRequest.status === 'cancelled' && (
                <div>
                  <dt className="text-sm text-muted-foreground">Cancellation Reason</dt>
                  <dd className="mt-1 p-3 rounded-lg bg-muted">
                    {detailRequest.cancellation_reason || 'No reason provided'}
                  </dd>
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
