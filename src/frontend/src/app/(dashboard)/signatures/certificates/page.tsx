"use client";

import { useState } from "react";
import Link from "next/link";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
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
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
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
import { Textarea } from "@/components/ui/textarea";
import {
  Shield,
  Plus,
  Search,
  MoreHorizontal,
  ArrowLeft,
  Key,
  Calendar,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Clock,
  Upload,
  Download,
  RefreshCw,
  Eye,
  Trash2,
  FileText,
  User,
  Users,
  Building,
  ShieldCheck,
  ShieldAlert,
  Lock,
  Loader2,
} from "lucide-react";

// Types
interface Certificate {
  id: string;
  name: string;
  type: string;
  holder_name: string;
  holder_type: string;
  serial_number: string;
  issuer: string;
  issued_at: string;
  expires_at: string;
  status: string;
  provider: string;
  usage_count: number;
}

// Mock data
const mockCertificates: Certificate[] = [
  {
    id: "1",
    name: "Organization DSC - Class 3",
    type: "class_3",
    holder_name: "Ganakys Technologies Pvt Ltd",
    holder_type: "organization",
    serial_number: "DSC-2024-ORG-001234",
    issuer: "eMudhra Limited",
    issued_at: "2024-01-15",
    expires_at: "2026-01-15",
    status: "active",
    provider: "eMudhra",
    usage_count: 156,
  },
  {
    id: "2",
    name: "Amit Patel - Authorized Signatory",
    type: "class_2",
    holder_name: "Amit Patel",
    holder_type: "individual",
    serial_number: "DSC-2024-IND-005678",
    issuer: "Sify Technologies",
    issued_at: "2024-03-10",
    expires_at: "2025-03-10",
    status: "active",
    provider: "Sify",
    usage_count: 89,
  },
  {
    id: "3",
    name: "Priya Sharma - Finance Head",
    type: "class_2",
    holder_name: "Priya Sharma",
    holder_type: "individual",
    serial_number: "DSC-2024-IND-009012",
    issuer: "NSDL e-Gov",
    issued_at: "2024-02-20",
    expires_at: "2025-02-20",
    status: "expiring_soon",
    provider: "NSDL",
    usage_count: 45,
  },
  {
    id: "4",
    name: "Aadhaar eSign - Employee Onboarding",
    type: "aadhaar",
    holder_name: "HR Department",
    holder_type: "department",
    serial_number: "AADH-2024-001",
    issuer: "UIDAI via NSDL",
    issued_at: "2024-01-01",
    expires_at: "2024-12-31",
    status: "active",
    provider: "NSDL eSign",
    usage_count: 234,
  },
  {
    id: "5",
    name: "Old Finance Certificate",
    type: "class_2",
    holder_name: "Rajesh Kumar",
    holder_type: "individual",
    serial_number: "DSC-2023-IND-003456",
    issuer: "eMudhra Limited",
    issued_at: "2022-06-15",
    expires_at: "2024-06-15",
    status: "expired",
    provider: "eMudhra",
    usage_count: 78,
  },
  {
    id: "6",
    name: "Legal Team Certificate",
    type: "class_3",
    holder_name: "Legal Department",
    holder_type: "department",
    serial_number: "DSC-2024-DEP-007890",
    issuer: "Capricorn Identity Services",
    issued_at: "2024-04-01",
    expires_at: "2026-04-01",
    status: "revoked",
    provider: "Capricorn",
    usage_count: 12,
  },
];

const certificateStats = {
  total: 6,
  active: 3,
  expiringSoon: 1,
  expired: 1,
  revoked: 1,
};

