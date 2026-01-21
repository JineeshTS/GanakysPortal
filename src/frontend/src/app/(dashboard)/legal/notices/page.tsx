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
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useApi, useToast } from "@/hooks";
import { formatDate } from "@/lib/format";
import {
  Plus,
  Search,
  Download,
  Eye,
  Edit,
  Bell,
  Calendar,
  AlertTriangle,
  Mail,
  Send,
  Inbox,
  Clock,
  Trash2,
  Loader2,
  FileText,
  CheckCircle2,
  XCircle,
  ArrowUpRight,
  ArrowDownLeft,
  MessageSquare,
  User,
  Building2,
} from "lucide-react";

// Constants
const NOTICE_TYPES = [
  { value: "legal_demand", label: "Legal Demand Notice" },
  { value: "cease_desist", label: "Cease & Desist" },
  { value: "contract_termination", label: "Contract Termination" },
  { value: "breach_notice", label: "Breach Notice" },
  { value: "compliance", label: "Compliance Notice" },
  { value: "show_cause", label: "Show Cause Notice" },
  { value: "eviction", label: "Eviction Notice" },
  { value: "ip_infringement", label: "IP Infringement Notice" },
  { value: "employment", label: "Employment Notice" },
  { value: "general", label: "General Notice" },
];

const NOTICE_STATUSES = [
  { value: "draft", label: "Draft", color: "bg-gray-500" },
  { value: "pending_review", label: "Pending Review", color: "bg-yellow-500" },
  { value: "sent", label: "Sent", color: "bg-blue-500" },
  { value: "delivered", label: "Delivered", color: "bg-indigo-500" },
  { value: "response_pending", label: "Response Pending", color: "bg-orange-500" },
  { value: "response_received", label: "Response Received", color: "bg-purple-500" },
  { value: "resolved", label: "Resolved", color: "bg-green-500" },
  { value: "escalated", label: "Escalated", color: "bg-red-500" },
  { value: "closed", label: "Closed", color: "bg-gray-700" },
];

const DIRECTIONS = [
  { value: "incoming", label: "Incoming", icon: ArrowDownLeft },
  { value: "outgoing", label: "Outgoing", icon: ArrowUpRight },
];

// TypeScript interfaces
interface LegalNotice {
  id: string;
  notice_number: string;
  title: string;
  notice_type: string;
  direction: "incoming" | "outgoing";
  status: string;
  sender_name: string;
  sender_address: string;
  sender_email: string;
  recipient_name: string;
  recipient_address: string;
  recipient_email: string;
  subject: string;
  content_summary: string;
  issue_date: string;
  received_date: string;
  response_due_date: string;
  response_date: string;
  response_summary: string;
  related_case_id: string;
  related_case_number: string;
  priority: string;
  document_url: string;
  created_at: string;
  updated_at: string;
}

