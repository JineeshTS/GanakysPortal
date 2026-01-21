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
import { Calendar } from "@/components/ui/calendar";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { cn } from "@/lib/utils";
import { format, differenceInDays, isAfter, isBefore, addDays } from "date-fns";
import {
  Plus,
  Search,
  MoreHorizontal,
  Edit,
  Trash2,
  ArrowRight,
  CalendarIcon,
  Clock,
  AlertTriangle,
  CheckCircle,
  XCircle,
  User,
  UserCheck,
  Shield,
  FileText,
  RefreshCw,
  Ban,
} from "lucide-react";

// Types
interface Delegation {
  id: string;
  delegatorId: string;
  delegatorName: string;
  delegatorEmail: string;
  delegatorDesignation: string;
  delegateeId: string;
  delegateeName: string;
  delegateeEmail: string;
  delegateeDesignation: string;
  authorityMatrixId: string;
  authorityMatrixName: string;
  authorityCode: string;
  delegationType: "full" | "partial" | "specific";
  startDate: string;
  endDate: string;
  reason: string;
  constraints: {
    maxAmount?: number;
    transactionTypes?: string[];
    excludedTransactions?: string[];
  };
  status: "pending" | "active" | "expired" | "revoked" | "rejected";
  requiresNotification: boolean;
  allowSubDelegation: boolean;
  approvedBy?: string;
  approvedAt?: string;
  revokedBy?: string;
  revokedAt?: string;
  revokeReason?: string;
  createdAt: string;
}

// Mock data
const mockDelegations: Delegation[] = [
  {
    id: "1",
    delegatorId: "u1",
    delegatorName: "Rajesh Kumar",
    delegatorEmail: "rajesh@company.com",
    delegatorDesignation: "Procurement Manager",
    delegateeId: "u2",
    delegateeName: "Priya Sharma",
    delegateeEmail: "priya@company.com",
    delegateeDesignation: "Senior Buyer",
    authorityMatrixId: "am1",
    authorityMatrixName: "Purchase Order Approval",
    authorityCode: "PO-APPROVE",
    delegationType: "partial",
    startDate: "2024-06-10",
    endDate: "2024-06-24",
    reason: "Annual leave - travelling abroad",
    constraints: {
      maxAmount: 50000,
      transactionTypes: ["purchase_order"],
    },
    status: "active",
    requiresNotification: true,
    allowSubDelegation: false,
    approvedBy: "Admin User",
    approvedAt: "2024-06-09T10:00:00Z",
    createdAt: "2024-06-08T14:30:00Z",
  },
  {
    id: "2",
    delegatorId: "u3",
    delegatorName: "Amit Patel",
    delegatorEmail: "amit@company.com",
    delegatorDesignation: "Finance Manager",
    delegateeId: "u6",
    delegateeName: "Sneha Reddy",
    delegateeEmail: "sneha@company.com",
    delegateeDesignation: "Senior Accountant",
    authorityMatrixId: "am2",
    authorityMatrixName: "Employee Expense Reimbursement",
    authorityCode: "EXP-REIMBURSE",
    delegationType: "full",
    startDate: "2024-06-15",
    endDate: "2024-06-22",
    reason: "Medical leave",
    constraints: {},
    status: "pending",
    requiresNotification: true,
    allowSubDelegation: false,
    createdAt: "2024-06-12T09:00:00Z",
  },
  {
    id: "3",
    delegatorId: "u5",
    delegatorName: "Meera Joshi",
    delegatorEmail: "meera@company.com",
    delegatorDesignation: "HR Director",
    delegateeId: "u7",
    delegateeName: "Vikram Singh",
    delegateeEmail: "vikram@company.com",
    delegateeDesignation: "HR Manager",
    authorityMatrixId: "am4",
    authorityMatrixName: "Hiring Approval",
    authorityCode: "HIRE-APPROVE",
    delegationType: "specific",
    startDate: "2024-05-01",
    endDate: "2024-05-15",
    reason: "Conference attendance",
    constraints: {
      transactionTypes: ["hiring_request"],
      excludedTransactions: ["salary_offer"],
    },
    status: "expired",
    requiresNotification: false,
    allowSubDelegation: false,
    approvedBy: "Admin User",
    approvedAt: "2024-04-30T16:00:00Z",
    createdAt: "2024-04-28T11:00:00Z",
  },
  {
    id: "4",
    delegatorId: "u1",
    delegatorName: "Rajesh Kumar",
    delegatorEmail: "rajesh@company.com",
    delegatorDesignation: "Procurement Manager",
    delegateeId: "u8",
    delegateeName: "Arjun Nair",
    delegateeEmail: "arjun@company.com",
    delegateeDesignation: "Buyer",
    authorityMatrixId: "am1",
    authorityMatrixName: "Purchase Order Approval",
    authorityCode: "PO-APPROVE",
    delegationType: "partial",
    startDate: "2024-04-01",
    endDate: "2024-04-10",
    reason: "Training session",
    constraints: {
      maxAmount: 25000,
    },
    status: "revoked",
    requiresNotification: true,
    allowSubDelegation: false,
    approvedBy: "Admin User",
    approvedAt: "2024-03-31T10:00:00Z",
    revokedBy: "Rajesh Kumar",
    revokedAt: "2024-04-05T14:00:00Z",
    revokeReason: "Training cancelled, returning to office early",
    createdAt: "2024-03-29T09:00:00Z",
  },
];

