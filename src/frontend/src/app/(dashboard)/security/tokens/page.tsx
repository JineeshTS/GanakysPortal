"use client";

import { useState } from "react";
import Link from "next/link";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
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
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { Checkbox } from "@/components/ui/checkbox";
import {
  ArrowLeft,
  Plus,
  Key,
  Clock,
  Copy,
  Eye,
  EyeOff,
  Trash2,
  AlertTriangle,
  CheckCircle,
} from "lucide-react";

// Mock tokens data
const tokens = [
  {
    id: "1",
    name: "Production API Key",
    description: "Main API key for production integrations",
    tokenType: "api_key",
    tokenPrefix: "gk_prod_",
    scopes: ["read:employees", "write:employees", "read:payroll"],
    createdAt: "2025-06-15T10:00:00Z",
    lastUsedAt: "2026-01-14T09:30:00Z",
    expiresAt: "2026-06-15T10:00:00Z",
    usageCount: 15420,
    isActive: true,
  },
  {
    id: "2",
    name: "Development API Key",
    description: "API key for development and testing",
    tokenType: "api_key",
    tokenPrefix: "gk_dev_",
    scopes: ["read:employees", "read:payroll"],
    createdAt: "2025-09-01T14:00:00Z",
    lastUsedAt: "2026-01-13T16:45:00Z",
    expiresAt: null,
    usageCount: 3250,
    isActive: true,
  },
  {
    id: "3",
    name: "Service Account - HR System",
    description: "Service account for HR system integration",
    tokenType: "service_account",
    tokenPrefix: "gk_svc_",
    scopes: ["read:employees", "write:employees", "read:attendance"],
    createdAt: "2025-08-20T08:00:00Z",
    lastUsedAt: "2026-01-14T10:15:00Z",
    expiresAt: "2026-08-20T08:00:00Z",
    usageCount: 8945,
    isActive: true,
  },
  {
    id: "4",
    name: "Personal Access Token",
    description: "My personal access token for CLI",
    tokenType: "personal_access",
    tokenPrefix: "gk_pat_",
    scopes: ["read:all"],
    createdAt: "2025-12-01T12:00:00Z",
    lastUsedAt: "2025-12-15T09:00:00Z",
    expiresAt: "2026-03-01T12:00:00Z",
    usageCount: 156,
    isActive: true,
  },
  {
    id: "5",
    name: "Legacy Integration Key",
    description: "Old integration key (deprecated)",
    tokenType: "api_key",
    tokenPrefix: "gk_leg_",
    scopes: ["read:employees"],
    createdAt: "2024-06-01T10:00:00Z",
    lastUsedAt: "2024-12-01T08:00:00Z",
    expiresAt: "2025-06-01T10:00:00Z",
    usageCount: 4520,
    isActive: false,
    revokedAt: "2025-01-15T10:00:00Z",
  },
];

const availableScopes = [
  { id: "read:employees", label: "Read Employees", description: "View employee data" },
  { id: "write:employees", label: "Write Employees", description: "Create and update employees" },
  { id: "read:payroll", label: "Read Payroll", description: "View payroll data" },
  { id: "write:payroll", label: "Write Payroll", description: "Manage payroll" },
  { id: "read:attendance", label: "Read Attendance", description: "View attendance data" },
  { id: "write:attendance", label: "Write Attendance", description: "Manage attendance" },
  { id: "read:documents", label: "Read Documents", description: "View documents" },
  { id: "write:documents", label: "Write Documents", description: "Upload documents" },
  { id: "read:all", label: "Read All", description: "Read access to all resources" },
];

