'use client';

import { useState, useEffect } from 'react';
import {
  Plus,
  Search,
  Wrench,
  Eye,
  Play,
  Pause,
  CheckCircle,
  Clock,
  Users,
  Loader2,
  AlertTriangle,
  Trash2,
  Settings,
  Timer,
  MoreVertical,
  Download,
  Filter,
  Cog,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { PageHeader } from '@/components/layout/page-header';
import { StatCard } from '@/components/layout/stat-card';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { useApi, useToast } from '@/hooks';
import { formatDate } from '@/lib/format';

interface Operator {
  id: string;
  name: string;
  employee_code: string;
}

interface WorkOrder {
  id: string;
  work_order_number: string;
  production_order: string;
  operation_name: string;
  operation_sequence: number;
  work_center: string;
  work_center_code: string;
  status: 'pending' | 'queued' | 'in_progress' | 'paused' | 'completed' | 'cancelled';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  planned_qty: number;
  completed_qty: number;
  rejected_qty: number;
  planned_start: string;
  planned_end: string;
  actual_start: string | null;
  actual_end: string | null;
  planned_hours: number;
  actual_hours: number;
  operators: Operator[];
  setup_time_mins: number;
  run_time_mins: number;
  notes: string;
  created_at: string;
}

const statusColors: Record<string, string> = {
  pending: 'bg-gray-100 text-gray-800',
  queued: 'bg-blue-100 text-blue-800',
  in_progress: 'bg-yellow-100 text-yellow-800',
  paused: 'bg-orange-100 text-orange-800',
  completed: 'bg-green-100 text-green-800',
  cancelled: 'bg-red-100 text-red-800',
};

const priorityColors: Record<string, string> = {
  low: 'bg-green-100 text-green-800',
  medium: 'bg-yellow-100 text-yellow-800',
  high: 'bg-orange-100 text-orange-800',
  urgent: 'bg-red-100 text-red-800',
};

const mockOperators: Operator[] = [
  { id: '1', name: 'Rajesh Kumar', employee_code: 'EMP-001' },
  { id: '2', name: 'Amit Singh', employee_code: 'EMP-002' },
  { id: '3', name: 'Priya Sharma', employee_code: 'EMP-003' },
  { id: '4', name: 'Suresh Patel', employee_code: 'EMP-004' },
  { id: '5', name: 'Meena Devi', employee_code: 'EMP-005' },
];

const mockWorkOrders: WorkOrder[] = [
  {
    id: '1',
    work_order_number: 'WO-000001',
    production_order: 'PO-000001',
    operation_name: 'Motor Assembly',
    operation_sequence: 1,
    work_center: 'Assembly Line 1',
    work_center_code: 'WC-001',
    status: 'in_progress',
    priority: 'high',
    planned_qty: 100,
    completed_qty: 45,
    rejected_qty: 2,
    planned_start: '2026-01-10',
    planned_end: '2026-01-15',
    actual_start: '2026-01-10',
    actual_end: null,
    planned_hours: 40,
    actual_hours: 18,
    operators: [mockOperators[0], mockOperators[1]],
    setup_time_mins: 30,
    run_time_mins: 15,
    notes: 'Priority assembly for ABC Corp order',
    created_at: '2026-01-08',
  },
  {
    id: '2',
    work_order_number: 'WO-000002',
    production_order: 'PO-000001',
    operation_name: 'Housing Fitting',
    operation_sequence: 2,
    work_center: 'Assembly Line 1',
    work_center_code: 'WC-001',
    status: 'queued',
    priority: 'high',
    planned_qty: 100,
    completed_qty: 0,
    rejected_qty: 0,
    planned_start: '2026-01-15',
    planned_end: '2026-01-18',
    actual_start: null,
    actual_end: null,
    planned_hours: 24,
    actual_hours: 0,
    operators: [mockOperators[2]],
    setup_time_mins: 20,
    run_time_mins: 12,
    notes: '',
    created_at: '2026-01-08',
  },
  {
    id: '3',
    work_order_number: 'WO-000003',
    production_order: 'PO-000002',
    operation_name: 'CNC Machining',
    operation_sequence: 1,
    work_center: 'CNC Machine Shop',
    work_center_code: 'WC-002',
    status: 'pending',
    priority: 'medium',
    planned_qty: 200,
    completed_qty: 0,
    rejected_qty: 0,
    planned_start: '2026-01-15',
    planned_end: '2026-01-22',
    actual_start: null,
    actual_end: null,
    planned_hours: 56,
    actual_hours: 0,
    operators: [],
    setup_time_mins: 45,
    run_time_mins: 8,
    notes: '',
    created_at: '2026-01-12',
  },
  {
    id: '4',
    work_order_number: 'WO-000004',
    production_order: 'PO-000003',
    operation_name: 'Final Assembly',
    operation_sequence: 3,
    work_center: 'Finishing Station',
    work_center_code: 'WC-003',
    status: 'completed',
    priority: 'low',
    planned_qty: 500,
    completed_qty: 500,
    rejected_qty: 5,
    planned_start: '2026-01-05',
    planned_end: '2026-01-09',
    actual_start: '2026-01-05',
    actual_end: '2026-01-09',
    planned_hours: 32,
    actual_hours: 30,
    operators: [mockOperators[3], mockOperators[4]],
    setup_time_mins: 15,
    run_time_mins: 4,
    notes: 'Completed ahead of schedule',
    created_at: '2025-12-28',
  },
  {
    id: '5',
    work_order_number: 'WO-000005',
    production_order: 'PO-000004',
    operation_name: 'Pump Assembly',
    operation_sequence: 1,
    work_center: 'Assembly Line 1',
    work_center_code: 'WC-001',
    status: 'paused',
    priority: 'urgent',
    planned_qty: 50,
    completed_qty: 15,
    rejected_qty: 0,
    planned_start: '2026-01-14',
    planned_end: '2026-01-16',
    actual_start: '2026-01-14',
    actual_end: null,
    planned_hours: 16,
    actual_hours: 5,
    operators: [mockOperators[0]],
    setup_time_mins: 25,
    run_time_mins: 18,
    notes: 'Paused - waiting for parts',
    created_at: '2026-01-13',
  },
];

export default function WorkOrdersPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [workCenterFilter, setWorkCenterFilter] = useState<string>('all');
  const { showToast } = useToast();
  const { data: workOrdersData, isLoading, get: getWorkOrders } = useApi<{ data: WorkOrder[] }>();
  const deleteApi = useApi();

  // Local state
  const [localWorkOrders, setLocalWorkOrders] = useState<WorkOrder[]>([]);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [itemToDelete, setItemToDelete] = useState<WorkOrder | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  // Dialog states
  const [viewDialogOpen, setViewDialogOpen] = useState(false);
  const [assignDialogOpen, setAssignDialogOpen] = useState(false);
  const [selectedWorkOrder, setSelectedWorkOrder] = useState<WorkOrder | null>(null);
  const [selectedOperators, setSelectedOperators] = useState<string[]>([]);

  useEffect(() => {
    getWorkOrders('/manufacturing/work-orders');
  }, [getWorkOrders]);

  useEffect(() => {
    if (workOrdersData?.data) {
      setLocalWorkOrders(workOrdersData.data);
    }
  }, [workOrdersData]);

  const workOrders = localWorkOrders.length > 0 ? localWorkOrders : mockWorkOrders;

  const filteredWorkOrders = workOrders.filter((wo) => {
    const matchesSearch =
      wo.work_order_number.toLowerCase().includes(searchQuery.toLowerCase()) ||
      wo.operation_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      wo.production_order.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = statusFilter === 'all' || wo.status === statusFilter;
    const matchesWorkCenter = workCenterFilter === 'all' || wo.work_center_code === workCenterFilter;
    return matchesSearch && matchesStatus && matchesWorkCenter;
  });

  const stats = {
    totalWorkOrders: workOrders.length,
    inProgress: workOrders.filter((wo) => wo.status === 'in_progress').length,
    queued: workOrders.filter((wo) => wo.status === 'queued').length,
    completedToday: workOrders.filter(
      (wo) => wo.status === 'completed' && wo.actual_end === '2026-01-16'
    ).length,
  };

  const handleDeleteClick = (wo: WorkOrder) => {
    setItemToDelete(wo);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!itemToDelete) return;
    setIsDeleting(true);
    try {
      await deleteApi.delete(`/manufacturing/work-orders/${itemToDelete.id}`);
      setLocalWorkOrders(localWorkOrders.filter((wo) => wo.id !== itemToDelete.id));
      setDeleteDialogOpen(false);
      setItemToDelete(null);
      showToast('success', 'Work order deleted successfully');
    } catch (error) {
      console.error('Failed to delete:', error);
      showToast('error', 'Failed to delete work order');
    } finally {
      setIsDeleting(false);
    }
  };

  const handleViewWorkOrder = (wo: WorkOrder) => {
    setSelectedWorkOrder(wo);
    setViewDialogOpen(true);
  };

  const handleAssignClick = (wo: WorkOrder) => {
    setSelectedWorkOrder(wo);
    setSelectedOperators(wo.operators.map((op) => op.id));
    setAssignDialogOpen(true);
  };

  const handleAssignOperators = async () => {
    if (!selectedWorkOrder) return;
    try {
      const assignedOperators = mockOperators.filter((op) => selectedOperators.includes(op.id));
      setLocalWorkOrders(
        localWorkOrders.map((wo) =>
          wo.id === selectedWorkOrder.id ? { ...wo, operators: assignedOperators } : wo
        )
      );
      setAssignDialogOpen(false);
      setSelectedWorkOrder(null);
      showToast('success', 'Operators assigned successfully');
    } catch (error) {
      console.error('Failed to assign operators:', error);
      showToast('error', 'Failed to assign operators');
    }
  };

  const handleStatusChange = async (wo: WorkOrder, newStatus: WorkOrder['status']) => {
    try {
      const updates: Partial<WorkOrder> = { status: newStatus };
      if (newStatus === 'in_progress' && !wo.actual_start) {
        updates.actual_start = new Date().toISOString().split('T')[0];
      }
      if (newStatus === 'completed') {
        updates.actual_end = new Date().toISOString().split('T')[0];
        updates.completed_qty = wo.planned_qty;
      }
      setLocalWorkOrders(
        localWorkOrders.map((item) => (item.id === wo.id ? { ...item, ...updates } : item))
      );
      showToast('success', `Work order status changed to ${newStatus.replace('_', ' ')}`);
    } catch (error) {
      console.error('Failed to update status:', error);
      showToast('error', 'Failed to update work order status');
    }
  };

  const getProgressPercentage = (wo: WorkOrder) => {
    if (wo.planned_qty === 0) return 0;
    return Math.round((wo.completed_qty / wo.planned_qty) * 100);
  };

  const getEfficiencyPercentage = (wo: WorkOrder) => {
    if (wo.actual_hours === 0 || wo.planned_hours === 0) return 0;
    return Math.round((wo.planned_hours / wo.actual_hours) * 100);
  };

  const toggleOperatorSelection = (operatorId: string) => {
    setSelectedOperators((prev) =>
      prev.includes(operatorId)
        ? prev.filter((id) => id !== operatorId)
        : [...prev, operatorId]
    );
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Work Orders"
        description="Track and manage shop floor work orders and operations"
        breadcrumbs={[
          { label: 'Manufacturing', href: '/manufacturing' },
          { label: 'Work Orders' },
        ]}
        actions={
          <Button variant="outline">
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
        }
      />

      {isLoading && (
        <Card className="p-8 flex items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <span className="ml-2">Loading work orders...</span>
        </Card>
      )}

      {/* Stats */}
      <div className="grid gap-4 md:grid-cols-4">
        <StatCard
          title="Total Work Orders"
          value={stats.totalWorkOrders}
          icon={Wrench}
          description="All operations"
        />
        <StatCard
          title="In Progress"
          value={stats.inProgress}
          icon={Play}
          description="Currently running"
        />
        <StatCard
          title="Queued"
          value={stats.queued}
          icon={Clock}
          description="Waiting to start"
        />
        <StatCard
          title="Completed Today"
          value={stats.completedToday}
          icon={CheckCircle}
          description="Operations finished"
        />
      </div>

      {/* Filters */}
      <div className="flex gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search work orders..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-9"
          />
        </div>
        <Select value={statusFilter} onValueChange={setStatusFilter}>
          <SelectTrigger className="w-[180px]">
            <Filter className="mr-2 h-4 w-4" />
            <SelectValue placeholder="Status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Status</SelectItem>
            <SelectItem value="pending">Pending</SelectItem>
            <SelectItem value="queued">Queued</SelectItem>
            <SelectItem value="in_progress">In Progress</SelectItem>
            <SelectItem value="paused">Paused</SelectItem>
            <SelectItem value="completed">Completed</SelectItem>
            <SelectItem value="cancelled">Cancelled</SelectItem>
          </SelectContent>
        </Select>
        <Select value={workCenterFilter} onValueChange={setWorkCenterFilter}>
          <SelectTrigger className="w-[200px]">
            <Cog className="mr-2 h-4 w-4" />
            <SelectValue placeholder="Work Center" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Work Centers</SelectItem>
            <SelectItem value="WC-001">Assembly Line 1</SelectItem>
            <SelectItem value="WC-002">CNC Machine Shop</SelectItem>
            <SelectItem value="WC-003">Finishing Station</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Work Orders Table */}
      <Card>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Work Order #</TableHead>
              <TableHead>Operation</TableHead>
              <TableHead>Production Order</TableHead>
              <TableHead>Work Center</TableHead>
              <TableHead>Progress</TableHead>
              <TableHead>Priority</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Operators</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filteredWorkOrders.map((wo) => (
              <TableRow key={wo.id}>
                <TableCell className="font-medium">{wo.work_order_number}</TableCell>
                <TableCell>
                  <div>
                    <p className="font-medium">{wo.operation_name}</p>
                    <p className="text-sm text-muted-foreground">Seq: {wo.operation_sequence}</p>
                  </div>
                </TableCell>
                <TableCell>{wo.production_order}</TableCell>
                <TableCell>
                  <div>
                    <p className="font-medium">{wo.work_center}</p>
                    <p className="text-sm text-muted-foreground">{wo.work_center_code}</p>
                  </div>
                </TableCell>
                <TableCell>
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <div className="h-2 w-20 bg-gray-200 rounded">
                        <div
                          className="h-2 bg-green-500 rounded"
                          style={{ width: `${getProgressPercentage(wo)}%` }}
                        />
                      </div>
                      <span className="text-sm">{getProgressPercentage(wo)}%</span>
                    </div>
                    <p className="text-xs text-muted-foreground">
                      {wo.completed_qty} / {wo.planned_qty} units
                    </p>
                  </div>
                </TableCell>
                <TableCell>
                  <Badge className={priorityColors[wo.priority]}>{wo.priority}</Badge>
                </TableCell>
                <TableCell>
                  <Badge className={statusColors[wo.status]}>
                    {wo.status.replace('_', ' ')}
                  </Badge>
                </TableCell>
                <TableCell>
                  <div className="flex items-center gap-1">
                    {wo.operators.length > 0 ? (
                      <>
                        <Users className="h-4 w-4 text-muted-foreground" />
                        <span className="text-sm">{wo.operators.length}</span>
                      </>
                    ) : (
                      <span className="text-sm text-muted-foreground">Unassigned</span>
                    )}
                  </div>
                </TableCell>
                <TableCell>
                  <div className="flex justify-end">
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button variant="ghost" size="sm">
                          <MoreVertical className="h-4 w-4" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuItem onClick={() => handleViewWorkOrder(wo)}>
                          <Eye className="h-4 w-4 mr-2" />
                          View Details
                        </DropdownMenuItem>
                        <DropdownMenuItem onClick={() => handleAssignClick(wo)}>
                          <Users className="h-4 w-4 mr-2" />
                          Assign Operators
                        </DropdownMenuItem>
                        {wo.status === 'pending' && (
                          <DropdownMenuItem onClick={() => handleStatusChange(wo, 'queued')}>
                            <Clock className="h-4 w-4 mr-2" />
                            Queue
                          </DropdownMenuItem>
                        )}
                        {wo.status === 'queued' && (
                          <DropdownMenuItem onClick={() => handleStatusChange(wo, 'in_progress')}>
                            <Play className="h-4 w-4 mr-2 text-green-500" />
                            Start
                          </DropdownMenuItem>
                        )}
                        {wo.status === 'in_progress' && (
                          <>
                            <DropdownMenuItem onClick={() => handleStatusChange(wo, 'paused')}>
                              <Pause className="h-4 w-4 mr-2 text-yellow-500" />
                              Pause
                            </DropdownMenuItem>
                            <DropdownMenuItem onClick={() => handleStatusChange(wo, 'completed')}>
                              <CheckCircle className="h-4 w-4 mr-2 text-green-500" />
                              Complete
                            </DropdownMenuItem>
                          </>
                        )}
                        {wo.status === 'paused' && (
                          <DropdownMenuItem onClick={() => handleStatusChange(wo, 'in_progress')}>
                            <Play className="h-4 w-4 mr-2 text-green-500" />
                            Resume
                          </DropdownMenuItem>
                        )}
                        {(wo.status === 'completed' || wo.status === 'cancelled') && (
                          <DropdownMenuItem
                            className="text-red-600"
                            onClick={() => handleDeleteClick(wo)}
                          >
                            <Trash2 className="h-4 w-4 mr-2" />
                            Delete
                          </DropdownMenuItem>
                        )}
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </div>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Card>

      {filteredWorkOrders.length === 0 && !isLoading && (
        <Card className="p-12 text-center">
          <Wrench className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
          <h3 className="text-lg font-medium mb-2">No work orders found</h3>
          <p className="text-muted-foreground">
            {searchQuery || statusFilter !== 'all' || workCenterFilter !== 'all'
              ? 'Try adjusting your filters'
              : 'Work orders are created from production orders'}
          </p>
        </Card>
      )}

      {/* View Work Order Dialog */}
      <Dialog open={viewDialogOpen} onOpenChange={setViewDialogOpen}>
        <DialogContent className="max-w-3xl">
          <DialogHeader>
            <DialogTitle>Work Order - {selectedWorkOrder?.work_order_number}</DialogTitle>
            <DialogDescription>
              View detailed information about this work order
            </DialogDescription>
          </DialogHeader>
          {selectedWorkOrder && (
            <div className="space-y-6">
              <div className="flex items-center gap-4">
                <Badge className={statusColors[selectedWorkOrder.status]}>
                  {selectedWorkOrder.status.replace('_', ' ')}
                </Badge>
                <Badge className={priorityColors[selectedWorkOrder.priority]}>
                  {selectedWorkOrder.priority} priority
                </Badge>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <h4 className="text-sm font-medium text-muted-foreground">Operation</h4>
                  <p className="font-medium">{selectedWorkOrder.operation_name}</p>
                  <p className="text-sm text-muted-foreground">
                    Sequence: {selectedWorkOrder.operation_sequence}
                  </p>
                </div>
                <div>
                  <h4 className="text-sm font-medium text-muted-foreground">Production Order</h4>
                  <p className="font-medium">{selectedWorkOrder.production_order}</p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <h4 className="text-sm font-medium text-muted-foreground">Work Center</h4>
                  <p className="font-medium">{selectedWorkOrder.work_center}</p>
                  <p className="text-sm text-muted-foreground">{selectedWorkOrder.work_center_code}</p>
                </div>
                <div>
                  <h4 className="text-sm font-medium text-muted-foreground">Assigned Operators</h4>
                  {selectedWorkOrder.operators.length > 0 ? (
                    <div className="flex flex-wrap gap-1 mt-1">
                      {selectedWorkOrder.operators.map((op) => (
                        <Badge key={op.id} variant="outline">
                          {op.name}
                        </Badge>
                      ))}
                    </div>
                  ) : (
                    <p className="text-sm text-muted-foreground">No operators assigned</p>
                  )}
                </div>
              </div>

              <div className="grid grid-cols-4 gap-4">
                <Card className="p-4">
                  <p className="text-sm text-muted-foreground">Planned</p>
                  <p className="text-lg font-bold">{selectedWorkOrder.planned_qty}</p>
                </Card>
                <Card className="p-4">
                  <p className="text-sm text-muted-foreground">Completed</p>
                  <p className="text-lg font-bold text-green-600">{selectedWorkOrder.completed_qty}</p>
                </Card>
                <Card className="p-4">
                  <p className="text-sm text-muted-foreground">Rejected</p>
                  <p className="text-lg font-bold text-red-600">{selectedWorkOrder.rejected_qty}</p>
                </Card>
                <Card className="p-4">
                  <p className="text-sm text-muted-foreground">Progress</p>
                  <p className="text-lg font-bold">{getProgressPercentage(selectedWorkOrder)}%</p>
                </Card>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <Card className="p-4">
                  <h4 className="text-sm font-medium text-muted-foreground mb-2">Time Tracking</h4>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span>Setup Time:</span>
                      <span className="font-medium">{selectedWorkOrder.setup_time_mins} mins</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Run Time per Unit:</span>
                      <span className="font-medium">{selectedWorkOrder.run_time_mins} mins</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Planned Hours:</span>
                      <span className="font-medium">{selectedWorkOrder.planned_hours} hrs</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Actual Hours:</span>
                      <span className="font-medium">{selectedWorkOrder.actual_hours} hrs</span>
                    </div>
                  </div>
                </Card>
                <Card className="p-4">
                  <h4 className="text-sm font-medium text-muted-foreground mb-2">Schedule</h4>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span>Planned Start:</span>
                      <span className="font-medium">{formatDate(selectedWorkOrder.planned_start)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Planned End:</span>
                      <span className="font-medium">{formatDate(selectedWorkOrder.planned_end)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Actual Start:</span>
                      <span className="font-medium">
                        {selectedWorkOrder.actual_start
                          ? formatDate(selectedWorkOrder.actual_start)
                          : '-'}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span>Actual End:</span>
                      <span className="font-medium">
                        {selectedWorkOrder.actual_end
                          ? formatDate(selectedWorkOrder.actual_end)
                          : '-'}
                      </span>
                    </div>
                  </div>
                </Card>
              </div>

              {selectedWorkOrder.actual_hours > 0 && (
                <Card className="p-4">
                  <h4 className="text-sm font-medium text-muted-foreground mb-2">Efficiency</h4>
                  <div className="flex items-center gap-4">
                    <div className="flex-1">
                      <div className="h-3 bg-gray-200 rounded">
                        <div
                          className={`h-3 rounded ${
                            getEfficiencyPercentage(selectedWorkOrder) >= 100
                              ? 'bg-green-500'
                              : getEfficiencyPercentage(selectedWorkOrder) >= 80
                              ? 'bg-yellow-500'
                              : 'bg-red-500'
                          }`}
                          style={{
                            width: `${Math.min(getEfficiencyPercentage(selectedWorkOrder), 100)}%`,
                          }}
                        />
                      </div>
                    </div>
                    <span className="text-lg font-bold">
                      {getEfficiencyPercentage(selectedWorkOrder)}%
                    </span>
                  </div>
                </Card>
              )}

              {selectedWorkOrder.notes && (
                <div>
                  <h4 className="text-sm font-medium text-muted-foreground mb-1">Notes</h4>
                  <p className="text-sm">{selectedWorkOrder.notes}</p>
                </div>
              )}
            </div>
          )}
          <DialogFooter>
            <Button variant="outline" onClick={() => setViewDialogOpen(false)}>
              Close
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Assign Operators Dialog */}
      <Dialog open={assignDialogOpen} onOpenChange={setAssignDialogOpen}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Assign Operators</DialogTitle>
            <DialogDescription>
              Select operators to assign to {selectedWorkOrder?.work_order_number}
            </DialogDescription>
          </DialogHeader>
          <div className="py-4">
            <div className="space-y-2">
              {mockOperators.map((operator) => (
                <div
                  key={operator.id}
                  className={`flex items-center justify-between p-3 border rounded-lg cursor-pointer transition-colors ${
                    selectedOperators.includes(operator.id)
                      ? 'border-primary bg-primary/5'
                      : 'hover:bg-muted/50'
                  }`}
                  onClick={() => toggleOperatorSelection(operator.id)}
                >
                  <div className="flex items-center gap-3">
                    <div
                      className={`w-4 h-4 rounded border-2 flex items-center justify-center ${
                        selectedOperators.includes(operator.id)
                          ? 'border-primary bg-primary'
                          : 'border-gray-300'
                      }`}
                    >
                      {selectedOperators.includes(operator.id) && (
                        <CheckCircle className="h-3 w-3 text-white" />
                      )}
                    </div>
                    <div>
                      <p className="font-medium">{operator.name}</p>
                      <p className="text-sm text-muted-foreground">{operator.employee_code}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setAssignDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleAssignOperators}>
              Assign ({selectedOperators.length})
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-red-500" />
              Delete Work Order
            </AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete work order{' '}
              <strong>{itemToDelete?.work_order_number}</strong>? This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={isDeleting}>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDeleteConfirm}
              disabled={isDeleting}
              className="bg-red-600 hover:bg-red-700 focus:ring-red-600"
            >
              {isDeleting ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Deleting...
                </>
              ) : (
                'Delete'
              )}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
