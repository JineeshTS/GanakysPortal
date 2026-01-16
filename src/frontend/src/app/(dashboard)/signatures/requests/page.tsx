"use client";

import { useState } from "react";
import Link from "next/link";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
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
import { useApi, useToast } from "@/hooks";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { cn } from "@/lib/utils";
import { format, formatDistanceToNow } from "date-fns";
import {
  Plus,
  Search,
  MoreHorizontal,
  Eye,
  Edit,
  Send,
  RefreshCw,
  XCircle,
  Trash2,
  Download,
  Copy,
  FileText,
  Clock,
  CheckCircle,
  AlertTriangle,
  User,
  Mail,
  Calendar,
  Paperclip,
  History,
  PenTool,
  Loader2,
} from "lucide-react";

// Types
interface Signer {
  id: string;
  name: string;
  email: string;
  role: string;
  order: number;
  status: "pending" | "viewed" | "signed" | "rejected" | "delegated";
  signedAt?: string;
}

interface SignatureRequest {
  id: string;
  requestNumber: string;
  subject: string;
  message: string;
  documentType: string;
  signatureType: string;
  requesterName: string;
  requesterEmail: string;
  status: "draft" | "pending" | "in_progress" | "completed" | "rejected" | "expired" | "cancelled";
  currentSignerOrder: number;
  totalSigners: number;
  completedSigners: number;
  signers: Signer[];
  documents: { name: string; size: string; pages: number }[];
  createdAt: string;
  sentAt?: string;
  expiresAt: string;
  completedAt?: string;
}

