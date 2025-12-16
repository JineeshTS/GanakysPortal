'use client';

/**
 * Project Detail Page
 */

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { DashboardLayout } from '@/components/layout/dashboard-layout';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from '@/components/ui/tabs';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import projectsApi from '@/lib/api/projects';
import type { Project, ProjectTask, Milestone, ProjectTeamMember, ProjectStatus, TaskStatus, MilestoneStatus } from '@/types/project';

const statusColors: Record<ProjectStatus, string> = {
  planning: 'bg-gray-100 text-gray-800',
  active: 'bg-green-100 text-green-800',
  on_hold: 'bg-yellow-100 text-yellow-800',
  completed: 'bg-blue-100 text-blue-800',
  cancelled: 'bg-red-100 text-red-800',
};

const taskStatusColors: Record<TaskStatus, string> = {
  todo: 'bg-gray-100 text-gray-800',
  in_progress: 'bg-blue-100 text-blue-800',
  review: 'bg-purple-100 text-purple-800',
  completed: 'bg-green-100 text-green-800',
  cancelled: 'bg-red-100 text-red-800',
};

const milestoneStatusColors: Record<MilestoneStatus, string> = {
  pending: 'bg-gray-100 text-gray-800',
  in_progress: 'bg-blue-100 text-blue-800',
  completed: 'bg-green-100 text-green-800',
  overdue: 'bg-red-100 text-red-800',
};

