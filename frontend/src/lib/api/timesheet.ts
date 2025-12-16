/**
 * Timesheet API
 */

import api from './client';
import type {
  Timesheet,
  TimesheetEntry,
  TimesheetEntryRequest,
  WeeklyTimesheetData,
  TimesheetApprovalRequest,
  TimesheetListParams,
  TimesheetSummary,
  Project,
  ProjectTask,
} from '@/types/timesheet';

interface PaginatedResponse<T> {
  items: T[];
  total: number;
  skip: number;
  limit: number;
}

export const timesheetApi = {
  // Weekly Timesheet
  getWeeklyTimesheet: async (weekStartDate?: string): Promise<WeeklyTimesheetData> => {
    const params = weekStartDate ? { week_start: weekStartDate } : undefined;
    return api.get<WeeklyTimesheetData>('/timesheets/weekly', { params });
  },

  // Timesheets
  getMyTimesheets: async (params?: TimesheetListParams): Promise<PaginatedResponse<Timesheet>> => {
    const searchParams: Record<string, string> = {};
    if (params?.status) searchParams.status = params.status;
    if (params?.start_date) searchParams.start_date = params.start_date;
    if (params?.end_date) searchParams.end_date = params.end_date;
    if (params?.skip !== undefined) searchParams.skip = String(params.skip);
    if (params?.limit !== undefined) searchParams.limit = String(params.limit);

    return api.get<PaginatedResponse<Timesheet>>('/timesheets/me', { params: searchParams });
  },

  getTimesheet: async (id: string): Promise<Timesheet> => {
    return api.get<Timesheet>(`/timesheets/${id}`);
  },

  // Create/Update Timesheet
  createOrUpdateTimesheet: async (weekStartDate: string): Promise<Timesheet> => {
    return api.post<Timesheet>('/timesheets', { week_start_date: weekStartDate });
  },

  // Entries
  addEntry: async (timesheetId: string, entry: TimesheetEntryRequest): Promise<TimesheetEntry> => {
    return api.post<TimesheetEntry>(`/timesheets/${timesheetId}/entries`, entry);
  },

  updateEntry: async (
    timesheetId: string,
    entryId: string,
    entry: Partial<TimesheetEntryRequest>
  ): Promise<TimesheetEntry> => {
    return api.patch<TimesheetEntry>(`/timesheets/${timesheetId}/entries/${entryId}`, entry);
  },

  deleteEntry: async (timesheetId: string, entryId: string): Promise<void> => {
    await api.delete(`/timesheets/${timesheetId}/entries/${entryId}`);
  },

  // Submit/Recall
  submitTimesheet: async (id: string): Promise<Timesheet> => {
    return api.post<Timesheet>(`/timesheets/${id}/submit`, {});
  },

  recallTimesheet: async (id: string): Promise<Timesheet> => {
    return api.post<Timesheet>(`/timesheets/${id}/recall`, {});
  },

  // Approvals
  getPendingApprovals: async (): Promise<PaginatedResponse<Timesheet>> => {
    return api.get<PaginatedResponse<Timesheet>>('/timesheets/approvals/pending');
  },

  getTeamTimesheets: async (
    params?: TimesheetListParams
  ): Promise<PaginatedResponse<Timesheet>> => {
    const searchParams: Record<string, string> = {};
    if (params?.status) searchParams.status = params.status;
    if (params?.employee_id) searchParams.employee_id = params.employee_id;
    if (params?.start_date) searchParams.start_date = params.start_date;
    if (params?.end_date) searchParams.end_date = params.end_date;
    if (params?.skip !== undefined) searchParams.skip = String(params.skip);
    if (params?.limit !== undefined) searchParams.limit = String(params.limit);

    return api.get<PaginatedResponse<Timesheet>>('/timesheets/team', { params: searchParams });
  },

  processApproval: async (id: string, data: TimesheetApprovalRequest): Promise<Timesheet> => {
    return api.post<Timesheet>(`/timesheets/${id}/process`, data);
  },

  // History/Summary
  getMySummary: async (year?: number): Promise<TimesheetSummary[]> => {
    const params = year ? { year: String(year) } : undefined;
    return api.get<TimesheetSummary[]>('/timesheets/summary/me', { params });
  },

  // Projects for timesheet
  getProjects: async (): Promise<Project[]> => {
    return api.get<Project[]>('/projects/active');
  },

  getProjectTasks: async (projectId: string): Promise<ProjectTask[]> => {
    return api.get<ProjectTask[]>(`/projects/${projectId}/tasks/assignable`);
  },

  // Quick add entry (creates timesheet if needed)
  quickAddEntry: async (entry: TimesheetEntryRequest & { week_start_date?: string }): Promise<TimesheetEntry> => {
    return api.post<TimesheetEntry>('/timesheets/quick-entry', entry);
  },

  // Copy previous week
  copyPreviousWeek: async (weekStartDate: string): Promise<Timesheet> => {
    return api.post<Timesheet>('/timesheets/copy-previous', { week_start_date: weekStartDate });
  },
};

export default timesheetApi;
