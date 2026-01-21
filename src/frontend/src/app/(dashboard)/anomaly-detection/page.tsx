"use client";

import { useState } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  AlertTriangle,
  Brain,
  TrendingUp,
  Activity,
  CheckCircle2,
  XCircle,
  Clock,
  Eye,
  MoreHorizontal,
  Play,
  RefreshCw,
  Settings,
  FileText,
  BarChart3,
  Zap,
  Shield,
  DollarSign,
  Users,
  AlertCircle,
} from "lucide-react";

// Mock data
const mockDashboard = {
  total_detections: 147,
  pending_review: 23,
  confirmed_anomalies: 89,
  false_positives: 12,
  resolved: 23,
  critical_count: 5,
  high_count: 18,
  medium_count: 67,
  low_count: 57,
  financial_count: 45,
  operational_count: 38,
  hr_count: 22,
  security_count: 28,
  compliance_count: 14,
  total_financial_impact: 1250000,
  precision_rate: 0.88,
  avg_resolution_time_hours: 4.5,
  active_rules_count: 24,
  active_models_count: 3,
  detection_trend_7d: [
    { date: "2026-01-08", count: 12 },
    { date: "2026-01-09", count: 18 },
    { date: "2026-01-10", count: 15 },
    { date: "2026-01-11", count: 22 },
    { date: "2026-01-12", count: 19 },
    { date: "2026-01-13", count: 25 },
    { date: "2026-01-14", count: 14 },
  ],
};

const mockDetections = [
  {
    id: "1",
    detection_number: "ANM-2026-000147",
    title: "Unusual expense pattern detected",
    category: "financial",
    severity: "high",
    status: "pending",
    data_source: "expenses",
    entity_name: "Marketing Department",
    observed_value: 125000,
    expected_value: 45000,
    deviation: 177.78,
    confidence_score: 0.94,
    detected_at: "2026-01-14T10:30:00Z",
  },
  {
    id: "2",
    detection_number: "ANM-2026-000146",
    title: "Employee attendance anomaly",
    category: "hr",
    severity: "medium",
    status: "investigating",
    data_source: "attendance",
    entity_name: "John Smith",
    observed_value: 2,
    expected_value: 22,
    deviation: -90.9,
    confidence_score: 0.87,
    detected_at: "2026-01-14T09:15:00Z",
  },
  {
    id: "3",
    detection_number: "ANM-2026-000145",
    title: "Invoice amount spike",
    category: "financial",
    severity: "critical",
    status: "confirmed",
    data_source: "invoices",
    entity_name: "Vendor ABC Corp",
    observed_value: 500000,
    expected_value: 75000,
    deviation: 566.67,
    confidence_score: 0.98,
    detected_at: "2026-01-13T16:45:00Z",
  },
  {
    id: "4",
    detection_number: "ANM-2026-000144",
    title: "Security access outside hours",
    category: "security",
    severity: "high",
    status: "pending",
    data_source: "access_logs",
    entity_name: "Server Room",
    observed_value: 15,
    expected_value: 0,
    deviation: 100,
    confidence_score: 0.91,
    detected_at: "2026-01-13T14:20:00Z",
  },
  {
    id: "5",
    detection_number: "ANM-2026-000143",
    title: "Compliance deadline missed pattern",
    category: "compliance",
    severity: "medium",
    status: "resolved",
    data_source: "compliance_tracker",
    entity_name: "GST Returns",
    observed_value: 3,
    expected_value: 0,
    deviation: 100,
    confidence_score: 0.85,
    detected_at: "2026-01-13T11:00:00Z",
  },
];

