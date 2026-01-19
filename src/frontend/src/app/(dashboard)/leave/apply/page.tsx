'use client'

import * as React from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { PageHeader } from '@/components/layout/page-header'
import { LeaveRequestForm } from '@/components/leave'
import { LeaveBalanceGrid } from '@/components/leave/LeaveBalanceCard'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { getFinancialYear, formatDate } from '@/lib/format'
import { useApi } from '@/hooks'
import {
  Calendar,
  Info,
  Star,
  Loader2
} from 'lucide-react'
import type { LeaveBalance, LeaveType } from '@/types'

// API Response types
interface LeaveTypeApiResponse {
  data: ApiLeaveType[]
  total: number
}

interface ApiLeaveType {
  id: string
  code: string
  name: string
  description: string
  is_paid: boolean
  is_encashable: boolean
  is_carry_forward: boolean
  max_days_per_year: string
  min_days_per_application: string
  max_days_per_application: string | null
  requires_document: boolean
  color_code: string
  is_active: boolean
}

interface LeaveBalanceApiResponse {
  employee_id: string
  employee_name: string
  financial_year: string
  balances: {
    leave_type_id: string
    leave_type_code: string
    leave_type_name: string
    color_code: string
    entitled: string
    used: string
    pending: string
    available: string
  }[]
}

interface HolidayApiResponse {
  data: {
    id: string
    name: string
    holiday_date: string
    is_mandatory: boolean
  }[]
  total: number
}

// ============================================================================
// Apply Leave Page
// ============================================================================

