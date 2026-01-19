'use client'

import { useState, useEffect, useCallback } from 'react'
import { PageHeader } from '@/components/layout/page-header'
import { useAuth } from "@/hooks/use-auth"
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Switch } from '@/components/ui/switch'
import { Label } from '@/components/ui/label'
import Link from 'next/link'
import {
  Check,
  X,
  Star,
  Zap,
  Users,
  Cloud,
  Bot,
  Building2,
  Loader2,
  RefreshCw,
  AlertTriangle,
  IndianRupee,
  ArrowLeft,
} from 'lucide-react'

// Types
interface SubscriptionPlan {
  id: string
  code: string
  name: string
  description: string | null
  plan_type: string
  base_price_monthly: number
  per_employee_monthly: number
  base_price_annual: number | null
  per_employee_annual: number | null
  currency: string
  max_employees: number | null
  max_users: number | null
  max_companies: number
  storage_gb: number
  api_calls_monthly: number
  ai_queries_monthly: number
  features: Record<string, boolean>
  modules_enabled: string[]
  trial_days: number
  is_active: boolean
  is_public: boolean
  highlight_text: string | null
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

// Plan feature list
const featureLabels: Record<string, string> = {
  payroll: 'Payroll Processing',
  leave_management: 'Leave Management',
  attendance: 'Attendance Tracking',
  timesheet: 'Timesheet Management',
  documents: 'Document Management',
  accounting: 'Accounting & Finance',
  gst_compliance: 'GST Compliance',
  crm: 'CRM',
  projects: 'Project Management',
  ai_assistant: 'AI Assistant',
  custom_reports: 'Custom Reports',
  api_access: 'API Access',
  sso: 'Single Sign-On',
  audit_logs: 'Audit Logs',
  dedicated_support: 'Dedicated Support',
  custom_branding: 'Custom Branding',
  priority_support: 'Priority Support',
  data_export: 'Data Export',
}

// Plan Card Component
function PlanCard({
  plan,
  isAnnual,
  isCurrentPlan,
  onSelect,
}: {
  plan: SubscriptionPlan
  isAnnual: boolean
  isCurrentPlan: boolean
  onSelect: (plan: SubscriptionPlan) => void
}) {
  const basePrice = isAnnual && plan.base_price_annual
    ? plan.base_price_annual / 12
    : plan.base_price_monthly

  const perEmployee = isAnnual && plan.per_employee_annual
    ? plan.per_employee_annual / 12
    : plan.per_employee_monthly

  const isProfessional = plan.plan_type === 'professional'
  const isEnterprise = plan.plan_type === 'enterprise'

  return (
    <Card className={`relative ${isProfessional ? 'border-primary shadow-lg' : ''}`}>
      {plan.highlight_text && (
        <div className="absolute -top-3 left-1/2 -translate-x-1/2">
          <Badge className="bg-primary text-primary-foreground">
            <Star className="h-3 w-3 mr-1" />
            {plan.highlight_text}
          </Badge>
        </div>
      )}

      <CardHeader className="text-center pb-2">
        <CardTitle className="text-xl">{plan.name}</CardTitle>
        <CardDescription>{plan.description}</CardDescription>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Pricing */}
        <div className="text-center">
          {basePrice > 0 ? (
            <>
              <div className="flex items-baseline justify-center gap-1">
                <IndianRupee className="h-5 w-5" />
                <span className="text-4xl font-bold">{basePrice.toLocaleString()}</span>
                <span className="text-muted-foreground">/mo</span>
              </div>
              {perEmployee > 0 && (
                <p className="text-sm text-muted-foreground mt-1">
                  + {formatCurrency(perEmployee)}/employee/mo
                </p>
              )}
              {isAnnual && (
                <Badge variant="secondary" className="mt-2">
                  Save 2 months with annual billing
                </Badge>
              )}
            </>
          ) : (
            <div className="text-4xl font-bold">Free</div>
          )}
        </div>

        {/* Limits */}
        <div className="space-y-2 pt-4 border-t">
          <div className="flex items-center justify-between text-sm">
            <span className="flex items-center gap-2">
              <Users className="h-4 w-4 text-muted-foreground" />
              Employees
            </span>
            <span className="font-medium">
              {plan.max_employees ? `Up to ${plan.max_employees}` : 'Unlimited'}
            </span>
          </div>
          <div className="flex items-center justify-between text-sm">
            <span className="flex items-center gap-2">
              <Cloud className="h-4 w-4 text-muted-foreground" />
              Storage
            </span>
            <span className="font-medium">{plan.storage_gb} GB</span>
          </div>
          <div className="flex items-center justify-between text-sm">
            <span className="flex items-center gap-2">
              <Zap className="h-4 w-4 text-muted-foreground" />
              API Calls
            </span>
            <span className="font-medium">
              {plan.api_calls_monthly >= 1000000
                ? 'Unlimited'
                : `${(plan.api_calls_monthly / 1000).toFixed(0)}K/mo`}
            </span>
          </div>
          <div className="flex items-center justify-between text-sm">
            <span className="flex items-center gap-2">
              <Bot className="h-4 w-4 text-muted-foreground" />
              AI Queries
            </span>
            <span className="font-medium">
              {plan.ai_queries_monthly >= 10000
                ? 'Unlimited'
                : `${plan.ai_queries_monthly}/mo`}
            </span>
          </div>
          <div className="flex items-center justify-between text-sm">
            <span className="flex items-center gap-2">
              <Building2 className="h-4 w-4 text-muted-foreground" />
              Companies
            </span>
            <span className="font-medium">{plan.max_companies}</span>
          </div>
        </div>

        {/* Features */}
        <div className="space-y-2 pt-4 border-t">
          <p className="text-sm font-medium">Features:</p>
          {Object.entries(plan.features).slice(0, 8).map(([key, enabled]) => (
            <div key={key} className="flex items-center gap-2 text-sm">
              {enabled ? (
                <Check className="h-4 w-4 text-green-600 shrink-0" />
              ) : (
                <X className="h-4 w-4 text-muted-foreground shrink-0" />
              )}
              <span className={enabled ? '' : 'text-muted-foreground'}>
                {featureLabels[key] || key}
              </span>
            </div>
          ))}
        </div>

        {/* Trial info */}
        {plan.trial_days > 0 && (
          <p className="text-center text-sm text-muted-foreground">
            {plan.trial_days}-day free trial
          </p>
        )}
      </CardContent>

      <CardFooter>
        <Button
          className="w-full"
          variant={isProfessional ? 'default' : 'outline'}
          disabled={isCurrentPlan}
          onClick={() => onSelect(plan)}
        >
          {isCurrentPlan ? 'Current Plan' : isEnterprise ? 'Contact Sales' : 'Get Started'}
        </Button>
      </CardFooter>
    </Card>
  )
}

