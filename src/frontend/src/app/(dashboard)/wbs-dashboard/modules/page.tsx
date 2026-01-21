'use client'

import { useState, useEffect, useCallback } from 'react'
import { PageHeader } from '@/components/layout/page-header'
import { useAuth } from '@/hooks/use-auth'
import { useToast } from '@/hooks/use-toast'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import Link from 'next/link'
import {
  FolderKanban,
  ChevronLeft,
  Database,
  Server,
  Layout,
  ListTodo,
  Clock,
  CheckCircle2,
  PlayCircle,
  Loader2,
  RefreshCw,
  TrendingUp,
  ArrowUpDown,
} from 'lucide-react'

// Types
interface WBSModule {
  id: string
  module_code: string
  name: string
  description: string | null
  new_tables: number
  new_endpoints: number
  new_pages: number
  priority: number
  status: 'pending' | 'in_progress' | 'completed'
  progress_percent: number
  task_count?: number
  completed_count?: number
  created_at: string
}

// Status config
const statusConfig: Record<string, { color: string; icon: React.ReactNode; label: string }> = {
  pending: { color: 'bg-slate-100 text-slate-700', icon: <Clock className="h-4 w-4" />, label: 'Pending' },
  in_progress: { color: 'bg-blue-100 text-blue-700', icon: <PlayCircle className="h-4 w-4" />, label: 'In Progress' },
  completed: { color: 'bg-green-100 text-green-700', icon: <CheckCircle2 className="h-4 w-4" />, label: 'Completed' },
}

// Priority colors
const priorityColors: Record<number, string> = {
  1: 'bg-red-500',
  2: 'bg-orange-500',
  3: 'bg-yellow-500',
  4: 'bg-lime-500',
  5: 'bg-green-500',
}

// Module Card Component
function ModuleCard({ module }: { module: WBSModule }) {
  const status = statusConfig[module.status] || statusConfig.pending
  const progressValue = Number(module.progress_percent)
  const priorityColor = priorityColors[Math.min(module.priority, 5)] || 'bg-slate-500'

  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardHeader className="pb-2">
        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <Badge variant="outline" className="text-xs font-mono">
                {module.module_code}
              </Badge>
              <div className={`w-2 h-2 rounded-full ${priorityColor}`} title={`Priority ${module.priority}`} />
            </div>
            <CardTitle className="text-base">{module.name}</CardTitle>
          </div>
          <Badge className={`text-xs ${status.color}`}>
            {status.icon}
            <span className="ml-1">{status.label}</span>
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {module.description && (
          <p className="text-sm text-muted-foreground line-clamp-2">{module.description}</p>
        )}

        {/* Scope */}
        <div className="grid grid-cols-3 gap-2">
          <div className="flex items-center gap-2 p-2 bg-muted/50 rounded">
            <Database className="h-4 w-4 text-amber-600" />
            <div>
              <p className="text-lg font-bold">{module.new_tables}</p>
              <p className="text-xs text-muted-foreground">Tables</p>
            </div>
          </div>
          <div className="flex items-center gap-2 p-2 bg-muted/50 rounded">
            <Server className="h-4 w-4 text-blue-600" />
            <div>
              <p className="text-lg font-bold">{module.new_endpoints}</p>
              <p className="text-xs text-muted-foreground">APIs</p>
            </div>
          </div>
          <div className="flex items-center gap-2 p-2 bg-muted/50 rounded">
            <Layout className="h-4 w-4 text-green-600" />
            <div>
              <p className="text-lg font-bold">{module.new_pages}</p>
              <p className="text-xs text-muted-foreground">Pages</p>
            </div>
          </div>
        </div>

        {/* Progress */}
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Progress</span>
            <span className="font-medium">{progressValue.toFixed(0)}%</span>
          </div>
          <Progress value={progressValue} className="h-2" />
        </div>

        {/* Task Count */}
        {module.task_count !== undefined && (
          <p className="text-xs text-muted-foreground">
            {module.completed_count || 0} / {module.task_count} tasks completed
          </p>
        )}

        {/* View Tasks Button */}
        <Link href={`/wbs-dashboard/tasks?module=${module.module_code}`}>
          <Button variant="outline" size="sm" className="w-full">
            <ListTodo className="h-4 w-4 mr-2" />
            View Tasks
          </Button>
        </Link>
      </CardContent>
    </Card>
  )
}

