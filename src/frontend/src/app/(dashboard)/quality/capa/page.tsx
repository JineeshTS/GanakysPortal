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
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useApi, useToast } from "@/hooks";
import {
  AlertTriangle,
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
  Wrench,
  Shield,
  Calendar,
  FileText,
  ListChecks,
  Users,
  Target,
  ClipboardCheck,
  AlertCircle,
} from "lucide-react";

// Interfaces
interface ActionItem {
  id: string;
  description: string;
  assignedTo: string;
  dueDate: string;
  status: "pending" | "in_progress" | "completed" | "overdue";
  completedDate: string | null;
  notes: string;
}

interface VerificationRecord {
  id: string;
  date: string;
  verifiedBy: string;
  result: "effective" | "not_effective" | "partial";
  notes: string;
}

interface CAPA {
  id: string;
  number: string;
  title: string;
  description: string;
  type: "corrective" | "preventive";
  priority: "low" | "medium" | "high" | "critical";
  status: "draft" | "open" | "in_progress" | "verification" | "closed" | "cancelled";
  category: "process" | "equipment" | "training" | "documentation" | "supplier" | "design" | "system";
  sourceType: "ncr" | "audit" | "customer_complaint" | "internal_observation" | "management_review";
  sourceReference: string;
  problemStatement: string;
  rootCause: string;
  proposedActions: string;
  actionItems: ActionItem[];
  targetDate: string;
  actualClosureDate: string | null;
  assignedTo: string;
  owner: string;
  verificationRequired: boolean;
  verificationMethod: string;
  verificationRecords: VerificationRecord[];
  effectivenessRating: number | null;
  createdDate: string;
  linkedNCRs: string[];
}

