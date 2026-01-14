'use client'

import { useState, useEffect } from 'react'
import { PageHeader } from '@/components/layout/page-header'
import { StatCard } from '@/components/layout/stat-card'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import Link from 'next/link'
import {
  Layers,
  ListTodo,
  Bot,
  Shield,
  Clock,
  CheckCircle2,
  AlertCircle,
  Pause,
  PlayCircle,
  TrendingUp,
  Calendar,
  ChevronRight,
  BarChart3,
  Target,
  Cpu,
  FolderKanban,
  Loader2,
  RefreshCw,
} from 'lucide-react'

// Types
interface WBSDashboardSummary {
  total_phases: number
  total_modules: number
  total_tasks: number
  tasks_by_status: Record<string, number>
  tasks_by_agent: Record<string, number>
  tasks_by_priority: Record<string, number>
  overall_progress: number
  recently_completed: WBSTask[]
  blocked_tasks: WBSTask[]
  in_progress_tasks: WBSTask[]
}

interface WBSPhase {
  id: string
  phase_code: string
  name: string
  description: string | null
  start_week: number | null
  end_week: number | null
  status: 'pending' | 'in_progress' | 'completed'
  progress_percent: number
  task_count?: number
  completed_count?: number
}

interface WBSTask {
  id: string
  task_id: string
  feature_code: string
  title: string
  description: string | null
  assigned_agent: string
  priority: string
  complexity: string
  status: string
  estimated_hours: number | null
  actual_hours: number | null
  started_at: string | null
  completed_at: string | null
}

// Status config for visual styling
const statusConfig: Record<string, { color: string; icon: React.ReactNode; label: string }> = {
  pending: { color: 'bg-slate-100 text-slate-700', icon: <Clock className="h-3.5 w-3.5" />, label: 'Pending' },
  blocked: { color: 'bg-red-100 text-red-700', icon: <AlertCircle className="h-3.5 w-3.5" />, label: 'Blocked' },
  in_progress: { color: 'bg-blue-100 text-blue-700', icon: <PlayCircle className="h-3.5 w-3.5" />, label: 'In Progress' },
  review: { color: 'bg-purple-100 text-purple-700', icon: <Shield className="h-3.5 w-3.5" />, label: 'In Review' },
  completed: { color: 'bg-green-100 text-green-700', icon: <CheckCircle2 className="h-3.5 w-3.5" />, label: 'Completed' },
  failed: { color: 'bg-red-100 text-red-700', icon: <AlertCircle className="h-3.5 w-3.5" />, label: 'Failed' },
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

// Phase Card Component
function PhaseCard({ phase }: { phase: WBSPhase }) {
  const status = statusConfig[phase.status] || statusConfig.pending

  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardHeader className="pb-2">
        <div className="flex items-start justify-between">
          <div>
            <Badge variant="outline" className="text-xs font-mono mb-2">
              {phase.phase_code}
            </Badge>
            <CardTitle className="text-base">{phase.name}</CardTitle>
            {phase.start_week && phase.end_week && (
              <CardDescription className="text-xs mt-1">
                <Calendar className="h-3 w-3 inline mr-1" />
                Week {phase.start_week} - {phase.end_week}
              </CardDescription>
            )}
          </div>
          <Badge className={`text-xs ${status.color}`}>
            {status.icon}
            <span className="ml-1">{status.label}</span>
          </Badge>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-2">
          <div className="flex justify-between text-xs">
            <span className="text-muted-foreground">Progress</span>
            <span className="font-medium">{phase.progress_percent.toFixed(0)}%</span>
          </div>
          <Progress value={Number(phase.progress_percent)} className="h-2" />
          {phase.task_count !== undefined && (
            <p className="text-xs text-muted-foreground">
              {phase.completed_count || 0} / {phase.task_count} tasks completed
            </p>
          )}
        </div>
      </CardContent>
    </Card>
  )
}

// Task Card Component
function TaskCard({ task }: { task: WBSTask }) {
  const status = statusConfig[task.status] || statusConfig.pending
  const agent = agentConfig[task.assigned_agent] || { color: 'bg-gray-100 text-gray-700', label: task.assigned_agent }
  const priority = priorityConfig[task.priority] || priorityConfig.P2

  return (
    <div className="flex items-center justify-between p-3 border rounded-lg hover:bg-muted/50 transition-colors">
      <div className="flex items-center gap-3 flex-1 min-w-0">
        <div className="flex flex-col gap-1">
          <div className="flex items-center gap-2">
            <Badge variant="outline" className="text-xs font-mono shrink-0">
              {task.task_id}
            </Badge>
            <Badge className={`text-xs shrink-0 ${priority.color}`}>
              {task.priority}
            </Badge>
            <Badge className={`text-xs shrink-0 ${agent.color}`}>
              {agent.label}
            </Badge>
          </div>
          <p className="text-sm font-medium truncate">{task.title}</p>
        </div>
      </div>
      <div className="flex items-center gap-2 shrink-0">
        <Badge className={`text-xs ${status.color}`}>
          {status.icon}
          <span className="ml-1">{status.label}</span>
        </Badge>
        {task.estimated_hours && (
          <span className="text-xs text-muted-foreground">
            {task.estimated_hours}h
          </span>
        )}
      </div>
    </div>
  )
}

