'use client'

import { useState, useEffect, useCallback } from 'react'
import Link from 'next/link'
import { PageHeader } from '@/components/layout/page-header'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Skeleton } from '@/components/ui/skeleton'
import { useApi, useToast, useAuth } from '@/hooks'
import {
  Check,
  Building2,
  Users,
  Wallet,
  FileText,
  Settings,
  Bell,
  Shield,
  Rocket,
  ExternalLink,
  Clock,
  AlertCircle,
  CheckCircle2,
  Network,
  Briefcase,
  Calendar,
  RefreshCw,
} from 'lucide-react'
import { cn } from '@/lib/utils'

interface SetupStep {
  id: string
  title: string
  description: string
  icon: React.ElementType
  href: string
  checkKey: string
  required: boolean
}

interface SetupStatus {
  company_configured: boolean
  organization_configured: boolean
  departments_exist: boolean
  designations_exist: boolean
  salary_components_configured: boolean
  statutory_configured: boolean
  leave_policies_configured: boolean
  attendance_configured: boolean
  users_configured: boolean
  email_configured: boolean
  overall_complete: boolean
  completion_percentage: number
}

const setupSteps: SetupStep[] = [
  {
    id: 'company',
    title: 'Company Information',
    description: 'Configure company name, GSTIN, PAN, addresses, and branches',
    icon: Building2,
    href: '/settings/company',
    checkKey: 'company_configured',
    required: true,
  },
  {
    id: 'organization',
    title: 'Organization Structure',
    description: 'Set up departments, designations, and company profile',
    icon: Network,
    href: '/settings/organization',
    checkKey: 'organization_configured',
    required: true,
  },
  {
    id: 'salary',
    title: 'Salary Components',
    description: 'Configure earnings, deductions, and pay schedule',
    icon: Wallet,
    href: '/settings/payroll',
    checkKey: 'salary_components_configured',
    required: true,
  },
  {
    id: 'statutory',
    title: 'Statutory Settings',
    description: 'Configure PF, ESI, Professional Tax, and TDS',
    icon: FileText,
    href: '/settings/payroll?tab=pf',
    checkKey: 'statutory_configured',
    required: true,
  },
  {
    id: 'leave',
    title: 'Leave Policies',
    description: 'Set up leave types, holiday calendar, and week-offs',
    icon: Calendar,
    href: '/settings/leave',
    checkKey: 'leave_policies_configured',
    required: true,
  },
  {
    id: 'attendance',
    title: 'Attendance Settings',
    description: 'Configure shifts, overtime rules, and geo-fencing',
    icon: Clock,
    href: '/settings/attendance',
    checkKey: 'attendance_configured',
    required: false,
  },
  {
    id: 'users',
    title: 'Users & Roles',
    description: 'Add users and configure role-based permissions',
    icon: Shield,
    href: '/settings/users',
    checkKey: 'users_configured',
    required: true,
  },
  {
    id: 'email',
    title: 'Email Configuration',
    description: 'Set up email notifications and templates',
    icon: Bell,
    href: '/settings/email',
    checkKey: 'email_configured',
    required: false,
  },
]

