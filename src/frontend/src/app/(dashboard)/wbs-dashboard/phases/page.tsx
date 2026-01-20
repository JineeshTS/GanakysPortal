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
  Layers,
  Clock,
  CheckCircle2,
  PlayCircle,
  ChevronLeft,
  Calendar,
  ListTodo,
  Target,
  Loader2,
  RefreshCw,
  TrendingUp,
} from 'lucide-react'

// Types
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
  created_at: string
  updated_at: string
}

// Status config
const statusConfig: Record<string, { color: string; icon: React.ReactNode; label: string; bgColor: string }> = {
  pending: {
    color: 'bg-slate-100 text-slate-700',
    bgColor: 'bg-slate-50 border-slate-200',
    icon: <Clock className="h-5 w-5" />,
    label: 'Pending'
  },
  in_progress: {
    color: 'bg-blue-100 text-blue-700',
    bgColor: 'bg-blue-50 border-blue-200',
    icon: <PlayCircle className="h-5 w-5" />,
    label: 'In Progress'
  },
  completed: {
    color: 'bg-green-100 text-green-700',
    bgColor: 'bg-green-50 border-green-200',
    icon: <CheckCircle2 className="h-5 w-5" />,
    label: 'Completed'
  },
}

// Phase Details Component
function PhaseDetailCard({ phase }: { phase: WBSPhase }) {
  const status = statusConfig[phase.status] || statusConfig.pending
  const progressValue = Number(phase.progress_percent)
  const weeks = phase.end_week && phase.start_week ? phase.end_week - phase.start_week + 1 : 0

  return (
    <Card className={`border-2 ${status.bgColor}`}>
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            <div className={`p-3 rounded-xl ${status.color}`}>
              {status.icon}
            </div>
            <div>
              <Badge variant="outline" className="text-xs font-mono mb-1">
                {phase.phase_code}
              </Badge>
              <CardTitle className="text-lg">{phase.name}</CardTitle>
            </div>
          </div>
          <Badge className={`${status.color}`}>
            {status.label}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {phase.description && (
          <p className="text-sm text-muted-foreground">{phase.description}</p>
        )}

        {/* Timeline */}
        <div className="flex items-center gap-4 text-sm">
          <div className="flex items-center gap-2">
            <Calendar className="h-4 w-4 text-muted-foreground" />
            <span>
              Week {phase.start_week || '?'} - {phase.end_week || '?'}
            </span>
          </div>
          <div className="flex items-center gap-2">
            <Clock className="h-4 w-4 text-muted-foreground" />
            <span>{weeks} weeks</span>
          </div>
        </div>

        {/* Progress */}
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span className="text-muted-foreground">Progress</span>
            <span className="font-medium">{progressValue.toFixed(0)}%</span>
          </div>
          <Progress value={progressValue} className="h-3" />
        </div>

        {/* Task Stats */}
        <div className="grid grid-cols-3 gap-4 pt-2">
          <div className="text-center p-3 bg-background rounded-lg">
            <p className="text-2xl font-bold">{phase.task_count || 0}</p>
            <p className="text-xs text-muted-foreground">Total Tasks</p>
          </div>
          <div className="text-center p-3 bg-background rounded-lg">
            <p className="text-2xl font-bold text-green-600">{phase.completed_count || 0}</p>
            <p className="text-xs text-muted-foreground">Completed</p>
          </div>
          <div className="text-center p-3 bg-background rounded-lg">
            <p className="text-2xl font-bold text-blue-600">
              {(phase.task_count || 0) - (phase.completed_count || 0)}
            </p>
            <p className="text-xs text-muted-foreground">Remaining</p>
          </div>
        </div>

        {/* View Tasks Button */}
        <Link href={`/wbs-dashboard/tasks?phase=${phase.phase_code}`}>
          <Button variant="outline" className="w-full mt-2">
            <ListTodo className="h-4 w-4 mr-2" />
            View Phase Tasks
          </Button>
        </Link>
      </CardContent>
    </Card>
  )
}

