"use client";

import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
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
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Textarea } from "@/components/ui/textarea";
import { Progress } from "@/components/ui/progress";
import { Separator } from "@/components/ui/separator";
import { ScrollArea } from "@/components/ui/scroll-area";
import { cn } from "@/lib/utils";
import { format, formatDistanceToNow } from "date-fns";
import {
  Plus,
  Search,
  MoreHorizontal,
  Eye,
  Edit,
  Trash2,
  FileText,
  Clock,
  CheckCircle,
  XCircle,
  AlertTriangle,
  ArrowUpRight,
  User,
  Building,
  DollarSign,
  Calendar,
  MessageSquare,
  Paperclip,
  History,
  Send,
  Copy,
  Download,
  Filter,
  ChevronRight,
  RefreshCw,
  AlertCircle,
} from "lucide-react";

// Types
interface ApprovalLevel {
  levelOrder: number;
  approverName: string;
  approverDesignation: string;
  status: "pending" | "approved" | "rejected" | "skipped" | "waiting";
  actedAt?: string;
  comments?: string;
}

interface ApprovalRequest {
  id: string;
  requestNumber: string;
  subject: string;
  description: string;
  transactionType: string;
  transactionRef: string;
  amount: number;
  currency: string;
  department: string;
  requesterId: string;
  requesterName: string;
  requesterEmail: string;
  workflowName: string;
  status: "draft" | "pending" | "in_progress" | "approved" | "rejected" | "cancelled" | "escalated";
  currentLevel: number;
  totalLevels: number;
  priority: "low" | "normal" | "high" | "urgent";
  riskLevel: "low" | "medium" | "high" | "critical";
  isUrgent: boolean;
  dueAt: string;
  slaStatus: "on_track" | "at_risk" | "breached";
  levels: ApprovalLevel[];
  attachments: { name: string; size: string; type: string }[];
  comments: { user: string; text: string; timestamp: string }[];
  createdAt: string;
  updatedAt: string;
  completedAt?: string;
}

