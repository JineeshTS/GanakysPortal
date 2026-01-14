'use client'

import * as React from 'react'
import { cn } from '@/lib/utils'
import { useApi } from '@/hooks/use-api'
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Label } from '@/components/ui/label'
import { MonthYearPicker } from '@/components/forms/date-picker'
import { SearchInput } from '@/components/forms/search-input'
import { DataTable, Column } from '@/components/layout/data-table'
import { formatCurrency, getMonthName, getFinancialYear } from '@/lib/format'
import {
  Check,
  ChevronLeft,
  ChevronRight,
  Calendar,
  Users,
  FileText,
  Calculator,
  Send,
  AlertCircle,
  Upload,
  Download,
  Edit,
  Clock,
  CheckCircle,
  Loader2
} from 'lucide-react'
import type { PayrollEntry } from '@/types'

// ============================================================================
// Types
// ============================================================================

export interface WizardStep {
  id: number
  title: string
  description: string
  icon: React.ElementType
}

export interface AttendanceData {
  employee_id: string
  employee_name: string
  employee_code: string
  department: string
  working_days: number
  present_days: number
  lop_days: number
  ot_hours: number
  paid_leaves: number
  unpaid_leaves: number
}

export interface VariableInputData {
  employee_id: string
  employee_name: string
  employee_code: string
  bonus: number
  incentive: number
  reimbursements: number
  arrears: number
  other_deductions: number
  advance_recovery: number
  loan_recovery: number
}

export interface PayrollPreviewData extends PayrollEntry {
  department: string
  designation: string
}

export interface PayrollWizardProps {
  onComplete?: (data: { month: number; year: number }) => void
  onCancel?: () => void
}

// ============================================================================
// Wizard Steps Definition
// ============================================================================

const steps: WizardStep[] = [
  {
    id: 1,
    title: 'Select Period',
    description: 'Choose payroll month and year',
    icon: Calendar
  },
  {
    id: 2,
    title: 'Review Attendance',
    description: 'Verify working days and LOP',
    icon: Users
  },
  {
    id: 3,
    title: 'Variable Inputs',
    description: 'Add bonus, incentives, deductions',
    icon: FileText
  },
  {
    id: 4,
    title: 'Preview & Calculate',
    description: 'Review salary calculations',
    icon: Calculator
  },
  {
    id: 5,
    title: 'Approve & Process',
    description: 'Final approval and processing',
    icon: Send
  }
]

// ============================================================================
// Mock Data
// ============================================================================

const mockAttendanceData: AttendanceData[] = [
  { employee_id: '1', employee_name: 'Rahul Kumar', employee_code: 'EMP001', department: 'Engineering', working_days: 22, present_days: 21, lop_days: 1, ot_hours: 8, paid_leaves: 0, unpaid_leaves: 1 },
  { employee_id: '2', employee_name: 'Priya Sharma', employee_code: 'EMP002', department: 'Engineering', working_days: 22, present_days: 22, lop_days: 0, ot_hours: 12, paid_leaves: 0, unpaid_leaves: 0 },
  { employee_id: '3', employee_name: 'Amit Patel', employee_code: 'EMP003', department: 'Sales', working_days: 22, present_days: 20, lop_days: 2, ot_hours: 0, paid_leaves: 0, unpaid_leaves: 2 },
  { employee_id: '4', employee_name: 'Sneha Reddy', employee_code: 'EMP004', department: 'HR', working_days: 22, present_days: 22, lop_days: 0, ot_hours: 4, paid_leaves: 0, unpaid_leaves: 0 },
  { employee_id: '5', employee_name: 'Vikram Singh', employee_code: 'EMP005', department: 'Finance', working_days: 22, present_days: 21, lop_days: 1, ot_hours: 6, paid_leaves: 0, unpaid_leaves: 1 },
  { employee_id: '6', employee_name: 'Neha Gupta', employee_code: 'EMP006', department: 'Engineering', working_days: 22, present_days: 22, lop_days: 0, ot_hours: 16, paid_leaves: 0, unpaid_leaves: 0 },
  { employee_id: '7', employee_name: 'Kiran Desai', employee_code: 'EMP007', department: 'Marketing', working_days: 22, present_days: 19, lop_days: 3, ot_hours: 0, paid_leaves: 0, unpaid_leaves: 3 },
  { employee_id: '8', employee_name: 'Arjun Mehta', employee_code: 'EMP008', department: 'Engineering', working_days: 22, present_days: 22, lop_days: 0, ot_hours: 10, paid_leaves: 0, unpaid_leaves: 0 }
]

const mockVariableInputData: VariableInputData[] = mockAttendanceData.map(emp => ({
  employee_id: emp.employee_id,
  employee_name: emp.employee_name,
  employee_code: emp.employee_code,
  bonus: 0,
  incentive: 0,
  reimbursements: 0,
  arrears: 0,
  other_deductions: 0,
  advance_recovery: 0,
  loan_recovery: 0
}))

