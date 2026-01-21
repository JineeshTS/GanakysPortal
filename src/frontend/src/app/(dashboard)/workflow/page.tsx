"use client";
import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { GitBranch, Clock, CheckCircle, XCircle, Play, Pause, Settings, Users, FileText, Search, Filter, Eye, BarChart3, Trash2, AlertTriangle, Loader2 } from "lucide-react";
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

interface Workflow {
  id: string;
  name: string;
  type: string;
  status: string;
  steps: number;
  pendingTasks: number;
  avgTime: string;
}

const initialWorkflows: Workflow[] = [
  { id: "1", name: "Purchase Requisition Approval", type: "approval", status: "active", steps: 3, pendingTasks: 5, avgTime: "2.5 days" },
  { id: "2", name: "Leave Request", type: "approval", status: "active", steps: 2, pendingTasks: 12, avgTime: "1 day" },
  { id: "3", name: "Sales Order Processing", type: "process", status: "inactive", steps: 5, pendingTasks: 0, avgTime: "3 days" },
  { id: "4", name: "Document Review", type: "approval", status: "draft", steps: 4, pendingTasks: 0, avgTime: "4 days" },
];

const pendingTasks = [
  { id: "1", workflow: "Purchase Requisition Approval", task: "Manager Approval", document: "PR-000045", requester: "Raj Kumar", dueDate: "2026-01-16", priority: "high" },
  { id: "2", workflow: "Leave Request", task: "HR Verification", document: "LR-000123", requester: "Priya Singh", dueDate: "2026-01-15", priority: "medium" },
  { id: "3", workflow: "Sales Order Processing", task: "Credit Check", document: "SO-000089", requester: "Amit Patel", dueDate: "2026-01-17", priority: "high" },
];

