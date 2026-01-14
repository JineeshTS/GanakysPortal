'use client'

import { useState, useEffect, useCallback } from 'react'
import { PageHeader } from '@/components/layout/page-header'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Progress } from '@/components/ui/progress'
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
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import {
  Search,
  Filter,
  ListTodo,
  Clock,
  CheckCircle2,
  AlertCircle,
  PlayCircle,
  Shield,
  ChevronLeft,
  ChevronRight,
  ExternalLink,
  Loader2,
  RefreshCw,
  Play,
  XCircle,
  CheckCircle,
  Eye,
} from 'lucide-react'
import Link from 'next/link'

// Types
interface WBSTask {
  id: string
  task_id: string
  phase_id: string | null
  module_id: string | null
  feature_code: string
  title: string
  description: string | null
  assigned_agent: string
  priority: string
  complexity: string
  status: string
  estimated_hours: number | null
  actual_hours: number | null
  blocking_deps: string[]
  non_blocking_deps: string[]
  input_files: string[]
  output_files: string[]
  acceptance_criteria: string[]
  started_at: string | null
  completed_at: string | null
  error_message: string | null
  quality_gate: string | null
  tests_passed: boolean | null
  review_approved: boolean | null
  created_at: string
  updated_at: string
}

interface TaskListResponse {
  tasks: WBSTask[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

// Status config
const statusConfig: Record<string, { color: string; icon: React.ReactNode; label: string }> = {
  pending: { color: 'bg-slate-100 text-slate-700', icon: <Clock className="h-3.5 w-3.5" />, label: 'Pending' },
  blocked: { color: 'bg-red-100 text-red-700', icon: <AlertCircle className="h-3.5 w-3.5" />, label: 'Blocked' },
  in_progress: { color: 'bg-blue-100 text-blue-700', icon: <PlayCircle className="h-3.5 w-3.5" />, label: 'In Progress' },
  review: { color: 'bg-purple-100 text-purple-700', icon: <Shield className="h-3.5 w-3.5" />, label: 'In Review' },
  completed: { color: 'bg-green-100 text-green-700', icon: <CheckCircle2 className="h-3.5 w-3.5" />, label: 'Completed' },
  failed: { color: 'bg-red-100 text-red-700', icon: <XCircle className="h-3.5 w-3.5" />, label: 'Failed' },
}

const agentConfig: Record<string, { color: string; label: string }> = {
  'DB-AGENT': { color: 'bg-amber-100 text-amber-700', label: 'Database' },
  'API-AGENT': { color: 'bg-blue-100 text-blue-700', label: 'API' },
  'SVC-AGENT': { color: 'bg-purple-100 text-purple-700', label: 'Service' },
  'PAGE-AGENT': { color: 'bg-green-100 text-green-700', label: 'Page' },
  'COMP-AGENT': { color: 'bg-pink-100 text-pink-700', label: 'Component' },
  'TEST-AGENT': { color: 'bg-cyan-100 text-cyan-700', label: 'Test' },
  'DOC-AGENT': { color: 'bg-slate-100 text-slate-700', label: 'Documentation' },
  'INT-AGENT': { color: 'bg-orange-100 text-orange-700', label: 'Integration' },
  'AI-AGENT': { color: 'bg-violet-100 text-violet-700', label: 'AI' },
}

const priorityConfig: Record<string, { color: string; label: string }> = {
  'P0': { color: 'bg-red-500 text-white', label: 'Critical' },
  'P1': { color: 'bg-orange-500 text-white', label: 'High' },
  'P2': { color: 'bg-blue-500 text-white', label: 'Medium' },
  'P3': { color: 'bg-slate-400 text-white', label: 'Low' },
}

const complexityConfig: Record<string, string> = {
  'low': 'text-green-600',
  'medium': 'text-blue-600',
  'high': 'text-orange-600',
  'critical': 'text-red-600',
}

// Task Detail Dialog
function TaskDetailDialog({
  task,
  open,
  onOpenChange,
  onStartTask,
  onCompleteTask,
  onFailTask,
}: {
  task: WBSTask | null
  open: boolean
  onOpenChange: (open: boolean) => void
  onStartTask: (taskId: string) => void
  onCompleteTask: (taskId: string) => void
  onFailTask: (taskId: string, error: string) => void
}) {
  const [failError, setFailError] = useState('')
  const [showFailDialog, setShowFailDialog] = useState(false)

  if (!task) return null

  const status = statusConfig[task.status] || statusConfig.pending
  const agent = agentConfig[task.assigned_agent] || { color: 'bg-gray-100 text-gray-700', label: task.assigned_agent }
  const priority = priorityConfig[task.priority] || priorityConfig.P2

  const canStart = task.status === 'pending' || task.status === 'blocked'
  const canComplete = task.status === 'in_progress' || task.status === 'review'
  const canFail = task.status === 'in_progress'

  return (
    <>
      <Dialog open={open} onOpenChange={onOpenChange}>
        <DialogContent className="sm:max-w-[700px] max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <div className="flex items-start justify-between">
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <Badge variant="outline" className="font-mono">{task.task_id}</Badge>
                  <Badge className={status.color}>
                    {status.icon}
                    <span className="ml-1">{status.label}</span>
                  </Badge>
                </div>
                <DialogTitle className="text-xl">{task.title}</DialogTitle>
                <DialogDescription className="flex items-center gap-2 mt-1">
                  Feature: {task.feature_code}
                </DialogDescription>
              </div>
            </div>
          </DialogHeader>

          <div className="space-y-6 py-4">
            {/* Description */}
            {task.description && (
              <div>
                <Label className="text-xs text-muted-foreground">Description</Label>
                <p className="text-sm mt-1">{task.description}</p>
              </div>
            )}

            {/* Key Info */}
            <div className="grid grid-cols-4 gap-4">
              <div className="bg-muted/50 rounded-lg p-3 text-center">
                <Badge className={agent.color}>{agent.label}</Badge>
                <p className="text-xs text-muted-foreground mt-1">Agent</p>
              </div>
              <div className="bg-muted/50 rounded-lg p-3 text-center">
                <Badge className={priority.color}>{task.priority}</Badge>
                <p className="text-xs text-muted-foreground mt-1">Priority</p>
              </div>
              <div className="bg-muted/50 rounded-lg p-3 text-center">
                <p className={`text-lg font-bold capitalize ${complexityConfig[task.complexity] || ''}`}>
                  {task.complexity}
                </p>
                <p className="text-xs text-muted-foreground">Complexity</p>
              </div>
              <div className="bg-muted/50 rounded-lg p-3 text-center">
                <p className="text-lg font-bold">{task.estimated_hours || '-'}h</p>
                <p className="text-xs text-muted-foreground">Estimated</p>
              </div>
            </div>

            {/* Dependencies */}
            {(task.blocking_deps.length > 0 || task.non_blocking_deps.length > 0) && (
              <div className="grid grid-cols-2 gap-4">
                {task.blocking_deps.length > 0 && (
                  <div>
                    <Label className="text-xs text-muted-foreground">Blocking Dependencies</Label>
                    <div className="mt-2 space-y-1">
                      {task.blocking_deps.map((dep) => (
                        <Badge key={dep} variant="outline" className="mr-1 text-red-600 border-red-200">
                          {dep}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
                {task.non_blocking_deps.length > 0 && (
                  <div>
                    <Label className="text-xs text-muted-foreground">Non-Blocking Dependencies</Label>
                    <div className="mt-2 space-y-1">
                      {task.non_blocking_deps.map((dep) => (
                        <Badge key={dep} variant="outline" className="mr-1">
                          {dep}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Files */}
            {(task.input_files.length > 0 || task.output_files.length > 0) && (
              <div className="grid grid-cols-2 gap-4">
                {task.input_files.length > 0 && (
                  <div>
                    <Label className="text-xs text-muted-foreground">Input Files</Label>
                    <div className="mt-2 space-y-1 text-xs font-mono">
                      {task.input_files.map((file, i) => (
                        <p key={i} className="text-muted-foreground truncate">{file}</p>
                      ))}
                    </div>
                  </div>
                )}
                {task.output_files.length > 0 && (
                  <div>
                    <Label className="text-xs text-muted-foreground">Output Files</Label>
                    <div className="mt-2 space-y-1 text-xs font-mono">
                      {task.output_files.map((file, i) => (
                        <p key={i} className="text-muted-foreground truncate">{file}</p>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Acceptance Criteria */}
            {task.acceptance_criteria.length > 0 && (
              <div>
                <Label className="text-xs text-muted-foreground">Acceptance Criteria</Label>
                <ul className="mt-2 space-y-1 text-sm list-disc list-inside">
                  {task.acceptance_criteria.map((criterion, i) => (
                    <li key={i} className="text-muted-foreground">{criterion}</li>
                  ))}
                </ul>
              </div>
            )}

            {/* Error Message */}
            {task.error_message && (
              <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
                <Label className="text-xs text-red-600">Error</Label>
                <p className="text-sm text-red-700 mt-1">{task.error_message}</p>
              </div>
            )}

            {/* Timestamps */}
            <div className="grid grid-cols-2 gap-4 text-xs text-muted-foreground">
              {task.started_at && (
                <p>Started: {new Date(task.started_at).toLocaleString()}</p>
              )}
              {task.completed_at && (
                <p>Completed: {new Date(task.completed_at).toLocaleString()}</p>
              )}
            </div>
          </div>

          <DialogFooter className="gap-2">
            {canStart && (
              <Button onClick={() => { onStartTask(task.task_id); onOpenChange(false) }}>
                <Play className="h-4 w-4 mr-2" />
                Start Task
              </Button>
            )}
            {canComplete && (
              <Button variant="default" className="bg-green-600 hover:bg-green-700" onClick={() => { onCompleteTask(task.task_id); onOpenChange(false) }}>
                <CheckCircle className="h-4 w-4 mr-2" />
                Mark Complete
              </Button>
            )}
            {canFail && (
              <Button variant="destructive" onClick={() => setShowFailDialog(true)}>
                <XCircle className="h-4 w-4 mr-2" />
                Mark Failed
              </Button>
            )}
            <Button variant="outline" onClick={() => onOpenChange(false)}>
              Close
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Fail Dialog */}
      <Dialog open={showFailDialog} onOpenChange={setShowFailDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Mark Task as Failed</DialogTitle>
            <DialogDescription>
              Please provide an error message for task {task?.task_id}
            </DialogDescription>
          </DialogHeader>
          <div className="py-4">
            <Label>Error Message</Label>
            <Input
              value={failError}
              onChange={(e) => setFailError(e.target.value)}
              placeholder="Describe what went wrong..."
              className="mt-2"
            />
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowFailDialog(false)}>
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={() => {
                if (task) {
                  onFailTask(task.task_id, failError)
                  setShowFailDialog(false)
                  onOpenChange(false)
                  setFailError('')
                }
              }}
            >
              Confirm Failure
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  )
}

export default function WBSTasksPage() {
  const [isLoading, setIsLoading] = useState(true)
  const [tasks, setTasks] = useState<WBSTask[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [pageSize] = useState(20)
  const [totalPages, setTotalPages] = useState(0)

  // Filters
  const [searchQuery, setSearchQuery] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [agentFilter, setAgentFilter] = useState<string>('all')
  const [priorityFilter, setPriorityFilter] = useState<string>('all')

  // Selected task for detail view
  const [selectedTask, setSelectedTask] = useState<WBSTask | null>(null)
  const [detailDialogOpen, setDetailDialogOpen] = useState(false)

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

  const fetchTasks = useCallback(async () => {
    setIsLoading(true)
    try {
      const params = new URLSearchParams()
      params.set('page', page.toString())
      params.set('page_size', pageSize.toString())
      if (statusFilter !== 'all') params.set('status', statusFilter)
      if (agentFilter !== 'all') params.set('assigned_agent', agentFilter)
      if (priorityFilter !== 'all') params.set('priority', priorityFilter)
      if (searchQuery) params.set('search', searchQuery)

      const res = await fetch(`${apiUrl}/wbs/tasks?${params.toString()}`)
      if (res.ok) {
        const data: TaskListResponse = await res.json()
        setTasks(data.tasks)
        setTotal(data.total)
        setTotalPages(data.total_pages)
      }
    } catch (err) {
      console.error('Failed to fetch tasks:', err)
    } finally {
      setIsLoading(false)
    }
  }, [apiUrl, page, pageSize, statusFilter, agentFilter, priorityFilter, searchQuery])

  useEffect(() => {
    fetchTasks()
  }, [fetchTasks])

  const handleStartTask = async (taskId: string) => {
    try {
      await fetch(`${apiUrl}/wbs/tasks/${taskId}/start`, { method: 'POST' })
      fetchTasks()
    } catch (err) {
      console.error('Failed to start task:', err)
    }
  }

  const handleCompleteTask = async (taskId: string) => {
    try {
      await fetch(`${apiUrl}/wbs/tasks/${taskId}/complete`, { method: 'POST' })
      fetchTasks()
    } catch (err) {
      console.error('Failed to complete task:', err)
    }
  }

  const handleFailTask = async (taskId: string, error: string) => {
    try {
      await fetch(`${apiUrl}/wbs/tasks/${taskId}/fail`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ error_message: error }),
      })
      fetchTasks()
    } catch (err) {
      console.error('Failed to mark task as failed:', err)
    }
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="WBS Tasks"
        description="View and manage all atomic development tasks"
        actions={
          <div className="flex gap-2">
            <Link href="/wbs-dashboard">
              <Button variant="outline">
                <ChevronLeft className="h-4 w-4 mr-1" />
                Dashboard
              </Button>
            </Link>
            <Button variant="outline" onClick={fetchTasks} disabled={isLoading}>
              <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
          </div>
        }
      />

      {/* Filters */}
      <Card>
        <CardContent className="pt-4">
          <div className="flex flex-wrap gap-4">
            <div className="flex-1 min-w-[200px]">
              <div className="relative">
                <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search tasks..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-8"
                />
              </div>
            </div>
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-[150px]">
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="pending">Pending</SelectItem>
                <SelectItem value="blocked">Blocked</SelectItem>
                <SelectItem value="in_progress">In Progress</SelectItem>
                <SelectItem value="review">In Review</SelectItem>
                <SelectItem value="completed">Completed</SelectItem>
                <SelectItem value="failed">Failed</SelectItem>
              </SelectContent>
            </Select>
            <Select value={agentFilter} onValueChange={setAgentFilter}>
              <SelectTrigger className="w-[150px]">
                <SelectValue placeholder="Agent" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Agents</SelectItem>
                {Object.entries(agentConfig).map(([code, config]) => (
                  <SelectItem key={code} value={code}>{config.label}</SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Select value={priorityFilter} onValueChange={setPriorityFilter}>
              <SelectTrigger className="w-[130px]">
                <SelectValue placeholder="Priority" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Priority</SelectItem>
                <SelectItem value="P0">P0 - Critical</SelectItem>
                <SelectItem value="P1">P1 - High</SelectItem>
                <SelectItem value="P2">P2 - Medium</SelectItem>
                <SelectItem value="P3">P3 - Low</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Task Stats */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center justify-between">
              <p className="text-sm text-muted-foreground">Total Tasks</p>
              <p className="text-2xl font-bold">{total}</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center justify-between">
              <p className="text-sm text-muted-foreground">Showing</p>
              <p className="text-2xl font-bold">{tasks.length}</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center justify-between">
              <p className="text-sm text-muted-foreground">Page</p>
              <p className="text-2xl font-bold">{page} / {totalPages || 1}</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                disabled={page <= 1}
                onClick={() => setPage((p) => Math.max(1, p - 1))}
              >
                <ChevronLeft className="h-4 w-4" />
              </Button>
              <Button
                variant="outline"
                size="sm"
                disabled={page >= totalPages}
                onClick={() => setPage((p) => p + 1)}
              >
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Loading State */}
      {isLoading && (
        <Card className="p-8 flex items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <span className="ml-2">Loading tasks...</span>
        </Card>
      )}

      {/* Tasks Table */}
      {!isLoading && (
        <Card>
          <CardContent className="p-0">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-[120px]">Task ID</TableHead>
                  <TableHead>Title</TableHead>
                  <TableHead className="w-[100px]">Agent</TableHead>
                  <TableHead className="w-[80px]">Priority</TableHead>
                  <TableHead className="w-[100px]">Status</TableHead>
                  <TableHead className="w-[80px]">Hours</TableHead>
                  <TableHead className="w-[80px]">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {tasks.map((task) => {
                  const status = statusConfig[task.status] || statusConfig.pending
                  const agent = agentConfig[task.assigned_agent] || { color: 'bg-gray-100 text-gray-700', label: task.assigned_agent }
                  const priority = priorityConfig[task.priority] || priorityConfig.P2

                  return (
                    <TableRow key={task.id} className="cursor-pointer hover:bg-muted/50">
                      <TableCell>
                        <Badge variant="outline" className="font-mono text-xs">
                          {task.task_id}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <div>
                          <p className="font-medium text-sm truncate max-w-[400px]">{task.title}</p>
                          <p className="text-xs text-muted-foreground">{task.feature_code}</p>
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge className={`text-xs ${agent.color}`}>{agent.label}</Badge>
                      </TableCell>
                      <TableCell>
                        <Badge className={`text-xs ${priority.color}`}>{task.priority}</Badge>
                      </TableCell>
                      <TableCell>
                        <Badge className={`text-xs ${status.color}`}>
                          {status.icon}
                          <span className="ml-1">{status.label}</span>
                        </Badge>
                      </TableCell>
                      <TableCell className="text-sm text-muted-foreground">
                        {task.estimated_hours ? `${task.estimated_hours}h` : '-'}
                      </TableCell>
                      <TableCell>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => {
                            setSelectedTask(task)
                            setDetailDialogOpen(true)
                          }}
                        >
                          <Eye className="h-4 w-4" />
                        </Button>
                      </TableCell>
                    </TableRow>
                  )
                })}
              </TableBody>
            </Table>

            {tasks.length === 0 && (
              <div className="text-center py-12">
                <ListTodo className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                <p className="text-muted-foreground">No tasks found</p>
                <p className="text-sm text-muted-foreground mt-1">
                  Tasks will appear here once generated from FEATURES.md
                </p>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Pagination */}
      {!isLoading && totalPages > 1 && (
        <div className="flex items-center justify-center gap-2">
          <Button
            variant="outline"
            disabled={page <= 1}
            onClick={() => setPage((p) => Math.max(1, p - 1))}
          >
            <ChevronLeft className="h-4 w-4 mr-1" />
            Previous
          </Button>
          <span className="text-sm text-muted-foreground px-4">
            Page {page} of {totalPages}
          </span>
          <Button
            variant="outline"
            disabled={page >= totalPages}
            onClick={() => setPage((p) => p + 1)}
          >
            Next
            <ChevronRight className="h-4 w-4 ml-1" />
          </Button>
        </div>
      )}

      {/* Task Detail Dialog */}
      <TaskDetailDialog
        task={selectedTask}
        open={detailDialogOpen}
        onOpenChange={setDetailDialogOpen}
        onStartTask={handleStartTask}
        onCompleteTask={handleCompleteTask}
        onFailTask={handleFailTask}
      />
    </div>
  )
}
