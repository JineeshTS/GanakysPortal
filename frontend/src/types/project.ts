/**
 * Project Management Types
 */

export type ProjectStatus = 'planning' | 'active' | 'on_hold' | 'completed' | 'cancelled';
export type ProjectPriority = 'low' | 'medium' | 'high' | 'critical';
export type TaskStatus = 'todo' | 'in_progress' | 'review' | 'completed' | 'cancelled';
export type TaskPriority = 'low' | 'medium' | 'high' | 'urgent';
export type MilestoneStatus = 'pending' | 'in_progress' | 'completed' | 'overdue';
export type ResourceAllocationStatus = 'planned' | 'active' | 'completed';

export interface Project {
  id: string;
  code: string;
  name: string;
  description?: string;
  customer_id?: string;
  customer_name?: string;
  project_manager_id?: string;
  project_manager_name?: string;
  status: ProjectStatus;
  priority: ProjectPriority;
  start_date: string;
  end_date?: string;
  estimated_hours: number;
  actual_hours: number;
  budget: number;
  actual_cost: number;
  is_billable: boolean;
  billing_type?: 'fixed' | 'hourly' | 'milestone';
  hourly_rate?: number;
  fixed_amount?: number;
  progress_percentage: number;
  team_size: number;
  tags?: string[];
  created_at: string;
  updated_at: string;
}

export interface ProjectTask {
  id: string;
  project_id: string;
  project_name?: string;
  project_code?: string;
  parent_task_id?: string;
  title: string;
  description?: string;
  assignee_id?: string;
  assignee_name?: string;
  status: TaskStatus;
  priority: TaskPriority;
  start_date?: string;
  due_date?: string;
  completed_at?: string;
  estimated_hours: number;
  actual_hours: number;
  progress_percentage: number;
  milestone_id?: string;
  milestone_name?: string;
  dependencies?: string[];
  tags?: string[];
  attachments?: TaskAttachment[];
  comments?: TaskComment[];
  created_at: string;
  updated_at: string;
}

export interface TaskAttachment {
  id: string;
  task_id: string;
  file_name: string;
  file_size: number;
  file_type: string;
  uploaded_by: string;
  uploaded_at: string;
  url: string;
}

export interface TaskComment {
  id: string;
  task_id: string;
  user_id: string;
  user_name: string;
  content: string;
  created_at: string;
}

export interface Milestone {
  id: string;
  project_id: string;
  project_name?: string;
  name: string;
  description?: string;
  due_date: string;
  completed_date?: string;
  status: MilestoneStatus;
  deliverables?: string;
  amount?: number;
  is_billable: boolean;
  tasks_count: number;
  completed_tasks_count: number;
  progress_percentage: number;
  created_at: string;
  updated_at: string;
}

export interface ResourceAllocation {
  id: string;
  project_id: string;
  project_name?: string;
  project_code?: string;
  employee_id: string;
  employee_name: string;
  employee_code: string;
  role: string;
  allocation_percentage: number;
  hourly_rate?: number;
  start_date: string;
  end_date?: string;
  status: ResourceAllocationStatus;
  estimated_hours: number;
  actual_hours: number;
  created_at: string;
  updated_at: string;
}

export interface ProjectTeamMember {
  employee_id: string;
  employee_name: string;
  employee_code: string;
  role: string;
  allocation_percentage: number;
  joined_date: string;
  hours_logged: number;
}

export interface ProjectDashboardStats {
  total_projects: number;
  active_projects: number;
  on_hold_projects: number;
  completed_projects: number;
  total_budget: number;
  total_spent: number;
  total_hours_estimated: number;
  total_hours_actual: number;
  overdue_tasks: number;
  upcoming_milestones: number;
}

export interface ProjectTimeline {
  project_id: string;
  milestones: Array<{
    id: string;
    name: string;
    due_date: string;
    status: MilestoneStatus;
  }>;
  tasks: Array<{
    id: string;
    title: string;
    start_date?: string;
    due_date?: string;
    status: TaskStatus;
  }>;
}

export interface ProjectReport {
  project_id: string;
  project_name: string;
  period_start: string;
  period_end: string;
  hours_summary: {
    estimated: number;
    actual: number;
    billable: number;
    non_billable: number;
  };
  cost_summary: {
    budget: number;
    actual: number;
    variance: number;
  };
  task_summary: {
    total: number;
    completed: number;
    in_progress: number;
    overdue: number;
  };
  team_utilization: Array<{
    employee_name: string;
    allocated_hours: number;
    actual_hours: number;
    utilization_rate: number;
  }>;
}

export interface GanttTask {
  id: string;
  name: string;
  start: string;
  end: string;
  progress: number;
  dependencies?: string[];
  type: 'project' | 'milestone' | 'task';
  parent?: string;
}

export interface ListParams {
  search?: string;
  status?: string;
  priority?: string;
  project_id?: string;
  assignee_id?: string;
  start_date?: string;
  end_date?: string;
  skip?: number;
  limit?: number;
}
