'use client'

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Checkbox } from '@/components/ui/checkbox'
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
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  Inbox,
  Search,
  Filter,
  CheckCircle,
  XCircle,
  Clock,
  AlertTriangle,
  AlertCircle,
  ChevronRight,
  IndianRupee,
  User,
  Building2,
  FileText,
  MessageSquare,
  Send,
  RotateCcw,
  Users,
} from 'lucide-react'
import { format, formatDistanceToNow } from 'date-fns'

interface ApprovalItem {
  id: string
  requestNumber: string
  subject: string
  description: string
  transactionType: string
  amount: number
  currency: string
  requesterName: string
  requesterDepartment: string
  assignedAt: Date
  dueAt: Date
  slaStatus: 'on_track' | 'at_risk' | 'breached'
  priority: number
  isUrgent: boolean
  riskLevel: 'low' | 'medium' | 'high' | 'critical'
  levelOrder: number
  totalLevels: number
  aiRecommendation?: 'approve' | 'reject' | 'review'
  aiConfidence?: number
  attachments: number
}

// Mock approval inbox data
const mockInboxItems: ApprovalItem[] = [
  {
    id: '1',
    requestNumber: 'APR-2026-000123',
    subject: 'Purchase Order - Office Equipment',
    description: 'Request for approval of office equipment purchase including 10 laptops and accessories',
    transactionType: 'purchase_order',
    amount: 450000,
    currency: 'INR',
    requesterName: 'Priya Sharma',
    requesterDepartment: 'IT Department',
    assignedAt: new Date('2026-01-14T08:00:00'),
    dueAt: new Date('2026-01-15T08:00:00'),
    slaStatus: 'on_track',
    priority: 2,
    isUrgent: false,
    riskLevel: 'medium',
    levelOrder: 2,
    totalLevels: 3,
    aiRecommendation: 'approve',
    aiConfidence: 0.92,
    attachments: 3,
  },
  {
    id: '2',
    requestNumber: 'APR-2026-000124',
    subject: 'Expense Claim - Client Meeting',
    description: 'Expense reimbursement for client meeting at Mumbai including travel and accommodation',
    transactionType: 'expense_claim',
    amount: 28500,
    currency: 'INR',
    requesterName: 'Rahul Kumar',
    requesterDepartment: 'Sales',
    assignedAt: new Date('2026-01-13T14:30:00'),
    dueAt: new Date('2026-01-14T14:30:00'),
    slaStatus: 'at_risk',
    priority: 3,
    isUrgent: false,
    riskLevel: 'low',
    levelOrder: 1,
    totalLevels: 2,
    aiRecommendation: 'approve',
    aiConfidence: 0.98,
    attachments: 5,
  },
  {
    id: '3',
    requestNumber: 'APR-2026-000125',
    subject: 'Capital Expenditure - Server Infrastructure',
    description: 'Request for approval of server infrastructure upgrade for data center',
    transactionType: 'capital_expenditure',
    amount: 2500000,
    currency: 'INR',
    requesterName: 'Amit Patel',
    requesterDepartment: 'IT Infrastructure',
    assignedAt: new Date('2026-01-12T10:00:00'),
    dueAt: new Date('2026-01-13T10:00:00'),
    slaStatus: 'breached',
    priority: 1,
    isUrgent: true,
    riskLevel: 'high',
    levelOrder: 3,
    totalLevels: 4,
    aiRecommendation: 'review',
    aiConfidence: 0.75,
    attachments: 8,
  },
  {
    id: '4',
    requestNumber: 'APR-2026-000126',
    subject: 'Vendor Payment - Software License',
    description: 'Annual software license renewal for enterprise ERP system',
    transactionType: 'vendor_payment',
    amount: 850000,
    currency: 'INR',
    requesterName: 'Neha Singh',
    requesterDepartment: 'Procurement',
    assignedAt: new Date('2026-01-14T09:15:00'),
    dueAt: new Date('2026-01-16T09:15:00'),
    slaStatus: 'on_track',
    priority: 2,
    isUrgent: false,
    riskLevel: 'medium',
    levelOrder: 1,
    totalLevels: 2,
    aiRecommendation: 'approve',
    aiConfidence: 0.95,
    attachments: 2,
  },
  {
    id: '5',
    requestNumber: 'APR-2026-000127',
    subject: 'Travel Request - Conference Attendance',
    description: 'Travel request for attending tech conference in Bangalore',
    transactionType: 'travel_request',
    amount: 45000,
    currency: 'INR',
    requesterName: 'Vikram Reddy',
    requesterDepartment: 'Engineering',
    assignedAt: new Date('2026-01-14T11:00:00'),
    dueAt: new Date('2026-01-15T11:00:00'),
    slaStatus: 'on_track',
    priority: 4,
    isUrgent: false,
    riskLevel: 'low',
    levelOrder: 1,
    totalLevels: 1,
    aiRecommendation: 'approve',
    aiConfidence: 0.99,
    attachments: 1,
  },
]

