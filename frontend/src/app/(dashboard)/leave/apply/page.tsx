'use client';

/**
 * Apply Leave Page
 */

import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { DashboardLayout } from '@/components/layout/dashboard-layout';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { LeaveBalanceCard } from '@/components/leave/leave-balance-card';
import leaveApi from '@/lib/api/leave';
import type { LeaveTypeConfig, LeaveBalance, DayType } from '@/types/leave';

const dayTypeLabels: Record<DayType, string> = {
  full: 'Full Day',
  first_half: 'First Half',
  second_half: 'Second Half',
};

export default function ApplyLeavePage() {
  const router = useRouter();
  const [leaveTypes, setLeaveTypes] = useState<LeaveTypeConfig[]>([]);
  const [balances, setBalances] = useState<LeaveBalance[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [calculatedDays, setCalculatedDays] = useState<number | null>(null);

  // Form state
  const [leaveTypeId, setLeaveTypeId] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [startDayType, setStartDayType] = useState<DayType>('full');
  const [endDayType, setEndDayType] = useState<DayType>('full');
  const [reason, setReason] = useState('');
  const [attachment, setAttachment] = useState<File | null>(null);

  const loadData = useCallback(async () => {
    try {
      const [typesData, balancesData] = await Promise.all([
        leaveApi.getLeaveTypes(),
        leaveApi.getMyBalances(),
      ]);
      setLeaveTypes(typesData.filter((t) => t.is_active));
      setBalances(balancesData);
    } catch (err) {
      console.error('Failed to load leave data:', err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  // Calculate days when dates change
  useEffect(() => {
    const calculateDays = async () => {
      if (!startDate || !endDate) {
        setCalculatedDays(null);
        return;
      }

      try {
        const result = await leaveApi.calculateDays(
          startDate,
          endDate,
          startDayType,
          endDayType
        );
        setCalculatedDays(result.days);
      } catch {
        // Simple calculation if API fails
        const start = new Date(startDate);
        const end = new Date(endDate);
        const diffTime = Math.abs(end.getTime() - start.getTime());
        const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1;

        let days = diffDays;
        if (startDayType !== 'full') days -= 0.5;
        if (endDayType !== 'full' && startDate !== endDate) days -= 0.5;

        setCalculatedDays(Math.max(0.5, days));
      }
    };

    calculateDays();
  }, [startDate, endDate, startDayType, endDayType]);

  const selectedLeaveType = leaveTypes.find((t) => t.id === leaveTypeId);
  const selectedBalance = balances.find((b) => b.leave_type_id === leaveTypeId);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!leaveTypeId) {
      setError('Please select a leave type');
      return;
    }
    if (!startDate || !endDate) {
      setError('Please select start and end dates');
      return;
    }
    if (!reason.trim()) {
      setError('Please provide a reason for the leave');
      return;
    }
    if (new Date(endDate) < new Date(startDate)) {
      setError('End date cannot be before start date');
      return;
    }
    if (selectedLeaveType?.requires_attachment && !attachment) {
      setError(`${selectedLeaveType.name} requires an attachment`);
      return;
    }
    if (calculatedDays && selectedBalance && calculatedDays > selectedBalance.available) {
      setError('Insufficient leave balance');
      return;
    }

    setIsSubmitting(true);
    try {
      await leaveApi.applyLeave({
        leave_type_id: leaveTypeId,
        start_date: startDate,
        end_date: endDate,
        start_day_type: startDayType,
        end_day_type: endDayType,
        reason: reason.trim(),
        attachment: attachment || undefined,
      });
      router.push('/leave/requests');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to apply leave');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleStartDateChange = (date: string) => {
    setStartDate(date);
    if (!endDate || date > endDate) {
      setEndDate(date);
    }
  };

  return (
    <DashboardLayout>
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" onClick={() => router.push('/leave')}>
            <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </Button>
          <div>
            <h1 className="text-2xl font-bold tracking-tight">Apply for Leave</h1>
            <p className="text-muted-foreground">
              Submit a new leave request
            </p>
          </div>
        </div>

        <div className="grid gap-6 md:grid-cols-3">
          {/* Form */}
          <div className="md:col-span-2">
            <Card>
              <CardHeader>
                <CardTitle>Leave Details</CardTitle>
                <CardDescription>Fill in the details for your leave request</CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleSubmit} className="space-y-4">
                  {error && (
                    <div className="rounded-lg border border-destructive/50 bg-destructive/10 p-3 text-sm text-destructive">
                      {error}
                    </div>
                  )}

                  <div className="space-y-2">
                    <Label htmlFor="leaveType">Leave Type *</Label>
                    <Select
                      value={leaveTypeId}
                      onValueChange={setLeaveTypeId}
                      disabled={isLoading || isSubmitting}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select leave type" />
                      </SelectTrigger>
                      <SelectContent>
                        {leaveTypes.map((type) => {
                          const balance = balances.find((b) => b.leave_type_id === type.id);
                          return (
                            <SelectItem key={type.id} value={type.id}>
                              {type.name}
                              {balance && (
                                <span className="ml-2 text-muted-foreground">
                                  ({balance.available} available)
                                </span>
                              )}
                            </SelectItem>
                          );
                        })}
                      </SelectContent>
                    </Select>
                    {selectedLeaveType && (
                      <p className="text-xs text-muted-foreground">
                        {selectedLeaveType.description}
                        {selectedLeaveType.max_consecutive_days && (
                          <span className="ml-2">
                            Max consecutive: {selectedLeaveType.max_consecutive_days} days
                          </span>
                        )}
                      </p>
                    )}
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="startDate">Start Date *</Label>
                      <Input
                        id="startDate"
                        type="date"
                        value={startDate}
                        onChange={(e) => handleStartDateChange(e.target.value)}
                        min={new Date().toISOString().split('T')[0]}
                        disabled={isSubmitting}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="startDayType">Start Day Type</Label>
                      <Select
                        value={startDayType}
                        onValueChange={(v) => setStartDayType(v as DayType)}
                        disabled={isSubmitting}
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          {Object.entries(dayTypeLabels).map(([value, label]) => (
                            <SelectItem key={value} value={value}>
                              {label}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="endDate">End Date *</Label>
                      <Input
                        id="endDate"
                        type="date"
                        value={endDate}
                        onChange={(e) => setEndDate(e.target.value)}
                        min={startDate || new Date().toISOString().split('T')[0]}
                        disabled={isSubmitting}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="endDayType">End Day Type</Label>
                      <Select
                        value={endDayType}
                        onValueChange={(v) => setEndDayType(v as DayType)}
                        disabled={isSubmitting || startDate === endDate}
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          {Object.entries(dayTypeLabels).map(([value, label]) => (
                            <SelectItem key={value} value={value}>
                              {label}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                  </div>

                  {calculatedDays !== null && (
                    <div className="rounded-lg bg-muted p-3">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium">Total Leave Days</span>
                        <span className="text-lg font-bold">{calculatedDays}</span>
                      </div>
                      {selectedBalance && calculatedDays > selectedBalance.available && (
                        <p className="mt-1 text-xs text-destructive">
                          Exceeds available balance ({selectedBalance.available} days)
                        </p>
                      )}
                    </div>
                  )}

                  <div className="space-y-2">
                    <Label htmlFor="reason">Reason *</Label>
                    <Textarea
                      id="reason"
                      placeholder="Please provide a reason for your leave request"
                      value={reason}
                      onChange={(e) => setReason(e.target.value)}
                      rows={3}
                      disabled={isSubmitting}
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="attachment">
                      Attachment
                      {selectedLeaveType?.requires_attachment && (
                        <span className="text-destructive"> *</span>
                      )}
                    </Label>
                    <Input
                      id="attachment"
                      type="file"
                      onChange={(e) => setAttachment(e.target.files?.[0] || null)}
                      disabled={isSubmitting}
                      accept=".pdf,.jpg,.jpeg,.png,.doc,.docx"
                    />
                    <p className="text-xs text-muted-foreground">
                      Supported formats: PDF, JPG, PNG, DOC, DOCX (Max 5MB)
                    </p>
                  </div>

                  <div className="flex justify-end gap-4 pt-4">
                    <Button
                      type="button"
                      variant="outline"
                      onClick={() => router.push('/leave')}
                      disabled={isSubmitting}
                    >
                      Cancel
                    </Button>
                    <Button type="submit" disabled={isSubmitting}>
                      {isSubmitting ? (
                        <>
                          <span className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-background border-t-transparent" />
                          Submitting...
                        </>
                      ) : (
                        'Submit Request'
                      )}
                    </Button>
                  </div>
                </form>
              </CardContent>
            </Card>
          </div>

          {/* Balance Card */}
          <div>
            <LeaveBalanceCard balances={balances} isLoading={isLoading} />
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
