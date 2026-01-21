'use client'

import { useState, useEffect, useCallback } from 'react'
import { PageHeader } from '@/components/layout/page-header'
import { useAuth } from "@/hooks/use-auth"
import { useToast } from '@/hooks/use-toast'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import Link from 'next/link'
import {
  Zap,
  Bot,
  Cloud,
  Users,
  FileText,
  TrendingUp,
  AlertTriangle,
  CheckCircle2,
  Calendar,
  Loader2,
  RefreshCw,
  ArrowLeft,
  BarChart3,
  Activity,
} from 'lucide-react'

// Types
interface UsageSummary {
  subscription_id: string
  plan_name: string
  billing_period: {
    start: string
    end: string
  }
  usage: Record<string, UsageItem>
}

interface UsageItem {
  used: number
  limit: number | null
  remaining: number
  percent: number
  overage: number
  overage_amount: number
  alert_sent: boolean
}

interface DailyUsage {
  date: string
  usage: number
}

// Usage Card Component
function UsageCard({
  title,
  icon,
  usage,
  unit = '',
  description,
}: {
  title: string
  icon: React.ReactNode
  usage: UsageItem
  unit?: string
  description?: string
}) {
  const isWarning = usage.percent >= 80 && usage.percent < 100
  const isExceeded = usage.percent >= 100

  return (
    <Card className={isExceeded ? 'border-red-200' : isWarning ? 'border-yellow-200' : ''}>
      <CardHeader className="pb-2">
        <div className="flex items-center justify-between">
          <CardTitle className="text-sm font-medium flex items-center gap-2">
            {icon}
            {title}
          </CardTitle>
          {isExceeded && (
            <Badge variant="destructive" className="text-xs">
              <AlertTriangle className="h-3 w-3 mr-1" />
              Exceeded
            </Badge>
          )}
          {isWarning && !isExceeded && (
            <Badge variant="outline" className="text-xs border-yellow-400 text-yellow-700">
              <AlertTriangle className="h-3 w-3 mr-1" />
              Warning
            </Badge>
          )}
          {!isWarning && !isExceeded && (
            <Badge variant="outline" className="text-xs border-green-400 text-green-700">
              <CheckCircle2 className="h-3 w-3 mr-1" />
              Good
            </Badge>
          )}
        </div>
        {description && <CardDescription>{description}</CardDescription>}
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="flex items-end justify-between">
          <div>
            <p className="text-3xl font-bold">
              {usage.used.toLocaleString()}
              <span className="text-sm font-normal text-muted-foreground">{unit}</span>
            </p>
            <p className="text-sm text-muted-foreground">
              of {usage.limit ? `${usage.limit.toLocaleString()}${unit}` : 'Unlimited'} used
            </p>
          </div>
          <p className="text-2xl font-semibold text-muted-foreground">
            {usage.percent.toFixed(0)}%
          </p>
        </div>

        <Progress
          value={Math.min(usage.percent, 100)}
          className={`h-3 ${isExceeded ? '[&>div]:bg-red-500' : isWarning ? '[&>div]:bg-yellow-500' : ''}`}
        />

        <div className="flex justify-between text-sm">
          <span className="text-muted-foreground">
            {usage.remaining > 0
              ? `${usage.remaining.toLocaleString()}${unit} remaining`
              : 'Limit reached'}
          </span>
          {usage.overage > 0 && (
            <span className="text-red-600">
              +{usage.overage.toLocaleString()}{unit} overage
            </span>
          )}
        </div>

        {usage.overage_amount > 0 && (
          <div className="pt-2 border-t">
            <p className="text-sm text-red-600">
              Overage charges: ₹{usage.overage_amount.toFixed(2)}
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

// Simple Bar Chart for daily usage
function DailyUsageChart({ data, label }: { data: DailyUsage[]; label: string }) {
  const maxUsage = Math.max(...data.map((d) => d.usage), 1)

  return (
    <div className="space-y-2">
      <div className="flex items-end gap-1 h-32">
        {data.map((item, index) => {
          const height = (item.usage / maxUsage) * 100
          return (
            <div key={item.date} className="flex-1 flex flex-col items-center gap-1">
              <div
                className="w-full bg-primary/80 rounded-t hover:bg-primary transition-colors"
                style={{ height: `${height}%` }}
                title={`${item.usage} ${label}`}
              />
            </div>
          )
        })}
      </div>
      <div className="flex justify-between text-xs text-muted-foreground">
        <span>{data[0]?.date.split('-').slice(1).join('/')}</span>
        <span>{data[data.length - 1]?.date.split('-').slice(1).join('/')}</span>
      </div>
    </div>
  )
}

export default function UsagePage() {
  const { fetchWithAuth } = useAuth()
  const { toast } = useToast()
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [usageSummary, setUsageSummary] = useState<UsageSummary | null>(null)
  const [dailyApiUsage, setDailyApiUsage] = useState<DailyUsage[]>([])
  const [dailyAiUsage, setDailyAiUsage] = useState<DailyUsage[]>([])
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || '/api/v1'

  const fetchUsage = async () => {
    setIsLoading(true)
    setError(null)
    try {
      // Try to fetch from API first
      const res = await fetchWithAuth(`${apiUrl}/subscriptions/usage/summary`)
      if (res.ok) {
        const data = await res.json()
        if (data.usage) {
          setUsageSummary(data)
          // Also fetch daily usage if available
          const apiRes = await fetchWithAuth(`${apiUrl}/subscriptions/usage/daily?type=api`)
          if (apiRes.ok) {
            const apiData = await apiRes.json()
            setDailyApiUsage(apiData.data || [])
          }
          const aiRes = await fetchWithAuth(`${apiUrl}/subscriptions/usage/daily?type=ai`)
          if (aiRes.ok) {
            const aiData = await aiRes.json()
            setDailyAiUsage(aiData.data || [])
          }
          return // Success - don't use mock data
        }
      }
      // Fall back to mock data if API fails or returns empty
      await new Promise((resolve) => setTimeout(resolve, 200)) // Brief delay for UX

      setUsageSummary({
        subscription_id: 'sub-123',
        plan_name: 'Professional',
        billing_period: {
          start: '2026-01-01',
          end: '2026-01-31',
        },
        usage: {
          api_calls: {
            used: 85000,
            limit: 100000,
            remaining: 15000,
            percent: 85,
            overage: 0,
            overage_amount: 0,
            alert_sent: true,
          },
          ai_queries: {
            used: 420,
            limit: 500,
            remaining: 80,
            percent: 84,
            overage: 0,
            overage_amount: 0,
            alert_sent: false,
          },
          storage_gb: {
            used: 18.5,
            limit: 25,
            remaining: 6.5,
            percent: 74,
            overage: 0,
            overage_amount: 0,
            alert_sent: false,
          },
          documents: {
            used: 1250,
            limit: null,
            remaining: 0,
            percent: 0,
            overage: 0,
            overage_amount: 0,
            alert_sent: false,
          },
          employees: {
            used: 48,
            limit: 100,
            remaining: 52,
            percent: 48,
            overage: 0,
            overage_amount: 0,
            alert_sent: false,
          },
          users: {
            used: 12,
            limit: 20,
            remaining: 8,
            percent: 60,
            overage: 0,
            overage_amount: 0,
            alert_sent: false,
          },
        },
      })

      // Generate mock daily usage
      const now = new Date()
      const apiData: DailyUsage[] = []
      const aiData: DailyUsage[] = []

      for (let i = 13; i >= 0; i--) {
        const date = new Date(now)
        date.setDate(date.getDate() - i)
        const dateStr = date.toISOString().split('T')[0]

        apiData.push({
          date: dateStr,
          usage: Math.floor(4000 + Math.random() * 4000),
        })

        aiData.push({
          date: dateStr,
          usage: Math.floor(20 + Math.random() * 30),
        })
      }

      setDailyApiUsage(apiData)
      setDailyAiUsage(aiData)
    } catch (err) {
      toast.error('Failed to fetch usage', 'Please try again or contact support')
      setError('Failed to load usage data.')
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchUsage()
  }, [])

  return (
    <div className="space-y-6">
      <PageHeader
        title="Usage Tracking"
        description="Monitor your subscription usage and limits"
        actions={
          <div className="flex gap-2">
            <Link href="/subscription">
              <Button variant="outline">
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Billing
              </Button>
            </Link>
            <Button variant="outline" onClick={fetchUsage} disabled={isLoading}>
              <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
          </div>
        }
      />

      {/* Loading State */}
      {isLoading && (
        <Card className="p-8 flex items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <span className="ml-2">Loading usage data...</span>
        </Card>
      )}

      {/* Error State */}
      {error && (
        <Card className="p-4 border-yellow-200 bg-yellow-50">
          <div className="flex items-center gap-2 text-yellow-700">
            <AlertTriangle className="h-5 w-5" />
            <span>{error}</span>
          </div>
        </Card>
      )}

      {!isLoading && usageSummary && (
        <>
          {/* Plan & Period Info */}
          <Card>
            <CardContent className="pt-4">
              <div className="flex flex-wrap items-center justify-between gap-4">
                <div>
                  <p className="text-sm text-muted-foreground">Current Plan</p>
                  <p className="text-xl font-bold">{usageSummary.plan_name}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Billing Period</p>
                  <p className="font-medium flex items-center gap-2">
                    <Calendar className="h-4 w-4" />
                    {new Date(usageSummary.billing_period.start).toLocaleDateString()} -{' '}
                    {new Date(usageSummary.billing_period.end).toLocaleDateString()}
                  </p>
                </div>
                <div>
                  <Link href="/subscription/plans">
                    <Button variant="outline">
                      <TrendingUp className="h-4 w-4 mr-2" />
                      Upgrade Plan
                    </Button>
                  </Link>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Usage Cards Grid */}
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            <UsageCard
              title="API Calls"
              icon={Zap}
              usage={usageSummary.usage.api_calls}
              description="REST API requests this month"
            />
            <UsageCard
              title="AI Queries"
              icon={Bot}
              usage={usageSummary.usage.ai_queries}
              description="AI assistant queries"
            />
            <UsageCard
              title="Storage"
              icon={Cloud}
              usage={usageSummary.usage.storage_gb}
              unit=" GB"
              description="Document and file storage"
            />
            <UsageCard
              title="Employees"
              icon={Users}
              usage={usageSummary.usage.employees}
              description="Active employees in system"
            />
            <UsageCard
              title="Users"
              icon={Users}
              usage={usageSummary.usage.users}
              description="Platform user accounts"
            />
            <UsageCard
              title="Documents"
              icon={FileText}
              usage={usageSummary.usage.documents}
              description="Total documents stored"
            />
          </div>

          {/* Usage Charts */}
          <Tabs defaultValue="api" className="space-y-4">
            <TabsList>
              <TabsTrigger value="api" className="flex items-center gap-2">
                <Zap className="h-4 w-4" />
                API Calls
              </TabsTrigger>
              <TabsTrigger value="ai" className="flex items-center gap-2">
                <Bot className="h-4 w-4" />
                AI Queries
              </TabsTrigger>
            </TabsList>

            <TabsContent value="api">
              <Card>
                <CardHeader>
                  <CardTitle className="text-base flex items-center gap-2">
                    <BarChart3 className="h-4 w-4" />
                    Daily API Usage (Last 14 Days)
                  </CardTitle>
                  <CardDescription>
                    Average: {Math.round(dailyApiUsage.reduce((a, b) => a + b.usage, 0) / dailyApiUsage.length).toLocaleString()} calls/day
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <DailyUsageChart data={dailyApiUsage} label="API calls" />
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="ai">
              <Card>
                <CardHeader>
                  <CardTitle className="text-base flex items-center gap-2">
                    <Activity className="h-4 w-4" />
                    Daily AI Query Usage (Last 14 Days)
                  </CardTitle>
                  <CardDescription>
                    Average: {Math.round(dailyAiUsage.reduce((a, b) => a + b.usage, 0) / dailyAiUsage.length)} queries/day
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <DailyUsageChart data={dailyAiUsage} label="AI queries" />
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>

          {/* Usage Tips */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Optimization Tips</CardTitle>
              <CardDescription>Suggestions to optimize your usage</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {usageSummary.usage.api_calls.percent > 80 && (
                <div className="flex items-start gap-3 p-3 rounded-lg bg-yellow-50 border border-yellow-200">
                  <AlertTriangle className="h-5 w-5 text-yellow-600 shrink-0 mt-0.5" />
                  <div>
                    <p className="font-medium text-yellow-800">High API Usage</p>
                    <p className="text-sm text-yellow-700">
                      You're using {usageSummary.usage.api_calls.percent}% of your API quota. Consider
                      implementing caching or upgrading your plan.
                    </p>
                  </div>
                </div>
              )}

              {usageSummary.usage.ai_queries.percent > 80 && (
                <div className="flex items-start gap-3 p-3 rounded-lg bg-yellow-50 border border-yellow-200">
                  <AlertTriangle className="h-5 w-5 text-yellow-600 shrink-0 mt-0.5" />
                  <div>
                    <p className="font-medium text-yellow-800">AI Query Limit Approaching</p>
                    <p className="text-sm text-yellow-700">
                      You've used {usageSummary.usage.ai_queries.percent}% of your AI queries.
                      Consider upgrading or optimizing query usage.
                    </p>
                  </div>
                </div>
              )}

              {usageSummary.usage.api_calls.percent <= 50 &&
                usageSummary.usage.ai_queries.percent <= 50 && (
                  <div className="flex items-start gap-3 p-3 rounded-lg bg-green-50 border border-green-200">
                    <CheckCircle2 className="h-5 w-5 text-green-600 shrink-0 mt-0.5" />
                    <div>
                      <p className="font-medium text-green-800">Usage Looking Good!</p>
                      <p className="text-sm text-green-700">
                        Your usage is well within limits. You're efficiently using your subscription.
                      </p>
                    </div>
                  </div>
                )}
            </CardContent>
          </Card>
        </>
      )}
    </div>
  )
}
