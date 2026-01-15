'use client';

import { useState, useEffect } from 'react';
import { Plus, Search, Warehouse, Truck, Package, Users, TrendingUp, AlertTriangle, MoreVertical, Loader2, BarChart3 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { PageHeader } from '@/components/layout/page-header';
import { StatCard } from '@/components/layout/stat-card';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useApi } from '@/hooks';
import { formatCurrency } from '@/lib/format';

interface WarehouseSummary {
  id: string;
  name: string;
  code: string;
  warehouse_type: string;
  location: string;
  total_items: number;
  total_value: number;
  utilization: number;
  is_active: boolean;
}

interface SupplierSummary {
  id: string;
  name: string;
  code: string;
  tier: string;
  status: string;
  rating: number;
  total_orders: number;
  on_time_delivery: number;
}

interface TransferSummary {
  id: string;
  transfer_number: string;
  from_warehouse: string;
  to_warehouse: string;
  status: string;
  items_count: number;
  requested_date: string;
}

const statusColors: Record<string, string> = {
  active: 'bg-green-100 text-green-800',
  inactive: 'bg-gray-100 text-gray-800',
  pending: 'bg-yellow-100 text-yellow-800',
  approved: 'bg-blue-100 text-blue-800',
  in_transit: 'bg-purple-100 text-purple-800',
  completed: 'bg-green-100 text-green-800',
  blacklisted: 'bg-red-100 text-red-800',
};

const tierColors: Record<string, string> = {
  strategic: 'bg-purple-100 text-purple-800',
  preferred: 'bg-blue-100 text-blue-800',
  approved: 'bg-green-100 text-green-800',
  probationary: 'bg-yellow-100 text-yellow-800',
};