export default function ApplyLeavePage() {
  const router = useRouter()
  const [isSubmitting, setIsSubmitting] = React.useState(false)
  const [isLoading, setIsLoading] = React.useState(true)
  const [leaveTypes, setLeaveTypes] = React.useState<LeaveType[]>([])
  const [leaveBalances, setLeaveBalances] = React.useState<LeaveBalance[]>([])
  const [upcomingHolidays, setUpcomingHolidays] = React.useState<{date: string, name: string, type: string}[]>([])

  const typesApi = useApi<LeaveTypeApiResponse>()
  const balanceApi = useApi<LeaveBalanceApiResponse>()
  const holidaysApi = useApi<HolidayApiResponse>()
  const submitApi = useApi()

  // Fetch leave types, balances, and holidays from API
  React.useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true)
      try {
        // Fetch leave types
        const typesResult = await typesApi.get('/leave/types')
        if (typesResult && typesResult.data) {
          const mappedTypes: LeaveType[] = typesResult.data.map((t: ApiLeaveType) => ({
            id: t.id,
            code: t.code,
            name: t.name,
            annual_quota: parseFloat(t.max_days_per_year),
            carry_forward_limit: t.is_carry_forward ? 30 : 0,
            encashment_allowed: t.is_encashable,
            is_paid: t.is_paid,
            applicable_to: ['full_time', 'contract'],
            requires_approval: true,
            min_days: parseFloat(t.min_days_per_application),
            max_days: t.max_days_per_application ? parseFloat(t.max_days_per_application) : parseFloat(t.max_days_per_year),
            notice_days: 1,
            applicable_from_months: 0
          }))
          setLeaveTypes(mappedTypes)
        }

        // Fetch leave balances
        const balanceResult = await balanceApi.get('/leave/balance')
        if (balanceResult && balanceResult.balances) {
          const mappedBalances: LeaveBalance[] = balanceResult.balances.map((b: LeaveBalanceApiResponse['balances'][0]) => ({
            employee_id: balanceResult.employee_id,
            leave_type_code: b.leave_type_code,
            leave_type_name: b.leave_type_name,
            year: 2026,
            opening_balance: parseFloat(b.entitled),
            credited: 0,
            used: parseFloat(b.used),
            lapsed: 0,
            available: parseFloat(b.available),
            pending_approval: parseFloat(b.pending)
          }))
          setLeaveBalances(mappedBalances)
        }

        // Fetch holidays
        const holidaysResult = await holidaysApi.get('/leave/holidays?year=2026')
        if (holidaysResult && holidaysResult.data) {
          const mappedHolidays = holidaysResult.data.map((h: HolidayApiResponse['data'][0]) => ({
            date: h.holiday_date,
            name: h.name,
            type: h.is_mandatory ? 'national' : 'optional'
          }))
          setUpcomingHolidays(mappedHolidays)
        }
      } catch (error) {
        console.error('Failed to fetch leave data:', error)
      } finally {
        setIsLoading(false)
      }
    }

    fetchData()
  }, [])

  const handleSubmit = async (data: {
    leave_type_code: string
    from_date: string
    to_date: string
    half_day: boolean
    half_day_type?: 'first_half' | 'second_half'
    reason: string
  }) => {
    setIsSubmitting(true)

    try {
      // Find the leave type ID from code
      const leaveType = leaveTypes.find(t => t.code === data.leave_type_code)
      if (!leaveType) {
        throw new Error('Invalid leave type')
      }

      // Prepare API request
      const requestData = {
        leave_type_id: leaveType.id,
        from_date: data.from_date,
        to_date: data.to_date,
        from_day_type: data.half_day && data.half_day_type === 'first_half' ? 'first_half' : 'full',
        to_day_type: data.half_day && data.half_day_type === 'second_half' ? 'second_half' : 'full',
        reason: data.reason,
        submit: true
      }

      const result = await submitApi.post('/leave/requests', requestData)

      if (result) {
        router.push('/leave/requests?status=pending')
      }
    } catch (error) {
      console.error('Failed to submit leave request:', error)
      throw error
    } finally {
      setIsSubmitting(false)
    }
  }

  if (isLoading) {
    return (
      <div className="space-y-6">
        <PageHeader
          title="Apply for Leave"
          description={`${getFinancialYear()} - Submit a new leave request`}
          breadcrumbs={[
            { label: 'Dashboard', href: '/' },
            { label: 'Leave', href: '/leave' },
            { label: 'Apply' }
          ]}
        />
        <Card>
          <CardContent className="flex items-center justify-center py-12">
            <div className="flex items-center gap-2 text-muted-foreground">
              <Loader2 className="h-5 w-5 animate-spin" />
              <span>Loading leave data...</span>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Apply for Leave"
        description={`${getFinancialYear()} - Submit a new leave request`}
        breadcrumbs={[
          { label: 'Dashboard', href: '/' },
          { label: 'Leave', href: '/leave' },
          { label: 'Apply' }
        ]}
      />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Form */}
        <div className="lg:col-span-2">
          <LeaveRequestForm
            leaveTypes={leaveTypes}
            balances={leaveBalances}
            approverName="Admin (Manager)"
            onSubmit={handleSubmit}
          />
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Leave Balances Card */}
          <Card>
            <CardHeader>
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <Calendar className="h-4 w-4" />
                My Leave Balance
              </CardTitle>
              <CardDescription>{getFinancialYear()}</CardDescription>
            </CardHeader>
            <CardContent>
              {leaveBalances.length > 0 ? (
                <LeaveBalanceGrid
                  balances={leaveBalances}
                  compact
                  columns={2}
                />
              ) : (
                <p className="text-sm text-muted-foreground">No leave balances found</p>
              )}
            </CardContent>
          </Card>

          {/* Upcoming Holidays */}
          <Card>
            <CardHeader>
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <Star className="h-4 w-4 text-orange-500" />
                Upcoming Holidays
              </CardTitle>
              <CardDescription>Plan your leaves around holidays</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {upcomingHolidays.length > 0 ? (
                  upcomingHolidays.slice(0, 4).map((holiday, index) => (
                    <div
                      key={index}
                      className="flex items-center justify-between p-2 rounded bg-orange-50 border border-orange-100"
                    >
                      <div>
                        <p className="text-sm font-medium">{holiday.name}</p>
                        <p className="text-xs text-muted-foreground capitalize">{holiday.type}</p>
                      </div>
                      <Badge variant="outline" className="bg-white text-xs">
                        {formatDate(holiday.date)}
                      </Badge>
                    </div>
                  ))
                ) : (
                  <p className="text-sm text-muted-foreground">No upcoming holidays</p>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Tips Card */}
          <Card>
            <CardHeader>
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <Info className="h-4 w-4 text-blue-500" />
                Tips
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="text-sm text-muted-foreground space-y-2">
                <li className="flex items-start gap-2">
                  <span className="text-primary">-</span>
                  <span>Apply for Earned Leave (EL) at least 7 days in advance</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary">-</span>
                  <span>Sick Leave beyond 2 days requires medical certificate</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary">-</span>
                  <span>Casual Leave cannot exceed 3 consecutive days</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary">-</span>
                  <span>Half day leave is available for CL and SL only</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-primary">-</span>
                  <span>Sandwich rule applies for leaves around holidays</span>
                </li>
              </ul>
            </CardContent>
          </Card>

          {/* Leave Policy Summary */}
          <Card>
            <CardHeader>
              <CardTitle className="text-sm font-medium">Leave Policy Summary</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3 text-sm">
                {leaveTypes.map((lt) => (
                  <div key={lt.code} className="border-b pb-2 last:border-0">
                    <div className="flex items-center justify-between">
                      <span className="font-medium">{lt.name} ({lt.code})</span>
                      <Badge variant={lt.is_paid ? 'default' : 'outline'}>
                        {lt.is_paid ? 'Paid' : 'Unpaid'}
                      </Badge>
                    </div>
                    <div className="text-xs text-muted-foreground mt-1">
                      <span>Max: {lt.max_days} days</span>
                      <span className="mx-2">|</span>
                      <span>Notice: {lt.notice_days} days</span>
                      {lt.carry_forward_limit > 0 && (
                        <>
                          <span className="mx-2">|</span>
                          <span>CF: {lt.carry_forward_limit} days</span>
                        </>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
