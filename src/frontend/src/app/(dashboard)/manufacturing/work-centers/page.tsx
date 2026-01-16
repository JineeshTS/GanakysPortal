'use client';

import { useState, useEffect } from 'react';
import {
  Plus,
  Search,
  Cog,
  Settings,
  Wrench,
  Play,
  Pause,
  MoreVertical,
  Loader2,
  Trash2,
  AlertTriangle,
  Activity,
  Users,
  Clock,
  CheckCircle,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Label } from '@/components/ui/label';
import { PageHeader } from '@/components/layout/page-header';
import { StatCard } from '@/components/layout/stat-card';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
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

interface WorkCenter {
  id: string;
  code: string;
  name: string;
  type: 'assembly' | 'machine' | 'finishing' | 'testing' | 'packaging';
  status: 'active' | 'maintenance' | 'inactive';
  capacity: number;
  capacity_uom: string;
  utilization: number;
  current_job: string | null;
  operators_assigned: number;
  shift_hours: number;
  hourly_rate: number;
  location: string;
  last_maintenance: string;
  next_maintenance: string;
}

const statusColors: Record<string, string> = {
  active: 'bg-green-100 text-green-800',
  maintenance: 'bg-orange-100 text-orange-800',
  inactive: 'bg-gray-100 text-gray-800',
};

const typeColors: Record<string, string> = {
  assembly: 'bg-blue-100 text-blue-800',
  machine: 'bg-purple-100 text-purple-800',
  finishing: 'bg-teal-100 text-teal-800',
  testing: 'bg-yellow-100 text-yellow-800',
  packaging: 'bg-pink-100 text-pink-800',
};

const mockWorkCenters: WorkCenter[] = [
  {
    id: '1',
    code: 'WC-001',
    name: 'Assembly Line 1',
    type: 'assembly',
    status: 'active',
    capacity: 100,
    capacity_uom: 'units/hr',
    utilization: 85,
    current_job: 'PO-000001',
    operators_assigned: 8,
    shift_hours: 8,
    hourly_rate: 1500,
    location: 'Building A, Floor 1',
    last_maintenance: '2026-01-01',
    next_maintenance: '2026-02-01',
  },
  {
    id: '2',
    code: 'WC-002',
    name: 'CNC Machine Shop',
    type: 'machine',
    status: 'active',
    capacity: 50,
    capacity_uom: 'units/hr',
    utilization: 72,
    current_job: 'PO-000002',
    operators_assigned: 4,
    shift_hours: 8,
    hourly_rate: 2500,
    location: 'Building A, Floor 2',
    last_maintenance: '2026-01-05',
    next_maintenance: '2026-02-05',
  },
  {
    id: '3',
    code: 'WC-003',
    name: 'Finishing Station',
    type: 'finishing',
    status: 'maintenance',
    capacity: 200,
    capacity_uom: 'units/hr',
    utilization: 0,
    current_job: null,
    operators_assigned: 6,
    shift_hours: 8,
    hourly_rate: 1200,
    location: 'Building B, Floor 1',
    last_maintenance: '2026-01-10',
    next_maintenance: '2026-01-17',
  },
  {
    id: '4',
    code: 'WC-004',
    name: 'Quality Testing Lab',
    type: 'testing',
    status: 'active',
    capacity: 150,
    capacity_uom: 'tests/hr',
    utilization: 60,
    current_job: null,
    operators_assigned: 3,
    shift_hours: 8,
    hourly_rate: 1800,
    location: 'Building B, Floor 2',
    last_maintenance: '2025-12-15',
    next_maintenance: '2026-01-15',
  },
  {
    id: '5',
    code: 'WC-005',
    name: 'Packaging Line',
    type: 'packaging',
    status: 'inactive',
    capacity: 300,
    capacity_uom: 'units/hr',
    utilization: 0,
    current_job: null,
    operators_assigned: 0,
    shift_hours: 8,
    hourly_rate: 800,
    location: 'Building C, Floor 1',
    last_maintenance: '2025-12-20',
    next_maintenance: '2026-01-20',
  },
];

