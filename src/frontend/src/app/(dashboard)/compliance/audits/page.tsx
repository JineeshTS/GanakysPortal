"use client";

import * as React from "react";
import { useState, useEffect, useMemo } from "react";
import Link from "next/link";
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
import { PageHeader } from "@/components/layout/page-header";
import { StatCard } from "@/components/layout/stat-card";
import { useApi, useToast } from "@/hooks";
import {
  Scale,
  Search,
  Plus,
  Download,
  Filter,
  CheckCircle,
  Clock,
  AlertTriangle,
  Calendar,
  User,
  Eye,
  Trash2,
  Loader2,
  FileText,
  Building,
  Shield,
  AlertCircle,
  ChevronDown,
  ChevronUp,
  RefreshCw,
} from "lucide-react";

// ============================================================================
// TypeScript Interfaces
// ============================================================================

interface AuditFinding {
  id: string;
  description: string;
  severity: "critical" | "major" | "minor" | "observation";
  status: "open" | "in_progress" | "resolved" | "closed";
  area: string;
  recommendation?: string;
  due_date?: string;
  assigned_to?: string;
}

interface Audit {
  id: string;
  name: string;
  type: "internal" | "external" | "statutory";
  auditor: string;
  auditor_firm?: string;
  entity: string;
  scope: string;
  start_date: string;
  end_date: string;
  status: "scheduled" | "in_progress" | "completed" | "cancelled";
  findings: AuditFinding[];
  total_findings: number;
  critical_findings: number;
  major_findings: number;
  minor_findings: number;
  observations: number;
  report_url?: string;
  created_at: string;
  updated_at: string;
}

