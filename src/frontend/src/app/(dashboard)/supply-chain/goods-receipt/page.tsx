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
  Package,
  CheckCircle,
  Clock,
  XCircle,
  Download,
  ClipboardCheck,
  FileText,
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
interface GRNLineItem {
  id: string;
  po_line_id: string;
  item_code: string;
  item_name: string;
  ordered_qty: number;
  received_qty: number;
  accepted_qty: number;
  rejected_qty: number;
  unit_price: number;
  inspection_status: 'pending' | 'passed' | 'failed' | 'partial';
  rejection_reason?: string;
}

interface GoodsReceipt {
  id: string;
  grn_number: string;
  po_id: string;
  po_number: string;
  vendor_id: string;
  vendor_name: string;
  vendor_code: string;
  status: 'draft' | 'pending_inspection' | 'inspected' | 'partial_accepted' | 'accepted' | 'rejected';
  receipt_date: string;
  line_items: GRNLineItem[];
  total_ordered: number;
  total_received: number;
  total_accepted: number;
  total_rejected: number;
  total_value: number;
  accepted_value: number;
  notes: string;
  inspector_name?: string;
  inspection_date?: string;
  created_at: string;
  updated_at: string;
}

interface PurchaseOrder {
  id: string;
  po_number: string;
  vendor_id: string;
  vendor_name: string;
  vendor_code: string;
  status: string;
  line_items: {
    id: string;
    item_code: string;
    item_name: string;
    quantity: number;
    received_qty: number;
    unit_price: number;
  }[];
}

// Status colors mapping
const statusColors: Record<string, string> = {
  draft: 'bg-gray-100 text-gray-800',
  pending_inspection: 'bg-yellow-100 text-yellow-800',
  inspected: 'bg-blue-100 text-blue-800',
  partial_accepted: 'bg-orange-100 text-orange-800',
  accepted: 'bg-green-100 text-green-800',
  rejected: 'bg-red-100 text-red-800',
};

const inspectionStatusColors: Record<string, string> = {
  pending: 'bg-yellow-100 text-yellow-800',
  passed: 'bg-green-100 text-green-800',
  failed: 'bg-red-100 text-red-800',
  partial: 'bg-orange-100 text-orange-800',
};

// Mock data
const mockPurchaseOrders: PurchaseOrder[] = [
  {
    id: '1',
    po_number: 'PO-2026-0001',
    vendor_id: '1',
    vendor_name: 'Tata Steel Ltd',
    vendor_code: 'SUP-001',
    status: 'approved',
    line_items: [
      { id: '1', item_code: 'STL-001', item_name: 'Steel Plates 10mm', quantity: 100, received_qty: 50, unit_price: 4500 },
      { id: '2', item_code: 'STL-002', item_name: 'Steel Rods 8mm', quantity: 200, received_qty: 100, unit_price: 2200 },
    ],
  },
  {
    id: '2',
    po_number: 'PO-2026-0002',
    vendor_id: '2',
    vendor_name: 'Reliance Industries',
    vendor_code: 'SUP-002',
    status: 'sent',
    line_items: [
      { id: '1', item_code: 'CHM-001', item_name: 'Industrial Chemicals', quantity: 50, received_qty: 25, unit_price: 8500 },
    ],
  },
  {
    id: '3',
    po_number: 'PO-2026-0003',
    vendor_id: '3',
    vendor_name: 'Mahindra Components',
    vendor_code: 'SUP-003',
    status: 'approved',
    line_items: [
      { id: '1', item_code: 'AUT-001', item_name: 'Engine Parts', quantity: 25, received_qty: 0, unit_price: 15000 },
      { id: '2', item_code: 'AUT-002', item_name: 'Brake Components', quantity: 100, received_qty: 0, unit_price: 3500 },
    ],
  },
];