const mockPreviewData: PayrollPreviewData[] = [
  {
    id: '1',
    payroll_run_id: '1',
    employee_id: '1',
    employee_name: 'Rahul Kumar',
    employee_code: 'EMP001',
    department: 'Engineering',
    designation: 'Senior Developer',
    working_days: 22,
    present_days: 21,
    paid_leaves: 0,
    unpaid_leaves: 1,
    holidays: 0,
    lop_days: 1,
    basic: 40000,
    hra: 20000,
    special_allowance: 15000,
    other_earnings: 5000,
    arrears: 0,
    bonus: 0,
    total_earnings: 76364, // LOP adjusted
    pf_employee: 4800, // 12% of Basic
    esi_employee: 0, // Gross > 21000
    pt: 200,
    tds: 8500,
    other_deductions: 0,
    loan_recovery: 0,
    advance_recovery: 0,
    total_deductions: 13500,
    pf_employer: 4800,
    esi_employer: 0,
    total_employer_contribution: 4800,
    net_salary: 62864,
    ctc_monthly: 85000,
    status: 'calculated',
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z'
  },
  {
    id: '2',
    payroll_run_id: '1',
    employee_id: '2',
    employee_name: 'Priya Sharma',
    employee_code: 'EMP002',
    department: 'Engineering',
    designation: 'Tech Lead',
    working_days: 22,
    present_days: 22,
    paid_leaves: 0,
    unpaid_leaves: 0,
    holidays: 0,
    lop_days: 0,
    basic: 50000,
    hra: 25000,
    special_allowance: 20000,
    other_earnings: 5000,
    arrears: 0,
    bonus: 0,
    total_earnings: 100000,
    pf_employee: 6000,
    esi_employee: 0,
    pt: 200,
    tds: 12500,
    other_deductions: 0,
    loan_recovery: 0,
    advance_recovery: 0,
    total_deductions: 18700,
    pf_employer: 6000,
    esi_employer: 0,
    total_employer_contribution: 6000,
    net_salary: 81300,
    ctc_monthly: 112000,
    status: 'calculated',
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z'
  },
  {
    id: '3',
    payroll_run_id: '1',
    employee_id: '3',
    employee_name: 'Amit Patel',
    employee_code: 'EMP003',
    department: 'Sales',
    designation: 'Sales Executive',
    working_days: 22,
    present_days: 20,
    paid_leaves: 0,
    unpaid_leaves: 2,
    holidays: 0,
    lop_days: 2,
    basic: 25000,
    hra: 12500,
    special_allowance: 7500,
    other_earnings: 5000,
    arrears: 0,
    bonus: 0,
    total_earnings: 45455,
    pf_employee: 3000,
    esi_employee: 0,
    pt: 200,
    tds: 3500,
    other_deductions: 0,
    loan_recovery: 0,
    advance_recovery: 0,
    total_deductions: 6700,
    pf_employer: 3000,
    esi_employer: 0,
    total_employer_contribution: 3000,
    net_salary: 38755,
    ctc_monthly: 56000,
    status: 'calculated',
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z'
  },
  {
    id: '4',
    payroll_run_id: '1',
    employee_id: '4',
    employee_name: 'Sneha Reddy',
    employee_code: 'EMP004',
    department: 'HR',
    designation: 'HR Manager',
    working_days: 22,
    present_days: 22,
    paid_leaves: 0,
    unpaid_leaves: 0,
    holidays: 0,
    lop_days: 0,
    basic: 35000,
    hra: 17500,
    special_allowance: 12500,
    other_earnings: 5000,
    arrears: 0,
    bonus: 0,
    total_earnings: 70000,
    pf_employee: 4200,
    esi_employee: 0,
    pt: 200,
    tds: 6500,
    other_deductions: 0,
    loan_recovery: 0,
    advance_recovery: 0,
    total_deductions: 10900,
    pf_employer: 4200,
    esi_employer: 0,
    total_employer_contribution: 4200,
    net_salary: 59100,
    ctc_monthly: 78400,
    status: 'calculated',
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z'
  },
  {
    id: '5',
    payroll_run_id: '1',
    employee_id: '5',
    employee_name: 'Vikram Singh',
    employee_code: 'EMP005',
    department: 'Finance',
    designation: 'Accountant',
    working_days: 22,
    present_days: 21,
    paid_leaves: 0,
    unpaid_leaves: 1,
    holidays: 0,
    lop_days: 1,
    basic: 30000,
    hra: 15000,
    special_allowance: 10000,
    other_earnings: 5000,
    arrears: 0,
    bonus: 0,
    total_earnings: 57273,
    pf_employee: 3600,
    esi_employee: 0,
    pt: 200,
    tds: 5000,
    other_deductions: 0,
    loan_recovery: 0,
    advance_recovery: 0,
    total_deductions: 8800,
    pf_employer: 3600,
    esi_employer: 0,
    total_employer_contribution: 3600,
    net_salary: 48473,
    ctc_monthly: 67200,
    status: 'calculated',
    created_at: '2026-01-01T00:00:00Z',
    updated_at: '2026-01-01T00:00:00Z'
  }
]

// ============================================================================
// Step Indicator Component
// ============================================================================

interface StepIndicatorProps {
  steps: WizardStep[]
  currentStep: number
  onStepClick?: (step: number) => void
}

