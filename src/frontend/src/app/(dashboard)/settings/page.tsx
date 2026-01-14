"use client"

import * as React from "react"
import { useState, useEffect, useCallback } from "react"
import Link from "next/link"
import { PageHeader } from "@/components/layout/page-header"
import { SettingsCard, SettingsCategoryGrid, SettingsSection } from "@/components/settings/SettingsCard"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { useAuthStore } from "@/hooks"
import {
  Building2,
  Users,
  Wallet,
  Calendar,
  Clock,
  Mail,
  Link2,
  Shield,
  FileText,
  IndianRupee,
  Landmark,
  Calculator,
  Bell,
  Palette,
  Database,
  HelpCircle,
  Sparkles,
  TrendingUp,
  Package,
  Network,
  CheckCircle2,
  AlertCircle,
  Rocket,
} from "lucide-react"

interface SetupStatus {
  company_profile_complete: boolean
  extended_profile_complete: boolean
  departments_exist: boolean
  designations_exist: boolean
  overall_complete: boolean
  completion_percentage: number
}

// ============================================================================
// Settings Overview Page
// ============================================================================

export default function SettingsPage() {
  const { accessToken } = useAuthStore()
  const API_BASE = process.env.NEXT_PUBLIC_API_URL || '/api/v1'

  const [status, setStatus] = useState<SetupStatus | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  const fetchStatus = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE}/company/setup-status`, {
        headers: { 'Authorization': `Bearer ${accessToken}` },
      })
      if (response.ok) {
        const data = await response.json()
        setStatus({
          company_profile_complete: data.company_profile_complete || false,
          extended_profile_complete: data.extended_profile_complete || false,
          departments_exist: data.departments_exist || false,
          designations_exist: data.designations_exist || false,
          overall_complete: data.overall_complete || false,
          completion_percentage: data.completion_percentage || 0,
        })
      }
    } catch (error) {
      console.error('Failed to fetch setup status:', error)
    } finally {
      setIsLoading(false)
    }
  }, [API_BASE, accessToken])

  useEffect(() => {
    fetchStatus()
  }, [fetchStatus])

  const isSetupComplete = status?.overall_complete || false
  const completionPercent = status?.completion_percentage || 0

  return (
    <div className="space-y-6">
      <PageHeader
        title="Settings"
        description="Manage your organization's settings and configurations"
        breadcrumbs={[
          { label: "Dashboard", href: "/" },
          { label: "Settings" }
        ]}
      />

      {/* Setup Progress Indicator */}
      {!isLoading && !isSetupComplete && (
        <Card className="border-yellow-200 bg-yellow-50/50 dark:border-yellow-900 dark:bg-yellow-950/20">
          <CardContent className="p-4">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-full bg-yellow-100 dark:bg-yellow-900 flex items-center justify-center flex-shrink-0">
                <AlertCircle className="h-6 w-6 text-yellow-600 dark:text-yellow-400" />
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-medium">Complete Your Setup</h3>
                  <span className="text-sm font-medium text-yellow-700 dark:text-yellow-400">{completionPercent}%</span>
                </div>
                <Progress value={completionPercent} className="h-2 mb-2" />
                <p className="text-sm text-muted-foreground">
                  Complete the setup wizard to start using all features
                </p>
              </div>
              <Link href="/settings/setup-wizard">
                <Button size="sm" className="flex-shrink-0">
                  <Rocket className="h-4 w-4 mr-2" />
                  Setup Wizard
                </Button>
              </Link>
            </div>
          </CardContent>
        </Card>
      )}

      {!isLoading && isSetupComplete && (
        <Card className="border-green-200 bg-green-50/50 dark:border-green-900 dark:bg-green-950/20">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <CheckCircle2 className="h-5 w-5 text-green-600 dark:text-green-400" />
              <span className="text-green-700 dark:text-green-400 font-medium">
                Setup complete! Your system is ready to use.
              </span>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Main Settings Categories */}
      <SettingsSection
        title="Organization"
        description="Configure your company and user settings"
      >
        <SettingsCategoryGrid columns={3}>
          <SettingsCard
            title="Company Settings"
            description="Company details, GSTIN, PAN, addresses, and branches"
            icon={Building2}
            href="/settings/company"
          />
          <SettingsCard
            title="Organization Setup"
            description="Company profile, org structure, departments, AI recommendations"
            icon={Network}
            href="/settings/organization"
            badge="AI Powered"
            badgeVariant="success"
          />
          <SettingsCard
            title="User Management"
            description="Manage users, roles, and access permissions"
            icon={Users}
            href="/settings/users"
            badge="5 Users"
            badgeVariant="default"
          />
          <SettingsCard
            title="Roles & Permissions"
            description="Configure role-based access control"
            icon={Shield}
            href="/settings/users?tab=roles"
          />
        </SettingsCategoryGrid>
      </SettingsSection>

      {/* Payroll & Compliance */}
      <SettingsSection
        title="Payroll & Compliance"
        description="Configure salary components and statutory compliance"
      >
        <SettingsCategoryGrid columns={3}>
          <SettingsCard
            title="Payroll Configuration"
            description="Salary components, earnings, deductions, and pay schedule"
            icon={Wallet}
            href="/settings/payroll"
          />
          <SettingsCard
            title="PF Settings"
            description="EPF contribution rates, ceilings, and opt-out rules"
            icon={Landmark}
            href="/settings/payroll?tab=pf"
            badge="12% Rate"
          />
          <SettingsCard
            title="ESI Settings"
            description="ESI contribution rates and wage ceiling"
            icon={Calculator}
            href="/settings/payroll?tab=esi"
            badge="21,000 Ceiling"
          />
          <SettingsCard
            title="PT Settings"
            description="State-wise Professional Tax configuration"
            icon={IndianRupee}
            href="/settings/payroll?tab=pt"
          />
          <SettingsCard
            title="TDS Settings"
            description="Income tax regime and TDS calculation rules"
            icon={FileText}
            href="/settings/payroll?tab=tds"
          />
        </SettingsCategoryGrid>
      </SettingsSection>

      {/* Leave & Attendance */}
      <SettingsSection
        title="Leave & Attendance"
        description="Configure leave policies and attendance rules"
      >
        <SettingsCategoryGrid columns={3}>
          <SettingsCard
            title="Leave Configuration"
            description="Leave types, entitlements, carry forward, and encashment"
            icon={Calendar}
            href="/settings/leave"
          />
          <SettingsCard
            title="Holiday Calendar"
            description="Manage public holidays and optional holidays"
            icon={Calendar}
            href="/settings/leave?tab=holidays"
          />
          <SettingsCard
            title="Attendance Settings"
            description="Shifts, grace period, overtime, and regularization rules"
            icon={Clock}
            href="/settings/attendance"
          />
        </SettingsCategoryGrid>
      </SettingsSection>

      {/* Document Management */}
      <SettingsSection
        title="Document Management"
        description="Configure document categories and types"
      >
        <SettingsCategoryGrid columns={3}>
          <SettingsCard
            title="Document Categories"
            description="Manage categories for organizing documents"
            icon={FileText}
            href="/settings/documents"
          />
          <SettingsCard
            title="Document Types"
            description="Configure document types within categories"
            icon={FileText}
            href="/settings/documents?tab=types"
          />
        </SettingsCategoryGrid>
      </SettingsSection>

      {/* Communications & Integrations */}
      <SettingsSection
        title="Communications & Integrations"
        description="Email templates and external system connections"
      >
        <SettingsCategoryGrid columns={3}>
          <SettingsCard
            title="Email Templates"
            description="Customize email notifications and templates"
            icon={Mail}
            href="/settings/email"
          />
          <SettingsCard
            title="Integrations"
            description="Bank, EPFO, ESIC, and GST portal connections"
            icon={Link2}
            href="/settings/integrations"
            badge="3 Active"
            badgeVariant="success"
          />
          <SettingsCard
            title="Notifications"
            description="Configure notification preferences"
            icon={Bell}
            href="/settings/notifications"
            disabled
            badge="Coming Soon"
          />
        </SettingsCategoryGrid>
      </SettingsSection>

      {/* Quick Links */}
      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Quick Actions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <QuickLink
                title="Organization Setup"
                href="/settings/organization"
                icon={Network}
              />
              <QuickLink
                title="Add Product/Service"
                href="/settings/organization?tab=products"
                icon={Package}
              />
              <QuickLink
                title="AI Org Builder"
                href="/settings/organization?tab=ai-builder"
                icon={Sparkles}
              />
              <QuickLink
                title="Add New User"
                href="/settings/users?action=add"
                icon={Users}
              />
              <QuickLink
                title="Add Salary Component"
                href="/settings/payroll?action=add-component"
                icon={Wallet}
              />
              <QuickLink
                title="Add Leave Type"
                href="/settings/leave?action=add-type"
                icon={Calendar}
              />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">System Information</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <SystemInfoRow label="Version" value="1.0.0" />
              <SystemInfoRow label="Financial Year" value="2024-25 (Apr - Mar)" />
              <SystemInfoRow label="Active Employees" value="156" />
              <SystemInfoRow label="Last Payroll Run" value="Dec 2024" />
              <SystemInfoRow label="Database" value="PostgreSQL 15" />
              <SystemInfoRow label="Environment" value="Production" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Help & Support */}
      <Card>
        <CardContent className="flex items-center justify-between py-4">
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center">
              <HelpCircle className="h-5 w-5 text-primary" />
            </div>
            <div>
              <div className="font-medium">Need Help?</div>
              <div className="text-sm text-muted-foreground">
                Check our documentation or contact support for assistance
              </div>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <a
              href="https://docs.ganaportal.in"
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm text-primary hover:underline"
            >
              Documentation
            </a>
            <span className="text-muted-foreground">|</span>
            <a
              href="mailto:support@ganaportal.in"
              className="text-sm text-primary hover:underline"
            >
              Contact Support
            </a>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

// ============================================================================
// Helper Components
// ============================================================================

interface QuickLinkProps {
  title: string
  href: string
  icon: React.ElementType
}

function QuickLink({ title, href, icon: Icon }: QuickLinkProps) {
  return (
    <a
      href={href}
      className="flex items-center gap-3 p-2 rounded-md hover:bg-muted transition-colors"
    >
      <Icon className="h-4 w-4 text-muted-foreground" />
      <span className="text-sm">{title}</span>
    </a>
  )
}

interface SystemInfoRowProps {
  label: string
  value: string
}

function SystemInfoRow({ label, value }: SystemInfoRowProps) {
  return (
    <div className="flex items-center justify-between py-1 border-b last:border-b-0">
      <span className="text-sm text-muted-foreground">{label}</span>
      <span className="text-sm font-medium">{value}</span>
    </div>
  )
}
