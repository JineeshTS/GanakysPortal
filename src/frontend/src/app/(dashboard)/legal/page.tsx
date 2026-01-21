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
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
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
import { useApi, useToast } from "@/hooks";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Progress } from "@/components/ui/progress";
import {
  Scale,
  Plus,
  Search,
  Download,
  Eye,
  Edit,
  Gavel,
  FileText,
  Users,
  Calendar,
  Clock,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  Building2,
  IndianRupee,
  Briefcase,
  ScrollText,
  Bell,
  TrendingUp,
  BarChart3,
  UserCheck,
  Trash2,
  Loader2,
} from "lucide-react";

const CASE_TYPES = [
  { value: "civil", label: "Civil" },
  { value: "criminal", label: "Criminal" },
  { value: "labor", label: "Labor" },
  { value: "tax", label: "Tax" },
  { value: "intellectual_property", label: "Intellectual Property" },
  { value: "contract", label: "Contract" },
  { value: "arbitration", label: "Arbitration" },
  { value: "consumer", label: "Consumer" },
  { value: "environmental", label: "Environmental" },
  { value: "regulatory", label: "Regulatory" },
  { value: "corporate", label: "Corporate" },
  { value: "employment", label: "Employment" },
];

const CASE_STATUSES = [
  { value: "draft", label: "Draft", color: "bg-gray-500" },
  { value: "filed", label: "Filed", color: "bg-blue-500" },
  { value: "pending", label: "Pending", color: "bg-yellow-500" },
  { value: "in_progress", label: "In Progress", color: "bg-orange-500" },
  { value: "hearing_scheduled", label: "Hearing Scheduled", color: "bg-purple-500" },
  { value: "awaiting_judgment", label: "Awaiting Judgment", color: "bg-indigo-500" },
  { value: "settled", label: "Settled", color: "bg-green-500" },
  { value: "closed", label: "Closed", color: "bg-green-700" },
  { value: "dismissed", label: "Dismissed", color: "bg-red-500" },
];

const COURT_LEVELS = [
  { value: "district_court", label: "District Court" },
  { value: "sessions_court", label: "Sessions Court" },
  { value: "high_court", label: "High Court" },
  { value: "supreme_court", label: "Supreme Court" },
  { value: "tribunal", label: "Tribunal" },
  { value: "nclt", label: "NCLT" },
  { value: "nclat", label: "NCLAT" },
  { value: "itat", label: "ITAT" },
];

const PRIORITIES = [
  { value: "critical", label: "Critical", color: "bg-red-600" },
  { value: "high", label: "High", color: "bg-orange-500" },
  { value: "medium", label: "Medium", color: "bg-yellow-500" },
  { value: "low", label: "Low", color: "bg-green-500" },
];

// TypeScript interfaces
interface LegalCase {
  id: string;
  case_number: string;
  case_title: string;
  case_type: string;
  status: string;
  priority: string;
  court_level: string;
  court_name: string;
  our_role: string;
  opposing_party: string;
  claim_amount: number;
  next_hearing_date: string;
  external_counsel: string;
}

interface Contract {
  id: string;
  contract_number: string;
  title: string;
  contract_type: string;
  party_name: string;
  status: string;
  effective_date: string;
  expiry_date: string;
  contract_value: number;
}

// Mock data
const mockDashboardStats = {
  total_cases: 45,
  active_cases: 28,
  closed_cases: 17,
  pending_hearings: 12,
  overdue_tasks: 5,
  total_claim_amount: 125000000,
  total_expenses: 4500000,
  total_contracts: 156,
  expiring_contracts: 8,
  pending_notices: 3,
};

