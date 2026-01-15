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
  CreditCard,
  Receipt,
  TrendingUp,
  Users,
  Zap,
  Cloud,
  Bot,
  AlertTriangle,
  CheckCircle2,
  Clock,
  IndianRupee,
  ArrowUpRight,
  ChevronRight,
  Loader2,
  RefreshCw,
  Building2,
  Calendar,
  BarChart3,
} from 'lucide-react'

// Types
interface SubscriptionDashboard {
  total_subscriptions: number
  active_subscriptions: number
  trial_subscriptions: number
  churned_subscriptions: number
  mrr: number
  arr: number
  avg_revenue_per_user: number
  total_employees_billed: number
  subscriptions_by_plan: Record<string, number>
  subscriptions_by_status: Record<string, number>
  revenue_trend: Array<{ month: string; revenue: number }>
}

interface Subscription {
  id: string
  company_id: string
  plan_id: string
  status: string
  billing_interval: string
  current_period_start: string
  current_period_end: string
  employee_count: number
  total_amount: number
  currency: string
}

interface Invoice {
  id: string
  invoice_number: string
  invoice_date: string
  due_date: string
  total_amount: number
  amount_due: number
  status: string
  customer_name: string
}

// Status configs
const statusConfig: Record<string, { color: string; icon: React.ReactNode; label: string }> = {
  trialing: { color: 'bg-blue-100 text-blue-700', icon: <Clock className="h-3.5 w-3.5" />, label: 'Trial' },
  active: { color: 'bg-green-100 text-green-700', icon: <CheckCircle2 className="h-3.5 w-3.5" />, label: 'Active' },
  past_due: { color: 'bg-yellow-100 text-yellow-700', icon: <AlertTriangle className="h-3.5 w-3.5" />, label: 'Past Due' },
  paused: { color: 'bg-slate-100 text-slate-700', icon: <Clock className="h-3.5 w-3.5" />, label: 'Paused' },
  cancelled: { color: 'bg-red-100 text-red-700', icon: <AlertTriangle className="h-3.5 w-3.5" />, label: 'Cancelled' },
  expired: { color: 'bg-gray-100 text-gray-700', icon: <Clock className="h-3.5 w-3.5" />, label: 'Expired' },
}

const invoiceStatusConfig: Record<string, { color: string; label: string }> = {
  draft: { color: 'bg-slate-100 text-slate-700', label: 'Draft' },
  pending: { color: 'bg-yellow-100 text-yellow-700', label: 'Pending' },
  paid: { color: 'bg-green-100 text-green-700', label: 'Paid' },
  partially_paid: { color: 'bg-blue-100 text-blue-700', label: 'Partial' },
  overdue: { color: 'bg-red-100 text-red-700', label: 'Overdue' },
  cancelled: { color: 'bg-gray-100 text-gray-700', label: 'Cancelled' },
}

// Format currency
function formatCurrency(amount: number, currency: string = 'INR'): string {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency,
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount)
}

// Usage Meter Component
function UsageMeter({
  label,
  used,
  limit,
  icon,
  unit = '',
}: {
  label: string
  used: number
  limit: number | null
  icon: React.ReactNode
  unit?: string
}) {
  const percent = limit ? Math.min((used / limit) * 100, 100) : 0
  const remaining = limit ? Math.max(limit - used, 0) : null

  return (
    <Card>
      <CardContent className="pt-4">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <div className="p-2 rounded-lg bg-muted">{icon}</div>
            <span className="font-medium">{label}</span>
          </div>
          <span className="text-sm text-muted-foreground">
            {used.toLocaleString()}{unit} / {limit ? `${limit.toLocaleString()}${unit}` : '∞'}
          </span>
        </div>
        <Progress value={percent} className="h-2" />
        <div className="flex justify-between mt-2 text-xs text-muted-foreground">
          <span>{percent.toFixed(0)}% used</span>
          {remaining !== null && <span>{remaining.toLocaleString()}{unit} remaining</span>}
        </div>
      </CardContent>
    </Card>
  )
}

