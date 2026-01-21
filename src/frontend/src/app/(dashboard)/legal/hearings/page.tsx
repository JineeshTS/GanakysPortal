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
import { Calendar } from "@/components/ui/calendar";
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
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useApi, useToast } from "@/hooks";
import { formatDate, formatTime } from "@/lib/format";
import {
  Plus,
  Search,
  Download,
  Eye,
  Edit,
  Calendar as CalendarIcon,
  Clock,
  AlertTriangle,
  Building2,
  User,
  Trash2,
  Loader2,
  Bell,
  MapPin,
  Gavel,
  FileText,
  UserCheck,
  CalendarDays,
  List,
} from "lucide-react";

// Constants
const HEARING_TYPES = [
  { value: "first_hearing", label: "First Hearing" },
  { value: "admission", label: "Admission" },
  { value: "arguments", label: "Arguments" },
  { value: "evidence", label: "Evidence" },
  { value: "cross_examination", label: "Cross Examination" },
  { value: "final_arguments", label: "Final Arguments" },
  { value: "judgment", label: "Judgment" },
  { value: "interim", label: "Interim Order" },
  { value: "miscellaneous", label: "Miscellaneous" },
];

const HEARING_STATUSES = [
  { value: "scheduled", label: "Scheduled", color: "bg-blue-500" },
  { value: "confirmed", label: "Confirmed", color: "bg-green-500" },
  { value: "adjourned", label: "Adjourned", color: "bg-yellow-500" },
  { value: "completed", label: "Completed", color: "bg-gray-500" },
  { value: "cancelled", label: "Cancelled", color: "bg-red-500" },
];

// TypeScript interfaces
interface Hearing {
  id: string;
  hearing_number: string;
  case_id: string;
  case_number: string;
  case_title: string;
  hearing_type: string;
  scheduled_date: string;
  scheduled_time: string;
  end_time: string;
  court_name: string;
  court_room: string;
  bench: string;
  purpose: string;
  status: string;
  advocate_id: string;
  advocate_name: string;
  advocate_contact: string;
  reminder_sent: boolean;
  notes: string;
  outcome: string;
  next_hearing_date: string;
  created_at: string;
  updated_at: string;
}