const mockGoodsReceipts: GoodsReceipt[] = [
  {
    id: '1',
    grn_number: 'GRN-2026-0001',
    po_id: '1',
    po_number: 'PO-2026-0001',
    vendor_id: '1',
    vendor_name: 'Tata Steel Ltd',
    vendor_code: 'SUP-001',
    status: 'accepted',
    receipt_date: '2026-01-12',
    line_items: [
      {
        id: '1',
        po_line_id: '1',
        item_code: 'STL-001',
        item_name: 'Steel Plates 10mm',
        ordered_qty: 100,
        received_qty: 50,
        accepted_qty: 48,
        rejected_qty: 2,
        unit_price: 4500,
        inspection_status: 'passed',
      },
      {
        id: '2',
        po_line_id: '2',
        item_code: 'STL-002',
        item_name: 'Steel Rods 8mm',
        ordered_qty: 200,
        received_qty: 100,
        accepted_qty: 100,
        rejected_qty: 0,
        unit_price: 2200,
        inspection_status: 'passed',
      },
    ],
    total_ordered: 300,
    total_received: 150,
    total_accepted: 148,
    total_rejected: 2,
    total_value: 445000,
    accepted_value: 436000,
    notes: 'Minor damage on 2 plates, rejected',
    inspector_name: 'Rajesh Kumar',
    inspection_date: '2026-01-12',
    created_at: '2026-01-12T10:00:00Z',
    updated_at: '2026-01-12T14:30:00Z',
  },
  {
    id: '2',
    grn_number: 'GRN-2026-0002',
    po_id: '2',
    po_number: 'PO-2026-0002',
    vendor_id: '2',
    vendor_name: 'Reliance Industries',
    vendor_code: 'SUP-002',
    status: 'pending_inspection',
    receipt_date: '2026-01-15',
    line_items: [
      {
        id: '1',
        po_line_id: '1',
        item_code: 'CHM-001',
        item_name: 'Industrial Chemicals',
        ordered_qty: 50,
        received_qty: 25,
        accepted_qty: 0,
        rejected_qty: 0,
        unit_price: 8500,
        inspection_status: 'pending',
      },
    ],
    total_ordered: 50,
    total_received: 25,
    total_accepted: 0,
    total_rejected: 0,
    total_value: 212500,
    accepted_value: 0,
    notes: 'Awaiting quality inspection',
    created_at: '2026-01-15T11:00:00Z',
    updated_at: '2026-01-15T11:00:00Z',
  },
  {
    id: '3',
    grn_number: 'GRN-2026-0003',
    po_id: '1',
    po_number: 'PO-2026-0001',
    vendor_id: '1',
    vendor_name: 'Tata Steel Ltd',
    vendor_code: 'SUP-001',
    status: 'partial_accepted',
    receipt_date: '2026-01-14',
    line_items: [
      {
        id: '1',
        po_line_id: '1',
        item_code: 'STL-001',
        item_name: 'Steel Plates 10mm',
        ordered_qty: 50,
        received_qty: 30,
        accepted_qty: 25,
        rejected_qty: 5,
        unit_price: 4500,
        inspection_status: 'partial',
        rejection_reason: 'Surface defects',
      },
    ],
    total_ordered: 50,
    total_received: 30,
    total_accepted: 25,
    total_rejected: 5,
    total_value: 135000,
    accepted_value: 112500,
    notes: 'Partial acceptance due to quality issues',
    inspector_name: 'Amit Sharma',
    inspection_date: '2026-01-14',
    created_at: '2026-01-14T09:00:00Z',
    updated_at: '2026-01-14T15:00:00Z',
  },
];

