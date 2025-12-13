'use client';

/**
 * Projects Overview Report Page
 */

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { DashboardLayout } from '@/components/layout/dashboard-layout';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import projectsApi from '@/lib/api/projects';
import type { ProjectStatus } from '@/types/project';

interface ProjectOverview {
  project_id: string;
  project_name: string;
  status: ProjectStatus;
  progress: number;
  budget_utilization: number;
  hours_utilization: number;
  team_size: number;
}

const statusColors: Record<ProjectStatus, string> = {
  planning: 'bg-gray-100 text-gray-800',
  active: 'bg-green-100 text-green-800',
  on_hold: 'bg-yellow-100 text-yellow-800',
  completed: 'bg-blue-100 text-blue-800',
  cancelled: 'bg-red-100 text-red-800',
};

export default function ProjectsOverviewReportPage() {
  const [projects, setProjects] = useState<ProjectOverview[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      try {
        const data = await projectsApi.getProjectsOverview();
        setProjects(data);
      } catch (error) {
        console.error('Failed to load data:', error);
      } finally {
        setIsLoading(false);
      }
    };
    loadData();
  }, []);

  // Calculate summary stats
  const stats = {
    total: projects.length,
    active: projects.filter((p) => p.status === 'active').length,
    avgProgress: projects.length > 0
      ? Math.round(projects.reduce((sum, p) => sum + p.progress, 0) / projects.length)
      : 0,
    overBudget: projects.filter((p) => p.budget_utilization > 100).length,
    overHours: projects.filter((p) => p.hours_utilization > 100).length,
  };

  const getUtilizationColor = (value: number) => {
    if (value > 100) return 'text-red-600';
    if (value > 80) return 'text-yellow-600';
    return 'text-green-600';
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center gap-4">
          <Link href="/projects">
            <Button variant="ghost" size="icon">
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
            </Button>
          </Link>
          <div>
            <h1 className="text-2xl font-bold tracking-tight">Projects Overview</h1>
            <p className="text-muted-foreground">
              Summary of all projects performance
            </p>
          </div>
        </div>

        {/* Summary Stats */}
        <div className="grid gap-4 md:grid-cols-5">
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Total Projects</CardDescription>
              <CardTitle className="text-2xl">{stats.total}</CardTitle>
            </CardHeader>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Active</CardDescription>
              <CardTitle className="text-2xl text-green-600">{stats.active}</CardTitle>
            </CardHeader>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Avg Progress</CardDescription>
              <CardTitle className="text-2xl">{stats.avgProgress}%</CardTitle>
            </CardHeader>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Over Budget</CardDescription>
              <CardTitle className={`text-2xl ${stats.overBudget > 0 ? 'text-red-600' : ''}`}>
                {stats.overBudget}
              </CardTitle>
            </CardHeader>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Over Hours</CardDescription>
              <CardTitle className={`text-2xl ${stats.overHours > 0 ? 'text-red-600' : ''}`}>
                {stats.overHours}
              </CardTitle>
            </CardHeader>
          </Card>
        </div>

        {/* Projects Table */}
        <Card>
          <CardHeader>
            <CardTitle>All Projects</CardTitle>
            <CardDescription>Performance metrics by project</CardDescription>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="py-8 text-center">
                <div className="h-8 w-8 mx-auto animate-spin rounded-full border-4 border-primary border-t-transparent" />
                <p className="mt-2 text-muted-foreground">Loading data...</p>
              </div>
            ) : projects.length === 0 ? (
              <p className="text-sm text-muted-foreground text-center py-8">No projects found</p>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Project</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Progress</TableHead>
                    <TableHead>Budget Util.</TableHead>
                    <TableHead>Hours Util.</TableHead>
                    <TableHead>Team Size</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {projects.map((project) => (
                    <TableRow key={project.project_id}>
                      <TableCell className="font-medium">
                        <Link href={`/projects/${project.project_id}`} className="hover:underline">
                          {project.project_name}
                        </Link>
                      </TableCell>
                      <TableCell>
                        <Badge variant="secondary" className={statusColors[project.status]}>
                          {project.status === 'on_hold' ? 'On Hold' : project.status.charAt(0).toUpperCase() + project.status.slice(1)}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <div className="w-20 h-2 bg-muted rounded-full overflow-hidden">
                            <div
                              className="h-full bg-primary transition-all"
                              style={{ width: `${project.progress}%` }}
                            />
                          </div>
                          <span className="text-sm">{project.progress}%</span>
                        </div>
                      </TableCell>
                      <TableCell>
                        <span className={getUtilizationColor(project.budget_utilization)}>
                          {project.budget_utilization}%
                        </span>
                      </TableCell>
                      <TableCell>
                        <span className={getUtilizationColor(project.hours_utilization)}>
                          {project.hours_utilization}%
                        </span>
                      </TableCell>
                      <TableCell>{project.team_size}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}
