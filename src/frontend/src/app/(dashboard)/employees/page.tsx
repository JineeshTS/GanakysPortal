'use client'

import * as React from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import { PageHeader } from '@/components/layout/page-header'
import { DataTable, Column } from '@/components/layout/data-table'
import { Pagination } from '@/components/layout/pagination'
import { EmptyState } from '@/components/layout/empty-state'
import { SearchInput } from '@/components/forms/search-input'
import { DatePicker } from '@/components/forms/date-picker'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { useDebounce, useApi } from '@/hooks'
import { useToast } from '@/hooks/use-toast'
import { formatCurrency, formatDate } from '@/lib/format'
import {
  Plus,
  Filter,
  Download,
  Upload,
  MoreVertical,
  Eye,
  Edit,
  Mail,
  Phone,
  X,
  FileSpreadsheet,
  FileText,
  ChevronRight,
  UserCheck,
  UserX,
  Users,
  Building2,
  Calendar,
  Briefcase,
  Loader2,
  Trash2,
  AlertTriangle
} from 'lucide-react'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog"
import type { Employee, EmploymentStatus, EmploymentType } from '@/types'

// Department and Designation mappings (fetched from API in production)
const departments: Record<string, string> = {
  '1': 'Engineering',
  '2': 'Human Resources',
  '3': 'Finance',
  '4': 'Marketing',
  '5': 'Sales',
  '6': 'Operations',
  '7': 'Product',
  '8': 'Design',
  '9': 'Legal',
  '10': 'Admin'
}

const designations: Record<string, string> = {
  '1': 'Software Engineer',
  '2': 'Senior Software Engineer',
  '3': 'Tech Lead',
  '4': 'Engineering Manager',
  '5': 'HR Executive',
  '6': 'HR Manager',
  '7': 'Accountant',
  '8': 'Finance Manager',
  '9': 'Marketing Executive',
  '10': 'Sales Executive'
}

// API response type
interface EmployeeApiResponse {
  id: string
  employee_code: string
  first_name: string
  middle_name: string | null
  last_name: string
  full_name: string
  date_of_birth: string | null
  gender: string | null
  date_of_joining: string
  department_name: string | null
  designation_name: string | null
  employment_status: string
  employment_type: string
  profile_photo_url: string | null
}

interface EmployeesListResponse {
  success: boolean
  data: EmployeeApiResponse[]
  meta: {
    page: number
    limit: number
    total: number
  }
}

interface QuickViewEmployee extends Employee {
  department_name?: string
  designation_name?: string
}

