'use client';

import { useState, useEffect } from 'react';
import {
  Plus,
  Search,
  ClipboardList,
  Eye,
  Edit,
  Play,
  Pause,
  CheckCircle,
  XCircle,
  Trash2,
  Loader2,
  AlertTriangle,
  Clock,
  Calendar,
  Factory,
  Package,
  Download,
  Filter,
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
import { useApi, useToast } from '@/hooks';
import { formatCurrency, formatDate } from '@/lib/format';

interface ProductionOrder {
  id: string;
  order_number: string;
  product_code: string;
  product_name: string;
  bom_number: string;
  quantity: number;
  completed_qty: number;
  rejected_qty: number;
  status: 'draft' | 'planned' | 'released' | 'in_progress' | 'completed' | 'cancelled';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  work_center: string;
  planned_start: string;
  planned_end: string;
  actual_start: string | null;
  actual_end: string | null;
  estimated_cost: number;
  actual_cost: number;
  customer_order: string | null;
  notes: string;
  created_by: string;
  created_at: string;
}

const statusColors: Record<string, string> = {
  draft: 'bg-gray-100 text-gray-800',
  planned: 'bg-blue-100 text-blue-800',
  released: 'bg-purple-100 text-purple-800',
  in_progress: 'bg-yellow-100 text-yellow-800',
  completed: 'bg-green-100 text-green-800',
  cancelled: 'bg-red-100 text-red-800',
};

const priorityColors: Record<string, string> = {
  low: 'bg-green-100 text-green-800',
  medium: 'bg-yellow-100 text-yellow-800',
  high: 'bg-orange-100 text-orange-800',
  urgent: 'bg-red-100 text-red-800',
};

const mockProductionOrders: ProductionOrder[] = [
  {
    id: '1',
    order_number: 'PO-000001',
    product_code: 'PUMP-A-001',
    product_name: 'Industrial Pump Model A',
    bom_number: 'BOM-000001',
    quantity: 100,
    completed_qty: 45,
    rejected_qty: 2,
    status: 'in_progress',
    priority: 'high',
    work_center: 'Assembly Line 1',
    planned_start: '2026-01-10',
    planned_end: '2026-01-25',
    actual_start: '2026-01-10',
    actual_end: null,
    estimated_cost: 1500000,
    actual_cost: 680000,
    customer_order: 'SO-000123',
    notes: 'Priority order for ABC Corp',
    created_by: 'John Smith',
    created_at: '2026-01-08',
  },
  {
    id: '2',
    order_number: 'PO-000002',
    product_code: 'MOTOR-B-001',
    product_name: 'Motor Assembly B',
    bom_number: 'BOM-000002',
    quantity: 200,
    completed_qty: 0,
    rejected_qty: 0,
    status: 'released',
    priority: 'medium',
    work_center: 'Machine Shop',
    planned_start: '2026-01-15',
    planned_end: '2026-01-30',
    actual_start: null,
    actual_end: null,
    estimated_cost: 1700000,
    actual_cost: 0,
    customer_order: null,
    notes: 'Stock replenishment',
    created_by: 'Jane Doe',
    created_at: '2026-01-12',
  },
  {
    id: '3',
    order_number: 'PO-000003',
    product_code: 'VALVE-C-001',
    product_name: 'Valve Kit C',
    bom_number: 'BOM-000003',
    quantity: 500,
    completed_qty: 500,
    rejected_qty: 5,
    status: 'completed',
    priority: 'low',
    work_center: 'Finishing Station',
    planned_start: '2026-01-01',
    planned_end: '2026-01-10',
    actual_start: '2026-01-01',
    actual_end: '2026-01-09',
    estimated_cost: 1900000,
    actual_cost: 1850000,
    customer_order: 'SO-000118',
    notes: '',
    created_by: 'Mike Johnson',
    created_at: '2025-12-28',
  },
  {
    id: '4',
    order_number: 'PO-000004',
    product_code: 'PUMP-A-001',
    product_name: 'Industrial Pump Model A',
    bom_number: 'BOM-000001',
    quantity: 50,
    completed_qty: 0,
    rejected_qty: 0,
    status: 'planned',
    priority: 'urgent',
    work_center: 'Assembly Line 1',
    planned_start: '2026-01-20',
    planned_end: '2026-01-28',
    actual_start: null,
    actual_end: null,
    estimated_cost: 750000,
    actual_cost: 0,
    customer_order: 'SO-000145',
    notes: 'Rush order - expedite',
    created_by: 'John Smith',
    created_at: '2026-01-14',
  },
  {
    id: '5',
    order_number: 'PO-000005',
    product_code: 'MOTOR-B-001',
    product_name: 'Motor Assembly B',
    bom_number: 'BOM-000002',
    quantity: 75,
    completed_qty: 0,
    rejected_qty: 0,
    status: 'draft',
    priority: 'medium',
    work_center: 'Machine Shop',
    planned_start: '2026-02-01',
    planned_end: '2026-02-10',
    actual_start: null,
    actual_end: null,
    estimated_cost: 637500,
    actual_cost: 0,
    customer_order: null,
    notes: 'Pending material availability',
    created_by: 'Jane Doe',
    created_at: '2026-01-15',
  },
];

export default function ProductionOrdersPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [priorityFilter, setPriorityFilter] = useState<string>('all');
  const { showToast } = useToast();
  const { data: ordersData, isLoading, get: getOrders } = useApi<{ data: ProductionOrder[] }>();
  const deleteApi = useApi();

  // Local state
  const [localOrders, setLocalOrders] = useState<ProductionOrder[]>([]);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [itemToDelete, setItemToDelete] = useState<ProductionOrder | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  // Dialog states
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [viewDialogOpen, setViewDialogOpen] = useState(false);
  const [selectedOrder, setSelectedOrder] = useState<ProductionOrder | null>(null);

  // Form state
  const [formData, setFormData] = useState({
    product_code: '',
    product_name: '',
    bom_number: '',
    quantity: '',
    priority: 'medium' as ProductionOrder['priority'],
    work_center: '',
    planned_start: '',
    planned_end: '',
    customer_order: '',
    notes: '',
  });

  useEffect(() => {
    getOrders('/manufacturing/production-orders');
  }, [getOrders]);

  useEffect(() => {
    if (ordersData?.data) {
      setLocalOrders(ordersData.data);
    }
  }, [ordersData]);

  const orders = localOrders.length > 0 ? localOrders : mockProductionOrders;

  const filteredOrders = orders.filter((order) => {
    const matchesSearch =
      order.order_number.toLowerCase().includes(searchQuery.toLowerCase()) ||
      order.product_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      order.product_code.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = statusFilter === 'all' || order.status === statusFilter;
    const matchesPriority = priorityFilter === 'all' || order.priority === priorityFilter;
    return matchesSearch && matchesStatus && matchesPriority;
  });

  const stats = {
    totalOrders: orders.length,
    inProgress: orders.filter((o) => o.status === 'in_progress').length,
    released: orders.filter((o) => o.status === 'released').length,
    completedThisMonth: orders.filter(
      (o) => o.status === 'completed' && o.actual_end?.startsWith('2026-01')
    ).length,
  };

  const handleDeleteClick = (order: ProductionOrder) => {
    setItemToDelete(order);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!itemToDelete) return;
    setIsDeleting(true);
    try {
      await deleteApi.delete(`/manufacturing/production-orders/${itemToDelete.id}`);
      setLocalOrders(localOrders.filter((o) => o.id !== itemToDelete.id));
      setDeleteDialogOpen(false);
      setItemToDelete(null);
      showToast('success', 'Production order deleted successfully');
    } catch (error) {
      showToast('error', 'Failed to delete production order');
    } finally {
      setIsDeleting(false);
    }
  };

  const handleViewOrder = (order: ProductionOrder) => {
    setSelectedOrder(order);
    setViewDialogOpen(true);
  };

  const handleCreateOrder = async () => {
    try {
      const newOrder: ProductionOrder = {
        id: Date.now().toString(),
        order_number: `PO-${String(orders.length + 1).padStart(6, '0')}`,
        product_code: formData.product_code,
        product_name: formData.product_name,
        bom_number: formData.bom_number,
        quantity: parseInt(formData.quantity) || 0,
        completed_qty: 0,
        rejected_qty: 0,
        status: 'draft',
        priority: formData.priority,
        work_center: formData.work_center,
        planned_start: formData.planned_start,
        planned_end: formData.planned_end,
        actual_start: null,
        actual_end: null,
        estimated_cost: (parseInt(formData.quantity) || 0) * 15000,
        actual_cost: 0,
        customer_order: formData.customer_order || null,
        notes: formData.notes,
        created_by: 'Current User',
        created_at: new Date().toISOString().split('T')[0],
      };
      setLocalOrders([...localOrders, newOrder]);
      setCreateDialogOpen(false);
      resetForm();
      showToast('success', 'Production order created successfully');
    } catch (error) {
      showToast('error', 'Failed to create production order');
    }
  };

  const handleStatusChange = async (order: ProductionOrder, newStatus: ProductionOrder['status']) => {
    try {
      const updates: Partial<ProductionOrder> = { status: newStatus };
      if (newStatus === 'in_progress' && !order.actual_start) {
        updates.actual_start = new Date().toISOString().split('T')[0];
      }
      if (newStatus === 'completed') {
        updates.actual_end = new Date().toISOString().split('T')[0];
        updates.completed_qty = order.quantity;
      }
      setLocalOrders(
        localOrders.map((o) => (o.id === order.id ? { ...o, ...updates } : o))
      );
      showToast('success', `Order status changed to ${newStatus.replace('_', ' ')}`);
    } catch (error) {
      showToast('error', 'Failed to update order status');
    }
  };

  const resetForm = () => {
    setFormData({
      product_code: '',
      product_name: '',
      bom_number: '',
      quantity: '',
      priority: 'medium',
      work_center: '',
      planned_start: '',
      planned_end: '',
      customer_order: '',
      notes: '',
    });
  };

  const getProgressPercentage = (order: ProductionOrder) => {
    if (order.quantity === 0) return 0;
    return Math.round((order.completed_qty / order.quantity) * 100);
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Production Orders"
        description="Manage production requisitions and track manufacturing progress"
        breadcrumbs={[
          { label: 'Manufacturing', href: '/manufacturing' },
          { label: 'Production Orders' },
        ]}
        actions={
          <div className="flex gap-2">
            <Button variant="outline">
              <Download className="h-4 w-4 mr-2" />
              Export
            </Button>
            <Dialog open={createDialogOpen} onOpenChange={setCreateDialogOpen}>
              <DialogTrigger asChild>
                <Button>
                  <Plus className="h-4 w-4 mr-2" />
                  Create Order
                </Button>
              </DialogTrigger>
              <DialogContent className="max-w-2xl">
                <DialogHeader>
                  <DialogTitle>Create Production Order</DialogTitle>
                  <DialogDescription>
                    Create a new production order for manufacturing
                  </DialogDescription>
                </DialogHeader>
                <div className="grid gap-4 py-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label>Product</Label>
                      <Select
                        value={formData.product_code}
                        onValueChange={(value) => {
                          const products: Record<string, string> = {
                            'PUMP-A-001': 'Industrial Pump Model A',
                            'MOTOR-B-001': 'Motor Assembly B',
                            'VALVE-C-001': 'Valve Kit C',
                          };
                          setFormData({
                            ...formData,
                            product_code: value,
                            product_name: products[value] || '',
                          });
                        }}
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="Select product" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="PUMP-A-001">Industrial Pump Model A</SelectItem>
                          <SelectItem value="MOTOR-B-001">Motor Assembly B</SelectItem>
                          <SelectItem value="VALVE-C-001">Valve Kit C</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="space-y-2">
                      <Label>BOM</Label>
                      <Select
                        value={formData.bom_number}
                        onValueChange={(value) => setFormData({ ...formData, bom_number: value })}
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="Select BOM" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="BOM-000001">BOM-000001 - Pump A</SelectItem>
                          <SelectItem value="BOM-000002">BOM-000002 - Motor B</SelectItem>
                          <SelectItem value="BOM-000003">BOM-000003 - Valve C</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label>Quantity</Label>
                      <Input
                        type="number"
                        placeholder="Enter quantity"
                        value={formData.quantity}
                        onChange={(e) => setFormData({ ...formData, quantity: e.target.value })}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label>Priority</Label>
                      <Select
                        value={formData.priority}
                        onValueChange={(value) =>
                          setFormData({ ...formData, priority: value as ProductionOrder['priority'] })
                        }
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="low">Low</SelectItem>
                          <SelectItem value="medium">Medium</SelectItem>
                          <SelectItem value="high">High</SelectItem>
                          <SelectItem value="urgent">Urgent</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label>Work Center</Label>
                      <Select
                        value={formData.work_center}
                        onValueChange={(value) => setFormData({ ...formData, work_center: value })}
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="Select work center" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="Assembly Line 1">Assembly Line 1</SelectItem>
                          <SelectItem value="Machine Shop">Machine Shop</SelectItem>
                          <SelectItem value="Finishing Station">Finishing Station</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="space-y-2">
                      <Label>Customer Order (Optional)</Label>
                      <Input
                        placeholder="SO-XXXXXX"
                        value={formData.customer_order}
                        onChange={(e) => setFormData({ ...formData, customer_order: e.target.value })}
                      />
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label>Planned Start Date</Label>
                      <Input
                        type="date"
                        value={formData.planned_start}
                        onChange={(e) => setFormData({ ...formData, planned_start: e.target.value })}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label>Planned End Date</Label>
                      <Input
                        type="date"
                        value={formData.planned_end}
                        onChange={(e) => setFormData({ ...formData, planned_end: e.target.value })}
                      />
                    </div>
                  </div>
                  <div className="space-y-2">
                    <Label>Notes</Label>
                    <Textarea
                      placeholder="Add any notes about this order"
                      value={formData.notes}
                      onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                    />
                  </div>
                </div>
                <DialogFooter>
                  <Button variant="outline" onClick={() => setCreateDialogOpen(false)}>
                    Cancel
                  </Button>
                  <Button onClick={handleCreateOrder}>Create Order</Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
          </div>
        }
      />

      {isLoading && (
        <Card className="p-8 flex items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <span className="ml-2">Loading production orders...</span>
        </Card>
      )}

      {/* Stats */}
      <div className="grid gap-4 md:grid-cols-4">
        <StatCard
          title="Total Orders"
          value={stats.totalOrders}
          icon={ClipboardList}
          description="All production orders"
        />
        <StatCard
          title="In Progress"
          value={stats.inProgress}
          icon={Factory}
          description="Currently manufacturing"
        />
        <StatCard
          title="Released"
          value={stats.released}
          icon={Play}
          description="Ready to start"
        />
        <StatCard
          title="Completed (MTD)"
          value={stats.completedThisMonth}
          icon={CheckCircle}
          description="This month"
        />
      </div>

      {/* Filters */}
      <div className="flex gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search orders..."
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
            <SelectItem value="draft">Draft</SelectItem>
            <SelectItem value="planned">Planned</SelectItem>
            <SelectItem value="released">Released</SelectItem>
            <SelectItem value="in_progress">In Progress</SelectItem>
            <SelectItem value="completed">Completed</SelectItem>
            <SelectItem value="cancelled">Cancelled</SelectItem>
          </SelectContent>
        </Select>
        <Select value={priorityFilter} onValueChange={setPriorityFilter}>
          <SelectTrigger className="w-[180px]">
            <SelectValue placeholder="Priority" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Priority</SelectItem>
            <SelectItem value="low">Low</SelectItem>
            <SelectItem value="medium">Medium</SelectItem>
            <SelectItem value="high">High</SelectItem>
            <SelectItem value="urgent">Urgent</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Orders Table */}
      <Card>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Order #</TableHead>
              <TableHead>Product</TableHead>
              <TableHead className="text-center">Quantity</TableHead>
              <TableHead>Progress</TableHead>
              <TableHead>Priority</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Work Center</TableHead>
              <TableHead>Schedule</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filteredOrders.map((order) => (
              <TableRow key={order.id}>
                <TableCell className="font-medium">{order.order_number}</TableCell>
                <TableCell>
                  <div>
                    <p className="font-medium">{order.product_name}</p>
                    <p className="text-sm text-muted-foreground">{order.product_code}</p>
                  </div>
                </TableCell>
                <TableCell className="text-center">
                  <div>
                    <p className="font-medium">{order.completed_qty} / {order.quantity}</p>
                    {order.rejected_qty > 0 && (
                      <p className="text-xs text-red-500">{order.rejected_qty} rejected</p>
                    )}
                  </div>
                </TableCell>
                <TableCell>
                  <div className="flex items-center gap-2">
                    <div className="h-2 w-24 bg-gray-200 rounded">
                      <div
                        className="h-2 bg-green-500 rounded"
                        style={{ width: `${getProgressPercentage(order)}%` }}
                      />
                    </div>
                    <span className="text-sm">{getProgressPercentage(order)}%</span>
                  </div>
                </TableCell>
                <TableCell>
                  <Badge className={priorityColors[order.priority]}>{order.priority}</Badge>
                </TableCell>
                <TableCell>
                  <Badge className={statusColors[order.status]}>
                    {order.status.replace('_', ' ')}
                  </Badge>
                </TableCell>
                <TableCell>{order.work_center}</TableCell>
                <TableCell>
                  <div className="text-sm">
                    <p>{formatDate(order.planned_start)}</p>
                    <p className="text-muted-foreground">to {formatDate(order.planned_end)}</p>
                  </div>
                </TableCell>
                <TableCell>
                  <div className="flex justify-end gap-1">
                    <Button variant="ghost" size="sm" onClick={() => handleViewOrder(order)}>
                      <Eye className="h-4 w-4" />
                    </Button>
                    {order.status === 'draft' && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleStatusChange(order, 'planned')}
                      >
                        <Calendar className="h-4 w-4 text-blue-500" />
                      </Button>
                    )}
                    {order.status === 'planned' && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleStatusChange(order, 'released')}
                      >
                        <CheckCircle className="h-4 w-4 text-purple-500" />
                      </Button>
                    )}
                    {order.status === 'released' && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleStatusChange(order, 'in_progress')}
                      >
                        <Play className="h-4 w-4 text-green-500" />
                      </Button>
                    )}
                    {order.status === 'in_progress' && (
                      <>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleStatusChange(order, 'completed')}
                        >
                          <CheckCircle className="h-4 w-4 text-green-500" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleStatusChange(order, 'released')}
                        >
                          <Pause className="h-4 w-4 text-yellow-500" />
                        </Button>
                      </>
                    )}
                    {(order.status === 'completed' || order.status === 'cancelled') && (
                      <Button
                        variant="ghost"
                        size="sm"
                        className="text-red-600 hover:text-red-700 hover:bg-red-50"
                        onClick={() => handleDeleteClick(order)}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    )}
                  </div>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Card>

      {filteredOrders.length === 0 && !isLoading && (
        <Card className="p-12 text-center">
          <ClipboardList className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
          <h3 className="text-lg font-medium mb-2">No production orders found</h3>
          <p className="text-muted-foreground mb-4">
            {searchQuery || statusFilter !== 'all' || priorityFilter !== 'all'
              ? 'Try adjusting your filters'
              : 'Get started by creating your first production order'}
          </p>
          <Button onClick={() => setCreateDialogOpen(true)}>
            <Plus className="h-4 w-4 mr-2" />
            Create Order
          </Button>
        </Card>
      )}

      {/* View Order Dialog */}
      <Dialog open={viewDialogOpen} onOpenChange={setViewDialogOpen}>
        <DialogContent className="max-w-3xl">
          <DialogHeader>
            <DialogTitle>Production Order - {selectedOrder?.order_number}</DialogTitle>
            <DialogDescription>
              View detailed information about this production order
            </DialogDescription>
          </DialogHeader>
          {selectedOrder && (
            <div className="space-y-6">
              <div className="flex items-center gap-4">
                <Badge className={statusColors[selectedOrder.status]}>
                  {selectedOrder.status.replace('_', ' ')}
                </Badge>
                <Badge className={priorityColors[selectedOrder.priority]}>
                  {selectedOrder.priority} priority
                </Badge>
                {selectedOrder.customer_order && (
                  <Badge variant="outline">Linked to {selectedOrder.customer_order}</Badge>
                )}
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <h4 className="text-sm font-medium text-muted-foreground">Product</h4>
                  <p className="font-medium">{selectedOrder.product_name}</p>
                  <p className="text-sm text-muted-foreground">{selectedOrder.product_code}</p>
                </div>
                <div>
                  <h4 className="text-sm font-medium text-muted-foreground">BOM Reference</h4>
                  <p className="font-medium">{selectedOrder.bom_number}</p>
                </div>
              </div>

              <div className="grid grid-cols-4 gap-4">
                <Card className="p-4">
                  <p className="text-sm text-muted-foreground">Ordered</p>
                  <p className="text-lg font-bold">{selectedOrder.quantity}</p>
                </Card>
                <Card className="p-4">
                  <p className="text-sm text-muted-foreground">Completed</p>
                  <p className="text-lg font-bold text-green-600">{selectedOrder.completed_qty}</p>
                </Card>
                <Card className="p-4">
                  <p className="text-sm text-muted-foreground">Rejected</p>
                  <p className="text-lg font-bold text-red-600">{selectedOrder.rejected_qty}</p>
                </Card>
                <Card className="p-4">
                  <p className="text-sm text-muted-foreground">Progress</p>
                  <p className="text-lg font-bold">{getProgressPercentage(selectedOrder)}%</p>
                </Card>
              </div>

              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="text-muted-foreground">Work Center</p>
                  <p className="font-medium">{selectedOrder.work_center}</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Created By</p>
                  <p className="font-medium">{selectedOrder.created_by}</p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <Card className="p-4">
                  <h4 className="text-sm font-medium text-muted-foreground mb-2">Planned Schedule</h4>
                  <div className="flex justify-between text-sm">
                    <span>Start:</span>
                    <span className="font-medium">{formatDate(selectedOrder.planned_start)}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span>End:</span>
                    <span className="font-medium">{formatDate(selectedOrder.planned_end)}</span>
                  </div>
                </Card>
                <Card className="p-4">
                  <h4 className="text-sm font-medium text-muted-foreground mb-2">Actual Schedule</h4>
                  <div className="flex justify-between text-sm">
                    <span>Start:</span>
                    <span className="font-medium">
                      {selectedOrder.actual_start ? formatDate(selectedOrder.actual_start) : '-'}
                    </span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span>End:</span>
                    <span className="font-medium">
                      {selectedOrder.actual_end ? formatDate(selectedOrder.actual_end) : '-'}
                    </span>
                  </div>
                </Card>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-muted-foreground">Estimated Cost</p>
                  <p className="text-lg font-bold">{formatCurrency(selectedOrder.estimated_cost)}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Actual Cost</p>
                  <p className="text-lg font-bold">{formatCurrency(selectedOrder.actual_cost)}</p>
                </div>
              </div>

              {selectedOrder.notes && (
                <div>
                  <h4 className="text-sm font-medium text-muted-foreground mb-1">Notes</h4>
                  <p className="text-sm">{selectedOrder.notes}</p>
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

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-red-500" />
              Delete Production Order
            </AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete order <strong>{itemToDelete?.order_number}</strong>?
              This action cannot be undone.
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
