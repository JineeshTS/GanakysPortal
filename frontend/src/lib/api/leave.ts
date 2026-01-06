/**
 * Leave API
 */

import api from './client';
import type {
  LeaveTypeConfig,
  LeaveBalance,
  LeaveRequest,
  LeaveApplyRequest,
  LeaveApprovalRequest,
  Holiday,
  TeamLeaveCalendarEntry,
  LeaveListParams,
  PendingApproval,
} from '@/types/leave';

interface PaginatedResponse<T> {
  items: T[];
  total: number;
  skip: number;
  limit: number;
}

export const leaveApi = {
  // Leave Types
  getLeaveTypes: async (): Promise<LeaveTypeConfig[]> => {
    return api.get<LeaveTypeConfig[]>('/leave/types');
  },

  // Leave Balances
  getMyBalances: async (): Promise<LeaveBalance[]> => {
    return api.get<LeaveBalance[]>('/leave/balances/me');
  },

  getEmployeeBalances: async (employeeId: string): Promise<LeaveBalance[]> => {
    return api.get<LeaveBalance[]>(`/leave/balances/${employeeId}`);
  },

  // Leave Requests
  getMyRequests: async (params?: LeaveListParams): Promise<PaginatedResponse<LeaveRequest>> => {
    const searchParams: Record<string, string> = {};
    if (params?.status) searchParams.status = params.status;
    if (params?.leave_type_id) searchParams.leave_type_id = params.leave_type_id;
    if (params?.start_date) searchParams.start_date = params.start_date;
    if (params?.end_date) searchParams.end_date = params.end_date;
    if (params?.skip !== undefined) searchParams.skip = String(params.skip);
    if (params?.limit !== undefined) searchParams.limit = String(params.limit);

    return api.get<PaginatedResponse<LeaveRequest>>('/leave/requests/me', { params: searchParams });
  },

  getRequest: async (id: string): Promise<LeaveRequest> => {
    return api.get<LeaveRequest>(`/leave/requests/${id}`);
  },

  applyLeave: async (data: LeaveApplyRequest): Promise<LeaveRequest> => {
    if (data.attachment) {
      const formData = new FormData();
      formData.append('leave_type_id', data.leave_type_id);
      formData.append('start_date', data.start_date);
      formData.append('end_date', data.end_date);
      formData.append('start_day_type', data.start_day_type);
      formData.append('end_day_type', data.end_day_type);
      formData.append('reason', data.reason);
      formData.append('attachment', data.attachment);

      return api.uploadFormData<LeaveRequest>('/leave/requests', formData);
    }

    return api.post<LeaveRequest>('/leave/requests', data);
  },

  cancelRequest: async (id: string, reason: string): Promise<LeaveRequest> => {
    return api.post<LeaveRequest>(`/leave/requests/${id}/cancel`, { reason });
  },

  // Approvals
  getPendingApprovals: async (): Promise<PaginatedResponse<LeaveRequest>> => {
    return api.get<PaginatedResponse<LeaveRequest>>('/leave/approvals/pending');
  },

  getTeamRequests: async (params?: LeaveListParams): Promise<PaginatedResponse<LeaveRequest>> => {
    const searchParams: Record<string, string> = {};
    if (params?.status) searchParams.status = params.status;
    if (params?.leave_type_id) searchParams.leave_type_id = params.leave_type_id;
    if (params?.start_date) searchParams.start_date = params.start_date;
    if (params?.end_date) searchParams.end_date = params.end_date;
    if (params?.skip !== undefined) searchParams.skip = String(params.skip);
    if (params?.limit !== undefined) searchParams.limit = String(params.limit);

    return api.get<PaginatedResponse<LeaveRequest>>('/leave/team/requests', { params: searchParams });
  },

  processApproval: async (id: string, data: LeaveApprovalRequest): Promise<LeaveRequest> => {
    return api.post<LeaveRequest>(`/leave/requests/${id}/process`, data);
  },

  // Team Calendar
  getTeamCalendar: async (
    startDate: string,
    endDate: string
  ): Promise<TeamLeaveCalendarEntry[]> => {
    return api.get<TeamLeaveCalendarEntry[]>('/leave/team/calendar', {
      params: { start_date: startDate, end_date: endDate },
    });
  },

  // Holidays
  getHolidays: async (year?: number): Promise<Holiday[]> => {
    const params = year ? { year: String(year) } : undefined;
    return api.get<Holiday[]>('/leave/holidays', { params });
  },

  // All Pending Approvals (aggregated)
  getAllPendingApprovals: async (): Promise<PendingApproval[]> => {
    return api.get<PendingApproval[]>('/approvals/pending');
  },

  // Calculate Leave Days
  calculateDays: async (
    startDate: string,
    endDate: string,
    startDayType: string,
    endDayType: string
  ): Promise<{ days: number }> => {
    return api.get<{ days: number }>('/leave/calculate-days', {
      params: {
        start_date: startDate,
        end_date: endDate,
        start_day_type: startDayType,
        end_day_type: endDayType,
      },
    });
  },
};

export default leaveApi;
