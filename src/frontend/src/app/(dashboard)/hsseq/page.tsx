"use client";
import { useState } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
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
import { Textarea } from "@/components/ui/textarea";
import { useApi, useToast } from "@/hooks";
import {
  AlertTriangle,
  Shield,
  ClipboardCheck,
  GraduationCap,
  FileWarning,
  Eye,
  TrendingUp,
  Plus,
  Search,
  Filter,
  Download,
  Calendar,
  Clock,
  CheckCircle2,
  XCircle,
  AlertCircle,
  Activity,
  Users,
  FileText,
  BarChart3,
  Target,
  Wrench,
  HardHat,
  Flame,
  Zap,
  Shovel,
  ArrowUp,
  Package,
  Trash2,
  Loader2,
} from "lucide-react";

// Dashboard Stats Component
function DashboardStats() {
  const stats = {
    daysWithoutIncident: 45,
    openIncidents: 3,
    overdueActions: 5,
    activePermits: 12,
    upcomingTrainings: 8,
    pendingInspections: 4,
  };

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Days Without Incident</CardTitle>
          <Shield className="h-4 w-4 text-green-600" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold text-green-600">{stats.daysWithoutIncident}</div>
          <p className="text-xs text-muted-foreground">Keep up the safe work!</p>
        </CardContent>
      </Card>
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Open Incidents</CardTitle>
          <AlertTriangle className="h-4 w-4 text-red-600" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold text-red-600">{stats.openIncidents}</div>
          <p className="text-xs text-muted-foreground">Require investigation</p>
        </CardContent>
      </Card>
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Overdue Actions</CardTitle>
          <Clock className="h-4 w-4 text-orange-600" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold text-orange-600">{stats.overdueActions}</div>
          <p className="text-xs text-muted-foreground">Need immediate attention</p>
        </CardContent>
      </Card>
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Active Permits</CardTitle>
          <FileText className="h-4 w-4 text-blue-600" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold text-blue-600">{stats.activePermits}</div>
          <p className="text-xs text-muted-foreground">Currently in progress</p>
        </CardContent>
      </Card>
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Upcoming Trainings</CardTitle>
          <GraduationCap className="h-4 w-4 text-purple-600" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold text-purple-600">{stats.upcomingTrainings}</div>
          <p className="text-xs text-muted-foreground">Next 30 days</p>
        </CardContent>
      </Card>
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Pending Inspections</CardTitle>
          <ClipboardCheck className="h-4 w-4 text-cyan-600" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold text-cyan-600">{stats.pendingInspections}</div>
          <p className="text-xs text-muted-foreground">Scheduled this week</p>
        </CardContent>
      </Card>
    </div>
  );
}

