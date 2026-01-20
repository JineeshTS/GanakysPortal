'use client'

import { useState, useEffect } from 'react'
import { PageHeader } from '@/components/layout/page-header'
import { StatCard } from '@/components/layout/stat-card'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Progress } from '@/components/ui/progress'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog"
import { formatCurrency, formatDate } from '@/lib/format'
import { useApi } from '@/hooks'
import { useToast } from '@/hooks/use-toast'
import type { Project, ProjectStatus, Task, Milestone } from '@/types'
import {
  Plus,
  Search,
  FolderKanban,
  Calendar,
  Users,
  Clock,
  IndianRupee,
  TrendingUp,
  CheckCircle2,
  AlertCircle,
  Pause,
  XCircle,
  MoreHorizontal,
  Target,
  Briefcase,
  Timer,
  ChevronRight,
  BarChart3,
  Loader2,
  Trash2,
  AlertTriangle,
} from 'lucide-react'

// API Response interfaces
interface ProjectListResponse {
  projects: (Project & { tasks_count: number; tasks_completed: number; customer_name?: string })[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

interface ProjectDashboard {
  total_projects: number
  active_projects: number
  completed_this_month: number
  total_budget: number
  total_spent: number
  avg_completion: number
  overdue_projects: number
  team_members: number
  by_status: {
    planning: number
    in_progress: number
    on_hold: number
    completed: number
    cancelled: number
  }
}

// Mock projects data
const mockProjects: (Project & { tasks_count: number; tasks_completed: number; customer_name?: string })[] = [
  {
    id: '1',
    company_id: 'comp-1',
    name: 'E-Commerce Platform Redesign',
    code: 'PRJ-2026-001',
    description: 'Complete redesign of customer-facing e-commerce platform with new UI/UX',
    customer_id: 'cust-1',
    customer_name: 'Bharat Retail Ltd',
    status: 'in_progress',
    start_date: '2025-11-01',
    end_date: '2026-03-31',
    budget: 2500000,
    actual_cost: 1250000,
    manager_id: 'user-1',
    team_members: ['user-1', 'user-2', 'user-3', 'user-4'],
    milestones: [
      { id: 'm1', project_id: '1', name: 'Design Phase', due_date: '2025-12-15', completed_date: '2025-12-12', status: 'completed', created_at: '', updated_at: '' },
      { id: 'm2', project_id: '1', name: 'Development Sprint 1', due_date: '2026-01-15', status: 'in_progress', created_at: '', updated_at: '' },
      { id: 'm3', project_id: '1', name: 'Development Sprint 2', due_date: '2026-02-15', status: 'pending', created_at: '', updated_at: '' },
      { id: 'm4', project_id: '1', name: 'UAT & Go-Live', due_date: '2026-03-31', status: 'pending', created_at: '', updated_at: '' },
    ],
    tasks_count: 48,
    tasks_completed: 22,
    created_at: '2025-10-15',
    updated_at: '2026-01-05',
  },
  {
    id: '2',
    company_id: 'comp-1',
    name: 'Mobile App Development',
    code: 'PRJ-2026-002',
    description: 'Native mobile apps for iOS and Android platforms',
    customer_id: 'cust-2',
    customer_name: 'Quick Services India',
    status: 'in_progress',
    start_date: '2025-12-01',
    end_date: '2026-05-31',
    budget: 1800000,
    actual_cost: 420000,
    manager_id: 'user-2',
    team_members: ['user-2', 'user-5', 'user-6'],
    milestones: [
      { id: 'm5', project_id: '2', name: 'Requirements & Design', due_date: '2025-12-31', completed_date: '2025-12-28', status: 'completed', created_at: '', updated_at: '' },
      { id: 'm6', project_id: '2', name: 'iOS Development', due_date: '2026-02-28', status: 'in_progress', created_at: '', updated_at: '' },
      { id: 'm7', project_id: '2', name: 'Android Development', due_date: '2026-04-30', status: 'pending', created_at: '', updated_at: '' },
    ],
    tasks_count: 36,
    tasks_completed: 12,
    created_at: '2025-11-20',
    updated_at: '2026-01-04',
  },
  {
    id: '3',
    company_id: 'comp-1',
    name: 'Data Migration - Legacy System',
    code: 'PRJ-2025-015',
    description: 'Migrate data from legacy Oracle system to new platform',
    customer_id: 'cust-3',
    customer_name: 'Sunrise Manufacturing',
    status: 'completed',
    start_date: '2025-09-01',
    end_date: '2025-12-31',
    budget: 800000,
    actual_cost: 750000,
    manager_id: 'user-1',
    team_members: ['user-1', 'user-7'],
    tasks_count: 24,
    tasks_completed: 24,
    created_at: '2025-08-15',
    updated_at: '2025-12-28',
  },
  {
    id: '4',
    company_id: 'comp-1',
    name: 'API Integration - Payment Gateway',
    code: 'PRJ-2026-003',
    description: 'Integrate Razorpay and PayU payment gateways',
    customer_name: 'Internal Project',
    status: 'planning',
    start_date: '2026-01-15',
    end_date: '2026-02-28',
    budget: 350000,
    manager_id: 'user-3',
    team_members: ['user-3', 'user-4'],
    tasks_count: 12,
    tasks_completed: 0,
    created_at: '2026-01-02',
    updated_at: '2026-01-02',
  },
  {
    id: '5',
    company_id: 'comp-1',
    name: 'Security Audit & Compliance',
    code: 'PRJ-2025-012',
    description: 'VAPT and compliance certification for banking client',
    customer_id: 'cust-4',
    customer_name: 'Secure Bank Ltd',
    status: 'on_hold',
    start_date: '2025-10-01',
    end_date: '2026-01-31',
    budget: 450000,
    actual_cost: 180000,
    manager_id: 'user-2',
    team_members: ['user-2', 'user-8'],
    tasks_count: 18,
    tasks_completed: 8,
    created_at: '2025-09-20',
    updated_at: '2025-12-15',
  },
]

// Project statistics
const projectStats = {
  totalProjects: 12,
  activeProjects: 6,
  completedThisMonth: 2,
  totalBudget: 8500000,
  totalSpent: 4200000,
  avgCompletion: 58,
  overdueProjects: 1,
  teamMembers: 15,
}

// Status colors and icons
const statusConfig: Record<ProjectStatus, { color: string; icon: React.ReactNode; label: string }> = {
  planning: { color: 'bg-slate-100 text-slate-700', icon: <Target className="h-3.5 w-3.5" />, label: 'Planning' },
  in_progress: { color: 'bg-blue-100 text-blue-700', icon: <TrendingUp className="h-3.5 w-3.5" />, label: 'In Progress' },
  on_hold: { color: 'bg-yellow-100 text-yellow-700', icon: <Pause className="h-3.5 w-3.5" />, label: 'On Hold' },
  completed: { color: 'bg-green-100 text-green-700', icon: <CheckCircle2 className="h-3.5 w-3.5" />, label: 'Completed' },
  cancelled: { color: 'bg-red-100 text-red-700', icon: <XCircle className="h-3.5 w-3.5" />, label: 'Cancelled' },
}

// Project Card Component
function ProjectCard({
  project,
  onClick,
  onDelete,
}: {
  project: typeof mockProjects[0]
  onClick: () => void
  onDelete?: (project: typeof mockProjects[0]) => void
}) {
  const status = statusConfig[project.status]
  const completionPercent = project.tasks_count > 0
    ? Math.round((project.tasks_completed / project.tasks_count) * 100)
    : 0
  const budgetUsedPercent = project.budget && project.actual_cost
    ? Math.round((project.actual_cost / project.budget) * 100)
    : 0

  const isOverdue = project.end_date && new Date(project.end_date) < new Date() && project.status !== 'completed'

  return (
    <Card className="hover:shadow-md transition-shadow cursor-pointer" onClick={onClick}>
      <CardHeader className="pb-2">
        <div className="flex items-start justify-between">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 mb-1">
              <Badge variant="outline" className="text-xs font-mono">
                {project.code}
              </Badge>
              <Badge className={`text-xs ${status.color}`}>
                {status.icon}
                <span className="ml-1">{status.label}</span>
              </Badge>
              {isOverdue && (
                <Badge variant="destructive" className="text-xs">
                  <AlertCircle className="h-3 w-3 mr-1" />
                  Overdue
                </Badge>
              )}
            </div>
            <CardTitle className="text-base truncate">{project.name}</CardTitle>
            {project.customer_name && (
              <CardDescription className="text-xs truncate mt-1">
                <Briefcase className="h-3 w-3 inline mr-1" />
                {project.customer_name}
              </CardDescription>
            )}
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <p className="text-xs text-muted-foreground line-clamp-2 mb-4">
          {project.description}
        </p>

        {/* Progress */}
        <div className="space-y-3">
          <div>
            <div className="flex justify-between text-xs mb-1">
              <span className="text-muted-foreground">Tasks Progress</span>
              <span className="font-medium">
                {project.tasks_completed}/{project.tasks_count} ({completionPercent}%)
              </span>
            </div>
            <Progress value={completionPercent} className="h-1.5" />
          </div>

          {project.budget && (
            <div>
              <div className="flex justify-between text-xs mb-1">
                <span className="text-muted-foreground">Budget Used</span>
                <span className={`font-medium ${budgetUsedPercent > 80 ? 'text-red-600' : ''}`}>
                  {formatCurrency(project.actual_cost || 0)} / {formatCurrency(project.budget)}
                </span>
              </div>
              <Progress
                value={budgetUsedPercent}
                className={`h-1.5 ${budgetUsedPercent > 80 ? '[&>div]:bg-red-500' : ''}`}
              />
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between mt-4 pt-3 border-t">
          <div className="flex items-center gap-3 text-xs text-muted-foreground">
            <div className="flex items-center gap-1">
              <Calendar className="h-3.5 w-3.5" />
              {formatDate(project.end_date || project.start_date)}
            </div>
            <div className="flex items-center gap-1">
              <Users className="h-3.5 w-3.5" />
              {project.team_members.length}
            </div>
          </div>
          <div className="flex items-center gap-1">
            {project.status === 'cancelled' && onDelete && (
              <Button
                variant="ghost"
                size="sm"
                className="h-7 text-xs text-red-600 hover:text-red-700 hover:bg-red-50"
                onClick={(e) => {
                  e.stopPropagation()
                  onDelete(project)
                }}
              >
                <Trash2 className="h-3.5 w-3.5" />
              </Button>
            )}
            <Button variant="ghost" size="sm" className="h-7 text-xs">
              View Details
              <ChevronRight className="h-3.5 w-3.5 ml-1" />
            </Button>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

// Project Detail Dialog
function ProjectDetailDialog({
  project,
  open,
  onOpenChange,
}: {
  project: typeof mockProjects[0] | null
  open: boolean
  onOpenChange: (open: boolean) => void
}) {
  if (!project) return null

  const status = statusConfig[project.status]
  const completionPercent = project.tasks_count > 0
    ? Math.round((project.tasks_completed / project.tasks_count) * 100)
    : 0

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[700px] max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <div className="flex items-start justify-between">
            <div>
              <div className="flex items-center gap-2 mb-2">
                <Badge variant="outline" className="font-mono">{project.code}</Badge>
                <Badge className={status.color}>
                  {status.icon}
                  <span className="ml-1">{status.label}</span>
                </Badge>
              </div>
              <DialogTitle className="text-xl">{project.name}</DialogTitle>
              {project.customer_name && (
                <DialogDescription className="flex items-center gap-2 mt-1">
                  <Briefcase className="h-4 w-4" />
                  {project.customer_name}
                </DialogDescription>
              )}
            </div>
          </div>
        </DialogHeader>

        <div className="space-y-6 py-4">
          {/* Description */}
          <div>
            <Label className="text-xs text-muted-foreground">Description</Label>
            <p className="text-sm mt-1">{project.description}</p>
          </div>

          {/* Key Metrics */}
          <div className="grid grid-cols-4 gap-4">
            <div className="bg-muted/50 rounded-lg p-3 text-center">
              <p className="text-2xl font-bold text-primary">{completionPercent}%</p>
              <p className="text-xs text-muted-foreground">Complete</p>
            </div>
            <div className="bg-muted/50 rounded-lg p-3 text-center">
              <p className="text-2xl font-bold">{project.tasks_completed}</p>
              <p className="text-xs text-muted-foreground">Tasks Done</p>
            </div>
            <div className="bg-muted/50 rounded-lg p-3 text-center">
              <p className="text-2xl font-bold">{project.team_members.length}</p>
              <p className="text-xs text-muted-foreground">Team Members</p>
            </div>
            <div className="bg-muted/50 rounded-lg p-3 text-center">
              <p className="text-2xl font-bold">{project.milestones?.length || 0}</p>
              <p className="text-xs text-muted-foreground">Milestones</p>
            </div>
          </div>

          {/* Timeline & Budget */}
          <div className="grid grid-cols-2 gap-6">
            <div>
              <Label className="text-xs text-muted-foreground">Timeline</Label>
              <div className="flex items-center gap-4 mt-2">
                <div>
                  <p className="text-xs text-muted-foreground">Start Date</p>
                  <p className="font-medium">{formatDate(project.start_date, { format: 'long' })}</p>
                </div>
                <ChevronRight className="h-4 w-4 text-muted-foreground" />
                <div>
                  <p className="text-xs text-muted-foreground">End Date</p>
                  <p className="font-medium">{formatDate(project.end_date, { format: 'long' })}</p>
                </div>
              </div>
            </div>
            <div>
              <Label className="text-xs text-muted-foreground">Budget</Label>
              <div className="mt-2">
                <div className="flex justify-between text-sm mb-1">
                  <span>Spent: {formatCurrency(project.actual_cost || 0)}</span>
                  <span>Budget: {formatCurrency(project.budget || 0)}</span>
                </div>
                <Progress
                  value={project.budget ? ((project.actual_cost || 0) / project.budget) * 100 : 0}
                  className="h-2"
                />
              </div>
            </div>
          </div>

          {/* Milestones */}
          {project.milestones && project.milestones.length > 0 && (
            <div>
              <Label className="text-xs text-muted-foreground">Milestones</Label>
              <div className="mt-2 space-y-2">
                {project.milestones.map((milestone) => {
                  const msStatus = milestone.status === 'completed'
                    ? 'bg-green-100 text-green-700'
                    : milestone.status === 'in_progress'
                    ? 'bg-blue-100 text-blue-700'
                    : milestone.status === 'overdue'
                    ? 'bg-red-100 text-red-700'
                    : 'bg-slate-100 text-slate-700'

                  return (
                    <div
                      key={milestone.id}
                      className="flex items-center justify-between p-3 border rounded-lg"
                    >
                      <div className="flex items-center gap-3">
                        {milestone.status === 'completed' ? (
                          <CheckCircle2 className="h-5 w-5 text-green-600" />
                        ) : milestone.status === 'in_progress' ? (
                          <Clock className="h-5 w-5 text-blue-600" />
                        ) : (
                          <Target className="h-5 w-5 text-muted-foreground" />
                        )}
                        <div>
                          <p className="font-medium text-sm">{milestone.name}</p>
                          <p className="text-xs text-muted-foreground">
                            Due: {formatDate(milestone.due_date)}
                            {milestone.completed_date && ` | Completed: ${formatDate(milestone.completed_date)}`}
                          </p>
                        </div>
                      </div>
                      <Badge className={`text-xs ${msStatus}`}>
                        {milestone.status.replace('_', ' ')}
                      </Badge>
                    </div>
                  )
                })}
              </div>
            </div>
          )}
        </div>

        <DialogFooter className="gap-2">
          <Button variant="outline">Edit Project</Button>
          <Button variant="outline">
            <BarChart3 className="h-4 w-4 mr-2" />
            View Reports
          </Button>
          <Button>
            <FolderKanban className="h-4 w-4 mr-2" />
            View Tasks
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

// Add Project Dialog
function AddProjectDialog({ open, onOpenChange }: { open: boolean; onOpenChange: (open: boolean) => void }) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[550px]">
        <DialogHeader>
          <DialogTitle>Create New Project</DialogTitle>
          <DialogDescription>
            Enter project details to create a new project
          </DialogDescription>
        </DialogHeader>
        <div className="grid gap-4 py-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="name">Project Name *</Label>
              <Input id="name" placeholder="E-Commerce Platform" />
            </div>
            <div className="space-y-2">
              <Label htmlFor="code">Project Code</Label>
              <Input id="code" placeholder="PRJ-2026-XXX" />
            </div>
          </div>
          <div className="space-y-2">
            <Label htmlFor="description">Description</Label>
            <Input id="description" placeholder="Brief project description..." />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="customer">Customer</Label>
              <Select>
                <SelectTrigger>
                  <SelectValue placeholder="Select customer" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="cust-1">Bharat Retail Ltd</SelectItem>
                  <SelectItem value="cust-2">Quick Services India</SelectItem>
                  <SelectItem value="cust-3">Sunrise Manufacturing</SelectItem>
                  <SelectItem value="internal">Internal Project</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="manager">Project Manager *</Label>
              <Select>
                <SelectTrigger>
                  <SelectValue placeholder="Select manager" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="user-1">Arun Sharma</SelectItem>
                  <SelectItem value="user-2">Neha Gupta</SelectItem>
                  <SelectItem value="user-3">Kiran Patel</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          <div className="grid grid-cols-3 gap-4">
            <div className="space-y-2">
              <Label htmlFor="start">Start Date *</Label>
              <Input id="start" type="date" />
            </div>
            <div className="space-y-2">
              <Label htmlFor="end">End Date</Label>
              <Input id="end" type="date" />
            </div>
            <div className="space-y-2">
              <Label htmlFor="budget">Budget (INR)</Label>
              <Input id="budget" type="number" placeholder="500000" />
            </div>
          </div>
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button onClick={() => onOpenChange(false)}>Create Project</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

export default function ProjectsPage() {
  const { toast } = useToast()
  const [searchQuery, setSearchQuery] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [addDialogOpen, setAddDialogOpen] = useState(false)
  const [selectedProject, setSelectedProject] = useState<typeof mockProjects[0] | null>(null)
  const [detailDialogOpen, setDetailDialogOpen] = useState(false)
  const [localProjects, setLocalProjects] = useState<typeof mockProjects>(mockProjects)

  // Delete state
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false)
  const [projectToDelete, setProjectToDelete] = useState<typeof mockProjects[0] | null>(null)
  const [isDeleting, setIsDeleting] = useState(false)
  const deleteApi = useApi()

  const handleDeleteClick = (project: typeof mockProjects[0]) => {
    setProjectToDelete(project)
    setDeleteDialogOpen(true)
  }

  const handleDeleteConfirm = async () => {
    if (!projectToDelete) return
    setIsDeleting(true)
    try {
      await deleteApi.delete(`/projects/${projectToDelete.id}`)
      setLocalProjects(localProjects.filter(p => p.id !== projectToDelete.id))
      setDeleteDialogOpen(false)
      setProjectToDelete(null)
    } catch (error) {
      console.error('Failed to delete project:', error)
      toast.error('Failed to delete project', 'Please try again or contact support')
    } finally {
      setIsDeleting(false)
    }
  }

  const { data: projectsData, isLoading: projectsLoading, error: projectsError, get: getProjects } = useApi<ProjectListResponse>()
  const { data: dashboardData, isLoading: dashboardLoading, get: getDashboard } = useApi<ProjectDashboard>()

  // Fetch projects and dashboard on mount
  useEffect(() => {
    const params = new URLSearchParams()
    if (statusFilter !== 'all') params.set('status', statusFilter)
    if (searchQuery) params.set('search', searchQuery)

    getProjects(`/projects?${params.toString()}`)
    getDashboard('/projects/dashboard')
  }, [statusFilter, searchQuery, getProjects, getDashboard])

  // Sync API data to local state
  useEffect(() => {
    if (projectsData?.projects) {
      setLocalProjects(projectsData.projects)
    }
  }, [projectsData])

  const projects = localProjects
  const isLoading = projectsLoading || dashboardLoading

  const filteredProjects = projects.filter((project) => {
    const matchesSearch = !searchQuery ||
      project.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      project.code.toLowerCase().includes(searchQuery.toLowerCase()) ||
      project.customer_name?.toLowerCase().includes(searchQuery.toLowerCase())

    const matchesStatus = statusFilter === 'all' || project.status === statusFilter

    return matchesSearch && matchesStatus
  })

  const handleProjectClick = (project: typeof mockProjects[0]) => {
    setSelectedProject(project)
    setDetailDialogOpen(true)
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Project Management"
        description="Track projects, milestones, and team progress"
        actions={
          <div className="flex gap-2">
            <div className="relative">
              <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search projects..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-8 w-64"
              />
            </div>
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-[140px]">
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="planning">Planning</SelectItem>
                <SelectItem value="in_progress">In Progress</SelectItem>
                <SelectItem value="on_hold">On Hold</SelectItem>
                <SelectItem value="completed">Completed</SelectItem>
              </SelectContent>
            </Select>
            <Button onClick={() => setAddDialogOpen(true)}>
              <Plus className="h-4 w-4 mr-2" />
              New Project
            </Button>
          </div>
        }
      />

      {/* Loading State */}
      {isLoading && (
        <Card className="p-8 flex items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <span className="ml-2">Loading projects...</span>
        </Card>
      )}

      {/* Error State */}
      {projectsError && (
        <Card className="p-4 border-red-200 bg-red-50">
          <div className="flex items-center gap-2 text-red-600">
            <AlertCircle className="h-5 w-5" />
            <span>{projectsError}</span>
          </div>
        </Card>
      )}

      {/* Stats */}
      <div className="grid gap-4 md:grid-cols-5">
        <StatCard
          title="Total Projects"
          value={dashboardData?.total_projects || projectStats.totalProjects}
          icon={FolderKanban}
          description={`${dashboardData?.active_projects || projectStats.activeProjects} active`}
        />
        <StatCard
          title="Total Budget"
          value={formatCurrency(dashboardData?.total_budget || projectStats.totalBudget)}
          icon={IndianRupee}
          description={`${formatCurrency(dashboardData?.total_spent || projectStats.totalSpent)} spent`}
        />
        <StatCard
          title="Avg Completion"
          value={`${dashboardData?.avg_completion || projectStats.avgCompletion}%`}
          icon={TrendingUp}
          description="Across all projects"
        />
        <StatCard
          title="Team Members"
          value={dashboardData?.team_members || projectStats.teamMembers}
          icon={Users}
          description="Assigned to projects"
        />
        <StatCard
          title="Overdue"
          value={dashboardData?.overdue_projects || projectStats.overdueProjects}
          icon={AlertCircle}
          description="Need attention"
        />
      </div>

      {/* Project Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {filteredProjects.map((project) => (
          <ProjectCard
            key={project.id}
            project={project}
            onClick={() => handleProjectClick(project)}
            onDelete={handleDeleteClick}
          />
        ))}
      </div>

      {filteredProjects.length === 0 && (
        <div className="text-center py-12">
          <FolderKanban className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
          <p className="text-muted-foreground">No projects found</p>
        </div>
      )}

      {/* Dialogs */}
      <AddProjectDialog open={addDialogOpen} onOpenChange={setAddDialogOpen} />
      <ProjectDetailDialog
        project={selectedProject}
        open={detailDialogOpen}
        onOpenChange={setDetailDialogOpen}
      />

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-red-500" />
              Delete Project
            </AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete the project <strong>{projectToDelete?.name}</strong>?
              This will remove all associated tasks and milestones. This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={isDeleting}>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDeleteConfirm}
              disabled={isDeleting}
              className="bg-red-600 hover:bg-red-700 focus:ring-red-600"
            >
              {isDeleting ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Deleting...
                </>
              ) : (
                'Delete'
              )}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
}