export default function ProjectDetailPage() {
  const params = useParams();
  const router = useRouter();
  const [project, setProject] = useState<Project | null>(null);
  const [tasks, setTasks] = useState<ProjectTask[]>([]);
  const [milestones, setMilestones] = useState<Milestone[]>([]);
  const [team, setTeam] = useState<ProjectTeamMember[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const loadProjectData = async () => {
      if (!params.id) return;
      try {
        const [projectData, tasksData, milestonesData, teamData] = await Promise.all([
          projectsApi.getProject(params.id as string),
          projectsApi.getTasks({ project_id: params.id as string, limit: 10 }),
          projectsApi.getMilestones({ project_id: params.id as string }),
          projectsApi.getProjectTeam(params.id as string),
        ]);
        setProject(projectData);
        setTasks(tasksData.items);
        setMilestones(milestonesData.items);
        setTeam(teamData);
      } catch (error) {
        console.error('Failed to load project data:', error);
      } finally {
        setIsLoading(false);
      }
    };
    loadProjectData();
  }, [params.id]);

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const formatDate = (date: string) => {
    return new Date(date).toLocaleDateString('en-IN', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
    });
  };

  if (isLoading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-64">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
        </div>
      </DashboardLayout>
    );
  }

  if (!project) {
    return (
      <DashboardLayout>
        <div className="text-center py-12">
          <h2 className="text-xl font-semibold">Project not found</h2>
          <Link href="/projects">
            <Button className="mt-4">Back to Projects</Button>
          </Link>
        </div>
      </DashboardLayout>
    );
  }

  const budgetUtilization = project.budget > 0 ? Math.round((project.actual_cost / project.budget) * 100) : 0;
  const hoursUtilization = project.estimated_hours > 0 ? Math.round((project.actual_hours / project.estimated_hours) * 100) : 0;

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href="/projects/list">
              <Button variant="ghost" size="icon">
                <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                </svg>
              </Button>
            </Link>
            <div>
              <div className="flex items-center gap-3">
                <h1 className="text-2xl font-bold tracking-tight">{project.name}</h1>
                <Badge variant="secondary" className={statusColors[project.status]}>
                  {project.status === 'on_hold' ? 'On Hold' : project.status.charAt(0).toUpperCase() + project.status.slice(1)}
                </Badge>
              </div>
              <p className="text-muted-foreground font-mono">{project.code}</p>
            </div>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" onClick={() => router.push(`/projects/${project.id}/edit`)}>
              Edit Project
            </Button>
            <Link href={`/projects/tasks?project_id=${project.id}`}>
              <Button>
                <svg className="mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
                Add Task
              </Button>
            </Link>
          </div>
        </div>

        {/* Summary Cards */}
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Progress</CardDescription>
              <CardTitle className="text-2xl">{project.progress_percentage}%</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="w-full h-2 bg-muted rounded-full overflow-hidden">
                <div
                  className="h-full bg-primary transition-all"
                  style={{ width: `${project.progress_percentage}%` }}
                />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Budget</CardDescription>
              <CardTitle className="text-2xl">{formatCurrency(project.budget)}</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Spent: {formatCurrency(project.actual_cost)}</span>
                <span className={budgetUtilization > 100 ? 'text-red-600' : ''}>{budgetUtilization}%</span>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Hours</CardDescription>
              <CardTitle className="text-2xl">{project.actual_hours}h</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Estimated: {project.estimated_hours}h</span>
                <span className={hoursUtilization > 100 ? 'text-red-600' : ''}>{hoursUtilization}%</span>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Team</CardDescription>
              <CardTitle className="text-2xl">{project.team_size}</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                {project.project_manager_name || 'No manager assigned'}
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Project Details & Activity */}
        <Tabs defaultValue="overview" className="space-y-4">
          <TabsList>
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="tasks">Tasks ({tasks.length})</TabsTrigger>
            <TabsTrigger value="milestones">Milestones ({milestones.length})</TabsTrigger>
            <TabsTrigger value="team">Team ({team.length})</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-4">
            <div className="grid gap-6 md:grid-cols-2">
              <Card>
                <CardHeader>
                  <CardTitle className="text-base">Project Details</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {project.description && (
                    <div>
                      <div className="text-sm text-muted-foreground">Description</div>
                      <div className="mt-1">{project.description}</div>
                    </div>
                  )}
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <div className="text-sm text-muted-foreground">Customer</div>
                      <div className="font-medium">{project.customer_name || '—'}</div>
                    </div>
                    <div>
                      <div className="text-sm text-muted-foreground">Manager</div>
                      <div className="font-medium">{project.project_manager_name || '—'}</div>
                    </div>
                    <div>
                      <div className="text-sm text-muted-foreground">Start Date</div>
                      <div className="font-medium">{formatDate(project.start_date)}</div>
                    </div>
                    <div>
                      <div className="text-sm text-muted-foreground">End Date</div>
                      <div className="font-medium">{project.end_date ? formatDate(project.end_date) : '—'}</div>
                    </div>
                    <div>
                      <div className="text-sm text-muted-foreground">Billing Type</div>
                      <div className="font-medium capitalize">{project.billing_type || 'Not set'}</div>
                    </div>
                    <div>
                      <div className="text-sm text-muted-foreground">Billable</div>
                      <div className="font-medium">{project.is_billable ? 'Yes' : 'No'}</div>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="text-base">Recent Activity</CardTitle>
                </CardHeader>
                <CardContent>
                  {tasks.length === 0 ? (
                    <p className="text-sm text-muted-foreground">No recent activity</p>
                  ) : (
                    <div className="space-y-3">
                      {tasks.slice(0, 5).map((task) => (
                        <div key={task.id} className="flex items-start gap-3 text-sm">
                          <div className={`mt-1 w-2 h-2 rounded-full ${
                            task.status === 'completed' ? 'bg-green-500' :
                            task.status === 'in_progress' ? 'bg-blue-500' : 'bg-gray-500'
                          }`} />
                          <div>
                            <div className="font-medium">{task.title}</div>
                            <div className="text-muted-foreground">
                              {task.assignee_name || 'Unassigned'}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="tasks">
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle>Tasks</CardTitle>
                  <Link href={`/projects/tasks/new?project_id=${project.id}`}>
                    <Button size="sm">Add Task</Button>
                  </Link>
                </div>
              </CardHeader>
              <CardContent>
                {tasks.length === 0 ? (
                  <p className="text-sm text-muted-foreground">No tasks created yet</p>
                ) : (
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Task</TableHead>
                        <TableHead>Assignee</TableHead>
                        <TableHead>Due Date</TableHead>
                        <TableHead>Hours</TableHead>
                        <TableHead>Status</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {tasks.map((task) => (
                        <TableRow key={task.id}>
                          <TableCell className="font-medium">{task.title}</TableCell>
                          <TableCell>{task.assignee_name || '—'}</TableCell>
                          <TableCell>{task.due_date ? formatDate(task.due_date) : '—'}</TableCell>
                          <TableCell>{task.actual_hours}/{task.estimated_hours}h</TableCell>
                          <TableCell>
                            <Badge variant="secondary" className={taskStatusColors[task.status]}>
                              {task.status === 'in_progress' ? 'In Progress' : task.status.charAt(0).toUpperCase() + task.status.slice(1)}
                            </Badge>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="milestones">
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle>Milestones</CardTitle>
                  <Link href={`/projects/milestones/new?project_id=${project.id}`}>
                    <Button size="sm">Add Milestone</Button>
                  </Link>
                </div>
              </CardHeader>
              <CardContent>
                {milestones.length === 0 ? (
                  <p className="text-sm text-muted-foreground">No milestones created yet</p>
                ) : (
                  <div className="space-y-4">
                    {milestones.map((milestone) => (
                      <div key={milestone.id} className="flex items-center justify-between p-4 border rounded-lg">
                        <div>
                          <div className="font-medium">{milestone.name}</div>
                          <div className="text-sm text-muted-foreground">
                            Due: {formatDate(milestone.due_date)}
                            {milestone.is_billable && ` • ${formatCurrency(milestone.amount || 0)}`}
                          </div>
                        </div>
                        <div className="flex items-center gap-4">
                          <div className="text-right">
                            <div className="text-sm">{milestone.completed_tasks_count}/{milestone.tasks_count} tasks</div>
                            <div className="text-sm text-muted-foreground">{milestone.progress_percentage}%</div>
                          </div>
                          <Badge variant="secondary" className={milestoneStatusColors[milestone.status]}>
                            {milestone.status === 'in_progress' ? 'In Progress' : milestone.status.charAt(0).toUpperCase() + milestone.status.slice(1)}
                          </Badge>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="team">
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle>Team Members</CardTitle>
                  <Link href={`/projects/resources?project_id=${project.id}`}>
                    <Button size="sm">Manage Allocations</Button>
                  </Link>
                </div>
              </CardHeader>
              <CardContent>
                {team.length === 0 ? (
                  <p className="text-sm text-muted-foreground">No team members assigned yet</p>
                ) : (
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Name</TableHead>
                        <TableHead>Role</TableHead>
                        <TableHead>Allocation</TableHead>
                        <TableHead>Hours Logged</TableHead>
                        <TableHead>Joined</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {team.map((member) => (
                        <TableRow key={member.employee_id}>
                          <TableCell>
                            <div>
                              <div className="font-medium">{member.employee_name}</div>
                              <div className="text-sm text-muted-foreground font-mono">{member.employee_code}</div>
                            </div>
                          </TableCell>
                          <TableCell>{member.role}</TableCell>
                          <TableCell>{member.allocation_percentage}%</TableCell>
                          <TableCell>{member.hours_logged}h</TableCell>
                          <TableCell>{formatDate(member.joined_date)}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </DashboardLayout>
  );
}
