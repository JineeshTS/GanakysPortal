"use client"

import * as React from "react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils"
import { useAuthStore, useHasPermission } from "@/hooks"
import {
  LayoutDashboard,
  Users,
  Building2,
  Wallet,
  Calendar,
  Clock,
  FileText,
  Receipt,
  CreditCard,
  Landmark,
  TrendingUp,
  FolderKanban,
  MessageSquare,
  Settings,
  ChevronDown,
  ChevronRight,
  LogOut,
  BarChart3,
  Target,
  CheckSquare,
  UserPlus,
  Network,
  GraduationCap,
  Award,
  UserMinus,
  Megaphone,
  Briefcase,
  UserCircle,
  Sparkles,
} from "lucide-react"

// ============================================================================
// Navigation Items
// ============================================================================

interface NavItem {
  title: string
  href?: string
  icon: React.ElementType
  permission?: string
  children?: NavItem[]
}

const navigationItems: NavItem[] = [
  {
    title: "Dashboard",
    href: "/",
    icon: LayoutDashboard
  },
  {
    title: "HRMS",
    icon: Users,
    permission: "employees.view",
    children: [
      { title: "Recruitment", href: "/recruitment", icon: Briefcase, permission: "employees.manage" },
      { title: "Onboarding", href: "/onboarding", icon: UserPlus, permission: "employees.manage" },
      { title: "Employees", href: "/employees", icon: Users, permission: "employees.view" },
      { title: "Attendance", href: "/attendance", icon: Clock, permission: "attendance.view" },
      { title: "Leave", href: "/leave", icon: Calendar, permission: "leave.view" },
      { title: "Performance", href: "/performance", icon: Award, permission: "employees.view" },
      { title: "Training", href: "/training", icon: GraduationCap, permission: "employees.view" },
      { title: "Exit", href: "/exit", icon: UserMinus, permission: "employees.manage" },
      { title: "Announcements", href: "/announcements", icon: Megaphone, permission: "employees.view" }
    ]
  },
  {
    title: "Document Manager",
    href: "/documents",
    icon: FileText,
    permission: "employees.view"
  },
  {
    title: "My Portal",
    icon: UserCircle,
    children: [
      { title: "My Profile", href: "/my/profile", icon: UserCircle },
      { title: "My Attendance", href: "/my/attendance", icon: Clock },
      { title: "My Leave", href: "/my/leave", icon: Calendar },
      { title: "My Payslips", href: "/my/payslips", icon: Receipt },
      { title: "My Documents", href: "/my/documents", icon: FileText },
      { title: "Alumni Portal", href: "/alumni", icon: GraduationCap }
    ]
  },
  {
    title: "Payroll",
    icon: Wallet,
    permission: "payroll.view",
    children: [
      { title: "Run Payroll", href: "/payroll/run", icon: Wallet, permission: "payroll.process" },
      { title: "Payslips", href: "/payroll/payslips", icon: Receipt, permission: "payroll.view" },
      { title: "Reports", href: "/payroll/reports", icon: FileText, permission: "payroll.view" }
    ]
  },
  {
    title: "Finance",
    icon: Landmark,
    permission: "finance.view",
    children: [
      { title: "Chart of Accounts", href: "/accounts", icon: Landmark, permission: "finance.view" },
      { title: "Journal Entries", href: "/journals", icon: FileText, permission: "finance.view" },
      { title: "Invoices", href: "/invoices", icon: Receipt, permission: "invoices.view" },
      { title: "Bills", href: "/bills", icon: Receipt, permission: "bills.view" },
      { title: "Payments", href: "/payments", icon: CreditCard, permission: "finance.view" },
      { title: "Bank Accounts", href: "/banking", icon: Landmark, permission: "finance.view" }
    ]
  },
  {
    title: "CRM",
    icon: Target,
    permission: "crm.view",
    children: [
      { title: "Pipeline", href: "/crm", icon: TrendingUp, permission: "crm.view" },
      { title: "Customers", href: "/crm/customers", icon: Users, permission: "crm.view" }
    ]
  },
  {
    title: "Statutory",
    icon: FileText,
    permission: "payroll.view",
    children: [
      { title: "Overview", href: "/statutory", icon: FileText, permission: "payroll.view" },
      { title: "PF", href: "/statutory/pf", icon: FileText, permission: "payroll.view" },
      { title: "ESI", href: "/statutory/esi", icon: FileText, permission: "payroll.view" },
      { title: "TDS", href: "/statutory/tds", icon: FileText, permission: "payroll.view" }
    ]
  },
  {
    title: "Projects",
    icon: FolderKanban,
    permission: "projects.view",
    children: [
      { title: "All Projects", href: "/projects", icon: FolderKanban, permission: "projects.view" },
      { title: "Tasks", href: "/tasks", icon: CheckSquare, permission: "projects.view" },
      { title: "Timesheets", href: "/timesheet", icon: Clock, permission: "projects.view" }
    ]
  },
  {
    title: "Reports",
    href: "/reports",
    icon: BarChart3,
    permission: "reports.view"
  },
  {
    title: "AI Assistant",
    href: "/ai",
    icon: MessageSquare
  },
  {
    title: "Settings",
    icon: Settings,
    permission: "settings.view",
    children: [
      { title: "Overview", href: "/settings", icon: Settings, permission: "settings.view" },
      { title: "Organization Setup", href: "/settings/organization-setup", icon: Network, permission: "settings.view" },
      { title: "Company", href: "/settings/company", icon: Building2, permission: "settings.view" },
      { title: "Users & Roles", href: "/settings/users", icon: Users, permission: "settings.view" },
      { title: "Leave Policies", href: "/settings/leave", icon: Calendar, permission: "settings.view" },
      { title: "Payroll Config", href: "/settings/payroll", icon: Wallet, permission: "settings.view" },
      { title: "Attendance", href: "/settings/attendance", icon: Clock, permission: "settings.view" },
      { title: "Documents", href: "/settings/documents", icon: FileText, permission: "settings.view" },
      { title: "Email", href: "/settings/email", icon: MessageSquare, permission: "settings.view" }
    ]
  }
]

