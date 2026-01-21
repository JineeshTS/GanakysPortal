'use client'

import * as React from 'react'
import Link from 'next/link'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { formatCurrency, formatDate } from '@/lib/format'
import {
  Mail,
  Phone,
  Building2,
  Calendar,
  Eye,
  Edit,
  MoreVertical,
  MapPin
} from 'lucide-react'
import type { Employee, EmploymentStatus, EmploymentType } from '@/types'

// ============================================================================
// Types
// ============================================================================

interface EmployeeCardProps {
  employee: Employee & {
    department_name?: string
    designation_name?: string
  }
  onQuickView?: (employee: Employee) => void
  variant?: 'default' | 'compact' | 'detailed'
  className?: string
}

// ============================================================================
// Helper Functions
// ============================================================================

const getStatusBadge = (status: EmploymentStatus) => {
  const statusConfig = {
    active: { label: 'Active', className: 'bg-green-100 text-green-800' },
    probation: { label: 'Probation', className: 'bg-blue-100 text-blue-800' },
    notice_period: { label: 'Notice Period', className: 'bg-yellow-100 text-yellow-800' },
    resigned: { label: 'Resigned', className: 'bg-gray-100 text-gray-800' },
    terminated: { label: 'Terminated', className: 'bg-red-100 text-red-800' },
    retired: { label: 'Retired', className: 'bg-purple-100 text-purple-800' },
    absconding: { label: 'Absconding', className: 'bg-red-100 text-red-800' }
  }

  const config = statusConfig[status] || statusConfig.active
  return <Badge className={config.className}>{config.label}</Badge>
}

const getTypeBadge = (type: EmploymentType) => {
  const typeConfig = {
    full_time: { label: 'Full Time', className: 'bg-blue-50 text-blue-700' },
    part_time: { label: 'Part Time', className: 'bg-purple-50 text-purple-700' },
    contract: { label: 'Contract', className: 'bg-orange-50 text-orange-700' },
    intern: { label: 'Intern', className: 'bg-teal-50 text-teal-700' },
    consultant: { label: 'Consultant', className: 'bg-pink-50 text-pink-700' }
  }

  const config = typeConfig[type] || typeConfig.full_time
  return <Badge variant="outline" className={config.className}>{config.label}</Badge>
}

// ============================================================================
// Component
// ============================================================================

export function EmployeeCard({
  employee,
  onQuickView,
  variant = 'default',
  className
}: EmployeeCardProps) {
  // Compact variant
  if (variant === 'compact') {
    return (
      <Card className={className}>
        <CardContent className="p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-primary/10 rounded-full flex items-center justify-center shrink-0">
              <span className="text-sm font-medium text-primary">
                {employee.first_name.charAt(0)}{employee.last_name.charAt(0)}
              </span>
            </div>
            <div className="min-w-0 flex-1">
              <p className="font-medium truncate">{employee.full_name}</p>
              <p className="text-sm text-muted-foreground truncate">
                {employee.designation_name || employee.employee_code}
              </p>
            </div>
            {getStatusBadge(employee.employment_status)}
          </div>
        </CardContent>
      </Card>
    )
  }

  // Detailed variant
  if (variant === 'detailed') {
    return (
      <Card className={className}>
        <CardContent className="p-6">
          <div className="flex items-start gap-4">
            <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center shrink-0">
              <span className="text-xl font-semibold text-primary">
                {employee.first_name.charAt(0)}{employee.last_name.charAt(0)}
              </span>
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="font-semibold text-lg">{employee.full_name}</h3>
                  <p className="text-sm text-muted-foreground">{employee.employee_code}</p>
                </div>
                <div className="flex items-center gap-1">
                  {onQuickView && (
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => onQuickView(employee)}
                    >
                      <Eye className="h-4 w-4" />
                    </Button>
                  )}
                  <Button variant="ghost" size="icon" asChild>
                    <Link href={`/employees/${employee.id}/edit`}>
                      <Edit className="h-4 w-4" />
                    </Link>
                  </Button>
                </div>
              </div>

              <div className="flex flex-wrap gap-2 mt-2">
                {getStatusBadge(employee.employment_status)}
                {getTypeBadge(employee.employment_type)}
              </div>

              <div className="grid grid-cols-2 gap-4 mt-4">
                <div className="flex items-center gap-2 text-sm">
                  <Building2 className="h-4 w-4 text-muted-foreground" />
                  <span>{employee.department_name || '-'}</span>
                </div>
                <div className="flex items-center gap-2 text-sm">
                  <MapPin className="h-4 w-4 text-muted-foreground" />
                  <span>{employee.designation_name || '-'}</span>
                </div>
                <div className="flex items-center gap-2 text-sm">
                  <Mail className="h-4 w-4 text-muted-foreground" />
                  <span className="truncate">{employee.work_email}</span>
                </div>
                <div className="flex items-center gap-2 text-sm">
                  <Phone className="h-4 w-4 text-muted-foreground" />
                  <span>{employee.mobile}</span>
                </div>
                <div className="flex items-center gap-2 text-sm">
                  <Calendar className="h-4 w-4 text-muted-foreground" />
                  <span>Joined {formatDate(employee.date_of_joining, { format: 'long' })}</span>
                </div>
                <div className="text-sm font-medium">
                  CTC: {formatCurrency(employee.ctc)}/year
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    )
  }

  // Default variant
  return (
    <Card className={className}>
      <CardContent className="p-4">
        <div className="flex items-start gap-4">
          <div className="w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center shrink-0">
            <span className="text-lg font-medium text-primary">
              {employee.first_name.charAt(0)}{employee.last_name.charAt(0)}
            </span>
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-start justify-between">
              <div>
                <Link
                  href={`/employees/${employee.id}`}
                  className="font-medium hover:underline"
                >
                  {employee.full_name}
                </Link>
                <p className="text-sm text-muted-foreground">{employee.employee_code}</p>
              </div>
              {getStatusBadge(employee.employment_status)}
            </div>

            <div className="mt-2 space-y-1">
              <p className="text-sm">
                {employee.designation_name} - {employee.department_name}
              </p>
              <div className="flex items-center gap-4 text-sm text-muted-foreground">
                <div className="flex items-center gap-1">
                  <Mail className="h-3 w-3" />
                  <span className="truncate max-w-[150px]">{employee.work_email}</span>
                </div>
                <div className="flex items-center gap-1">
                  <Phone className="h-3 w-3" />
                  <span>{employee.mobile}</span>
                </div>
              </div>
            </div>

            <div className="flex items-center justify-between mt-3 pt-3 border-t">
              <div className="flex items-center gap-1 text-sm text-muted-foreground">
                <Calendar className="h-3 w-3" />
                <span>{formatDate(employee.date_of_joining, { format: 'long' })}</span>
              </div>
              <div className="flex items-center gap-1">
                {onQuickView && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => onQuickView(employee)}
                  >
                    <Eye className="h-3 w-3 mr-1" />
                    View
                  </Button>
                )}
                <Button variant="ghost" size="sm" asChild>
                  <Link href={`/employees/${employee.id}/edit`}>
                    <Edit className="h-3 w-3 mr-1" />
                    Edit
                  </Link>
                </Button>
              </div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

