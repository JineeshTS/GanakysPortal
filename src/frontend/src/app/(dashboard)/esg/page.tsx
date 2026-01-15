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
import { Progress } from "@/components/ui/progress";
import {
  Leaf,
  Factory,
  Droplets,
  Trash2,
  Zap,
  Target,
  AlertTriangle,
  Award,
  TrendingDown,
  TrendingUp,
  Users,
  Globe,
  MoreHorizontal,
  Plus,
  FileText,
  RefreshCw,
  Building,
  Gauge,
  BarChart3,
} from "lucide-react";

// Mock data
const mockDashboard = {
  total_scope1_emissions: 1250.5,
  total_scope2_emissions: 3420.8,
  total_scope3_emissions: 8750.2,
  total_emissions: 13421.5,
  yoy_emissions_change: -12.5,
  total_energy_consumption: 45000,
  renewable_energy_pct: 35.5,
  total_water_withdrawal: 12500,
  water_recycled_pct: 28.3,
  total_waste_generated: 850,
  waste_diversion_rate: 72.5,
  total_initiatives: 15,
  initiatives_in_progress: 8,
  initiatives_completed: 5,
  total_budget: 5000000,
  total_spend: 3200000,
  total_risks: 12,
  critical_risks: 2,
  high_risks: 4,
  total_targets: 20,
  targets_on_track: 14,
  targets_at_risk: 6,
  active_certifications: 5,
  certifications_expiring_soon: 1,
  sdg_coverage: [3, 6, 7, 8, 12, 13],
};

const mockEmissions = [
  {
    id: "1",
    scope: "scope_1",
    category: "Stationary Combustion",
    source_name: "Natural Gas Boilers",
    total_co2e: 450.5,
    period: "Q4 2025",
    facility_name: "Mumbai HQ",
  },
  {
    id: "2",
    scope: "scope_1",
    category: "Mobile Combustion",
    source_name: "Company Fleet",
    total_co2e: 320.2,
    period: "Q4 2025",
    facility_name: "All Locations",
  },
  {
    id: "3",
    scope: "scope_2",
    category: "Purchased Electricity",
    source_name: "Grid Electricity",
    total_co2e: 2100.8,
    period: "Q4 2025",
    facility_name: "Mumbai HQ",
  },
  {
    id: "4",
    scope: "scope_2",
    category: "Purchased Electricity",
    source_name: "Grid Electricity",
    total_co2e: 1320.0,
    period: "Q4 2025",
    facility_name: "Bangalore Office",
  },
  {
    id: "5",
    scope: "scope_3",
    category: "Business Travel",
    source_name: "Air Travel",
    total_co2e: 4500.2,
    period: "Q4 2025",
    facility_name: "All Locations",
  },
];

const mockInitiatives = [
  {
    id: "1",
    name: "Solar Panel Installation",
    category: "environmental",
    status: "in_progress",
    progress_pct: 65,
    budget_amount: 1500000,
    actual_spend: 975000,
    sdg_goals: [7, 13],
    target_end_date: "2026-06-30",
  },
  {
    id: "2",
    name: "Water Recycling System",
    category: "environmental",
    status: "completed",
    progress_pct: 100,
    budget_amount: 800000,
    actual_spend: 750000,
    sdg_goals: [6, 12],
    target_end_date: "2025-12-31",
  },
  {
    id: "3",
    name: "Employee Wellness Program",
    category: "social",
    status: "in_progress",
    progress_pct: 45,
    budget_amount: 500000,
    actual_spend: 225000,
    sdg_goals: [3, 8],
    target_end_date: "2026-03-31",
  },
  {
    id: "4",
    name: "Board Diversity Initiative",
    category: "governance",
    status: "in_progress",
    progress_pct: 30,
    budget_amount: 200000,
    actual_spend: 60000,
    sdg_goals: [5, 10],
    target_end_date: "2026-09-30",
  },
];

