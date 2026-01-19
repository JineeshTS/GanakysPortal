'use client';

import { useState, useEffect } from 'react';
import {
  Plus,
  Search,
  Filter,
  Eye,
  Edit,
  Trash2,
  Loader2,
  AlertTriangle,
  FileText,
  CheckCircle,
  Clock,
  XCircle,
  Package,
  Download,
  MoreVertical,
  X,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { PageHeader } from '@/components/layout/page-header';
import { StatCard } from '@/components/layout/stat-card';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
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

// Types
interface PurchaseOrderLineItem {
  id: string;
  item_code: string;
  item_name: string;
  quantity: number;
  unit_price: number;
  tax_rate: number;
  total: number;
}

interface PurchaseOrder {
  id: string;
  po_number: string;
  vendor_id: string;
  vendor_name: string;
  vendor_code: string;
  status: 'draft' | 'pending_approval' | 'approved' | 'sent' | 'partial_received' | 'received' | 'cancelled';
  approval_status: 'pending' | 'approved' | 'rejected';
  order_date: string;
  expected_delivery: string;
  line_items: PurchaseOrderLineItem[];
  subtotal: number;
  tax_amount: number;
  total_amount: number;
  received_amount: number;
  notes: string;
  created_at: string;
  updated_at: string;
}

interface Vendor {
  id: string;
  name: string;
  code: string;
}

// Status colors mapping
const statusColors: Record<string, string> = {
  draft: 'bg-gray-100 text-gray-800',
  pending_approval: 'bg-yellow-100 text-yellow-800',
  approved: 'bg-blue-100 text-blue-800',
  sent: 'bg-purple-100 text-purple-800',
  partial_received: 'bg-orange-100 text-orange-800',
  received: 'bg-green-100 text-green-800',
  cancelled: 'bg-red-100 text-red-800',
};

const approvalStatusColors: Record<string, string> = {
  pending: 'bg-yellow-100 text-yellow-800',
  approved: 'bg-green-100 text-green-800',
  rejected: 'bg-red-100 text-red-800',
};

// Mock data
const mockVendors: Vendor[] = [
  { id: '1', name: 'Tata Steel Ltd', code: 'SUP-001' },
  { id: '2', name: 'Reliance Industries', code: 'SUP-002' },
  { id: '3', name: 'Mahindra Components', code: 'SUP-003' },
  { id: '4', name: 'Jindal Steel', code: 'SUP-004' },
  { id: '5', name: 'Larsen & Toubro', code: 'SUP-005' },
];

const mockPurchaseOrders: PurchaseOrder[] = [
  {
    id: '1',
    po_number: 'PO-2026-0001',
    vendor_id: '1',
    vendor_name: 'Tata Steel Ltd',
    vendor_code: 'SUP-001',
    status: 'approved',
    approval_status: 'approved',
    order_date: '2026-01-10',
    expected_delivery: '2026-01-25',
    line_items: [
      { id: '1', item_code: 'STL-001', item_name: 'Steel Plates 10mm', quantity: 100, unit_price: 4500, tax_rate: 18, total: 531000 },
      { id: '2', item_code: 'STL-002', item_name: 'Steel Rods 8mm', quantity: 200, unit_price: 2200, tax_rate: 18, total: 519200 },
    ],
    subtotal: 890000,
    tax_amount: 160200,
    total_amount: 1050200,
    received_amount: 0,
    notes: 'Urgent delivery required',
    created_at: '2026-01-10T10:00:00Z',
    updated_at: '2026-01-10T14:30:00Z',
  },
  {
    id: '2',
    po_number: 'PO-2026-0002',
    vendor_id: '2',
    vendor_name: 'Reliance Industries',
    vendor_code: 'SUP-002',
    status: 'partial_received',
    approval_status: 'approved',
    order_date: '2026-01-08',
    expected_delivery: '2026-01-20',
    line_items: [
      { id: '1', item_code: 'CHM-001', item_name: 'Industrial Chemicals', quantity: 50, unit_price: 8500, tax_rate: 18, total: 501500 },
    ],
    subtotal: 425000,
    tax_amount: 76500,
    total_amount: 501500,
    received_amount: 250000,
    notes: '',
    created_at: '2026-01-08T09:00:00Z',
    updated_at: '2026-01-15T11:00:00Z',
  },
  {
    id: '3',
    po_number: 'PO-2026-0003',
    vendor_id: '3',
    vendor_name: 'Mahindra Components',
    vendor_code: 'SUP-003',
    status: 'pending_approval',
    approval_status: 'pending',
    order_date: '2026-01-15',
    expected_delivery: '2026-02-01',
    line_items: [
      { id: '1', item_code: 'AUT-001', item_name: 'Engine Parts', quantity: 25, unit_price: 15000, tax_rate: 18, total: 442500 },
      { id: '2', item_code: 'AUT-002', item_name: 'Brake Components', quantity: 100, unit_price: 3500, tax_rate: 18, total: 413000 },
    ],
    subtotal: 725000,
    tax_amount: 130500,
    total_amount: 855500,
    received_amount: 0,
    notes: 'Standard delivery',
    created_at: '2026-01-15T10:30:00Z',
    updated_at: '2026-01-15T10:30:00Z',
  },
  {
    id: '4',
    po_number: 'PO-2026-0004',
    vendor_id: '4',
    vendor_name: 'Jindal Steel',
    vendor_code: 'SUP-004',
    status: 'received',
    approval_status: 'approved',
    order_date: '2026-01-05',
    expected_delivery: '2026-01-12',
    line_items: [
      { id: '1', item_code: 'STL-003', item_name: 'Stainless Steel Sheets', quantity: 75, unit_price: 6500, tax_rate: 18, total: 575250 },
    ],
    subtotal: 487500,
    tax_amount: 87750,
    total_amount: 575250,
    received_amount: 575250,
    notes: '',
    created_at: '2026-01-05T08:00:00Z',
    updated_at: '2026-01-12T16:00:00Z',
  },
  {
    id: '5',
    po_number: 'PO-2026-0005',
    vendor_id: '5',
    vendor_name: 'Larsen & Toubro',
    vendor_code: 'SUP-005',
    status: 'draft',
    approval_status: 'pending',
    order_date: '2026-01-16',
    expected_delivery: '2026-02-15',
    line_items: [],
    subtotal: 0,
    tax_amount: 0,
    total_amount: 0,
    received_amount: 0,
    notes: 'Draft PO for machinery',
    created_at: '2026-01-16T09:00:00Z',
    updated_at: '2026-01-16T09:00:00Z',
  },
];

// Empty line item template
const emptyLineItem: Omit<PurchaseOrderLineItem, 'id'> = {
  item_code: '',
  item_name: '',
  quantity: 0,
  unit_price: 0,
  tax_rate: 18,
  total: 0,
};

export default function PurchaseOrdersPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [vendorFilter, setVendorFilter] = useState<string>('all');
  const [dateFrom, setDateFrom] = useState<string>('');
  const [dateTo, setDateTo] = useState<string>('');
  const [showFilters, setShowFilters] = useState(false);
  const { showToast } = useToast();

  // API hooks
  const { data: poData, isLoading, get: getPurchaseOrders } = useApi<{ data: PurchaseOrder[] }>();
  const { data: vendorsData, get: getVendors } = useApi<{ data: Vendor[] }>();
  const createApi = useApi<PurchaseOrder>();
  const deleteApi = useApi();

  // Local state
  const [localPurchaseOrders, setLocalPurchaseOrders] = useState<PurchaseOrder[]>(mockPurchaseOrders);
  const [vendors] = useState<Vendor[]>(mockVendors);

  // Dialog states
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [viewDialogOpen, setViewDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [selectedPO, setSelectedPO] = useState<PurchaseOrder | null>(null);
  const [isCreating, setIsCreating] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  // Form state for creating PO
  const [formData, setFormData] = useState({
    vendor_id: '',
    expected_delivery: '',
    notes: '',
    line_items: [] as Omit<PurchaseOrderLineItem, 'id'>[],
  });

  useEffect(() => {
    getPurchaseOrders('/supply-chain/purchase-orders');
    getVendors('/supply-chain/suppliers');
  }, [getPurchaseOrders, getVendors]);

  useEffect(() => {
    if (poData?.data) {
      setLocalPurchaseOrders(poData.data);
    }
  }, [poData]);

  const purchaseOrders = localPurchaseOrders;

  // Filter purchase orders
  const filteredPOs = purchaseOrders.filter((po) => {
    const matchesSearch =
      !searchQuery ||
      po.po_number.toLowerCase().includes(searchQuery.toLowerCase()) ||
      po.vendor_name.toLowerCase().includes(searchQuery.toLowerCase());

    const matchesStatus = statusFilter === 'all' || po.status === statusFilter;
    const matchesVendor = vendorFilter === 'all' || po.vendor_id === vendorFilter;

    const orderDate = new Date(po.order_date);
    const matchesDateFrom = !dateFrom || orderDate >= new Date(dateFrom);
    const matchesDateTo = !dateTo || orderDate <= new Date(dateTo);

    return matchesSearch && matchesStatus && matchesVendor && matchesDateFrom && matchesDateTo;
  });

  // Stats
  const stats = {
    total: purchaseOrders.length,
    pendingApproval: purchaseOrders.filter((po) => po.approval_status === 'pending').length,
    inProgress: purchaseOrders.filter((po) => ['approved', 'sent', 'partial_received'].includes(po.status)).length,
    completed: purchaseOrders.filter((po) => po.status === 'received').length,
    totalValue: purchaseOrders.reduce((sum, po) => sum + po.total_amount, 0),
  };

  // Add line item
  const addLineItem = () => {
    setFormData((prev) => ({
      ...prev,
      line_items: [...prev.line_items, { ...emptyLineItem }],
    }));
  };

  // Remove line item
  const removeLineItem = (index: number) => {
    setFormData((prev) => ({
      ...prev,
      line_items: prev.line_items.filter((_, i) => i !== index),
    }));
  };

  // Update line item
  const updateLineItem = (index: number, field: keyof PurchaseOrderLineItem, value: string | number) => {
    setFormData((prev) => {
      const newLineItems = [...prev.line_items];
      newLineItems[index] = { ...newLineItems[index], [field]: value };

      // Calculate total
      const qty = field === 'quantity' ? Number(value) : newLineItems[index].quantity;
      const price = field === 'unit_price' ? Number(value) : newLineItems[index].unit_price;
      const taxRate = field === 'tax_rate' ? Number(value) : newLineItems[index].tax_rate;
      newLineItems[index].total = qty * price * (1 + taxRate / 100);

      return { ...prev, line_items: newLineItems };
    });
  };

  // Calculate form totals
  const formSubtotal = formData.line_items.reduce((sum, item) => sum + item.quantity * item.unit_price, 0);
  const formTaxAmount = formData.line_items.reduce(
    (sum, item) => sum + item.quantity * item.unit_price * (item.tax_rate / 100),
    0
  );
  const formTotal = formSubtotal + formTaxAmount;

  // Handle create PO
  const handleCreatePO = async () => {
    if (!formData.vendor_id) {
      showToast('error', 'Please select a vendor');
      return;
    }
    if (formData.line_items.length === 0) {
      showToast('error', 'Please add at least one line item');
      return;
    }

    setIsCreating(true);
    try {
      const vendor = vendors.find((v) => v.id === formData.vendor_id);
      const newPO: PurchaseOrder = {
        id: String(Date.now()),
        po_number: `PO-2026-${String(purchaseOrders.length + 1).padStart(4, '0')}`,
        vendor_id: formData.vendor_id,
        vendor_name: vendor?.name || '',
        vendor_code: vendor?.code || '',
        status: 'draft',
        approval_status: 'pending',
        order_date: new Date().toISOString().split('T')[0],
        expected_delivery: formData.expected_delivery,
        line_items: formData.line_items.map((item, idx) => ({ ...item, id: String(idx + 1) })),
        subtotal: formSubtotal,
        tax_amount: formTaxAmount,
        total_amount: formTotal,
        received_amount: 0,
        notes: formData.notes,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };

      await createApi.post('/supply-chain/purchase-orders', newPO);
      setLocalPurchaseOrders([newPO, ...localPurchaseOrders]);
      setCreateDialogOpen(false);
      resetForm();
      showToast('success', 'Purchase order created successfully');
    } catch (error) {
      console.error('Failed to create PO:', error);
      showToast('error', 'Failed to create purchase order');
    } finally {
      setIsCreating(false);
    }
  };

  // Handle delete PO
  const handleDeletePO = async () => {
    if (!selectedPO) return;

    setIsDeleting(true);
    try {
      await deleteApi.delete(`/supply-chain/purchase-orders/${selectedPO.id}`);
      setLocalPurchaseOrders(localPurchaseOrders.filter((po) => po.id !== selectedPO.id));
      setDeleteDialogOpen(false);
      setSelectedPO(null);
      showToast('success', 'Purchase order deleted successfully');
    } catch (error) {
      console.error('Failed to delete PO:', error);
      showToast('error', 'Failed to delete purchase order');
    } finally {
      setIsDeleting(false);
    }
  };

  const resetForm = () => {
    setFormData({
      vendor_id: '',
      expected_delivery: '',
      notes: '',
      line_items: [],
    });
  };

  const openViewDialog = (po: PurchaseOrder) => {
    setSelectedPO(po);
    setViewDialogOpen(true);
  };

  const openDeleteDialog = (po: PurchaseOrder) => {
    setSelectedPO(po);
    setDeleteDialogOpen(true);
  };

  // Export POs to CSV
  const handleExport = () => {
    const headers = ['PO Number', 'Vendor', 'Order Date', 'Expected Delivery', 'Status', 'Approval Status', 'Total Amount', 'Received Amount'];
    const rows = filteredPOs.map(po => [
      po.po_number,
      po.vendor_name,
      po.order_date,
      po.expected_delivery,
      po.status,
      po.approval_status,
      po.total_amount.toString(),
      po.received_amount.toString()
    ]);
    const csv = [headers, ...rows].map(row => row.join(',')).join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'purchase_orders.csv';
    a.click();
    window.URL.revokeObjectURL(url);
  };

  // Edit PO dialog state
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [editFormData, setEditFormData] = useState<PurchaseOrder | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const editApi = useApi<PurchaseOrder>();

  const openEditDialog = (po: PurchaseOrder) => {
    setEditFormData({ ...po });
    setEditDialogOpen(true);
  };

  const handleSavePO = async () => {
    if (!editFormData) return;
    setIsEditing(true);
    try {
      await editApi.put(`/supply-chain/purchase-orders/${editFormData.id}`, editFormData);
      setLocalPurchaseOrders(localPurchaseOrders.map(po => po.id === editFormData.id ? editFormData : po));
      setEditDialogOpen(false);
      showToast('success', 'Purchase order updated successfully');
    } catch (error) {
      console.error('Failed to update PO:', error);
      showToast('error', 'Failed to update purchase order');
    } finally {
      setIsEditing(false);
    }
  };

  const clearFilters = () => {
    setStatusFilter('all');
    setVendorFilter('all');
    setDateFrom('');
    setDateTo('');
  };

  const activeFiltersCount = [
    statusFilter !== 'all',
    vendorFilter !== 'all',
    dateFrom,
    dateTo,
  ].filter(Boolean).length;

  return (
    <div className="space-y-6">
      <PageHeader
        title="Purchase Orders"
        description="Manage purchase orders, approvals, and vendor deliveries"
        breadcrumbs={[
          { label: 'Dashboard', href: '/' },
          { label: 'Supply Chain', href: '/supply-chain' },
          { label: 'Purchase Orders' },
        ]}
        actions={
          <div className="flex items-center gap-2">
            <Button variant="outline" onClick={handleExport}>
              <Download className="h-4 w-4 mr-2" />
              Export
            </Button>
            <Button onClick={() => setCreateDialogOpen(true)}>
              <Plus className="h-4 w-4 mr-2" />
              Create PO
            </Button>
          </div>
        }
      />

      {isLoading && (
        <Card className="p-8 flex items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <span className="ml-2">Loading purchase orders...</span>
        </Card>
      )}

      {/* Stats */}
      <div className="grid gap-4 md:grid-cols-5">
        <StatCard title="Total POs" value={stats.total} icon={FileText} description="All purchase orders" />
        <StatCard
          title="Pending Approval"
          value={stats.pendingApproval}
          icon={Clock}
          description="Awaiting approval"
          className="border-yellow-200 bg-yellow-50"
        />
        <StatCard
          title="In Progress"
          value={stats.inProgress}
          icon={Package}
          description="Approved & sent"
          className="border-blue-200 bg-blue-50"
        />
        <StatCard
          title="Completed"
          value={stats.completed}
          icon={CheckCircle}
          description="Fully received"
          className="border-green-200 bg-green-50"
        />
        <StatCard title="Total Value" value={formatCurrency(stats.totalValue)} icon={FileText} description="All PO value" />
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col gap-4">
            <div className="flex flex-col sm:flex-row gap-4">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search by PO number or vendor..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-9"
                />
              </div>
              <Button
                variant={showFilters ? 'secondary' : 'outline'}
                onClick={() => setShowFilters(!showFilters)}
              >
                <Filter className="h-4 w-4 mr-2" />
                Filters
                {activeFiltersCount > 0 && (
                  <Badge className="ml-2 bg-primary text-primary-foreground">{activeFiltersCount}</Badge>
                )}
              </Button>
            </div>

            {showFilters && (
              <div className="pt-4 border-t">
                <div className="grid gap-4 md:grid-cols-4">
                  <div>
                    <Label className="text-sm font-medium mb-1 block">Status</Label>
                    <Select value={statusFilter} onValueChange={setStatusFilter}>
                      <SelectTrigger>
                        <SelectValue placeholder="All Status" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">All Status</SelectItem>
                        <SelectItem value="draft">Draft</SelectItem>
                        <SelectItem value="pending_approval">Pending Approval</SelectItem>
                        <SelectItem value="approved">Approved</SelectItem>
                        <SelectItem value="sent">Sent</SelectItem>
                        <SelectItem value="partial_received">Partial Received</SelectItem>
                        <SelectItem value="received">Received</SelectItem>
                        <SelectItem value="cancelled">Cancelled</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label className="text-sm font-medium mb-1 block">Vendor</Label>
                    <Select value={vendorFilter} onValueChange={setVendorFilter}>
                      <SelectTrigger>
                        <SelectValue placeholder="All Vendors" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">All Vendors</SelectItem>
                        {vendors.map((vendor) => (
                          <SelectItem key={vendor.id} value={vendor.id}>
                            {vendor.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label className="text-sm font-medium mb-1 block">Date From</Label>
                    <Input type="date" value={dateFrom} onChange={(e) => setDateFrom(e.target.value)} />
                  </div>
                  <div>
                    <Label className="text-sm font-medium mb-1 block">Date To</Label>
                    <Input type="date" value={dateTo} onChange={(e) => setDateTo(e.target.value)} />
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

      {/* PO Table */}
      <Card>
        <CardHeader>
          <CardTitle>Purchase Orders ({filteredPOs.length})</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="border rounded-lg overflow-hidden">
            <table className="w-full">
              <thead className="bg-muted/50">
                <tr>
                  <th className="text-left p-4 font-medium">PO Number</th>
                  <th className="text-left p-4 font-medium">Vendor</th>
                  <th className="text-left p-4 font-medium">Order Date</th>
                  <th className="text-left p-4 font-medium">Expected Delivery</th>
                  <th className="text-right p-4 font-medium">Total Amount</th>
                  <th className="text-center p-4 font-medium">Status</th>
                  <th className="text-center p-4 font-medium">Approval</th>
                  <th className="text-center p-4 font-medium">Receipt</th>
                  <th className="text-right p-4 font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredPOs.map((po) => {
                  const receiptPercentage = po.total_amount > 0 ? (po.received_amount / po.total_amount) * 100 : 0;
                  return (
                    <tr key={po.id} className="border-t hover:bg-muted/30">
                      <td className="p-4 font-medium">{po.po_number}</td>
                      <td className="p-4">
                        <div>
                          <p className="font-medium">{po.vendor_name}</p>
                          <p className="text-xs text-muted-foreground">{po.vendor_code}</p>
                        </div>
                      </td>
                      <td className="p-4 text-muted-foreground">{formatDate(po.order_date)}</td>
                      <td className="p-4 text-muted-foreground">{formatDate(po.expected_delivery)}</td>
                      <td className="p-4 text-right font-medium">{formatCurrency(po.total_amount)}</td>
                      <td className="p-4 text-center">
                        <Badge className={statusColors[po.status]}>{po.status.replace(/_/g, ' ')}</Badge>
                      </td>
                      <td className="p-4 text-center">
                        <Badge className={approvalStatusColors[po.approval_status]}>{po.approval_status}</Badge>
                      </td>
                      <td className="p-4">
                        <div className="flex flex-col items-center">
                          <div className="w-20 bg-gray-200 rounded-full h-2 mb-1">
                            <div
                              className="bg-green-500 rounded-full h-2"
                              style={{ width: `${receiptPercentage}%` }}
                            />
                          </div>
                          <span className="text-xs text-muted-foreground">{receiptPercentage.toFixed(0)}%</span>
                        </div>
                      </td>
                      <td className="p-4 text-right">
                        <div className="flex justify-end gap-1">
                          <Button variant="ghost" size="icon" onClick={() => openViewDialog(po)}>
                            <Eye className="h-4 w-4" />
                          </Button>
                          <Button variant="ghost" size="icon" onClick={() => openEditDialog(po)}>
                            <Edit className="h-4 w-4" />
                          </Button>
                          {(po.status === 'draft' || po.status === 'cancelled') && (
                            <Button
                              variant="ghost"
                              size="icon"
                              className="text-red-600 hover:text-red-700 hover:bg-red-50"
                              onClick={() => openDeleteDialog(po)}
                            >
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          )}
                        </div>
                      </td>
                    </tr>
                  );
                })}
                {filteredPOs.length === 0 && (
                  <tr>
                    <td colSpan={9} className="p-8 text-center text-muted-foreground">
                      No purchase orders found
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Create PO Dialog */}
      <Dialog open={createDialogOpen} onOpenChange={setCreateDialogOpen}>
        <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Create Purchase Order</DialogTitle>
            <DialogDescription>Create a new purchase order with line items</DialogDescription>
          </DialogHeader>

          <div className="space-y-6 py-4">
            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <Label htmlFor="vendor">Vendor *</Label>
                <Select value={formData.vendor_id} onValueChange={(value) => setFormData({ ...formData, vendor_id: value })}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select vendor" />
                  </SelectTrigger>
                  <SelectContent>
                    {vendors.map((vendor) => (
                      <SelectItem key={vendor.id} value={vendor.id}>
                        {vendor.name} ({vendor.code})
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label htmlFor="expected_delivery">Expected Delivery *</Label>
                <Input
                  id="expected_delivery"
                  type="date"
                  value={formData.expected_delivery}
                  onChange={(e) => setFormData({ ...formData, expected_delivery: e.target.value })}
                />
              </div>
            </div>

            <div>
              <Label htmlFor="notes">Notes</Label>
              <Textarea
                id="notes"
                placeholder="Additional notes..."
                value={formData.notes}
                onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
              />
            </div>

            {/* Line Items */}
            <div>
              <div className="flex items-center justify-between mb-4">
                <Label>Line Items</Label>
                <Button type="button" variant="outline" size="sm" onClick={addLineItem}>
                  <Plus className="h-4 w-4 mr-1" />
                  Add Item
                </Button>
              </div>

              {formData.line_items.length === 0 ? (
                <div className="text-center py-8 border rounded-lg border-dashed">
                  <Package className="h-12 w-12 mx-auto text-muted-foreground mb-2" />
                  <p className="text-muted-foreground">No items added yet</p>
                  <Button type="button" variant="outline" size="sm" className="mt-2" onClick={addLineItem}>
                    Add First Item
                  </Button>
                </div>
              ) : (
                <div className="border rounded-lg overflow-hidden">
                  <table className="w-full">
                    <thead className="bg-muted/50">
                      <tr>
                        <th className="text-left p-2 font-medium text-sm">Item Code</th>
                        <th className="text-left p-2 font-medium text-sm">Item Name</th>
                        <th className="text-right p-2 font-medium text-sm">Qty</th>
                        <th className="text-right p-2 font-medium text-sm">Unit Price</th>
                        <th className="text-right p-2 font-medium text-sm">Tax %</th>
                        <th className="text-right p-2 font-medium text-sm">Total</th>
                        <th className="w-10"></th>
                      </tr>
                    </thead>
                    <tbody>
                      {formData.line_items.map((item, index) => (
                        <tr key={index} className="border-t">
                          <td className="p-2">
                            <Input
                              value={item.item_code}
                              onChange={(e) => updateLineItem(index, 'item_code', e.target.value)}
                              placeholder="Code"
                              className="h-8"
                            />
                          </td>
                          <td className="p-2">
                            <Input
                              value={item.item_name}
                              onChange={(e) => updateLineItem(index, 'item_name', e.target.value)}
                              placeholder="Item name"
                              className="h-8"
                            />
                          </td>
                          <td className="p-2">
                            <Input
                              type="number"
                              value={item.quantity || ''}
                              onChange={(e) => updateLineItem(index, 'quantity', Number(e.target.value))}
                              placeholder="0"
                              className="h-8 w-20 text-right"
                            />
                          </td>
                          <td className="p-2">
                            <Input
                              type="number"
                              value={item.unit_price || ''}
                              onChange={(e) => updateLineItem(index, 'unit_price', Number(e.target.value))}
                              placeholder="0"
                              className="h-8 w-24 text-right"
                            />
                          </td>
                          <td className="p-2">
                            <Input
                              type="number"
                              value={item.tax_rate || ''}
                              onChange={(e) => updateLineItem(index, 'tax_rate', Number(e.target.value))}
                              placeholder="18"
                              className="h-8 w-16 text-right"
                            />
                          </td>
                          <td className="p-2 text-right font-medium">{formatCurrency(item.total)}</td>
                          <td className="p-2">
                            <Button
                              type="button"
                              variant="ghost"
                              size="icon"
                              className="h-8 w-8 text-red-600"
                              onClick={() => removeLineItem(index)}
                            >
                              <X className="h-4 w-4" />
                            </Button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}

              {formData.line_items.length > 0 && (
                <div className="mt-4 flex justify-end">
                  <div className="w-64 space-y-2">
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Subtotal:</span>
                      <span>{formatCurrency(formSubtotal)}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Tax:</span>
                      <span>{formatCurrency(formTaxAmount)}</span>
                    </div>
                    <div className="flex justify-between font-medium border-t pt-2">
                      <span>Total:</span>
                      <span>{formatCurrency(formTotal)}</span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setCreateDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleCreatePO} disabled={isCreating}>
              {isCreating ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Creating...
                </>
              ) : (
                'Create Purchase Order'
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* View PO Dialog */}
      <Dialog open={viewDialogOpen} onOpenChange={setViewDialogOpen}>
        <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Purchase Order Details</DialogTitle>
            <DialogDescription>{selectedPO?.po_number}</DialogDescription>
          </DialogHeader>

          {selectedPO && (
            <div className="space-y-6 py-4">
              <div className="grid gap-4 md:grid-cols-2">
                <div>
                  <Label className="text-muted-foreground">Vendor</Label>
                  <p className="font-medium">{selectedPO.vendor_name}</p>
                  <p className="text-sm text-muted-foreground">{selectedPO.vendor_code}</p>
                </div>
                <div>
                  <Label className="text-muted-foreground">Status</Label>
                  <div className="flex gap-2 mt-1">
                    <Badge className={statusColors[selectedPO.status]}>{selectedPO.status.replace(/_/g, ' ')}</Badge>
                    <Badge className={approvalStatusColors[selectedPO.approval_status]}>
                      {selectedPO.approval_status}
                    </Badge>
                  </div>
                </div>
                <div>
                  <Label className="text-muted-foreground">Order Date</Label>
                  <p className="font-medium">{formatDate(selectedPO.order_date, { format: 'long' })}</p>
                </div>
                <div>
                  <Label className="text-muted-foreground">Expected Delivery</Label>
                  <p className="font-medium">{formatDate(selectedPO.expected_delivery, { format: 'long' })}</p>
                </div>
              </div>

              {selectedPO.notes && (
                <div>
                  <Label className="text-muted-foreground">Notes</Label>
                  <p>{selectedPO.notes}</p>
                </div>
              )}

              <div>
                <Label className="text-muted-foreground mb-2 block">Line Items</Label>
                <div className="border rounded-lg overflow-hidden">
                  <table className="w-full">
                    <thead className="bg-muted/50">
                      <tr>
                        <th className="text-left p-3 font-medium">Item</th>
                        <th className="text-right p-3 font-medium">Qty</th>
                        <th className="text-right p-3 font-medium">Unit Price</th>
                        <th className="text-right p-3 font-medium">Tax</th>
                        <th className="text-right p-3 font-medium">Total</th>
                      </tr>
                    </thead>
                    <tbody>
                      {selectedPO.line_items.map((item) => (
                        <tr key={item.id} className="border-t">
                          <td className="p-3">
                            <p className="font-medium">{item.item_name}</p>
                            <p className="text-xs text-muted-foreground">{item.item_code}</p>
                          </td>
                          <td className="p-3 text-right">{item.quantity}</td>
                          <td className="p-3 text-right">{formatCurrency(item.unit_price)}</td>
                          <td className="p-3 text-right">{item.tax_rate}%</td>
                          <td className="p-3 text-right font-medium">{formatCurrency(item.total)}</td>
                        </tr>
                      ))}
                    </tbody>
                    <tfoot className="bg-muted/30">
                      <tr className="border-t">
                        <td colSpan={4} className="p-3 text-right font-medium">
                          Subtotal:
                        </td>
                        <td className="p-3 text-right">{formatCurrency(selectedPO.subtotal)}</td>
                      </tr>
                      <tr>
                        <td colSpan={4} className="p-3 text-right font-medium">
                          Tax:
                        </td>
                        <td className="p-3 text-right">{formatCurrency(selectedPO.tax_amount)}</td>
                      </tr>
                      <tr className="border-t">
                        <td colSpan={4} className="p-3 text-right font-bold">
                          Total:
                        </td>
                        <td className="p-3 text-right font-bold">{formatCurrency(selectedPO.total_amount)}</td>
                      </tr>
                    </tfoot>
                  </table>
                </div>
              </div>

              <div>
                <Label className="text-muted-foreground mb-2 block">Receipt Progress</Label>
                <div className="flex items-center gap-4">
                  <div className="flex-1 bg-gray-200 rounded-full h-3">
                    <div
                      className="bg-green-500 rounded-full h-3"
                      style={{ width: `${(selectedPO.received_amount / selectedPO.total_amount) * 100}%` }}
                    />
                  </div>
                  <span className="text-sm font-medium">
                    {formatCurrency(selectedPO.received_amount)} / {formatCurrency(selectedPO.total_amount)}
                  </span>
                </div>
              </div>
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
              Delete Purchase Order
            </AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete <strong>{selectedPO?.po_number}</strong>? This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={isDeleting}>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDeletePO}
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

      {/* Edit PO Dialog */}
      <Dialog open={editDialogOpen} onOpenChange={setEditDialogOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Edit Purchase Order</DialogTitle>
            <DialogDescription>{editFormData?.po_number}</DialogDescription>
          </DialogHeader>
          {editFormData && (
            <div className="space-y-4 py-4">
              <div className="grid gap-4 md:grid-cols-2">
                <div>
                  <Label>Vendor</Label>
                  <Select
                    value={editFormData.vendor_id}
                    onValueChange={(value) => {
                      const vendor = vendors.find(v => v.id === value);
                      setEditFormData({
                        ...editFormData,
                        vendor_id: value,
                        vendor_name: vendor?.name || '',
                        vendor_code: vendor?.code || ''
                      });
                    }}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {vendors.map((vendor) => (
                        <SelectItem key={vendor.id} value={vendor.id}>
                          {vendor.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label>Expected Delivery</Label>
                  <Input
                    type="date"
                    value={editFormData.expected_delivery}
                    onChange={(e) => setEditFormData({ ...editFormData, expected_delivery: e.target.value })}
                  />
                </div>
              </div>
              <div className="grid gap-4 md:grid-cols-2">
                <div>
                  <Label>Status</Label>
                  <Select
                    value={editFormData.status}
                    onValueChange={(value: PurchaseOrder['status']) => setEditFormData({ ...editFormData, status: value })}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="draft">Draft</SelectItem>
                      <SelectItem value="pending_approval">Pending Approval</SelectItem>
                      <SelectItem value="approved">Approved</SelectItem>
                      <SelectItem value="sent">Sent</SelectItem>
                      <SelectItem value="partial_received">Partial Received</SelectItem>
                      <SelectItem value="received">Received</SelectItem>
                      <SelectItem value="cancelled">Cancelled</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <Label>Approval Status</Label>
                  <Select
                    value={editFormData.approval_status}
                    onValueChange={(value: PurchaseOrder['approval_status']) => setEditFormData({ ...editFormData, approval_status: value })}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="pending">Pending</SelectItem>
                      <SelectItem value="approved">Approved</SelectItem>
                      <SelectItem value="rejected">Rejected</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <div>
                <Label>Notes</Label>
                <Textarea
                  value={editFormData.notes}
                  onChange={(e) => setEditFormData({ ...editFormData, notes: e.target.value })}
                />
              </div>
            </div>
          )}
          <DialogFooter>
            <Button variant="outline" onClick={() => setEditDialogOpen(false)}>Cancel</Button>
            <Button onClick={handleSavePO} disabled={isEditing}>
              {isEditing ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Saving...
                </>
              ) : (
                'Save Changes'
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
