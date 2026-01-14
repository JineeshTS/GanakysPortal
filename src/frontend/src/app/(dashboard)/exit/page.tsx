'use client'

import { useState, useEffect, useCallback } from 'react'
import { PageHeader } from '@/components/layout/page-header'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Skeleton } from '@/components/ui/skeleton'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  DialogFooter,
} from '@/components/ui/dialog'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { useApi, useToast } from '@/hooks'
import {
  UserMinus,
  Plus,
  FileText,
  CheckCircle,
  Clock,
  Calendar,
  IndianRupee,
  Laptop,
  Key,
  CreditCard,
  RefreshCw,
  Loader2,
  Eye,
  AlertCircle,
  Building2,
  User,
  CheckSquare
} from 'lucide-react'

// Types
interface ExitStats {
  total_exits: number
  initiated: number
  clearance_pending: number
  fnf_pending: number
  completed: number
  resignations: number
  terminations: number
  this_month: number
}

interface EmployeeBasicInfo {
  id: string
  employee_code: string
  full_name: string
  department_name?: string
  designation_name?: string
  date_of_joining?: string
}

interface ExitCase {
  id: string
  company_id: string
  employee_id: string
  employee?: EmployeeBasicInfo
  exit_type: string
  resignation_date?: string
  requested_lwd?: string
  approved_lwd?: string
  last_working_day?: string
  reason?: string
  reason_category?: string
  status: string
  notice_period_days?: number
  notice_served_days: number
  notice_buyout_days: number
  notice_recovery_amount?: string
  rehire_eligible: boolean
  rehire_notes?: string
  exit_interview_date?: string
  exit_interview_notes?: string
  manager_id?: string
  manager_name?: string
  hr_owner_id?: string
  clearance_progress: number
  tasks_completed: number
  tasks_total: number
  notes?: string
  created_at: string
  updated_at: string
}

interface ClearanceTask {
  id: string
  exit_case_id: string
  department: string
  task_name: string
  description?: string
  assigned_to?: string
  assigned_role?: string
  status: string
  due_date?: string
  completed_date?: string
  recovery_amount?: string
  notes?: string
  created_at: string
}

interface FinalSettlement {
  id: string
  exit_case_id: string
  basic_salary_dues: string
  leave_encashment: string
  bonus_dues: string
  gratuity: string
  reimbursements: string
  other_earnings: string
  total_earnings: string
  notice_recovery: string
  asset_recovery: string
  loan_recovery: string
  advance_recovery: string
  tds: string
  pf_employee: string
  other_deductions: string
  total_deductions: string
  net_payable: string
  status: string
  calculation_date?: string
  approved_date?: string
  processed_date?: string
  payment_date?: string
  payment_reference?: string
  notes?: string
  created_at: string
  updated_at: string
}

interface ExitCaseDetail extends ExitCase {
  clearance_tasks: ClearanceTask[]
  final_settlement?: FinalSettlement
}

interface Employee {
  id: string
  employee_code: string
  first_name: string
  last_name: string
  full_name: string
  department_name?: string
  designation_name?: string
  employment_status: string
}

interface ExitCaseListResponse {
  success: boolean
  data: ExitCase[]
  meta: { page: number; limit: number; total: number }
}

interface ClearanceTaskListResponse {
  success: boolean
  data: ClearanceTask[]
  meta: { page: number; limit: number; total: number }
}

interface EmployeeListResponse {
  success: boolean
  data: Employee[]
  meta: { page: number; limit: number; total: number }
}

const statusColors: Record<string, string> = {
  initiated: 'bg-gray-100 text-gray-800',
  clearance_pending: 'bg-blue-100 text-blue-800',
  clearance_completed: 'bg-blue-100 text-blue-800',
  fnf_pending: 'bg-yellow-100 text-yellow-800',
  fnf_processed: 'bg-green-100 text-green-800',
  completed: 'bg-green-100 text-green-800',
  cancelled: 'bg-red-100 text-red-800',
}

const statusLabels: Record<string, string> = {
  initiated: 'Initiated',
  clearance_pending: 'Clearance Pending',
  clearance_completed: 'Clearance Done',
  fnf_pending: 'F&F Pending',
  fnf_processed: 'F&F Processed',
  completed: 'Completed',
  cancelled: 'Cancelled',
}