// Mock data
const mockHearings: Hearing[] = [
  {
    id: "1",
    hearing_number: "HRG-2025-00042",
    case_id: "1",
    case_number: "CASE-2024-00089",
    case_title: "Tax Assessment Appeal - FY 2021-22",
    hearing_type: "final_arguments",
    scheduled_date: "2025-01-18",
    scheduled_time: "10:30",
    end_time: "12:30",
    court_name: "ITAT Mumbai",
    court_room: "Court Room 3",
    bench: "Justice A.K. Sharma",
    purpose: "Final Arguments on Tax Assessment",
    status: "confirmed",
    advocate_id: "adv-1",
    advocate_name: "Adv. Suresh Kumar",
    advocate_contact: "+91 98765 43210",
    reminder_sent: true,
    notes: "Bring all supporting documents for deductions",
    outcome: "",
    next_hearing_date: "",
    created_at: "2025-01-10T09:00:00",
    updated_at: "2025-01-15T14:00:00",
  },
  {
    id: "2",
    hearing_number: "HRG-2025-00045",
    case_id: "2",
    case_number: "CASE-2025-00001",
    case_title: "XYZ Corp vs ABC Ltd - Contract Dispute",
    hearing_type: "evidence",
    scheduled_date: "2025-01-25",
    scheduled_time: "11:00",
    end_time: "13:00",
    court_name: "Bombay High Court",
    court_room: "Court Room 12",
    bench: "Justice M.N. Patel",
    purpose: "Evidence Submission and Witness Examination",
    status: "scheduled",
    advocate_id: "adv-2",
    advocate_name: "Adv. Rajesh Sharma",
    advocate_contact: "+91 98765 43211",
    reminder_sent: false,
    notes: "Prepare witness list and evidence documents",
    outcome: "",
    next_hearing_date: "",
    created_at: "2025-01-12T10:00:00",
    updated_at: "2025-01-12T10:00:00",
  },
  {
    id: "3",
    hearing_number: "HRG-2025-00038",
    case_id: "3",
    case_number: "CASE-2025-00002",
    case_title: "Employment Dispute - Former Employee",
    hearing_type: "cross_examination",
    scheduled_date: "2025-02-10",
    scheduled_time: "14:00",
    end_time: "16:00",
    court_name: "Industrial Tribunal, Mumbai",
    court_room: "Court Room 5",
    bench: "Presiding Officer R.S. Gupta",
    purpose: "Cross Examination of Company Witnesses",
    status: "scheduled",
    advocate_id: "adv-3",
    advocate_name: "Adv. Priya Mehta",
    advocate_contact: "+91 98765 43212",
    reminder_sent: false,
    notes: "Review HR records and attendance data",
    outcome: "",
    next_hearing_date: "",
    created_at: "2025-01-08T11:00:00",
    updated_at: "2025-01-08T11:00:00",
  },
  {
    id: "4",
    hearing_number: "HRG-2025-00050",
    case_id: "4",
    case_number: "CASE-2024-00056",
    case_title: "IP Infringement - Trademark",
    hearing_type: "interim",
    scheduled_date: "2025-02-05",
    scheduled_time: "10:00",
    end_time: "11:00",
    court_name: "Delhi High Court",
    court_room: "Court Room 8",
    bench: "Justice P.K. Singh",
    purpose: "Interim Injunction Application",
    status: "scheduled",
    advocate_id: "adv-4",
    advocate_name: "Adv. Amit Desai",
    advocate_contact: "+91 98765 43213",
    reminder_sent: false,
    notes: "Prepare arguments for interim relief",
    outcome: "",
    next_hearing_date: "",
    created_at: "2025-01-14T09:00:00",
    updated_at: "2025-01-14T09:00:00",
  },
  {
    id: "5",
    hearing_number: "HRG-2025-00032",
    case_id: "1",
    case_number: "CASE-2024-00089",
    case_title: "Tax Assessment Appeal - FY 2021-22",
    hearing_type: "arguments",
    scheduled_date: "2025-01-05",
    scheduled_time: "11:00",
    end_time: "13:00",
    court_name: "ITAT Mumbai",
    court_room: "Court Room 3",
    bench: "Justice A.K. Sharma",
    purpose: "Preliminary Arguments",
    status: "completed",
    advocate_id: "adv-1",
    advocate_name: "Adv. Suresh Kumar",
    advocate_contact: "+91 98765 43210",
    reminder_sent: true,
    notes: "Arguments presented successfully",
    outcome: "Matter adjourned for final arguments",
    next_hearing_date: "2025-01-18",
    created_at: "2024-12-20T10:00:00",
    updated_at: "2025-01-05T16:00:00",
  },
];

