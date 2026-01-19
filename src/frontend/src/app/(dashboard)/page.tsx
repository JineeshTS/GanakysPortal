'use client'

import * as React from 'react'
import Link from 'next/link'
import { useAuthStore, useApi } from '@/hooks'
import { formatCurrency, getMonthName, getFinancialYear } from '@/lib/format'
import { PageHeader } from '@/components/layout/page-header'
import { StatCard, StatsGrid } from '@/components/layout/stat-card'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import {
  Users,
  Wallet,
  Receipt,
  Calendar,
  TrendingUp,
  AlertCircle,
  CheckCircle,
  Clock,
  FileText,
  ArrowRight,
  CalendarDays,
  IndianRupee,
  Building2,
  Bot,
  Loader2
} from 'lucide-react'

interface DashboardStats {
  total_employees: number
  active_employees: number
  on_leave_today: number
  pending_leave_requests: number
  monthly_payroll: number
  pf_contribution: number
  esi_contribution: number
  tds_deducted: number
  receivables: number
  payables: number
  overdue_invoices: number
  overdue_bills: number
}

interface ComplianceItem {
  name: string
  status: string
  due_date: string
  amount: number | null
  status_type: string
}

interface DashboardData {
  stats: DashboardStats
  compliance_status: ComplianceItem[]
  recent_activities: Array<{
    type: string
    message: string
    time: string
  }>
  ai_insights: Array<{
    title: string
    description: string
  }>
}

