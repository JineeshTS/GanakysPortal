'use client'

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Label } from '@/components/ui/label'
import { Switch } from '@/components/ui/switch'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import { Textarea } from '@/components/ui/textarea'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import {
  GitBranch,
  Plus,
  Search,
  MoreHorizontal,
  Edit,
  Copy,
  Trash2,
  ArrowRight,
  ArrowDownRight,
  Users,
  Clock,
  AlertTriangle,
  CheckCircle,
  Settings,
} from 'lucide-react'
import { format } from 'date-fns'

type WorkflowType = 'sequential' | 'parallel' | 'hybrid' | 'conditional'

interface WorkflowLevel {
  id: string
  levelOrder: number
  levelName: string
  approverType: string
  approverName?: string
  isParallel: boolean
  slaHours: number
}

interface WorkflowTemplate {
  id: string
  name: string
  code: string
  description: string
  workflowType: WorkflowType
  transactionType: string
  isActive: boolean
  levels: WorkflowLevel[]
  escalationHours: number
  maxEscalations: number
  createdAt: Date
  updatedAt: Date
}

// Mock workflow templates
const mockWorkflows: WorkflowTemplate[] = [
  {
    id: '1',
    name: 'Purchase Order Approval',
    code: 'WF-PO-001',
    description: 'Standard approval workflow for purchase orders with multi-level approval based on amount',
    workflowType: 'sequential',
    transactionType: 'purchase_order',
    isActive: true,
    levels: [
      { id: '1-1', levelOrder: 1, levelName: 'Department Head', approverType: 'role', approverName: 'Department Head', isParallel: false, slaHours: 24 },
      { id: '1-2', levelOrder: 2, levelName: 'Finance Manager', approverType: 'role', approverName: 'Finance Manager', isParallel: false, slaHours: 24 },
      { id: '1-3', levelOrder: 3, levelName: 'CFO', approverType: 'position', approverName: 'CFO', isParallel: false, slaHours: 48 },
    ],
    escalationHours: 24,
    maxEscalations: 3,
    createdAt: new Date('2025-06-15'),
    updatedAt: new Date('2026-01-10'),
  },
  {
    id: '2',
    name: 'Expense Claim Approval',
    code: 'WF-EXP-001',
    description: 'Fast track approval for expense claims under budget',
    workflowType: 'sequential',
    transactionType: 'expense_claim',
    isActive: true,
    levels: [
      { id: '2-1', levelOrder: 1, levelName: 'Reporting Manager', approverType: 'reporting_manager', approverName: 'Reporting Manager', isParallel: false, slaHours: 24 },
      { id: '2-2', levelOrder: 2, levelName: 'Finance', approverType: 'role', approverName: 'Finance Team', isParallel: false, slaHours: 24 },
    ],
    escalationHours: 24,
    maxEscalations: 2,
    createdAt: new Date('2025-06-20'),
    updatedAt: new Date('2025-12-15'),
  },
  {
    id: '3',
    name: 'Capital Expenditure Approval',
    code: 'WF-CAPEX-001',
    description: 'Multi-level approval for capital expenditures with parallel finance and legal review',
    workflowType: 'hybrid',
    transactionType: 'capital_expenditure',
    isActive: true,
    levels: [
      { id: '3-1', levelOrder: 1, levelName: 'Project Manager', approverType: 'role', approverName: 'Project Manager', isParallel: false, slaHours: 24 },
      { id: '3-2', levelOrder: 2, levelName: 'Finance Review', approverType: 'role', approverName: 'Finance Manager', isParallel: true, slaHours: 48 },
      { id: '3-3', levelOrder: 2, levelName: 'Legal Review', approverType: 'role', approverName: 'Legal Head', isParallel: true, slaHours: 48 },
      { id: '3-4', levelOrder: 3, levelName: 'CFO', approverType: 'position', approverName: 'CFO', isParallel: false, slaHours: 48 },
      { id: '3-5', levelOrder: 4, levelName: 'CEO', approverType: 'position', approverName: 'CEO', isParallel: false, slaHours: 72 },
    ],
    escalationHours: 48,
    maxEscalations: 3,
    createdAt: new Date('2025-07-01'),
    updatedAt: new Date('2026-01-05'),
  },
  {
    id: '4',
    name: 'Travel Request Approval',
    code: 'WF-TRV-001',
    description: 'Simple single-level approval for travel requests',
    workflowType: 'sequential',
    transactionType: 'travel_request',
    isActive: true,
    levels: [
      { id: '4-1', levelOrder: 1, levelName: 'Reporting Manager', approverType: 'reporting_manager', approverName: 'Reporting Manager', isParallel: false, slaHours: 24 },
    ],
    escalationHours: 24,
    maxEscalations: 1,
    createdAt: new Date('2025-08-10'),
    updatedAt: new Date('2025-11-20'),
  },
  {
    id: '5',
    name: 'Vendor Payment Approval',
    code: 'WF-VND-001',
    description: 'Approval workflow for vendor payments with procurement and finance review',
    workflowType: 'sequential',
    transactionType: 'vendor_payment',
    isActive: false,
    levels: [
      { id: '5-1', levelOrder: 1, levelName: 'Procurement', approverType: 'role', approverName: 'Procurement Manager', isParallel: false, slaHours: 24 },
      { id: '5-2', levelOrder: 2, levelName: 'Finance', approverType: 'role', approverName: 'Finance Manager', isParallel: false, slaHours: 24 },
    ],
    escalationHours: 24,
    maxEscalations: 2,
    createdAt: new Date('2025-09-01'),
    updatedAt: new Date('2025-12-01'),
  },
]

