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
import { useApi, useToast } from "@/hooks";
import { Textarea } from "@/components/ui/textarea";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Shield,
  FileCheck,
  AlertTriangle,
  Calendar,
  Search,
  Plus,
  Download,
  Filter,
  CheckCircle,
  Clock,
  XCircle,
  Building,
  Scale,
  ClipboardList,
  Bell,
  TrendingUp,
  FileText,
  Users,
  Eye,
  Trash2,
  Loader2,
} from "lucide-react";

// TypeScript interfaces
interface ComplianceRequirement {
  id: string;
  name: string;
  category: string;
  act: string;
  frequency: string;
  dueDate: string;
  status: string;
  entity: string;
  riskLevel: string;
}

interface ComplianceTask {
  id: string;
  requirementId: string;
  requirementName: string;
  task: string;
  assignee: string;
  dueDate: string;
  status: string;
  priority: string;
}

interface Audit {
  id: string;
  name: string;
  type: string;
  auditor: string;
  startDate: string;
  endDate: string;
  status: string;
  findings: number;
}

// Mock data for compliance requirements
const complianceRequirements = [
  {
    id: "1",
    name: "GST Return Filing (GSTR-1)",
    category: "tax",
    act: "GST Act 2017",
    frequency: "monthly",
    dueDate: "2026-01-11",
    status: "completed",
    entity: "Gana Industries Pvt Ltd",
    riskLevel: "high",
  },
  {
    id: "2",
    name: "TDS Return Filing",
    category: "tax",
    act: "Income Tax Act 1961",
    frequency: "quarterly",
    dueDate: "2026-01-31",
    status: "pending",
    entity: "Gana Industries Pvt Ltd",
    riskLevel: "high",
  },
  {
    id: "3",
    name: "EPF Monthly Return",
    category: "labor",
    act: "EPF Act 1952",
    frequency: "monthly",
    dueDate: "2026-01-15",
    status: "in_progress",
    entity: "Gana Industries Pvt Ltd",
    riskLevel: "medium",
  },
  {
    id: "4",
    name: "Factory License Renewal",
    category: "regulatory",
    act: "Factories Act 1948",
    frequency: "annual",
    dueDate: "2026-03-31",
    status: "pending",
    entity: "Manufacturing Unit - Pune",
    riskLevel: "high",
  },
  {
    id: "5",
    name: "Pollution Control Certificate",
    category: "environment",
    act: "Environment Protection Act 1986",
    frequency: "annual",
    dueDate: "2026-06-30",
    status: "pending",
    entity: "Manufacturing Unit - Pune",
    riskLevel: "medium",
  },
];

// Mock data for compliance tasks
const complianceTasks = [
  {
    id: "1",
    requirementId: "2",
    requirementName: "TDS Return Filing",
    task: "Prepare Form 24Q",
    assignee: "Rajesh Kumar",
    dueDate: "2026-01-25",
    status: "in_progress",
    priority: "high",
  },
  {
    id: "2",
    requirementId: "2",
    requirementName: "TDS Return Filing",
    task: "Verify TDS calculations",
    assignee: "Priya Sharma",
    dueDate: "2026-01-28",
    status: "pending",
    priority: "high",
  },
  {
    id: "3",
    requirementId: "4",
    requirementName: "Factory License Renewal",
    task: "Prepare application documents",
    assignee: "Amit Patel",
    dueDate: "2026-02-15",
    status: "pending",
    priority: "medium",
  },
];

// Mock data for audits
const audits = [
  {
    id: "1",
    name: "Annual Statutory Audit FY 2025-26",
    type: "statutory",
    auditor: "KPMG India",
    startDate: "2026-04-01",
    endDate: "2026-05-15",
    status: "scheduled",
    findings: 0,
  },
  {
    id: "2",
    name: "Internal Compliance Audit Q3",
    type: "internal",
    auditor: "Internal Audit Team",
    startDate: "2025-10-01",
    endDate: "2025-10-31",
    status: "completed",
    findings: 5,
  },
  {
    id: "3",
    name: "GST Audit FY 2024-25",
    type: "tax",
    auditor: "Deloitte India",
    startDate: "2025-08-01",
    endDate: "2025-09-30",
    status: "completed",
    findings: 2,
  },
];

