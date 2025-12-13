'use client';

/**
 * Resource Allocation Page
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
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import projectsApi from '@/lib/api/projects';
import type { ResourceAllocation, Project, ResourceAllocationStatus } from '@/types/project';

const statusColors: Record<ResourceAllocationStatus, string> = {
  planned: 'bg-gray-100 text-gray-800',
  active: 'bg-green-100 text-green-800',
  completed: 'bg-blue-100 text-blue-800',
};

export default function ResourcesPage() {
  const searchParams = useSearchParams();
  const [allocations, setAllocations] = useState<ResourceAllocation[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [isLoading, setIsLoading] = useState(true);
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
    employee_id: '',
    role: '',
    allocation_percentage: 100,
    start_date: new Date().toISOString().split('T')[0],
    end_date: '',
    hourly_rate: 0,
  });

  const loadData = useCallback(async () => {
    setIsLoading(true);
    try {
      const [allocationsData, projectsData] = await Promise.all([
        projectsApi.getAllocations({
          project_id: projectFilter || undefined,
          skip: (currentPage - 1) * pageSize,
          limit: pageSize,
        }),
        projectsApi.getProjects({ limit: 100, status: 'active' }),
      ]);
      setAllocations(allocationsData.items);
      setTotal(allocationsData.total);
      setProjects(projectsData.items);
    } catch (error) {
      console.error('Failed to load data:', error);
    } finally {
      setIsLoading(false);
    }
  }, [projectFilter, currentPage]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleOpenDialog = () => {
    setFormData({
      project_id: projectFilter || '',
      employee_id: '',
      role: '',
      allocation_percentage: 100,
      start_date: new Date().toISOString().split('T')[0],
      end_date: '',
      hourly_rate: 0,
    });
    setDialogOpen(true);
  };

  const handleSave = async () => {
    setIsSaving(true);
    try {
      await projectsApi.createAllocation({
        ...formData,
        end_date: formData.end_date || undefined,
      });
      setDialogOpen(false);
      loadData();
    } catch (error) {
      console.error('Failed to create allocation:', error);
    } finally {
      setIsSaving(false);
    }
  };

  const handleDeleteAllocation = async (id: string) => {
    if (!confirm('Are you sure you want to remove this allocation?')) return;
    try {
      await projectsApi.deleteAllocation(id);
      loadData();
    } catch (error) {
      console.error('Failed to delete allocation:', error);
    }
  };

  const formatDate = (date: string) => {
    return new Date(date).toLocaleDateString('en-IN', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
    });
  };

  // Group allocations by employee for summary
  const employeeSummary = allocations.reduce((acc, alloc) => {
    if (!acc[alloc.employee_id]) {
      acc[alloc.employee_id] = {
        name: alloc.employee_name,
        total_allocation: 0,
        projects: 0,
      };
    }
    acc[alloc.employee_id].total_allocation += alloc.allocation_percentage;
    acc[alloc.employee_id].projects += 1;
    return acc;
  }, {} as Record<string, { name: string; total_allocation: number; projects: number }>);

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
              <h1 className="text-2xl font-bold tracking-tight">Resource Allocation</h1>
              <p className="text-muted-foreground">
                Manage team assignments to projects
              </p>
            </div>
          </div>
          <Button onClick={handleOpenDialog}>
            <svg className="mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            Add Allocation
          </Button>
        </div>

        {/* Summary Cards */}
        {Object.keys(employeeSummary).length > 0 && (
          <div className="grid gap-4 md:grid-cols-4">
            {Object.entries(employeeSummary).slice(0, 4).map(([id, data]) => (
              <Card key={id}>
                <CardHeader className="pb-2">
                  <CardDescription>{data.name}</CardDescription>
                  <CardTitle className={`text-2xl ${data.total_allocation > 100 ? 'text-red-600' : ''}`}>
                    {data.total_allocation}%
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground">
                    {data.projects} project{data.projects !== 1 ? 's' : ''}
                    {data.total_allocation > 100 && (
                      <span className="text-red-600 ml-2">(Over-allocated)</span>
                    )}
                  </p>
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        {/* Filters */}
        <div className="flex gap-4">
          <Select
            value={projectFilter}
            onValueChange={(v) => {
              setProjectFilter(v);
              setCurrentPage(1);
            }}
          >
            <SelectTrigger className="w-[250px]">
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
        </div>

        {/* Table */}
        <div className="rounded-lg border bg-card">
          {isLoading ? (
            <div className="p-8 text-center">
              <div className="h-8 w-8 mx-auto animate-spin rounded-full border-4 border-primary border-t-transparent" />
              <p className="mt-2 text-muted-foreground">Loading allocations...</p>
            </div>
          ) : allocations.length === 0 ? (
            <div className="p-8 text-center">
              <svg className="mx-auto h-12 w-12 text-muted-foreground" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
              </svg>
              <h3 className="mt-2 font-medium">No allocations found</h3>
              <p className="text-sm text-muted-foreground">
                {projectFilter ? 'No team members allocated to this project' : 'Start allocating resources to projects'}
              </p>
              <Button className="mt-4" onClick={handleOpenDialog}>
                Add Allocation
              </Button>
            </div>
          ) : (
            <>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Employee</TableHead>
                    <TableHead>Project</TableHead>
                    <TableHead>Role</TableHead>
                    <TableHead>Allocation</TableHead>
                    <TableHead>Period</TableHead>
                    <TableHead>Hours</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {allocations.map((allocation) => (
                    <TableRow key={allocation.id}>
                      <TableCell>
                        <div>
                          <div className="font-medium">{allocation.employee_name}</div>
                          <div className="text-sm text-muted-foreground font-mono">{allocation.employee_code}</div>
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="text-sm">
                          <div>{allocation.project_name}</div>
                          <div className="text-muted-foreground font-mono text-xs">{allocation.project_code}</div>
                        </div>
                      </TableCell>
                      <TableCell>{allocation.role}</TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <div className="w-12 h-2 bg-muted rounded-full overflow-hidden">
                            <div
                              className={`h-full transition-all ${
                                allocation.allocation_percentage > 100 ? 'bg-red-500' : 'bg-primary'
                              }`}
                              style={{ width: `${Math.min(allocation.allocation_percentage, 100)}%` }}
                            />
                          </div>
                          <span className={allocation.allocation_percentage > 100 ? 'text-red-600' : ''}>
                            {allocation.allocation_percentage}%
                          </span>
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="text-sm">
                          <div>{formatDate(allocation.start_date)}</div>
                          {allocation.end_date && (
                            <div className="text-muted-foreground">to {formatDate(allocation.end_date)}</div>
                          )}
                        </div>
                      </TableCell>
                      <TableCell>
                        <span className="text-sm">{allocation.actual_hours}/{allocation.estimated_hours}h</span>
                      </TableCell>
                      <TableCell>
                        <Badge variant="secondary" className={statusColors[allocation.status]}>
                          {allocation.status.charAt(0).toUpperCase() + allocation.status.slice(1)}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-right">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleDeleteAllocation(allocation.id)}
                        >
                          Remove
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>

              {/* Pagination */}
              {totalPages > 1 && (
                <div className="flex items-center justify-between border-t px-4 py-3">
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
        </div>

        {/* Add Allocation Dialog */}
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogContent className="max-w-lg">
            <DialogHeader>
              <DialogTitle>Add Resource Allocation</DialogTitle>
              <DialogDescription>Allocate a team member to a project</DialogDescription>
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
                <Label htmlFor="employee_id">Employee ID *</Label>
                <Input
                  id="employee_id"
                  value={formData.employee_id}
                  onChange={(e) => setFormData({ ...formData, employee_id: e.target.value })}
                  placeholder="Enter employee ID"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="role">Role *</Label>
                <Input
                  id="role"
                  value={formData.role}
                  onChange={(e) => setFormData({ ...formData, role: e.target.value })}
                  placeholder="e.g., Developer, Designer, QA"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="allocation">Allocation %</Label>
                  <Input
                    id="allocation"
                    type="number"
                    value={formData.allocation_percentage}
                    onChange={(e) => setFormData({ ...formData, allocation_percentage: parseInt(e.target.value) || 0 })}
                    min={0}
                    max={100}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="hourly_rate">Hourly Rate</Label>
                  <Input
                    id="hourly_rate"
                    type="number"
                    value={formData.hourly_rate}
                    onChange={(e) => setFormData({ ...formData, hourly_rate: parseFloat(e.target.value) || 0 })}
                    min={0}
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="start_date">Start Date *</Label>
                  <Input
                    id="start_date"
                    type="date"
                    value={formData.start_date}
                    onChange={(e) => setFormData({ ...formData, start_date: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="end_date">End Date</Label>
                  <Input
                    id="end_date"
                    type="date"
                    value={formData.end_date}
                    onChange={(e) => setFormData({ ...formData, end_date: e.target.value })}
                  />
                </div>
              </div>
            </div>

            <DialogFooter>
              <Button variant="outline" onClick={() => setDialogOpen(false)} disabled={isSaving}>
                Cancel
              </Button>
              <Button
                onClick={handleSave}
                disabled={isSaving || !formData.project_id || !formData.employee_id || !formData.role}
              >
                {isSaving ? 'Saving...' : 'Add Allocation'}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>
    </DashboardLayout>
  );
}
