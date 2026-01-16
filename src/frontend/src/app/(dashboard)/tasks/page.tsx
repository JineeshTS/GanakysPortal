'use client'

import { useState, useEffect } from 'react'
import { useApi } from '@/hooks'
import { PageHeader } from '@/components/layout/page-header'
import { Card, CardContent, CardHeader } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
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
import { formatDate } from '@/lib/format'
import type { Task } from '@/types'
import {
  Plus,
  Search,
  Calendar,
  Clock,
  User,
  Flag,
  MoreHorizontal,
  CheckCircle2,
  Circle,
  Timer,
  Eye,
  MessageSquare,
  Paperclip,
  ChevronDown,
  Filter,
  LayoutGrid,
  List,
  FolderKanban,
  Loader2,
  AlertCircle,
  Trash2,
  AlertTriangle,
} from 'lucide-react'

// Task status columns for kanban
type TaskStatus = 'todo' | 'in_progress' | 'review' | 'done'
type TaskPriority = 'low' | 'medium' | 'high' | 'urgent'

const taskColumns: { id: TaskStatus; label: string; color: string }[] = [
  { id: 'todo', label: 'To Do', color: 'bg-slate-100 border-slate-300' },
  { id: 'in_progress', label: 'In Progress', color: 'bg-blue-50 border-blue-300' },
  { id: 'review', label: 'In Review', color: 'bg-purple-50 border-purple-300' },
  { id: 'done', label: 'Done', color: 'bg-green-50 border-green-300' },
]

// Priority config
const priorityConfig: Record<TaskPriority, { color: string; icon: React.ReactNode; label: string }> = {
  low: { color: 'text-slate-500', icon: <Flag className="h-3 w-3" />, label: 'Low' },
  medium: { color: 'text-blue-500', icon: <Flag className="h-3 w-3" />, label: 'Medium' },
  high: { color: 'text-orange-500', icon: <Flag className="h-3 w-3 fill-current" />, label: 'High' },
  urgent: { color: 'text-red-500', icon: <Flag className="h-3 w-3 fill-current" />, label: 'Urgent' },
}

// Extended task interface
interface TaskItem extends Omit<Task, 'priority' | 'status'> {
  priority: TaskPriority
  status: TaskStatus
  project_name?: string
  assignee_name?: string
  assignee_avatar?: string
  comments_count?: number
  attachments_count?: number
  labels?: string[]
}

