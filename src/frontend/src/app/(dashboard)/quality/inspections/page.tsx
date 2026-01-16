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
import { Checkbox } from "@/components/ui/checkbox";
import { useApi, useToast } from "@/hooks";
import {
  CheckCircle,
  XCircle,
  AlertTriangle,
  ClipboardCheck,
  Search,
  Plus,
  Download,
  Filter,
  Eye,
  Calendar,
  Trash2,
  Loader2,
  Clock,
  BarChart3,
  Edit,
  ListChecks,
  Play,
} from "lucide-react";

// Interfaces
interface ChecklistItem {
  id: string;
  description: string;
  passed: boolean | null;
  notes: string;
}

interface Inspection {
  id: string;
  number: string;
  type: "incoming" | "in_process" | "final" | "supplier";
  product: string;
  lotNumber: string;
  result: "pass" | "fail" | "conditional" | "pending";
  status: "scheduled" | "in_progress" | "completed" | "cancelled";
  scheduledDate: string;
  completedDate: string | null;
  inspector: string;
  checklist: ChecklistItem[];
  notes: string;
}

// Mock data
const initialInspections: Inspection[] = [
  {
    id: "1",
    number: "QI-000001",
    type: "incoming",
    product: "Raw Material A - Steel Plates",
    lotNumber: "LOT-2026-001",
    result: "pass",
    status: "completed",
    scheduledDate: "2026-01-14",
    completedDate: "2026-01-14",
    inspector: "Raj Kumar",
    checklist: [
      { id: "c1", description: "Visual inspection for defects", passed: true, notes: "" },
      { id: "c2", description: "Dimensional verification", passed: true, notes: "" },
      { id: "c3", description: "Material certification check", passed: true, notes: "" },
    ],
    notes: "All parameters within specification",
  },
  {
    id: "2",
    number: "QI-000002",
    type: "in_process",
    product: "Assembly B - Motor Housing",
    lotNumber: "LOT-2026-002",
    result: "fail",
    status: "completed",
    scheduledDate: "2026-01-14",
    completedDate: "2026-01-14",
    inspector: "Priya Singh",
    checklist: [
      { id: "c1", description: "Torque verification", passed: true, notes: "" },
      { id: "c2", description: "Alignment check", passed: false, notes: "2mm deviation observed" },
      { id: "c3", description: "Weld quality inspection", passed: true, notes: "" },
    ],
    notes: "NCR-000004 raised for alignment deviation",
  },
  {
    id: "3",
    number: "QI-000003",
    type: "final",
    product: "Finished Good C - Industrial Pump",
    lotNumber: "LOT-2026-003",
    result: "pending",
    status: "scheduled",
    scheduledDate: "2026-01-16",
    completedDate: null,
    inspector: "Assigned",
    checklist: [
      { id: "c1", description: "Functional test", passed: null, notes: "" },
      { id: "c2", description: "Leak test", passed: null, notes: "" },
      { id: "c3", description: "Performance verification", passed: null, notes: "" },
      { id: "c4", description: "Packaging inspection", passed: null, notes: "" },
    ],
    notes: "",
  },
  {
    id: "4",
    number: "QI-000004",
    type: "supplier",
    product: "Component D - Bearings",
    lotNumber: "LOT-2026-004",
    result: "conditional",
    status: "completed",
    scheduledDate: "2026-01-13",
    completedDate: "2026-01-13",
    inspector: "Amit Sharma",
    checklist: [
      { id: "c1", description: "Certificate verification", passed: true, notes: "" },
      { id: "c2", description: "Sample testing", passed: true, notes: "" },
      { id: "c3", description: "Dimensional check", passed: false, notes: "Minor deviation within tolerance" },
    ],
    notes: "Accepted with minor deviation documented",
  },
  {
    id: "5",
    number: "QI-000005",
    type: "incoming",
    product: "Raw Material E - Copper Wire",
    lotNumber: "LOT-2026-005",
    result: "pending",
    status: "in_progress",
    scheduledDate: "2026-01-15",
    completedDate: null,
    inspector: "Raj Kumar",
    checklist: [
      { id: "c1", description: "Conductivity test", passed: true, notes: "" },
      { id: "c2", description: "Diameter verification", passed: null, notes: "" },
      { id: "c3", description: "Surface quality check", passed: null, notes: "" },
    ],
    notes: "In progress",
  },
];