// Mock data
const mockRequests: ApprovalRequest[] = [
  {
    id: "1",
    requestNumber: "REQ-2024-00156",
    subject: "Server Infrastructure Upgrade",
    description: "Purchase of new Dell PowerEdge servers for data center expansion",
    transactionType: "purchase_order",
    transactionRef: "PO-2024-00234",
    amount: 850000,
    currency: "INR",
    department: "IT",
    requesterId: "u10",
    requesterName: "Karthik Menon",
    requesterEmail: "karthik@company.com",
    workflowName: "High Value Purchase Approval",
    status: "in_progress",
    currentLevel: 2,
    totalLevels: 3,
    priority: "high",
    riskLevel: "medium",
    isUrgent: false,
    dueAt: "2024-06-20T17:00:00Z",
    slaStatus: "on_track",
    levels: [
      {
        levelOrder: 1,
        approverName: "Ravi Iyer",
        approverDesignation: "IT Manager",
        status: "approved",
        actedAt: "2024-06-12T10:30:00Z",
        comments: "Approved. Budget allocation confirmed.",
      },
      {
        levelOrder: 2,
        approverName: "Sanjay Gupta",
        approverDesignation: "Finance Director",
        status: "pending",
      },
      {
        levelOrder: 3,
        approverName: "CEO",
        approverDesignation: "Chief Executive Officer",
        status: "waiting",
      },
    ],
    attachments: [
      { name: "vendor_quotation.pdf", size: "2.3 MB", type: "pdf" },
      { name: "technical_specs.xlsx", size: "156 KB", type: "excel" },
    ],
    comments: [
      {
        user: "Karthik Menon",
        text: "Urgent requirement for Q3 expansion. Current capacity at 85%.",
        timestamp: "2024-06-10T14:00:00Z",
      },
      {
        user: "Ravi Iyer",
        text: "Technical review completed. Specs align with requirements.",
        timestamp: "2024-06-12T10:30:00Z",
      },
    ],
    createdAt: "2024-06-10T09:00:00Z",
    updatedAt: "2024-06-12T10:30:00Z",
  },
  {
    id: "2",
    requestNumber: "REQ-2024-00157",
    subject: "Marketing Campaign Budget",
    description: "Q3 digital marketing campaign for product launch",
    transactionType: "budget_request",
    transactionRef: "BUD-2024-00089",
    amount: 250000,
    currency: "INR",
    department: "Marketing",
    requesterId: "u11",
    requesterName: "Ananya Das",
    requesterEmail: "ananya@company.com",
    workflowName: "Marketing Budget Approval",
    status: "pending",
    currentLevel: 1,
    totalLevels: 2,
    priority: "normal",
    riskLevel: "low",
    isUrgent: false,
    dueAt: "2024-06-25T17:00:00Z",
    slaStatus: "on_track",
    levels: [
      {
        levelOrder: 1,
        approverName: "Marketing Head",
        approverDesignation: "VP Marketing",
        status: "pending",
      },
      {
        levelOrder: 2,
        approverName: "Finance Director",
        approverDesignation: "Finance Director",
        status: "waiting",
      },
    ],
    attachments: [{ name: "campaign_proposal.pdf", size: "4.5 MB", type: "pdf" }],
    comments: [],
    createdAt: "2024-06-14T11:00:00Z",
    updatedAt: "2024-06-14T11:00:00Z",
  },
  {
    id: "3",
    requestNumber: "REQ-2024-00155",
    subject: "Office Furniture Replacement",
    description: "Ergonomic chairs and standing desks for new hires",
    transactionType: "purchase_order",
    transactionRef: "PO-2024-00231",
    amount: 120000,
    currency: "INR",
    department: "Admin",
    requesterId: "u12",
    requesterName: "Pradeep Kumar",
    requesterEmail: "pradeep@company.com",
    workflowName: "Standard Purchase Approval",
    status: "approved",
    currentLevel: 2,
    totalLevels: 2,
    priority: "low",
    riskLevel: "low",
    isUrgent: false,
    dueAt: "2024-06-15T17:00:00Z",
    slaStatus: "on_track",
    levels: [
      {
        levelOrder: 1,
        approverName: "Admin Manager",
        approverDesignation: "Admin Manager",
        status: "approved",
        actedAt: "2024-06-08T14:00:00Z",
        comments: "Approved",
      },
      {
        levelOrder: 2,
        approverName: "Finance Manager",
        approverDesignation: "Finance Manager",
        status: "approved",
        actedAt: "2024-06-10T09:30:00Z",
        comments: "Approved. Within quarterly budget.",
      },
    ],
    attachments: [{ name: "furniture_catalog.pdf", size: "8.2 MB", type: "pdf" }],
    comments: [],
    createdAt: "2024-06-05T10:00:00Z",
    updatedAt: "2024-06-10T09:30:00Z",
    completedAt: "2024-06-10T09:30:00Z",
  },
  {
    id: "4",
    requestNumber: "REQ-2024-00154",
    subject: "Emergency Server Repair",
    description: "Critical hardware failure in production server",
    transactionType: "emergency_expense",
    transactionRef: "EMG-2024-00012",
    amount: 75000,
    currency: "INR",
    department: "IT",
    requesterId: "u10",
    requesterName: "Karthik Menon",
    requesterEmail: "karthik@company.com",
    workflowName: "Emergency Expense Approval",
    status: "escalated",
    currentLevel: 2,
    totalLevels: 2,
    priority: "urgent",
    riskLevel: "high",
    isUrgent: true,
    dueAt: "2024-06-13T12:00:00Z",
    slaStatus: "breached",
    levels: [
      {
        levelOrder: 1,
        approverName: "IT Manager",
        approverDesignation: "IT Manager",
        status: "skipped",
        comments: "Auto-escalated due to timeout",
      },
      {
        levelOrder: 2,
        approverName: "CTO",
        approverDesignation: "Chief Technology Officer",
        status: "pending",
      },
    ],
    attachments: [
      { name: "incident_report.pdf", size: "1.1 MB", type: "pdf" },
      { name: "vendor_diagnosis.pdf", size: "890 KB", type: "pdf" },
    ],
    comments: [
      {
        user: "Karthik Menon",
        text: "Production server down. Immediate action required.",
        timestamp: "2024-06-12T08:00:00Z",
      },
      {
        user: "System",
        text: "Auto-escalated to CTO due to SLA breach at Level 1",
        timestamp: "2024-06-13T12:01:00Z",
      },
    ],
    createdAt: "2024-06-12T08:00:00Z",
    updatedAt: "2024-06-13T12:01:00Z",
  },
  {
    id: "5",
    requestNumber: "REQ-2024-00153",
    subject: "Training Program Registration",
    description: "Leadership development program for senior managers",
    transactionType: "training_expense",
    transactionRef: "TRN-2024-00045",
    amount: 180000,
    currency: "INR",
    department: "HR",
    requesterId: "u5",
    requesterName: "Meera Joshi",
    requesterEmail: "meera@company.com",
    workflowName: "Training Budget Approval",
    status: "rejected",
    currentLevel: 2,
    totalLevels: 2,
    priority: "normal",
    riskLevel: "low",
    isUrgent: false,
    dueAt: "2024-06-18T17:00:00Z",
    slaStatus: "on_track",
    levels: [
      {
        levelOrder: 1,
        approverName: "HR Director",
        approverDesignation: "HR Director",
        status: "approved",
        actedAt: "2024-06-08T11:00:00Z",
        comments: "Recommended for management development.",
      },
      {
        levelOrder: 2,
        approverName: "CFO",
        approverDesignation: "Chief Financial Officer",
        status: "rejected",
        actedAt: "2024-06-11T15:30:00Z",
        comments: "Budget constraints this quarter. Please resubmit in Q4.",
      },
    ],
    attachments: [{ name: "program_brochure.pdf", size: "3.4 MB", type: "pdf" }],
    comments: [],
    createdAt: "2024-06-06T14:00:00Z",
    updatedAt: "2024-06-11T15:30:00Z",
    completedAt: "2024-06-11T15:30:00Z",
  },
];

