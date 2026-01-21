"use client"

import * as React from "react"
import { cn } from "@/lib/utils"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import {
  Shield,
  Users,
  Eye,
  Edit,
  Trash2,
  Plus,
  Check,
  X,
  ChevronDown,
  ChevronRight
} from "lucide-react"

// ============================================================================
// Types
// ============================================================================

export interface Permission {
  id: string
  name: string
  description: string
  module: string
}

export interface Role {
  id: string
  name: string
  description: string
  permissions: string[]
  userCount?: number
  isSystem?: boolean
}

export interface PermissionModule {
  id: string
  name: string
  permissions: Permission[]
}

// ============================================================================
// Default Modules and Permissions for Indian HRMS
// ============================================================================

export const DEFAULT_PERMISSION_MODULES: PermissionModule[] = [
  {
    id: 'employees',
    name: 'Employees',
    permissions: [
      { id: 'employees.view', name: 'View Employees', description: 'View employee list and details', module: 'employees' },
      { id: 'employees.create', name: 'Add Employee', description: 'Create new employee records', module: 'employees' },
      { id: 'employees.edit', name: 'Edit Employee', description: 'Modify employee information', module: 'employees' },
      { id: 'employees.delete', name: 'Delete Employee', description: 'Remove employee records', module: 'employees' },
      { id: 'employees.documents', name: 'Manage Documents', description: 'Upload and manage employee documents', module: 'employees' }
    ]
  },
  {
    id: 'payroll',
    name: 'Payroll',
    permissions: [
      { id: 'payroll.view', name: 'View Payroll', description: 'View payroll data and payslips', module: 'payroll' },
      { id: 'payroll.process', name: 'Process Payroll', description: 'Run monthly payroll processing', module: 'payroll' },
      { id: 'payroll.approve', name: 'Approve Payroll', description: 'Approve payroll before release', module: 'payroll' },
      { id: 'payroll.config', name: 'Payroll Settings', description: 'Configure salary components', module: 'payroll' },
      { id: 'payroll.arrears', name: 'Manage Arrears', description: 'Handle arrear calculations', module: 'payroll' }
    ]
  },
  {
    id: 'compliance',
    name: 'Statutory Compliance',
    permissions: [
      { id: 'compliance.pf', name: 'PF Management', description: 'Manage PF contributions and returns', module: 'compliance' },
      { id: 'compliance.esi', name: 'ESI Management', description: 'Manage ESI contributions and claims', module: 'compliance' },
      { id: 'compliance.pt', name: 'PT Management', description: 'Manage Professional Tax deductions', module: 'compliance' },
      { id: 'compliance.tds', name: 'TDS Management', description: 'Manage TDS calculations and Form 16', module: 'compliance' },
      { id: 'compliance.returns', name: 'File Returns', description: 'Submit statutory returns', module: 'compliance' }
    ]
  },
  {
    id: 'leave',
    name: 'Leave Management',
    permissions: [
      { id: 'leave.view', name: 'View Leave', description: 'View leave applications and balances', module: 'leave' },
      { id: 'leave.apply', name: 'Apply Leave', description: 'Submit leave applications', module: 'leave' },
      { id: 'leave.approve', name: 'Approve Leave', description: 'Approve/reject leave requests', module: 'leave' },
      { id: 'leave.config', name: 'Leave Settings', description: 'Configure leave types and policies', module: 'leave' }
    ]
  },
  {
    id: 'attendance',
    name: 'Attendance',
    permissions: [
      { id: 'attendance.view', name: 'View Attendance', description: 'View attendance records', module: 'attendance' },
      { id: 'attendance.mark', name: 'Mark Attendance', description: 'Mark daily attendance', module: 'attendance' },
      { id: 'attendance.regularize', name: 'Regularize', description: 'Handle attendance regularization', module: 'attendance' },
      { id: 'attendance.config', name: 'Attendance Settings', description: 'Configure shifts and rules', module: 'attendance' }
    ]
  },
  {
    id: 'reports',
    name: 'Reports',
    permissions: [
      { id: 'reports.payroll', name: 'Payroll Reports', description: 'Generate payroll reports', module: 'reports' },
      { id: 'reports.compliance', name: 'Compliance Reports', description: 'Generate statutory reports', module: 'reports' },
      { id: 'reports.attendance', name: 'Attendance Reports', description: 'Generate attendance reports', module: 'reports' },
      { id: 'reports.export', name: 'Export Data', description: 'Export reports to Excel/PDF', module: 'reports' }
    ]
  },
  {
    id: 'settings',
    name: 'Settings',
    permissions: [
      { id: 'settings.company', name: 'Company Settings', description: 'Manage company information', module: 'settings' },
      { id: 'settings.users', name: 'User Management', description: 'Manage users and roles', module: 'settings' },
      { id: 'settings.integrations', name: 'Integrations', description: 'Manage external integrations', module: 'settings' }
    ]
  }
]

