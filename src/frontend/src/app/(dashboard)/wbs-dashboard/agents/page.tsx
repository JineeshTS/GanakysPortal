'use client'

import { useState, useEffect, useCallback } from 'react'
import { PageHeader } from '@/components/layout/page-header'
import { useAuth } from '@/hooks/use-auth'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import Link from 'next/link'
import {
  Bot,
  ChevronLeft,
  Cpu,
  ListTodo,
  CheckCircle2,
  PlayCircle,
  Clock,
  AlertCircle,
  Loader2,
  RefreshCw,
  Code,
  Database,
  Server,
  Layout,
  TestTube,
  FileText,
  Plug,
  Sparkles,
  Target,
} from 'lucide-react'

// Types
interface WBSAgentConfig {
  id: string
  agent_code: string
  name: string
  description: string | null
  purpose: string | null
  triggers: string[]
  output_types: string[]
  system_prompt: string | null
  pattern_files: string[]
  is_active: boolean
  created_at: string
  updated_at: string
}

interface AgentStats {
  total_tasks: number
  pending: number
  in_progress: number
  completed: number
  failed: number
}

// Agent icon mapping
const agentIcons: Record<string, React.ReactNode> = {
  'DB-AGENT': <Database className="h-6 w-6" />,
  'API-AGENT': <Server className="h-6 w-6" />,
  'SVC-AGENT': <Cpu className="h-6 w-6" />,
  'PAGE-AGENT': <Layout className="h-6 w-6" />,
  'COMP-AGENT': <Code className="h-6 w-6" />,
  'TEST-AGENT': <TestTube className="h-6 w-6" />,
  'DOC-AGENT': <FileText className="h-6 w-6" />,
  'INT-AGENT': <Plug className="h-6 w-6" />,
  'AI-AGENT': <Sparkles className="h-6 w-6" />,
}

const agentColors: Record<string, { bg: string; text: string; border: string }> = {
  'DB-AGENT': { bg: 'bg-amber-50', text: 'text-amber-700', border: 'border-amber-200' },
  'API-AGENT': { bg: 'bg-blue-50', text: 'text-blue-700', border: 'border-blue-200' },
  'SVC-AGENT': { bg: 'bg-purple-50', text: 'text-purple-700', border: 'border-purple-200' },
  'PAGE-AGENT': { bg: 'bg-green-50', text: 'text-green-700', border: 'border-green-200' },
  'COMP-AGENT': { bg: 'bg-pink-50', text: 'text-pink-700', border: 'border-pink-200' },
  'TEST-AGENT': { bg: 'bg-cyan-50', text: 'text-cyan-700', border: 'border-cyan-200' },
  'DOC-AGENT': { bg: 'bg-slate-50', text: 'text-slate-700', border: 'border-slate-200' },
  'INT-AGENT': { bg: 'bg-orange-50', text: 'text-orange-700', border: 'border-orange-200' },
  'AI-AGENT': { bg: 'bg-violet-50', text: 'text-violet-700', border: 'border-violet-200' },
}

