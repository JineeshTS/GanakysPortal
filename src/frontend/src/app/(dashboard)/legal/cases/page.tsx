"use client";

import { useState, useEffect } from "react";
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
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
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
import { formatCurrency, formatDate } from "@/lib/format";
import {
  Plus,
  Search,
  Download,
  Eye,
  Edit,
  Gavel,
  Calendar,
  AlertTriangle,
  Building2,
  Users,
  IndianRupee,
  Trash2,
  Loader2,
  Filter,
  Clock,
  FileText,
} from "lucide-react";

// Constants
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
  { value: "labor_court", label: "Labor Court" },
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
  petitioner: string;
  respondent: string;
  claim_amount: number;
  filing_date: string;
  next_hearing_date: string;
  external_counsel: string;
  description: string;
  created_at: string;
  updated_at: string;
}

// Mock data
const mockCases: LegalCase[] = [
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
    petitioner: "XYZ Corporation Pvt Ltd",
    respondent: "ABC Ltd (Our Company)",
    claim_amount: 50000000,
    filing_date: "2024-11-15",
    next_hearing_date: "2025-01-25",
    external_counsel: "Adv. Rajesh Sharma",
    description: "Contract breach dispute regarding IT services agreement",
    created_at: "2024-11-15T10:00:00",
    updated_at: "2025-01-10T14:30:00",
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
    petitioner: "John Doe",
    respondent: "ABC Ltd (Our Company)",
    claim_amount: 2500000,
    filing_date: "2024-12-01",
    next_hearing_date: "2025-02-10",
    external_counsel: "Adv. Priya Mehta",
    description: "Wrongful termination claim by former employee",
    created_at: "2024-12-01T09:00:00",
    updated_at: "2025-01-05T11:00:00",
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
    petitioner: "ABC Ltd (Our Company)",
    respondent: "Income Tax Department",
    claim_amount: 15000000,
    filing_date: "2024-06-15",
    next_hearing_date: "2025-01-18",
    external_counsel: "Adv. Suresh Kumar",
    description: "Appeal against tax assessment order for FY 2021-22",
    created_at: "2024-06-15T14:00:00",
    updated_at: "2025-01-12T10:00:00",
  },
  {
    id: "4",
    case_number: "CASE-2024-00056",
    case_title: "IP Infringement - Trademark",
    case_type: "intellectual_property",
    status: "filed",
    priority: "high",
    court_level: "high_court",
    court_name: "Delhi High Court",
    our_role: "plaintiff",
    opposing_party: "Counterfeit Goods Inc",
    petitioner: "ABC Ltd (Our Company)",
    respondent: "Counterfeit Goods Inc",
    claim_amount: 10000000,
    filing_date: "2024-09-20",
    next_hearing_date: "2025-02-05",
    external_counsel: "Adv. Amit Desai",
    description: "Trademark infringement case against counterfeit goods seller",
    created_at: "2024-09-20T11:00:00",
    updated_at: "2025-01-08T16:00:00",
  },
];

