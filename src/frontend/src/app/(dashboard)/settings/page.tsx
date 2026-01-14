"use client"

import * as React from "react"
import { PageHeader } from "@/components/layout/page-header"
import { SettingsCard, SettingsCategoryGrid, SettingsSection } from "@/components/settings/SettingsCard"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
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
} from "lucide-react"

// ============================================================================
// Settings Overview Page
// ============================================================================

export default function SettingsPage() {
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
            href="/settings/organization-setup"
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
                title="Setup Company Profile"
                href="/settings/company-profile"
                icon={TrendingUp}
              />
              <QuickLink
                title="Add Product/Service"
                href="/settings/company-profile?tab=products"
                icon={Package}
              />
              <QuickLink
                title="AI Org Builder"
                href="/org-builder"
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