export default function CompliancePage() {
  const [activeTab, setActiveTab] = useState("dashboard");
  const [searchTerm, setSearchTerm] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("all");
  const [statusFilter, setStatusFilter] = useState("all");
  const { showToast } = useToast();
  const deleteApi = useApi();

  // Local state for data management
  const [requirements, setRequirements] = useState<ComplianceRequirement[]>(complianceRequirements);
  const [tasks, setTasks] = useState<ComplianceTask[]>(complianceTasks);
  const [auditList, setAuditList] = useState<Audit[]>(audits);

  // Delete state
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [itemToDelete, setItemToDelete] = useState<{ type: "requirement" | "task" | "audit"; item: ComplianceRequirement | ComplianceTask | Audit } | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  const handleDeleteClick = (type: "requirement" | "task" | "audit", item: ComplianceRequirement | ComplianceTask | Audit) => {
    setItemToDelete({ type, item });
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!itemToDelete) return;
    setIsDeleting(true);
    try {
      const endpoint = itemToDelete.type === "requirement"
        ? `/compliance/requirements/${itemToDelete.item.id}`
        : itemToDelete.type === "task"
        ? `/compliance/tasks/${itemToDelete.item.id}`
        : `/compliance/audits/${itemToDelete.item.id}`;

      await deleteApi.delete(endpoint);

      if (itemToDelete.type === "requirement") {
        setRequirements(requirements.filter(r => r.id !== itemToDelete.item.id));
      } else if (itemToDelete.type === "task") {
        setTasks(tasks.filter(t => t.id !== itemToDelete.item.id));
      } else {
        setAuditList(auditList.filter(a => a.id !== itemToDelete.item.id));
      }

      setDeleteDialogOpen(false);
      setItemToDelete(null);
      showToast("success", `${itemToDelete.type.charAt(0).toUpperCase() + itemToDelete.type.slice(1)} deleted successfully`);
    } catch (error) {
      console.error(`Failed to delete ${itemToDelete.type}:`, error);
      showToast("error", `Failed to delete ${itemToDelete.type}`);
    } finally {
      setIsDeleting(false);
    }
  };

  const getDeleteItemName = () => {
    if (!itemToDelete) return "";
    return (itemToDelete.item as ComplianceRequirement).name ||
           (itemToDelete.item as ComplianceTask).task ||
           (itemToDelete.item as Audit).name;
  };

  const getStatusBadge = (status: string) => {
    const styles: Record<string, string> = {
      completed: "bg-green-100 text-green-800",
      in_progress: "bg-blue-100 text-blue-800",
      pending: "bg-yellow-100 text-yellow-800",
      overdue: "bg-red-100 text-red-800",
      scheduled: "bg-purple-100 text-purple-800",
    };
    return styles[status] || "bg-gray-100 text-gray-800";
  };

  const getRiskBadge = (risk: string) => {
    const styles: Record<string, string> = {
      high: "bg-red-100 text-red-800",
      medium: "bg-yellow-100 text-yellow-800",
      low: "bg-green-100 text-green-800",
    };
    return styles[risk] || "bg-gray-100 text-gray-800";
  };

  const filteredRequirements = requirements.filter((req) => {
    const matchesSearch =
      req.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      req.act.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory =
      categoryFilter === "all" || req.category === categoryFilter;
    const matchesStatus =
      statusFilter === "all" || req.status === statusFilter;
    return matchesSearch && matchesCategory && matchesStatus;
  });

  // Dashboard stats
  const stats = {
    totalRequirements: requirements.length,
    completed: requirements.filter((r) => r.status === "completed").length,
    pending: requirements.filter((r) => r.status === "pending").length,
    overdue: requirements.filter((r) => r.status === "overdue").length,
    complianceRate: 85,
  };

  return (
    <div className="flex flex-col gap-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">
            Compliance Master
          </h1>
          <p className="text-muted-foreground">
            Regulatory compliance tracking and management
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline">
            <Download className="mr-2 h-4 w-4" />
            Export Report
          </Button>
          <Dialog>
            <DialogTrigger asChild>
              <Button>
                <Plus className="mr-2 h-4 w-4" />
                Add Requirement
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl">
              <DialogHeader>
                <DialogTitle>Add Compliance Requirement</DialogTitle>
                <DialogDescription>
                  Add a new regulatory compliance requirement
                </DialogDescription>
              </DialogHeader>
              <div className="grid gap-4 py-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>Requirement Name</Label>
                    <Input placeholder="Enter requirement name" />
                  </div>
                  <div className="space-y-2">
                    <Label>Category</Label>
                    <Select>
                      <SelectTrigger>
                        <SelectValue placeholder="Select category" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="tax">Tax</SelectItem>
                        <SelectItem value="labor">Labor</SelectItem>
                        <SelectItem value="regulatory">Regulatory</SelectItem>
                        <SelectItem value="environment">Environment</SelectItem>
                        <SelectItem value="corporate">Corporate</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>Applicable Act/Law</Label>
                    <Input placeholder="e.g., GST Act 2017" />
                  </div>
                  <div className="space-y-2">
                    <Label>Frequency</Label>
                    <Select>
                      <SelectTrigger>
                        <SelectValue placeholder="Select frequency" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="monthly">Monthly</SelectItem>
                        <SelectItem value="quarterly">Quarterly</SelectItem>
                        <SelectItem value="half_yearly">Half Yearly</SelectItem>
                        <SelectItem value="annual">Annual</SelectItem>
                        <SelectItem value="one_time">One Time</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>Entity</Label>
                    <Select>
                      <SelectTrigger>
                        <SelectValue placeholder="Select entity" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="gana_industries">
                          Gana Industries Pvt Ltd
                        </SelectItem>
                        <SelectItem value="mfg_pune">
                          Manufacturing Unit - Pune
                        </SelectItem>
                        <SelectItem value="mfg_chennai">
                          Manufacturing Unit - Chennai
                        </SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label>Risk Level</Label>
                    <Select>
                      <SelectTrigger>
                        <SelectValue placeholder="Select risk level" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="high">High</SelectItem>
                        <SelectItem value="medium">Medium</SelectItem>
                        <SelectItem value="low">Low</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <div className="space-y-2">
                  <Label>Description</Label>
                  <Textarea placeholder="Enter requirement details" />
                </div>
              </div>
              <DialogFooter>
                <Button variant="outline">Cancel</Button>
                <Button>Save Requirement</Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="dashboard">
            <TrendingUp className="mr-2 h-4 w-4" />
            Dashboard
          </TabsTrigger>
          <TabsTrigger value="requirements">
            <FileCheck className="mr-2 h-4 w-4" />
            Requirements
          </TabsTrigger>
          <TabsTrigger value="tasks">
            <ClipboardList className="mr-2 h-4 w-4" />
            Tasks
          </TabsTrigger>
          <TabsTrigger value="audits">
            <Scale className="mr-2 h-4 w-4" />
            Audits
          </TabsTrigger>
          <TabsTrigger value="calendar">
            <Calendar className="mr-2 h-4 w-4" />
            Calendar
          </TabsTrigger>
        </TabsList>

        <TabsContent value="dashboard" className="space-y-6">
          {/* Stats Cards */}
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-5">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium">
                  Total Requirements
                </CardTitle>
                <FileCheck className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats.totalRequirements}</div>
                <p className="text-xs text-muted-foreground">
                  Across all categories
                </p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium">Completed</CardTitle>
                <CheckCircle className="h-4 w-4 text-green-500" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-green-600">
                  {stats.completed}
                </div>
                <p className="text-xs text-muted-foreground">This period</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium">Pending</CardTitle>
                <Clock className="h-4 w-4 text-yellow-500" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-yellow-600">
                  {stats.pending}
                </div>
                <p className="text-xs text-muted-foreground">Due soon</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium">Overdue</CardTitle>
                <XCircle className="h-4 w-4 text-red-500" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-red-600">
                  {stats.overdue}
                </div>
                <p className="text-xs text-muted-foreground">Needs attention</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium">
                  Compliance Rate
                </CardTitle>
                <Shield className="h-4 w-4 text-blue-500" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-blue-600">
                  {stats.complianceRate}%
                </div>
                <p className="text-xs text-muted-foreground">Overall score</p>
              </CardContent>
            </Card>
          </div>

          {/* Category Breakdown */}
          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Compliance by Category</CardTitle>
                <CardDescription>
                  Distribution across regulatory categories
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div className="h-3 w-3 rounded-full bg-blue-500" />
                      <span>Tax Compliance</span>
                    </div>
                    <span className="font-medium">12 requirements</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div className="h-3 w-3 rounded-full bg-green-500" />
                      <span>Labor Laws</span>
                    </div>
                    <span className="font-medium">8 requirements</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div className="h-3 w-3 rounded-full bg-yellow-500" />
                      <span>Regulatory</span>
                    </div>
                    <span className="font-medium">6 requirements</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div className="h-3 w-3 rounded-full bg-purple-500" />
                      <span>Environment</span>
                    </div>
                    <span className="font-medium">4 requirements</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div className="h-3 w-3 rounded-full bg-orange-500" />
                      <span>Corporate</span>
                    </div>
                    <span className="font-medium">5 requirements</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Upcoming Deadlines</CardTitle>
                <CardDescription>Next 30 days compliance due dates</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {requirements
                    .filter((r) => r.status !== "completed")
                    .slice(0, 5)
                    .map((req) => (
                      <div
                        key={req.id}
                        className="flex items-center justify-between border-b pb-2 last:border-0"
                      >
                        <div>
                          <p className="font-medium">{req.name}</p>
                          <p className="text-sm text-muted-foreground">
                            {req.entity}
                          </p>
                        </div>
                        <div className="text-right">
                          <p className="font-medium">{req.dueDate}</p>
                          <Badge className={getRiskBadge(req.riskLevel)}>
                            {req.riskLevel}
                          </Badge>
                        </div>
                      </div>
                    ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="requirements" className="space-y-4">
          <div className="flex items-center gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search requirements..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-8"
              />
            </div>
            <Select value={categoryFilter} onValueChange={setCategoryFilter}>
              <SelectTrigger className="w-[180px]">
                <Filter className="mr-2 h-4 w-4" />
                <SelectValue placeholder="Category" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Categories</SelectItem>
                <SelectItem value="tax">Tax</SelectItem>
                <SelectItem value="labor">Labor</SelectItem>
                <SelectItem value="regulatory">Regulatory</SelectItem>
                <SelectItem value="environment">Environment</SelectItem>
                <SelectItem value="corporate">Corporate</SelectItem>
              </SelectContent>
            </Select>
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-[150px]">
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="completed">Completed</SelectItem>
                <SelectItem value="in_progress">In Progress</SelectItem>
                <SelectItem value="pending">Pending</SelectItem>
                <SelectItem value="overdue">Overdue</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <Card>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Requirement</TableHead>
                  <TableHead>Category</TableHead>
                  <TableHead>Applicable Law</TableHead>
                  <TableHead>Entity</TableHead>
                  <TableHead>Due Date</TableHead>
                  <TableHead>Risk</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredRequirements.map((req) => (
                  <TableRow key={req.id}>
                    <TableCell className="font-medium">{req.name}</TableCell>
                    <TableCell className="capitalize">{req.category}</TableCell>
                    <TableCell>{req.act}</TableCell>
                    <TableCell>{req.entity}</TableCell>
                    <TableCell>{req.dueDate}</TableCell>
                    <TableCell>
                      <Badge className={getRiskBadge(req.riskLevel)}>
                        {req.riskLevel}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Badge className={getStatusBadge(req.status)}>
                        {req.status.replace("_", " ")}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <div className="flex gap-1">
                        <Button variant="ghost" size="sm">
                          <Eye className="h-4 w-4" />
                        </Button>
                        {req.status === "completed" && (
                          <Button
                            variant="ghost"
                            size="sm"
                            className="text-red-600 hover:text-red-700 hover:bg-red-50"
                            onClick={() => handleDeleteClick("requirement", req)}
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

        <TabsContent value="tasks" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Compliance Tasks</CardTitle>
              <CardDescription>
                Track and manage compliance-related tasks
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Task</TableHead>
                    <TableHead>Requirement</TableHead>
                    <TableHead>Assignee</TableHead>
                    <TableHead>Due Date</TableHead>
                    <TableHead>Priority</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {tasks.map((task) => (
                    <TableRow key={task.id}>
                      <TableCell className="font-medium">{task.task}</TableCell>
                      <TableCell>{task.requirementName}</TableCell>
                      <TableCell>{task.assignee}</TableCell>
                      <TableCell>{task.dueDate}</TableCell>
                      <TableCell>
                        <Badge
                          className={
                            task.priority === "high"
                              ? "bg-red-100 text-red-800"
                              : task.priority === "medium"
                              ? "bg-yellow-100 text-yellow-800"
                              : "bg-green-100 text-green-800"
                          }
                        >
                          {task.priority}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <Badge className={getStatusBadge(task.status)}>
                          {task.status.replace("_", " ")}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <div className="flex gap-1">
                          <Button variant="ghost" size="sm">
                            <Eye className="h-4 w-4" />
                          </Button>
                          {task.status === "completed" && (
                            <Button
                              variant="ghost"
                              size="sm"
                              className="text-red-600 hover:text-red-700 hover:bg-red-50"
                              onClick={() => handleDeleteClick("task", task)}
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
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="audits" className="space-y-4">
          <div className="flex justify-end">
            <Dialog>
              <DialogTrigger asChild>
                <Button>
                  <Plus className="mr-2 h-4 w-4" />
                  Schedule Audit
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Schedule New Audit</DialogTitle>
                  <DialogDescription>
                    Plan a compliance audit
                  </DialogDescription>
                </DialogHeader>
                <div className="grid gap-4 py-4">
                  <div className="space-y-2">
                    <Label>Audit Name</Label>
                    <Input placeholder="Enter audit name" />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label>Audit Type</Label>
                      <Select>
                        <SelectTrigger>
                          <SelectValue placeholder="Select type" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="statutory">Statutory</SelectItem>
                          <SelectItem value="internal">Internal</SelectItem>
                          <SelectItem value="tax">Tax</SelectItem>
                          <SelectItem value="regulatory">Regulatory</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="space-y-2">
                      <Label>Auditor</Label>
                      <Input placeholder="Enter auditor name" />
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label>Start Date</Label>
                      <Input type="date" />
                    </div>
                    <div className="space-y-2">
                      <Label>End Date</Label>
                      <Input type="date" />
                    </div>
                  </div>
                </div>
                <DialogFooter>
                  <Button variant="outline">Cancel</Button>
                  <Button>Schedule Audit</Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
          </div>

          <Card>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Audit Name</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Auditor</TableHead>
                  <TableHead>Start Date</TableHead>
                  <TableHead>End Date</TableHead>
                  <TableHead>Findings</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {auditList.map((audit) => (
                  <TableRow key={audit.id}>
                    <TableCell className="font-medium">{audit.name}</TableCell>
                    <TableCell className="capitalize">{audit.type}</TableCell>
                    <TableCell>{audit.auditor}</TableCell>
                    <TableCell>{audit.startDate}</TableCell>
                    <TableCell>{audit.endDate}</TableCell>
                    <TableCell>
                      <Badge
                        variant={audit.findings > 0 ? "destructive" : "secondary"}
                      >
                        {audit.findings} findings
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <Badge className={getStatusBadge(audit.status)}>
                        {audit.status}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <div className="flex gap-1">
                        <Button variant="ghost" size="sm">
                          <Eye className="h-4 w-4" />
                        </Button>
                        {audit.status === "completed" && (
                          <Button
                            variant="ghost"
                            size="sm"
                            className="text-red-600 hover:text-red-700 hover:bg-red-50"
                            onClick={() => handleDeleteClick("audit", audit)}
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

        <TabsContent value="calendar" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Compliance Calendar</CardTitle>
              <CardDescription>
                View all compliance deadlines in calendar format
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-12 text-muted-foreground">
                Calendar view with compliance deadlines
              </div>
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
              Delete {itemToDelete?.type === "requirement" ? "Requirement" : itemToDelete?.type === "task" ? "Task" : "Audit"}
            </AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete <strong>{getDeleteItemName()}</strong>?
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