// Agent Card Component
function AgentCard({ agent, stats }: { agent: WBSAgentConfig; stats?: AgentStats }) {
  const colors = agentColors[agent.agent_code] || agentColors['SVC-AGENT']
  const icon = agentIcons[agent.agent_code] || <Bot className="h-6 w-6" />

  return (
    <Card className={`border-2 ${colors.border} ${colors.bg}`}>
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            <div className={`p-3 rounded-xl ${colors.bg} ${colors.text} border ${colors.border}`}>
              {icon}
            </div>
            <div>
              <Badge variant="outline" className="text-xs font-mono mb-1">
                {agent.agent_code}
              </Badge>
              <CardTitle className="text-base">{agent.name}</CardTitle>
            </div>
          </div>
          <Badge className={agent.is_active ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}>
            {agent.is_active ? 'Active' : 'Inactive'}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {agent.description && (
          <p className="text-sm text-muted-foreground">{agent.description}</p>
        )}

        {/* Purpose */}
        {agent.purpose && (
          <div>
            <p className="text-xs font-medium text-muted-foreground mb-1">Purpose</p>
            <p className="text-sm">{agent.purpose}</p>
          </div>
        )}

        {/* Triggers */}
        {(agent.triggers?.length || 0) > 0 && (
          <div>
            <p className="text-xs font-medium text-muted-foreground mb-2">Triggers</p>
            <div className="flex flex-wrap gap-1">
              {agent.triggers?.slice(0, 4).map((trigger, i) => (
                <Badge key={i} variant="outline" className="text-xs">
                  {trigger}
                </Badge>
              ))}
              {(agent.triggers?.length || 0) > 4 && (
                <Badge variant="outline" className="text-xs">
                  +{(agent.triggers?.length || 0) - 4} more
                </Badge>
              )}
            </div>
          </div>
        )}

        {/* Output Types */}
        {(agent.output_types?.length || 0) > 0 && (
          <div>
            <p className="text-xs font-medium text-muted-foreground mb-2">Outputs</p>
            <div className="flex flex-wrap gap-1">
              {agent.output_types?.map((output, i) => (
                <Badge key={i} variant="secondary" className="text-xs">
                  {output}
                </Badge>
              ))}
            </div>
          </div>
        )}

        {/* Task Stats */}
        {stats && (
          <div className="grid grid-cols-4 gap-2 pt-2">
            <div className="text-center p-2 bg-background rounded">
              <p className="text-lg font-bold">{stats.total_tasks}</p>
              <p className="text-xs text-muted-foreground">Total</p>
            </div>
            <div className="text-center p-2 bg-background rounded">
              <p className="text-lg font-bold text-blue-600">{stats.in_progress}</p>
              <p className="text-xs text-muted-foreground">Active</p>
            </div>
            <div className="text-center p-2 bg-background rounded">
              <p className="text-lg font-bold text-green-600">{stats.completed}</p>
              <p className="text-xs text-muted-foreground">Done</p>
            </div>
            <div className="text-center p-2 bg-background rounded">
              <p className="text-lg font-bold text-slate-600">{stats.pending}</p>
              <p className="text-xs text-muted-foreground">Pending</p>
            </div>
          </div>
        )}

        {/* View Tasks Button */}
        <Link href={`/wbs-dashboard/tasks?agent=${agent.agent_code}`}>
          <Button variant="outline" className="w-full mt-2">
            <ListTodo className="h-4 w-4 mr-2" />
            View Agent Tasks
          </Button>
        </Link>
      </CardContent>
    </Card>
  )
}