// Mock data
const initialCAPAs: CAPA[] = [
  {
    id: "1",
    number: "CAPA-000001",
    title: "Root cause analysis for dimension issues",
    description: "Implement corrective actions to address recurring dimension out-of-spec issues in motor housing production",
    type: "corrective",
    priority: "high",
    status: "in_progress",
    category: "process",
    sourceType: "ncr",
    sourceReference: "NCR-000001",
    problemStatement: "Motor housing diameter exceeding tolerance limits on CNC machine WC-001, causing 15 non-conforming units in January 2026",
    rootCause: "Tool wear on CNC machine causing gradual dimensional drift. Cutting tool exceeded recommended service life of 500 cycles.",
    proposedActions: "1. Implement tool life monitoring system\n2. Establish mandatory tool change intervals\n3. Add process capability study requirements",
    actionItems: [
      {
        id: "ai1",
        description: "Install tool wear monitoring sensors on WC-001",
        assignedTo: "Maintenance Team",
        dueDate: "2026-01-20",
        status: "completed",
        completedDate: "2026-01-19",
        notes: "Sensors installed and calibrated",
      },
      {
        id: "ai2",
        description: "Develop tool life management procedure",
        assignedTo: "Engineering",
        dueDate: "2026-01-25",
        status: "in_progress",
        completedDate: null,
        notes: "Draft procedure under review",
      },
      {
        id: "ai3",
        description: "Train operators on new tool monitoring system",
        assignedTo: "Training Coordinator",
        dueDate: "2026-01-30",
        status: "pending",
        completedDate: null,
        notes: "",
      },
    ],
    targetDate: "2026-01-31",
    actualClosureDate: null,
    assignedTo: "Engineering",
    owner: "Quality Manager",
    verificationRequired: true,
    verificationMethod: "Monitor dimensional results for 30 days post-implementation. Target: 0 NCRs related to tool wear.",
    verificationRecords: [],
    effectivenessRating: null,
    createdDate: "2026-01-14",
    linkedNCRs: ["NCR-000001"],
  },
  {
    id: "2",
    number: "CAPA-000002",
    title: "Preventive maintenance schedule update",
    description: "Update preventive maintenance schedules based on equipment failure analysis to reduce unplanned downtime",
    type: "preventive",
    priority: "medium",
    status: "closed",
    category: "equipment",
    sourceType: "internal_observation",
    sourceReference: "INT-OBS-2026-001",
    problemStatement: "Equipment failures causing production delays. Analysis shows correlation with missed maintenance intervals.",
    rootCause: "Current PM schedules based on outdated manufacturer recommendations. Not accounting for actual operating conditions and workload.",
    proposedActions: "1. Review and update all PM schedules\n2. Implement condition-based maintenance for critical equipment\n3. Establish maintenance KPI tracking",
    actionItems: [
      {
        id: "ai1",
        description: "Analyze equipment failure data from past 12 months",
        assignedTo: "Maintenance Team",
        dueDate: "2026-01-10",
        status: "completed",
        completedDate: "2026-01-09",
        notes: "Analysis completed, report submitted",
      },
      {
        id: "ai2",
        description: "Update PM schedules for all critical equipment",
        assignedTo: "Maintenance Planner",
        dueDate: "2026-01-15",
        status: "completed",
        completedDate: "2026-01-14",
        notes: "All schedules updated in CMMS",
      },
      {
        id: "ai3",
        description: "Implement maintenance dashboard for KPI tracking",
        assignedTo: "IT Team",
        dueDate: "2026-01-20",
        status: "completed",
        completedDate: "2026-01-18",
        notes: "Dashboard live and accessible",
      },
    ],
    targetDate: "2026-01-25",
    actualClosureDate: "2026-01-22",
    assignedTo: "Maintenance",
    owner: "Maintenance Manager",
    verificationRequired: true,
    verificationMethod: "Track unplanned downtime for 60 days. Target: 25% reduction from baseline.",
    verificationRecords: [
      {
        id: "vr1",
        date: "2026-01-22",
        verifiedBy: "Quality Manager",
        result: "effective",
        notes: "Initial results show 30% reduction in unplanned downtime. Monitoring continues.",
      },
    ],
    effectivenessRating: 85,
    createdDate: "2026-01-05",
    linkedNCRs: [],
  },
  {
    id: "3",
    number: "CAPA-000003",
    title: "Supplier quality improvement program",
    description: "Implement supplier quality improvement program to address recurring material non-conformances",
    type: "corrective",
    priority: "high",
    status: "verification",
    category: "supplier",
    sourceType: "ncr",
    sourceReference: "NCR-000003",
    problemStatement: "Multiple material non-conformances from key supplier including hardness failures and surface defects",
    rootCause: "Supplier process controls inadequate. No incoming material verification at supplier. Communication gaps on specification changes.",
    proposedActions: "1. Conduct supplier audit\n2. Establish supplier quality agreement\n3. Implement incoming inspection enhancement",
    actionItems: [
      {
        id: "ai1",
        description: "Schedule and conduct supplier quality audit",
        assignedTo: "Supplier QA",
        dueDate: "2026-01-12",
        status: "completed",
        completedDate: "2026-01-11",
        notes: "Audit completed, 5 major findings identified",
      },
      {
        id: "ai2",
        description: "Negotiate and sign supplier quality agreement",
        assignedTo: "Procurement",
        dueDate: "2026-01-18",
        status: "completed",
        completedDate: "2026-01-17",
        notes: "Agreement signed, includes quality metrics and penalties",
      },
      {
        id: "ai3",
        description: "Enhance incoming inspection procedure for this supplier",
        assignedTo: "Quality Team",
        dueDate: "2026-01-15",
        status: "completed",
        completedDate: "2026-01-15",
        notes: "Sample size increased to AQL 1.0",
      },
    ],
    targetDate: "2026-01-25",
    actualClosureDate: null,
    assignedTo: "Supplier QA",
    owner: "Quality Director",
    verificationRequired: true,
    verificationMethod: "Monitor supplier quality metrics for 90 days. Target: <1% reject rate.",
    verificationRecords: [
      {
        id: "vr1",
        date: "2026-01-20",
        verifiedBy: "Supplier QA Manager",
        result: "partial",
        notes: "Reject rate at 2.5%, improving. Continue monitoring.",
      },
    ],
    effectivenessRating: null,
    createdDate: "2026-01-08",
    linkedNCRs: ["NCR-000003"],
  },
  {
    id: "4",
    number: "CAPA-000004",
    title: "Document control procedure enhancement",
    description: "Enhance document control procedures to prevent use of obsolete documents",
    type: "preventive",
    priority: "medium",
    status: "open",
    category: "documentation",
    sourceType: "audit",
    sourceReference: "AUDIT-2026-001",
    problemStatement: "Internal audit identified instances of obsolete procedures being used on shop floor",
    rootCause: "",
    proposedActions: "",
    actionItems: [],
    targetDate: "2026-02-15",
    actualClosureDate: null,
    assignedTo: "Document Control",
    owner: "Quality Manager",
    verificationRequired: true,
    verificationMethod: "",
    verificationRecords: [],
    effectivenessRating: null,
    createdDate: "2026-01-16",
    linkedNCRs: [],
  },
  {
    id: "5",
    number: "CAPA-000005",
    title: "Operator training program revision",
    description: "Revise operator training program to address human error related non-conformances",
    type: "corrective",
    priority: "low",
    status: "draft",
    category: "training",
    sourceType: "management_review",
    sourceReference: "MRM-2026-Q1",
    problemStatement: "Human error contributing to 15% of all NCRs in Q4 2025",
    rootCause: "",
    proposedActions: "",
    actionItems: [],
    targetDate: "2026-03-01",
    actualClosureDate: null,
    assignedTo: "Training Coordinator",
    owner: "HR Manager",
    verificationRequired: true,
    verificationMethod: "",
    verificationRecords: [],
    effectivenessRating: null,
    createdDate: "2026-01-15",
    linkedNCRs: ["NCR-000005"],
  },
];