const mockTargets = [
  {
    id: "1",
    name: "Net Zero Emissions",
    category: "environmental",
    target_year: 2050,
    baseline_value: 15000,
    target_value: 0,
    current_value: 13421,
    progress_pct: 10.5,
    on_track: true,
    sbti_validated: true,
  },
  {
    id: "2",
    name: "50% Renewable Energy",
    category: "environmental",
    target_year: 2030,
    baseline_value: 20,
    target_value: 50,
    current_value: 35.5,
    progress_pct: 51.7,
    on_track: true,
    sbti_validated: false,
  },
  {
    id: "3",
    name: "Zero Waste to Landfill",
    category: "environmental",
    target_year: 2030,
    baseline_value: 50,
    target_value: 100,
    current_value: 72.5,
    progress_pct: 45,
    on_track: false,
    sbti_validated: false,
  },
  {
    id: "4",
    name: "Gender Pay Equity",
    category: "social",
    target_year: 2027,
    baseline_value: 85,
    target_value: 100,
    current_value: 92,
    progress_pct: 46.7,
    on_track: true,
    sbti_validated: false,
  },
];

const mockRisks = [
  {
    id: "1",
    name: "Carbon Pricing Regulation",
    category: "environmental",
    risk_level: "high",
    likelihood: 4,
    impact: 5,
    risk_score: 20,
    financial_impact: 5000000,
  },
  {
    id: "2",
    name: "Water Scarcity",
    category: "environmental",
    risk_level: "critical",
    likelihood: 4,
    impact: 4,
    risk_score: 16,
    financial_impact: 3000000,
  },
  {
    id: "3",
    name: "Supply Chain Labor Issues",
    category: "social",
    risk_level: "medium",
    likelihood: 3,
    impact: 4,
    risk_score: 12,
    financial_impact: 2000000,
  },
  {
    id: "4",
    name: "Data Privacy Breach",
    category: "governance",
    risk_level: "high",
    likelihood: 3,
    impact: 5,
    risk_score: 15,
    financial_impact: 10000000,
  },
];

const getScopeBadge = (scope: string) => {
  const variants: Record<string, string> = {
    scope_1: "bg-red-100 text-red-700",
    scope_2: "bg-orange-100 text-orange-700",
    scope_3: "bg-yellow-100 text-yellow-700",
  };
  return (
    <Badge className={variants[scope] || variants.scope_1}>
      {scope.replace("_", " ").toUpperCase()}
    </Badge>
  );
};

const getCategoryBadge = (category: string) => {
  const variants: Record<string, { className: string; icon: React.ReactNode }> = {
    environmental: { className: "bg-green-100 text-green-700", icon: <Leaf className="h-3 w-3" /> },
    social: { className: "bg-blue-100 text-blue-700", icon: <Users className="h-3 w-3" /> },
    governance: { className: "bg-purple-100 text-purple-700", icon: <Building className="h-3 w-3" /> },
  };
  const config = variants[category] || variants.environmental;
  return (
    <Badge className={`gap-1 ${config.className}`}>
      {config.icon}
      {category}
    </Badge>
  );
};

const getStatusBadge = (status: string) => {
  const variants: Record<string, string> = {
    planned: "bg-gray-100 text-gray-700",
    in_progress: "bg-blue-100 text-blue-700",
    completed: "bg-green-100 text-green-700",
    on_hold: "bg-yellow-100 text-yellow-700",
    cancelled: "bg-red-100 text-red-700",
  };
  return (
    <Badge className={variants[status] || variants.planned}>
      {status.replace("_", " ")}
    </Badge>
  );
};

const getRiskBadge = (level: string) => {
  const variants: Record<string, string> = {
    low: "bg-green-100 text-green-700",
    medium: "bg-yellow-100 text-yellow-700",
    high: "bg-orange-100 text-orange-700",
    critical: "bg-red-100 text-red-700",
  };
  return <Badge className={variants[level] || variants.medium}>{level}</Badge>;
};

