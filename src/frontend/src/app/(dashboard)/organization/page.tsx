'use client'

import { useState, useEffect, useCallback } from 'react'
import { PageHeader } from '@/components/layout/page-header'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Skeleton } from '@/components/ui/skeleton'
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
  Network,
  Building2,
  Users,
  Plus,
  Search,
  ChevronDown,
  ChevronRight,
  Edit,
  Trash2,
  Briefcase,
  RefreshCw,
  Loader2,
  User
} from 'lucide-react'

// Types
interface Department {
  id: string
  name: string
  code?: string
  parent_id?: string
  parent_name?: string
  head_employee_id?: string
  head_employee_name?: string
  is_active: boolean
  employee_count: number
}

interface Designation {
  id: string
  name: string
  code?: string
  level?: number
  is_active: boolean
  employee_count: number
}

interface Employee {
  id: string
  employee_code: string
  first_name: string
  last_name: string
  full_name: string
  department_id?: string
  department_name?: string
  designation_id?: string
  designation_name?: string
  reporting_to?: string
  reporting_to_name?: string
  employment_status: string
}

interface DepartmentListResponse {
  success: boolean
  data: Department[]
  meta: { page: number; limit: number; total: number }
}

interface DesignationListResponse {
  success: boolean
  data: Designation[]
  meta: { page: number; limit: number; total: number }
}

interface EmployeeListResponse {
  success: boolean
  data: Employee[]
  meta: { page: number; limit: number; total: number }
}

interface OrgNode {
  id: string
  name: string
  title: string
  employee: string
  children: OrgNode[]
}

function buildOrgTree(employees: Employee[]): OrgNode | null {
  if (employees.length === 0) return null

  // Find employees without a manager (top of hierarchy)
  const topEmployees = employees.filter(emp => !emp.reporting_to)

  // If no clear top, use the first active employee
  if (topEmployees.length === 0 && employees.length > 0) {
    const root = employees[0]
    return {
      id: root.id,
      name: root.designation_name || 'Employee',
      title: root.designation_name || 'Employee',
      employee: root.full_name,
      children: buildChildNodes(root.id, employees)
    }
  }

  // Build tree from top employees
  if (topEmployees.length === 1) {
    const root = topEmployees[0]
    return {
      id: root.id,
      name: root.designation_name || 'CEO',
      title: root.designation_name || 'CEO',
      employee: root.full_name,
      children: buildChildNodes(root.id, employees)
    }
  }

  // Multiple top-level employees, create a virtual root
  return {
    id: 'root',
    name: 'Organization',
    title: 'Organization',
    employee: 'Company',
    children: topEmployees.map(emp => ({
      id: emp.id,
      name: emp.designation_name || 'Manager',
      title: emp.designation_name || 'Manager',
      employee: emp.full_name,
      children: buildChildNodes(emp.id, employees)
    }))
  }
}

function buildChildNodes(parentId: string, employees: Employee[]): OrgNode[] {
  const children = employees.filter(emp => emp.reporting_to === parentId)
  return children.map(child => ({
    id: child.id,
    name: child.designation_name || 'Employee',
    title: child.designation_name || 'Employee',
    employee: child.full_name,
    children: buildChildNodes(child.id, employees)
  }))
}

interface OrgNodeProps {
  node: OrgNode
  level?: number
}