// Agent Workflow Diagram
function AgentWorkflowDiagram() {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Agent Handoff Chain</CardTitle>
        <CardDescription>Feature implementation flow between specialized agents</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="relative overflow-x-auto">
          <div className="flex items-center justify-center gap-2 min-w-[800px] py-4">
            {/* DB Agent */}
            <div className="flex flex-col items-center">
              <div className="p-3 rounded-xl bg-amber-100 text-amber-700 border border-amber-200">
                <Database className="h-6 w-6" />
              </div>
              <p className="text-xs mt-1 font-medium">DB-AGENT</p>
              <p className="text-xs text-muted-foreground">Models</p>
            </div>

            <div className="text-muted-foreground">→</div>

            {/* API Agent */}
            <div className="flex flex-col items-center">
              <div className="p-3 rounded-xl bg-blue-100 text-blue-700 border border-blue-200">
                <Server className="h-6 w-6" />
              </div>
              <p className="text-xs mt-1 font-medium">API-AGENT</p>
              <p className="text-xs text-muted-foreground">Endpoints</p>
            </div>

            <div className="text-muted-foreground">→</div>

            {/* Service Agent */}
            <div className="flex flex-col items-center">
              <div className="p-3 rounded-xl bg-purple-100 text-purple-700 border border-purple-200">
                <Cpu className="h-6 w-6" />
              </div>
              <p className="text-xs mt-1 font-medium">SVC-AGENT</p>
              <p className="text-xs text-muted-foreground">Logic</p>
            </div>

            <div className="text-muted-foreground">→</div>

            {/* Page Agent */}
            <div className="flex flex-col items-center">
              <div className="p-3 rounded-xl bg-green-100 text-green-700 border border-green-200">
                <Layout className="h-6 w-6" />
              </div>
              <p className="text-xs mt-1 font-medium">PAGE-AGENT</p>
              <p className="text-xs text-muted-foreground">Pages</p>
            </div>

            <div className="text-muted-foreground">→</div>

            {/* Component Agent */}
            <div className="flex flex-col items-center">
              <div className="p-3 rounded-xl bg-pink-100 text-pink-700 border border-pink-200">
                <Code className="h-6 w-6" />
              </div>
              <p className="text-xs mt-1 font-medium">COMP-AGENT</p>
              <p className="text-xs text-muted-foreground">Components</p>
            </div>

            <div className="text-muted-foreground">→</div>

            {/* Test Agent */}
            <div className="flex flex-col items-center">
              <div className="p-3 rounded-xl bg-cyan-100 text-cyan-700 border border-cyan-200">
                <TestTube className="h-6 w-6" />
              </div>
              <p className="text-xs mt-1 font-medium">TEST-AGENT</p>
              <p className="text-xs text-muted-foreground">Tests</p>
            </div>

            <div className="text-muted-foreground">→</div>

            {/* Doc Agent */}
            <div className="flex flex-col items-center">
              <div className="p-3 rounded-xl bg-slate-100 text-slate-700 border border-slate-200">
                <FileText className="h-6 w-6" />
              </div>
              <p className="text-xs mt-1 font-medium">DOC-AGENT</p>
              <p className="text-xs text-muted-foreground">Docs</p>
            </div>
          </div>

          {/* Supporting Agents */}
          <div className="flex items-center justify-center gap-8 mt-4 pt-4 border-t">
            <div className="flex flex-col items-center">
              <div className="p-2 rounded-lg bg-orange-100 text-orange-700 border border-orange-200">
                <Plug className="h-5 w-5" />
              </div>
              <p className="text-xs mt-1 font-medium">INT-AGENT</p>
              <p className="text-xs text-muted-foreground">Integrations</p>
            </div>

            <div className="flex flex-col items-center">
              <div className="p-2 rounded-lg bg-violet-100 text-violet-700 border border-violet-200">
                <Sparkles className="h-5 w-5" />
              </div>
              <p className="text-xs mt-1 font-medium">AI-AGENT</p>
              <p className="text-xs text-muted-foreground">AI Features</p>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

export default function WBSAgentsPage() {
  const [isLoading, setIsLoading] = useState(true)
  const [agents, setAgents] = useState<WBSAgentConfig[]>([])
  const [taskStats, setTaskStats] = useState<Record<string, AgentStats>>({})
  const { fetchWithAuth } = useAuth()

  const fetchData = useCallback(async () => {
    setIsLoading(true)
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || '/api/v1'

      // Fetch agent configs
      const agentsRes = await fetchWithAuth(`${apiUrl}/wbs/agents`)
      if (agentsRes.ok) {
        const agentsData = await agentsRes.json()
        setAgents(agentsData)
      }

      // Fetch dashboard for task stats per agent
      const dashboardRes = await fetchWithAuth(`${apiUrl}/wbs/dashboard`)
      if (dashboardRes.ok) {
        const dashboardData = await dashboardRes.json()
        // Convert tasks_by_agent to stats object
        const stats: Record<string, AgentStats> = {}
        if (dashboardData.tasks_by_agent) {
          Object.entries(dashboardData.tasks_by_agent).forEach(([agent, count]) => {
            stats[agent] = {
              total_tasks: count as number,
              pending: 0,
              in_progress: 0,
              completed: 0,
              failed: 0,
            }
          })
        }
        setTaskStats(stats)
      }
    } catch (err) {
      console.error('Failed to fetch agents:', err)
    } finally {
      setIsLoading(false)
    }
  }, [fetchWithAuth])

  useEffect(() => {
    fetchData()
  }, [fetchData])

  // Calculate stats
  const totalAgents = agents.length
  const activeAgents = agents.filter(a => a.is_active).length

  return (
    <div className="space-y-6">
      <PageHeader
        title="Agent Framework"
        description="9 specialized Claude agents for precise task execution"
        actions={
          <div className="flex gap-2">
            <Link href="/wbs-dashboard">
              <Button variant="outline">
                <ChevronLeft className="h-4 w-4 mr-1" />
                Dashboard
              </Button>
            </Link>
            <Button variant="outline" onClick={fetchData} disabled={isLoading}>
              <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
          </div>
        }
      />

      {/* Agent Stats */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-primary/10">
                  <Bot className="h-5 w-5 text-primary" />
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Total Agents</p>
                  <p className="text-2xl font-bold">{totalAgents}</p>
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
                  <p className="text-sm text-muted-foreground">Active Agents</p>
                  <p className="text-2xl font-bold">{activeAgents}</p>
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
                  <Target className="h-5 w-5 text-blue-600" />
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Agent Types</p>
                  <p className="text-2xl font-bold">9</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Workflow Diagram */}
      <AgentWorkflowDiagram />

      {/* Loading State */}
      {isLoading && (
        <Card className="p-8 flex items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <span className="ml-2">Loading agents...</span>
        </Card>
      )}

      {/* Agent Cards */}
      {!isLoading && (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {agents.map((agent) => (
            <AgentCard
              key={agent.id}
              agent={agent}
              stats={taskStats[agent.agent_code]}
            />
          ))}
        </div>
      )}

      {!isLoading && agents.length === 0 && (
        <Card className="p-8 text-center">
          <Bot className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
          <p className="text-muted-foreground">No agent configurations found</p>
          <p className="text-sm text-muted-foreground mt-1">
            Run the WBS seed script to populate agent configurations
          </p>
        </Card>
      )}
    </div>
  )
}
