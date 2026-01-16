"use client";

import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
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
import { Textarea } from "@/components/ui/textarea";
import { useApi, useToast } from "@/hooks";
import { Switch } from "@/components/ui/switch";
import { format } from "date-fns";
import {
  Plus,
  Search,
  MoreHorizontal,
  Eye,
  Edit,
  Copy,
  Trash2,
  FileSignature,
  FileText,
  Users,
  Clock,
  CheckCircle,
  Settings,
  PenTool,
  Shield,
  Loader2,
  AlertTriangle,
} from "lucide-react";

// Types
interface SignerRole {
  roleName: string;
  order: number;
  required: boolean;
  allowDelegation: boolean;
}

interface SignatureTemplate {
  id: string;
  name: string;
  templateCode: string;
  description: string;
  documentType: string;
  signatureType: string;
  signerRoles: SignerRole[];
  signingOrder: string;
  expiryDays: number;
  reminderFrequencyDays: number;
  allowDecline: boolean;
  allowDelegation: boolean;
  requireOtp: boolean;
  requireAadhaar: boolean;
  isActive: boolean;
  version: number;
  usageCount: number;
  createdAt: string;
  updatedAt: string;
}

// Mock data
const mockTemplates: SignatureTemplate[] = [
  {
    id: "1",
    name: "Standard Employment Contract",
    templateCode: "EMP-CONTRACT",
    description: "Template for standard employment contracts with HR and management approval",
    documentType: "contract",
    signatureType: "electronic",
    signerRoles: [
      { roleName: "Employee", order: 1, required: true, allowDelegation: false },
      { roleName: "HR Manager", order: 2, required: true, allowDelegation: true },
      { roleName: "Department Head", order: 3, required: true, allowDelegation: true },
    ],
    signingOrder: "sequential",
    expiryDays: 14,
    reminderFrequencyDays: 3,
    allowDecline: true,
    allowDelegation: true,
    requireOtp: false,
    requireAadhaar: false,
    isActive: true,
    version: 3,
    usageCount: 45,
    createdAt: "2024-01-15T10:00:00Z",
    updatedAt: "2024-05-20T14:30:00Z",
  },
  {
    id: "2",
    name: "Vendor Agreement",
    templateCode: "VENDOR-AGR",
    description: "Standard vendor agreement template with legal review",
    documentType: "agreement",
    signatureType: "digital",
    signerRoles: [
      { roleName: "Vendor Representative", order: 1, required: true, allowDelegation: false },
      { roleName: "Procurement Manager", order: 2, required: true, allowDelegation: true },
      { roleName: "Legal Head", order: 3, required: true, allowDelegation: false },
    ],
    signingOrder: "sequential",
    expiryDays: 30,
    reminderFrequencyDays: 5,
    allowDecline: true,
    allowDelegation: false,
    requireOtp: false,
    requireAadhaar: false,
    isActive: true,
    version: 2,
    usageCount: 28,
    createdAt: "2024-02-01T09:00:00Z",
    updatedAt: "2024-04-15T11:00:00Z",
  },
  {
    id: "3",
    name: "NDA - Standard",
    templateCode: "NDA-STD",
    description: "Non-disclosure agreement for external parties",
    documentType: "legal_document",
    signatureType: "electronic",
    signerRoles: [
      { roleName: "External Party", order: 1, required: true, allowDelegation: false },
      { roleName: "Company Representative", order: 2, required: true, allowDelegation: true },
    ],
    signingOrder: "parallel",
    expiryDays: 7,
    reminderFrequencyDays: 2,
    allowDecline: false,
    allowDelegation: false,
    requireOtp: true,
    requireAadhaar: false,
    isActive: true,
    version: 1,
    usageCount: 62,
    createdAt: "2024-01-01T08:00:00Z",
    updatedAt: "2024-01-01T08:00:00Z",
  },
  {
    id: "4",
    name: "Board Resolution",
    templateCode: "BOARD-RES",
    description: "Board resolution requiring DSC signatures from all directors",
    documentType: "legal_document",
    signatureType: "dsc",
    signerRoles: [
      { roleName: "Director 1", order: 1, required: true, allowDelegation: false },
      { roleName: "Director 2", order: 1, required: true, allowDelegation: false },
      { roleName: "Director 3", order: 1, required: true, allowDelegation: false },
      { roleName: "Chairman", order: 2, required: true, allowDelegation: false },
    ],
    signingOrder: "sequential",
    expiryDays: 5,
    reminderFrequencyDays: 1,
    allowDecline: false,
    allowDelegation: false,
    requireOtp: false,
    requireAadhaar: false,
    isActive: true,
    version: 1,
    usageCount: 8,
    createdAt: "2024-03-10T14:00:00Z",
    updatedAt: "2024-03-10T14:00:00Z",
  },
  {
    id: "5",
    name: "Purchase Order Approval",
    templateCode: "PO-APPROVE",
    description: "Purchase order requiring finance and admin approval",
    documentType: "purchase_order",
    signatureType: "electronic",
    signerRoles: [
      { roleName: "Finance Manager", order: 1, required: true, allowDelegation: true },
      { roleName: "Department Head", order: 2, required: true, allowDelegation: true },
    ],
    signingOrder: "sequential",
    expiryDays: 3,
    reminderFrequencyDays: 1,
    allowDecline: true,
    allowDelegation: true,
    requireOtp: false,
    requireAadhaar: false,
    isActive: false,
    version: 2,
    usageCount: 156,
    createdAt: "2024-01-20T16:00:00Z",
    updatedAt: "2024-06-01T09:00:00Z",
  },
];

