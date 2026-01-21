"use client";
import { useState } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useApi, useToast } from "@/hooks";
import {
  Factory,
  Cog,
  Package,
  ClipboardList,
  Search,
  Plus,
  Download,
  Filter,
  Play,
  Pause,
  CheckCircle,
  Clock,
  AlertTriangle,
  Wrench,
  BarChart3,
  Calendar,
  Eye,
  Settings,
  Trash2,
  Loader2,
} from "lucide-react";

// Mock data
const productionOrders = [
  {
    id: "1",
    orderNumber: "PO-000001",
    product: "Industrial Pump Model A",
    quantity: 100,
    completed: 45,
    status: "in_progress",
    priority: "high",
    startDate: "2026-01-10",
    endDate: "2026-01-25",
    workCenter: "Assembly Line 1",
  },
  {
    id: "2",
    orderNumber: "PO-000002",
    product: "Motor Assembly B",
    quantity: 200,
    completed: 0,
    status: "released",
    priority: "medium",
    startDate: "2026-01-15",
    endDate: "2026-01-30",
    workCenter: "Machine Shop",
  },
  {
    id: "3",
    orderNumber: "PO-000003",
    product: "Valve Kit C",
    quantity: 500,
    completed: 500,
    status: "completed",
    priority: "low",
    startDate: "2026-01-01",
    endDate: "2026-01-10",
    workCenter: "Finishing Station",
  },
];

const workCenters = [
  {
    id: "1",
    code: "WC-001",
    name: "Assembly Line 1",
    type: "assembly",
    status: "active",
    capacity: 100,
    utilization: 85,
    currentJob: "PO-000001",
  },
  {
    id: "2",
    code: "WC-002",
    name: "Machine Shop",
    type: "machine",
    status: "active",
    capacity: 50,
    utilization: 72,
    currentJob: null,
  },
  {
    id: "3",
    code: "WC-003",
    name: "Finishing Station",
    type: "finishing",
    status: "maintenance",
    capacity: 200,
    utilization: 0,
    currentJob: null,
  },
];

const boms = [
  {
    id: "1",
    bomNumber: "BOM-000001",
    product: "Industrial Pump Model A",
    version: 1,
    status: "active",
    components: 12,
    totalCost: 15000,
  },
  {
    id: "2",
    bomNumber: "BOM-000002",
    product: "Motor Assembly B",
    version: 2,
    status: "active",
    components: 8,
    totalCost: 8500,
  },
];

interface ProductionOrder {
  id: string;
  orderNumber: string;
  product: string;
  quantity: number;
  completed: number;
  status: string;
  priority: string;
  startDate: string;
  endDate: string;
  workCenter: string;
}

