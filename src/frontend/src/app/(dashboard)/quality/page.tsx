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
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  CheckCircle,
  XCircle,
  AlertTriangle,
  ClipboardCheck,
  FileWarning,
  Wrench,
  Search,
  Plus,
  Download,
  Filter,
  Eye,
  TrendingUp,
  BarChart3,
  Calendar,
} from "lucide-react";

// Mock data
const inspections = [
  { id: "1", number: "QI-000001", type: "incoming", product: "Raw Material A", lotNumber: "LOT-001", result: "pass", status: "completed", date: "2026-01-14", inspector: "Raj Kumar" },
  { id: "2", number: "QI-000002", type: "in_process", product: "Assembly B", lotNumber: "LOT-002", result: "fail", status: "completed", date: "2026-01-14", inspector: "Priya Singh" },
  { id: "3", number: "QI-000003", type: "final", product: "Finished Good C", lotNumber: "LOT-003", result: "pending", status: "pending", date: "2026-01-15", inspector: "Assigned" },
];

const ncrs = [
  { id: "1", number: "NCR-000001", title: "Dimension out of spec", severity: "major", status: "corrective_action", product: "Assembly B", detectedDate: "2026-01-14", assignedTo: "Quality Team" },
  { id: "2", number: "NCR-000002", title: "Surface finish defect", severity: "minor", status: "open", product: "Component D", detectedDate: "2026-01-13", assignedTo: "Production" },
  { id: "3", number: "NCR-000003", title: "Material hardness failure", severity: "critical", status: "under_review", product: "Raw Material E", detectedDate: "2026-01-12", assignedTo: "Supplier QA" },
];

const capas = [
  { id: "1", number: "CAPA-000001", title: "Root cause analysis for dimension issues", type: "corrective", status: "in_progress", targetDate: "2026-01-25", assignedTo: "Engineering" },
  { id: "2", number: "CAPA-000002", title: "Preventive maintenance schedule update", type: "preventive", status: "open", targetDate: "2026-02-01", assignedTo: "Maintenance" },
];