export default function WBSModulesPage() {
  const [isLoading, setIsLoading] = useState(true)
  const [modules, setModules] = useState<WBSModule[]>([])
  const [sortBy, setSortBy] = useState<'priority' | 'name' | 'progress'>('priority')
  const { fetchWithAuth } = useAuth()
  const { toast } = useToast()

  const fetchModules = useCallback(async () => {
    setIsLoading(true)
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || '/api/v1'
      const res = await fetchWithAuth(`${apiUrl}/wbs/modules`)
      if (res.ok) {
        const data = await res.json()
        setModules(data)
      }
    } catch (err) {
      toast.error('Failed to fetch modules', 'Please try again or contact support')
    } finally {
      setIsLoading(false)
    }
  }, [fetchWithAuth])

  useEffect(() => {
    fetchModules()
  }, [fetchModules])

  // Sort modules
  const sortedModules = [...modules].sort((a, b) => {
    if (sortBy === 'priority') return a.priority - b.priority
    if (sortBy === 'name') return a.name.localeCompare(b.name)
    if (sortBy === 'progress') return Number(b.progress_percent) - Number(a.progress_percent)
    return 0
  })

  // Calculate stats
  const totalModules = modules.length
  const completedModules = modules.filter(m => m.status === 'completed').length
  const inProgressModules = modules.filter(m => m.status === 'in_progress').length
  const totalTables = modules.reduce((sum, m) => sum + m.new_tables, 0)
  const totalEndpoints = modules.reduce((sum, m) => sum + m.new_endpoints, 0)
  const totalPages = modules.reduce((sum, m) => sum + m.new_pages, 0)

  return (
    <div className="space-y-6">
      <PageHeader
        title="Feature Modules"
        description="21 modules organized by priority for development"
        actions={
          <div className="flex gap-2">
            <Link href="/wbs-dashboard">
              <Button variant="outline">
                <ChevronLeft className="h-4 w-4 mr-1" />
                Dashboard
              </Button>
            </Link>
            <Button variant="outline" onClick={fetchModules} disabled={isLoading}>
              <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
          </div>
        }
      />

      {/* Module Stats */}
      <div className="grid gap-4 md:grid-cols-6">
        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-primary/10">
                <FolderKanban className="h-5 w-5 text-primary" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Modules</p>
                <p className="text-2xl font-bold">{totalModules}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-blue-100">
                <PlayCircle className="h-5 w-5 text-blue-600" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Active</p>
                <p className="text-2xl font-bold">{inProgressModules}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-green-100">
                <CheckCircle2 className="h-5 w-5 text-green-600" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Complete</p>
                <p className="text-2xl font-bold">{completedModules}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-amber-100">
                <Database className="h-5 w-5 text-amber-600" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">New Tables</p>
                <p className="text-2xl font-bold">{totalTables}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-blue-100">
                <Server className="h-5 w-5 text-blue-600" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">New APIs</p>
                <p className="text-2xl font-bold">{totalEndpoints}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-green-100">
                <Layout className="h-5 w-5 text-green-600" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">New Pages</p>
                <p className="text-2xl font-bold">{totalPages}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Sort Options */}
      <Card>
        <CardContent className="pt-4">
          <div className="flex items-center gap-4">
            <span className="text-sm text-muted-foreground">Sort by:</span>
            <Button
              variant={sortBy === 'priority' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setSortBy('priority')}
            >
              <ArrowUpDown className="h-3 w-3 mr-1" />
              Priority
            </Button>
            <Button
              variant={sortBy === 'name' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setSortBy('name')}
            >
              <ArrowUpDown className="h-3 w-3 mr-1" />
              Name
            </Button>
            <Button
              variant={sortBy === 'progress' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setSortBy('progress')}
            >
              <ArrowUpDown className="h-3 w-3 mr-1" />
              Progress
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Loading State */}
      {isLoading && (
        <Card className="p-8 flex items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <span className="ml-2">Loading modules...</span>
        </Card>
      )}

      {/* Module Cards */}
      {!isLoading && (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {sortedModules.map((module) => (
            <ModuleCard key={module.id} module={module} />
          ))}
        </div>
      )}

      {!isLoading && modules.length === 0 && (
        <Card className="p-8 text-center">
          <FolderKanban className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
          <p className="text-muted-foreground">No modules found</p>
          <p className="text-sm text-muted-foreground mt-1">
            Run the WBS seed script to populate modules
          </p>
        </Card>
      )}
    </div>
  )
}
