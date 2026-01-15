"use client";

import { useState } from "react";
import Link from "next/link";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import {
  Shield,
  ShieldAlert,
  ShieldCheck,
  Users,
  Key,
  Lock,
  Eye,
  AlertTriangle,
  Activity,
  Globe,
  Clock,
  ArrowRight,
  CheckCircle,
  XCircle,
  FileText,
  Monitor,
  Smartphone,
} from "lucide-react";

// Mock data
const securityStats = {
  activeSessions: 24,
  failedLogins24h: 8,
  suspiciousActivities: 3,
  openIncidents: 1,
  blockedIPs: 5,
  mfaAdoptionRate: 68,
  usersWithMFA: 45,
  totalUsers: 66,
};

const recentAlerts = [
  {
    id: "1",
    type: "suspicious_login",
    title: "Suspicious login attempt",
    message: "Multiple failed login attempts from IP 203.45.67.89",
    severity: "high",
    time: "10 minutes ago",
    isRead: false,
  },
  {
    id: "2",
    type: "new_device",
    title: "New device detected",
    message: "User priya.sharma@company.com logged in from a new device",
    severity: "medium",
    time: "1 hour ago",
    isRead: false,
  },
  {
    id: "3",
    type: "permission_change",
    title: "Permission modified",
    message: "Admin role assigned to user rajesh.kumar@company.com",
    severity: "low",
    time: "2 hours ago",
    isRead: true,
  },
  {
    id: "4",
    type: "bulk_data_access",
    title: "Bulk data export",
    message: "User exported 500+ employee records",
    severity: "medium",
    time: "3 hours ago",
    isRead: true,
  },
];

const recentLogins = [
  {
    user: "amit.patel@company.com",
    ip: "192.168.1.45",
    location: "Mumbai, IN",
    device: "Chrome / Windows",
    time: "5 minutes ago",
    success: true,
  },
  {
    user: "priya.sharma@company.com",
    ip: "10.0.0.23",
    location: "Bangalore, IN",
    device: "Safari / macOS",
    time: "15 minutes ago",
    success: true,
  },
  {
    user: "unknown@company.com",
    ip: "203.45.67.89",
    location: "Unknown",
    device: "Firefox / Linux",
    time: "20 minutes ago",
    success: false,
  },
  {
    user: "rajesh.kumar@company.com",
    ip: "172.16.0.12",
    location: "Delhi, IN",
    device: "Mobile / Android",
    time: "1 hour ago",
    success: true,
  },
];

const activeSessions = [
  {
    user: "amit.patel@company.com",
    device: "Desktop",
    browser: "Chrome",
    location: "Mumbai, IN",
    lastActive: "Active now",
  },
  {
    user: "priya.sharma@company.com",
    device: "Desktop",
    browser: "Safari",
    location: "Bangalore, IN",
    lastActive: "5 min ago",
  },
  {
    user: "neha.gupta@company.com",
    device: "Mobile",
    browser: "Safari",
    location: "Chennai, IN",
    lastActive: "10 min ago",
  },
];

