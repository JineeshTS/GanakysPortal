'use client'

import { useState, useEffect, useCallback } from 'react'
import { PageHeader } from '@/components/layout/page-header'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Progress } from '@/components/ui/progress'
import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Skeleton } from '@/components/ui/skeleton'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { useApi, useToast } from '@/hooks'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog'
import {
  UserPlus,
  Users,
  Clock,
  CheckCircle2,
  AlertCircle,
  FileText,
  Laptop,
  CreditCard,
  Mail,
  Calendar,
  ChevronRight,
  Search,
  Filter,
  MoreVertical,
  Eye,
  Edit,
  Send,
  UserCheck,
  Building2,
  GraduationCap,
  Loader2,
  RefreshCw,
  Trash2,
  AlertTriangle
} from 'lucide-react'

// Types
interface OnboardingStats {
  total: number
  pending: number
  in_progress: number
  completed: number
  blocked: number
  overdue_tasks: number
}

interface EmployeeInfo {
  id: string
  employee_code: string
  full_name: string
  position?: string
  department?: string
  profile_photo_url?: string
}

interface OnboardingSession {
  id: string
  company_id: string
  employee_id: string
  employee?: EmployeeInfo
  template_id?: string
  status: string
  joining_date: string
  expected_completion_date?: string
  actual_completion_date?: string
  mentor_id?: string
  mentor_name?: string
  reporting_manager_id?: string
  manager_name?: string
  progress_percent: number
  tasks_completed: number
  tasks_total: number
  documents_collected: number
  documents_total: number
  notes?: string
  blocked_reason?: string
  created_at: string
  updated_at: string
}

interface OnboardingTask {
  id: string
  session_id: string
  title: string
  description?: string
  category: string
  assigned_to?: string
  assigned_role?: string
  due_date?: string
  completed_date?: string
  status: string
  priority: string
  is_required: boolean
  order: number
  notes?: string
  created_at: string
}

interface OnboardingTemplate {
  id: string
  company_id: string
  name: string
  description?: string
  department_id?: string
  duration_days: number
  is_default: boolean
  is_active: boolean
  task_count: number
  created_at: string
}

interface OnboardingDocument {
  id: string
  session_id: string
  document_type: string
  document_name: string
  is_required: boolean
  is_collected: boolean
  is_verified: boolean
  document_id?: string
  collected_date?: string
  notes?: string
}

interface SessionListResponse {
  success: boolean
  data: OnboardingSession[]
  meta: { page: number; limit: number; total: number }
}

interface TaskListResponse {
  success: boolean
  data: OnboardingTask[]
  meta: { page: number; limit: number; total: number }
}

interface TemplateListResponse {
  success: boolean
  data: OnboardingTemplate[]
  meta: { page: number; limit: number; total: number }
}

interface Employee {
  id: string
  employee_code: string
  first_name: string
  last_name: string
  department_id?: string
}

interface EmployeeListResponse {
  data: Employee[]
  total: number
}

const statusColors: Record<string, string> = {
  pending: 'bg-yellow-100 text-yellow-800',
  in_progress: 'bg-blue-100 text-blue-800',
  completed: 'bg-green-100 text-green-800',
  blocked: 'bg-red-100 text-red-800',
  overdue: 'bg-red-100 text-red-800',
}

const priorityColors: Record<string, string> = {
  low: 'bg-gray-100 text-gray-800',
  medium: 'bg-yellow-100 text-yellow-800',
  high: 'bg-red-100 text-red-800',
}

const categoryLabels: Record<string, string> = {
  documentation: 'Documentation',
  it_setup: 'IT Setup',
  communication: 'Communication',
  training: 'Training',
  compliance: 'Compliance',
  finance: 'Finance',
  integration: 'Integration',
  other: 'Other',
}

