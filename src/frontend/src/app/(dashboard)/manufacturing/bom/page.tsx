'use client';

import { useState, useEffect } from 'react';
import {
  Plus,
  Search,
  Package,
  Eye,
  Edit,
  Copy,
  Trash2,
  ChevronRight,
  ChevronDown,
  Loader2,
  AlertTriangle,
  FileText,
  Layers,
  IndianRupee,
  Clock,
  Download,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { PageHeader } from '@/components/layout/page-header';
import { StatCard } from '@/components/layout/stat-card';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
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
import { formatCurrency } from '@/lib/format';

interface BOMComponent {
  id: string;
  item_code: string;
  item_name: string;
  quantity: number;
  uom: string;
  unit_cost: number;
  total_cost: number;
  level: number;
  is_subassembly: boolean;
  children?: BOMComponent[];
}

interface BOM {
  id: string;
  bom_number: string;
  product_code: string;
  product_name: string;
  version: number;
  status: 'draft' | 'active' | 'obsolete';
  components_count: number;
  total_material_cost: number;
  total_labor_cost: number;
  total_overhead_cost: number;
  total_cost: number;
  lead_time_days: number;
  effective_date: string;
  expiry_date: string | null;
  created_by: string;
  created_at: string;
  notes: string;
}

const statusColors: Record<string, string> = {
  draft: 'bg-gray-100 text-gray-800',
  active: 'bg-green-100 text-green-800',
  obsolete: 'bg-red-100 text-red-800',
};

const mockBOMs: BOM[] = [
  {
    id: '1',
    bom_number: 'BOM-000001',
    product_code: 'PUMP-A-001',
    product_name: 'Industrial Pump Model A',
    version: 1,
    status: 'active',
    components_count: 12,
    total_material_cost: 12500,
    total_labor_cost: 1800,
    total_overhead_cost: 700,
    total_cost: 15000,
    lead_time_days: 7,
    effective_date: '2026-01-01',
    expiry_date: null,
    created_by: 'John Smith',
    created_at: '2025-12-15',
    notes: 'Standard configuration for Model A pump',
  },
  {
    id: '2',
    bom_number: 'BOM-000002',
    product_code: 'MOTOR-B-001',
    product_name: 'Motor Assembly B',
    version: 2,
    status: 'active',
    components_count: 8,
    total_material_cost: 7200,
    total_labor_cost: 950,
    total_overhead_cost: 350,
    total_cost: 8500,
    lead_time_days: 5,
    effective_date: '2026-01-05',
    expiry_date: null,
    created_by: 'Jane Doe',
    created_at: '2025-12-20',
    notes: 'Updated version with improved bearings',
  },
  {
    id: '3',
    bom_number: 'BOM-000003',
    product_code: 'VALVE-C-001',
    product_name: 'Valve Kit C',
    version: 1,
    status: 'draft',
    components_count: 6,
    total_material_cost: 3200,
    total_labor_cost: 450,
    total_overhead_cost: 150,
    total_cost: 3800,
    lead_time_days: 3,
    effective_date: '2026-02-01',
    expiry_date: null,
    created_by: 'Mike Johnson',
    created_at: '2026-01-10',
    notes: 'New valve kit for pressure systems',
  },
  {
    id: '4',
    bom_number: 'BOM-000004',
    product_code: 'PUMP-A-001',
    product_name: 'Industrial Pump Model A',
    version: 0,
    status: 'obsolete',
    components_count: 10,
    total_material_cost: 11000,
    total_labor_cost: 1600,
    total_overhead_cost: 600,
    total_cost: 13200,
    lead_time_days: 8,
    effective_date: '2025-06-01',
    expiry_date: '2025-12-31',
    created_by: 'John Smith',
    created_at: '2025-05-15',
    notes: 'Original design - replaced by v1',
  },
];

const mockComponents: BOMComponent[] = [
  {
    id: '1',
    item_code: 'MTR-001',
    item_name: 'Electric Motor 5HP',
    quantity: 1,
    uom: 'PCS',
    unit_cost: 4500,
    total_cost: 4500,
    level: 0,
    is_subassembly: false,
  },
  {
    id: '2',
    item_code: 'IMP-001',
    item_name: 'Impeller Assembly',
    quantity: 1,
    uom: 'PCS',
    unit_cost: 2800,
    total_cost: 2800,
    level: 0,
    is_subassembly: true,
    children: [
      {
        id: '2-1',
        item_code: 'IMP-BLADE',
        item_name: 'Impeller Blade',
        quantity: 6,
        uom: 'PCS',
        unit_cost: 350,
        total_cost: 2100,
        level: 1,
        is_subassembly: false,
      },
      {
        id: '2-2',
        item_code: 'IMP-HUB',
        item_name: 'Impeller Hub',
        quantity: 1,
        uom: 'PCS',
        unit_cost: 700,
        total_cost: 700,
        level: 1,
        is_subassembly: false,
      },
    ],
  },
  {
    id: '3',
    item_code: 'HSG-001',
    item_name: 'Pump Housing',
    quantity: 1,
    uom: 'PCS',
    unit_cost: 3200,
    total_cost: 3200,
    level: 0,
    is_subassembly: false,
  },
  {
    id: '4',
    item_code: 'SEAL-KIT',
    item_name: 'Mechanical Seal Kit',
    quantity: 2,
    uom: 'SET',
    unit_cost: 450,
    total_cost: 900,
    level: 0,
    is_subassembly: false,
  },
  {
    id: '5',
    item_code: 'BRG-001',
    item_name: 'Bearing Assembly',
    quantity: 2,
    uom: 'PCS',
    unit_cost: 550,
    total_cost: 1100,
    level: 0,
    is_subassembly: false,
  },
];

export default function BOMPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [activeTab, setActiveTab] = useState('list');
  const { showToast } = useToast();
  const { data: bomsData, isLoading, get: getBOMs } = useApi<{ data: BOM[] }>();
  const deleteApi = useApi();

  // Local state
  const [localBOMs, setLocalBOMs] = useState<BOM[]>([]);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [itemToDelete, setItemToDelete] = useState<BOM | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  // Dialog states
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [viewDialogOpen, setViewDialogOpen] = useState(false);
  const [selectedBOM, setSelectedBOM] = useState<BOM | null>(null);
  const [expandedComponents, setExpandedComponents] = useState<Set<string>>(new Set());

  // Form state
  const [formData, setFormData] = useState({
    product_code: '',
    product_name: '',
    lead_time_days: '7',
    notes: '',
  });

  useEffect(() => {
    getBOMs('/manufacturing/bom');
  }, [getBOMs]);

  useEffect(() => {
    if (bomsData?.data) {
      setLocalBOMs(bomsData.data);
    }
  }, [bomsData]);

  const boms = localBOMs.length > 0 ? localBOMs : mockBOMs;

  const filteredBOMs = boms.filter((bom) => {
    const matchesSearch =
      bom.bom_number.toLowerCase().includes(searchQuery.toLowerCase()) ||
      bom.product_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      bom.product_code.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = statusFilter === 'all' || bom.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const stats = {
    totalBOMs: boms.length,
    activeBOMs: boms.filter((b) => b.status === 'active').length,
    draftBOMs: boms.filter((b) => b.status === 'draft').length,
    totalCostValue: boms.reduce((sum, b) => sum + b.total_cost, 0),
  };

  const handleDeleteClick = (bom: BOM) => {
    setItemToDelete(bom);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!itemToDelete) return;
    setIsDeleting(true);
    try {
      await deleteApi.delete(`/manufacturing/bom/${itemToDelete.id}`);
      setLocalBOMs(localBOMs.filter((b) => b.id !== itemToDelete.id));
      setDeleteDialogOpen(false);
      setItemToDelete(null);
      showToast('success', 'BOM deleted successfully');
    } catch (error) {
      console.error('Failed to delete:', error);
      showToast('error', 'Failed to delete BOM');
    } finally {
      setIsDeleting(false);
    }
  };

  const handleViewBOM = (bom: BOM) => {
    setSelectedBOM(bom);
    setViewDialogOpen(true);
  };

  const handleCreateBOM = async () => {
    try {
      const newBOM: BOM = {
        id: Date.now().toString(),
        bom_number: `BOM-${String(boms.length + 1).padStart(6, '0')}`,
        product_code: formData.product_code,
        product_name: formData.product_name,
        version: 1,
        status: 'draft',
        components_count: 0,
        total_material_cost: 0,
        total_labor_cost: 0,
        total_overhead_cost: 0,
        total_cost: 0,
        lead_time_days: parseInt(formData.lead_time_days) || 7,
        effective_date: new Date().toISOString().split('T')[0],
        expiry_date: null,
        created_by: 'Current User',
        created_at: new Date().toISOString().split('T')[0],
        notes: formData.notes,
      };
      setLocalBOMs([...localBOMs, newBOM]);
      setCreateDialogOpen(false);
      resetForm();
      showToast('success', 'BOM created successfully');
    } catch (error) {
      console.error('Failed to create BOM:', error);
      showToast('error', 'Failed to create BOM');
    }
  };

  const handleDuplicateBOM = (bom: BOM) => {
    const newBOM: BOM = {
      ...bom,
      id: Date.now().toString(),
      bom_number: `BOM-${String(boms.length + 1).padStart(6, '0')}`,
      version: bom.version + 1,
      status: 'draft',
      created_at: new Date().toISOString().split('T')[0],
      notes: `Copy of ${bom.bom_number}`,
    };
    setLocalBOMs([...localBOMs, newBOM]);
    showToast('success', 'BOM duplicated successfully');
  };

  const handleActivateBOM = (bom: BOM) => {
    setLocalBOMs(
      localBOMs.map((b) =>
        b.id === bom.id ? { ...b, status: 'active' as const } : b
      )
    );
    showToast('success', 'BOM activated successfully');
  };

  const resetForm = () => {
    setFormData({
      product_code: '',
      product_name: '',
      lead_time_days: '7',
      notes: '',
    });
  };

  const toggleComponentExpand = (id: string) => {
    const newExpanded = new Set(expandedComponents);
    if (newExpanded.has(id)) {
      newExpanded.delete(id);
    } else {
      newExpanded.add(id);
    }
    setExpandedComponents(newExpanded);
  };

  const renderComponentRow = (component: BOMComponent, depth: number = 0) => {
    const hasChildren = component.children && component.children.length > 0;
    const isExpanded = expandedComponents.has(component.id);

    return (
      <>
        <TableRow key={component.id}>
          <TableCell>
            <div className="flex items-center" style={{ paddingLeft: `${depth * 24}px` }}>
              {hasChildren ? (
                <Button
                  variant="ghost"
                  size="sm"
                  className="h-6 w-6 p-0 mr-2"
                  onClick={() => toggleComponentExpand(component.id)}
                >
                  {isExpanded ? (
                    <ChevronDown className="h-4 w-4" />
                  ) : (
                    <ChevronRight className="h-4 w-4" />
                  )}
                </Button>
              ) : (
                <span className="w-8" />
              )}
              <span className="font-medium">{component.item_code}</span>
            </div>
          </TableCell>
          <TableCell>
            <div className="flex items-center gap-2">
              {component.item_name}
              {component.is_subassembly && (
                <Badge variant="outline" className="text-xs">
                  Sub-assembly
                </Badge>
              )}
            </div>
          </TableCell>
          <TableCell className="text-right">{component.quantity}</TableCell>
          <TableCell>{component.uom}</TableCell>
          <TableCell className="text-right">{formatCurrency(component.unit_cost)}</TableCell>
          <TableCell className="text-right font-medium">{formatCurrency(component.total_cost)}</TableCell>
        </TableRow>
        {hasChildren && isExpanded && component.children?.map((child) => renderComponentRow(child, depth + 1))}
      </>
    );
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Bill of Materials"
        description="Manage product structures and component hierarchies"
        breadcrumbs={[
          { label: 'Manufacturing', href: '/manufacturing' },
          { label: 'Bill of Materials' },
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
                  Create BOM
                </Button>
              </DialogTrigger>
              <DialogContent className="max-w-lg">
                <DialogHeader>
                  <DialogTitle>Create Bill of Materials</DialogTitle>
                  <DialogDescription>
                    Create a new BOM for a product
                  </DialogDescription>
                </DialogHeader>
                <div className="grid gap-4 py-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label>Product Code</Label>
                      <Input
                        placeholder="PROD-XXX"
                        value={formData.product_code}
                        onChange={(e) => setFormData({ ...formData, product_code: e.target.value })}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label>Lead Time (Days)</Label>
                      <Input
                        type="number"
                        placeholder="7"
                        value={formData.lead_time_days}
                        onChange={(e) => setFormData({ ...formData, lead_time_days: e.target.value })}
                      />
                    </div>
                  </div>
                  <div className="space-y-2">
                    <Label>Product Name</Label>
                    <Input
                      placeholder="Enter product name"
                      value={formData.product_name}
                      onChange={(e) => setFormData({ ...formData, product_name: e.target.value })}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Notes</Label>
                    <Textarea
                      placeholder="Add any notes about this BOM"
                      value={formData.notes}
                      onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                    />
                  </div>
                </div>
                <DialogFooter>
                  <Button variant="outline" onClick={() => setCreateDialogOpen(false)}>
                    Cancel
                  </Button>
                  <Button onClick={handleCreateBOM}>Create BOM</Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
          </div>
        }
      />

      {isLoading && (
        <Card className="p-8 flex items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <span className="ml-2">Loading BOMs...</span>
        </Card>
      )}

      {/* Stats */}
      <div className="grid gap-4 md:grid-cols-4">
        <StatCard
          title="Total BOMs"
          value={stats.totalBOMs}
          icon={FileText}
          description="All versions"
        />
        <StatCard
          title="Active BOMs"
          value={stats.activeBOMs}
          icon={Package}
          description="In production"
        />
        <StatCard
          title="Draft BOMs"
          value={stats.draftBOMs}
          icon={Layers}
          description="Pending approval"
        />
        <StatCard
          title="Total Cost Value"
          value={formatCurrency(stats.totalCostValue)}
          icon={IndianRupee}
          description="All active BOMs"
        />
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="list">BOM List</TabsTrigger>
          <TabsTrigger value="hierarchy">Component Hierarchy</TabsTrigger>
        </TabsList>

        <TabsContent value="list" className="mt-4 space-y-4">
          {/* Filters */}
          <div className="flex gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search BOMs..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-9"
              />
            </div>
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="draft">Draft</SelectItem>
                <SelectItem value="active">Active</SelectItem>
                <SelectItem value="obsolete">Obsolete</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* BOM Table */}
          <Card>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>BOM #</TableHead>
                  <TableHead>Product</TableHead>
                  <TableHead className="text-center">Version</TableHead>
                  <TableHead className="text-center">Components</TableHead>
                  <TableHead className="text-right">Total Cost</TableHead>
                  <TableHead className="text-center">Lead Time</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredBOMs.map((bom) => (
                  <TableRow key={bom.id}>
                    <TableCell className="font-medium">{bom.bom_number}</TableCell>
                    <TableCell>
                      <div>
                        <p className="font-medium">{bom.product_name}</p>
                        <p className="text-sm text-muted-foreground">{bom.product_code}</p>
                      </div>
                    </TableCell>
                    <TableCell className="text-center">v{bom.version}</TableCell>
                    <TableCell className="text-center">{bom.components_count} items</TableCell>
                    <TableCell className="text-right font-medium">
                      {formatCurrency(bom.total_cost)}
                    </TableCell>
                    <TableCell className="text-center">{bom.lead_time_days} days</TableCell>
                    <TableCell>
                      <Badge className={statusColors[bom.status]}>{bom.status}</Badge>
                    </TableCell>
                    <TableCell>
                      <div className="flex justify-end gap-1">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleViewBOM(bom)}
                        >
                          <Eye className="h-4 w-4" />
                        </Button>
                        <Button variant="ghost" size="sm">
                          <Edit className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleDuplicateBOM(bom)}
                        >
                          <Copy className="h-4 w-4" />
                        </Button>
                        {(bom.status === 'draft' || bom.status === 'obsolete') && (
                          <Button
                            variant="ghost"
                            size="sm"
                            className="text-red-600 hover:text-red-700 hover:bg-red-50"
                            onClick={() => handleDeleteClick(bom)}
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

          {filteredBOMs.length === 0 && !isLoading && (
            <Card className="p-12 text-center">
              <Package className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
              <h3 className="text-lg font-medium mb-2">No BOMs found</h3>
              <p className="text-muted-foreground mb-4">
                {searchQuery || statusFilter !== 'all'
                  ? 'Try adjusting your filters'
                  : 'Get started by creating your first BOM'}
              </p>
              <Button onClick={() => setCreateDialogOpen(true)}>
                <Plus className="h-4 w-4 mr-2" />
                Create BOM
              </Button>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="hierarchy" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle>Component Hierarchy</CardTitle>
              <CardDescription>
                Select a BOM to view its component structure
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="mb-4">
                <Select
                  value={selectedBOM?.id || ''}
                  onValueChange={(value) => {
                    const bom = boms.find((b) => b.id === value);
                    setSelectedBOM(bom || null);
                  }}
                >
                  <SelectTrigger className="w-[300px]">
                    <SelectValue placeholder="Select a BOM" />
                  </SelectTrigger>
                  <SelectContent>
                    {boms.filter((b) => b.status === 'active').map((bom) => (
                      <SelectItem key={bom.id} value={bom.id}>
                        {bom.bom_number} - {bom.product_name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {selectedBOM ? (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Item Code</TableHead>
                      <TableHead>Description</TableHead>
                      <TableHead className="text-right">Qty</TableHead>
                      <TableHead>UOM</TableHead>
                      <TableHead className="text-right">Unit Cost</TableHead>
                      <TableHead className="text-right">Total Cost</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {mockComponents.map((component) => renderComponentRow(component))}
                  </TableBody>
                </Table>
              ) : (
                <div className="text-center py-12 text-muted-foreground">
                  <Layers className="h-12 w-12 mx-auto mb-4" />
                  <p>Select a BOM to view its component hierarchy</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* View BOM Dialog */}
      <Dialog open={viewDialogOpen} onOpenChange={setViewDialogOpen}>
        <DialogContent className="max-w-3xl">
          <DialogHeader>
            <DialogTitle>BOM Details - {selectedBOM?.bom_number}</DialogTitle>
            <DialogDescription>
              View detailed information about this Bill of Materials
            </DialogDescription>
          </DialogHeader>
          {selectedBOM && (
            <div className="space-y-6">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <h4 className="text-sm font-medium text-muted-foreground">Product</h4>
                  <p className="font-medium">{selectedBOM.product_name}</p>
                  <p className="text-sm text-muted-foreground">{selectedBOM.product_code}</p>
                </div>
                <div>
                  <h4 className="text-sm font-medium text-muted-foreground">Version & Status</h4>
                  <div className="flex items-center gap-2 mt-1">
                    <span className="font-medium">v{selectedBOM.version}</span>
                    <Badge className={statusColors[selectedBOM.status]}>{selectedBOM.status}</Badge>
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-4 gap-4">
                <Card className="p-4">
                  <p className="text-sm text-muted-foreground">Material Cost</p>
                  <p className="text-lg font-bold">{formatCurrency(selectedBOM.total_material_cost)}</p>
                </Card>
                <Card className="p-4">
                  <p className="text-sm text-muted-foreground">Labor Cost</p>
                  <p className="text-lg font-bold">{formatCurrency(selectedBOM.total_labor_cost)}</p>
                </Card>
                <Card className="p-4">
                  <p className="text-sm text-muted-foreground">Overhead Cost</p>
                  <p className="text-lg font-bold">{formatCurrency(selectedBOM.total_overhead_cost)}</p>
                </Card>
                <Card className="p-4 bg-primary/5">
                  <p className="text-sm text-muted-foreground">Total Cost</p>
                  <p className="text-lg font-bold text-primary">{formatCurrency(selectedBOM.total_cost)}</p>
                </Card>
              </div>

              <div className="grid grid-cols-3 gap-4 text-sm">
                <div>
                  <p className="text-muted-foreground">Components</p>
                  <p className="font-medium">{selectedBOM.components_count} items</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Lead Time</p>
                  <p className="font-medium">{selectedBOM.lead_time_days} days</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Effective Date</p>
                  <p className="font-medium">{selectedBOM.effective_date}</p>
                </div>
              </div>

              {selectedBOM.notes && (
                <div>
                  <h4 className="text-sm font-medium text-muted-foreground mb-1">Notes</h4>
                  <p className="text-sm">{selectedBOM.notes}</p>
                </div>
              )}
            </div>
          )}
          <DialogFooter>
            {selectedBOM?.status === 'draft' && (
              <Button onClick={() => {
                handleActivateBOM(selectedBOM);
                setViewDialogOpen(false);
              }}>
                Activate BOM
              </Button>
            )}
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
              Delete Bill of Materials
            </AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete BOM <strong>{itemToDelete?.bom_number}</strong> for{' '}
              <strong>{itemToDelete?.product_name}</strong>? This action cannot be undone.
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
