'use client';

import { useState, useEffect } from 'react';
import { Plus, Search, Laptop, Car, Building, Printer, Package, MoreVertical, TrendingDown, AlertCircle, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { PageHeader } from '@/components/layout/page-header';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useApi } from '@/hooks';

// API Response interfaces
interface Asset {
  id: string;
  asset_code: string;
  name: string;
  category_id: string;
  category_name: string;
  purchase_date: string;
  purchase_value: number;
  current_value: number;
  assigned_to: string | null;
  assigned_to_name: string | null;
  status: string;
  location: string;
}

interface AssetCategory {
  id: string;
  name: string;
  code: string;
  asset_count: number;
  total_value: number;
  depreciation_rate: number;
  depreciation_method: string;
}

interface AssetListResponse {
  assets: Asset[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

interface AssetSummary {
  total_assets: number;
  total_purchase_value: number;
  total_current_value: number;
  total_depreciation: number;
  assets_for_disposal: number;
  by_status: {
    in_use: number;
    available: number;
    maintenance: number;
    disposed: number;
  };
  by_category: AssetCategory[];
}

const assetCategories = [
  { name: 'IT Equipment', icon: Laptop, count: 45, value: 2500000 },
  { name: 'Vehicles', icon: Car, count: 5, value: 3500000 },
  { name: 'Furniture', icon: Building, count: 120, value: 800000 },
  { name: 'Office Equipment', icon: Printer, count: 25, value: 350000 },
  { name: 'Other', icon: Package, count: 15, value: 200000 },
];

const sampleAssets = [
  {
    id: 'AST-001',
    name: 'Dell Latitude 5520',
    category: 'IT Equipment',
    purchaseDate: '2023-06-15',
    purchaseValue: 85000,
    currentValue: 68000,
    assignedTo: 'John Doe',
    status: 'in_use',
    location: 'Mumbai Office',
  },
  {
    id: 'AST-002',
    name: 'Toyota Innova',
    category: 'Vehicles',
    purchaseDate: '2022-01-10',
    purchaseValue: 1800000,
    currentValue: 1440000,
    assignedTo: 'Company Pool',
    status: 'in_use',
    location: 'Mumbai Office',
  },
  {
    id: 'AST-003',
    name: 'HP LaserJet Pro',
    category: 'Office Equipment',
    purchaseDate: '2023-03-20',
    purchaseValue: 45000,
    currentValue: 36000,
    assignedTo: 'HR Department',
    status: 'in_use',
    location: 'Mumbai Office',
  },
  {
    id: 'AST-004',
    name: 'MacBook Pro 16"',
    category: 'IT Equipment',
    purchaseDate: '2024-01-05',
    purchaseValue: 250000,
    currentValue: 237500,
    assignedTo: 'Jane Smith',
    status: 'in_use',
    location: 'Bangalore Office',
  },
];

const statusColors: Record<string, string> = {
  in_use: 'bg-green-100 text-green-800',
  available: 'bg-blue-100 text-blue-800',
  maintenance: 'bg-yellow-100 text-yellow-800',
  disposed: 'bg-gray-100 text-gray-800',
};

export default function AssetsPage() {
  const [searchQuery, setSearchQuery] = useState('');

  const { data: assetsData, isLoading: assetsLoading, error: assetsError, get: getAssets } = useApi<AssetListResponse>();
  const { data: summaryData, isLoading: summaryLoading, get: getSummary } = useApi<AssetSummary>();

  // Fetch assets and summary on mount
  useEffect(() => {
    const params = new URLSearchParams();
    if (searchQuery) params.set('search', searchQuery);

    getAssets(`/assets?${params.toString()}`);
    getSummary('/assets/summary');
  }, [searchQuery, getAssets, getSummary]);

  const assets = assetsData?.assets || sampleAssets.map(a => ({
    id: a.id,
    asset_code: a.id,
    name: a.name,
    category_id: '',
    category_name: a.category,
    purchase_date: a.purchaseDate,
    purchase_value: a.purchaseValue,
    current_value: a.currentValue,
    assigned_to: null,
    assigned_to_name: a.assignedTo,
    status: a.status,
    location: a.location,
  }));
  const isLoading = assetsLoading || summaryLoading;

  const totalValue = summaryData?.total_current_value || assetCategories.reduce((sum, cat) => sum + cat.value, 0);
  const totalAssets = summaryData?.total_assets || assetCategories.reduce((sum, cat) => sum + cat.count, 0);

  return (
    <div className="space-y-6">
      <PageHeader
        title="Asset Management"
        description="Track and manage company fixed assets"
      >
        <Button>
          <Plus className="h-4 w-4 mr-2" />
          Add Asset
        </Button>
      </PageHeader>

      {/* Loading State */}
      {isLoading && (
        <Card className="p-8 flex items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <span className="ml-2">Loading assets...</span>
        </Card>
      )}

      {/* Error State */}
      {assetsError && (
        <Card className="p-4 border-red-200 bg-red-50">
          <div className="flex items-center gap-2 text-red-600">
            <AlertCircle className="h-5 w-5" />
            <span>{assetsError}</span>
          </div>
        </Card>
      )}

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Total Assets
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{totalAssets}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Total Value
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              ₹{(totalValue / 100000).toFixed(1)}L
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              This Year Depreciation
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">
              ₹{((summaryData?.total_depreciation || 1250000) / 100000).toFixed(1)}L
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Assets for Disposal
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{summaryData?.assets_for_disposal || 8}</div>
          </CardContent>
        </Card>
      </div>

      {/* Categories */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        {assetCategories.map((category) => {
          const Icon = category.icon;
          return (
            <Card key={category.name} className="cursor-pointer hover:shadow-md transition-shadow">
              <CardContent className="pt-6">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-primary/10 rounded-lg">
                    <Icon className="h-5 w-5 text-primary" />
                  </div>
                  <div>
                    <div className="font-medium text-sm">{category.name}</div>
                    <div className="text-xs text-muted-foreground">
                      {category.count} items
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      <Tabs defaultValue="all">
        <TabsList>
          <TabsTrigger value="all">All Assets</TabsTrigger>
          <TabsTrigger value="depreciation">Depreciation</TabsTrigger>
          <TabsTrigger value="disposal">For Disposal</TabsTrigger>
        </TabsList>

        <TabsContent value="all" className="mt-4">
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
                  <th className="text-left p-4 font-medium">Asset ID</th>
                  <th className="text-left p-4 font-medium">Name</th>
                  <th className="text-left p-4 font-medium">Category</th>
                  <th className="text-right p-4 font-medium">Purchase Value</th>
                  <th className="text-right p-4 font-medium">Current Value</th>
                  <th className="text-left p-4 font-medium">Assigned To</th>
                  <th className="text-left p-4 font-medium">Status</th>
                  <th className="text-right p-4 font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {assets.map((asset) => (
                  <tr key={asset.id} className="border-t hover:bg-muted/30">
                    <td className="p-4 font-medium">{asset.asset_code}</td>
                    <td className="p-4">{asset.name}</td>
                    <td className="p-4 text-muted-foreground">{asset.category_name}</td>
                    <td className="p-4 text-right">
                      ₹{asset.purchase_value.toLocaleString('en-IN')}
                    </td>
                    <td className="p-4 text-right">
                      <div className="flex items-center justify-end gap-1">
                        <TrendingDown className="h-3 w-3 text-red-500" />
                        ₹{asset.current_value.toLocaleString('en-IN')}
                      </div>
                    </td>
                    <td className="p-4">{asset.assigned_to_name || '-'}</td>
                    <td className="p-4">
                      <Badge className={statusColors[asset.status] || statusColors.available}>
                        {asset.status.replace('_', ' ')}
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
      </Tabs>
    </div>
  );
}