const mockRules = [
  {
    id: "1",
    name: "Expense Spike Detection",
    code: "EXP-SPIKE-001",
    category: "financial",
    data_source: "expenses",
    severity: "high",
    is_active: true,
    confidence_threshold: 0.85,
    detections_count: 45,
  },
  {
    id: "2",
    name: "Attendance Anomaly",
    code: "HR-ATT-001",
    category: "hr",
    data_source: "attendance",
    severity: "medium",
    is_active: true,
    confidence_threshold: 0.80,
    detections_count: 22,
  },
  {
    id: "3",
    name: "Invoice Pattern Analyzer",
    code: "FIN-INV-001",
    category: "financial",
    data_source: "invoices",
    severity: "high",
    is_active: true,
    confidence_threshold: 0.90,
    detections_count: 38,
  },
  {
    id: "4",
    name: "After Hours Access",
    code: "SEC-ACC-001",
    category: "security",
    data_source: "access_logs",
    severity: "critical",
    is_active: true,
    confidence_threshold: 0.85,
    detections_count: 28,
  },
];

const mockModels = [
  {
    id: "1",
    name: "Financial Anomaly Detector",
    model_type: "isolation_forest",
    version: "1.0.20260110",
    status: "deployed",
    accuracy: 0.95,
    precision: 0.92,
    recall: 0.89,
    inference_count: 12500,
  },
  {
    id: "2",
    name: "Time Series Predictor",
    model_type: "lstm",
    version: "1.0.20260105",
    status: "deployed",
    accuracy: 0.91,
    precision: 0.88,
    recall: 0.85,
    inference_count: 8200,
  },
  {
    id: "3",
    name: "Pattern Autoencoder",
    model_type: "autoencoder",
    version: "1.0.20260101",
    status: "training",
    accuracy: null,
    precision: null,
    recall: null,
    inference_count: 0,
  },
];

const getSeverityBadge = (severity: string) => {
  const variants: Record<string, { variant: "default" | "secondary" | "destructive" | "outline"; className: string }> = {
    critical: { variant: "destructive", className: "bg-red-600" },
    high: { variant: "destructive", className: "bg-orange-500" },
    medium: { variant: "secondary", className: "bg-yellow-500 text-black" },
    low: { variant: "outline", className: "bg-blue-100 text-blue-700" },
  };
  const config = variants[severity] || variants.medium;
  return <Badge className={config.className}>{severity}</Badge>;
};

const getStatusBadge = (status: string) => {
  const variants: Record<string, { icon: React.ReactNode; className: string }> = {
    pending: { icon: <Clock className="h-3 w-3" />, className: "bg-gray-100 text-gray-700" },
    investigating: { icon: <Eye className="h-3 w-3" />, className: "bg-blue-100 text-blue-700" },
    confirmed: { icon: <AlertCircle className="h-3 w-3" />, className: "bg-red-100 text-red-700" },
    false_positive: { icon: <XCircle className="h-3 w-3" />, className: "bg-gray-100 text-gray-500" },
    resolved: { icon: <CheckCircle2 className="h-3 w-3" />, className: "bg-green-100 text-green-700" },
  };
  const config = variants[status] || variants.pending;
  return (
    <Badge variant="outline" className={`gap-1 ${config.className}`}>
      {config.icon}
      {status.replace("_", " ")}
    </Badge>
  );
};

const getCategoryIcon = (category: string) => {
  const icons: Record<string, React.ReactNode> = {
    financial: <DollarSign className="h-4 w-4 text-green-600" />,
    operational: <Activity className="h-4 w-4 text-blue-600" />,
    hr: <Users className="h-4 w-4 text-purple-600" />,
    security: <Shield className="h-4 w-4 text-red-600" />,
    compliance: <FileText className="h-4 w-4 text-orange-600" />,
  };
  return icons[category] || <AlertTriangle className="h-4 w-4" />;
};

const getModelStatusBadge = (status: string) => {
  const variants: Record<string, string> = {
    deployed: "bg-green-100 text-green-700",
    training: "bg-blue-100 text-blue-700",
    trained: "bg-yellow-100 text-yellow-700",
    draft: "bg-gray-100 text-gray-700",
    failed: "bg-red-100 text-red-700",
    retired: "bg-gray-100 text-gray-500",
  };
  return <Badge className={variants[status] || variants.draft}>{status}</Badge>;
};

