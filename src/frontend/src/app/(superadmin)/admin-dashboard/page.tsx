'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import {
  Building2,
  Users,
  DollarSign,
  TrendingUp,
  TrendingDown,
  Activity,
  Zap,
  Bot,
  Cloud,
  HeadphonesIcon,
  AlertTriangle,
  CheckCircle2,
  Clock,
  ArrowUpRight,
  ArrowDownRight,
  RefreshCw,
  BarChart3,
  Flag,
  Megaphone,
} from 'lucide-react'

// Types
interface DashboardStats {
  total_tenants: number
  active_tenants: number
  new_tenants_30d: number
  churn_rate: number
  total_users: number
  active_users_30d: number
  total_employees: number
  mrr: number
  arr: number
  mrr_growth: number
  total_revenue_mtd: number
  avg_revenue_per_tenant: number
  api_calls_today: number
  ai_queries_today: number
  storage_used_total_gb: number
  open_tickets: number
  avg_resolution_time_hours: number | null
  uptime_30d: number
  error_rate_24h: number
}

interface TenantHealthDistribution {
  healthy: number
  at_risk: number
  critical: number
}

// Stat Card Component
function StatCard({
  title,
  value,
  change,
  changeType = 'neutral',
  icon: Icon,
  suffix = '',
  prefix = '',
  description,
}: {
  title: string
  value: string | number
  change?: string
  changeType?: 'up' | 'down' | 'neutral'
  icon: React.ElementType
  suffix?: string
  prefix?: string
  description?: string
}) {
  return (
    <Card>
      <CardContent className="pt-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-muted-foreground">{title}</p>
            <p className="text-2xl font-bold mt-1">
              {prefix}
              {typeof value === 'number' ? value.toLocaleString() : value}
              {suffix}
            </p>
            {change && (
              <div className="flex items-center gap-1 mt-1">
                {changeType === 'up' && <ArrowUpRight className="h-4 w-4 text-green-500" />}
                {changeType === 'down' && <ArrowDownRight className="h-4 w-4 text-red-500" />}
                <span
                  className={`text-sm ${
                    changeType === 'up'
                      ? 'text-green-500'
                      : changeType === 'down'
                      ? 'text-red-500'
                      : 'text-muted-foreground'
                  }`}
                >
                  {change}
                </span>
              </div>
            )}
            {description && (
              <p className="text-xs text-muted-foreground mt-1">{description}</p>
            )}
          </div>
          <div className="p-3 bg-primary/10 rounded-lg">
            <Icon className="h-6 w-6 text-primary" />
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

// Health Distribution Card
function TenantHealthCard({ distribution }: { distribution: TenantHealthDistribution }) {
  const total = distribution.healthy + distribution.at_risk + distribution.critical
  const healthyPercent = total > 0 ? (distribution.healthy / total) * 100 : 0
  const atRiskPercent = total > 0 ? (distribution.at_risk / total) * 100 : 0
  const criticalPercent = total > 0 ? (distribution.critical / total) * 100 : 0

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-base">Tenant Health Distribution</CardTitle>
        <CardDescription>Active tenant health status breakdown</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm">
            <div className="flex items-center gap-2">
              <CheckCircle2 className="h-4 w-4 text-green-500" />
              <span>Healthy</span>
            </div>
            <span className="font-medium">{distribution.healthy}</span>
          </div>
          <Progress value={healthyPercent} className="h-2 [&>div]:bg-green-500" />
        </div>

        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm">
            <div className="flex items-center gap-2">
              <AlertTriangle className="h-4 w-4 text-yellow-500" />
              <span>At Risk</span>
            </div>
            <span className="font-medium">{distribution.at_risk}</span>
          </div>
          <Progress value={atRiskPercent} className="h-2 [&>div]:bg-yellow-500" />
        </div>

        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm">
            <div className="flex items-center gap-2">
              <AlertTriangle className="h-4 w-4 text-red-500" />
              <span>Critical</span>
            </div>
            <span className="font-medium">{distribution.critical}</span>
          </div>
          <Progress value={criticalPercent} className="h-2 [&>div]:bg-red-500" />
        </div>
      </CardContent>
    </Card>
  )
}

// Recent Activity Item
function ActivityItem({
  action,
  tenant,
  time,
  type,
}: {
  action: string
  tenant: string
  time: string
  type: 'success' | 'warning' | 'info'
}) {
  return (
    <div className="flex items-start gap-3 py-3 border-b last:border-0">
      <div
        className={`p-1.5 rounded-full ${
          type === 'success'
            ? 'bg-green-100 text-green-600'
            : type === 'warning'
            ? 'bg-yellow-100 text-yellow-600'
            : 'bg-blue-100 text-blue-600'
        }`}
      >
        {type === 'success' ? (
          <CheckCircle2 className="h-4 w-4" />
        ) : type === 'warning' ? (
          <AlertTriangle className="h-4 w-4" />
        ) : (
          <Activity className="h-4 w-4" />
        )}
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium">{action}</p>
        <p className="text-xs text-muted-foreground">{tenant}</p>
      </div>
      <span className="text-xs text-muted-foreground whitespace-nowrap">{time}</span>
    </div>
  )
}

export default function SuperAdminDashboard() {
  const [isLoading, setIsLoading] = useState(true)
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [healthDistribution, setHealthDistribution] = useState<TenantHealthDistribution>({
    healthy: 0,
    at_risk: 0,
    critical: 0,
  })

  const fetchDashboard = async () => {
    setIsLoading(true)
    try {
      // Mock data - in production would fetch from API
      await new Promise((resolve) => setTimeout(resolve, 500))

      setStats({
        total_tenants: 156,
        active_tenants: 142,
        new_tenants_30d: 18,
        churn_rate: 2.1,
        total_users: 1842,
        active_users_30d: 1456,
        total_employees: 12450,
        mrr: 485000,
        arr: 5820000,
        mrr_growth: 8.5,
        total_revenue_mtd: 520000,
        avg_revenue_per_tenant: 3109,
        api_calls_today: 245678,
        ai_queries_today: 4521,
        storage_used_total_gb: 856.5,
        open_tickets: 12,
        avg_resolution_time_hours: 4.2,
        uptime_30d: 99.97,
        error_rate_24h: 0.02,
      })

      setHealthDistribution({
        healthy: 118,
        at_risk: 19,
        critical: 5,
      })
    } catch (err) {
      console.error('Failed to fetch dashboard:', err)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchDashboard()
  }, [])

  // Mock recent activity
  const recentActivity = [
    { action: 'New tenant signup', tenant: 'Acme Corp', time: '5 min ago', type: 'success' as const },
    { action: 'Ticket escalated', tenant: 'Tech Solutions', time: '15 min ago', type: 'warning' as const },
    { action: 'Subscription upgraded', tenant: 'Global Industries', time: '1 hour ago', type: 'info' as const },
    { action: 'Tenant suspended', tenant: 'Old Company', time: '2 hours ago', type: 'warning' as const },
    { action: 'Payment received', tenant: 'StartupXYZ', time: '3 hours ago', type: 'success' as const },
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold">Platform Dashboard</h1>
          <p className="text-muted-foreground">
            Overview of your SaaS platform performance
          </p>
        </div>
        <Button onClick={fetchDashboard} variant="outline" disabled={isLoading}>
          <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </div>

      {/* Key Metrics */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="Total Tenants"
          value={stats?.total_tenants || 0}
          change={`+${stats?.new_tenants_30d || 0} this month`}
          changeType="up"
          icon={Building2}
        />
        <StatCard
          title="Monthly Revenue (MRR)"
          value={stats?.mrr || 0}
          prefix="₹"
          change={`${stats?.mrr_growth || 0}% growth`}
          changeType="up"
          icon={DollarSign}
        />
        <StatCard
          title="Active Users"
          value={stats?.active_users_30d || 0}
          change={`of ${stats?.total_users || 0} total`}
          icon={Users}
        />
        <StatCard
          title="Open Tickets"
          value={stats?.open_tickets || 0}
          change={stats?.avg_resolution_time_hours ? `${stats.avg_resolution_time_hours}h avg resolution` : undefined}
          icon={HeadphonesIcon}
        />
      </div>

      {/* Revenue & Growth */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="Annual Revenue (ARR)"
          value={stats?.arr || 0}
          prefix="₹"
          icon={TrendingUp}
        />
        <StatCard
          title="Revenue MTD"
          value={stats?.total_revenue_mtd || 0}
          prefix="₹"
          icon={BarChart3}
        />
        <StatCard
          title="Avg Revenue/Tenant"
          value={stats?.avg_revenue_per_tenant || 0}
          prefix="₹"
          icon={DollarSign}
        />
        <StatCard
          title="Churn Rate"
          value={`${stats?.churn_rate || 0}%`}
          changeType={stats?.churn_rate && stats.churn_rate > 5 ? 'down' : 'up'}
          icon={TrendingDown}
        />
      </div>

      {/* Platform Usage & Health */}
      <div className="grid gap-4 lg:grid-cols-3">
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="text-base">Platform Usage Today</CardTitle>
            <CardDescription>Real-time usage metrics</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 sm:grid-cols-3">
              <div className="flex items-center gap-3 p-4 rounded-lg bg-muted/50">
                <div className="p-2 bg-blue-100 rounded-lg">
                  <Zap className="h-5 w-5 text-blue-600" />
                </div>
                <div>
                  <p className="text-2xl font-bold">
                    {stats?.api_calls_today?.toLocaleString() || 0}
                  </p>
                  <p className="text-sm text-muted-foreground">API Calls</p>
                </div>
              </div>

              <div className="flex items-center gap-3 p-4 rounded-lg bg-muted/50">
                <div className="p-2 bg-purple-100 rounded-lg">
                  <Bot className="h-5 w-5 text-purple-600" />
                </div>
                <div>
                  <p className="text-2xl font-bold">
                    {stats?.ai_queries_today?.toLocaleString() || 0}
                  </p>
                  <p className="text-sm text-muted-foreground">AI Queries</p>
                </div>
              </div>

              <div className="flex items-center gap-3 p-4 rounded-lg bg-muted/50">
                <div className="p-2 bg-green-100 rounded-lg">
                  <Cloud className="h-5 w-5 text-green-600" />
                </div>
                <div>
                  <p className="text-2xl font-bold">
                    {stats?.storage_used_total_gb?.toFixed(1) || 0} GB
                  </p>
                  <p className="text-sm text-muted-foreground">Storage Used</p>
                </div>
              </div>
            </div>

            {/* System Health */}
            <div className="mt-6 pt-6 border-t">
              <div className="flex items-center justify-between mb-4">
                <h4 className="font-medium">System Health</h4>
                <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">
                  Operational
                </Badge>
              </div>
              <div className="grid gap-4 sm:grid-cols-2">
                <div className="flex items-center justify-between p-3 rounded-lg border">
                  <div className="flex items-center gap-2">
                    <Activity className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm">Uptime (30d)</span>
                  </div>
                  <span className="font-medium text-green-600">
                    {stats?.uptime_30d?.toFixed(2) || 99.99}%
                  </span>
                </div>
                <div className="flex items-center justify-between p-3 rounded-lg border">
                  <div className="flex items-center gap-2">
                    <AlertTriangle className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm">Error Rate (24h)</span>
                  </div>
                  <span className="font-medium text-green-600">
                    {stats?.error_rate_24h?.toFixed(2) || 0}%
                  </span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <TenantHealthCard distribution={healthDistribution} />
      </div>

      {/* Recent Activity & Quick Actions */}
      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Recent Activity</CardTitle>
            <CardDescription>Latest platform events</CardDescription>
          </CardHeader>
          <CardContent>
            {recentActivity.map((activity, index) => (
              <ActivityItem key={index} {...activity} />
            ))}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">Quick Actions</CardTitle>
            <CardDescription>Common administrative tasks</CardDescription>
          </CardHeader>
          <CardContent className="grid gap-3">
            <Button variant="outline" className="justify-start h-auto py-3">
              <Building2 className="h-4 w-4 mr-3" />
              <div className="text-left">
                <p className="font-medium">View At-Risk Tenants</p>
                <p className="text-xs text-muted-foreground">
                  {healthDistribution.at_risk + healthDistribution.critical} tenants need attention
                </p>
              </div>
            </Button>
            <Button variant="outline" className="justify-start h-auto py-3">
              <HeadphonesIcon className="h-4 w-4 mr-3" />
              <div className="text-left">
                <p className="font-medium">Manage Support Queue</p>
                <p className="text-xs text-muted-foreground">
                  {stats?.open_tickets || 0} open tickets
                </p>
              </div>
            </Button>
            <Button variant="outline" className="justify-start h-auto py-3">
              <Flag className="h-4 w-4 mr-3" />
              <div className="text-left">
                <p className="font-medium">Feature Flag Management</p>
                <p className="text-xs text-muted-foreground">Control feature rollouts</p>
              </div>
            </Button>
            <Button variant="outline" className="justify-start h-auto py-3">
              <Megaphone className="h-4 w-4 mr-3" />
              <div className="text-left">
                <p className="font-medium">Send Announcement</p>
                <p className="text-xs text-muted-foreground">Broadcast to all tenants</p>
              </div>
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