// Mock data
const mockNotices: LegalNotice[] = [
  {
    id: "1",
    notice_number: "NTC-2025-00012",
    title: "Payment Demand Notice - Outstanding Invoice",
    notice_type: "legal_demand",
    direction: "outgoing",
    status: "response_pending",
    sender_name: "ABC Ltd (Our Company)",
    sender_address: "123 Business Park, Mumbai 400001",
    sender_email: "legal@abcltd.com",
    recipient_name: "XYZ Trading Co",
    recipient_address: "456 Commercial Street, Pune 411001",
    recipient_email: "accounts@xyztrading.com",
    subject: "Notice for Outstanding Payment of Rs. 25,00,000",
    content_summary: "Demand notice for outstanding payment against invoice INV-2024-1234 dated 15-Oct-2024. Payment was due within 30 days as per agreement terms.",
    issue_date: "2025-01-05",
    received_date: "",
    response_due_date: "2025-01-20",
    response_date: "",
    response_summary: "",
    related_case_id: "",
    related_case_number: "",
    priority: "high",
    document_url: "/documents/ntc-2025-00012.pdf",
    created_at: "2025-01-05T10:00:00",
    updated_at: "2025-01-05T10:00:00",
  },
  {
    id: "2",
    notice_number: "NTC-2025-00008",
    title: "Income Tax Assessment Notice",
    notice_type: "compliance",
    direction: "incoming",
    status: "response_received",
    sender_name: "Income Tax Department",
    sender_address: "Income Tax Office, Bandra-Kurla Complex, Mumbai",
    sender_email: "notices@incometax.gov.in",
    recipient_name: "ABC Ltd",
    recipient_address: "123 Business Park, Mumbai 400001",
    recipient_email: "legal@abcltd.com",
    subject: "Assessment Notice for AY 2023-24",
    content_summary: "Notice for scrutiny assessment under section 143(2) of Income Tax Act for Assessment Year 2023-24.",
    issue_date: "2024-12-20",
    received_date: "2024-12-22",
    response_due_date: "2025-01-15",
    response_date: "2025-01-10",
    response_summary: "Detailed response submitted with all supporting documents and computation sheets.",
    related_case_id: "3",
    related_case_number: "CASE-2024-00089",
    priority: "critical",
    document_url: "/documents/ntc-2025-00008.pdf",
    created_at: "2024-12-22T11:00:00",
    updated_at: "2025-01-10T16:00:00",
  },
  {
    id: "3",
    notice_number: "NTC-2025-00015",
    title: "Contract Breach Notice",
    notice_type: "breach_notice",
    direction: "incoming",
    status: "sent",
    sender_name: "XYZ Corporation Pvt Ltd",
    sender_address: "789 Tech Park, Bengaluru 560001",
    sender_email: "legal@xyzcorp.com",
    recipient_name: "ABC Ltd",
    recipient_address: "123 Business Park, Mumbai 400001",
    recipient_email: "legal@abcltd.com",
    subject: "Notice of Breach - Service Level Agreement",
    content_summary: "Notice alleging breach of SLA terms regarding system uptime requirements under IT Services Agreement dated 01-Apr-2024.",
    issue_date: "2025-01-12",
    received_date: "2025-01-13",
    response_due_date: "2025-01-28",
    response_date: "",
    response_summary: "",
    related_case_id: "1",
    related_case_number: "CASE-2025-00001",
    priority: "high",
    document_url: "/documents/ntc-2025-00015.pdf",
    created_at: "2025-01-13T09:00:00",
    updated_at: "2025-01-13T09:00:00",
  },
  {
    id: "4",
    notice_number: "NTC-2025-00003",
    title: "Cease and Desist - Trademark Infringement",
    notice_type: "cease_desist",
    direction: "outgoing",
    status: "resolved",
    sender_name: "ABC Ltd (Our Company)",
    sender_address: "123 Business Park, Mumbai 400001",
    sender_email: "legal@abcltd.com",
    recipient_name: "Counterfeit Goods Seller",
    recipient_address: "321 Market Area, Delhi 110001",
    recipient_email: "contact@fakeshop.com",
    subject: "Cease and Desist - Unauthorized Use of Trademark",
    content_summary: "Notice to cease unauthorized use of our registered trademark on counterfeit products being sold through online platforms.",
    issue_date: "2024-12-01",
    received_date: "",
    response_due_date: "2024-12-15",
    response_date: "2024-12-10",
    response_summary: "Recipient agreed to stop selling counterfeit products and remove all listings.",
    related_case_id: "",
    related_case_number: "",
    priority: "medium",
    document_url: "/documents/ntc-2025-00003.pdf",
    created_at: "2024-12-01T14:00:00",
    updated_at: "2024-12-12T10:00:00",
  },
  {
    id: "5",
    notice_number: "NTC-2025-00018",
    title: "Show Cause Notice - Labour Compliance",
    notice_type: "show_cause",
    direction: "incoming",
    status: "draft",
    sender_name: "Labour Commissioner Office",
    sender_address: "Labour Commission Building, Mumbai",
    sender_email: "labour.mumbai@gov.in",
    recipient_name: "ABC Ltd",
    recipient_address: "123 Business Park, Mumbai 400001",
    recipient_email: "hr@abcltd.com",
    subject: "Show Cause Notice - PF Compliance",
    content_summary: "Show cause notice regarding alleged delay in PF deposits for employees during Q3 2024.",
    issue_date: "2025-01-10",
    received_date: "2025-01-11",
    response_due_date: "2025-01-25",
    response_date: "",
    response_summary: "",
    related_case_id: "",
    related_case_number: "",
    priority: "high",
    document_url: "/documents/ntc-2025-00018.pdf",
    created_at: "2025-01-11T15:00:00",
    updated_at: "2025-01-11T15:00:00",
  },
];