// ============================================================================
// Sidebar Component
// ============================================================================

interface SidebarProps {
  collapsed?: boolean
  onCollapsedChange?: (collapsed: boolean) => void
}

export function Sidebar({ collapsed = false, onCollapsedChange }: SidebarProps) {
  const pathname = usePathname()
  const { user, logout } = useAuthStore()
  const [expandedItems, setExpandedItems] = React.useState<string[]>([])

  const toggleExpanded = (title: string) => {
    setExpandedItems(prev =>
      prev.includes(title)
        ? prev.filter(item => item !== title)
        : [...prev, title]
    )
  }

  const isActive = (href?: string) => {
    if (!href) return false
    return pathname === href || pathname.startsWith(`${href}/`)
  }

  const hasChildActive = (children?: NavItem[]) => {
    if (!children) return false
    return children.some(child => isActive(child.href))
  }

  return (
    <aside
      className={cn(
        "flex flex-col h-screen bg-card border-r transition-all duration-300",
        collapsed ? "w-16" : "w-64"
      )}
    >
      {/* Logo */}
      <div className="flex items-center h-16 px-4 border-b">
        <Link href="/dashboard" className="flex items-center gap-2">
          <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
            <span className="text-primary-foreground font-bold text-sm">GP</span>
          </div>
          {!collapsed && (
            <span className="font-semibold text-lg">GanaPortal</span>
          )}
        </Link>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto py-4 px-2">
        <ul className="space-y-1">
          {navigationItems.map((item) => (
            <NavMenuItem
              key={item.title}
              item={item}
              collapsed={collapsed}
              isExpanded={expandedItems.includes(item.title) || hasChildActive(item.children)}
              onToggle={() => toggleExpanded(item.title)}
              isActive={isActive(item.href)}
              pathname={pathname}
            />
          ))}
        </ul>
      </nav>

      {/* User Section */}
      <div className="border-t p-4">
        {collapsed ? (
          <button
            onClick={logout}
            className="w-full flex items-center justify-center p-2 rounded-md hover:bg-muted transition-colors"
            title="Logout"
          >
            <LogOut className="h-5 w-5" />
          </button>
        ) : (
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 min-w-0">
              <div className="w-8 h-8 bg-muted rounded-full flex items-center justify-center flex-shrink-0">
                <span className="text-xs font-medium">
                  {user?.full_name?.charAt(0).toUpperCase()}
                </span>
              </div>
              <div className="min-w-0">
                <p className="text-sm font-medium truncate">{user?.full_name}</p>
                <p className="text-xs text-muted-foreground truncate">{user?.role}</p>
              </div>
            </div>
            <button
              onClick={logout}
              className="p-2 rounded-md hover:bg-muted transition-colors"
              title="Logout"
            >
              <LogOut className="h-4 w-4" />
            </button>
          </div>
        )}
      </div>
    </aside>
  )
}