// Mock data
const mockRequests: SignatureRequest[] = [
  {
    id: "1",
    requestNumber: "SIG-2024-000156",
    subject: "Employment Contract - John Doe",
    message: "Please review and sign the employment contract for the Software Engineer position.",
    documentType: "contract",
    signatureType: "electronic",
    requesterName: "HR Department",
    requesterEmail: "hr@company.com",
    status: "in_progress",
    currentSignerOrder: 2,
    totalSigners: 3,
    completedSigners: 1,
    signers: [
      { id: "s1", name: "John Doe", email: "john@example.com", role: "Employee", order: 1, status: "signed", signedAt: "2024-06-15T10:30:00Z" },
      { id: "s2", name: "HR Manager", email: "hrm@company.com", role: "HR Approval", order: 2, status: "pending" },
      { id: "s3", name: "CEO", email: "ceo@company.com", role: "Final Approval", order: 3, status: "pending" },
    ],
    documents: [{ name: "Employment_Contract.pdf", size: "245 KB", pages: 8 }],
    createdAt: "2024-06-14T09:00:00Z",
    sentAt: "2024-06-14T09:30:00Z",
    expiresAt: "2024-06-28T23:59:59Z",
  },
  {
    id: "2",
    requestNumber: "SIG-2024-000155",
    subject: "Vendor Agreement - Tech Solutions",
    message: "Annual service agreement with Tech Solutions for IT support.",
    documentType: "agreement",
    signatureType: "digital",
    requesterName: "Procurement",
    requesterEmail: "procurement@company.com",
    status: "pending",
    currentSignerOrder: 1,
    totalSigners: 2,
    completedSigners: 0,
    signers: [
      { id: "s4", name: "Vendor Rep", email: "rep@techsolutions.com", role: "Vendor", order: 1, status: "viewed" },
      { id: "s5", name: "Legal Head", email: "legal@company.com", role: "Legal Approval", order: 2, status: "pending" },
    ],
    documents: [
      { name: "Vendor_Agreement.pdf", size: "512 KB", pages: 15 },
      { name: "Service_Terms.pdf", size: "128 KB", pages: 4 },
    ],
    createdAt: "2024-06-13T14:00:00Z",
    sentAt: "2024-06-13T14:30:00Z",
    expiresAt: "2024-06-27T23:59:59Z",
  },
  {
    id: "3",
    requestNumber: "SIG-2024-000154",
    subject: "NDA - Confidential Project",
    message: "Non-disclosure agreement for Project Phoenix.",
    documentType: "legal_document",
    signatureType: "electronic",
    requesterName: "Legal",
    requesterEmail: "legal@company.com",
    status: "completed",
    currentSignerOrder: 2,
    totalSigners: 2,
    completedSigners: 2,
    signers: [
      { id: "s6", name: "External Consultant", email: "consultant@external.com", role: "Consultant", order: 1, status: "signed", signedAt: "2024-06-12T11:00:00Z" },
      { id: "s7", name: "Project Manager", email: "pm@company.com", role: "Internal", order: 2, status: "signed", signedAt: "2024-06-12T14:30:00Z" },
    ],
    documents: [{ name: "NDA_Phoenix.pdf", size: "156 KB", pages: 3 }],
    createdAt: "2024-06-11T10:00:00Z",
    sentAt: "2024-06-11T10:30:00Z",
    expiresAt: "2024-06-25T23:59:59Z",
    completedAt: "2024-06-12T14:30:00Z",
  },
  {
    id: "4",
    requestNumber: "SIG-2024-000153",
    subject: "Board Resolution - Q2",
    message: "Board resolution for Q2 strategic decisions.",
    documentType: "legal_document",
    signatureType: "dsc",
    requesterName: "Company Secretary",
    requesterEmail: "cs@company.com",
    status: "rejected",
    currentSignerOrder: 2,
    totalSigners: 3,
    completedSigners: 1,
    signers: [
      { id: "s8", name: "Director 1", email: "d1@company.com", role: "Director", order: 1, status: "signed" },
      { id: "s9", name: "Director 2", email: "d2@company.com", role: "Director", order: 2, status: "rejected" },
      { id: "s10", name: "Chairman", email: "chairman@company.com", role: "Chairman", order: 3, status: "pending" },
    ],
    documents: [{ name: "Board_Resolution_Q2.pdf", size: "89 KB", pages: 2 }],
    createdAt: "2024-06-10T16:00:00Z",
    sentAt: "2024-06-10T16:30:00Z",
    expiresAt: "2024-06-24T23:59:59Z",
  },
  {
    id: "5",
    requestNumber: "SIG-2024-000152",
    subject: "Purchase Order - Office Equipment",
    message: "PO for new office furniture and equipment.",
    documentType: "purchase_order",
    signatureType: "electronic",
    requesterName: "Admin",
    requesterEmail: "admin@company.com",
    status: "draft",
    currentSignerOrder: 1,
    totalSigners: 2,
    completedSigners: 0,
    signers: [
      { id: "s11", name: "Finance Manager", email: "fm@company.com", role: "Finance Approval", order: 1, status: "pending" },
      { id: "s12", name: "Admin Head", email: "admin.head@company.com", role: "Admin Approval", order: 2, status: "pending" },
    ],
    documents: [{ name: "PO_Office_Equipment.pdf", size: "178 KB", pages: 2 }],
    createdAt: "2024-06-15T08:00:00Z",
    expiresAt: "2024-06-29T23:59:59Z",
  },
];

const documentTypes = [
  { value: "contract", label: "Contract" },
  { value: "agreement", label: "Agreement" },
  { value: "purchase_order", label: "Purchase Order" },
  { value: "legal_document", label: "Legal Document" },
  { value: "hr_document", label: "HR Document" },
  { value: "other", label: "Other" },
];

const signatureTypes = [
  { value: "electronic", label: "Electronic Signature" },
  { value: "digital", label: "Digital Signature" },
  { value: "aadhaar_esign", label: "Aadhaar eSign" },
  { value: "dsc", label: "DSC Token" },
];