export const DEFAULT_ROLES: Role[] = [
  {
    id: 'super_admin',
    name: 'Super Admin',
    description: 'Full access to all features',
    permissions: ['*'],
    isSystem: true
  },
  {
    id: 'hr_manager',
    name: 'HR Manager',
    description: 'Manage employees, leave, and attendance',
    permissions: [
      'employees.*', 'leave.*', 'attendance.*', 'reports.attendance'
    ],
    isSystem: true
  },
  {
    id: 'payroll_manager',
    name: 'Payroll Manager',
    description: 'Process payroll and manage compliance',
    permissions: [
      'payroll.*', 'compliance.*', 'reports.payroll', 'reports.compliance', 'reports.export'
    ],
    isSystem: true
  },
  {
    id: 'team_lead',
    name: 'Team Lead',
    description: 'Approve team leave and view attendance',
    permissions: [
      'employees.view', 'leave.view', 'leave.approve', 'attendance.view'
    ]
  },
  {
    id: 'employee',
    name: 'Employee',
    description: 'Basic employee access',
    permissions: [
      'leave.apply', 'leave.view', 'attendance.view', 'attendance.mark'
    ],
    isSystem: true
  }
]

// ============================================================================
// Permission Checkbox Component
// ============================================================================

interface PermissionCheckboxProps {
  permission: Permission
  checked: boolean
  onChange: (checked: boolean) => void
  disabled?: boolean
}

function PermissionCheckbox({ permission, checked, onChange, disabled }: PermissionCheckboxProps) {
  return (
    <label className={cn(
      "flex items-start gap-3 p-3 rounded-md border cursor-pointer transition-colors",
      checked ? "border-primary bg-primary/5" : "border-border hover:bg-muted/50",
      disabled && "opacity-50 cursor-not-allowed"
    )}>
      <input
        type="checkbox"
        checked={checked}
        onChange={(e) => onChange(e.target.checked)}
        disabled={disabled}
        className="mt-0.5 h-4 w-4 rounded border-input text-primary focus:ring-ring"
      />
      <div className="flex-1 min-w-0">
        <div className="font-medium text-sm">{permission.name}</div>
        <div className="text-xs text-muted-foreground mt-0.5">{permission.description}</div>
      </div>
    </label>
  )
}

// ============================================================================
// Permission Module Component
// ============================================================================

interface PermissionModuleProps {
  module: PermissionModule
  selectedPermissions: string[]
  onPermissionChange: (permissionId: string, checked: boolean) => void
  disabled?: boolean
}

function PermissionModule({ module, selectedPermissions, onPermissionChange, disabled }: PermissionModuleProps) {
  const [expanded, setExpanded] = React.useState(true)

  const permissions = module.permissions || []
  const modulePermissionIds = permissions.map(p => p.id)
  const selectedCount = modulePermissionIds.filter(id => selectedPermissions.includes(id)).length
  const allSelected = permissions.length > 0 && selectedCount === permissions.length
  const someSelected = selectedCount > 0 && !allSelected

  const handleModuleToggle = () => {
    const newChecked = !allSelected
    modulePermissionIds.forEach(id => {
      if (selectedPermissions.includes(id) !== newChecked) {
        onPermissionChange(id, newChecked)
      }
    })
  }

  return (
    <div className="border rounded-lg">
      <div
        className="flex items-center justify-between p-4 cursor-pointer hover:bg-muted/50"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex items-center gap-3">
          <button
            type="button"
            onClick={(e) => {
              e.stopPropagation()
              handleModuleToggle()
            }}
            disabled={disabled}
            className={cn(
              "h-5 w-5 rounded border flex items-center justify-center transition-colors",
              allSelected && "bg-primary border-primary text-primary-foreground",
              someSelected && "bg-primary/50 border-primary",
              !allSelected && !someSelected && "border-input"
            )}
          >
            {allSelected && <Check className="h-3 w-3" />}
            {someSelected && <div className="h-2 w-2 bg-primary-foreground rounded-sm" />}
          </button>
          <div>
            <div className="font-medium">{module.name}</div>
            <div className="text-sm text-muted-foreground">
              {selectedCount} of {module.permissions.length} permissions
            </div>
          </div>
        </div>
        {expanded ? (
          <ChevronDown className="h-5 w-5 text-muted-foreground" />
        ) : (
          <ChevronRight className="h-5 w-5 text-muted-foreground" />
        )}
      </div>
      {expanded && (
        <div className="px-4 pb-4 grid gap-2 sm:grid-cols-2">
          {module.permissions.map(permission => (
            <PermissionCheckbox
              key={permission.id}
              permission={permission}
              checked={selectedPermissions.includes(permission.id)}
              onChange={(checked) => onPermissionChange(permission.id, checked)}
              disabled={disabled}
            />
          ))}
        </div>
      )}
    </div>
  )
}