// ============================================================================
// Nav Menu Item Component
// ============================================================================

interface NavMenuItemProps {
  item: NavItem
  collapsed: boolean
  isExpanded: boolean
  onToggle: () => void
  isActive: boolean
  pathname: string
}

function NavMenuItem({ item, collapsed, isExpanded, onToggle, isActive, pathname }: NavMenuItemProps) {
  const hasPermission = useHasPermission(item.permission || '')
  const Icon = item.icon

  // Check permission (if no permission required, always show)
  if (item.permission && !hasPermission) {
    return null
  }

  // Has children - render as expandable
  if (item.children && item.children.length > 0) {
    return (
      <li>
        <button
          onClick={onToggle}
          className={cn(
            "w-full flex items-center gap-2 px-3 py-2 rounded-md text-sm transition-colors",
            "hover:bg-muted",
            isExpanded && "bg-muted"
          )}
        >
          <Icon className="h-5 w-5 flex-shrink-0" />
          {!collapsed && (
            <>
              <span className="flex-1 text-left">{item.title}</span>
              {isExpanded ? (
                <ChevronDown className="h-4 w-4" />
              ) : (
                <ChevronRight className="h-4 w-4" />
              )}
            </>
          )}
        </button>

        {/* Children */}
        {isExpanded && !collapsed && (
          <ul className="mt-1 ml-4 pl-4 border-l space-y-1">
            {item.children.map((child) => (
              <NavChildItem
                key={child.title}
                item={child}
                isActive={pathname === child.href}
              />
            ))}
          </ul>
        )}
      </li>
    )
  }

  // No children - render as link
  return (
    <li>
      <Link
        href={item.href || '#'}
        className={cn(
          "flex items-center gap-2 px-3 py-2 rounded-md text-sm transition-colors",
          "hover:bg-muted",
          isActive && "bg-primary text-primary-foreground hover:bg-primary/90"
        )}
      >
        <Icon className="h-5 w-5 flex-shrink-0" />
        {!collapsed && <span>{item.title}</span>}
      </Link>
    </li>
  )
}

// ============================================================================
// Nav Child Item Component
// ============================================================================

interface NavChildItemProps {
  item: NavItem
  isActive: boolean
}

function NavChildItem({ item, isActive }: NavChildItemProps) {
  const hasPermission = useHasPermission(item.permission || '')
  const Icon = item.icon

  if (item.permission && !hasPermission) {
    return null
  }

  return (
    <li>
      <Link
        href={item.href || '#'}
        className={cn(
          "flex items-center gap-2 px-3 py-1.5 rounded-md text-sm transition-colors",
          "hover:bg-muted",
          isActive && "bg-primary text-primary-foreground hover:bg-primary/90"
        )}
      >
        <Icon className="h-4 w-4 flex-shrink-0" />
        <span>{item.title}</span>
      </Link>
    </li>
  )
}

export default Sidebar