interface AuditApiResponse {
  items: Audit[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

// ============================================================================
// Mock Data
// ============================================================================

const mockAudits: Audit[] = [
  {
    id: "1",
    name: "Annual Statutory Audit FY 2025-26",
    type: "statutory",
    auditor: "Sanjay Mehta",
    auditor_firm: "KPMG India",
    entity: "Gana Industries Pvt Ltd",
    scope: "Full financial statements audit including balance sheet, P&L, cash flow, and notes",
    start_date: "2026-04-01",
    end_date: "2026-05-15",
    status: "scheduled",
    findings: [],
    total_findings: 0,
    critical_findings: 0,
    major_findings: 0,
    minor_findings: 0,
    observations: 0,
    created_at: "2026-01-10T10:00:00Z",
    updated_at: "2026-01-10T10:00:00Z",
  },
  {
    id: "2",
    name: "Internal Compliance Audit Q4 2025",
    type: "internal",
    auditor: "Internal Audit Team",
    entity: "Gana Industries Pvt Ltd",
    scope: "Review of compliance with internal policies, SOPs, and regulatory requirements",
    start_date: "2025-10-01",
    end_date: "2025-10-31",
    status: "completed",
    findings: [
      {
        id: "F1",
        description: "Leave approval workflow not consistently followed",
        severity: "minor",
        status: "resolved",
        area: "HR Compliance",
        recommendation: "Implement automated workflow enforcement",
      },
      {
        id: "F2",
        description: "Missing documentation for expense claims",
        severity: "major",
        status: "in_progress",
        area: "Finance",
        recommendation: "Mandatory attachment requirement before approval",
        due_date: "2026-01-31",
        assigned_to: "Priya Sharma",
      },
      {
        id: "F3",
        description: "IT access rights review overdue",
        severity: "major",
        status: "open",
        area: "IT Security",
        recommendation: "Quarterly access review process to be implemented",
        due_date: "2026-02-15",
        assigned_to: "Vikram Singh",
      },
      {
        id: "F4",
        description: "Training records not updated for new joiners",
        severity: "minor",
        status: "resolved",
        area: "HR Compliance",
      },
      {
        id: "F5",
        description: "Vendor evaluation process improvement opportunity",
        severity: "observation",
        status: "closed",
        area: "Procurement",
      },
    ],
    total_findings: 5,
    critical_findings: 0,
    major_findings: 2,
    minor_findings: 2,
    observations: 1,
    report_url: "/reports/internal-audit-q4-2025.pdf",
    created_at: "2025-09-15T09:00:00Z",
    updated_at: "2025-11-05T16:00:00Z",
  },
  {
    id: "3",
    name: "GST Audit FY 2024-25",
    type: "statutory",
    auditor: "Rakesh Gupta",
    auditor_firm: "Deloitte India",
    entity: "Gana Industries Pvt Ltd",
    scope: "GST compliance audit covering GSTR-1, GSTR-3B, ITC reconciliation",
    start_date: "2025-08-01",
    end_date: "2025-09-30",
    status: "completed",
    findings: [
      {
        id: "F6",
        description: "ITC reversal not done for credit notes received",
        severity: "major",
        status: "resolved",
        area: "GST Compliance",
        recommendation: "Implement automated ITC tracking system",
      },
      {
        id: "F7",
        description: "HSN code classification discrepancy",
        severity: "minor",
        status: "closed",
        area: "GST Compliance",
      },
    ],
    total_findings: 2,
    critical_findings: 0,
    major_findings: 1,
    minor_findings: 1,
    observations: 0,
    report_url: "/reports/gst-audit-fy2024-25.pdf",
    created_at: "2025-07-15T10:00:00Z",
    updated_at: "2025-10-10T14:00:00Z",
  },
  {
    id: "4",
    name: "Factory Safety Audit 2025",
    type: "external",
    auditor: "Safety First Consultants",
    entity: "Manufacturing Unit - Pune",
    scope: "Comprehensive safety audit covering fire safety, electrical safety, and occupational health",
    start_date: "2025-11-01",
    end_date: "2025-11-15",
    status: "completed",
    findings: [
      {
        id: "F8",
        description: "Fire extinguisher inspection overdue in Storage Area B",
        severity: "critical",
        status: "resolved",
        area: "Fire Safety",
        recommendation: "Immediate inspection and maintenance required",
      },
      {
        id: "F9",
        description: "Emergency exit signage not illuminated",
        severity: "major",
        status: "resolved",
        area: "Fire Safety",
      },
      {
        id: "F10",
        description: "PPE compliance below 95% target",
        severity: "minor",
        status: "in_progress",
        area: "Occupational Safety",
        due_date: "2026-01-20",
        assigned_to: "Amit Patel",
      },
    ],
    total_findings: 3,
    critical_findings: 1,
    major_findings: 1,
    minor_findings: 1,
    observations: 0,
    report_url: "/reports/safety-audit-2025.pdf",
    created_at: "2025-10-15T09:00:00Z",
    updated_at: "2025-11-20T15:00:00Z",
  },
  {
    id: "5",
    name: "IT Security Audit Q1 2026",
    type: "internal",
    auditor: "IT Security Team",
    entity: "Gana Industries Pvt Ltd",
    scope: "Review of IT security controls, access management, and data protection measures",
    start_date: "2026-01-15",
    end_date: "2026-02-15",
    status: "in_progress",
    findings: [
      {
        id: "F11",
        description: "Weak password policy for service accounts",
        severity: "critical",
        status: "open",
        area: "Access Management",
        recommendation: "Implement strong password policy and MFA",
        due_date: "2026-01-25",
        assigned_to: "Vikram Singh",
      },
    ],
    total_findings: 1,
    critical_findings: 1,
    major_findings: 0,
    minor_findings: 0,
    observations: 0,
    created_at: "2026-01-10T10:00:00Z",
    updated_at: "2026-01-15T11:00:00Z",
  },
  {
    id: "6",
    name: "Environmental Compliance Audit",
    type: "external",
    auditor: "Green Compliance Pvt Ltd",
    entity: "Manufacturing Unit - Pune",
    scope: "Environmental compliance audit covering emissions, waste management, and pollution control",
    start_date: "2026-03-01",
    end_date: "2026-03-15",
    status: "scheduled",
    findings: [],
    total_findings: 0,
    critical_findings: 0,
    major_findings: 0,
    minor_findings: 0,
    observations: 0,
    created_at: "2026-01-12T09:00:00Z",
    updated_at: "2026-01-12T09:00:00Z",
  },
];

// ============================================================================
// Compliance Audits Page
// ============================================================================

export default function ComplianceAuditsPage() {
  const [audits, setAudits] = useState<Audit[]>(mockAudits);
  const [searchTerm, setSearchTerm] = useState("");
  const [typeFilter, setTypeFilter] = useState("all");
  const [statusFilter, setStatusFilter] = useState("all");
  const [isLoading, setIsLoading] = useState(true);
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [selectedAudit, setSelectedAudit] = useState<Audit | null>(null);
  const [isViewDialogOpen, setIsViewDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [auditToDelete, setAuditToDelete] = useState<Audit | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);
  const [expandedFindings, setExpandedFindings] = useState<string | null>(null);

  // Form state for creating audits
  const [formData, setFormData] = useState({
    name: "",
    type: "internal",
    auditor: "",
    auditor_firm: "",
    entity: "Gana Industries Pvt Ltd",
    scope: "",
    start_date: "",
    end_date: "",
  });

  const { showToast } = useToast();
  const auditsApi = useApi<AuditApiResponse>();

  // Fetch audits
  useEffect(() => {
    const fetchAudits = async () => {
      setIsLoading(true);
      try {
        const result = await auditsApi.get("/compliance/audits");
        if (result && result.items) {
          setAudits(result.items);
        }
      } catch (error) {
        showToast("error", "Failed to fetch audits");
      } finally {
        setIsLoading(false);
      }
    };

    fetchAudits();
  }, []);

  // Filter audits
  const filteredAudits = useMemo(() => {
    return audits.filter((audit) => {
      const matchesSearch =
        audit.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        audit.auditor.toLowerCase().includes(searchTerm.toLowerCase()) ||
        audit.entity.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesType = typeFilter === "all" || audit.type === typeFilter;
      const matchesStatus =
        statusFilter === "all" || audit.status === statusFilter;
      return matchesSearch && matchesType && matchesStatus;
    });
  }, [audits, searchTerm, typeFilter, statusFilter]);

  // Calculate stats
  const stats = useMemo(() => {
    const total = audits.length;
    const scheduled = audits.filter((a) => a.status === "scheduled").length;
    const inProgress = audits.filter((a) => a.status === "in_progress").length;
    const completed = audits.filter((a) => a.status === "completed").length;
    const totalFindings = audits.reduce((sum, a) => sum + a.total_findings, 0);
    const openFindings = audits.reduce(
      (sum, a) =>
        sum +
        a.findings.filter((f) => f.status === "open" || f.status === "in_progress")
          .length,
      0
    );
    const criticalFindings = audits.reduce(
      (sum, a) => sum + a.critical_findings,
      0
    );
    return {
      total,
      scheduled,
      inProgress,
      completed,
      totalFindings,
      openFindings,
      criticalFindings,
    };
  }, [audits]);

  // Status badge styles
  const getStatusBadge = (status: string) => {
    const styles: Record<string, string> = {
      scheduled: "bg-purple-100 text-purple-800",
      in_progress: "bg-blue-100 text-blue-800",
      completed: "bg-green-100 text-green-800",
      cancelled: "bg-gray-100 text-gray-800",
    };
    return styles[status] || "bg-gray-100 text-gray-800";
  };

  // Type badge styles
  const getTypeBadge = (type: string) => {
    const styles: Record<string, string> = {
      internal: "bg-blue-100 text-blue-800",
      external: "bg-orange-100 text-orange-800",
      statutory: "bg-purple-100 text-purple-800",
    };
    return styles[type] || "bg-gray-100 text-gray-800";
  };

  // Severity badge styles
  const getSeverityBadge = (severity: string) => {
    const styles: Record<string, string> = {
      critical: "bg-red-100 text-red-800",
      major: "bg-orange-100 text-orange-800",
      minor: "bg-yellow-100 text-yellow-800",
      observation: "bg-blue-100 text-blue-800",
    };
    return styles[severity] || "bg-gray-100 text-gray-800";
  };

  // Finding status badge styles
  const getFindingStatusBadge = (status: string) => {
    const styles: Record<string, string> = {
      open: "bg-red-100 text-red-800",
      in_progress: "bg-yellow-100 text-yellow-800",
      resolved: "bg-green-100 text-green-800",
      closed: "bg-gray-100 text-gray-800",
    };
    return styles[status] || "bg-gray-100 text-gray-800";
  };

  // Handle audit creation
  const handleCreateAudit = async () => {
    try {
      const newAudit: Audit = {
        id: `AUD-${Date.now()}`,
        name: formData.name,
        type: formData.type as Audit["type"],
        auditor: formData.auditor,
        auditor_firm: formData.auditor_firm || undefined,
        entity: formData.entity,
        scope: formData.scope,
        start_date: formData.start_date,
        end_date: formData.end_date,
        status: "scheduled",
        findings: [],
        total_findings: 0,
        critical_findings: 0,
        major_findings: 0,
        minor_findings: 0,
        observations: 0,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };

      setAudits([newAudit, ...audits]);
      setIsCreateDialogOpen(false);
      setFormData({
        name: "",
        type: "internal",
        auditor: "",
        auditor_firm: "",
        entity: "Gana Industries Pvt Ltd",
        scope: "",
        start_date: "",
        end_date: "",
      });
      showToast("success", "Audit scheduled successfully");
    } catch (error) {
      showToast("error", "Failed to schedule audit");
    }
  };

  // Handle delete
  const handleDeleteClick = (audit: Audit) => {
    setAuditToDelete(audit);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!auditToDelete) return;
    setIsDeleting(true);
    try {
      setAudits(audits.filter((a) => a.id !== auditToDelete.id));
      setDeleteDialogOpen(false);
      setAuditToDelete(null);
      showToast("success", "Audit deleted successfully");
    } catch (error) {
      showToast("error", "Failed to delete audit");
    } finally {
      setIsDeleting(false);
    }
  };

  // View audit details
  const handleViewAudit = (audit: Audit) => {
    setSelectedAudit(audit);
    setIsViewDialogOpen(true);
  };

  // Format date
  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString("en-IN", {
      day: "2-digit",
      month: "short",
      year: "numeric",
    });
  };