export default function SubscriptionDashboardPage() {
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [dashboard, setDashboard] = useState<SubscriptionDashboard | null>(null)
  const [subscriptions, setSubscriptions] = useState<Subscription[]>([])
  const [invoices, setInvoices] = useState<Invoice[]>([])

  const fetchData = async () => {
    setIsLoading(true)
    setError(null)
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

      // Fetch dashboard
      const dashboardRes = await fetch(`${apiUrl}/subscriptions/dashboard`)
      if (dashboardRes.ok) {
        const data = await dashboardRes.json()
        setDashboard(data)
      }

      // Fetch recent subscriptions
      const subsRes = await fetch(`${apiUrl}/subscriptions?limit=5`)
      if (subsRes.ok) {
        const data = await subsRes.json()
        setSubscriptions(data)
      }

      // Fetch recent invoices
      const invoicesRes = await fetch(`${apiUrl}/subscriptions/invoices?limit=5`)
      if (invoicesRes.ok) {
        const data = await invoicesRes.json()
        setInvoices(data)
      }
    } catch (err) {
      console.error('Failed to fetch subscription data:', err)
      setError('Failed to load data. API may not be running.')
      // Mock data for demo
      setDashboard({
        total_subscriptions: 150,
        active_subscriptions: 125,
        trial_subscriptions: 18,
        churned_subscriptions: 7,
        mrr: 487500,
        arr: 5850000,
        avg_revenue_per_user: 3900,
        total_employees_billed: 1250,
        subscriptions_by_plan: {
          'Free': 25,
          'Starter': 45,
          'Professional': 60,
          'Enterprise': 20,
        },
        subscriptions_by_status: {
          active: 125,
          trialing: 18,
          past_due: 3,
          cancelled: 4,
        },
        revenue_trend: [
          { month: '2025-08', revenue: 420000 },
          { month: '2025-09', revenue: 445000 },
          { month: '2025-10', revenue: 462000 },
          { month: '2025-11', revenue: 475000 },
          { month: '2025-12', revenue: 480000 },
          { month: '2026-01', revenue: 487500 },
        ],
      })
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [])

  return (
    <div className="space-y-6">
      <PageHeader
        title="Subscription & Billing"
        description="Manage subscriptions, billing, and usage tracking"
        actions={
          <div className="flex gap-2">
            <Button variant="outline" onClick={fetchData} disabled={isLoading}>
              <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
            <Link href="/subscription/plans">
              <Button>
                <CreditCard className="h-4 w-4 mr-2" />
                View Plans
              </Button>
            </Link>
          </div>
        }
      />

      {/* Loading State */}
      {isLoading && (
        <Card className="p-8 flex items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <span className="ml-2">Loading subscription data...</span>
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

      {!isLoading && dashboard && (
        <>
          {/* Revenue Stats */}
          <div className="grid gap-4 md:grid-cols-4">
            <StatCard
              title="Monthly Recurring Revenue"
              value={formatCurrency(dashboard.mrr)}
              icon={<IndianRupee className="h-4 w-4" />}
              description="MRR this month"
              trend="up"
            />
            <StatCard
              title="Annual Recurring Revenue"
              value={formatCurrency(dashboard.arr)}
              icon={<TrendingUp className="h-4 w-4" />}
              description="ARR projection"
            />
            <StatCard
              title="Avg Revenue Per User"
              value={formatCurrency(dashboard.avg_revenue_per_user)}
              icon={<BarChart3 className="h-4 w-4" />}
              description="ARPU"
            />
            <StatCard
              title="Total Employees"
              value={dashboard.total_employees_billed.toLocaleString()}
              icon={<Users className="h-4 w-4" />}
              description="Billable employees"
            />
          </div>

          {/* Subscription Stats */}
          <div className="grid gap-4 md:grid-cols-4">
            <StatCard
              title="Total Subscriptions"
              value={dashboard.total_subscriptions}
              icon={<Building2 className="h-4 w-4" />}
              description="All companies"
            />
            <StatCard
              title="Active"
              value={dashboard.active_subscriptions}
              icon={<CheckCircle2 className="h-4 w-4 text-green-600" />}
              description="Paying customers"
            />
            <StatCard
              title="In Trial"
              value={dashboard.trial_subscriptions}
              icon={<Clock className="h-4 w-4 text-blue-600" />}
              description="14-day trial"
            />
            <StatCard
              title="Churned"
              value={dashboard.churned_subscriptions}
              icon={<AlertTriangle className="h-4 w-4 text-red-600" />}
              description="Cancelled/Expired"
              trend={dashboard.churned_subscriptions > 5 ? 'up' : undefined}
            />
          </div>

          {/* Main Content */}
          <Tabs defaultValue="overview" className="space-y-4">
            <TabsList>
              <TabsTrigger value="overview" className="flex items-center gap-2">
                <BarChart3 className="h-4 w-4" />
                Overview
              </TabsTrigger>
              <TabsTrigger value="usage" className="flex items-center gap-2">
                <Zap className="h-4 w-4" />
                Usage
              </TabsTrigger>
              <TabsTrigger value="invoices" className="flex items-center gap-2">
                <Receipt className="h-4 w-4" />
                Invoices
              </TabsTrigger>
            </TabsList>

            {/* Overview Tab */}
            <TabsContent value="overview" className="space-y-4">
              <div className="grid gap-6 md:grid-cols-2">
                {/* Subscriptions by Plan */}
                <Card>
                  <CardHeader>
                    <CardTitle className="text-base">Subscriptions by Plan</CardTitle>
                    <CardDescription>Distribution across pricing tiers</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    {Object.entries(dashboard.subscriptions_by_plan).map(([plan, count]) => (
                      <div key={plan} className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <Badge variant="outline">{plan}</Badge>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="text-sm font-medium">{count}</span>
                          <Progress
                            value={(count / dashboard.total_subscriptions) * 100}
                            className="w-24 h-2"
                          />
                        </div>
                      </div>
                    ))}
                  </CardContent>
                </Card>

                {/* Subscriptions by Status */}
                <Card>
                  <CardHeader>
                    <CardTitle className="text-base">Subscriptions by Status</CardTitle>
                    <CardDescription>Current subscription states</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-3">
                    {Object.entries(dashboard.subscriptions_by_status).map(([status, count]) => {
                      const config = statusConfig[status] || statusConfig.active
                      return (
                        <div key={status} className="flex items-center justify-between">
                          <Badge className={config.color}>
                            {config.icon}
                            <span className="ml-1">{config.label}</span>
                          </Badge>
                          <span className="text-sm font-medium">{count}</span>
                        </div>
                      )
                    })}
                  </CardContent>
                </Card>

                {/* Revenue Trend */}
                <Card className="md:col-span-2">
                  <CardHeader>
                    <CardTitle className="text-base">Revenue Trend</CardTitle>
                    <CardDescription>Monthly recurring revenue over time</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="flex items-end gap-2 h-32">
                      {dashboard.revenue_trend.map((item, index) => {
                        const maxRevenue = Math.max(...dashboard.revenue_trend.map(r => r.revenue))
                        const height = (item.revenue / maxRevenue) * 100
                        return (
                          <div key={item.month} className="flex-1 flex flex-col items-center gap-1">
                            <div
                              className="w-full bg-primary rounded-t transition-all hover:bg-primary/80"
                              style={{ height: `${height}%` }}
                              title={formatCurrency(item.revenue)}
                            />
                            <span className="text-xs text-muted-foreground">
                              {item.month.split('-')[1]}
                            </span>
                          </div>
                        )
                      })}
                    </div>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>

            {/* Usage Tab */}
            <TabsContent value="usage" className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold">Platform Usage Metrics</h3>
                <Link href="/subscription/usage">
                  <Button variant="outline" size="sm">
                    View Details
                    <ChevronRight className="h-4 w-4 ml-1" />
                  </Button>
                </Link>
              </div>
              <div className="grid gap-4 md:grid-cols-3">
                <UsageMeter
                  label="API Calls"
                  used={8500}
                  limit={10000}
                  icon={<Zap className="h-4 w-4" />}
                  unit=""
                />
                <UsageMeter
                  label="AI Queries"
                  used={75}
                  limit={100}
                  icon={<Bot className="h-4 w-4" />}
                  unit=""
                />
                <UsageMeter
                  label="Storage"
                  used={6.5}
                  limit={10}
                  icon={<Cloud className="h-4 w-4" />}
                  unit=" GB"
                />
              </div>
            </TabsContent>

            {/* Invoices Tab */}
            <TabsContent value="invoices" className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold">Recent Invoices</h3>
                <Link href="/subscription/invoices">
                  <Button variant="outline" size="sm">
                    View All Invoices
                    <ChevronRight className="h-4 w-4 ml-1" />
                  </Button>
                </Link>
              </div>
              <Card>
                <CardContent className="pt-4">
                  {invoices.length > 0 ? (
                    <div className="space-y-3">
                      {invoices.map((invoice) => {
                        const status = invoiceStatusConfig[invoice.status] || invoiceStatusConfig.pending
                        return (
                          <div
                            key={invoice.id}
                            className="flex items-center justify-between p-3 border rounded-lg hover:bg-muted/50"
                          >
                            <div className="flex items-center gap-3">
                              <Receipt className="h-5 w-5 text-muted-foreground" />
                              <div>
                                <p className="font-medium">{invoice.invoice_number}</p>
                                <p className="text-xs text-muted-foreground">
                                  {invoice.customer_name}
                                </p>
                              </div>
                            </div>
                            <div className="flex items-center gap-3">
                              <div className="text-right">
                                <p className="font-medium">{formatCurrency(invoice.total_amount)}</p>
                                <p className="text-xs text-muted-foreground">
                                  Due: {new Date(invoice.due_date).toLocaleDateString()}
                                </p>
                              </div>
                              <Badge className={status.color}>{status.label}</Badge>
                            </div>
                          </div>
                        )
                      })}
                    </div>
                  ) : (
                    <p className="text-center text-muted-foreground py-8">
                      No invoices yet
                    </p>
                  )}
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>

          {/* Quick Actions */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Quick Actions</CardTitle>
              <CardDescription>Navigate to billing features</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-3 md:grid-cols-4">
                <Link href="/subscription/plans">
                  <Button variant="outline" className="w-full justify-start">
                    <CreditCard className="h-4 w-4 mr-2" />
                    Subscription Plans
                  </Button>
                </Link>
                <Link href="/subscription/invoices">
                  <Button variant="outline" className="w-full justify-start">
                    <Receipt className="h-4 w-4 mr-2" />
                    Invoices
                  </Button>
                </Link>
                <Link href="/subscription/usage">
                  <Button variant="outline" className="w-full justify-start">
                    <Zap className="h-4 w-4 mr-2" />
                    Usage Tracking
                  </Button>
                </Link>
                <Link href="/settings/company">
                  <Button variant="outline" className="w-full justify-start">
                    <Building2 className="h-4 w-4 mr-2" />
                    Company Settings
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
