'use client';

/**
 * Project Milestones Page
 */

import { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';
import { useSearchParams } from 'next/navigation';
import { DashboardLayout } from '@/components/layout/dashboard-layout';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
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
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Badge } from '@/components/ui/badge';
import { Checkbox } from '@/components/ui/checkbox';
import projectsApi from '@/lib/api/projects';
import type { Milestone, Project, MilestoneStatus } from '@/types/project';

const statusColors: Record<MilestoneStatus, string> = {
  pending: 'bg-gray-100 text-gray-800',
  in_progress: 'bg-blue-100 text-blue-800',
  completed: 'bg-green-100 text-green-800',
  overdue: 'bg-red-100 text-red-800',
};

export default function MilestonesPage() {
  const searchParams = useSearchParams();
  const [milestones, setMilestones] = useState<Milestone[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [projectFilter, setProjectFilter] = useState<string>(searchParams.get('project_id') || '');
  const [total, setTotal] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 10;

  // Dialog state
  const [dialogOpen, setDialogOpen] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  // Form state
  const [formData, setFormData] = useState({
    project_id: searchParams.get('project_id') || '',
    name: '',
    description: '',
    due_date: '',
    deliverables: '',
    is_billable: false,
    amount: 0,
  });

  const loadData = useCallback(async () => {
    setIsLoading(true);
    try {
      const [milestonesData, projectsData] = await Promise.all([
        projectsApi.getMilestones({
          search: searchQuery || undefined,
          status: (statusFilter as MilestoneStatus) || undefined,
          project_id: projectFilter || undefined,
          skip: (currentPage - 1) * pageSize,
          limit: pageSize,
        }),
        projectsApi.getProjects({ limit: 100, status: 'active' }),
      ]);
      setMilestones(milestonesData.items);
      setTotal(milestonesData.total);
      setProjects(projectsData.items);
    } catch (error) {
      console.error('Failed to load data:', error);
    } finally {
      setIsLoading(false);
    }
  }, [searchQuery, statusFilter, projectFilter, currentPage]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleOpenDialog = () => {
    setFormData({
      project_id: projectFilter || '',
      name: '',
      description: '',
      due_date: '',
      deliverables: '',
      is_billable: false,
      amount: 0,
    });
    setDialogOpen(true);
  };

  const handleSave = async () => {
    setIsSaving(true);
    try {
      await projectsApi.createMilestone({
        ...formData,
        amount: formData.is_billable ? formData.amount : undefined,
      });
      setDialogOpen(false);
      loadData();
    } catch (error) {
      console.error('Failed to create milestone:', error);
    } finally {
      setIsSaving(false);
    }
  };

  const handleCompleteMilestone = async (id: string) => {
    try {
      await projectsApi.completeMilestone(id);
      loadData();
    } catch (error) {
      console.error('Failed to complete milestone:', error);
    }
  };

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

  const getDaysUntilDue = (dueDate: string) => {
    const today = new Date();
    const due = new Date(dueDate);
    const diff = Math.ceil((due.getTime() - today.getTime()) / (1000 * 60 * 60 * 24));
    return diff;
  };

  const totalPages = Math.ceil(total / pageSize);

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href="/projects">
              <Button variant="ghost" size="icon">
                <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                </svg>
              </Button>
            </Link>
            <div>
              <h1 className="text-2xl font-bold tracking-tight">Milestones</h1>
              <p className="text-muted-foreground">
                Track project deliverables and deadlines
              </p>
            </div>
          </div>
          <Button onClick={handleOpenDialog}>
            <svg className="mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            New Milestone
          </Button>
        </div>

        {/* Filters */}
        <div className="flex gap-4 flex-wrap">
          <div className="flex-1 max-w-sm">
            <Input
              placeholder="Search milestones..."
              value={searchQuery}
              onChange={(e) => {
                setSearchQuery(e.target.value);
                setCurrentPage(1);
              }}
            />
          </div>
          <Select
            value={projectFilter}
            onValueChange={(v) => {
              setProjectFilter(v);
              setCurrentPage(1);
            }}
          >
            <SelectTrigger className="w-[200px]">
              <SelectValue placeholder="All Projects" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="">All Projects</SelectItem>
              {projects.map((project) => (
                <SelectItem key={project.id} value={project.id}>
                  {project.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Select
            value={statusFilter}
            onValueChange={(v) => {
              setStatusFilter(v);
              setCurrentPage(1);
            }}
          >
            <SelectTrigger className="w-[150px]">
              <SelectValue placeholder="All Status" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="">All Status</SelectItem>
              <SelectItem value="pending">Pending</SelectItem>
              <SelectItem value="in_progress">In Progress</SelectItem>
              <SelectItem value="completed">Completed</SelectItem>
              <SelectItem value="overdue">Overdue</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Milestones Grid */}
        {isLoading ? (
          <div className="p-8 text-center">
            <div className="h-8 w-8 mx-auto animate-spin rounded-full border-4 border-primary border-t-transparent" />
            <p className="mt-2 text-muted-foreground">Loading milestones...</p>
          </div>
        ) : milestones.length === 0 ? (
          <Card>
            <CardContent className="py-8 text-center">
              <svg className="mx-auto h-12 w-12 text-muted-foreground" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
              <h3 className="mt-2 font-medium">No milestones found</h3>
              <p className="text-sm text-muted-foreground">
                {searchQuery || statusFilter || projectFilter ? 'Try adjusting your filters' : 'Create your first milestone'}
              </p>
              {!searchQuery && !statusFilter && (
                <Button className="mt-4" onClick={handleOpenDialog}>
                  New Milestone
                </Button>
              )}
            </CardContent>
          </Card>
        ) : (
          <>
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {milestones.map((milestone) => {
                const daysUntilDue = getDaysUntilDue(milestone.due_date);
                const isOverdue = daysUntilDue < 0 && milestone.status !== 'completed';

                return (
                  <Card key={milestone.id} className={isOverdue ? 'border-red-200' : ''}>
                    <CardHeader className="pb-2">
                      <div className="flex items-start justify-between">
                        <div className="space-y-1">
                          <CardTitle className="text-base">{milestone.name}</CardTitle>
                          <CardDescription>{milestone.project_name}</CardDescription>
                        </div>
                        <Badge variant="secondary" className={statusColors[milestone.status]}>
                          {milestone.status === 'in_progress' ? 'In Progress' : milestone.status.charAt(0).toUpperCase() + milestone.status.slice(1)}
                        </Badge>
                      </div>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      {milestone.description && (
                        <p className="text-sm text-muted-foreground">{milestone.description}</p>
                      )}

                      <div className="flex items-center justify-between text-sm">
                        <span className="text-muted-foreground">Due Date</span>
                        <span className={isOverdue ? 'text-red-600 font-medium' : ''}>
                          {formatDate(milestone.due_date)}
                          {isOverdue && ' (Overdue)'}
                          {!isOverdue && daysUntilDue <= 7 && daysUntilDue >= 0 && (
                            <span className="text-yellow-600 ml-1">({daysUntilDue}d left)</span>
                          )}
                        </span>
                      </div>

                      <div className="flex items-center justify-between text-sm">
                        <span className="text-muted-foreground">Tasks</span>
                        <span>{milestone.completed_tasks_count}/{milestone.tasks_count}</span>
                      </div>

                      {/* Progress bar */}
                      <div className="space-y-1">
                        <div className="flex justify-between text-sm">
                          <span className="text-muted-foreground">Progress</span>
                          <span>{milestone.progress_percentage}%</span>
                        </div>
                        <div className="w-full h-2 bg-muted rounded-full overflow-hidden">
                          <div
                            className={`h-full transition-all ${
                              milestone.progress_percentage === 100 ? 'bg-green-500' : 'bg-primary'
                            }`}
                            style={{ width: `${milestone.progress_percentage}%` }}
                          />
                        </div>
                      </div>

                      {milestone.is_billable && (
                        <div className="flex items-center justify-between text-sm pt-2 border-t">
                          <span className="text-muted-foreground">Amount</span>
                          <span className="font-medium">{formatCurrency(milestone.amount || 0)}</span>
                        </div>
                      )}

                      {milestone.status !== 'completed' && (
                        <div className="pt-2">
                          <Button
                            size="sm"
                            variant="outline"
                            className="w-full"
                            onClick={() => handleCompleteMilestone(milestone.id)}
                          >
                            Mark Complete
                          </Button>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                );
              })}
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="flex items-center justify-between">
                <div className="text-sm text-muted-foreground">
                  Showing {(currentPage - 1) * pageSize + 1} to {Math.min(currentPage * pageSize, total)} of {total}
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

        {/* Create Milestone Dialog */}
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogContent className="max-w-lg">
            <DialogHeader>
              <DialogTitle>New Milestone</DialogTitle>
              <DialogDescription>Create a new project milestone</DialogDescription>
            </DialogHeader>

            <div className="grid gap-4 py-4">
              <div className="space-y-2">
                <Label htmlFor="project">Project *</Label>
                <Select
                  value={formData.project_id}
                  onValueChange={(v) => setFormData({ ...formData, project_id: v })}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select project" />
                  </SelectTrigger>
                  <SelectContent>
                    {projects.map((project) => (
                      <SelectItem key={project.id} value={project.id}>
                        {project.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="name">Milestone Name *</Label>
                <Input
                  id="name"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder="e.g., Phase 1 Delivery"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="description">Description</Label>
                <textarea
                  id="description"
                  className="w-full min-h-[80px] rounded-md border border-input bg-background px-3 py-2 text-sm"
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  placeholder="Describe this milestone..."
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="due_date">Due Date *</Label>
                <Input
                  id="due_date"
                  type="date"
                  value={formData.due_date}
                  onChange={(e) => setFormData({ ...formData, due_date: e.target.value })}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="deliverables">Deliverables</Label>
                <textarea
                  id="deliverables"
                  className="w-full min-h-[60px] rounded-md border border-input bg-background px-3 py-2 text-sm"
                  value={formData.deliverables}
                  onChange={(e) => setFormData({ ...formData, deliverables: e.target.value })}
                  placeholder="List the deliverables for this milestone..."
                />
              </div>

              <div className="flex items-center space-x-2">
                <Checkbox
                  id="is_billable"
                  checked={formData.is_billable}
                  onCheckedChange={(checked) => setFormData({ ...formData, is_billable: !!checked })}
                />
                <Label htmlFor="is_billable">This is a billable milestone</Label>
              </div>

              {formData.is_billable && (
                <div className="space-y-2">
                  <Label htmlFor="amount">Billing Amount</Label>
                  <Input
                    id="amount"
                    type="number"
                    value={formData.amount}
                    onChange={(e) => setFormData({ ...formData, amount: parseFloat(e.target.value) || 0 })}
                    min={0}
                  />
                </div>
              )}
            </div>

            <DialogFooter>
              <Button variant="outline" onClick={() => setDialogOpen(false)} disabled={isSaving}>
                Cancel
              </Button>
              <Button
                onClick={handleSave}
                disabled={isSaving || !formData.project_id || !formData.name || !formData.due_date}
              >
                {isSaving ? 'Creating...' : 'Create Milestone'}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>
    </DashboardLayout>
  );
}