export default function DashboardPage() {
  const { user } = useAuthStore()
  const { data: dashboardData, isLoading, error, get } = useApi<DashboardData>()

  const currentDate = new Date()
  const currentMonth = getMonthName(currentDate.getMonth() + 1)
  const currentYear = currentDate.getFullYear()
  const financialYear = getFinancialYear(currentDate)

  // Fetch dashboard data on mount
  React.useEffect(() => {
    get('/reports/dashboard')
  }, [get])

  // Mock dashboard stats - fallback if API doesn't return data
  const stats = dashboardData?.stats || {
    totalEmployees: 47,
    activeEmployees: 45,
    onLeaveToday: 3,
    pendingLeaveRequests: 5,
    monthlyPayroll: 1847500,
    pfContribution: 221700,
    esiContribution: 73900,
    tdsDeducted: 142300,
    receivables: 2340000,
    payables: 1560000,
    overdueInvoices: 4,
    overdueBills: 2
  }

  // Quick stats for the grid
  const quickStats = [
    {
      title: 'Total Employees',
      value: stats.total_employees || stats.totalEmployees,
      icon: Users,
      description: `${stats.active_employees || stats.activeEmployees} active`,
      trend: { value: 4.5, label: 'vs last month' }
    },
    {
      title: 'Pending Leave Requests',
      value: stats.pending_leave_requests || stats.pendingLeaveRequests,
      icon: Calendar,
      description: `${stats.on_leave_today || stats.onLeaveToday} on leave today`,
      trend: { value: -10, type: 'decrease' as const }
    },
    {
      title: `Payroll (${currentMonth})`,
      value: formatCurrency(stats.monthly_payroll || stats.monthlyPayroll),
      icon: Wallet,
      description: 'Gross salary',
      trend: { value: 2.3, label: 'vs last month' }
    },
    {
      title: 'Outstanding Receivables',
      value: formatCurrency(stats.receivables),
      icon: IndianRupee,
      description: `${stats.overdue_invoices || stats.overdueInvoices} overdue invoices`,
      valueClassName: 'text-green-600'
    }
  ]

  // Recent activities
  const recentActivities = [
    {
      type: 'success',
      message: 'Payroll processed for December 2025',
      time: '2 hours ago',
      icon: CheckCircle
    },
    {
      type: 'warning',
      message: 'GST Return GSTR-1 due in 5 days',
      time: '3 hours ago',
      icon: AlertCircle
    },
    {
      type: 'info',
      message: 'New employee Priya Sharma onboarded',
      time: '5 hours ago',
      icon: Users
    },
    {
      type: 'success',
      message: 'Invoice INV-2025-0147 - Rs. 45,000 received',
      time: '1 day ago',
      icon: CheckCircle
    },
    {
      type: 'warning',
      message: 'PF ECR file generated - pending submission',
      time: '1 day ago',
      icon: Clock
    }
  ]

  // AI Insights
  const aiInsights = [
    {
      title: 'Cash Flow Forecast',
      description: 'Positive cash flow expected for next 30 days. Projected surplus: Rs. 4.2L'
    },
    {
      title: 'Compliance Alert',
      description: 'TDS quarterly return (24Q) due on 31st January. 3 challans pending.'
    },
    {
      title: 'Invoice Reminder',
      description: '2 invoices from ABC Corp overdue by 15+ days. Total: Rs. 1.8L'
    },
    {
      title: 'Cost Anomaly',
      description: 'AWS infrastructure costs 35% higher than 3-month average.'
    }
  ]

  // Compliance summary
  const complianceStatus = [
    { name: 'PF', status: 'Paid', dueDate: '15th Jan', amount: 221700, statusType: 'success' },
    { name: 'ESI', status: 'Due', dueDate: '15th Jan', amount: 73900, statusType: 'warning' },
    { name: 'PT', status: 'Paid', dueDate: '20th Jan', amount: 9400, statusType: 'success' },
    { name: 'TDS', status: 'Due', dueDate: '7th Jan', amount: 142300, statusType: 'warning' },
    { name: 'GSTR-1', status: 'Pending', dueDate: '11th Jan', amount: null, statusType: 'pending' }
  ]

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'success': return 'bg-green-100 text-green-800'
      case 'warning': return 'bg-yellow-100 text-yellow-800'
      case 'pending': return 'bg-gray-100 text-gray-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  // Use API data for compliance status if available
  const complianceStatusData = dashboardData?.compliance_status || complianceStatus

  return (
    <div className="space-y-6">
      {/* Loading State */}
      {isLoading && (
        <Card className="p-8 flex items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <span className="ml-2">Loading dashboard...</span>
        </Card>
      )}

      {/* Welcome Header */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div>
              <h1 className="text-2xl font-bold">
                Welcome back, {user?.full_name || 'User'}!
              </h1>
              <p className="text-muted-foreground mt-1">
                Here's what's happening with your business today - {financialYear}
              </p>
            </div>
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <CalendarDays className="h-4 w-4" />
              <span>{currentDate.toLocaleDateString('en-IN', {
                weekday: 'long',
                year: 'numeric',
                month: 'long',
                day: 'numeric'
              })}</span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Stats Grid */}
      <StatsGrid stats={quickStats} columns={4} />

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Activity */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
            <CardDescription>Latest updates across your organization</CardDescription>
          </CardHeader>
          <CardContent>
            <ul className="space-y-4">
              {recentActivities.map((activity, index) => {
                const Icon = activity.icon
                const iconColors = {
                  success: 'text-green-500',
                  warning: 'text-yellow-500',
                  info: 'text-blue-500'
                }

                return (
                  <li key={index} className="flex items-start gap-3">
                    <Icon className={`h-5 w-5 mt-0.5 ${iconColors[activity.type as keyof typeof iconColors]}`} />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm">{activity.message}</p>
                      <p className="text-xs text-muted-foreground">{activity.time}</p>
                    </div>
                  </li>
                )
              })}
            </ul>
          </CardContent>
        </Card>

        {/* Compliance Status */}
        <Card>
          <CardHeader>
            <CardTitle>Compliance Status</CardTitle>
            <CardDescription>January 2026 statutory dues</CardDescription>
          </CardHeader>
          <CardContent>
            <ul className="space-y-3">
              {complianceStatus.map((item) => (
                <li key={item.name} className="flex items-center justify-between py-2 border-b last:border-0">
                  <div>
                    <p className="font-medium">{item.name}</p>
                    <p className="text-xs text-muted-foreground">Due: {item.dueDate}</p>
                  </div>
                  <div className="text-right">
                    {item.amount && (
                      <p className="text-sm font-medium">{formatCurrency(item.amount)}</p>
                    )}
                    <Badge className={getStatusColor(item.statusType)}>
                      {item.status}
                    </Badge>
                  </div>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      </div>

      {/* AI Insights */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <Bot className="h-5 w-5 text-primary" />
              AI Insights
            </CardTitle>
            <CardDescription>Intelligent analysis of your business data</CardDescription>
          </div>
          <Button variant="outline" size="sm" asChild>
            <Link href="/ai">
              Open AI Assistant
              <ArrowRight className="h-4 w-4 ml-2" />
            </Link>
          </Button>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {aiInsights.map((insight, index) => (
              <div
                key={index}
                className="p-4 rounded-lg border bg-muted/50"
              >
                <div className="flex items-start gap-3">
                  <TrendingUp className="h-5 w-5 text-primary mt-0.5" />
                  <div>
                    <p className="font-medium text-sm">{insight.title}</p>
                    <p className="text-sm text-muted-foreground mt-1">{insight.description}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
          <CardDescription>Common tasks you can perform quickly</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-6 gap-4">
            <Link
              href="/dashboard/employees/new"
              className="flex flex-col items-center p-4 border rounded-lg hover:bg-muted transition-colors"
            >
              <Users className="h-8 w-8 text-primary" />
              <span className="mt-2 text-sm text-center">Add Employee</span>
            </Link>

            <Link
              href="/dashboard/payroll"
              className="flex flex-col items-center p-4 border rounded-lg hover:bg-muted transition-colors"
            >
              <Wallet className="h-8 w-8 text-primary" />
              <span className="mt-2 text-sm text-center">Run Payroll</span>
            </Link>

            <Link
              href="/dashboard/invoices/new"
              className="flex flex-col items-center p-4 border rounded-lg hover:bg-muted transition-colors"
            >
              <Receipt className="h-8 w-8 text-primary" />
              <span className="mt-2 text-sm text-center">Create Invoice</span>
            </Link>

            <Link
              href="/dashboard/leave"
              className="flex flex-col items-center p-4 border rounded-lg hover:bg-muted transition-colors"
            >
              <Calendar className="h-8 w-8 text-primary" />
              <span className="mt-2 text-sm text-center">Approve Leave</span>
            </Link>

            <Link
              href="/dashboard/payroll/compliance"
              className="flex flex-col items-center p-4 border rounded-lg hover:bg-muted transition-colors"
            >
              <FileText className="h-8 w-8 text-primary" />
              <span className="mt-2 text-sm text-center">File Returns</span>
            </Link>

            <Link
              href="/dashboard/ai"
              className="flex flex-col items-center p-4 border rounded-lg hover:bg-muted transition-colors"
            >
              <Bot className="h-8 w-8 text-primary" />
              <span className="mt-2 text-sm text-center">Ask AI</span>
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
