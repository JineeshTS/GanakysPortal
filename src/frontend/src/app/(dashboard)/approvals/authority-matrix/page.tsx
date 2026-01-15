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
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Textarea } from "@/components/ui/textarea";
import { Switch } from "@/components/ui/switch";
import {
  Plus,
  Search,
  MoreHorizontal,
  Edit,
  Trash2,
  Users,
  Shield,
  DollarSign,
  FileText,
  Building,
  UserPlus,
  History,
  AlertTriangle,
  CheckCircle,
  Eye,
} from "lucide-react";

// Types
interface AuthorityHolder {
  id: string;
  userId: string;
  userName: string;
  userEmail: string;
  designation: string;
  department: string;
  isPrimary: boolean;
  canDelegate: boolean;
  maxDelegationDays: number;
  validFrom: string;
  validTo: string | null;
  status: "active" | "inactive" | "expired";
}

interface AuthorityMatrix {
  id: string;
  name: string;
  authorityCode: string;
  authorityType: "financial" | "operational" | "hr" | "procurement" | "legal" | "it" | "admin";
  description: string;
  transactionTypes: string[];
  minAmount: number | null;
  maxAmount: number | null;
  currency: string;
  requiresDocumentation: boolean;
  requiresJustification: boolean;
  riskLevel: "low" | "medium" | "high" | "critical";
  department: string | null;
  isActive: boolean;
  holders: AuthorityHolder[];
  createdAt: string;
  updatedAt: string;
}

// Mock data
const mockMatrices: AuthorityMatrix[] = [
  {
    id: "1",
    name: "Purchase Order Approval",
    authorityCode: "PO-APPROVE",
    authorityType: "procurement",
    description: "Authority to approve purchase orders within specified limits",
    transactionTypes: ["purchase_order", "vendor_payment"],
    minAmount: 0,
    maxAmount: 100000,
    currency: "INR",
    requiresDocumentation: true,
    requiresJustification: true,
    riskLevel: "medium",
    department: "Procurement",
    isActive: true,
    holders: [
      {
        id: "h1",
        userId: "u1",
        userName: "Rajesh Kumar",
        userEmail: "rajesh@company.com",
        designation: "Procurement Manager",
        department: "Procurement",
        isPrimary: true,
        canDelegate: true,
        maxDelegationDays: 14,
        validFrom: "2024-01-01",
        validTo: null,
        status: "active",
      },
      {
        id: "h2",
        userId: "u2",
        userName: "Priya Sharma",
        userEmail: "priya@company.com",
        designation: "Senior Buyer",
        department: "Procurement",
        isPrimary: false,
        canDelegate: false,
        maxDelegationDays: 0,
        validFrom: "2024-03-15",
        validTo: "2024-12-31",
        status: "active",
      },
    ],
    createdAt: "2024-01-01T00:00:00Z",
    updatedAt: "2024-06-15T10:30:00Z",
  },
  {
    id: "2",
    name: "Employee Expense Reimbursement",
    authorityCode: "EXP-REIMBURSE",
    authorityType: "financial",
    description: "Authority to approve employee expense reimbursements",
    transactionTypes: ["expense_claim", "travel_reimbursement"],
    minAmount: 0,
    maxAmount: 50000,
    currency: "INR",
    requiresDocumentation: true,
    requiresJustification: false,
    riskLevel: "low",
    department: "Finance",
    isActive: true,
    holders: [
      {
        id: "h3",
        userId: "u3",
        userName: "Amit Patel",
        userEmail: "amit@company.com",
        designation: "Finance Manager",
        department: "Finance",
        isPrimary: true,
        canDelegate: true,
        maxDelegationDays: 7,
        validFrom: "2024-01-01",
        validTo: null,
        status: "active",
      },
    ],
    createdAt: "2024-01-01T00:00:00Z",
    updatedAt: "2024-05-20T14:15:00Z",
  },
  {
    id: "3",
    name: "Contract Signing Authority",
    authorityCode: "CONTRACT-SIGN",
    authorityType: "legal",
    description: "Authority to sign contracts and legal agreements",
    transactionTypes: ["contract", "agreement", "mou"],
    minAmount: 0,
    maxAmount: 5000000,
    currency: "INR",
    requiresDocumentation: true,
    requiresJustification: true,
    riskLevel: "critical",
    department: "Legal",
    isActive: true,
    holders: [
      {
        id: "h4",
        userId: "u4",
        userName: "Sunita Verma",
        userEmail: "sunita@company.com",
        designation: "Legal Head",
        department: "Legal",
        isPrimary: true,
        canDelegate: false,
        maxDelegationDays: 0,
        validFrom: "2024-01-01",
        validTo: null,
        status: "active",
      },
    ],
    createdAt: "2024-01-01T00:00:00Z",
    updatedAt: "2024-04-10T09:00:00Z",
  },
  {
    id: "4",
    name: "Hiring Approval",
    authorityCode: "HIRE-APPROVE",
    authorityType: "hr",
    description: "Authority to approve new hire requisitions and offers",
    transactionTypes: ["hiring_request", "salary_offer"],
    minAmount: null,
    maxAmount: null,
    currency: "INR",
    requiresDocumentation: true,
    requiresJustification: true,
    riskLevel: "medium",
    department: "Human Resources",
    isActive: true,
    holders: [
      {
        id: "h5",
        userId: "u5",
        userName: "Meera Joshi",
        userEmail: "meera@company.com",
        designation: "HR Director",
        department: "Human Resources",
        isPrimary: true,
        canDelegate: true,
        maxDelegationDays: 10,
        validFrom: "2024-01-01",
        validTo: null,
        status: "active",
      },
    ],
    createdAt: "2024-02-01T00:00:00Z",
    updatedAt: "2024-06-01T11:45:00Z",
  },
];