function StepIndicator({ steps, currentStep, onStepClick }: StepIndicatorProps) {
  return (
    <div className="w-full">
      <div className="flex items-center justify-between">
        {steps.map((step, index) => {
          const Icon = step.icon
          const isCompleted = step.id < currentStep
          const isCurrent = step.id === currentStep
          const isClickable = step.id < currentStep

          return (
            <React.Fragment key={step.id}>
              {/* Step Circle */}
              <div className="flex flex-col items-center relative">
                <button
                  type="button"
                  onClick={() => isClickable && onStepClick?.(step.id)}
                  disabled={!isClickable}
                  className={cn(
                    "w-10 h-10 rounded-full flex items-center justify-center transition-all duration-200",
                    isCompleted && "bg-primary text-primary-foreground cursor-pointer hover:bg-primary/90",
                    isCurrent && "bg-primary text-primary-foreground ring-4 ring-primary/20",
                    !isCompleted && !isCurrent && "bg-muted text-muted-foreground",
                    !isClickable && "cursor-default"
                  )}
                >
                  {isCompleted ? (
                    <Check className="h-5 w-5" />
                  ) : (
                    <Icon className="h-5 w-5" />
                  )}
                </button>
                <div className="mt-2 text-center">
                  <p className={cn(
                    "text-sm font-medium",
                    isCurrent ? "text-primary" : "text-muted-foreground"
                  )}>
                    {step.title}
                  </p>
                  <p className="text-xs text-muted-foreground hidden lg:block">
                    {step.description}
                  </p>
                </div>
              </div>

              {/* Connector Line */}
              {index < steps.length - 1 && (
                <div className={cn(
                  "flex-1 h-0.5 mx-2 mt-[-24px]",
                  step.id < currentStep ? "bg-primary" : "bg-muted"
                )} />
              )}
            </React.Fragment>
          )
        })}
      </div>
    </div>
  )
}

// ============================================================================
// Step 1: Select Period
// ============================================================================

interface Step1Props {
  month: number
  year: number
  onMonthChange: (month: number) => void
  onYearChange: (year: number) => void
  existingRun: boolean
}

