"use client";

import { useState } from "react";
import Link from "next/link";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
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
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import {
  ArrowLeft,
  Search,
  Download,
  Eye,
  Filter,
  LogIn,
  LogOut,
  Key,
  Shield,
  Settings,
  FileText,
  AlertTriangle,
  Clock,
  User,
  MapPin,
  Monitor,
} from "lucide-react";

// Mock audit log data
const auditLogs = [
  {
    id: "1",
    eventType: "login_success",
    eventCategory: "auth",
    severity: "info",
    description: "User logged in successfully",
    userName: "Amit Patel",
    userEmail: "amit.patel@company.com",
    ipAddress: "192.168.1.45",
    geoCountry: "India",
    geoCity: "Mumbai",
    deviceType: "desktop",
    deviceBrowser: "Chrome 120",
    success: true,
    createdAt: "2026-01-14T10:30:00Z",
  },
  {
    id: "2",
    eventType: "login_failed",
    eventCategory: "auth",
    severity: "medium",
    description: "Failed login attempt - invalid password",
    userName: null,
    userEmail: "unknown@company.com",
    ipAddress: "203.45.67.89",
    geoCountry: "Unknown",
    geoCity: "Unknown",
    deviceType: "desktop",
    deviceBrowser: "Firefox 121",
    success: false,
    isSuspicious: true,
    createdAt: "2026-01-14T10:25:00Z",
  },
  {
    id: "3",
    eventType: "permission_granted",
    eventCategory: "access",
    severity: "low",
    description: "Admin role assigned to user",
    userName: "Priya Sharma",
    userEmail: "priya.sharma@company.com",
    targetName: "Rajesh Kumar",
    ipAddress: "10.0.0.23",
    geoCountry: "India",
    geoCity: "Bangalore",
    deviceType: "desktop",
    deviceBrowser: "Safari 17",
    success: true,
    createdAt: "2026-01-14T10:00:00Z",
  },
  {
    id: "4",
    eventType: "data_export",
    eventCategory: "data",
    severity: "medium",
    description: "Bulk employee data export",
    userName: "Neha Gupta",
    userEmail: "neha.gupta@company.com",
    ipAddress: "172.16.0.12",
    geoCountry: "India",
    geoCity: "Delhi",
    deviceType: "desktop",
    deviceBrowser: "Chrome 120",
    success: true,
    createdAt: "2026-01-14T09:45:00Z",
  },
  {
    id: "5",
    eventType: "password_change",
    eventCategory: "auth",
    severity: "info",
    description: "User changed password",
    userName: "Amit Patel",
    userEmail: "amit.patel@company.com",
    ipAddress: "192.168.1.45",
    geoCountry: "India",
    geoCity: "Mumbai",
    deviceType: "desktop",
    deviceBrowser: "Chrome 120",
    success: true,
    createdAt: "2026-01-14T09:30:00Z",
  },
  {
    id: "6",
    eventType: "mfa_enabled",
    eventCategory: "auth",
    severity: "info",
    description: "MFA enabled for user account",
    userName: "Vikram Singh",
    userEmail: "vikram.singh@company.com",
    ipAddress: "10.0.0.45",
    geoCountry: "India",
    geoCity: "Chennai",
    deviceType: "mobile",
    deviceBrowser: "Safari Mobile",
    success: true,
    createdAt: "2026-01-14T09:00:00Z",
  },
  {
    id: "7",
    eventType: "config_change",
    eventCategory: "config",
    severity: "high",
    description: "Security policy updated",
    userName: "Admin User",
    userEmail: "admin@company.com",
    ipAddress: "10.0.0.1",
    geoCountry: "India",
    geoCity: "Mumbai",
    deviceType: "desktop",
    deviceBrowser: "Chrome 120",
    success: true,
    oldValues: { mfa_required: false },
    newValues: { mfa_required: true },
    createdAt: "2026-01-13T18:00:00Z",
  },
];