const checklistTemplates = [
  {
    type: "incoming",
    items: [
      "Visual inspection for defects",
      "Dimensional verification",
      "Material certification check",
      "Quantity verification",
      "Packaging condition",
    ],
  },
  {
    type: "in_process",
    items: [
      "Process parameter verification",
      "Dimensional check",
      "Visual inspection",
      "Assembly verification",
      "Documentation check",
    ],
  },
  {
    type: "final",
    items: [
      "Functional test",
      "Performance verification",
      "Safety check",
      "Cosmetic inspection",
      "Packaging inspection",
      "Documentation completeness",
    ],
  },
  {
    type: "supplier",
    items: [
      "Certificate verification",
      "Sample testing",
      "Dimensional check",
      "Material composition test",
      "Traceability verification",
    ],
  },
];

export default function InspectionsPage() {
  const [searchTerm, setSearchTerm] = useState("");
  const [typeFilter, setTypeFilter] = useState("all");
  const [statusFilter, setStatusFilter] = useState("all");
  const [resultFilter, setResultFilter] = useState("all");
  const { showToast } = useToast();
  const api = useApi();

  // Local state for data management
  const [inspections, setInspections] = useState<Inspection[]>(initialInspections);
  const [loading, setLoading] = useState(false);

  // Dialog states
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [viewDialogOpen, setViewDialogOpen] = useState(false);
  const [checklistDialogOpen, setChecklistDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [selectedInspection, setSelectedInspection] = useState<Inspection | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  // Form state
  const [newInspection, setNewInspection] = useState({
    type: "" as "incoming" | "in_process" | "final" | "supplier" | "",
    product: "",
    lotNumber: "",
    scheduledDate: "",
    inspector: "",
    notes: "",
  });

  // Checklist state
  const [checklistState, setChecklistState] = useState<ChecklistItem[]>([]);

  // Load data from API
  useEffect(() => {
    const fetchInspections = async () => {
      setLoading(true);
      try {
        const response = await api.get("/api/v1/quality/inspections");
        if (response.data) {
          setInspections(response.data);
        }
      } catch (error) {
        console.error("Failed to fetch inspections:", error);
        // Use mock data if API fails
      } finally {
        setLoading(false);
      }
    };
    fetchInspections();
  }, []);

  const handleDeleteClick = (inspection: Inspection) => {
    setSelectedInspection(inspection);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!selectedInspection) return;
    setIsDeleting(true);
    try {
      await api.delete(`/api/v1/quality/inspections/${selectedInspection.id}`);
      setInspections(inspections.filter((i) => i.id !== selectedInspection.id));
      setDeleteDialogOpen(false);
      setSelectedInspection(null);
      showToast("success", "Inspection deleted successfully");
    } catch (error) {
      console.error("Failed to delete inspection:", error);
      showToast("error", "Failed to delete inspection");
    } finally {
      setIsDeleting(false);
    }
  };

  const handleViewInspection = (inspection: Inspection) => {
    setSelectedInspection(inspection);
    setViewDialogOpen(true);
  };

  const handleStartInspection = (inspection: Inspection) => {
    setSelectedInspection(inspection);
    setChecklistState([...inspection.checklist]);
    setChecklistDialogOpen(true);
  };

  const handleChecklistChange = (itemId: string, passed: boolean) => {
    setChecklistState(
      checklistState.map((item) =>
        item.id === itemId ? { ...item, passed } : item
      )
    );
  };

  const handleChecklistNotes = (itemId: string, notes: string) => {
    setChecklistState(
      checklistState.map((item) =>
        item.id === itemId ? { ...item, notes } : item
      )
    );
  };

  const handleCompleteInspection = async () => {
    if (!selectedInspection) return;

    const allChecked = checklistState.every((item) => item.passed !== null);
    if (!allChecked) {
      showToast("error", "Please complete all checklist items");
      return;
    }

    const allPassed = checklistState.every((item) => item.passed === true);
    const anyFailed = checklistState.some((item) => item.passed === false);

    const result = allPassed ? "pass" : anyFailed ? "fail" : "conditional";

    try {
      await api.put(`/api/v1/quality/inspections/${selectedInspection.id}`, {
        status: "completed",
        result,
        checklist: checklistState,
        completedDate: new Date().toISOString().split("T")[0],
      });

      setInspections(
        inspections.map((i) =>
          i.id === selectedInspection.id
            ? {
                ...i,
                status: "completed",
                result,
                checklist: checklistState,
                completedDate: new Date().toISOString().split("T")[0],
              }
            : i
        )
      );

      setChecklistDialogOpen(false);
      setSelectedInspection(null);
      showToast("success", `Inspection completed with result: ${result.toUpperCase()}`);
    } catch (error) {
      console.error("Failed to complete inspection:", error);
      showToast("error", "Failed to complete inspection");
    }
  };

  const handleCreateInspection = async () => {
    if (!newInspection.type || !newInspection.product || !newInspection.scheduledDate) {
      showToast("error", "Please fill in all required fields");
      return;
    }

    const template = checklistTemplates.find((t) => t.type === newInspection.type);
    const checklist: ChecklistItem[] =
      template?.items.map((item, index) => ({
        id: `c${index + 1}`,
        description: item,
        passed: null,
        notes: "",
      })) || [];

    const inspection: Inspection = {
      id: String(inspections.length + 1),
      number: `QI-${String(inspections.length + 1).padStart(6, "0")}`,
      type: newInspection.type as "incoming" | "in_process" | "final" | "supplier",
      product: newInspection.product,
      lotNumber: newInspection.lotNumber,
      result: "pending",
      status: "scheduled",
      scheduledDate: newInspection.scheduledDate,
      completedDate: null,
      inspector: newInspection.inspector || "Unassigned",
      checklist,
      notes: newInspection.notes,
    };

    try {
      const response = await api.post("/api/v1/quality/inspections", inspection);
      setInspections([...inspections, response.data || inspection]);
      setCreateDialogOpen(false);
      setNewInspection({
        type: "",
        product: "",
        lotNumber: "",
        scheduledDate: "",
        inspector: "",
        notes: "",
      });
      showToast("success", "Inspection scheduled successfully");
    } catch (error) {
      console.error("Failed to create inspection:", error);
      // Add locally even if API fails
      setInspections([...inspections, inspection]);
      setCreateDialogOpen(false);
      showToast("success", "Inspection scheduled successfully");
    }
  };

  const getResultBadge = (result: string) => {
    const styles: Record<string, string> = {
      pass: "bg-green-100 text-green-800",
      fail: "bg-red-100 text-red-800",
      conditional: "bg-yellow-100 text-yellow-800",
      pending: "bg-gray-100 text-gray-800",
    };
    return styles[result] || "bg-gray-100 text-gray-800";
  };

  const getStatusBadge = (status: string) => {
    const styles: Record<string, string> = {
      scheduled: "bg-blue-100 text-blue-800",
      in_progress: "bg-yellow-100 text-yellow-800",
      completed: "bg-green-100 text-green-800",
      cancelled: "bg-red-100 text-red-800",
    };
    return styles[status] || "bg-gray-100 text-gray-800";
  };

  const getResultIcon = (result: string) => {
    switch (result) {
      case "pass":
        return <CheckCircle className="h-4 w-4 text-green-600" />;
      case "fail":
        return <XCircle className="h-4 w-4 text-red-600" />;
      case "conditional":
        return <AlertTriangle className="h-4 w-4 text-yellow-600" />;
      default:
        return <Clock className="h-4 w-4 text-gray-400" />;
    }
  };

  const filteredInspections = inspections.filter((inspection) => {
    const matchesSearch =
      inspection.number.toLowerCase().includes(searchTerm.toLowerCase()) ||
      inspection.product.toLowerCase().includes(searchTerm.toLowerCase()) ||
      inspection.lotNumber.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesType = typeFilter === "all" || inspection.type === typeFilter;
    const matchesStatus = statusFilter === "all" || inspection.status === statusFilter;
    const matchesResult = resultFilter === "all" || inspection.result === resultFilter;
    return matchesSearch && matchesType && matchesStatus && matchesResult;
  });

  // Calculate statistics
  const stats = {
    total: inspections.length,
    scheduled: inspections.filter((i) => i.status === "scheduled").length,
    inProgress: inspections.filter((i) => i.status === "in_progress").length,
    completed: inspections.filter((i) => i.status === "completed").length,
    passRate:
      inspections.filter((i) => i.status === "completed").length > 0
        ? Math.round(
            (inspections.filter((i) => i.result === "pass").length /
              inspections.filter((i) => i.status === "completed").length) *
              100
          )
        : 0,
  };

  return (
    <div className="flex flex-col gap-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Quality Inspections</h1>
          <p className="text-muted-foreground">
            Manage inspection schedules, checklists, and pass/fail results
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
                Schedule Inspection
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl">
              <DialogHeader>
                <DialogTitle>Schedule Quality Inspection</DialogTitle>
                <DialogDescription>
                  Create a new quality inspection with checklist
                </DialogDescription>
              </DialogHeader>
              <div className="grid gap-4 py-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>Inspection Type *</Label>
                    <Select
                      value={newInspection.type}
                      onValueChange={(value) =>
                        setNewInspection({ ...newInspection, type: value as any })
                      }
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select type" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="incoming">Incoming</SelectItem>
                        <SelectItem value="in_process">In-Process</SelectItem>
                        <SelectItem value="final">Final</SelectItem>
                        <SelectItem value="supplier">Supplier</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label>Scheduled Date *</Label>
                    <Input
                      type="date"
                      value={newInspection.scheduledDate}
                      onChange={(e) =>
                        setNewInspection({ ...newInspection, scheduledDate: e.target.value })
                      }
                    />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>Product *</Label>
                    <Select
                      value={newInspection.product}
                      onValueChange={(value) =>
                        setNewInspection({ ...newInspection, product: value })
                      }
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select product" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="Raw Material A - Steel Plates">
                          Raw Material A - Steel Plates
                        </SelectItem>
                        <SelectItem value="Assembly B - Motor Housing">
                          Assembly B - Motor Housing
                        </SelectItem>
                        <SelectItem value="Finished Good C - Industrial Pump">
                          Finished Good C - Industrial Pump
                        </SelectItem>
                        <SelectItem value="Component D - Bearings">
                          Component D - Bearings
                        </SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label>Lot Number</Label>
                    <Input
                      placeholder="Enter lot number"
                      value={newInspection.lotNumber}
                      onChange={(e) =>
                        setNewInspection({ ...newInspection, lotNumber: e.target.value })
                      }
                    />
                  </div>
                </div>
                <div className="space-y-2">
                  <Label>Inspector</Label>
                  <Select
                    value={newInspection.inspector}
                    onValueChange={(value) =>
                      setNewInspection({ ...newInspection, inspector: value })
                    }
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Assign inspector" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="Raj Kumar">Raj Kumar</SelectItem>
                      <SelectItem value="Priya Singh">Priya Singh</SelectItem>
                      <SelectItem value="Amit Sharma">Amit Sharma</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label>Notes</Label>
                  <Textarea
                    placeholder="Additional notes..."
                    value={newInspection.notes}
                    onChange={(e) =>
                      setNewInspection({ ...newInspection, notes: e.target.value })
                    }
                  />
                </div>
                {newInspection.type && (
                  <div className="space-y-2">
                    <Label>Checklist Preview</Label>
                    <div className="border rounded-md p-3 bg-muted/50">
                      <ul className="space-y-1 text-sm">
                        {checklistTemplates
                          .find((t) => t.type === newInspection.type)
                          ?.items.map((item, index) => (
                            <li key={index} className="flex items-center gap-2">
                              <ListChecks className="h-4 w-4 text-muted-foreground" />
                              {item}
                            </li>
                          ))}
                      </ul>
                    </div>
                  </div>
                )}
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={() => setCreateDialogOpen(false)}>
                  Cancel
                </Button>
                <Button onClick={handleCreateInspection}>Schedule Inspection</Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* Statistics Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-5">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Total Inspections</CardTitle>
            <ClipboardCheck className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.total}</div>
            <p className="text-xs text-muted-foreground">All time</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Scheduled</CardTitle>
            <Calendar className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">{stats.scheduled}</div>
            <p className="text-xs text-muted-foreground">Awaiting execution</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">In Progress</CardTitle>
            <Clock className="h-4 w-4 text-yellow-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-600">{stats.inProgress}</div>
            <p className="text-xs text-muted-foreground">Currently running</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Completed</CardTitle>
            <CheckCircle className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{stats.completed}</div>
            <p className="text-xs text-muted-foreground">This month</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Pass Rate</CardTitle>
            <BarChart3 className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{stats.passRate}%</div>
            <p className="text-xs text-muted-foreground">Overall</p>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-4 flex-wrap">
        <div className="relative flex-1 min-w-[200px]">
          <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search inspections..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-8"
          />
        </div>
        <Select value={typeFilter} onValueChange={setTypeFilter}>
          <SelectTrigger className="w-[150px]">
            <Filter className="mr-2 h-4 w-4" />
            <SelectValue placeholder="Type" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Types</SelectItem>
            <SelectItem value="incoming">Incoming</SelectItem>
            <SelectItem value="in_process">In-Process</SelectItem>
            <SelectItem value="final">Final</SelectItem>
            <SelectItem value="supplier">Supplier</SelectItem>
          </SelectContent>
        </Select>
        <Select value={statusFilter} onValueChange={setStatusFilter}>
          <SelectTrigger className="w-[150px]">
            <SelectValue placeholder="Status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Status</SelectItem>
            <SelectItem value="scheduled">Scheduled</SelectItem>
            <SelectItem value="in_progress">In Progress</SelectItem>
            <SelectItem value="completed">Completed</SelectItem>
            <SelectItem value="cancelled">Cancelled</SelectItem>
          </SelectContent>
        </Select>
        <Select value={resultFilter} onValueChange={setResultFilter}>
          <SelectTrigger className="w-[150px]">
            <SelectValue placeholder="Result" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Results</SelectItem>
            <SelectItem value="pass">Pass</SelectItem>
            <SelectItem value="fail">Fail</SelectItem>
            <SelectItem value="conditional">Conditional</SelectItem>
            <SelectItem value="pending">Pending</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Inspections Table */}
      <Card>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Inspection #</TableHead>
              <TableHead>Type</TableHead>
              <TableHead>Product</TableHead>
              <TableHead>Lot #</TableHead>
              <TableHead>Result</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Scheduled Date</TableHead>
              <TableHead>Inspector</TableHead>
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
            ) : filteredInspections.length === 0 ? (
              <TableRow>
                <TableCell colSpan={9} className="text-center py-8 text-muted-foreground">
                  No inspections found
                </TableCell>
              </TableRow>
            ) : (
              filteredInspections.map((inspection) => (
                <TableRow key={inspection.id}>
                  <TableCell className="font-medium">{inspection.number}</TableCell>
                  <TableCell className="capitalize">
                    {inspection.type.replace("_", " ")}
                  </TableCell>
                  <TableCell className="max-w-[200px] truncate">
                    {inspection.product}
                  </TableCell>
                  <TableCell>{inspection.lotNumber}</TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      {getResultIcon(inspection.result)}
                      <Badge className={getResultBadge(inspection.result)}>
                        {inspection.result}
                      </Badge>
                    </div>
                  </TableCell>
                  <TableCell>
                    <Badge className={getStatusBadge(inspection.status)}>
                      {inspection.status.replace("_", " ")}
                    </Badge>
                  </TableCell>
                  <TableCell>{inspection.scheduledDate}</TableCell>
                  <TableCell>{inspection.inspector}</TableCell>
                  <TableCell>
                    <div className="flex gap-1">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => handleViewInspection(inspection)}
                      >
                        <Eye className="h-4 w-4" />
                      </Button>
                      {(inspection.status === "scheduled" ||
                        inspection.status === "in_progress") && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleStartInspection(inspection)}
                        >
                          <Play className="h-4 w-4 text-green-500" />
                        </Button>
                      )}
                      {inspection.status === "completed" && (
                        <Button
                          variant="ghost"
                          size="sm"
                          className="text-red-600 hover:text-red-700 hover:bg-red-50"
                          onClick={() => handleDeleteClick(inspection)}
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

      {/* View Inspection Dialog */}
      <Dialog open={viewDialogOpen} onOpenChange={setViewDialogOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Inspection Details - {selectedInspection?.number}</DialogTitle>
            <DialogDescription>
              View inspection information and checklist results
            </DialogDescription>
          </DialogHeader>
          {selectedInspection && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label className="text-muted-foreground">Type</Label>
                  <p className="capitalize">{selectedInspection.type.replace("_", " ")}</p>
                </div>
                <div>
                  <Label className="text-muted-foreground">Status</Label>
                  <Badge className={getStatusBadge(selectedInspection.status)}>
                    {selectedInspection.status.replace("_", " ")}
                  </Badge>
                </div>
                <div>
                  <Label className="text-muted-foreground">Product</Label>
                  <p>{selectedInspection.product}</p>
                </div>
                <div>
                  <Label className="text-muted-foreground">Lot Number</Label>
                  <p>{selectedInspection.lotNumber}</p>
                </div>
                <div>
                  <Label className="text-muted-foreground">Scheduled Date</Label>
                  <p>{selectedInspection.scheduledDate}</p>
                </div>
                <div>
                  <Label className="text-muted-foreground">Completed Date</Label>
                  <p>{selectedInspection.completedDate || "-"}</p>
                </div>
                <div>
                  <Label className="text-muted-foreground">Inspector</Label>
                  <p>{selectedInspection.inspector}</p>
                </div>
                <div>
                  <Label className="text-muted-foreground">Result</Label>
                  <div className="flex items-center gap-2">
                    {getResultIcon(selectedInspection.result)}
                    <Badge className={getResultBadge(selectedInspection.result)}>
                      {selectedInspection.result}
                    </Badge>
                  </div>
                </div>
              </div>

              <div>
                <Label className="text-muted-foreground">Checklist</Label>
                <div className="border rounded-md mt-2">
                  <Table>
                    <TableHeader>
                      <TableRow>
                        <TableHead>Item</TableHead>
                        <TableHead className="w-[100px]">Result</TableHead>
                        <TableHead>Notes</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {selectedInspection.checklist.map((item) => (
                        <TableRow key={item.id}>
                          <TableCell>{item.description}</TableCell>
                          <TableCell>
                            {item.passed === true && (
                              <CheckCircle className="h-5 w-5 text-green-600" />
                            )}
                            {item.passed === false && (
                              <XCircle className="h-5 w-5 text-red-600" />
                            )}
                            {item.passed === null && (
                              <Clock className="h-5 w-5 text-gray-400" />
                            )}
                          </TableCell>
                          <TableCell className="text-muted-foreground">
                            {item.notes || "-"}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </div>
              </div>

              {selectedInspection.notes && (
                <div>
                  <Label className="text-muted-foreground">Notes</Label>
                  <p className="mt-1">{selectedInspection.notes}</p>
                </div>
              )}
            </div>
          )}
          <DialogFooter>
            <Button variant="outline" onClick={() => setViewDialogOpen(false)}>
              Close
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Checklist Execution Dialog */}
      <Dialog open={checklistDialogOpen} onOpenChange={setChecklistDialogOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Execute Inspection - {selectedInspection?.number}</DialogTitle>
            <DialogDescription>
              Complete the inspection checklist for {selectedInspection?.product}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 max-h-[60vh] overflow-y-auto">
            {checklistState.map((item) => (
              <div key={item.id} className="border rounded-md p-4 space-y-3">
                <div className="flex items-center justify-between">
                  <span className="font-medium">{item.description}</span>
                  <div className="flex gap-2">
                    <Button
                      variant={item.passed === true ? "default" : "outline"}
                      size="sm"
                      className={item.passed === true ? "bg-green-600 hover:bg-green-700" : ""}
                      onClick={() => handleChecklistChange(item.id, true)}
                    >
                      <CheckCircle className="h-4 w-4 mr-1" />
                      Pass
                    </Button>
                    <Button
                      variant={item.passed === false ? "default" : "outline"}
                      size="sm"
                      className={item.passed === false ? "bg-red-600 hover:bg-red-700" : ""}
                      onClick={() => handleChecklistChange(item.id, false)}
                    >
                      <XCircle className="h-4 w-4 mr-1" />
                      Fail
                    </Button>
                  </div>
                </div>
                <Input
                  placeholder="Add notes (optional)..."
                  value={item.notes}
                  onChange={(e) => handleChecklistNotes(item.id, e.target.value)}
                />
              </div>
            ))}
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setChecklistDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleCompleteInspection}>Complete Inspection</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-red-500" />
              Delete Inspection
            </AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete{" "}
              <strong>{selectedInspection?.number}</strong>? This action cannot be undone.
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
