"use client";
import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
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
import { useApi, useToast } from "@/hooks";
import { BarChart3, PieChart, LineChart, Download, Calendar, Filter, FileText, TrendingUp, DollarSign, Users, Package, Factory, Clock, Search, Play, Trash2, AlertTriangle, Loader2 } from "lucide-react";

interface RecentReport {
  id: string;
  name: string;
  category: string;
  lastRun: string;
  status: string;
  format: string;
}

interface ScheduledReport {
  id: string;
  name: string;
  frequency: string;
  nextRun: string;
  recipients: number;
}

const reportCategories = [
  { id: "finance", name: "Finance Reports", icon: DollarSign, reports: 15, description: "P&L, Balance Sheet, Cash Flow" },
  { id: "sales", name: "Sales Reports", icon: TrendingUp, reports: 12, description: "Revenue, Orders, Customer Analysis" },
  { id: "inventory", name: "Inventory Reports", icon: Package, reports: 10, description: "Stock, Valuation, Movement" },
  { id: "manufacturing", name: "Manufacturing Reports", icon: Factory, reports: 8, description: "Production, OEE, Efficiency" },
  { id: "hr", name: "HR Reports", icon: Users, reports: 9, description: "Headcount, Attendance, Payroll" },
  { id: "compliance", name: "Compliance Reports", icon: FileText, reports: 7, description: "Statutory, Tax, Audit" },
];

const initialRecentReports: RecentReport[] = [
  { id: "1", name: "Monthly Sales Summary", category: "Sales", lastRun: "2026-01-15 09:30", status: "completed", format: "PDF" },
  { id: "2", name: "Stock Valuation Report", category: "Inventory", lastRun: "2026-01-15 08:00", status: "completed", format: "Excel" },
  { id: "3", name: "Payroll Summary - Jan 2026", category: "HR", lastRun: "2026-01-14 17:45", status: "completed", format: "PDF" },
  { id: "4", name: "Production Efficiency Report", category: "Manufacturing", lastRun: "2026-01-14 16:00", status: "completed", format: "Excel" },
];

const initialScheduledReports: ScheduledReport[] = [
  { id: "1", name: "Daily Sales Report", frequency: "Daily", nextRun: "2026-01-16 06:00", recipients: 5 },
  { id: "2", name: "Weekly Inventory Summary", frequency: "Weekly", nextRun: "2026-01-20 08:00", recipients: 3 },
  { id: "3", name: "Monthly P&L Statement", frequency: "Monthly", nextRun: "2026-02-01 09:00", recipients: 8 },
];