export default function ESGPage() {
  const [reportingYear, setReportingYear] = useState("2025-26");

  const formatNumber = (num: number, decimals: number = 1) => {
    return num.toLocaleString("en-IN", { maximumFractionDigits: decimals });
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat("en-IN", {
      style: "currency",
      currency: "INR",
      maximumFractionDigits: 0,
    }).format(amount);
  };

  return (
    <div className="flex flex-col gap-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <Globe className="h-8 w-8 text-green-600" />
            ESG Management
          </h1>
          <p className="text-muted-foreground mt-1">
            Environmental, Social & Governance tracking and reporting
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Select value={reportingYear} onValueChange={setReportingYear}>
            <SelectTrigger className="w-36">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="2025-26">FY 2025-26</SelectItem>
              <SelectItem value="2024-25">FY 2024-25</SelectItem>
              <SelectItem value="2023-24">FY 2023-24</SelectItem>
            </SelectContent>
          </Select>
          <Button variant="outline">
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
          <Button>
            <FileText className="h-4 w-4 mr-2" />
            Generate BRSR
          </Button>
        </div>
      </div>

      {/* ESG Summary Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card className="border-l-4 border-l-green-500">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Total Emissions</CardTitle>
            <Factory className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {formatNumber(mockDashboard.total_emissions)} tCO2e
            </div>
            <div className="flex items-center text-sm text-green-600 mt-1">
              <TrendingDown className="h-4 w-4 mr-1" />
              {mockDashboard.yoy_emissions_change}% vs last year
            </div>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-yellow-500">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Energy Consumption</CardTitle>
            <Zap className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {formatNumber(mockDashboard.total_energy_consumption)} MWh
            </div>
            <div className="text-sm text-muted-foreground mt-1">
              {mockDashboard.renewable_energy_pct}% renewable
            </div>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-blue-500">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Water Usage</CardTitle>
            <Droplets className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {formatNumber(mockDashboard.total_water_withdrawal)} KL
            </div>
            <div className="text-sm text-muted-foreground mt-1">
              {mockDashboard.water_recycled_pct}% recycled
            </div>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-orange-500">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Waste Generated</CardTitle>
            <Trash2 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {formatNumber(mockDashboard.total_waste_generated)} MT
            </div>
            <div className="text-sm text-muted-foreground mt-1">
              {mockDashboard.waste_diversion_rate}% diverted from landfill
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Emissions by Scope */}
      <Card>
        <CardHeader>
          <CardTitle>GHG Emissions by Scope</CardTitle>
          <CardDescription>Greenhouse gas emissions breakdown (tCO2e)</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div>
              <div className="flex items-center justify-between mb-1">
                <span className="text-sm font-medium">Scope 1 (Direct)</span>
                <span className="text-sm">{formatNumber(mockDashboard.total_scope1_emissions)} tCO2e</span>
              </div>
              <Progress value={(mockDashboard.total_scope1_emissions / mockDashboard.total_emissions) * 100} className="h-3 bg-gray-200" />
            </div>
            <div>
              <div className="flex items-center justify-between mb-1">
                <span className="text-sm font-medium">Scope 2 (Indirect - Energy)</span>
                <span className="text-sm">{formatNumber(mockDashboard.total_scope2_emissions)} tCO2e</span>
              </div>
              <Progress value={(mockDashboard.total_scope2_emissions / mockDashboard.total_emissions) * 100} className="h-3 bg-gray-200" />
            </div>
            <div>
              <div className="flex items-center justify-between mb-1">
                <span className="text-sm font-medium">Scope 3 (Value Chain)</span>
                <span className="text-sm">{formatNumber(mockDashboard.total_scope3_emissions)} tCO2e</span>
              </div>
              <Progress value={(mockDashboard.total_scope3_emissions / mockDashboard.total_emissions) * 100} className="h-3 bg-gray-200" />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Secondary Metrics */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Initiatives</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{mockDashboard.total_initiatives}</div>
            <div className="text-sm text-muted-foreground">
              {mockDashboard.initiatives_in_progress} in progress
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">ESG Risks</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{mockDashboard.total_risks}</div>
            <div className="text-sm text-red-600">
              {mockDashboard.critical_risks} critical, {mockDashboard.high_risks} high
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Targets Progress</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {mockDashboard.targets_on_track}/{mockDashboard.total_targets}
            </div>
            <div className="text-sm text-green-600">on track</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Certifications</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{mockDashboard.active_certifications}</div>
            <div className="text-sm text-yellow-600">
              {mockDashboard.certifications_expiring_soon} expiring soon
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Tabs */}
      <Tabs defaultValue="emissions" className="space-y-4">
        <TabsList>
          <TabsTrigger value="emissions" className="gap-2">
            <Factory className="h-4 w-4" />
            Emissions
          </TabsTrigger>
          <TabsTrigger value="initiatives" className="gap-2">
            <Target className="h-4 w-4" />
            Initiatives
          </TabsTrigger>
          <TabsTrigger value="targets" className="gap-2">
            <Gauge className="h-4 w-4" />
            Targets
          </TabsTrigger>
          <TabsTrigger value="risks" className="gap-2">
            <AlertTriangle className="h-4 w-4" />
            Risks
          </TabsTrigger>
        </TabsList>

        {/* Emissions Tab */}
        <TabsContent value="emissions">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Carbon Emissions Records</CardTitle>
                  <CardDescription>GHG emissions by source and scope</CardDescription>
                </div>
                <Button>
                  <Plus className="h-4 w-4 mr-2" />
                  Add Emission
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Scope</TableHead>
                    <TableHead>Category</TableHead>
                    <TableHead>Source</TableHead>
                    <TableHead>Facility</TableHead>
                    <TableHead>Period</TableHead>
                    <TableHead className="text-right">tCO2e</TableHead>
                    <TableHead></TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {mockEmissions.map((emission) => (
                    <TableRow key={emission.id}>
                      <TableCell>{getScopeBadge(emission.scope)}</TableCell>
                      <TableCell>{emission.category}</TableCell>
                      <TableCell>{emission.source_name}</TableCell>
                      <TableCell>{emission.facility_name}</TableCell>
                      <TableCell>{emission.period}</TableCell>
                      <TableCell className="text-right font-medium">
                        {formatNumber(emission.total_co2e)}
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
                            <DropdownMenuItem>Edit</DropdownMenuItem>
                            <DropdownMenuItem>Verify</DropdownMenuItem>
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

        {/* Initiatives Tab */}
        <TabsContent value="initiatives">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>ESG Initiatives</CardTitle>
                  <CardDescription>Active sustainability projects and programs</CardDescription>
                </div>
                <Button>
                  <Plus className="h-4 w-4 mr-2" />
                  Add Initiative
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Initiative</TableHead>
                    <TableHead>Category</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Progress</TableHead>
                    <TableHead className="text-right">Budget</TableHead>
                    <TableHead className="text-right">Spent</TableHead>
                    <TableHead>SDGs</TableHead>
                    <TableHead></TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {mockInitiatives.map((initiative) => (
                    <TableRow key={initiative.id}>
                      <TableCell className="font-medium">{initiative.name}</TableCell>
                      <TableCell>{getCategoryBadge(initiative.category)}</TableCell>
                      <TableCell>{getStatusBadge(initiative.status)}</TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <Progress value={initiative.progress_pct} className="w-20 h-2" />
                          <span className="text-sm">{initiative.progress_pct}%</span>
                        </div>
                      </TableCell>
                      <TableCell className="text-right">
                        {formatCurrency(initiative.budget_amount)}
                      </TableCell>
                      <TableCell className="text-right">
                        {formatCurrency(initiative.actual_spend)}
                      </TableCell>
                      <TableCell>
                        <div className="flex gap-1">
                          {initiative.sdg_goals.map((sdg) => (
                            <Badge key={sdg} variant="outline" className="text-xs">
                              SDG {sdg}
                            </Badge>
                          ))}
                        </div>
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
                            <DropdownMenuItem>Edit</DropdownMenuItem>
                            <DropdownMenuItem>Update Progress</DropdownMenuItem>
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

        {/* Targets Tab */}
        <TabsContent value="targets">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>ESG Targets</CardTitle>
                  <CardDescription>Long-term sustainability goals and progress</CardDescription>
                </div>
                <Button>
                  <Plus className="h-4 w-4 mr-2" />
                  Add Target
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Target</TableHead>
                    <TableHead>Category</TableHead>
                    <TableHead>Target Year</TableHead>
                    <TableHead>Baseline</TableHead>
                    <TableHead>Target</TableHead>
                    <TableHead>Current</TableHead>
                    <TableHead>Progress</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead></TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {mockTargets.map((target) => (
                    <TableRow key={target.id}>
                      <TableCell>
                        <div className="font-medium">{target.name}</div>
                        {target.sbti_validated && (
                          <Badge variant="outline" className="mt-1 text-xs">
                            SBTi Validated
                          </Badge>
                        )}
                      </TableCell>
                      <TableCell>{getCategoryBadge(target.category)}</TableCell>
                      <TableCell>{target.target_year}</TableCell>
                      <TableCell>{formatNumber(target.baseline_value)}</TableCell>
                      <TableCell>{formatNumber(target.target_value)}</TableCell>
                      <TableCell>{formatNumber(target.current_value)}</TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          <Progress value={target.progress_pct} className="w-16 h-2" />
                          <span className="text-sm">{formatNumber(target.progress_pct)}%</span>
                        </div>
                      </TableCell>
                      <TableCell>
                        {target.on_track ? (
                          <Badge className="bg-green-100 text-green-700 gap-1">
                            <TrendingUp className="h-3 w-3" />
                            On Track
                          </Badge>
                        ) : (
                          <Badge className="bg-red-100 text-red-700 gap-1">
                            <TrendingDown className="h-3 w-3" />
                            At Risk
                          </Badge>
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
                            <DropdownMenuItem>View Details</DropdownMenuItem>
                            <DropdownMenuItem>Edit</DropdownMenuItem>
                            <DropdownMenuItem>Update Progress</DropdownMenuItem>
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

        {/* Risks Tab */}
        <TabsContent value="risks">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>ESG Risks</CardTitle>
                  <CardDescription>Environmental, social and governance risk assessment</CardDescription>
                </div>
                <Button>
                  <Plus className="h-4 w-4 mr-2" />
                  Add Risk
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Risk</TableHead>
                    <TableHead>Category</TableHead>
                    <TableHead>Risk Level</TableHead>
                    <TableHead>Likelihood</TableHead>
                    <TableHead>Impact</TableHead>
                    <TableHead>Score</TableHead>
                    <TableHead className="text-right">Financial Impact</TableHead>
                    <TableHead></TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {mockRisks.map((risk) => (
                    <TableRow key={risk.id}>
                      <TableCell className="font-medium">{risk.name}</TableCell>
                      <TableCell>{getCategoryBadge(risk.category)}</TableCell>
                      <TableCell>{getRiskBadge(risk.risk_level)}</TableCell>
                      <TableCell>{risk.likelihood}/5</TableCell>
                      <TableCell>{risk.impact}/5</TableCell>
                      <TableCell>
                        <Badge variant="outline">{risk.risk_score}</Badge>
                      </TableCell>
                      <TableCell className="text-right">
                        {formatCurrency(risk.financial_impact)}
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
                            <DropdownMenuItem>Edit</DropdownMenuItem>
                            <DropdownMenuItem>Add Mitigation</DropdownMenuItem>
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

      {/* SDG Alignment */}
      <Card>
        <CardHeader>
          <CardTitle>UN Sustainable Development Goals Alignment</CardTitle>
          <CardDescription>Company initiatives mapped to UN SDGs</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2">
            {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17].map((sdg) => (
              <div
                key={sdg}
                className={`w-12 h-12 rounded-lg flex items-center justify-center text-white font-bold ${
                  mockDashboard.sdg_coverage.includes(sdg)
                    ? "bg-blue-600"
                    : "bg-gray-300"
                }`}
              >
                {sdg}
              </div>
            ))}
          </div>
          <p className="text-sm text-muted-foreground mt-4">
            {mockDashboard.sdg_coverage.length} out of 17 SDGs addressed through company initiatives
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
