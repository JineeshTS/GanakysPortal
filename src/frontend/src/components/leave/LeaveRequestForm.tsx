'use client'

import * as React from 'react'
import { useRouter } from 'next/navigation'
import { cn } from '@/lib/utils'
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Label } from '@/components/ui/label'
import { FormTextarea } from '@/components/forms/form-field'
import { DateRangePicker } from '@/components/forms/date-picker'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue
} from '@/components/ui/select'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle
} from '@/components/ui/dialog'
import { formatDate, getFinancialYear } from '@/lib/format'
import {
  Calendar,
  Send,
  AlertCircle,
  CheckCircle,
  Info,
  User,
  Loader2
} from 'lucide-react'
import type { LeaveBalance, LeaveType } from '@/types'

// ============================================================================
// Types
// ============================================================================

interface LeaveFormData {
  leave_type_code: string
  from_date: string
  to_date: string
  half_day: boolean
  half_day_type?: 'first_half' | 'second_half'
  reason: string
}

interface LeaveRequestFormProps {
  leaveTypes: LeaveType[]
  balances: LeaveBalance[]
  approverName?: string
  onSubmit: (data: LeaveFormData) => Promise<void>
  className?: string
}

// ============================================================================
// Helper Functions
// ============================================================================

function calculateLeaveDays(
  fromDate: string,
  toDate: string,
  halfDay: boolean
): number {
  if (!fromDate || !toDate) return 0

  const from = new Date(fromDate)
  const to = new Date(toDate)

  if (isNaN(from.getTime()) || isNaN(to.getTime())) return 0
  if (from > to) return 0

  // Calculate difference in days (inclusive)
  const diffTime = to.getTime() - from.getTime()
  const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24)) + 1

  // Exclude weekends (Saturday and Sunday)
  let workingDays = 0
  const currentDate = new Date(from)

  while (currentDate <= to) {
    const dayOfWeek = currentDate.getDay()
    if (dayOfWeek !== 0 && dayOfWeek !== 6) {
      workingDays++
    }
    currentDate.setDate(currentDate.getDate() + 1)
  }

  if (halfDay && workingDays > 0) {
    return workingDays - 0.5
  }

  return workingDays
}

function getTodayISO(): string {
  return new Date().toISOString().split('T')[0]
}

// ============================================================================
// Leave Request Form Component
// ============================================================================