const slaStatusConfig = {
  on_track: { label: 'On Track', color: 'bg-green-100 text-green-700', icon: CheckCircle },
  at_risk: { label: 'At Risk', color: 'bg-yellow-100 text-yellow-700', icon: AlertTriangle },
  breached: { label: 'Breached', color: 'bg-red-100 text-red-700', icon: AlertCircle },
}

const riskLevelConfig = {
  low: { label: 'Low', color: 'bg-green-100 text-green-700' },
  medium: { label: 'Medium', color: 'bg-yellow-100 text-yellow-700' },
  high: { label: 'High', color: 'bg-orange-100 text-orange-700' },
  critical: { label: 'Critical', color: 'bg-red-100 text-red-700' },
}

const transactionTypeLabels: Record<string, string> = {
  purchase_order: 'Purchase Order',
  expense_claim: 'Expense Claim',
  capital_expenditure: 'Capital Expenditure',
  vendor_payment: 'Vendor Payment',
  travel_request: 'Travel Request',
}

export default function ApprovalInboxPage() {
  const [items, setItems] = useState(mockInboxItems)
  const [selectedItems, setSelectedItems] = useState<string[]>([])
  const [searchQuery, setSearchQuery] = useState('')
  const [filterType, setFilterType] = useState<string>('all')
  const [filterSla, setFilterSla] = useState<string>('all')
  const [actionDialogOpen, setActionDialogOpen] = useState(false)
  const [selectedItem, setSelectedItem] = useState<ApprovalItem | null>(null)
  const [actionType, setActionType] = useState<'approve' | 'reject'>('approve')
  const [comments, setComments] = useState('')

  const filteredItems = items.filter(item => {
    const matchesSearch = item.requestNumber.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.subject.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.requesterName.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesType = filterType === 'all' || item.transactionType === filterType
    const matchesSla = filterSla === 'all' || item.slaStatus === filterSla
    return matchesSearch && matchesType && matchesSla
  })

  const pendingCount = items.length
  const urgentCount = items.filter(i => i.isUrgent).length
  const overdueCount = items.filter(i => i.slaStatus === 'breached').length
  const totalAmount = items.reduce((sum, i) => sum + i.amount, 0)

  const handleSelectAll = (checked: boolean) => {
    if (checked) {
      setSelectedItems(filteredItems.map(i => i.id))
    } else {
      setSelectedItems([])
    }
  }

  const handleSelectItem = (id: string, checked: boolean) => {
    if (checked) {
      setSelectedItems([...selectedItems, id])
    } else {
      setSelectedItems(selectedItems.filter(i => i !== id))
    }
  }

  const handleAction = (item: ApprovalItem, action: 'approve' | 'reject') => {
    setSelectedItem(item)
    setActionType(action)
    setComments('')
    setActionDialogOpen(true)
  }

  const handleSubmitAction = () => {
    // Would call API here
    if (selectedItem) {
      setItems(items.filter(i => i.id !== selectedItem.id))
    }
    setActionDialogOpen(false)
    setSelectedItem(null)
    setComments('')
  }

  const handleBulkAction = (action: 'approve' | 'reject') => {
    setItems(items.filter(i => !selectedItems.includes(i.id)))
    setSelectedItems([])
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Approval Inbox</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Review and process pending approval requests
          </p>
        </div>
        {selectedItems.length > 0 && (
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-500">{selectedItems.length} selected</span>
            <Button
              variant="outline"
              className="text-green-600 border-green-600 hover:bg-green-50"
              onClick={() => handleBulkAction('approve')}
            >
              <CheckCircle className="h-4 w-4 mr-2" />
              Approve All
            </Button>
            <Button
              variant="outline"
              className="text-red-600 border-red-600 hover:bg-red-50"
              onClick={() => handleBulkAction('reject')}
            >
              <XCircle className="h-4 w-4 mr-2" />
              Reject All
            </Button>
          </div>
        )}
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Pending</p>
                <p className="text-2xl font-bold">{pendingCount}</p>
              </div>
              <Inbox className="h-8 w-8 text-blue-400" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Urgent</p>
                <p className="text-2xl font-bold text-orange-600">{urgentCount}</p>
              </div>
              <AlertTriangle className="h-8 w-8 text-orange-400" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Overdue</p>
                <p className="text-2xl font-bold text-red-600">{overdueCount}</p>
              </div>
              <AlertCircle className="h-8 w-8 text-red-400" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Total Amount</p>
                <p className="text-2xl font-bold">
                  <span className="text-lg">INR</span> {(totalAmount / 100000).toFixed(1)}L
                </p>
              </div>
              <IndianRupee className="h-8 w-8 text-green-400" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-4">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
          <Input
            placeholder="Search requests..."
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
            <SelectItem value="purchase_order">Purchase Order</SelectItem>
            <SelectItem value="expense_claim">Expense Claim</SelectItem>
            <SelectItem value="capital_expenditure">Capital Expenditure</SelectItem>
            <SelectItem value="vendor_payment">Vendor Payment</SelectItem>
            <SelectItem value="travel_request">Travel Request</SelectItem>
          </SelectContent>
        </Select>
        <Select value={filterSla} onValueChange={setFilterSla}>
          <SelectTrigger className="w-40">
            <SelectValue placeholder="SLA Status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Status</SelectItem>
            <SelectItem value="on_track">On Track</SelectItem>
            <SelectItem value="at_risk">At Risk</SelectItem>
            <SelectItem value="breached">Breached</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Inbox Table */}
      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="w-12">
                  <Checkbox
                    checked={selectedItems.length === filteredItems.length && filteredItems.length > 0}
                    onCheckedChange={handleSelectAll}
                  />
                </TableHead>
                <TableHead>Request</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Amount</TableHead>
                <TableHead>Requester</TableHead>
                <TableHead>SLA</TableHead>
                <TableHead>Level</TableHead>
                <TableHead>AI</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredItems.map((item) => {
                const SlaIcon = slaStatusConfig[item.slaStatus].icon
                return (
                  <TableRow key={item.id} className={item.isUrgent ? 'bg-orange-50 dark:bg-orange-900/10' : ''}>
                    <TableCell>
                      <Checkbox
                        checked={selectedItems.includes(item.id)}
                        onCheckedChange={(checked) => handleSelectItem(item.id, checked as boolean)}
                      />
                    </TableCell>
                    <TableCell>
                      <div className="max-w-xs">
                        <div className="flex items-center gap-2">
                          <span className="font-medium">{item.requestNumber}</span>
                          {item.isUrgent && (
                            <Badge variant="destructive" className="text-xs">Urgent</Badge>
                          )}
                        </div>
                        <p className="text-sm text-gray-500 truncate">{item.subject}</p>
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline">
                        {transactionTypeLabels[item.transactionType] || item.transactionType}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-1">
                        <IndianRupee className="h-3.5 w-3.5 text-gray-400" />
                        <span className="font-medium">
                          {item.amount >= 100000
                            ? `${(item.amount / 100000).toFixed(1)}L`
                            : item.amount.toLocaleString()}
                        </span>
                      </div>
                      <Badge className={`text-xs ${riskLevelConfig[item.riskLevel].color}`}>
                        {riskLevelConfig[item.riskLevel].label} Risk
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <div className="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center">
                          <User className="h-4 w-4 text-gray-500" />
                        </div>
                        <div>
                          <p className="font-medium text-sm">{item.requesterName}</p>
                          <p className="text-xs text-gray-500">{item.requesterDepartment}</p>
                        </div>
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className={`inline-flex items-center gap-1.5 px-2 py-1 rounded-full ${slaStatusConfig[item.slaStatus].color}`}>
                        <SlaIcon className="h-3.5 w-3.5" />
                        <span className="text-xs font-medium">{slaStatusConfig[item.slaStatus].label}</span>
                      </div>
                      <p className="text-xs text-gray-500 mt-1">
                        Due {formatDistanceToNow(item.dueAt, { addSuffix: true })}
                      </p>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-1">
                        <span className="text-sm font-medium">{item.levelOrder}</span>
                        <span className="text-gray-400">/</span>
                        <span className="text-sm text-gray-500">{item.totalLevels}</span>
                      </div>
                    </TableCell>
                    <TableCell>
                      {item.aiRecommendation && (
                        <div className="text-center">
                          <Badge
                            className={
                              item.aiRecommendation === 'approve'
                                ? 'bg-green-100 text-green-700'
                                : item.aiRecommendation === 'reject'
                                ? 'bg-red-100 text-red-700'
                                : 'bg-yellow-100 text-yellow-700'
                            }
                          >
                            {item.aiRecommendation === 'approve' ? 'Approve' : item.aiRecommendation === 'reject' ? 'Reject' : 'Review'}
                          </Badge>
                          <p className="text-xs text-gray-500 mt-1">{Math.round((item.aiConfidence || 0) * 100)}% conf</p>
                        </div>
                      )}
                    </TableCell>
                    <TableCell className="text-right">
                      <div className="flex items-center justify-end gap-2">
                        <Button
                          size="sm"
                          variant="outline"
                          className="text-green-600 border-green-600 hover:bg-green-50"
                          onClick={() => handleAction(item, 'approve')}
                        >
                          <CheckCircle className="h-4 w-4" />
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          className="text-red-600 border-red-600 hover:bg-red-50"
                          onClick={() => handleAction(item, 'reject')}
                        >
                          <XCircle className="h-4 w-4" />
                        </Button>
                        <Button size="sm" variant="ghost">
                          <ChevronRight className="h-4 w-4" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                )
              })}
            </TableBody>
          </Table>

          {filteredItems.length === 0 && (
            <div className="text-center py-12">
              <Inbox className="h-12 w-12 text-gray-300 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900">No pending approvals</h3>
              <p className="text-gray-500">All caught up! Check back later for new requests.</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Action Dialog */}
      <Dialog open={actionDialogOpen} onOpenChange={setActionDialogOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>
              {actionType === 'approve' ? 'Approve Request' : 'Reject Request'}
            </DialogTitle>
            <DialogDescription>
              {selectedItem?.requestNumber} - {selectedItem?.subject}
            </DialogDescription>
          </DialogHeader>

          {selectedItem && (
            <div className="space-y-4">
              {/* Request Summary */}
              <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4 space-y-3">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-gray-500">Amount</p>
                    <p className="font-medium flex items-center gap-1">
                      <IndianRupee className="h-4 w-4" />
                      {selectedItem.amount.toLocaleString()}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Transaction Type</p>
                    <p className="font-medium">{transactionTypeLabels[selectedItem.transactionType]}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Requester</p>
                    <p className="font-medium">{selectedItem.requesterName}</p>
                    <p className="text-sm text-gray-500">{selectedItem.requesterDepartment}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Risk Level</p>
                    <Badge className={riskLevelConfig[selectedItem.riskLevel].color}>
                      {riskLevelConfig[selectedItem.riskLevel].label}
                    </Badge>
                  </div>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Description</p>
                  <p className="text-sm">{selectedItem.description}</p>
                </div>
              </div>

              {/* AI Recommendation */}
              {selectedItem.aiRecommendation && (
                <div className={`p-4 rounded-lg border-l-4 ${
                  selectedItem.aiRecommendation === 'approve'
                    ? 'bg-green-50 border-green-500'
                    : selectedItem.aiRecommendation === 'reject'
                    ? 'bg-red-50 border-red-500'
                    : 'bg-yellow-50 border-yellow-500'
                }`}>
                  <p className="font-medium">AI Recommendation: {selectedItem.aiRecommendation === 'approve' ? 'Approve' : selectedItem.aiRecommendation === 'reject' ? 'Reject' : 'Review Required'}</p>
                  <p className="text-sm text-gray-600">Confidence: {Math.round((selectedItem.aiConfidence || 0) * 100)}%</p>
                </div>
              )}

              {/* Comments */}
              <div className="space-y-2">
                <label className="text-sm font-medium">Comments {actionType === 'reject' && <span className="text-red-500">*</span>}</label>
                <Textarea
                  placeholder={actionType === 'approve' ? 'Add optional comments...' : 'Please provide reason for rejection...'}
                  value={comments}
                  onChange={(e) => setComments(e.target.value)}
                  rows={3}
                />
              </div>
            </div>
          )}

          <DialogFooter>
            <Button variant="outline" onClick={() => setActionDialogOpen(false)}>
              Cancel
            </Button>
            <Button
              onClick={handleSubmitAction}
              className={actionType === 'approve' ? 'bg-green-600 hover:bg-green-700' : 'bg-red-600 hover:bg-red-700'}
              disabled={actionType === 'reject' && !comments.trim()}
            >
              {actionType === 'approve' ? (
                <>
                  <CheckCircle className="h-4 w-4 mr-2" />
                  Approve
                </>
              ) : (
                <>
                  <XCircle className="h-4 w-4 mr-2" />
                  Reject
                </>
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