export default function AnomalyDetectionPage() {
  const [timeRange, setTimeRange] = useState("30d");
  const [categoryFilter, setCategoryFilter] = useState("all");

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat("en-IN", {
      style: "currency",
      currency: "INR",
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const formatPercent = (value: number | null) => {
    if (value === null) return "N/A";
    return `${(value * 100).toFixed(1)}%`;
  };

  return (
    <div className="flex flex-col gap-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <Brain className="h-8 w-8 text-purple-600" />
            AI Anomaly Detection
          </h1>
          <p className="text-muted-foreground mt-1">
            Intelligent detection of unusual patterns across your business data
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Select value={timeRange} onValueChange={setTimeRange}>
            <SelectTrigger className="w-32">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="7d">Last 7 days</SelectItem>
              <SelectItem value="30d">Last 30 days</SelectItem>
              <SelectItem value="90d">Last 90 days</SelectItem>
            </SelectContent>
          </Select>
          <Button variant="outline">
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
          <Button>
            <Play className="h-4 w-4 mr-2" />
            Run Detection
          </Button>
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-5">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Total Detections</CardTitle>
            <AlertTriangle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{mockDashboard.total_detections}</div>
            <p className="text-xs text-muted-foreground">
              +12% from last period
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Pending Review</CardTitle>
            <Clock className="h-4 w-4 text-yellow-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-600">
              {mockDashboard.pending_review}
            </div>
            <p className="text-xs text-muted-foreground">
              Requires investigation
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Confirmed</CardTitle>
            <AlertCircle className="h-4 w-4 text-red-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">
              {mockDashboard.confirmed_anomalies}
            </div>
            <p className="text-xs text-muted-foreground">
              True anomalies detected
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Precision Rate</CardTitle>
            <TrendingUp className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              {formatPercent(mockDashboard.precision_rate)}
            </div>
            <p className="text-xs text-muted-foreground">
              Detection accuracy
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Financial Impact</CardTitle>
            <DollarSign className="h-4 w-4 text-purple-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {formatCurrency(mockDashboard.total_financial_impact)}
            </div>
            <p className="text-xs text-muted-foreground">
              Potential savings identified
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Severity & Category Distribution */}
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>By Severity</CardTitle>
            <CardDescription>Distribution of anomalies by severity level</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="h-3 w-3 rounded-full bg-red-600" />
                  <span>Critical</span>
                </div>
                <span className="font-bold">{mockDashboard.critical_count}</span>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="h-3 w-3 rounded-full bg-orange-500" />
                  <span>High</span>
                </div>
                <span className="font-bold">{mockDashboard.high_count}</span>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="h-3 w-3 rounded-full bg-yellow-500" />
                  <span>Medium</span>
                </div>
                <span className="font-bold">{mockDashboard.medium_count}</span>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="h-3 w-3 rounded-full bg-blue-400" />
                  <span>Low</span>
                </div>
                <span className="font-bold">{mockDashboard.low_count}</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>By Category</CardTitle>
            <CardDescription>Distribution of anomalies by business area</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <DollarSign className="h-4 w-4 text-green-600" />
                  <span>Financial</span>
                </div>
                <span className="font-bold">{mockDashboard.financial_count}</span>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Activity className="h-4 w-4 text-blue-600" />
                  <span>Operational</span>
                </div>
                <span className="font-bold">{mockDashboard.operational_count}</span>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Shield className="h-4 w-4 text-red-600" />
                  <span>Security</span>
                </div>
                <span className="font-bold">{mockDashboard.security_count}</span>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Users className="h-4 w-4 text-purple-600" />
                  <span>HR</span>
                </div>
                <span className="font-bold">{mockDashboard.hr_count}</span>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <FileText className="h-4 w-4 text-orange-600" />
                  <span>Compliance</span>
                </div>
                <span className="font-bold">{mockDashboard.compliance_count}</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Detection Trend Chart */}
      <Card>
        <CardHeader>
          <CardTitle>Detection Trend (Last 7 Days)</CardTitle>
          <CardDescription>Daily anomaly detections over time</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-end gap-2 h-32">
            {mockDashboard.detection_trend_7d.map((day, i) => (
              <div key={i} className="flex-1 flex flex-col items-center gap-1">
                <div
                  className="w-full bg-purple-500 rounded-t"
                  style={{ height: `${(day.count / 30) * 100}%` }}
                />
                <span className="text-xs text-muted-foreground">
                  {new Date(day.date).toLocaleDateString("en-US", { weekday: "short" })}
                </span>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Tabs for Detections, Rules, and Models */}
      <Tabs defaultValue="detections" className="space-y-4">
        <TabsList>
          <TabsTrigger value="detections" className="gap-2">
            <AlertTriangle className="h-4 w-4" />
            Recent Detections
          </TabsTrigger>
          <TabsTrigger value="rules" className="gap-2">
            <Settings className="h-4 w-4" />
            Rules ({mockDashboard.active_rules_count})
          </TabsTrigger>
          <TabsTrigger value="models" className="gap-2">
            <Brain className="h-4 w-4" />
            ML Models ({mockDashboard.active_models_count})
          </TabsTrigger>
        </TabsList>

        {/* Detections Tab */}
        <TabsContent value="detections">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Recent Anomaly Detections</CardTitle>
                  <CardDescription>Latest detected anomalies requiring attention</CardDescription>
                </div>
                <Select value={categoryFilter} onValueChange={setCategoryFilter}>
                  <SelectTrigger className="w-40">
                    <SelectValue placeholder="Filter by category" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Categories</SelectItem>
                    <SelectItem value="financial">Financial</SelectItem>
                    <SelectItem value="operational">Operational</SelectItem>
                    <SelectItem value="hr">HR</SelectItem>
                    <SelectItem value="security">Security</SelectItem>
                    <SelectItem value="compliance">Compliance</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Detection</TableHead>
                    <TableHead>Category</TableHead>
                    <TableHead>Severity</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Entity</TableHead>
                    <TableHead className="text-right">Deviation</TableHead>
                    <TableHead className="text-right">Confidence</TableHead>
                    <TableHead>Detected</TableHead>
                    <TableHead></TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {mockDetections.map((detection) => (
                    <TableRow key={detection.id}>
                      <TableCell>
                        <div>
                          <div className="font-medium">{detection.title}</div>
                          <div className="text-xs text-muted-foreground">
                            {detection.detection_number}
                          </div>
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          {getCategoryIcon(detection.category)}
                          <span className="capitalize">{detection.category}</span>
                        </div>
                      </TableCell>
                      <TableCell>{getSeverityBadge(detection.severity)}</TableCell>
                      <TableCell>{getStatusBadge(detection.status)}</TableCell>
                      <TableCell>{detection.entity_name}</TableCell>
                      <TableCell className="text-right">
                        <span className={detection.deviation > 0 ? "text-red-600" : "text-blue-600"}>
                          {detection.deviation > 0 ? "+" : ""}{detection.deviation.toFixed(1)}%
                        </span>
                      </TableCell>
                      <TableCell className="text-right">
                        {formatPercent(detection.confidence_score)}
                      </TableCell>
                      <TableCell>
                        {new Date(detection.detected_at).toLocaleDateString()}
                      </TableCell>
                      <TableCell>
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button variant="ghost" size="icon">
                              <MoreHorizontal className="h-4 w-4" />
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end">
                            <DropdownMenuItem>
                              <Eye className="h-4 w-4 mr-2" />
                              View Details
                            </DropdownMenuItem>
                            <DropdownMenuItem>
                              <CheckCircle2 className="h-4 w-4 mr-2" />
                              Confirm Anomaly
                            </DropdownMenuItem>
                            <DropdownMenuItem>
                              <XCircle className="h-4 w-4 mr-2" />
                              Mark False Positive
                            </DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Rules Tab */}
        <TabsContent value="rules">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Detection Rules</CardTitle>
                  <CardDescription>Configure rules for anomaly detection</CardDescription>
                </div>
                <Button>
                  <Zap className="h-4 w-4 mr-2" />
                  Add Rule
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Rule</TableHead>
                    <TableHead>Code</TableHead>
                    <TableHead>Category</TableHead>
                    <TableHead>Data Source</TableHead>
                    <TableHead>Severity</TableHead>
                    <TableHead className="text-right">Threshold</TableHead>
                    <TableHead className="text-right">Detections</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead></TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {mockRules.map((rule) => (
                    <TableRow key={rule.id}>
                      <TableCell className="font-medium">{rule.name}</TableCell>
                      <TableCell>
                        <code className="text-xs bg-muted px-1 py-0.5 rounded">
                          {rule.code}
                        </code>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          {getCategoryIcon(rule.category)}
                          <span className="capitalize">{rule.category}</span>
                        </div>
                      </TableCell>
                      <TableCell>{rule.data_source}</TableCell>
                      <TableCell>{getSeverityBadge(rule.severity)}</TableCell>
                      <TableCell className="text-right">
                        {formatPercent(rule.confidence_threshold)}
                      </TableCell>
                      <TableCell className="text-right">{rule.detections_count}</TableCell>
                      <TableCell>
                        <Badge variant={rule.is_active ? "default" : "secondary"}>
                          {rule.is_active ? "Active" : "Inactive"}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button variant="ghost" size="icon">
                              <MoreHorizontal className="h-4 w-4" />
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end">
                            <DropdownMenuItem>Edit Rule</DropdownMenuItem>
                            <DropdownMenuItem>
                              {rule.is_active ? "Deactivate" : "Activate"}
                            </DropdownMenuItem>
                            <DropdownMenuItem>Run Now</DropdownMenuItem>
                            <DropdownMenuItem className="text-red-600">Delete</DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Models Tab */}
        <TabsContent value="models">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>ML Models</CardTitle>
                  <CardDescription>Machine learning models for advanced detection</CardDescription>
                </div>
                <Button>
                  <Brain className="h-4 w-4 mr-2" />
                  Train New Model
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Model</TableHead>
                    <TableHead>Type</TableHead>
                    <TableHead>Version</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead className="text-right">Accuracy</TableHead>
                    <TableHead className="text-right">Precision</TableHead>
                    <TableHead className="text-right">Recall</TableHead>
                    <TableHead className="text-right">Inferences</TableHead>
                    <TableHead></TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {mockModels.map((model) => (
                    <TableRow key={model.id}>
                      <TableCell className="font-medium">{model.name}</TableCell>
                      <TableCell>
                        <code className="text-xs bg-muted px-1 py-0.5 rounded">
                          {model.model_type}
                        </code>
                      </TableCell>
                      <TableCell>{model.version}</TableCell>
                      <TableCell>{getModelStatusBadge(model.status)}</TableCell>
                      <TableCell className="text-right">
                        {model.accuracy ? formatPercent(model.accuracy) : "-"}
                      </TableCell>
                      <TableCell className="text-right">
                        {model.precision ? formatPercent(model.precision) : "-"}
                      </TableCell>
                      <TableCell className="text-right">
                        {model.recall ? formatPercent(model.recall) : "-"}
                      </TableCell>
                      <TableCell className="text-right">
                        {model.inference_count.toLocaleString()}
                      </TableCell>
                      <TableCell>
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button variant="ghost" size="icon">
                              <MoreHorizontal className="h-4 w-4" />
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end">
                            <DropdownMenuItem>View Details</DropdownMenuItem>
                            <DropdownMenuItem>
                              <BarChart3 className="h-4 w-4 mr-2" />
                              Performance Metrics
                            </DropdownMenuItem>
                            {model.status === "trained" && (
                              <DropdownMenuItem>Deploy Model</DropdownMenuItem>
                            )}
                            {model.status === "deployed" && (
                              <DropdownMenuItem>Retire Model</DropdownMenuItem>
                            )}
                            <DropdownMenuItem>Retrain</DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* System Stats */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Active Rules</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{mockDashboard.active_rules_count}</div>
            <p className="text-xs text-muted-foreground">
              Monitoring your data continuously
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Deployed Models</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{mockDashboard.active_models_count}</div>
            <p className="text-xs text-muted-foreground">
              ML models in production
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Avg Resolution Time</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {mockDashboard.avg_resolution_time_hours?.toFixed(1)}h
            </div>
            <p className="text-xs text-muted-foreground">
              Time to resolve anomalies
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
