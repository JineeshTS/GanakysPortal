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
  ArrowLeft,
  Search,
  Monitor,
  Smartphone,
  Tablet,
  XCircle,
  Clock,
  MapPin,
  Globe,
  User,
  RefreshCw,
} from "lucide-react";

// Mock session data
const sessions = [
  {
    id: "1",
    userName: "Amit Patel",
    userEmail: "amit.patel@company.com",
    deviceType: "desktop",
    deviceOs: "Windows 11",
    deviceBrowser: "Chrome 120",
    ipAddress: "192.168.1.45",
    geoCountry: "India",
    geoCity: "Mumbai",
    createdAt: "2026-01-14T08:00:00Z",
    lastActivityAt: "2026-01-14T10:35:00Z",
    expiresAt: "2026-01-14T16:00:00Z",
    isActive: true,
    mfaVerified: true,
    isCurrent: true,
  },
  {
    id: "2",
    userName: "Priya Sharma",
    userEmail: "priya.sharma@company.com",
    deviceType: "desktop",
    deviceOs: "macOS Sonoma",
    deviceBrowser: "Safari 17",
    ipAddress: "10.0.0.23",
    geoCountry: "India",
    geoCity: "Bangalore",
    createdAt: "2026-01-14T09:15:00Z",
    lastActivityAt: "2026-01-14T10:30:00Z",
    expiresAt: "2026-01-14T17:15:00Z",
    isActive: true,
    mfaVerified: true,
    isCurrent: false,
  },
  {
    id: "3",
    userName: "Rajesh Kumar",
    userEmail: "rajesh.kumar@company.com",
    deviceType: "mobile",
    deviceOs: "Android 14",
    deviceBrowser: "Chrome Mobile",
    ipAddress: "172.16.0.12",
    geoCountry: "India",
    geoCity: "Delhi",
    createdAt: "2026-01-14T07:30:00Z",
    lastActivityAt: "2026-01-14T09:45:00Z",
    expiresAt: "2026-01-14T15:30:00Z",
    isActive: true,
    mfaVerified: false,
    isCurrent: false,
  },
  {
    id: "4",
    userName: "Neha Gupta",
    userEmail: "neha.gupta@company.com",
    deviceType: "tablet",
    deviceOs: "iPadOS 17",
    deviceBrowser: "Safari",
    ipAddress: "10.0.0.89",
    geoCountry: "India",
    geoCity: "Chennai",
    createdAt: "2026-01-14T06:00:00Z",
    lastActivityAt: "2026-01-14T08:20:00Z",
    expiresAt: "2026-01-14T14:00:00Z",
    isActive: true,
    mfaVerified: true,
    isCurrent: false,
  },
  {
    id: "5",
    userName: "Vikram Singh",
    userEmail: "vikram.singh@company.com",
    deviceType: "desktop",
    deviceOs: "Ubuntu 22.04",
    deviceBrowser: "Firefox 121",
    ipAddress: "10.0.0.45",
    geoCountry: "India",
    geoCity: "Hyderabad",
    createdAt: "2026-01-13T14:00:00Z",
    lastActivityAt: "2026-01-13T18:30:00Z",
    expiresAt: "2026-01-13T22:00:00Z",
    isActive: false,
    mfaVerified: true,
    isCurrent: false,
  },
];

