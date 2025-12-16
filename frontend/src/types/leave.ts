/**
 * Leave Types
 */

export type LeaveType = 'earned' | 'casual' | 'sick' | 'maternity' | 'paternity' | 'bereavement' | 'comp_off' | 'unpaid';
export type LeaveStatus = 'pending' | 'approved' | 'rejected' | 'cancelled';
export type DayType = 'full' | 'first_half' | 'second_half';

export interface LeaveTypeConfig {
  id: string;
  name: string;
  code: LeaveType;
  description?: string;
  annual_quota: number;
  carry_forward_limit: number;
  max_consecutive_days: number;
  min_notice_days: number;
  requires_attachment: boolean;
  is_paid: boolean;
  is_active: boolean;
}

export interface LeaveBalance {
  leave_type_id: string;
  leave_type_name: string;
  leave_type_code: LeaveType;
  total_quota: number;
  used: number;
  pending: number;
  available: number;
  carry_forward: number;
}

export interface LeaveRequest {
  id: string;
  employee_id: string;
  employee_name: string;
  employee_code: string;
  leave_type_id: string;
  leave_type_name: string;
  leave_type_code: LeaveType;
  start_date: string;
  end_date: string;
  start_day_type: DayType;
  end_day_type: DayType;
  total_days: number;
  reason: string;
  attachment_path?: string;
  status: LeaveStatus;
  applied_at: string;
  approved_by?: string;
  approver_name?: string;
  approved_at?: string;
  rejection_reason?: string;
  cancellation_reason?: string;
  cancelled_at?: string;
}

export interface LeaveApplyRequest {
  leave_type_id: string;
  start_date: string;
  end_date: string;
  start_day_type: DayType;
  end_day_type: DayType;
  reason: string;
  attachment?: File;
}

export interface LeaveApprovalRequest {
  action: 'approve' | 'reject';
  rejection_reason?: string;
}

export interface Holiday {
  id: string;
  name: string;
  date: string;
  type: 'national' | 'regional' | 'optional';
  description?: string;
  is_optional: boolean;
  optional_quota?: number;
  applicable_locations?: string[];
}

export interface TeamLeaveCalendarEntry {
  employee_id: string;
  employee_name: string;
  leave_type: string;
  start_date: string;
  end_date: string;
  status: LeaveStatus;
}

export interface LeaveListParams {
  status?: LeaveStatus;
  leave_type_id?: string;
  start_date?: string;
  end_date?: string;
  skip?: number;
  limit?: number;
}

export interface PendingApproval {
  id: string;
  type: 'leave' | 'timesheet' | 'expense';
  employee_name: string;
  employee_code: string;
  description: string;
  submitted_at: string;
  days?: number;
  amount?: number;
}