export default function SupplyChainPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [activeTab, setActiveTab] = useState('warehouses');
  const { data: warehousesData, isLoading: warehousesLoading, get: getWarehouses } = useApi<{ data: WarehouseSummary[] }>();
  const { data: suppliersData, isLoading: suppliersLoading, get: getSuppliers } = useApi<{ data: SupplierSummary[] }>();
  const { data: transfersData, isLoading: transfersLoading, get: getTransfers } = useApi<{ data: TransferSummary[] }>();

  useEffect(() => {
    getWarehouses('/supply-chain/warehouses');
    getSuppliers('/supply-chain/suppliers');
    getTransfers('/supply-chain/transfers');
  }, [getWarehouses, getSuppliers, getTransfers]);

  const warehouses = warehousesData?.data || [];
  const suppliers = suppliersData?.data || [];
  const transfers = transfersData?.data || [];
  const isLoading = warehousesLoading || suppliersLoading || transfersLoading;

  const stats = {
    totalWarehouses: warehouses.length || 5,
    totalSuppliers: suppliers.length || 42,
    pendingTransfers: transfers.filter(t => t.status === 'pending').length || 8,
    lowStockAlerts: 12,
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Supply Chain Management"
        description="Manage warehouses, suppliers, inventory, and stock transfers"
        actions={
          <Button>
            <Plus className="h-4 w-4 mr-2" />
            Add Warehouse
          </Button>
        }
      />

      {isLoading && (
        <Card className="p-8 flex items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <span className="ml-2">Loading supply chain data...</span>
        </Card>
      )}

      <div className="grid gap-4 md:grid-cols-4">
        <StatCard
          title="Warehouses"
          value={stats.totalWarehouses}
          icon={Warehouse}
          description="Active locations"
        />
        <StatCard
          title="Suppliers"
          value={stats.totalSuppliers}
          icon={Users}
          description="Registered vendors"
        />
        <StatCard
          title="Pending Transfers"
          value={stats.pendingTransfers}
          icon={Truck}
          description="Awaiting action"
        />
        <StatCard
          title="Low Stock Alerts"
          value={stats.lowStockAlerts}
          icon={AlertTriangle}
          description="Items below reorder level"
          className="border-orange-200 bg-orange-50"
        />
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="warehouses">Warehouses</TabsTrigger>
          <TabsTrigger value="suppliers">Suppliers</TabsTrigger>
          <TabsTrigger value="transfers">Stock Transfers</TabsTrigger>
          <TabsTrigger value="forecasts">Demand Forecasts</TabsTrigger>
        </TabsList>

        <TabsContent value="warehouses" className="mt-4">
          <div className="flex gap-4 mb-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search warehouses..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-9"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {(warehouses.length ? warehouses : [
              { id: '1', name: 'Mumbai Central Warehouse', code: 'WH-MUM-01', warehouse_type: 'main', location: 'Mumbai', total_items: 1250, total_value: 45000000, utilization: 78, is_active: true },
              { id: '2', name: 'Delhi Distribution Center', code: 'WH-DEL-01', warehouse_type: 'distribution', location: 'Delhi NCR', total_items: 890, total_value: 32000000, utilization: 65, is_active: true },
              { id: '3', name: 'Bangalore Tech Hub', code: 'WH-BLR-01', warehouse_type: 'transit', location: 'Bangalore', total_items: 450, total_value: 18000000, utilization: 45, is_active: true },
            ]).map((warehouse) => (
              <Card key={warehouse.id} className="hover:shadow-md transition-shadow cursor-pointer">
                <CardHeader className="pb-2">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-sm font-medium">{warehouse.name}</CardTitle>
                    <Badge className={warehouse.is_active ? statusColors.active : statusColors.inactive}>
                      {warehouse.is_active ? 'Active' : 'Inactive'}
                    </Badge>
                  </div>
                  <p className="text-xs text-muted-foreground">{warehouse.code} • {warehouse.location}</p>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <p className="text-muted-foreground text-xs">Items</p>
                      <p className="font-medium">{warehouse.total_items.toLocaleString()}</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground text-xs">Value</p>
                      <p className="font-medium">{formatCurrency(warehouse.total_value)}</p>
                    </div>
                  </div>
                  <div className="mt-3">
                    <div className="flex justify-between text-xs mb-1">
                      <span className="text-muted-foreground">Utilization</span>
                      <span className="font-medium">{warehouse.utilization}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-primary rounded-full h-2"
                        style={{ width: `${warehouse.utilization}%` }}
                      />
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="suppliers" className="mt-4">
          <div className="border rounded-lg overflow-hidden">
            <table className="w-full">
              <thead className="bg-muted/50">
                <tr>
                  <th className="text-left p-4 font-medium">Supplier</th>
                  <th className="text-left p-4 font-medium">Code</th>
                  <th className="text-left p-4 font-medium">Tier</th>
                  <th className="text-center p-4 font-medium">Rating</th>
                  <th className="text-right p-4 font-medium">Total Orders</th>
                  <th className="text-right p-4 font-medium">On-Time %</th>
                  <th className="text-left p-4 font-medium">Status</th>
                  <th className="text-right p-4 font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {(suppliers.length ? suppliers : [
                  { id: '1', name: 'Tata Steel Ltd', code: 'SUP-001', tier: 'strategic', status: 'active', rating: 4.8, total_orders: 156, on_time_delivery: 98 },
                  { id: '2', name: 'Reliance Industries', code: 'SUP-002', tier: 'strategic', status: 'active', rating: 4.6, total_orders: 89, on_time_delivery: 95 },
                  { id: '3', name: 'Mahindra Components', code: 'SUP-003', tier: 'preferred', status: 'active', rating: 4.2, total_orders: 67, on_time_delivery: 92 },
                ]).map((supplier) => (
                  <tr key={supplier.id} className="border-t hover:bg-muted/30">
                    <td className="p-4 font-medium">{supplier.name}</td>
                    <td className="p-4 text-muted-foreground">{supplier.code}</td>
                    <td className="p-4">
                      <Badge className={tierColors[supplier.tier] || tierColors.approved}>
                        {supplier.tier}
                      </Badge>
                    </td>
                    <td className="p-4 text-center">
                      <span className="font-medium">{supplier.rating}</span>
                      <span className="text-yellow-500 ml-1">★</span>
                    </td>
                    <td className="p-4 text-right">{supplier.total_orders}</td>
                    <td className="p-4 text-right">
                      <span className={supplier.on_time_delivery >= 95 ? 'text-green-600' : 'text-yellow-600'}>
                        {supplier.on_time_delivery}%
                      </span>
                    </td>
                    <td className="p-4">
                      <Badge className={statusColors[supplier.status]}>
                        {supplier.status}
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
        </TabsContent>

        <TabsContent value="transfers" className="mt-4">
          <div className="border rounded-lg overflow-hidden">
            <table className="w-full">
              <thead className="bg-muted/50">
                <tr>
                  <th className="text-left p-4 font-medium">Transfer #</th>
                  <th className="text-left p-4 font-medium">From</th>
                  <th className="text-left p-4 font-medium">To</th>
                  <th className="text-center p-4 font-medium">Items</th>
                  <th className="text-left p-4 font-medium">Status</th>
                  <th className="text-left p-4 font-medium">Date</th>
                  <th className="text-right p-4 font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {(transfers.length ? transfers : [
                  { id: '1', transfer_number: 'TRF-2026-001', from_warehouse: 'Mumbai Central', to_warehouse: 'Delhi Distribution', status: 'in_transit', items_count: 45, requested_date: '2026-01-14' },
                  { id: '2', transfer_number: 'TRF-2026-002', from_warehouse: 'Delhi Distribution', to_warehouse: 'Bangalore Hub', status: 'pending', items_count: 23, requested_date: '2026-01-15' },
                  { id: '3', transfer_number: 'TRF-2026-003', from_warehouse: 'Mumbai Central', to_warehouse: 'Chennai Branch', status: 'approved', items_count: 67, requested_date: '2026-01-13' },
                ]).map((transfer) => (
                  <tr key={transfer.id} className="border-t hover:bg-muted/30">
                    <td className="p-4 font-medium">{transfer.transfer_number}</td>
                    <td className="p-4">{transfer.from_warehouse}</td>
                    <td className="p-4">{transfer.to_warehouse}</td>
                    <td className="p-4 text-center">{transfer.items_count}</td>
                    <td className="p-4">
                      <Badge className={statusColors[transfer.status]}>
                        {transfer.status.replace('_', ' ')}
                      </Badge>
                    </td>
                    <td className="p-4 text-muted-foreground">{transfer.requested_date}</td>
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
        </TabsContent>

        <TabsContent value="forecasts" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="h-5 w-5" />
                Demand Forecasting
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground">
                View demand forecasts, generate predictions using historical data, and plan inventory accordingly.
              </p>
              <Button className="mt-4">
                <TrendingUp className="h-4 w-4 mr-2" />
                Generate Forecast
              </Button>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