export default function SessionsPage() {
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState("active");
  const [deviceFilter, setDeviceFilter] = useState("all");
  const [revokeDialogOpen, setRevokeDialogOpen] = useState(false);
  const [selectedSession, setSelectedSession] = useState<typeof sessions[0] | null>(null);
  const [revokeAllDialogOpen, setRevokeAllDialogOpen] = useState(false);

  const getDeviceIcon = (deviceType: string) => {
    switch (deviceType) {
      case "desktop":
        return <Monitor className="h-4 w-4" />;
      case "mobile":
        return <Smartphone className="h-4 w-4" />;
      case "tablet":
        return <Tablet className="h-4 w-4" />;
      default:
        return <Monitor className="h-4 w-4" />;
    }
  };

  const formatDateTime = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString("en-IN", {
      day: "2-digit",
      month: "short",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const getTimeSince = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);

    if (diffMins < 1) return "Just now";
    if (diffMins < 60) return `${diffMins} min ago`;
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours}h ago`;
    const diffDays = Math.floor(diffHours / 24);
    return `${diffDays}d ago`;
  };

  const filteredSessions = sessions.filter((session) => {
    const matchesSearch =
      session.userName.toLowerCase().includes(searchQuery.toLowerCase()) ||
      session.userEmail.toLowerCase().includes(searchQuery.toLowerCase()) ||
      session.ipAddress.includes(searchQuery);

    const matchesStatus =
      statusFilter === "all" ||
      (statusFilter === "active" && session.isActive) ||
      (statusFilter === "expired" && !session.isActive);

    const matchesDevice =
      deviceFilter === "all" || session.deviceType === deviceFilter;

    return matchesSearch && matchesStatus && matchesDevice;
  });

  const handleRevokeSession = (session: typeof sessions[0]) => {
    setSelectedSession(session);
    setRevokeDialogOpen(true);
  };

  const activeSessions = sessions.filter((s) => s.isActive).length;

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
            <h1 className="text-3xl font-bold tracking-tight">Active Sessions</h1>
            <p className="text-muted-foreground">
              Manage user sessions across all devices
            </p>
          </div>
        </div>
        <div className="flex gap-2">
          <Button variant="outline">
            <RefreshCw className="mr-2 h-4 w-4" />
            Refresh
          </Button>
          <Button
            variant="destructive"
            onClick={() => setRevokeAllDialogOpen(true)}
          >
            <XCircle className="mr-2 h-4 w-4" />
            Revoke All
          </Button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Sessions</CardTitle>
            <User className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{activeSessions}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Desktop</CardTitle>
            <Monitor className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {sessions.filter((s) => s.isActive && s.deviceType === "desktop").length}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Mobile</CardTitle>
            <Smartphone className="h-4 w-4 text-purple-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {sessions.filter((s) => s.isActive && s.deviceType === "mobile").length}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Tablet</CardTitle>
            <Tablet className="h-4 w-4 text-orange-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {sessions.filter((s) => s.isActive && s.deviceType === "tablet").length}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Sessions Table */}
      <Card>
        <CardHeader>
          <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <div>
              <CardTitle>All Sessions</CardTitle>
              <CardDescription>View and manage active user sessions</CardDescription>
            </div>
            <div className="flex flex-wrap gap-2">
              <div className="relative">
                <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search sessions..."
                  className="pl-8 w-[200px]"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </div>
              <Select value={statusFilter} onValueChange={setStatusFilter}>
                <SelectTrigger className="w-[120px]">
                  <SelectValue placeholder="Status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Status</SelectItem>
                  <SelectItem value="active">Active</SelectItem>
                  <SelectItem value="expired">Expired</SelectItem>
                </SelectContent>
              </Select>
              <Select value={deviceFilter} onValueChange={setDeviceFilter}>
                <SelectTrigger className="w-[120px]">
                  <SelectValue placeholder="Device" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Devices</SelectItem>
                  <SelectItem value="desktop">Desktop</SelectItem>
                  <SelectItem value="mobile">Mobile</SelectItem>
                  <SelectItem value="tablet">Tablet</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>User</TableHead>
                <TableHead>Device</TableHead>
                <TableHead>Location</TableHead>
                <TableHead>Last Active</TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="w-[100px]"></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredSessions.map((session) => (
                <TableRow key={session.id}>
                  <TableCell>
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-medium">{session.userName}</span>
                        {session.isCurrent && (
                          <Badge variant="outline" className="text-xs">You</Badge>
                        )}
                      </div>
                      <div className="text-xs text-muted-foreground">
                        {session.userEmail}
                      </div>
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      {getDeviceIcon(session.deviceType)}
                      <div>
                        <div className="text-sm">{session.deviceOs}</div>
                        <div className="text-xs text-muted-foreground">
                          {session.deviceBrowser}
                        </div>
                      </div>
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      <MapPin className="h-4 w-4 text-muted-foreground" />
                      <div>
                        <div className="text-sm">
                          {session.geoCity}, {session.geoCountry}
                        </div>
                        <div className="text-xs text-muted-foreground font-mono">
                          {session.ipAddress}
                        </div>
                      </div>
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      <Clock className="h-4 w-4 text-muted-foreground" />
                      <div>
                        <div className="text-sm">{getTimeSince(session.lastActivityAt)}</div>
                        <div className="text-xs text-muted-foreground">
                          {formatDateTime(session.lastActivityAt)}
                        </div>
                      </div>
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="flex flex-col gap-1">
                      {session.isActive ? (
                        <Badge className="bg-green-100 text-green-800 w-fit">Active</Badge>
                      ) : (
                        <Badge className="bg-gray-100 text-gray-800 w-fit">Expired</Badge>
                      )}
                      {session.mfaVerified && (
                        <Badge variant="outline" className="text-xs w-fit">MFA</Badge>
                      )}
                    </div>
                  </TableCell>
                  <TableCell>
                    {session.isActive && !session.isCurrent && (
                      <Button
                        variant="ghost"
                        size="sm"
                        className="text-red-600 hover:text-red-700"
                        onClick={() => handleRevokeSession(session)}
                      >
                        <XCircle className="mr-1 h-4 w-4" />
                        Revoke
                      </Button>
                    )}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Revoke Session Dialog */}
      <AlertDialog open={revokeDialogOpen} onOpenChange={setRevokeDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Revoke Session</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to revoke this session? The user will be logged out
              immediately.
              {selectedSession && (
                <div className="mt-4 p-3 bg-muted rounded-lg">
                  <div className="font-medium">{selectedSession.userName}</div>
                  <div className="text-sm">{selectedSession.deviceOs} - {selectedSession.deviceBrowser}</div>
                  <div className="text-sm text-muted-foreground">
                    {selectedSession.geoCity}, {selectedSession.geoCountry}
                  </div>
                </div>
              )}
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction className="bg-red-600 hover:bg-red-700">
              Revoke Session
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      {/* Revoke All Dialog */}
      <AlertDialog open={revokeAllDialogOpen} onOpenChange={setRevokeAllDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Revoke All Sessions</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to revoke all sessions except your current one?
              All users will be logged out immediately.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction className="bg-red-600 hover:bg-red-700">
              Revoke All Sessions
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