// ============================================================================
// Role Permissions Component
// ============================================================================

interface RolePermissionsProps {
  modules?: PermissionModule[]
  selectedPermissions: string[]
  onPermissionsChange: (permissions: string[]) => void
  disabled?: boolean
  className?: string
}

export function RolePermissions({
  modules = DEFAULT_PERMISSION_MODULES,
  selectedPermissions,
  onPermissionsChange,
  disabled = false,
  className
}: RolePermissionsProps) {
  const handlePermissionChange = (permissionId: string, checked: boolean) => {
    if (checked) {
      onPermissionsChange([...selectedPermissions, permissionId])
    } else {
      onPermissionsChange(selectedPermissions.filter(id => id !== permissionId))
    }
  }

  const allPermissions = modules.flatMap(m => m.permissions.map(p => p.id))
  const allSelected = allPermissions.every(id => selectedPermissions.includes(id))

  const handleSelectAll = () => {
    if (allSelected) {
      onPermissionsChange([])
    } else {
      onPermissionsChange(allPermissions)
    }
  }

  return (
    <div className={cn("space-y-4", className)}>
      <div className="flex items-center justify-between">
        <div className="text-sm text-muted-foreground">
          {selectedPermissions.length} permissions selected
        </div>
        <Button
          type="button"
          variant="outline"
          size="sm"
          onClick={handleSelectAll}
          disabled={disabled}
        >
          {allSelected ? 'Deselect All' : 'Select All'}
        </Button>
      </div>

      <div className="space-y-3">
        {modules.map(module => (
          <PermissionModule
            key={module.id}
            module={module}
            selectedPermissions={selectedPermissions}
            onPermissionChange={handlePermissionChange}
            disabled={disabled}
          />
        ))}
      </div>
    </div>
  )
}

// ============================================================================
// Role Card Component
// ============================================================================

interface RoleCardProps {
  role: Role
  onClick?: () => void
  onEdit?: () => void
  onDelete?: () => void
  isSelected?: boolean
}

export function RoleCard({ role, onClick, onEdit, onDelete, isSelected }: RoleCardProps) {
  return (
    <Card
      className={cn(
        "cursor-pointer transition-all",
        isSelected ? "border-primary shadow-md" : "hover:border-primary/50",
        onClick && "hover:shadow-sm"
      )}
      onClick={onClick}
    >
      <CardHeader className="flex flex-row items-start justify-between space-y-0 pb-2">
        <div className="flex items-start gap-3">
          <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center">
            <Shield className="h-5 w-5 text-primary" />
          </div>
          <div>
            <CardTitle className="text-base flex items-center gap-2">
              {role.name}
              {role.isSystem && (
                <Badge variant="secondary" className="text-xs">System</Badge>
              )}
            </CardTitle>
            <p className="text-sm text-muted-foreground mt-1">{role.description}</p>
          </div>
        </div>
        {(!role.isSystem && (onEdit || onDelete)) && (
          <div className="flex items-center gap-1">
            {onEdit && (
              <Button
                variant="ghost"
                size="icon"
                onClick={(e) => {
                  e.stopPropagation()
                  onEdit()
                }}
              >
                <Edit className="h-4 w-4" />
              </Button>
            )}
            {onDelete && (
              <Button
                variant="ghost"
                size="icon"
                onClick={(e) => {
                  e.stopPropagation()
                  onDelete()
                }}
              >
                <Trash2 className="h-4 w-4 text-destructive" />
              </Button>
            )}
          </div>
        )}
      </CardHeader>
      <CardContent>
        <div className="flex items-center gap-4 text-sm text-muted-foreground">
          <div className="flex items-center gap-1">
            <Users className="h-4 w-4" />
            <span>{role.userCount || 0} users</span>
          </div>
          <div className="flex items-center gap-1">
            <Eye className="h-4 w-4" />
            <span>
              {role.permissions.includes('*')
                ? 'All permissions'
                : `${role.permissions.length} permissions`}
            </span>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

export default RolePermissions