export default function SecurityDashboardPage() {
  const getSeverityBadge = (severity: string) => {
    switch (severity) {
      case "high":
        return <Badge className="bg-red-100 text-red-800">High</Badge>;
      case "medium":
        return <Badge className="bg-yellow-100 text-yellow-800">Medium</Badge>;
      case "low":
        return <Badge className="bg-blue-100 text-blue-800">Low</Badge>;
      default:
        return <Badge variant="outline">{severity}</Badge>;
    }
  };

  const getAlertIcon = (type: string) => {
    switch (type) {
      case "suspicious_login":
        return <ShieldAlert className="h-4 w-4 text-red-600" />;
      case "new_device":
        return <Monitor className="h-4 w-4 text-blue-600" />;
      case "permission_change":
        return <Key className="h-4 w-4 text-purple-600" />;
      case "bulk_data_access":
        return <FileText className="h-4 w-4 text-orange-600" />;
      default:
        return <AlertTriangle className="h-4 w-4 text-yellow-600" />;
    }
  };

  return (
    <div className="flex flex-col gap-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Security Center</h1>
          <p className="text-muted-foreground">
            Monitor security events and manage access controls
          </p>
        </div>
        <div className="flex gap-2">
          <Link href="/security/settings">
            <Button variant="outline">
              <Lock className="mr-2 h-4 w-4" />
              Security Settings
            </Button>
          </Link>
          <Link href="/security/incidents/new">
            <Button>
              <ShieldAlert className="mr-2 h-4 w-4" />
              Report Incident
            </Button>
          </Link>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-5">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Sessions</CardTitle>
            <Users className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{securityStats.activeSessions}</div>
            <p className="text-xs text-muted-foreground">Currently online</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Failed Logins</CardTitle>
            <XCircle className="h-4 w-4 text-red-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">{securityStats.failedLogins24h}</div>
            <p className="text-xs text-muted-foreground">Last 24 hours</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Suspicious Activity</CardTitle>
            <AlertTriangle className="h-4 w-4 text-yellow-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-600">{securityStats.suspiciousActivities}</div>
            <p className="text-xs text-muted-foreground">Needs review</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Open Incidents</CardTitle>
            <ShieldAlert className="h-4 w-4 text-orange-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-600">{securityStats.openIncidents}</div>
            <p className="text-xs text-muted-foreground">Unresolved</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Blocked IPs</CardTitle>
            <Globe className="h-4 w-4 text-gray-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{securityStats.blockedIPs}</div>
            <p className="text-xs text-muted-foreground">Active blocks</p>
          </CardContent>
        </Card>
      </div>

      {/* MFA Adoption */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>MFA Adoption</CardTitle>
              <CardDescription>Multi-factor authentication status</CardDescription>
            </div>
            <Link href="/security/mfa">
              <Button variant="outline" size="sm">
                Manage MFA
                <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </Link>
          </div>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-8">
            <div className="flex-1">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium">Adoption Rate</span>
                <span className="text-sm text-muted-foreground">
                  {securityStats.usersWithMFA} of {securityStats.totalUsers} users
                </span>
              </div>
              <Progress value={securityStats.mfaAdoptionRate} className="h-3" />
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold">{securityStats.mfaAdoptionRate}%</div>
              <p className="text-xs text-muted-foreground">with MFA enabled</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Main Content Grid */}
      <div className="grid gap-6 md:grid-cols-2">
        {/* Recent Alerts */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Recent Alerts</CardTitle>
                <CardDescription>Security alerts requiring attention</CardDescription>
              </div>
              <Link href="/security/alerts">
                <Button variant="outline" size="sm">
                  View All
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </Link>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {recentAlerts.map((alert) => (
                <div
                  key={alert.id}
                  className={`flex items-start gap-3 p-3 rounded-lg border ${
                    !alert.isRead ? "bg-muted/50" : ""
                  }`}
                >
                  <div className="mt-0.5">{getAlertIcon(alert.type)}</div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="font-medium text-sm">{alert.title}</span>
                      {!alert.isRead && (
                        <span className="w-2 h-2 rounded-full bg-blue-600" />
                      )}
                    </div>
                    <p className="text-xs text-muted-foreground truncate">
                      {alert.message}
                    </p>
                    <div className="flex items-center gap-2 mt-1">
                      {getSeverityBadge(alert.severity)}
                      <span className="text-xs text-muted-foreground">{alert.time}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Recent Login Activity */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Recent Logins</CardTitle>
                <CardDescription>Login activity overview</CardDescription>
              </div>
              <Link href="/security/login-history">
                <Button variant="outline" size="sm">
                  View All
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </Link>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {recentLogins.map((login, index) => (
                <div key={index} className="flex items-center gap-3">
                  <div className="flex-shrink-0">
                    {login.success ? (
                      <CheckCircle className="h-5 w-5 text-green-600" />
                    ) : (
                      <XCircle className="h-5 w-5 text-red-600" />
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium truncate">{login.user}</span>
                      <span className="text-xs text-muted-foreground">{login.time}</span>
                    </div>
                    <div className="text-xs text-muted-foreground">
                      {login.ip} • {login.location} • {login.device}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Active Sessions and Quick Actions */}
      <div className="grid gap-6 md:grid-cols-3">
        {/* Active Sessions */}
        <Card className="md:col-span-2">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Active Sessions</CardTitle>
                <CardDescription>Currently logged in users</CardDescription>
              </div>
              <Link href="/security/sessions">
                <Button variant="outline" size="sm">
                  Manage Sessions
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </Link>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {activeSessions.map((session, index) => (
                <div key={index} className="flex items-center gap-4 p-3 border rounded-lg">
                  <div className="p-2 bg-muted rounded-lg">
                    {session.device === "Mobile" ? (
                      <Smartphone className="h-5 w-5" />
                    ) : (
                      <Monitor className="h-5 w-5" />
                    )}
                  </div>
                  <div className="flex-1">
                    <div className="font-medium text-sm">{session.user}</div>
                    <div className="text-xs text-muted-foreground">
                      {session.browser} • {session.location}
                    </div>
                  </div>
                  <div className="text-right">
                    <Badge
                      variant="outline"
                      className={session.lastActive === "Active now" ? "border-green-500 text-green-600" : ""}
                    >
                      {session.lastActive}
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Quick Actions */}
        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <Link href="/security/audit-logs">
                <div className="p-3 border rounded-lg hover:bg-muted cursor-pointer transition-colors">
                  <div className="flex items-center gap-3">
                    <Eye className="h-5 w-5 text-blue-600" />
                    <div>
                      <div className="font-medium text-sm">Audit Logs</div>
                      <div className="text-xs text-muted-foreground">
                        View security events
                      </div>
                    </div>
                  </div>
                </div>
              </Link>

              <Link href="/security/tokens">
                <div className="p-3 border rounded-lg hover:bg-muted cursor-pointer transition-colors">
                  <div className="flex items-center gap-3">
                    <Key className="h-5 w-5 text-purple-600" />
                    <div>
                      <div className="font-medium text-sm">API Tokens</div>
                      <div className="text-xs text-muted-foreground">
                        Manage access tokens
                      </div>
                    </div>
                  </div>
                </div>
              </Link>

              <Link href="/security/ip-blocklist">
                <div className="p-3 border rounded-lg hover:bg-muted cursor-pointer transition-colors">
                  <div className="flex items-center gap-3">
                    <Globe className="h-5 w-5 text-red-600" />
                    <div>
                      <div className="font-medium text-sm">IP Blocklist</div>
                      <div className="text-xs text-muted-foreground">
                        Manage blocked IPs
                      </div>
                    </div>
                  </div>
                </div>
              </Link>

              <Link href="/security/incidents">
                <div className="p-3 border rounded-lg hover:bg-muted cursor-pointer transition-colors">
                  <div className="flex items-center gap-3">
                    <ShieldAlert className="h-5 w-5 text-orange-600" />
                    <div>
                      <div className="font-medium text-sm">Incidents</div>
                      <div className="text-xs text-muted-foreground">
                        Security incidents
                      </div>
                    </div>
                  </div>
                </div>
              </Link>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