export default function AuditLogsPage() {
  const [searchQuery, setSearchQuery] = useState("");
  const [eventTypeFilter, setEventTypeFilter] = useState("all");
  const [severityFilter, setSeverityFilter] = useState("all");
  const [categoryFilter, setCategoryFilter] = useState("all");
  const [selectedLog, setSelectedLog] = useState<typeof auditLogs[0] | null>(null);
  const [isDetailOpen, setIsDetailOpen] = useState(false);

  const getEventIcon = (eventType: string) => {
    switch (eventType) {
      case "login_success":
        return <LogIn className="h-4 w-4 text-green-600" />;
      case "login_failed":
        return <LogIn className="h-4 w-4 text-red-600" />;
      case "logout":
        return <LogOut className="h-4 w-4 text-blue-600" />;
      case "permission_granted":
      case "permission_revoked":
        return <Key className="h-4 w-4 text-purple-600" />;
      case "data_export":
      case "data_access":
        return <FileText className="h-4 w-4 text-orange-600" />;
      case "password_change":
      case "password_reset":
      case "mfa_enabled":
      case "mfa_disabled":
        return <Shield className="h-4 w-4 text-blue-600" />;
      case "config_change":
        return <Settings className="h-4 w-4 text-gray-600" />;
      case "suspicious_activity":
        return <AlertTriangle className="h-4 w-4 text-red-600" />;
      default:
        return <Clock className="h-4 w-4 text-gray-600" />;
    }
  };

  const getSeverityBadge = (severity: string) => {
    switch (severity) {
      case "critical":
        return <Badge className="bg-red-600 text-white">Critical</Badge>;
      case "high":
        return <Badge className="bg-red-100 text-red-800">High</Badge>;
      case "medium":
        return <Badge className="bg-yellow-100 text-yellow-800">Medium</Badge>;
      case "low":
        return <Badge className="bg-blue-100 text-blue-800">Low</Badge>;
      case "info":
        return <Badge className="bg-gray-100 text-gray-800">Info</Badge>;
      default:
        return <Badge variant="outline">{severity}</Badge>;
    }
  };

  const formatEventType = (eventType: string) => {
    return eventType
      .split("_")
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(" ");
  };

  const formatDateTime = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString("en-IN", {
      day: "2-digit",
      month: "short",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const filteredLogs = auditLogs.filter((log) => {
    const matchesSearch =
      (log.userName?.toLowerCase().includes(searchQuery.toLowerCase()) ?? false) ||
      (log.userEmail?.toLowerCase().includes(searchQuery.toLowerCase()) ?? false) ||
      log.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      log.ipAddress.toLowerCase().includes(searchQuery.toLowerCase());

    const matchesEventType = eventTypeFilter === "all" || log.eventType === eventTypeFilter;
    const matchesSeverity = severityFilter === "all" || log.severity === severityFilter;
    const matchesCategory = categoryFilter === "all" || log.eventCategory === categoryFilter;

    return matchesSearch && matchesEventType && matchesSeverity && matchesCategory;
  });

  const handleViewDetails = (log: typeof auditLogs[0]) => {
    setSelectedLog(log);
    setIsDetailOpen(true);
  };

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
            <h1 className="text-3xl font-bold tracking-tight">Audit Logs</h1>
            <p className="text-muted-foreground">
              Complete audit trail of security events
            </p>
          </div>
        </div>
        <Button variant="outline">
          <Download className="mr-2 h-4 w-4" />
          Export Logs
        </Button>
      </div>

      {/* Filters */}
      <Card>
        <CardHeader>
          <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <div>
              <CardTitle>Security Audit Logs</CardTitle>
              <CardDescription>
                View and filter security events across the system
              </CardDescription>
            </div>
            <div className="flex flex-wrap gap-2">
              <div className="relative">
                <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search logs..."
                  className="pl-8 w-[200px]"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </div>
              <Select value={categoryFilter} onValueChange={setCategoryFilter}>
                <SelectTrigger className="w-[130px]">
                  <SelectValue placeholder="Category" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Categories</SelectItem>
                  <SelectItem value="auth">Authentication</SelectItem>
                  <SelectItem value="access">Access Control</SelectItem>
                  <SelectItem value="data">Data Access</SelectItem>
                  <SelectItem value="config">Configuration</SelectItem>
                </SelectContent>
              </Select>
              <Select value="all" onValueChange={setEventTypeFilter}>
                <SelectTrigger className="w-[150px]">
                  <SelectValue placeholder="Event Type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Events</SelectItem>
                  <SelectItem value="login_success">Login Success</SelectItem>
                  <SelectItem value="login_failed">Login Failed</SelectItem>
                  <SelectItem value="logout">Logout</SelectItem>
                  <SelectItem value="password_change">Password Change</SelectItem>
                  <SelectItem value="mfa_enabled">MFA Enabled</SelectItem>
                  <SelectItem value="permission_granted">Permission Granted</SelectItem>
                  <SelectItem value="data_export">Data Export</SelectItem>
                  <SelectItem value="config_change">Config Change</SelectItem>
                </SelectContent>
              </Select>
              <Select value={severityFilter} onValueChange={setSeverityFilter}>
                <SelectTrigger className="w-[120px]">
                  <SelectValue placeholder="Severity" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Severity</SelectItem>
                  <SelectItem value="critical">Critical</SelectItem>
                  <SelectItem value="high">High</SelectItem>
                  <SelectItem value="medium">Medium</SelectItem>
                  <SelectItem value="low">Low</SelectItem>
                  <SelectItem value="info">Info</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Event</TableHead>
                <TableHead>User</TableHead>
                <TableHead>IP / Location</TableHead>
                <TableHead>Severity</TableHead>
                <TableHead>Time</TableHead>
                <TableHead className="w-[50px]"></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredLogs.map((log) => (
                <TableRow key={log.id} className={log.isSuspicious ? "bg-red-50" : ""}>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      {getEventIcon(log.eventType)}
                      <div>
                        <div className="font-medium text-sm">
                          {formatEventType(log.eventType)}
                        </div>
                        <div className="text-xs text-muted-foreground truncate max-w-[200px]">
                          {log.description}
                        </div>
                      </div>
                    </div>
                  </TableCell>
                  <TableCell>
                    <div>
                      <div className="text-sm">{log.userName || "Unknown"}</div>
                      <div className="text-xs text-muted-foreground">{log.userEmail}</div>
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="text-sm font-mono">{log.ipAddress}</div>
                    <div className="text-xs text-muted-foreground">
                      {log.geoCity}, {log.geoCountry}
                    </div>
                  </TableCell>
                  <TableCell>{getSeverityBadge(log.severity)}</TableCell>
                  <TableCell>
                    <div className="text-sm">{formatDateTime(log.createdAt)}</div>
                  </TableCell>
                  <TableCell>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => handleViewDetails(log)}
                    >
                      <Eye className="h-4 w-4" />
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Detail Dialog */}
      <Dialog open={isDetailOpen} onOpenChange={setIsDetailOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Audit Log Details</DialogTitle>
            <DialogDescription>
              Complete details of this security event
            </DialogDescription>
          </DialogHeader>
          {selectedLog && (
            <div className="space-y-6">
              <div className="flex items-center gap-3">
                <div className="p-3 bg-muted rounded-lg">
                  {getEventIcon(selectedLog.eventType)}
                </div>
                <div>
                  <h3 className="font-semibold">
                    {formatEventType(selectedLog.eventType)}
                  </h3>
                  <p className="text-sm text-muted-foreground">
                    {selectedLog.description}
                  </p>
                </div>
                {getSeverityBadge(selectedLog.severity)}
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1">
                  <Label className="text-xs text-muted-foreground">User</Label>
                  <div className="flex items-center gap-2">
                    <User className="h-4 w-4 text-muted-foreground" />
                    <span>{selectedLog.userName || "Unknown"}</span>
                  </div>
                  <div className="text-xs text-muted-foreground pl-6">
                    {selectedLog.userEmail}
                  </div>
                </div>

                <div className="space-y-1">
                  <Label className="text-xs text-muted-foreground">Time</Label>
                  <div className="flex items-center gap-2">
                    <Clock className="h-4 w-4 text-muted-foreground" />
                    <span>{formatDateTime(selectedLog.createdAt)}</span>
                  </div>
                </div>

                <div className="space-y-1">
                  <Label className="text-xs text-muted-foreground">IP Address</Label>
                  <div className="font-mono">{selectedLog.ipAddress}</div>
                </div>

                <div className="space-y-1">
                  <Label className="text-xs text-muted-foreground">Location</Label>
                  <div className="flex items-center gap-2">
                    <MapPin className="h-4 w-4 text-muted-foreground" />
                    <span>{selectedLog.geoCity}, {selectedLog.geoCountry}</span>
                  </div>
                </div>

                <div className="space-y-1">
                  <Label className="text-xs text-muted-foreground">Device</Label>
                  <div className="flex items-center gap-2">
                    <Monitor className="h-4 w-4 text-muted-foreground" />
                    <span className="capitalize">{selectedLog.deviceType}</span>
                  </div>
                </div>

                <div className="space-y-1">
                  <Label className="text-xs text-muted-foreground">Browser</Label>
                  <div>{selectedLog.deviceBrowser}</div>
                </div>
              </div>

              {(selectedLog.oldValues || selectedLog.newValues) && (
                <div className="p-4 bg-muted rounded-lg">
                  <Label className="text-xs text-muted-foreground">Changes</Label>
                  <div className="mt-2 space-y-2">
                    {selectedLog.oldValues && (
                      <div>
                        <span className="text-xs text-red-600">- Old: </span>
                        <span className="font-mono text-xs">
                          {JSON.stringify(selectedLog.oldValues)}
                        </span>
                      </div>
                    )}
                    {selectedLog.newValues && (
                      <div>
                        <span className="text-xs text-green-600">+ New: </span>
                        <span className="font-mono text-xs">
                          {JSON.stringify(selectedLog.newValues)}
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