export default function SignatureRequestsPage() {
  const [requests, setRequests] = useState<SignatureRequest[]>(mockRequests);
  const [searchQuery, setSearchQuery] = useState("");
  const [filterStatus, setFilterStatus] = useState<string>("all");
  const [filterType, setFilterType] = useState<string>("all");
  const [selectedRequest, setSelectedRequest] = useState<SignatureRequest | null>(null);
  const [activeTab, setActiveTab] = useState("all");
  const { showToast } = useToast();
  const deleteApi = useApi();

  // Delete state
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [requestToDelete, setRequestToDelete] = useState<SignatureRequest | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  const handleDeleteClick = (request: SignatureRequest) => {
    setRequestToDelete(request);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!requestToDelete) return;
    setIsDeleting(true);
    try {
      await deleteApi.delete(`/signatures/requests/${requestToDelete.id}`);
      setRequests(requests.filter(r => r.id !== requestToDelete.id));
      setDeleteDialogOpen(false);
      setRequestToDelete(null);
      showToast("success", "Signature request deleted successfully");
    } catch (error) {
      console.error("Failed to delete signature request:", error);
      showToast("error", "Failed to delete signature request");
    } finally {
      setIsDeleting(false);
    }
  };

  // Filter requests
  const filteredRequests = requests.filter((request) => {
    const matchesSearch =
      request.requestNumber.toLowerCase().includes(searchQuery.toLowerCase()) ||
      request.subject.toLowerCase().includes(searchQuery.toLowerCase()) ||
      request.requesterName.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = filterStatus === "all" || request.status === filterStatus;
    const matchesType = filterType === "all" || request.documentType === filterType;

    // Tab filtering
    let matchesTab = true;
    if (activeTab === "pending") {
      matchesTab = request.status === "pending" || request.status === "in_progress";
    } else if (activeTab === "completed") {
      matchesTab = request.status === "completed";
    } else if (activeTab === "draft") {
      matchesTab = request.status === "draft";
    }

    return matchesSearch && matchesStatus && matchesType && matchesTab;
  });

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "draft":
        return <Badge variant="outline">Draft</Badge>;
      case "pending":
        return <Badge className="bg-yellow-100 text-yellow-800">Pending</Badge>;
      case "in_progress":
        return <Badge className="bg-blue-100 text-blue-800">In Progress</Badge>;
      case "completed":
        return <Badge className="bg-green-100 text-green-800">Completed</Badge>;
      case "rejected":
        return <Badge className="bg-red-100 text-red-800">Rejected</Badge>;
      case "expired":
        return <Badge className="bg-gray-100 text-gray-800">Expired</Badge>;
      case "cancelled":
        return <Badge className="bg-gray-100 text-gray-800">Cancelled</Badge>;
      default:
        return <Badge variant="outline">{status}</Badge>;
    }
  };

  const getSignerStatusIcon = (status: string) => {
    switch (status) {
      case "signed":
        return <CheckCircle className="h-4 w-4 text-green-600" />;
      case "rejected":
        return <XCircle className="h-4 w-4 text-red-600" />;
      case "viewed":
        return <Eye className="h-4 w-4 text-blue-600" />;
      case "pending":
        return <Clock className="h-4 w-4 text-yellow-600" />;
      case "delegated":
        return <RefreshCw className="h-4 w-4 text-purple-600" />;
      default:
        return null;
    }
  };

  const getSignatureTypeBadge = (type: string) => {
    const config = signatureTypes.find((t) => t.value === type);
    return <Badge variant="outline">{config?.label || type}</Badge>;
  };

  // Summary stats
  const stats = {
    total: requests.length,
    draft: requests.filter((r) => r.status === "draft").length,
    pending: requests.filter((r) => r.status === "pending" || r.status === "in_progress").length,
    completed: requests.filter((r) => r.status === "completed").length,
  };

  return (
    <div className="flex flex-col gap-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Signature Requests</h1>
          <p className="text-muted-foreground">
            Manage and track document signature requests
          </p>
        </div>
        <Link href="/signatures/requests/new">
          <Button>
            <Plus className="mr-2 h-4 w-4" />
            New Request
          </Button>
        </Link>
      </div>

      {/* Summary Cards */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Requests</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.total}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Draft</CardTitle>
            <Edit className="h-4 w-4 text-gray-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.draft}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">In Progress</CardTitle>
            <Clock className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.pending}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Completed</CardTitle>
            <CheckCircle className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.completed}</div>
          </CardContent>
        </Card>
      </div>

      {/* Main Content */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <div className="flex items-center justify-between flex-wrap gap-4">
          <TabsList>
            <TabsTrigger value="all">All Requests</TabsTrigger>
            <TabsTrigger value="draft">Drafts</TabsTrigger>
            <TabsTrigger value="pending">In Progress</TabsTrigger>
            <TabsTrigger value="completed">Completed</TabsTrigger>
          </TabsList>

          {/* Filters */}
          <div className="flex items-center gap-2">
            <div className="relative">
              <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search requests..."
                className="pl-8 w-[200px]"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
            <Select value={filterStatus} onValueChange={setFilterStatus}>
              <SelectTrigger className="w-[130px]">
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="draft">Draft</SelectItem>
                <SelectItem value="pending">Pending</SelectItem>
                <SelectItem value="in_progress">In Progress</SelectItem>
                <SelectItem value="completed">Completed</SelectItem>
                <SelectItem value="rejected">Rejected</SelectItem>
              </SelectContent>
            </Select>
            <Select value={filterType} onValueChange={setFilterType}>
              <SelectTrigger className="w-[150px]">
                <SelectValue placeholder="Doc Type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Types</SelectItem>
                {documentTypes.map((type) => (
                  <SelectItem key={type.value} value={type.value}>
                    {type.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>

        <TabsContent value={activeTab} className="mt-4">
          <Card>
            <CardContent className="p-0">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Request</TableHead>
                    <TableHead>Type</TableHead>
                    <TableHead>Progress</TableHead>
                    <TableHead>Expires</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead className="w-[50px]"></TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredRequests.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={6} className="text-center py-8">
                        <div className="flex flex-col items-center gap-2">
                          <FileText className="h-8 w-8 text-muted-foreground" />
                          <p className="text-muted-foreground">No requests found</p>
                        </div>
                      </TableCell>
                    </TableRow>
                  ) : (
                    filteredRequests.map((request) => (
                      <TableRow key={request.id}>
                        <TableCell>
                          <div>
                            <div className="font-medium">{request.requestNumber}</div>
                            <div className="text-sm text-muted-foreground truncate max-w-[300px]">
                              {request.subject}
                            </div>
                            <div className="text-xs text-muted-foreground flex items-center gap-1 mt-1">
                              <User className="h-3 w-3" />
                              {request.requesterName}
                            </div>
                          </div>
                        </TableCell>
                        <TableCell>
                          <div className="space-y-1">
                            <Badge variant="outline">
                              {documentTypes.find((t) => t.value === request.documentType)?.label}
                            </Badge>
                            {getSignatureTypeBadge(request.signatureType)}
                          </div>
                        </TableCell>
                        <TableCell>
                          <div className="space-y-1">
                            <div className="flex items-center gap-2">
                              <Progress
                                value={(request.completedSigners / request.totalSigners) * 100}
                                className="h-2 w-20"
                              />
                              <span className="text-xs text-muted-foreground">
                                {request.completedSigners}/{request.totalSigners}
                              </span>
                            </div>
                            <div className="flex items-center gap-1">
                              {request.signers.slice(0, 3).map((signer) => (
                                <div key={signer.id} title={`${signer.name} - ${signer.status}`}>
                                  {getSignerStatusIcon(signer.status)}
                                </div>
                              ))}
                              {request.signers.length > 3 && (
                                <span className="text-xs text-muted-foreground">
                                  +{request.signers.length - 3}
                                </span>
                              )}
                            </div>
                          </div>
                        </TableCell>
                        <TableCell>
                          <div className="text-sm">
                            {format(new Date(request.expiresAt), "MMM d, yyyy")}
                          </div>
                          <div className="text-xs text-muted-foreground">
                            {formatDistanceToNow(new Date(request.expiresAt), { addSuffix: true })}
                          </div>
                        </TableCell>
                        <TableCell>{getStatusBadge(request.status)}</TableCell>
                        <TableCell>
                          <DropdownMenu>
                            <DropdownMenuTrigger asChild>
                              <Button variant="ghost" size="icon">
                                <MoreHorizontal className="h-4 w-4" />
                              </Button>
                            </DropdownMenuTrigger>
                            <DropdownMenuContent align="end">
                              <DropdownMenuItem onClick={() => setSelectedRequest(request)}>
                                <Eye className="mr-2 h-4 w-4" />
                                View Details
                              </DropdownMenuItem>
                              {request.status === "draft" && (
                                <>
                                  <DropdownMenuItem>
                                    <Edit className="mr-2 h-4 w-4" />
                                    Edit
                                  </DropdownMenuItem>
                                  <DropdownMenuItem>
                                    <Send className="mr-2 h-4 w-4" />
                                    Send for Signature
                                  </DropdownMenuItem>
                                </>
                              )}
                              {(request.status === "pending" || request.status === "in_progress") && (
                                <DropdownMenuItem>
                                  <RefreshCw className="mr-2 h-4 w-4" />
                                  Send Reminder
                                </DropdownMenuItem>
                              )}
                              <DropdownMenuItem>
                                <History className="mr-2 h-4 w-4" />
                                View History
                              </DropdownMenuItem>
                              <DropdownMenuItem>
                                <Download className="mr-2 h-4 w-4" />
                                Download Documents
                              </DropdownMenuItem>
                              <DropdownMenuItem>
                                <Copy className="mr-2 h-4 w-4" />
                                Duplicate
                              </DropdownMenuItem>
                              <DropdownMenuSeparator />
                              {request.status !== "completed" && request.status !== "cancelled" && (
                                <DropdownMenuItem className="text-red-600">
                                  <XCircle className="mr-2 h-4 w-4" />
                                  Cancel Request
                                </DropdownMenuItem>
                              )}
                              {(request.status === "completed" || request.status === "cancelled" || request.status === "expired" || request.status === "rejected") && (
                                <DropdownMenuItem
                                  className="text-red-600"
                                  onClick={() => handleDeleteClick(request)}
                                >
                                  <Trash2 className="mr-2 h-4 w-4" />
                                  Delete
                                </DropdownMenuItem>
                              )}
                            </DropdownMenuContent>
                          </DropdownMenu>
                        </TableCell>
                      </TableRow>
                    ))
                  )}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Request Detail Dialog */}
      <Dialog open={!!selectedRequest} onOpenChange={() => setSelectedRequest(null)}>
        <DialogContent className="max-w-3xl max-h-[90vh]">
          <DialogHeader>
            <div className="flex items-center justify-between">
              <div>
                <DialogTitle>{selectedRequest?.requestNumber}</DialogTitle>
                <DialogDescription>{selectedRequest?.subject}</DialogDescription>
              </div>
              {selectedRequest && getStatusBadge(selectedRequest.status)}
            </div>
          </DialogHeader>
          {selectedRequest && (
            <ScrollArea className="max-h-[65vh]">
              <div className="space-y-6 pr-4">
                {/* Request Info */}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label className="text-muted-foreground">Document Type</Label>
                    <div className="mt-1">
                      <Badge variant="outline">
                        {documentTypes.find((t) => t.value === selectedRequest.documentType)?.label}
                      </Badge>
                    </div>
                  </div>
                  <div>
                    <Label className="text-muted-foreground">Signature Type</Label>
                    <div className="mt-1">
                      {getSignatureTypeBadge(selectedRequest.signatureType)}
                    </div>
                  </div>
                  <div>
                    <Label className="text-muted-foreground">Requester</Label>
                    <div className="mt-1 font-medium">{selectedRequest.requesterName}</div>
                    <div className="text-sm text-muted-foreground">{selectedRequest.requesterEmail}</div>
                  </div>
                  <div>
                    <Label className="text-muted-foreground">Expires</Label>
                    <div className="mt-1 font-medium">
                      {format(new Date(selectedRequest.expiresAt), "PPP")}
                    </div>
                  </div>
                </div>

                {selectedRequest.message && (
                  <div>
                    <Label className="text-muted-foreground">Message to Signers</Label>
                    <p className="mt-1">{selectedRequest.message}</p>
                  </div>
                )}

                <Separator />

                {/* Documents */}
                <div>
                  <Label className="text-muted-foreground mb-2 block">Documents</Label>
                  <div className="space-y-2">
                    {selectedRequest.documents.map((doc, index) => (
                      <div
                        key={index}
                        className="flex items-center justify-between p-3 border rounded-lg"
                      >
                        <div className="flex items-center gap-3">
                          <FileText className="h-5 w-5 text-blue-600" />
                          <div>
                            <div className="font-medium">{doc.name}</div>
                            <div className="text-xs text-muted-foreground">
                              {doc.size} | {doc.pages} pages
                            </div>
                          </div>
                        </div>
                        <Button variant="ghost" size="sm">
                          <Download className="h-4 w-4" />
                        </Button>
                      </div>
                    ))}
                  </div>
                </div>

                <Separator />

                {/* Signers */}
                <div>
                  <Label className="text-muted-foreground mb-2 block">Signers</Label>
                  <div className="space-y-3">
                    {selectedRequest.signers.map((signer, index) => (
                      <div key={signer.id} className="flex items-start gap-4">
                        <div className="flex flex-col items-center">
                          <div className={cn(
                            "w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium",
                            signer.status === "signed" ? "bg-green-100 text-green-800" :
                            signer.status === "rejected" ? "bg-red-100 text-red-800" :
                            signer.status === "viewed" ? "bg-blue-100 text-blue-800" :
                            "bg-gray-100 text-gray-800"
                          )}>
                            {signer.order}
                          </div>
                          {index < selectedRequest.signers.length - 1 && (
                            <div className="w-0.5 h-8 bg-gray-200 mt-1" />
                          )}
                        </div>
                        <div className="flex-1 pb-2">
                          <div className="flex items-center justify-between">
                            <div>
                              <div className="font-medium">{signer.name}</div>
                              <div className="text-sm text-muted-foreground">{signer.email}</div>
                              <Badge variant="outline" className="mt-1">{signer.role}</Badge>
                            </div>
                            <div className="flex items-center gap-2">
                              {getSignerStatusIcon(signer.status)}
                              <span className="text-sm capitalize">{signer.status}</span>
                            </div>
                          </div>
                          {signer.signedAt && (
                            <div className="text-xs text-muted-foreground mt-1">
                              Signed: {format(new Date(signer.signedAt), "PPp")}
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Timestamps */}
                <div className="flex gap-4 text-xs text-muted-foreground pt-4">
                  <div>Created: {format(new Date(selectedRequest.createdAt), "PPp")}</div>
                  {selectedRequest.sentAt && (
                    <div>Sent: {format(new Date(selectedRequest.sentAt), "PPp")}</div>
                  )}
                  {selectedRequest.completedAt && (
                    <div>Completed: {format(new Date(selectedRequest.completedAt), "PPp")}</div>
                  )}
                </div>
              </div>
            </ScrollArea>
          )}
          <DialogFooter>
            <Button variant="outline" onClick={() => setSelectedRequest(null)}>
              Close
            </Button>
            <Button variant="outline">
              <History className="mr-2 h-4 w-4" />
              Audit Trail
            </Button>
            {selectedRequest?.status === "completed" && (
              <Button>
                <Download className="mr-2 h-4 w-4" />
                Download Signed
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
              Delete Signature Request
            </AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete <strong>{requestToDelete?.requestNumber}</strong> ({requestToDelete?.subject})?
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