export default function CertificatesPage() {
  const [certificates, setCertificates] = useState<Certificate[]>(mockCertificates);
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [typeFilter, setTypeFilter] = useState("all");
  const [isAddDialogOpen, setIsAddDialogOpen] = useState(false);
  const [isViewDialogOpen, setIsViewDialogOpen] = useState(false);
  const [selectedCertificate, setSelectedCertificate] = useState<Certificate | null>(null);
  const { showToast } = useToast();
  const deleteApi = useApi();

  // Delete state
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [certToDelete, setCertToDelete] = useState<Certificate | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  const handleDeleteClick = (cert: Certificate) => {
    setCertToDelete(cert);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!certToDelete) return;
    setIsDeleting(true);
    try {
      await deleteApi.delete(`/signatures/certificates/${certToDelete.id}`);
      setCertificates(certificates.filter(c => c.id !== certToDelete.id));
      setDeleteDialogOpen(false);
      setCertToDelete(null);
      showToast("success", "Certificate deleted successfully");
    } catch (error) {
      console.error("Failed to delete certificate:", error);
      showToast("error", "Failed to delete certificate");
    } finally {
      setIsDeleting(false);
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "active":
        return <Badge className="bg-green-100 text-green-800">Active</Badge>;
      case "expiring_soon":
        return <Badge className="bg-yellow-100 text-yellow-800">Expiring Soon</Badge>;
      case "expired":
        return <Badge className="bg-red-100 text-red-800">Expired</Badge>;
      case "revoked":
        return <Badge className="bg-gray-100 text-gray-800">Revoked</Badge>;
      case "pending":
        return <Badge className="bg-blue-100 text-blue-800">Pending</Badge>;
      default:
        return <Badge variant="outline">{status}</Badge>;
    }
  };

  const getTypeBadge = (type: string) => {
    switch (type) {
      case "class_1":
        return <Badge variant="outline" className="border-blue-300 text-blue-700">Class 1</Badge>;
      case "class_2":
        return <Badge variant="outline" className="border-purple-300 text-purple-700">Class 2</Badge>;
      case "class_3":
        return <Badge variant="outline" className="border-green-300 text-green-700">Class 3</Badge>;
      case "aadhaar":
        return <Badge variant="outline" className="border-orange-300 text-orange-700">Aadhaar</Badge>;
      default:
        return <Badge variant="outline">{type}</Badge>;
    }
  };

  const getHolderIcon = (holderType: string) => {
    switch (holderType) {
      case "individual":
        return <User className="h-4 w-4 text-blue-600" />;
      case "organization":
        return <Building className="h-4 w-4 text-purple-600" />;
      case "department":
        return <Users className="h-4 w-4 text-green-600" />;
      default:
        return <User className="h-4 w-4" />;
    }
  };

  const filteredCertificates = certificates.filter((cert) => {
    const matchesSearch =
      cert.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      cert.holder_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      cert.serial_number.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = statusFilter === "all" || cert.status === statusFilter;
    const matchesType = typeFilter === "all" || cert.type === typeFilter;
    return matchesSearch && matchesStatus && matchesType;
  });

  const handleViewCertificate = (cert: Certificate) => {
    setSelectedCertificate(cert);
    setIsViewDialogOpen(true);
  };

  return (
    <div className="flex flex-col gap-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link href="/signatures">
            <Button variant="ghost" size="icon">
              <ArrowLeft className="h-4 w-4" />
            </Button>
          </Link>
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Digital Certificates</h1>
            <p className="text-muted-foreground">
              Manage digital signing certificates and DSC tokens
            </p>
          </div>
        </div>
        <Dialog open={isAddDialogOpen} onOpenChange={setIsAddDialogOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              Add Certificate
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>Add Digital Certificate</DialogTitle>
              <DialogDescription>
                Register a new digital signing certificate or DSC token
              </DialogDescription>
            </DialogHeader>
            <div className="grid gap-4 py-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="cert_name">Certificate Name</Label>
                  <Input id="cert_name" placeholder="e.g., Finance Team DSC" />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="cert_type">Certificate Type</Label>
                  <Select>
                    <SelectTrigger>
                      <SelectValue placeholder="Select type" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="class_1">Class 1 - Basic Verification</SelectItem>
                      <SelectItem value="class_2">Class 2 - Identity Verified</SelectItem>
                      <SelectItem value="class_3">Class 3 - In-Person Verified</SelectItem>
                      <SelectItem value="aadhaar">Aadhaar eSign</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="holder_type">Holder Type</Label>
                  <Select>
                    <SelectTrigger>
                      <SelectValue placeholder="Select holder type" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="individual">Individual</SelectItem>
                      <SelectItem value="organization">Organization</SelectItem>
                      <SelectItem value="department">Department</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="holder_name">Holder Name</Label>
                  <Input id="holder_name" placeholder="Certificate holder name" />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="serial_number">Serial Number</Label>
                  <Input id="serial_number" placeholder="Certificate serial number" />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="issuer">Issuer</Label>
                  <Input id="issuer" placeholder="e.g., eMudhra Limited" />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="issued_at">Issue Date</Label>
                  <Input id="issued_at" type="date" />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="expires_at">Expiry Date</Label>
                  <Input id="expires_at" type="date" />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="provider">Signature Provider</Label>
                <Select>
                  <SelectTrigger>
                    <SelectValue placeholder="Select provider" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="emudhra">eMudhra</SelectItem>
                    <SelectItem value="nsdl">NSDL e-Gov</SelectItem>
                    <SelectItem value="sify">Sify Technologies</SelectItem>
                    <SelectItem value="capricorn">Capricorn Identity</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label>Certificate File</Label>
                <div className="border-2 border-dashed rounded-lg p-6 text-center">
                  <Upload className="h-8 w-8 mx-auto text-muted-foreground mb-2" />
                  <p className="text-sm text-muted-foreground">
                    Drop certificate file here or click to upload
                  </p>
                  <p className="text-xs text-muted-foreground mt-1">
                    Supports .pfx, .p12, .cer formats
                  </p>
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="notes">Notes</Label>
                <Textarea id="notes" placeholder="Additional notes about this certificate" />
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setIsAddDialogOpen(false)}>
                Cancel
              </Button>
              <Button onClick={() => setIsAddDialogOpen(false)}>
                Add Certificate
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-5">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Certificates</CardTitle>
            <Shield className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{certificateStats.total}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active</CardTitle>
            <ShieldCheck className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{certificateStats.active}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Expiring Soon</CardTitle>
            <AlertTriangle className="h-4 w-4 text-yellow-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-600">{certificateStats.expiringSoon}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Expired</CardTitle>
            <XCircle className="h-4 w-4 text-red-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">{certificateStats.expired}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Revoked</CardTitle>
            <ShieldAlert className="h-4 w-4 text-gray-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-gray-600">{certificateStats.revoked}</div>
          </CardContent>
        </Card>
      </div>

      {/* Filters and Table */}
      <Card>
        <CardHeader>
          <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <div>
              <CardTitle>Certificates</CardTitle>
              <CardDescription>All registered digital certificates</CardDescription>
            </div>
            <div className="flex flex-col gap-2 md:flex-row md:items-center">
              <div className="relative">
                <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search certificates..."
                  className="pl-8 w-full md:w-[250px]"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </div>
              <Select value={statusFilter} onValueChange={setStatusFilter}>
                <SelectTrigger className="w-[140px]">
                  <SelectValue placeholder="Status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Status</SelectItem>
                  <SelectItem value="active">Active</SelectItem>
                  <SelectItem value="expiring_soon">Expiring Soon</SelectItem>
                  <SelectItem value="expired">Expired</SelectItem>
                  <SelectItem value="revoked">Revoked</SelectItem>
                </SelectContent>
              </Select>
              <Select value={typeFilter} onValueChange={setTypeFilter}>
                <SelectTrigger className="w-[140px]">
                  <SelectValue placeholder="Type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Types</SelectItem>
                  <SelectItem value="class_1">Class 1</SelectItem>
                  <SelectItem value="class_2">Class 2</SelectItem>
                  <SelectItem value="class_3">Class 3</SelectItem>
                  <SelectItem value="aadhaar">Aadhaar</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Certificate</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Holder</TableHead>
                <TableHead>Issuer</TableHead>
                <TableHead>Validity</TableHead>
                <TableHead>Usage</TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="w-[50px]"></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredCertificates.map((cert) => (
                <TableRow key={cert.id}>
                  <TableCell>
                    <div>
                      <div className="font-medium">{cert.name}</div>
                      <div className="text-xs text-muted-foreground font-mono">
                        {cert.serial_number}
                      </div>
                    </div>
                  </TableCell>
                  <TableCell>{getTypeBadge(cert.type)}</TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      {getHolderIcon(cert.holder_type)}
                      <span className="text-sm">{cert.holder_name}</span>
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="text-sm">{cert.issuer}</div>
                    <div className="text-xs text-muted-foreground">{cert.provider}</div>
                  </TableCell>
                  <TableCell>
                    <div className="text-sm">
                      <div className="flex items-center gap-1">
                        <Calendar className="h-3 w-3" />
                        {cert.issued_at}
                      </div>
                      <div className="text-xs text-muted-foreground">
                        Expires: {cert.expires_at}
                      </div>
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="text-sm font-medium">{cert.usage_count}</div>
                    <div className="text-xs text-muted-foreground">signatures</div>
                  </TableCell>
                  <TableCell>{getStatusBadge(cert.status)}</TableCell>
                  <TableCell>
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button variant="ghost" size="icon">
                          <MoreHorizontal className="h-4 w-4" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuItem onClick={() => handleViewCertificate(cert)}>
                          <Eye className="mr-2 h-4 w-4" />
                          View Details
                        </DropdownMenuItem>
                        <DropdownMenuItem>
                          <Download className="mr-2 h-4 w-4" />
                          Download Certificate
                        </DropdownMenuItem>
                        <DropdownMenuItem>
                          <RefreshCw className="mr-2 h-4 w-4" />
                          Renew Certificate
                        </DropdownMenuItem>
                        <DropdownMenuSeparator />
                        {cert.status === "active" && (
                          <DropdownMenuItem className="text-red-600">
                            <ShieldAlert className="mr-2 h-4 w-4" />
                            Revoke Certificate
                          </DropdownMenuItem>
                        )}
                        {(cert.status === "expired" || cert.status === "revoked") && (
                          <DropdownMenuItem
                            className="text-red-600"
                            onClick={() => handleDeleteClick(cert)}
                          >
                            <Trash2 className="mr-2 h-4 w-4" />
                            Delete
                          </DropdownMenuItem>
                        )}
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Certificate Types Info */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-3">
            <div className="flex items-center gap-2">
              <div className="p-2 bg-blue-100 rounded-lg">
                <Shield className="h-4 w-4 text-blue-600" />
              </div>
              <CardTitle className="text-sm">Class 1</CardTitle>
            </div>
          </CardHeader>
          <CardContent>
            <p className="text-xs text-muted-foreground">
              Basic verification, email-based identity confirmation. Suitable for low-risk documents.
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-3">
            <div className="flex items-center gap-2">
              <div className="p-2 bg-purple-100 rounded-lg">
                <ShieldCheck className="h-4 w-4 text-purple-600" />
              </div>
              <CardTitle className="text-sm">Class 2</CardTitle>
            </div>
          </CardHeader>
          <CardContent>
            <p className="text-xs text-muted-foreground">
              Database-verified identity. Required for GST, Income Tax, MCA filings.
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-3">
            <div className="flex items-center gap-2">
              <div className="p-2 bg-green-100 rounded-lg">
                <Lock className="h-4 w-4 text-green-600" />
              </div>
              <CardTitle className="text-sm">Class 3</CardTitle>
            </div>
          </CardHeader>
          <CardContent>
            <p className="text-xs text-muted-foreground">
              In-person verified identity. Highest assurance level for e-tendering, e-auctions.
            </p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-3">
            <div className="flex items-center gap-2">
              <div className="p-2 bg-orange-100 rounded-lg">
                <Key className="h-4 w-4 text-orange-600" />
              </div>
              <CardTitle className="text-sm">Aadhaar eSign</CardTitle>
            </div>
          </CardHeader>
          <CardContent>
            <p className="text-xs text-muted-foreground">
              OTP-based Aadhaar authentication. Legally valid for most documents under IT Act.
            </p>
          </CardContent>
        </Card>
      </div>

      {/* View Certificate Dialog */}
      <Dialog open={isViewDialogOpen} onOpenChange={setIsViewDialogOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Certificate Details</DialogTitle>
            <DialogDescription>
              Complete information about this digital certificate
            </DialogDescription>
          </DialogHeader>
          {selectedCertificate && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="p-3 bg-muted rounded-lg">
                    <Shield className="h-6 w-6" />
                  </div>
                  <div>
                    <h3 className="font-semibold">{selectedCertificate.name}</h3>
                    <p className="text-sm text-muted-foreground font-mono">
                      {selectedCertificate.serial_number}
                    </p>
                  </div>
                </div>
                {getStatusBadge(selectedCertificate.status)}
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1">
                  <Label className="text-xs text-muted-foreground">Certificate Type</Label>
                  <div>{getTypeBadge(selectedCertificate.type)}</div>
                </div>
                <div className="space-y-1">
                  <Label className="text-xs text-muted-foreground">Holder Type</Label>
                  <div className="flex items-center gap-2">
                    {getHolderIcon(selectedCertificate.holder_type)}
                    <span className="capitalize">{selectedCertificate.holder_type}</span>
                  </div>
                </div>
                <div className="space-y-1">
                  <Label className="text-xs text-muted-foreground">Holder Name</Label>
                  <div className="font-medium">{selectedCertificate.holder_name}</div>
                </div>
                <div className="space-y-1">
                  <Label className="text-xs text-muted-foreground">Issuing Authority</Label>
                  <div className="font-medium">{selectedCertificate.issuer}</div>
                </div>
                <div className="space-y-1">
                  <Label className="text-xs text-muted-foreground">Issue Date</Label>
                  <div className="flex items-center gap-2">
                    <Calendar className="h-4 w-4 text-muted-foreground" />
                    {selectedCertificate.issued_at}
                  </div>
                </div>
                <div className="space-y-1">
                  <Label className="text-xs text-muted-foreground">Expiry Date</Label>
                  <div className="flex items-center gap-2">
                    <Clock className="h-4 w-4 text-muted-foreground" />
                    {selectedCertificate.expires_at}
                  </div>
                </div>
                <div className="space-y-1">
                  <Label className="text-xs text-muted-foreground">Provider</Label>
                  <div>{selectedCertificate.provider}</div>
                </div>
                <div className="space-y-1">
                  <Label className="text-xs text-muted-foreground">Total Signatures</Label>
                  <div className="text-lg font-bold">{selectedCertificate.usage_count}</div>
                </div>
              </div>

              <div className="flex gap-2">
                <Button variant="outline" className="flex-1">
                  <Download className="mr-2 h-4 w-4" />
                  Download
                </Button>
                <Button variant="outline" className="flex-1">
                  <RefreshCw className="mr-2 h-4 w-4" />
                  Renew
                </Button>
                {selectedCertificate.status === "active" && (
                  <Button variant="destructive" className="flex-1">
                    <ShieldAlert className="mr-2 h-4 w-4" />
                    Revoke
                  </Button>
                )}
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-red-500" />
              Delete Certificate
            </AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete <strong>{certToDelete?.name}</strong>?
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