const typeColors: Record<string, string> = {
  resignation: 'bg-blue-100 text-blue-800',
  termination: 'bg-red-100 text-red-800',
  retirement: 'bg-purple-100 text-purple-800',
  end_of_contract: 'bg-gray-100 text-gray-800',
  mutual_separation: 'bg-orange-100 text-orange-800',
  absconding: 'bg-red-100 text-red-800',
  death: 'bg-gray-100 text-gray-800',
}

const exitTypes: Record<string, string> = {
  resignation: 'Resignation',
  termination: 'Termination',
  retirement: 'Retirement',
  end_of_contract: 'End of Contract',
  mutual_separation: 'Mutual Separation',
  absconding: 'Absconding',
  death: 'Death',
}

const reasonCategories = [
  'Better Opportunity',
  'Higher Education',
  'Personal Reasons',
  'Health Issues',
  'Relocation',
  'Career Change',
  'Work Environment',
  'Compensation',
  'Work-Life Balance',
  'Family Reasons',
  'Other',
]

const clearanceTaskColors: Record<string, string> = {
  pending: 'bg-gray-100 text-gray-800',
  in_progress: 'bg-blue-100 text-blue-800',
  cleared: 'bg-green-100 text-green-800',
  not_applicable: 'bg-gray-100 text-gray-500',
}

const departmentIcons: Record<string, React.ComponentType<{ className?: string }>> = {
  IT: Laptop,
  HR: User,
  Finance: IndianRupee,
  Admin: Building2,
  Department: FileText,
}

