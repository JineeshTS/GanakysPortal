'use client';

import { useState, useEffect } from 'react';
import { Plus, Search, ShoppingCart, Package, CreditCard, Store, TrendingUp, Users, MoreVertical, Loader2, IndianRupee, Gift, Trash2, AlertTriangle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { PageHeader } from '@/components/layout/page-header';
import { StatCard } from '@/components/layout/stat-card';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
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
import { useApi, useToast } from '@/hooks';
import { formatCurrency } from '@/lib/format';

interface Product {
  id: string;
  sku: string;
  name: string;
  category: string;
  price: number;
  stock_quantity: number;
  status: string;
  image_url?: string;
}

interface Order {
  id: string;
  order_number: string;
  customer_name: string;
  total_amount: number;
  status: string;
  payment_status: string;
  order_date: string;
  items_count: number;
}

interface POSTerminal {
  id: string;
  terminal_name: string;
  store_name: string;
  status: string;
  current_operator: string | null;
  today_sales: number;
}

const statusColors: Record<string, string> = {
  active: 'bg-green-100 text-green-800',
  inactive: 'bg-gray-100 text-gray-800',
  pending: 'bg-yellow-100 text-yellow-800',
  processing: 'bg-blue-100 text-blue-800',
  shipped: 'bg-purple-100 text-purple-800',
  delivered: 'bg-green-100 text-green-800',
  cancelled: 'bg-red-100 text-red-800',
  paid: 'bg-green-100 text-green-800',
  unpaid: 'bg-red-100 text-red-800',
  out_of_stock: 'bg-red-100 text-red-800',
  low_stock: 'bg-yellow-100 text-yellow-800',
  in_stock: 'bg-green-100 text-green-800',
  online: 'bg-green-100 text-green-800',
  offline: 'bg-gray-100 text-gray-800',
};

export default function EcommercePage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [activeTab, setActiveTab] = useState('products');
  const { showToast } = useToast();
  const deleteApi = useApi();
  const { data: productsData, isLoading: productsLoading, get: getProducts } = useApi<{ data: Product[] }>();
  const { data: ordersData, isLoading: ordersLoading, get: getOrders } = useApi<{ data: Order[] }>();
  const { data: terminalsData, isLoading: terminalsLoading, get: getTerminals } = useApi<{ data: POSTerminal[] }>();

  // Local state for data management
  const [localProducts, setLocalProducts] = useState<Product[]>([]);
  const [localOrders, setLocalOrders] = useState<Order[]>([]);

  // Delete state
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [itemToDelete, setItemToDelete] = useState<{ type: string; item: Product | Order } | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  useEffect(() => {
    getProducts('/ecommerce/products');
    getOrders('/ecommerce/orders');
    getTerminals('/ecommerce/pos/terminals');
  }, [getProducts, getOrders, getTerminals]);

  useEffect(() => {
    if (productsData?.data) {
      setLocalProducts(productsData.data);
    }
  }, [productsData]);

  useEffect(() => {
    if (ordersData?.data) {
      setLocalOrders(ordersData.data);
    }
  }, [ordersData]);

  const handleDeleteClick = (type: string, item: Product | Order) => {
    setItemToDelete({ type, item });
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!itemToDelete) return;
    setIsDeleting(true);
    try {
      const endpoint = itemToDelete.type === "product"
        ? `/ecommerce/products/${itemToDelete.item.id}`
        : `/ecommerce/orders/${itemToDelete.item.id}`;

      await deleteApi.delete(endpoint);

      if (itemToDelete.type === "product") {
        setLocalProducts(localProducts.filter(p => p.id !== itemToDelete.item.id));
      } else {
        setLocalOrders(localOrders.filter(o => o.id !== itemToDelete.item.id));
      }

      setDeleteDialogOpen(false);
      setItemToDelete(null);
      showToast("success", `${itemToDelete.type === "product" ? "Product" : "Order"} deleted successfully`);
    } catch (error) {
      showToast("error", `Failed to delete ${itemToDelete.type}`);
    } finally {
      setIsDeleting(false);
    }
  };

  const products = localProducts.length ? localProducts : productsData?.data || [];
  const orders = localOrders.length ? localOrders : ordersData?.data || [];
  const terminals = terminalsData?.data || [];
  const isLoading = productsLoading || ordersLoading || terminalsLoading;

  const stats = {
    totalProducts: products.length || 156,
    totalOrders: orders.length || 342,
    todaySales: 245000,
    activeTerminals: terminals.filter(t => t.status === 'online').length || 4,
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="E-commerce & POS"
        description="Manage products, online orders, POS terminals, and loyalty programs"
        actions={
          <Button>
            <Plus className="h-4 w-4 mr-2" />
            Add Product
          </Button>
        }
      />

      {isLoading && (
        <Card className="p-8 flex items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <span className="ml-2">Loading e-commerce data...</span>
        </Card>
      )}

      <div className="grid gap-4 md:grid-cols-4">
        <StatCard
          title="Products"
          value={stats.totalProducts}
          icon={Package}
          description="Active catalog items"
        />
        <StatCard
          title="Orders Today"
          value={orders.filter(o => o.order_date === new Date().toISOString().split('T')[0]).length || 28}
          icon={ShoppingCart}
          description="New orders"
        />
        <StatCard
          title="Today's Sales"
          value={formatCurrency(stats.todaySales)}
          icon={IndianRupee}
          description="Combined POS & Online"
          trend={{ value: 12.5, type: 'increase' }}
        />
        <StatCard
          title="Active POS"
          value={stats.activeTerminals}
          icon={Store}
          description="Terminals online"
        />
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="products">Products</TabsTrigger>
          <TabsTrigger value="orders">Orders</TabsTrigger>
          <TabsTrigger value="pos">POS Terminals</TabsTrigger>
          <TabsTrigger value="loyalty">Loyalty Program</TabsTrigger>
        </TabsList>

        <TabsContent value="products" className="mt-4">
          <div className="flex gap-4 mb-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search products..."
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
                  <th className="text-left p-4 font-medium">Product</th>
                  <th className="text-left p-4 font-medium">SKU</th>
                  <th className="text-left p-4 font-medium">Category</th>
                  <th className="text-right p-4 font-medium">Price</th>
                  <th className="text-right p-4 font-medium">Stock</th>
                  <th className="text-left p-4 font-medium">Status</th>
                  <th className="text-right p-4 font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {(products.length ? products : [
                  { id: '1', sku: 'PRD-001', name: 'Premium Wireless Headphones', category: 'Electronics', price: 4999, stock_quantity: 45, status: 'in_stock' },
                  { id: '2', sku: 'PRD-002', name: 'Organic Cotton T-Shirt', category: 'Apparel', price: 899, stock_quantity: 120, status: 'in_stock' },
                  { id: '3', sku: 'PRD-003', name: 'Stainless Steel Water Bottle', category: 'Accessories', price: 599, stock_quantity: 8, status: 'low_stock' },
                  { id: '4', sku: 'PRD-004', name: 'Yoga Mat Premium', category: 'Fitness', price: 1499, stock_quantity: 0, status: 'out_of_stock' },
                ]).map((product) => (
                  <tr key={product.id} className="border-t hover:bg-muted/30">
                    <td className="p-4 font-medium">{product.name}</td>
                    <td className="p-4 text-muted-foreground">{product.sku}</td>
                    <td className="p-4">{product.category}</td>
                    <td className="p-4 text-right">{formatCurrency(product.price)}</td>
                    <td className="p-4 text-right">{product.stock_quantity}</td>
                    <td className="p-4">
                      <Badge className={statusColors[product.status]}>
                        {product.status.replace('_', ' ')}
                      </Badge>
                    </td>
                    <td className="p-4 text-right">
                      <div className="flex justify-end gap-1">
                        <Button variant="ghost" size="icon">
                          <MoreVertical className="h-4 w-4" />
                        </Button>
                        {product.status === 'out_of_stock' && (
                          <Button
                            variant="ghost"
                            size="icon"
                            className="text-red-600 hover:text-red-700 hover:bg-red-50"
                            onClick={() => handleDeleteClick('product', product)}
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

        <TabsContent value="orders" className="mt-4">
          <div className="border rounded-lg overflow-hidden">
            <table className="w-full">
              <thead className="bg-muted/50">
                <tr>
                  <th className="text-left p-4 font-medium">Order #</th>
                  <th className="text-left p-4 font-medium">Customer</th>
                  <th className="text-center p-4 font-medium">Items</th>
                  <th className="text-right p-4 font-medium">Amount</th>
                  <th className="text-left p-4 font-medium">Status</th>
                  <th className="text-left p-4 font-medium">Payment</th>
                  <th className="text-left p-4 font-medium">Date</th>
                  <th className="text-right p-4 font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {(orders.length ? orders : [
                  { id: '1', order_number: 'ORD-2026-0001', customer_name: 'Rahul Sharma', items_count: 3, total_amount: 12500, status: 'processing', payment_status: 'paid', order_date: '2026-01-15' },
                  { id: '2', order_number: 'ORD-2026-0002', customer_name: 'Priya Patel', items_count: 1, total_amount: 4999, status: 'shipped', payment_status: 'paid', order_date: '2026-01-15' },
                  { id: '3', order_number: 'ORD-2026-0003', customer_name: 'Amit Kumar', items_count: 5, total_amount: 8750, status: 'pending', payment_status: 'unpaid', order_date: '2026-01-14' },
                ]).map((order) => (
                  <tr key={order.id} className="border-t hover:bg-muted/30">
                    <td className="p-4 font-medium">{order.order_number}</td>
                    <td className="p-4">{order.customer_name}</td>
                    <td className="p-4 text-center">{order.items_count}</td>
                    <td className="p-4 text-right">{formatCurrency(order.total_amount)}</td>
                    <td className="p-4">
                      <Badge className={statusColors[order.status]}>
                        {order.status}
                      </Badge>
                    </td>
                    <td className="p-4">
                      <Badge className={statusColors[order.payment_status]}>
                        {order.payment_status}
                      </Badge>
                    </td>
                    <td className="p-4 text-muted-foreground">{order.order_date}</td>
                    <td className="p-4 text-right">
                      <div className="flex justify-end gap-1">
                        <Button variant="ghost" size="icon">
                          <MoreVertical className="h-4 w-4" />
                        </Button>
                        {order.status === 'cancelled' && (
                          <Button
                            variant="ghost"
                            size="icon"
                            className="text-red-600 hover:text-red-700 hover:bg-red-50"
                            onClick={() => handleDeleteClick('order', order)}
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

        <TabsContent value="pos" className="mt-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {(terminals.length ? terminals : [
              { id: '1', terminal_name: 'POS-001', store_name: 'Mumbai Main Store', status: 'online', current_operator: 'Ramesh Kumar', today_sales: 85000 },
              { id: '2', terminal_name: 'POS-002', store_name: 'Mumbai Main Store', status: 'online', current_operator: 'Priya Shah', today_sales: 62000 },
              { id: '3', terminal_name: 'POS-003', store_name: 'Delhi Outlet', status: 'online', current_operator: 'Amit Singh', today_sales: 48000 },
              { id: '4', terminal_name: 'POS-004', store_name: 'Bangalore Store', status: 'offline', current_operator: null, today_sales: 0 },
            ]).map((terminal) => (
              <Card key={terminal.id} className="hover:shadow-md transition-shadow">
                <CardHeader className="pb-2">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-sm font-medium">{terminal.terminal_name}</CardTitle>
                    <Badge className={statusColors[terminal.status]}>
                      {terminal.status}
                    </Badge>
                  </div>
                  <p className="text-xs text-muted-foreground">{terminal.store_name}</p>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <div>
                      <p className="text-xs text-muted-foreground">Operator</p>
                      <p className="font-medium text-sm">{terminal.current_operator || 'Not assigned'}</p>
                    </div>
                    <div>
                      <p className="text-xs text-muted-foreground">Today's Sales</p>
                      <p className="font-bold text-lg text-green-600">{formatCurrency(terminal.today_sales)}</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="loyalty" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Gift className="h-5 w-5" />
                Loyalty Programs
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="p-4 bg-purple-50 rounded-lg">
                  <p className="text-sm text-muted-foreground">Active Members</p>
                  <p className="text-2xl font-bold">2,456</p>
                </div>
                <div className="p-4 bg-blue-50 rounded-lg">
                  <p className="text-sm text-muted-foreground">Points Issued</p>
                  <p className="text-2xl font-bold">1.2M</p>
                </div>
                <div className="p-4 bg-green-50 rounded-lg">
                  <p className="text-sm text-muted-foreground">Points Redeemed</p>
                  <p className="text-2xl font-bold">890K</p>
                </div>
              </div>
              <Button className="mt-4">
                <Plus className="h-4 w-4 mr-2" />
                Create Program
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
              Delete {itemToDelete?.type === 'product' ? 'Product' : 'Order'}
            </AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete{' '}
              <strong>
                {itemToDelete?.type === 'product'
                  ? (itemToDelete.item as Product).name
                  : (itemToDelete?.item as Order).order_number}
              </strong>?
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
                "Delete"
              )}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