const documentTypes = [
  { value: "contract", label: "Contract", icon: FileText },
  { value: "agreement", label: "Agreement", icon: FileSignature },
  { value: "legal_document", label: "Legal Document", icon: Shield },
  { value: "purchase_order", label: "Purchase Order", icon: FileText },
  { value: "hr_document", label: "HR Document", icon: Users },
  { value: "other", label: "Other", icon: FileText },
];

const signatureTypes = [
  { value: "electronic", label: "Electronic", icon: PenTool },
  { value: "digital", label: "Digital", icon: Shield },
  { value: "aadhaar_esign", label: "Aadhaar eSign", icon: FileSignature },
  { value: "dsc", label: "DSC Token", icon: Shield },
];

export default function SignatureTemplatesPage() {
  const [templates, setTemplates] = useState<SignatureTemplate[]>(mockTemplates);
  const [searchQuery, setSearchQuery] = useState("");
  const [filterDocType, setFilterDocType] = useState<string>("all");
  const [filterSignType, setFilterSignType] = useState<string>("all");
  const [selectedTemplate, setSelectedTemplate] = useState<SignatureTemplate | null>(null);
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const { showToast } = useToast();
  const deleteApi = useApi();

  // Delete state
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [templateToDelete, setTemplateToDelete] = useState<SignatureTemplate | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  const handleDeleteClick = (template: SignatureTemplate) => {
    setTemplateToDelete(template);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!templateToDelete) return;
    setIsDeleting(true);
    try {
      await deleteApi.delete(`/signatures/templates/${templateToDelete.id}`);
      setTemplates(templates.filter(t => t.id !== templateToDelete.id));
      setDeleteDialogOpen(false);
      setTemplateToDelete(null);
      showToast("success", "Template deleted successfully");
    } catch (error) {
      console.error("Failed to delete template:", error);
      showToast("error", "Failed to delete template");
    } finally {
      setIsDeleting(false);
    }
  };

  // Filter templates
  const filteredTemplates = templates.filter((template) => {
    const matchesSearch =
      template.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      template.templateCode.toLowerCase().includes(searchQuery.toLowerCase()) ||
      template.description.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesDocType = filterDocType === "all" || template.documentType === filterDocType;
    const matchesSignType = filterSignType === "all" || template.signatureType === filterSignType;
    return matchesSearch && matchesDocType && matchesSignType;
  });

  const getDocTypeConfig = (type: string) => {
    return documentTypes.find((t) => t.value === type) || documentTypes[0];
  };

  const getSignTypeConfig = (type: string) => {
    return signatureTypes.find((t) => t.value === type) || signatureTypes[0];
  };

  // Stats
  const stats = {
    total: templates.length,
    active: templates.filter((t) => t.isActive).length,
    totalUsage: templates.reduce((sum, t) => sum + t.usageCount, 0),
  };

  return (
    <div className="flex flex-col gap-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Signature Templates</h1>
          <p className="text-muted-foreground">
            Create and manage reusable signature workflow templates
          </p>
        </div>
        <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              Create Template
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>Create Signature Template</DialogTitle>
              <DialogDescription>
                Define a reusable template for signature workflows
              </DialogDescription>
            </DialogHeader>
            <div className="grid gap-4 py-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="name">Template Name</Label>
                  <Input id="name" placeholder="e.g., Employment Contract" />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="code">Template Code</Label>
                  <Input id="code" placeholder="e.g., EMP-CONTRACT" />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="description">Description</Label>
                <Textarea
                  id="description"
                  placeholder="Describe the purpose of this template"
                  rows={2}
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Document Type</Label>
                  <Select>
                    <SelectTrigger>
                      <SelectValue placeholder="Select type" />
                    </SelectTrigger>
                    <SelectContent>
                      {documentTypes.map((type) => (
                        <SelectItem key={type.value} value={type.value}>
                          {type.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label>Signature Type</Label>
                  <Select>
                    <SelectTrigger>
                      <SelectValue placeholder="Select type" />
                    </SelectTrigger>
                    <SelectContent>
                      {signatureTypes.map((type) => (
                        <SelectItem key={type.value} value={type.value}>
                          {type.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="space-y-2">
                <Label>Signing Order</Label>
                <Select defaultValue="sequential">
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="sequential">Sequential (one after another)</SelectItem>
                    <SelectItem value="parallel">Parallel (all at once)</SelectItem>
                    <SelectItem value="any_order">Any Order</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label>Signer Roles</Label>
                <div className="border rounded-lg p-4 space-y-3">
                  {[1, 2].map((order) => (
                    <div key={order} className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-full bg-muted flex items-center justify-center text-sm font-medium">
                        {order}
                      </div>
                      <Input placeholder={`Role name (e.g., Employee, Manager)`} className="flex-1" />
                      <div className="flex items-center gap-2">
                        <Switch id={`required-${order}`} defaultChecked />
                        <Label htmlFor={`required-${order}`} className="text-sm">Required</Label>
                      </div>
                    </div>
                  ))}
                  <Button variant="outline" size="sm" className="w-full">
                    <Plus className="h-4 w-4 mr-2" />
                    Add Role
                  </Button>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="expiry">Expiry (days)</Label>
                  <Input id="expiry" type="number" defaultValue="14" />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="reminder">Reminder Frequency (days)</Label>
                  <Input id="reminder" type="number" defaultValue="3" />
                </div>
              </div>

              <div className="space-y-3">
                <Label>Options</Label>
                <div className="grid grid-cols-2 gap-4">
                  <div className="flex items-center space-x-2">
                    <Switch id="allowDecline" defaultChecked />
                    <Label htmlFor="allowDecline">Allow Decline</Label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Switch id="allowDelegation" />
                    <Label htmlFor="allowDelegation">Allow Delegation</Label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Switch id="requireOtp" />
                    <Label htmlFor="requireOtp">Require OTP</Label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Switch id="requireAadhaar" />
                    <Label htmlFor="requireAadhaar">Require Aadhaar</Label>
                  </div>
                </div>
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setIsCreateDialogOpen(false)}>
                Cancel
              </Button>
              <Button onClick={() => setIsCreateDialogOpen(false)}>Create Template</Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      {/* Summary Cards */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Templates</CardTitle>
            <FileSignature className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.total}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Templates</CardTitle>
            <CheckCircle className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.active}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Usage</CardTitle>
            <Users className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalUsage}</div>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-4">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search templates..."
            className="pl-8"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
        <Select value={filterDocType} onValueChange={setFilterDocType}>
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
        <Select value={filterSignType} onValueChange={setFilterSignType}>
          <SelectTrigger className="w-[150px]">
            <SelectValue placeholder="Sign Type" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Types</SelectItem>
            {signatureTypes.map((type) => (
              <SelectItem key={type.value} value={type.value}>
                {type.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Templates Table */}
      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Template</TableHead>
                <TableHead>Types</TableHead>
                <TableHead>Signers</TableHead>
                <TableHead>Settings</TableHead>
                <TableHead>Usage</TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="w-[50px]"></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredTemplates.map((template) => {
                const docType = getDocTypeConfig(template.documentType);
                const signType = getSignTypeConfig(template.signatureType);
                const DocIcon = docType.icon;
                const SignIcon = signType.icon;

                return (
                  <TableRow key={template.id}>
                    <TableCell>
                      <div>
                        <div className="font-medium">{template.name}</div>
                        <div className="text-sm text-muted-foreground">{template.templateCode}</div>
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="space-y-1">
                        <div className="flex items-center gap-1">
                          <DocIcon className="h-3 w-3" />
                          <span className="text-sm">{docType.label}</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <SignIcon className="h-3 w-3" />
                          <span className="text-sm">{signType.label}</span>
                        </div>
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-1">
                        <Users className="h-4 w-4 text-muted-foreground" />
                        <span>{template.signerRoles.length}</span>
                      </div>
                      <div className="text-xs text-muted-foreground capitalize">
                        {template.signingOrder}
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="flex flex-wrap gap-1">
                        <Badge variant="outline" className="text-xs">
                          <Clock className="h-3 w-3 mr-1" />
                          {template.expiryDays}d
                        </Badge>
                        {template.requireOtp && (
                          <Badge variant="outline" className="text-xs">OTP</Badge>
                        )}
                        {template.allowDelegation && (
                          <Badge variant="outline" className="text-xs">Delegate</Badge>
                        )}
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="font-medium">{template.usageCount}</div>
                      <div className="text-xs text-muted-foreground">v{template.version}</div>
                    </TableCell>
                    <TableCell>
                      {template.isActive ? (
                        <Badge className="bg-green-100 text-green-800">Active</Badge>
                      ) : (
                        <Badge variant="outline">Inactive</Badge>
                      )}
                    </TableCell>
                    <TableCell>
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="icon">
                            <MoreHorizontal className="h-4 w-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuItem onClick={() => setSelectedTemplate(template)}>
                            <Eye className="mr-2 h-4 w-4" />
                            View Details
                          </DropdownMenuItem>
                          <DropdownMenuItem>
                            <Edit className="mr-2 h-4 w-4" />
                            Edit
                          </DropdownMenuItem>
                          <DropdownMenuItem>
                            <Copy className="mr-2 h-4 w-4" />
                            Duplicate
                          </DropdownMenuItem>
                          <DropdownMenuItem>
                            <Settings className="mr-2 h-4 w-4" />
                            Configure Fields
                          </DropdownMenuItem>
                          <DropdownMenuSeparator />
                          {(!template.isActive || template.usageCount === 0) && (
                            <DropdownMenuItem
                              className="text-red-600"
                              onClick={() => handleDeleteClick(template)}
                            >
                              <Trash2 className="mr-2 h-4 w-4" />
                              Delete
                            </DropdownMenuItem>
                          )}
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Template Detail Dialog */}
      <Dialog open={!!selectedTemplate} onOpenChange={() => setSelectedTemplate(null)}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>{selectedTemplate?.name}</DialogTitle>
            <DialogDescription>{selectedTemplate?.templateCode}</DialogDescription>
          </DialogHeader>
          {selectedTemplate && (
            <div className="space-y-6">
              <p className="text-muted-foreground">{selectedTemplate.description}</p>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label className="text-muted-foreground">Document Type</Label>
                  <div className="mt-1 font-medium">
                    {getDocTypeConfig(selectedTemplate.documentType).label}
                  </div>
                </div>
                <div>
                  <Label className="text-muted-foreground">Signature Type</Label>
                  <div className="mt-1 font-medium">
                    {getSignTypeConfig(selectedTemplate.signatureType).label}
                  </div>
                </div>
                <div>
                  <Label className="text-muted-foreground">Signing Order</Label>
                  <div className="mt-1 font-medium capitalize">{selectedTemplate.signingOrder}</div>
                </div>
                <div>
                  <Label className="text-muted-foreground">Expiry</Label>
                  <div className="mt-1 font-medium">{selectedTemplate.expiryDays} days</div>
                </div>
              </div>

              <div>
                <Label className="text-muted-foreground mb-2 block">Signer Roles</Label>
                <div className="space-y-2">
                  {selectedTemplate.signerRoles.map((role, index) => (
                    <div key={index} className="flex items-center gap-3 p-3 bg-muted rounded-lg">
                      <div className="w-8 h-8 rounded-full bg-background flex items-center justify-center text-sm font-medium">
                        {role.order}
                      </div>
                      <div className="flex-1">
                        <div className="font-medium">{role.roleName}</div>
                        <div className="text-xs text-muted-foreground flex gap-2">
                          {role.required && <span>Required</span>}
                          {role.allowDelegation && <span>Can Delegate</span>}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="flex flex-wrap gap-2">
                {selectedTemplate.allowDecline && <Badge variant="outline">Allow Decline</Badge>}
                {selectedTemplate.allowDelegation && <Badge variant="outline">Allow Delegation</Badge>}
                {selectedTemplate.requireOtp && <Badge variant="outline">Require OTP</Badge>}
                {selectedTemplate.requireAadhaar && <Badge variant="outline">Require Aadhaar</Badge>}
              </div>

              <div className="flex gap-4 text-xs text-muted-foreground">
                <div>Version: {selectedTemplate.version}</div>
                <div>Usage: {selectedTemplate.usageCount} times</div>
                <div>Updated: {format(new Date(selectedTemplate.updatedAt), "PPP")}</div>
              </div>
            </div>
          )}
          <DialogFooter>
            <Button variant="outline" onClick={() => setSelectedTemplate(null)}>
              Close
            </Button>
            <Button>
              <Edit className="mr-2 h-4 w-4" />
              Edit Template
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
              Delete Template
            </AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete <strong>{templateToDelete?.name}</strong> ({templateToDelete?.templateCode})?
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