// KPI Dashboard Component
function KPIDashboard() {
  const kpis = [
    { name: "LTIFR", value: 0.5, target: 1.0, unit: "per million hours", trend: "down", status: "good" },
    { name: "TRIFR", value: 2.3, target: 3.0, unit: "per million hours", trend: "down", status: "good" },
    { name: "Severity Rate", value: 15, target: 20, unit: "days per million hours", trend: "stable", status: "good" },
    { name: "Near Miss Ratio", value: 12, target: 10, unit: "per incident", trend: "up", status: "good" },
    { name: "Training Compliance", value: 92, target: 95, unit: "%", trend: "up", status: "warning" },
    { name: "Inspection Completion", value: 88, target: 90, unit: "%", trend: "stable", status: "warning" },
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case "good": return "text-green-600";
      case "warning": return "text-yellow-600";
      case "critical": return "text-red-600";
      default: return "text-gray-600";
    }
  };

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case "up": return <TrendingUp className="h-4 w-4 text-green-600" />;
      case "down": return <TrendingUp className="h-4 w-4 text-green-600 rotate-180" />;
      default: return <Activity className="h-4 w-4 text-gray-600" />;
    }
  };

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      {kpis.map((kpi) => (
        <Card key={kpi.name}>
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <CardTitle className="text-sm font-medium">{kpi.name}</CardTitle>
              {getTrendIcon(kpi.trend)}
            </div>
          </CardHeader>
          <CardContent>
            <div className="flex items-baseline space-x-2">
              <span className={`text-2xl font-bold ${getStatusColor(kpi.status)}`}>
                {kpi.value}
              </span>
              <span className="text-sm text-muted-foreground">{kpi.unit}</span>
            </div>
            <div className="mt-2">
              <div className="flex justify-between text-xs text-muted-foreground mb-1">
                <span>Target: {kpi.target}</span>
                <span>{Math.round((kpi.value / kpi.target) * 100)}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className={`h-2 rounded-full ${
                    kpi.status === "good" ? "bg-green-600" : kpi.status === "warning" ? "bg-yellow-600" : "bg-red-600"
                  }`}
                  style={{ width: `${Math.min((kpi.value / kpi.target) * 100, 100)}%` }}
                />
              </div>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}

// Incident Interface
interface Incident {
  id: string;
  title: string;
  category: string;
  type: string;
  severity: string;
  status: string;
  date: string;
  location: string;
  reportedBy: string;
}

// Incidents Tab Component
function IncidentsTab() {
  const [showNewDialog, setShowNewDialog] = useState(false);
  const { showToast } = useToast();
  const deleteApi = useApi();

  const [incidents, setIncidents] = useState<Incident[]>([
    {
      id: "INC-2026-00045",
      title: "Slip and fall in warehouse",
      category: "safety",
      type: "first_aid",
      severity: "minor",
      status: "under_investigation",
      date: "2026-01-12",
      location: "Warehouse A",
      reportedBy: "John Smith",
    },
    {
      id: "INC-2026-00044",
      title: "Near miss - forklift incident",
      category: "safety",
      type: "near_miss",
      severity: "moderate",
      status: "corrective_action_pending",
      date: "2026-01-10",
      location: "Loading Bay",
      reportedBy: "Mike Johnson",
    },
    {
      id: "INC-2026-00043",
      title: "Chemical spill in lab",
      category: "environment",
      type: "environmental_spill",
      severity: "major",
      status: "closed",
      date: "2026-01-08",
      location: "Laboratory B",
      reportedBy: "Sarah Wilson",
    },
  ]);

  // Delete state
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [incidentToDelete, setIncidentToDelete] = useState<Incident | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  const handleDeleteClick = (incident: Incident) => {
    setIncidentToDelete(incident);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!incidentToDelete) return;
    setIsDeleting(true);
    try {
      await deleteApi.delete(`/hsseq/incidents/${incidentToDelete.id}`);
      setIncidents(incidents.filter(i => i.id !== incidentToDelete.id));
      setDeleteDialogOpen(false);
      setIncidentToDelete(null);
      showToast("success", "Incident deleted successfully");
    } catch (error) {
      console.error("Failed to delete incident:", error);
      showToast("error", "Failed to delete incident");
    } finally {
      setIsDeleting(false);
    }
  };

  const getSeverityBadge = (severity: string) => {
    const variants: Record<string, string> = {
      minor: "bg-green-100 text-green-800",
      moderate: "bg-yellow-100 text-yellow-800",
      major: "bg-orange-100 text-orange-800",
      critical: "bg-red-100 text-red-800",
      catastrophic: "bg-purple-100 text-purple-800",
    };
    return <Badge className={variants[severity] || "bg-gray-100"}>{severity}</Badge>;
  };

  const getStatusBadge = (status: string) => {
    const variants: Record<string, string> = {
      reported: "bg-blue-100 text-blue-800",
      under_investigation: "bg-yellow-100 text-yellow-800",
      investigation_complete: "bg-purple-100 text-purple-800",
      corrective_action_pending: "bg-orange-100 text-orange-800",
      closed: "bg-green-100 text-green-800",
    };
    return <Badge className={variants[status] || "bg-gray-100"}>{status.replace(/_/g, " ")}</Badge>;
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <div className="relative">
            <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input placeholder="Search incidents..." className="pl-8 w-64" />
          </div>
          <Select defaultValue="all">
            <SelectTrigger className="w-32">
              <SelectValue placeholder="Category" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Categories</SelectItem>
              <SelectItem value="safety">Safety</SelectItem>
              <SelectItem value="health">Health</SelectItem>
              <SelectItem value="environment">Environment</SelectItem>
              <SelectItem value="security">Security</SelectItem>
              <SelectItem value="quality">Quality</SelectItem>
            </SelectContent>
          </Select>
          <Select defaultValue="all">
            <SelectTrigger className="w-32">
              <SelectValue placeholder="Status" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Status</SelectItem>
              <SelectItem value="open">Open</SelectItem>
              <SelectItem value="under_investigation">Under Investigation</SelectItem>
              <SelectItem value="closed">Closed</SelectItem>
            </SelectContent>
          </Select>
        </div>
        <div className="flex items-center space-x-2">
          <Button variant="outline" size="sm">
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
          <Dialog open={showNewDialog} onOpenChange={setShowNewDialog}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="h-4 w-4 mr-2" />
                Report Incident
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl">
              <DialogHeader>
                <DialogTitle>Report New Incident</DialogTitle>
                <DialogDescription>
                  Report a new HSE incident. All fields marked with * are required.
                </DialogDescription>
              </DialogHeader>
              <div className="grid gap-4 py-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="category">Category *</Label>
                    <Select>
                      <SelectTrigger>
                        <SelectValue placeholder="Select category" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="safety">Safety</SelectItem>
                        <SelectItem value="health">Health</SelectItem>
                        <SelectItem value="environment">Environment</SelectItem>
                        <SelectItem value="security">Security</SelectItem>
                        <SelectItem value="quality">Quality</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="type">Incident Type *</Label>
                    <Select>
                      <SelectTrigger>
                        <SelectValue placeholder="Select type" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="near_miss">Near Miss</SelectItem>
                        <SelectItem value="first_aid">First Aid</SelectItem>
                        <SelectItem value="medical_treatment">Medical Treatment</SelectItem>
                        <SelectItem value="lost_time">Lost Time</SelectItem>
                        <SelectItem value="property_damage">Property Damage</SelectItem>
                        <SelectItem value="environmental_spill">Environmental Spill</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="title">Title *</Label>
                  <Input id="title" placeholder="Brief description of the incident" />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="date">Date *</Label>
                    <Input id="date" type="date" />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="time">Time</Label>
                    <Input id="time" type="time" />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="location">Location *</Label>
                    <Input id="location" placeholder="Where did it happen?" />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="severity">Severity *</Label>
                    <Select>
                      <SelectTrigger>
                        <SelectValue placeholder="Select severity" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="minor">Minor</SelectItem>
                        <SelectItem value="moderate">Moderate</SelectItem>
                        <SelectItem value="major">Major</SelectItem>
                        <SelectItem value="critical">Critical</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="description">Description *</Label>
                  <Textarea id="description" placeholder="Detailed description of what happened..." rows={4} />
                </div>
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={() => setShowNewDialog(false)}>Cancel</Button>
                <Button onClick={() => setShowNewDialog(false)}>Submit Report</Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      <Card>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>ID</TableHead>
              <TableHead>Title</TableHead>
              <TableHead>Category</TableHead>
              <TableHead>Type</TableHead>
              <TableHead>Severity</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Date</TableHead>
              <TableHead>Location</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {incidents.map((incident) => (
              <TableRow key={incident.id}>
                <TableCell className="font-mono text-sm">{incident.id}</TableCell>
                <TableCell className="font-medium">{incident.title}</TableCell>
                <TableCell>
                  <Badge variant="outline">{incident.category}</Badge>
                </TableCell>
                <TableCell>{incident.type.replace(/_/g, " ")}</TableCell>
                <TableCell>{getSeverityBadge(incident.severity)}</TableCell>
                <TableCell>{getStatusBadge(incident.status)}</TableCell>
                <TableCell>{incident.date}</TableCell>
                <TableCell>{incident.location}</TableCell>
                <TableCell className="text-right">
                  <div className="flex justify-end gap-1">
                    <Button variant="ghost" size="sm">
                      <Eye className="h-4 w-4" />
                    </Button>
                    {incident.status === "closed" && (
                      <Button
                        variant="ghost"
                        size="sm"
                        className="text-red-600 hover:text-red-700 hover:bg-red-50"
                        onClick={() => handleDeleteClick(incident)}
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

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-red-500" />
              Delete Incident
            </AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete incident <strong>{incidentToDelete?.id}</strong>?
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

// Permit Interface
interface Permit {
  id: string;
  title: string;
  type: string;
  status: string;
  location: string;
  validFrom: string;
  validUntil: string;
  requestor: string;
}

// Work Permits Tab Component
function PermitsTab() {
  const [showNewDialog, setShowNewDialog] = useState(false);
  const { showToast } = useToast();
  const deleteApi = useApi();

  const [permits, setPermits] = useState<Permit[]>([
    {
      id: "PTW-2026-00123",
      title: "Welding work on storage tank",
      type: "hot_work",
      status: "active",
      location: "Tank Farm Area",
      validFrom: "2026-01-15 08:00",
      validUntil: "2026-01-15 18:00",
      requestor: "Mike Wilson",
    },
    {
      id: "PTW-2026-00122",
      title: "Electrical panel maintenance",
      type: "electrical",
      status: "pending_approval",
      location: "Substation B",
      validFrom: "2026-01-16 09:00",
      validUntil: "2026-01-16 17:00",
      requestor: "David Brown",
    },
    {
      id: "PTW-2026-00121",
      title: "Confined space entry - vessel inspection",
      type: "confined_space",
      status: "approved",
      location: "Vessel V-101",
      validFrom: "2026-01-15 07:00",
      validUntil: "2026-01-15 15:00",
      requestor: "Tom Clark",
    },
  ]);

  // Delete state
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [permitToDelete, setPermitToDelete] = useState<Permit | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  const handleDeleteClick = (permit: Permit) => {
    setPermitToDelete(permit);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!permitToDelete) return;
    setIsDeleting(true);
    try {
      await deleteApi.delete(`/hsseq/permits/${permitToDelete.id}`);
      setPermits(permits.filter(p => p.id !== permitToDelete.id));
      setDeleteDialogOpen(false);
      setPermitToDelete(null);
      showToast("success", "Permit deleted successfully");
    } catch (error) {
      console.error("Failed to delete permit:", error);
      showToast("error", "Failed to delete permit");
    } finally {
      setIsDeleting(false);
    }
  };

  const getPermitTypeIcon = (type: string) => {
    switch (type) {
      case "hot_work": return <Flame className="h-4 w-4 text-orange-600" />;
      case "electrical": return <Zap className="h-4 w-4 text-yellow-600" />;
      case "confined_space": return <Package className="h-4 w-4 text-blue-600" />;
      case "working_at_height": return <ArrowUp className="h-4 w-4 text-purple-600" />;
      case "excavation": return <Shovel className="h-4 w-4 text-brown-600" />;
      case "lifting": return <Wrench className="h-4 w-4 text-gray-600" />;
      default: return <FileText className="h-4 w-4 text-gray-600" />;
    }
  };

  const getStatusBadge = (status: string) => {
    const variants: Record<string, string> = {
      draft: "bg-gray-100 text-gray-800",
      pending_approval: "bg-yellow-100 text-yellow-800",
      approved: "bg-blue-100 text-blue-800",
      active: "bg-green-100 text-green-800",
      suspended: "bg-red-100 text-red-800",
      completed: "bg-purple-100 text-purple-800",
      cancelled: "bg-gray-100 text-gray-800",
    };
    return <Badge className={variants[status] || "bg-gray-100"}>{status.replace(/_/g, " ")}</Badge>;
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <div className="relative">
            <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input placeholder="Search permits..." className="pl-8 w-64" />
          </div>
          <Select defaultValue="all">
            <SelectTrigger className="w-40">
              <SelectValue placeholder="Permit Type" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Types</SelectItem>
              <SelectItem value="hot_work">Hot Work</SelectItem>
              <SelectItem value="confined_space">Confined Space</SelectItem>
              <SelectItem value="electrical">Electrical</SelectItem>
              <SelectItem value="working_at_height">Working at Height</SelectItem>
              <SelectItem value="excavation">Excavation</SelectItem>
              <SelectItem value="lifting">Lifting</SelectItem>
            </SelectContent>
          </Select>
          <Select defaultValue="active">
            <SelectTrigger className="w-32">
              <SelectValue placeholder="Status" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Status</SelectItem>
              <SelectItem value="active">Active</SelectItem>
              <SelectItem value="pending">Pending</SelectItem>
              <SelectItem value="completed">Completed</SelectItem>
            </SelectContent>
          </Select>
        </div>
        <Dialog open={showNewDialog} onOpenChange={setShowNewDialog}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              New Permit
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>Create Work Permit</DialogTitle>
              <DialogDescription>
                Request a new permit to work. Complete all required fields.
              </DialogDescription>
            </DialogHeader>
            <div className="grid gap-4 py-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Permit Type *</Label>
                  <Select>
                    <SelectTrigger>
                      <SelectValue placeholder="Select type" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="hot_work">Hot Work</SelectItem>
                      <SelectItem value="confined_space">Confined Space</SelectItem>
                      <SelectItem value="electrical">Electrical</SelectItem>
                      <SelectItem value="working_at_height">Working at Height</SelectItem>
                      <SelectItem value="excavation">Excavation</SelectItem>
                      <SelectItem value="lifting">Lifting</SelectItem>
                      <SelectItem value="general">General</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label>Work Location *</Label>
                  <Input placeholder="Enter work location" />
                </div>
              </div>
              <div className="space-y-2">
                <Label>Work Description *</Label>
                <Input placeholder="Brief description of the work" />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Valid From *</Label>
                  <Input type="datetime-local" />
                </div>
                <div className="space-y-2">
                  <Label>Valid Until *</Label>
                  <Input type="datetime-local" />
                </div>
              </div>
              <div className="space-y-2">
                <Label>Identified Hazards</Label>
                <Textarea placeholder="List all identified hazards..." rows={3} />
              </div>
              <div className="space-y-2">
                <Label>Control Measures</Label>
                <Textarea placeholder="Describe control measures..." rows={3} />
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setShowNewDialog(false)}>Cancel</Button>
              <Button onClick={() => setShowNewDialog(false)}>Submit for Approval</Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {permits.map((permit) => (
          <Card key={permit.id} className="hover:shadow-md transition-shadow">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  {getPermitTypeIcon(permit.type)}
                  <span className="text-sm font-mono">{permit.id}</span>
                </div>
                {getStatusBadge(permit.status)}
              </div>
              <CardTitle className="text-base">{permit.title}</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex items-center text-sm text-muted-foreground">
                <Target className="h-4 w-4 mr-2" />
                {permit.location}
              </div>
              <div className="flex items-center text-sm text-muted-foreground">
                <Clock className="h-4 w-4 mr-2" />
                {permit.validFrom} - {permit.validUntil.split(" ")[1]}
              </div>
              <div className="flex items-center text-sm text-muted-foreground">
                <Users className="h-4 w-4 mr-2" />
                {permit.requestor}
              </div>
              <div className="flex justify-end space-x-2 pt-2">
                <Button variant="outline" size="sm">View</Button>
                {permit.status === "pending_approval" && (
                  <Button size="sm">Approve</Button>
                )}
                {(permit.status === "completed" || permit.status === "cancelled") && (
                  <Button
                    variant="ghost"
                    size="sm"
                    className="text-red-600 hover:text-red-700 hover:bg-red-50"
                    onClick={() => handleDeleteClick(permit)}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                )}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-red-500" />
              Delete Permit
            </AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete permit <strong>{permitToDelete?.id}</strong>?
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

// Training Interface
interface Training {
  id: string;
  title: string;
  type: string;
  category: string;
  date: string;
  time: string;
  location: string;
  trainer: string;
  registered: number;
  max: number;
  mandatory: boolean;
}

// Trainings Tab Component
function TrainingsTab() {
  const { showToast } = useToast();
  const deleteApi = useApi();

  const [trainings, setTrainings] = useState<Training[]>([
    {
      id: "TRN-2026-00089",
      title: "Fire Safety Training",
      type: "certification",
      category: "safety",
      date: "2026-01-20",
      time: "09:00 - 17:00",
      location: "Training Room A",
      trainer: "Safety Institute",
      registered: 25,
      max: 30,
      mandatory: true,
    },
    {
      id: "TRN-2026-00088",
      title: "First Aid and CPR",
      type: "certification",
      category: "health",
      date: "2026-01-22",
      time: "09:00 - 13:00",
      location: "Medical Center",
      trainer: "Red Cross",
      registered: 15,
      max: 20,
      mandatory: true,
    },
    {
      id: "TRN-2026-00087",
      title: "Toolbox Talk - Working at Heights",
      type: "toolbox_talk",
      category: "safety",
      date: "2026-01-15",
      time: "07:00 - 07:30",
      location: "Site Office",
      trainer: "HSE Manager",
      registered: 40,
      max: 50,
      mandatory: false,
    },
  ]);

  // Delete state
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [trainingToDelete, setTrainingToDelete] = useState<Training | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  const handleDeleteClick = (training: Training) => {
    setTrainingToDelete(training);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!trainingToDelete) return;
    setIsDeleting(true);
    try {
      await deleteApi.delete(`/hsseq/trainings/${trainingToDelete.id}`);
      setTrainings(trainings.filter(t => t.id !== trainingToDelete.id));
      setDeleteDialogOpen(false);
      setTrainingToDelete(null);
      showToast("success", "Training deleted successfully");
    } catch (error) {
      console.error("Failed to delete training:", error);
      showToast("error", "Failed to delete training");
    } finally {
      setIsDeleting(false);
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <div className="relative">
            <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input placeholder="Search trainings..." className="pl-8 w-64" />
          </div>
          <Select defaultValue="all">
            <SelectTrigger className="w-32">
              <SelectValue placeholder="Type" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Types</SelectItem>
              <SelectItem value="induction">Induction</SelectItem>
              <SelectItem value="certification">Certification</SelectItem>
              <SelectItem value="refresher">Refresher</SelectItem>
              <SelectItem value="toolbox_talk">Toolbox Talk</SelectItem>
            </SelectContent>
          </Select>
        </div>
        <Button>
          <Plus className="h-4 w-4 mr-2" />
          Schedule Training
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {trainings.map((training) => (
          <Card key={training.id} className="hover:shadow-md transition-shadow">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <Badge variant="outline">{training.type.replace(/_/g, " ")}</Badge>
                {training.mandatory && (
                  <Badge className="bg-red-100 text-red-800">Mandatory</Badge>
                )}
              </div>
              <CardTitle className="text-base">{training.title}</CardTitle>
              <CardDescription>{training.id}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex items-center text-sm text-muted-foreground">
                <Calendar className="h-4 w-4 mr-2" />
                {training.date}
              </div>
              <div className="flex items-center text-sm text-muted-foreground">
                <Clock className="h-4 w-4 mr-2" />
                {training.time}
              </div>
              <div className="flex items-center text-sm text-muted-foreground">
                <Target className="h-4 w-4 mr-2" />
                {training.location}
              </div>
              <div className="flex items-center text-sm text-muted-foreground">
                <Users className="h-4 w-4 mr-2" />
                {training.registered}/{training.max} registered
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-blue-600 h-2 rounded-full"
                  style={{ width: `${(training.registered / training.max) * 100}%` }}
                />
              </div>
              <div className="flex justify-end space-x-2 pt-2">
                <Button variant="outline" size="sm">View</Button>
                <Button size="sm">Register</Button>
                {!training.mandatory && training.registered === 0 && (
                  <Button
                    variant="ghost"
                    size="sm"
                    className="text-red-600 hover:text-red-700 hover:bg-red-50"
                    onClick={() => handleDeleteClick(training)}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                )}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-red-500" />
              Delete Training
            </AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete training <strong>{trainingToDelete?.title}</strong>?
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

// Hazard Interface
interface Hazard {
  id: string;
  title: string;
  category: string;
  location: string;
  riskLevel: string;
  riskScore: number;
  status: string;
}

// Hazards Tab Component
function HazardsTab() {
  const { showToast } = useToast();
  const deleteApi = useApi();

  const [hazards, setHazards] = useState<Hazard[]>([
    {
      id: "HAZ-2026-00034",
      title: "Slippery floor near water cooler",
      category: "safety",
      location: "Office Building",
      riskLevel: "medium",
      riskScore: 9,
      status: "active",
    },
    {
      id: "HAZ-2026-00033",
      title: "Exposed electrical wiring",
      category: "safety",
      location: "Maintenance Workshop",
      riskLevel: "high",
      riskScore: 15,
      status: "active",
    },
    {
      id: "HAZ-2026-00032",
      title: "Chemical storage area ventilation",
      category: "environment",
      location: "Chemical Store",
      riskLevel: "extreme",
      riskScore: 20,
      status: "active",
    },
  ]);

  // Delete state
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [hazardToDelete, setHazardToDelete] = useState<Hazard | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  const handleDeleteClick = (hazard: Hazard) => {
    setHazardToDelete(hazard);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!hazardToDelete) return;
    setIsDeleting(true);
    try {
      await deleteApi.delete(`/hsseq/hazards/${hazardToDelete.id}`);
      setHazards(hazards.filter(h => h.id !== hazardToDelete.id));
      setDeleteDialogOpen(false);
      setHazardToDelete(null);
      showToast("success", "Hazard deleted successfully");
    } catch (error) {
      console.error("Failed to delete hazard:", error);
      showToast("error", "Failed to delete hazard");
    } finally {
      setIsDeleting(false);
    }
  };

  const getRiskBadge = (level: string) => {
    const variants: Record<string, string> = {
      low: "bg-green-100 text-green-800",
      medium: "bg-yellow-100 text-yellow-800",
      high: "bg-orange-100 text-orange-800",
      extreme: "bg-red-100 text-red-800",
    };
    return <Badge className={variants[level]}>{level}</Badge>;
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <div className="relative">
            <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input placeholder="Search hazards..." className="pl-8 w-64" />
          </div>
          <Select defaultValue="all">
            <SelectTrigger className="w-32">
              <SelectValue placeholder="Risk Level" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Levels</SelectItem>
              <SelectItem value="extreme">Extreme</SelectItem>
              <SelectItem value="high">High</SelectItem>
              <SelectItem value="medium">Medium</SelectItem>
              <SelectItem value="low">Low</SelectItem>
            </SelectContent>
          </Select>
        </div>
        <Button>
          <Plus className="h-4 w-4 mr-2" />
          Report Hazard
        </Button>
      </div>

      <Card>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>ID</TableHead>
              <TableHead>Title</TableHead>
              <TableHead>Category</TableHead>
              <TableHead>Location</TableHead>
              <TableHead>Risk Level</TableHead>
              <TableHead>Risk Score</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {hazards.map((hazard) => (
              <TableRow key={hazard.id}>
                <TableCell className="font-mono text-sm">{hazard.id}</TableCell>
                <TableCell className="font-medium">{hazard.title}</TableCell>
                <TableCell>
                  <Badge variant="outline">{hazard.category}</Badge>
                </TableCell>
                <TableCell>{hazard.location}</TableCell>
                <TableCell>{getRiskBadge(hazard.riskLevel)}</TableCell>
                <TableCell>
                  <span className={`font-bold ${
                    hazard.riskScore >= 15 ? "text-red-600" :
                    hazard.riskScore >= 9 ? "text-orange-600" : "text-yellow-600"
                  }`}>
                    {hazard.riskScore}
                  </span>
                </TableCell>
                <TableCell className="text-right">
                  <div className="flex justify-end gap-1">
                    <Button variant="ghost" size="sm">
                      <Eye className="h-4 w-4" />
                    </Button>
                    {hazard.status === "mitigated" && (
                      <Button
                        variant="ghost"
                        size="sm"
                        className="text-red-600 hover:text-red-700 hover:bg-red-50"
                        onClick={() => handleDeleteClick(hazard)}
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

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-red-500" />
              Delete Hazard
            </AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete hazard <strong>{hazardToDelete?.id}</strong>?
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

// Action Interface
interface Action {
  id: string;
  title: string;
  source: string;
  priority: string;
  status: string;
  assignee: string;
  dueDate: string;
  completion: number;
}

// Corrective Actions Tab Component
function ActionsTab() {
  const { showToast } = useToast();
  const deleteApi = useApi();

  const [actions, setActions] = useState<Action[]>([
    {
      id: "ACT-2026-00156",
      title: "Install anti-slip mats",
      source: "Incident INC-2026-00045",
      priority: "high",
      status: "in_progress",
      assignee: "Maintenance Team",
      dueDate: "2026-01-20",
      completion: 60,
    },
    {
      id: "ACT-2026-00155",
      title: "Update forklift safety procedures",
      source: "Incident INC-2026-00044",
      priority: "critical",
      status: "open",
      assignee: "HSE Manager",
      dueDate: "2026-01-18",
      completion: 0,
    },
    {
      id: "ACT-2026-00154",
      title: "Chemical spill kit replenishment",
      source: "Incident INC-2026-00043",
      priority: "medium",
      status: "pending_verification",
      assignee: "Lab Supervisor",
      dueDate: "2026-01-15",
      completion: 100,
    },
  ]);

  // Delete state
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [actionToDelete, setActionToDelete] = useState<Action | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  const handleDeleteClick = (action: Action) => {
    setActionToDelete(action);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!actionToDelete) return;
    setIsDeleting(true);
    try {
      await deleteApi.delete(`/hsseq/actions/${actionToDelete.id}`);
      setActions(actions.filter(a => a.id !== actionToDelete.id));
      setDeleteDialogOpen(false);
      setActionToDelete(null);
      showToast("success", "Action deleted successfully");
    } catch (error) {
      console.error("Failed to delete action:", error);
      showToast("error", "Failed to delete action");
    } finally {
      setIsDeleting(false);
    }
  };

  const getPriorityBadge = (priority: string) => {
    const variants: Record<string, string> = {
      low: "bg-blue-100 text-blue-800",
      medium: "bg-yellow-100 text-yellow-800",
      high: "bg-orange-100 text-orange-800",
      critical: "bg-red-100 text-red-800",
    };
    return <Badge className={variants[priority]}>{priority}</Badge>;
  };

  const getStatusBadge = (status: string) => {
    const variants: Record<string, string> = {
      open: "bg-blue-100 text-blue-800",
      in_progress: "bg-yellow-100 text-yellow-800",
      pending_verification: "bg-purple-100 text-purple-800",
      closed: "bg-green-100 text-green-800",
      overdue: "bg-red-100 text-red-800",
    };
    return <Badge className={variants[status] || "bg-gray-100"}>{status.replace(/_/g, " ")}</Badge>;
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <div className="relative">
            <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input placeholder="Search actions..." className="pl-8 w-64" />
          </div>
          <Select defaultValue="all">
            <SelectTrigger className="w-32">
              <SelectValue placeholder="Status" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Status</SelectItem>
              <SelectItem value="open">Open</SelectItem>
              <SelectItem value="in_progress">In Progress</SelectItem>
              <SelectItem value="overdue">Overdue</SelectItem>
              <SelectItem value="closed">Closed</SelectItem>
            </SelectContent>
          </Select>
          <Select defaultValue="all">
            <SelectTrigger className="w-32">
              <SelectValue placeholder="Priority" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Priority</SelectItem>
              <SelectItem value="critical">Critical</SelectItem>
              <SelectItem value="high">High</SelectItem>
              <SelectItem value="medium">Medium</SelectItem>
              <SelectItem value="low">Low</SelectItem>
            </SelectContent>
          </Select>
        </div>
        <Button>
          <Plus className="h-4 w-4 mr-2" />
          New Action
        </Button>
      </div>

      <Card>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>ID</TableHead>
              <TableHead>Title</TableHead>
              <TableHead>Source</TableHead>
              <TableHead>Priority</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Assignee</TableHead>
              <TableHead>Due Date</TableHead>
              <TableHead>Progress</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {actions.map((action) => (
              <TableRow key={action.id}>
                <TableCell className="font-mono text-sm">{action.id}</TableCell>
                <TableCell className="font-medium">{action.title}</TableCell>
                <TableCell className="text-sm text-muted-foreground">{action.source}</TableCell>
                <TableCell>{getPriorityBadge(action.priority)}</TableCell>
                <TableCell>{getStatusBadge(action.status)}</TableCell>
                <TableCell>{action.assignee}</TableCell>
                <TableCell>{action.dueDate}</TableCell>
                <TableCell>
                  <div className="flex items-center space-x-2">
                    <div className="w-16 bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-blue-600 h-2 rounded-full"
                        style={{ width: `${action.completion}%` }}
                      />
                    </div>
                    <span className="text-sm">{action.completion}%</span>
                  </div>
                </TableCell>
                <TableCell className="text-right">
                  <div className="flex justify-end gap-1">
                    <Button variant="ghost" size="sm">
                      <Eye className="h-4 w-4" />
                    </Button>
                    {action.status === "closed" && (
                      <Button
                        variant="ghost"
                        size="sm"
                        className="text-red-600 hover:text-red-700 hover:bg-red-50"
                        onClick={() => handleDeleteClick(action)}
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

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-red-500" />
              Delete Action
            </AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete action <strong>{actionToDelete?.id}</strong>?
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

// Main HSSEQ Page Component
export default function HSSeqPage() {
  return (
    <div className="flex-1 space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">HSSEQ Management</h1>
          <p className="text-muted-foreground">
            Health, Safety, Security, Environment, and Quality Management
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Button variant="outline">
            <BarChart3 className="h-4 w-4 mr-2" />
            Reports
          </Button>
          <Button variant="outline">
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
        </div>
      </div>

      <DashboardStats />

      <Tabs defaultValue="dashboard" className="space-y-4">
        <TabsList className="grid w-full grid-cols-7">
          <TabsTrigger value="dashboard" className="flex items-center space-x-2">
            <BarChart3 className="h-4 w-4" />
            <span>Dashboard</span>
          </TabsTrigger>
          <TabsTrigger value="incidents" className="flex items-center space-x-2">
            <AlertTriangle className="h-4 w-4" />
            <span>Incidents</span>
          </TabsTrigger>
          <TabsTrigger value="hazards" className="flex items-center space-x-2">
            <FileWarning className="h-4 w-4" />
            <span>Hazards</span>
          </TabsTrigger>
          <TabsTrigger value="actions" className="flex items-center space-x-2">
            <CheckCircle2 className="h-4 w-4" />
            <span>Actions</span>
          </TabsTrigger>
          <TabsTrigger value="permits" className="flex items-center space-x-2">
            <FileText className="h-4 w-4" />
            <span>Permits</span>
          </TabsTrigger>
          <TabsTrigger value="trainings" className="flex items-center space-x-2">
            <GraduationCap className="h-4 w-4" />
            <span>Training</span>
          </TabsTrigger>
          <TabsTrigger value="inspections" className="flex items-center space-x-2">
            <ClipboardCheck className="h-4 w-4" />
            <span>Inspections</span>
          </TabsTrigger>
        </TabsList>

        <TabsContent value="dashboard" className="space-y-4">
          <div className="grid gap-4 lg:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Key Performance Indicators</CardTitle>
                <CardDescription>Leading and lagging safety metrics</CardDescription>
              </CardHeader>
              <CardContent>
                <KPIDashboard />
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle>Incident Trend</CardTitle>
                <CardDescription>Monthly incident counts (last 12 months)</CardDescription>
              </CardHeader>
              <CardContent className="h-64 flex items-center justify-center text-muted-foreground">
                <BarChart3 className="h-16 w-16" />
                <span className="ml-4">Chart visualization placeholder</span>
              </CardContent>
            </Card>
          </div>
          <div className="grid gap-4 lg:grid-cols-3">
            <Card>
              <CardHeader>
                <CardTitle>Incidents by Category</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {[
                  { category: "Safety", count: 15, color: "bg-blue-600" },
                  { category: "Health", count: 5, color: "bg-green-600" },
                  { category: "Environment", count: 3, color: "bg-yellow-600" },
                  { category: "Security", count: 2, color: "bg-red-600" },
                  { category: "Quality", count: 8, color: "bg-purple-600" },
                ].map((item) => (
                  <div key={item.category} className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <div className={`w-3 h-3 rounded-full ${item.color}`} />
                      <span>{item.category}</span>
                    </div>
                    <span className="font-semibold">{item.count}</span>
                  </div>
                ))}
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle>Top Hazards</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {[
                  { title: "Chemical storage ventilation", risk: "extreme" },
                  { title: "Exposed electrical wiring", risk: "high" },
                  { title: "Forklift traffic area", risk: "high" },
                  { title: "Slippery floors", risk: "medium" },
                ].map((hazard, index) => (
                  <div key={index} className="flex items-center justify-between">
                    <span className="text-sm">{hazard.title}</span>
                    <Badge className={
                      hazard.risk === "extreme" ? "bg-red-100 text-red-800" :
                      hazard.risk === "high" ? "bg-orange-100 text-orange-800" :
                      "bg-yellow-100 text-yellow-800"
                    }>
                      {hazard.risk}
                    </Badge>
                  </div>
                ))}
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle>Upcoming Due</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {[
                  { title: "Fire Safety Training", type: "Training", date: "Jan 20" },
                  { title: "Warehouse Inspection", type: "Inspection", date: "Jan 18" },
                  { title: "Update safety procedures", type: "Action", date: "Jan 18" },
                  { title: "First Aid Training", type: "Training", date: "Jan 22" },
                ].map((item, index) => (
                  <div key={index} className="flex items-center justify-between">
                    <div>
                      <span className="text-sm font-medium">{item.title}</span>
                      <p className="text-xs text-muted-foreground">{item.type}</p>
                    </div>
                    <Badge variant="outline">{item.date}</Badge>
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="incidents">
          <IncidentsTab />
        </TabsContent>

        <TabsContent value="hazards">
          <HazardsTab />
        </TabsContent>

        <TabsContent value="actions">
          <ActionsTab />
        </TabsContent>

        <TabsContent value="permits">
          <PermitsTab />
        </TabsContent>

        <TabsContent value="trainings">
          <TrainingsTab />
        </TabsContent>

        <TabsContent value="inspections">
          <div className="text-center py-12 text-muted-foreground">
            <ClipboardCheck className="h-16 w-16 mx-auto mb-4" />
            <h3 className="text-lg font-semibold">Inspections Module</h3>
            <p>Schedule and conduct HSE inspections with checklists</p>
            <Button className="mt-4">
              <Plus className="h-4 w-4 mr-2" />
              Schedule Inspection
            </Button>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