const workflowTypeConfig = {
  sequential: { label: 'Sequential', icon: ArrowRight, color: 'bg-blue-100 text-blue-700' },
  parallel: { label: 'Parallel', icon: Users, color: 'bg-purple-100 text-purple-700' },
  hybrid: { label: 'Hybrid', icon: GitBranch, color: 'bg-green-100 text-green-700' },
  conditional: { label: 'Conditional', icon: ArrowDownRight, color: 'bg-orange-100 text-orange-700' },
}

const transactionTypes = [
  { value: 'purchase_order', label: 'Purchase Order' },
  { value: 'expense_claim', label: 'Expense Claim' },
  { value: 'capital_expenditure', label: 'Capital Expenditure' },
  { value: 'vendor_payment', label: 'Vendor Payment' },
  { value: 'travel_request', label: 'Travel Request' },
  { value: 'leave_request', label: 'Leave Request' },
  { value: 'recruitment', label: 'Recruitment' },
]

export default function WorkflowsPage() {
  const [workflows, setWorkflows] = useState(mockWorkflows)
  const [searchQuery, setSearchQuery] = useState('')
  const [filterType, setFilterType] = useState<string>('all')
  const [createDialogOpen, setCreateDialogOpen] = useState(false)
  const [selectedWorkflow, setSelectedWorkflow] = useState<WorkflowTemplate | null>(null)

  const filteredWorkflows = workflows.filter(wf => {
    const matchesSearch = wf.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      wf.code.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesType = filterType === 'all' || wf.transactionType === filterType
    return matchesSearch && matchesType
  })

  const handleToggleActive = (id: string) => {
    setWorkflows(workflows.map(wf =>
      wf.id === id ? { ...wf, isActive: !wf.isActive } : wf
    ))
  }

  const handleDelete = (id: string) => {
    setWorkflows(workflows.filter(wf => wf.id !== id))
  }

  const activeCount = workflows.filter(wf => wf.isActive).length

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Approval Workflows</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Configure and manage approval workflow templates
          </p>
        </div>
        <Dialog open={createDialogOpen} onOpenChange={setCreateDialogOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              Create Workflow
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>Create Workflow Template</DialogTitle>
              <DialogDescription>
                Define a new approval workflow for transactions
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Workflow Name</Label>
                  <Input placeholder="e.g., Purchase Order Approval" />
                </div>
                <div className="space-y-2">
                  <Label>Code</Label>
                  <Input placeholder="e.g., WF-PO-001" />
                </div>
              </div>
              <div className="space-y-2">
                <Label>Description</Label>
                <Textarea placeholder="Describe the workflow purpose and triggers..." />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Transaction Type</Label>
                  <Select>
                    <SelectTrigger>
                      <SelectValue placeholder="Select type" />
                    </SelectTrigger>
                    <SelectContent>
                      {transactionTypes.map(type => (
                        <SelectItem key={type.value} value={type.value}>
                          {type.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label>Workflow Type</Label>
                  <Select>
                    <SelectTrigger>
                      <SelectValue placeholder="Select type" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="sequential">Sequential</SelectItem>
                      <SelectItem value="parallel">Parallel</SelectItem>
                      <SelectItem value="hybrid">Hybrid</SelectItem>
                      <SelectItem value="conditional">Conditional</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Escalation Hours</Label>
                  <Input type="number" defaultValue={24} />
                </div>
                <div className="space-y-2">
                  <Label>Max Escalations</Label>
                  <Input type="number" defaultValue={3} />
                </div>
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setCreateDialogOpen(false)}>
                Cancel
              </Button>
              <Button onClick={() => setCreateDialogOpen(false)}>
                Continue to Add Levels
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Total Workflows</p>
                <p className="text-2xl font-bold">{workflows.length}</p>
              </div>
              <GitBranch className="h-8 w-8 text-gray-400" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Active</p>
                <p className="text-2xl font-bold text-green-600">{activeCount}</p>
              </div>
              <CheckCircle className="h-8 w-8 text-green-400" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Transaction Types</p>
                <p className="text-2xl font-bold">{new Set(workflows.map(w => w.transactionType)).size}</p>
              </div>
              <Settings className="h-8 w-8 text-blue-400" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Avg. Levels</p>
                <p className="text-2xl font-bold">
                  {(workflows.reduce((sum, w) => sum + w.levels.length, 0) / workflows.length).toFixed(1)}
                </p>
              </div>
              <Users className="h-8 w-8 text-purple-400" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-4">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
          <Input
            placeholder="Search workflows..."
            className="pl-10"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
        <Select value={filterType} onValueChange={setFilterType}>
          <SelectTrigger className="w-48">
            <SelectValue placeholder="Transaction Type" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Types</SelectItem>
            {transactionTypes.map(type => (
              <SelectItem key={type.value} value={type.value}>
                {type.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Workflows List */}
      <div className="grid gap-4">
        {filteredWorkflows.map((workflow) => {
          const TypeIcon = workflowTypeConfig[workflow.workflowType].icon
          return (
            <Card key={workflow.id} className={!workflow.isActive ? 'opacity-60' : ''}>
              <CardContent className="p-6">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-lg font-semibold">{workflow.name}</h3>
                      <Badge variant="outline">{workflow.code}</Badge>
                      <Badge className={workflowTypeConfig[workflow.workflowType].color}>
                        <TypeIcon className="h-3 w-3 mr-1" />
                        {workflowTypeConfig[workflow.workflowType].label}
                      </Badge>
                      {!workflow.isActive && (
                        <Badge variant="secondary">Inactive</Badge>
                      )}
                    </div>
                    <p className="text-gray-500 text-sm mb-4">{workflow.description}</p>

                    {/* Workflow Levels Visualization */}
                    <div className="flex items-center gap-2 flex-wrap">
                      {workflow.levels.map((level, index) => {
                        const isParallelGroup = level.isParallel &&
                          workflow.levels.some(l => l.id !== level.id && l.levelOrder === level.levelOrder && l.isParallel)

                        return (
                          <div key={level.id} className="flex items-center gap-2">
                            {index > 0 && workflow.levels[index - 1].levelOrder !== level.levelOrder && (
                              <ArrowRight className="h-4 w-4 text-gray-400" />
                            )}
                            {index > 0 && workflow.levels[index - 1].levelOrder === level.levelOrder && level.isParallel && (
                              <span className="text-gray-400 text-sm">+</span>
                            )}
                            <div className={`px-3 py-1.5 rounded-lg border ${level.isParallel ? 'bg-purple-50 border-purple-200' : 'bg-gray-50 border-gray-200'}`}>
                              <p className="text-sm font-medium">{level.levelName}</p>
                              <p className="text-xs text-gray-500 flex items-center gap-1">
                                <Clock className="h-3 w-3" />
                                {level.slaHours}h SLA
                              </p>
                            </div>
                          </div>
                        )
                      })}
                    </div>
                  </div>

                  <div className="flex items-center gap-4 ml-4">
                    <div className="text-right text-sm">
                      <p className="text-gray-500">Updated</p>
                      <p className="font-medium">{format(workflow.updatedAt, 'MMM d, yyyy')}</p>
                    </div>
                    <Switch
                      checked={workflow.isActive}
                      onCheckedChange={() => handleToggleActive(workflow.id)}
                    />
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button variant="ghost" size="icon">
                          <MoreHorizontal className="h-4 w-4" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuItem onClick={() => setSelectedWorkflow(workflow)}>
                          <Edit className="h-4 w-4 mr-2" />
                          Edit
                        </DropdownMenuItem>
                        <DropdownMenuItem>
                          <Copy className="h-4 w-4 mr-2" />
                          Clone
                        </DropdownMenuItem>
                        <DropdownMenuItem
                          className="text-red-600"
                          onClick={() => handleDelete(workflow.id)}
                        >
                          <Trash2 className="h-4 w-4 mr-2" />
                          Delete
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </div>
                </div>
              </CardContent>
            </Card>
          )
        })}
      </div>

      {filteredWorkflows.length === 0 && (
        <Card>
          <CardContent className="py-12">
            <div className="text-center">
              <GitBranch className="h-12 w-12 text-gray-300 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900">No workflows found</h3>
              <p className="text-gray-500">Try adjusting your search or create a new workflow.</p>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