function OrgNodeComponent({ node, level = 0 }: OrgNodeProps) {
  const [expanded, setExpanded] = useState(level < 2)
  const hasChildren = node.children && node.children.length > 0

  return (
    <div className={level > 0 ? 'ml-8 mt-2' : ''}>
      <div className="flex items-start gap-2">
        {hasChildren && (
          <button onClick={() => setExpanded(!expanded)} className="mt-3">
            {expanded ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
          </button>
        )}
        {!hasChildren && <div className="w-4" />}
        <Card className="flex-1 max-w-xs">
          <CardContent className="p-3">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-primary/10 rounded-full flex items-center justify-center">
                <span className="text-sm font-medium text-primary">
                  {node.employee?.split(' ').map(n => n[0]).join('').slice(0, 2)}
                </span>
              </div>
              <div>
                <p className="font-medium text-sm">{node.employee}</p>
                <p className="text-xs text-muted-foreground">{node.title || node.name}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
      {expanded && hasChildren && (
        <div className="border-l-2 border-muted ml-2">
          {node.children?.map((child, index) => (
            <OrgNodeComponent key={child.id || index} node={child} level={level + 1} />
          ))}
        </div>
      )}
    </div>
  )
}

export default function OrganizationPage() {
  const [searchQuery, setSearchQuery] = useState('')
  const [activeTab, setActiveTab] = useState('orgchart')
  const [isNewDeptOpen, setIsNewDeptOpen] = useState(false)
  const [isNewDesigOpen, setIsNewDesigOpen] = useState(false)
  const [isEditDeptOpen, setIsEditDeptOpen] = useState(false)
  const [isEditDesigOpen, setIsEditDesigOpen] = useState(false)
  const [selectedDept, setSelectedDept] = useState<Department | null>(null)
  const [selectedDesig, setSelectedDesig] = useState<Designation | null>(null)
  const { showToast } = useToast()

  // Form states
  const [deptForm, setDeptForm] = useState({
    name: '',
    code: '',
    parent_id: '',
    head_employee_id: '',
  })

  const [desigForm, setDesigForm] = useState({
    name: '',
    code: '',
    level: 1,
  })

  // API hooks
  const { data: deptData, isLoading: isLoadingDepts, get: getDepts } = useApi<DepartmentListResponse>()
  const { data: desigData, isLoading: isLoadingDesigs, get: getDesigs } = useApi<DesignationListResponse>()
  const { data: empData, isLoading: isLoadingEmps, get: getEmps } = useApi<EmployeeListResponse>()
  const { isLoading: isCreatingDept, post: createDept } = useApi<Department>()
  const { isLoading: isCreatingDesig, post: createDesig } = useApi<Designation>()
  const { isLoading: isUpdatingDept, put: updateDept } = useApi<Department>()
  const { isLoading: isUpdatingDesig, put: updateDesig } = useApi<Designation>()
  const { del: deleteDept } = useApi()
  const { del: deleteDesig } = useApi()

  // Fetch data
  const fetchData = useCallback(() => {
    getDepts('/departments?page=1&limit=100')
    getDesigs('/departments/designations/?page=1&limit=100')
    getEmps('/employees?page=1&limit=200&status=active')
  }, [getDepts, getDesigs, getEmps])

  useEffect(() => {
    fetchData()
  }, [fetchData])

  const departments = deptData?.data || []
  const designations = desigData?.data || []
  const employees = empData?.data || []

  // Build org tree from employee reporting relationships
  const orgTree = buildOrgTree(employees)

  // Filter departments by search
  const filteredDepartments = departments.filter(dept =>
    dept.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    (dept.head_employee_name || '').toLowerCase().includes(searchQuery.toLowerCase())
  )

  // Filter designations by search
  const filteredDesignations = designations.filter(des =>
    des.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    (des.code || '').toLowerCase().includes(searchQuery.toLowerCase())
  )

  // Calculate stats
  const totalEmployees = employees.length
  const hierarchyLevels = designations.reduce((max, d) => Math.max(max, d.level || 0), 0) || 4

  // Handlers
  const handleCreateDept = async () => {
    if (!deptForm.name) {
      showToast('error', 'Please enter department name')
      return
    }

    const result = await createDept('/departments', {
      name: deptForm.name,
      code: deptForm.code || undefined,
      parent_id: deptForm.parent_id || undefined,
      head_employee_id: deptForm.head_employee_id || undefined,
    })

    if (result) {
      showToast('success', 'Department created successfully')
      setIsNewDeptOpen(false)
      setDeptForm({ name: '', code: '', parent_id: '', head_employee_id: '' })
      fetchData()
    }
  }

  const handleUpdateDept = async () => {
    if (!selectedDept || !deptForm.name) return

    const result = await updateDept(`/departments/${selectedDept.id}`, {
      name: deptForm.name,
      code: deptForm.code || undefined,
      parent_id: deptForm.parent_id || undefined,
      head_employee_id: deptForm.head_employee_id || undefined,
    })

    if (result) {
      showToast('success', 'Department updated successfully')
      setIsEditDeptOpen(false)
      setSelectedDept(null)
      setDeptForm({ name: '', code: '', parent_id: '', head_employee_id: '' })
      fetchData()
    }
  }

  const handleDeleteDept = async (deptId: string) => {
    if (!confirm('Are you sure you want to delete this department?')) return

    try {
      await deleteDept(`/departments/${deptId}`)
      showToast('success', 'Department deleted')
      fetchData()
    } catch {
      showToast('error', 'Cannot delete department with employees')
    }
  }

  const handleCreateDesig = async () => {
    if (!desigForm.name) {
      showToast('error', 'Please enter designation name')
      return
    }

    const result = await createDesig('/departments/designations/', {
      name: desigForm.name,
      code: desigForm.code || undefined,
      level: desigForm.level || undefined,
    })

    if (result) {
      showToast('success', 'Designation created successfully')
      setIsNewDesigOpen(false)
      setDesigForm({ name: '', code: '', level: 1 })
      fetchData()
    }
  }

  const handleUpdateDesig = async () => {
    if (!selectedDesig || !desigForm.name) return

    const result = await updateDesig(`/departments/designations/${selectedDesig.id}`, {
      name: desigForm.name,
      code: desigForm.code || undefined,
      level: desigForm.level || undefined,
    })

    if (result) {
      showToast('success', 'Designation updated successfully')
      setIsEditDesigOpen(false)
      setSelectedDesig(null)
      setDesigForm({ name: '', code: '', level: 1 })
      fetchData()
    }
  }

  const handleDeleteDesig = async (desigId: string) => {
    if (!confirm('Are you sure you want to delete this designation?')) return

    try {
      await deleteDesig(`/departments/designations/${desigId}`)
      showToast('success', 'Designation deleted')
      fetchData()
    } catch {
      showToast('error', 'Cannot delete designation with employees')
    }
  }

  const openEditDept = (dept: Department) => {
    setSelectedDept(dept)
    setDeptForm({
      name: dept.name,
      code: dept.code || '',
      parent_id: dept.parent_id || '',
      head_employee_id: dept.head_employee_id || '',
    })
    setIsEditDeptOpen(true)
  }

  const openEditDesig = (desig: Designation) => {
    setSelectedDesig(desig)
    setDesigForm({
      name: desig.name,
      code: desig.code || '',
      level: desig.level || 1,
    })
    setIsEditDesigOpen(true)
  }

  // Loading state
  if (isLoadingDepts || isLoadingDesigs || isLoadingEmps) {
    return (
      <div className="space-y-6">
        <PageHeader
          title="Organization"
          description="Manage organization structure, departments, and designations"
          icon={<Network className="h-6 w-6" />}
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

  return (
    <div className="space-y-6">
      <PageHeader
        title="Organization"
        description="Manage organization structure, departments, and designations"
        icon={<Network className="h-6 w-6" />}
        actions={
          <div className="flex gap-2">
            <Button variant="outline" onClick={fetchData}>
              <RefreshCw className="h-4 w-4 mr-2" />
              Refresh
            </Button>
            <Dialog open={isNewDeptOpen} onOpenChange={setIsNewDeptOpen}>
              <DialogTrigger asChild>
                <Button variant="outline">
                  <Building2 className="h-4 w-4 mr-2" />
                  Add Department
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Create Department</DialogTitle>
                  <DialogDescription>Add a new department to your organization</DialogDescription>
                </DialogHeader>
                <div className="grid gap-4 py-4">
                  <div className="grid gap-2">
                    <Label>Department Name *</Label>
                    <Input
                      value={deptForm.name}
                      onChange={(e) => setDeptForm({ ...deptForm, name: e.target.value })}
                      placeholder="e.g., Engineering"
                    />
                  </div>
                  <div className="grid gap-2">
                    <Label>Code</Label>
                    <Input
                      value={deptForm.code}
                      onChange={(e) => setDeptForm({ ...deptForm, code: e.target.value })}
                      placeholder="e.g., ENG"
                    />
                  </div>
                  <div className="grid gap-2">
                    <Label>Parent Department</Label>
                    <Select
                      value={deptForm.parent_id}
                      onValueChange={(v) => setDeptForm({ ...deptForm, parent_id: v })}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select parent (optional)" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="">None</SelectItem>
                        {departments.map((d) => (
                          <SelectItem key={d.id} value={d.id}>{d.name}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="grid gap-2">
                    <Label>Department Head</Label>
                    <Select
                      value={deptForm.head_employee_id}
                      onValueChange={(v) => setDeptForm({ ...deptForm, head_employee_id: v })}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select head (optional)" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="">None</SelectItem>
                        {employees.map((e) => (
                          <SelectItem key={e.id} value={e.id}>{e.full_name}</SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <DialogFooter>
                  <Button variant="outline" onClick={() => setIsNewDeptOpen(false)}>Cancel</Button>
                  <Button onClick={handleCreateDept} disabled={isCreatingDept}>
                    {isCreatingDept ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
                    Create
                  </Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
            <Dialog open={isNewDesigOpen} onOpenChange={setIsNewDesigOpen}>
              <DialogTrigger asChild>
                <Button>
                  <Briefcase className="h-4 w-4 mr-2" />
                  Add Designation
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Create Designation</DialogTitle>
                  <DialogDescription>Add a new job title/designation</DialogDescription>
                </DialogHeader>
                <div className="grid gap-4 py-4">
                  <div className="grid gap-2">
                    <Label>Designation Name *</Label>
                    <Input
                      value={desigForm.name}
                      onChange={(e) => setDesigForm({ ...desigForm, name: e.target.value })}
                      placeholder="e.g., Software Engineer"
                    />
                  </div>
                  <div className="grid gap-2">
                    <Label>Code</Label>
                    <Input
                      value={desigForm.code}
                      onChange={(e) => setDesigForm({ ...desigForm, code: e.target.value })}
                      placeholder="e.g., SWE"
                    />
                  </div>
                  <div className="grid gap-2">
                    <Label>Level</Label>
                    <Input
                      type="number"
                      value={desigForm.level}
                      onChange={(e) => setDesigForm({ ...desigForm, level: parseInt(e.target.value) || 1 })}
                      min={1}
                      max={10}
                    />
                    <p className="text-xs text-muted-foreground">1 = Entry level, higher = senior</p>
                  </div>
                </div>
                <DialogFooter>
                  <Button variant="outline" onClick={() => setIsNewDesigOpen(false)}>Cancel</Button>
                  <Button onClick={handleCreateDesig} disabled={isCreatingDesig}>
                    {isCreatingDesig ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
                    Create
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
                <Building2 className="h-5 w-5 text-blue-600" />
              </div>
              <div>
                <p className="text-2xl font-bold">{departments.length}</p>
                <p className="text-sm text-muted-foreground">Departments</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-green-100 rounded-lg">
                <Briefcase className="h-5 w-5 text-green-600" />
              </div>
              <div>
                <p className="text-2xl font-bold">{designations.length}</p>
                <p className="text-sm text-muted-foreground">Designations</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-purple-100 rounded-lg">
                <Users className="h-5 w-5 text-purple-600" />
              </div>
              <div>
                <p className="text-2xl font-bold">{totalEmployees}</p>
                <p className="text-sm text-muted-foreground">Total Employees</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-orange-100 rounded-lg">
                <Network className="h-5 w-5 text-orange-600" />
              </div>
              <div>
                <p className="text-2xl font-bold">{hierarchyLevels}</p>
                <p className="text-sm text-muted-foreground">Hierarchy Levels</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="orgchart">Org Chart</TabsTrigger>
          <TabsTrigger value="departments">Departments ({departments.length})</TabsTrigger>
          <TabsTrigger value="designations">Designations ({designations.length})</TabsTrigger>
        </TabsList>

        <TabsContent value="orgchart" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle>Organization Chart</CardTitle>
              <CardDescription>Visual representation of company hierarchy based on reporting relationships</CardDescription>
            </CardHeader>
            <CardContent className="overflow-x-auto">
              {orgTree ? (
                <OrgNodeComponent node={orgTree} />
              ) : (
                <div className="text-center py-12 text-muted-foreground">
                  <Network className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>No employees found to build org chart</p>
                  <p className="text-sm mt-2">Add employees with reporting relationships to see the hierarchy</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="departments" className="mt-4">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Departments</CardTitle>
                  <CardDescription>Manage company departments</CardDescription>
                </div>
                <div className="relative w-64">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <Input
                    placeholder="Search departments..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-9"
                  />
                </div>
              </div>
            </CardHeader>
            <CardContent>
              {filteredDepartments.length === 0 ? (
                <div className="text-center py-12 text-muted-foreground">
                  <Building2 className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>No departments found</p>
                  <Button className="mt-4" onClick={() => setIsNewDeptOpen(true)}>
                    <Plus className="h-4 w-4 mr-2" />
                    Create First Department
                  </Button>
                </div>
              ) : (
                <div className="border rounded-lg overflow-hidden">
                  <table className="w-full">
                    <thead className="bg-muted/50">
                      <tr>
                        <th className="text-left p-4 font-medium">Department</th>
                        <th className="text-left p-4 font-medium">Code</th>
                        <th className="text-left p-4 font-medium">Head</th>
                        <th className="text-center p-4 font-medium">Employees</th>
                        <th className="text-center p-4 font-medium">Status</th>
                        <th className="text-right p-4 font-medium">Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {filteredDepartments.map((dept) => (
                        <tr key={dept.id} className="border-t hover:bg-muted/30">
                          <td className="p-4">
                            <div className="flex items-center gap-2">
                              <Building2 className="h-4 w-4 text-muted-foreground" />
                              <div>
                                <span className="font-medium">{dept.name}</span>
                                {dept.parent_name && (
                                  <p className="text-xs text-muted-foreground">Under {dept.parent_name}</p>
                                )}
                              </div>
                            </div>
                          </td>
                          <td className="p-4">
                            <Badge variant="outline">{dept.code || '-'}</Badge>
                          </td>
                          <td className="p-4">{dept.head_employee_name || '-'}</td>
                          <td className="p-4 text-center">
                            <Badge variant="secondary">{dept.employee_count}</Badge>
                          </td>
                          <td className="p-4 text-center">
                            <Badge className={dept.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}>
                              {dept.is_active ? 'Active' : 'Inactive'}
                            </Badge>
                          </td>
                          <td className="p-4 text-right">
                            <div className="flex items-center justify-end gap-1">
                              <Button variant="ghost" size="icon" onClick={() => openEditDept(dept)}>
                                <Edit className="h-4 w-4" />
                              </Button>
                              <Button
                                variant="ghost"
                                size="icon"
                                onClick={() => handleDeleteDept(dept.id)}
                                disabled={dept.employee_count > 0}
                              >
                                <Trash2 className="h-4 w-4" />
                              </Button>
                            </div>
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

        <TabsContent value="designations" className="mt-4">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Designations</CardTitle>
                  <CardDescription>Manage job titles and levels</CardDescription>
                </div>
                <div className="relative w-64">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <Input
                    placeholder="Search designations..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-9"
                  />
                </div>
              </div>
            </CardHeader>
            <CardContent>
              {filteredDesignations.length === 0 ? (
                <div className="text-center py-12 text-muted-foreground">
                  <Briefcase className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>No designations found</p>
                  <Button className="mt-4" onClick={() => setIsNewDesigOpen(true)}>
                    <Plus className="h-4 w-4 mr-2" />
                    Create First Designation
                  </Button>
                </div>
              ) : (
                <div className="border rounded-lg overflow-hidden">
                  <table className="w-full">
                    <thead className="bg-muted/50">
                      <tr>
                        <th className="text-left p-4 font-medium">Title</th>
                        <th className="text-left p-4 font-medium">Code</th>
                        <th className="text-center p-4 font-medium">Level</th>
                        <th className="text-center p-4 font-medium">Employees</th>
                        <th className="text-center p-4 font-medium">Status</th>
                        <th className="text-right p-4 font-medium">Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {filteredDesignations.map((des) => (
                        <tr key={des.id} className="border-t hover:bg-muted/30">
                          <td className="p-4">
                            <span className="font-medium">{des.name}</span>
                          </td>
                          <td className="p-4">
                            <Badge variant="outline">{des.code || '-'}</Badge>
                          </td>
                          <td className="p-4 text-center">
                            <Badge variant="outline">L{des.level || 1}</Badge>
                          </td>
                          <td className="p-4 text-center">
                            <Badge variant="secondary">{des.employee_count}</Badge>
                          </td>
                          <td className="p-4 text-center">
                            <Badge className={des.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}>
                              {des.is_active ? 'Active' : 'Inactive'}
                            </Badge>
                          </td>
                          <td className="p-4 text-right">
                            <div className="flex items-center justify-end gap-1">
                              <Button variant="ghost" size="icon" onClick={() => openEditDesig(des)}>
                                <Edit className="h-4 w-4" />
                              </Button>
                              <Button
                                variant="ghost"
                                size="icon"
                                onClick={() => handleDeleteDesig(des.id)}
                                disabled={des.employee_count > 0}
                              >
                                <Trash2 className="h-4 w-4" />
                              </Button>
                            </div>
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

      {/* Edit Department Dialog */}
      <Dialog open={isEditDeptOpen} onOpenChange={setIsEditDeptOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Edit Department</DialogTitle>
            <DialogDescription>Update department information</DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div className="grid gap-2">
              <Label>Department Name *</Label>
              <Input
                value={deptForm.name}
                onChange={(e) => setDeptForm({ ...deptForm, name: e.target.value })}
              />
            </div>
            <div className="grid gap-2">
              <Label>Code</Label>
              <Input
                value={deptForm.code}
                onChange={(e) => setDeptForm({ ...deptForm, code: e.target.value })}
              />
            </div>
            <div className="grid gap-2">
              <Label>Parent Department</Label>
              <Select
                value={deptForm.parent_id}
                onValueChange={(v) => setDeptForm({ ...deptForm, parent_id: v })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select parent (optional)" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">None</SelectItem>
                  {departments
                    .filter(d => d.id !== selectedDept?.id)
                    .map((d) => (
                      <SelectItem key={d.id} value={d.id}>{d.name}</SelectItem>
                    ))}
                </SelectContent>
              </Select>
            </div>
            <div className="grid gap-2">
              <Label>Department Head</Label>
              <Select
                value={deptForm.head_employee_id}
                onValueChange={(v) => setDeptForm({ ...deptForm, head_employee_id: v })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select head (optional)" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">None</SelectItem>
                  {employees.map((e) => (
                    <SelectItem key={e.id} value={e.id}>{e.full_name}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsEditDeptOpen(false)}>Cancel</Button>
            <Button onClick={handleUpdateDept} disabled={isUpdatingDept}>
              {isUpdatingDept ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
              Save Changes
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Edit Designation Dialog */}
      <Dialog open={isEditDesigOpen} onOpenChange={setIsEditDesigOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Edit Designation</DialogTitle>
            <DialogDescription>Update designation information</DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div className="grid gap-2">
              <Label>Designation Name *</Label>
              <Input
                value={desigForm.name}
                onChange={(e) => setDesigForm({ ...desigForm, name: e.target.value })}
              />
            </div>
            <div className="grid gap-2">
              <Label>Code</Label>
              <Input
                value={desigForm.code}
                onChange={(e) => setDesigForm({ ...desigForm, code: e.target.value })}
              />
            </div>
            <div className="grid gap-2">
              <Label>Level</Label>
              <Input
                type="number"
                value={desigForm.level}
                onChange={(e) => setDesigForm({ ...desigForm, level: parseInt(e.target.value) || 1 })}
                min={1}
                max={10}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsEditDesigOpen(false)}>Cancel</Button>
            <Button onClick={handleUpdateDesig} disabled={isUpdatingDesig}>
              {isUpdatingDesig ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
              Save Changes
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
