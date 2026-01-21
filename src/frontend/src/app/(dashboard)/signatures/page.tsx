"use client";

import { useState } from "react";
import Link from "next/link";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
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
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  PenTool,
  FileText,
  Clock,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Plus,
  ArrowRight,
  Send,
  Eye,
  RefreshCw,
  TrendingUp,
  Users,
  FileSignature,
  Shield,
} from "lucide-react";

// Mock data
const dashboardStats = {
  pendingRequests: 12,
  inProgressRequests: 8,
  completedToday: 5,
  expiringSoon: 3,
  totalActive: 20,
  completionRate: 87.5,
  avgTimeToSign: 4.2,
};

const pendingSignatures = [
  {
    id: "1",
    requestNumber: "SIG-2024-000156",
    subject: "Employment Contract - John Doe",
    requester: "HR Department",
    dueDate: "2024-06-18",
    signers: 2,
    completed: 1,
    status: "in_progress",
  },
  {
    id: "2",
    requestNumber: "SIG-2024-000155",
    subject: "Vendor Agreement - Tech Solutions",
    requester: "Procurement",
    dueDate: "2024-06-20",
    signers: 3,
    completed: 0,
    status: "pending",
  },
  {
    id: "3",
    requestNumber: "SIG-2024-000154",
    subject: "NDA - Confidential Project",
    requester: "Legal",
    dueDate: "2024-06-15",
    signers: 2,
    completed: 2,
    status: "completed",
  },
];

const recentActivity = [
  {
    action: "Document Signed",
    request: "SIG-2024-000154",
    signer: "Amit Patel",
    time: "2 hours ago",
    status: "success",
  },
  {
    action: "Request Sent",
    request: "SIG-2024-000156",
    signer: "HR Department",
    time: "3 hours ago",
    status: "info",
  },
  {
    action: "Reminder Sent",
    request: "SIG-2024-000150",
    signer: "Priya Sharma",
    time: "5 hours ago",
    status: "warning",
  },
  {
    action: "Document Rejected",
    request: "SIG-2024-000148",
    signer: "Rajesh Kumar",
    time: "1 day ago",
    status: "error",
  },
];

const bySignatureType = {
  electronic: 45,
  digital: 30,
  aadhaar_esign: 20,
  dsc: 5,
};

