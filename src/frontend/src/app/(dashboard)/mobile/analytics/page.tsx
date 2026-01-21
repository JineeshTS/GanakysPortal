'use client'

import { useState, useEffect, useCallback } from 'react'
import Link from 'next/link'
import { PageHeader } from '@/components/layout/page-header'
import { useAuth } from "@/hooks/use-auth"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Progress } from '@/components/ui/progress'
import {
  ChevronLeft,
  RefreshCw,
  Loader2,
  BarChart3,
  TrendingUp,
  TrendingDown,
  Users,
  Smartphone,
  Clock,
  Activity,
  Download,
  Eye,
  MousePointer,
  Timer,
  Zap,
  ArrowUpRight,
  ArrowDownRight,
} from 'lucide-react'

interface AnalyticsData {
  daily_active_users: number
  weekly_active_users: number
  monthly_active_users: number
  total_sessions: number
  avg_session_duration_mins: number
  screens_per_session: number
  crash_free_rate: number
  app_opens_today: number
  new_users_today: number
  retention_rate_7d: number
  retention_rate_30d: number
  top_features: { name: string; usage: number }[]
  device_breakdown: { platform: string; count: number; percentage: number }[]
  hourly_usage: { hour: number; users: number }[]
}

function StatCard({
  title,
  value,
  change,
  changeLabel,
  icon,
  iconColor,
}: {
  title: string
  value: string | number
  change?: number
  changeLabel?: string
  icon: React.ReactNode
  iconColor: string
}) {
  const isPositive = change && change > 0

  return (
    <Card>
      <CardContent className="pt-4">
        <div className="flex items-start justify-between">
          <div>
            <p className="text-sm text-muted-foreground">{title}</p>
            <p className="text-2xl font-bold mt-1">{value}</p>
            {change !== undefined && (
              <div className={`flex items-center gap-1 mt-1 text-xs ${isPositive ? 'text-green-600' : 'text-red-600'}`}>
                {isPositive ? <ArrowUpRight className="h-3 w-3" /> : <ArrowDownRight className="h-3 w-3" />}
                <span>{Math.abs(change)}% {changeLabel || 'vs last period'}</span>
              </div>
            )}
          </div>
          <div className={`p-2 rounded-lg ${iconColor}`}>
            {icon}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

export default function MobileAnalyticsPage() {
  const [isLoading, setIsLoading] = useState(true)
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null)
  const [period, setPeriod] = useState<string>('7d')

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || '/api/v1'

  const fetchAnalytics = useCallback(async () => {
    setIsLoading(true)
    try {
      const res = await fetchWithAuth(`${apiUrl}/mobile/analytics?period=${period}`)
      if (res.ok) {
        const data = await res.json()
        setAnalytics(data)
      }
    } catch (err) {
      console.error('Failed to fetch analytics:', err)
    } finally {
      setIsLoading(false)
    }
  }, [apiUrl, period])

  useEffect(() => {
    fetchAnalytics()
  }, [fetchAnalytics])

  // Mock data
  const mockAnalytics: AnalyticsData = {
    daily_active_users: 142,
    weekly_active_users: 856,
    monthly_active_users: 2340,
    total_sessions: 4520,
    avg_session_duration_mins: 8.5,
    screens_per_session: 12.3,
    crash_free_rate: 99.2,
    app_opens_today: 312,
    new_users_today: 8,
    retention_rate_7d: 72.5,
    retention_rate_30d: 45.8,
    top_features: [
      { name: 'Attendance', usage: 89 },
      { name: 'Leave Request', usage: 76 },
      { name: 'Expenses', usage: 68 },
      { name: 'Approvals', usage: 54 },
      { name: 'Notifications', usage: 48 },
      { name: 'Profile', usage: 35 },
    ],
    device_breakdown: [
      { platform: 'Android', count: 1520, percentage: 65 },
      { platform: 'iOS', count: 820, percentage: 35 },
    ],
    hourly_usage: [
      { hour: 6, users: 12 }, { hour: 7, users: 28 }, { hour: 8, users: 85 }, { hour: 9, users: 120 },
      { hour: 10, users: 95 }, { hour: 11, users: 88 }, { hour: 12, users: 45 }, { hour: 13, users: 52 },
      { hour: 14, users: 78 }, { hour: 15, users: 82 }, { hour: 16, users: 76 }, { hour: 17, users: 92 },
      { hour: 18, users: 68 }, { hour: 19, users: 35 }, { hour: 20, users: 22 }, { hour: 21, users: 15 },
    ],
  }

  const data = analytics || mockAnalytics
  const maxHourlyUsage = Math.max(...data.hourly_usage.map(h => h.users))

  return (
    <div className="space-y-6">
      <PageHeader
        title="Mobile Analytics"
        description="Usage statistics and app performance metrics"
        actions={
          <div className="flex gap-2">
            <Link href="/mobile">
              <Button variant="outline">
                <ChevronLeft className="h-4 w-4 mr-1" />
                Back
              </Button>
            </Link>
            <Select value={period} onValueChange={setPeriod}>
              <SelectTrigger className="w-[120px]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="1d">Today</SelectItem>
                <SelectItem value="7d">Last 7 Days</SelectItem>
                <SelectItem value="30d">Last 30 Days</SelectItem>
                <SelectItem value="90d">Last 90 Days</SelectItem>
              </SelectContent>
            </Select>
            <Button onClick={fetchAnalytics} disabled={isLoading}>
              <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
          </div>
        }
      />

      {isLoading ? (
        <Card className="p-8 flex items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <span className="ml-2">Loading analytics...</span>
        </Card>
      ) : (
        <>
          {/* Active Users */}
          <div className="grid gap-4 md:grid-cols-4">
            <StatCard
              title="Daily Active Users"
              value={data.daily_active_users}
              change={12}
              icon={Users}
              iconColor="bg-primary/10"
            />
            <StatCard
              title="Weekly Active Users"
              value={data.weekly_active_users}
              change={8}
              icon={Activity}
              iconColor="bg-blue-100"
            />
            <StatCard
              title="Monthly Active Users"
              value={data.monthly_active_users.toLocaleString()}
              change={15}
              icon={TrendingUp}
              iconColor="bg-green-100"
            />
            <StatCard
              title="New Users Today"
              value={data.new_users_today}
              change={-5}
              icon={Users}
              iconColor="bg-purple-100"
            />
          </div>

          {/* Engagement Metrics */}
          <div className="grid gap-4 md:grid-cols-4">
            <StatCard
              title="Total Sessions"
              value={data.total_sessions.toLocaleString()}
              change={18}
              icon={MousePointer}
              iconColor="bg-orange-100"
            />
            <StatCard
              title="Avg Session Duration"
              value={`${data.avg_session_duration_mins}m`}
              change={5}
              icon={Timer}
              iconColor="bg-teal-100"
            />
            <StatCard
              title="Screens Per Session"
              value={data.screens_per_session}
              change={3}
              icon={Eye}
              iconColor="bg-indigo-100"
            />
            <StatCard
              title="App Opens Today"
              value={data.app_opens_today}
              change={22}
              icon={Zap}
              iconColor="bg-yellow-100"
            />
          </div>

          <div className="grid gap-6 md:grid-cols-2">
            {/* Top Features */}
            <Card>
              <CardHeader>
                <CardTitle className="text-base flex items-center gap-2">
                  <BarChart3 className="h-5 w-5" />
                  Top Features
                </CardTitle>
                <CardDescription>Most used app features</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {data.top_features.map((feature, index) => (
                  <div key={feature.name} className="space-y-1">
                    <div className="flex items-center justify-between text-sm">
                      <span className="font-medium">{feature.name}</span>
                      <span className="text-muted-foreground">{feature.usage}%</span>
                    </div>
                    <Progress value={feature.usage} className="h-2" />
                  </div>
                ))}
              </CardContent>
            </Card>

            {/* Device Breakdown */}
            <Card>
              <CardHeader>
                <CardTitle className="text-base flex items-center gap-2">
                  <Smartphone className="h-5 w-5" />
                  Device Breakdown
                </CardTitle>
                <CardDescription>Users by platform</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                {data.device_breakdown.map((device) => (
                  <div key={device.platform} className="space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <div className={`w-3 h-3 rounded-full ${device.platform === 'Android' ? 'bg-green-500' : 'bg-blue-500'}`} />
                        <span className="font-medium">{device.platform}</span>
                      </div>
                      <div className="text-sm">
                        <span className="font-medium">{device.count.toLocaleString()}</span>
                        <span className="text-muted-foreground ml-1">({device.percentage}%)</span>
                      </div>
                    </div>
                    <Progress value={device.percentage} className="h-3" />
                  </div>
                ))}
              </CardContent>
            </Card>

            {/* Retention */}
            <Card>
              <CardHeader>
                <CardTitle className="text-base flex items-center gap-2">
                  <TrendingUp className="h-5 w-5" />
                  Retention Rates
                </CardTitle>
                <CardDescription>User retention over time</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-6">
                  <div className="text-center p-4 rounded-lg bg-green-50 border border-green-200">
                    <p className="text-3xl font-bold text-green-700">{data.retention_rate_7d}%</p>
                    <p className="text-sm text-green-600 mt-1">7-Day Retention</p>
                  </div>
                  <div className="text-center p-4 rounded-lg bg-blue-50 border border-blue-200">
                    <p className="text-3xl font-bold text-blue-700">{data.retention_rate_30d}%</p>
                    <p className="text-sm text-blue-600 mt-1">30-Day Retention</p>
                  </div>
                </div>
                <div className="mt-4 p-4 rounded-lg bg-purple-50 border border-purple-200">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-purple-700">Crash-Free Rate</span>
                    <span className="text-lg font-bold text-purple-800">{data.crash_free_rate}%</span>
                  </div>
                  <Progress value={data.crash_free_rate} className="h-2 mt-2" />
                </div>
              </CardContent>
            </Card>

            {/* Hourly Usage */}
            <Card>
              <CardHeader>
                <CardTitle className="text-base flex items-center gap-2">
                  <Clock className="h-5 w-5" />
                  Hourly Usage Pattern
                </CardTitle>
                <CardDescription>Active users by hour of day</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex items-end gap-1 h-32">
                  {data.hourly_usage.map((item) => (
                    <div key={item.hour} className="flex-1 flex flex-col items-center">
                      <div
                        className="w-full bg-primary/80 rounded-t hover:bg-primary transition-colors"
                        style={{ height: `${(item.users / maxHourlyUsage) * 100}%` }}
                        title={`${item.hour}:00 - ${item.users} users`}
                      />
                    </div>
                  ))}
                </div>
                <div className="flex justify-between mt-2 text-xs text-muted-foreground">
                  <span>6AM</span>
                  <span>12PM</span>
                  <span>6PM</span>
                  <span>9PM</span>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Export */}
          <Card>
            <CardContent className="pt-4 flex items-center justify-between">
              <div>
                <p className="font-medium">Export Analytics Report</p>
                <p className="text-sm text-muted-foreground">Download detailed analytics data as CSV or PDF</p>
              </div>
              <div className="flex gap-2">
                <Button variant="outline">
                  <Download className="h-4 w-4 mr-2" />
                  CSV
                </Button>
                <Button variant="outline">
                  <Download className="h-4 w-4 mr-2" />
                  PDF
                </Button>
              </div>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  )
}
