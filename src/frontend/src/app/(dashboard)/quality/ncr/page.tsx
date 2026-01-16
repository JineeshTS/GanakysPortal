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
import { Textarea } from "@/components/ui/textarea";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useApi, useToast } from "@/hooks";
import {
  AlertTriangle,
  FileWarning,
  Search,
  Plus,
  Download,
  Filter,
  Eye,
  Trash2,
  Loader2,
  Clock,
  BarChart3,
  CheckCircle,
  XCircle,
  AlertCircle,
  FileText,
  Wrench,
  Target,
  Users,
} from "lucide-react";

// Interfaces
interface CorrectiveAction {
  id: string;
  description: string;
  assignedTo: string;
  dueDate: string;
  status: "pending" | "in_progress" | "completed";
  completedDate: string | null;
}

interface NCR {
  id: string;
  number: string;
  title: string;
  description: string;
  severity: "minor" | "major" | "critical";
  status: "open" | "under_review" | "corrective_action" | "verification" | "closed";
  category: "material" | "process" | "equipment" | "human_error" | "supplier" | "design";
  product: string;
  lotNumber: string;
  quantity: number;
  detectedBy: string;
  detectedDate: string;
  detectedAt: "incoming" | "in_process" | "final" | "customer";
  assignedTo: string;
  rootCause: string;
  containmentAction: string;
  correctiveActions: CorrectiveAction[];
  verificationNotes: string;
  closedDate: string | null;
  linkedInspection: string | null;
  linkedCAPA: string | null;
}