export default function OnboardingPage() {
  const [searchQuery, setSearchQuery] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')
  const [selectedSession, setSelectedSession] = useState<OnboardingSession | null>(null)
  const [isNewOnboardingOpen, setIsNewOnboardingOpen] = useState(false)
  const [newOnboardingForm, setNewOnboardingForm] = useState({
    employee_id: '',
    joining_date: '',
    reporting_manager_id: '',
    mentor_id: '',
    template_id: '',
    notes: ''
  })
  const { showToast } = useToast()

  // API hooks
  const { data: statsData, isLoading: isLoadingStats, get: getStats } = useApi<OnboardingStats>()
  const { data: sessionsData, isLoading: isLoadingSessions, get: getSessions } = useApi<SessionListResponse>()
  const { data: tasksData, isLoading: isLoadingTasks, get: getTasks } = useApi<TaskListResponse>()
  const { data: templatesData, isLoading: isLoadingTemplates, get: getTemplates } = useApi<TemplateListResponse>()
  const { data: employeesData, get: getEmployees } = useApi<EmployeeListResponse>()
  const { isLoading: isCreating, post: createSession } = useApi<OnboardingSession>()
  const { post: completeTask } = useApi<OnboardingTask>()
  const deleteSessionApi = useApi()
  const deleteTemplateApi = useApi()

  // Local state for data management
  const [localSessions, setLocalSessions] = useState<OnboardingSession[]>([])
  const [localTemplates, setLocalTemplates] = useState<OnboardingTemplate[]>([])

  // Delete state for sessions
  const [deleteSessionDialogOpen, setDeleteSessionDialogOpen] = useState(false)
  const [sessionToDelete, setSessionToDelete] = useState<OnboardingSession | null>(null)
  const [isDeletingSession, setIsDeletingSession] = useState(false)

  // Delete state for templates
  const [deleteTemplateDialogOpen, setDeleteTemplateDialogOpen] = useState(false)
  const [templateToDelete, setTemplateToDelete] = useState<OnboardingTemplate | null>(null)
  const [isDeletingTemplate, setIsDeletingTemplate] = useState(false)

  // Template view/edit state
  const [selectedTemplate, setSelectedTemplate] = useState<OnboardingTemplate | null>(null)
  const [isViewTemplateOpen, setIsViewTemplateOpen] = useState(false)
  const [isEditTemplateOpen, setIsEditTemplateOpen] = useState(false)

  const handleViewTemplate = (template: OnboardingTemplate) => {
    setSelectedTemplate(template)
    setIsViewTemplateOpen(true)
  }

  const handleEditTemplate = (template: OnboardingTemplate) => {
    setSelectedTemplate(template)
    setIsEditTemplateOpen(true)
  }

  const handleDeleteSessionClick = (session: OnboardingSession) => {
    setSessionToDelete(session)
    setDeleteSessionDialogOpen(true)
  }

  const handleDeleteSessionConfirm = async () => {
    if (!sessionToDelete) return
    setIsDeletingSession(true)
    try {
      await deleteSessionApi.delete(`/onboarding/sessions/${sessionToDelete.id}`)
      setLocalSessions(localSessions.filter(s => s.id !== sessionToDelete.id))
      if (selectedSession?.id === sessionToDelete.id) {
        setSelectedSession(null)
      }
      setDeleteSessionDialogOpen(false)
      setSessionToDelete(null)
      showToast('success', 'Onboarding session deleted successfully')
    } catch (error) {
      console.error('Failed to delete session:', error)
      showToast('error', 'Failed to delete onboarding session')
    } finally {
      setIsDeletingSession(false)
    }
  }

  const handleDeleteTemplateClick = (template: OnboardingTemplate) => {
    setTemplateToDelete(template)
    setDeleteTemplateDialogOpen(true)
  }

  const handleDeleteTemplateConfirm = async () => {
    if (!templateToDelete) return
    setIsDeletingTemplate(true)
    try {
      await deleteTemplateApi.delete(`/onboarding/templates/${templateToDelete.id}`)
      setLocalTemplates(localTemplates.filter(t => t.id !== templateToDelete.id))
      setDeleteTemplateDialogOpen(false)
      setTemplateToDelete(null)
      showToast('success', 'Template deleted successfully')
    } catch (error) {
      console.error('Failed to delete template:', error)
      showToast('error', 'Failed to delete template')
    } finally {
      setIsDeletingTemplate(false)
    }
  }

  // Fetch data
  const fetchData = useCallback(() => {
    getStats('/onboarding/stats')
    getSessions(`/onboarding/sessions?status_filter=${statusFilter}&page=1&limit=50`)
    getTasks('/onboarding/tasks?page=1&limit=50')
    getTemplates('/onboarding/templates?page=1&limit=20')
    getEmployees('/employees?page=1&limit=100')
  }, [getStats, getSessions, getTasks, getTemplates, getEmployees, statusFilter])

  useEffect(() => {
    fetchData()
  }, [fetchData])

  // Sync API data to local state
  useEffect(() => {
    if (sessionsData?.data) {
      setLocalSessions(sessionsData.data)
    }
  }, [sessionsData])

  useEffect(() => {
    if (templatesData?.data) {
      setLocalTemplates(templatesData.data)
    }
  }, [templatesData])

  // Stats
  const stats = statsData || {
    total: 0,
    pending: 0,
    in_progress: 0,
    completed: 0,
    blocked: 0,
    overdue_tasks: 0
  }

  const sessions = localSessions.length > 0 ? localSessions : (sessionsData?.data || [])
  const tasks = tasksData?.data || []
  const templates = localTemplates.length > 0 ? localTemplates : (templatesData?.data || [])
  const employees = employeesData?.data || []

  const filteredSessions = sessions.filter(session => {
    if (!searchQuery) return true
    const employee = session.employee
    if (!employee) return false
    return (
      employee.full_name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      employee.employee_code?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      employee.department?.toLowerCase().includes(searchQuery.toLowerCase())
    )
  })

  const handleCreateOnboarding = async () => {
    if (!newOnboardingForm.employee_id || !newOnboardingForm.joining_date) {
      showToast('error', 'Please select an employee and joining date')
      return
    }

    const result = await createSession('/onboarding/sessions', {
      employee_id: newOnboardingForm.employee_id,
      joining_date: newOnboardingForm.joining_date,
      reporting_manager_id: newOnboardingForm.reporting_manager_id || undefined,
      mentor_id: newOnboardingForm.mentor_id || undefined,
      template_id: newOnboardingForm.template_id || undefined,
      notes: newOnboardingForm.notes || undefined
    })

    if (result) {
      showToast('success', 'Onboarding started successfully')
      setIsNewOnboardingOpen(false)
      setNewOnboardingForm({
        employee_id: '',
        joining_date: '',
        reporting_manager_id: '',
        mentor_id: '',
        template_id: '',
        notes: ''
      })
      fetchData()
    }
  }

  const handleCompleteTask = async (taskId: string) => {
    const result = await completeTask(`/onboarding/tasks/${taskId}/complete`, {})
    if (result) {
      showToast('success', 'Task completed')
      fetchData()
    }
  }

  // State for task editing
  const [editTaskDialogOpen, setEditTaskDialogOpen] = useState(false)
  const [taskToEdit, setTaskToEdit] = useState<OnboardingTask | null>(null)

  const handleEditTask = (task: OnboardingTask) => {
    setTaskToEdit(task)
    setEditTaskDialogOpen(true)
  }

  const handleUpdateTask = async () => {
    if (!taskToEdit) return
    try {
      await completeTask(`/onboarding/tasks/${taskToEdit.id}`, {
        method: 'PUT',
        body: JSON.stringify({
          title: taskToEdit.title,
          description: taskToEdit.description,
          due_date: taskToEdit.due_date,
          priority: taskToEdit.priority,
          notes: taskToEdit.notes
        })
      })
      showToast('success', 'Task updated')
      setEditTaskDialogOpen(false)
      setTaskToEdit(null)
      fetchData()
    } catch (error) {
      showToast('error', 'Failed to update task')
    }
  }

  // Handle session actions (for MoreVertical menu)
  const [sessionActionsOpen, setSessionActionsOpen] = useState(false)

  const handleViewSessionDetails = () => {
    if (selectedSession) {
      // Scroll to session details or expand the panel
      setSessionActionsOpen(false)
    }
  }

  const handleResendWelcomeEmail = async () => {
    if (!selectedSession) return
    try {
      await completeTask(`/onboarding/sessions/${selectedSession.id}/resend-welcome`, {})
      showToast('success', 'Welcome email sent')
      setSessionActionsOpen(false)
    } catch (error) {
      showToast('error', 'Failed to send welcome email')
    }
  }

  const isLoading = isLoadingStats || isLoadingSessions

  if (isLoading) {
    return (
      <div className="space-y-6">
        <PageHeader
          title="Employee Onboarding"
          description="Manage new hire onboarding process and tasks"
          icon={UserPlus}
        />
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          {[1, 2, 3, 4, 5].map(i => (
            <Card key={i}>
              <CardContent className="pt-6">
                <Skeleton className="h-16 w-full" />
              </CardContent>
            </Card>
          ))}
        </div>
        <Card>
          <CardContent className="pt-6">
            <Skeleton className="h-64 w-full" />
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Employee Onboarding"
        description="Manage new hire onboarding process and tasks"
        icon={UserPlus}
        actions={
          <div className="flex items-center gap-2">
            <Button variant="outline" onClick={fetchData}>
              <RefreshCw className="h-4 w-4 mr-2" />
              Refresh
            </Button>
            <Dialog open={isNewOnboardingOpen} onOpenChange={setIsNewOnboardingOpen}>
              <DialogTrigger asChild>
                <Button>
                  <UserPlus className="h-4 w-4 mr-2" />
                  Start Onboarding
                </Button>
              </DialogTrigger>
              <DialogContent className="sm:max-w-lg">
                <DialogHeader>
                  <DialogTitle>Start New Employee Onboarding</DialogTitle>
                  <DialogDescription>
                    Initiate the onboarding process for a new hire
                  </DialogDescription>
                </DialogHeader>
                <div className="space-y-4 py-4">
                  <div className="space-y-2">
                    <Label>Select Employee *</Label>
                    <Select
                      value={newOnboardingForm.employee_id}
                      onValueChange={(value) => setNewOnboardingForm(prev => ({ ...prev, employee_id: value }))}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Choose employee to onboard" />
                      </SelectTrigger>
                      <SelectContent>
                        {employees.map(emp => (
                          <SelectItem key={emp.id} value={emp.id}>
                            {emp.first_name} {emp.last_name} ({emp.employee_code})
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label>Joining Date *</Label>
                    <Input
                      type="date"
                      value={newOnboardingForm.joining_date}
                      onChange={(e) => setNewOnboardingForm(prev => ({ ...prev, joining_date: e.target.value }))}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Reporting Manager</Label>
                    <Select
                      value={newOnboardingForm.reporting_manager_id}
                      onValueChange={(value) => setNewOnboardingForm(prev => ({ ...prev, reporting_manager_id: value }))}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select manager" />
                      </SelectTrigger>
                      <SelectContent>
                        {employees.map(emp => (
                          <SelectItem key={emp.id} value={emp.id}>
                            {emp.first_name} {emp.last_name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label>Assign Buddy/Mentor</Label>
                    <Select
                      value={newOnboardingForm.mentor_id}
                      onValueChange={(value) => setNewOnboardingForm(prev => ({ ...prev, mentor_id: value }))}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select buddy" />
                      </SelectTrigger>
                      <SelectContent>
                        {employees.map(emp => (
                          <SelectItem key={emp.id} value={emp.id}>
                            {emp.first_name} {emp.last_name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label>Onboarding Template</Label>
                    <Select
                      value={newOnboardingForm.template_id}
                      onValueChange={(value) => setNewOnboardingForm(prev => ({ ...prev, template_id: value }))}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select template (optional)" />
                      </SelectTrigger>
                      <SelectContent>
                        {templates.map(t => (
                          <SelectItem key={t.id} value={t.id}>
                            {t.name} ({t.task_count} tasks, {t.duration_days} days)
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label>Notes</Label>
                    <Textarea
                      placeholder="Any special instructions..."
                      value={newOnboardingForm.notes}
                      onChange={(e) => setNewOnboardingForm(prev => ({ ...prev, notes: e.target.value }))}
                    />
                  </div>
                  <div className="flex justify-end gap-2 pt-4">
                    <Button variant="outline" onClick={() => setIsNewOnboardingOpen(false)}>
                      Cancel
                    </Button>
                    <Button onClick={handleCreateOnboarding} disabled={isCreating}>
                      {isCreating && <Loader2 className="h-4 w-4 mr-2 animate-spin" />}
                      Start Onboarding
                    </Button>
                  </div>
                </div>
              </DialogContent>
            </Dialog>
          </div>
        }
      />

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-100 rounded-lg">
                <Users className="h-5 w-5 text-blue-600" />
              </div>
              <div>
                <p className="text-2xl font-bold">{stats.total}</p>
                <p className="text-sm text-muted-foreground">Total</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-yellow-100 rounded-lg">
                <Clock className="h-5 w-5 text-yellow-600" />
              </div>
              <div>
                <p className="text-2xl font-bold">{stats.pending}</p>
                <p className="text-sm text-muted-foreground">Pending</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-100 rounded-lg">
                <UserCheck className="h-5 w-5 text-blue-600" />
              </div>
              <div>
                <p className="text-2xl font-bold">{stats.in_progress}</p>
                <p className="text-sm text-muted-foreground">In Progress</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-green-100 rounded-lg">
                <CheckCircle2 className="h-5 w-5 text-green-600" />
              </div>
              <div>
                <p className="text-2xl font-bold">{stats.completed}</p>
                <p className="text-sm text-muted-foreground">Completed</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-red-100 rounded-lg">
                <AlertCircle className="h-5 w-5 text-red-600" />
              </div>
              <div>
                <p className="text-2xl font-bold">{stats.blocked}</p>
                <p className="text-sm text-muted-foreground">Blocked</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="employees">
        <div className="flex items-center justify-between">
          <TabsList>
            <TabsTrigger value="employees">New Hires</TabsTrigger>
            <TabsTrigger value="tasks">Tasks ({tasks.length})</TabsTrigger>
            <TabsTrigger value="templates">Templates ({templates.length})</TabsTrigger>
          </TabsList>
          <div className="flex items-center gap-2">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-9 w-64"
              />
            </div>
            <Select value={statusFilter} onValueChange={(value) => { setStatusFilter(value); }}>
              <SelectTrigger className="w-36">
                <Filter className="h-4 w-4 mr-2" />
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="pending">Pending</SelectItem>
                <SelectItem value="in_progress">In Progress</SelectItem>
                <SelectItem value="completed">Completed</SelectItem>
                <SelectItem value="blocked">Blocked</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        {/* New Hires Tab */}
        <TabsContent value="employees" className="mt-4">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Session List */}
            <div className="lg:col-span-2">
              <Card>
                <CardHeader>
                  <CardTitle>Onboarding Queue</CardTitle>
                  <CardDescription>New employees in the onboarding process</CardDescription>
                </CardHeader>
                <CardContent>
                  {filteredSessions.length === 0 ? (
                    <div className="flex flex-col items-center justify-center py-12 text-center">
                      <UserPlus className="h-12 w-12 text-muted-foreground mb-4" />
                      <p className="text-muted-foreground">No onboarding sessions found</p>
                      <Button
                        variant="outline"
                        className="mt-4"
                        onClick={() => setIsNewOnboardingOpen(true)}
                      >
                        Start First Onboarding
                      </Button>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {filteredSessions.map((session) => (
                        <div
                          key={session.id}
                          className={`p-4 border rounded-lg cursor-pointer transition-colors hover:bg-muted/50 ${
                            selectedSession?.id === session.id ? 'border-primary bg-muted/30' : ''
                          }`}
                          onClick={() => setSelectedSession(session)}
                        >
                          <div className="flex items-start gap-4">
                            <Avatar className="h-12 w-12">
                              <AvatarFallback className="bg-primary/10 text-primary">
                                {session.employee?.full_name?.split(' ').map(n => n[0]).join('') || '?'}
                              </AvatarFallback>
                            </Avatar>
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center justify-between">
                                <div>
                                  <h4 className="font-semibold">{session.employee?.full_name || 'Unknown'}</h4>
                                  <p className="text-sm text-muted-foreground">
                                    {session.employee?.position || 'No position'}
                                  </p>
                                </div>
                                <Badge className={statusColors[session.status]}>
                                  {session.status.replace('_', ' ')}
                                </Badge>
                              </div>
                              <div className="flex items-center gap-4 mt-2 text-sm text-muted-foreground">
                                <span className="flex items-center gap-1">
                                  <Building2 className="h-3 w-3" />
                                  {session.employee?.department || 'N/A'}
                                </span>
                                <span className="flex items-center gap-1">
                                  <Calendar className="h-3 w-3" />
                                  Joining: {new Date(session.joining_date).toLocaleDateString('en-IN', { day: 'numeric', month: 'short' })}
                                </span>
                              </div>
                              <div className="mt-3">
                                <div className="flex items-center justify-between text-sm mb-1">
                                  <span>Progress</span>
                                  <span className="font-medium">{session.progress_percent}%</span>
                                </div>
                                <Progress value={session.progress_percent} className="h-2" />
                              </div>
                            </div>
                            <ChevronRight className="h-5 w-5 text-muted-foreground" />
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>

            {/* Session Details */}
            <div>
              {selectedSession ? (
                <Card>
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <CardTitle>Onboarding Details</CardTitle>
                      <Dialog open={sessionActionsOpen} onOpenChange={setSessionActionsOpen}>
                        <DialogTrigger asChild>
                          <Button variant="ghost" size="icon">
                            <MoreVertical className="h-4 w-4" />
                          </Button>
                        </DialogTrigger>
                        <DialogContent className="sm:max-w-sm">
                          <DialogHeader>
                            <DialogTitle>Session Actions</DialogTitle>
                            <DialogDescription>
                              Actions for {selectedSession.employee?.full_name}'s onboarding
                            </DialogDescription>
                          </DialogHeader>
                          <div className="flex flex-col gap-2 py-4">
                            <Button variant="outline" onClick={handleResendWelcomeEmail}>
                              <Mail className="h-4 w-4 mr-2" />
                              Resend Welcome Email
                            </Button>
                            <Button variant="outline" onClick={() => {
                              setSessionActionsOpen(false)
                              // Scroll to tasks section
                            }}>
                              <FileText className="h-4 w-4 mr-2" />
                              View All Tasks
                            </Button>
                            <Button
                              variant="outline"
                              className="text-red-600 hover:text-red-700"
                              onClick={() => {
                                setSessionActionsOpen(false)
                                handleDeleteSessionClick(selectedSession)
                              }}
                            >
                              <Trash2 className="h-4 w-4 mr-2" />
                              Cancel Onboarding
                            </Button>
                          </div>
                        </DialogContent>
                      </Dialog>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    <div className="text-center">
                      <Avatar className="h-20 w-20 mx-auto">
                        <AvatarFallback className="bg-primary/10 text-primary text-xl">
                          {selectedSession.employee?.full_name?.split(' ').map(n => n[0]).join('') || '?'}
                        </AvatarFallback>
                      </Avatar>
                      <h3 className="font-semibold mt-3">{selectedSession.employee?.full_name}</h3>
                      <p className="text-sm text-muted-foreground">{selectedSession.employee?.position}</p>
                      <Badge className={`mt-2 ${statusColors[selectedSession.status]}`}>
                        {selectedSession.status.replace('_', ' ')}
                      </Badge>
                    </div>

                    <div className="space-y-3">
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-muted-foreground">Department</span>
                        <span className="font-medium">{selectedSession.employee?.department || 'N/A'}</span>
                      </div>
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-muted-foreground">Joining Date</span>
                        <span className="font-medium">
                          {new Date(selectedSession.joining_date).toLocaleDateString('en-IN')}
                        </span>
                      </div>
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-muted-foreground">Manager</span>
                        <span className="font-medium">{selectedSession.manager_name || 'Not assigned'}</span>
                      </div>
                      {selectedSession.mentor_name && (
                        <div className="flex items-center justify-between text-sm">
                          <span className="text-muted-foreground">Buddy/Mentor</span>
                          <span className="font-medium">{selectedSession.mentor_name}</span>
                        </div>
                      )}
                    </div>

                    <div className="space-y-3">
                      <h4 className="font-medium">Progress Overview</h4>
                      <div className="space-y-2">
                        <div className="flex items-center justify-between text-sm">
                          <span className="flex items-center gap-2">
                            <CheckCircle2 className="h-4 w-4 text-green-600" />
                            Tasks
                          </span>
                          <span>{selectedSession.tasks_completed}/{selectedSession.tasks_total}</span>
                        </div>
                        <Progress
                          value={selectedSession.tasks_total > 0 ? (selectedSession.tasks_completed / selectedSession.tasks_total) * 100 : 0}
                          className="h-2"
                        />
                      </div>
                      <div className="space-y-2">
                        <div className="flex items-center justify-between text-sm">
                          <span className="flex items-center gap-2">
                            <FileText className="h-4 w-4 text-blue-600" />
                            Documents
                          </span>
                          <span>{selectedSession.documents_collected}/{selectedSession.documents_total}</span>
                        </div>
                        <Progress
                          value={selectedSession.documents_total > 0 ? (selectedSession.documents_collected / selectedSession.documents_total) * 100 : 0}
                          className="h-2"
                        />
                      </div>
                    </div>

                    <div className="flex gap-2">
                      <Button
                        className="flex-1"
                        size="sm"
                        onClick={() => {
                          // Navigate to session details or expand details panel
                          const detailsSection = document.getElementById('session-details')
                          detailsSection?.scrollIntoView({ behavior: 'smooth' })
                        }}
                      >
                        <Eye className="h-4 w-4 mr-2" />
                        View Details
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={handleResendWelcomeEmail}
                        title="Resend welcome email"
                      >
                        <Send className="h-4 w-4" />
                      </Button>
                      {selectedSession.status === 'blocked' && (
                        <Button
                          variant="outline"
                          size="sm"
                          className="text-red-600 hover:text-red-700 hover:bg-red-50"
                          onClick={() => handleDeleteSessionClick(selectedSession)}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      )}
                    </div>
                  </CardContent>
                </Card>
              ) : (
                <Card>
                  <CardContent className="pt-6">
                    <div className="text-center py-8">
                      <UserPlus className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                      <p className="text-muted-foreground">Select an employee to view details</p>
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>
          </div>
        </TabsContent>

        {/* Tasks Tab */}
        <TabsContent value="tasks" className="mt-4">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Onboarding Tasks</CardTitle>
                  <CardDescription>Track and manage onboarding tasks across all new hires</CardDescription>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              {tasks.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-12 text-center">
                  <CheckCircle2 className="h-12 w-12 text-muted-foreground mb-4" />
                  <p className="text-muted-foreground">No onboarding tasks found</p>
                </div>
              ) : (
                <div className="border rounded-lg overflow-hidden">
                  <table className="w-full">
                    <thead className="bg-muted/50">
                      <tr>
                        <th className="text-left p-4 font-medium">Task</th>
                        <th className="text-left p-4 font-medium">Category</th>
                        <th className="text-left p-4 font-medium">Assigned To</th>
                        <th className="text-left p-4 font-medium">Due Date</th>
                        <th className="text-center p-4 font-medium">Priority</th>
                        <th className="text-center p-4 font-medium">Status</th>
                        <th className="text-right p-4 font-medium">Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {tasks.map((task) => (
                        <tr key={task.id} className="border-t hover:bg-muted/30">
                          <td className="p-4 font-medium">{task.title}</td>
                          <td className="p-4 text-muted-foreground">
                            {categoryLabels[task.category] || task.category}
                          </td>
                          <td className="p-4">{task.assigned_role || '-'}</td>
                          <td className="p-4 text-muted-foreground">
                            {task.due_date
                              ? new Date(task.due_date).toLocaleDateString('en-IN', { day: 'numeric', month: 'short' })
                              : '-'}
                          </td>
                          <td className="p-4 text-center">
                            <Badge className={priorityColors[task.priority]}>{task.priority}</Badge>
                          </td>
                          <td className="p-4 text-center">
                            <Badge className={statusColors[task.status]}>
                              {task.status.replace('_', ' ')}
                            </Badge>
                          </td>
                          <td className="p-4 text-right">
                            <div className="flex items-center justify-end gap-1">
                              <Button
                                variant="ghost"
                                size="icon"
                                onClick={() => handleEditTask(task)}
                                title="Edit task"
                              >
                                <Edit className="h-4 w-4" />
                              </Button>
                              {task.status !== 'completed' && (
                                <Button
                                  variant="ghost"
                                  size="icon"
                                  onClick={() => handleCompleteTask(task.id)}
                                >
                                  <CheckCircle2 className="h-4 w-4" />
                                </Button>
                              )}
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Templates Tab */}
        <TabsContent value="templates" className="mt-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {templates.map((template) => (
              <Card key={template.id} className="hover:shadow-md transition-shadow cursor-pointer">
                <CardContent className="pt-6">
                  <div className="flex items-start gap-4">
                    <div className="p-3 bg-primary/10 rounded-lg">
                      <Users className="h-6 w-6 text-primary" />
                    </div>
                    <div className="flex-1">
                      <h3 className="font-semibold">{template.name}</h3>
                      <p className="text-sm text-muted-foreground mt-1">
                        {template.description || 'No description'}
                      </p>
                      <div className="flex items-center gap-3 mt-2 text-sm text-muted-foreground">
                        <span>{template.task_count} tasks</span>
                        <span>{template.duration_days} days</span>
                      </div>
                    </div>
                  </div>
                  <div className="flex gap-2 mt-4">
                    <Button
                      variant="outline"
                      size="sm"
                      className="flex-1"
                      onClick={() => handleViewTemplate(template)}
                    >
                      <Eye className="h-4 w-4 mr-2" />
                      View
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      className="flex-1"
                      onClick={() => handleEditTemplate(template)}
                    >
                      <Edit className="h-4 w-4 mr-2" />
                      Edit
                    </Button>
                    {!template.is_active && (
                      <Button
                        variant="outline"
                        size="sm"
                        className="text-red-600 hover:text-red-700 hover:bg-red-50"
                        onClick={() => handleDeleteTemplateClick(template)}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
            {templates.length === 0 && (
              <Card className="col-span-full">
                <CardContent className="pt-6">
                  <div className="flex flex-col items-center justify-center py-12 text-center">
                    <GraduationCap className="h-12 w-12 text-muted-foreground mb-4" />
                    <p className="text-muted-foreground">No templates found</p>
                    <p className="text-sm text-muted-foreground mt-1">
                      Create your first onboarding template to streamline the process
                    </p>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </TabsContent>
      </Tabs>

      {/* Delete Session Confirmation Dialog */}
      <AlertDialog open={deleteSessionDialogOpen} onOpenChange={setDeleteSessionDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-red-500" />
              Delete Onboarding Session
            </AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete the onboarding session for <strong>{sessionToDelete?.employee?.full_name}</strong>?
              This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={isDeletingSession}>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDeleteSessionConfirm}
              disabled={isDeletingSession}
              className="bg-red-600 hover:bg-red-700 focus:ring-red-600"
            >
              {isDeletingSession ? (
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

      {/* Delete Template Confirmation Dialog */}
      <AlertDialog open={deleteTemplateDialogOpen} onOpenChange={setDeleteTemplateDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-red-500" />
              Delete Template
            </AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete the template <strong>{templateToDelete?.name}</strong>?
              This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={isDeletingTemplate}>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDeleteTemplateConfirm}
              disabled={isDeletingTemplate}
              className="bg-red-600 hover:bg-red-700 focus:ring-red-600"
            >
              {isDeletingTemplate ? (
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

      {/* View Template Dialog */}
      <Dialog open={isViewTemplateOpen} onOpenChange={setIsViewTemplateOpen}>
        <DialogContent className="sm:max-w-lg">
          <DialogHeader>
            <DialogTitle>{selectedTemplate?.name}</DialogTitle>
            <DialogDescription>
              {selectedTemplate?.description || 'No description provided'}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <p className="text-muted-foreground">Total Tasks</p>
                <p className="font-medium">{selectedTemplate?.task_count || 0}</p>
              </div>
              <div>
                <p className="text-muted-foreground">Duration</p>
                <p className="font-medium">{selectedTemplate?.duration_days || 0} days</p>
              </div>
              <div>
                <p className="text-muted-foreground">Status</p>
                <Badge className={selectedTemplate?.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}>
                  {selectedTemplate?.is_active ? 'Active' : 'Inactive'}
                </Badge>
              </div>
              <div>
                <p className="text-muted-foreground">Department</p>
                <p className="font-medium">{selectedTemplate?.department || 'All departments'}</p>
              </div>
            </div>
          </div>
          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={() => setIsViewTemplateOpen(false)}>
              Close
            </Button>
            <Button onClick={() => {
              setIsViewTemplateOpen(false)
              if (selectedTemplate) handleEditTemplate(selectedTemplate)
            }}>
              <Edit className="h-4 w-4 mr-2" />
              Edit Template
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      {/* Edit Template Dialog */}
      <Dialog open={isEditTemplateOpen} onOpenChange={setIsEditTemplateOpen}>
        <DialogContent className="sm:max-w-lg">
          <DialogHeader>
            <DialogTitle>Edit Template</DialogTitle>
            <DialogDescription>
              Modify the onboarding template settings
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="template-name">Template Name</Label>
              <Input
                id="template-name"
                defaultValue={selectedTemplate?.name}
                placeholder="Enter template name"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="template-description">Description</Label>
              <Textarea
                id="template-description"
                defaultValue={selectedTemplate?.description}
                placeholder="Enter description"
                rows={3}
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="template-duration">Duration (days)</Label>
                <Input
                  id="template-duration"
                  type="number"
                  defaultValue={selectedTemplate?.duration_days}
                  placeholder="30"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="template-department">Department</Label>
                <Input
                  id="template-department"
                  defaultValue={selectedTemplate?.department}
                  placeholder="All departments"
                />
              </div>
            </div>
          </div>
          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={() => setIsEditTemplateOpen(false)}>
              Cancel
            </Button>
            <Button onClick={() => {
              showToast('success', 'Template updated successfully')
              setIsEditTemplateOpen(false)
            }}>
              Save Changes
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  )
}