export default function HearingsPage() {
  const api = useApi();
  const { showToast } = useToast();

  // State
  const [hearings, setHearings] = useState<Hearing[]>(mockHearings);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [hearingTypeFilter, setHearingTypeFilter] = useState("all");
  const [statusFilter, setStatusFilter] = useState("all");
  const [activeTab, setActiveTab] = useState("list");
  const [selectedDate, setSelectedDate] = useState<Date | undefined>(new Date());

  // Dialog states
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isViewDialogOpen, setIsViewDialogOpen] = useState(false);
  const [selectedHearing, setSelectedHearing] = useState<Hearing | null>(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [hearingToDelete, setHearingToDelete] = useState<Hearing | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  // Form state
  const [formData, setFormData] = useState({
    case_id: "",
    hearing_type: "",
    scheduled_date: "",
    scheduled_time: "",
    end_time: "",
    court_name: "",
    court_room: "",
    bench: "",
    purpose: "",
    advocate_name: "",
    advocate_contact: "",
    notes: "",
  });
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Fetch hearings from API
  useEffect(() => {
    const fetchHearings = async () => {
      setLoading(true);
      try {
        const response = await api.get("/legal/hearings?limit=100");
        if (response?.data && Array.isArray(response.data)) {
          setHearings(response.data.length > 0 ? response.data : mockHearings);
        }
      } catch (error) {
        console.error("Failed to fetch hearings:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchHearings();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Filter hearings
  const filteredHearings = hearings.filter((h) => {
    const matchesSearch =
      !searchTerm ||
      h.hearing_number.toLowerCase().includes(searchTerm.toLowerCase()) ||
      h.case_number.toLowerCase().includes(searchTerm.toLowerCase()) ||
      h.case_title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      h.advocate_name.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesType = hearingTypeFilter === "all" || h.hearing_type === hearingTypeFilter;
    const matchesStatus = statusFilter === "all" || h.status === statusFilter;

    return matchesSearch && matchesType && matchesStatus;
  });

  // Get hearings for selected date (calendar view)
  const hearingsOnSelectedDate = selectedDate
    ? hearings.filter(
        (h) => new Date(h.scheduled_date).toDateString() === selectedDate.toDateString()
      )
    : [];

  // Get dates with hearings for calendar highlighting
  const datesWithHearings = hearings
    .filter((h) => h.status !== "cancelled" && h.status !== "completed")
    .map((h) => new Date(h.scheduled_date));

  // Helpers
  const getStatusBadge = (status: string) => {
    const statusConfig = HEARING_STATUSES.find((s) => s.value === status);
    return (
      <Badge className={`${statusConfig?.color || "bg-gray-500"} text-white`}>
        {statusConfig?.label || status}
      </Badge>
    );
  };

  const getHearingTypeBadge = (type: string) => {
    const typeConfig = HEARING_TYPES.find((t) => t.value === type);
    return (
      <Badge variant="outline" className="capitalize">
        {typeConfig?.label || type.replace("_", " ")}
      </Badge>
    );
  };

  const isUpcoming = (date: string) => {
    const hearingDate = new Date(date);
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const diffDays = Math.ceil((hearingDate.getTime() - today.getTime()) / (1000 * 60 * 60 * 24));
    return diffDays >= 0 && diffDays <= 7;
  };

  const isToday = (date: string) => {
    const hearingDate = new Date(date);
    const today = new Date();
    return hearingDate.toDateString() === today.toDateString();
  };

  // Handlers
  const handleViewHearing = (hearing: Hearing) => {
    setSelectedHearing(hearing);
    setIsViewDialogOpen(true);
  };

  const handleDeleteClick = (hearing: Hearing) => {
    setHearingToDelete(hearing);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!hearingToDelete) return;
    setIsDeleting(true);

    try {
      await api.delete(`/legal/hearings/${hearingToDelete.id}`);
      setHearings(hearings.filter((h) => h.id !== hearingToDelete.id));
      setDeleteDialogOpen(false);
      setHearingToDelete(null);
      showToast("success", "Hearing deleted successfully");
    } catch (error) {
      console.error("Failed to delete hearing:", error);
      showToast("error", "Failed to delete hearing");
    } finally {
      setIsDeleting(false);
    }
  };

  const handleCreateHearing = async () => {
    if (!formData.case_id || !formData.hearing_type || !formData.scheduled_date) {
      showToast("error", "Please fill in required fields");
      return;
    }

    setIsSubmitting(true);
    try {
      const response = await api.post("/legal/hearings", formData);

      if (response) {
        setHearings([response as Hearing, ...hearings]);
        showToast("success", "Hearing scheduled successfully");
        setIsCreateDialogOpen(false);
        setFormData({
          case_id: "",
          hearing_type: "",
          scheduled_date: "",
          scheduled_time: "",
          end_time: "",
          court_name: "",
          court_room: "",
          bench: "",
          purpose: "",
          advocate_name: "",
          advocate_contact: "",
          notes: "",
        });
      }
    } catch (error) {
      console.error("Failed to create hearing:", error);
      showToast("error", "Failed to schedule hearing");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleSendReminder = async (hearing: Hearing) => {
    try {
      await api.post(`/legal/hearings/${hearing.id}/remind`, {});
      showToast("success", "Reminder sent successfully");
      setHearings(
        hearings.map((h) => (h.id === hearing.id ? { ...h, reminder_sent: true } : h))
      );
    } catch (error) {
      console.error("Failed to send reminder:", error);
      showToast("error", "Failed to send reminder");
    }
  };

  // Stats
  const stats = {
    total: hearings.length,
    upcoming: hearings.filter((h) => isUpcoming(h.scheduled_date) && h.status === "scheduled").length,
    today: hearings.filter((h) => isToday(h.scheduled_date) && h.status !== "cancelled").length,
    pendingReminders: hearings.filter(
      (h) => isUpcoming(h.scheduled_date) && !h.reminder_sent && h.status === "scheduled"
    ).length,
  };

  return (
    <div className="flex-1 space-y-4 p-4 md:p-8 pt-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Hearing Schedule</h2>
          <p className="text-muted-foreground">
            Manage court hearings and appearances
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
                Schedule Hearing
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl">
              <DialogHeader>
                <DialogTitle>Schedule New Hearing</DialogTitle>
                <DialogDescription>Add a new court hearing</DialogDescription>
              </DialogHeader>
              <div className="grid gap-4 py-4 max-h-[60vh] overflow-y-auto">
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>Case *</Label>
                    <Select
                      value={formData.case_id}
                      onValueChange={(value) => setFormData({ ...formData, case_id: value })}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select case" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="1">CASE-2024-00089 - Tax Appeal</SelectItem>
                        <SelectItem value="2">CASE-2025-00001 - Contract Dispute</SelectItem>
                        <SelectItem value="3">CASE-2025-00002 - Employment Dispute</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label>Hearing Type *</Label>
                    <Select
                      value={formData.hearing_type}
                      onValueChange={(value) => setFormData({ ...formData, hearing_type: value })}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select type" />
                      </SelectTrigger>
                      <SelectContent>
                        {HEARING_TYPES.map((type) => (
                          <SelectItem key={type.value} value={type.value}>
                            {type.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <div className="grid grid-cols-3 gap-4">
                  <div className="space-y-2">
                    <Label>Date *</Label>
                    <Input
                      type="date"
                      value={formData.scheduled_date}
                      onChange={(e) => setFormData({ ...formData, scheduled_date: e.target.value })}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Start Time</Label>
                    <Input
                      type="time"
                      value={formData.scheduled_time}
                      onChange={(e) => setFormData({ ...formData, scheduled_time: e.target.value })}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>End Time</Label>
                    <Input
                      type="time"
                      value={formData.end_time}
                      onChange={(e) => setFormData({ ...formData, end_time: e.target.value })}
                    />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>Court Name</Label>
                    <Input
                      placeholder="Enter court name"
                      value={formData.court_name}
                      onChange={(e) => setFormData({ ...formData, court_name: e.target.value })}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Court Room</Label>
                    <Input
                      placeholder="Enter court room"
                      value={formData.court_room}
                      onChange={(e) => setFormData({ ...formData, court_room: e.target.value })}
                    />
                  </div>
                </div>
                <div className="space-y-2">
                  <Label>Bench / Judge</Label>
                  <Input
                    placeholder="Enter bench or judge name"
                    value={formData.bench}
                    onChange={(e) => setFormData({ ...formData, bench: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <Label>Purpose</Label>
                  <Input
                    placeholder="Purpose of hearing"
                    value={formData.purpose}
                    onChange={(e) => setFormData({ ...formData, purpose: e.target.value })}
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>Advocate Name</Label>
                    <Input
                      placeholder="Assigned advocate"
                      value={formData.advocate_name}
                      onChange={(e) => setFormData({ ...formData, advocate_name: e.target.value })}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Advocate Contact</Label>
                    <Input
                      placeholder="Contact number"
                      value={formData.advocate_contact}
                      onChange={(e) => setFormData({ ...formData, advocate_contact: e.target.value })}
                    />
                  </div>
                </div>
                <div className="space-y-2">
                  <Label>Notes</Label>
                  <Textarea
                    placeholder="Additional notes or instructions"
                    value={formData.notes}
                    onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                  />
                </div>
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={() => setIsCreateDialogOpen(false)}>
                  Cancel
                </Button>
                <Button onClick={handleCreateHearing} disabled={isSubmitting}>
                  {isSubmitting ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Scheduling...
                    </>
                  ) : (
                    "Schedule Hearing"
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
            <CardTitle className="text-sm font-medium">Total Hearings</CardTitle>
            <CalendarIcon className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.total}</div>
            <p className="text-xs text-muted-foreground">All scheduled</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Today</CardTitle>
            <Clock className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{stats.today}</div>
            <p className="text-xs text-muted-foreground">Hearings today</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Upcoming</CardTitle>
            <CalendarDays className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.upcoming}</div>
            <p className="text-xs text-muted-foreground">Next 7 days</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Pending Reminders</CardTitle>
            <Bell className="h-4 w-4 text-orange-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-600">{stats.pendingReminders}</div>
            <p className="text-xs text-muted-foreground">Need to send</p>
          </CardContent>
        </Card>
      </div>

      {/* View Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="list" className="gap-2">
            <List className="h-4 w-4" />
            List View
          </TabsTrigger>
          <TabsTrigger value="calendar" className="gap-2">
            <CalendarDays className="h-4 w-4" />
            Calendar View
          </TabsTrigger>
        </TabsList>

        {/* List View */}
        <TabsContent value="list" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Hearing List</CardTitle>
              <CardDescription>View and manage all hearings</CardDescription>
            </CardHeader>
            <CardContent>
              {/* Filters */}
              <div className="flex items-center gap-4 mb-4">
                <div className="relative flex-1">
                  <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                  <Input
                    placeholder="Search hearings..."
                    className="pl-8"
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                  />
                </div>
                <Select value={hearingTypeFilter} onValueChange={setHearingTypeFilter}>
                  <SelectTrigger className="w-[150px]">
                    <SelectValue placeholder="Type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Types</SelectItem>
                    {HEARING_TYPES.map((type) => (
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
                    {HEARING_STATUSES.map((status) => (
                      <SelectItem key={status.value} value={status.value}>
                        {status.label}
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
              ) : filteredHearings.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  No hearings found. Click "Schedule Hearing" to add one.
                </div>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Case</TableHead>
                      <TableHead>Type</TableHead>
                      <TableHead>Date & Time</TableHead>
                      <TableHead>Court</TableHead>
                      <TableHead>Advocate</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Reminder</TableHead>
                      <TableHead>Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {filteredHearings.map((hearing) => (
                      <TableRow key={hearing.id}>
                        <TableCell>
                          <div>
                            <p className="font-medium">{hearing.case_number}</p>
                            <p className="text-xs text-muted-foreground truncate max-w-[200px]">
                              {hearing.case_title}
                            </p>
                          </div>
                        </TableCell>
                        <TableCell>{getHearingTypeBadge(hearing.hearing_type)}</TableCell>
                        <TableCell>
                          <div className="flex items-center gap-2">
                            {isToday(hearing.scheduled_date) && (
                              <Badge className="bg-green-500 text-white text-xs">Today</Badge>
                            )}
                            <div>
                              <p
                                className={
                                  isUpcoming(hearing.scheduled_date)
                                    ? "font-medium text-blue-600"
                                    : ""
                                }
                              >
                                {formatDate(hearing.scheduled_date)}
                              </p>
                              <p className="text-xs text-muted-foreground">
                                {hearing.scheduled_time} - {hearing.end_time}
                              </p>
                            </div>
                          </div>
                        </TableCell>
                        <TableCell>
                          <div>
                            <p className="text-sm">{hearing.court_name}</p>
                            <p className="text-xs text-muted-foreground">{hearing.court_room}</p>
                          </div>
                        </TableCell>
                        <TableCell>
                          <div>
                            <p className="text-sm">{hearing.advocate_name}</p>
                            <p className="text-xs text-muted-foreground">{hearing.advocate_contact}</p>
                          </div>
                        </TableCell>
                        <TableCell>{getStatusBadge(hearing.status)}</TableCell>
                        <TableCell>
                          {hearing.reminder_sent ? (
                            <Badge variant="outline" className="text-green-600 border-green-300">
                              Sent
                            </Badge>
                          ) : (
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => handleSendReminder(hearing)}
                              disabled={hearing.status === "cancelled" || hearing.status === "completed"}
                            >
                              <Bell className="h-3 w-3 mr-1" />
                              Send
                            </Button>
                          )}
                        </TableCell>
                        <TableCell>
                          <div className="flex gap-2">
                            <Button
                              variant="ghost"
                              size="icon"
                              onClick={() => handleViewHearing(hearing)}
                            >
                              <Eye className="h-4 w-4" />
                            </Button>
                            <Button variant="ghost" size="icon">
                              <Edit className="h-4 w-4" />
                            </Button>
                            {hearing.status === "cancelled" && (
                              <Button
                                variant="ghost"
                                size="icon"
                                className="text-red-600 hover:text-red-700 hover:bg-red-50"
                                onClick={() => handleDeleteClick(hearing)}
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
        </TabsContent>

        {/* Calendar View */}
        <TabsContent value="calendar" className="space-y-4">
          <div className="grid md:grid-cols-[350px_1fr] gap-4">
            {/* Calendar */}
            <Card>
              <CardHeader>
                <CardTitle className="text-sm font-medium">Select Date</CardTitle>
              </CardHeader>
              <CardContent>
                <Calendar
                  mode="single"
                  selected={selectedDate}
                  onSelect={setSelectedDate}
                  modifiers={{
                    hearing: datesWithHearings,
                  }}
                  modifiersStyles={{
                    hearing: {
                      fontWeight: "bold",
                      backgroundColor: "hsl(var(--primary) / 0.1)",
                      borderRadius: "50%",
                    },
                  }}
                  className="rounded-md border"
                />
              </CardContent>
            </Card>

            {/* Hearings for selected date */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <CalendarIcon className="h-5 w-5" />
                  Hearings on {selectedDate ? formatDate(selectedDate.toISOString()) : "Selected Date"}
                </CardTitle>
                <CardDescription>
                  {hearingsOnSelectedDate.length} hearing(s) scheduled
                </CardDescription>
              </CardHeader>
              <CardContent>
                {hearingsOnSelectedDate.length === 0 ? (
                  <div className="text-center py-8 text-muted-foreground">
                    No hearings scheduled for this date
                  </div>
                ) : (
                  <div className="space-y-4">
                    {hearingsOnSelectedDate.map((hearing) => (
                      <Card key={hearing.id} className="bg-muted/50">
                        <CardContent className="p-4">
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <div className="flex items-center gap-2 mb-2">
                                <p className="font-medium">{hearing.case_number}</p>
                                {getStatusBadge(hearing.status)}
                              </div>
                              <p className="text-sm text-muted-foreground mb-2">
                                {hearing.case_title}
                              </p>
                              <div className="grid grid-cols-2 gap-2 text-sm">
                                <div className="flex items-center gap-1">
                                  <Clock className="h-3 w-3 text-muted-foreground" />
                                  {hearing.scheduled_time} - {hearing.end_time}
                                </div>
                                <div className="flex items-center gap-1">
                                  <Building2 className="h-3 w-3 text-muted-foreground" />
                                  {hearing.court_room}
                                </div>
                                <div className="flex items-center gap-1">
                                  <MapPin className="h-3 w-3 text-muted-foreground" />
                                  {hearing.court_name}
                                </div>
                                <div className="flex items-center gap-1">
                                  <UserCheck className="h-3 w-3 text-muted-foreground" />
                                  {hearing.advocate_name}
                                </div>
                              </div>
                              <p className="text-sm mt-2">
                                <span className="font-medium">Purpose:</span> {hearing.purpose}
                              </p>
                            </div>
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => handleViewHearing(hearing)}
                            >
                              <Eye className="h-4 w-4" />
                            </Button>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>

      {/* View Hearing Dialog */}
      <Dialog open={isViewDialogOpen} onOpenChange={setIsViewDialogOpen}>
        <DialogContent className="max-w-3xl">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Gavel className="h-5 w-5" />
              {selectedHearing?.hearing_number}
            </DialogTitle>
            <DialogDescription>
              {selectedHearing?.case_number} - {selectedHearing?.case_title}
            </DialogDescription>
          </DialogHeader>
          {selectedHearing && (
            <div className="grid gap-6 py-4">
              {/* Status and Type */}
              <div className="flex items-center gap-4">
                {getStatusBadge(selectedHearing.status)}
                {getHearingTypeBadge(selectedHearing.hearing_type)}
                {selectedHearing.reminder_sent && (
                  <Badge variant="outline" className="text-green-600 border-green-300">
                    <Bell className="h-3 w-3 mr-1" />
                    Reminder Sent
                  </Badge>
                )}
              </div>

              {/* Schedule */}
              <div className="grid grid-cols-3 gap-4">
                <div className="space-y-1">
                  <Label className="text-xs text-muted-foreground">Date</Label>
                  <div className="flex items-center gap-2">
                    <CalendarIcon className="h-4 w-4 text-muted-foreground" />
                    <span className="font-medium">{formatDate(selectedHearing.scheduled_date)}</span>
                  </div>
                </div>
                <div className="space-y-1">
                  <Label className="text-xs text-muted-foreground">Time</Label>
                  <div className="flex items-center gap-2">
                    <Clock className="h-4 w-4 text-muted-foreground" />
                    <span>{selectedHearing.scheduled_time} - {selectedHearing.end_time}</span>
                  </div>
                </div>
                <div className="space-y-1">
                  <Label className="text-xs text-muted-foreground">Purpose</Label>
                  <span>{selectedHearing.purpose}</span>
                </div>
              </div>

              {/* Court Details */}
              <div className="grid grid-cols-3 gap-4">
                <div className="space-y-1">
                  <Label className="text-xs text-muted-foreground">Court</Label>
                  <div className="flex items-center gap-2">
                    <Building2 className="h-4 w-4 text-muted-foreground" />
                    <span>{selectedHearing.court_name}</span>
                  </div>
                </div>
                <div className="space-y-1">
                  <Label className="text-xs text-muted-foreground">Court Room</Label>
                  <div className="flex items-center gap-2">
                    <MapPin className="h-4 w-4 text-muted-foreground" />
                    <span>{selectedHearing.court_room}</span>
                  </div>
                </div>
                <div className="space-y-1">
                  <Label className="text-xs text-muted-foreground">Bench</Label>
                  <span>{selectedHearing.bench}</span>
                </div>
              </div>

              {/* Advocate */}
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1">
                  <Label className="text-xs text-muted-foreground">Assigned Advocate</Label>
                  <div className="flex items-center gap-2">
                    <UserCheck className="h-4 w-4 text-muted-foreground" />
                    <span>{selectedHearing.advocate_name}</span>
                  </div>
                </div>
                <div className="space-y-1">
                  <Label className="text-xs text-muted-foreground">Contact</Label>
                  <span>{selectedHearing.advocate_contact}</span>
                </div>
              </div>

              {/* Notes */}
              {selectedHearing.notes && (
                <div className="space-y-1">
                  <Label className="text-xs text-muted-foreground">Notes</Label>
                  <div className="p-3 bg-muted/50 rounded-md text-sm">
                    {selectedHearing.notes}
                  </div>
                </div>
              )}

              {/* Outcome (for completed hearings) */}
              {selectedHearing.status === "completed" && selectedHearing.outcome && (
                <div className="space-y-1">
                  <Label className="text-xs text-muted-foreground">Outcome</Label>
                  <div className="p-3 bg-green-50 border border-green-200 rounded-md text-sm">
                    {selectedHearing.outcome}
                  </div>
                </div>
              )}

              {/* Next Hearing */}
              {selectedHearing.next_hearing_date && (
                <div className="space-y-1">
                  <Label className="text-xs text-muted-foreground">Next Hearing</Label>
                  <div className="flex items-center gap-2">
                    <CalendarIcon className="h-4 w-4 text-blue-500" />
                    <span className="text-blue-600 font-medium">
                      {formatDate(selectedHearing.next_hearing_date)}
                    </span>
                  </div>
                </div>
              )}
            </div>
          )}
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsViewDialogOpen(false)}>
              Close
            </Button>
            {selectedHearing && !selectedHearing.reminder_sent && selectedHearing.status === "scheduled" && (
              <Button variant="outline" onClick={() => handleSendReminder(selectedHearing)}>
                <Bell className="mr-2 h-4 w-4" />
                Send Reminder
              </Button>
            )}
            <Button>
              <Edit className="mr-2 h-4 w-4" />
              Edit Hearing
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
              Delete Hearing
            </AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete <strong>{hearingToDelete?.hearing_number}</strong>?
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
