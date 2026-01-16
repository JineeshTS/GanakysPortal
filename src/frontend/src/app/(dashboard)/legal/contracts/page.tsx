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
import { FileUpload } from "@/components/forms/file-upload";
import { formatCurrency, formatDate } from "@/lib/format";
import {
  Plus,
  Search,
  Download,
  Eye,
  Edit,
  ScrollText,
  Calendar,
  AlertTriangle,
  Building2,
  IndianRupee,
  Trash2,
  Loader2,
  RefreshCw,
  Clock,
  FileText,
  Upload,
  User,
  Briefcase,
} from "lucide-react";

// Constants
const CONTRACT_TYPES = [
  { value: "vendor", label: "Vendor Agreement" },
  { value: "client", label: "Client Agreement" },
  { value: "employment", label: "Employment Contract" },
  { value: "service", label: "Service Agreement" },
  { value: "supply", label: "Supply Agreement" },
  { value: "nda", label: "Non-Disclosure Agreement" },
  { value: "lease", label: "Lease Agreement" },
  { value: "license", label: "License Agreement" },
  { value: "partnership", label: "Partnership Agreement" },
  { value: "mou", label: "Memorandum of Understanding" },
];

const CONTRACT_STATUSES = [
  { value: "draft", label: "Draft", color: "bg-gray-500" },
  { value: "pending_approval", label: "Pending Approval", color: "bg-yellow-500" },
  { value: "active", label: "Active", color: "bg-green-500" },
  { value: "expiring_soon", label: "Expiring Soon", color: "bg-orange-500" },
  { value: "expired", label: "Expired", color: "bg-red-500" },
  { value: "renewed", label: "Renewed", color: "bg-blue-500" },
  { value: "terminated", label: "Terminated", color: "bg-red-700" },
];

const PARTY_TYPES = [
  { value: "vendor", label: "Vendor" },
  { value: "customer", label: "Customer" },
  { value: "employee", label: "Employee" },
  { value: "partner", label: "Partner" },
  { value: "contractor", label: "Contractor" },
  { value: "landlord", label: "Landlord" },
];

// TypeScript interfaces
interface Contract {
  id: string;
  contract_number: string;
  title: string;
  contract_type: string;
  party_type: string;
  party_name: string;
  party_contact: string;
  status: string;
  effective_date: string;
  expiry_date: string;
  contract_value: number;
  renewal_type: string;
  renewal_reminder_days: number;
  auto_renewal: boolean;
  terms_summary: string;
  document_url: string;
  created_at: string;
  updated_at: string;
}

// Mock data
const mockContracts: Contract[] = [
  {
    id: "1",
    contract_number: "CON-2024-00045",
    title: "IT Services Agreement - TechVendor",
    contract_type: "service",
    party_type: "vendor",
    party_name: "TechVendor Solutions Pvt Ltd",
    party_contact: "vendor@techvendor.com",
    status: "active",
    effective_date: "2024-01-01",
    expiry_date: "2025-02-28",
    contract_value: 12000000,
    renewal_type: "annual",
    renewal_reminder_days: 30,
    auto_renewal: false,
    terms_summary: "IT support and maintenance services for corporate infrastructure",
    document_url: "/documents/con-2024-00045.pdf",
    created_at: "2024-01-01T10:00:00",
    updated_at: "2024-12-15T14:30:00",
  },
  {
    id: "2",
    contract_number: "CON-2024-00078",
    title: "Office Lease Agreement",
    contract_type: "lease",
    party_type: "landlord",
    party_name: "Premium Properties Ltd",
    party_contact: "lease@premiumproperties.com",
    status: "active",
    effective_date: "2023-04-01",
    expiry_date: "2025-03-31",
    contract_value: 24000000,
    renewal_type: "annual",
    renewal_reminder_days: 60,
    auto_renewal: true,
    terms_summary: "Office space lease for corporate headquarters - 5000 sq ft",
    document_url: "/documents/con-2024-00078.pdf",
    created_at: "2023-04-01T09:00:00",
    updated_at: "2024-10-20T11:00:00",
  },
  {
    id: "3",
    contract_number: "CON-2024-00092",
    title: "Software License Agreement - Enterprise Suite",
    contract_type: "license",
    party_type: "vendor",
    party_name: "Global Software Inc",
    party_contact: "licensing@globalsoftware.com",
    status: "expiring_soon",
    effective_date: "2024-02-01",
    expiry_date: "2025-01-31",
    contract_value: 5000000,
    renewal_type: "annual",
    renewal_reminder_days: 45,
    auto_renewal: false,
    terms_summary: "Enterprise software license for 200 users",
    document_url: "/documents/con-2024-00092.pdf",
    created_at: "2024-02-01T14:00:00",
    updated_at: "2025-01-10T09:00:00",
  },
  {
    id: "4",
    contract_number: "CON-2024-00105",
    title: "Employment Contract - Senior Developer",
    contract_type: "employment",
    party_type: "employee",
    party_name: "Rahul Sharma",
    party_contact: "rahul.sharma@company.com",
    status: "active",
    effective_date: "2024-06-15",
    expiry_date: "2027-06-14",
    contract_value: 3600000,
    renewal_type: "triennial",
    renewal_reminder_days: 90,
    auto_renewal: false,
    terms_summary: "3-year employment contract for Senior Developer role",
    document_url: "/documents/con-2024-00105.pdf",
    created_at: "2024-06-15T10:00:00",
    updated_at: "2024-06-15T10:00:00",
  },
  {
    id: "5",
    contract_number: "CON-2023-00089",
    title: "NDA - Strategic Partner",
    contract_type: "nda",
    party_type: "partner",
    party_name: "Innovation Labs Pvt Ltd",
    party_contact: "legal@innovationlabs.in",
    status: "expired",
    effective_date: "2023-01-01",
    expiry_date: "2024-12-31",
    contract_value: 0,
    renewal_type: "annual",
    renewal_reminder_days: 30,
    auto_renewal: false,
    terms_summary: "Mutual non-disclosure agreement for joint development project",
    document_url: "/documents/con-2023-00089.pdf",
    created_at: "2023-01-01T11:00:00",
    updated_at: "2025-01-02T08:00:00",
  },
];