export default function SignaturesDashboardPage() {
  const [activeTab, setActiveTab] = useState("overview");

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "pending":
        return <Badge className="bg-yellow-100 text-yellow-800">Pending</Badge>;
      case "in_progress":
        return <Badge className="bg-blue-100 text-blue-800">In Progress</Badge>;
      case "completed":
        return <Badge className="bg-green-100 text-green-800">Completed</Badge>;
      case "rejected":
        return <Badge className="bg-red-100 text-red-800">Rejected</Badge>;
      default:
        return <Badge variant="outline">{status}</Badge>;
    }
  };

  const getActivityIcon = (status: string) => {
    switch (status) {
      case "success":
        return <CheckCircle className="h-4 w-4 text-green-600" />;
      case "error":
        return <XCircle className="h-4 w-4 text-red-600" />;
      case "warning":
        return <AlertTriangle className="h-4 w-4 text-yellow-600" />;
      default:
        return <FileText className="h-4 w-4 text-blue-600" />;
    }
  };

  return (
    <div className="flex flex-col gap-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Digital Signatures</h1>
          <p className="text-muted-foreground">
            Manage document signing workflows and track signature requests
          </p>
        </div>
        <div className="flex gap-2">
          <Link href="/signatures/templates">
            <Button variant="outline">
              <FileSignature className="mr-2 h-4 w-4" />
              Templates
            </Button>
          </Link>
          <Link href="/signatures/requests/new">
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              New Request
            </Button>
          </Link>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Pending Signatures</CardTitle>
            <Clock className="h-4 w-4 text-yellow-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{dashboardStats.pendingRequests}</div>
            <p className="text-xs text-muted-foreground">Awaiting action</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">In Progress</CardTitle>
            <RefreshCw className="h-4 w-4 text-blue-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{dashboardStats.inProgressRequests}</div>
            <p className="text-xs text-muted-foreground">Partially signed</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Completed Today</CardTitle>
            <CheckCircle className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{dashboardStats.completedToday}</div>
            <p className="text-xs text-muted-foreground">All signatures done</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Expiring Soon</CardTitle>
            <AlertTriangle className="h-4 w-4 text-orange-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{dashboardStats.expiringSoon}</div>
            <p className="text-xs text-muted-foreground">Within 3 days</p>
          </CardContent>
        </Card>
      </div>

      {/* Main Content */}
      <div className="grid gap-6 md:grid-cols-3">
        {/* Pending Requests */}
        <Card className="md:col-span-2">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Recent Requests</CardTitle>
                <CardDescription>Latest signature requests</CardDescription>
              </div>
              <Link href="/signatures/requests">
                <Button variant="outline" size="sm">
                  View All
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </Link>
            </div>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Request</TableHead>
                  <TableHead>Due Date</TableHead>
                  <TableHead>Progress</TableHead>
                  <TableHead>Status</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {pendingSignatures.map((request) => (
                  <TableRow key={request.id}>
                    <TableCell>
                      <div>
                        <div className="font-medium">{request.requestNumber}</div>
                        <div className="text-sm text-muted-foreground truncate max-w-[250px]">
                          {request.subject}
                        </div>
                      </div>
                    </TableCell>
                    <TableCell>{request.dueDate}</TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <Progress
                          value={(request.completed / request.signers) * 100}
                          className="h-2 w-16"
                        />
                        <span className="text-xs text-muted-foreground">
                          {request.completed}/{request.signers}
                        </span>
                      </div>
                    </TableCell>
                    <TableCell>{getStatusBadge(request.status)}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>

        {/* Recent Activity */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
            <CardDescription>Latest signature events</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {recentActivity.map((activity, index) => (
                <div key={index} className="flex items-start gap-3">
                  <div className="mt-0.5">{getActivityIcon(activity.status)}</div>
                  <div className="flex-1">
                    <div className="text-sm font-medium">{activity.action}</div>
                    <div className="text-xs text-muted-foreground">
                      {activity.request} - {activity.signer}
                    </div>
                    <div className="text-xs text-muted-foreground">{activity.time}</div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Analytics Row */}
      <div className="grid gap-6 md:grid-cols-2">
        {/* Performance Metrics */}
        <Card>
          <CardHeader>
            <CardTitle>Performance Metrics</CardTitle>
            <CardDescription>Last 30 days</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-6">
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium">Completion Rate</span>
                  <span className="text-sm text-muted-foreground">
                    {dashboardStats.completionRate}%
                  </span>
                </div>
                <Progress value={dashboardStats.completionRate} className="h-2" />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="p-4 bg-muted rounded-lg">
                  <div className="flex items-center gap-2">
                    <TrendingUp className="h-4 w-4 text-green-600" />
                    <span className="text-sm font-medium">Avg. Sign Time</span>
                  </div>
                  <div className="text-2xl font-bold mt-2">
                    {dashboardStats.avgTimeToSign}h
                  </div>
                </div>
                <div className="p-4 bg-muted rounded-lg">
                  <div className="flex items-center gap-2">
                    <Users className="h-4 w-4 text-blue-600" />
                    <span className="text-sm font-medium">Total Active</span>
                  </div>
                  <div className="text-2xl font-bold mt-2">
                    {dashboardStats.totalActive}
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* By Signature Type */}
        <Card>
          <CardHeader>
            <CardTitle>By Signature Type</CardTitle>
            <CardDescription>Distribution of signature methods</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <PenTool className="h-4 w-4 text-blue-600" />
                  <span className="text-sm">Electronic Signature</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium">{bySignatureType.electronic}%</span>
                  <Progress value={bySignatureType.electronic} className="h-2 w-20" />
                </div>
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Shield className="h-4 w-4 text-green-600" />
                  <span className="text-sm">Digital Signature</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium">{bySignatureType.digital}%</span>
                  <Progress value={bySignatureType.digital} className="h-2 w-20" />
                </div>
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <FileSignature className="h-4 w-4 text-purple-600" />
                  <span className="text-sm">Aadhaar eSign</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium">{bySignatureType.aadhaar_esign}%</span>
                  <Progress value={bySignatureType.aadhaar_esign} className="h-2 w-20" />
                </div>
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <FileText className="h-4 w-4 text-orange-600" />
                  <span className="text-sm">DSC Token</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium">{bySignatureType.dsc}%</span>
                  <Progress value={bySignatureType.dsc} className="h-2 w-20" />
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-4">
            <Link href="/signatures/requests/new">
              <div className="p-4 border rounded-lg hover:bg-muted cursor-pointer transition-colors">
                <Send className="h-6 w-6 text-blue-600 mb-2" />
                <div className="font-medium">Send for Signature</div>
                <div className="text-sm text-muted-foreground">
                  Create new signature request
                </div>
              </div>
            </Link>

            <Link href="/signatures/templates">
              <div className="p-4 border rounded-lg hover:bg-muted cursor-pointer transition-colors">
                <FileSignature className="h-6 w-6 text-green-600 mb-2" />
                <div className="font-medium">Manage Templates</div>
                <div className="text-sm text-muted-foreground">
                  Create and edit templates
                </div>
              </div>
            </Link>

            <Link href="/signatures/certificates">
              <div className="p-4 border rounded-lg hover:bg-muted cursor-pointer transition-colors">
                <Shield className="h-6 w-6 text-purple-600 mb-2" />
                <div className="font-medium">Certificates</div>
                <div className="text-sm text-muted-foreground">
                  Manage digital certificates
                </div>
              </div>
            </Link>

            <Link href="/signatures/requests">
              <div className="p-4 border rounded-lg hover:bg-muted cursor-pointer transition-colors">
                <Eye className="h-6 w-6 text-orange-600 mb-2" />
                <div className="font-medium">View All Requests</div>
                <div className="text-sm text-muted-foreground">
                  Browse signature requests
                </div>
              </div>
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
