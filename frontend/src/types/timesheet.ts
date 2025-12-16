/**
 * Timesheet Types
 */

export type TimesheetStatus = 'draft' | 'submitted' | 'approved' | 'rejected';
export type TimesheetEntryType = 'regular' | 'overtime' | 'on_call';

export interface Timesheet {
  id: string;
  employee_id: string;
  employee_name?: string;
  employee_code?: string;
  week_start_date: string;
  week_end_date: string;
  total_hours: number;
  billable_hours: number;
  status: TimesheetStatus;
  submitted_at?: string;
  approved_by?: string;
  approver_name?: string;
  approved_at?: string;
  rejection_reason?: string;
  entries: TimesheetEntry[];
  created_at: string;
  updated_at: string;
}

export interface TimesheetEntry {
  id: string;
  timesheet_id: string;
  date: string;
  project_id?: string;
  project_name?: string;
  project_code?: string;
  task_id?: string;
  task_name?: string;
  hours: number;
  entry_type: TimesheetEntryType;
  is_billable: boolean;
  description?: string;
  created_at: string;
  updated_at: string;
}

export interface TimesheetEntryRequest {
  date: string;
  project_id?: string;
  task_id?: string;
  hours: number;
  entry_type?: TimesheetEntryType;
  is_billable?: boolean;
  description?: string;
}

export interface WeeklyTimesheetData {
  timesheet: Timesheet | null;
  week_start: string;
  week_end: string;
  entries_by_day: Record<string, TimesheetEntry[]>;
  total_hours: number;
  billable_hours: number;
}

export interface TimesheetApprovalRequest {
  action: 'approve' | 'reject';
  rejection_reason?: string;
}

export interface TimesheetListParams {
  status?: TimesheetStatus;
  employee_id?: string;
  start_date?: string;
  end_date?: string;
  skip?: number;
  limit?: number;
}

export interface TimesheetSummary {
  week_start: string;
  week_end: string;
  total_hours: number;
  billable_hours: number;
  status: TimesheetStatus;
}

export interface Project {
  id: string;
  code: string;
  name: string;
  customer_name?: string;
  status: string;
  is_billable: boolean;
}

export interface ProjectTask {
  id: string;
  project_id: string;
  name: string;
  status: string;
  estimated_hours?: number;
  actual_hours?: number;
}
