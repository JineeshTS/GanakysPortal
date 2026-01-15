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
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
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
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Progress } from "@/components/ui/progress";
import {
  Heart,
  Plus,
  Search,
  Filter,
  Download,
  Eye,
  Edit,
  Users,
  Target,
  IndianRupee,
  FileText,
  TrendingUp,
  Calendar,
  Building2,
  Globe,
  HeartHandshake,
  GraduationCap,
  Leaf,
  HeartPulse,
  Baby,
  Droplets,
  Lightbulb,
  Award,
  BarChart3,
  PieChart,
  CheckCircle2,
  Clock,
  AlertTriangle,
  XCircle,
} from "lucide-react";

// CSR Categories as per Schedule VII
const CSR_CATEGORIES = [
  { value: "eradicating_hunger", label: "Eradicating Hunger & Poverty", icon: Heart },
  { value: "promoting_education", label: "Promoting Education", icon: GraduationCap },
  { value: "promoting_gender_equality", label: "Gender Equality & Women Empowerment", icon: Users },
  { value: "environmental_sustainability", label: "Environmental Sustainability", icon: Leaf },
  { value: "protection_heritage", label: "Protection of National Heritage", icon: Building2 },
  { value: "armed_forces_veterans", label: "Armed Forces Veterans Welfare", icon: Award },
  { value: "sports_training", label: "Training for Sports", icon: Target },
  { value: "pm_relief_fund", label: "PM National Relief Fund", icon: HeartHandshake },
  { value: "technology_incubators", label: "Technology Incubators", icon: Lightbulb },
  { value: "rural_development", label: "Rural Development Projects", icon: Globe },
  { value: "slum_area_development", label: "Slum Area Development", icon: Building2 },
  { value: "disaster_management", label: "Disaster Management", icon: AlertTriangle },
  { value: "healthcare", label: "Healthcare & Sanitation", icon: HeartPulse },
  { value: "safe_drinking_water", label: "Safe Drinking Water", icon: Droplets },
  { value: "childcare", label: "Childcare & Development", icon: Baby },
];

const PROJECT_STATUSES = [
  { value: "proposed", label: "Proposed", color: "bg-gray-500" },
  { value: "approved", label: "Approved", color: "bg-blue-500" },
  { value: "in_progress", label: "In Progress", color: "bg-yellow-500" },
  { value: "completed", label: "Completed", color: "bg-green-500" },
  { value: "on_hold", label: "On Hold", color: "bg-orange-500" },
  { value: "cancelled", label: "Cancelled", color: "bg-red-500" },
];

const SDG_GOALS = [
  { value: 1, label: "No Poverty", color: "#E5243B" },
  { value: 2, label: "Zero Hunger", color: "#DDA63A" },
  { value: 3, label: "Good Health", color: "#4C9F38" },
  { value: 4, label: "Quality Education", color: "#C5192D" },
  { value: 5, label: "Gender Equality", color: "#FF3A21" },
  { value: 6, label: "Clean Water", color: "#26BDE2" },
  { value: 7, label: "Affordable Energy", color: "#FCC30B" },
  { value: 8, label: "Decent Work", color: "#A21942" },
  { value: 9, label: "Industry & Innovation", color: "#FD6925" },
  { value: 10, label: "Reduced Inequalities", color: "#DD1367" },
  { value: 11, label: "Sustainable Cities", color: "#FD9D24" },
  { value: 12, label: "Responsible Consumption", color: "#BF8B2E" },
  { value: 13, label: "Climate Action", color: "#3F7E44" },
  { value: 14, label: "Life Below Water", color: "#0A97D9" },
  { value: 15, label: "Life on Land", color: "#56C02B" },
  { value: 16, label: "Peace & Justice", color: "#00689D" },
  { value: 17, label: "Partnerships", color: "#19486A" },
];

// Mock data for dashboard
const mockDashboardStats = {
  total_budget: 5000000,
  amount_spent: 3250000,
  amount_available: 1750000,
  spending_percentage: 65,
  total_projects: 12,
  active_projects: 5,
  completed_projects: 6,
  total_beneficiaries: 15420,
  total_volunteers: 285,
  volunteer_hours: 4560,
};

const mockProjects = [
  {
    id: "1",
    project_code: "CSR-2025-001",
    name: "Rural Education Initiative",
    category: "promoting_education",
    status: "in_progress",
    state: "Maharashtra",
    district: "Pune",
    approved_budget: 1200000,
    amount_utilized: 850000,
    progress_percentage: 70,
    start_date: "2025-04-01",
    end_date: "2026-03-31",
    implementing_agency: "Teach India Foundation",
  },
  {
    id: "2",
    project_code: "CSR-2025-002",
    name: "Clean Drinking Water Project",
    category: "safe_drinking_water",
    status: "approved",
    state: "Gujarat",
    district: "Ahmedabad",
    approved_budget: 800000,
    amount_utilized: 0,
    progress_percentage: 0,
    start_date: "2025-06-01",
    end_date: "2025-12-31",
    implementing_agency: "Water.org India",
  },
  {
    id: "3",
    project_code: "CSR-2024-015",
    name: "Healthcare Camp Program",
    category: "healthcare",
    status: "completed",
    state: "Karnataka",
    district: "Bangalore Rural",
    approved_budget: 500000,
    amount_utilized: 485000,
    progress_percentage: 100,
    start_date: "2024-07-01",
    end_date: "2025-01-31",
    implementing_agency: "Rural Health Trust",
  },
];