export default function ContractsPage() {
  const api = useApi();
  const { showToast } = useToast();

  // State
  const [contracts, setContracts] = useState<Contract[]>(mockContracts);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [contractTypeFilter, setContractTypeFilter] = useState("all");
  const [statusFilter, setStatusFilter] = useState("all");
  const [partyTypeFilter, setPartyTypeFilter] = useState("all");

  // Dialog states
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isViewDialogOpen, setIsViewDialogOpen] = useState(false);
  const [isUploadDialogOpen, setIsUploadDialogOpen] = useState(false);
  const [selectedContract, setSelectedContract] = useState<Contract | null>(null);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [contractToDelete, setContractToDelete] = useState<Contract | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  // Form state
  const [formData, setFormData] = useState({
    title: "",
    contract_type: "",
    party_type: "",
    party_name: "",
    party_contact: "",
    effective_date: "",
    expiry_date: "",
    contract_value: "",
    renewal_type: "annual",
    renewal_reminder_days: "30",
    auto_renewal: false,
    terms_summary: "",
  });
  const [uploadFiles, setUploadFiles] = useState<File[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Fetch contracts from API
  useEffect(() => {
    const fetchContracts = async () => {
      setLoading(true);
      try {
        const response = await api.get("/legal/contracts?limit=100");
        if (response?.data && Array.isArray(response.data)) {
          setContracts(response.data.length > 0 ? response.data : mockContracts);
        }
      } catch (error) {
        console.error("Failed to fetch contracts:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchContracts();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Filter contracts
  const filteredContracts = contracts.filter((c) => {
    const matchesSearch =
      !searchTerm ||
      c.contract_number.toLowerCase().includes(searchTerm.toLowerCase()) ||
      c.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      c.party_name.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesType = contractTypeFilter === "all" || c.contract_type === contractTypeFilter;
    const matchesStatus = statusFilter === "all" || c.status === statusFilter;
    const matchesPartyType = partyTypeFilter === "all" || c.party_type === partyTypeFilter;

    return matchesSearch && matchesType && matchesStatus && matchesPartyType;
  });

  // Helpers
  const getStatusBadge = (status: string) => {
    const statusConfig = CONTRACT_STATUSES.find((s) => s.value === status);
    return (
      <Badge className={`${statusConfig?.color || "bg-gray-500"} text-white`}>
        {statusConfig?.label || status}
      </Badge>
    );
  };

  const getContractTypeBadge = (type: string) => {
    const typeConfig = CONTRACT_TYPES.find((t) => t.value === type);
    return (
      <Badge variant="outline" className="capitalize">
        {typeConfig?.label || type}
      </Badge>
    );
  };

  const isExpiringSoon = (expiryDate: string) => {
    const expiry = new Date(expiryDate);
    const today = new Date();
    const diffDays = Math.ceil((expiry.getTime() - today.getTime()) / (1000 * 60 * 60 * 24));
    return diffDays >= 0 && diffDays <= 30;
  };

  const daysUntilExpiry = (expiryDate: string) => {
    const expiry = new Date(expiryDate);
    const today = new Date();
    return Math.ceil((expiry.getTime() - today.getTime()) / (1000 * 60 * 60 * 24));
  };

  // Handlers
  const handleViewContract = (contract: Contract) => {
    setSelectedContract(contract);
    setIsViewDialogOpen(true);
  };

  const handleUploadDocument = (contract: Contract) => {
    setSelectedContract(contract);
    setIsUploadDialogOpen(true);
  };

  const handleDeleteClick = (contract: Contract) => {
    setContractToDelete(contract);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!contractToDelete) return;
    setIsDeleting(true);

    try {
      await api.delete(`/legal/contracts/${contractToDelete.id}`);
      setContracts(contracts.filter((c) => c.id !== contractToDelete.id));
      setDeleteDialogOpen(false);
      setContractToDelete(null);
      showToast("success", "Contract deleted successfully");
    } catch (error) {
      console.error("Failed to delete contract:", error);
      showToast("error", "Failed to delete contract");
    } finally {
      setIsDeleting(false);
    }
  };

  const handleCreateContract = async () => {
    if (!formData.title || !formData.contract_type || !formData.party_name) {
      showToast("error", "Please fill in required fields");
      return;
    }

    setIsSubmitting(true);
    try {
      const response = await api.post("/legal/contracts", {
        ...formData,
        contract_value: formData.contract_value ? parseFloat(formData.contract_value) : 0,
        renewal_reminder_days: parseInt(formData.renewal_reminder_days),
      });

      if (response) {
        setContracts([response as Contract, ...contracts]);
        showToast("success", "Contract created successfully");
        setIsCreateDialogOpen(false);
        setFormData({
          title: "",
          contract_type: "",
          party_type: "",
          party_name: "",
          party_contact: "",
          effective_date: "",
          expiry_date: "",
          contract_value: "",
          renewal_type: "annual",
          renewal_reminder_days: "30",
          auto_renewal: false,
          terms_summary: "",
        });
      }
    } catch (error) {
      console.error("Failed to create contract:", error);
      showToast("error", "Failed to create contract");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDocumentUpload = async () => {
    if (!selectedContract || uploadFiles.length === 0) return;

    setIsSubmitting(true);
    try {
      // In a real implementation, this would upload to the server
      showToast("success", "Document uploaded successfully");
      setIsUploadDialogOpen(false);
      setUploadFiles([]);
    } catch (error) {
      console.error("Failed to upload document:", error);
      showToast("error", "Failed to upload document");
    } finally {
      setIsSubmitting(false);
    }
  };

  // Stats
  const stats = {
    total: contracts.length,
    active: contracts.filter((c) => c.status === "active").length,
    expiringSoon: contracts.filter((c) => isExpiringSoon(c.expiry_date) && c.status === "active").length,
    totalValue: contracts
      .filter((c) => c.status === "active")
      .reduce((sum, c) => sum + (c.contract_value || 0), 0),
  };

  return (
    <div className="flex-1 space-y-4 p-4 md:p-8 pt-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Contract Management</h2>
          <p className="text-muted-foreground">
            Manage contracts, agreements, and renewals
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
                New Contract
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl">
              <DialogHeader>
                <DialogTitle>Create New Contract</DialogTitle>
                <DialogDescription>Add a new contract or agreement</DialogDescription>
              </DialogHeader>
              <div className="grid gap-4 py-4 max-h-[60vh] overflow-y-auto">
                <div className="space-y-2">
                  <Label>Contract Title *</Label>
                  <Input
                    placeholder="Enter contract title"
                    value={formData.title}
                    onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>Contract Type *</Label>
                    <Select
                      value={formData.contract_type}
                      onValueChange={(value) => setFormData({ ...formData, contract_type: value })}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select type" />
                      </SelectTrigger>
                      <SelectContent>
                        {CONTRACT_TYPES.map((type) => (
                          <SelectItem key={type.value} value={type.value}>
                            {type.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label>Party Type</Label>
                    <Select
                      value={formData.party_type}
                      onValueChange={(value) => setFormData({ ...formData, party_type: value })}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select party type" />
                      </SelectTrigger>
                      <SelectContent>
                        {PARTY_TYPES.map((type) => (
                          <SelectItem key={type.value} value={type.value}>
                            {type.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>Party Name *</Label>
                    <Input
                      placeholder="Enter party name"
                      value={formData.party_name}
                      onChange={(e) => setFormData({ ...formData, party_name: e.target.value })}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Party Contact</Label>
                    <Input
                      placeholder="Email or phone"
                      value={formData.party_contact}
                      onChange={(e) => setFormData({ ...formData, party_contact: e.target.value })}
                    />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>Effective Date</Label>
                    <Input
                      type="date"
                      value={formData.effective_date}
                      onChange={(e) => setFormData({ ...formData, effective_date: e.target.value })}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Expiry Date</Label>
                    <Input
                      type="date"
                      value={formData.expiry_date}
                      onChange={(e) => setFormData({ ...formData, expiry_date: e.target.value })}
                    />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>Contract Value (INR)</Label>
                    <Input
                      type="number"
                      placeholder="0.00"
                      value={formData.contract_value}
                      onChange={(e) => setFormData({ ...formData, contract_value: e.target.value })}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Renewal Type</Label>
                    <Select
                      value={formData.renewal_type}
                      onValueChange={(value) => setFormData({ ...formData, renewal_type: value })}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select renewal type" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="monthly">Monthly</SelectItem>
                        <SelectItem value="quarterly">Quarterly</SelectItem>
                        <SelectItem value="annual">Annual</SelectItem>
                        <SelectItem value="biennial">Biennial</SelectItem>
                        <SelectItem value="triennial">Triennial</SelectItem>
                        <SelectItem value="none">No Renewal</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label>Renewal Reminder (days before)</Label>
                    <Input
                      type="number"
                      placeholder="30"
                      value={formData.renewal_reminder_days}
                      onChange={(e) => setFormData({ ...formData, renewal_reminder_days: e.target.value })}
                    />
                  </div>
                  <div className="space-y-2 flex items-end">
                    <label className="flex items-center gap-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={formData.auto_renewal}
                        onChange={(e) => setFormData({ ...formData, auto_renewal: e.target.checked })}
                        className="rounded border-gray-300"
                      />
                      <span className="text-sm">Auto-renewal enabled</span>
                    </label>
                  </div>
                </div>
                <div className="space-y-2">
                  <Label>Terms Summary</Label>
                  <Textarea
                    placeholder="Brief summary of contract terms"
                    value={formData.terms_summary}
                    onChange={(e) => setFormData({ ...formData, terms_summary: e.target.value })}
                  />
                </div>
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={() => setIsCreateDialogOpen(false)}>
                  Cancel
                </Button>
                <Button onClick={handleCreateContract} disabled={isSubmitting}>
                  {isSubmitting ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Creating...
                    </>
                  ) : (
                    "Create Contract"
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
            <CardTitle className="text-sm font-medium">Total Contracts</CardTitle>
            <ScrollText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.total}</div>
            <p className="text-xs text-muted-foreground">{stats.active} active</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Expiring Soon</CardTitle>
            <AlertTriangle className="h-4 w-4 text-orange-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-600">{stats.expiringSoon}</div>
            <p className="text-xs text-muted-foreground">Within 30 days</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Value</CardTitle>
            <IndianRupee className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatCurrency(stats.totalValue)}</div>
            <p className="text-xs text-muted-foreground">Active contracts</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Renewal Due</CardTitle>
            <RefreshCw className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.expiringSoon}</div>
            <p className="text-xs text-muted-foreground">Need attention</p>
          </CardContent>
        </Card>
      </div>

      {/* Expiry Alerts */}
      {stats.expiringSoon > 0 && (
        <Card className="border-orange-200 bg-orange-50">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <AlertTriangle className="h-4 w-4 text-orange-500" />
              Expiry Alerts
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {contracts
                .filter((c) => isExpiringSoon(c.expiry_date) && c.status === "active")
                .map((contract) => (
                  <div key={contract.id} className="flex items-center justify-between text-sm">
                    <div>
                      <span className="font-medium">{contract.contract_number}</span>
                      <span className="text-muted-foreground"> - {contract.title}</span>
                    </div>
                    <Badge variant="outline" className="text-orange-600 border-orange-300">
                      {daysUntilExpiry(contract.expiry_date)} days left
                    </Badge>
                  </div>
                ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Filters and Table */}
      <Card>
        <CardHeader>
          <CardTitle>Contract List</CardTitle>
          <CardDescription>View and manage all contracts</CardDescription>
        </CardHeader>
        <CardContent>
          {/* Filters */}
          <div className="flex items-center gap-4 mb-4">
            <div className="relative flex-1">
              <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search contracts..."
                className="pl-8"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
            <Select value={contractTypeFilter} onValueChange={setContractTypeFilter}>
              <SelectTrigger className="w-[150px]">
                <SelectValue placeholder="Type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Types</SelectItem>
                {CONTRACT_TYPES.map((type) => (
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
                {CONTRACT_STATUSES.map((status) => (
                  <SelectItem key={status.value} value={status.value}>
                    {status.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Select value={partyTypeFilter} onValueChange={setPartyTypeFilter}>
              <SelectTrigger className="w-[150px]">
                <SelectValue placeholder="Party Type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Parties</SelectItem>
                {PARTY_TYPES.map((type) => (
                  <SelectItem key={type.value} value={type.value}>
                    {type.label}
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
          ) : filteredContracts.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              No contracts found. Click "New Contract" to create one.
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Contract Number</TableHead>
                  <TableHead>Title</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Party</TableHead>
                  <TableHead>Value</TableHead>
                  <TableHead>Effective Date</TableHead>
                  <TableHead>Expiry Date</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredContracts.map((contract) => (
                  <TableRow key={contract.id}>
                    <TableCell className="font-medium">{contract.contract_number}</TableCell>
                    <TableCell>
                      <div>
                        <p className="font-medium">{contract.title}</p>
                        {contract.auto_renewal && (
                          <Badge variant="outline" className="text-xs mt-1">
                            <RefreshCw className="h-3 w-3 mr-1" />
                            Auto-renewal
                          </Badge>
                        )}
                      </div>
                    </TableCell>
                    <TableCell>{getContractTypeBadge(contract.contract_type)}</TableCell>
                    <TableCell>
                      <div>
                        <p className="text-sm">{contract.party_name}</p>
                        <p className="text-xs text-muted-foreground capitalize">
                          {contract.party_type}
                        </p>
                      </div>
                    </TableCell>
                    <TableCell>{formatCurrency(contract.contract_value)}</TableCell>
                    <TableCell>{formatDate(contract.effective_date)}</TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        {isExpiringSoon(contract.expiry_date) && contract.status === "active" && (
                          <Clock className="h-4 w-4 text-orange-500" />
                        )}
                        <span
                          className={
                            isExpiringSoon(contract.expiry_date) && contract.status === "active"
                              ? "text-orange-600 font-medium"
                              : ""
                          }
                        >
                          {formatDate(contract.expiry_date)}
                        </span>
                      </div>
                    </TableCell>
                    <TableCell>{getStatusBadge(contract.status)}</TableCell>
                    <TableCell>
                      <div className="flex gap-2">
                        <Button variant="ghost" size="icon" onClick={() => handleViewContract(contract)}>
                          <Eye className="h-4 w-4" />
                        </Button>
                        <Button variant="ghost" size="icon" onClick={() => handleUploadDocument(contract)}>
                          <Upload className="h-4 w-4" />
                        </Button>
                        <Button variant="ghost" size="icon">
                          <Edit className="h-4 w-4" />
                        </Button>
                        {["expired", "terminated"].includes(contract.status) && (
                          <Button
                            variant="ghost"
                            size="icon"
                            className="text-red-600 hover:text-red-700 hover:bg-red-50"
                            onClick={() => handleDeleteClick(contract)}
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

      {/* View Contract Dialog */}
      <Dialog open={isViewDialogOpen} onOpenChange={setIsViewDialogOpen}>
        <DialogContent className="max-w-3xl">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <ScrollText className="h-5 w-5" />
              {selectedContract?.contract_number}
            </DialogTitle>
            <DialogDescription>{selectedContract?.title}</DialogDescription>
          </DialogHeader>
          {selectedContract && (
            <div className="grid gap-6 py-4">
              {/* Status and Type */}
              <div className="flex items-center gap-4">
                {getStatusBadge(selectedContract.status)}
                {getContractTypeBadge(selectedContract.contract_type)}
                {selectedContract.auto_renewal && (
                  <Badge variant="outline" className="text-blue-600 border-blue-300">
                    <RefreshCw className="h-3 w-3 mr-1" />
                    Auto-renewal
                  </Badge>
                )}
              </div>

              {/* Party Details */}
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1">
                  <Label className="text-xs text-muted-foreground">Party Name</Label>
                  <div className="flex items-center gap-2">
                    <Building2 className="h-4 w-4 text-muted-foreground" />
                    <span>{selectedContract.party_name}</span>
                  </div>
                </div>
                <div className="space-y-1">
                  <Label className="text-xs text-muted-foreground">Party Type</Label>
                  <div className="flex items-center gap-2">
                    <User className="h-4 w-4 text-muted-foreground" />
                    <span className="capitalize">{selectedContract.party_type}</span>
                  </div>
                </div>
              </div>

              {/* Dates */}
              <div className="grid grid-cols-3 gap-4">
                <div className="space-y-1">
                  <Label className="text-xs text-muted-foreground">Effective Date</Label>
                  <div className="flex items-center gap-2">
                    <Calendar className="h-4 w-4 text-muted-foreground" />
                    <span>{formatDate(selectedContract.effective_date)}</span>
                  </div>
                </div>
                <div className="space-y-1">
                  <Label className="text-xs text-muted-foreground">Expiry Date</Label>
                  <div className="flex items-center gap-2">
                    <Calendar className="h-4 w-4 text-muted-foreground" />
                    <span
                      className={
                        isExpiringSoon(selectedContract.expiry_date)
                          ? "text-orange-600 font-medium"
                          : ""
                      }
                    >
                      {formatDate(selectedContract.expiry_date)}
                    </span>
                  </div>
                </div>
                <div className="space-y-1">
                  <Label className="text-xs text-muted-foreground">Contract Value</Label>
                  <div className="flex items-center gap-2">
                    <IndianRupee className="h-4 w-4 text-muted-foreground" />
                    <span className="font-medium">
                      {formatCurrency(selectedContract.contract_value)}
                    </span>
                  </div>
                </div>
              </div>

              {/* Renewal Details */}
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1">
                  <Label className="text-xs text-muted-foreground">Renewal Type</Label>
                  <span className="capitalize">{selectedContract.renewal_type}</span>
                </div>
                <div className="space-y-1">
                  <Label className="text-xs text-muted-foreground">Reminder Before</Label>
                  <span>{selectedContract.renewal_reminder_days} days</span>
                </div>
              </div>

              {/* Terms Summary */}
              <div className="space-y-1">
                <Label className="text-xs text-muted-foreground">Terms Summary</Label>
                <div className="p-3 bg-muted/50 rounded-md text-sm">
                  {selectedContract.terms_summary || "No terms summary provided"}
                </div>
              </div>

              {/* Document */}
              {selectedContract.document_url && (
                <div className="space-y-1">
                  <Label className="text-xs text-muted-foreground">Contract Document</Label>
                  <div className="flex items-center gap-2 p-2 bg-muted/50 rounded-md">
                    <FileText className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm flex-1">Contract Document.pdf</span>
                    <Button variant="outline" size="sm">
                      <Download className="h-4 w-4 mr-1" />
                      Download
                    </Button>
                  </div>
                </div>
              )}
            </div>
          )}
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsViewDialogOpen(false)}>
              Close
            </Button>
            <Button>
              <Edit className="mr-2 h-4 w-4" />
              Edit Contract
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Upload Document Dialog */}
      <Dialog open={isUploadDialogOpen} onOpenChange={setIsUploadDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Upload Contract Document</DialogTitle>
            <DialogDescription>
              Upload the contract document for {selectedContract?.contract_number}
            </DialogDescription>
          </DialogHeader>
          <div className="py-4">
            <FileUpload
              label="Contract Document"
              name="contract_document"
              accept=".pdf,.doc,.docx"
              maxSize={10}
              value={uploadFiles}
              onChange={setUploadFiles}
              hint="Upload PDF or Word documents (max 10MB)"
            />
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsUploadDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleDocumentUpload} disabled={isSubmitting || uploadFiles.length === 0}>
              {isSubmitting ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Uploading...
                </>
              ) : (
                <>
                  <Upload className="mr-2 h-4 w-4" />
                  Upload
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
              Delete Contract
            </AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete <strong>{contractToDelete?.contract_number}</strong>?
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
