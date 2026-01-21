'use client';

import { useState, useEffect } from 'react';
import { Plus, Search, Building2, TrendingDown, Wrench, ArrowRightLeft, Trash2, MoreVertical, Loader2, Calculator, FileText, IndianRupee, AlertTriangle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { PageHeader } from '@/components/layout/page-header';
import { StatCard } from '@/components/layout/stat-card';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { useApi } from '@/hooks';
import { formatCurrency } from '@/lib/format';

interface FixedAsset {
  id: string;
  asset_number: string;
  name: string;
  category: string;
  location: string;
  acquisition_date: string;
  acquisition_cost: number;
  book_value: number;
  status: string;
}

interface DepreciationSchedule {
  id: string;
  asset_name: string;
  period: string;
  opening_value: number;
  depreciation: number;
  closing_value: number;
  status: string;
}

interface MaintenanceRecord {
  id: string;
  asset_name: string;
  maintenance_type: string;
  scheduled_date: string;
  cost: number;
  status: string;
  vendor: string;
}

interface AssetTransfer {
  id: string;
  transfer_number: string;
  asset_name: string;
  from_location: string;
  to_location: string;
  transfer_date: string;
  status: string;
}

const statusColors: Record<string, string> = {
  active: 'bg-green-100 text-green-800',
  inactive: 'bg-gray-100 text-gray-800',
  disposed: 'bg-red-100 text-red-800',
  under_maintenance: 'bg-yellow-100 text-yellow-800',
  pending: 'bg-yellow-100 text-yellow-800',
  posted: 'bg-green-100 text-green-800',
  completed: 'bg-green-100 text-green-800',
  scheduled: 'bg-blue-100 text-blue-800',
  overdue: 'bg-red-100 text-red-800',
  in_transit: 'bg-purple-100 text-purple-800',
};

export default function FixedAssetsPage() {
  const [activeTab, setActiveTab] = useState('assets');
  const [searchQuery, setSearchQuery] = useState('');
  const [localAssets, setLocalAssets] = useState<FixedAsset[]>([]);

  // Delete state
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [assetToDelete, setAssetToDelete] = useState<FixedAsset | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);
  const deleteApi = useApi();

  const handleDeleteClick = (asset: FixedAsset) => {
    setAssetToDelete(asset);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!assetToDelete) return;
    setIsDeleting(true);
    try {
      await deleteApi.delete(`/fixed-assets/assets/${assetToDelete.id}`);
      setLocalAssets(localAssets.filter(a => a.id !== assetToDelete.id));
      setDeleteDialogOpen(false);
      setAssetToDelete(null);
    } catch (error) {
      console.error('Failed to delete asset:', error);
    } finally {
      setIsDeleting(false);
    }
  };

  const { data: assetsData, isLoading: assetsLoading, get: getAssets } = useApi<{ data: FixedAsset[] }>();
  const { data: depreciationData, isLoading: depreciationLoading, get: getDepreciation } = useApi<{ data: DepreciationSchedule[] }>();
  const { data: maintenanceData, isLoading: maintenanceLoading, get: getMaintenance } = useApi<{ data: MaintenanceRecord[] }>();
  const { data: transfersData, isLoading: transfersLoading, get: getTransfers } = useApi<{ data: AssetTransfer[] }>();

  useEffect(() => {
    getAssets('/fixed-assets/assets');
    getDepreciation('/fixed-assets/depreciation');
    getMaintenance('/fixed-assets/maintenance');
    getTransfers('/fixed-assets/transfers');
  }, [getAssets, getDepreciation, getMaintenance, getTransfers]);

  // Sync API data to local state
  useEffect(() => {
    if (assetsData?.data) {
      setLocalAssets(assetsData.data);
    }
  }, [assetsData]);

  const assets = localAssets;
  const depreciation = depreciationData?.data || [];
  const maintenance = maintenanceData?.data || [];
  const transfers = transfersData?.data || [];
  const isLoading = assetsLoading || depreciationLoading || maintenanceLoading || transfersLoading;

  const stats = {
    totalAssets: assets.length || 245,
    totalValue: 125000000,
    monthlyDepreciation: 850000,
    maintenanceDue: maintenance.filter(m => m.status === 'scheduled').length || 8,
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Fixed Assets Management"
        description="Track assets, depreciation, maintenance, and disposals"
        actions={
          <Button>
            <Plus className="h-4 w-4 mr-2" />
            Add Asset
          </Button>
        }
      />

      {isLoading && (
        <Card className="p-8 flex items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <span className="ml-2">Loading fixed assets data...</span>
        </Card>
      )}

      <div className="grid gap-4 md:grid-cols-4">
        <StatCard
          title="Total Assets"
          value={stats.totalAssets}
          icon={Building2}
          description="Active fixed assets"
        />
        <StatCard
          title="Total Book Value"
          value={formatCurrency(stats.totalValue)}
          icon={IndianRupee}
          description="Net asset value"
        />
        <StatCard
          title="Monthly Depreciation"
          value={formatCurrency(stats.monthlyDepreciation)}
          icon={TrendingDown}
          description="Current month"
        />
        <StatCard
          title="Maintenance Due"
          value={stats.maintenanceDue}
          icon={Wrench}
          description="Scheduled services"
          className={stats.maintenanceDue > 0 ? "border-yellow-200 bg-yellow-50" : ""}
        />
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="assets">Asset Register</TabsTrigger>
          <TabsTrigger value="depreciation">Depreciation</TabsTrigger>
          <TabsTrigger value="maintenance">Maintenance</TabsTrigger>
          <TabsTrigger value="transfers">Transfers</TabsTrigger>
          <TabsTrigger value="disposals">Disposals</TabsTrigger>
        </TabsList>

        <TabsContent value="assets" className="mt-4">
          <div className="flex gap-4 mb-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search assets..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-9"
              />
            </div>
          </div>

          <div className="border rounded-lg overflow-hidden">
            <table className="w-full">
              <thead className="bg-muted/50">
                <tr>
                  <th className="text-left p-4 font-medium">Asset #</th>
                  <th className="text-left p-4 font-medium">Name</th>
                  <th className="text-left p-4 font-medium">Category</th>
                  <th className="text-left p-4 font-medium">Location</th>
                  <th className="text-right p-4 font-medium">Cost</th>
                  <th className="text-right p-4 font-medium">Book Value</th>
                  <th className="text-left p-4 font-medium">Status</th>
                  <th className="text-right p-4 font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {(assets.length ? assets : [
                  { id: '1', asset_number: 'FA-001', name: 'Dell Server PowerEdge R750', category: 'IT Equipment', location: 'Mumbai Data Center', acquisition_date: '2024-06-15', acquisition_cost: 450000, book_value: 337500, status: 'active' },
                  { id: '2', asset_number: 'FA-002', name: 'Toyota Innova Crysta', category: 'Vehicles', location: 'Mumbai Office', acquisition_date: '2023-03-20', acquisition_cost: 2200000, book_value: 1540000, status: 'active' },
                  { id: '3', asset_number: 'FA-003', name: 'Office Furniture Set', category: 'Furniture', location: 'Delhi Office', acquisition_date: '2024-01-10', acquisition_cost: 350000, book_value: 315000, status: 'active' },
                  { id: '4', asset_number: 'FA-004', name: 'CNC Milling Machine', category: 'Machinery', location: 'Pune Factory', acquisition_date: '2022-08-05', acquisition_cost: 8500000, book_value: 5950000, status: 'under_maintenance' },
                ]).map((asset) => (
                  <tr key={asset.id} className="border-t hover:bg-muted/30">
                    <td className="p-4 font-medium">{asset.asset_number}</td>
                    <td className="p-4">{asset.name}</td>
                    <td className="p-4">
                      <Badge variant="outline">{asset.category}</Badge>
                    </td>
                    <td className="p-4 text-muted-foreground">{asset.location}</td>
                    <td className="p-4 text-right">{formatCurrency(asset.acquisition_cost)}</td>
                    <td className="p-4 text-right font-medium">{formatCurrency(asset.book_value)}</td>
                    <td className="p-4">
                      <Badge className={statusColors[asset.status]}>
                        {asset.status.replace('_', ' ')}
                      </Badge>
                    </td>
                    <td className="p-4 text-right">
                      <div className="flex items-center justify-end gap-1">
                        <Button variant="ghost" size="icon">
                          <MoreVertical className="h-4 w-4" />
                        </Button>
                        {asset.status === 'disposed' && (
                          <Button
                            variant="ghost"
                            size="icon"
                            className="text-red-600 hover:text-red-700 hover:bg-red-50"
                            onClick={() => handleDeleteClick(asset)}
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </TabsContent>

        <TabsContent value="depreciation" className="mt-4">
          <div className="flex justify-between mb-4">
            <div className="text-sm text-muted-foreground">
              Depreciation calculated using Straight Line Method (SLM) as per Companies Act 2013
            </div>
            <Button>
              <Calculator className="h-4 w-4 mr-2" />
              Run Depreciation
            </Button>
          </div>

          <div className="border rounded-lg overflow-hidden">
            <table className="w-full">
              <thead className="bg-muted/50">
                <tr>
                  <th className="text-left p-4 font-medium">Asset</th>
                  <th className="text-left p-4 font-medium">Period</th>
                  <th className="text-right p-4 font-medium">Opening Value</th>
                  <th className="text-right p-4 font-medium">Depreciation</th>
                  <th className="text-right p-4 font-medium">Closing Value</th>
                  <th className="text-left p-4 font-medium">Status</th>
                </tr>
              </thead>
              <tbody>
                {(depreciation.length ? depreciation : [
                  { id: '1', asset_name: 'Dell Server PowerEdge R750', period: 'Jan 2026', opening_value: 350000, depreciation: 12500, closing_value: 337500, status: 'posted' },
                  { id: '2', asset_name: 'Toyota Innova Crysta', period: 'Jan 2026', opening_value: 1600000, depreciation: 60000, closing_value: 1540000, status: 'posted' },
                  { id: '3', asset_name: 'Office Furniture Set', period: 'Jan 2026', opening_value: 325000, depreciation: 10000, closing_value: 315000, status: 'pending' },
                  { id: '4', asset_name: 'CNC Milling Machine', period: 'Jan 2026', opening_value: 6100000, depreciation: 150000, closing_value: 5950000, status: 'pending' },
                ]).map((dep) => (
                  <tr key={dep.id} className="border-t hover:bg-muted/30">
                    <td className="p-4 font-medium">{dep.asset_name}</td>
                    <td className="p-4">{dep.period}</td>
                    <td className="p-4 text-right">{formatCurrency(dep.opening_value)}</td>
                    <td className="p-4 text-right text-red-600">-{formatCurrency(dep.depreciation)}</td>
                    <td className="p-4 text-right font-medium">{formatCurrency(dep.closing_value)}</td>
                    <td className="p-4">
                      <Badge className={statusColors[dep.status]}>
                        {dep.status}
                      </Badge>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </TabsContent>

        <TabsContent value="maintenance" className="mt-4">
          <div className="border rounded-lg overflow-hidden">
            <table className="w-full">
              <thead className="bg-muted/50">
                <tr>
                  <th className="text-left p-4 font-medium">Asset</th>
                  <th className="text-left p-4 font-medium">Type</th>
                  <th className="text-left p-4 font-medium">Scheduled Date</th>
                  <th className="text-left p-4 font-medium">Vendor</th>
                  <th className="text-right p-4 font-medium">Est. Cost</th>
                  <th className="text-left p-4 font-medium">Status</th>
                  <th className="text-right p-4 font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {(maintenance.length ? maintenance : [
                  { id: '1', asset_name: 'CNC Milling Machine', maintenance_type: 'Preventive', scheduled_date: '2026-01-20', vendor: 'Precision Engineering', cost: 45000, status: 'scheduled' },
                  { id: '2', asset_name: 'Dell Server PowerEdge R750', maintenance_type: 'AMC Service', scheduled_date: '2026-01-25', vendor: 'Dell Support', cost: 15000, status: 'scheduled' },
                  { id: '3', asset_name: 'Toyota Innova Crysta', maintenance_type: 'Regular Service', scheduled_date: '2026-01-15', vendor: 'Toyota Authorized', cost: 8500, status: 'overdue' },
                ]).map((maint) => (
                  <tr key={maint.id} className="border-t hover:bg-muted/30">
                    <td className="p-4 font-medium">{maint.asset_name}</td>
                    <td className="p-4">
                      <Badge variant="outline">{maint.maintenance_type}</Badge>
                    </td>
                    <td className="p-4">{maint.scheduled_date}</td>
                    <td className="p-4">{maint.vendor}</td>
                    <td className="p-4 text-right">{formatCurrency(maint.cost)}</td>
                    <td className="p-4">
                      <Badge className={statusColors[maint.status]}>
                        {maint.status}
                      </Badge>
                    </td>
                    <td className="p-4 text-right">
                      <Button variant="ghost" size="icon">
                        <MoreVertical className="h-4 w-4" />
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="mt-4">
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              Schedule Maintenance
            </Button>
          </div>
        </TabsContent>

        <TabsContent value="transfers" className="mt-4">
          <div className="border rounded-lg overflow-hidden">
            <table className="w-full">
              <thead className="bg-muted/50">
                <tr>
                  <th className="text-left p-4 font-medium">Transfer #</th>
                  <th className="text-left p-4 font-medium">Asset</th>
                  <th className="text-left p-4 font-medium">From</th>
                  <th className="text-left p-4 font-medium">To</th>
                  <th className="text-left p-4 font-medium">Date</th>
                  <th className="text-left p-4 font-medium">Status</th>
                  <th className="text-right p-4 font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {(transfers.length ? transfers : [
                  { id: '1', transfer_number: 'TRF-2026-001', asset_name: 'MacBook Pro 16"', from_location: 'Mumbai Office', to_location: 'Delhi Office', transfer_date: '2026-01-12', status: 'completed' },
                  { id: '2', transfer_number: 'TRF-2026-002', asset_name: 'Conference Room Setup', from_location: 'Delhi Office', to_location: 'Bangalore Office', transfer_date: '2026-01-15', status: 'in_transit' },
                  { id: '3', transfer_number: 'TRF-2026-003', asset_name: 'Testing Equipment', from_location: 'Pune Factory', to_location: 'Mumbai Lab', transfer_date: '2026-01-18', status: 'pending' },
                ]).map((transfer) => (
                  <tr key={transfer.id} className="border-t hover:bg-muted/30">
                    <td className="p-4 font-medium">{transfer.transfer_number}</td>
                    <td className="p-4">{transfer.asset_name}</td>
                    <td className="p-4">{transfer.from_location}</td>
                    <td className="p-4">{transfer.to_location}</td>
                    <td className="p-4 text-muted-foreground">{transfer.transfer_date}</td>
                    <td className="p-4">
                      <Badge className={statusColors[transfer.status]}>
                        {transfer.status.replace('_', ' ')}
                      </Badge>
                    </td>
                    <td className="p-4 text-right">
                      <Button variant="ghost" size="icon">
                        <MoreVertical className="h-4 w-4" />
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="mt-4">
            <Button>
              <ArrowRightLeft className="h-4 w-4 mr-2" />
              New Transfer
            </Button>
          </div>
        </TabsContent>

        <TabsContent value="disposals" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Trash2 className="h-5 w-5" />
                Asset Disposals
              </CardTitle>
              <CardDescription>Manage asset write-offs, sales, and scrapping</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="p-4 border rounded-lg flex items-center justify-between">
                  <div>
                    <p className="font-medium">FA-OLD-001 - Old Desktop Computers (5 units)</p>
                    <p className="text-sm text-muted-foreground">Disposed on: 2025-12-15 • Method: Sale • Amount: ₹25,000</p>
                  </div>
                  <Badge className="bg-green-100 text-green-800">Completed</Badge>
                </div>
                <div className="p-4 border rounded-lg flex items-center justify-between">
                  <div>
                    <p className="font-medium">FA-OLD-002 - Office Chairs (10 units)</p>
                    <p className="text-sm text-muted-foreground">Disposed on: 2025-11-20 • Method: Scrap • Amount: ₹5,000</p>
                  </div>
                  <Badge className="bg-green-100 text-green-800">Completed</Badge>
                </div>
              </div>
              <Button className="mt-4">
                <Trash2 className="h-4 w-4 mr-2" />
                Record Disposal
              </Button>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-red-500" />
              Delete Asset
            </AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete <strong>{assetToDelete?.name}</strong> ({assetToDelete?.asset_number})?
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