export function LeaveRequestForm({
  leaveTypes,
  balances,
  approverName = 'Manager',
  onSubmit,
  className
}: LeaveRequestFormProps) {
  const router = useRouter()

  // Form state
  const [formData, setFormData] = React.useState<LeaveFormData>({
    leave_type_code: '',
    from_date: '',
    to_date: '',
    half_day: false,
    half_day_type: undefined,
    reason: ''
  })

  const [errors, setErrors] = React.useState<Partial<Record<keyof LeaveFormData, string>>>({})
  const [isSubmitting, setIsSubmitting] = React.useState(false)
  const [showConfirmDialog, setShowConfirmDialog] = React.useState(false)

  // Derived state
  const selectedLeaveType = leaveTypes.find(lt => lt.code === formData.leave_type_code)
  const selectedBalance = balances.find(b => b.leave_type_code === formData.leave_type_code)

  const calculatedDays = React.useMemo(() => {
    return calculateLeaveDays(formData.from_date, formData.to_date, formData.half_day)
  }, [formData.from_date, formData.to_date, formData.half_day])

  const availableBalance = selectedBalance?.available ?? 0
  const hasSufficientBalance = calculatedDays <= availableBalance

  // Validation
  const validateForm = (): boolean => {
    const newErrors: Partial<Record<keyof LeaveFormData, string>> = {}

    if (!formData.leave_type_code) {
      newErrors.leave_type_code = 'Please select a leave type'
    }

    if (!formData.from_date) {
      newErrors.from_date = 'Start date is required'
    }

    if (!formData.to_date) {
      newErrors.to_date = 'End date is required'
    }

    if (formData.from_date && formData.to_date) {
      const from = new Date(formData.from_date)
      const to = new Date(formData.to_date)

      if (from > to) {
        newErrors.to_date = 'End date must be after start date'
      }

      // Check notice period
      if (selectedLeaveType && selectedLeaveType.notice_days > 0) {
        const today = new Date()
        const noticeDays = Math.floor((from.getTime() - today.getTime()) / (1000 * 60 * 60 * 24))
        if (noticeDays < selectedLeaveType.notice_days) {
          newErrors.from_date = `${selectedLeaveType.name} requires ${selectedLeaveType.notice_days} days advance notice`
        }
      }

      // Check max continuous days
      if (selectedLeaveType && calculatedDays > selectedLeaveType.max_days) {
        newErrors.to_date = `Maximum ${selectedLeaveType.max_days} continuous days allowed for ${selectedLeaveType.name}`
      }
    }

    if (formData.half_day && !formData.half_day_type) {
      newErrors.half_day_type = 'Please select first half or second half'
    }

    if (!formData.reason.trim()) {
      newErrors.reason = 'Please provide a reason for leave'
    } else if (formData.reason.trim().length < 10) {
      newErrors.reason = 'Reason must be at least 10 characters'
    }

    if (!hasSufficientBalance && selectedLeaveType?.is_paid) {
      newErrors.leave_type_code = 'Insufficient leave balance'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  // Handlers
  const handleChange = (field: keyof LeaveFormData, value: string | boolean) => {
    setFormData(prev => ({
      ...prev,
      [field]: value,
      // Reset half day type if half day is unchecked
      ...(field === 'half_day' && !value ? { half_day_type: undefined } : {}),
      // If half day is enabled and dates are same, auto-set to_date
      ...(field === 'half_day' && value && formData.from_date && !formData.to_date
        ? { to_date: formData.from_date }
        : {}),
      // If from_date changes and half_day is enabled, set to_date same
      ...(field === 'from_date' && formData.half_day ? { to_date: value as string } : {})
    }))

    // Clear error for this field
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: undefined }))
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!validateForm()) return

    setShowConfirmDialog(true)
  }

  const handleConfirmSubmit = async () => {
    setIsSubmitting(true)

    try {
      await onSubmit({
        ...formData,
        half_day_type: formData.half_day ? formData.half_day_type : undefined
      })

      // Success - redirect or show success message
      router.push('/leave/requests')
    } catch (error) {
      console.error('Failed to submit leave request:', error)
    } finally {
      setIsSubmitting(false)
      setShowConfirmDialog(false)
    }
  }

  return (
    <>
      <Card className={className}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Calendar className="h-5 w-5" />
            Apply for Leave
          </CardTitle>
          <CardDescription>
            {getFinancialYear()} - Submit your leave request for approval
          </CardDescription>
        </CardHeader>

        <form onSubmit={handleSubmit}>
          <CardContent className="space-y-6">
            {/* Leave Type Selection */}
            <div className="space-y-2">
              <Label htmlFor="leave_type">
                Leave Type <span className="text-destructive">*</span>
              </Label>
              <Select
                value={formData.leave_type_code}
                onValueChange={(value) => handleChange('leave_type_code', value)}
              >
                <SelectTrigger
                  id="leave_type"
                  className={cn(errors.leave_type_code && "border-destructive")}
                >
                  <SelectValue placeholder="Select leave type" />
                </SelectTrigger>
                <SelectContent>
                  {leaveTypes.map((lt) => {
                    const balance = balances.find(b => b.leave_type_code === lt.code)
                    return (
                      <SelectItem key={lt.code} value={lt.code}>
                        <div className="flex items-center justify-between gap-4 w-full">
                          <span>{lt.name} ({lt.code})</span>
                          {balance && (
                            <Badge variant="outline" className="ml-2">
                              {balance.available} days
                            </Badge>
                          )}
                        </div>
                      </SelectItem>
                    )
                  })}
                </SelectContent>
              </Select>
              {errors.leave_type_code && (
                <p className="text-sm text-destructive flex items-center gap-1">
                  <AlertCircle className="h-3 w-3" />
                  {errors.leave_type_code}
                </p>
              )}

              {/* Leave Balance Info */}
              {selectedBalance && (
                <div className={cn(
                  "p-3 rounded-md border mt-2",
                  hasSufficientBalance ? "bg-green-50 border-green-200" : "bg-red-50 border-red-200"
                )}>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      {hasSufficientBalance ? (
                        <CheckCircle className="h-4 w-4 text-green-600" />
                      ) : (
                        <AlertCircle className="h-4 w-4 text-red-600" />
                      )}
                      <span className="text-sm font-medium">
                        Available Balance: {selectedBalance.available} days
                      </span>
                    </div>
                    {selectedBalance.pending_approval > 0 && (
                      <Badge variant="outline" className="bg-yellow-50 text-yellow-800 border-yellow-200">
                        {selectedBalance.pending_approval} pending
                      </Badge>
                    )}
                  </div>
                </div>
              )}
            </div>

            {/* Date Range */}
            <DateRangePicker
              label="Leave Duration"
              name="leave_dates"
              startValue={formData.from_date}
              endValue={formData.to_date}
              onStartChange={(date) => handleChange('from_date', date)}
              onEndChange={(date) => handleChange('to_date', date)}
              required
              error={errors.from_date || errors.to_date}
            />

            {/* Days Calculation */}
            {calculatedDays > 0 && (
              <div className="p-4 bg-muted rounded-lg">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Number of Days:</span>
                  <span className="text-2xl font-bold">
                    {calculatedDays} {calculatedDays === 1 ? 'day' : 'days'}
                  </span>
                </div>
                <p className="text-xs text-muted-foreground mt-1">
                  {formatDate(formData.from_date)} - {formatDate(formData.to_date)}
                  {formData.half_day && ` (${formData.half_day_type === 'first_half' ? 'First Half' : 'Second Half'})`}
                </p>
              </div>
            )}

            {/* Half Day Option */}
            <div className="space-y-3">
              <div className="flex items-center gap-3">
                <input
                  type="checkbox"
                  id="half_day"
                  checked={formData.half_day}
                  onChange={(e) => handleChange('half_day', e.target.checked)}
                  className="h-4 w-4 rounded border-input"
                />
                <Label htmlFor="half_day" className="text-sm font-normal cursor-pointer">
                  Half Day Leave
                </Label>
              </div>

              {formData.half_day && (
                <div className="ml-7 space-y-2">
                  <div className="flex gap-4">
                    <label className="flex items-center gap-2 cursor-pointer">
                      <input
                        type="radio"
                        name="half_day_type"
                        value="first_half"
                        checked={formData.half_day_type === 'first_half'}
                        onChange={() => handleChange('half_day_type', 'first_half')}
                        className="h-4 w-4"
                      />
                      <span className="text-sm">First Half (Morning)</span>
                    </label>
                    <label className="flex items-center gap-2 cursor-pointer">
                      <input
                        type="radio"
                        name="half_day_type"
                        value="second_half"
                        checked={formData.half_day_type === 'second_half'}
                        onChange={() => handleChange('half_day_type', 'second_half')}
                        className="h-4 w-4"
                      />
                      <span className="text-sm">Second Half (Afternoon)</span>
                    </label>
                  </div>
                  {errors.half_day_type && (
                    <p className="text-sm text-destructive flex items-center gap-1">
                      <AlertCircle className="h-3 w-3" />
                      {errors.half_day_type}
                    </p>
                  )}
                </div>
              )}
            </div>

            {/* Reason */}
            <FormTextarea
              label="Reason for Leave"
              name="reason"
              value={formData.reason}
              onChange={(e) => handleChange('reason', e.target.value)}
              placeholder="Please provide a detailed reason for your leave request..."
              rows={4}
              required
              error={errors.reason}
              hint="Minimum 10 characters"
            />

            {/* Approver Info */}
            <div className="p-3 bg-muted rounded-md flex items-center gap-3">
              <User className="h-4 w-4 text-muted-foreground" />
              <div>
                <p className="text-sm font-medium">Approver</p>
                <p className="text-xs text-muted-foreground">{approverName}</p>
              </div>
            </div>

            {/* Leave Policy Info */}
            {selectedLeaveType && (
              <div className="p-3 border rounded-md space-y-2">
                <div className="flex items-center gap-2">
                  <Info className="h-4 w-4 text-blue-600" />
                  <span className="text-sm font-medium">Leave Policy - {selectedLeaveType.name}</span>
                </div>
                <div className="grid grid-cols-2 gap-2 text-xs text-muted-foreground">
                  <div>Max Continuous Days: {selectedLeaveType.max_days}</div>
                  <div>Notice Required: {selectedLeaveType.notice_days} days</div>
                  <div>Paid Leave: {selectedLeaveType.is_paid ? 'Yes' : 'No'}</div>
                  <div>Approval Required: {selectedLeaveType.requires_approval ? 'Yes' : 'No'}</div>
                </div>
              </div>
            )}
          </CardContent>

          <CardFooter className="flex justify-between">
            <Button
              type="button"
              variant="outline"
              onClick={() => router.back()}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={isSubmitting || !hasSufficientBalance}
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Submitting...
                </>
              ) : (
                <>
                  <Send className="h-4 w-4 mr-2" />
                  Submit Request
                </>
              )}
            </Button>
          </CardFooter>
        </form>
      </Card>

      {/* Confirmation Dialog */}
      <Dialog open={showConfirmDialog} onOpenChange={setShowConfirmDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Confirm Leave Request</DialogTitle>
            <DialogDescription>
              Please review your leave request details before submitting.
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-3 py-4">
            <div className="grid grid-cols-2 gap-2 text-sm">
              <div className="text-muted-foreground">Leave Type:</div>
              <div className="font-medium">{selectedLeaveType?.name}</div>

              <div className="text-muted-foreground">From:</div>
              <div className="font-medium">{formatDate(formData.from_date)}</div>

              <div className="text-muted-foreground">To:</div>
              <div className="font-medium">{formatDate(formData.to_date)}</div>

              <div className="text-muted-foreground">Days:</div>
              <div className="font-medium">
                {calculatedDays} {calculatedDays === 1 ? 'day' : 'days'}
                {formData.half_day && ` (${formData.half_day_type === 'first_half' ? 'First Half' : 'Second Half'})`}
              </div>

              <div className="text-muted-foreground">Approver:</div>
              <div className="font-medium">{approverName}</div>
            </div>

            <div className="pt-2 border-t">
              <p className="text-sm text-muted-foreground">Reason:</p>
              <p className="text-sm mt-1">{formData.reason}</p>
            </div>
          </div>

          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setShowConfirmDialog(false)}
              disabled={isSubmitting}
            >
              Cancel
            </Button>
            <Button
              onClick={handleConfirmSubmit}
              disabled={isSubmitting}
            >
              {isSubmitting ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Submitting...
                </>
              ) : (
                'Confirm & Submit'
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  )
}

export default LeaveRequestForm