const mockCases = [
  {
    id: "1",
    case_number: "CASE-2025-00001",
    case_title: "XYZ Corp vs ABC Ltd - Contract Dispute",
    case_type: "contract",
    status: "hearing_scheduled",
    priority: "high",
    court_level: "high_court",
    court_name: "Bombay High Court",
    our_role: "defendant",
    opposing_party: "XYZ Corporation Pvt Ltd",
    claim_amount: 50000000,
    next_hearing_date: "2025-01-25",
    external_counsel: "Adv. Rajesh Sharma",
  },
  {
    id: "2",
    case_number: "CASE-2025-00002",
    case_title: "Employment Dispute - Former Employee",
    case_type: "labor",
    status: "in_progress",
    priority: "medium",
    court_level: "labor_court",
    court_name: "Industrial Tribunal, Mumbai",
    our_role: "respondent",
    opposing_party: "John Doe (Former Employee)",
    claim_amount: 2500000,
    next_hearing_date: "2025-02-10",
    external_counsel: "Adv. Priya Mehta",
  },
  {
    id: "3",
    case_number: "CASE-2024-00089",
    case_title: "Tax Assessment Appeal - FY 2021-22",
    case_type: "tax",
    status: "pending",
    priority: "critical",
    court_level: "itat",
    court_name: "ITAT Mumbai",
    our_role: "appellant",
    opposing_party: "Income Tax Department",
    claim_amount: 15000000,
    next_hearing_date: "2025-01-18",
    external_counsel: "Adv. Suresh Kumar",
  },
];

const mockHearings = [
  {
    id: "1",
    case_number: "CASE-2024-00089",
    case_title: "Tax Assessment Appeal",
    hearing_type: "arguments",
    scheduled_date: "2025-01-18",
    scheduled_time: "10:30 AM",
    court_name: "ITAT Mumbai",
    court_room: "Court Room 3",
    purpose: "Final Arguments",
    status: "scheduled",
  },
  {
    id: "2",
    case_number: "CASE-2025-00001",
    case_title: "XYZ Corp vs ABC Ltd",
    hearing_type: "evidence",
    scheduled_date: "2025-01-25",
    scheduled_time: "11:00 AM",
    court_name: "Bombay High Court",
    court_room: "Court Room 12",
    purpose: "Evidence Submission",
    status: "scheduled",
  },
];

const mockTasks = [
  {
    id: "1",
    task_number: "TASK-00125",
    title: "Prepare Written Statement",
    case_number: "CASE-2025-00001",
    task_type: "drafting",
    status: "overdue",
    priority: "high",
    due_date: "2025-01-10",
    assigned_to: "Legal Team",
  },
  {
    id: "2",
    task_number: "TASK-00126",
    title: "Review Evidence Documents",
    case_number: "CASE-2025-00002",
    task_type: "review",
    status: "in_progress",
    priority: "medium",
    due_date: "2025-01-20",
    assigned_to: "Adv. Priya Mehta",
  },
];

const mockContracts = [
  {
    id: "1",
    contract_number: "CON-2024-00045",
    title: "IT Services Agreement - TechVendor",
    contract_type: "service",
    party_name: "TechVendor Solutions Pvt Ltd",
    status: "active",
    effective_date: "2024-01-01",
    expiry_date: "2025-02-28",
    contract_value: 12000000,
  },
  {
    id: "2",
    contract_number: "CON-2024-00078",
    title: "Office Lease Agreement",
    contract_type: "lease",
    party_name: "Premium Properties Ltd",
    status: "active",
    effective_date: "2023-04-01",
    expiry_date: "2025-03-31",
    contract_value: 24000000,
  },
];

const mockCounsels = [
  {
    id: "1",
    counsel_code: "COUN-0001",
    name: "Adv. Rajesh Sharma",
    firm_name: "Sharma & Associates",
    specialization: ["Corporate Law", "Contract Disputes"],
    email: "rajesh@sharmalaw.com",
    phone: "+91 98765 43210",
    is_empanelled: true,
    rating: 5,
  },
  {
    id: "2",
    counsel_code: "COUN-0002",
    name: "Adv. Priya Mehta",
    firm_name: "Mehta Legal Services",
    specialization: ["Labor Law", "Employment"],
    email: "priya@mehtalegal.com",
    phone: "+91 98765 43211",
    is_empanelled: true,
    rating: 4,
  },
];