function Step1SelectPeriod({ month, year, onMonthChange, onYearChange, existingRun }: Step1Props) {
  const financialYear = getFinancialYear(new Date(year, month - 1))

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>Select Payroll Period</CardTitle>
          <CardDescription>
            Choose the month and year for payroll processing
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <MonthYearPicker
            label="Payroll Period"
            name="payroll-period"
            month={month}
            year={year}
            onMonthChange={onMonthChange}
            onYearChange={onYearChange}
          />

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card className="bg-muted/50">
              <CardContent className="pt-4">
                <p className="text-sm text-muted-foreground">Selected Period</p>
                <p className="text-lg font-semibold">{getMonthName(month)} {year}</p>
              </CardContent>
            </Card>
            <Card className="bg-muted/50">
              <CardContent className="pt-4">
                <p className="text-sm text-muted-foreground">Financial Year</p>
                <p className="text-lg font-semibold">{financialYear}</p>
              </CardContent>
            </Card>
            <Card className="bg-muted/50">
              <CardContent className="pt-4">
                <p className="text-sm text-muted-foreground">Total Employees</p>
                <p className="text-lg font-semibold">47</p>
              </CardContent>
            </Card>
          </div>

          {existingRun && (
            <div className="flex items-start gap-3 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
              <AlertCircle className="h-5 w-5 text-yellow-600 mt-0.5" />
              <div>
                <p className="font-medium text-yellow-800">Existing Payroll Run Found</p>
                <p className="text-sm text-yellow-700 mt-1">
                  A payroll run already exists for this period. Proceeding will update the existing run.
                </p>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

// ============================================================================
// Step 2: Review Attendance
// ============================================================================

interface Step2Props {
  attendanceData: AttendanceData[]
  onAttendanceChange: (data: AttendanceData[]) => void
}

function Step2ReviewAttendance({ attendanceData, onAttendanceChange }: Step2Props) {
  const [searchQuery, setSearchQuery] = React.useState('')
  const [editingId, setEditingId] = React.useState<string | null>(null)

  const filteredData = attendanceData.filter(emp =>
    emp.employee_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    emp.employee_code.toLowerCase().includes(searchQuery.toLowerCase())
  )

  const handleFieldChange = (employeeId: string, field: keyof AttendanceData, value: number) => {
    const updated = attendanceData.map(emp =>
      emp.employee_id === employeeId ? { ...emp, [field]: value } : emp
    )
    onAttendanceChange(updated)
  }

  const columns: Column<AttendanceData>[] = [
    {
      key: 'employee',
      header: 'Employee',
      accessor: (row) => (
        <div>
          <p className="font-medium">{row.employee_name}</p>
          <p className="text-sm text-muted-foreground">{row.employee_code}</p>
        </div>
      )
    },
    {
      key: 'department',
      header: 'Department',
      accessor: 'department'
    },
    {
      key: 'working_days',
      header: 'Working Days',
      className: 'text-center',
      headerClassName: 'text-center',
      accessor: (row) => row.working_days
    },
    {
      key: 'present_days',
      header: 'Present',
      className: 'text-center',
      headerClassName: 'text-center',
      accessor: (row) => (
        editingId === row.employee_id ? (
          <input
            type="number"
            value={row.present_days}
            onChange={(e) => handleFieldChange(row.employee_id, 'present_days', parseInt(e.target.value) || 0)}
            className="w-16 h-8 text-center border rounded"
            min={0}
            max={row.working_days}
          />
        ) : (
          <span className={row.present_days < row.working_days ? 'text-yellow-600' : 'text-green-600'}>
            {row.present_days}
          </span>
        )
      )
    },
    {
      key: 'lop_days',
      header: 'LOP Days',
      className: 'text-center',
      headerClassName: 'text-center',
      accessor: (row) => (
        editingId === row.employee_id ? (
          <input
            type="number"
            value={row.lop_days}
            onChange={(e) => handleFieldChange(row.employee_id, 'lop_days', parseInt(e.target.value) || 0)}
            className="w-16 h-8 text-center border rounded"
            min={0}
          />
        ) : (
          <span className={row.lop_days > 0 ? 'text-red-600 font-medium' : ''}>
            {row.lop_days}
          </span>
        )
      )
    },
    {
      key: 'ot_hours',
      header: 'OT Hours',
      className: 'text-center',
      headerClassName: 'text-center',
      accessor: (row) => (
        editingId === row.employee_id ? (
          <input
            type="number"
            value={row.ot_hours}
            onChange={(e) => handleFieldChange(row.employee_id, 'ot_hours', parseInt(e.target.value) || 0)}
            className="w-16 h-8 text-center border rounded"
            min={0}
          />
        ) : (
          <span className={row.ot_hours > 0 ? 'text-blue-600' : ''}>
            {row.ot_hours}
          </span>
        )
      )
    },
    {
      key: 'actions',
      header: '',
      accessor: (row) => (
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setEditingId(editingId === row.employee_id ? null : row.employee_id)}
        >
          <Edit className="h-4 w-4" />
        </Button>
      )
    }
  ]

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div>
              <CardTitle>Review Attendance</CardTitle>
              <CardDescription>
                Verify working days, present days, and LOP for each employee
              </CardDescription>
            </div>
            <div className="flex items-center gap-2">
              <Button variant="outline" size="sm">
                <Upload className="h-4 w-4 mr-2" />
                Import from Attendance
              </Button>
              <Button variant="outline" size="sm">
                <Download className="h-4 w-4 mr-2" />
                Export Template
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <SearchInput
            placeholder="Search by employee name or code..."
            value={searchQuery}
            onChange={setSearchQuery}
            className="max-w-sm"
          />

          <DataTable
            data={filteredData}
            columns={columns}
            keyExtractor={(row) => row.employee_id}
          />

          <div className="flex items-center gap-4 text-sm">
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-red-500" />
              <span>LOP Applied: {attendanceData.filter(e => e.lop_days > 0).length}</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-blue-500" />
              <span>OT Applicable: {attendanceData.filter(e => e.ot_hours > 0).length}</span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

// ============================================================================
// Step 3: Variable Inputs
// ============================================================================

interface Step3Props {
  variableData: VariableInputData[]
  onVariableChange: (data: VariableInputData[]) => void
}

function Step3VariableInputs({ variableData, onVariableChange }: Step3Props) {
  const [searchQuery, setSearchQuery] = React.useState('')
  const [editingId, setEditingId] = React.useState<string | null>(null)

  const filteredData = variableData.filter(emp =>
    emp.employee_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    emp.employee_code.toLowerCase().includes(searchQuery.toLowerCase())
  )

  const handleFieldChange = (employeeId: string, field: keyof VariableInputData, value: number) => {
    const updated = variableData.map(emp =>
      emp.employee_id === employeeId ? { ...emp, [field]: value } : emp
    )
    onVariableChange(updated)
  }

  const columns: Column<VariableInputData>[] = [
    {
      key: 'employee',
      header: 'Employee',
      accessor: (row) => (
        <div>
          <p className="font-medium">{row.employee_name}</p>
          <p className="text-sm text-muted-foreground">{row.employee_code}</p>
        </div>
      )
    },
    {
      key: 'bonus',
      header: 'Bonus',
      className: 'text-right',
      headerClassName: 'text-right',
      accessor: (row) => (
        editingId === row.employee_id ? (
          <input
            type="number"
            value={row.bonus}
            onChange={(e) => handleFieldChange(row.employee_id, 'bonus', parseFloat(e.target.value) || 0)}
            className="w-24 h-8 text-right border rounded px-2"
            min={0}
          />
        ) : (
          <span className={row.bonus > 0 ? 'text-green-600' : ''}>
            {formatCurrency(row.bonus)}
          </span>
        )
      )
    },
    {
      key: 'incentive',
      header: 'Incentive',
      className: 'text-right',
      headerClassName: 'text-right',
      accessor: (row) => (
        editingId === row.employee_id ? (
          <input
            type="number"
            value={row.incentive}
            onChange={(e) => handleFieldChange(row.employee_id, 'incentive', parseFloat(e.target.value) || 0)}
            className="w-24 h-8 text-right border rounded px-2"
            min={0}
          />
        ) : (
          <span className={row.incentive > 0 ? 'text-green-600' : ''}>
            {formatCurrency(row.incentive)}
          </span>
        )
      )
    },
    {
      key: 'reimbursements',
      header: 'Reimbursements',
      className: 'text-right',
      headerClassName: 'text-right',
      accessor: (row) => (
        editingId === row.employee_id ? (
          <input
            type="number"
            value={row.reimbursements}
            onChange={(e) => handleFieldChange(row.employee_id, 'reimbursements', parseFloat(e.target.value) || 0)}
            className="w-24 h-8 text-right border rounded px-2"
            min={0}
          />
        ) : (
          formatCurrency(row.reimbursements)
        )
      )
    },
    {
      key: 'arrears',
      header: 'Arrears',
      className: 'text-right',
      headerClassName: 'text-right',
      accessor: (row) => (
        editingId === row.employee_id ? (
          <input
            type="number"
            value={row.arrears}
            onChange={(e) => handleFieldChange(row.employee_id, 'arrears', parseFloat(e.target.value) || 0)}
            className="w-24 h-8 text-right border rounded px-2"
          />
        ) : (
          formatCurrency(row.arrears)
        )
      )
    },
    {
      key: 'deductions',
      header: 'Deductions',
      className: 'text-right',
      headerClassName: 'text-right',
      accessor: (row) => (
        editingId === row.employee_id ? (
          <input
            type="number"
            value={row.other_deductions}
            onChange={(e) => handleFieldChange(row.employee_id, 'other_deductions', parseFloat(e.target.value) || 0)}
            className="w-24 h-8 text-right border rounded px-2"
            min={0}
          />
        ) : (
          <span className={row.other_deductions > 0 ? 'text-red-600' : ''}>
            {formatCurrency(row.other_deductions)}
          </span>
        )
      )
    },
    {
      key: 'actions',
      header: '',
      accessor: (row) => (
        <Button
          variant="ghost"
          size="sm"
          onClick={() => setEditingId(editingId === row.employee_id ? null : row.employee_id)}
        >
          <Edit className="h-4 w-4" />
        </Button>
      )
    }
  ]

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div>
              <CardTitle>Variable Inputs</CardTitle>
              <CardDescription>
                Add bonus, incentives, reimbursements, and deductions
              </CardDescription>
            </div>
            <div className="flex items-center gap-2">
              <Button variant="outline" size="sm">
                <Upload className="h-4 w-4 mr-2" />
                Bulk Upload
              </Button>
              <Button variant="outline" size="sm">
                <Download className="h-4 w-4 mr-2" />
                Download Template
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <SearchInput
            placeholder="Search by employee name or code..."
            value={searchQuery}
            onChange={setSearchQuery}
            className="max-w-sm"
          />

          <DataTable
            data={filteredData}
            columns={columns}
            keyExtractor={(row) => row.employee_id}
          />
        </CardContent>
      </Card>
    </div>
  )
}

// ============================================================================
// Step 4: Preview & Calculate
// ============================================================================

interface Step4Props {
  previewData: PayrollPreviewData[]
  isCalculating: boolean
  onCalculate: () => void
}

function Step4PreviewCalculate({ previewData, isCalculating, onCalculate }: Step4Props) {
  const [searchQuery, setSearchQuery] = React.useState('')

  const filteredData = previewData.filter(emp =>
    emp.employee_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    emp.employee_code.toLowerCase().includes(searchQuery.toLowerCase())
  )

  // Calculate summary
  const summary = previewData.reduce((acc, emp) => ({
    totalGross: acc.totalGross + emp.total_earnings,
    totalDeductions: acc.totalDeductions + emp.total_deductions,
    totalNet: acc.totalNet + emp.net_salary,
    totalPF: acc.totalPF + emp.pf_employee + emp.pf_employer,
    totalESI: acc.totalESI + emp.esi_employee + emp.esi_employer,
    totalPT: acc.totalPT + emp.pt,
    totalTDS: acc.totalTDS + emp.tds
  }), {
    totalGross: 0,
    totalDeductions: 0,
    totalNet: 0,
    totalPF: 0,
    totalESI: 0,
    totalPT: 0,
    totalTDS: 0
  })

  // Department-wise summary
  const deptSummary = previewData.reduce((acc, emp) => {
    if (!acc[emp.department]) {
      acc[emp.department] = { count: 0, gross: 0, net: 0 }
    }
    acc[emp.department].count++
    acc[emp.department].gross += emp.total_earnings
    acc[emp.department].net += emp.net_salary
    return acc
  }, {} as Record<string, { count: number; gross: number; net: number }>)

  const columns: Column<PayrollPreviewData>[] = [
    {
      key: 'employee',
      header: 'Employee',
      accessor: (row) => (
        <div>
          <p className="font-medium">{row.employee_name}</p>
          <p className="text-sm text-muted-foreground">{row.employee_code}</p>
        </div>
      )
    },
    {
      key: 'department',
      header: 'Department',
      accessor: 'department'
    },
    {
      key: 'gross',
      header: 'Gross',
      className: 'text-right',
      headerClassName: 'text-right',
      accessor: (row) => formatCurrency(row.total_earnings)
    },
    {
      key: 'pf',
      header: 'PF (12%)',
      className: 'text-right',
      headerClassName: 'text-right',
      accessor: (row) => (
        <span className="text-red-600">-{formatCurrency(row.pf_employee)}</span>
      )
    },
    {
      key: 'esi',
      header: 'ESI (0.75%)',
      className: 'text-right',
      headerClassName: 'text-right',
      accessor: (row) => (
        row.esi_employee > 0 ? (
          <span className="text-red-600">-{formatCurrency(row.esi_employee)}</span>
        ) : (
          <span className="text-muted-foreground">N/A</span>
        )
      )
    },
    {
      key: 'pt',
      header: 'PT',
      className: 'text-right',
      headerClassName: 'text-right',
      accessor: (row) => (
        <span className="text-red-600">-{formatCurrency(row.pt)}</span>
      )
    },
    {
      key: 'tds',
      header: 'TDS',
      className: 'text-right',
      headerClassName: 'text-right',
      accessor: (row) => (
        <span className="text-red-600">-{formatCurrency(row.tds)}</span>
      )
    },
    {
      key: 'net',
      header: 'Net Pay',
      className: 'text-right font-medium',
      headerClassName: 'text-right',
      accessor: (row) => (
        <span className="text-green-600">{formatCurrency(row.net_salary)}</span>
      )
    }
  ]

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-4">
            <p className="text-sm text-muted-foreground">Total Gross Salary</p>
            <p className="text-2xl font-bold">{formatCurrency(summary.totalGross)}</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-4">
            <p className="text-sm text-muted-foreground">Total Deductions</p>
            <p className="text-2xl font-bold text-red-600">-{formatCurrency(summary.totalDeductions)}</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-4">
            <p className="text-sm text-muted-foreground">Total Net Payable</p>
            <p className="text-2xl font-bold text-green-600">{formatCurrency(summary.totalNet)}</p>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-4">
            <p className="text-sm text-muted-foreground">Employees Processed</p>
            <p className="text-2xl font-bold">{previewData.length}</p>
          </CardContent>
        </Card>
      </div>

      {/* Statutory Deductions Summary */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="bg-blue-50 border-blue-200">
          <CardContent className="pt-4">
            <p className="text-sm text-blue-700">PF (Employee + Employer)</p>
            <p className="text-lg font-semibold text-blue-800">{formatCurrency(summary.totalPF)}</p>
            <p className="text-xs text-blue-600 mt-1">12% + 12% of Basic</p>
          </CardContent>
        </Card>
        <Card className="bg-green-50 border-green-200">
          <CardContent className="pt-4">
            <p className="text-sm text-green-700">ESI (Employee + Employer)</p>
            <p className="text-lg font-semibold text-green-800">{formatCurrency(summary.totalESI)}</p>
            <p className="text-xs text-green-600 mt-1">0.75% + 3.25% (Gross &lt;= 21K)</p>
          </CardContent>
        </Card>
        <Card className="bg-purple-50 border-purple-200">
          <CardContent className="pt-4">
            <p className="text-sm text-purple-700">Professional Tax</p>
            <p className="text-lg font-semibold text-purple-800">{formatCurrency(summary.totalPT)}</p>
            <p className="text-xs text-purple-600 mt-1">State-wise slab</p>
          </CardContent>
        </Card>
        <Card className="bg-orange-50 border-orange-200">
          <CardContent className="pt-4">
            <p className="text-sm text-orange-700">TDS (Income Tax)</p>
            <p className="text-lg font-semibold text-orange-800">{formatCurrency(summary.totalTDS)}</p>
            <p className="text-xs text-orange-600 mt-1">As per regime selected</p>
          </CardContent>
        </Card>
      </div>

      {/* Department-wise Summary */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Department-wise Summary</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {Object.entries(deptSummary).map(([dept, data]) => (
              <div key={dept} className="p-4 bg-muted/50 rounded-lg">
                <p className="font-medium">{dept}</p>
                <p className="text-sm text-muted-foreground">{data.count} employees</p>
                <p className="text-sm font-medium mt-1">Net: {formatCurrency(data.net)}</p>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Employee-wise Table */}
      <Card>
        <CardHeader>
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <div>
              <CardTitle>Employee-wise Breakdown</CardTitle>
              <CardDescription>Review individual salary calculations</CardDescription>
            </div>
            <Button onClick={onCalculate} disabled={isCalculating}>
              {isCalculating ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Calculating...
                </>
              ) : (
                <>
                  <Calculator className="h-4 w-4 mr-2" />
                  Recalculate
                </>
              )}
            </Button>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <SearchInput
            placeholder="Search by employee name or code..."
            value={searchQuery}
            onChange={setSearchQuery}
            className="max-w-sm"
          />

          <DataTable
            data={filteredData}
            columns={columns}
            keyExtractor={(row) => row.id}
          />
        </CardContent>
      </Card>
    </div>
  )
}

// ============================================================================
// Step 5: Approve & Process
// ============================================================================

interface Step5Props {
  month: number
  year: number
  previewData: PayrollPreviewData[]
  isProcessing: boolean
  onProcess: () => void
}

function Step5ApproveProcess({ month, year, previewData, isProcessing, onProcess }: Step5Props) {
  const [approver, setApprover] = React.useState('')
  const [generatePayslips, setGeneratePayslips] = React.useState(true)
  const [generateBankFile, setGenerateBankFile] = React.useState(true)
  const [sendEmails, setSendEmails] = React.useState(false)

  const summary = previewData.reduce((acc, emp) => ({
    totalGross: acc.totalGross + emp.total_earnings,
    totalDeductions: acc.totalDeductions + emp.total_deductions,
    totalNet: acc.totalNet + emp.net_salary,
    totalEmployerCost: acc.totalEmployerCost + emp.ctc_monthly
  }), {
    totalGross: 0,
    totalDeductions: 0,
    totalNet: 0,
    totalEmployerCost: 0
  })

  return (
    <div className="space-y-6">
      {/* Final Summary */}
      <Card className="bg-primary/5 border-primary/20">
        <CardHeader>
          <CardTitle>Final Payroll Summary</CardTitle>
          <CardDescription>
            {getMonthName(month)} {year} - {previewData.length} Employees
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            <div>
              <p className="text-sm text-muted-foreground">Total Gross</p>
              <p className="text-2xl font-bold">{formatCurrency(summary.totalGross)}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Total Deductions</p>
              <p className="text-2xl font-bold text-red-600">-{formatCurrency(summary.totalDeductions)}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Net Payable</p>
              <p className="text-2xl font-bold text-green-600">{formatCurrency(summary.totalNet)}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Total CTC</p>
              <p className="text-2xl font-bold">{formatCurrency(summary.totalEmployerCost)}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Approval & Processing Options */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Approval</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="approver">Select Approver</Label>
              <select
                id="approver"
                value={approver}
                onChange={(e) => setApprover(e.target.value)}
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
              >
                <option value="">Select an approver</option>
                <option value="cfo">CFO - Rajesh Menon</option>
                <option value="ceo">CEO - Anil Kumar</option>
                <option value="hr_head">HR Head - Priya Nair</option>
              </select>
            </div>

            <div className="pt-4 border-t">
              <p className="text-sm text-muted-foreground mb-2">Approval Status</p>
              <div className="flex items-center gap-2">
                <Clock className="h-5 w-5 text-yellow-500" />
                <span className="font-medium">Pending Approval</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Processing Options</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <label className="flex items-center gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={generatePayslips}
                onChange={(e) => setGeneratePayslips(e.target.checked)}
                className="h-4 w-4 rounded border-gray-300"
              />
              <div>
                <p className="font-medium">Generate Payslips (PDF)</p>
                <p className="text-sm text-muted-foreground">Create individual payslip PDFs</p>
              </div>
            </label>

            <label className="flex items-center gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={generateBankFile}
                onChange={(e) => setGenerateBankFile(e.target.checked)}
                className="h-4 w-4 rounded border-gray-300"
              />
              <div>
                <p className="font-medium">Generate Bank File</p>
                <p className="text-sm text-muted-foreground">NEFT/RTGS payment file for bank upload</p>
              </div>
            </label>

            <label className="flex items-center gap-3 cursor-pointer">
              <input
                type="checkbox"
                checked={sendEmails}
                onChange={(e) => setSendEmails(e.target.checked)}
                className="h-4 w-4 rounded border-gray-300"
              />
              <div>
                <p className="font-medium">Email Payslips</p>
                <p className="text-sm text-muted-foreground">Send payslips to employee emails</p>
              </div>
            </label>
          </CardContent>
        </Card>
      </div>

      {/* Checklist */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Pre-Processing Checklist</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div className="flex items-center gap-3">
              <CheckCircle className="h-5 w-5 text-green-500" />
              <span>Attendance data verified for all employees</span>
            </div>
            <div className="flex items-center gap-3">
              <CheckCircle className="h-5 w-5 text-green-500" />
              <span>Variable inputs (bonus, incentives, deductions) added</span>
            </div>
            <div className="flex items-center gap-3">
              <CheckCircle className="h-5 w-5 text-green-500" />
              <span>Salary calculations reviewed</span>
            </div>
            <div className="flex items-center gap-3">
              <CheckCircle className="h-5 w-5 text-green-500" />
              <span>Statutory deductions (PF, ESI, PT, TDS) verified</span>
            </div>
            <div className="flex items-center gap-3">
              {approver ? (
                <CheckCircle className="h-5 w-5 text-green-500" />
              ) : (
                <AlertCircle className="h-5 w-5 text-yellow-500" />
              )}
              <span className={!approver ? 'text-yellow-600' : ''}>
                Approver selected
              </span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Process Button */}
      <div className="flex justify-center">
        <Button
          size="lg"
          onClick={onProcess}
          disabled={!approver || isProcessing}
          className="min-w-[200px]"
        >
          {isProcessing ? (
            <>
              <Loader2 className="h-5 w-5 mr-2 animate-spin" />
              Processing...
            </>
          ) : (
            <>
              <Send className="h-5 w-5 mr-2" />
              Submit for Approval
            </>
          )}
        </Button>
      </div>
    </div>
  )
}

// ============================================================================
// Main Wizard Component
// ============================================================================

// Mock employee salary structures for API calculation demo
const mockEmployeeSalaries = [
  { id: '1', name: 'Rahul Kumar', code: 'EMP001', dept: 'Engineering', desg: 'Senior Developer', basic: 40000, hra: 20000, special: 15000, other: 5000 },
  { id: '2', name: 'Priya Sharma', code: 'EMP002', dept: 'Engineering', desg: 'Tech Lead', basic: 50000, hra: 25000, special: 20000, other: 5000 },
  { id: '3', name: 'Amit Patel', code: 'EMP003', dept: 'Sales', desg: 'Sales Executive', basic: 25000, hra: 12500, special: 7500, other: 5000 },
  { id: '4', name: 'Sneha Reddy', code: 'EMP004', dept: 'HR', desg: 'HR Manager', basic: 35000, hra: 17500, special: 12500, other: 5000 },
  { id: '5', name: 'Vikram Singh', code: 'EMP005', dept: 'Finance', desg: 'Accountant', basic: 30000, hra: 15000, special: 10000, other: 5000 },
]

export function PayrollWizard({ onComplete, onCancel }: PayrollWizardProps) {
  const currentDate = new Date()
  const api = useApi()
  const [currentStep, setCurrentStep] = React.useState(1)
  const [month, setMonth] = React.useState(currentDate.getMonth() + 1)
  const [year, setYear] = React.useState(currentDate.getFullYear())
  const [attendanceData, setAttendanceData] = React.useState(mockAttendanceData)
  const [variableData, setVariableData] = React.useState(mockVariableInputData)
  const [previewData, setPreviewData] = React.useState(mockPreviewData)
  const [isCalculating, setIsCalculating] = React.useState(false)
  const [isProcessing, setIsProcessing] = React.useState(false)
  const [existingRun] = React.useState(false)

  const handleNext = () => {
    if (currentStep < steps.length) {
      setCurrentStep(currentStep + 1)
    }
  }

  const handlePrevious = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1)
    }
  }

  const handleCalculate = async () => {
    setIsCalculating(true)
    try {
      // Calculate salary for each employee using the API
      const calculatedData: PayrollPreviewData[] = []

      for (const emp of mockEmployeeSalaries) {
        const attendance = attendanceData.find(a => a.employee_id === emp.id)
        const variable = variableData.find(v => v.employee_id === emp.id)

        const workingDays = attendance?.working_days || 22
        const daysWorked = attendance?.present_days || workingDays

        const requestData = {
          salary: {
            basic: emp.basic,
            hra: emp.hra,
            da: 0,
            conveyance: 0,
            special_allowance: emp.special,
            medical_allowance: 0,
            lta: 0,
            other_allowances: emp.other
          },
          month: month,
          year: year,
          working_days: workingDays,
          days_worked: daysWorked,
          tax_regime: 'new',
          deductions_80c: 0,
          deductions_80d: 0
        }

        try {
          const result = await api.post('/payroll/calculate', requestData)

          calculatedData.push({
            id: emp.id,
            payroll_run_id: '1',
            employee_id: emp.id,
            employee_name: emp.name,
            employee_code: emp.code,
            department: emp.dept,
            designation: emp.desg,
            working_days: workingDays,
            present_days: daysWorked,
            paid_leaves: attendance?.paid_leaves || 0,
            unpaid_leaves: attendance?.unpaid_leaves || 0,
            holidays: 0,
            lop_days: attendance?.lop_days || 0,
            basic: result.earnings.basic,
            hra: result.earnings.hra,
            special_allowance: result.earnings.special_allowance,
            other_earnings: result.earnings.other_allowances,
            arrears: variable?.arrears || 0,
            bonus: variable?.bonus || 0,
            total_earnings: result.earnings.total,
            pf_employee: result.deductions.employee_pf,
            esi_employee: result.deductions.employee_esi,
            pt: result.deductions.professional_tax,
            tds: result.deductions.tds,
            other_deductions: variable?.other_deductions || 0,
            loan_recovery: variable?.loan_recovery || 0,
            advance_recovery: variable?.advance_recovery || 0,
            total_deductions: result.deductions.total,
            pf_employer: result.employer_contributions.employer_pf,
            esi_employer: result.employer_contributions.employer_esi,
            total_employer_contribution: result.employer_contributions.total,
            net_salary: result.summary.net_salary,
            ctc_monthly: result.summary.ctc_monthly,
            status: 'calculated',
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString()
          })
        } catch (err) {
          console.error(`Failed to calculate for ${emp.name}:`, err)
        }
      }

      if (calculatedData.length > 0) {
        setPreviewData(calculatedData)
      }
    } catch (err) {
      console.error('Calculation failed:', err)
    } finally {
      setIsCalculating(false)
    }
  }

  const handleProcess = async () => {
    setIsProcessing(true)
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 2000))
    setIsProcessing(false)
    onComplete?.({ month, year })
  }

  const handleStepClick = (step: number) => {
    if (step < currentStep) {
      setCurrentStep(step)
    }
  }

  const canProceed = () => {
    switch (currentStep) {
      case 1:
        return month > 0 && year > 0
      case 2:
        return attendanceData.length > 0
      case 3:
        return true
      case 4:
        return previewData.length > 0
      case 5:
        return true
      default:
        return false
    }
  }

  const renderStep = () => {
    switch (currentStep) {
      case 1:
        return (
          <Step1SelectPeriod
            month={month}
            year={year}
            onMonthChange={setMonth}
            onYearChange={setYear}
            existingRun={existingRun}
          />
        )
      case 2:
        return (
          <Step2ReviewAttendance
            attendanceData={attendanceData}
            onAttendanceChange={setAttendanceData}
          />
        )
      case 3:
        return (
          <Step3VariableInputs
            variableData={variableData}
            onVariableChange={setVariableData}
          />
        )
      case 4:
        return (
          <Step4PreviewCalculate
            previewData={previewData}
            isCalculating={isCalculating}
            onCalculate={handleCalculate}
          />
        )
      case 5:
        return (
          <Step5ApproveProcess
            month={month}
            year={year}
            previewData={previewData}
            isProcessing={isProcessing}
            onProcess={handleProcess}
          />
        )
      default:
        return null
    }
  }

  return (
    <div className="space-y-6">
      {/* Step Indicator */}
      <Card>
        <CardContent className="pt-6">
          <StepIndicator
            steps={steps}
            currentStep={currentStep}
            onStepClick={handleStepClick}
          />
        </CardContent>
      </Card>

      {/* Step Content */}
      {renderStep()}

      {/* Navigation Buttons */}
      <div className="flex items-center justify-between pt-4">
        <div>
          {onCancel && (
            <Button variant="outline" onClick={onCancel}>
              Cancel
            </Button>
          )}
        </div>
        <div className="flex items-center gap-2">
          {currentStep > 1 && (
            <Button variant="outline" onClick={handlePrevious}>
              <ChevronLeft className="h-4 w-4 mr-2" />
              Previous
            </Button>
          )}
          {currentStep < steps.length && (
            <Button onClick={handleNext} disabled={!canProceed()}>
              Next
              <ChevronRight className="h-4 w-4 ml-2" />
            </Button>
          )}
        </div>
      </div>
    </div>
  )
}

export default PayrollWizard