const authorityTypes = [
  { value: "financial", label: "Financial", icon: DollarSign, color: "bg-green-100 text-green-800" },
  { value: "operational", label: "Operational", icon: Building, color: "bg-blue-100 text-blue-800" },
  { value: "hr", label: "Human Resources", icon: Users, color: "bg-purple-100 text-purple-800" },
  { value: "procurement", label: "Procurement", icon: FileText, color: "bg-orange-100 text-orange-800" },
  { value: "legal", label: "Legal", icon: Shield, color: "bg-red-100 text-red-800" },
  { value: "it", label: "IT", icon: Building, color: "bg-cyan-100 text-cyan-800" },
  { value: "admin", label: "Administrative", icon: Building, color: "bg-gray-100 text-gray-800" },
];

const riskLevels = [
  { value: "low", label: "Low", color: "bg-green-100 text-green-800" },
  { value: "medium", label: "Medium", color: "bg-yellow-100 text-yellow-800" },
  { value: "high", label: "High", color: "bg-orange-100 text-orange-800" },
  { value: "critical", label: "Critical", color: "bg-red-100 text-red-800" },
];

export default function AuthorityMatrixPage() {
  const [matrices, setMatrices] = useState<AuthorityMatrix[]>(mockMatrices);
  const [searchQuery, setSearchQuery] = useState("");
  const [filterType, setFilterType] = useState<string>("all");
  const [filterRisk, setFilterRisk] = useState<string>("all");
  const [selectedMatrix, setSelectedMatrix] = useState<AuthorityMatrix | null>(null);
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isHolderDialogOpen, setIsHolderDialogOpen] = useState(false);
  const [activeTab, setActiveTab] = useState("list");

  // Filter matrices
  const filteredMatrices = matrices.filter((matrix) => {
    const matchesSearch =
      matrix.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      matrix.authorityCode.toLowerCase().includes(searchQuery.toLowerCase()) ||
      matrix.description.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesType = filterType === "all" || matrix.authorityType === filterType;
    const matchesRisk = filterRisk === "all" || matrix.riskLevel === filterRisk;
    return matchesSearch && matchesType && matchesRisk;
  });

  const getAuthorityTypeConfig = (type: string) => {
    return authorityTypes.find((t) => t.value === type) || authorityTypes[0];
  };

  const getRiskLevelConfig = (level: string) => {
    return riskLevels.find((r) => r.value === level) || riskLevels[0];
  };

  const formatCurrency = (amount: number | null, currency: string) => {
    if (amount === null) return "N/A";
    return new Intl.NumberFormat("en-IN", {
      style: "currency",
      currency: currency,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "active":
        return <Badge className="bg-green-100 text-green-800">Active</Badge>;
      case "inactive":
        return <Badge className="bg-gray-100 text-gray-800">Inactive</Badge>;
      case "expired":
        return <Badge className="bg-red-100 text-red-800">Expired</Badge>;
      default:
        return <Badge variant="outline">{status}</Badge>;
    }
  };

  // Summary stats
  const stats = {
    total: matrices.length,
    active: matrices.filter((m) => m.isActive).length,
    totalHolders: matrices.reduce((sum, m) => sum + m.holders.length, 0),
    criticalAuthorities: matrices.filter((m) => m.riskLevel === "critical").length,
  };

  return (
    <div className="flex flex-col gap-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Authority Matrix</h1>
          <p className="text-muted-foreground">
            Define and manage delegation of authority across your organization
          </p>
        </div>
        <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              Create Authority
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>Create New Authority</DialogTitle>
              <DialogDescription>
                Define a new authority with approval limits and assign holders
              </DialogDescription>
            </DialogHeader>
            <div className="grid gap-4 py-4 max-h-[60vh] overflow-y-auto">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="name">Authority Name</Label>
                  <Input id="name" placeholder="e.g., Purchase Order Approval" />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="code">Authority Code</Label>
                  <Input id="code" placeholder="e.g., PO-APPROVE" />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="type">Authority Type</Label>
                  <Select>
                    <SelectTrigger>
                      <SelectValue placeholder="Select type" />
                    </SelectTrigger>
                    <SelectContent>
                      {authorityTypes.map((type) => (
                        <SelectItem key={type.value} value={type.value}>
                          {type.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="risk">Risk Level</Label>
                  <Select>
                    <SelectTrigger>
                      <SelectValue placeholder="Select risk level" />
                    </SelectTrigger>
                    <SelectContent>
                      {riskLevels.map((risk) => (
                        <SelectItem key={risk.value} value={risk.value}>
                          {risk.label}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="description">Description</Label>
                <Textarea
                  id="description"
                  placeholder="Describe the authority and its scope"
                  rows={3}
                />
              </div>

              <div className="grid grid-cols-3 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="minAmount">Minimum Amount</Label>
                  <Input id="minAmount" type="number" placeholder="0" />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="maxAmount">Maximum Amount</Label>
                  <Input id="maxAmount" type="number" placeholder="100000" />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="currency">Currency</Label>
                  <Select defaultValue="INR">
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="INR">INR</SelectItem>
                      <SelectItem value="USD">USD</SelectItem>
                      <SelectItem value="EUR">EUR</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="department">Department (Optional)</Label>
                <Select>
                  <SelectTrigger>
                    <SelectValue placeholder="Select department" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Departments</SelectItem>
                    <SelectItem value="finance">Finance</SelectItem>
                    <SelectItem value="procurement">Procurement</SelectItem>
                    <SelectItem value="hr">Human Resources</SelectItem>
                    <SelectItem value="legal">Legal</SelectItem>
                    <SelectItem value="it">IT</SelectItem>
                    <SelectItem value="operations">Operations</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Switch id="requiresDocs" defaultChecked />
                  <Label htmlFor="requiresDocs">Requires Documentation</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <Switch id="requiresJustification" />
                  <Label htmlFor="requiresJustification">Requires Justification</Label>
                </div>
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setIsCreateDialogOpen(false)}>
                Cancel
              </Button>
              <Button onClick={() => setIsCreateDialogOpen(false)}>Create Authority</Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      {/* Summary Cards */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Authorities</CardTitle>
            <Shield className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.total}</div>
            <p className="text-xs text-muted-foreground">Defined in matrix</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Authorities</CardTitle>
            <CheckCircle className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.active}</div>
            <p className="text-xs text-muted-foreground">Currently in use</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Authority Holders</CardTitle>
            <Users className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalHolders}</div>
            <p className="text-xs text-muted-foreground">Assigned users</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Critical Authorities</CardTitle>
            <AlertTriangle className="h-4 w-4 text-red-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.criticalAuthorities}</div>
            <p className="text-xs text-muted-foreground">High-risk items</p>
          </CardContent>
        </Card>
      </div>

      {/* Main Content */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <div className="flex items-center justify-between">
          <TabsList>
            <TabsTrigger value="list">Authority List</TabsTrigger>
            <TabsTrigger value="matrix">Matrix View</TabsTrigger>
            <TabsTrigger value="history">Change History</TabsTrigger>
          </TabsList>

          {/* Filters */}
          <div className="flex items-center gap-2">
            <div className="relative">
              <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search authorities..."
                className="pl-8 w-[250px]"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
            <Select value={filterType} onValueChange={setFilterType}>
              <SelectTrigger className="w-[150px]">
                <SelectValue placeholder="Type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Types</SelectItem>
                {authorityTypes.map((type) => (
                  <SelectItem key={type.value} value={type.value}>
                    {type.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Select value={filterRisk} onValueChange={setFilterRisk}>
              <SelectTrigger className="w-[130px]">
                <SelectValue placeholder="Risk" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Risks</SelectItem>
                {riskLevels.map((risk) => (
                  <SelectItem key={risk.value} value={risk.value}>
                    {risk.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>

        {/* Authority List */}
        <TabsContent value="list" className="mt-4">
          <Card>
            <CardContent className="p-0">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Authority</TableHead>
                    <TableHead>Type</TableHead>
                    <TableHead>Limits</TableHead>
                    <TableHead>Risk</TableHead>
                    <TableHead>Holders</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead className="w-[50px]"></TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredMatrices.map((matrix) => {
                    const typeConfig = getAuthorityTypeConfig(matrix.authorityType);
                    const riskConfig = getRiskLevelConfig(matrix.riskLevel);
                    const TypeIcon = typeConfig.icon;

                    return (
                      <TableRow key={matrix.id}>
                        <TableCell>
                          <div className="flex items-center gap-3">
                            <div className={`p-2 rounded-lg ${typeConfig.color}`}>
                              <TypeIcon className="h-4 w-4" />
                            </div>
                            <div>
                              <div className="font-medium">{matrix.name}</div>
                              <div className="text-sm text-muted-foreground">
                                {matrix.authorityCode}
                              </div>
                            </div>
                          </div>
                        </TableCell>
                        <TableCell>
                          <Badge variant="outline" className={typeConfig.color}>
                            {typeConfig.label}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <div className="text-sm">
                            {matrix.minAmount !== null && matrix.maxAmount !== null ? (
                              <>
                                <div>{formatCurrency(matrix.minAmount, matrix.currency)}</div>
                                <div className="text-muted-foreground">
                                  to {formatCurrency(matrix.maxAmount, matrix.currency)}
                                </div>
                              </>
                            ) : (
                              <span className="text-muted-foreground">No limit</span>
                            )}
                          </div>
                        </TableCell>
                        <TableCell>
                          <Badge className={riskConfig.color}>{riskConfig.label}</Badge>
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center gap-2">
                            <Users className="h-4 w-4 text-muted-foreground" />
                            <span>{matrix.holders.length}</span>
                          </div>
                        </TableCell>
                        <TableCell>
                          {matrix.isActive ? (
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
                              <DropdownMenuItem onClick={() => setSelectedMatrix(matrix)}>
                                <Eye className="mr-2 h-4 w-4" />
                                View Details
                              </DropdownMenuItem>
                              <DropdownMenuItem>
                                <Edit className="mr-2 h-4 w-4" />
                                Edit
                              </DropdownMenuItem>
                              <DropdownMenuItem onClick={() => setIsHolderDialogOpen(true)}>
                                <UserPlus className="mr-2 h-4 w-4" />
                                Manage Holders
                              </DropdownMenuItem>
                              <DropdownMenuItem>
                                <History className="mr-2 h-4 w-4" />
                                View History
                              </DropdownMenuItem>
                              <DropdownMenuItem className="text-red-600">
                                <Trash2 className="mr-2 h-4 w-4" />
                                Delete
                              </DropdownMenuItem>
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
        </TabsContent>

        {/* Matrix View */}
        <TabsContent value="matrix" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle>Authority Matrix Overview</CardTitle>
              <CardDescription>
                Visual representation of authorities by type and approval limits
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {authorityTypes.map((type) => {
                  const typeMatrices = matrices.filter((m) => m.authorityType === type.value);
                  const TypeIcon = type.icon;

                  return (
                    <Card key={type.value} className="overflow-hidden">
                      <CardHeader className={`${type.color} py-3`}>
                        <div className="flex items-center gap-2">
                          <TypeIcon className="h-5 w-5" />
                          <CardTitle className="text-base">{type.label}</CardTitle>
                        </div>
                      </CardHeader>
                      <CardContent className="p-4">
                        {typeMatrices.length === 0 ? (
                          <p className="text-sm text-muted-foreground text-center py-4">
                            No authorities defined
                          </p>
                        ) : (
                          <div className="space-y-3">
                            {typeMatrices.map((matrix) => (
                              <div
                                key={matrix.id}
                                className="flex items-center justify-between p-2 rounded-lg bg-muted/50"
                              >
                                <div>
                                  <div className="font-medium text-sm">{matrix.name}</div>
                                  <div className="text-xs text-muted-foreground">
                                    {matrix.holders.length} holder(s)
                                  </div>
                                </div>
                                <Badge
                                  className={getRiskLevelConfig(matrix.riskLevel).color}
                                  variant="outline"
                                >
                                  {matrix.riskLevel}
                                </Badge>
                              </div>
                            ))}
                          </div>
                        )}
                      </CardContent>
                    </Card>
                  );
                })}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Change History */}
        <TabsContent value="history" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle>Change History</CardTitle>
              <CardDescription>Audit trail of all changes to authority matrix</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {[
                  {
                    action: "Holder Added",
                    authority: "Purchase Order Approval",
                    details: "Priya Sharma added as secondary holder",
                    user: "Admin User",
                    date: "2024-06-15 10:30",
                  },
                  {
                    action: "Limit Updated",
                    authority: "Employee Expense Reimbursement",
                    details: "Maximum limit increased from ₹30,000 to ₹50,000",
                    user: "Finance Manager",
                    date: "2024-05-20 14:15",
                  },
                  {
                    action: "Authority Created",
                    authority: "Hiring Approval",
                    details: "New authority created for HR requisitions",
                    user: "Admin User",
                    date: "2024-02-01 09:00",
                  },
                  {
                    action: "Holder Removed",
                    authority: "Contract Signing Authority",
                    details: "Previous holder access revoked due to role change",
                    user: "Legal Head",
                    date: "2024-01-15 16:45",
                  },
                ].map((log, index) => (
                  <div
                    key={index}
                    className="flex items-start gap-4 p-4 rounded-lg border bg-card"
                  >
                    <div className="p-2 rounded-full bg-muted">
                      <History className="h-4 w-4" />
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center justify-between">
                        <div className="font-medium">{log.action}</div>
                        <div className="text-sm text-muted-foreground">{log.date}</div>
                      </div>
                      <div className="text-sm text-muted-foreground mt-1">
                        <span className="font-medium text-foreground">{log.authority}</span>
                        {" - "}
                        {log.details}
                      </div>
                      <div className="text-xs text-muted-foreground mt-2">By {log.user}</div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Authority Detail Dialog */}
      <Dialog open={!!selectedMatrix} onOpenChange={() => setSelectedMatrix(null)}>
        <DialogContent className="max-w-3xl">
          <DialogHeader>
            <DialogTitle>{selectedMatrix?.name}</DialogTitle>
            <DialogDescription>
              Code: {selectedMatrix?.authorityCode}
            </DialogDescription>
          </DialogHeader>
          {selectedMatrix && (
            <div className="space-y-6">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label className="text-muted-foreground">Type</Label>
                  <div className="mt-1">
                    <Badge className={getAuthorityTypeConfig(selectedMatrix.authorityType).color}>
                      {getAuthorityTypeConfig(selectedMatrix.authorityType).label}
                    </Badge>
                  </div>
                </div>
                <div>
                  <Label className="text-muted-foreground">Risk Level</Label>
                  <div className="mt-1">
                    <Badge className={getRiskLevelConfig(selectedMatrix.riskLevel).color}>
                      {getRiskLevelConfig(selectedMatrix.riskLevel).label}
                    </Badge>
                  </div>
                </div>
                <div>
                  <Label className="text-muted-foreground">Approval Limits</Label>
                  <div className="mt-1 font-medium">
                    {formatCurrency(selectedMatrix.minAmount, selectedMatrix.currency)} -{" "}
                    {formatCurrency(selectedMatrix.maxAmount, selectedMatrix.currency)}
                  </div>
                </div>
                <div>
                  <Label className="text-muted-foreground">Department</Label>
                  <div className="mt-1 font-medium">
                    {selectedMatrix.department || "All Departments"}
                  </div>
                </div>
              </div>

              <div>
                <Label className="text-muted-foreground">Description</Label>
                <p className="mt-1">{selectedMatrix.description}</p>
              </div>

              <div className="flex gap-4">
                <div className="flex items-center gap-2">
                  {selectedMatrix.requiresDocumentation ? (
                    <CheckCircle className="h-4 w-4 text-green-600" />
                  ) : (
                    <div className="h-4 w-4 rounded-full border-2" />
                  )}
                  <span className="text-sm">Requires Documentation</span>
                </div>
                <div className="flex items-center gap-2">
                  {selectedMatrix.requiresJustification ? (
                    <CheckCircle className="h-4 w-4 text-green-600" />
                  ) : (
                    <div className="h-4 w-4 rounded-full border-2" />
                  )}
                  <span className="text-sm">Requires Justification</span>
                </div>
              </div>

              <div>
                <Label className="text-muted-foreground mb-2 block">Authority Holders</Label>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Name</TableHead>
                      <TableHead>Designation</TableHead>
                      <TableHead>Type</TableHead>
                      <TableHead>Can Delegate</TableHead>
                      <TableHead>Status</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {selectedMatrix.holders.map((holder) => (
                      <TableRow key={holder.id}>
                        <TableCell>
                          <div>
                            <div className="font-medium">{holder.userName}</div>
                            <div className="text-sm text-muted-foreground">{holder.userEmail}</div>
                          </div>
                        </TableCell>
                        <TableCell>{holder.designation}</TableCell>
                        <TableCell>
                          {holder.isPrimary ? (
                            <Badge className="bg-blue-100 text-blue-800">Primary</Badge>
                          ) : (
                            <Badge variant="outline">Secondary</Badge>
                          )}
                        </TableCell>
                        <TableCell>
                          {holder.canDelegate ? (
                            <span className="text-green-600">Yes ({holder.maxDelegationDays} days)</span>
                          ) : (
                            <span className="text-muted-foreground">No</span>
                          )}
                        </TableCell>
                        <TableCell>{getStatusBadge(holder.status)}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            </div>
          )}
          <DialogFooter>
            <Button variant="outline" onClick={() => setSelectedMatrix(null)}>
              Close
            </Button>
            <Button>
              <Edit className="mr-2 h-4 w-4" />
              Edit Authority
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Add Holder Dialog */}
      <Dialog open={isHolderDialogOpen} onOpenChange={setIsHolderDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Add Authority Holder</DialogTitle>
            <DialogDescription>
              Assign a user as an authority holder with specific permissions
            </DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="user">Select User</Label>
              <Select>
                <SelectTrigger>
                  <SelectValue placeholder="Search and select user" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="u1">Rajesh Kumar - Procurement Manager</SelectItem>
                  <SelectItem value="u2">Priya Sharma - Senior Buyer</SelectItem>
                  <SelectItem value="u3">Amit Patel - Finance Manager</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Switch id="isPrimary" />
                <Label htmlFor="isPrimary">Primary Holder</Label>
              </div>
              <div className="flex items-center space-x-2">
                <Switch id="canDelegate" />
                <Label htmlFor="canDelegate">Can Delegate</Label>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="validFrom">Valid From</Label>
                <Input id="validFrom" type="date" />
              </div>
              <div className="space-y-2">
                <Label htmlFor="validTo">Valid To (Optional)</Label>
                <Input id="validTo" type="date" />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="maxDelegation">Max Delegation Days</Label>
              <Input id="maxDelegation" type="number" placeholder="14" />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsHolderDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={() => setIsHolderDialogOpen(false)}>Add Holder</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