export default function ReportsPage() {
  const [activeTab, setActiveTab] = useState("dashboard");
  const [searchTerm, setSearchTerm] = useState("");
  const { showToast } = useToast();

  // Local state for data management
  const [recentReports, setRecentReports] = useState<RecentReport[]>(initialRecentReports);
  const [scheduledReports, setScheduledReports] = useState<ScheduledReport[]>(initialScheduledReports);

  // Delete state for recent reports
  const [deleteReportDialogOpen, setDeleteReportDialogOpen] = useState(false);
  const [reportToDelete, setReportToDelete] = useState<RecentReport | null>(null);
  const [isDeletingReport, setIsDeletingReport] = useState(false);
  const deleteReportApi = useApi();

  // Delete state for scheduled reports
  const [deleteScheduleDialogOpen, setDeleteScheduleDialogOpen] = useState(false);
  const [scheduleToDelete, setScheduleToDelete] = useState<ScheduledReport | null>(null);
  const [isDeletingSchedule, setIsDeletingSchedule] = useState(false);
  const deleteScheduleApi = useApi();

  const handleDeleteReportClick = (report: RecentReport) => {
    setReportToDelete(report);
    setDeleteReportDialogOpen(true);
  };

  const handleDeleteReportConfirm = async () => {
    if (!reportToDelete) return;
    setIsDeletingReport(true);
    try {
      await deleteReportApi.delete(`/reports/history/${reportToDelete.id}`);
      setRecentReports(recentReports.filter(r => r.id !== reportToDelete.id));
      setDeleteReportDialogOpen(false);
      setReportToDelete(null);
      showToast("success", "Report deleted successfully");
    } catch (error) {
      console.error("Failed to delete report:", error);
      showToast("error", "Failed to delete report");
    } finally {
      setIsDeletingReport(false);
    }
  };

  const handleDeleteScheduleClick = (schedule: ScheduledReport) => {
    setScheduleToDelete(schedule);
    setDeleteScheduleDialogOpen(true);
  };

  const handleDeleteScheduleConfirm = async () => {
    if (!scheduleToDelete) return;
    setIsDeletingSchedule(true);
    try {
      await deleteScheduleApi.delete(`/reports/schedules/${scheduleToDelete.id}`);
      setScheduledReports(scheduledReports.filter(s => s.id !== scheduleToDelete.id));
      setDeleteScheduleDialogOpen(false);
      setScheduleToDelete(null);
      showToast("success", "Schedule deleted successfully");
    } catch (error) {
      console.error("Failed to delete schedule:", error);
      showToast("error", "Failed to delete schedule");
    } finally {
      setIsDeletingSchedule(false);
    }
  };

  return (
    <div className="flex flex-col gap-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Reports & Analytics</h1>
          <p className="text-muted-foreground">Generate, schedule, and analyze business reports</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline"><Calendar className="mr-2 h-4 w-4" />Schedule Report</Button>
          <Button><FileText className="mr-2 h-4 w-4" />New Report</Button>
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="dashboard"><BarChart3 className="mr-2 h-4 w-4" />Dashboard</TabsTrigger>
          <TabsTrigger value="browse"><FileText className="mr-2 h-4 w-4" />Browse Reports</TabsTrigger>
          <TabsTrigger value="scheduled"><Clock className="mr-2 h-4 w-4" />Scheduled</TabsTrigger>
          <TabsTrigger value="builder"><PieChart className="mr-2 h-4 w-4" />Report Builder</TabsTrigger>
        </TabsList>

        <TabsContent value="dashboard" className="space-y-6">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium">Total Reports</CardTitle>
                <FileText className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">61</div>
                <p className="text-xs text-muted-foreground">Available reports</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium">Generated Today</CardTitle>
                <BarChart3 className="h-4 w-4 text-blue-500" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-blue-600">23</div>
                <p className="text-xs text-muted-foreground">Reports run</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium">Scheduled</CardTitle>
                <Clock className="h-4 w-4 text-yellow-500" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-yellow-600">12</div>
                <p className="text-xs text-muted-foreground">Active schedules</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium">Custom Reports</CardTitle>
                <PieChart className="h-4 w-4 text-purple-500" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-purple-600">8</div>
                <p className="text-xs text-muted-foreground">User created</p>
              </CardContent>
            </Card>
          </div>

          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {reportCategories.map((cat) => {
              const Icon = cat.icon;
              return (
                <Card key={cat.id} className="cursor-pointer hover:bg-muted/50">
                  <CardHeader>
                    <div className="flex items-center gap-3">
                      <div className="p-2 rounded-lg bg-primary/10">
                        <Icon className="h-5 w-5 text-primary" />
                      </div>
                      <div>
                        <CardTitle className="text-base">{cat.name}</CardTitle>
                        <CardDescription>{cat.reports} reports</CardDescription>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-muted-foreground">{cat.description}</p>
                  </CardContent>
                </Card>
              );
            })}
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Recent Reports</CardTitle>
              <CardDescription>Recently generated reports</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {recentReports.map((report) => (
                  <div key={report.id} className="flex items-center justify-between border-b pb-3 last:border-0">
                    <div>
                      <p className="font-medium">{report.name}</p>
                      <p className="text-sm text-muted-foreground">{report.category} - {report.lastRun}</p>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge variant="secondary">{report.format}</Badge>
                      <Button variant="ghost" size="sm"><Download className="h-4 w-4" /></Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        className="text-red-600 hover:text-red-700 hover:bg-red-50"
                        onClick={() => handleDeleteReportClick(report)}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="browse" className="space-y-4">
          <div className="flex items-center gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input placeholder="Search reports..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} className="pl-8" />
            </div>
            <Select>
              <SelectTrigger className="w-[180px]"><Filter className="mr-2 h-4 w-4" /><SelectValue placeholder="Category" /></SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Categories</SelectItem>
                <SelectItem value="finance">Finance</SelectItem>
                <SelectItem value="sales">Sales</SelectItem>
                <SelectItem value="inventory">Inventory</SelectItem>
                <SelectItem value="manufacturing">Manufacturing</SelectItem>
                <SelectItem value="hr">HR</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <Card>
            <CardContent className="pt-6">
              <div className="text-center py-8 text-muted-foreground">Report browser with filtering options</div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="scheduled" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Scheduled Reports</CardTitle>
              <CardDescription>Automated report generation schedules</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {scheduledReports.map((report) => (
                  <div key={report.id} className="flex items-center justify-between border-b pb-3 last:border-0">
                    <div>
                      <p className="font-medium">{report.name}</p>
                      <p className="text-sm text-muted-foreground">{report.frequency} - Next: {report.nextRun}</p>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge variant="secondary">{report.recipients} recipients</Badge>
                      <Button variant="ghost" size="sm"><Play className="h-4 w-4" /></Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        className="text-red-600 hover:text-red-700 hover:bg-red-50"
                        onClick={() => handleDeleteScheduleClick(report)}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="builder" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Report Builder</CardTitle>
              <CardDescription>Create custom reports with drag-and-drop</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-12 text-muted-foreground">Interactive report builder interface</div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Delete Report Confirmation Dialog */}
      <AlertDialog open={deleteReportDialogOpen} onOpenChange={setDeleteReportDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-red-500" />
              Delete Report
            </AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete <strong>{reportToDelete?.name}</strong>?
              This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={isDeletingReport}>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDeleteReportConfirm}
              disabled={isDeletingReport}
              className="bg-red-600 hover:bg-red-700 focus:ring-red-600"
            >
              {isDeletingReport ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Deleting...
                </>
              ) : (
                "Delete"
              )}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      {/* Delete Schedule Confirmation Dialog */}
      <AlertDialog open={deleteScheduleDialogOpen} onOpenChange={setDeleteScheduleDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-red-500" />
              Delete Schedule
            </AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete the schedule for <strong>{scheduleToDelete?.name}</strong>?
              This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={isDeletingSchedule}>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDeleteScheduleConfirm}
              disabled={isDeletingSchedule}
              className="bg-red-600 hover:bg-red-700 focus:ring-red-600"
            >
              {isDeletingSchedule ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Deleting...
                </>
              ) : (
                "Delete"
              )}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