export default function QualityPage() {
  const [activeTab, setActiveTab] = useState("dashboard");
  const [searchTerm, setSearchTerm] = useState("");

  const getResultBadge = (result: string) => {
    const styles: Record<string, string> = {
      pass: "bg-green-100 text-green-800",
      fail: "bg-red-100 text-red-800",
      conditional: "bg-yellow-100 text-yellow-800",
      pending: "bg-gray-100 text-gray-800",
    };
    return styles[result] || "bg-gray-100 text-gray-800";
  };

  const getStatusBadge = (status: string) => {
    const styles: Record<string, string> = {
      pending: "bg-gray-100 text-gray-800",
      in_progress: "bg-blue-100 text-blue-800",
      completed: "bg-green-100 text-green-800",
      open: "bg-yellow-100 text-yellow-800",
      under_review: "bg-purple-100 text-purple-800",
      corrective_action: "bg-orange-100 text-orange-800",
      verification: "bg-blue-100 text-blue-800",
      closed: "bg-green-100 text-green-800",
    };
    return styles[status] || "bg-gray-100 text-gray-800";
  };

  const getSeverityBadge = (severity: string) => {
    const styles: Record<string, string> = {
      minor: "bg-yellow-100 text-yellow-800",
      major: "bg-orange-100 text-orange-800",
      critical: "bg-red-100 text-red-800",
    };
    return styles[severity] || "bg-gray-100 text-gray-800";
  };

  return (
    <div className="flex flex-col gap-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Quality Control</h1>
          <p className="text-muted-foreground">
            Inspection, NCR, and CAPA management
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline">
            <Download className="mr-2 h-4 w-4" />
            Export
          </Button>
          <Dialog>
            <DialogTrigger asChild>
              <Button>
                <Plus className="mr-2 h-4 w-4" />
                New Inspection
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Create Quality Inspection</DialogTitle>
                <DialogDescription>Start a new quality inspection</DialogDescription>
              </DialogHeader>
              <div className="grid gap-4 py-4">
                <div className="space-y-2">
                  <Label>Inspection Type</Label>
                  <Select>
                    <SelectTrigger>
                      <SelectValue placeholder="Select type" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="incoming">Incoming</SelectItem>
                      <SelectItem value="in_process">In-Process</SelectItem>
                      <SelectItem value="final">Final</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label>Product</Label>
                  <Select>
                    <SelectTrigger>
                      <SelectValue placeholder="Select product" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="product1">Raw Material A</SelectItem>
                      <SelectItem value="product2">Assembly B</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label>Lot Number</Label>
                  <Input placeholder="Enter lot number" />
                </div>
              </div>
              <DialogFooter>
                <Button variant="outline">Cancel</Button>
                <Button>Create Inspection</Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="dashboard">
            <BarChart3 className="mr-2 h-4 w-4" />
            Dashboard
          </TabsTrigger>
          <TabsTrigger value="inspections">
            <ClipboardCheck className="mr-2 h-4 w-4" />
            Inspections
          </TabsTrigger>
          <TabsTrigger value="ncr">
            <FileWarning className="mr-2 h-4 w-4" />
            NCR
          </TabsTrigger>
          <TabsTrigger value="capa">
            <Wrench className="mr-2 h-4 w-4" />
            CAPA
          </TabsTrigger>
          <TabsTrigger value="calibration">
            <Calendar className="mr-2 h-4 w-4" />
            Calibration
          </TabsTrigger>
        </TabsList>

        <TabsContent value="dashboard" className="space-y-6">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-5">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium">Pass Rate</CardTitle>
                <TrendingUp className="h-4 w-4 text-green-500" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-green-600">94.5%</div>
                <p className="text-xs text-muted-foreground">This month</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium">Pending Inspections</CardTitle>
                <ClipboardCheck className="h-4 w-4 text-yellow-500" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">8</div>
                <p className="text-xs text-muted-foreground">Awaiting review</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium">Open NCRs</CardTitle>
                <FileWarning className="h-4 w-4 text-orange-500" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-orange-600">5</div>
                <p className="text-xs text-muted-foreground">1 critical</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium">Open CAPAs</CardTitle>
                <Wrench className="h-4 w-4 text-blue-500" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">3</div>
                <p className="text-xs text-muted-foreground">In progress</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium">Calibration Due</CardTitle>
                <Calendar className="h-4 w-4 text-red-500" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-red-600">2</div>
                <p className="text-xs text-muted-foreground">Next 30 days</p>
              </CardContent>
            </Card>
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Inspection Results (MTD)</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <div className="flex justify-between mb-1">
                      <span className="text-sm">Pass</span>
                      <span className="text-sm font-medium">156 (94.5%)</span>
                    </div>
                    <div className="h-2 bg-gray-200 rounded">
                      <div className="h-2 bg-green-500 rounded" style={{ width: "94.5%" }} />
                    </div>
                  </div>
                  <div>
                    <div className="flex justify-between mb-1">
                      <span className="text-sm">Fail</span>
                      <span className="text-sm font-medium">9 (5.5%)</span>
                    </div>
                    <div className="h-2 bg-gray-200 rounded">
                      <div className="h-2 bg-red-500 rounded" style={{ width: "5.5%" }} />
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>NCR by Category</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex justify-between"><span>Material</span><span className="font-medium">3</span></div>
                  <div className="flex justify-between"><span>Process</span><span className="font-medium">2</span></div>
                  <div className="flex justify-between"><span>Equipment</span><span className="font-medium">1</span></div>
                  <div className="flex justify-between"><span>Human Error</span><span className="font-medium">1</span></div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="inspections" className="space-y-4">
          <div className="flex items-center gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input placeholder="Search inspections..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} className="pl-8" />
            </div>
            <Select>
              <SelectTrigger className="w-[150px]">
                <Filter className="mr-2 h-4 w-4" /><SelectValue placeholder="Type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Types</SelectItem>
                <SelectItem value="incoming">Incoming</SelectItem>
                <SelectItem value="in_process">In-Process</SelectItem>
                <SelectItem value="final">Final</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <Card>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Inspection #</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Product</TableHead>
                  <TableHead>Lot #</TableHead>
                  <TableHead>Result</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Date</TableHead>
                  <TableHead>Inspector</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {inspections.map((insp) => (
                  <TableRow key={insp.id}>
                    <TableCell className="font-medium">{insp.number}</TableCell>
                    <TableCell className="capitalize">{insp.type.replace("_", " ")}</TableCell>
                    <TableCell>{insp.product}</TableCell>
                    <TableCell>{insp.lotNumber}</TableCell>
                    <TableCell><Badge className={getResultBadge(insp.result)}>{insp.result}</Badge></TableCell>
                    <TableCell><Badge className={getStatusBadge(insp.status)}>{insp.status}</Badge></TableCell>
                    <TableCell>{insp.date}</TableCell>
                    <TableCell>{insp.inspector}</TableCell>
                    <TableCell><Button variant="ghost" size="sm"><Eye className="h-4 w-4" /></Button></TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </Card>
        </TabsContent>

        <TabsContent value="ncr" className="space-y-4">
          <div className="flex justify-end">
            <Button><Plus className="mr-2 h-4 w-4" />Create NCR</Button>
          </div>
          <Card>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>NCR #</TableHead>
                  <TableHead>Title</TableHead>
                  <TableHead>Severity</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Product</TableHead>
                  <TableHead>Detected</TableHead>
                  <TableHead>Assigned To</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {ncrs.map((ncr) => (
                  <TableRow key={ncr.id}>
                    <TableCell className="font-medium">{ncr.number}</TableCell>
                    <TableCell>{ncr.title}</TableCell>
                    <TableCell><Badge className={getSeverityBadge(ncr.severity)}>{ncr.severity}</Badge></TableCell>
                    <TableCell><Badge className={getStatusBadge(ncr.status)}>{ncr.status.replace("_", " ")}</Badge></TableCell>
                    <TableCell>{ncr.product}</TableCell>
                    <TableCell>{ncr.detectedDate}</TableCell>
                    <TableCell>{ncr.assignedTo}</TableCell>
                    <TableCell><Button variant="ghost" size="sm"><Eye className="h-4 w-4" /></Button></TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </Card>
        </TabsContent>

        <TabsContent value="capa" className="space-y-4">
          <div className="flex justify-end">
            <Button><Plus className="mr-2 h-4 w-4" />Create CAPA</Button>
          </div>
          <Card>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>CAPA #</TableHead>
                  <TableHead>Title</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Target Date</TableHead>
                  <TableHead>Assigned To</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {capas.map((capa) => (
                  <TableRow key={capa.id}>
                    <TableCell className="font-medium">{capa.number}</TableCell>
                    <TableCell>{capa.title}</TableCell>
                    <TableCell className="capitalize">{capa.type}</TableCell>
                    <TableCell><Badge className={getStatusBadge(capa.status)}>{capa.status.replace("_", " ")}</Badge></TableCell>
                    <TableCell>{capa.targetDate}</TableCell>
                    <TableCell>{capa.assignedTo}</TableCell>
                    <TableCell><Button variant="ghost" size="sm"><Eye className="h-4 w-4" /></Button></TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </Card>
        </TabsContent>

        <TabsContent value="calibration" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Equipment Calibration</CardTitle>
              <CardDescription>Track calibration schedules for measuring equipment</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8 text-muted-foreground">
                Calibration tracking table with due dates and certificates
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