export default function WBSDashboardPage() {
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [dashboard, setDashboard] = useState<WBSDashboardSummary | null>(null)
  const [phases, setPhases] = useState<WBSPhase[]>([])

  const fetchData = async () => {
    setIsLoading(true)
    setError(null)
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

      // Fetch dashboard summary
      const dashboardRes = await fetch(`${apiUrl}/wbs/dashboard`)
      if (dashboardRes.ok) {
        const dashboardData = await dashboardRes.json()
        setDashboard(dashboardData)
      }

      // Fetch phases
      const phasesRes = await fetch(`${apiUrl}/wbs/phases`)
      if (phasesRes.ok) {
        const phasesData = await phasesRes.json()
        setPhases(phasesData)
      }
    } catch (err) {
      console.error('Failed to fetch WBS data:', err)
      setError('Failed to load WBS data. API may not be running.')
      // Use mock data
      setDashboard({
        total_phases: 12,
        total_modules: 21,
        total_tasks: 0,
        tasks_by_status: {},
        tasks_by_agent: {},
        tasks_by_priority: {},
        overall_progress: 0,
        recently_completed: [],
        blocked_tasks: [],
        in_progress_tasks: [],
      })
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [])

  // Calculate stats
  const totalTasks = dashboard?.total_tasks || 0
  const completedTasks = dashboard?.tasks_by_status?.completed || 0
  const inProgressTasks = dashboard?.tasks_by_status?.in_progress || 0
  const blockedTasks = dashboard?.tasks_by_status?.blocked || 0
  const pendingTasks = dashboard?.tasks_by_status?.pending || 0

  return (
    <div className="space-y-6">
      <PageHeader
        title="WBS Dashboard"
        description="Work Breakdown Structure - Track development progress with specialized agents"
        actions={
          <div className="flex gap-2">
            <Button variant="outline" onClick={fetchData} disabled={isLoading}>
              <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
            <Link href="/wbs-dashboard/tasks">
              <Button>
                <ListTodo className="h-4 w-4 mr-2" />
                View All Tasks
              </Button>
            </Link>
          </div>
        }
      />

      {/* Loading State */}
      {isLoading && (
        <Card className="p-8 flex items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <span className="ml-2">Loading WBS data...</span>
        </Card>
      )}

      {/* Error State */}
      {error && (
        <Card className="p-4 border-yellow-200 bg-yellow-50">
          <div className="flex items-center gap-2 text-yellow-700">
            <AlertCircle className="h-5 w-5" />
            <span>{error}</span>
          </div>
        </Card>
      )}

      {!isLoading && (
        <>
          {/* Overall Stats */}
          <div className="grid gap-4 md:grid-cols-6">
            <StatCard
              title="Total Phases"
              value={dashboard?.total_phases || 12}
              icon={<Layers className="h-4 w-4" />}
              description="Project phases"
            />
            <StatCard
              title="Total Modules"
              value={dashboard?.total_modules || 21}
              icon={<FolderKanban className="h-4 w-4" />}
              description="Feature modules"
            />
            <StatCard
              title="Total Tasks"
              value={totalTasks}
              icon={<ListTodo className="h-4 w-4" />}
              description={`${completedTasks} completed`}
            />
            <StatCard
              title="In Progress"
              value={inProgressTasks}
              icon={<PlayCircle className="h-4 w-4" />}
              description="Active tasks"
            />
            <StatCard
              title="Blocked"
              value={blockedTasks}
              icon={<AlertCircle className="h-4 w-4" />}
              description="Need attention"
              trend={blockedTasks > 0 ? 'up' : undefined}
            />
            <StatCard
              title="Overall Progress"
              value={`${dashboard?.overall_progress?.toFixed(0) || 0}%`}
              icon={<TrendingUp className="h-4 w-4" />}
              description="Completion rate"
            />
          </div>

          {/* Main Content Tabs */}
          <Tabs defaultValue="phases" className="space-y-4">
            <TabsList>
              <TabsTrigger value="phases" className="flex items-center gap-2">
                <Layers className="h-4 w-4" />
                Phases
              </TabsTrigger>
              <TabsTrigger value="tasks" className="flex items-center gap-2">
                <ListTodo className="h-4 w-4" />
                Recent Tasks
              </TabsTrigger>
              <TabsTrigger value="agents" className="flex items-center gap-2">
                <Bot className="h-4 w-4" />
                Agent Stats
              </TabsTrigger>
            </TabsList>

            {/* Phases Tab */}
            <TabsContent value="phases" className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold">Development Phases (48 Weeks)</h3>
                <Link href="/wbs-dashboard/phases">
                  <Button variant="outline" size="sm">
                    View All Phases
                    <ChevronRight className="h-4 w-4 ml-1" />
                  </Button>
                </Link>
              </div>
              <div className="grid gap-4 md:grid-cols-3 lg:grid-cols-4">
                {phases.map((phase) => (
                  <PhaseCard key={phase.id} phase={phase} />
                ))}
              </div>
            </TabsContent>

            {/* Recent Tasks Tab */}
            <TabsContent value="tasks" className="space-y-4">
              <div className="grid gap-6 md:grid-cols-2">
                {/* In Progress Tasks */}
                <Card>
                  <CardHeader>
                    <CardTitle className="text-base flex items-center gap-2">
                      <PlayCircle className="h-4 w-4 text-blue-600" />
                      In Progress ({dashboard?.in_progress_tasks?.length || 0})
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-2">
                    {dashboard?.in_progress_tasks && dashboard.in_progress_tasks.length > 0 ? (
                      dashboard.in_progress_tasks.slice(0, 5).map((task) => (
                        <TaskCard key={task.id} task={task} />
                      ))
                    ) : (
                      <p className="text-sm text-muted-foreground text-center py-4">
                        No tasks in progress
                      </p>
                    )}
                  </CardContent>
                </Card>

                {/* Blocked Tasks */}
                <Card>
                  <CardHeader>
                    <CardTitle className="text-base flex items-center gap-2">
                      <AlertCircle className="h-4 w-4 text-red-600" />
                      Blocked ({dashboard?.blocked_tasks?.length || 0})
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-2">
                    {dashboard?.blocked_tasks && dashboard.blocked_tasks.length > 0 ? (
                      dashboard.blocked_tasks.slice(0, 5).map((task) => (
                        <TaskCard key={task.id} task={task} />
                      ))
                    ) : (
                      <p className="text-sm text-muted-foreground text-center py-4">
                        No blocked tasks
                      </p>
                    )}
                  </CardContent>
                </Card>

                {/* Recently Completed */}
                <Card className="md:col-span-2">
                  <CardHeader>
                    <CardTitle className="text-base flex items-center gap-2">
                      <CheckCircle2 className="h-4 w-4 text-green-600" />
                      Recently Completed ({dashboard?.recently_completed?.length || 0})
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-2">
                    {dashboard?.recently_completed && dashboard.recently_completed.length > 0 ? (
                      dashboard.recently_completed.slice(0, 5).map((task) => (
                        <TaskCard key={task.id} task={task} />
                      ))
                    ) : (
                      <p className="text-sm text-muted-foreground text-center py-4">
                        No recently completed tasks
                      </p>
                    )}
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            {/* Agent Stats Tab */}
            <TabsContent value="agents" className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold">Agent Assignment Distribution</h3>
                <Link href="/wbs-dashboard/agents">
                  <Button variant="outline" size="sm">
                    View Agent Details
                    <ChevronRight className="h-4 w-4 ml-1" />
                  </Button>
                </Link>
              </div>
              <div className="grid gap-4 md:grid-cols-3">
                {Object.entries(agentConfig).map(([code, config]) => {
                  const taskCount = dashboard?.tasks_by_agent?.[code] || 0
                  return (
                    <Card key={code}>
                      <CardContent className="pt-4">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-3">
                            <div className={`p-2 rounded-lg ${config.color}`}>
                              <Cpu className="h-5 w-5" />
                            </div>
                            <div>
                              <p className="font-medium">{config.label} Agent</p>
                              <p className="text-xs text-muted-foreground">{code}</p>
                            </div>
                          </div>
                          <div className="text-right">
                            <p className="text-2xl font-bold">{taskCount}</p>
                            <p className="text-xs text-muted-foreground">tasks</p>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  )
                })}
              </div>
            </TabsContent>
          </Tabs>

          {/* Quick Actions */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Quick Actions</CardTitle>
              <CardDescription>Navigate to different WBS sections</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-3 md:grid-cols-5">
                <Link href="/wbs-dashboard/phases">
                  <Button variant="outline" className="w-full justify-start">
                    <Layers className="h-4 w-4 mr-2" />
                    Phases
                  </Button>
                </Link>
                <Link href="/wbs-dashboard/modules">
                  <Button variant="outline" className="w-full justify-start">
                    <FolderKanban className="h-4 w-4 mr-2" />
                    Modules
                  </Button>
                </Link>
                <Link href="/wbs-dashboard/tasks">
                  <Button variant="outline" className="w-full justify-start">
                    <ListTodo className="h-4 w-4 mr-2" />
                    Tasks
                  </Button>
                </Link>
                <Link href="/wbs-dashboard/agents">
                  <Button variant="outline" className="w-full justify-start">
                    <Bot className="h-4 w-4 mr-2" />
                    Agents
                  </Button>
                </Link>
                <Link href="/wbs-dashboard/quality-gates">
                  <Button variant="outline" className="w-full justify-start">
                    <Shield className="h-4 w-4 mr-2" />
                    Quality Gates
                  </Button>
                </Link>
              </div>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  )
}