export default function EmployeesPage() {
  const router = useRouter()
  const { toast } = useToast()
  const [searchQuery, setSearchQuery] = React.useState('')
  const [employees, setEmployees] = React.useState<EmployeeApiResponse[]>([])
  const [page, setPage] = React.useState(1)
  const [pageSize, setPageSize] = React.useState(20)
  const [total, setTotal] = React.useState(0)
  const [sortBy, setSortBy] = React.useState('employee_code')
  const [sortOrder, setSortOrder] = React.useState<'asc' | 'desc'>('asc')
  const [isLoading, setIsLoading] = React.useState(true)
  const [error, setError] = React.useState<string | null>(null)

  const api = useApi<EmployeesListResponse>()
  const importApi = useApi()

  // Fetch employees from API
  const fetchEmployees = React.useCallback(async () => {
    setIsLoading(true)
    setError(null)
    try {
      const params = new URLSearchParams({
        page: String(page),
        limit: String(pageSize)
      })
      if (searchQuery) params.set('search', searchQuery)

      const result = await api.get(`/employees?${params.toString()}`)
      if (result && result.success) {
        setEmployees(result.data)
        setTotal(result.meta.total)
      }
    } catch (err) {
      setError('Failed to load employees')
    } finally {
      setIsLoading(false)
    }
  }, [api, page, pageSize, searchQuery])

  // Fetch on mount and when params change
  React.useEffect(() => {
    fetchEmployees()
  }, [page, pageSize])

  // Advanced filters
  const [showFilters, setShowFilters] = React.useState(false)
  const [statusFilter, setStatusFilter] = React.useState<string>('')
  const [departmentFilter, setDepartmentFilter] = React.useState<string>('')
  const [designationFilter, setDesignationFilter] = React.useState<string>('')
  const [employmentTypeFilter, setEmploymentTypeFilter] = React.useState<string>('')
  const [dateOfJoiningFrom, setDateOfJoiningFrom] = React.useState<string>('')
  const [dateOfJoiningTo, setDateOfJoiningTo] = React.useState<string>('')

  // Bulk selection
  const [selectedEmployees, setSelectedEmployees] = React.useState<string[]>([])
  const [selectAll, setSelectAll] = React.useState(false)

  // Quick view sidebar
  const [quickViewEmployee, setQuickViewEmployee] = React.useState<QuickViewEmployee | null>(null)

  // Delete dialog state
  const [deleteDialogOpen, setDeleteDialogOpen] = React.useState(false)
  const [employeeToDelete, setEmployeeToDelete] = React.useState<EmployeeApiResponse | null>(null)
  const [isDeleting, setIsDeleting] = React.useState(false)
  const deleteApi = useApi()

  const debouncedSearch = useDebounce(searchQuery, 300)

  // Trigger search when debounced value changes
  React.useEffect(() => {
    if (debouncedSearch !== undefined) {
      setPage(1) // Reset to first page on search
      fetchEmployees()
    }
  }, [debouncedSearch])

  // Filter and search - now mostly handled by API, but we keep client-side filtering for non-API filters
  const filteredEmployees = React.useMemo(() => {
    let result = [...employees]

    // Status filter (client-side for now)
    if (statusFilter) {
      result = result.filter(emp => emp.employment_status === statusFilter)
    }

    // Employment type filter (client-side for now)
    if (employmentTypeFilter) {
      result = result.filter(emp => emp.employment_type === employmentTypeFilter)
    }

    // Sort (client-side)
    result.sort((a, b) => {
      const aVal = a[sortBy as keyof EmployeeApiResponse]
      const bVal = b[sortBy as keyof EmployeeApiResponse]
      if (aVal === undefined || bVal === undefined) return 0
      if (aVal < bVal) return sortOrder === 'asc' ? -1 : 1
      if (aVal > bVal) return sortOrder === 'asc' ? 1 : -1
      return 0
    })

    return result
  }, [employees, statusFilter, employmentTypeFilter, sortBy, sortOrder])

  // Count active filters
  const activeFiltersCount = React.useMemo(() => {
    let count = 0
    if (statusFilter) count++
    if (departmentFilter) count++
    if (designationFilter) count++
    if (employmentTypeFilter) count++
    if (dateOfJoiningFrom) count++
    if (dateOfJoiningTo) count++
    return count
  }, [statusFilter, departmentFilter, designationFilter, employmentTypeFilter, dateOfJoiningFrom, dateOfJoiningTo])

  const clearFilters = () => {
    setStatusFilter('')
    setDepartmentFilter('')
    setDesignationFilter('')
    setEmploymentTypeFilter('')
    setDateOfJoiningFrom('')
    setDateOfJoiningTo('')
  }

  const handleSort = (key: string) => {
    if (sortBy === key) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')
    } else {
      setSortBy(key)
      setSortOrder('asc')
    }
  }

  // Handle select all
  const handleSelectAll = () => {
    if (selectAll) {
      setSelectedEmployees([])
    } else {
      setSelectedEmployees(filteredEmployees.map(emp => emp.id))
    }
    setSelectAll(!selectAll)
  }

  // Handle individual selection
  const handleSelectEmployee = (id: string) => {
    if (selectedEmployees.includes(id)) {
      setSelectedEmployees(selectedEmployees.filter(empId => empId !== id))
    } else {
      setSelectedEmployees([...selectedEmployees, id])
    }
  }

  // Bulk actions
  const handleBulkActivate = () => {
    setEmployees(employees.map(emp =>
      selectedEmployees.includes(emp.id)
        ? { ...emp, employment_status: 'active' as EmploymentStatus }
        : emp
    ))
    setSelectedEmployees([])
    setSelectAll(false)
  }

  const handleBulkDeactivate = () => {
    setEmployees(employees.map(emp =>
      selectedEmployees.includes(emp.id)
        ? { ...emp, employment_status: 'resigned' as EmploymentStatus }
        : emp
    ))
    setSelectedEmployees([])
    setSelectAll(false)
  }

  // Delete employee
  const handleDeleteClick = (emp: EmployeeApiResponse, e: React.MouseEvent) => {
    e.stopPropagation()
    setEmployeeToDelete(emp)
    setDeleteDialogOpen(true)
  }

  const handleDeleteConfirm = async () => {
    if (!employeeToDelete) return

    setIsDeleting(true)
    try {
      await deleteApi.delete(`/employees/${employeeToDelete.id}`)
      // Remove from local state
      setEmployees(employees.filter(emp => emp.id !== employeeToDelete.id))
      setTotal(prev => prev - 1)
      setDeleteDialogOpen(false)
      setEmployeeToDelete(null)
    } catch (error) {
      toast.error('Failed to delete employee', 'Please try again or contact support')
    } finally {
      setIsDeleting(false)
    }
  }

  // Export functions
  const exportToExcel = () => {
    // In production, this would use a library like xlsx or call an API
    const csvContent = generateCSV(filteredEmployees)
    downloadFile(csvContent, 'employees.csv', 'text/csv')
  }

  const exportToPDF = async () => {
    try {
      // Create PDF content using browser's print functionality
      // This creates a print-friendly version of the employee list
      const printWindow = window.open('', '_blank')
      if (!printWindow) {
        alert('Please allow popups to export PDF')
        return
      }

      const employeeRows = filteredEmployees.map(emp => `
        <tr>
          <td style="padding: 8px; border-bottom: 1px solid #ddd;">${emp.employee_code}</td>
          <td style="padding: 8px; border-bottom: 1px solid #ddd;">${emp.full_name}</td>
          <td style="padding: 8px; border-bottom: 1px solid #ddd;">${emp.work_email}</td>
          <td style="padding: 8px; border-bottom: 1px solid #ddd;">${emp.mobile || '-'}</td>
          <td style="padding: 8px; border-bottom: 1px solid #ddd;">${departments[emp.department_id] || '-'}</td>
          <td style="padding: 8px; border-bottom: 1px solid #ddd;">${designations[emp.designation_id] || '-'}</td>
          <td style="padding: 8px; border-bottom: 1px solid #ddd;">${emp.date_of_joining || '-'}</td>
          <td style="padding: 8px; border-bottom: 1px solid #ddd;">${emp.employment_status}</td>
        </tr>
      `).join('')

      printWindow.document.write(`
        <!DOCTYPE html>
        <html>
        <head>
          <title>Employee List Export</title>
          <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            h1 { color: #333; margin-bottom: 20px; }
            table { width: 100%; border-collapse: collapse; }
            th { background-color: #f4f4f4; padding: 10px; text-align: left; border-bottom: 2px solid #ddd; }
            td { padding: 8px; border-bottom: 1px solid #ddd; }
            .meta { color: #666; font-size: 12px; margin-bottom: 20px; }
            @media print {
              body { margin: 0; }
            }
          </style>
        </head>
        <body>
          <h1>Employee List</h1>
          <p class="meta">Generated on ${new Date().toLocaleDateString('en-IN', { day: 'numeric', month: 'long', year: 'numeric' })} | Total: ${filteredEmployees.length} employees</p>
          <table>
            <thead>
              <tr>
                <th>Employee Code</th>
                <th>Name</th>
                <th>Email</th>
                <th>Mobile</th>
                <th>Department</th>
                <th>Designation</th>
                <th>Joining Date</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              ${employeeRows}
            </tbody>
          </table>
          <script>
            window.onload = function() {
              window.print()
              window.onafterprint = function() {
                window.close()
              }
            }
          </script>
        </body>
        </html>
      `)
      printWindow.document.close()
    } catch (error) {
      toast.error('Failed to export PDF', 'Please try again')
    }
  }

  const generateCSV = (data: Employee[]) => {
    const headers = ['Employee Code', 'Name', 'Email', 'Mobile', 'Department', 'Designation', 'Date of Joining', 'Status', 'CTC']
    const rows = data.map(emp => [
      emp.employee_code || '',
      emp.full_name || '',
      emp.work_email || '',
      emp.mobile || '',
      departments[emp.department_id] || '',
      designations[emp.designation_id] || '',
      emp.date_of_joining || '',
      emp.employment_status || '',
      emp.ctc?.toString() || ''
    ])

    return [headers, ...rows].map(row => row.join(',')).join('\n')
  }

  const downloadFile = (content: string, filename: string, type: string) => {
    const blob = new Blob([content], { type })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    a.click()
    URL.revokeObjectURL(url)
  }

  // Open quick view
  const openQuickView = (emp: Employee, e: React.MouseEvent) => {
    e.stopPropagation()
    setQuickViewEmployee({
      ...emp,
      department_name: departments[emp.department_id],
      designation_name: designations[emp.designation_id]
    })
  }

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

  const formatCTC = (ctc: number) => {
    if (ctc >= 100000) {
      return `${(ctc / 100000).toFixed(1)}L`
    }
    return ctc.toLocaleString('en-IN')
  }

  // Stats
  const stats = React.useMemo(() => {
    const totalCount = total || employees.length
    const active = employees.filter(e => e.employment_status === 'active').length
    const probation = employees.filter(e => e.employment_status === 'probation').length
    const noticePeriod = employees.filter(e => e.employment_status === 'notice_period').length
    return { total: totalCount, active, probation, noticePeriod }
  }, [employees, total])

  const columns: Column<EmployeeApiResponse>[] = [
    {
      key: 'select',
      header: (
        <input
          type="checkbox"
          checked={selectAll}
          onChange={handleSelectAll}
          className="h-4 w-4 rounded border-gray-300"
        />
      ) as unknown as string,
      accessor: (row) => (
        <input
          type="checkbox"
          checked={selectedEmployees.includes(row.id)}
          onChange={() => handleSelectEmployee(row.id)}
          onClick={(e) => e.stopPropagation()}
          className="h-4 w-4 rounded border-gray-300"
        />
      )
    },
    {
      key: 'employee_code',
      header: 'Employee',
      sortable: true,
      accessor: (row) => (
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-primary/10 rounded-full flex items-center justify-center">
            <span className="text-sm font-medium text-primary">
              {row.first_name.charAt(0)}{row.last_name.charAt(0)}
            </span>
          </div>
          <div>
            <p className="font-medium">{row.full_name}</p>
            <p className="text-sm text-muted-foreground">{row.employee_code}</p>
          </div>
        </div>
      )
    },
    {
      key: 'department',
      header: 'Department',
      accessor: (row) => (
        <div>
          <p>{row.department_name || '-'}</p>
          <p className="text-sm text-muted-foreground">{row.designation_name || '-'}</p>
        </div>
      )
    },
    {
      key: 'gender',
      header: 'Gender',
      accessor: (row) => (
        <span className="capitalize">{row.gender || '-'}</span>
      )
    },
    {
      key: 'employment_type',
      header: 'Type',
      accessor: (row) => getTypeBadge(row.employment_type as EmploymentType)
    },
    {
      key: 'employment_status',
      header: 'Status',
      sortable: true,
      accessor: (row) => getStatusBadge(row.employment_status as EmploymentStatus)
    },
    {
      key: 'date_of_joining',
      header: 'Joined',
      sortable: true,
      accessor: (row) => formatDate(row.date_of_joining, { format: 'long' })
    },
    {
      key: 'actions',
      header: '',
      accessor: (row) => (
        <div className="flex items-center gap-1">
          <Button variant="ghost" size="icon" onClick={(e) => openQuickView(row as unknown as Employee, e)} title="Quick View">
            <Eye className="h-4 w-4" />
          </Button>
          <Button variant="ghost" size="icon" asChild>
            <Link href={`/employees/${row.id}/edit`}>
              <Edit className="h-4 w-4" />
            </Link>
          </Button>
          <Button
            variant="ghost"
            size="icon"
            onClick={(e) => handleDeleteClick(row, e)}
            title="Delete"
            className="text-red-600 hover:text-red-700 hover:bg-red-50"
          >
            <Trash2 className="h-4 w-4" />
          </Button>
        </div>
      )
    }
  ]

  return (
    <div className="space-y-6">
      <PageHeader
        title="Employees"
        description="Manage your organization's workforce"
        breadcrumbs={[
          { label: 'Dashboard', href: '/' },
          { label: 'Employees' }
        ]}
        actions={
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={() => document.getElementById('employee-import-input')?.click()}>
              <Upload className="h-4 w-4 mr-2" />
              Import
            </Button>
            <input
              id="employee-import-input"
              type="file"
              accept=".csv,.xlsx,.xls"
              className="hidden"
              onChange={async (e) => {
                const file = e.target.files?.[0]
                if (file) {
                  const formData = new FormData()
                  formData.append('file', file)
                  try {
                    const response = await importApi.postFormData('/employees/import', formData)
                    if (response) {
                      alert('Employees imported successfully!')
                      fetchEmployees()
                    } else {
                      alert('Failed to import employees. Please check the file format.')
                    }
                  } catch {
                    alert('Failed to import employees')
                  }
                  e.target.value = ''
                }
              }}
            />
            <div className="relative group">
              <Button variant="outline" size="sm">
                <Download className="h-4 w-4 mr-2" />
                Export
              </Button>
              <div className="absolute right-0 top-full mt-1 hidden group-hover:block bg-white border rounded-md shadow-lg z-10 min-w-[140px]">
                <button
                  onClick={exportToExcel}
                  className="flex items-center gap-2 w-full px-3 py-2 text-sm hover:bg-muted"
                >
                  <FileSpreadsheet className="h-4 w-4" />
                  Export to Excel
                </button>
                <button
                  onClick={exportToPDF}
                  className="flex items-center gap-2 w-full px-3 py-2 text-sm hover:bg-muted"
                >
                  <FileText className="h-4 w-4" />
                  Export to PDF
                </button>
              </div>
            </div>
            <Button asChild>
              <Link href="/employees/add">
                <Plus className="h-4 w-4 mr-2" />
                Add Employee
              </Link>
            </Button>
          </div>
        }
      />

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Total Employees</p>
                <p className="text-2xl font-bold">{stats.total}</p>
              </div>
              <Users className="h-8 w-8 text-muted-foreground" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Active</p>
                <p className="text-2xl font-bold text-green-600">{stats.active}</p>
              </div>
              <UserCheck className="h-8 w-8 text-green-600" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Probation</p>
                <p className="text-2xl font-bold text-blue-600">{stats.probation}</p>
              </div>
              <Briefcase className="h-8 w-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Notice Period</p>
                <p className="text-2xl font-bold text-yellow-600">{stats.noticePeriod}</p>
              </div>
              <UserX className="h-8 w-8 text-yellow-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Bulk Actions Bar */}
      {selectedEmployees.length > 0 && (
        <Card className="bg-primary/5 border-primary/20">
          <CardContent className="py-3">
            <div className="flex items-center justify-between">
              <p className="text-sm font-medium">
                {selectedEmployees.length} employee{selectedEmployees.length > 1 ? 's' : ''} selected
              </p>
              <div className="flex items-center gap-2">
                <Button variant="outline" size="sm" onClick={handleBulkActivate}>
                  <UserCheck className="h-4 w-4 mr-1" />
                  Activate
                </Button>
                <Button variant="outline" size="sm" onClick={handleBulkDeactivate}>
                  <UserX className="h-4 w-4 mr-1" />
                  Deactivate
                </Button>
                <Button variant="ghost" size="sm" onClick={() => { setSelectedEmployees([]); setSelectAll(false) }}>
                  <X className="h-4 w-4 mr-1" />
                  Clear
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Search and Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col gap-4">
            <div className="flex flex-col sm:flex-row gap-4">
              <div className="flex-1">
                <SearchInput
                  value={searchQuery}
                  onChange={setSearchQuery}
                  placeholder="Search by name, code, email, or mobile..."
                />
              </div>
              <Button
                variant={showFilters ? "secondary" : "outline"}
                onClick={() => setShowFilters(!showFilters)}
              >
                <Filter className="h-4 w-4 mr-2" />
                Filters
                {activeFiltersCount > 0 && (
                  <Badge className="ml-2 bg-primary text-primary-foreground">{activeFiltersCount}</Badge>
                )}
              </Button>
            </div>

            {/* Advanced Filters */}
            {showFilters && (
              <div className="pt-4 border-t">
                <div className="grid gap-4 md:grid-cols-3 lg:grid-cols-6">
                  <div>
                    <label className="text-sm font-medium mb-1 block">Department</label>
                    <select
                      value={departmentFilter}
                      onChange={(e) => setDepartmentFilter(e.target.value)}
                      className="h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                    >
                      <option value="">All Departments</option>
                      {Object.entries(departments).map(([id, name]) => (
                        <option key={id} value={id}>{name}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="text-sm font-medium mb-1 block">Designation</label>
                    <select
                      value={designationFilter}
                      onChange={(e) => setDesignationFilter(e.target.value)}
                      className="h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                    >
                      <option value="">All Designations</option>
                      {Object.entries(designations).map(([id, name]) => (
                        <option key={id} value={id}>{name}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="text-sm font-medium mb-1 block">Status</label>
                    <select
                      value={statusFilter}
                      onChange={(e) => setStatusFilter(e.target.value)}
                      className="h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                    >
                      <option value="">All Status</option>
                      <option value="active">Active</option>
                      <option value="probation">Probation</option>
                      <option value="notice_period">Notice Period</option>
                      <option value="resigned">Resigned</option>
                      <option value="terminated">Terminated</option>
                    </select>
                  </div>
                  <div>
                    <label className="text-sm font-medium mb-1 block">Employment Type</label>
                    <select
                      value={employmentTypeFilter}
                      onChange={(e) => setEmploymentTypeFilter(e.target.value)}
                      className="h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                    >
                      <option value="">All Types</option>
                      <option value="full_time">Full Time</option>
                      <option value="part_time">Part Time</option>
                      <option value="contract">Contract</option>
                      <option value="intern">Intern</option>
                      <option value="consultant">Consultant</option>
                    </select>
                  </div>
                  <div>
                    <label className="text-sm font-medium mb-1 block">DOJ From</label>
                    <input
                      type="date"
                      value={dateOfJoiningFrom}
                      onChange={(e) => setDateOfJoiningFrom(e.target.value)}
                      className="h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                    />
                  </div>
                  <div>
                    <label className="text-sm font-medium mb-1 block">DOJ To</label>
                    <input
                      type="date"
                      value={dateOfJoiningTo}
                      onChange={(e) => setDateOfJoiningTo(e.target.value)}
                      className="h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                    />
                  </div>
                </div>
                {activeFiltersCount > 0 && (
                  <div className="mt-4 flex justify-end">
                    <Button variant="ghost" size="sm" onClick={clearFilters}>
                      <X className="h-4 w-4 mr-1" />
                      Clear all filters
                    </Button>
                  </div>
                )}
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Employee Table */}
      {isLoading ? (
        <Card>
          <CardContent className="py-12">
            <div className="flex flex-col items-center justify-center">
              <Loader2 className="h-8 w-8 animate-spin text-primary mb-4" />
              <p className="text-muted-foreground">Loading employees...</p>
            </div>
          </CardContent>
        </Card>
      ) : error ? (
        <Card>
          <CardContent className="py-12">
            <div className="flex flex-col items-center justify-center text-center">
              <p className="text-red-600 mb-4">{error}</p>
              <Button onClick={fetchEmployees}>Retry</Button>
            </div>
          </CardContent>
        </Card>
      ) : filteredEmployees.length === 0 ? (
        <EmptyState
          type="employees"
          action={{
            label: 'Add Employee',
            onClick: () => router.push('/employees/add')
          }}
        />
      ) : (
        <>
          <DataTable
            data={filteredEmployees}
            columns={columns}
            keyExtractor={(row) => row.id}
            sortBy={sortBy}
            sortOrder={sortOrder}
            onSort={handleSort}
            onRowClick={(row) => router.push(`/employees/${row.id}`)}
          />

          <Pagination
            page={page}
            pageSize={pageSize}
            total={total}
            totalPages={Math.ceil(total / pageSize)}
            onPageChange={setPage}
            onPageSizeChange={setPageSize}
          />
        </>
      )}

      {/* Quick View Sidebar */}
      {quickViewEmployee && (
        <>
          <div
            className="fixed inset-0 bg-black/20 z-40"
            onClick={() => setQuickViewEmployee(null)}
          />
          <div className="fixed right-0 top-0 h-full w-96 bg-white shadow-xl z-50 overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-lg font-semibold">Quick View</h2>
                <Button variant="ghost" size="icon" onClick={() => setQuickViewEmployee(null)}>
                  <X className="h-5 w-5" />
                </Button>
              </div>

              {/* Employee Header */}
              <div className="flex items-center gap-4 mb-6">
                <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center">
                  <span className="text-xl font-semibold text-primary">
                    {quickViewEmployee.first_name.charAt(0)}{quickViewEmployee.last_name.charAt(0)}
                  </span>
                </div>
                <div>
                  <h3 className="font-semibold text-lg">{quickViewEmployee.full_name}</h3>
                  <p className="text-sm text-muted-foreground">{quickViewEmployee.employee_code}</p>
                  {getStatusBadge(quickViewEmployee.employment_status)}
                </div>
              </div>

              {/* Details */}
              <div className="space-y-4">
                <div>
                  <h4 className="text-sm font-medium text-muted-foreground mb-2">Contact</h4>
                  <div className="space-y-2">
                    <div className="flex items-center gap-2 text-sm">
                      <Mail className="h-4 w-4 text-muted-foreground" />
                      <span>{quickViewEmployee.work_email}</span>
                    </div>
                    <div className="flex items-center gap-2 text-sm">
                      <Phone className="h-4 w-4 text-muted-foreground" />
                      <span>{quickViewEmployee.mobile}</span>
                    </div>
                  </div>
                </div>

                <div>
                  <h4 className="text-sm font-medium text-muted-foreground mb-2">Employment</h4>
                  <div className="space-y-2 text-sm">
                    <div className="flex items-center gap-2">
                      <Building2 className="h-4 w-4 text-muted-foreground" />
                      <span>{quickViewEmployee.department_name}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Briefcase className="h-4 w-4 text-muted-foreground" />
                      <span>{quickViewEmployee.designation_name}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Calendar className="h-4 w-4 text-muted-foreground" />
                      <span>Joined {formatDate(quickViewEmployee.date_of_joining, { format: 'long' })}</span>
                    </div>
                  </div>
                </div>

                <div>
                  <h4 className="text-sm font-medium text-muted-foreground mb-2">Compensation</h4>
                  <p className="text-lg font-semibold">{formatCurrency(quickViewEmployee.ctc)}/year</p>
                  {getTypeBadge(quickViewEmployee.employment_type)}
                </div>

                <div>
                  <h4 className="text-sm font-medium text-muted-foreground mb-2">Personal</h4>
                  <div className="grid grid-cols-2 gap-2 text-sm">
                    <div>
                      <span className="text-muted-foreground">DOB:</span>
                      <span className="ml-1">{formatDate(quickViewEmployee.date_of_birth, { format: 'long' })}</span>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Blood:</span>
                      <span className="ml-1">{quickViewEmployee.blood_group || '-'}</span>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Gender:</span>
                      <span className="ml-1 capitalize">{quickViewEmployee.gender}</span>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Status:</span>
                      <span className="ml-1 capitalize">{quickViewEmployee.marital_status}</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Actions */}
              <div className="mt-6 pt-6 border-t space-y-2">
                <Button className="w-full" asChild>
                  <Link href={`/employees/${quickViewEmployee.id}`}>
                    View Full Profile
                    <ChevronRight className="h-4 w-4 ml-2" />
                  </Link>
                </Button>
                <Button variant="outline" className="w-full" asChild>
                  <Link href={`/employees/${quickViewEmployee.id}/edit`}>
                    <Edit className="h-4 w-4 mr-2" />
                    Edit Employee
                  </Link>
                </Button>
              </div>
            </div>
          </div>
        </>
      )}

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-red-600" />
              Delete Employee
            </AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete <strong>{employeeToDelete?.full_name}</strong> ({employeeToDelete?.employee_code})?
              This action cannot be undone. All associated data including payroll history, leave records, and documents will be permanently removed.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={isDeleting}>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDeleteConfirm}
              disabled={isDeleting}
              className="bg-red-600 hover:bg-red-700"
            >
              {isDeleting ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Deleting...
                </>
              ) : (
                <>
                  <Trash2 className="h-4 w-4 mr-2" />
                  Delete Employee
                </>
              )}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
}