const transactionTypes = [
  { value: "purchase_order", label: "Purchase Order" },
  { value: "budget_request", label: "Budget Request" },
  { value: "expense_claim", label: "Expense Claim" },
  { value: "travel_request", label: "Travel Request" },
  { value: "training_expense", label: "Training Expense" },
  { value: "emergency_expense", label: "Emergency Expense" },
  { value: "contract", label: "Contract" },
  { value: "hiring_request", label: "Hiring Request" },
];

export default function ApprovalRequestsPage() {
  const [requests, setRequests] = useState<ApprovalRequest[]>(mockRequests);
  const [searchQuery, setSearchQuery] = useState("");
  const [filterStatus, setFilterStatus] = useState<string>("all");
  const [filterType, setFilterType] = useState<string>("all");
  const [filterDepartment, setFilterDepartment] = useState<string>("all");
  const [selectedRequest, setSelectedRequest] = useState<ApprovalRequest | null>(null);
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [activeTab, setActiveTab] = useState("all");

  // Filter requests
  const filteredRequests = requests.filter((request) => {
    const matchesSearch =
      request.requestNumber.toLowerCase().includes(searchQuery.toLowerCase()) ||
      request.subject.toLowerCase().includes(searchQuery.toLowerCase()) ||
      request.requesterName.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = filterStatus === "all" || request.status === filterStatus;
    const matchesType = filterType === "all" || request.transactionType === filterType;
    const matchesDept = filterDepartment === "all" || request.department === filterDepartment;

    // Tab filtering
    let matchesTab = true;
    if (activeTab === "pending") {
      matchesTab = request.status === "pending" || request.status === "in_progress";
    } else if (activeTab === "completed") {
      matchesTab = request.status === "approved" || request.status === "rejected";
    } else if (activeTab === "my-requests") {
      // Assuming current user is Karthik Menon
      matchesTab = request.requesterId === "u10";
    }

    return matchesSearch && matchesStatus && matchesType && matchesDept && matchesTab;
  });

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "draft":
        return <Badge variant="outline">Draft</Badge>;
      case "pending":
        return <Badge className="bg-yellow-100 text-yellow-800">Pending</Badge>;
      case "in_progress":
        return <Badge className="bg-blue-100 text-blue-800">In Progress</Badge>;
      case "approved":
        return <Badge className="bg-green-100 text-green-800">Approved</Badge>;
      case "rejected":
        return <Badge className="bg-red-100 text-red-800">Rejected</Badge>;
      case "cancelled":
        return <Badge className="bg-gray-100 text-gray-800">Cancelled</Badge>;
      case "escalated":
        return <Badge className="bg-orange-100 text-orange-800">Escalated</Badge>;
      default:
        return <Badge variant="outline">{status}</Badge>;
    }
  };

  const getPriorityBadge = (priority: string) => {
    switch (priority) {
      case "low":
        return <Badge variant="outline">Low</Badge>;
      case "normal":
        return <Badge className="bg-blue-100 text-blue-800">Normal</Badge>;
      case "high":
        return <Badge className="bg-orange-100 text-orange-800">High</Badge>;
      case "urgent":
        return <Badge className="bg-red-100 text-red-800">Urgent</Badge>;
      default:
        return <Badge variant="outline">{priority}</Badge>;
    }
  };

  const getSlaStatusIcon = (slaStatus: string) => {
    switch (slaStatus) {
      case "on_track":
        return <CheckCircle className="h-4 w-4 text-green-600" />;
      case "at_risk":
        return <AlertTriangle className="h-4 w-4 text-yellow-600" />;
      case "breached":
        return <AlertCircle className="h-4 w-4 text-red-600" />;
      default:
        return null;
    }
  };

  const formatCurrency = (amount: number, currency: string) => {
    return new Intl.NumberFormat("en-IN", {
      style: "currency",
      currency: currency,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const getLevelStatusIcon = (status: string) => {
    switch (status) {
      case "approved":
        return <CheckCircle className="h-5 w-5 text-green-600" />;
      case "rejected":
        return <XCircle className="h-5 w-5 text-red-600" />;
      case "pending":
        return <Clock className="h-5 w-5 text-yellow-600" />;
      case "skipped":
        return <ArrowUpRight className="h-5 w-5 text-orange-600" />;
      case "waiting":
        return <div className="h-5 w-5 rounded-full border-2 border-gray-300" />;
      default:
        return null;
    }
  };

  // Summary stats
  const stats = {
    total: requests.length,
    pending: requests.filter((r) => r.status === "pending" || r.status === "in_progress").length,
    approved: requests.filter((r) => r.status === "approved").length,
    rejected: requests.filter((r) => r.status === "rejected").length,
    escalated: requests.filter((r) => r.status === "escalated").length,
  };

  return (
    <div className="flex flex-col gap-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Approval Requests</h1>
          <p className="text-muted-foreground">
            Track and manage all approval requests across your organization
          </p>
        </div>
        <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              New Request
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>Create Approval Request</DialogTitle>
              <DialogDescription>
                Submit a new request for approval through the workflow
              </DialogDescription>
            </DialogHeader>
            <div className="grid gap-4 py-4 max-h-[60vh] overflow-y-auto">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="transactionType">Transaction Type</Label>
                  <Select>
                    <SelectTrigger>
                      <SelectValue placeholder="Select type" />
                    </SelectTrigger>
                    <SelectContent>
                      {transactionTypes.map((type) => (
                        <SelectItem key={type.value} value={type.value}>
                          {type.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="workflow">Approval Workflow</Label>
                  <Select>
                    <SelectTrigger>
                      <SelectValue placeholder="Auto-selected based on type" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="w1">Standard Purchase Approval</SelectItem>
                      <SelectItem value="w2">High Value Purchase Approval</SelectItem>
                      <SelectItem value="w3">Emergency Expense Approval</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="subject">Subject</Label>
                <Input id="subject" placeholder="Brief description of the request" />
              </div>

              <div className="space-y-2">
                <Label htmlFor="description">Description</Label>
                <Textarea
                  id="description"
                  placeholder="Detailed description and justification"
                  rows={4}
                />
              </div>

              <div className="grid grid-cols-3 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="amount">Amount</Label>
                  <Input id="amount" type="number" placeholder="0" />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="currency">Currency</Label>
                  <Select defaultValue="INR">
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="INR">INR</SelectItem>
                      <SelectItem value="USD">USD</SelectItem>
                      <SelectItem value="EUR">EUR</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="priority">Priority</Label>
                  <Select defaultValue="normal">
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="low">Low</SelectItem>
                      <SelectItem value="normal">Normal</SelectItem>
                      <SelectItem value="high">High</SelectItem>
                      <SelectItem value="urgent">Urgent</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="department">Department</Label>
                  <Select>
                    <SelectTrigger>
                      <SelectValue placeholder="Select department" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="it">IT</SelectItem>
                      <SelectItem value="finance">Finance</SelectItem>
                      <SelectItem value="hr">HR</SelectItem>
                      <SelectItem value="marketing">Marketing</SelectItem>
                      <SelectItem value="admin">Admin</SelectItem>
                      <SelectItem value="operations">Operations</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="transactionRef">Reference Number</Label>
                  <Input id="transactionRef" placeholder="e.g., PO-2024-00234" />
                </div>
              </div>

              <div className="space-y-2">
                <Label>Attachments</Label>
                <div className="border-2 border-dashed rounded-lg p-6 text-center">
                  <Paperclip className="h-8 w-8 mx-auto text-muted-foreground" />
                  <p className="mt-2 text-sm text-muted-foreground">
                    Drag and drop files here, or click to browse
                  </p>
                  <Button variant="outline" size="sm" className="mt-2">
                    Browse Files
                  </Button>
                </div>
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setIsCreateDialogOpen(false)}>
                Save as Draft
              </Button>
              <Button onClick={() => setIsCreateDialogOpen(false)}>
                <Send className="mr-2 h-4 w-4" />
                Submit Request
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      {/* Summary Cards */}
      <div className="grid gap-4 md:grid-cols-5">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Requests</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.total}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">In Progress</CardTitle>
            <Clock className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.pending}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Approved</CardTitle>
            <CheckCircle className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.approved}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Rejected</CardTitle>
            <XCircle className="h-4 w-4 text-red-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.rejected}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Escalated</CardTitle>
            <ArrowUpRight className="h-4 w-4 text-orange-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.escalated}</div>
          </CardContent>
        </Card>
      </div>

      {/* Main Content */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <div className="flex items-center justify-between flex-wrap gap-4">
          <TabsList>
            <TabsTrigger value="all">All Requests</TabsTrigger>
            <TabsTrigger value="pending">In Progress</TabsTrigger>
            <TabsTrigger value="completed">Completed</TabsTrigger>
            <TabsTrigger value="my-requests">My Requests</TabsTrigger>
          </TabsList>

          {/* Filters */}
          <div className="flex items-center gap-2">
            <div className="relative">
              <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search requests..."
                className="pl-8 w-[200px]"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
            <Select value={filterStatus} onValueChange={setFilterStatus}>
              <SelectTrigger className="w-[130px]">
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="pending">Pending</SelectItem>
                <SelectItem value="in_progress">In Progress</SelectItem>
                <SelectItem value="approved">Approved</SelectItem>
                <SelectItem value="rejected">Rejected</SelectItem>
                <SelectItem value="escalated">Escalated</SelectItem>
              </SelectContent>
            </Select>
            <Select value={filterType} onValueChange={setFilterType}>
              <SelectTrigger className="w-[150px]">
                <SelectValue placeholder="Type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Types</SelectItem>
                {transactionTypes.map((type) => (
                  <SelectItem key={type.value} value={type.value}>
                    {type.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>

        <TabsContent value={activeTab} className="mt-4">
          <Card>
            <CardContent className="p-0">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Request</TableHead>
                    <TableHead>Type</TableHead>
                    <TableHead>Amount</TableHead>
                    <TableHead>Progress</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>SLA</TableHead>
                    <TableHead className="w-[50px]"></TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredRequests.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={7} className="text-center py-8">
                        <div className="flex flex-col items-center gap-2">
                          <FileText className="h-8 w-8 text-muted-foreground" />
                          <p className="text-muted-foreground">No requests found</p>
                        </div>
                      </TableCell>
                    </TableRow>
                  ) : (
                    filteredRequests.map((request) => (
                      <TableRow key={request.id}>
                        <TableCell>
                          <div>
                            <div className="flex items-center gap-2">
                              <span className="font-medium">{request.requestNumber}</span>
                              {request.isUrgent && (
                                <Badge className="bg-red-100 text-red-800">Urgent</Badge>
                              )}
                            </div>
                            <div className="text-sm text-muted-foreground truncate max-w-[300px]">
                              {request.subject}
                            </div>
                            <div className="text-xs text-muted-foreground flex items-center gap-1 mt-1">
                              <User className="h-3 w-3" />
                              {request.requesterName}
                              <span className="mx-1">|</span>
                              <Building className="h-3 w-3" />
                              {request.department}
                            </div>
                          </div>
                        </TableCell>
                        <TableCell>
                          <Badge variant="outline">
                            {transactionTypes.find((t) => t.value === request.transactionType)?.label ||
                              request.transactionType}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <div className="font-medium">
                            {formatCurrency(request.amount, request.currency)}
                          </div>
                        </TableCell>
                        <TableCell>
                          <div className="space-y-1">
                            <div className="flex items-center gap-2">
                              <Progress
                                value={(request.currentLevel / request.totalLevels) * 100}
                                className="h-2 w-20"
                              />
                              <span className="text-xs text-muted-foreground">
                                {request.currentLevel}/{request.totalLevels}
                              </span>
                            </div>
                            <div className="text-xs text-muted-foreground">
                              {request.workflowName}
                            </div>
                          </div>
                        </TableCell>
                        <TableCell>
                          <div className="space-y-1">
                            {getStatusBadge(request.status)}
                            {getPriorityBadge(request.priority)}
                          </div>
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center gap-1">
                            {getSlaStatusIcon(request.slaStatus)}
                            <span className="text-xs">
                              {format(new Date(request.dueAt), "MMM d")}
                            </span>
                          </div>
                        </TableCell>
                        <TableCell>
                          <DropdownMenu>
                            <DropdownMenuTrigger asChild>
                              <Button variant="ghost" size="icon">
                                <MoreHorizontal className="h-4 w-4" />
                              </Button>
                            </DropdownMenuTrigger>
                            <DropdownMenuContent align="end">
                              <DropdownMenuItem onClick={() => setSelectedRequest(request)}>
                                <Eye className="mr-2 h-4 w-4" />
                                View Details
                              </DropdownMenuItem>
                              <DropdownMenuItem>
                                <History className="mr-2 h-4 w-4" />
                                View History
                              </DropdownMenuItem>
                              <DropdownMenuItem>
                                <Copy className="mr-2 h-4 w-4" />
                                Duplicate
                              </DropdownMenuItem>
                              <DropdownMenuSeparator />
                              {request.status === "pending" && (
                                <DropdownMenuItem>
                                  <RefreshCw className="mr-2 h-4 w-4" />
                                  Send Reminder
                                </DropdownMenuItem>
                              )}
                              {(request.status === "draft" || request.status === "pending") && (
                                <>
                                  <DropdownMenuItem>
                                    <Edit className="mr-2 h-4 w-4" />
                                    Edit
                                  </DropdownMenuItem>
                                  <DropdownMenuItem className="text-red-600">
                                    <Trash2 className="mr-2 h-4 w-4" />
                                    Cancel
                                  </DropdownMenuItem>
                                </>
                              )}
                            </DropdownMenuContent>
                          </DropdownMenu>
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Request Detail Dialog */}
      <Dialog open={!!selectedRequest} onOpenChange={() => setSelectedRequest(null)}>
        <DialogContent className="max-w-4xl max-h-[90vh]">
          <DialogHeader>
            <div className="flex items-center justify-between">
              <div>
                <DialogTitle className="flex items-center gap-2">
                  {selectedRequest?.requestNumber}
                  {selectedRequest?.isUrgent && (
                    <Badge className="bg-red-100 text-red-800">Urgent</Badge>
                  )}
                </DialogTitle>
                <DialogDescription>{selectedRequest?.subject}</DialogDescription>
              </div>
              <div className="flex items-center gap-2">
                {selectedRequest && getStatusBadge(selectedRequest.status)}
                {selectedRequest && getPriorityBadge(selectedRequest.priority)}
              </div>
            </div>
          </DialogHeader>
          {selectedRequest && (
            <ScrollArea className="max-h-[70vh]">
              <div className="space-y-6 pr-4">
                {/* Request Info */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div>
                    <Label className="text-muted-foreground">Transaction Type</Label>
                    <div className="mt-1 font-medium">
                      {transactionTypes.find((t) => t.value === selectedRequest.transactionType)?.label}
                    </div>
                  </div>
                  <div>
                    <Label className="text-muted-foreground">Reference</Label>
                    <div className="mt-1 font-medium">{selectedRequest.transactionRef}</div>
                  </div>
                  <div>
                    <Label className="text-muted-foreground">Amount</Label>
                    <div className="mt-1 font-medium text-lg">
                      {formatCurrency(selectedRequest.amount, selectedRequest.currency)}
                    </div>
                  </div>
                  <div>
                    <Label className="text-muted-foreground">Due Date</Label>
                    <div className="mt-1 flex items-center gap-2">
                      {getSlaStatusIcon(selectedRequest.slaStatus)}
                      <span className="font-medium">
                        {format(new Date(selectedRequest.dueAt), "PPP")}
                      </span>
                    </div>
                  </div>
                </div>

                <Separator />

                {/* Requester Info */}
                <div>
                  <Label className="text-muted-foreground">Requester</Label>
                  <div className="mt-2 flex items-center gap-3 p-3 bg-muted rounded-lg">
                    <div className="p-2 rounded-full bg-background">
                      <User className="h-5 w-5" />
                    </div>
                    <div>
                      <div className="font-medium">{selectedRequest.requesterName}</div>
                      <div className="text-sm text-muted-foreground">
                        {selectedRequest.requesterEmail} | {selectedRequest.department}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Description */}
                <div>
                  <Label className="text-muted-foreground">Description</Label>
                  <p className="mt-1">{selectedRequest.description}</p>
                </div>

                {/* Approval Progress */}
                <div>
                  <Label className="text-muted-foreground mb-3 block">Approval Progress</Label>
                  <div className="relative">
                    {selectedRequest.levels.map((level, index) => (
                      <div key={level.levelOrder} className="flex items-start gap-4 mb-4">
                        <div className="flex flex-col items-center">
                          {getLevelStatusIcon(level.status)}
                          {index < selectedRequest.levels.length - 1 && (
                            <div
                              className={cn(
                                "w-0.5 h-12 mt-2",
                                level.status === "approved"
                                  ? "bg-green-200"
                                  : level.status === "rejected"
                                  ? "bg-red-200"
                                  : "bg-gray-200"
                              )}
                            />
                          )}
                        </div>
                        <div className="flex-1 pb-4">
                          <div className="flex items-center justify-between">
                            <div>
                              <div className="font-medium">
                                Level {level.levelOrder}: {level.approverName}
                              </div>
                              <div className="text-sm text-muted-foreground">
                                {level.approverDesignation}
                              </div>
                            </div>
                            <Badge
                              variant="outline"
                              className={cn(
                                level.status === "approved" && "bg-green-50 border-green-200",
                                level.status === "rejected" && "bg-red-50 border-red-200",
                                level.status === "pending" && "bg-yellow-50 border-yellow-200",
                                level.status === "skipped" && "bg-orange-50 border-orange-200"
                              )}
                            >
                              {level.status.charAt(0).toUpperCase() + level.status.slice(1)}
                            </Badge>
                          </div>
                          {level.actedAt && (
                            <div className="text-xs text-muted-foreground mt-1">
                              {format(new Date(level.actedAt), "PPp")}
                            </div>
                          )}
                          {level.comments && (
                            <div className="mt-2 p-2 bg-muted rounded text-sm">
                              <MessageSquare className="h-3 w-3 inline mr-1" />
                              {level.comments}
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Attachments */}
                {selectedRequest.attachments.length > 0 && (
                  <div>
                    <Label className="text-muted-foreground mb-2 block">Attachments</Label>
                    <div className="space-y-2">
                      {selectedRequest.attachments.map((attachment, index) => (
                        <div
                          key={index}
                          className="flex items-center justify-between p-3 border rounded-lg"
                        >
                          <div className="flex items-center gap-3">
                            <Paperclip className="h-4 w-4 text-muted-foreground" />
                            <div>
                              <div className="font-medium">{attachment.name}</div>
                              <div className="text-xs text-muted-foreground">{attachment.size}</div>
                            </div>
                          </div>
                          <Button variant="ghost" size="sm">
                            <Download className="h-4 w-4" />
                          </Button>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Comments */}
                {selectedRequest.comments.length > 0 && (
                  <div>
                    <Label className="text-muted-foreground mb-2 block">Comments</Label>
                    <div className="space-y-3">
                      {selectedRequest.comments.map((comment, index) => (
                        <div key={index} className="p-3 bg-muted rounded-lg">
                          <div className="flex items-center justify-between">
                            <span className="font-medium">{comment.user}</span>
                            <span className="text-xs text-muted-foreground">
                              {format(new Date(comment.timestamp), "PPp")}
                            </span>
                          </div>
                          <p className="text-sm mt-1">{comment.text}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Timestamps */}
                <div className="flex gap-4 text-xs text-muted-foreground">
                  <div>
                    Created: {format(new Date(selectedRequest.createdAt), "PPp")}
                  </div>
                  <div>
                    Updated: {format(new Date(selectedRequest.updatedAt), "PPp")}
                  </div>
                  {selectedRequest.completedAt && (
                    <div>
                      Completed: {format(new Date(selectedRequest.completedAt), "PPp")}
                    </div>
                  )}
                </div>
              </div>
            </ScrollArea>
          )}
          <DialogFooter>
            <Button variant="outline" onClick={() => setSelectedRequest(null)}>
              Close
            </Button>
            <Button variant="outline">
              <History className="mr-2 h-4 w-4" />
              View Audit Trail
            </Button>
            <Button>
              <Download className="mr-2 h-4 w-4" />
              Export PDF
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