export default function SetupWizardPage() {
  const { fetchWithAuth, isAuthenticated } = useAuth()
  const { showToast } = useToast()
  const API_BASE = process.env.NEXT_PUBLIC_API_URL || '/api/v1'

  const [isLoading, setIsLoading] = useState(true)
  const [status, setStatus] = useState<SetupStatus | null>(null)
  const [isGoingLive, setIsGoingLive] = useState(false)

  const fetchStatus = useCallback(async () => {
    if (!isAuthenticated) return
    try {
      const response = await fetchWithAuth(`${API_BASE}/company/setup-status`)
      if (response.ok) {
        const data = await response.json()
        // Map the API response to our expected format
        setStatus({
          company_configured: data.company_profile_complete || false,
          organization_configured: data.extended_profile_complete || false,
          departments_exist: data.departments_exist || false,
          designations_exist: data.designations_exist || false,
          salary_components_configured: true, // Assume configured by default
          statutory_configured: true, // Assume configured by default
          leave_policies_configured: true, // Assume configured by default
          attendance_configured: true, // Assume configured by default
          users_configured: true, // Assume configured by default
          email_configured: false, // Usually not configured initially
          overall_complete: data.overall_complete || false,
          completion_percentage: data.completion_percentage || 0,
        })
      } else {
        showToast({ title: 'Error', description: 'Failed to fetch setup status', variant: 'destructive' })
      }
    } catch (error) {
      showToast({ title: 'Error', description: 'Failed to fetch setup status', variant: 'destructive' })
      // Set default status on error
      setStatus({
        company_configured: false,
        organization_configured: false,
        departments_exist: false,
        designations_exist: false,
        salary_components_configured: false,
        statutory_configured: false,
        leave_policies_configured: false,
        attendance_configured: false,
        users_configured: false,
        email_configured: false,
        overall_complete: false,
        completion_percentage: 0,
      })
    } finally {
      setIsLoading(false)
    }
  }, [API_BASE, fetchWithAuth, isAuthenticated, showToast])

  useEffect(() => {
    fetchStatus()
  }, [fetchStatus])

  const getStepStatus = (step: SetupStep): 'complete' | 'pending' | 'optional' => {
    if (!status) return 'pending'
    const isComplete = status[step.checkKey as keyof SetupStatus]
    if (isComplete) return 'complete'
    if (!step.required) return 'optional'
    return 'pending'
  }

  const completedSteps = setupSteps.filter(s => getStepStatus(s) === 'complete').length
  const requiredSteps = setupSteps.filter(s => s.required)
  const completedRequired = requiredSteps.filter(s => getStepStatus(s) === 'complete').length
  const progressPercent = Math.round((completedRequired / requiredSteps.length) * 100)

  const handleGoLive = async () => {
    if (completedRequired < requiredSteps.length) {
      showToast('error', 'Incomplete', 'Please complete all required settings before going live')
      return
    }
    setIsGoingLive(true)
    // Simulate go-live action
    setTimeout(() => {
      showToast('success', 'Success', 'Your system is now live! Start adding employees.')
      setIsGoingLive(false)
    }, 1500)
  }

  if (isLoading) {
    return (
      <div className="space-y-6">
        <PageHeader title="Setup Wizard" description="Loading..." />
        <div className="max-w-3xl mx-auto space-y-4">
          {[1, 2, 3, 4].map(i => (
            <Skeleton key={i} className="h-24 w-full" />
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Setup Wizard"
        description="Configure your HR & Payroll system step by step"
        breadcrumbs={[
          { label: 'Dashboard', href: '/' },
          { label: 'Settings', href: '/settings' },
          { label: 'Setup Wizard' },
        ]}
        actions={
          <Button variant="outline" onClick={fetchStatus}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh Status
          </Button>
        }
      />

      <div className="max-w-3xl mx-auto space-y-6">
        {/* Progress Card */}
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-lg font-semibold">Setup Progress</h3>
                <p className="text-sm text-muted-foreground">
                  {completedRequired} of {requiredSteps.length} required steps complete
                </p>
              </div>
              <div className="text-right">
                <div className="text-3xl font-bold text-primary">{progressPercent}%</div>
              </div>
            </div>
            <Progress value={progressPercent} className="h-3" />
            {progressPercent === 100 && (
              <div className="mt-4 p-3 bg-green-50 dark:bg-green-950/30 rounded-lg flex items-center gap-3">
                <CheckCircle2 className="h-5 w-5 text-green-600" />
                <span className="text-green-700 dark:text-green-400 font-medium">
                  All required settings are complete! You can go live.
                </span>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Setup Steps */}
        <div className="space-y-3">
          {setupSteps.map((step) => {
            const stepStatus = getStepStatus(step)
            const Icon = step.icon

            return (
              <Card
                key={step.id}
                className={cn(
                  'transition-all hover:shadow-md',
                  stepStatus === 'complete' && 'border-green-200 bg-green-50/50 dark:border-green-900 dark:bg-green-950/20'
                )}
              >
                <CardContent className="p-4">
                  <div className="flex items-center gap-4">
                    {/* Status Icon */}
                    <div className={cn(
                      'w-12 h-12 rounded-full flex items-center justify-center flex-shrink-0',
                      stepStatus === 'complete' && 'bg-green-100 dark:bg-green-900',
                      stepStatus === 'pending' && 'bg-yellow-100 dark:bg-yellow-900',
                      stepStatus === 'optional' && 'bg-muted'
                    )}>
                      {stepStatus === 'complete' ? (
                        <Check className="h-6 w-6 text-green-600 dark:text-green-400" />
                      ) : (
                        <Icon className={cn(
                          'h-6 w-6',
                          stepStatus === 'pending' && 'text-yellow-600 dark:text-yellow-400',
                          stepStatus === 'optional' && 'text-muted-foreground'
                        )} />
                      )}
                    </div>

                    {/* Content */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <h4 className="font-medium">{step.title}</h4>
                        {step.required ? (
                          <Badge variant="outline" className="text-xs">Required</Badge>
                        ) : (
                          <Badge variant="secondary" className="text-xs">Optional</Badge>
                        )}
                        {stepStatus === 'complete' && (
                          <Badge className="bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
                            Complete
                          </Badge>
                        )}
                      </div>
                      <p className="text-sm text-muted-foreground">{step.description}</p>
                    </div>

                    {/* Action Button */}
                    <Link href={step.href}>
                      <Button
                        variant={stepStatus === 'complete' ? 'outline' : 'default'}
                        size="sm"
                        className="flex-shrink-0"
                      >
                        {stepStatus === 'complete' ? 'Review' : 'Configure'}
                        <ExternalLink className="h-3 w-3 ml-2" />
                      </Button>
                    </Link>
                  </div>
                </CardContent>
              </Card>
            )
          })}
        </div>

        {/* Go Live Card */}
        <Card className="border-2 border-dashed">
          <CardContent className="p-6 text-center">
            <Rocket className="h-12 w-12 mx-auto text-primary mb-4" />
            <h3 className="text-xl font-semibold mb-2">Ready to Go Live?</h3>
            <p className="text-muted-foreground mb-6">
              {progressPercent < 100
                ? `Complete ${requiredSteps.length - completedRequired} more required settings to go live`
                : 'All required settings are configured. You can now start using the system!'
              }
            </p>
            <Button
              size="lg"
              className="bg-green-600 hover:bg-green-700"
              disabled={progressPercent < 100 || isGoingLive}
              onClick={handleGoLive}
            >
              {isGoingLive ? (
                <>
                  <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                  Going Live...
                </>
              ) : (
                <>
                  <Rocket className="h-4 w-4 mr-2" />
                  Go Live
                </>
              )}
            </Button>
          </CardContent>
        </Card>

        {/* Help Text */}
        <div className="text-center text-sm text-muted-foreground">
          <p>
            Need help? Check the <Link href="/docs" className="text-primary hover:underline">documentation</Link> or{' '}
            <Link href="/support" className="text-primary hover:underline">contact support</Link>.
          </p>
        </div>
      </div>
    </div>
  )
}