  // Toggle findings expansion in table
  const toggleFindings = (auditId: string) => {
    setExpandedFindings(expandedFindings === auditId ? null : auditId);
  };

  return (
    <div className="flex flex-col gap-6 p-6">
      <PageHeader
        title="Audit Records"
        description="Track and manage compliance audits and findings"
        breadcrumbs={[
          { label: "Dashboard", href: "/" },
          { label: "Compliance", href: "/compliance" },
          { label: "Audits" },
        ]}
        actions={
          <div className="flex gap-2">
            <Button variant="outline">
              <Download className="mr-2 h-4 w-4" />
              Export Report
            </Button>
            <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
              <DialogTrigger asChild>
                <Button>
                  <Plus className="mr-2 h-4 w-4" />
                  Schedule Audit
                </Button>
              </DialogTrigger>
              <DialogContent className="max-w-2xl">
                <DialogHeader>
                  <DialogTitle>Schedule New Audit</DialogTitle>
                  <DialogDescription>
                    Plan a compliance audit with details and timeline
                  </DialogDescription>
                </DialogHeader>
                <div className="grid gap-4 py-4">
                  <div className="space-y-2">
                    <Label>Audit Name</Label>
                    <Input
                      placeholder="Enter audit name"
                      value={formData.name}
                      onChange={(e) =>
                        setFormData({ ...formData, name: e.target.value })
                      }
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label>Audit Type</Label>
                      <Select
                        value={formData.type}
                        onValueChange={(value) =>
                          setFormData({ ...formData, type: value })
                        }
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="Select type" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="internal">Internal</SelectItem>
                          <SelectItem value="external">External</SelectItem>
                          <SelectItem value="statutory">Statutory</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="space-y-2">
                      <Label>Entity</Label>
                      <Select
                        value={formData.entity}
                        onValueChange={(value) =>
                          setFormData({ ...formData, entity: value })
                        }
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="Select entity" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="Gana Industries Pvt Ltd">
                            Gana Industries Pvt Ltd
                          </SelectItem>
                          <SelectItem value="Manufacturing Unit - Pune">
                            Manufacturing Unit - Pune
                          </SelectItem>
                          <SelectItem value="Manufacturing Unit - Chennai">
                            Manufacturing Unit - Chennai
                          </SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label>Auditor Name</Label>
                      <Input
                        placeholder="Enter auditor name"
                        value={formData.auditor}
                        onChange={(e) =>
                          setFormData({ ...formData, auditor: e.target.value })
                        }
                      />
                    </div>
                    <div className="space-y-2">
                      <Label>Auditor Firm (Optional)</Label>
                      <Input
                        placeholder="Enter auditor firm"
                        value={formData.auditor_firm}
                        onChange={(e) =>
                          setFormData({ ...formData, auditor_firm: e.target.value })
                        }
                      />
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label>Start Date</Label>
                      <Input
                        type="date"
                        value={formData.start_date}
                        onChange={(e) =>
                          setFormData({ ...formData, start_date: e.target.value })
                        }
                      />
                    </div>
                    <div className="space-y-2">
                      <Label>End Date</Label>
                      <Input
                        type="date"
                        value={formData.end_date}
                        onChange={(e) =>
                          setFormData({ ...formData, end_date: e.target.value })
                        }
                      />
                    </div>
                  </div>
                  <div className="space-y-2">
                    <Label>Audit Scope</Label>
                    <Textarea
                      placeholder="Describe the scope of the audit"
                      value={formData.scope}
                      onChange={(e) =>
                        setFormData({ ...formData, scope: e.target.value })
                      }
                    />
                  </div>
                </div>
                <DialogFooter>
                  <Button
                    variant="outline"
                    onClick={() => setIsCreateDialogOpen(false)}
                  >
                    Cancel
                  </Button>
                  <Button onClick={handleCreateAudit}>Schedule Audit</Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
          </div>
        }
      />

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-6">
        <StatCard
          title="Total Audits"
          value={stats.total}
          icon={Scale}
          description="All audit records"
        />
        <StatCard
          title="Scheduled"
          value={stats.scheduled}
          icon={Calendar}
          description="Upcoming audits"
          valueClassName="text-purple-600"
        />
        <StatCard
          title="In Progress"
          value={stats.inProgress}
          icon={Clock}
          description="Currently running"
          valueClassName="text-blue-600"
        />
        <StatCard
          title="Completed"
          value={stats.completed}
          icon={CheckCircle}
          description="Finished audits"
          valueClassName="text-green-600"
        />
        <StatCard
          title="Open Findings"
          value={stats.openFindings}
          icon={AlertCircle}
          description="Pending resolution"
          valueClassName="text-yellow-600"
        />
        <StatCard
          title="Critical"
          value={stats.criticalFindings}
          icon={AlertTriangle}
          description="Critical findings"
          valueClassName="text-red-600"
        />
      </div>

      {/* Filters */}
      <div className="flex items-center gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search audits by name, auditor, or entity..."
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
            <SelectItem value="internal">Internal</SelectItem>
            <SelectItem value="external">External</SelectItem>
            <SelectItem value="statutory">Statutory</SelectItem>
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
        <Button
          variant="outline"
          size="icon"
          onClick={() => {
            setSearchTerm("");
            setTypeFilter("all");
            setStatusFilter("all");
          }}
        >
          <RefreshCw className="h-4 w-4" />
        </Button>
      </div>

      {/* Audits Table */}
      <Card>
        <CardHeader>
          <CardTitle>Audit Records</CardTitle>
          <CardDescription>{filteredAudits.length} audit(s) found</CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
              <span className="ml-2 text-muted-foreground">Loading audits...</span>
            </div>
          ) : filteredAudits.length === 0 ? (
            <div className="text-center py-12 text-muted-foreground">
              <Scale className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p>No audits found matching your criteria</p>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Audit Name</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Auditor</TableHead>
                  <TableHead>Entity</TableHead>
                  <TableHead>Period</TableHead>
                  <TableHead>Findings</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredAudits.map((audit) => (
                  <React.Fragment key={audit.id}>
                    <TableRow>
                      <TableCell>
                        <div className="font-medium">{audit.name}</div>
                        {audit.scope && (
                          <div className="text-sm text-muted-foreground truncate max-w-[200px]">
                            {audit.scope}
                          </div>
                        )}
                      </TableCell>
                      <TableCell>
                        <Badge className={getTypeBadge(audit.type)}>
                          {audit.type}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <User className="h-4 w-4 text-muted-foreground" />
                          <div>
                            <div>{audit.auditor}</div>
                            {audit.auditor_firm && (
                              <div className="text-xs text-muted-foreground">
                                {audit.auditor_firm}
                              </div>
                            )}
                          </div>
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <Building className="h-4 w-4 text-muted-foreground" />
                          <span className="text-sm">{audit.entity}</span>
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="text-sm">
                          {formatDate(audit.start_date)}
                        </div>
                        <div className="text-xs text-muted-foreground">
                          to {formatDate(audit.end_date)}
                        </div>
                      </TableCell>
                      <TableCell>
                        {audit.total_findings > 0 ? (
                          <Button
                            variant="ghost"
                            size="sm"
                            className="p-1 h-auto"
                            onClick={() => toggleFindings(audit.id)}
                          >
                            <div className="flex items-center gap-2">
                              <div className="flex gap-1">
                                {audit.critical_findings > 0 && (
                                  <Badge className="bg-red-100 text-red-800 text-xs px-1.5">
                                    {audit.critical_findings}C
                                  </Badge>
                                )}
                                {audit.major_findings > 0 && (
                                  <Badge className="bg-orange-100 text-orange-800 text-xs px-1.5">
                                    {audit.major_findings}M
                                  </Badge>
                                )}
                                {audit.minor_findings > 0 && (
                                  <Badge className="bg-yellow-100 text-yellow-800 text-xs px-1.5">
                                    {audit.minor_findings}m
                                  </Badge>
                                )}
                                {audit.observations > 0 && (
                                  <Badge className="bg-blue-100 text-blue-800 text-xs px-1.5">
                                    {audit.observations}O
                                  </Badge>
                                )}
                              </div>
                              {expandedFindings === audit.id ? (
                                <ChevronUp className="h-4 w-4" />
                              ) : (
                                <ChevronDown className="h-4 w-4" />
                              )}
                            </div>
                          </Button>
                        ) : (
                          <Badge variant="secondary">No findings</Badge>
                        )}
                      </TableCell>
                      <TableCell>
                        <Badge className={getStatusBadge(audit.status)}>
                          {audit.status.replace("_", " ")}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <div className="flex gap-1">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleViewAudit(audit)}
                          >
                            <Eye className="h-4 w-4" />
                          </Button>
                          {audit.report_url && (
                            <Button variant="ghost" size="sm" asChild>
                              <a
                                href={audit.report_url}
                                target="_blank"
                                rel="noopener noreferrer"
                              >
                                <FileText className="h-4 w-4" />
                              </a>
                            </Button>
                          )}
                          {(audit.status === "completed" ||
                            audit.status === "cancelled") && (
                            <Button
                              variant="ghost"
                              size="sm"
                              className="text-red-600 hover:text-red-700 hover:bg-red-50"
                              onClick={() => handleDeleteClick(audit)}
                            >
                              <Trash2 className="h-4 w-4" />
                            </Button>
                          )}
                        </div>
                      </TableCell>
                    </TableRow>
                    {/* Expanded Findings Row */}
                    {expandedFindings === audit.id && audit.findings.length > 0 && (
                      <TableRow>
                        <TableCell colSpan={8} className="bg-muted/30 p-4">
                          <div className="space-y-3">
                            <h4 className="font-medium text-sm flex items-center gap-2">
                              <AlertCircle className="h-4 w-4" />
                              Findings ({audit.total_findings})
                            </h4>
                            <div className="grid gap-2">
                              {audit.findings.map((finding) => (
                                <div
                                  key={finding.id}
                                  className="bg-white p-3 rounded-lg border flex items-start justify-between gap-4"
                                >
                                  <div className="flex-1">
                                    <div className="flex items-center gap-2 mb-1">
                                      <Badge
                                        className={getSeverityBadge(finding.severity)}
                                      >
                                        {finding.severity}
                                      </Badge>
                                      <span className="text-sm text-muted-foreground">
                                        {finding.area}
                                      </span>
                                    </div>
                                    <p className="text-sm">{finding.description}</p>
                                    {finding.recommendation && (
                                      <p className="text-xs text-muted-foreground mt-1">
                                        <strong>Recommendation:</strong>{" "}
                                        {finding.recommendation}
                                      </p>
                                    )}
                                    {(finding.assigned_to || finding.due_date) && (
                                      <div className="flex gap-4 mt-2 text-xs text-muted-foreground">
                                        {finding.assigned_to && (
                                          <span>Assigned: {finding.assigned_to}</span>
                                        )}
                                        {finding.due_date && (
                                          <span>
                                            Due: {formatDate(finding.due_date)}
                                          </span>
                                        )}
                                      </div>
                                    )}
                                  </div>
                                  <Badge
                                    className={getFindingStatusBadge(finding.status)}
                                  >
                                    {finding.status.replace("_", " ")}
                                  </Badge>
                                </div>
                              ))}
                            </div>
                          </div>
                        </TableCell>
                      </TableRow>
                    )}
                  </React.Fragment>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      {/* View Audit Dialog */}
      <Dialog open={isViewDialogOpen} onOpenChange={setIsViewDialogOpen}>
        <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Scale className="h-5 w-5" />
              Audit Details
            </DialogTitle>
          </DialogHeader>
          {selectedAudit && (
            <div className="space-y-6">
              {/* Audit Info */}
              <div className="p-4 bg-muted rounded-lg">
                <h3 className="font-medium text-lg">{selectedAudit.name}</h3>
                <p className="text-sm text-muted-foreground mt-1">
                  {selectedAudit.scope}
                </p>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm">
                <div>
                  <p className="text-muted-foreground">Type</p>
                  <Badge className={getTypeBadge(selectedAudit.type)}>
                    {selectedAudit.type}
                  </Badge>
                </div>
                <div>
                  <p className="text-muted-foreground">Status</p>
                  <Badge className={getStatusBadge(selectedAudit.status)}>
                    {selectedAudit.status.replace("_", " ")}
                  </Badge>
                </div>
                <div>
                  <p className="text-muted-foreground">Entity</p>
                  <p className="font-medium">{selectedAudit.entity}</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Auditor</p>
                  <p className="font-medium">{selectedAudit.auditor}</p>
                  {selectedAudit.auditor_firm && (
                    <p className="text-xs text-muted-foreground">
                      {selectedAudit.auditor_firm}
                    </p>
                  )}
                </div>
                <div>
                  <p className="text-muted-foreground">Start Date</p>
                  <p className="font-medium">{formatDate(selectedAudit.start_date)}</p>
                </div>
                <div>
                  <p className="text-muted-foreground">End Date</p>
                  <p className="font-medium">{formatDate(selectedAudit.end_date)}</p>
                </div>
              </div>

              {/* Findings Summary */}
              {selectedAudit.total_findings > 0 && (
                <div className="border rounded-lg p-4">
                  <h4 className="font-medium mb-3 flex items-center gap-2">
                    <AlertCircle className="h-4 w-4" />
                    Findings Summary
                  </h4>
                  <div className="grid grid-cols-4 gap-4 text-center">
                    <div className="p-3 bg-red-50 rounded-lg">
                      <div className="text-2xl font-bold text-red-600">
                        {selectedAudit.critical_findings}
                      </div>
                      <div className="text-xs text-red-800">Critical</div>
                    </div>
                    <div className="p-3 bg-orange-50 rounded-lg">
                      <div className="text-2xl font-bold text-orange-600">
                        {selectedAudit.major_findings}
                      </div>
                      <div className="text-xs text-orange-800">Major</div>
                    </div>
                    <div className="p-3 bg-yellow-50 rounded-lg">
                      <div className="text-2xl font-bold text-yellow-600">
                        {selectedAudit.minor_findings}
                      </div>
                      <div className="text-xs text-yellow-800">Minor</div>
                    </div>
                    <div className="p-3 bg-blue-50 rounded-lg">
                      <div className="text-2xl font-bold text-blue-600">
                        {selectedAudit.observations}
                      </div>
                      <div className="text-xs text-blue-800">Observations</div>
                    </div>
                  </div>
                </div>
              )}

              {/* Findings List */}
              {selectedAudit.findings.length > 0 && (
                <div>
                  <h4 className="font-medium mb-3">Detailed Findings</h4>
                  <div className="space-y-3">
                    {selectedAudit.findings.map((finding) => (
                      <div
                        key={finding.id}
                        className="border rounded-lg p-4"
                      >
                        <div className="flex items-start justify-between gap-4">
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-2">
                              <Badge className={getSeverityBadge(finding.severity)}>
                                {finding.severity}
                              </Badge>
                              <Badge variant="outline">{finding.area}</Badge>
                              <Badge
                                className={getFindingStatusBadge(finding.status)}
                              >
                                {finding.status.replace("_", " ")}
                              </Badge>
                            </div>
                            <p className="text-sm">{finding.description}</p>
                            {finding.recommendation && (
                              <div className="mt-2 p-2 bg-muted rounded text-sm">
                                <strong>Recommendation:</strong>{" "}
                                {finding.recommendation}
                              </div>
                            )}
                            {(finding.assigned_to || finding.due_date) && (
                              <div className="flex gap-4 mt-2 text-sm text-muted-foreground">
                                {finding.assigned_to && (
                                  <div className="flex items-center gap-1">
                                    <User className="h-3 w-3" />
                                    {finding.assigned_to}
                                  </div>
                                )}
                                {finding.due_date && (
                                  <div className="flex items-center gap-1">
                                    <Calendar className="h-3 w-3" />
                                    {formatDate(finding.due_date)}
                                  </div>
                                )}
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsViewDialogOpen(false)}>
              Close
            </Button>
            {selectedAudit?.report_url && (
              <Button asChild>
                <a
                  href={selectedAudit.report_url}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  <FileText className="mr-2 h-4 w-4" />
                  View Report
                </a>
              </Button>
            )}
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-red-500" />
              Delete Audit Record
            </AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete{" "}
              <strong>{auditToDelete?.name}</strong>? This will also delete all
              associated findings. This action cannot be undone.
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