export default function LegalCasesPage() {
  const api = useApi();
  const { showToast } = useToast();

  // State
  const [cases, setCases] = useState<LegalCase[]>(mockCases);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [caseTypeFilter, setCaseTypeFilter] = useState("all");
  const [statusFilter, setStatusFilter] = useState("all");
  const [priorityFilter, setPriorityFilter] = useState("all");

  // Dialog states
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isViewDialogOpen, setIsViewDialogOpen] = useState(false);
  const [selectedCase, setSelectedCase] = useState<LegalCase | null>(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [caseToDelete, setCaseToDelete] = useState<LegalCase | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  // Form state
  const [formData, setFormData] = useState({
    case_title: "",
    case_type: "",
    priority: "medium",
    court_level: "",
    court_name: "",
    our_role: "",
    opposing_party: "",
    claim_amount: "",
    filing_date: "",
    description: "",
  });
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Fetch cases from API
  useEffect(() => {
    const fetchCases = async () => {
      setLoading(true);
      try {
        const response = await api.get("/legal/cases?limit=100");
        if (response?.data && Array.isArray(response.data)) {
          setCases(response.data.length > 0 ? response.data : mockCases);
        }
      } catch (error) {
        console.error("Failed to fetch cases:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchCases();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Filter cases
  const filteredCases = cases.filter((c) => {
    const matchesSearch =
      !searchTerm ||
      c.case_number.toLowerCase().includes(searchTerm.toLowerCase()) ||
      c.case_title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      c.opposing_party.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesType = caseTypeFilter === "all" || c.case_type === caseTypeFilter;
    const matchesStatus = statusFilter === "all" || c.status === statusFilter;
    const matchesPriority = priorityFilter === "all" || c.priority === priorityFilter;

    return matchesSearch && matchesType && matchesStatus && matchesPriority;
  });

  // Helpers
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

  const isUpcomingHearing = (date: string) => {
    const hearingDate = new Date(date);
    const today = new Date();
    const diffDays = Math.ceil((hearingDate.getTime() - today.getTime()) / (1000 * 60 * 60 * 24));
    return diffDays >= 0 && diffDays <= 7;
  };

  // Handlers
  const handleViewCase = (legalCase: LegalCase) => {
    setSelectedCase(legalCase);
    setIsViewDialogOpen(true);
  };

  const handleDeleteClick = (legalCase: LegalCase) => {
    setCaseToDelete(legalCase);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!caseToDelete) return;
    setIsDeleting(true);

    try {
      await api.delete(`/legal/cases/${caseToDelete.id}`);
      setCases(cases.filter((c) => c.id !== caseToDelete.id));
      setDeleteDialogOpen(false);
      setCaseToDelete(null);
      showToast("success", "Case deleted successfully");
    } catch (error) {
      console.error("Failed to delete case:", error);
      showToast("error", "Failed to delete case");
    } finally {
      setIsDeleting(false);
    }
  };

  const handleCreateCase = async () => {
    if (!formData.case_title || !formData.case_type) {
      showToast("error", "Please fill in required fields");
      return;
    }

    setIsSubmitting(true);
    try {
      const response = await api.post("/legal/cases", {
        ...formData,
        claim_amount: formData.claim_amount ? parseFloat(formData.claim_amount) : 0,
      });

      if (response) {
        setCases([response as LegalCase, ...cases]);
        showToast("success", "Case created successfully");
        setIsCreateDialogOpen(false);
        setFormData({
          case_title: "",
          case_type: "",
          priority: "medium",
          court_level: "",
          court_name: "",
          our_role: "",
          opposing_party: "",
          claim_amount: "",
          filing_date: "",
          description: "",
        });
      }
    } catch (error) {
      console.error("Failed to create case:", error);
      showToast("error", "Failed to create case");
    } finally {
      setIsSubmitting(false);
    }
  };

  // Stats
  const stats = {
    total: cases.length,
    active: cases.filter((c) => !["closed", "dismissed", "settled"].includes(c.status)).length,
    upcomingHearings: cases.filter((c) => c.next_hearing_date && isUpcomingHearing(c.next_hearing_date)).length,
    criticalCases: cases.filter((c) => c.priority === "critical").length,
  };

  return (
    <div className="flex-1 space-y-4 p-4 md:p-8 pt-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Legal Cases</h2>
          <p className="text-muted-foreground">
            Manage all legal cases and matters
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Button variant="outline">
            <Download className="mr-2 h-4 w-4" />
            Export
          </Button>
          <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
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
                  <Label>Case Title *</Label>
                  <Input
                    placeholder="Enter case title"
                    value={formData.case_title}
                    onChange={(e) => setFormData({ ...formData, case_title: e.target.value })}
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>Case Type *</Label>
                    <Select
                      value={formData.case_type}
                      onValueChange={(value) => setFormData({ ...formData, case_type: value })}
                    >
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
                    <Select
                      value={formData.priority}
                      onValueChange={(value) => setFormData({ ...formData, priority: value })}
                    >
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
                    <Select
                      value={formData.court_level}
                      onValueChange={(value) => setFormData({ ...formData, court_level: value })}
                    >
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
                    <Input
                      placeholder="Enter court name"
                      value={formData.court_name}
                      onChange={(e) => setFormData({ ...formData, court_name: e.target.value })}
                    />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>Our Role</Label>
                    <Select
                      value={formData.our_role}
                      onValueChange={(value) => setFormData({ ...formData, our_role: value })}
                    >
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
                    <Input
                      placeholder="Enter opposing party name"
                      value={formData.opposing_party}
                      onChange={(e) => setFormData({ ...formData, opposing_party: e.target.value })}
                    />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>Claim Amount (INR)</Label>
                    <Input
                      type="number"
                      placeholder="0.00"
                      value={formData.claim_amount}
                      onChange={(e) => setFormData({ ...formData, claim_amount: e.target.value })}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Filing Date</Label>
                    <Input
                      type="date"
                      value={formData.filing_date}
                      onChange={(e) => setFormData({ ...formData, filing_date: e.target.value })}
                    />
                  </div>
                </div>
                <div className="space-y-2">
                  <Label>Description</Label>
                  <Textarea
                    placeholder="Case description and details"
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  />
                </div>
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={() => setIsCreateDialogOpen(false)}>
                  Cancel
                </Button>
                <Button onClick={handleCreateCase} disabled={isSubmitting}>
                  {isSubmitting ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Creating...
                    </>
                  ) : (
                    "Create Case"
                  )}
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Cases</CardTitle>
            <Gavel className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.total}</div>
            <p className="text-xs text-muted-foreground">{stats.active} active</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Upcoming Hearings</CardTitle>
            <Calendar className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.upcomingHearings}</div>
            <p className="text-xs text-muted-foreground">Within 7 days</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Critical Cases</CardTitle>
            <AlertTriangle className="h-4 w-4 text-red-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">{stats.criticalCases}</div>
            <p className="text-xs text-muted-foreground">Require attention</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Claim Value</CardTitle>
            <IndianRupee className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {formatCurrency(cases.reduce((sum, c) => sum + (c.claim_amount || 0), 0))}
            </div>
            <p className="text-xs text-muted-foreground">All cases</p>
          </CardContent>
        </Card>
      </div>

      {/* Filters and Table */}
      <Card>
        <CardHeader>
          <CardTitle>Case List</CardTitle>
          <CardDescription>View and manage all legal cases</CardDescription>
        </CardHeader>
        <CardContent>
          {/* Filters */}
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
            <Select value={priorityFilter} onValueChange={setPriorityFilter}>
              <SelectTrigger className="w-[150px]">
                <SelectValue placeholder="Priority" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Priority</SelectItem>
                {PRIORITIES.map((p) => (
                  <SelectItem key={p.value} value={p.value}>
                    {p.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Table */}
          {loading ? (
            <div className="flex items-center justify-center h-64">
              <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
            </div>
          ) : filteredCases.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              No cases found. Click "New Case" to create one.
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Case Number</TableHead>
                  <TableHead>Title / Parties</TableHead>
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
                {filteredCases.map((legalCase) => (
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
                        {legalCase.case_type.replace("_", " ")}
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
                    <TableCell>
                      <div className="flex items-center gap-2">
                        {legalCase.next_hearing_date && isUpcomingHearing(legalCase.next_hearing_date) && (
                          <Clock className="h-4 w-4 text-orange-500" />
                        )}
                        <span className={isUpcomingHearing(legalCase.next_hearing_date) ? "text-orange-600 font-medium" : ""}>
                          {formatDate(legalCase.next_hearing_date)}
                        </span>
                      </div>
                    </TableCell>
                    <TableCell>{getPriorityBadge(legalCase.priority)}</TableCell>
                    <TableCell>{getStatusBadge(legalCase.status)}</TableCell>
                    <TableCell>
                      <div className="flex gap-2">
                        <Button variant="ghost" size="icon" onClick={() => handleViewCase(legalCase)}>
                          <Eye className="h-4 w-4" />
                        </Button>
                        <Button variant="ghost" size="icon">
                          <Edit className="h-4 w-4" />
                        </Button>
                        {["closed", "dismissed", "settled"].includes(legalCase.status) && (
                          <Button
                            variant="ghost"
                            size="icon"
                            className="text-red-600 hover:text-red-700 hover:bg-red-50"
                            onClick={() => handleDeleteClick(legalCase)}
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
          )}
        </CardContent>
      </Card>

      {/* View Case Dialog */}
      <Dialog open={isViewDialogOpen} onOpenChange={setIsViewDialogOpen}>
        <DialogContent className="max-w-3xl">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Gavel className="h-5 w-5" />
              {selectedCase?.case_number}
            </DialogTitle>
            <DialogDescription>{selectedCase?.case_title}</DialogDescription>
          </DialogHeader>
          {selectedCase && (
            <div className="grid gap-6 py-4">
              {/* Status and Priority */}
              <div className="flex items-center gap-4">
                {getStatusBadge(selectedCase.status)}
                {getPriorityBadge(selectedCase.priority)}
                <Badge variant="outline" className="capitalize">
                  {selectedCase.case_type.replace("_", " ")}
                </Badge>
              </div>

              {/* Parties */}
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1">
                  <Label className="text-xs text-muted-foreground">Petitioner</Label>
                  <div className="flex items-center gap-2">
                    <Users className="h-4 w-4 text-muted-foreground" />
                    <span>{selectedCase.petitioner}</span>
                  </div>
                </div>
                <div className="space-y-1">
                  <Label className="text-xs text-muted-foreground">Respondent</Label>
                  <div className="flex items-center gap-2">
                    <Users className="h-4 w-4 text-muted-foreground" />
                    <span>{selectedCase.respondent}</span>
                  </div>
                </div>
              </div>

              {/* Court Details */}
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1">
                  <Label className="text-xs text-muted-foreground">Court Name</Label>
                  <div className="flex items-center gap-2">
                    <Building2 className="h-4 w-4 text-muted-foreground" />
                    <span>{selectedCase.court_name}</span>
                  </div>
                </div>
                <div className="space-y-1">
                  <Label className="text-xs text-muted-foreground">Court Level</Label>
                  <span className="capitalize">{selectedCase.court_level.replace("_", " ")}</span>
                </div>
              </div>

              {/* Dates and Amounts */}
              <div className="grid grid-cols-3 gap-4">
                <div className="space-y-1">
                  <Label className="text-xs text-muted-foreground">Filing Date</Label>
                  <div className="flex items-center gap-2">
                    <Calendar className="h-4 w-4 text-muted-foreground" />
                    <span>{formatDate(selectedCase.filing_date)}</span>
                  </div>
                </div>
                <div className="space-y-1">
                  <Label className="text-xs text-muted-foreground">Next Hearing</Label>
                  <div className="flex items-center gap-2">
                    <Calendar className="h-4 w-4 text-blue-500" />
                    <span className={isUpcomingHearing(selectedCase.next_hearing_date) ? "text-orange-600 font-medium" : ""}>
                      {formatDate(selectedCase.next_hearing_date)}
                    </span>
                  </div>
                </div>
                <div className="space-y-1">
                  <Label className="text-xs text-muted-foreground">Claim Amount</Label>
                  <div className="flex items-center gap-2">
                    <IndianRupee className="h-4 w-4 text-muted-foreground" />
                    <span className="font-medium">{formatCurrency(selectedCase.claim_amount)}</span>
                  </div>
                </div>
              </div>

              {/* External Counsel */}
              <div className="space-y-1">
                <Label className="text-xs text-muted-foreground">External Counsel</Label>
                <p>{selectedCase.external_counsel || "Not assigned"}</p>
              </div>

              {/* Description */}
              <div className="space-y-1">
                <Label className="text-xs text-muted-foreground">Description</Label>
                <div className="p-3 bg-muted/50 rounded-md text-sm">
                  {selectedCase.description || "No description provided"}
                </div>
              </div>
            </div>
          )}
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsViewDialogOpen(false)}>
              Close
            </Button>
            <Button>
              <Edit className="mr-2 h-4 w-4" />
              Edit Case
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
              Delete Case
            </AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete <strong>{caseToDelete?.case_number}</strong>?
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