const delegationTypes = [
  { value: "full", label: "Full Delegation", description: "Complete authority transfer" },
  { value: "partial", label: "Partial Delegation", description: "Limited by amount or scope" },
  { value: "specific", label: "Specific Transactions", description: "Only certain transaction types" },
];

export default function DelegationsPage() {
  const [delegations, setDelegations] = useState<Delegation[]>(mockDelegations);
  const [searchQuery, setSearchQuery] = useState("");
  const [filterStatus, setFilterStatus] = useState<string>("all");
  const [filterType, setFilterType] = useState<string>("all");
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [selectedDelegation, setSelectedDelegation] = useState<Delegation | null>(null);
  const [isRevokeDialogOpen, setIsRevokeDialogOpen] = useState(false);
  const [revokeReason, setRevokeReason] = useState("");
  const [activeTab, setActiveTab] = useState("all");
  const [dateRange, setDateRange] = useState<{ from: Date | undefined; to: Date | undefined }>({
    from: undefined,
    to: undefined,
  });

  // Filter delegations
  const filteredDelegations = delegations.filter((delegation) => {
    const matchesSearch =
      delegation.delegatorName.toLowerCase().includes(searchQuery.toLowerCase()) ||
      delegation.delegateeName.toLowerCase().includes(searchQuery.toLowerCase()) ||
      delegation.authorityMatrixName.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = filterStatus === "all" || delegation.status === filterStatus;
    const matchesType = filterType === "all" || delegation.delegationType === filterType;

    // Tab filtering
    let matchesTab = true;
    if (activeTab === "active") {
      matchesTab = delegation.status === "active";
    } else if (activeTab === "pending") {
      matchesTab = delegation.status === "pending";
    } else if (activeTab === "my-delegations") {
      // Assuming current user is Rajesh Kumar (u1)
      matchesTab = delegation.delegatorId === "u1";
    } else if (activeTab === "delegated-to-me") {
      // Assuming current user is Priya Sharma (u2)
      matchesTab = delegation.delegateeId === "u2";
    }

    return matchesSearch && matchesStatus && matchesType && matchesTab;
  });

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "active":
        return <Badge className="bg-green-100 text-green-800">Active</Badge>;
      case "pending":
        return <Badge className="bg-yellow-100 text-yellow-800">Pending Approval</Badge>;
      case "expired":
        return <Badge className="bg-gray-100 text-gray-800">Expired</Badge>;
      case "revoked":
        return <Badge className="bg-red-100 text-red-800">Revoked</Badge>;
      case "rejected":
        return <Badge className="bg-red-100 text-red-800">Rejected</Badge>;
      default:
        return <Badge variant="outline">{status}</Badge>;
    }
  };

  const getDelegationTypeBadge = (type: string) => {
    switch (type) {
      case "full":
        return <Badge className="bg-blue-100 text-blue-800">Full</Badge>;
      case "partial":
        return <Badge className="bg-purple-100 text-purple-800">Partial</Badge>;
      case "specific":
        return <Badge className="bg-orange-100 text-orange-800">Specific</Badge>;
      default:
        return <Badge variant="outline">{type}</Badge>;
    }
  };

  const getDaysRemaining = (endDate: string) => {
    const end = new Date(endDate);
    const today = new Date();
    const days = differenceInDays(end, today);

    if (days < 0) return { text: "Expired", color: "text-gray-500" };
    if (days === 0) return { text: "Expires today", color: "text-red-600" };
    if (days <= 3) return { text: `${days} days left`, color: "text-orange-600" };
    return { text: `${days} days left`, color: "text-green-600" };
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat("en-IN", {
      style: "currency",
      currency: "INR",
      maximumFractionDigits: 0,
    }).format(amount);
  };

  // Summary stats
  const stats = {
    total: delegations.length,
    active: delegations.filter((d) => d.status === "active").length,
    pending: delegations.filter((d) => d.status === "pending").length,
    expiringSoon: delegations.filter((d) => {
      if (d.status !== "active") return false;
      const days = differenceInDays(new Date(d.endDate), new Date());
      return days >= 0 && days <= 3;
    }).length,
  };

  const handleRevoke = () => {
    if (selectedDelegation) {
      setDelegations(
        delegations.map((d) =>
          d.id === selectedDelegation.id
            ? {
                ...d,
                status: "revoked" as const,
                revokedBy: "Current User",
                revokedAt: new Date().toISOString(),
                revokeReason: revokeReason,
              }
            : d
        )
      );
      setIsRevokeDialogOpen(false);
      setSelectedDelegation(null);
      setRevokeReason("");
    }
  };

  return (
    <div className="flex flex-col gap-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Delegations</h1>
          <p className="text-muted-foreground">
            Manage authority delegations during absences or for workload distribution
          </p>
        </div>
        <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              Create Delegation
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>Create New Delegation</DialogTitle>
              <DialogDescription>
                Temporarily delegate your approval authority to another user
              </DialogDescription>
            </DialogHeader>
            <div className="grid gap-4 py-4 max-h-[60vh] overflow-y-auto">
              <div className="space-y-2">
                <Label htmlFor="authority">Select Authority to Delegate</Label>
                <Select>
                  <SelectTrigger>
                    <SelectValue placeholder="Choose an authority" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="am1">Purchase Order Approval (PO-APPROVE)</SelectItem>
                    <SelectItem value="am2">Expense Reimbursement (EXP-REIMBURSE)</SelectItem>
                    <SelectItem value="am4">Hiring Approval (HIRE-APPROVE)</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="delegatee">Delegate To</Label>
                <Select>
                  <SelectTrigger>
                    <SelectValue placeholder="Select user" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="u2">Priya Sharma - Senior Buyer</SelectItem>
                    <SelectItem value="u6">Sneha Reddy - Senior Accountant</SelectItem>
                    <SelectItem value="u7">Vikram Singh - HR Manager</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label>Delegation Type</Label>
                <div className="grid grid-cols-3 gap-2">
                  {delegationTypes.map((type) => (
                    <div
                      key={type.value}
                      className="flex items-center space-x-2 border rounded-lg p-3 cursor-pointer hover:bg-muted"
                    >
                      <input
                        type="radio"
                        name="delegationType"
                        id={type.value}
                        value={type.value}
                        className="h-4 w-4"
                      />
                      <div>
                        <Label htmlFor={type.value} className="cursor-pointer font-medium">
                          {type.label}
                        </Label>
                        <p className="text-xs text-muted-foreground">{type.description}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Start Date</Label>
                  <Popover>
                    <PopoverTrigger asChild>
                      <Button variant="outline" className="w-full justify-start text-left font-normal">
                        <CalendarIcon className="mr-2 h-4 w-4" />
                        {dateRange.from ? format(dateRange.from, "PPP") : "Pick a date"}
                      </Button>
                    </PopoverTrigger>
                    <PopoverContent className="w-auto p-0" align="start">
                      <Calendar
                        mode="single"
                        selected={dateRange.from}
                        onSelect={(date) => setDateRange({ ...dateRange, from: date })}
                        initialFocus
                      />
                    </PopoverContent>
                  </Popover>
                </div>
                <div className="space-y-2">
                  <Label>End Date</Label>
                  <Popover>
                    <PopoverTrigger asChild>
                      <Button variant="outline" className="w-full justify-start text-left font-normal">
                        <CalendarIcon className="mr-2 h-4 w-4" />
                        {dateRange.to ? format(dateRange.to, "PPP") : "Pick a date"}
                      </Button>
                    </PopoverTrigger>
                    <PopoverContent className="w-auto p-0" align="start">
                      <Calendar
                        mode="single"
                        selected={dateRange.to}
                        onSelect={(date) => setDateRange({ ...dateRange, to: date })}
                        initialFocus
                      />
                    </PopoverContent>
                  </Popover>
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="maxAmount">Maximum Amount Limit (Optional)</Label>
                <Input id="maxAmount" type="number" placeholder="Leave empty for no limit" />
              </div>

              <div className="space-y-2">
                <Label htmlFor="reason">Reason for Delegation</Label>
                <Textarea
                  id="reason"
                  placeholder="e.g., Annual leave, Medical leave, Training..."
                  rows={3}
                />
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Switch id="notify" defaultChecked />
                  <Label htmlFor="notify">Notify on each approval</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <Switch id="subDelegate" />
                  <Label htmlFor="subDelegate">Allow sub-delegation</Label>
                </div>
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setIsCreateDialogOpen(false)}>
                Cancel
              </Button>
              <Button onClick={() => setIsCreateDialogOpen(false)}>Submit for Approval</Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      {/* Summary Cards */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Delegations</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.total}</div>
            <p className="text-xs text-muted-foreground">All time records</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Delegations</CardTitle>
            <CheckCircle className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.active}</div>
            <p className="text-xs text-muted-foreground">Currently in effect</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Pending Approval</CardTitle>
            <Clock className="h-4 w-4 text-yellow-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.pending}</div>
            <p className="text-xs text-muted-foreground">Awaiting approval</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Expiring Soon</CardTitle>
            <AlertTriangle className="h-4 w-4 text-orange-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.expiringSoon}</div>
            <p className="text-xs text-muted-foreground">Within 3 days</p>
          </CardContent>
        </Card>
      </div>

      {/* Main Content */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <div className="flex items-center justify-between">
          <TabsList>
            <TabsTrigger value="all">All Delegations</TabsTrigger>
            <TabsTrigger value="active">Active</TabsTrigger>
            <TabsTrigger value="pending">Pending</TabsTrigger>
            <TabsTrigger value="my-delegations">My Delegations</TabsTrigger>
            <TabsTrigger value="delegated-to-me">Delegated to Me</TabsTrigger>
          </TabsList>

          {/* Filters */}
          <div className="flex items-center gap-2">
            <div className="relative">
              <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search delegations..."
                className="pl-8 w-[200px]"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
            <Select value={filterType} onValueChange={setFilterType}>
              <SelectTrigger className="w-[130px]">
                <SelectValue placeholder="Type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Types</SelectItem>
                <SelectItem value="full">Full</SelectItem>
                <SelectItem value="partial">Partial</SelectItem>
                <SelectItem value="specific">Specific</SelectItem>
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
                    <TableHead>Delegation</TableHead>
                    <TableHead>Authority</TableHead>
                    <TableHead>Type</TableHead>
                    <TableHead>Duration</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead className="w-[50px]"></TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredDelegations.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={6} className="text-center py-8">
                        <div className="flex flex-col items-center gap-2">
                          <FileText className="h-8 w-8 text-muted-foreground" />
                          <p className="text-muted-foreground">No delegations found</p>
                        </div>
                      </TableCell>
                    </TableRow>
                  ) : (
                    filteredDelegations.map((delegation) => {
                      const daysInfo = getDaysRemaining(delegation.endDate);

                      return (
                        <TableRow key={delegation.id}>
                          <TableCell>
                            <div className="flex items-center gap-3">
                              <div className="flex items-center gap-2">
                                <div className="p-2 rounded-full bg-muted">
                                  <User className="h-4 w-4" />
                                </div>
                                <div>
                                  <div className="font-medium">{delegation.delegatorName}</div>
                                  <div className="text-xs text-muted-foreground">
                                    {delegation.delegatorDesignation}
                                  </div>
                                </div>
                              </div>
                              <ArrowRight className="h-4 w-4 text-muted-foreground" />
                              <div className="flex items-center gap-2">
                                <div className="p-2 rounded-full bg-muted">
                                  <UserCheck className="h-4 w-4" />
                                </div>
                                <div>
                                  <div className="font-medium">{delegation.delegateeName}</div>
                                  <div className="text-xs text-muted-foreground">
                                    {delegation.delegateeDesignation}
                                  </div>
                                </div>
                              </div>
                            </div>
                          </TableCell>
                          <TableCell>
                            <div>
                              <div className="font-medium">{delegation.authorityMatrixName}</div>
                              <div className="text-xs text-muted-foreground">
                                {delegation.authorityCode}
                              </div>
                            </div>
                          </TableCell>
                          <TableCell>
                            <div className="space-y-1">
                              {getDelegationTypeBadge(delegation.delegationType)}
                              {delegation.constraints.maxAmount && (
                                <div className="text-xs text-muted-foreground">
                                  Max: {formatCurrency(delegation.constraints.maxAmount)}
                                </div>
                              )}
                            </div>
                          </TableCell>
                          <TableCell>
                            <div className="text-sm">
                              <div>
                                {format(new Date(delegation.startDate), "MMM d")} -{" "}
                                {format(new Date(delegation.endDate), "MMM d, yyyy")}
                              </div>
                              {delegation.status === "active" && (
                                <div className={cn("text-xs", daysInfo.color)}>{daysInfo.text}</div>
                              )}
                            </div>
                          </TableCell>
                          <TableCell>{getStatusBadge(delegation.status)}</TableCell>
                          <TableCell>
                            <DropdownMenu>
                              <DropdownMenuTrigger asChild>
                                <Button variant="ghost" size="icon">
                                  <MoreHorizontal className="h-4 w-4" />
                                </Button>
                              </DropdownMenuTrigger>
                              <DropdownMenuContent align="end">
                                <DropdownMenuItem onClick={() => setSelectedDelegation(delegation)}>
                                  <FileText className="mr-2 h-4 w-4" />
                                  View Details
                                </DropdownMenuItem>
                                {delegation.status === "active" && (
                                  <>
                                    <DropdownMenuItem>
                                      <RefreshCw className="mr-2 h-4 w-4" />
                                      Extend Duration
                                    </DropdownMenuItem>
                                    <DropdownMenuItem
                                      className="text-red-600"
                                      onClick={() => {
                                        setSelectedDelegation(delegation);
                                        setIsRevokeDialogOpen(true);
                                      }}
                                    >
                                      <Ban className="mr-2 h-4 w-4" />
                                      Revoke
                                    </DropdownMenuItem>
                                  </>
                                )}
                                {delegation.status === "pending" && (
                                  <>
                                    <DropdownMenuItem>
                                      <CheckCircle className="mr-2 h-4 w-4" />
                                      Approve
                                    </DropdownMenuItem>
                                    <DropdownMenuItem className="text-red-600">
                                      <XCircle className="mr-2 h-4 w-4" />
                                      Reject
                                    </DropdownMenuItem>
                                  </>
                                )}
                              </DropdownMenuContent>
                            </DropdownMenu>
                          </TableCell>
                        </TableRow>
                      );
                    })
                  )}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Delegation Detail Dialog */}
      <Dialog open={!!selectedDelegation && !isRevokeDialogOpen} onOpenChange={() => setSelectedDelegation(null)}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Delegation Details</DialogTitle>
            <DialogDescription>
              Authority delegation from {selectedDelegation?.delegatorName} to{" "}
              {selectedDelegation?.delegateeName}
            </DialogDescription>
          </DialogHeader>
          {selectedDelegation && (
            <div className="space-y-6">
              {/* Delegation Flow */}
              <div className="flex items-center justify-center gap-4 p-4 bg-muted rounded-lg">
                <div className="text-center">
                  <div className="p-3 rounded-full bg-background mx-auto w-fit">
                    <User className="h-6 w-6" />
                  </div>
                  <div className="mt-2 font-medium">{selectedDelegation.delegatorName}</div>
                  <div className="text-sm text-muted-foreground">
                    {selectedDelegation.delegatorDesignation}
                  </div>
                  <Badge variant="outline" className="mt-1">
                    Delegator
                  </Badge>
                </div>
                <ArrowRight className="h-6 w-6 text-muted-foreground" />
                <div className="text-center">
                  <div className="p-3 rounded-full bg-background mx-auto w-fit">
                    <UserCheck className="h-6 w-6" />
                  </div>
                  <div className="mt-2 font-medium">{selectedDelegation.delegateeName}</div>
                  <div className="text-sm text-muted-foreground">
                    {selectedDelegation.delegateeDesignation}
                  </div>
                  <Badge variant="outline" className="mt-1">
                    Delegatee
                  </Badge>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label className="text-muted-foreground">Authority</Label>
                  <div className="mt-1 font-medium">{selectedDelegation.authorityMatrixName}</div>
                  <div className="text-sm text-muted-foreground">{selectedDelegation.authorityCode}</div>
                </div>
                <div>
                  <Label className="text-muted-foreground">Status</Label>
                  <div className="mt-1">{getStatusBadge(selectedDelegation.status)}</div>
                </div>
                <div>
                  <Label className="text-muted-foreground">Delegation Type</Label>
                  <div className="mt-1">{getDelegationTypeBadge(selectedDelegation.delegationType)}</div>
                </div>
                <div>
                  <Label className="text-muted-foreground">Duration</Label>
                  <div className="mt-1 font-medium">
                    {format(new Date(selectedDelegation.startDate), "MMM d, yyyy")} -{" "}
                    {format(new Date(selectedDelegation.endDate), "MMM d, yyyy")}
                  </div>
                </div>
              </div>

              <div>
                <Label className="text-muted-foreground">Reason</Label>
                <p className="mt-1">{selectedDelegation.reason}</p>
              </div>

              {/* Constraints */}
              {(selectedDelegation.constraints.maxAmount ||
                selectedDelegation.constraints.transactionTypes?.length ||
                selectedDelegation.constraints.excludedTransactions?.length) && (
                <div>
                  <Label className="text-muted-foreground mb-2 block">Constraints</Label>
                  <div className="space-y-2 p-3 bg-muted rounded-lg">
                    {selectedDelegation.constraints.maxAmount && (
                      <div className="flex items-center gap-2">
                        <Shield className="h-4 w-4 text-muted-foreground" />
                        <span>
                          Maximum Amount: {formatCurrency(selectedDelegation.constraints.maxAmount)}
                        </span>
                      </div>
                    )}
                    {selectedDelegation.constraints.transactionTypes?.length && (
                      <div className="flex items-center gap-2">
                        <FileText className="h-4 w-4 text-muted-foreground" />
                        <span>
                          Allowed: {selectedDelegation.constraints.transactionTypes.join(", ")}
                        </span>
                      </div>
                    )}
                    {selectedDelegation.constraints.excludedTransactions?.length && (
                      <div className="flex items-center gap-2">
                        <XCircle className="h-4 w-4 text-red-500" />
                        <span>
                          Excluded: {selectedDelegation.constraints.excludedTransactions.join(", ")}
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Settings */}
              <div className="flex gap-4">
                <div className="flex items-center gap-2">
                  {selectedDelegation.requiresNotification ? (
                    <CheckCircle className="h-4 w-4 text-green-600" />
                  ) : (
                    <XCircle className="h-4 w-4 text-gray-400" />
                  )}
                  <span className="text-sm">Notifications on approval</span>
                </div>
                <div className="flex items-center gap-2">
                  {selectedDelegation.allowSubDelegation ? (
                    <CheckCircle className="h-4 w-4 text-green-600" />
                  ) : (
                    <XCircle className="h-4 w-4 text-gray-400" />
                  )}
                  <span className="text-sm">Sub-delegation allowed</span>
                </div>
              </div>

              {/* Approval Info */}
              {selectedDelegation.approvedBy && (
                <div className="p-3 bg-green-50 rounded-lg">
                  <div className="flex items-center gap-2 text-green-800">
                    <CheckCircle className="h-4 w-4" />
                    <span className="font-medium">Approved by {selectedDelegation.approvedBy}</span>
                  </div>
                  <div className="text-sm text-green-700 mt-1">
                    {selectedDelegation.approvedAt &&
                      format(new Date(selectedDelegation.approvedAt), "PPp")}
                  </div>
                </div>
              )}

              {/* Revocation Info */}
              {selectedDelegation.status === "revoked" && (
                <div className="p-3 bg-red-50 rounded-lg">
                  <div className="flex items-center gap-2 text-red-800">
                    <Ban className="h-4 w-4" />
                    <span className="font-medium">Revoked by {selectedDelegation.revokedBy}</span>
                  </div>
                  <div className="text-sm text-red-700 mt-1">
                    {selectedDelegation.revokedAt &&
                      format(new Date(selectedDelegation.revokedAt), "PPp")}
                  </div>
                  {selectedDelegation.revokeReason && (
                    <div className="text-sm text-red-700 mt-2">
                      Reason: {selectedDelegation.revokeReason}
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
          <DialogFooter>
            <Button variant="outline" onClick={() => setSelectedDelegation(null)}>
              Close
            </Button>
            {selectedDelegation?.status === "active" && (
              <Button
                variant="destructive"
                onClick={() => setIsRevokeDialogOpen(true)}
              >
                <Ban className="mr-2 h-4 w-4" />
                Revoke Delegation
              </Button>
            )}
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Revoke Dialog */}
      <Dialog open={isRevokeDialogOpen} onOpenChange={setIsRevokeDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Revoke Delegation</DialogTitle>
            <DialogDescription>
              Are you sure you want to revoke this delegation? The delegatee will immediately lose
              the delegated authority.
            </DialogDescription>
          </DialogHeader>
          <div className="py-4">
            <div className="space-y-2">
              <Label htmlFor="revokeReason">Reason for Revocation</Label>
              <Textarea
                id="revokeReason"
                placeholder="Please provide a reason..."
                rows={3}
                value={revokeReason}
                onChange={(e) => setRevokeReason(e.target.value)}
              />
            </div>
          </div>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => {
                setIsRevokeDialogOpen(false);
                setRevokeReason("");
              }}
            >
              Cancel
            </Button>
            <Button variant="destructive" onClick={handleRevoke}>
              Revoke Delegation
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