export default function WBSPhasesPage() {
  const [isLoading, setIsLoading] = useState(true)
  const [phases, setPhases] = useState<WBSPhase[]>([])
  const { fetchWithAuth } = useAuth()
  const { toast } = useToast()

  const fetchPhases = useCallback(async () => {
    setIsLoading(true)
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || '/api/v1'
      const res = await fetchWithAuth(`${apiUrl}/wbs/phases`)
      if (res.ok) {
        const data = await res.json()
        setPhases(data)
      }
    } catch (err) {
      toast.error('Failed to fetch phases', 'Please try again or contact support')
    } finally {
      setIsLoading(false)
    }
  }, [fetchWithAuth])

  useEffect(() => {
    fetchPhases()
  }, [fetchPhases])

  // Calculate stats
  const totalPhases = phases.length
  const completedPhases = phases.filter(p => p.status === 'completed').length
  const inProgressPhases = phases.filter(p => p.status === 'in_progress').length
  const overallProgress = phases.length > 0
    ? phases.reduce((sum, p) => sum + Number(p.progress_percent), 0) / phases.length
    : 0

  return (
    <div className="space-y-6">
      <PageHeader
        title="Development Phases"
        description="48-week development timeline with 12 phases"
        actions={
          <div className="flex gap-2">
            <Link href="/wbs-dashboard">
              <Button variant="outline">
                <ChevronLeft className="h-4 w-4 mr-1" />
                Dashboard
              </Button>
            </Link>
            <Button variant="outline" onClick={fetchPhases} disabled={isLoading}>
              <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
          </div>
        }
      />

      {/* Phase Stats */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-primary/10">
                  <Layers className="h-5 w-5 text-primary" />
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Total Phases</p>
                  <p className="text-2xl font-bold">{totalPhases}</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-blue-100">
                  <PlayCircle className="h-5 w-5 text-blue-600" />
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">In Progress</p>
                  <p className="text-2xl font-bold">{inProgressPhases}</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-green-100">
                  <CheckCircle2 className="h-5 w-5 text-green-600" />
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Completed</p>
                  <p className="text-2xl font-bold">{completedPhases}</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-amber-100">
                  <TrendingUp className="h-5 w-5 text-amber-600" />
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Overall Progress</p>
                  <p className="text-2xl font-bold">{overallProgress.toFixed(0)}%</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Timeline Visual */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Timeline Overview (48 Weeks)</CardTitle>
          <CardDescription>Visual representation of phase timeline</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="relative">
            {/* Week markers */}
            <div className="flex justify-between text-xs text-muted-foreground mb-2">
              <span>Week 1</span>
              <span>Week 12</span>
              <span>Week 24</span>
              <span>Week 36</span>
              <span>Week 48</span>
            </div>
            {/* Timeline bars */}
            <div className="space-y-2">
              {phases.map((phase) => {
                const start = ((phase.start_week || 1) - 1) / 48 * 100
                const width = phase.end_week && phase.start_week
                  ? ((phase.end_week - phase.start_week + 1) / 48) * 100
                  : 10
                const status = statusConfig[phase.status] || statusConfig.pending

                return (
                  <div key={phase.id} className="relative h-8 bg-muted/30 rounded">
                    <div
                      className={`absolute h-full rounded ${status.color} flex items-center px-2`}
                      style={{ left: `${start}%`, width: `${width}%` }}
                    >
                      <span className="text-xs font-medium truncate">
                        {phase.phase_code}: {phase.name}
                      </span>
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Loading State */}
      {isLoading && (
        <Card className="p-8 flex items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <span className="ml-2">Loading phases...</span>
        </Card>
      )}

      {/* Phase Cards */}
      {!isLoading && (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {phases.map((phase) => (
            <PhaseDetailCard key={phase.id} phase={phase} />
          ))}
        </div>
      )}

      {!isLoading && phases.length === 0 && (
        <Card className="p-8 text-center">
          <Layers className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
          <p className="text-muted-foreground">No phases found</p>
          <p className="text-sm text-muted-foreground mt-1">
            Run the WBS seed script to populate phases
          </p>
        </Card>
      )}
    </div>
  )
}