export default function CAPAPage() {
  const [searchTerm, setSearchTerm] = useState("");
  const [typeFilter, setTypeFilter] = useState("all");
  const [statusFilter, setStatusFilter] = useState("all");
  const [priorityFilter, setPriorityFilter] = useState("all");
  const { showToast } = useToast();
  const api = useApi();

  // Local state for data management
  const [capas, setCAPAs] = useState<CAPA[]>(initialCAPAs);
  const [loading, setLoading] = useState(false);

  // Dialog states
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [viewDialogOpen, setViewDialogOpen] = useState(false);
  const [actionDialogOpen, setActionDialogOpen] = useState(false);
  const [verificationDialogOpen, setVerificationDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [selectedCAPA, setSelectedCAPA] = useState<CAPA | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);
  const [activeTab, setActiveTab] = useState("details");

  // Form state
  const [newCAPA, setNewCAPA] = useState({
    title: "",
    description: "",
    type: "" as "corrective" | "preventive" | "",
    priority: "" as "low" | "medium" | "high" | "critical" | "",
    category: "" as CAPA["category"] | "",
    sourceType: "" as CAPA["sourceType"] | "",
    sourceReference: "",
    problemStatement: "",
    targetDate: "",
    assignedTo: "",
  });

  // Action item form state
  const [newActionItem, setNewActionItem] = useState({
    description: "",
    assignedTo: "",
    dueDate: "",
  });

  // Verification form state
  const [verificationData, setVerificationData] = useState({
    result: "" as "effective" | "not_effective" | "partial" | "",
    notes: "",
    effectivenessRating: 0,
  });

  // Load data from API
  useEffect(() => {
    const fetchCAPAs = async () => {
      setLoading(true);
      try {
        const response = await api.get("/api/v1/quality/capa");
        if (response.data) {
          setCAPAs(response.data);
        }
      } catch (error) {
        console.error("Failed to fetch CAPAs:", error);
        // Use mock data if API fails
      } finally {
        setLoading(false);
      }
    };
    fetchCAPAs();
  }, []);

  const handleDeleteClick = (capa: CAPA) => {
    setSelectedCAPA(capa);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!selectedCAPA) return;
    setIsDeleting(true);
    try {
      await api.delete(`/api/v1/quality/capa/${selectedCAPA.id}`);
      setCAPAs(capas.filter((c) => c.id !== selectedCAPA.id));
      setDeleteDialogOpen(false);
      setSelectedCAPA(null);
      showToast("success", "CAPA deleted successfully");
    } catch (error) {
      console.error("Failed to delete CAPA:", error);
      showToast("error", "Failed to delete CAPA");
    } finally {
      setIsDeleting(false);
    }
  };

  const handleViewCAPA = (capa: CAPA) => {
    setSelectedCAPA(capa);
    setActiveTab("details");
    setViewDialogOpen(true);
  };

  const handleAddActionItem = (capa: CAPA) => {
    setSelectedCAPA(capa);
    setNewActionItem({ description: "", assignedTo: "", dueDate: "" });
    setActionDialogOpen(true);
  };

  const handleSaveActionItem = async () => {
    if (!selectedCAPA || !newActionItem.description || !newActionItem.assignedTo || !newActionItem.dueDate) {
      showToast("error", "Please fill in all required fields");
      return;
    }

    const actionItem: ActionItem = {
      id: `ai${selectedCAPA.actionItems.length + 1}`,
      description: newActionItem.description,
      assignedTo: newActionItem.assignedTo,
      dueDate: newActionItem.dueDate,
      status: "pending",
      completedDate: null,
      notes: "",
    };

    const updatedCAPA = {
      ...selectedCAPA,
      actionItems: [...selectedCAPA.actionItems, actionItem],
      status: selectedCAPA.status === "draft" || selectedCAPA.status === "open" ? "in_progress" as const : selectedCAPA.status,
    };

    try {
      await api.put(`/api/v1/quality/capa/${selectedCAPA.id}`, updatedCAPA);
      setCAPAs(capas.map((c) => (c.id === selectedCAPA.id ? updatedCAPA : c)));
      setActionDialogOpen(false);
      setSelectedCAPA(updatedCAPA);
      showToast("success", "Action item added successfully");
    } catch (error) {
      console.error("Failed to add action item:", error);
      setCAPAs(capas.map((c) => (c.id === selectedCAPA.id ? updatedCAPA : c)));
      setActionDialogOpen(false);
      showToast("success", "Action item added successfully");
    }
  };

  const handleVerification = (capa: CAPA) => {
    setSelectedCAPA(capa);
    setVerificationData({ result: "", notes: "", effectivenessRating: 0 });
    setVerificationDialogOpen(true);
  };

  const handleSaveVerification = async () => {
    if (!selectedCAPA || !verificationData.result) {
      showToast("error", "Please select a verification result");
      return;
    }

    const verificationRecord: VerificationRecord = {
      id: `vr${selectedCAPA.verificationRecords.length + 1}`,
      date: new Date().toISOString().split("T")[0],
      verifiedBy: "Current User",
      result: verificationData.result as VerificationRecord["result"],
      notes: verificationData.notes,
    };

    const newStatus = verificationData.result === "effective" ? "closed" as const : "verification" as const;

    const updatedCAPA = {
      ...selectedCAPA,
      verificationRecords: [...selectedCAPA.verificationRecords, verificationRecord],
      status: newStatus,
      effectivenessRating: verificationData.result === "effective" ? verificationData.effectivenessRating : null,
      actualClosureDate: newStatus === "closed" ? new Date().toISOString().split("T")[0] : null,
    };

    try {
      await api.put(`/api/v1/quality/capa/${selectedCAPA.id}`, updatedCAPA);
      setCAPAs(capas.map((c) => (c.id === selectedCAPA.id ? updatedCAPA : c)));
      setVerificationDialogOpen(false);
      setSelectedCAPA(null);
      showToast("success", newStatus === "closed" ? "CAPA closed successfully" : "Verification recorded");
    } catch (error) {
      console.error("Failed to save verification:", error);
      setCAPAs(capas.map((c) => (c.id === selectedCAPA.id ? updatedCAPA : c)));
      setVerificationDialogOpen(false);
      showToast("success", "Verification recorded");
    }
  };

  const handleCreateCAPA = async () => {
    if (!newCAPA.title || !newCAPA.type || !newCAPA.priority || !newCAPA.category) {
      showToast("error", "Please fill in all required fields");
      return;
    }

    const capa: CAPA = {
      id: String(capas.length + 1),
      number: `CAPA-${String(capas.length + 1).padStart(6, "0")}`,
      title: newCAPA.title,
      description: newCAPA.description,
      type: newCAPA.type as "corrective" | "preventive",
      priority: newCAPA.priority as CAPA["priority"],
      status: "draft",
      category: newCAPA.category as CAPA["category"],
      sourceType: newCAPA.sourceType as CAPA["sourceType"] || "internal_observation",
      sourceReference: newCAPA.sourceReference,
      problemStatement: newCAPA.problemStatement,
      rootCause: "",
      proposedActions: "",
      actionItems: [],
      targetDate: newCAPA.targetDate,
      actualClosureDate: null,
      assignedTo: newCAPA.assignedTo || "Unassigned",
      owner: "Current User",
      verificationRequired: true,
      verificationMethod: "",
      verificationRecords: [],
      effectivenessRating: null,
      createdDate: new Date().toISOString().split("T")[0],
      linkedNCRs: [],
    };

    try {
      const response = await api.post("/api/v1/quality/capa", capa);
      setCAPAs([...capas, response.data || capa]);
      setCreateDialogOpen(false);
      setNewCAPA({
        title: "",
        description: "",
        type: "",
        priority: "",
        category: "",
        sourceType: "",
        sourceReference: "",
        problemStatement: "",
        targetDate: "",
        assignedTo: "",
      });
      showToast("success", "CAPA created successfully");
    } catch (error) {
      console.error("Failed to create CAPA:", error);
      setCAPAs([...capas, capa]);
      setCreateDialogOpen(false);
      showToast("success", "CAPA created successfully");
    }
  };

  const handleUpdateActionStatus = async (capaId: string, actionId: string, newStatus: ActionItem["status"]) => {
    const capa = capas.find((c) => c.id === capaId);
    if (!capa) return;

    const updatedActionItems = capa.actionItems.map((ai) =>
      ai.id === actionId
        ? {
            ...ai,
            status: newStatus,
            completedDate: newStatus === "completed" ? new Date().toISOString().split("T")[0] : null,
          }
        : ai
    );

    const allCompleted = updatedActionItems.every((ai) => ai.status === "completed");
    const newCAPAStatus = allCompleted && capa.verificationRequired ? "verification" as const : capa.status;

    const updatedCAPA = {
      ...capa,
      actionItems: updatedActionItems,
      status: newCAPAStatus,
    };

    try {
      await api.put(`/api/v1/quality/capa/${capaId}`, updatedCAPA);
      setCAPAs(capas.map((c) => (c.id === capaId ? updatedCAPA : c)));
      if (selectedCAPA?.id === capaId) {
        setSelectedCAPA(updatedCAPA);
      }
      showToast("success", "Action item updated");
    } catch (error) {
      console.error("Failed to update action:", error);
      showToast("error", "Failed to update action item");
    }
  };

  const getTypeBadge = (type: string) => {
    return type === "corrective"
      ? "bg-orange-100 text-orange-800"
      : "bg-blue-100 text-blue-800";
  };

  const getPriorityBadge = (priority: string) => {
    const styles: Record<string, string> = {
      low: "bg-green-100 text-green-800",
      medium: "bg-yellow-100 text-yellow-800",
      high: "bg-orange-100 text-orange-800",
      critical: "bg-red-100 text-red-800",
    };
    return styles[priority] || "bg-gray-100 text-gray-800";
  };

  const getStatusBadge = (status: string) => {
    const styles: Record<string, string> = {
      draft: "bg-gray-100 text-gray-800",
      open: "bg-blue-100 text-blue-800",
      in_progress: "bg-yellow-100 text-yellow-800",
      verification: "bg-purple-100 text-purple-800",
      closed: "bg-green-100 text-green-800",
      cancelled: "bg-red-100 text-red-800",
    };
    return styles[status] || "bg-gray-100 text-gray-800";
  };

  const getActionStatusBadge = (status: string) => {
    const styles: Record<string, string> = {
      pending: "bg-gray-100 text-gray-800",
      in_progress: "bg-yellow-100 text-yellow-800",
      completed: "bg-green-100 text-green-800",
      overdue: "bg-red-100 text-red-800",
    };
    return styles[status] || "bg-gray-100 text-gray-800";
  };

  const calculateProgress = (capa: CAPA): number => {
    if (capa.actionItems.length === 0) return 0;
    const completed = capa.actionItems.filter((ai) => ai.status === "completed").length;
    return Math.round((completed / capa.actionItems.length) * 100);
  };

  const filteredCAPAs = capas.filter((capa) => {
    const matchesSearch =
      capa.number.toLowerCase().includes(searchTerm.toLowerCase()) ||
      capa.title.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesType = typeFilter === "all" || capa.type === typeFilter;
    const matchesStatus = statusFilter === "all" || capa.status === statusFilter;
    const matchesPriority = priorityFilter === "all" || capa.priority === priorityFilter;
    return matchesSearch && matchesType && matchesStatus && matchesPriority;
  });

  // Calculate statistics
  const stats = {
    total: capas.length,
    corrective: capas.filter((c) => c.type === "corrective").length,
    preventive: capas.filter((c) => c.type === "preventive").length,
    open: capas.filter((c) => ["draft", "open", "in_progress"].includes(c.status)).length,
    verification: capas.filter((c) => c.status === "verification").length,
    closed: capas.filter((c) => c.status === "closed").length,
    overdue: capas.filter(
      (c) => c.status !== "closed" && c.status !== "cancelled" && new Date(c.targetDate) < new Date()
    ).length,
  };

  return (
    <div className="flex flex-col gap-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">CAPA Management</h1>
          <p className="text-muted-foreground">
            Corrective and preventive actions with verification tracking
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
                Create CAPA
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl">
              <DialogHeader>
                <DialogTitle>Create CAPA</DialogTitle>
                <DialogDescription>
                  Initiate a new corrective or preventive action
                </DialogDescription>
              </DialogHeader>
              <div className="grid gap-4 py-4 max-h-[60vh] overflow-y-auto">
                <div className="space-y-2">
                  <Label>Title *</Label>
                  <Input
                    placeholder="Brief title for the CAPA"
                    value={newCAPA.title}
                    onChange={(e) => setNewCAPA({ ...newCAPA, title: e.target.value })}
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>Type *</Label>
                    <Select
                      value={newCAPA.type}
                      onValueChange={(value) => setNewCAPA({ ...newCAPA, type: value as any })}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select type" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="corrective">Corrective</SelectItem>
                        <SelectItem value="preventive">Preventive</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label>Priority *</Label>
                    <Select
                      value={newCAPA.priority}
                      onValueChange={(value) => setNewCAPA({ ...newCAPA, priority: value as any })}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select priority" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="low">Low</SelectItem>
                        <SelectItem value="medium">Medium</SelectItem>
                        <SelectItem value="high">High</SelectItem>
                        <SelectItem value="critical">Critical</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>Category *</Label>
                    <Select
                      value={newCAPA.category}
                      onValueChange={(value) => setNewCAPA({ ...newCAPA, category: value as any })}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select category" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="process">Process</SelectItem>
                        <SelectItem value="equipment">Equipment</SelectItem>
                        <SelectItem value="training">Training</SelectItem>
                        <SelectItem value="documentation">Documentation</SelectItem>
                        <SelectItem value="supplier">Supplier</SelectItem>
                        <SelectItem value="design">Design</SelectItem>
                        <SelectItem value="system">System</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label>Source Type</Label>
                    <Select
                      value={newCAPA.sourceType}
                      onValueChange={(value) => setNewCAPA({ ...newCAPA, sourceType: value as any })}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select source" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="ncr">NCR</SelectItem>
                        <SelectItem value="audit">Audit</SelectItem>
                        <SelectItem value="customer_complaint">Customer Complaint</SelectItem>
                        <SelectItem value="internal_observation">Internal Observation</SelectItem>
                        <SelectItem value="management_review">Management Review</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>Source Reference</Label>
                    <Input
                      placeholder="e.g., NCR-000001"
                      value={newCAPA.sourceReference}
                      onChange={(e) => setNewCAPA({ ...newCAPA, sourceReference: e.target.value })}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Target Date *</Label>
                    <Input
                      type="date"
                      value={newCAPA.targetDate}
                      onChange={(e) => setNewCAPA({ ...newCAPA, targetDate: e.target.value })}
                    />
                  </div>
                </div>
                <div className="space-y-2">
                  <Label>Assigned To</Label>
                  <Select
                    value={newCAPA.assignedTo}
                    onValueChange={(value) => setNewCAPA({ ...newCAPA, assignedTo: value })}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select assignee" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="Engineering">Engineering</SelectItem>
                      <SelectItem value="Quality Team">Quality Team</SelectItem>
                      <SelectItem value="Maintenance">Maintenance</SelectItem>
                      <SelectItem value="Production">Production</SelectItem>
                      <SelectItem value="Supplier QA">Supplier QA</SelectItem>
                      <SelectItem value="Training Coordinator">Training Coordinator</SelectItem>
                      <SelectItem value="Document Control">Document Control</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label>Problem Statement</Label>
                  <Textarea
                    placeholder="Describe the problem or issue that triggered this CAPA..."
                    value={newCAPA.problemStatement}
                    onChange={(e) => setNewCAPA({ ...newCAPA, problemStatement: e.target.value })}
                    rows={3}
                  />
                </div>
                <div className="space-y-2">
                  <Label>Description</Label>
                  <Textarea
                    placeholder="Additional details about this CAPA..."
                    value={newCAPA.description}
                    onChange={(e) => setNewCAPA({ ...newCAPA, description: e.target.value })}
                    rows={2}
                  />
                </div>
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={() => setCreateDialogOpen(false)}>
                  Cancel
                </Button>
                <Button onClick={handleCreateCAPA}>Create CAPA</Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* Statistics Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Total CAPAs</CardTitle>
            <Wrench className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.total}</div>
            <p className="text-xs text-muted-foreground">All time</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Corrective</CardTitle>
            <Target className="h-4 w-4 text-orange-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-600">{stats.corrective}</div>
            <p className="text-xs text-muted-foreground">Fix existing issues</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Preventive</CardTitle>
            <Shield className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">{stats.preventive}</div>
            <p className="text-xs text-muted-foreground">Prevent future issues</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Open</CardTitle>
            <Clock className="h-4 w-4 text-yellow-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-600">{stats.open}</div>
            <p className="text-xs text-muted-foreground">In progress</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Verification</CardTitle>
            <ClipboardCheck className="h-4 w-4 text-purple-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-purple-600">{stats.verification}</div>
            <p className="text-xs text-muted-foreground">Pending verification</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Overdue</CardTitle>
            <AlertCircle className="h-4 w-4 text-red-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">{stats.overdue}</div>
            <p className="text-xs text-muted-foreground">Past target date</p>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-4 flex-wrap">
        <div className="relative flex-1 min-w-[200px]">
          <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search CAPAs..."
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
            <SelectItem value="corrective">Corrective</SelectItem>
            <SelectItem value="preventive">Preventive</SelectItem>
          </SelectContent>
        </Select>
        <Select value={statusFilter} onValueChange={setStatusFilter}>
          <SelectTrigger className="w-[150px]">
            <SelectValue placeholder="Status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Status</SelectItem>
            <SelectItem value="draft">Draft</SelectItem>
            <SelectItem value="open">Open</SelectItem>
            <SelectItem value="in_progress">In Progress</SelectItem>
            <SelectItem value="verification">Verification</SelectItem>
            <SelectItem value="closed">Closed</SelectItem>
            <SelectItem value="cancelled">Cancelled</SelectItem>
          </SelectContent>
        </Select>
        <Select value={priorityFilter} onValueChange={setPriorityFilter}>
          <SelectTrigger className="w-[150px]">
            <SelectValue placeholder="Priority" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Priority</SelectItem>
            <SelectItem value="low">Low</SelectItem>
            <SelectItem value="medium">Medium</SelectItem>
            <SelectItem value="high">High</SelectItem>
            <SelectItem value="critical">Critical</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* CAPAs Table */}
      <Card>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>CAPA #</TableHead>
              <TableHead>Title</TableHead>
              <TableHead>Type</TableHead>
              <TableHead>Priority</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Progress</TableHead>
              <TableHead>Target Date</TableHead>
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
            ) : filteredCAPAs.length === 0 ? (
              <TableRow>
                <TableCell colSpan={9} className="text-center py-8 text-muted-foreground">
                  No CAPAs found
                </TableCell>
              </TableRow>
            ) : (
              filteredCAPAs.map((capa) => (
                <TableRow key={capa.id}>
                  <TableCell className="font-medium">{capa.number}</TableCell>
                  <TableCell className="max-w-[200px] truncate">{capa.title}</TableCell>
                  <TableCell>
                    <Badge className={getTypeBadge(capa.type)}>{capa.type}</Badge>
                  </TableCell>
                  <TableCell>
                    <Badge className={getPriorityBadge(capa.priority)}>{capa.priority}</Badge>
                  </TableCell>
                  <TableCell>
                    <Badge className={getStatusBadge(capa.status)}>
                      {capa.status.replace("_", " ")}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      <Progress value={calculateProgress(capa)} className="w-16 h-2" />
                      <span className="text-sm text-muted-foreground">
                        {calculateProgress(capa)}%
                      </span>
                    </div>
                  </TableCell>
                  <TableCell>
                    <span
                      className={
                        new Date(capa.targetDate) < new Date() && capa.status !== "closed"
                          ? "text-red-600"
                          : ""
                      }
                    >
                      {capa.targetDate}
                    </span>
                  </TableCell>
                  <TableCell>{capa.assignedTo}</TableCell>
                  <TableCell>
                    <div className="flex gap-1">
                      <Button variant="ghost" size="sm" onClick={() => handleViewCAPA(capa)}>
                        <Eye className="h-4 w-4" />
                      </Button>
                      {capa.status !== "closed" && capa.status !== "cancelled" && (
                        <Button variant="ghost" size="sm" onClick={() => handleAddActionItem(capa)}>
                          <Plus className="h-4 w-4 text-green-500" />
                        </Button>
                      )}
                      {capa.status === "verification" && (
                        <Button variant="ghost" size="sm" onClick={() => handleVerification(capa)}>
                          <ClipboardCheck className="h-4 w-4 text-purple-500" />
                        </Button>
                      )}
                      {capa.status === "closed" && (
                        <Button
                          variant="ghost"
                          size="sm"
                          className="text-red-600 hover:text-red-700 hover:bg-red-50"
                          onClick={() => handleDeleteClick(capa)}
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

      {/* View CAPA Dialog */}
      <Dialog open={viewDialogOpen} onOpenChange={setViewDialogOpen}>
        <DialogContent className="max-w-3xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>CAPA Details - {selectedCAPA?.number}</DialogTitle>
            <DialogDescription>{selectedCAPA?.title}</DialogDescription>
          </DialogHeader>
          {selectedCAPA && (
            <Tabs value={activeTab} onValueChange={setActiveTab}>
              <TabsList className="grid w-full grid-cols-4">
                <TabsTrigger value="details">
                  <FileText className="h-4 w-4 mr-2" />
                  Details
                </TabsTrigger>
                <TabsTrigger value="actions">
                  <ListChecks className="h-4 w-4 mr-2" />
                  Actions ({selectedCAPA.actionItems.length})
                </TabsTrigger>
                <TabsTrigger value="verification">
                  <ClipboardCheck className="h-4 w-4 mr-2" />
                  Verification
                </TabsTrigger>
                <TabsTrigger value="timeline">
                  <Clock className="h-4 w-4 mr-2" />
                  Timeline
                </TabsTrigger>
              </TabsList>

              <TabsContent value="details" className="space-y-4 mt-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label className="text-muted-foreground">Type</Label>
                    <div className="mt-1">
                      <Badge className={getTypeBadge(selectedCAPA.type)}>{selectedCAPA.type}</Badge>
                    </div>
                  </div>
                  <div>
                    <Label className="text-muted-foreground">Status</Label>
                    <div className="mt-1">
                      <Badge className={getStatusBadge(selectedCAPA.status)}>
                        {selectedCAPA.status.replace("_", " ")}
                      </Badge>
                    </div>
                  </div>
                  <div>
                    <Label className="text-muted-foreground">Priority</Label>
                    <div className="mt-1">
                      <Badge className={getPriorityBadge(selectedCAPA.priority)}>
                        {selectedCAPA.priority}
                      </Badge>
                    </div>
                  </div>
                  <div>
                    <Label className="text-muted-foreground">Category</Label>
                    <p className="capitalize mt-1">{selectedCAPA.category}</p>
                  </div>
                  <div>
                    <Label className="text-muted-foreground">Source</Label>
                    <p className="mt-1">
                      {selectedCAPA.sourceType.replace("_", " ")} - {selectedCAPA.sourceReference}
                    </p>
                  </div>
                  <div>
                    <Label className="text-muted-foreground">Target Date</Label>
                    <p
                      className={
                        new Date(selectedCAPA.targetDate) < new Date() &&
                        selectedCAPA.status !== "closed"
                          ? "text-red-600 mt-1"
                          : "mt-1"
                      }
                    >
                      {selectedCAPA.targetDate}
                    </p>
                  </div>
                  <div>
                    <Label className="text-muted-foreground">Assigned To</Label>
                    <p className="mt-1">{selectedCAPA.assignedTo}</p>
                  </div>
                  <div>
                    <Label className="text-muted-foreground">Owner</Label>
                    <p className="mt-1">{selectedCAPA.owner}</p>
                  </div>
                </div>
                <div>
                  <Label className="text-muted-foreground">Problem Statement</Label>
                  <p className="mt-1 p-3 bg-muted rounded-md">{selectedCAPA.problemStatement || "-"}</p>
                </div>
                <div>
                  <Label className="text-muted-foreground">Root Cause</Label>
                  <p className="mt-1 p-3 bg-muted rounded-md">{selectedCAPA.rootCause || "Not yet determined"}</p>
                </div>
                <div>
                  <Label className="text-muted-foreground">Proposed Actions</Label>
                  <p className="mt-1 p-3 bg-muted rounded-md whitespace-pre-wrap">
                    {selectedCAPA.proposedActions || "Not yet defined"}
                  </p>
                </div>
                {selectedCAPA.linkedNCRs.length > 0 && (
                  <div>
                    <Label className="text-muted-foreground">Linked NCRs</Label>
                    <div className="flex gap-2 mt-1">
                      {selectedCAPA.linkedNCRs.map((ncr) => (
                        <Badge key={ncr} variant="outline">
                          {ncr}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
              </TabsContent>

              <TabsContent value="actions" className="space-y-4 mt-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h4 className="font-medium">Action Items</h4>
                    <p className="text-sm text-muted-foreground">
                      {selectedCAPA.actionItems.filter((ai) => ai.status === "completed").length} of{" "}
                      {selectedCAPA.actionItems.length} completed
                    </p>
                  </div>
                  <Progress value={calculateProgress(selectedCAPA)} className="w-32" />
                </div>
                {selectedCAPA.actionItems.length === 0 ? (
                  <div className="text-center py-8 text-muted-foreground">
                    No action items defined yet
                  </div>
                ) : (
                  <div className="space-y-3">
                    {selectedCAPA.actionItems.map((action) => (
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
                                <span className="flex items-center gap-1">
                                  <Calendar className="h-4 w-4" />
                                  Due: {action.dueDate}
                                </span>
                              </div>
                              {action.notes && (
                                <p className="text-sm text-muted-foreground mt-2">{action.notes}</p>
                              )}
                            </div>
                            <div className="flex items-center gap-2">
                              <Badge className={getActionStatusBadge(action.status)}>
                                {action.status.replace("_", " ")}
                              </Badge>
                              {action.status !== "completed" && (
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  onClick={() =>
                                    handleUpdateActionStatus(selectedCAPA.id, action.id, "completed")
                                  }
                                >
                                  <CheckCircle className="h-4 w-4 text-green-500" />
                                </Button>
                              )}
                            </div>
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
                {selectedCAPA.status !== "closed" && selectedCAPA.status !== "cancelled" && (
                  <Button
                    variant="outline"
                    className="w-full"
                    onClick={() => handleAddActionItem(selectedCAPA)}
                  >
                    <Plus className="h-4 w-4 mr-2" />
                    Add Action Item
                  </Button>
                )}
              </TabsContent>

              <TabsContent value="verification" className="space-y-4 mt-4">
                <div>
                  <Label className="text-muted-foreground">Verification Required</Label>
                  <p className="mt-1">{selectedCAPA.verificationRequired ? "Yes" : "No"}</p>
                </div>
                <div>
                  <Label className="text-muted-foreground">Verification Method</Label>
                  <p className="mt-1 p-3 bg-muted rounded-md">
                    {selectedCAPA.verificationMethod || "Not specified"}
                  </p>
                </div>
                {selectedCAPA.effectivenessRating !== null && (
                  <div>
                    <Label className="text-muted-foreground">Effectiveness Rating</Label>
                    <div className="flex items-center gap-2 mt-1">
                      <Progress value={selectedCAPA.effectivenessRating} className="w-32" />
                      <span className="font-medium">{selectedCAPA.effectivenessRating}%</span>
                    </div>
                  </div>
                )}
                <div>
                  <Label className="text-muted-foreground">Verification Records</Label>
                  {selectedCAPA.verificationRecords.length === 0 ? (
                    <div className="text-center py-4 text-muted-foreground border rounded-md mt-2">
                      No verification records yet
                    </div>
                  ) : (
                    <div className="space-y-2 mt-2">
                      {selectedCAPA.verificationRecords.map((record) => (
                        <Card key={record.id}>
                          <CardContent className="pt-4">
                            <div className="flex items-start justify-between">
                              <div>
                                <p className="text-sm text-muted-foreground">{record.date}</p>
                                <p className="text-sm">Verified by: {record.verifiedBy}</p>
                                <p className="mt-2">{record.notes}</p>
                              </div>
                              <Badge
                                className={
                                  record.result === "effective"
                                    ? "bg-green-100 text-green-800"
                                    : record.result === "not_effective"
                                    ? "bg-red-100 text-red-800"
                                    : "bg-yellow-100 text-yellow-800"
                                }
                              >
                                {record.result.replace("_", " ")}
                              </Badge>
                            </div>
                          </CardContent>
                        </Card>
                      ))}
                    </div>
                  )}
                </div>
                {selectedCAPA.status === "verification" && (
                  <Button
                    variant="outline"
                    className="w-full"
                    onClick={() => handleVerification(selectedCAPA)}
                  >
                    <ClipboardCheck className="h-4 w-4 mr-2" />
                    Record Verification
                  </Button>
                )}
              </TabsContent>

              <TabsContent value="timeline" className="space-y-4 mt-4">
                <div className="space-y-4">
                  <div className="flex gap-4">
                    <div className="w-24 text-sm text-muted-foreground">{selectedCAPA.createdDate}</div>
                    <div className="flex-1">
                      <p className="font-medium">CAPA Created</p>
                      <p className="text-sm text-muted-foreground">
                        Created by {selectedCAPA.owner}
                      </p>
                    </div>
                  </div>
                  {selectedCAPA.actionItems
                    .filter((ai) => ai.completedDate)
                    .sort((a, b) => new Date(a.completedDate!).getTime() - new Date(b.completedDate!).getTime())
                    .map((action) => (
                      <div key={action.id} className="flex gap-4">
                        <div className="w-24 text-sm text-muted-foreground">{action.completedDate}</div>
                        <div className="flex-1">
                          <p className="font-medium">Action Completed</p>
                          <p className="text-sm text-muted-foreground">{action.description}</p>
                        </div>
                      </div>
                    ))}
                  {selectedCAPA.verificationRecords.map((record) => (
                    <div key={record.id} className="flex gap-4">
                      <div className="w-24 text-sm text-muted-foreground">{record.date}</div>
                      <div className="flex-1">
                        <p className="font-medium">Verification: {record.result.replace("_", " ")}</p>
                        <p className="text-sm text-muted-foreground">{record.notes}</p>
                      </div>
                    </div>
                  ))}
                  {selectedCAPA.actualClosureDate && (
                    <div className="flex gap-4">
                      <div className="w-24 text-sm text-muted-foreground">
                        {selectedCAPA.actualClosureDate}
                      </div>
                      <div className="flex-1">
                        <p className="font-medium text-green-600">CAPA Closed</p>
                        <p className="text-sm text-muted-foreground">
                          Effectiveness Rating: {selectedCAPA.effectivenessRating}%
                        </p>
                      </div>
                    </div>
                  )}
                </div>
              </TabsContent>
            </Tabs>
          )}
          <DialogFooter>
            <Button variant="outline" onClick={() => setViewDialogOpen(false)}>
              Close
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Add Action Item Dialog */}
      <Dialog open={actionDialogOpen} onOpenChange={setActionDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Add Action Item</DialogTitle>
            <DialogDescription>
              Add a new action item to {selectedCAPA?.number}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label>Description *</Label>
              <Textarea
                placeholder="Describe the action to be taken..."
                value={newActionItem.description}
                onChange={(e) =>
                  setNewActionItem({ ...newActionItem, description: e.target.value })
                }
                rows={3}
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Assigned To *</Label>
                <Select
                  value={newActionItem.assignedTo}
                  onValueChange={(value) =>
                    setNewActionItem({ ...newActionItem, assignedTo: value })
                  }
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select assignee" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Engineering">Engineering</SelectItem>
                    <SelectItem value="Quality Team">Quality Team</SelectItem>
                    <SelectItem value="Maintenance Team">Maintenance Team</SelectItem>
                    <SelectItem value="Production">Production</SelectItem>
                    <SelectItem value="IT Team">IT Team</SelectItem>
                    <SelectItem value="Training Coordinator">Training Coordinator</SelectItem>
                    <SelectItem value="Procurement">Procurement</SelectItem>
                    <SelectItem value="Supplier QA">Supplier QA</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label>Due Date *</Label>
                <Input
                  type="date"
                  value={newActionItem.dueDate}
                  onChange={(e) => setNewActionItem({ ...newActionItem, dueDate: e.target.value })}
                />
              </div>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setActionDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleSaveActionItem}>Add Action Item</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Verification Dialog */}
      <Dialog open={verificationDialogOpen} onOpenChange={setVerificationDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Record Verification</DialogTitle>
            <DialogDescription>
              Verify the effectiveness of {selectedCAPA?.number}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label>Verification Result *</Label>
              <Select
                value={verificationData.result}
                onValueChange={(value) =>
                  setVerificationData({ ...verificationData, result: value as any })
                }
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select result" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="effective">Effective - Close CAPA</SelectItem>
                  <SelectItem value="partial">Partial - Continue Monitoring</SelectItem>
                  <SelectItem value="not_effective">Not Effective - Requires Additional Action</SelectItem>
                </SelectContent>
              </Select>
            </div>
            {verificationData.result === "effective" && (
              <div className="space-y-2">
                <Label>Effectiveness Rating (%)</Label>
                <Input
                  type="number"
                  min="0"
                  max="100"
                  value={verificationData.effectivenessRating}
                  onChange={(e) =>
                    setVerificationData({
                      ...verificationData,
                      effectivenessRating: parseInt(e.target.value) || 0,
                    })
                  }
                />
              </div>
            )}
            <div className="space-y-2">
              <Label>Notes</Label>
              <Textarea
                placeholder="Verification notes and observations..."
                value={verificationData.notes}
                onChange={(e) =>
                  setVerificationData({ ...verificationData, notes: e.target.value })
                }
                rows={3}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setVerificationDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleSaveVerification}>Save Verification</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-red-500" />
              Delete CAPA
            </AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete <strong>{selectedCAPA?.number}</strong>? This action
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