export default function LegalManagementPage() {
  const [activeTab, setActiveTab] = useState("dashboard");
  const [searchTerm, setSearchTerm] = useState("");
  const [caseTypeFilter, setCaseTypeFilter] = useState("all");
  const [statusFilter, setStatusFilter] = useState("all");
  const [isCaseDialogOpen, setIsCaseDialogOpen] = useState(false);
  const [isContractDialogOpen, setIsContractDialogOpen] = useState(false);
  const { showToast } = useToast();
  const deleteApi = useApi();

  // Local state for data management
  const [cases, setCases] = useState<LegalCase[]>(mockCases);
  const [contracts, setContracts] = useState<Contract[]>(mockContracts);

  // Delete state
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [itemToDelete, setItemToDelete] = useState<{ type: "case" | "contract"; item: LegalCase | Contract } | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  const handleDeleteClick = (type: "case" | "contract", item: LegalCase | Contract) => {
    setItemToDelete({ type, item });
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!itemToDelete) return;
    setIsDeleting(true);
    try {
      const endpoint = itemToDelete.type === "case"
        ? `/legal/cases/${itemToDelete.item.id}`
        : `/legal/contracts/${itemToDelete.item.id}`;

      await deleteApi.delete(endpoint);

      if (itemToDelete.type === "case") {
        setCases(cases.filter(c => c.id !== itemToDelete.item.id));
      } else {
        setContracts(contracts.filter(c => c.id !== itemToDelete.item.id));
      }

      setDeleteDialogOpen(false);
      setItemToDelete(null);
      showToast("success", `${itemToDelete.type === "case" ? "Case" : "Contract"} deleted successfully`);
    } catch (error) {
      console.error(`Failed to delete ${itemToDelete.type}:`, error);
      showToast("error", `Failed to delete ${itemToDelete.type}`);
    } finally {
      setIsDeleting(false);
    }
  };

  const getDeleteItemName = () => {
    if (!itemToDelete) return "";
    if (itemToDelete.type === "case") {
      return (itemToDelete.item as LegalCase).case_number;
    }
    return (itemToDelete.item as Contract).contract_number;
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat("en-IN", {
      style: "currency",
      currency: "INR",
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const getStatusBadge = (status: string) => {
    const statusConfig = CASE_STATUSES.find((s) => s.value === status);
    return (
      <Badge className={`${statusConfig?.color || "bg-gray-500"} text-white`}>
        {statusConfig?.label || status}
      </Badge>
    );
  };

  const getPriorityBadge = (priority: string) => {
    const priorityConfig = PRIORITIES.find((p) => p.value === priority);
    return (
      <Badge className={`${priorityConfig?.color || "bg-gray-500"} text-white`}>
        {priorityConfig?.label || priority}
      </Badge>
    );
  };

  return (
    <div className="flex-1 space-y-4 p-4 md:p-8 pt-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Legal Case Management</h2>
          <p className="text-muted-foreground">
            Manage legal cases, contracts, hearings, and compliance
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Button variant="outline">
            <Download className="mr-2 h-4 w-4" />
            Export
          </Button>
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <TabsList className="grid w-full grid-cols-7">
          <TabsTrigger value="dashboard">
            <BarChart3 className="mr-2 h-4 w-4" />
            Dashboard
          </TabsTrigger>
          <TabsTrigger value="cases">
            <Gavel className="mr-2 h-4 w-4" />
            Cases
          </TabsTrigger>
          <TabsTrigger value="hearings">
            <Calendar className="mr-2 h-4 w-4" />
            Hearings
          </TabsTrigger>
          <TabsTrigger value="tasks">
            <CheckCircle2 className="mr-2 h-4 w-4" />
            Tasks
          </TabsTrigger>
          <TabsTrigger value="contracts">
            <ScrollText className="mr-2 h-4 w-4" />
            Contracts
          </TabsTrigger>
          <TabsTrigger value="notices">
            <Bell className="mr-2 h-4 w-4" />
            Notices
          </TabsTrigger>
          <TabsTrigger value="counsels">
            <UserCheck className="mr-2 h-4 w-4" />
            Counsels
          </TabsTrigger>
        </TabsList>

        {/* Dashboard Tab */}
        <TabsContent value="dashboard" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-5">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Cases</CardTitle>
                <Gavel className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{mockDashboardStats.total_cases}</div>
                <div className="flex gap-2 mt-2">
                  <Badge variant="outline" className="text-orange-600">
                    {mockDashboardStats.active_cases} Active
                  </Badge>
                  <Badge variant="outline" className="text-green-600">
                    {mockDashboardStats.closed_cases} Closed
                  </Badge>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Pending Hearings</CardTitle>
                <Calendar className="h-4 w-4 text-blue-500" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{mockDashboardStats.pending_hearings}</div>
                <p className="text-xs text-muted-foreground mt-1">Scheduled this month</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Overdue Tasks</CardTitle>
                <AlertTriangle className="h-4 w-4 text-red-500" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-red-600">
                  {mockDashboardStats.overdue_tasks}
                </div>
                <p className="text-xs text-muted-foreground mt-1">Require immediate attention</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Claim Amount</CardTitle>
                <IndianRupee className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {formatCurrency(mockDashboardStats.total_claim_amount)}
                </div>
                <p className="text-xs text-muted-foreground mt-1">Active cases</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Legal Expenses</CardTitle>
                <TrendingUp className="h-4 w-4 text-green-500" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {formatCurrency(mockDashboardStats.total_expenses)}
                </div>
                <p className="text-xs text-muted-foreground mt-1">FY 2024-25</p>
              </CardContent>
            </Card>
          </div>

          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Contracts</CardTitle>
                <ScrollText className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{mockDashboardStats.total_contracts}</div>
                <Badge variant="outline" className="text-orange-600 mt-2">
                  {mockDashboardStats.expiring_contracts} Expiring Soon
                </Badge>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Pending Notices</CardTitle>
                <Bell className="h-4 w-4 text-yellow-500" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{mockDashboardStats.pending_notices}</div>
                <p className="text-xs text-muted-foreground mt-1">Awaiting response</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle className="text-sm font-medium">Cases by Type</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Contract</span>
                    <span className="font-medium">12</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span>Labor</span>
                    <span className="font-medium">8</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span>Tax</span>
                    <span className="font-medium">6</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span>Regulatory</span>
                    <span className="font-medium">5</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Upcoming Hearings</CardTitle>
                <CardDescription>Next 7 days</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {mockHearings.map((hearing) => (
                    <div
                      key={hearing.id}
                      className="flex items-center justify-between border-b pb-3 last:border-0"
                    >
                      <div>
                        <p className="font-medium text-sm">{hearing.case_title}</p>
                        <p className="text-xs text-muted-foreground">
                          {hearing.court_name} | {hearing.court_room}
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="text-sm font-medium">{hearing.scheduled_date}</p>
                        <p className="text-xs text-muted-foreground">{hearing.scheduled_time}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Overdue Tasks</CardTitle>
                <CardDescription>Require immediate attention</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {mockTasks
                    .filter((t) => t.status === "overdue")
                    .map((task) => (
                      <div
                        key={task.id}
                        className="flex items-center justify-between border-b pb-3 last:border-0"
                      >
                        <div>
                          <p className="font-medium text-sm">{task.title}</p>
                          <p className="text-xs text-muted-foreground">
                            {task.case_number} | {task.assigned_to}
                          </p>
                        </div>
                        <div className="text-right">
                          <Badge className="bg-red-500">Overdue</Badge>
                          <p className="text-xs text-muted-foreground mt-1">
                            Due: {task.due_date}
                          </p>
                        </div>
                      </div>
                    ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Cases Tab */}
        <TabsContent value="cases" className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Legal Cases</CardTitle>
                  <CardDescription>Manage all legal cases and matters</CardDescription>
                </div>
                <Dialog open={isCaseDialogOpen} onOpenChange={setIsCaseDialogOpen}>
                  <DialogTrigger asChild>
                    <Button>
                      <Plus className="mr-2 h-4 w-4" />
                      New Case
                    </Button>
                  </DialogTrigger>
                  <DialogContent className="max-w-2xl">
                    <DialogHeader>
                      <DialogTitle>Create New Case</DialogTitle>
                      <DialogDescription>Add a new legal case or matter</DialogDescription>
                    </DialogHeader>
                    <div className="grid gap-4 py-4">
                      <div className="space-y-2">
                        <Label>Case Title</Label>
                        <Input placeholder="Enter case title" />
                      </div>
                      <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-2">
                          <Label>Case Type</Label>
                          <Select>
                            <SelectTrigger>
                              <SelectValue placeholder="Select type" />
                            </SelectTrigger>
                            <SelectContent>
                              {CASE_TYPES.map((type) => (
                                <SelectItem key={type.value} value={type.value}>
                                  {type.label}
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                        </div>
                        <div className="space-y-2">
                          <Label>Priority</Label>
                          <Select>
                            <SelectTrigger>
                              <SelectValue placeholder="Select priority" />
                            </SelectTrigger>
                            <SelectContent>
                              {PRIORITIES.map((p) => (
                                <SelectItem key={p.value} value={p.value}>
                                  {p.label}
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                        </div>
                      </div>
                      <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-2">
                          <Label>Court Level</Label>
                          <Select>
                            <SelectTrigger>
                              <SelectValue placeholder="Select court" />
                            </SelectTrigger>
                            <SelectContent>
                              {COURT_LEVELS.map((court) => (
                                <SelectItem key={court.value} value={court.value}>
                                  {court.label}
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                        </div>
                        <div className="space-y-2">
                          <Label>Court Name</Label>
                          <Input placeholder="Enter court name" />
                        </div>
                      </div>
                      <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-2">
                          <Label>Our Role</Label>
                          <Select>
                            <SelectTrigger>
                              <SelectValue placeholder="Select role" />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="plaintiff">Plaintiff</SelectItem>
                              <SelectItem value="defendant">Defendant</SelectItem>
                              <SelectItem value="petitioner">Petitioner</SelectItem>
                              <SelectItem value="respondent">Respondent</SelectItem>
                              <SelectItem value="appellant">Appellant</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                        <div className="space-y-2">
                          <Label>Opposing Party</Label>
                          <Input placeholder="Enter opposing party name" />
                        </div>
                      </div>
                      <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-2">
                          <Label>Claim Amount (INR)</Label>
                          <Input type="number" placeholder="0.00" />
                        </div>
                        <div className="space-y-2">
                          <Label>Filing Date</Label>
                          <Input type="date" />
                        </div>
                      </div>
                      <div className="space-y-2">
                        <Label>Description</Label>
                        <Textarea placeholder="Case description and details" />
                      </div>
                    </div>
                    <DialogFooter>
                      <Button variant="outline" onClick={() => setIsCaseDialogOpen(false)}>
                        Cancel
                      </Button>
                      <Button onClick={() => setIsCaseDialogOpen(false)}>Create Case</Button>
                    </DialogFooter>
                  </DialogContent>
                </Dialog>
              </div>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-4 mb-4">
                <div className="relative flex-1">
                  <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                  <Input
                    placeholder="Search cases..."
                    className="pl-8"
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                  />
                </div>
                <Select value={caseTypeFilter} onValueChange={setCaseTypeFilter}>
                  <SelectTrigger className="w-[150px]">
                    <SelectValue placeholder="Case Type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Types</SelectItem>
                    {CASE_TYPES.map((type) => (
                      <SelectItem key={type.value} value={type.value}>
                        {type.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <Select value={statusFilter} onValueChange={setStatusFilter}>
                  <SelectTrigger className="w-[150px]">
                    <SelectValue placeholder="Status" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Status</SelectItem>
                    {CASE_STATUSES.map((status) => (
                      <SelectItem key={status.value} value={status.value}>
                        {status.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Case Number</TableHead>
                    <TableHead>Title</TableHead>
                    <TableHead>Type</TableHead>
                    <TableHead>Court</TableHead>
                    <TableHead>Claim Amount</TableHead>
                    <TableHead>Next Hearing</TableHead>
                    <TableHead>Priority</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {cases.map((legalCase) => (
                    <TableRow key={legalCase.id}>
                      <TableCell className="font-medium">{legalCase.case_number}</TableCell>
                      <TableCell>
                        <div>
                          <p className="font-medium">{legalCase.case_title}</p>
                          <p className="text-xs text-muted-foreground">
                            vs {legalCase.opposing_party}
                          </p>
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge variant="outline" className="capitalize">
                          {legalCase.case_type}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <div>
                          <p className="text-sm">{legalCase.court_name}</p>
                          <p className="text-xs text-muted-foreground capitalize">
                            {legalCase.court_level.replace("_", " ")}
                          </p>
                        </div>
                      </TableCell>
                      <TableCell>{formatCurrency(legalCase.claim_amount)}</TableCell>
                      <TableCell>{legalCase.next_hearing_date}</TableCell>
                      <TableCell>{getPriorityBadge(legalCase.priority)}</TableCell>
                      <TableCell>{getStatusBadge(legalCase.status)}</TableCell>
                      <TableCell>
                        <div className="flex gap-2">
                          <Button variant="ghost" size="icon">
                            <Eye className="h-4 w-4" />
                          </Button>
                          <Button variant="ghost" size="icon">
                            <Edit className="h-4 w-4" />
                          </Button>
                          {(legalCase.status === "closed" || legalCase.status === "dismissed" || legalCase.status === "settled") && (
                            <Button
                              variant="ghost"
                              size="icon"
                              className="text-red-600 hover:text-red-700 hover:bg-red-50"
                              onClick={() => handleDeleteClick("case", legalCase)}
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

        {/* Hearings Tab */}
        <TabsContent value="hearings" className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Court Hearings</CardTitle>
                  <CardDescription>Schedule and track court appearances</CardDescription>
                </div>
                <Button>
                  <Plus className="mr-2 h-4 w-4" />
                  Schedule Hearing
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Case</TableHead>
                    <TableHead>Hearing Type</TableHead>
                    <TableHead>Court</TableHead>
                    <TableHead>Date & Time</TableHead>
                    <TableHead>Purpose</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {mockHearings.map((hearing) => (
                    <TableRow key={hearing.id}>
                      <TableCell>
                        <div>
                          <p className="font-medium">{hearing.case_number}</p>
                          <p className="text-xs text-muted-foreground">{hearing.case_title}</p>
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge variant="outline" className="capitalize">
                          {hearing.hearing_type}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <div>
                          <p className="text-sm">{hearing.court_name}</p>
                          <p className="text-xs text-muted-foreground">{hearing.court_room}</p>
                        </div>
                      </TableCell>
                      <TableCell>
                        <div>
                          <p className="font-medium">{hearing.scheduled_date}</p>
                          <p className="text-xs text-muted-foreground">{hearing.scheduled_time}</p>
                        </div>
                      </TableCell>
                      <TableCell>{hearing.purpose}</TableCell>
                      <TableCell>
                        <Badge className="bg-blue-500">{hearing.status}</Badge>
                      </TableCell>
                      <TableCell>
                        <div className="flex gap-2">
                          <Button variant="ghost" size="icon">
                            <Eye className="h-4 w-4" />
                          </Button>
                          <Button variant="ghost" size="icon">
                            <Edit className="h-4 w-4" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Tasks Tab */}
        <TabsContent value="tasks" className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Legal Tasks</CardTitle>
                  <CardDescription>Track tasks and deadlines</CardDescription>
                </div>
                <Button>
                  <Plus className="mr-2 h-4 w-4" />
                  Add Task
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Task</TableHead>
                    <TableHead>Case</TableHead>
                    <TableHead>Type</TableHead>
                    <TableHead>Assigned To</TableHead>
                    <TableHead>Due Date</TableHead>
                    <TableHead>Priority</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {mockTasks.map((task) => (
                    <TableRow key={task.id}>
                      <TableCell>
                        <div>
                          <p className="font-medium">{task.title}</p>
                          <p className="text-xs text-muted-foreground">{task.task_number}</p>
                        </div>
                      </TableCell>
                      <TableCell>{task.case_number}</TableCell>
                      <TableCell>
                        <Badge variant="outline" className="capitalize">
                          {task.task_type}
                        </Badge>
                      </TableCell>
                      <TableCell>{task.assigned_to}</TableCell>
                      <TableCell>{task.due_date}</TableCell>
                      <TableCell>{getPriorityBadge(task.priority)}</TableCell>
                      <TableCell>
                        <Badge
                          className={
                            task.status === "overdue"
                              ? "bg-red-500"
                              : task.status === "in_progress"
                              ? "bg-yellow-500"
                              : "bg-green-500"
                          }
                        >
                          {task.status}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <div className="flex gap-2">
                          <Button variant="ghost" size="icon">
                            <CheckCircle2 className="h-4 w-4" />
                          </Button>
                          <Button variant="ghost" size="icon">
                            <Edit className="h-4 w-4" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Contracts Tab */}
        <TabsContent value="contracts" className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Legal Contracts</CardTitle>
                  <CardDescription>Manage contracts and agreements</CardDescription>
                </div>
                <Dialog open={isContractDialogOpen} onOpenChange={setIsContractDialogOpen}>
                  <DialogTrigger asChild>
                    <Button>
                      <Plus className="mr-2 h-4 w-4" />
                      New Contract
                    </Button>
                  </DialogTrigger>
                  <DialogContent className="max-w-2xl">
                    <DialogHeader>
                      <DialogTitle>Create New Contract</DialogTitle>
                      <DialogDescription>Add a new contract or agreement</DialogDescription>
                    </DialogHeader>
                    <div className="grid gap-4 py-4">
                      <div className="space-y-2">
                        <Label>Contract Title</Label>
                        <Input placeholder="Enter contract title" />
                      </div>
                      <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-2">
                          <Label>Contract Type</Label>
                          <Select>
                            <SelectTrigger>
                              <SelectValue placeholder="Select type" />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="service">Service Agreement</SelectItem>
                              <SelectItem value="supply">Supply Agreement</SelectItem>
                              <SelectItem value="employment">Employment Contract</SelectItem>
                              <SelectItem value="nda">NDA</SelectItem>
                              <SelectItem value="lease">Lease Agreement</SelectItem>
                              <SelectItem value="license">License Agreement</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                        <div className="space-y-2">
                          <Label>Party Type</Label>
                          <Select>
                            <SelectTrigger>
                              <SelectValue placeholder="Select party type" />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="vendor">Vendor</SelectItem>
                              <SelectItem value="customer">Customer</SelectItem>
                              <SelectItem value="employee">Employee</SelectItem>
                              <SelectItem value="partner">Partner</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                      </div>
                      <div className="space-y-2">
                        <Label>Party Name</Label>
                        <Input placeholder="Enter party name" />
                      </div>
                      <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-2">
                          <Label>Effective Date</Label>
                          <Input type="date" />
                        </div>
                        <div className="space-y-2">
                          <Label>Expiry Date</Label>
                          <Input type="date" />
                        </div>
                      </div>
                      <div className="space-y-2">
                        <Label>Contract Value (INR)</Label>
                        <Input type="number" placeholder="0.00" />
                      </div>
                    </div>
                    <DialogFooter>
                      <Button variant="outline" onClick={() => setIsContractDialogOpen(false)}>
                        Cancel
                      </Button>
                      <Button onClick={() => setIsContractDialogOpen(false)}>
                        Create Contract
                      </Button>
                    </DialogFooter>
                  </DialogContent>
                </Dialog>
              </div>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Contract Number</TableHead>
                    <TableHead>Title</TableHead>
                    <TableHead>Party</TableHead>
                    <TableHead>Type</TableHead>
                    <TableHead>Value</TableHead>
                    <TableHead>Expiry Date</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {contracts.map((contract) => (
                    <TableRow key={contract.id}>
                      <TableCell className="font-medium">{contract.contract_number}</TableCell>
                      <TableCell>{contract.title}</TableCell>
                      <TableCell>{contract.party_name}</TableCell>
                      <TableCell>
                        <Badge variant="outline" className="capitalize">
                          {contract.contract_type}
                        </Badge>
                      </TableCell>
                      <TableCell>{formatCurrency(contract.contract_value)}</TableCell>
                      <TableCell>
                        <span
                          className={
                            new Date(contract.expiry_date) < new Date(Date.now() + 30 * 24 * 60 * 60 * 1000)
                              ? "text-orange-600 font-medium"
                              : ""
                          }
                        >
                          {contract.expiry_date}
                        </span>
                      </TableCell>
                      <TableCell>
                        <Badge className={contract.status === "active" ? "bg-green-500" : contract.status === "expired" ? "bg-red-500" : "bg-gray-500"}>
                          {contract.status}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <div className="flex gap-2">
                          <Button variant="ghost" size="icon">
                            <Eye className="h-4 w-4" />
                          </Button>
                          <Button variant="ghost" size="icon">
                            <Edit className="h-4 w-4" />
                          </Button>
                          {(contract.status === "expired" || contract.status === "terminated") && (
                            <Button
                              variant="ghost"
                              size="icon"
                              className="text-red-600 hover:text-red-700 hover:bg-red-50"
                              onClick={() => handleDeleteClick("contract", contract)}
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

        {/* Notices Tab */}
        <TabsContent value="notices" className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Legal Notices</CardTitle>
                  <CardDescription>Track sent and received legal notices</CardDescription>
                </div>
                <Button>
                  <Plus className="mr-2 h-4 w-4" />
                  New Notice
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8 text-muted-foreground">
                No notices found. Click "New Notice" to create one.
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Counsels Tab */}
        <TabsContent value="counsels" className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Legal Counsels</CardTitle>
                  <CardDescription>Manage external legal counsels and law firms</CardDescription>
                </div>
                <Button>
                  <Plus className="mr-2 h-4 w-4" />
                  Add Counsel
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Code</TableHead>
                    <TableHead>Name</TableHead>
                    <TableHead>Firm</TableHead>
                    <TableHead>Specialization</TableHead>
                    <TableHead>Contact</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Rating</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {mockCounsels.map((counsel) => (
                    <TableRow key={counsel.id}>
                      <TableCell className="font-medium">{counsel.counsel_code}</TableCell>
                      <TableCell>{counsel.name}</TableCell>
                      <TableCell>{counsel.firm_name}</TableCell>
                      <TableCell>
                        <div className="flex flex-wrap gap-1">
                          {counsel.specialization.map((spec, idx) => (
                            <Badge key={idx} variant="outline" className="text-xs">
                              {spec}
                            </Badge>
                          ))}
                        </div>
                      </TableCell>
                      <TableCell>
                        <div>
                          <p className="text-sm">{counsel.email}</p>
                          <p className="text-xs text-muted-foreground">{counsel.phone}</p>
                        </div>
                      </TableCell>
                      <TableCell>
                        {counsel.is_empanelled ? (
                          <Badge className="bg-green-500">Empanelled</Badge>
                        ) : (
                          <Badge variant="outline">External</Badge>
                        )}
                      </TableCell>
                      <TableCell>
                        <div className="flex">
                          {[...Array(5)].map((_, i) => (
                            <span
                              key={i}
                              className={i < counsel.rating ? "text-yellow-500" : "text-gray-300"}
                            >
                              ★
                            </span>
                          ))}
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="flex gap-2">
                          <Button variant="ghost" size="icon">
                            <Eye className="h-4 w-4" />
                          </Button>
                          <Button variant="ghost" size="icon">
                            <Edit className="h-4 w-4" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
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
              Delete {itemToDelete?.type === "case" ? "Case" : "Contract"}
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
