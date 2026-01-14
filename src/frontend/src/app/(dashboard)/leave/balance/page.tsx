'use client'

import * as React from 'react'
import Link from 'next/link'
import { PageHeader } from '@/components/layout/page-header'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { formatDate, getFinancialYear } from '@/lib/format'
import { useApi } from '@/hooks'
import {
  Calendar,
  Sun,
  Heart,
  Umbrella,
  Clock,
  Download,
  ArrowLeft,
  TrendingUp,
  TrendingDown,
  Loader2
} from 'lucide-react'
import type { LeaveBalance } from '@/types'

// Mock leave balances
const mockLeaveBalances: LeaveBalance[] = [
  { employee_id: '1', leave_type_code: 'CL', leave_type_name: 'Casual Leave', year: 2026, opening_balance: 12, credited: 0, used: 2, lapsed: 0, available: 10, pending_approval: 1 },
  { employee_id: '1', leave_type_code: 'SL', leave_type_name: 'Sick Leave', year: 2026, opening_balance: 12, credited: 0, used: 0, lapsed: 0, available: 12, pending_approval: 0 },
  { employee_id: '1', leave_type_code: 'EL', leave_type_name: 'Earned Leave', year: 2026, opening_balance: 10, credited: 1.25, used: 0, lapsed: 0, available: 11.25, pending_approval: 0 },
  { employee_id: '1', leave_type_code: 'LWP', leave_type_name: 'Leave Without Pay', year: 2026, opening_balance: 0, credited: 0, used: 0, lapsed: 0, available: 0, pending_approval: 0 },
  { employee_id: '1', leave_type_code: 'CO', leave_type_name: 'Compensatory Off', year: 2026, opening_balance: 0, credited: 2, used: 1, lapsed: 0, available: 1, pending_approval: 0 },
  { employee_id: '1', leave_type_code: 'ML', leave_type_name: 'Maternity Leave', year: 2026, opening_balance: 182, credited: 0, used: 0, lapsed: 0, available: 182, pending_approval: 0 },
]

const leaveTypeIcons: Record<string, React.ElementType> = {
  CL: Sun,
  SL: Heart,
  EL: Umbrella,
  LWP: Clock,
  CO: TrendingUp,
  ML: Heart,
}

const leaveTypeColors: Record<string, string> = {
  CL: 'bg-yellow-100 text-yellow-800 border-yellow-200',
  SL: 'bg-red-100 text-red-800 border-red-200',
  EL: 'bg-blue-100 text-blue-800 border-blue-200',
  LWP: 'bg-gray-100 text-gray-800 border-gray-200',
  CO: 'bg-purple-100 text-purple-800 border-purple-200',
  ML: 'bg-pink-100 text-pink-800 border-pink-200',
}