export default function GoodsReceiptPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [inspectionFilter, setInspectionFilter] = useState<string>('all');
  const [dateFrom, setDateFrom] = useState<string>('');
  const [dateTo, setDateTo] = useState<string>('');
  const [showFilters, setShowFilters] = useState(false);
  const { showToast } = useToast();

  // API hooks
  const { data: grnData, isLoading, get: getGRNs } = useApi<{ data: GoodsReceipt[] }>();
  const { data: poData, get: getPOs } = useApi<{ data: PurchaseOrder[] }>();
  const createApi = useApi<GoodsReceipt>();
  const deleteApi = useApi();

  // Local state
  const [localGRNs, setLocalGRNs] = useState<GoodsReceipt[]>(mockGoodsReceipts);
  const [purchaseOrders] = useState<PurchaseOrder[]>(mockPurchaseOrders);

  // Dialog states
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [viewDialogOpen, setViewDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [selectedGRN, setSelectedGRN] = useState<GoodsReceipt | null>(null);
  const [isCreating, setIsCreating] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  // Form state for creating GRN
  const [formData, setFormData] = useState({
    po_id: '',
    notes: '',
    line_items: [] as {
      po_line_id: string;
      item_code: string;
      item_name: string;
      ordered_qty: number;
      received_qty: number;
      unit_price: number;
    }[],
  });

  useEffect(() => {
    getGRNs('/supply-chain/goods-receipt');
    getPOs('/supply-chain/purchase-orders?status=approved,sent,partial_received');
  }, [getGRNs, getPOs]);

  useEffect(() => {
    if (grnData?.data) {
      setLocalGRNs(grnData.data);
    }
  }, [grnData]);

  const goodsReceipts = localGRNs;

  // Filter GRNs
  const filteredGRNs = goodsReceipts.filter((grn) => {
    const matchesSearch =
      !searchQuery ||
      grn.grn_number.toLowerCase().includes(searchQuery.toLowerCase()) ||
      grn.po_number.toLowerCase().includes(searchQuery.toLowerCase()) ||
      grn.vendor_name.toLowerCase().includes(searchQuery.toLowerCase());

    const matchesStatus = statusFilter === 'all' || grn.status === statusFilter;

    const matchesInspection =
      inspectionFilter === 'all' ||
      grn.line_items.some((item) => item.inspection_status === inspectionFilter);

    const receiptDate = new Date(grn.receipt_date);
    const matchesDateFrom = !dateFrom || receiptDate >= new Date(dateFrom);
    const matchesDateTo = !dateTo || receiptDate <= new Date(dateTo);

    return matchesSearch && matchesStatus && matchesInspection && matchesDateFrom && matchesDateTo;
  });

  // Stats
  const stats = {
    total: goodsReceipts.length,
    pendingInspection: goodsReceipts.filter((grn) => grn.status === 'pending_inspection').length,
    accepted: goodsReceipts.filter((grn) => grn.status === 'accepted').length,
    totalValue: goodsReceipts.reduce((sum, grn) => sum + grn.total_value, 0),
    acceptedValue: goodsReceipts.reduce((sum, grn) => sum + grn.accepted_value, 0),
  };

  // Handle PO selection
  const handlePOSelect = (poId: string) => {
    const po = purchaseOrders.find((p) => p.id === poId);
    if (po) {
      setFormData({
        po_id: poId,
        notes: '',
        line_items: po.line_items
          .filter((item) => item.quantity > item.received_qty)
          .map((item) => ({
            po_line_id: item.id,
            item_code: item.item_code,
            item_name: item.item_name,
            ordered_qty: item.quantity - item.received_qty,
            received_qty: 0,
            unit_price: item.unit_price,
          })),
      });
    }
  };

  // Update line item received qty
  const updateReceivedQty = (index: number, qty: number) => {
    setFormData((prev) => {
      const newLineItems = [...prev.line_items];
      newLineItems[index] = { ...newLineItems[index], received_qty: Math.min(qty, newLineItems[index].ordered_qty) };
      return { ...prev, line_items: newLineItems };
    });
  };

  // Calculate form totals
  const formTotalReceived = formData.line_items.reduce((sum, item) => sum + item.received_qty, 0);
  const formTotalValue = formData.line_items.reduce((sum, item) => sum + item.received_qty * item.unit_price, 0);

  // Handle create GRN
  const handleCreateGRN = async () => {
    if (!formData.po_id) {
      showToast('error', 'Please select a purchase order');
      return;
    }
    if (formTotalReceived === 0) {
      showToast('error', 'Please enter received quantities');
      return;
    }

    setIsCreating(true);
    try {
      const po = purchaseOrders.find((p) => p.id === formData.po_id);
      const newGRN: GoodsReceipt = {
        id: String(Date.now()),
        grn_number: `GRN-2026-${String(goodsReceipts.length + 1).padStart(4, '0')}`,
        po_id: formData.po_id,
        po_number: po?.po_number || '',
        vendor_id: po?.vendor_id || '',
        vendor_name: po?.vendor_name || '',
        vendor_code: po?.vendor_code || '',
        status: 'pending_inspection',
        receipt_date: new Date().toISOString().split('T')[0],
        line_items: formData.line_items
          .filter((item) => item.received_qty > 0)
          .map((item, idx) => ({
            id: String(idx + 1),
            po_line_id: item.po_line_id,
            item_code: item.item_code,
            item_name: item.item_name,
            ordered_qty: item.ordered_qty,
            received_qty: item.received_qty,
            accepted_qty: 0,
            rejected_qty: 0,
            unit_price: item.unit_price,
            inspection_status: 'pending' as const,
          })),
        total_ordered: formData.line_items.reduce((sum, item) => sum + item.ordered_qty, 0),
        total_received: formTotalReceived,
        total_accepted: 0,
        total_rejected: 0,
        total_value: formTotalValue,
        accepted_value: 0,
        notes: formData.notes,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };

      await createApi.post('/supply-chain/goods-receipt', newGRN);
      setLocalGRNs([newGRN, ...localGRNs]);
      setCreateDialogOpen(false);
      resetForm();
      showToast('success', 'Goods receipt created successfully');
    } catch (error) {
      showToast('error', 'Failed to create goods receipt');
    } finally {
      setIsCreating(false);
    }
  };

  // Handle delete GRN
  const handleDeleteGRN = async () => {
    if (!selectedGRN) return;

    setIsDeleting(true);
    try {
      await deleteApi.delete(`/supply-chain/goods-receipt/${selectedGRN.id}`);
      setLocalGRNs(localGRNs.filter((grn) => grn.id !== selectedGRN.id));
      setDeleteDialogOpen(false);
      setSelectedGRN(null);
      showToast('success', 'Goods receipt deleted successfully');
    } catch (error) {
      showToast('error', 'Failed to delete goods receipt');
    } finally {
      setIsDeleting(false);
    }
  };

  const resetForm = () => {
    setFormData({
      po_id: '',
      notes: '',
      line_items: [],
    });
  };

  const openViewDialog = (grn: GoodsReceipt) => {
    setSelectedGRN(grn);
    setViewDialogOpen(true);
  };

  const openDeleteDialog = (grn: GoodsReceipt) => {
    setSelectedGRN(grn);
    setDeleteDialogOpen(true);
  };

  const clearFilters = () => {
    setStatusFilter('all');
    setInspectionFilter('all');
    setDateFrom('');
    setDateTo('');
  };

  const activeFiltersCount = [
    statusFilter !== 'all',
    inspectionFilter !== 'all',
    dateFrom,
    dateTo,
  ].filter(Boolean).length;

  // Get available POs for GRN creation (those with pending items)
  const availablePOs = purchaseOrders.filter((po) =>
    po.line_items.some((item) => item.quantity > item.received_qty)
  );

  return (
    <div className="space-y-6">
      <PageHeader
        title="Goods Receipt"
        description="Manage goods receipt notes, inspections, and quality checks"
        breadcrumbs={[
          { label: 'Dashboard', href: '/' },
          { label: 'Supply Chain', href: '/supply-chain' },
          { label: 'Goods Receipt' },
        ]}
        actions={
          <div className="flex items-center gap-2">
            <Button variant="outline">
              <Download className="h-4 w-4 mr-2" />
              Export
            </Button>
            <Button onClick={() => setCreateDialogOpen(true)}>
              <Plus className="h-4 w-4 mr-2" />
              Create GRN
            </Button>
          </div>
        }
      />

      {isLoading && (
        <Card className="p-8 flex items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <span className="ml-2">Loading goods receipts...</span>
        </Card>
      )}

      {/* Stats */}
      <div className="grid gap-4 md:grid-cols-5">
        <StatCard title="Total GRNs" value={stats.total} icon={FileText} description="All receipts" />
        <StatCard
          title="Pending Inspection"
          value={stats.pendingInspection}
          icon={Clock}
          description="Awaiting QC"
          className="border-yellow-200 bg-yellow-50"
        />
        <StatCard
          title="Accepted"
          value={stats.accepted}
          icon={CheckCircle}
          description="Quality passed"
          className="border-green-200 bg-green-50"
        />
        <StatCard title="Total Value" value={formatCurrency(stats.totalValue)} icon={Package} description="Received value" />
        <StatCard
          title="Accepted Value"
          value={formatCurrency(stats.acceptedValue)}
          icon={ClipboardCheck}
          description="QC passed value"
          className="border-blue-200 bg-blue-50"
        />
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col gap-4">
            <div className="flex flex-col sm:flex-row gap-4">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search by GRN number, PO number or vendor..."
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
                        <SelectItem value="pending_inspection">Pending Inspection</SelectItem>
                        <SelectItem value="inspected">Inspected</SelectItem>
                        <SelectItem value="partial_accepted">Partial Accepted</SelectItem>
                        <SelectItem value="accepted">Accepted</SelectItem>
                        <SelectItem value="rejected">Rejected</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label className="text-sm font-medium mb-1 block">Inspection Status</Label>
                    <Select value={inspectionFilter} onValueChange={setInspectionFilter}>
                      <SelectTrigger>
                        <SelectValue placeholder="All Inspection" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">All Inspection</SelectItem>
                        <SelectItem value="pending">Pending</SelectItem>
                        <SelectItem value="passed">Passed</SelectItem>
                        <SelectItem value="failed">Failed</SelectItem>
                        <SelectItem value="partial">Partial</SelectItem>
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

      {/* GRN Table */}
      <Card>
        <CardHeader>
          <CardTitle>Goods Receipt Notes ({filteredGRNs.length})</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="border rounded-lg overflow-hidden">
            <table className="w-full">
              <thead className="bg-muted/50">
                <tr>
                  <th className="text-left p-4 font-medium">GRN Number</th>
                  <th className="text-left p-4 font-medium">PO Number</th>
                  <th className="text-left p-4 font-medium">Vendor</th>
                  <th className="text-left p-4 font-medium">Receipt Date</th>
                  <th className="text-center p-4 font-medium">Received</th>
                  <th className="text-center p-4 font-medium">Accepted</th>
                  <th className="text-right p-4 font-medium">Value</th>
                  <th className="text-center p-4 font-medium">Status</th>
                  <th className="text-center p-4 font-medium">Inspection</th>
                  <th className="text-right p-4 font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredGRNs.map((grn) => {
                  const overallInspection = grn.line_items.every((item) => item.inspection_status === 'passed')
                    ? 'passed'
                    : grn.line_items.every((item) => item.inspection_status === 'failed')
                    ? 'failed'
                    : grn.line_items.some((item) => item.inspection_status === 'pending')
                    ? 'pending'
                    : 'partial';

                  return (
                    <tr key={grn.id} className="border-t hover:bg-muted/30">
                      <td className="p-4 font-medium">{grn.grn_number}</td>
                      <td className="p-4 text-muted-foreground">{grn.po_number}</td>
                      <td className="p-4">
                        <div>
                          <p className="font-medium">{grn.vendor_name}</p>
                          <p className="text-xs text-muted-foreground">{grn.vendor_code}</p>
                        </div>
                      </td>
                      <td className="p-4 text-muted-foreground">{formatDate(grn.receipt_date)}</td>
                      <td className="p-4 text-center">{grn.total_received}</td>
                      <td className="p-4 text-center">
                        <span className={grn.total_accepted > 0 ? 'text-green-600' : ''}>{grn.total_accepted}</span>
                        {grn.total_rejected > 0 && (
                          <span className="text-red-600 ml-1">({grn.total_rejected} rejected)</span>
                        )}
                      </td>
                      <td className="p-4 text-right font-medium">{formatCurrency(grn.total_value)}</td>
                      <td className="p-4 text-center">
                        <Badge className={statusColors[grn.status]}>{grn.status.replace(/_/g, ' ')}</Badge>
                      </td>
                      <td className="p-4 text-center">
                        <Badge className={inspectionStatusColors[overallInspection]}>{overallInspection}</Badge>
                      </td>
                      <td className="p-4 text-right">
                        <div className="flex justify-end gap-1">
                          <Button variant="ghost" size="icon" onClick={() => openViewDialog(grn)}>
                            <Eye className="h-4 w-4" />
                          </Button>
                          <Button variant="ghost" size="icon">
                            <Edit className="h-4 w-4" />
                          </Button>
                          {grn.status === 'draft' && (
                            <Button
                              variant="ghost"
                              size="icon"
                              className="text-red-600 hover:text-red-700 hover:bg-red-50"
                              onClick={() => openDeleteDialog(grn)}
                            >
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          )}
                        </div>
                      </td>
                    </tr>
                  );
                })}
                {filteredGRNs.length === 0 && (
                  <tr>
                    <td colSpan={10} className="p-8 text-center text-muted-foreground">
                      No goods receipts found
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* Create GRN Dialog */}
      <Dialog open={createDialogOpen} onOpenChange={setCreateDialogOpen}>
        <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Create Goods Receipt Note</DialogTitle>
            <DialogDescription>Record receipt of goods against a purchase order</DialogDescription>
          </DialogHeader>

          <div className="space-y-6 py-4">
            <div>
              <Label htmlFor="po">Select Purchase Order *</Label>
              <Select value={formData.po_id} onValueChange={handlePOSelect}>
                <SelectTrigger>
                  <SelectValue placeholder="Select a purchase order" />
                </SelectTrigger>
                <SelectContent>
                  {availablePOs.length === 0 ? (
                    <SelectItem value="" disabled>
                      No pending purchase orders
                    </SelectItem>
                  ) : (
                    availablePOs.map((po) => (
                      <SelectItem key={po.id} value={po.id}>
                        {po.po_number} - {po.vendor_name}
                      </SelectItem>
                    ))
                  )}
                </SelectContent>
              </Select>
            </div>

            {formData.po_id && (
              <>
                <div>
                  <Label htmlFor="notes">Notes</Label>
                  <Textarea
                    id="notes"
                    placeholder="Additional notes about this receipt..."
                    value={formData.notes}
                    onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                  />
                </div>

                {/* Line Items */}
                <div>
                  <Label className="mb-4 block">Received Items</Label>

                  {formData.line_items.length === 0 ? (
                    <div className="text-center py-8 border rounded-lg border-dashed">
                      <Package className="h-12 w-12 mx-auto text-muted-foreground mb-2" />
                      <p className="text-muted-foreground">All items have been received</p>
                    </div>
                  ) : (
                    <div className="border rounded-lg overflow-hidden">
                      <table className="w-full">
                        <thead className="bg-muted/50">
                          <tr>
                            <th className="text-left p-3 font-medium">Item</th>
                            <th className="text-right p-3 font-medium">Pending Qty</th>
                            <th className="text-right p-3 font-medium">Unit Price</th>
                            <th className="text-right p-3 font-medium">Received Qty</th>
                            <th className="text-right p-3 font-medium">Value</th>
                          </tr>
                        </thead>
                        <tbody>
                          {formData.line_items.map((item, index) => (
                            <tr key={index} className="border-t">
                              <td className="p-3">
                                <p className="font-medium">{item.item_name}</p>
                                <p className="text-xs text-muted-foreground">{item.item_code}</p>
                              </td>
                              <td className="p-3 text-right">{item.ordered_qty}</td>
                              <td className="p-3 text-right">{formatCurrency(item.unit_price)}</td>
                              <td className="p-3 text-right">
                                <Input
                                  type="number"
                                  min={0}
                                  max={item.ordered_qty}
                                  value={item.received_qty || ''}
                                  onChange={(e) => updateReceivedQty(index, Number(e.target.value))}
                                  className="h-8 w-24 text-right"
                                />
                              </td>
                              <td className="p-3 text-right font-medium">
                                {formatCurrency(item.received_qty * item.unit_price)}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                        <tfoot className="bg-muted/30">
                          <tr className="border-t">
                            <td colSpan={3} className="p-3 text-right font-medium">
                              Total:
                            </td>
                            <td className="p-3 text-right font-bold">{formTotalReceived}</td>
                            <td className="p-3 text-right font-bold">{formatCurrency(formTotalValue)}</td>
                          </tr>
                        </tfoot>
                      </table>
                    </div>
                  )}
                </div>
              </>
            )}
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setCreateDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleCreateGRN} disabled={isCreating || !formData.po_id || formTotalReceived === 0}>
              {isCreating ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Creating...
                </>
              ) : (
                'Create GRN'
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* View GRN Dialog */}
      <Dialog open={viewDialogOpen} onOpenChange={setViewDialogOpen}>
        <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Goods Receipt Details</DialogTitle>
            <DialogDescription>{selectedGRN?.grn_number}</DialogDescription>
          </DialogHeader>

          {selectedGRN && (
            <div className="space-y-6 py-4">
              <div className="grid gap-4 md:grid-cols-3">
                <div>
                  <Label className="text-muted-foreground">PO Number</Label>
                  <p className="font-medium">{selectedGRN.po_number}</p>
                </div>
                <div>
                  <Label className="text-muted-foreground">Vendor</Label>
                  <p className="font-medium">{selectedGRN.vendor_name}</p>
                  <p className="text-sm text-muted-foreground">{selectedGRN.vendor_code}</p>
                </div>
                <div>
                  <Label className="text-muted-foreground">Status</Label>
                  <div className="mt-1">
                    <Badge className={statusColors[selectedGRN.status]}>{selectedGRN.status.replace(/_/g, ' ')}</Badge>
                  </div>
                </div>
                <div>
                  <Label className="text-muted-foreground">Receipt Date</Label>
                  <p className="font-medium">{formatDate(selectedGRN.receipt_date, { format: 'long' })}</p>
                </div>
                {selectedGRN.inspector_name && (
                  <>
                    <div>
                      <Label className="text-muted-foreground">Inspector</Label>
                      <p className="font-medium">{selectedGRN.inspector_name}</p>
                    </div>
                    <div>
                      <Label className="text-muted-foreground">Inspection Date</Label>
                      <p className="font-medium">{formatDate(selectedGRN.inspection_date, { format: 'long' })}</p>
                    </div>
                  </>
                )}
              </div>

              {selectedGRN.notes && (
                <div>
                  <Label className="text-muted-foreground">Notes</Label>
                  <p>{selectedGRN.notes}</p>
                </div>
              )}

              <div>
                <Label className="text-muted-foreground mb-2 block">Line Items</Label>
                <div className="border rounded-lg overflow-hidden">
                  <table className="w-full">
                    <thead className="bg-muted/50">
                      <tr>
                        <th className="text-left p-3 font-medium">Item</th>
                        <th className="text-right p-3 font-medium">Ordered</th>
                        <th className="text-right p-3 font-medium">Received</th>
                        <th className="text-right p-3 font-medium">Accepted</th>
                        <th className="text-right p-3 font-medium">Rejected</th>
                        <th className="text-center p-3 font-medium">Inspection</th>
                        <th className="text-right p-3 font-medium">Value</th>
                      </tr>
                    </thead>
                    <tbody>
                      {selectedGRN.line_items.map((item) => (
                        <tr key={item.id} className="border-t">
                          <td className="p-3">
                            <p className="font-medium">{item.item_name}</p>
                            <p className="text-xs text-muted-foreground">{item.item_code}</p>
                            {item.rejection_reason && (
                              <p className="text-xs text-red-600 mt-1">Reason: {item.rejection_reason}</p>
                            )}
                          </td>
                          <td className="p-3 text-right">{item.ordered_qty}</td>
                          <td className="p-3 text-right">{item.received_qty}</td>
                          <td className="p-3 text-right text-green-600">{item.accepted_qty}</td>
                          <td className="p-3 text-right text-red-600">{item.rejected_qty}</td>
                          <td className="p-3 text-center">
                            <Badge className={inspectionStatusColors[item.inspection_status]}>
                              {item.inspection_status}
                            </Badge>
                          </td>
                          <td className="p-3 text-right font-medium">
                            {formatCurrency(item.received_qty * item.unit_price)}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                    <tfoot className="bg-muted/30">
                      <tr className="border-t">
                        <td className="p-3 font-medium">Totals</td>
                        <td className="p-3 text-right font-medium">{selectedGRN.total_ordered}</td>
                        <td className="p-3 text-right font-medium">{selectedGRN.total_received}</td>
                        <td className="p-3 text-right font-medium text-green-600">{selectedGRN.total_accepted}</td>
                        <td className="p-3 text-right font-medium text-red-600">{selectedGRN.total_rejected}</td>
                        <td className="p-3"></td>
                        <td className="p-3 text-right font-bold">{formatCurrency(selectedGRN.total_value)}</td>
                      </tr>
                    </tfoot>
                  </table>
                </div>
              </div>

              <div className="grid gap-4 md:grid-cols-2">
                <div>
                  <Label className="text-muted-foreground">Total Received Value</Label>
                  <p className="text-xl font-bold">{formatCurrency(selectedGRN.total_value)}</p>
                </div>
                <div>
                  <Label className="text-muted-foreground">Accepted Value</Label>
                  <p className="text-xl font-bold text-green-600">{formatCurrency(selectedGRN.accepted_value)}</p>
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
              Delete Goods Receipt
            </AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete <strong>{selectedGRN?.grn_number}</strong>? This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={isDeleting}>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDeleteGRN}
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
