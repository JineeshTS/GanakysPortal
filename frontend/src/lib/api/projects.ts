/**
 * Project Management API
 */

import api from './client';
import type {
  Project,
  ProjectTask,
  Milestone,
  ResourceAllocation,
  ProjectTeamMember,
  ProjectDashboardStats,
  ProjectTimeline,
  ProjectReport,
  GanttTask,
  ListParams,
  ProjectStatus,
  TaskStatus,
  MilestoneStatus,
} from '@/types/project';

interface PaginatedResponse<T> {
  items: T[];
  total: number;
  skip: number;
  limit: number;
}

export const projectsApi = {
  // Dashboard
  getDashboardStats: async (): Promise<ProjectDashboardStats> => {
    return api.get<ProjectDashboardStats>('/projects/dashboard');
  },

  // Projects
  getProjects: async (params?: ListParams & { status?: ProjectStatus }): Promise<PaginatedResponse<Project>> => {
    const searchParams: Record<string, string> = {};
    if (params?.search) searchParams.search = params.search;
    if (params?.status) searchParams.status = params.status;
    if (params?.priority) searchParams.priority = params.priority;
    if (params?.start_date) searchParams.start_date = params.start_date;
    if (params?.end_date) searchParams.end_date = params.end_date;
    if (params?.skip !== undefined) searchParams.skip = String(params.skip);
    if (params?.limit !== undefined) searchParams.limit = String(params.limit);
    return api.get<PaginatedResponse<Project>>('/projects', { params: searchParams });
  },

  getProject: async (id: string): Promise<Project> => {
    return api.get<Project>(`/projects/${id}`);
  },

  createProject: async (data: Partial<Project>): Promise<Project> => {
    return api.post<Project>('/projects', data);
  },

  updateProject: async (id: string, data: Partial<Project>): Promise<Project> => {
    return api.patch<Project>(`/projects/${id}`, data);
  },

  deleteProject: async (id: string): Promise<void> => {
    return api.delete(`/projects/${id}`);
  },

  updateProjectStatus: async (id: string, status: ProjectStatus): Promise<Project> => {
    return api.patch<Project>(`/projects/${id}/status`, { status });
  },

  getProjectTeam: async (id: string): Promise<ProjectTeamMember[]> => {
    return api.get<ProjectTeamMember[]>(`/projects/${id}/team`);
  },

  getProjectTimeline: async (id: string): Promise<ProjectTimeline> => {
    return api.get<ProjectTimeline>(`/projects/${id}/timeline`);
  },

  getProjectGantt: async (id: string): Promise<GanttTask[]> => {
    return api.get<GanttTask[]>(`/projects/${id}/gantt`);
  },

  // Tasks
  getTasks: async (params?: ListParams & { status?: TaskStatus }): Promise<PaginatedResponse<ProjectTask>> => {
    const searchParams: Record<string, string> = {};
    if (params?.search) searchParams.search = params.search;
    if (params?.status) searchParams.status = params.status;
    if (params?.priority) searchParams.priority = params.priority;
    if (params?.project_id) searchParams.project_id = params.project_id;
    if (params?.assignee_id) searchParams.assignee_id = params.assignee_id;
    if (params?.start_date) searchParams.start_date = params.start_date;
    if (params?.end_date) searchParams.end_date = params.end_date;
    if (params?.skip !== undefined) searchParams.skip = String(params.skip);
    if (params?.limit !== undefined) searchParams.limit = String(params.limit);
    return api.get<PaginatedResponse<ProjectTask>>('/projects/tasks', { params: searchParams });
  },

  getMyTasks: async (params?: ListParams & { status?: TaskStatus }): Promise<PaginatedResponse<ProjectTask>> => {
    const searchParams: Record<string, string> = {};
    if (params?.status) searchParams.status = params.status;
    if (params?.priority) searchParams.priority = params.priority;
    if (params?.project_id) searchParams.project_id = params.project_id;
    if (params?.skip !== undefined) searchParams.skip = String(params.skip);
    if (params?.limit !== undefined) searchParams.limit = String(params.limit);
    return api.get<PaginatedResponse<ProjectTask>>('/projects/tasks/my', { params: searchParams });
  },

  getTask: async (id: string): Promise<ProjectTask> => {
    return api.get<ProjectTask>(`/projects/tasks/${id}`);
  },

  createTask: async (data: Partial<ProjectTask>): Promise<ProjectTask> => {
    return api.post<ProjectTask>('/projects/tasks', data);
  },

  updateTask: async (id: string, data: Partial<ProjectTask>): Promise<ProjectTask> => {
    return api.patch<ProjectTask>(`/projects/tasks/${id}`, data);
  },

  deleteTask: async (id: string): Promise<void> => {
    return api.delete(`/projects/tasks/${id}`);
  },

  updateTaskStatus: async (id: string, status: TaskStatus): Promise<ProjectTask> => {
    return api.patch<ProjectTask>(`/projects/tasks/${id}/status`, { status });
  },

  assignTask: async (id: string, assigneeId: string): Promise<ProjectTask> => {
    return api.patch<ProjectTask>(`/projects/tasks/${id}/assign`, { assignee_id: assigneeId });
  },

  logTaskHours: async (id: string, hours: number, description?: string): Promise<ProjectTask> => {
    return api.post<ProjectTask>(`/projects/tasks/${id}/log-hours`, { hours, description });
  },

  addTaskComment: async (id: string, content: string): Promise<ProjectTask> => {
    return api.post<ProjectTask>(`/projects/tasks/${id}/comments`, { content });
  },

  // Milestones
  getMilestones: async (params?: ListParams & { status?: MilestoneStatus }): Promise<PaginatedResponse<Milestone>> => {
    const searchParams: Record<string, string> = {};
    if (params?.search) searchParams.search = params.search;
    if (params?.status) searchParams.status = params.status;
    if (params?.project_id) searchParams.project_id = params.project_id;
    if (params?.skip !== undefined) searchParams.skip = String(params.skip);
    if (params?.limit !== undefined) searchParams.limit = String(params.limit);
    return api.get<PaginatedResponse<Milestone>>('/projects/milestones', { params: searchParams });
  },

  getMilestone: async (id: string): Promise<Milestone> => {
    return api.get<Milestone>(`/projects/milestones/${id}`);
  },

  createMilestone: async (data: Partial<Milestone>): Promise<Milestone> => {
    return api.post<Milestone>('/projects/milestones', data);
  },

  updateMilestone: async (id: string, data: Partial<Milestone>): Promise<Milestone> => {
    return api.patch<Milestone>(`/projects/milestones/${id}`, data);
  },

  deleteMilestone: async (id: string): Promise<void> => {
    return api.delete(`/projects/milestones/${id}`);
  },

  completeMilestone: async (id: string): Promise<Milestone> => {
    return api.post<Milestone>(`/projects/milestones/${id}/complete`, {});
  },

  // Resource Allocations
  getAllocations: async (params?: ListParams): Promise<PaginatedResponse<ResourceAllocation>> => {
    const searchParams: Record<string, string> = {};
    if (params?.project_id) searchParams.project_id = params.project_id;
    if (params?.start_date) searchParams.start_date = params.start_date;
    if (params?.end_date) searchParams.end_date = params.end_date;
    if (params?.skip !== undefined) searchParams.skip = String(params.skip);
    if (params?.limit !== undefined) searchParams.limit = String(params.limit);
    return api.get<PaginatedResponse<ResourceAllocation>>('/projects/allocations', { params: searchParams });
  },

  getMyAllocations: async (): Promise<ResourceAllocation[]> => {
    return api.get<ResourceAllocation[]>('/projects/allocations/my');
  },

  createAllocation: async (data: Partial<ResourceAllocation>): Promise<ResourceAllocation> => {
    return api.post<ResourceAllocation>('/projects/allocations', data);
  },

  updateAllocation: async (id: string, data: Partial<ResourceAllocation>): Promise<ResourceAllocation> => {
    return api.patch<ResourceAllocation>(`/projects/allocations/${id}`, data);
  },

  deleteAllocation: async (id: string): Promise<void> => {
    return api.delete(`/projects/allocations/${id}`);
  },

  // Resource Availability
  getResourceAvailability: async (startDate: string, endDate: string): Promise<Array<{
    employee_id: string;
    employee_name: string;
    total_allocation: number;
    available_percentage: number;
    allocations: ResourceAllocation[];
  }>> => {
    return api.get('/projects/resources/availability', {
      params: { start_date: startDate, end_date: endDate },
    });
  },

  // Reports
  getProjectReport: async (id: string, startDate?: string, endDate?: string): Promise<ProjectReport> => {
    const params: Record<string, string> = {};
    if (startDate) params.start_date = startDate;
    if (endDate) params.end_date = endDate;
    return api.get<ProjectReport>(`/projects/${id}/report`, { params });
  },

  getProjectsOverview: async (): Promise<Array<{
    project_id: string;
    project_name: string;
    status: ProjectStatus;
    progress: number;
    budget_utilization: number;
    hours_utilization: number;
    team_size: number;
  }>> => {
    return api.get('/projects/reports/overview');
  },

  getResourceUtilization: async (startDate: string, endDate: string): Promise<Array<{
    employee_id: string;
    employee_name: string;
    allocated_hours: number;
    actual_hours: number;
    utilization_rate: number;
    projects: string[];
  }>> => {
    return api.get('/projects/reports/resource-utilization', {
      params: { start_date: startDate, end_date: endDate },
    });
  },
};

export default projectsApi;