export default function ManufacturingPage() {
  const [activeTab, setActiveTab] = useState("dashboard");
  const [searchTerm, setSearchTerm] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const { showToast } = useToast();
  const deleteApi = useApi();

  // Local state for production orders
  const [orders, setOrders] = useState<ProductionOrder[]>(productionOrders);

  // Delete state
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [orderToDelete, setOrderToDelete] = useState<ProductionOrder | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  const handleDeleteClick = (order: ProductionOrder) => {
    setOrderToDelete(order);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!orderToDelete) return;
    setIsDeleting(true);
    try {
      await deleteApi.delete(`/manufacturing/orders/${orderToDelete.id}`);
      setOrders(orders.filter(o => o.id !== orderToDelete.id));
      setDeleteDialogOpen(false);
      setOrderToDelete(null);
      showToast("success", "Production order deleted successfully");
    } catch (error) {
      showToast("error", "Failed to delete production order");
    } finally {
      setIsDeleting(false);
    }
  };

  const getStatusBadge = (status: string) => {
    const styles: Record<string, string> = {
      draft: "bg-gray-100 text-gray-800",
      planned: "bg-blue-100 text-blue-800",
      released: "bg-purple-100 text-purple-800",
      in_progress: "bg-yellow-100 text-yellow-800",
      completed: "bg-green-100 text-green-800",
      cancelled: "bg-red-100 text-red-800",
      active: "bg-green-100 text-green-800",
      maintenance: "bg-orange-100 text-orange-800",
      inactive: "bg-gray-100 text-gray-800",
    };
    return styles[status] || "bg-gray-100 text-gray-800";
  };

  const getPriorityBadge = (priority: string) => {
    const styles: Record<string, string> = {
      urgent: "bg-red-100 text-red-800",
      high: "bg-orange-100 text-orange-800",
      medium: "bg-yellow-100 text-yellow-800",
      low: "bg-green-100 text-green-800",
    };
    return styles[priority] || "bg-gray-100 text-gray-800";
  };

  const filteredOrders = orders.filter((order) => {
    const matchesSearch =
      order.orderNumber.toLowerCase().includes(searchTerm.toLowerCase()) ||
      order.product.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus =
      statusFilter === "all" || order.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  return (
    <div className="flex flex-col gap-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Manufacturing</h1>
          <p className="text-muted-foreground">
            Production planning, BOM, and shop floor management
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline">
            <Download className="mr-2 h-4 w-4" />
            Export
          </Button>
          <Dialog>
            <DialogTrigger asChild>
              <Button>
                <Plus className="mr-2 h-4 w-4" />
                New Production Order
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
                    <Select>
                      <SelectTrigger>
                        <SelectValue placeholder="Select product" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="pump_a">Industrial Pump Model A</SelectItem>
                        <SelectItem value="motor_b">Motor Assembly B</SelectItem>
                        <SelectItem value="valve_c">Valve Kit C</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label>BOM</Label>
                    <Select>
                      <SelectTrigger>
                        <SelectValue placeholder="Select BOM" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="bom1">BOM-000001</SelectItem>
                        <SelectItem value="bom2">BOM-000002</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>Quantity</Label>
                    <Input type="number" placeholder="Enter quantity" />
                  </div>
                  <div className="space-y-2">
                    <Label>Priority</Label>
                    <Select>
                      <SelectTrigger>
                        <SelectValue placeholder="Select priority" />
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
                    <Label>Planned Start Date</Label>
                    <Input type="date" />
                  </div>
                  <div className="space-y-2">
                    <Label>Planned End Date</Label>
                    <Input type="date" />
                  </div>
                </div>
              </div>
              <DialogFooter>
                <Button variant="outline">Cancel</Button>
                <Button>Create Order</Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="dashboard">
            <BarChart3 className="mr-2 h-4 w-4" />
            Dashboard
          </TabsTrigger>
          <TabsTrigger value="orders">
            <ClipboardList className="mr-2 h-4 w-4" />
            Production Orders
          </TabsTrigger>
          <TabsTrigger value="bom">
            <Package className="mr-2 h-4 w-4" />
            Bill of Materials
          </TabsTrigger>
          <TabsTrigger value="workcenters">
            <Cog className="mr-2 h-4 w-4" />
            Work Centers
          </TabsTrigger>
          <TabsTrigger value="scheduling">
            <Calendar className="mr-2 h-4 w-4" />
            Scheduling
          </TabsTrigger>
        </TabsList>

        <TabsContent value="dashboard" className="space-y-6">
          {/* KPI Cards */}
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium">
                  Active Orders
                </CardTitle>
                <Factory className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">12</div>
                <p className="text-xs text-muted-foreground">
                  3 released, 9 in progress
                </p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium">
                  Completed Today
                </CardTitle>
                <CheckCircle className="h-4 w-4 text-green-500" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-green-600">847</div>
                <p className="text-xs text-muted-foreground">Units produced</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium">OEE</CardTitle>
                <BarChart3 className="h-4 w-4 text-blue-500" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-blue-600">77.2%</div>
                <p className="text-xs text-muted-foreground">
                  Overall Equipment Effectiveness
                </p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium">
                  Work Centers
                </CardTitle>
                <Cog className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">8/10</div>
                <p className="text-xs text-muted-foreground">Active / Total</p>
              </CardContent>
            </Card>
          </div>

          {/* OEE Breakdown */}
          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>OEE Breakdown</CardTitle>
                <CardDescription>Performance metrics for today</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <div className="flex justify-between mb-1">
                      <span className="text-sm">Availability</span>
                      <span className="text-sm font-medium">85.5%</span>
                    </div>
                    <div className="h-2 bg-gray-200 rounded">
                      <div
                        className="h-2 bg-green-500 rounded"
                        style={{ width: "85.5%" }}
                      />
                    </div>
                  </div>
                  <div>
                    <div className="flex justify-between mb-1">
                      <span className="text-sm">Performance</span>
                      <span className="text-sm font-medium">92.3%</span>
                    </div>
                    <div className="h-2 bg-gray-200 rounded">
                      <div
                        className="h-2 bg-blue-500 rounded"
                        style={{ width: "92.3%" }}
                      />
                    </div>
                  </div>
                  <div>
                    <div className="flex justify-between mb-1">
                      <span className="text-sm">Quality</span>
                      <span className="text-sm font-medium">98.1%</span>
                    </div>
                    <div className="h-2 bg-gray-200 rounded">
                      <div
                        className="h-2 bg-purple-500 rounded"
                        style={{ width: "98.1%" }}
                      />
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Production Status</CardTitle>
                <CardDescription>Orders by current status</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div className="h-3 w-3 rounded-full bg-yellow-500" />
                      <span>In Progress</span>
                    </div>
                    <span className="font-medium">9 orders</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div className="h-3 w-3 rounded-full bg-purple-500" />
                      <span>Released</span>
                    </div>
                    <span className="font-medium">3 orders</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div className="h-3 w-3 rounded-full bg-blue-500" />
                      <span>Planned</span>
                    </div>
                    <span className="font-medium">5 orders</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div className="h-3 w-3 rounded-full bg-green-500" />
                      <span>Completed (MTD)</span>
                    </div>
                    <span className="font-medium">23 orders</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="orders" className="space-y-4">
          <div className="flex items-center gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search orders..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-8"
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
              </SelectContent>
            </Select>
          </div>

          <Card>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Order #</TableHead>
                  <TableHead>Product</TableHead>
                  <TableHead>Quantity</TableHead>
                  <TableHead>Progress</TableHead>
                  <TableHead>Priority</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Work Center</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredOrders.map((order) => (
                  <TableRow key={order.id}>
                    <TableCell className="font-medium">
                      {order.orderNumber}
                    </TableCell>
                    <TableCell>{order.product}</TableCell>
                    <TableCell>
                      {order.completed} / {order.quantity}
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <div className="h-2 w-24 bg-gray-200 rounded">
                          <div
                            className="h-2 bg-green-500 rounded"
                            style={{
                              width: `${(order.completed / order.quantity) * 100}%`,
                            }}
                          />
                        </div>
                        <span className="text-sm">
                          {Math.round((order.completed / order.quantity) * 100)}%
                        </span>
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge className={getPriorityBadge(order.priority)}>
                        {order.priority}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Badge className={getStatusBadge(order.status)}>
                        {order.status.replace("_", " ")}
                      </Badge>
                    </TableCell>
                    <TableCell>{order.workCenter}</TableCell>
                    <TableCell>
                      <div className="flex gap-1">
                        <Button variant="ghost" size="sm">
                          <Eye className="h-4 w-4" />
                        </Button>
                        {order.status === "released" && (
                          <Button variant="ghost" size="sm">
                            <Play className="h-4 w-4 text-green-500" />
                          </Button>
                        )}
                        {order.status === "in_progress" && (
                          <Button variant="ghost" size="sm">
                            <Pause className="h-4 w-4 text-yellow-500" />
                          </Button>
                        )}
                        {(order.status === "completed" || order.status === "cancelled") && (
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
        </TabsContent>

        <TabsContent value="bom" className="space-y-4">
          <div className="flex justify-end">
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              Create BOM
            </Button>
          </div>

          <Card>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>BOM #</TableHead>
                  <TableHead>Product</TableHead>
                  <TableHead>Version</TableHead>
                  <TableHead>Components</TableHead>
                  <TableHead>Total Cost</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {boms.map((bom) => (
                  <TableRow key={bom.id}>
                    <TableCell className="font-medium">{bom.bomNumber}</TableCell>
                    <TableCell>{bom.product}</TableCell>
                    <TableCell>v{bom.version}</TableCell>
                    <TableCell>{bom.components} items</TableCell>
                    <TableCell>Rs. {bom.totalCost.toLocaleString()}</TableCell>
                    <TableCell>
                      <Badge className={getStatusBadge(bom.status)}>
                        {bom.status}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Button variant="ghost" size="sm">
                        <Eye className="h-4 w-4" />
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </Card>
        </TabsContent>

        <TabsContent value="workcenters" className="space-y-4">
          <div className="flex justify-end">
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              Add Work Center
            </Button>
          </div>

          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {workCenters.map((wc) => (
              <Card key={wc.id}>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg">{wc.name}</CardTitle>
                    <Badge className={getStatusBadge(wc.status)}>
                      {wc.status}
                    </Badge>
                  </div>
                  <CardDescription>
                    {wc.code} - {wc.type}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div>
                      <div className="flex justify-between mb-1">
                        <span className="text-sm">Utilization</span>
                        <span className="text-sm font-medium">
                          {wc.utilization}%
                        </span>
                      </div>
                      <div className="h-2 bg-gray-200 rounded">
                        <div
                          className={`h-2 rounded ${
                            wc.utilization > 80
                              ? "bg-green-500"
                              : wc.utilization > 50
                              ? "bg-yellow-500"
                              : "bg-red-500"
                          }`}
                          style={{ width: `${wc.utilization}%` }}
                        />
                      </div>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Capacity</span>
                      <span>{wc.capacity} units/hr</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-muted-foreground">Current Job</span>
                      <span>{wc.currentJob || "None"}</span>
                    </div>
                    <div className="flex gap-2">
                      <Button variant="outline" size="sm" className="flex-1">
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
        </TabsContent>

        <TabsContent value="scheduling" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Production Schedule</CardTitle>
              <CardDescription>
                Visual production planning and scheduling
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-12 text-muted-foreground">
                Gantt chart view for production scheduling
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Delete Production Order Confirmation Dialog */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-red-500" />
              Delete Production Order
            </AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete order <strong>{orderToDelete?.orderNumber}</strong>?
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