export default function SubscriptionPlansPage() {
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [plans, setPlans] = useState<SubscriptionPlan[]>([])
  const [isAnnual, setIsAnnual] = useState(false)

  const fetchPlans = async () => {
    setIsLoading(true)
    setError(null)
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || '/api/v1'
      const res = await fetchWithAuth(`${apiUrl}/subscriptions/plans`)
      if (res.ok) {
        const data = await res.json()
        setPlans(data)
      }
    } catch (err) {
      console.error('Failed to fetch plans:', err)
      setError('Failed to load plans. Using demo data.')
      // Mock data
      setPlans([
        {
          id: '1',
          code: 'free',
          name: 'Free',
          description: 'For small teams getting started',
          plan_type: 'free',
          base_price_monthly: 0,
          per_employee_monthly: 0,
          base_price_annual: null,
          per_employee_annual: null,
          currency: 'INR',
          max_employees: 5,
          max_users: 2,
          max_companies: 1,
          storage_gb: 1,
          api_calls_monthly: 1000,
          ai_queries_monthly: 10,
          features: {
            payroll: true,
            leave_management: true,
            attendance: true,
            documents: false,
            accounting: false,
            gst_compliance: false,
            ai_assistant: false,
          },
          modules_enabled: ['payroll', 'leave', 'attendance'],
          trial_days: 0,
          is_active: true,
          is_public: true,
          highlight_text: null,
        },
        {
          id: '2',
          code: 'starter',
          name: 'Starter',
          description: 'For growing teams',
          plan_type: 'starter',
          base_price_monthly: 999,
          per_employee_monthly: 49,
          base_price_annual: 9990,
          per_employee_annual: 490,
          currency: 'INR',
          max_employees: 25,
          max_users: 5,
          max_companies: 1,
          storage_gb: 5,
          api_calls_monthly: 10000,
          ai_queries_monthly: 50,
          features: {
            payroll: true,
            leave_management: true,
            attendance: true,
            documents: true,
            accounting: true,
            gst_compliance: false,
            ai_assistant: true,
            custom_reports: false,
          },
          modules_enabled: ['payroll', 'leave', 'attendance', 'documents', 'accounting'],
          trial_days: 14,
          is_active: true,
          is_public: true,
          highlight_text: null,
        },
        {
          id: '3',
          code: 'professional',
          name: 'Professional',
          description: 'For established businesses',
          plan_type: 'professional',
          base_price_monthly: 2999,
          per_employee_monthly: 79,
          base_price_annual: 29990,
          per_employee_annual: 790,
          currency: 'INR',
          max_employees: 100,
          max_users: 20,
          max_companies: 3,
          storage_gb: 25,
          api_calls_monthly: 100000,
          ai_queries_monthly: 500,
          features: {
            payroll: true,
            leave_management: true,
            attendance: true,
            documents: true,
            accounting: true,
            gst_compliance: true,
            crm: true,
            projects: true,
            ai_assistant: true,
            custom_reports: true,
            api_access: true,
          },
          modules_enabled: ['all'],
          trial_days: 14,
          is_active: true,
          is_public: true,
          highlight_text: 'Most Popular',
        },
        {
          id: '4',
          code: 'enterprise',
          name: 'Enterprise',
          description: 'For large organizations',
          plan_type: 'enterprise',
          base_price_monthly: 9999,
          per_employee_monthly: 99,
          base_price_annual: 99990,
          per_employee_annual: 990,
          currency: 'INR',
          max_employees: null,
          max_users: null,
          max_companies: 10,
          storage_gb: 100,
          api_calls_monthly: 1000000,
          ai_queries_monthly: 10000,
          features: {
            payroll: true,
            leave_management: true,
            attendance: true,
            documents: true,
            accounting: true,
            gst_compliance: true,
            crm: true,
            projects: true,
            ai_assistant: true,
            custom_reports: true,
            api_access: true,
            sso: true,
            audit_logs: true,
            dedicated_support: true,
            custom_branding: true,
          },
          modules_enabled: ['all'],
          trial_days: 30,
          is_active: true,
          is_public: true,
          highlight_text: null,
        },
      ])
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchPlans()
  }, [])

  const handleSelectPlan = (plan: SubscriptionPlan) => {
    if (plan.plan_type === 'enterprise') {
      // Contact sales
      window.location.href = 'mailto:sales@ganakys.com?subject=Enterprise Plan Inquiry'
    } else {
      // Navigate to checkout
      // TODO: Implement checkout navigation
    }
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Subscription Plans"
        description="Choose the right plan for your business"
        actions={
          <div className="flex gap-2">
            <Link href="/subscription">
              <Button variant="outline">
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back to Billing
              </Button>
            </Link>
            <Button variant="outline" onClick={fetchPlans} disabled={isLoading}>
              <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
          </div>
        }
      />

      {/* Billing Toggle */}
      <Card className="p-4">
        <div className="flex items-center justify-center gap-4">
          <Label htmlFor="billing-toggle" className={!isAnnual ? 'font-bold' : ''}>
            Monthly
          </Label>
          <Switch
            id="billing-toggle"
            checked={isAnnual}
            onCheckedChange={setIsAnnual}
          />
          <Label htmlFor="billing-toggle" className={isAnnual ? 'font-bold' : ''}>
            Annual
            <Badge variant="secondary" className="ml-2">
              Save 16%
            </Badge>
          </Label>
        </div>
      </Card>

      {/* Loading State */}
      {isLoading && (
        <Card className="p-8 flex items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <span className="ml-2">Loading plans...</span>
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

      {/* Plans Grid */}
      {!isLoading && (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
          {plans.map((plan) => (
            <PlanCard
              key={plan.id}
              plan={plan}
              isAnnual={isAnnual}
              isCurrentPlan={false}
              onSelect={handleSelectPlan}
            />
          ))}
        </div>
      )}

      {/* FAQ / Additional Info */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Frequently Asked Questions</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <p className="font-medium">Can I change plans later?</p>
            <p className="text-sm text-muted-foreground">
              Yes, you can upgrade or downgrade your plan at any time. Changes take effect immediately.
            </p>
          </div>
          <div>
            <p className="font-medium">What payment methods are accepted?</p>
            <p className="text-sm text-muted-foreground">
              We accept all major credit/debit cards, UPI, net banking, and bank transfers.
            </p>
          </div>
          <div>
            <p className="font-medium">Is there a setup fee?</p>
            <p className="text-sm text-muted-foreground">
              No, there are no setup fees. Start your free trial today.
            </p>
          </div>
          <div>
            <p className="font-medium">What happens when my trial ends?</p>
            <p className="text-sm text-muted-foreground">
              Your trial will convert to a paid subscription. You can cancel anytime before the trial ends.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