const mockBeneficiaries = [
  {
    id: "1",
    beneficiary_code: "BEN-2025-00001",
    name: "Village Primary School, Kasara",
    beneficiary_type: "institution",
    category: "Education",
    state: "Maharashtra",
    district: "Thane",
    is_active: true,
    support_type: "Infrastructure & Materials",
    verified: true,
  },
  {
    id: "2",
    beneficiary_code: "BEN-2025-00042",
    name: "Women Self Help Group - Annapurna",
    beneficiary_type: "group",
    category: "Livelihood",
    state: "Gujarat",
    district: "Surat",
    is_active: true,
    support_type: "Skill Development",
    verified: true,
  },
  {
    id: "3",
    beneficiary_code: "BEN-2025-00156",
    name: "Ramesh Kumar",
    beneficiary_type: "individual",
    category: "Healthcare",
    state: "Karnataka",
    district: "Mysore",
    is_active: true,
    support_type: "Medical Assistance",
    verified: false,
  },
];

const mockVolunteers = [
  {
    id: "1",
    employee_name: "Priya Sharma",
    employee_id: "EMP001",
    project_name: "Rural Education Initiative",
    activity_name: "Teaching Workshop",
    activity_date: "2025-01-10",
    hours_contributed: 8,
    status: "completed",
    location: "Pune, Maharashtra",
  },
  {
    id: "2",
    employee_name: "Amit Patel",
    employee_id: "EMP045",
    project_name: "Clean Drinking Water Project",
    activity_name: "Site Assessment",
    activity_date: "2025-01-15",
    hours_contributed: 0,
    status: "registered",
    location: "Ahmedabad, Gujarat",
  },
];

const mockImpactMetrics = [
  {
    id: "1",
    metric_name: "Students Educated",
    metric_type: "output",
    target_value: 5000,
    actual_value: 4250,
    unit: "students",
    sdg_goal: 4,
    target_achieved: false,
    variance_percentage: -15,
    trend: "improving",
  },
  {
    id: "2",
    metric_name: "Villages with Clean Water",
    metric_type: "outcome",
    target_value: 25,
    actual_value: 28,
    unit: "villages",
    sdg_goal: 6,
    target_achieved: true,
    variance_percentage: 12,
    trend: "improving",
  },
  {
    id: "3",
    metric_name: "Health Camps Conducted",
    metric_type: "output",
    target_value: 50,
    actual_value: 52,
    unit: "camps",
    sdg_goal: 3,
    target_achieved: true,
    variance_percentage: 4,
    trend: "stable",
  },
];

const mockReports = [
  {
    id: "1",
    financial_year: "2024-25",
    report_type: "annual",
    status: "approved",
    total_projects: 15,
    amount_spent: 4500000,
    created_at: "2025-04-15",
  },
  {
    id: "2",
    financial_year: "2024-25",
    report_type: "quarterly",
    status: "submitted",
    total_projects: 12,
    amount_spent: 3250000,
    created_at: "2025-01-10",
  },
];