export default function NoticesPage() {
  const api = useApi();
  const { showToast } = useToast();

  // State
  const [notices, setNotices] = useState<LegalNotice[]>(mockNotices);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [noticeTypeFilter, setNoticeTypeFilter] = useState("all");
  const [statusFilter, setStatusFilter] = useState("all");
  const [directionFilter, setDirectionFilter] = useState("all");
  const [activeTab, setActiveTab] = useState("all");

  // Dialog states
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isViewDialogOpen, setIsViewDialogOpen] = useState(false);
  const [isResponseDialogOpen, setIsResponseDialogOpen] = useState(false);
  const [selectedNotice, setSelectedNotice] = useState<LegalNotice | null>(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [noticeToDelete, setNoticeToDelete] = useState<LegalNotice | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  // Form state
  const [formData, setFormData] = useState({
    title: "",
    notice_type: "",
    direction: "outgoing" as "incoming" | "outgoing",
    recipient_name: "",
    recipient_address: "",
    recipient_email: "",
    subject: "",
    content_summary: "",
    response_due_date: "",
    priority: "medium",
  });
  const [responseData, setResponseData] = useState({
    response_date: "",
    response_summary: "",
  });
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Fetch notices from API
  useEffect(() => {
    const fetchNotices = async () => {
      setLoading(true);
      try {
        const response = await api.get("/legal/notices?limit=100");
        if (response?.data && Array.isArray(response.data)) {
          setNotices(response.data.length > 0 ? response.data : mockNotices);
        }
      } catch (error) {
        console.error("Failed to fetch notices:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchNotices();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Filter notices
  const filteredNotices = notices.filter((n) => {
    const matchesSearch =
      !searchTerm ||
      n.notice_number.toLowerCase().includes(searchTerm.toLowerCase()) ||
      n.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      n.sender_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      n.recipient_name.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesType = noticeTypeFilter === "all" || n.notice_type === noticeTypeFilter;
    const matchesStatus = statusFilter === "all" || n.status === statusFilter;
    const matchesDirection = directionFilter === "all" || n.direction === directionFilter;
    const matchesTab =
      activeTab === "all" ||
      (activeTab === "incoming" && n.direction === "incoming") ||
      (activeTab === "outgoing" && n.direction === "outgoing") ||
      (activeTab === "pending" && n.status === "response_pending");

    return matchesSearch && matchesType && matchesStatus && matchesDirection && matchesTab;
  });

  // Helpers
  const getStatusBadge = (status: string) => {
    const statusConfig = NOTICE_STATUSES.find((s) => s.value === status);
    return (
      <Badge className={`${statusConfig?.color || "bg-gray-500"} text-white`}>
        {statusConfig?.label || status}
      </Badge>
    );
  };

  const getDirectionBadge = (direction: "incoming" | "outgoing") => {
    const Icon = direction === "incoming" ? ArrowDownLeft : ArrowUpRight;
    const color = direction === "incoming" ? "text-blue-600 bg-blue-50 border-blue-200" : "text-green-600 bg-green-50 border-green-200";
    return (
      <Badge variant="outline" className={`${color} capitalize`}>
        <Icon className="h-3 w-3 mr-1" />
        {direction}
      </Badge>
    );
  };

  const getPriorityBadge = (priority: string) => {
    const colors: Record<string, string> = {
      critical: "bg-red-600",
      high: "bg-orange-500",
      medium: "bg-yellow-500",
      low: "bg-green-500",
    };
    return (
      <Badge className={`${colors[priority] || "bg-gray-500"} text-white capitalize`}>
        {priority}
      </Badge>
    );
  };

  const isOverdue = (dueDate: string, status: string) => {
    if (!dueDate || status === "resolved" || status === "closed" || status === "response_received") {
      return false;
    }
    const due = new Date(dueDate);
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    return due < today;
  };

  const isDueSoon = (dueDate: string, status: string) => {
    if (!dueDate || status === "resolved" || status === "closed" || status === "response_received") {
      return false;
    }
    const due = new Date(dueDate);
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const diffDays = Math.ceil((due.getTime() - today.getTime()) / (1000 * 60 * 60 * 24));
    return diffDays >= 0 && diffDays <= 5;
  };

  // Handlers
  const handleViewNotice = (notice: LegalNotice) => {
    setSelectedNotice(notice);
    setIsViewDialogOpen(true);
  };

  const handleAddResponse = (notice: LegalNotice) => {
    setSelectedNotice(notice);
    setResponseData({
      response_date: new Date().toISOString().split("T")[0],
      response_summary: "",
    });
    setIsResponseDialogOpen(true);
  };

  const handleDeleteClick = (notice: LegalNotice) => {
    setNoticeToDelete(notice);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!noticeToDelete) return;
    setIsDeleting(true);

    try {
      await api.delete(`/legal/notices/${noticeToDelete.id}`);
      setNotices(notices.filter((n) => n.id !== noticeToDelete.id));
      setDeleteDialogOpen(false);
      setNoticeToDelete(null);
      showToast("success", "Notice deleted successfully");
    } catch (error) {
      console.error("Failed to delete notice:", error);
      showToast("error", "Failed to delete notice");
    } finally {
      setIsDeleting(false);
    }
  };

  const handleCreateNotice = async () => {
    if (!formData.title || !formData.notice_type || !formData.recipient_name) {
      showToast("error", "Please fill in required fields");
      return;
    }

    setIsSubmitting(true);
    try {
      const response = await api.post("/legal/notices", {
        ...formData,
        issue_date: new Date().toISOString().split("T")[0],
      });

      if (response) {
        setNotices([response as LegalNotice, ...notices]);
        showToast("success", "Notice created successfully");
        setIsCreateDialogOpen(false);
        setFormData({
          title: "",
          notice_type: "",
          direction: "outgoing",
          recipient_name: "",
          recipient_address: "",
          recipient_email: "",
          subject: "",
          content_summary: "",
          response_due_date: "",
          priority: "medium",
        });
      }
    } catch (error) {
      console.error("Failed to create notice:", error);
      showToast("error", "Failed to create notice");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleSubmitResponse = async () => {
    if (!selectedNotice || !responseData.response_summary) {
      showToast("error", "Please provide response details");
      return;
    }

    setIsSubmitting(true);
    try {
      const response = await api.patch(`/legal/notices/${selectedNotice.id}`, {
        status: "response_received",
        response_date: responseData.response_date,
        response_summary: responseData.response_summary,
      });

      if (response) {
        setNotices(
          notices.map((n) =>
            n.id === selectedNotice.id
              ? {
                  ...n,
                  status: "response_received",
                  response_date: responseData.response_date,
                  response_summary: responseData.response_summary,
                }
              : n
          )
        );
        showToast("success", "Response recorded successfully");
        setIsResponseDialogOpen(false);
      }
    } catch (error) {
      console.error("Failed to record response:", error);
      showToast("error", "Failed to record response");
    } finally {
      setIsSubmitting(false);
    }
  };

  // Stats
  const stats = {
    total: notices.length,
    incoming: notices.filter((n) => n.direction === "incoming").length,
    outgoing: notices.filter((n) => n.direction === "outgoing").length,
    pendingResponse: notices.filter((n) => n.status === "response_pending").length,
    overdue: notices.filter((n) => isOverdue(n.response_due_date, n.status)).length,
  };

  return (
    <div className="flex-1 space-y-4 p-4 md:p-8 pt-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Legal Notices</h2>
          <p className="text-muted-foreground">
            Track sent and received legal notices
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
                New Notice
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl">
              <DialogHeader>
                <DialogTitle>Create New Notice</DialogTitle>
                <DialogDescription>Create and send a legal notice</DialogDescription>
              </DialogHeader>
              <div className="grid gap-4 py-4 max-h-[60vh] overflow-y-auto">
                <div className="space-y-2">
                  <Label>Notice Title *</Label>
                  <Input
                    placeholder="Enter notice title"
                    value={formData.title}
                    onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  />
                </div>
                <div className="grid grid-cols-3 gap-4">
                  <div className="space-y-2">
                    <Label>Notice Type *</Label>
                    <Select
                      value={formData.notice_type}
                      onValueChange={(value) => setFormData({ ...formData, notice_type: value })}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select type" />
                      </SelectTrigger>
                      <SelectContent>
                        {NOTICE_TYPES.map((type) => (
                          <SelectItem key={type.value} value={type.value}>
                            {type.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label>Direction</Label>
                    <Select
                      value={formData.direction}
                      onValueChange={(value) =>
                        setFormData({ ...formData, direction: value as "incoming" | "outgoing" })
                      }
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select direction" />
                      </SelectTrigger>
                      <SelectContent>
                        {DIRECTIONS.map((d) => (
                          <SelectItem key={d.value} value={d.value}>
                            {d.label}
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
                        <SelectItem value="critical">Critical</SelectItem>
                        <SelectItem value="high">High</SelectItem>
                        <SelectItem value="medium">Medium</SelectItem>
                        <SelectItem value="low">Low</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>Recipient Name *</Label>
                    <Input
                      placeholder="Enter recipient name"
                      value={formData.recipient_name}
                      onChange={(e) => setFormData({ ...formData, recipient_name: e.target.value })}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Recipient Email</Label>
                    <Input
                      type="email"
                      placeholder="Enter email"
                      value={formData.recipient_email}
                      onChange={(e) => setFormData({ ...formData, recipient_email: e.target.value })}
                    />
                  </div>
                </div>
                <div className="space-y-2">
                  <Label>Recipient Address</Label>
                  <Textarea
                    placeholder="Enter recipient address"
                    value={formData.recipient_address}
                    onChange={(e) => setFormData({ ...formData, recipient_address: e.target.value })}
                    rows={2}
                  />
                </div>
                <div className="space-y-2">
                  <Label>Subject</Label>
                  <Input
                    placeholder="Notice subject"
                    value={formData.subject}
                    onChange={(e) => setFormData({ ...formData, subject: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <Label>Response Due Date</Label>
                  <Input
                    type="date"
                    value={formData.response_due_date}
                    onChange={(e) => setFormData({ ...formData, response_due_date: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <Label>Content Summary</Label>
                  <Textarea
                    placeholder="Brief summary of notice content"
                    value={formData.content_summary}
                    onChange={(e) => setFormData({ ...formData, content_summary: e.target.value })}
                    rows={3}
                  />
                </div>
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={() => setIsCreateDialogOpen(false)}>
                  Cancel
                </Button>
                <Button onClick={handleCreateNotice} disabled={isSubmitting}>
                  {isSubmitting ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Creating...
                    </>
                  ) : (
                    "Create Notice"
                  )}
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-5">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Notices</CardTitle>
            <Bell className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.total}</div>
            <p className="text-xs text-muted-foreground">All notices</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Incoming</CardTitle>
            <Inbox className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.incoming}</div>
            <p className="text-xs text-muted-foreground">Received</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Outgoing</CardTitle>
            <Send className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.outgoing}</div>
            <p className="text-xs text-muted-foreground">Sent</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Pending Response</CardTitle>
            <Clock className="h-4 w-4 text-orange-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-600">{stats.pendingResponse}</div>
            <p className="text-xs text-muted-foreground">Awaiting reply</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Overdue</CardTitle>
            <AlertTriangle className="h-4 w-4 text-red-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">{stats.overdue}</div>
            <p className="text-xs text-muted-foreground">Past due date</p>
          </CardContent>
        </Card>
      </div>

      {/* Due Date Alerts */}
      {stats.overdue > 0 && (
        <Card className="border-red-200 bg-red-50">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2 text-red-700">
              <AlertTriangle className="h-4 w-4" />
              Overdue Alerts
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {notices
                .filter((n) => isOverdue(n.response_due_date, n.status))
                .map((notice) => (
                  <div key={notice.id} className="flex items-center justify-between text-sm">
                    <div className="flex items-center gap-2">
                      {getDirectionBadge(notice.direction)}
                      <span className="font-medium">{notice.notice_number}</span>
                      <span className="text-muted-foreground">- {notice.title}</span>
                    </div>
                    <Badge variant="outline" className="text-red-600 border-red-300">
                      Due: {formatDate(notice.response_due_date)}
                    </Badge>
                  </div>
                ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Tabs and Table */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="all" className="gap-2">
            <FileText className="h-4 w-4" />
            All Notices
          </TabsTrigger>
          <TabsTrigger value="incoming" className="gap-2">
            <ArrowDownLeft className="h-4 w-4" />
            Incoming
          </TabsTrigger>
          <TabsTrigger value="outgoing" className="gap-2">
            <ArrowUpRight className="h-4 w-4" />
            Outgoing
          </TabsTrigger>
          <TabsTrigger value="pending" className="gap-2">
            <Clock className="h-4 w-4" />
            Pending Response
          </TabsTrigger>
        </TabsList>

        <TabsContent value={activeTab} className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Notice List</CardTitle>
              <CardDescription>View and manage legal notices</CardDescription>
            </CardHeader>
            <CardContent>
              {/* Filters */}
              <div className="flex items-center gap-4 mb-4">
                <div className="relative flex-1">
                  <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                  <Input
                    placeholder="Search notices..."
                    className="pl-8"
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                  />
                </div>
                <Select value={noticeTypeFilter} onValueChange={setNoticeTypeFilter}>
                  <SelectTrigger className="w-[180px]">
                    <SelectValue placeholder="Notice Type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Types</SelectItem>
                    {NOTICE_TYPES.map((type) => (
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
                    {NOTICE_STATUSES.map((status) => (
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
              ) : filteredNotices.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  No notices found. Click "New Notice" to create one.
                </div>
              ) : (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Notice</TableHead>
                      <TableHead>Type</TableHead>
                      <TableHead>Direction</TableHead>
                      <TableHead>From / To</TableHead>
                      <TableHead>Issue Date</TableHead>
                      <TableHead>Response Due</TableHead>
                      <TableHead>Priority</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {filteredNotices.map((notice) => (
                      <TableRow key={notice.id}>
                        <TableCell>
                          <div>
                            <p className="font-medium">{notice.notice_number}</p>
                            <p className="text-xs text-muted-foreground truncate max-w-[200px]">
                              {notice.title}
                            </p>
                          </div>
                        </TableCell>
                        <TableCell>
                          <Badge variant="outline" className="capitalize text-xs">
                            {NOTICE_TYPES.find((t) => t.value === notice.notice_type)?.label ||
                              notice.notice_type}
                          </Badge>
                        </TableCell>
                        <TableCell>{getDirectionBadge(notice.direction)}</TableCell>
                        <TableCell>
                          <div>
                            <p className="text-sm">
                              {notice.direction === "incoming"
                                ? notice.sender_name
                                : notice.recipient_name}
                            </p>
                            <p className="text-xs text-muted-foreground">
                              {notice.direction === "incoming" ? "From" : "To"}
                            </p>
                          </div>
                        </TableCell>
                        <TableCell>{formatDate(notice.issue_date)}</TableCell>
                        <TableCell>
                          <div className="flex items-center gap-2">
                            {isOverdue(notice.response_due_date, notice.status) && (
                              <AlertTriangle className="h-4 w-4 text-red-500" />
                            )}
                            {isDueSoon(notice.response_due_date, notice.status) &&
                              !isOverdue(notice.response_due_date, notice.status) && (
                                <Clock className="h-4 w-4 text-orange-500" />
                              )}
                            <span
                              className={
                                isOverdue(notice.response_due_date, notice.status)
                                  ? "text-red-600 font-medium"
                                  : isDueSoon(notice.response_due_date, notice.status)
                                  ? "text-orange-600 font-medium"
                                  : ""
                              }
                            >
                              {notice.response_due_date
                                ? formatDate(notice.response_due_date)
                                : "-"}
                            </span>
                          </div>
                        </TableCell>
                        <TableCell>{getPriorityBadge(notice.priority)}</TableCell>
                        <TableCell>{getStatusBadge(notice.status)}</TableCell>
                        <TableCell>
                          <div className="flex gap-2">
                            <Button
                              variant="ghost"
                              size="icon"
                              onClick={() => handleViewNotice(notice)}
                            >
                              <Eye className="h-4 w-4" />
                            </Button>
                            {notice.status === "response_pending" && (
                              <Button
                                variant="ghost"
                                size="icon"
                                onClick={() => handleAddResponse(notice)}
                                className="text-green-600 hover:text-green-700"
                              >
                                <MessageSquare className="h-4 w-4" />
                              </Button>
                            )}
                            <Button variant="ghost" size="icon">
                              <Edit className="h-4 w-4" />
                            </Button>
                            {["closed", "resolved"].includes(notice.status) && (
                              <Button
                                variant="ghost"
                                size="icon"
                                className="text-red-600 hover:text-red-700 hover:bg-red-50"
                                onClick={() => handleDeleteClick(notice)}
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
      </Tabs>

      {/* View Notice Dialog */}
      <Dialog open={isViewDialogOpen} onOpenChange={setIsViewDialogOpen}>
        <DialogContent className="max-w-3xl">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Bell className="h-5 w-5" />
              {selectedNotice?.notice_number}
            </DialogTitle>
            <DialogDescription>{selectedNotice?.title}</DialogDescription>
          </DialogHeader>
          {selectedNotice && (
            <div className="grid gap-6 py-4">
              {/* Status Row */}
              <div className="flex items-center gap-4">
                {getDirectionBadge(selectedNotice.direction)}
                {getStatusBadge(selectedNotice.status)}
                {getPriorityBadge(selectedNotice.priority)}
                <Badge variant="outline" className="capitalize">
                  {NOTICE_TYPES.find((t) => t.value === selectedNotice.notice_type)?.label ||
                    selectedNotice.notice_type}
                </Badge>
              </div>

              {/* Sender / Recipient */}
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1">
                  <Label className="text-xs text-muted-foreground">
                    {selectedNotice.direction === "incoming" ? "Sender" : "From (Us)"}
                  </Label>
                  <div className="flex items-start gap-2">
                    <Building2 className="h-4 w-4 text-muted-foreground mt-0.5" />
                    <div>
                      <p className="font-medium">{selectedNotice.sender_name}</p>
                      <p className="text-xs text-muted-foreground">{selectedNotice.sender_email}</p>
                    </div>
                  </div>
                </div>
                <div className="space-y-1">
                  <Label className="text-xs text-muted-foreground">
                    {selectedNotice.direction === "outgoing" ? "Recipient" : "To (Us)"}
                  </Label>
                  <div className="flex items-start gap-2">
                    <User className="h-4 w-4 text-muted-foreground mt-0.5" />
                    <div>
                      <p className="font-medium">{selectedNotice.recipient_name}</p>
                      <p className="text-xs text-muted-foreground">{selectedNotice.recipient_email}</p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Subject */}
              <div className="space-y-1">
                <Label className="text-xs text-muted-foreground">Subject</Label>
                <p className="font-medium">{selectedNotice.subject}</p>
              </div>

              {/* Dates */}
              <div className="grid grid-cols-3 gap-4">
                <div className="space-y-1">
                  <Label className="text-xs text-muted-foreground">Issue Date</Label>
                  <div className="flex items-center gap-2">
                    <Calendar className="h-4 w-4 text-muted-foreground" />
                    <span>{formatDate(selectedNotice.issue_date)}</span>
                  </div>
                </div>
                {selectedNotice.received_date && (
                  <div className="space-y-1">
                    <Label className="text-xs text-muted-foreground">Received Date</Label>
                    <div className="flex items-center gap-2">
                      <Calendar className="h-4 w-4 text-muted-foreground" />
                      <span>{formatDate(selectedNotice.received_date)}</span>
                    </div>
                  </div>
                )}
                <div className="space-y-1">
                  <Label className="text-xs text-muted-foreground">Response Due</Label>
                  <div className="flex items-center gap-2">
                    <Clock className="h-4 w-4 text-muted-foreground" />
                    <span
                      className={
                        isOverdue(selectedNotice.response_due_date, selectedNotice.status)
                          ? "text-red-600 font-medium"
                          : ""
                      }
                    >
                      {selectedNotice.response_due_date
                        ? formatDate(selectedNotice.response_due_date)
                        : "Not set"}
                    </span>
                  </div>
                </div>
              </div>

              {/* Content Summary */}
              <div className="space-y-1">
                <Label className="text-xs text-muted-foreground">Content Summary</Label>
                <div className="p-3 bg-muted/50 rounded-md text-sm">
                  {selectedNotice.content_summary || "No summary provided"}
                </div>
              </div>

              {/* Response (if received) */}
              {selectedNotice.response_date && (
                <div className="space-y-1">
                  <Label className="text-xs text-muted-foreground">
                    Response ({formatDate(selectedNotice.response_date)})
                  </Label>
                  <div className="p-3 bg-green-50 border border-green-200 rounded-md text-sm">
                    {selectedNotice.response_summary}
                  </div>
                </div>
              )}

              {/* Related Case */}
              {selectedNotice.related_case_number && (
                <div className="space-y-1">
                  <Label className="text-xs text-muted-foreground">Related Case</Label>
                  <Badge variant="outline">
                    {selectedNotice.related_case_number}
                  </Badge>
                </div>
              )}
            </div>
          )}
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsViewDialogOpen(false)}>
              Close
            </Button>
            {selectedNotice?.status === "response_pending" && (
              <Button
                variant="outline"
                onClick={() => {
                  setIsViewDialogOpen(false);
                  handleAddResponse(selectedNotice);
                }}
              >
                <MessageSquare className="mr-2 h-4 w-4" />
                Add Response
              </Button>
            )}
            <Button>
              <Edit className="mr-2 h-4 w-4" />
              Edit Notice
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Response Dialog */}
      <Dialog open={isResponseDialogOpen} onOpenChange={setIsResponseDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Record Response</DialogTitle>
            <DialogDescription>
              Record the response for notice {selectedNotice?.notice_number}
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div className="space-y-2">
              <Label>Response Date</Label>
              <Input
                type="date"
                value={responseData.response_date}
                onChange={(e) => setResponseData({ ...responseData, response_date: e.target.value })}
              />
            </div>
            <div className="space-y-2">
              <Label>Response Summary *</Label>
              <Textarea
                placeholder="Summarize the response received or sent"
                value={responseData.response_summary}
                onChange={(e) =>
                  setResponseData({ ...responseData, response_summary: e.target.value })
                }
                rows={4}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsResponseDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleSubmitResponse} disabled={isSubmitting}>
              {isSubmitting ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Saving...
                </>
              ) : (
                <>
                  <CheckCircle2 className="mr-2 h-4 w-4" />
                  Save Response
                </>
              )}
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
              Delete Notice
            </AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete <strong>{noticeToDelete?.notice_number}</strong>?
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