export default function LeaveBalancePage() {
  const [balances, setBalances] = React.useState<LeaveBalance[]>(mockLeaveBalances)
  const [isLoading, setIsLoading] = React.useState(true)
  const api = useApi()

  React.useEffect(() => {
    const fetchBalances = async () => {
      setIsLoading(true)
      try {
        const result = await api.get('/leave/balance')
        if (result?.balances) {
          const mappedBalances: LeaveBalance[] = result.balances.map((b: any) => ({
            employee_id: result.employee_id,
            leave_type_code: b.leave_type_code,
            leave_type_name: b.leave_type_name,
            year: parseInt(result.financial_year?.split('-')[0]) || 2026,
            opening_balance: parseFloat(b.entitled) || 0,
            credited: 0,
            used: parseFloat(b.used) || 0,
            lapsed: 0,
            available: parseFloat(b.available) || 0,
            pending_approval: parseFloat(b.pending) || 0
          }))
          setBalances(mappedBalances.length > 0 ? mappedBalances : mockLeaveBalances)
        }
      } catch (error) {
        console.error('Failed to fetch leave balances:', error)
      } finally {
        setIsLoading(false)
      }
    }

    fetchBalances()
  }, [])

  const totalAvailable = balances.reduce((sum, b) => sum + b.available, 0)
  const totalUsed = balances.reduce((sum, b) => sum + b.used, 0)
  const totalPending = balances.reduce((sum, b) => sum + b.pending_approval, 0)

  const getIcon = (code: string) => {
    const Icon = leaveTypeIcons[code] || Calendar
    return <Icon className="h-5 w-5" />
  }

  const getProgressColor = (used: number, total: number) => {
    const percentage = total > 0 ? (used / total) * 100 : 0
    if (percentage >= 80) return 'bg-red-500'
    if (percentage >= 50) return 'bg-yellow-500'
    return 'bg-green-500'
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Leave Balance"
        description={`Your leave balance for ${getFinancialYear()}`}
        breadcrumbs={[
          { label: 'Dashboard', href: '/' },
          { label: 'Leave', href: '/leave' },
          { label: 'Balance' }
        ]}
        actions={
          <div className="flex items-center gap-2">
            <Button variant="outline" asChild>
              <Link href="/leave">
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Leave
              </Link>
            </Button>
            <Button variant="outline">
              <Download className="h-4 w-4 mr-2" />
              Export
            </Button>
          </div>
        }
      />

      {isLoading ? (
        <div className="flex items-center justify-center h-64">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        </div>
      ) : (
        <>
          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center gap-4">
                  <div className="p-3 bg-green-100 rounded-full">
                    <TrendingUp className="h-6 w-6 text-green-600" />
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Total Available</p>
                    <p className="text-2xl font-bold text-green-600">{totalAvailable.toFixed(1)} days</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center gap-4">
                  <div className="p-3 bg-orange-100 rounded-full">
                    <TrendingDown className="h-6 w-6 text-orange-600" />
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Total Used</p>
                    <p className="text-2xl font-bold text-orange-600">{totalUsed.toFixed(1)} days</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center gap-4">
                  <div className="p-3 bg-yellow-100 rounded-full">
                    <Clock className="h-6 w-6 text-yellow-600" />
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Pending Approval</p>
                    <p className="text-2xl font-bold text-yellow-600">{totalPending.toFixed(1)} days</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Leave Balance Details */}
          <Card>
            <CardHeader>
              <CardTitle>Leave Balance Details</CardTitle>
              <CardDescription>Breakdown by leave type for {getFinancialYear()}</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                {balances.map((balance) => {
                  const total = balance.opening_balance + balance.credited
                  const usedPercentage = total > 0 ? (balance.used / total) * 100 : 0

                  return (
                    <div key={balance.leave_type_code} className="space-y-3">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <div className={`p-2 rounded-lg ${leaveTypeColors[balance.leave_type_code] || 'bg-gray-100'}`}>
                            {getIcon(balance.leave_type_code)}
                          </div>
                          <div>
                            <p className="font-medium">{balance.leave_type_name}</p>
                            <p className="text-sm text-muted-foreground">{balance.leave_type_code}</p>
                          </div>
                        </div>
                        <div className="text-right">
                          <p className="text-lg font-bold">{balance.available.toFixed(1)}</p>
                          <p className="text-sm text-muted-foreground">available</p>
                        </div>
                      </div>

                      <div className="space-y-2">
                        <div className="flex items-center justify-between text-sm">
                          <span className="text-muted-foreground">Used: {balance.used.toFixed(1)} / {total.toFixed(1)}</span>
                          <span className="text-muted-foreground">{usedPercentage.toFixed(0)}%</span>
                        </div>
                        <Progress value={usedPercentage} className="h-2" />
                      </div>

                      <div className="grid grid-cols-4 gap-4 text-sm border-t pt-3">
                        <div>
                          <p className="text-muted-foreground">Opening</p>
                          <p className="font-medium">{balance.opening_balance.toFixed(1)}</p>
                        </div>
                        <div>
                          <p className="text-muted-foreground">Credited</p>
                          <p className="font-medium text-green-600">+{balance.credited.toFixed(1)}</p>
                        </div>
                        <div>
                          <p className="text-muted-foreground">Used</p>
                          <p className="font-medium text-red-600">-{balance.used.toFixed(1)}</p>
                        </div>
                        <div>
                          <p className="text-muted-foreground">Pending</p>
                          <p className="font-medium text-yellow-600">{balance.pending_approval.toFixed(1)}</p>
                        </div>
                      </div>
                    </div>
                  )
                })}
              </div>
            </CardContent>
          </Card>

          {/* Leave History */}
          <Card>
            <CardHeader>
              <CardTitle>Recent Leave History</CardTitle>
              <CardDescription>Your recent leave applications</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8 text-muted-foreground">
                <Calendar className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>No recent leave history</p>
                <Button variant="link" asChild className="mt-2">
                  <Link href="/leave/apply">Apply for leave</Link>
                </Button>
              </div>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  )
}