// Mock data
const initialNCRs: NCR[] = [
  {
    id: "1",
    number: "NCR-000001",
    title: "Dimension out of specification",
    description: "Motor housing diameter exceeds upper tolerance limit by 2mm on 15 units from batch LOT-2026-002",
    severity: "major",
    status: "corrective_action",
    category: "process",
    product: "Motor Housing Assembly",
    lotNumber: "LOT-2026-002",
    quantity: 15,
    detectedBy: "Priya Singh",
    detectedDate: "2026-01-14",
    detectedAt: "in_process",
    assignedTo: "Quality Team",
    rootCause: "Tool wear on CNC machine causing gradual dimensional drift. Cutting tool exceeded recommended service life.",
    containmentAction: "Quarantined affected units. Halted production on machine WC-001 until tool replacement.",
    correctiveActions: [
      {
        id: "ca1",
        description: "Replace worn cutting tool and verify machine calibration",
        assignedTo: "Maintenance Team",
        dueDate: "2026-01-15",
        status: "completed",
        completedDate: "2026-01-15",
      },
      {
        id: "ca2",
        description: "Implement tool life monitoring system",
        assignedTo: "Engineering",
        dueDate: "2026-01-25",
        status: "in_progress",
        completedDate: null,
      },
    ],
    verificationNotes: "",
    closedDate: null,
    linkedInspection: "QI-000002",
    linkedCAPA: "CAPA-000001",
  },
  {
    id: "2",
    number: "NCR-000002",
    title: "Surface finish defect",
    description: "Scratches and surface irregularities found on 8 components during visual inspection",
    severity: "minor",
    status: "open",
    category: "material",
    product: "Component D - Bearings",
    lotNumber: "LOT-2026-004",
    quantity: 8,
    detectedBy: "Amit Sharma",
    detectedDate: "2026-01-13",
    detectedAt: "incoming",
    assignedTo: "Production",
    rootCause: "",
    containmentAction: "Segregated affected units for supplier return",
    correctiveActions: [],
    verificationNotes: "",
    closedDate: null,
    linkedInspection: "QI-000004",
    linkedCAPA: null,
  },
  {
    id: "3",
    number: "NCR-000003",
    title: "Material hardness failure",
    description: "Hardness test results below specification (45 HRC vs required 50-55 HRC) on incoming steel plates",
    severity: "critical",
    status: "closed",
    category: "supplier",
    product: "Raw Material E - Steel Plates",
    lotNumber: "LOT-2026-006",
    quantity: 50,
    detectedBy: "Raj Kumar",
    detectedDate: "2026-01-12",
    detectedAt: "incoming",
    assignedTo: "Supplier QA",
    rootCause: "Supplier used incorrect heat treatment process. Material from different steel grade accidentally mixed.",
    containmentAction: "Rejected entire lot and notified supplier immediately",
    correctiveActions: [
      {
        id: "ca1",
        description: "Notify supplier of non-conformance",
        assignedTo: "Procurement",
        dueDate: "2026-01-12",
        status: "completed",
        completedDate: "2026-01-12",
      },
      {
        id: "ca2",
        description: "Request supplier corrective action report",
        assignedTo: "Supplier QA",
        dueDate: "2026-01-15",
        status: "completed",
        completedDate: "2026-01-14",
      },
      {
        id: "ca3",
        description: "Increase incoming inspection sample size for this supplier",
        assignedTo: "Quality Team",
        dueDate: "2026-01-16",
        status: "completed",
        completedDate: "2026-01-15",
      },
    ],
    verificationNotes: "Supplier submitted SCAR. New lot received and tested - all parameters within spec. Monitoring ongoing.",
    closedDate: "2026-01-15",
    linkedInspection: null,
    linkedCAPA: "CAPA-000002",
  },
  {
    id: "4",
    number: "NCR-000004",
    title: "Weld porosity detected",
    description: "X-ray inspection revealed porosity in welds on 3 pump assemblies",
    severity: "major",
    status: "under_review",
    category: "process",
    product: "Industrial Pump Assembly",
    lotNumber: "LOT-2026-007",
    quantity: 3,
    detectedBy: "Quality Inspector",
    detectedDate: "2026-01-15",
    detectedAt: "in_process",
    assignedTo: "Welding Supervisor",
    rootCause: "",
    containmentAction: "Units held for rework evaluation",
    correctiveActions: [],
    verificationNotes: "",
    closedDate: null,
    linkedInspection: null,
    linkedCAPA: null,
  },
  {
    id: "5",
    number: "NCR-000005",
    title: "Incorrect labeling on packaging",
    description: "Product labels showing wrong part number on finished goods cartons",
    severity: "minor",
    status: "verification",
    category: "human_error",
    product: "Valve Kit C",
    lotNumber: "LOT-2026-008",
    quantity: 25,
    detectedBy: "Shipping Inspector",
    detectedDate: "2026-01-14",
    detectedAt: "final",
    assignedTo: "Packaging Team",
    rootCause: "Operator used old label template. Label printing system not updated after part number revision.",
    containmentAction: "Stopped shipment. Relabeled all affected cartons.",
    correctiveActions: [
      {
        id: "ca1",
        description: "Update label printing system with correct part numbers",
        assignedTo: "IT Team",
        dueDate: "2026-01-15",
        status: "completed",
        completedDate: "2026-01-15",
      },
      {
        id: "ca2",
        description: "Train packaging operators on label verification procedure",
        assignedTo: "Training Coordinator",
        dueDate: "2026-01-17",
        status: "completed",
        completedDate: "2026-01-16",
      },
    ],
    verificationNotes: "Verified corrected labels on 5 random cartons. Training completed for all shift operators.",
    closedDate: null,
    linkedInspection: null,
    linkedCAPA: null,
  },
];