export default function APITokensPage() {
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isRevokeDialogOpen, setIsRevokeDialogOpen] = useState(false);
  const [selectedToken, setSelectedToken] = useState<typeof tokens[0] | null>(null);
  const [newToken, setNewToken] = useState<string | null>(null);
  const [showToken, setShowToken] = useState(false);
  const [selectedScopes, setSelectedScopes] = useState<string[]>([]);

  const formatDate = (dateString: string | null) => {
    if (!dateString) return "Never";
    const date = new Date(dateString);
    return date.toLocaleDateString("en-IN", {
      day: "2-digit",
      month: "short",
      year: "numeric",
    });
  };

  const getTokenTypeBadge = (type: string) => {
    switch (type) {
      case "api_key":
        return <Badge variant="outline">API Key</Badge>;
      case "personal_access":
        return <Badge className="bg-purple-100 text-purple-800">Personal</Badge>;
      case "service_account":
        return <Badge className="bg-blue-100 text-blue-800">Service</Badge>;
      default:
        return <Badge variant="outline">{type}</Badge>;
    }
  };

  const handleCreateToken = () => {
    // Simulate token creation
    setNewToken("gk_prod_" + Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15));
    setIsCreateDialogOpen(false);
  };

  const handleRevokeToken = (token: typeof tokens[0]) => {
    setSelectedToken(token);
    setIsRevokeDialogOpen(true);
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    // Could add toast notification here
  };

  const activeTokens = tokens.filter((t) => t.isActive);

  return (
    <div className="flex flex-col gap-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link href="/security">
            <Button variant="ghost" size="icon">
              <ArrowLeft className="h-4 w-4" />
            </Button>
          </Link>
          <div>
            <h1 className="text-3xl font-bold tracking-tight">API Tokens</h1>
            <p className="text-muted-foreground">
              Manage API access tokens and service accounts
            </p>
          </div>
        </div>
        <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              Create Token
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-lg">
            <DialogHeader>
              <DialogTitle>Create API Token</DialogTitle>
              <DialogDescription>
                Create a new API token for integrations
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4 py-4">
              <div className="space-y-2">
                <Label htmlFor="token_name">Token Name</Label>
                <Input id="token_name" placeholder="e.g., Production API Key" />
              </div>
              <div className="space-y-2">
                <Label htmlFor="token_description">Description</Label>
                <Textarea
                  id="token_description"
                  placeholder="What is this token used for?"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="token_type">Token Type</Label>
                <Select>
                  <SelectTrigger>
                    <SelectValue placeholder="Select type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="api_key">API Key</SelectItem>
                    <SelectItem value="personal_access">Personal Access Token</SelectItem>
                    <SelectItem value="service_account">Service Account</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label>Scopes</Label>
                <div className="border rounded-lg p-3 max-h-[200px] overflow-y-auto space-y-2">
                  {availableScopes.map((scope) => (
                    <div key={scope.id} className="flex items-center space-x-2">
                      <Checkbox
                        id={scope.id}
                        checked={selectedScopes.includes(scope.id)}
                        onCheckedChange={(checked) => {
                          if (checked) {
                            setSelectedScopes([...selectedScopes, scope.id]);
                          } else {
                            setSelectedScopes(selectedScopes.filter((s) => s !== scope.id));
                          }
                        }}
                      />
                      <div className="flex-1">
                        <label htmlFor={scope.id} className="text-sm font-medium cursor-pointer">
                          {scope.label}
                        </label>
                        <p className="text-xs text-muted-foreground">{scope.description}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="expires_at">Expiration</Label>
                <Select>
                  <SelectTrigger>
                    <SelectValue placeholder="Select expiration" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="30d">30 days</SelectItem>
                    <SelectItem value="90d">90 days</SelectItem>
                    <SelectItem value="180d">180 days</SelectItem>
                    <SelectItem value="1y">1 year</SelectItem>
                    <SelectItem value="never">Never expires</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setIsCreateDialogOpen(false)}>
                Cancel
              </Button>
              <Button onClick={handleCreateToken}>Create Token</Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      {/* New Token Display */}
      {newToken && (
        <Card className="border-green-200 bg-green-50">
          <CardHeader>
            <div className="flex items-center gap-2">
              <CheckCircle className="h-5 w-5 text-green-600" />
              <CardTitle className="text-green-800">Token Created Successfully</CardTitle>
            </div>
            <CardDescription className="text-green-700">
              Copy this token now. You won't be able to see it again!
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <div className="flex-1 p-3 bg-white rounded-lg border font-mono text-sm">
                {showToken ? newToken : "••••••••••••••••••••••••••••••••"}
              </div>
              <Button
                variant="outline"
                size="icon"
                onClick={() => setShowToken(!showToken)}
              >
                {showToken ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              </Button>
              <Button
                variant="outline"
                size="icon"
                onClick={() => copyToClipboard(newToken)}
              >
                <Copy className="h-4 w-4" />
              </Button>
            </div>
            <Button
              variant="ghost"
              size="sm"
              className="mt-2"
              onClick={() => setNewToken(null)}
            >
              Dismiss
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Stats */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Tokens</CardTitle>
            <Key className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{activeTokens.length}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Usage</CardTitle>
            <Clock className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {activeTokens.reduce((sum, t) => sum + t.usageCount, 0).toLocaleString()}
            </div>
            <p className="text-xs text-muted-foreground">API calls</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Expiring Soon</CardTitle>
            <AlertTriangle className="h-4 w-4 text-yellow-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {activeTokens.filter((t) => {
                if (!t.expiresAt) return false;
                const exp = new Date(t.expiresAt);
                const now = new Date();
                const diffDays = Math.floor((exp.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));
                return diffDays <= 30;
              }).length}
            </div>
            <p className="text-xs text-muted-foreground">Within 30 days</p>
          </CardContent>
        </Card>
      </div>

      {/* Tokens Table */}
      <Card>
        <CardHeader>
          <CardTitle>All Tokens</CardTitle>
          <CardDescription>Manage your API tokens and service accounts</CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Token</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Scopes</TableHead>
                <TableHead>Last Used</TableHead>
                <TableHead>Expires</TableHead>
                <TableHead>Usage</TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="w-[50px]"></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {tokens.map((token) => (
                <TableRow key={token.id} className={!token.isActive ? "opacity-60" : ""}>
                  <TableCell>
                    <div>
                      <div className="font-medium">{token.name}</div>
                      <div className="text-xs text-muted-foreground font-mono">
                        {token.tokenPrefix}...
                      </div>
                    </div>
                  </TableCell>
                  <TableCell>{getTokenTypeBadge(token.tokenType)}</TableCell>
                  <TableCell>
                    <div className="flex flex-wrap gap-1">
                      {token.scopes.slice(0, 2).map((scope) => (
                        <Badge key={scope} variant="outline" className="text-xs">
                          {scope.split(":")[1]}
                        </Badge>
                      ))}
                      {token.scopes.length > 2 && (
                        <Badge variant="outline" className="text-xs">
                          +{token.scopes.length - 2}
                        </Badge>
                      )}
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="text-sm">{formatDate(token.lastUsedAt)}</div>
                  </TableCell>
                  <TableCell>
                    <div className="text-sm">
                      {token.expiresAt ? formatDate(token.expiresAt) : "Never"}
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="text-sm font-medium">
                      {token.usageCount.toLocaleString()}
                    </div>
                  </TableCell>
                  <TableCell>
                    {token.isActive ? (
                      <Badge className="bg-green-100 text-green-800">Active</Badge>
                    ) : (
                      <Badge className="bg-red-100 text-red-800">Revoked</Badge>
                    )}
                  </TableCell>
                  <TableCell>
                    {token.isActive && (
                      <Button
                        variant="ghost"
                        size="icon"
                        className="text-red-600 hover:text-red-700"
                        onClick={() => handleRevokeToken(token)}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Revoke Dialog */}
      <AlertDialog open={isRevokeDialogOpen} onOpenChange={setIsRevokeDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Revoke API Token</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to revoke this token? Any applications using this
              token will immediately lose access.
              {selectedToken && (
                <div className="mt-4 p-3 bg-muted rounded-lg">
                  <div className="font-medium">{selectedToken.name}</div>
                  <div className="text-sm text-muted-foreground">
                    {selectedToken.description}
                  </div>
                  <div className="text-xs text-muted-foreground mt-1">
                    {selectedToken.usageCount.toLocaleString()} API calls
                  </div>
                </div>
              )}
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction className="bg-red-600 hover:bg-red-700">
              Revoke Token
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