export default function CSRTrackingPage() {
  const [activeTab, setActiveTab] = useState("dashboard");
  const [searchTerm, setSearchTerm] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("all");
  const [statusFilter, setStatusFilter] = useState("all");
  const [stateFilter, setStateFilter] = useState("all");
  const [isProjectDialogOpen, setIsProjectDialogOpen] = useState(false);
  const [isBeneficiaryDialogOpen, setIsBeneficiaryDialogOpen] = useState(false);
  const [isVolunteerDialogOpen, setIsVolunteerDialogOpen] = useState(false);
  const [isMetricDialogOpen, setIsMetricDialogOpen] = useState(false);

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat("en-IN", {
      style: "currency",
      currency: "INR",
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const getStatusBadge = (status: string) => {
    const statusConfig = PROJECT_STATUSES.find((s) => s.value === status);
    return (
      <Badge className={`${statusConfig?.color} text-white`}>
        {statusConfig?.label || status}
      </Badge>
    );
  };

  const getCategoryIcon = (category: string) => {
    const cat = CSR_CATEGORIES.find((c) => c.value === category);
    if (cat) {
      const Icon = cat.icon;
      return <Icon className="h-4 w-4" />;
    }
    return <Heart className="h-4 w-4" />;
  };

  const getCategoryLabel = (category: string) => {
    return CSR_CATEGORIES.find((c) => c.value === category)?.label || category;
  };

  const getSDGBadge = (goalNumber: number) => {
    const goal = SDG_GOALS.find((g) => g.value === goalNumber);
    if (goal) {
      return (
        <Badge style={{ backgroundColor: goal.color }} className="text-white">
          SDG {goalNumber}: {goal.label}
        </Badge>
      );
    }
    return null;
  };

  return (
    <div className="flex-1 space-y-4 p-4 md:p-8 pt-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">CSR Tracking</h2>
          <p className="text-muted-foreground">
            Corporate Social Responsibility Management - Schedule VII Compliance
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Button variant="outline">
            <Download className="mr-2 h-4 w-4" />
            Export
          </Button>
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <TabsList className="grid w-full grid-cols-7">
          <TabsTrigger value="dashboard">
            <BarChart3 className="mr-2 h-4 w-4" />
            Dashboard
          </TabsTrigger>
          <TabsTrigger value="projects">
            <Target className="mr-2 h-4 w-4" />
            Projects
          </TabsTrigger>
          <TabsTrigger value="beneficiaries">
            <Users className="mr-2 h-4 w-4" />
            Beneficiaries
          </TabsTrigger>
          <TabsTrigger value="volunteers">
            <HeartHandshake className="mr-2 h-4 w-4" />
            Volunteers
          </TabsTrigger>
          <TabsTrigger value="impact">
            <TrendingUp className="mr-2 h-4 w-4" />
            Impact
          </TabsTrigger>
          <TabsTrigger value="reports">
            <FileText className="mr-2 h-4 w-4" />
            Reports
          </TabsTrigger>
          <TabsTrigger value="sdg">
            <Globe className="mr-2 h-4 w-4" />
            SDG
          </TabsTrigger>
        </TabsList>

        {/* Dashboard Tab */}
        <TabsContent value="dashboard" className="space-y-4">
          {/* Budget Overview */}
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total CSR Budget</CardTitle>
                <IndianRupee className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {formatCurrency(mockDashboardStats.total_budget)}
                </div>
                <p className="text-xs text-muted-foreground">FY 2024-25</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Amount Spent</CardTitle>
                <TrendingUp className="h-4 w-4 text-green-500" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {formatCurrency(mockDashboardStats.amount_spent)}
                </div>
                <Progress value={mockDashboardStats.spending_percentage} className="mt-2" />
                <p className="text-xs text-muted-foreground mt-1">
                  {mockDashboardStats.spending_percentage}% of budget utilized
                </p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Amount Available</CardTitle>
                <IndianRupee className="h-4 w-4 text-blue-500" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {formatCurrency(mockDashboardStats.amount_available)}
                </div>
                <p className="text-xs text-muted-foreground">Remaining for allocation</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Compliance Status</CardTitle>
                <CheckCircle2 className="h-4 w-4 text-green-500" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-green-600">On Track</div>
                <p className="text-xs text-muted-foreground">2% statutory requirement met</p>
              </CardContent>
            </Card>
          </div>

          {/* Project & Impact Stats */}
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Projects</CardTitle>
                <Target className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{mockDashboardStats.total_projects}</div>
                <div className="flex gap-2 mt-2">
                  <Badge variant="outline" className="text-yellow-600">
                    {mockDashboardStats.active_projects} Active
                  </Badge>
                  <Badge variant="outline" className="text-green-600">
                    {mockDashboardStats.completed_projects} Completed
                  </Badge>
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Beneficiaries</CardTitle>
                <Users className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {mockDashboardStats.total_beneficiaries.toLocaleString()}
                </div>
                <p className="text-xs text-muted-foreground">Lives impacted</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Volunteers</CardTitle>
                <HeartHandshake className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{mockDashboardStats.total_volunteers}</div>
                <p className="text-xs text-muted-foreground">Employee participants</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Volunteer Hours</CardTitle>
                <Clock className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {mockDashboardStats.volunteer_hours.toLocaleString()}
                </div>
                <p className="text-xs text-muted-foreground">Hours contributed</p>
              </CardContent>
            </Card>
          </div>

          {/* Spending by Category & Recent Projects */}
          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Spending by Category</CardTitle>
                <CardDescription>Schedule VII category-wise distribution</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <GraduationCap className="h-4 w-4 text-blue-500" />
                      <span className="text-sm">Education</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Progress value={40} className="w-24" />
                      <span className="text-sm font-medium">{formatCurrency(2000000)}</span>
                    </div>
                  </div>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <HeartPulse className="h-4 w-4 text-red-500" />
                      <span className="text-sm">Healthcare</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Progress value={25} className="w-24" />
                      <span className="text-sm font-medium">{formatCurrency(1250000)}</span>
                    </div>
                  </div>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Leaf className="h-4 w-4 text-green-500" />
                      <span className="text-sm">Environment</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Progress value={20} className="w-24" />
                      <span className="text-sm font-medium">{formatCurrency(1000000)}</span>
                    </div>
                  </div>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <Droplets className="h-4 w-4 text-cyan-500" />
                      <span className="text-sm">Clean Water</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Progress value={15} className="w-24" />
                      <span className="text-sm font-medium">{formatCurrency(750000)}</span>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Recent Projects</CardTitle>
                <CardDescription>Latest CSR initiatives</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {mockProjects.slice(0, 3).map((project) => (
                    <div
                      key={project.id}
                      className="flex items-center justify-between border-b pb-3 last:border-0"
                    >
                      <div className="flex items-center gap-3">
                        {getCategoryIcon(project.category)}
                        <div>
                          <p className="text-sm font-medium">{project.name}</p>
                          <p className="text-xs text-muted-foreground">
                            {project.project_code} | {project.state}
                          </p>
                        </div>
                      </div>
                      <div className="text-right">
                        {getStatusBadge(project.status)}
                        <p className="text-xs text-muted-foreground mt-1">
                          {project.progress_percentage}% complete
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Projects Tab */}
        <TabsContent value="projects" className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>CSR Projects</CardTitle>
                  <CardDescription>Manage CSR projects and initiatives</CardDescription>
                </div>
                <Dialog open={isProjectDialogOpen} onOpenChange={setIsProjectDialogOpen}>
                  <DialogTrigger asChild>
                    <Button>
                      <Plus className="mr-2 h-4 w-4" />
                      New Project
                    </Button>
                  </DialogTrigger>
                  <DialogContent className="max-w-2xl">
                    <DialogHeader>
                      <DialogTitle>Create CSR Project</DialogTitle>
                      <DialogDescription>
                        Add a new CSR project under Schedule VII activities
                      </DialogDescription>
                    </DialogHeader>
                    <div className="grid gap-4 py-4">
                      <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-2">
                          <Label>Project Name</Label>
                          <Input placeholder="Enter project name" />
                        </div>
                        <div className="space-y-2">
                          <Label>Category (Schedule VII)</Label>
                          <Select>
                            <SelectTrigger>
                              <SelectValue placeholder="Select category" />
                            </SelectTrigger>
                            <SelectContent>
                              {CSR_CATEGORIES.map((cat) => (
                                <SelectItem key={cat.value} value={cat.value}>
                                  {cat.label}
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                        </div>
                      </div>
                      <div className="space-y-2">
                        <Label>Description</Label>
                        <Textarea placeholder="Project description and objectives" />
                      </div>
                      <div className="grid grid-cols-3 gap-4">
                        <div className="space-y-2">
                          <Label>State</Label>
                          <Input placeholder="State" />
                        </div>
                        <div className="space-y-2">
                          <Label>District</Label>
                          <Input placeholder="District" />
                        </div>
                        <div className="space-y-2">
                          <Label>Pincode</Label>
                          <Input placeholder="Pincode" />
                        </div>
                      </div>
                      <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-2">
                          <Label>Proposed Budget (INR)</Label>
                          <Input type="number" placeholder="0.00" />
                        </div>
                        <div className="space-y-2">
                          <Label>Implementing Agency</Label>
                          <Input placeholder="Partner NGO/Agency name" />
                        </div>
                      </div>
                      <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-2">
                          <Label>Start Date</Label>
                          <Input type="date" />
                        </div>
                        <div className="space-y-2">
                          <Label>End Date</Label>
                          <Input type="date" />
                        </div>
                      </div>
                    </div>
                    <DialogFooter>
                      <Button variant="outline" onClick={() => setIsProjectDialogOpen(false)}>
                        Cancel
                      </Button>
                      <Button onClick={() => setIsProjectDialogOpen(false)}>Create Project</Button>
                    </DialogFooter>
                  </DialogContent>
                </Dialog>
              </div>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-4 mb-4">
                <div className="relative flex-1">
                  <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                  <Input
                    placeholder="Search projects..."
                    className="pl-8"
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                  />
                </div>
                <Select value={categoryFilter} onValueChange={setCategoryFilter}>
                  <SelectTrigger className="w-[200px]">
                    <SelectValue placeholder="Category" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Categories</SelectItem>
                    {CSR_CATEGORIES.map((cat) => (
                      <SelectItem key={cat.value} value={cat.value}>
                        {cat.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <Select value={statusFilter} onValueChange={setStatusFilter}>
                  <SelectTrigger className="w-[150px]">
                    <SelectValue placeholder="Status" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Status</SelectItem>
                    {PROJECT_STATUSES.map((status) => (
                      <SelectItem key={status.value} value={status.value}>
                        {status.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Project Code</TableHead>
                    <TableHead>Name</TableHead>
                    <TableHead>Category</TableHead>
                    <TableHead>Location</TableHead>
                    <TableHead>Budget</TableHead>
                    <TableHead>Progress</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {mockProjects.map((project) => (
                    <TableRow key={project.id}>
                      <TableCell className="font-medium">{project.project_code}</TableCell>
                      <TableCell>
                        <div>
                          <p className="font-medium">{project.name}</p>
                          <p className="text-xs text-muted-foreground">
                            {project.implementing_agency}
                          </p>
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2">
                          {getCategoryIcon(project.category)}
                          <span className="text-sm">{getCategoryLabel(project.category)}</span>
                        </div>
                      </TableCell>
                      <TableCell>
                        {project.district}, {project.state}
                      </TableCell>
                      <TableCell>
                        <div>
                          <p className="font-medium">{formatCurrency(project.approved_budget)}</p>
                          <p className="text-xs text-muted-foreground">
                            Utilized: {formatCurrency(project.amount_utilized)}
                          </p>
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="w-24">
                          <Progress value={project.progress_percentage} className="h-2" />
                          <span className="text-xs">{project.progress_percentage}%</span>
                        </div>
                      </TableCell>
                      <TableCell>{getStatusBadge(project.status)}</TableCell>
                      <TableCell>
                        <div className="flex gap-2">
                          <Button variant="ghost" size="icon">
                            <Eye className="h-4 w-4" />
                          </Button>
                          <Button variant="ghost" size="icon">
                            <Edit className="h-4 w-4" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Beneficiaries Tab */}
        <TabsContent value="beneficiaries" className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Beneficiaries</CardTitle>
                  <CardDescription>
                    Manage individuals, groups, and institutions benefiting from CSR
                  </CardDescription>
                </div>
                <Dialog open={isBeneficiaryDialogOpen} onOpenChange={setIsBeneficiaryDialogOpen}>
                  <DialogTrigger asChild>
                    <Button>
                      <Plus className="mr-2 h-4 w-4" />
                      Add Beneficiary
                    </Button>
                  </DialogTrigger>
                  <DialogContent className="max-w-2xl">
                    <DialogHeader>
                      <DialogTitle>Add Beneficiary</DialogTitle>
                      <DialogDescription>Register a new CSR beneficiary</DialogDescription>
                    </DialogHeader>
                    <div className="grid gap-4 py-4">
                      <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-2">
                          <Label>Beneficiary Type</Label>
                          <Select>
                            <SelectTrigger>
                              <SelectValue placeholder="Select type" />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="individual">Individual</SelectItem>
                              <SelectItem value="group">Group/Community</SelectItem>
                              <SelectItem value="institution">Institution</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                        <div className="space-y-2">
                          <Label>Category</Label>
                          <Select>
                            <SelectTrigger>
                              <SelectValue placeholder="Select category" />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="education">Education</SelectItem>
                              <SelectItem value="healthcare">Healthcare</SelectItem>
                              <SelectItem value="livelihood">Livelihood</SelectItem>
                              <SelectItem value="environment">Environment</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                      </div>
                      <div className="space-y-2">
                        <Label>Name</Label>
                        <Input placeholder="Beneficiary name" />
                      </div>
                      <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-2">
                          <Label>Contact Person</Label>
                          <Input placeholder="Contact person name" />
                        </div>
                        <div className="space-y-2">
                          <Label>Phone</Label>
                          <Input placeholder="Phone number" />
                        </div>
                      </div>
                      <div className="grid grid-cols-3 gap-4">
                        <div className="space-y-2">
                          <Label>State</Label>
                          <Input placeholder="State" />
                        </div>
                        <div className="space-y-2">
                          <Label>District</Label>
                          <Input placeholder="District" />
                        </div>
                        <div className="space-y-2">
                          <Label>Pincode</Label>
                          <Input placeholder="Pincode" />
                        </div>
                      </div>
                      <div className="space-y-2">
                        <Label>Support Type</Label>
                        <Textarea placeholder="Type of support provided" />
                      </div>
                    </div>
                    <DialogFooter>
                      <Button variant="outline" onClick={() => setIsBeneficiaryDialogOpen(false)}>
                        Cancel
                      </Button>
                      <Button onClick={() => setIsBeneficiaryDialogOpen(false)}>
                        Add Beneficiary
                      </Button>
                    </DialogFooter>
                  </DialogContent>
                </Dialog>
              </div>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-4 mb-4">
                <div className="relative flex-1">
                  <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                  <Input placeholder="Search beneficiaries..." className="pl-8" />
                </div>
                <Select>
                  <SelectTrigger className="w-[150px]">
                    <SelectValue placeholder="Type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Types</SelectItem>
                    <SelectItem value="individual">Individual</SelectItem>
                    <SelectItem value="group">Group</SelectItem>
                    <SelectItem value="institution">Institution</SelectItem>
                  </SelectContent>
                </Select>
                <Select>
                  <SelectTrigger className="w-[150px]">
                    <SelectValue placeholder="State" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All States</SelectItem>
                    <SelectItem value="maharashtra">Maharashtra</SelectItem>
                    <SelectItem value="gujarat">Gujarat</SelectItem>
                    <SelectItem value="karnataka">Karnataka</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Code</TableHead>
                    <TableHead>Name</TableHead>
                    <TableHead>Type</TableHead>
                    <TableHead>Category</TableHead>
                    <TableHead>Location</TableHead>
                    <TableHead>Support Type</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {mockBeneficiaries.map((beneficiary) => (
                    <TableRow key={beneficiary.id}>
                      <TableCell className="font-medium">{beneficiary.beneficiary_code}</TableCell>
                      <TableCell>{beneficiary.name}</TableCell>
                      <TableCell>
                        <Badge variant="outline" className="capitalize">
                          {beneficiary.beneficiary_type}
                        </Badge>
                      </TableCell>
                      <TableCell>{beneficiary.category}</TableCell>
                      <TableCell>
                        {beneficiary.district}, {beneficiary.state}
                      </TableCell>
                      <TableCell>{beneficiary.support_type}</TableCell>
                      <TableCell>
                        <div className="flex gap-2">
                          {beneficiary.is_active && (
                            <Badge className="bg-green-500">Active</Badge>
                          )}
                          {beneficiary.verified ? (
                            <Badge className="bg-blue-500">Verified</Badge>
                          ) : (
                            <Badge variant="outline">Pending</Badge>
                          )}
                        </div>
                      </TableCell>
                      <TableCell>
                        <div className="flex gap-2">
                          <Button variant="ghost" size="icon">
                            <Eye className="h-4 w-4" />
                          </Button>
                          <Button variant="ghost" size="icon">
                            <Edit className="h-4 w-4" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Volunteers Tab */}
        <TabsContent value="volunteers" className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Employee Volunteering</CardTitle>
                  <CardDescription>
                    Track employee participation in CSR activities
                  </CardDescription>
                </div>
                <Dialog open={isVolunteerDialogOpen} onOpenChange={setIsVolunteerDialogOpen}>
                  <DialogTrigger asChild>
                    <Button>
                      <Plus className="mr-2 h-4 w-4" />
                      Register Volunteer
                    </Button>
                  </DialogTrigger>
                  <DialogContent>
                    <DialogHeader>
                      <DialogTitle>Register for Volunteering</DialogTitle>
                      <DialogDescription>
                        Sign up for a CSR volunteering activity
                      </DialogDescription>
                    </DialogHeader>
                    <div className="grid gap-4 py-4">
                      <div className="space-y-2">
                        <Label>Project</Label>
                        <Select>
                          <SelectTrigger>
                            <SelectValue placeholder="Select project" />
                          </SelectTrigger>
                          <SelectContent>
                            {mockProjects.map((project) => (
                              <SelectItem key={project.id} value={project.id}>
                                {project.name}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                      <div className="space-y-2">
                        <Label>Activity Name</Label>
                        <Input placeholder="Activity name" />
                      </div>
                      <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-2">
                          <Label>Activity Date</Label>
                          <Input type="date" />
                        </div>
                        <div className="space-y-2">
                          <Label>Hours Committed</Label>
                          <Input type="number" placeholder="0" />
                        </div>
                      </div>
                      <div className="space-y-2">
                        <Label>Location</Label>
                        <Input placeholder="Activity location" />
                      </div>
                      <div className="space-y-2">
                        <Label>Role</Label>
                        <Input placeholder="Your role in the activity" />
                      </div>
                    </div>
                    <DialogFooter>
                      <Button variant="outline" onClick={() => setIsVolunteerDialogOpen(false)}>
                        Cancel
                      </Button>
                      <Button onClick={() => setIsVolunteerDialogOpen(false)}>Register</Button>
                    </DialogFooter>
                  </DialogContent>
                </Dialog>
              </div>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Employee</TableHead>
                    <TableHead>Project</TableHead>
                    <TableHead>Activity</TableHead>
                    <TableHead>Date</TableHead>
                    <TableHead>Location</TableHead>
                    <TableHead>Hours</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {mockVolunteers.map((volunteer) => (
                    <TableRow key={volunteer.id}>
                      <TableCell>
                        <div>
                          <p className="font-medium">{volunteer.employee_name}</p>
                          <p className="text-xs text-muted-foreground">{volunteer.employee_id}</p>
                        </div>
                      </TableCell>
                      <TableCell>{volunteer.project_name}</TableCell>
                      <TableCell>{volunteer.activity_name}</TableCell>
                      <TableCell>{volunteer.activity_date}</TableCell>
                      <TableCell>{volunteer.location}</TableCell>
                      <TableCell>
                        {volunteer.hours_contributed > 0
                          ? `${volunteer.hours_contributed} hrs`
                          : "-"}
                      </TableCell>
                      <TableCell>
                        <Badge
                          className={
                            volunteer.status === "completed"
                              ? "bg-green-500"
                              : volunteer.status === "registered"
                              ? "bg-blue-500"
                              : "bg-gray-500"
                          }
                        >
                          {volunteer.status}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <div className="flex gap-2">
                          <Button variant="ghost" size="icon">
                            <Eye className="h-4 w-4" />
                          </Button>
                          <Button variant="ghost" size="icon">
                            <Edit className="h-4 w-4" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Impact Tab */}
        <TabsContent value="impact" className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Impact Metrics</CardTitle>
                  <CardDescription>
                    Track and measure CSR impact against targets
                  </CardDescription>
                </div>
                <Dialog open={isMetricDialogOpen} onOpenChange={setIsMetricDialogOpen}>
                  <DialogTrigger asChild>
                    <Button>
                      <Plus className="mr-2 h-4 w-4" />
                      Add Metric
                    </Button>
                  </DialogTrigger>
                  <DialogContent>
                    <DialogHeader>
                      <DialogTitle>Add Impact Metric</DialogTitle>
                      <DialogDescription>Define a new impact measurement metric</DialogDescription>
                    </DialogHeader>
                    <div className="grid gap-4 py-4">
                      <div className="space-y-2">
                        <Label>Metric Name</Label>
                        <Input placeholder="e.g., Students Educated" />
                      </div>
                      <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-2">
                          <Label>Metric Type</Label>
                          <Select>
                            <SelectTrigger>
                              <SelectValue placeholder="Select type" />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="input">Input</SelectItem>
                              <SelectItem value="output">Output</SelectItem>
                              <SelectItem value="outcome">Outcome</SelectItem>
                              <SelectItem value="impact">Impact</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                        <div className="space-y-2">
                          <Label>Unit</Label>
                          <Input placeholder="e.g., students, villages" />
                        </div>
                      </div>
                      <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-2">
                          <Label>Target Value</Label>
                          <Input type="number" placeholder="0" />
                        </div>
                        <div className="space-y-2">
                          <Label>Baseline Value</Label>
                          <Input type="number" placeholder="0" />
                        </div>
                      </div>
                      <div className="space-y-2">
                        <Label>SDG Goal</Label>
                        <Select>
                          <SelectTrigger>
                            <SelectValue placeholder="Select SDG goal" />
                          </SelectTrigger>
                          <SelectContent>
                            {SDG_GOALS.map((goal) => (
                              <SelectItem key={goal.value} value={goal.value.toString()}>
                                SDG {goal.value}: {goal.label}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                    </div>
                    <DialogFooter>
                      <Button variant="outline" onClick={() => setIsMetricDialogOpen(false)}>
                        Cancel
                      </Button>
                      <Button onClick={() => setIsMetricDialogOpen(false)}>Add Metric</Button>
                    </DialogFooter>
                  </DialogContent>
                </Dialog>
              </div>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Metric</TableHead>
                    <TableHead>Type</TableHead>
                    <TableHead>Target</TableHead>
                    <TableHead>Actual</TableHead>
                    <TableHead>Variance</TableHead>
                    <TableHead>SDG Goal</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Trend</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {mockImpactMetrics.map((metric) => (
                    <TableRow key={metric.id}>
                      <TableCell className="font-medium">{metric.metric_name}</TableCell>
                      <TableCell>
                        <Badge variant="outline" className="capitalize">
                          {metric.metric_type}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        {metric.target_value.toLocaleString()} {metric.unit}
                      </TableCell>
                      <TableCell>
                        {metric.actual_value.toLocaleString()} {metric.unit}
                      </TableCell>
                      <TableCell>
                        <span
                          className={
                            metric.variance_percentage >= 0 ? "text-green-600" : "text-red-600"
                          }
                        >
                          {metric.variance_percentage >= 0 ? "+" : ""}
                          {metric.variance_percentage}%
                        </span>
                      </TableCell>
                      <TableCell>{getSDGBadge(metric.sdg_goal)}</TableCell>
                      <TableCell>
                        {metric.target_achieved ? (
                          <Badge className="bg-green-500">
                            <CheckCircle2 className="mr-1 h-3 w-3" />
                            Achieved
                          </Badge>
                        ) : (
                          <Badge variant="outline">
                            <Clock className="mr-1 h-3 w-3" />
                            In Progress
                          </Badge>
                        )}
                      </TableCell>
                      <TableCell>
                        <Badge
                          variant="outline"
                          className={
                            metric.trend === "improving"
                              ? "text-green-600"
                              : metric.trend === "declining"
                              ? "text-red-600"
                              : ""
                          }
                        >
                          {metric.trend === "improving" ? (
                            <TrendingUp className="mr-1 h-3 w-3" />
                          ) : metric.trend === "declining" ? (
                            <TrendingUp className="mr-1 h-3 w-3 rotate-180" />
                          ) : null}
                          {metric.trend}
                        </Badge>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Reports Tab */}
        <TabsContent value="reports" className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>CSR Reports</CardTitle>
                  <CardDescription>
                    Generate and manage statutory CSR reports
                  </CardDescription>
                </div>
                <Button>
                  <Plus className="mr-2 h-4 w-4" />
                  Generate Report
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Financial Year</TableHead>
                    <TableHead>Report Type</TableHead>
                    <TableHead>Total Projects</TableHead>
                    <TableHead>Amount Spent</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Created On</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {mockReports.map((report) => (
                    <TableRow key={report.id}>
                      <TableCell className="font-medium">{report.financial_year}</TableCell>
                      <TableCell>
                        <Badge variant="outline" className="capitalize">
                          {report.report_type}
                        </Badge>
                      </TableCell>
                      <TableCell>{report.total_projects}</TableCell>
                      <TableCell>{formatCurrency(report.amount_spent)}</TableCell>
                      <TableCell>
                        <Badge
                          className={
                            report.status === "approved"
                              ? "bg-green-500"
                              : report.status === "submitted"
                              ? "bg-blue-500"
                              : "bg-gray-500"
                          }
                        >
                          {report.status}
                        </Badge>
                      </TableCell>
                      <TableCell>{report.created_at}</TableCell>
                      <TableCell>
                        <div className="flex gap-2">
                          <Button variant="ghost" size="icon">
                            <Eye className="h-4 w-4" />
                          </Button>
                          <Button variant="ghost" size="icon">
                            <Download className="h-4 w-4" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        {/* SDG Tab */}
        <TabsContent value="sdg" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>UN Sustainable Development Goals</CardTitle>
              <CardDescription>
                Track CSR contribution to UN SDG targets
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-3 lg:grid-cols-4">
                {SDG_GOALS.slice(0, 8).map((goal) => (
                  <Card
                    key={goal.value}
                    className="cursor-pointer hover:shadow-md transition-shadow"
                    style={{ borderLeftColor: goal.color, borderLeftWidth: "4px" }}
                  >
                    <CardHeader className="pb-2">
                      <div className="flex items-center justify-between">
                        <Badge style={{ backgroundColor: goal.color }} className="text-white">
                          SDG {goal.value}
                        </Badge>
                        <span className="text-2xl font-bold">
                          {Math.floor(Math.random() * 10) + 1}
                        </span>
                      </div>
                    </CardHeader>
                    <CardContent>
                      <p className="text-sm font-medium">{goal.label}</p>
                      <p className="text-xs text-muted-foreground mt-1">Projects contributing</p>
                    </CardContent>
                  </Card>
                ))}
              </div>

              <div className="mt-8">
                <h3 className="text-lg font-semibold mb-4">SDG Contribution Summary</h3>
                <div className="grid gap-4 md:grid-cols-2">
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-base">Top Contributing Goals</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-3">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <div
                              className="w-3 h-3 rounded-full"
                              style={{ backgroundColor: "#C5192D" }}
                            />
                            <span className="text-sm">SDG 4: Quality Education</span>
                          </div>
                          <span className="font-medium">35%</span>
                        </div>
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <div
                              className="w-3 h-3 rounded-full"
                              style={{ backgroundColor: "#4C9F38" }}
                            />
                            <span className="text-sm">SDG 3: Good Health</span>
                          </div>
                          <span className="font-medium">25%</span>
                        </div>
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <div
                              className="w-3 h-3 rounded-full"
                              style={{ backgroundColor: "#26BDE2" }}
                            />
                            <span className="text-sm">SDG 6: Clean Water</span>
                          </div>
                          <span className="font-medium">20%</span>
                        </div>
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-2">
                            <div
                              className="w-3 h-3 rounded-full"
                              style={{ backgroundColor: "#E5243B" }}
                            />
                            <span className="text-sm">SDG 1: No Poverty</span>
                          </div>
                          <span className="font-medium">15%</span>
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader>
                      <CardTitle className="text-base">Impact Alignment</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-3">
                        <div>
                          <div className="flex justify-between text-sm mb-1">
                            <span>Metrics aligned to SDGs</span>
                            <span>85%</span>
                          </div>
                          <Progress value={85} />
                        </div>
                        <div>
                          <div className="flex justify-between text-sm mb-1">
                            <span>Projects with SDG mapping</span>
                            <span>92%</span>
                          </div>
                          <Progress value={92} />
                        </div>
                        <div>
                          <div className="flex justify-between text-sm mb-1">
                            <span>SDG targets achieved</span>
                            <span>68%</span>
                          </div>
                          <Progress value={68} />
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