export default function WorkCentersPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [typeFilter, setTypeFilter] = useState<string>('all');
  const { showToast } = useToast();
  const { data: workCentersData, isLoading, get: getWorkCenters } = useApi<{ data: WorkCenter[] }>();
  const deleteApi = useApi();

  // Local state
  const [localWorkCenters, setLocalWorkCenters] = useState<WorkCenter[]>([]);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [itemToDelete, setItemToDelete] = useState<WorkCenter | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  // Dialog state for add/configure
  const [addDialogOpen, setAddDialogOpen] = useState(false);
  const [configureDialogOpen, setConfigureDialogOpen] = useState(false);
  const [selectedWorkCenter, setSelectedWorkCenter] = useState<WorkCenter | null>(null);

  // Form state
  const [formData, setFormData] = useState({
    code: '',
    name: '',
    type: 'assembly' as WorkCenter['type'],
    capacity: '',
    capacity_uom: 'units/hr',
    hourly_rate: '',
    location: '',
    shift_hours: '8',
  });

  useEffect(() => {
    getWorkCenters('/manufacturing/work-centers');
  }, [getWorkCenters]);

  useEffect(() => {
    if (workCentersData?.data) {
      setLocalWorkCenters(workCentersData.data);
    }
  }, [workCentersData]);

  const workCenters = localWorkCenters.length > 0 ? localWorkCenters : mockWorkCenters;

  const filteredWorkCenters = workCenters.filter((wc) => {
    const matchesSearch =
      wc.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      wc.code.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = statusFilter === 'all' || wc.status === statusFilter;
    const matchesType = typeFilter === 'all' || wc.type === typeFilter;
    return matchesSearch && matchesStatus && matchesType;
  });

  const stats = {
    totalWorkCenters: workCenters.length,
    activeWorkCenters: workCenters.filter((wc) => wc.status === 'active').length,
    averageUtilization: Math.round(
      workCenters.filter((wc) => wc.status === 'active').reduce((sum, wc) => sum + wc.utilization, 0) /
        (workCenters.filter((wc) => wc.status === 'active').length || 1)
    ),
    maintenanceDue: workCenters.filter((wc) => wc.status === 'maintenance').length,
  };

  const handleDeleteClick = (wc: WorkCenter) => {
    setItemToDelete(wc);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!itemToDelete) return;
    setIsDeleting(true);
    try {
      await deleteApi.delete(`/manufacturing/work-centers/${itemToDelete.id}`);
      setLocalWorkCenters(localWorkCenters.filter((wc) => wc.id !== itemToDelete.id));
      setDeleteDialogOpen(false);
      setItemToDelete(null);
      showToast('success', 'Work center deleted successfully');
    } catch (error) {
      console.error('Failed to delete:', error);
      showToast('error', 'Failed to delete work center');
    } finally {
      setIsDeleting(false);
    }
  };

  const handleConfigureClick = (wc: WorkCenter) => {
    setSelectedWorkCenter(wc);
    setFormData({
      code: wc.code,
      name: wc.name,
      type: wc.type,
      capacity: wc.capacity.toString(),
      capacity_uom: wc.capacity_uom,
      hourly_rate: wc.hourly_rate.toString(),
      location: wc.location,
      shift_hours: wc.shift_hours.toString(),
    });
    setConfigureDialogOpen(true);
  };

  const handleAddWorkCenter = async () => {
    try {
      // In real implementation, this would call the API
      const newWorkCenter: WorkCenter = {
        id: Date.now().toString(),
        code: formData.code,
        name: formData.name,
        type: formData.type,
        status: 'inactive',
        capacity: parseInt(formData.capacity) || 0,
        capacity_uom: formData.capacity_uom,
        utilization: 0,
        current_job: null,
        operators_assigned: 0,
        shift_hours: parseInt(formData.shift_hours) || 8,
        hourly_rate: parseInt(formData.hourly_rate) || 0,
        location: formData.location,
        last_maintenance: new Date().toISOString().split('T')[0],
        next_maintenance: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      };
      setLocalWorkCenters([...localWorkCenters, newWorkCenter]);
      setAddDialogOpen(false);
      resetForm();
      showToast('success', 'Work center added successfully');
    } catch (error) {
      console.error('Failed to add work center:', error);
      showToast('error', 'Failed to add work center');
    }
  };

  const handleUpdateWorkCenter = async () => {
    if (!selectedWorkCenter) return;
    try {
      const updatedWorkCenter: WorkCenter = {
        ...selectedWorkCenter,
        code: formData.code,
        name: formData.name,
        type: formData.type,
        capacity: parseInt(formData.capacity) || 0,
        capacity_uom: formData.capacity_uom,
        hourly_rate: parseInt(formData.hourly_rate) || 0,
        location: formData.location,
        shift_hours: parseInt(formData.shift_hours) || 8,
      };
      setLocalWorkCenters(
        localWorkCenters.map((wc) => (wc.id === selectedWorkCenter.id ? updatedWorkCenter : wc))
      );
      setConfigureDialogOpen(false);
      setSelectedWorkCenter(null);
      resetForm();
      showToast('success', 'Work center updated successfully');
    } catch (error) {
      console.error('Failed to update work center:', error);
      showToast('error', 'Failed to update work center');
    }
  };

  const handleStatusChange = async (wc: WorkCenter, newStatus: WorkCenter['status']) => {
    try {
      setLocalWorkCenters(
        localWorkCenters.map((item) =>
          item.id === wc.id ? { ...item, status: newStatus, utilization: newStatus === 'active' ? item.utilization : 0 } : item
        )
      );
      showToast('success', `Work center status changed to ${newStatus}`);
    } catch (error) {
      console.error('Failed to update status:', error);
      showToast('error', 'Failed to update work center status');
    }
  };

  const resetForm = () => {
    setFormData({
      code: '',
      name: '',
      type: 'assembly',
      capacity: '',
      capacity_uom: 'units/hr',
      hourly_rate: '',
      location: '',
      shift_hours: '8',
    });
  };

  const getUtilizationColor = (utilization: number) => {
    if (utilization >= 80) return 'text-green-600';
    if (utilization >= 50) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getProgressColor = (utilization: number) => {
    if (utilization >= 80) return 'bg-green-500';
    if (utilization >= 50) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Work Centers"
        description="Manage shop floor resources and production capacity"
        breadcrumbs={[
          { label: 'Manufacturing', href: '/manufacturing' },
          { label: 'Work Centers' },
        ]}
        actions={
          <Dialog open={addDialogOpen} onOpenChange={setAddDialogOpen}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="h-4 w-4 mr-2" />
                Add Work Center
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-lg">
              <DialogHeader>
                <DialogTitle>Add Work Center</DialogTitle>
                <DialogDescription>
                  Create a new work center for production operations
                </DialogDescription>
              </DialogHeader>
              <div className="grid gap-4 py-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>Code</Label>
                    <Input
                      placeholder="WC-XXX"
                      value={formData.code}
                      onChange={(e) => setFormData({ ...formData, code: e.target.value })}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Type</Label>
                    <Select
                      value={formData.type}
                      onValueChange={(value) => setFormData({ ...formData, type: value as WorkCenter['type'] })}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select type" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="assembly">Assembly</SelectItem>
                        <SelectItem value="machine">Machine</SelectItem>
                        <SelectItem value="finishing">Finishing</SelectItem>
                        <SelectItem value="testing">Testing</SelectItem>
                        <SelectItem value="packaging">Packaging</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <div className="space-y-2">
                  <Label>Name</Label>
                  <Input
                    placeholder="Enter work center name"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>Capacity</Label>
                    <Input
                      type="number"
                      placeholder="100"
                      value={formData.capacity}
                      onChange={(e) => setFormData({ ...formData, capacity: e.target.value })}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Capacity UOM</Label>
                    <Select
                      value={formData.capacity_uom}
                      onValueChange={(value) => setFormData({ ...formData, capacity_uom: value })}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="units/hr">Units/Hour</SelectItem>
                        <SelectItem value="kg/hr">Kg/Hour</SelectItem>
                        <SelectItem value="tests/hr">Tests/Hour</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>Hourly Rate (Rs.)</Label>
                    <Input
                      type="number"
                      placeholder="1500"
                      value={formData.hourly_rate}
                      onChange={(e) => setFormData({ ...formData, hourly_rate: e.target.value })}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Shift Hours</Label>
                    <Input
                      type="number"
                      placeholder="8"
                      value={formData.shift_hours}
                      onChange={(e) => setFormData({ ...formData, shift_hours: e.target.value })}
                    />
                  </div>
                </div>
                <div className="space-y-2">
                  <Label>Location</Label>
                  <Input
                    placeholder="Building A, Floor 1"
                    value={formData.location}
                    onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                  />
                </div>
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={() => setAddDialogOpen(false)}>
                  Cancel
                </Button>
                <Button onClick={handleAddWorkCenter}>Add Work Center</Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        }
      />

      {isLoading && (
        <Card className="p-8 flex items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <span className="ml-2">Loading work centers...</span>
        </Card>
      )}

      {/* Stats */}
      <div className="grid gap-4 md:grid-cols-4">
        <StatCard
          title="Total Work Centers"
          value={stats.totalWorkCenters}
          icon={Cog}
          description="Registered resources"
        />
        <StatCard
          title="Active"
          value={stats.activeWorkCenters}
          icon={CheckCircle}
          description="Currently operational"
        />
        <StatCard
          title="Avg. Utilization"
          value={`${stats.averageUtilization}%`}
          icon={Activity}
          description="Active work centers"
        />
        <StatCard
          title="In Maintenance"
          value={stats.maintenanceDue}
          icon={Wrench}
          description="Scheduled maintenance"
          className="border-orange-200 bg-orange-50"
        />
      </div>

      {/* Filters */}
      <div className="flex gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search work centers..."
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
            <SelectItem value="active">Active</SelectItem>
            <SelectItem value="maintenance">Maintenance</SelectItem>
            <SelectItem value="inactive">Inactive</SelectItem>
          </SelectContent>
        </Select>
        <Select value={typeFilter} onValueChange={setTypeFilter}>
          <SelectTrigger className="w-[180px]">
            <SelectValue placeholder="Type" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Types</SelectItem>
            <SelectItem value="assembly">Assembly</SelectItem>
            <SelectItem value="machine">Machine</SelectItem>
            <SelectItem value="finishing">Finishing</SelectItem>
            <SelectItem value="testing">Testing</SelectItem>
            <SelectItem value="packaging">Packaging</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Work Center Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {filteredWorkCenters.map((wc) => (
          <Card key={wc.id} className="hover:shadow-md transition-shadow">
            <CardHeader className="pb-2">
              <div className="flex items-center justify-between">
                <CardTitle className="text-lg">{wc.name}</CardTitle>
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="ghost" size="icon">
                      <MoreVertical className="h-4 w-4" />
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end">
                    <DropdownMenuItem onClick={() => handleConfigureClick(wc)}>
                      <Settings className="h-4 w-4 mr-2" />
                      Configure
                    </DropdownMenuItem>
                    {wc.status !== 'active' && (
                      <DropdownMenuItem onClick={() => handleStatusChange(wc, 'active')}>
                        <Play className="h-4 w-4 mr-2" />
                        Set Active
                      </DropdownMenuItem>
                    )}
                    {wc.status === 'active' && (
                      <DropdownMenuItem onClick={() => handleStatusChange(wc, 'maintenance')}>
                        <Wrench className="h-4 w-4 mr-2" />
                        Set Maintenance
                      </DropdownMenuItem>
                    )}
                    {wc.status !== 'inactive' && (
                      <DropdownMenuItem onClick={() => handleStatusChange(wc, 'inactive')}>
                        <Pause className="h-4 w-4 mr-2" />
                        Set Inactive
                      </DropdownMenuItem>
                    )}
                    {wc.status === 'inactive' && (
                      <DropdownMenuItem
                        className="text-red-600"
                        onClick={() => handleDeleteClick(wc)}
                      >
                        <Trash2 className="h-4 w-4 mr-2" />
                        Delete
                      </DropdownMenuItem>
                    )}
                  </DropdownMenuContent>
                </DropdownMenu>
              </div>
              <div className="flex items-center gap-2 mt-1">
                <span className="text-sm text-muted-foreground">{wc.code}</span>
                <Badge className={typeColors[wc.type]}>{wc.type}</Badge>
                <Badge className={statusColors[wc.status]}>{wc.status}</Badge>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {/* Utilization */}
                <div>
                  <div className="flex justify-between mb-1">
                    <span className="text-sm text-muted-foreground">Utilization</span>
                    <span className={`text-sm font-medium ${getUtilizationColor(wc.utilization)}`}>
                      {wc.utilization}%
                    </span>
                  </div>
                  <div className="h-2 bg-gray-200 rounded">
                    <div
                      className={`h-2 rounded ${getProgressColor(wc.utilization)}`}
                      style={{ width: `${wc.utilization}%` }}
                    />
                  </div>
                </div>

                {/* Details */}
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div className="flex items-center gap-2">
                    <Activity className="h-4 w-4 text-muted-foreground" />
                    <div>
                      <p className="text-muted-foreground text-xs">Capacity</p>
                      <p className="font-medium">
                        {wc.capacity} {wc.capacity_uom}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Users className="h-4 w-4 text-muted-foreground" />
                    <div>
                      <p className="text-muted-foreground text-xs">Operators</p>
                      <p className="font-medium">{wc.operators_assigned}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Clock className="h-4 w-4 text-muted-foreground" />
                    <div>
                      <p className="text-muted-foreground text-xs">Shift</p>
                      <p className="font-medium">{wc.shift_hours} hrs</p>
                    </div>
                  </div>
                  <div>
                    <p className="text-muted-foreground text-xs">Current Job</p>
                    <p className="font-medium">{wc.current_job || 'None'}</p>
                  </div>
                </div>

                {/* Location */}
                <div className="text-sm border-t pt-3">
                  <p className="text-muted-foreground text-xs">Location</p>
                  <p className="font-medium">{wc.location}</p>
                </div>

                {/* Action Buttons */}
                <div className="flex gap-2 pt-2">
                  <Button
                    variant="outline"
                    size="sm"
                    className="flex-1"
                    onClick={() => handleConfigureClick(wc)}
                  >
                    <Settings className="mr-1 h-4 w-4" />
                    Configure
                  </Button>
                  <Button variant="outline" size="sm" className="flex-1">
                    <Wrench className="mr-1 h-4 w-4" />
                    Maintenance
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {filteredWorkCenters.length === 0 && !isLoading && (
        <Card className="p-12 text-center">
          <Cog className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
          <h3 className="text-lg font-medium mb-2">No work centers found</h3>
          <p className="text-muted-foreground mb-4">
            {searchQuery || statusFilter !== 'all' || typeFilter !== 'all'
              ? 'Try adjusting your filters'
              : 'Get started by adding your first work center'}
          </p>
          <Button onClick={() => setAddDialogOpen(true)}>
            <Plus className="h-4 w-4 mr-2" />
            Add Work Center
          </Button>
        </Card>
      )}

      {/* Configure Dialog */}
      <Dialog open={configureDialogOpen} onOpenChange={setConfigureDialogOpen}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>Configure Work Center</DialogTitle>
            <DialogDescription>
              Update work center settings and capacity
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Code</Label>
                <Input
                  value={formData.code}
                  onChange={(e) => setFormData({ ...formData, code: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label>Type</Label>
                <Select
                  value={formData.type}
                  onValueChange={(value) => setFormData({ ...formData, type: value as WorkCenter['type'] })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="assembly">Assembly</SelectItem>
                    <SelectItem value="machine">Machine</SelectItem>
                    <SelectItem value="finishing">Finishing</SelectItem>
                    <SelectItem value="testing">Testing</SelectItem>
                    <SelectItem value="packaging">Packaging</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div className="space-y-2">
              <Label>Name</Label>
              <Input
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Capacity</Label>
                <Input
                  type="number"
                  value={formData.capacity}
                  onChange={(e) => setFormData({ ...formData, capacity: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label>Capacity UOM</Label>
                <Select
                  value={formData.capacity_uom}
                  onValueChange={(value) => setFormData({ ...formData, capacity_uom: value })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="units/hr">Units/Hour</SelectItem>
                    <SelectItem value="kg/hr">Kg/Hour</SelectItem>
                    <SelectItem value="tests/hr">Tests/Hour</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Hourly Rate (Rs.)</Label>
                <Input
                  type="number"
                  value={formData.hourly_rate}
                  onChange={(e) => setFormData({ ...formData, hourly_rate: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label>Shift Hours</Label>
                <Input
                  type="number"
                  value={formData.shift_hours}
                  onChange={(e) => setFormData({ ...formData, shift_hours: e.target.value })}
                />
              </div>
            </div>
            <div className="space-y-2">
              <Label>Location</Label>
              <Input
                value={formData.location}
                onChange={(e) => setFormData({ ...formData, location: e.target.value })}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setConfigureDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleUpdateWorkCenter}>Save Changes</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-red-500" />
              Delete Work Center
            </AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete work center <strong>{itemToDelete?.name}</strong> ({itemToDelete?.code})?
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