export default function ExitPage() {
  const [activeTab, setActiveTab] = useState('active')
  const [isInitiateOpen, setIsInitiateOpen] = useState(false)
  const [isApproveOpen, setIsApproveOpen] = useState(false)
  const [isDetailOpen, setIsDetailOpen] = useState(false)
  const [isCalculateFnfOpen, setIsCalculateFnfOpen] = useState(false)
  const [selectedCase, setSelectedCase] = useState<ExitCaseDetail | null>(null)
  const { showToast } = useToast()

  // Form states
  const [initiateForm, setInitiateForm] = useState({
    employee_id: '',
    exit_type: 'resignation',
    resignation_date: '',
    requested_lwd: '',
    reason: '',
    reason_category: '',
    notes: '',
  })

  const [approveForm, setApproveForm] = useState({
    approved_lwd: '',
    notes: '',
  })

  const [fnfForm, setFnfForm] = useState({
    leave_encashment_days: 0,
    bonus_dues: 0,
    reimbursements: 0,
    other_earnings: 0,
    loan_recovery: 0,
    advance_recovery: 0,
    other_deductions: 0,
    notes: '',
  })

  // API hooks
  const { data: statsData, isLoading: isLoadingStats, get: getStats } = useApi<ExitStats>()
  const { data: casesData, isLoading: isLoadingCases, get: getCases } = useApi<ExitCaseListResponse>()
  const { data: employeesData, get: getEmployees } = useApi<EmployeeListResponse>()
  const { data: caseDetailData, isLoading: isLoadingDetail, get: getCaseDetail } = useApi<ExitCaseDetail>()
  const { isLoading: isInitiating, post: initiateExit } = useApi<ExitCase>()
  const { isLoading: isApproving, post: approveExit } = useApi<ExitCase>()
  const { isLoading: isCompletingTask, post: completeTask } = useApi<ClearanceTask>()
  const { isLoading: isCalculatingFnf, post: calculateFnf } = useApi<FinalSettlement>()
  const { post: completeExit } = useApi()

  // Fetch data
  const fetchData = useCallback(() => {
    getStats('/exit/stats')
    getCases('/exit/cases?page=1&limit=50')
    getEmployees('/employees?page=1&limit=100&status=active')
  }, [getStats, getCases, getEmployees])

  useEffect(() => {
    fetchData()
  }, [fetchData])

  // Stats
  const stats = statsData || {
    total_exits: 0,
    initiated: 0,
    clearance_pending: 0,
    fnf_pending: 0,
    completed: 0,
    resignations: 0,
    terminations: 0,
    this_month: 0,
  }

  const exitCases = casesData?.data || []
  const employees = employeesData?.data || []

  // Filter employees to exclude those already in exit process
  const availableEmployees = employees.filter(emp =>
    emp.employment_status === 'active' || emp.employment_status === 'probation'
  )

  // Handlers
  const handleInitiateExit = async () => {
    if (!initiateForm.employee_id) {
      showToast('error', 'Please select an employee')
      return
    }

    const result = await initiateExit('/exit/cases', {
      employee_id: initiateForm.employee_id,
      exit_type: initiateForm.exit_type,
      resignation_date: initiateForm.resignation_date || undefined,
      requested_lwd: initiateForm.requested_lwd || undefined,
      reason: initiateForm.reason || undefined,
      reason_category: initiateForm.reason_category || undefined,
      notes: initiateForm.notes || undefined,
    })

    if (result) {
      showToast('success', 'Exit process initiated successfully')
      setIsInitiateOpen(false)
      setInitiateForm({
        employee_id: '',
        exit_type: 'resignation',
        resignation_date: '',
        requested_lwd: '',
        reason: '',
        reason_category: '',
        notes: '',
      })
      fetchData()
    }
  }

  const handleViewDetail = async (caseId: string) => {
    const result = await getCaseDetail(`/exit/cases/${caseId}`)
    if (result) {
      setSelectedCase(result)
      setIsDetailOpen(true)
    }
  }

  const handleApproveExit = async () => {
    if (!selectedCase || !approveForm.approved_lwd) {
      showToast('error', 'Please select last working day')
      return
    }

    const result = await approveExit(`/exit/cases/${selectedCase.id}/approve`, {
      approved_lwd: approveForm.approved_lwd,
      notes: approveForm.notes || undefined,
    })

    if (result) {
      showToast('success', 'Exit approved successfully')
      setIsApproveOpen(false)
      setApproveForm({ approved_lwd: '', notes: '' })
      // Refresh detail
      handleViewDetail(selectedCase.id)
      fetchData()
    }
  }

  const handleCompleteTask = async (taskId: string) => {
    const result = await completeTask(`/exit/tasks/${taskId}/complete`, {})

    if (result) {
      showToast('success', 'Task completed successfully')
      // Refresh detail
      if (selectedCase) {
        handleViewDetail(selectedCase.id)
      }
      fetchData()
    }
  }

  const handleCalculateFnf = async () => {
    if (!selectedCase) return

    const result = await calculateFnf(`/exit/cases/${selectedCase.id}/settlement/calculate`, {
      leave_encashment_days: fnfForm.leave_encashment_days,
      bonus_dues: fnfForm.bonus_dues,
      reimbursements: fnfForm.reimbursements,
      other_earnings: fnfForm.other_earnings,
      loan_recovery: fnfForm.loan_recovery,
      advance_recovery: fnfForm.advance_recovery,
      other_deductions: fnfForm.other_deductions,
      notes: fnfForm.notes || undefined,
    })

    if (result) {
      showToast('success', 'F&F settlement calculated')
      setIsCalculateFnfOpen(false)
      setFnfForm({
        leave_encashment_days: 0,
        bonus_dues: 0,
        reimbursements: 0,
        other_earnings: 0,
        loan_recovery: 0,
        advance_recovery: 0,
        other_deductions: 0,
        notes: '',
      })
      handleViewDetail(selectedCase.id)
      fetchData()
    }
  }

  const handleCompleteExit = async () => {
    if (!selectedCase) return

    const result = await completeExit(`/exit/cases/${selectedCase.id}/complete`, {})

    if (result) {
      showToast('success', 'Exit process completed!')
      setIsDetailOpen(false)
      setSelectedCase(null)
      fetchData()
    }
  }

  const formatCurrency = (amount?: string | number) => {
    if (!amount) return '0'
    const num = typeof amount === 'string' ? parseFloat(amount) : amount
    return new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(num)
  }

  // Loading state
  if (isLoadingStats || isLoadingCases) {
    return (
      <div className="space-y-6">
        <PageHeader
          title="Exit Management"
          description="Manage employee offboarding and clearance"
          icon={<UserMinus className="h-6 w-6" />}
        />
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map((i) => (
            <Card key={i}>
              <CardContent className="pt-6">
                <Skeleton className="h-16 w-full" />
              </CardContent>
            </Card>
          ))}
        </div>
        <Card>
          <CardContent className="pt-6">
            <Skeleton className="h-64 w-full" />
          </CardContent>
        </Card>
      </div>
    )
  }

  // Active/In-progress exits
  const activeExits = exitCases.filter(e => !['completed', 'cancelled'].includes(e.status))
  const completedExits = exitCases.filter(e => e.status === 'completed')

  return (
    <div className="space-y-6">
      <PageHeader
        title="Exit Management"
        description="Manage employee offboarding and clearance"
        icon={<UserMinus className="h-6 w-6" />}
        actions={
          <div className="flex gap-2">
            <Button variant="outline" onClick={fetchData}>
              <RefreshCw className="h-4 w-4 mr-2" />
              Refresh
            </Button>
            <Dialog open={isInitiateOpen} onOpenChange={setIsInitiateOpen}>
              <DialogTrigger asChild>
                <Button>
                  <Plus className="h-4 w-4 mr-2" />
                  Initiate Exit
                </Button>
              </DialogTrigger>
              <DialogContent className="max-w-lg">
                <DialogHeader>
                  <DialogTitle>Initiate Exit Process</DialogTitle>
                  <DialogDescription>Start offboarding process for an employee</DialogDescription>
                </DialogHeader>
                <div className="grid gap-4 py-4">
                  <div className="grid gap-2">
                    <Label>Employee *</Label>
                    <Select
                      value={initiateForm.employee_id}
                      onValueChange={(v) => setInitiateForm({ ...initiateForm, employee_id: v })}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select employee" />
                      </SelectTrigger>
                      <SelectContent>
                        {availableEmployees.map((emp) => (
                          <SelectItem key={emp.id} value={emp.id}>
                            {emp.full_name} ({emp.employee_code})
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="grid gap-2">
                    <Label>Exit Type</Label>
                    <Select
                      value={initiateForm.exit_type}
                      onValueChange={(v) => setInitiateForm({ ...initiateForm, exit_type: v })}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {Object.entries(exitTypes).map(([value, label]) => (
                          <SelectItem key={value} value={value}>{label}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="grid gap-2">
                      <Label>Resignation Date</Label>
                      <Input
                        type="date"
                        value={initiateForm.resignation_date}
                        onChange={(e) => setInitiateForm({ ...initiateForm, resignation_date: e.target.value })}
                      />
                    </div>
                    <div className="grid gap-2">
                      <Label>Requested LWD</Label>
                      <Input
                        type="date"
                        value={initiateForm.requested_lwd}
                        onChange={(e) => setInitiateForm({ ...initiateForm, requested_lwd: e.target.value })}
                      />
                    </div>
                  </div>
                  <div className="grid gap-2">
                    <Label>Reason Category</Label>
                    <Select
                      value={initiateForm.reason_category}
                      onValueChange={(v) => setInitiateForm({ ...initiateForm, reason_category: v })}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select reason" />
                      </SelectTrigger>
                      <SelectContent>
                        {reasonCategories.map((cat) => (
                          <SelectItem key={cat} value={cat}>{cat}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="grid gap-2">
                    <Label>Reason Details</Label>
                    <Textarea
                      value={initiateForm.reason}
                      onChange={(e) => setInitiateForm({ ...initiateForm, reason: e.target.value })}
                      placeholder="Additional details about the exit..."
                      rows={2}
                    />
                  </div>
                  <div className="grid gap-2">
                    <Label>Notes</Label>
                    <Textarea
                      value={initiateForm.notes}
                      onChange={(e) => setInitiateForm({ ...initiateForm, notes: e.target.value })}
                      placeholder="Internal notes..."
                      rows={2}
                    />
                  </div>
                </div>
                <DialogFooter>
                  <Button variant="outline" onClick={() => setIsInitiateOpen(false)}>Cancel</Button>
                  <Button onClick={handleInitiateExit} disabled={isInitiating}>
                    {isInitiating ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
                    Initiate Exit
                  </Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
          </div>
        }
      />

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-100 rounded-lg">
                <Clock className="h-5 w-5 text-blue-600" />
              </div>
              <div>
                <p className="text-2xl font-bold">{stats.initiated + stats.clearance_pending}</p>
                <p className="text-sm text-muted-foreground">Active Exits</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-red-100 rounded-lg">
                <Calendar className="h-5 w-5 text-red-600" />
              </div>
              <div>
                <p className="text-2xl font-bold">{stats.this_month}</p>
                <p className="text-sm text-muted-foreground">This Month</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-yellow-100 rounded-lg">
                <IndianRupee className="h-5 w-5 text-yellow-600" />
              </div>
              <div>
                <p className="text-2xl font-bold">{stats.fnf_pending}</p>
                <p className="text-sm text-muted-foreground">Pending Settlements</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-green-100 rounded-lg">
                <CheckCircle className="h-5 w-5 text-green-600" />
              </div>
              <div>
                <p className="text-2xl font-bold">{stats.completed}</p>
                <p className="text-sm text-muted-foreground">Completed</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="active">Active Exits ({activeExits.length})</TabsTrigger>
          <TabsTrigger value="completed">Completed ({completedExits.length})</TabsTrigger>
        </TabsList>

        <TabsContent value="active" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle>Active Exit Cases</CardTitle>
              <CardDescription>Employees currently in offboarding process</CardDescription>
            </CardHeader>
            <CardContent>
              {activeExits.length === 0 ? (
                <div className="text-center py-12 text-muted-foreground">
                  <UserMinus className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>No active exit cases</p>
                  <Button className="mt-4" onClick={() => setIsInitiateOpen(true)}>
                    <Plus className="h-4 w-4 mr-2" />
                    Initiate First Exit
                  </Button>
                </div>
              ) : (
                <div className="space-y-4">
                  {activeExits.map((exitCase) => (
                    <div key={exitCase.id} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                      <div className="flex items-start justify-between mb-3">
                        <div>
                          <div className="flex items-center gap-2">
                            <h4 className="font-medium">{exitCase.employee?.full_name || 'Unknown Employee'}</h4>
                            <Badge className={typeColors[exitCase.exit_type] || 'bg-gray-100'}>
                              {exitTypes[exitCase.exit_type] || exitCase.exit_type}
                            </Badge>
                            <Badge className={statusColors[exitCase.status] || 'bg-gray-100'}>
                              {statusLabels[exitCase.status] || exitCase.status}
                            </Badge>
                          </div>
                          <p className="text-sm text-muted-foreground">
                            {exitCase.employee?.employee_code} - {exitCase.employee?.department_name || 'No Department'}
                          </p>
                          {exitCase.reason_category && (
                            <p className="text-sm text-muted-foreground mt-1">
                              Reason: {exitCase.reason_category}
                            </p>
                          )}
                        </div>
                        <div className="text-right">
                          <p className="text-sm font-medium">Last Working Day</p>
                          <p className="text-sm text-muted-foreground">
                            {exitCase.last_working_day
                              ? new Date(exitCase.last_working_day).toLocaleDateString('en-IN')
                              : exitCase.requested_lwd
                                ? `Requested: ${new Date(exitCase.requested_lwd).toLocaleDateString('en-IN')}`
                                : 'Not set'}
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center gap-4">
                        <div className="flex-1">
                          <div className="flex items-center justify-between mb-1">
                            <span className="text-sm text-muted-foreground">Clearance Progress</span>
                            <span className="text-sm font-medium">{exitCase.tasks_completed}/{exitCase.tasks_total}</span>
                          </div>
                          <Progress value={exitCase.clearance_progress} />
                        </div>
                        <span className="text-sm font-medium w-16">{exitCase.clearance_progress}%</span>
                        <Button variant="outline" size="sm" onClick={() => handleViewDetail(exitCase.id)}>
                          <Eye className="h-3 w-3 mr-1" /> View
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="completed" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle>Completed Exits</CardTitle>
              <CardDescription>Employees who have completed the exit process</CardDescription>
            </CardHeader>
            <CardContent>
              {completedExits.length === 0 ? (
                <div className="text-center py-12 text-muted-foreground">
                  <CheckCircle className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>No completed exits yet</p>
                </div>
              ) : (
                <div className="border rounded-lg overflow-hidden">
                  <table className="w-full">
                    <thead className="bg-muted/50">
                      <tr>
                        <th className="text-left p-4 font-medium">Employee</th>
                        <th className="text-left p-4 font-medium">Exit Type</th>
                        <th className="text-left p-4 font-medium">Last Working Day</th>
                        <th className="text-left p-4 font-medium">Reason</th>
                        <th className="text-right p-4 font-medium">Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {completedExits.map((exitCase) => (
                        <tr key={exitCase.id} className="border-t hover:bg-muted/30">
                          <td className="p-4">
                            <div>
                              <p className="font-medium">{exitCase.employee?.full_name}</p>
                              <p className="text-xs text-muted-foreground">{exitCase.employee?.employee_code}</p>
                            </div>
                          </td>
                          <td className="p-4">
                            <Badge className={typeColors[exitCase.exit_type] || 'bg-gray-100'}>
                              {exitTypes[exitCase.exit_type] || exitCase.exit_type}
                            </Badge>
                          </td>
                          <td className="p-4 text-muted-foreground">
                            {exitCase.last_working_day
                              ? new Date(exitCase.last_working_day).toLocaleDateString('en-IN')
                              : '-'}
                          </td>
                          <td className="p-4 text-muted-foreground">
                            {exitCase.reason_category || '-'}
                          </td>
                          <td className="p-4 text-right">
                            <Button variant="outline" size="sm" onClick={() => handleViewDetail(exitCase.id)}>
                              <Eye className="h-3 w-3 mr-1" /> View
                            </Button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Exit Detail Dialog */}
      <Dialog open={isDetailOpen} onOpenChange={setIsDetailOpen}>
        <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              Exit Case: {selectedCase?.employee?.full_name}
              <Badge className={statusColors[selectedCase?.status || ''] || 'bg-gray-100'}>
                {statusLabels[selectedCase?.status || ''] || selectedCase?.status}
              </Badge>
            </DialogTitle>
            <DialogDescription>
              {selectedCase?.employee?.employee_code} - {selectedCase?.employee?.department_name}
            </DialogDescription>
          </DialogHeader>

          {isLoadingDetail ? (
            <div className="py-8">
              <Skeleton className="h-32 w-full mb-4" />
              <Skeleton className="h-32 w-full" />
            </div>
          ) : selectedCase ? (
            <div className="space-y-6 py-4">
              {/* Exit Info */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div>
                  <p className="text-sm text-muted-foreground">Exit Type</p>
                  <p className="font-medium">{exitTypes[selectedCase.exit_type] || selectedCase.exit_type}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Resignation Date</p>
                  <p className="font-medium">
                    {selectedCase.resignation_date
                      ? new Date(selectedCase.resignation_date).toLocaleDateString('en-IN')
                      : '-'}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Last Working Day</p>
                  <p className="font-medium">
                    {selectedCase.last_working_day
                      ? new Date(selectedCase.last_working_day).toLocaleDateString('en-IN')
                      : selectedCase.approved_lwd
                        ? new Date(selectedCase.approved_lwd).toLocaleDateString('en-IN')
                        : 'Not approved'}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Notice Period</p>
                  <p className="font-medium">{selectedCase.notice_period_days || 30} days</p>
                </div>
              </div>

              {selectedCase.reason_category && (
                <div>
                  <p className="text-sm text-muted-foreground">Reason</p>
                  <p className="font-medium">{selectedCase.reason_category}</p>
                  {selectedCase.reason && <p className="text-sm text-muted-foreground mt-1">{selectedCase.reason}</p>}
                </div>
              )}

              {/* Action Buttons */}
              {selectedCase.status === 'initiated' && (
                <div className="flex gap-2">
                  <Button onClick={() => setIsApproveOpen(true)}>
                    <CheckCircle className="h-4 w-4 mr-2" />
                    Approve Exit
                  </Button>
                </div>
              )}

              {/* Clearance Tasks */}
              <div>
                <div className="flex items-center justify-between mb-3">
                  <h3 className="font-semibold">Clearance Tasks</h3>
                  <span className="text-sm text-muted-foreground">
                    {selectedCase.tasks_completed}/{selectedCase.tasks_total} completed
                  </span>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {selectedCase.clearance_tasks?.map((task) => {
                    const Icon = departmentIcons[task.department] || FileText
                    return (
                      <Card key={task.id} className={task.status === 'cleared' ? 'bg-green-50' : ''}>
                        <CardContent className="p-3">
                          <div className="flex items-start justify-between">
                            <div className="flex items-center gap-2">
                              <div className={`p-1.5 rounded ${task.status === 'cleared' ? 'bg-green-100' : 'bg-muted'}`}>
                                <Icon className={`h-4 w-4 ${task.status === 'cleared' ? 'text-green-600' : 'text-muted-foreground'}`} />
                              </div>
                              <div>
                                <p className="font-medium text-sm">{task.task_name}</p>
                                <p className="text-xs text-muted-foreground">{task.department}</p>
                              </div>
                            </div>
                            {task.status === 'cleared' ? (
                              <Badge className="bg-green-100 text-green-800">
                                <CheckCircle className="h-3 w-3 mr-1" />
                                Done
                              </Badge>
                            ) : task.status === 'pending' ? (
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => handleCompleteTask(task.id)}
                                disabled={isCompletingTask}
                              >
                                {isCompletingTask ? (
                                  <Loader2 className="h-3 w-3 animate-spin" />
                                ) : (
                                  <CheckSquare className="h-3 w-3 mr-1" />
                                )}
                                Complete
                              </Button>
                            ) : (
                              <Badge className={clearanceTaskColors[task.status] || 'bg-gray-100'}>
                                {task.status}
                              </Badge>
                            )}
                          </div>
                        </CardContent>
                      </Card>
                    )
                  })}
                </div>
              </div>

              {/* Final Settlement */}
              {selectedCase.final_settlement ? (
                <div>
                  <h3 className="font-semibold mb-3">Full & Final Settlement</h3>
                  <Card>
                    <CardContent className="p-4">
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <h4 className="font-medium text-sm mb-2 text-green-600">Earnings</h4>
                          <div className="space-y-1 text-sm">
                            <div className="flex justify-between">
                              <span>Basic Salary Dues</span>
                              <span>{formatCurrency(selectedCase.final_settlement.basic_salary_dues)}</span>
                            </div>
                            <div className="flex justify-between">
                              <span>Leave Encashment</span>
                              <span>{formatCurrency(selectedCase.final_settlement.leave_encashment)}</span>
                            </div>
                            <div className="flex justify-between">
                              <span>Bonus</span>
                              <span>{formatCurrency(selectedCase.final_settlement.bonus_dues)}</span>
                            </div>
                            <div className="flex justify-between">
                              <span>Gratuity</span>
                              <span>{formatCurrency(selectedCase.final_settlement.gratuity)}</span>
                            </div>
                            <div className="flex justify-between font-medium border-t pt-1">
                              <span>Total Earnings</span>
                              <span className="text-green-600">{formatCurrency(selectedCase.final_settlement.total_earnings)}</span>
                            </div>
                          </div>
                        </div>
                        <div>
                          <h4 className="font-medium text-sm mb-2 text-red-600">Deductions</h4>
                          <div className="space-y-1 text-sm">
                            <div className="flex justify-between">
                              <span>Notice Recovery</span>
                              <span>{formatCurrency(selectedCase.final_settlement.notice_recovery)}</span>
                            </div>
                            <div className="flex justify-between">
                              <span>Asset Recovery</span>
                              <span>{formatCurrency(selectedCase.final_settlement.asset_recovery)}</span>
                            </div>
                            <div className="flex justify-between">
                              <span>Loan Recovery</span>
                              <span>{formatCurrency(selectedCase.final_settlement.loan_recovery)}</span>
                            </div>
                            <div className="flex justify-between">
                              <span>TDS</span>
                              <span>{formatCurrency(selectedCase.final_settlement.tds)}</span>
                            </div>
                            <div className="flex justify-between font-medium border-t pt-1">
                              <span>Total Deductions</span>
                              <span className="text-red-600">{formatCurrency(selectedCase.final_settlement.total_deductions)}</span>
                            </div>
                          </div>
                        </div>
                      </div>
                      <div className="mt-4 pt-4 border-t flex justify-between items-center">
                        <span className="text-lg font-semibold">Net Payable</span>
                        <span className="text-2xl font-bold text-primary">
                          {formatCurrency(selectedCase.final_settlement.net_payable)}
                        </span>
                      </div>
                      <div className="mt-2 flex items-center gap-2">
                        <Badge className={
                          selectedCase.final_settlement.status === 'paid' ? 'bg-green-100 text-green-800' :
                          selectedCase.final_settlement.status === 'approved' ? 'bg-blue-100 text-blue-800' :
                          'bg-yellow-100 text-yellow-800'
                        }>
                          {selectedCase.final_settlement.status.toUpperCase()}
                        </Badge>
                        {selectedCase.final_settlement.payment_date && (
                          <span className="text-sm text-muted-foreground">
                            Paid on {new Date(selectedCase.final_settlement.payment_date).toLocaleDateString('en-IN')}
                          </span>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                </div>
              ) : selectedCase.status === 'clearance_completed' ? (
                <div>
                  <h3 className="font-semibold mb-3">Full & Final Settlement</h3>
                  <Card className="bg-muted/30">
                    <CardContent className="p-6 text-center">
                      <IndianRupee className="h-10 w-10 mx-auto text-muted-foreground mb-2" />
                      <p className="text-muted-foreground mb-4">F&F settlement not calculated yet</p>
                      <Button onClick={() => setIsCalculateFnfOpen(true)}>
                        <CreditCard className="h-4 w-4 mr-2" />
                        Calculate F&F Settlement
                      </Button>
                    </CardContent>
                  </Card>
                </div>
              ) : null}

              {/* Complete Exit Button */}
              {selectedCase.status === 'fnf_pending' && selectedCase.final_settlement && (
                <div className="flex justify-end">
                  <Button onClick={handleCompleteExit} className="bg-green-600 hover:bg-green-700">
                    <CheckCircle className="h-4 w-4 mr-2" />
                    Complete Exit Process
                  </Button>
                </div>
              )}
            </div>
          ) : null}
        </DialogContent>
      </Dialog>

      {/* Approve Exit Dialog */}
      <Dialog open={isApproveOpen} onOpenChange={setIsApproveOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Approve Exit</DialogTitle>
            <DialogDescription>Confirm the last working day for this employee</DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div className="grid gap-2">
              <Label>Approved Last Working Day *</Label>
              <Input
                type="date"
                value={approveForm.approved_lwd}
                onChange={(e) => setApproveForm({ ...approveForm, approved_lwd: e.target.value })}
              />
              {selectedCase?.requested_lwd && (
                <p className="text-sm text-muted-foreground">
                  Requested: {new Date(selectedCase.requested_lwd).toLocaleDateString('en-IN')}
                </p>
              )}
            </div>
            <div className="grid gap-2">
              <Label>Notes</Label>
              <Textarea
                value={approveForm.notes}
                onChange={(e) => setApproveForm({ ...approveForm, notes: e.target.value })}
                rows={2}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsApproveOpen(false)}>Cancel</Button>
            <Button onClick={handleApproveExit} disabled={isApproving}>
              {isApproving ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
              Approve Exit
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Calculate F&F Dialog */}
      <Dialog open={isCalculateFnfOpen} onOpenChange={setIsCalculateFnfOpen}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>Calculate F&F Settlement</DialogTitle>
            <DialogDescription>Enter settlement details</DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="grid gap-2">
                <Label>Leave Encashment Days</Label>
                <Input
                  type="number"
                  value={fnfForm.leave_encashment_days}
                  onChange={(e) => setFnfForm({ ...fnfForm, leave_encashment_days: parseInt(e.target.value) || 0 })}
                />
              </div>
              <div className="grid gap-2">
                <Label>Bonus Dues</Label>
                <Input
                  type="number"
                  value={fnfForm.bonus_dues}
                  onChange={(e) => setFnfForm({ ...fnfForm, bonus_dues: parseFloat(e.target.value) || 0 })}
                />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="grid gap-2">
                <Label>Reimbursements</Label>
                <Input
                  type="number"
                  value={fnfForm.reimbursements}
                  onChange={(e) => setFnfForm({ ...fnfForm, reimbursements: parseFloat(e.target.value) || 0 })}
                />
              </div>
              <div className="grid gap-2">
                <Label>Other Earnings</Label>
                <Input
                  type="number"
                  value={fnfForm.other_earnings}
                  onChange={(e) => setFnfForm({ ...fnfForm, other_earnings: parseFloat(e.target.value) || 0 })}
                />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="grid gap-2">
                <Label>Loan Recovery</Label>
                <Input
                  type="number"
                  value={fnfForm.loan_recovery}
                  onChange={(e) => setFnfForm({ ...fnfForm, loan_recovery: parseFloat(e.target.value) || 0 })}
                />
              </div>
              <div className="grid gap-2">
                <Label>Advance Recovery</Label>
                <Input
                  type="number"
                  value={fnfForm.advance_recovery}
                  onChange={(e) => setFnfForm({ ...fnfForm, advance_recovery: parseFloat(e.target.value) || 0 })}
                />
              </div>
            </div>
            <div className="grid gap-2">
              <Label>Other Deductions</Label>
              <Input
                type="number"
                value={fnfForm.other_deductions}
                onChange={(e) => setFnfForm({ ...fnfForm, other_deductions: parseFloat(e.target.value) || 0 })}
              />
            </div>
            <div className="grid gap-2">
              <Label>Notes</Label>
              <Textarea
                value={fnfForm.notes}
                onChange={(e) => setFnfForm({ ...fnfForm, notes: e.target.value })}
                rows={2}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsCalculateFnfOpen(false)}>Cancel</Button>
            <Button onClick={handleCalculateFnf} disabled={isCalculatingFnf}>
              {isCalculatingFnf ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
              Calculate Settlement
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