// ============================================================================
// Grid Component for displaying multiple cards
// ============================================================================

interface EmployeeGridProps {
  employees: Array<Employee & {
    department_name?: string
    designation_name?: string
  }>
  variant?: 'default' | 'compact' | 'detailed'
  onQuickView?: (employee: Employee) => void
  columns?: 1 | 2 | 3 | 4
}

export function EmployeeGrid({
  employees,
  variant = 'default',
  onQuickView,
  columns = 3
}: EmployeeGridProps) {
  const gridCols = {
    1: 'grid-cols-1',
    2: 'grid-cols-1 md:grid-cols-2',
    3: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3',
    4: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4'
  }

  return (
    <div className={`grid gap-4 ${gridCols[columns]}`}>
      {employees.map((employee) => (
        <EmployeeCard
          key={employee.id}
          employee={employee}
          variant={variant}
          onQuickView={onQuickView}
        />
      ))}
    </div>
  )
}

// ============================================================================
// Mini Card for quick selection/display
// ============================================================================

interface EmployeeMiniCardProps {
  employee: {
    id: string
    full_name: string
    first_name: string
    last_name: string
    employee_code: string
    designation_name?: string
    photo_url?: string
  }
  selected?: boolean
  onSelect?: (id: string) => void
  className?: string
}

export function EmployeeMiniCard({
  employee,
  selected = false,
  onSelect,
  className
}: EmployeeMiniCardProps) {
  return (
    <div
      className={`
        flex items-center gap-3 p-3 rounded-lg border cursor-pointer transition-colors
        ${selected ? 'border-primary bg-primary/5' : 'hover:bg-muted'}
        ${className}
      `}
      onClick={() => onSelect?.(employee.id)}
    >
      <div className="w-8 h-8 bg-primary/10 rounded-full flex items-center justify-center shrink-0">
        <span className="text-xs font-medium text-primary">
          {employee.first_name.charAt(0)}{employee.last_name.charAt(0)}
        </span>
      </div>
      <div className="min-w-0 flex-1">
        <p className="text-sm font-medium truncate">{employee.full_name}</p>
        <p className="text-xs text-muted-foreground truncate">
          {employee.designation_name || employee.employee_code}
        </p>
      </div>
      {selected && (
        <div className="w-5 h-5 rounded-full bg-primary flex items-center justify-center">
          <svg className="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
        </div>
      )}
    </div>
  )
}

export default EmployeeCard