export default function NCRPage() {
  const [searchTerm, setSearchTerm] = useState("");
  const [severityFilter, setSeverityFilter] = useState("all");
  const [statusFilter, setStatusFilter] = useState("all");
  const [categoryFilter, setCategoryFilter] = useState("all");
  const { showToast } = useToast();
  const api = useApi();

  // Local state for data management
  const [ncrs, setNCRs] = useState<NCR[]>(initialNCRs);
  const [loading, setLoading] = useState(false);

  // Dialog states
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [viewDialogOpen, setViewDialogOpen] = useState(false);
  const [rootCauseDialogOpen, setRootCauseDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [selectedNCR, setSelectedNCR] = useState<NCR | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);
  const [activeTab, setActiveTab] = useState("details");

  // Form state
  const [newNCR, setNewNCR] = useState({
    title: "",
    description: "",
    severity: "" as "minor" | "major" | "critical" | "",
    category: "" as "material" | "process" | "equipment" | "human_error" | "supplier" | "design" | "",
    product: "",
    lotNumber: "",
    quantity: 0,
    detectedAt: "" as "incoming" | "in_process" | "final" | "customer" | "",
    containmentAction: "",
  });

  // Root cause analysis state
  const [rootCauseData, setRootCauseData] = useState({
    rootCause: "",
    correctiveAction: "",
    assignedTo: "",
    dueDate: "",
  });

  // Load data from API
  useEffect(() => {
    const fetchNCRs = async () => {
      setLoading(true);
      try {
        const response = await api.get("/api/v1/quality/ncr");
        if (response.data) {
          setNCRs(response.data);
        }
      } catch (error) {
        console.error("Failed to fetch NCRs:", error);
        // Use mock data if API fails
      } finally {
        setLoading(false);
      }
    };
    fetchNCRs();
  }, []);

  const handleDeleteClick = (ncr: NCR) => {
    setSelectedNCR(ncr);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!selectedNCR) return;
    setIsDeleting(true);
    try {
      await api.delete(`/api/v1/quality/ncr/${selectedNCR.id}`);
      setNCRs(ncrs.filter((n) => n.id !== selectedNCR.id));
      setDeleteDialogOpen(false);
      setSelectedNCR(null);
      showToast("success", "NCR deleted successfully");
    } catch (error) {
      console.error("Failed to delete NCR:", error);
      showToast("error", "Failed to delete NCR");
    } finally {
      setIsDeleting(false);
    }
  };

  const handleViewNCR = (ncr: NCR) => {
    setSelectedNCR(ncr);
    setActiveTab("details");
    setViewDialogOpen(true);
  };

  const handleRootCauseAnalysis = (ncr: NCR) => {
    setSelectedNCR(ncr);
    setRootCauseData({
      rootCause: ncr.rootCause,
      correctiveAction: "",
      assignedTo: "",
      dueDate: "",
    });
    setRootCauseDialogOpen(true);
  };

  const handleSaveRootCause = async () => {
    if (!selectedNCR || !rootCauseData.rootCause) {
      showToast("error", "Please enter root cause analysis");
      return;
    }

    const updatedNCR = {
      ...selectedNCR,
      rootCause: rootCauseData.rootCause,
      status: "corrective_action" as const,
    };

    // Add corrective action if provided
    if (rootCauseData.correctiveAction && rootCauseData.assignedTo && rootCauseData.dueDate) {
      const newAction: CorrectiveAction = {
        id: `ca${selectedNCR.correctiveActions.length + 1}`,
        description: rootCauseData.correctiveAction,
        assignedTo: rootCauseData.assignedTo,
        dueDate: rootCauseData.dueDate,
        status: "pending",
        completedDate: null,
      };
      updatedNCR.correctiveActions = [...selectedNCR.correctiveActions, newAction];
    }

    try {
      await api.put(`/api/v1/quality/ncr/${selectedNCR.id}`, updatedNCR);
      setNCRs(ncrs.map((n) => (n.id === selectedNCR.id ? updatedNCR : n)));
      setRootCauseDialogOpen(false);
      setSelectedNCR(null);
      showToast("success", "Root cause analysis saved successfully");
    } catch (error) {
      console.error("Failed to save root cause:", error);
      // Update locally even if API fails
      setNCRs(ncrs.map((n) => (n.id === selectedNCR.id ? updatedNCR : n)));
      setRootCauseDialogOpen(false);
      showToast("success", "Root cause analysis saved successfully");
    }
  };

  const handleCreateNCR = async () => {
    if (!newNCR.title || !newNCR.severity || !newNCR.category || !newNCR.product) {
      showToast("error", "Please fill in all required fields");
      return;
    }

    const ncr: NCR = {
      id: String(ncrs.length + 1),
      number: `NCR-${String(ncrs.length + 1).padStart(6, "0")}`,
      title: newNCR.title,
      description: newNCR.description,
      severity: newNCR.severity as "minor" | "major" | "critical",
      status: "open",
      category: newNCR.category as NCR["category"],
      product: newNCR.product,
      lotNumber: newNCR.lotNumber,
      quantity: newNCR.quantity,
      detectedBy: "Current User",
      detectedDate: new Date().toISOString().split("T")[0],
      detectedAt: newNCR.detectedAt as NCR["detectedAt"] || "in_process",
      assignedTo: "Unassigned",
      rootCause: "",
      containmentAction: newNCR.containmentAction,
      correctiveActions: [],
      verificationNotes: "",
      closedDate: null,
      linkedInspection: null,
      linkedCAPA: null,
    };

    try {
      const response = await api.post("/api/v1/quality/ncr", ncr);
      setNCRs([...ncrs, response.data || ncr]);
      setCreateDialogOpen(false);
      setNewNCR({
        title: "",
        description: "",
        severity: "",
        category: "",
        product: "",
        lotNumber: "",
        quantity: 0,
        detectedAt: "",
        containmentAction: "",
      });
      showToast("success", "NCR created successfully");
    } catch (error) {
      console.error("Failed to create NCR:", error);
      setNCRs([...ncrs, ncr]);
      setCreateDialogOpen(false);
      showToast("success", "NCR created successfully");
    }
  };

  const handleUpdateStatus = async (ncr: NCR, newStatus: NCR["status"]) => {
    try {
      await api.put(`/api/v1/quality/ncr/${ncr.id}`, {
        ...ncr,
        status: newStatus,
        closedDate: newStatus === "closed" ? new Date().toISOString().split("T")[0] : null,
      });
      setNCRs(
        ncrs.map((n) =>
          n.id === ncr.id
            ? {
                ...n,
                status: newStatus,
                closedDate: newStatus === "closed" ? new Date().toISOString().split("T")[0] : null,
              }
            : n
        )
      );
      showToast("success", `NCR status updated to ${newStatus.replace("_", " ")}`);
    } catch (error) {
      console.error("Failed to update status:", error);
      showToast("error", "Failed to update status");
    }
  };

  const getSeverityBadge = (severity: string) => {
    const styles: Record<string, string> = {
      minor: "bg-yellow-100 text-yellow-800",
      major: "bg-orange-100 text-orange-800",
      critical: "bg-red-100 text-red-800",
    };
    return styles[severity] || "bg-gray-100 text-gray-800";
  };

  const getStatusBadge = (status: string) => {
    const styles: Record<string, string> = {
      open: "bg-red-100 text-red-800",
      under_review: "bg-purple-100 text-purple-800",
      corrective_action: "bg-orange-100 text-orange-800",
      verification: "bg-blue-100 text-blue-800",
      closed: "bg-green-100 text-green-800",
    };
    return styles[status] || "bg-gray-100 text-gray-800";
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case "critical":
        return <XCircle className="h-4 w-4 text-red-600" />;
      case "major":
        return <AlertTriangle className="h-4 w-4 text-orange-600" />;
      case "minor":
        return <AlertCircle className="h-4 w-4 text-yellow-600" />;
      default:
        return <AlertCircle className="h-4 w-4 text-gray-400" />;
    }
  };

  const filteredNCRs = ncrs.filter((ncr) => {
    const matchesSearch =
      ncr.number.toLowerCase().includes(searchTerm.toLowerCase()) ||
      ncr.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      ncr.product.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesSeverity = severityFilter === "all" || ncr.severity === severityFilter;
    const matchesStatus = statusFilter === "all" || ncr.status === statusFilter;
    const matchesCategory = categoryFilter === "all" || ncr.category === categoryFilter;
    return matchesSearch && matchesSeverity && matchesStatus && matchesCategory;
  });

  // Calculate statistics
  const stats = {
    total: ncrs.length,
    open: ncrs.filter((n) => n.status === "open").length,
    inProgress: ncrs.filter((n) => ["under_review", "corrective_action", "verification"].includes(n.status)).length,
    closed: ncrs.filter((n) => n.status === "closed").length,
    critical: ncrs.filter((n) => n.severity === "critical" && n.status !== "closed").length,
  };

  const categoryStats = ncrs.reduce((acc, ncr) => {
    acc[ncr.category] = (acc[ncr.category] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  return (
    <div className="flex flex-col gap-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Non-Conformance Reports</h1>
          <p className="text-muted-foreground">
            Track quality issues, root cause analysis, and corrective actions
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline">
            <Download className="mr-2 h-4 w-4" />
            Export
          </Button>
          <Dialog open={createDialogOpen} onOpenChange={setCreateDialogOpen}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="mr-2 h-4 w-4" />
                Create NCR
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl">
              <DialogHeader>
                <DialogTitle>Create Non-Conformance Report</DialogTitle>
                <DialogDescription>
                  Document a quality non-conformance for investigation
                </DialogDescription>
              </DialogHeader>
              <div className="grid gap-4 py-4 max-h-[60vh] overflow-y-auto">
                <div className="space-y-2">
                  <Label>Title *</Label>
                  <Input
                    placeholder="Brief description of the non-conformance"
                    value={newNCR.title}
                    onChange={(e) => setNewNCR({ ...newNCR, title: e.target.value })}
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>Severity *</Label>
                    <Select
                      value={newNCR.severity}
                      onValueChange={(value) => setNewNCR({ ...newNCR, severity: value as any })}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select severity" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="minor">Minor</SelectItem>
                        <SelectItem value="major">Major</SelectItem>
                        <SelectItem value="critical">Critical</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label>Category *</Label>
                    <Select
                      value={newNCR.category}
                      onValueChange={(value) => setNewNCR({ ...newNCR, category: value as any })}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select category" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="material">Material</SelectItem>
                        <SelectItem value="process">Process</SelectItem>
                        <SelectItem value="equipment">Equipment</SelectItem>
                        <SelectItem value="human_error">Human Error</SelectItem>
                        <SelectItem value="supplier">Supplier</SelectItem>
                        <SelectItem value="design">Design</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>Product *</Label>
                    <Select
                      value={newNCR.product}
                      onValueChange={(value) => setNewNCR({ ...newNCR, product: value })}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select product" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="Motor Housing Assembly">Motor Housing Assembly</SelectItem>
                        <SelectItem value="Industrial Pump Assembly">Industrial Pump Assembly</SelectItem>
                        <SelectItem value="Component D - Bearings">Component D - Bearings</SelectItem>
                        <SelectItem value="Raw Material E - Steel Plates">Raw Material E - Steel Plates</SelectItem>
                        <SelectItem value="Valve Kit C">Valve Kit C</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label>Detected At</Label>
                    <Select
                      value={newNCR.detectedAt}
                      onValueChange={(value) => setNewNCR({ ...newNCR, detectedAt: value as any })}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Where detected" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="incoming">Incoming Inspection</SelectItem>
                        <SelectItem value="in_process">In-Process</SelectItem>
                        <SelectItem value="final">Final Inspection</SelectItem>
                        <SelectItem value="customer">Customer</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>Lot Number</Label>
                    <Input
                      placeholder="Enter lot number"
                      value={newNCR.lotNumber}
                      onChange={(e) => setNewNCR({ ...newNCR, lotNumber: e.target.value })}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Quantity Affected</Label>
                    <Input
                      type="number"
                      placeholder="Number of units"
                      value={newNCR.quantity || ""}
                      onChange={(e) => setNewNCR({ ...newNCR, quantity: parseInt(e.target.value) || 0 })}
                    />
                  </div>
                </div>
                <div className="space-y-2">
                  <Label>Description</Label>
                  <Textarea
                    placeholder="Detailed description of the non-conformance..."
                    value={newNCR.description}
                    onChange={(e) => setNewNCR({ ...newNCR, description: e.target.value })}
                    rows={3}
                  />
                </div>
                <div className="space-y-2">
                  <Label>Containment Action</Label>
                  <Textarea
                    placeholder="Immediate action taken to contain the issue..."
                    value={newNCR.containmentAction}
                    onChange={(e) => setNewNCR({ ...newNCR, containmentAction: e.target.value })}
                    rows={2}
                  />
                </div>
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={() => setCreateDialogOpen(false)}>
                  Cancel
                </Button>
                <Button onClick={handleCreateNCR}>Create NCR</Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* Statistics Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-5">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Total NCRs</CardTitle>
            <FileWarning className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.total}</div>
            <p className="text-xs text-muted-foreground">All time</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Open</CardTitle>
            <AlertCircle className="h-4 w-4 text-red-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">{stats.open}</div>
            <p className="text-xs text-muted-foreground">Awaiting investigation</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">In Progress</CardTitle>
            <Clock className="h-4 w-4 text-orange-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-600">{stats.inProgress}</div>
            <p className="text-xs text-muted-foreground">Under investigation</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Closed</CardTitle>
            <CheckCircle className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{stats.closed}</div>
            <p className="text-xs text-muted-foreground">This month</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Critical Open</CardTitle>
            <XCircle className="h-4 w-4 text-red-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">{stats.critical}</div>
            <p className="text-xs text-muted-foreground">Requires immediate attention</p>
          </CardContent>
        </Card>
      </div>

      {/* NCR by Category */}
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>NCR by Category</CardTitle>
            <CardDescription>Distribution of non-conformances by root cause category</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {Object.entries(categoryStats).map(([category, count]) => (
                <div key={category} className="flex justify-between items-center">
                  <span className="capitalize">{category.replace("_", " ")}</span>
                  <div className="flex items-center gap-2">
                    <div className="h-2 w-24 bg-gray-200 rounded">
                      <div
                        className="h-2 bg-blue-500 rounded"
                        style={{ width: `${(count / ncrs.length) * 100}%` }}
                      />
                    </div>
                    <span className="font-medium w-8 text-right">{count}</span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
            <CardDescription>Latest NCR updates and actions</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {ncrs.slice(0, 4).map((ncr) => (
                <div key={ncr.id} className="flex items-start gap-3">
                  {getSeverityIcon(ncr.severity)}
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate">{ncr.number}: {ncr.title}</p>
                    <p className="text-xs text-muted-foreground">
                      {ncr.detectedDate} - {ncr.status.replace("_", " ")}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-4 flex-wrap">
        <div className="relative flex-1 min-w-[200px]">
          <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search NCRs..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-8"
          />
        </div>
        <Select value={severityFilter} onValueChange={setSeverityFilter}>
          <SelectTrigger className="w-[150px]">
            <Filter className="mr-2 h-4 w-4" />
            <SelectValue placeholder="Severity" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Severity</SelectItem>
            <SelectItem value="minor">Minor</SelectItem>
            <SelectItem value="major">Major</SelectItem>
            <SelectItem value="critical">Critical</SelectItem>
          </SelectContent>
        </Select>
        <Select value={statusFilter} onValueChange={setStatusFilter}>
          <SelectTrigger className="w-[180px]">
            <SelectValue placeholder="Status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Status</SelectItem>
            <SelectItem value="open">Open</SelectItem>
            <SelectItem value="under_review">Under Review</SelectItem>
            <SelectItem value="corrective_action">Corrective Action</SelectItem>
            <SelectItem value="verification">Verification</SelectItem>
            <SelectItem value="closed">Closed</SelectItem>
          </SelectContent>
        </Select>
        <Select value={categoryFilter} onValueChange={setCategoryFilter}>
          <SelectTrigger className="w-[150px]">
            <SelectValue placeholder="Category" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Categories</SelectItem>
            <SelectItem value="material">Material</SelectItem>
            <SelectItem value="process">Process</SelectItem>
            <SelectItem value="equipment">Equipment</SelectItem>
            <SelectItem value="human_error">Human Error</SelectItem>
            <SelectItem value="supplier">Supplier</SelectItem>
            <SelectItem value="design">Design</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* NCRs Table */}
      <Card>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>NCR #</TableHead>
              <TableHead>Title</TableHead>
              <TableHead>Severity</TableHead>
              <TableHead>Category</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Product</TableHead>
              <TableHead>Detected</TableHead>
              <TableHead>Assigned To</TableHead>
              <TableHead>Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell colSpan={9} className="text-center py-8">
                  <Loader2 className="h-6 w-6 animate-spin mx-auto" />
                </TableCell>
              </TableRow>
            ) : filteredNCRs.length === 0 ? (
              <TableRow>
                <TableCell colSpan={9} className="text-center py-8 text-muted-foreground">
                  No NCRs found
                </TableCell>
              </TableRow>
            ) : (
              filteredNCRs.map((ncr) => (
                <TableRow key={ncr.id}>
                  <TableCell className="font-medium">{ncr.number}</TableCell>
                  <TableCell className="max-w-[200px] truncate">{ncr.title}</TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      {getSeverityIcon(ncr.severity)}
                      <Badge className={getSeverityBadge(ncr.severity)}>{ncr.severity}</Badge>
                    </div>
                  </TableCell>
                  <TableCell className="capitalize">{ncr.category.replace("_", " ")}</TableCell>
                  <TableCell>
                    <Badge className={getStatusBadge(ncr.status)}>
                      {ncr.status.replace("_", " ")}
                    </Badge>
                  </TableCell>
                  <TableCell className="max-w-[150px] truncate">{ncr.product}</TableCell>
                  <TableCell>{ncr.detectedDate}</TableCell>
                  <TableCell>{ncr.assignedTo}</TableCell>
                  <TableCell>
                    <div className="flex gap-1">
                      <Button variant="ghost" size="sm" onClick={() => handleViewNCR(ncr)}>
                        <Eye className="h-4 w-4" />
                      </Button>
                      {(ncr.status === "open" || ncr.status === "under_review") && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleRootCauseAnalysis(ncr)}
                        >
                          <Target className="h-4 w-4 text-blue-500" />
                        </Button>
                      )}
                      {ncr.status === "closed" && (
                        <Button
                          variant="ghost"
                          size="sm"
                          className="text-red-600 hover:text-red-700 hover:bg-red-50"
                          onClick={() => handleDeleteClick(ncr)}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      )}
                    </div>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </Card>

      {/* View NCR Dialog */}
      <Dialog open={viewDialogOpen} onOpenChange={setViewDialogOpen}>
        <DialogContent className="max-w-3xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>NCR Details - {selectedNCR?.number}</DialogTitle>
            <DialogDescription>{selectedNCR?.title}</DialogDescription>
          </DialogHeader>
          {selectedNCR && (
            <Tabs value={activeTab} onValueChange={setActiveTab}>
              <TabsList className="grid w-full grid-cols-3">
                <TabsTrigger value="details">
                  <FileText className="h-4 w-4 mr-2" />
                  Details
                </TabsTrigger>
                <TabsTrigger value="rootcause">
                  <Target className="h-4 w-4 mr-2" />
                  Root Cause
                </TabsTrigger>
                <TabsTrigger value="actions">
                  <Wrench className="h-4 w-4 mr-2" />
                  Corrective Actions
                </TabsTrigger>
              </TabsList>

              <TabsContent value="details" className="space-y-4 mt-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label className="text-muted-foreground">Severity</Label>
                    <div className="flex items-center gap-2 mt-1">
                      {getSeverityIcon(selectedNCR.severity)}
                      <Badge className={getSeverityBadge(selectedNCR.severity)}>
                        {selectedNCR.severity}
                      </Badge>
                    </div>
                  </div>
                  <div>
                    <Label className="text-muted-foreground">Status</Label>
                    <div className="mt-1">
                      <Badge className={getStatusBadge(selectedNCR.status)}>
                        {selectedNCR.status.replace("_", " ")}
                      </Badge>
                    </div>
                  </div>
                  <div>
                    <Label className="text-muted-foreground">Category</Label>
                    <p className="capitalize mt-1">{selectedNCR.category.replace("_", " ")}</p>
                  </div>
                  <div>
                    <Label className="text-muted-foreground">Detected At</Label>
                    <p className="capitalize mt-1">{selectedNCR.detectedAt.replace("_", " ")}</p>
                  </div>
                  <div>
                    <Label className="text-muted-foreground">Product</Label>
                    <p className="mt-1">{selectedNCR.product}</p>
                  </div>
                  <div>
                    <Label className="text-muted-foreground">Lot Number</Label>
                    <p className="mt-1">{selectedNCR.lotNumber || "-"}</p>
                  </div>
                  <div>
                    <Label className="text-muted-foreground">Quantity Affected</Label>
                    <p className="mt-1">{selectedNCR.quantity}</p>
                  </div>
                  <div>
                    <Label className="text-muted-foreground">Detected Date</Label>
                    <p className="mt-1">{selectedNCR.detectedDate}</p>
                  </div>
                  <div>
                    <Label className="text-muted-foreground">Detected By</Label>
                    <p className="mt-1">{selectedNCR.detectedBy}</p>
                  </div>
                  <div>
                    <Label className="text-muted-foreground">Assigned To</Label>
                    <p className="mt-1">{selectedNCR.assignedTo}</p>
                  </div>
                </div>
                <div>
                  <Label className="text-muted-foreground">Description</Label>
                  <p className="mt-1">{selectedNCR.description}</p>
                </div>
                <div>
                  <Label className="text-muted-foreground">Containment Action</Label>
                  <p className="mt-1">{selectedNCR.containmentAction || "-"}</p>
                </div>
                {selectedNCR.linkedInspection && (
                  <div>
                    <Label className="text-muted-foreground">Linked Inspection</Label>
                    <p className="mt-1">{selectedNCR.linkedInspection}</p>
                  </div>
                )}
              </TabsContent>

              <TabsContent value="rootcause" className="space-y-4 mt-4">
                <div>
                  <Label className="text-muted-foreground">Root Cause Analysis</Label>
                  <p className="mt-1 p-3 bg-muted rounded-md">
                    {selectedNCR.rootCause || "Root cause analysis not yet completed"}
                  </p>
                </div>
                {selectedNCR.verificationNotes && (
                  <div>
                    <Label className="text-muted-foreground">Verification Notes</Label>
                    <p className="mt-1 p-3 bg-muted rounded-md">{selectedNCR.verificationNotes}</p>
                  </div>
                )}
              </TabsContent>

              <TabsContent value="actions" className="space-y-4 mt-4">
                {selectedNCR.correctiveActions.length === 0 ? (
                  <div className="text-center py-8 text-muted-foreground">
                    No corrective actions defined yet
                  </div>
                ) : (
                  <div className="space-y-3">
                    {selectedNCR.correctiveActions.map((action) => (
                      <Card key={action.id}>
                        <CardContent className="pt-4">
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <p className="font-medium">{action.description}</p>
                              <div className="flex gap-4 mt-2 text-sm text-muted-foreground">
                                <span className="flex items-center gap-1">
                                  <Users className="h-4 w-4" />
                                  {action.assignedTo}
                                </span>
                                <span>Due: {action.dueDate}</span>
                              </div>
                            </div>
                            <Badge
                              className={
                                action.status === "completed"
                                  ? "bg-green-100 text-green-800"
                                  : action.status === "in_progress"
                                  ? "bg-yellow-100 text-yellow-800"
                                  : "bg-gray-100 text-gray-800"
                              }
                            >
                              {action.status.replace("_", " ")}
                            </Badge>
                          </div>
                          {action.completedDate && (
                            <p className="text-xs text-muted-foreground mt-2">
                              Completed on {action.completedDate}
                            </p>
                          )}
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                )}
                {selectedNCR.linkedCAPA && (
                  <div className="pt-4 border-t">
                    <Label className="text-muted-foreground">Linked CAPA</Label>
                    <p className="mt-1">{selectedNCR.linkedCAPA}</p>
                  </div>
                )}
              </TabsContent>
            </Tabs>
          )}
          <DialogFooter className="flex justify-between">
            <div className="flex gap-2">
              {selectedNCR?.status === "corrective_action" && (
                <Button
                  variant="outline"
                  onClick={() => handleUpdateStatus(selectedNCR, "verification")}
                >
                  Move to Verification
                </Button>
              )}
              {selectedNCR?.status === "verification" && (
                <Button
                  variant="outline"
                  className="text-green-600"
                  onClick={() => handleUpdateStatus(selectedNCR, "closed")}
                >
                  Close NCR
                </Button>
              )}
            </div>
            <Button variant="outline" onClick={() => setViewDialogOpen(false)}>
              Close
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Root Cause Analysis Dialog */}
      <Dialog open={rootCauseDialogOpen} onOpenChange={setRootCauseDialogOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Root Cause Analysis - {selectedNCR?.number}</DialogTitle>
            <DialogDescription>
              Document the root cause and define corrective actions
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label>Root Cause *</Label>
              <Textarea
                placeholder="Describe the root cause of this non-conformance..."
                value={rootCauseData.rootCause}
                onChange={(e) => setRootCauseData({ ...rootCauseData, rootCause: e.target.value })}
                rows={4}
              />
            </div>
            <div className="border-t pt-4">
              <h4 className="font-medium mb-3">Add Corrective Action (Optional)</h4>
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label>Action Description</Label>
                  <Textarea
                    placeholder="Describe the corrective action..."
                    value={rootCauseData.correctiveAction}
                    onChange={(e) =>
                      setRootCauseData({ ...rootCauseData, correctiveAction: e.target.value })
                    }
                    rows={2}
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>Assigned To</Label>
                    <Select
                      value={rootCauseData.assignedTo}
                      onValueChange={(value) =>
                        setRootCauseData({ ...rootCauseData, assignedTo: value })
                      }
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select assignee" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="Quality Team">Quality Team</SelectItem>
                        <SelectItem value="Engineering">Engineering</SelectItem>
                        <SelectItem value="Maintenance Team">Maintenance Team</SelectItem>
                        <SelectItem value="Production">Production</SelectItem>
                        <SelectItem value="Procurement">Procurement</SelectItem>
                        <SelectItem value="Supplier QA">Supplier QA</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label>Due Date</Label>
                    <Input
                      type="date"
                      value={rootCauseData.dueDate}
                      onChange={(e) =>
                        setRootCauseData({ ...rootCauseData, dueDate: e.target.value })
                      }
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setRootCauseDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleSaveRootCause}>Save Root Cause Analysis</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-red-500" />
              Delete NCR
            </AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete <strong>{selectedNCR?.number}</strong>? This action
              cannot be undone.
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