// API Response interfaces
interface TasksListResponse {
  tasks: TaskItem[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

interface TasksSummary {
  total: number
  by_status: {
    todo: number
    in_progress: number
    review: number
    done: number
  }
  by_priority: {
    low: number
    medium: number
    high: number
    urgent: number
  }
  overdue: number
  due_this_week: number
}

// Mock tasks data
const mockTasks: TaskItem[] = [
  {
    id: '1',
    project_id: 'prj-1',
    project_name: 'E-Commerce Platform',
    title: 'Design homepage wireframes',
    description: 'Create wireframes for the new homepage layout with mobile responsiveness',
    assigned_to: 'user-1',
    assignee_name: 'Arun Sharma',
    assignee_avatar: '',
    priority: 'high',
    status: 'done',
    due_date: '2026-01-03',
    estimated_hours: 8,
    actual_hours: 6,
    comments_count: 5,
    attachments_count: 3,
    labels: ['design', 'ui/ux'],
    created_at: '2025-12-28',
    updated_at: '2026-01-03',
  },
  {
    id: '2',
    project_id: 'prj-1',
    project_name: 'E-Commerce Platform',
    title: 'Implement user authentication',
    description: 'JWT-based authentication with refresh tokens and OAuth support',
    assigned_to: 'user-2',
    assignee_name: 'Neha Gupta',
    priority: 'urgent',
    status: 'in_progress',
    due_date: '2026-01-08',
    estimated_hours: 16,
    actual_hours: 10,
    comments_count: 8,
    labels: ['backend', 'security'],
    created_at: '2026-01-02',
    updated_at: '2026-01-06',
  },
  {
    id: '3',
    project_id: 'prj-1',
    project_name: 'E-Commerce Platform',
    title: 'Setup CI/CD pipeline',
    description: 'Configure GitHub Actions for automated testing and deployment',
    assigned_to: 'user-3',
    assignee_name: 'Kiran Patel',
    priority: 'medium',
    status: 'review',
    due_date: '2026-01-10',
    estimated_hours: 12,
    actual_hours: 11,
    comments_count: 3,
    labels: ['devops'],
    created_at: '2026-01-04',
    updated_at: '2026-01-06',
  },
  {
    id: '4',
    project_id: 'prj-1',
    project_name: 'E-Commerce Platform',
    title: 'Product catalog API',
    description: 'RESTful API endpoints for product CRUD operations with search',
    assigned_to: 'user-2',
    assignee_name: 'Neha Gupta',
    priority: 'high',
    status: 'todo',
    due_date: '2026-01-12',
    estimated_hours: 20,
    labels: ['backend', 'api'],
    created_at: '2026-01-05',
    updated_at: '2026-01-05',
  },
  {
    id: '5',
    project_id: 'prj-2',
    project_name: 'Mobile App',
    title: 'Design app navigation',
    description: 'Bottom navigation and drawer menu for main app screens',
    assigned_to: 'user-1',
    assignee_name: 'Arun Sharma',
    priority: 'medium',
    status: 'in_progress',
    due_date: '2026-01-09',
    estimated_hours: 6,
    actual_hours: 3,
    comments_count: 2,
    labels: ['mobile', 'design'],
    created_at: '2026-01-04',
    updated_at: '2026-01-06',
  },
  {
    id: '6',
    project_id: 'prj-1',
    project_name: 'E-Commerce Platform',
    title: 'Shopping cart functionality',
    description: 'Add to cart, update quantity, remove items, persist cart state',
    assigned_to: 'user-4',
    assignee_name: 'Priya Singh',
    priority: 'high',
    status: 'todo',
    due_date: '2026-01-15',
    estimated_hours: 24,
    labels: ['frontend', 'feature'],
    created_at: '2026-01-05',
    updated_at: '2026-01-05',
  },
  {
    id: '7',
    project_id: 'prj-2',
    project_name: 'Mobile App',
    title: 'Push notifications setup',
    description: 'Configure Firebase Cloud Messaging for iOS and Android',
    priority: 'low',
    status: 'todo',
    due_date: '2026-01-20',
    estimated_hours: 8,
    labels: ['mobile', 'infrastructure'],
    created_at: '2026-01-06',
    updated_at: '2026-01-06',
  },
  {
    id: '8',
    project_id: 'prj-1',
    project_name: 'E-Commerce Platform',
    title: 'Payment gateway integration',
    description: 'Integrate Razorpay for payments with webhook handling',
    assigned_to: 'user-2',
    assignee_name: 'Neha Gupta',
    priority: 'urgent',
    status: 'todo',
    due_date: '2026-01-18',
    estimated_hours: 20,
    labels: ['backend', 'payments'],
    created_at: '2026-01-05',
    updated_at: '2026-01-05',
  },
  {
    id: '9',
    project_id: 'prj-1',
    project_name: 'E-Commerce Platform',
    title: 'Unit tests for auth module',
    description: 'Write comprehensive unit tests for authentication services',
    assigned_to: 'user-2',
    assignee_name: 'Neha Gupta',
    priority: 'medium',
    status: 'review',
    due_date: '2026-01-07',
    estimated_hours: 8,
    actual_hours: 7,
    comments_count: 4,
    labels: ['testing'],
    created_at: '2026-01-03',
    updated_at: '2026-01-06',
  },
  {
    id: '10',
    project_id: 'prj-1',
    project_name: 'E-Commerce Platform',
    title: 'Database schema design',
    description: 'PostgreSQL schema for products, orders, users with proper indexes',
    assigned_to: 'user-3',
    assignee_name: 'Kiran Patel',
    priority: 'high',
    status: 'done',
    due_date: '2025-12-30',
    estimated_hours: 12,
    actual_hours: 10,
    comments_count: 6,
    attachments_count: 2,
    labels: ['database', 'design'],
    created_at: '2025-12-25',
    updated_at: '2025-12-30',
  },
]

// Label colors
const labelColors: Record<string, string> = {
  design: 'bg-pink-100 text-pink-700',
  'ui/ux': 'bg-purple-100 text-purple-700',
  backend: 'bg-blue-100 text-blue-700',
  frontend: 'bg-cyan-100 text-cyan-700',
  security: 'bg-red-100 text-red-700',
  devops: 'bg-orange-100 text-orange-700',
  api: 'bg-indigo-100 text-indigo-700',
  mobile: 'bg-green-100 text-green-700',
  feature: 'bg-yellow-100 text-yellow-700',
  testing: 'bg-teal-100 text-teal-700',
  database: 'bg-slate-100 text-slate-700',
  payments: 'bg-emerald-100 text-emerald-700',
  infrastructure: 'bg-gray-100 text-gray-700',
}

// Task Card Component
function TaskCard({ task, onClick }: { task: TaskItem; onClick: () => void }) {
  const priority = priorityConfig[task.priority]
  const isOverdue = task.due_date && new Date(task.due_date) < new Date() && task.status !== 'done'

  return (
    <Card
      className="cursor-pointer hover:shadow-md transition-all group bg-white"
      onClick={onClick}
    >
      <CardContent className="p-3">
        {/* Labels */}
        {task.labels && task.labels.length > 0 && (
          <div className="flex flex-wrap gap-1 mb-2">
            {task.labels.slice(0, 3).map((label) => (
              <Badge
                key={label}
                variant="secondary"
                className={`text-[10px] px-1.5 py-0 ${labelColors[label] || 'bg-gray-100 text-gray-700'}`}
              >
                {label}
              </Badge>
            ))}
            {task.labels.length > 3 && (
              <Badge variant="outline" className="text-[10px] px-1.5 py-0">
                +{task.labels.length - 3}
              </Badge>
            )}
          </div>
        )}

        {/* Title */}
        <p className="font-medium text-sm line-clamp-2 mb-2">{task.title}</p>

        {/* Project */}
        {task.project_name && (
          <p className="text-xs text-muted-foreground mb-2 truncate">
            <FolderKanban className="h-3 w-3 inline mr-1" />
            {task.project_name}
          </p>
        )}

        {/* Footer */}
        <div className="flex items-center justify-between pt-2 border-t">
          <div className="flex items-center gap-2">
            {/* Priority */}
            <span className={priority.color} title={`${priority.label} priority`}>
              {priority.icon}
            </span>

            {/* Due date */}
            {task.due_date && (
              <span
                className={`flex items-center gap-1 text-xs ${
                  isOverdue ? 'text-red-600' : 'text-muted-foreground'
                }`}
              >
                <Calendar className="h-3 w-3" />
                {formatDate(task.due_date)}
              </span>
            )}
          </div>

          <div className="flex items-center gap-2">
            {/* Comments */}
            {task.comments_count && task.comments_count > 0 && (
              <span className="flex items-center gap-0.5 text-xs text-muted-foreground">
                <MessageSquare className="h-3 w-3" />
                {task.comments_count}
              </span>
            )}

            {/* Attachments */}
            {task.attachments_count && task.attachments_count > 0 && (
              <span className="flex items-center gap-0.5 text-xs text-muted-foreground">
                <Paperclip className="h-3 w-3" />
                {task.attachments_count}
              </span>
            )}

            {/* Assignee */}
            {task.assignee_name && (
              <Avatar className="h-6 w-6">
                <AvatarImage src={task.assignee_avatar} />
                <AvatarFallback className="text-[10px]">
                  {task.assignee_name.split(' ').map((n) => n[0]).join('')}
                </AvatarFallback>
              </Avatar>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

// Kanban Column Component
function KanbanColumn({
  column,
  tasks,
  onTaskClick,
}: {
  column: typeof taskColumns[0]
  tasks: TaskItem[]
  onTaskClick: (task: TaskItem) => void
}) {
  const columnTasks = tasks.filter((t) => t.status === column.id)

  return (
    <div className={`flex-shrink-0 w-80 rounded-lg border ${column.color}`}>
      <div className="p-3 border-b bg-white/50 rounded-t-lg">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            {column.id === 'todo' && <Circle className="h-4 w-4 text-slate-500" />}
            {column.id === 'in_progress' && <Timer className="h-4 w-4 text-blue-500" />}
            {column.id === 'review' && <Eye className="h-4 w-4 text-purple-500" />}
            {column.id === 'done' && <CheckCircle2 className="h-4 w-4 text-green-500" />}
            <h3 className="font-medium text-sm">{column.label}</h3>
          </div>
          <Badge variant="secondary" className="text-xs">
            {columnTasks.length}
          </Badge>
        </div>
      </div>
      <div className="p-2 space-y-2 max-h-[calc(100vh-320px)] overflow-y-auto">
        {columnTasks.map((task) => (
          <TaskCard key={task.id} task={task} onClick={() => onTaskClick(task)} />
        ))}
        {columnTasks.length === 0 && (
          <div className="text-center py-8 text-xs text-muted-foreground">
            No tasks
          </div>
        )}
        <Button variant="ghost" className="w-full h-8 text-xs text-muted-foreground border-dashed border">
          <Plus className="h-3 w-3 mr-1" />
          Add Task
        </Button>
      </div>
    </div>
  )
}

// Task Detail Dialog
function TaskDetailDialog({
  task,
  open,
  onOpenChange,
}: {
  task: TaskItem | null
  open: boolean
  onOpenChange: (open: boolean) => void
}) {
  if (!task) return null

  const priority = priorityConfig[task.priority]
  const isOverdue = task.due_date && new Date(task.due_date) < new Date() && task.status !== 'done'

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[600px]">
        <DialogHeader>
          <div className="flex items-start gap-3">
            {task.status === 'done' ? (
              <CheckCircle2 className="h-6 w-6 text-green-500 mt-0.5" />
            ) : (
              <Circle className="h-6 w-6 text-muted-foreground mt-0.5" />
            )}
            <div className="flex-1">
              <DialogTitle className="text-lg">{task.title}</DialogTitle>
              {task.project_name && (
                <DialogDescription className="flex items-center gap-1 mt-1">
                  <FolderKanban className="h-4 w-4" />
                  {task.project_name}
                </DialogDescription>
              )}
            </div>
          </div>
        </DialogHeader>

        <div className="space-y-4 py-4">
          {/* Labels */}
          {task.labels && task.labels.length > 0 && (
            <div className="flex flex-wrap gap-1.5">
              {task.labels.map((label) => (
                <Badge
                  key={label}
                  variant="secondary"
                  className={`text-xs ${labelColors[label] || 'bg-gray-100 text-gray-700'}`}
                >
                  {label}
                </Badge>
              ))}
            </div>
          )}

          {/* Description */}
          {task.description && (
            <div>
              <Label className="text-xs text-muted-foreground">Description</Label>
              <p className="text-sm mt-1">{task.description}</p>
            </div>
          )}

          {/* Meta info grid */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label className="text-xs text-muted-foreground">Status</Label>
              <Select defaultValue={task.status}>
                <SelectTrigger className="mt-1">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {taskColumns.map((col) => (
                    <SelectItem key={col.id} value={col.id}>
                      {col.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label className="text-xs text-muted-foreground">Priority</Label>
              <Select defaultValue={task.priority}>
                <SelectTrigger className="mt-1">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="low">Low</SelectItem>
                  <SelectItem value="medium">Medium</SelectItem>
                  <SelectItem value="high">High</SelectItem>
                  <SelectItem value="urgent">Urgent</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label className="text-xs text-muted-foreground">Assignee</Label>
              <div className="flex items-center gap-2 mt-1 p-2 border rounded-md">
                {task.assignee_name ? (
                  <>
                    <Avatar className="h-6 w-6">
                      <AvatarFallback className="text-xs">
                        {task.assignee_name.split(' ').map((n) => n[0]).join('')}
                      </AvatarFallback>
                    </Avatar>
                    <span className="text-sm">{task.assignee_name}</span>
                  </>
                ) : (
                  <span className="text-sm text-muted-foreground">Unassigned</span>
                )}
              </div>
            </div>
            <div>
              <Label className="text-xs text-muted-foreground">Due Date</Label>
              <div className={`flex items-center gap-2 mt-1 p-2 border rounded-md ${isOverdue ? 'border-red-300 bg-red-50' : ''}`}>
                <Calendar className={`h-4 w-4 ${isOverdue ? 'text-red-500' : 'text-muted-foreground'}`} />
                <span className={`text-sm ${isOverdue ? 'text-red-600 font-medium' : ''}`}>
                  {task.due_date ? formatDate(task.due_date) : 'No due date'}
                </span>
              </div>
            </div>
          </div>

          {/* Time tracking */}
          {(task.estimated_hours || task.actual_hours) && (
            <div>
              <Label className="text-xs text-muted-foreground">Time Tracking</Label>
              <div className="flex items-center gap-4 mt-1">
                <div className="flex items-center gap-2 text-sm">
                  <Clock className="h-4 w-4 text-muted-foreground" />
                  <span>Estimated: {task.estimated_hours || 0}h</span>
                </div>
                {task.actual_hours !== undefined && (
                  <div className="flex items-center gap-2 text-sm">
                    <Timer className="h-4 w-4 text-muted-foreground" />
                    <span>Logged: {task.actual_hours}h</span>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        <DialogFooter className="gap-2">
          <Button variant="outline" size="sm">
            <MessageSquare className="h-4 w-4 mr-2" />
            Comments ({task.comments_count || 0})
          </Button>
          <Button variant="outline" size="sm">
            <Paperclip className="h-4 w-4 mr-2" />
            Files ({task.attachments_count || 0})
          </Button>
          <Button size="sm">Save Changes</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

// Add Task Dialog
function AddTaskDialog({ open, onOpenChange }: { open: boolean; onOpenChange: (open: boolean) => void }) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>Create New Task</DialogTitle>
          <DialogDescription>
            Add a new task to the board
          </DialogDescription>
        </DialogHeader>
        <div className="grid gap-4 py-4">
          <div className="space-y-2">
            <Label htmlFor="title">Task Title *</Label>
            <Input id="title" placeholder="Enter task title..." />
          </div>
          <div className="space-y-2">
            <Label htmlFor="description">Description</Label>
            <Input id="description" placeholder="Task description..." />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label>Project</Label>
              <Select>
                <SelectTrigger>
                  <SelectValue placeholder="Select project" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="prj-1">E-Commerce Platform</SelectItem>
                  <SelectItem value="prj-2">Mobile App</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label>Assignee</Label>
              <Select>
                <SelectTrigger>
                  <SelectValue placeholder="Select assignee" />
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
              <Label>Priority</Label>
              <Select defaultValue="medium">
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="low">Low</SelectItem>
                  <SelectItem value="medium">Medium</SelectItem>
                  <SelectItem value="high">High</SelectItem>
                  <SelectItem value="urgent">Urgent</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label>Due Date</Label>
              <Input type="date" />
            </div>
            <div className="space-y-2">
              <Label>Estimate (hrs)</Label>
              <Input type="number" placeholder="8" />
            </div>
          </div>
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button onClick={() => onOpenChange(false)}>Create Task</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

export default function TasksPage() {
  const [searchQuery, setSearchQuery] = useState('')
  const [projectFilter, setProjectFilter] = useState<string>('all')
  const [priorityFilter, setPriorityFilter] = useState<string>('all')
  const [viewMode, setViewMode] = useState<'board' | 'list'>('board')
  const [addDialogOpen, setAddDialogOpen] = useState(false)
  const [selectedTask, setSelectedTask] = useState<TaskItem | null>(null)
  const [detailDialogOpen, setDetailDialogOpen] = useState(false)
  const [localTasks, setLocalTasks] = useState<TaskItem[]>(mockTasks)

  // Delete state
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false)
  const [taskToDelete, setTaskToDelete] = useState<TaskItem | null>(null)
  const [isDeleting, setIsDeleting] = useState(false)
  const deleteApi = useApi()

  const handleDeleteClick = (task: TaskItem, e: React.MouseEvent) => {
    e.stopPropagation()
    setTaskToDelete(task)
    setDeleteDialogOpen(true)
  }

  const handleDeleteConfirm = async () => {
    if (!taskToDelete) return
    setIsDeleting(true)
    try {
      await deleteApi.delete(`/tasks/${taskToDelete.id}`)
      setLocalTasks(localTasks.filter(t => t.id !== taskToDelete.id))
      setDeleteDialogOpen(false)
      setTaskToDelete(null)
    } catch (error) {
      console.error('Failed to delete task:', error)
    } finally {
      setIsDeleting(false)
    }
  }

  const { data: tasksData, isLoading: tasksLoading, error: tasksError, get: getTasks } = useApi<TasksListResponse>()
  const { data: summaryData, isLoading: summaryLoading, get: getSummary } = useApi<TasksSummary>()

  // Fetch tasks on mount and when filters change
  useEffect(() => {
    const params = new URLSearchParams()
    if (searchQuery) params.set('search', searchQuery)
    if (projectFilter !== 'all') params.set('project_id', projectFilter)
    if (priorityFilter !== 'all') params.set('priority', priorityFilter)

    getTasks(`/tasks?${params.toString()}`)
    getSummary('/tasks/summary')
  }, [searchQuery, projectFilter, priorityFilter, getTasks, getSummary])

  // Sync API data to local state
  useEffect(() => {
    if (tasksData?.tasks) {
      setLocalTasks(tasksData.tasks)
    }
  }, [tasksData])

  const tasks = localTasks
  const isLoading = tasksLoading || summaryLoading

  const filteredTasks = tasks.filter((task) => {
    const matchesSearch = !searchQuery ||
      task.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      task.description?.toLowerCase().includes(searchQuery.toLowerCase())

    const matchesProject = projectFilter === 'all' || task.project_id === projectFilter
    const matchesPriority = priorityFilter === 'all' || task.priority === priorityFilter

    return matchesSearch && matchesProject && matchesPriority
  })

  const handleTaskClick = (task: TaskItem) => {
    setSelectedTask(task)
    setDetailDialogOpen(true)
  }

  // Stats - use API data if available with fallback to computed mock data
  const stats = {
    total: summaryData?.total ?? tasks.length,
    todo: summaryData?.by_status?.todo ?? tasks.filter((t) => t.status === 'todo').length,
    inProgress: summaryData?.by_status?.in_progress ?? tasks.filter((t) => t.status === 'in_progress').length,
    review: summaryData?.by_status?.review ?? tasks.filter((t) => t.status === 'review').length,
    done: summaryData?.by_status?.done ?? tasks.filter((t) => t.status === 'done').length,
    overdue: summaryData?.overdue ?? tasks.filter((t) => t.due_date && new Date(t.due_date) < new Date() && t.status !== 'done').length,
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Task Board"
        description={`${stats.total} tasks | ${stats.inProgress} in progress | ${stats.overdue} overdue`}
        actions={
          <div className="flex gap-2">
            <div className="relative">
              <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search tasks..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-8 w-56"
              />
            </div>
            <Select value={projectFilter} onValueChange={setProjectFilter}>
              <SelectTrigger className="w-[160px]">
                <SelectValue placeholder="Project" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Projects</SelectItem>
                <SelectItem value="prj-1">E-Commerce Platform</SelectItem>
                <SelectItem value="prj-2">Mobile App</SelectItem>
              </SelectContent>
            </Select>
            <Select value={priorityFilter} onValueChange={setPriorityFilter}>
              <SelectTrigger className="w-[120px]">
                <SelectValue placeholder="Priority" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Priority</SelectItem>
                <SelectItem value="urgent">Urgent</SelectItem>
                <SelectItem value="high">High</SelectItem>
                <SelectItem value="medium">Medium</SelectItem>
                <SelectItem value="low">Low</SelectItem>
              </SelectContent>
            </Select>
            <div className="flex border rounded-md">
              <Button
                variant={viewMode === 'board' ? 'secondary' : 'ghost'}
                size="sm"
                className="rounded-r-none"
                onClick={() => setViewMode('board')}
              >
                <LayoutGrid className="h-4 w-4" />
              </Button>
              <Button
                variant={viewMode === 'list' ? 'secondary' : 'ghost'}
                size="sm"
                className="rounded-l-none"
                onClick={() => setViewMode('list')}
              >
                <List className="h-4 w-4" />
              </Button>
            </div>
            <Button onClick={() => setAddDialogOpen(true)}>
              <Plus className="h-4 w-4 mr-2" />
              Add Task
            </Button>
          </div>
        }
      />

      {/* Loading State */}
      {isLoading && (
        <Card className="p-8 flex items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <span className="ml-2">Loading tasks...</span>
        </Card>
      )}

      {/* Error State */}
      {tasksError && (
        <Card className="p-4 border-red-200 bg-red-50">
          <div className="flex items-center gap-2 text-red-600">
            <AlertCircle className="h-5 w-5" />
            <span>{tasksError}</span>
          </div>
        </Card>
      )}

      {/* Kanban Board */}
      {viewMode === 'board' && (
        <div className="flex gap-4 overflow-x-auto pb-4">
          {taskColumns.map((column) => (
            <KanbanColumn
              key={column.id}
              column={column}
              tasks={filteredTasks}
              onTaskClick={handleTaskClick}
            />
          ))}
        </div>
      )}

      {/* List View */}
      {viewMode === 'list' && (
        <Card>
          <CardContent className="p-0">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b bg-muted/50">
                    <th className="text-left p-3 text-xs font-medium text-muted-foreground w-8"></th>
                    <th className="text-left p-3 text-xs font-medium text-muted-foreground">Task</th>
                    <th className="text-left p-3 text-xs font-medium text-muted-foreground">Project</th>
                    <th className="text-left p-3 text-xs font-medium text-muted-foreground">Status</th>
                    <th className="text-left p-3 text-xs font-medium text-muted-foreground">Priority</th>
                    <th className="text-left p-3 text-xs font-medium text-muted-foreground">Assignee</th>
                    <th className="text-left p-3 text-xs font-medium text-muted-foreground">Due Date</th>
                    <th className="text-right p-3 text-xs font-medium text-muted-foreground">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredTasks.map((task) => {
                    const priority = priorityConfig[task.priority]
                    const isOverdue = task.due_date && new Date(task.due_date) < new Date() && task.status !== 'done'

                    return (
                      <tr
                        key={task.id}
                        className="border-b hover:bg-muted/30 cursor-pointer"
                        onClick={() => handleTaskClick(task)}
                      >
                        <td className="p-3">
                          {task.status === 'done' ? (
                            <CheckCircle2 className="h-4 w-4 text-green-500" />
                          ) : (
                            <Circle className="h-4 w-4 text-muted-foreground" />
                          )}
                        </td>
                        <td className="p-3">
                          <p className={`font-medium text-sm ${task.status === 'done' ? 'line-through text-muted-foreground' : ''}`}>
                            {task.title}
                          </p>
                          {task.labels && task.labels.length > 0 && (
                            <div className="flex gap-1 mt-1">
                              {task.labels.slice(0, 2).map((label) => (
                                <Badge
                                  key={label}
                                  variant="secondary"
                                  className={`text-[10px] px-1.5 py-0 ${labelColors[label] || ''}`}
                                >
                                  {label}
                                </Badge>
                              ))}
                            </div>
                          )}
                        </td>
                        <td className="p-3">
                          <p className="text-sm text-muted-foreground">{task.project_name}</p>
                        </td>
                        <td className="p-3">
                          <Badge variant="outline" className="text-xs capitalize">
                            {task.status.replace('_', ' ')}
                          </Badge>
                        </td>
                        <td className="p-3">
                          <span className={`flex items-center gap-1 text-xs ${priority.color}`}>
                            {priority.icon}
                            {priority.label}
                          </span>
                        </td>
                        <td className="p-3">
                          {task.assignee_name ? (
                            <div className="flex items-center gap-2">
                              <Avatar className="h-6 w-6">
                                <AvatarFallback className="text-xs">
                                  {task.assignee_name.split(' ').map((n) => n[0]).join('')}
                                </AvatarFallback>
                              </Avatar>
                              <span className="text-sm">{task.assignee_name}</span>
                            </div>
                          ) : (
                            <span className="text-sm text-muted-foreground">-</span>
                          )}
                        </td>
                        <td className="p-3">
                          <span className={`text-sm ${isOverdue ? 'text-red-600 font-medium' : 'text-muted-foreground'}`}>
                            {task.due_date ? formatDate(task.due_date) : '-'}
                          </span>
                        </td>
                        <td className="p-3 text-right">
                          <div className="flex items-center justify-end gap-1">
                            <Button variant="ghost" size="icon" className="h-8 w-8">
                              <MoreHorizontal className="h-4 w-4" />
                            </Button>
                            <Button
                              variant="ghost"
                              size="icon"
                              className="h-8 w-8 text-red-600 hover:text-red-700 hover:bg-red-50"
                              onClick={(e) => handleDeleteClick(task, e)}
                            >
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          </div>
                        </td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Dialogs */}
      <AddTaskDialog open={addDialogOpen} onOpenChange={setAddDialogOpen} />
      <TaskDetailDialog
        task={selectedTask}
        open={detailDialogOpen}
        onOpenChange={setDetailDialogOpen}
      />

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-red-500" />
              Delete Task
            </AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete the task <strong>{taskToDelete?.title}</strong>?
              This action cannot be undone.
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