export default function WorkflowPage() {
  const [activeTab, setActiveTab] = useState("dashboard");
  const [searchTerm, setSearchTerm] = useState("");
  const { showToast } = useToast();
  const deleteApi = useApi();

  // Local state for data management
  const [workflows, setWorkflows] = useState<Workflow[]>(initialWorkflows);

  // Delete state
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [workflowToDelete, setWorkflowToDelete] = useState<Workflow | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  const handleDeleteClick = (workflow: Workflow) => {
    setWorkflowToDelete(workflow);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!workflowToDelete) return;
    setIsDeleting(true);
    try {
      await deleteApi.delete(`/workflow/definitions/${workflowToDelete.id}`);
      setWorkflows(workflows.filter(w => w.id !== workflowToDelete.id));
      setDeleteDialogOpen(false);
      setWorkflowToDelete(null);
      showToast("success", "Workflow deleted successfully");
    } catch (error) {
      showToast("error", "Failed to delete workflow");
    } finally {
      setIsDeleting(false);
    }
  };

  const getStatusBadge = (status: string) => {
    const styles: Record<string, string> = {
      active: "bg-green-100 text-green-800",
      inactive: "bg-gray-100 text-gray-800",
      draft: "bg-yellow-100 text-yellow-800",
    };
    return styles[status] || "bg-gray-100 text-gray-800";
  };

  const getPriorityBadge = (priority: string) => {
    const styles: Record<string, string> = {
      high: "bg-red-100 text-red-800",
      medium: "bg-yellow-100 text-yellow-800",
      low: "bg-green-100 text-green-800",
    };
    return styles[priority] || "bg-gray-100 text-gray-800";
  };

  return (
    <div className="flex flex-col gap-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Workflow Engine</h1>
          <p className="text-muted-foreground">Business process automation and approval workflows</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline"><Settings className="mr-2 h-4 w-4" />Configure</Button>
          <Button><GitBranch className="mr-2 h-4 w-4" />New Workflow</Button>
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="dashboard"><BarChart3 className="mr-2 h-4 w-4" />Dashboard</TabsTrigger>
          <TabsTrigger value="inbox"><Clock className="mr-2 h-4 w-4" />My Tasks ({pendingTasks.length})</TabsTrigger>
          <TabsTrigger value="workflows"><GitBranch className="mr-2 h-4 w-4" />Workflows</TabsTrigger>
          <TabsTrigger value="history"><FileText className="mr-2 h-4 w-4" />History</TabsTrigger>
        </TabsList>

        <TabsContent value="dashboard" className="space-y-6">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium">Active Workflows</CardTitle>
                <GitBranch className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">12</div>
                <p className="text-xs text-muted-foreground">Running processes</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium">Pending Tasks</CardTitle>
                <Clock className="h-4 w-4 text-yellow-500" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-yellow-600">28</div>
                <p className="text-xs text-muted-foreground">Awaiting action</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium">Completed Today</CardTitle>
                <CheckCircle className="h-4 w-4 text-green-500" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-green-600">15</div>
                <p className="text-xs text-muted-foreground">Tasks completed</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium">Avg. Completion</CardTitle>
                <BarChart3 className="h-4 w-4 text-blue-500" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-blue-600">2.3 days</div>
                <p className="text-xs text-muted-foreground">This month</p>
              </CardContent>
            </Card>
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle>Workflow Performance</CardTitle>
                <CardDescription>Average completion time by workflow</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {workflows.slice(0, 4).map((wf) => (
                    <div key={wf.id} className="flex items-center justify-between">
                      <span className="text-sm">{wf.name}</span>
                      <span className="text-sm font-medium">{wf.avgTime}</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle>Tasks by Status</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex justify-between"><span>Pending</span><span className="font-medium">28</span></div>
                  <div className="flex justify-between"><span>In Progress</span><span className="font-medium">12</span></div>
                  <div className="flex justify-between"><span>Completed (MTD)</span><span className="font-medium">156</span></div>
                  <div className="flex justify-between"><span>Rejected</span><span className="font-medium">8</span></div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="inbox" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>My Pending Tasks</CardTitle>
              <CardDescription>Tasks assigned to you awaiting action</CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Workflow</TableHead>
                    <TableHead>Task</TableHead>
                    <TableHead>Document</TableHead>
                    <TableHead>Requester</TableHead>
                    <TableHead>Due Date</TableHead>
                    <TableHead>Priority</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {pendingTasks.map((task) => (
                    <TableRow key={task.id}>
                      <TableCell>{task.workflow}</TableCell>
                      <TableCell className="font-medium">{task.task}</TableCell>
                      <TableCell>{task.document}</TableCell>
                      <TableCell>{task.requester}</TableCell>
                      <TableCell>{task.dueDate}</TableCell>
                      <TableCell><Badge className={getPriorityBadge(task.priority)}>{task.priority}</Badge></TableCell>
                      <TableCell>
                        <div className="flex gap-1">
                          <Button size="sm" variant="outline"><CheckCircle className="h-4 w-4 text-green-500" /></Button>
                          <Button size="sm" variant="outline"><XCircle className="h-4 w-4 text-red-500" /></Button>
                          <Button size="sm" variant="ghost"><Eye className="h-4 w-4" /></Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="workflows" className="space-y-4">
          <Card>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Workflow Name</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Steps</TableHead>
                  <TableHead>Pending</TableHead>
                  <TableHead>Avg. Time</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {workflows.map((wf) => (
                  <TableRow key={wf.id}>
                    <TableCell className="font-medium">{wf.name}</TableCell>
                    <TableCell className="capitalize">{wf.type}</TableCell>
                    <TableCell>{wf.steps}</TableCell>
                    <TableCell>{wf.pendingTasks}</TableCell>
                    <TableCell>{wf.avgTime}</TableCell>
                    <TableCell><Badge className={getStatusBadge(wf.status)}>{wf.status}</Badge></TableCell>
                    <TableCell>
                      <div className="flex gap-1">
                        <Button variant="ghost" size="sm"><Eye className="h-4 w-4" /></Button>
                        <Button variant="ghost" size="sm"><Settings className="h-4 w-4" /></Button>
                        {(wf.status === "inactive" || wf.status === "draft") && (
                          <Button
                            variant="ghost"
                            size="sm"
                            className="text-red-600 hover:text-red-700 hover:bg-red-50"
                            onClick={() => handleDeleteClick(wf)}
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        )}
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </Card>
        </TabsContent>

        <TabsContent value="history" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Workflow History</CardTitle>
              <CardDescription>Completed workflow instances</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8 text-muted-foreground">Workflow history will appear here</div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Delete Workflow Confirmation Dialog */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-red-500" />
              Delete Workflow
            </AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete <strong>{workflowToDelete?.name}</strong>?
              This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={isDeleting}>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDeleteConfirm}
              disabled={isDeleting}
              className="bg-red-600 hover:bg-red-700 focus:ring-red-600"
            >
              {isDeleting ? (
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
