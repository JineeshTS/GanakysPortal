"use client";

import * as React from "react";
import { useState, useEffect, useMemo } from "react";
import Link from "next/link";
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
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { PageHeader } from "@/components/layout/page-header";
import { StatCard, StatsGrid } from "@/components/layout/stat-card";
import { useApi, useToast } from "@/hooks";
import {
  ClipboardList,
  Search,
  Plus,
  Download,
  Filter,
  CheckCircle,
  Clock,
  XCircle,
  AlertTriangle,
  Calendar,
  User,
  Eye,
  Edit,
  Trash2,
  Loader2,
  Play,
  RefreshCw,
} from "lucide-react";

// ============================================================================
// TypeScript Interfaces
// ============================================================================

interface ComplianceTask {
  id: string;
  task_name: string;
  description: string;
  requirement_id: string;
  requirement_name: string;
  category: "statutory" | "regulatory" | "internal";
  assignee_id: string;
  assignee_name: string;
  due_date: string;
  status: "pending" | "in_progress" | "completed" | "overdue";
  priority: "high" | "medium" | "low";
  created_at: string;
  updated_at: string;
  completed_at?: string;
  notes?: string;
}

interface TaskApiResponse {
  items: ComplianceTask[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

interface CreateTaskPayload {
  task_name: string;
  description: string;
  requirement_id?: string;
  category: string;
  assignee_id: string;
  due_date: string;
  priority: string;
}

// ============================================================================
// Mock Data
// ============================================================================

const mockTasks: ComplianceTask[] = [
  {
    id: "1",
    task_name: "Prepare Form 24Q for TDS Return",
    description: "Quarterly TDS return preparation for Q3",
    requirement_id: "REQ-001",
    requirement_name: "TDS Return Filing",
    category: "statutory",
    assignee_id: "EMP-001",
    assignee_name: "Rajesh Kumar",
    due_date: "2026-01-25",
    status: "in_progress",
    priority: "high",
    created_at: "2026-01-10T10:00:00Z",
    updated_at: "2026-01-15T14:30:00Z",
  },
  {
    id: "2",
    task_name: "Verify TDS Calculations",
    description: "Cross-verify TDS calculations with payroll data",
    requirement_id: "REQ-001",
    requirement_name: "TDS Return Filing",
    category: "statutory",
    assignee_id: "EMP-002",
    assignee_name: "Priya Sharma",
    due_date: "2026-01-28",
    status: "pending",
    priority: "high",
    created_at: "2026-01-10T10:00:00Z",
    updated_at: "2026-01-10T10:00:00Z",
  },
  {
    id: "3",
    task_name: "Prepare Factory License Renewal Documents",
    description: "Gather and prepare all documents for factory license renewal",
    requirement_id: "REQ-002",
    requirement_name: "Factory License Renewal",
    category: "regulatory",
    assignee_id: "EMP-003",
    assignee_name: "Amit Patel",
    due_date: "2026-02-15",
    status: "pending",
    priority: "medium",
    created_at: "2026-01-05T09:00:00Z",
    updated_at: "2026-01-05T09:00:00Z",
  },
  {
    id: "4",
    task_name: "Internal Audit Checklist Review",
    description: "Review and update internal audit checklist for Q1",
    requirement_id: "REQ-003",
    requirement_name: "Internal Compliance Review",
    category: "internal",
    assignee_id: "EMP-004",
    assignee_name: "Sneha Reddy",
    due_date: "2026-01-20",
    status: "completed",
    priority: "medium",
    created_at: "2026-01-01T08:00:00Z",
    updated_at: "2026-01-18T16:00:00Z",
    completed_at: "2026-01-18T16:00:00Z",
  },
  {
    id: "5",
    task_name: "GST Reconciliation for December",
    description: "Reconcile GST input/output for December 2025",
    requirement_id: "REQ-004",
    requirement_name: "Monthly GST Filing",
    category: "statutory",
    assignee_id: "EMP-001",
    assignee_name: "Rajesh Kumar",
    due_date: "2026-01-10",
    status: "overdue",
    priority: "high",
    created_at: "2025-12-28T10:00:00Z",
    updated_at: "2026-01-10T18:00:00Z",
  },
  {
    id: "6",
    task_name: "Update Employee Safety Training Records",
    description: "Ensure all employee safety training records are updated",
    requirement_id: "REQ-005",
    requirement_name: "Safety Compliance",
    category: "regulatory",
    assignee_id: "EMP-005",
    assignee_name: "Vikram Singh",
    due_date: "2026-01-30",
    status: "pending",
    priority: "low",
    created_at: "2026-01-12T11:00:00Z",
    updated_at: "2026-01-12T11:00:00Z",
  },
];

const mockAssignees = [
  { id: "EMP-001", name: "Rajesh Kumar" },
  { id: "EMP-002", name: "Priya Sharma" },
  { id: "EMP-003", name: "Amit Patel" },
  { id: "EMP-004", name: "Sneha Reddy" },
  { id: "EMP-005", name: "Vikram Singh" },
];

// ============================================================================
// Compliance Tasks Page
// ============================================================================

export default function ComplianceTasksPage() {
  const [tasks, setTasks] = useState<ComplianceTask[]>(mockTasks);
  const [searchTerm, setSearchTerm] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("all");
  const [statusFilter, setStatusFilter] = useState("all");
  const [isLoading, setIsLoading] = useState(true);
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [selectedTask, setSelectedTask] = useState<ComplianceTask | null>(null);
  const [isViewDialogOpen, setIsViewDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [taskToDelete, setTaskToDelete] = useState<ComplianceTask | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  // Form state for creating/editing tasks
  const [formData, setFormData] = useState<CreateTaskPayload>({
    task_name: "",
    description: "",
    requirement_id: "",
    category: "statutory",
    assignee_id: "",
    due_date: "",
    priority: "medium",
  });

  const { showToast } = useToast();
  const tasksApi = useApi<TaskApiResponse>();

  // Fetch tasks from API
  useEffect(() => {
    const fetchTasks = async () => {
      setIsLoading(true);
      try {
        const result = await tasksApi.get("/compliance/tasks");
        if (result && result.items) {
          setTasks(result.items);
        }
      } catch (error) {
        showToast("error", "Failed to fetch compliance tasks");
        // Keep using mock data on error
      } finally {
        setIsLoading(false);
      }
    };

    fetchTasks();
  }, []);

  // Filter tasks
  const filteredTasks = useMemo(() => {
    return tasks.filter((task) => {
      const matchesSearch =
        task.task_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        task.requirement_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        task.assignee_name.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesCategory =
        categoryFilter === "all" || task.category === categoryFilter;
      const matchesStatus =
        statusFilter === "all" || task.status === statusFilter;
      return matchesSearch && matchesCategory && matchesStatus;
    });
  }, [tasks, searchTerm, categoryFilter, statusFilter]);

  // Calculate stats
  const stats = useMemo(() => {
    const total = tasks.length;
    const pending = tasks.filter((t) => t.status === "pending").length;
    const inProgress = tasks.filter((t) => t.status === "in_progress").length;
    const completed = tasks.filter((t) => t.status === "completed").length;
    const overdue = tasks.filter((t) => t.status === "overdue").length;
    return { total, pending, inProgress, completed, overdue };
  }, [tasks]);

  // Status badge styles
  const getStatusBadge = (status: string) => {
    const styles: Record<string, string> = {
      completed: "bg-green-100 text-green-800",
      in_progress: "bg-blue-100 text-blue-800",
      pending: "bg-yellow-100 text-yellow-800",
      overdue: "bg-red-100 text-red-800",
    };
    return styles[status] || "bg-gray-100 text-gray-800";
  };

  // Priority badge styles
  const getPriorityBadge = (priority: string) => {
    const styles: Record<string, string> = {
      high: "bg-red-100 text-red-800",
      medium: "bg-yellow-100 text-yellow-800",
      low: "bg-green-100 text-green-800",
    };
    return styles[priority] || "bg-gray-100 text-gray-800";
  };

  // Category badge styles
  const getCategoryBadge = (category: string) => {
    const styles: Record<string, string> = {
      statutory: "bg-purple-100 text-purple-800",
      regulatory: "bg-blue-100 text-blue-800",
      internal: "bg-gray-100 text-gray-800",
    };
    return styles[category] || "bg-gray-100 text-gray-800";
  };

  // Status icon
  const getStatusIcon = (status: string) => {
    switch (status) {
      case "completed":
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case "in_progress":
        return <Play className="h-4 w-4 text-blue-500" />;
      case "pending":
        return <Clock className="h-4 w-4 text-yellow-500" />;
      case "overdue":
        return <AlertTriangle className="h-4 w-4 text-red-500" />;
      default:
        return <Clock className="h-4 w-4 text-gray-500" />;
    }
  };

  // Handle task creation
  const handleCreateTask = async () => {
    try {
      const newTask: ComplianceTask = {
        id: `TASK-${Date.now()}`,
        task_name: formData.task_name,
        description: formData.description,
        requirement_id: formData.requirement_id || "",
        requirement_name: "New Requirement",
        category: formData.category as "statutory" | "regulatory" | "internal",
        assignee_id: formData.assignee_id,
        assignee_name:
          mockAssignees.find((a) => a.id === formData.assignee_id)?.name || "",
        due_date: formData.due_date,
        status: "pending",
        priority: formData.priority as "high" | "medium" | "low",
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };

      setTasks([newTask, ...tasks]);
      setIsCreateDialogOpen(false);
      setFormData({
        task_name: "",
        description: "",
        requirement_id: "",
        category: "statutory",
        assignee_id: "",
        due_date: "",
        priority: "medium",
      });
      showToast("success", "Task created successfully");
    } catch (error) {
      showToast("error", "Failed to create task");
    }
  };

  // Handle task status update
  const handleStatusUpdate = async (
    taskId: string,
    newStatus: ComplianceTask["status"]
  ) => {
    setTasks(
      tasks.map((task) =>
        task.id === taskId
          ? {
              ...task,
              status: newStatus,
              updated_at: new Date().toISOString(),
              completed_at:
                newStatus === "completed" ? new Date().toISOString() : undefined,
            }
          : task
      )
    );
    showToast("success", "Task status updated");
  };

  // Handle task deletion
  const handleDeleteClick = (task: ComplianceTask) => {
    setTaskToDelete(task);
    setDeleteDialogOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!taskToDelete) return;
    setIsDeleting(true);
    try {
      setTasks(tasks.filter((t) => t.id !== taskToDelete.id));
      setDeleteDialogOpen(false);
      setTaskToDelete(null);
      showToast("success", "Task deleted successfully");
    } catch (error) {
      showToast("error", "Failed to delete task");
    } finally {
      setIsDeleting(false);
    }
  };

  // View task details
  const handleViewTask = (task: ComplianceTask) => {
    setSelectedTask(task);
    setIsViewDialogOpen(true);
  };

  // Format date for display
  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString("en-IN", {
      day: "2-digit",
      month: "short",
      year: "numeric",
    });
  };

  // Check if due date is approaching (within 3 days)
  const isDueSoon = (dueDate: string) => {
    const due = new Date(dueDate);
    const today = new Date();
    const diffDays = Math.ceil(
      (due.getTime() - today.getTime()) / (1000 * 60 * 60 * 24)
    );
    return diffDays > 0 && diffDays <= 3;
  };

  return (
    <div className="flex flex-col gap-6 p-6">
      <PageHeader
        title="Compliance Tasks"
        description="Track and manage compliance-related tasks and deadlines"
        breadcrumbs={[
          { label: "Dashboard", href: "/" },
          { label: "Compliance", href: "/compliance" },
          { label: "Tasks" },
        ]}
        actions={
          <div className="flex gap-2">
            <Button variant="outline">
              <Download className="mr-2 h-4 w-4" />
              Export
            </Button>
            <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
              <DialogTrigger asChild>
                <Button>
                  <Plus className="mr-2 h-4 w-4" />
                  Add Task
                </Button>
              </DialogTrigger>
              <DialogContent className="max-w-2xl">
                <DialogHeader>
                  <DialogTitle>Create Compliance Task</DialogTitle>
                  <DialogDescription>
                    Add a new compliance task with assignment and due date
                  </DialogDescription>
                </DialogHeader>
                <div className="grid gap-4 py-4">
                  <div className="space-y-2">
                    <Label>Task Name</Label>
                    <Input
                      placeholder="Enter task name"
                      value={formData.task_name}
                      onChange={(e) =>
                        setFormData({ ...formData, task_name: e.target.value })
                      }
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label>Category</Label>
                      <Select
                        value={formData.category}
                        onValueChange={(value) =>
                          setFormData({ ...formData, category: value })
                        }
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="Select category" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="statutory">Statutory</SelectItem>
                          <SelectItem value="regulatory">Regulatory</SelectItem>
                          <SelectItem value="internal">Internal</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="space-y-2">
                      <Label>Priority</Label>
                      <Select
                        value={formData.priority}
                        onValueChange={(value) =>
                          setFormData({ ...formData, priority: value })
                        }
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="Select priority" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="high">High</SelectItem>
                          <SelectItem value="medium">Medium</SelectItem>
                          <SelectItem value="low">Low</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label>Assignee</Label>
                      <Select
                        value={formData.assignee_id}
                        onValueChange={(value) =>
                          setFormData({ ...formData, assignee_id: value })
                        }
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="Select assignee" />
                        </SelectTrigger>
                        <SelectContent>
                          {mockAssignees.map((assignee) => (
                            <SelectItem key={assignee.id} value={assignee.id}>
                              {assignee.name}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="space-y-2">
                      <Label>Due Date</Label>
                      <Input
                        type="date"
                        value={formData.due_date}
                        onChange={(e) =>
                          setFormData({ ...formData, due_date: e.target.value })
                        }
                      />
                    </div>
                  </div>
                  <div className="space-y-2">
                    <Label>Description</Label>
                    <Textarea
                      placeholder="Enter task description"
                      value={formData.description}
                      onChange={(e) =>
                        setFormData({ ...formData, description: e.target.value })
                      }
                    />
                  </div>
                </div>
                <DialogFooter>
                  <Button
                    variant="outline"
                    onClick={() => setIsCreateDialogOpen(false)}
                  >
                    Cancel
                  </Button>
                  <Button onClick={handleCreateTask}>Create Task</Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
          </div>
        }
      />

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-5">
        <StatCard
          title="Total Tasks"
          value={stats.total}
          icon={ClipboardList}
          description="All compliance tasks"
        />
        <StatCard
          title="Pending"
          value={stats.pending}
          icon={Clock}
          description="Awaiting action"
          valueClassName="text-yellow-600"
        />
        <StatCard
          title="In Progress"
          value={stats.inProgress}
          icon={Play}
          description="Currently working"
          valueClassName="text-blue-600"
        />
        <StatCard
          title="Completed"
          value={stats.completed}
          icon={CheckCircle}
          description="Successfully done"
          valueClassName="text-green-600"
        />
        <StatCard
          title="Overdue"
          value={stats.overdue}
          icon={AlertTriangle}
          description="Past due date"
          valueClassName="text-red-600"
        />
      </div>

      {/* Filters */}
      <div className="flex items-center gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search tasks by name, requirement, or assignee..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-8"
          />
        </div>
        <Select value={categoryFilter} onValueChange={setCategoryFilter}>
          <SelectTrigger className="w-[180px]">
            <Filter className="mr-2 h-4 w-4" />
            <SelectValue placeholder="Category" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Categories</SelectItem>
            <SelectItem value="statutory">Statutory</SelectItem>
            <SelectItem value="regulatory">Regulatory</SelectItem>
            <SelectItem value="internal">Internal</SelectItem>
          </SelectContent>
        </Select>
        <Select value={statusFilter} onValueChange={setStatusFilter}>
          <SelectTrigger className="w-[150px]">
            <SelectValue placeholder="Status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Status</SelectItem>
            <SelectItem value="pending">Pending</SelectItem>
            <SelectItem value="in_progress">In Progress</SelectItem>
            <SelectItem value="completed">Completed</SelectItem>
            <SelectItem value="overdue">Overdue</SelectItem>
          </SelectContent>
        </Select>
        <Button
          variant="outline"
          size="icon"
          onClick={() => {
            setSearchTerm("");
            setCategoryFilter("all");
            setStatusFilter("all");
          }}
        >
          <RefreshCw className="h-4 w-4" />
        </Button>
      </div>

      {/* Tasks Table */}
      <Card>
        <CardHeader>
          <CardTitle>Task List</CardTitle>
          <CardDescription>
            {filteredTasks.length} task(s) found
          </CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
              <span className="ml-2 text-muted-foreground">Loading tasks...</span>
            </div>
          ) : filteredTasks.length === 0 ? (
            <div className="text-center py-12 text-muted-foreground">
              <ClipboardList className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p>No tasks found matching your criteria</p>
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Task</TableHead>
                  <TableHead>Category</TableHead>
                  <TableHead>Requirement</TableHead>
                  <TableHead>Assignee</TableHead>
                  <TableHead>Due Date</TableHead>
                  <TableHead>Priority</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredTasks.map((task) => (
                  <TableRow key={task.id}>
                    <TableCell>
                      <div className="font-medium">{task.task_name}</div>
                      {task.description && (
                        <div className="text-sm text-muted-foreground truncate max-w-[200px]">
                          {task.description}
                        </div>
                      )}
                    </TableCell>
                    <TableCell>
                      <Badge className={getCategoryBadge(task.category)}>
                        {task.category}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-sm">
                      {task.requirement_name}
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <User className="h-4 w-4 text-muted-foreground" />
                        <span>{task.assignee_name}</span>
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <Calendar className="h-4 w-4 text-muted-foreground" />
                        <span
                          className={
                            isDueSoon(task.due_date) && task.status !== "completed"
                              ? "text-orange-600 font-medium"
                              : ""
                          }
                        >
                          {formatDate(task.due_date)}
                        </span>
                        {isDueSoon(task.due_date) && task.status !== "completed" && (
                          <Badge variant="outline" className="text-xs bg-orange-50">
                            Due soon
                          </Badge>
                        )}
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge className={getPriorityBadge(task.priority)}>
                        {task.priority}
                      </Badge>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        {getStatusIcon(task.status)}
                        <Badge className={getStatusBadge(task.status)}>
                          {task.status.replace("_", " ")}
                        </Badge>
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="flex gap-1">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleViewTask(task)}
                        >
                          <Eye className="h-4 w-4" />
                        </Button>
                        {task.status === "pending" && (
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleStatusUpdate(task.id, "in_progress")}
                            title="Start task"
                          >
                            <Play className="h-4 w-4 text-blue-500" />
                          </Button>
                        )}
                        {task.status === "in_progress" && (
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleStatusUpdate(task.id, "completed")}
                            title="Mark complete"
                          >
                            <CheckCircle className="h-4 w-4 text-green-500" />
                          </Button>
                        )}
                        {(task.status === "completed" || task.status === "overdue") && (
                          <Button
                            variant="ghost"
                            size="sm"
                            className="text-red-600 hover:text-red-700 hover:bg-red-50"
                            onClick={() => handleDeleteClick(task)}
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
          )}
        </CardContent>
      </Card>

      {/* View Task Dialog */}
      <Dialog open={isViewDialogOpen} onOpenChange={setIsViewDialogOpen}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              {selectedTask && getStatusIcon(selectedTask.status)}
              Task Details
            </DialogTitle>
          </DialogHeader>
          {selectedTask && (
            <div className="space-y-4">
              <div className="p-3 bg-muted rounded-lg">
                <h3 className="font-medium">{selectedTask.task_name}</h3>
                <p className="text-sm text-muted-foreground mt-1">
                  {selectedTask.description}
                </p>
              </div>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <p className="text-muted-foreground">Category</p>
                  <Badge className={getCategoryBadge(selectedTask.category)}>
                    {selectedTask.category}
                  </Badge>
                </div>
                <div>
                  <p className="text-muted-foreground">Priority</p>
                  <Badge className={getPriorityBadge(selectedTask.priority)}>
                    {selectedTask.priority}
                  </Badge>
                </div>
                <div>
                  <p className="text-muted-foreground">Requirement</p>
                  <p className="font-medium">{selectedTask.requirement_name}</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Assignee</p>
                  <p className="font-medium">{selectedTask.assignee_name}</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Due Date</p>
                  <p className="font-medium">{formatDate(selectedTask.due_date)}</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Status</p>
                  <Badge className={getStatusBadge(selectedTask.status)}>
                    {selectedTask.status.replace("_", " ")}
                  </Badge>
                </div>
                <div>
                  <p className="text-muted-foreground">Created</p>
                  <p className="font-medium">{formatDate(selectedTask.created_at)}</p>
                </div>
                <div>
                  <p className="text-muted-foreground">Last Updated</p>
                  <p className="font-medium">{formatDate(selectedTask.updated_at)}</p>
                </div>
              </div>
              {selectedTask.completed_at && (
                <div className="p-3 bg-green-50 border border-green-200 rounded-lg text-sm">
                  <p className="text-green-800">
                    Completed on {formatDate(selectedTask.completed_at)}
                  </p>
                </div>
              )}
            </div>
          )}
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsViewDialogOpen(false)}>
              Close
            </Button>
            <Button asChild variant="outline">
              <Link href="/compliance">View All Compliance</Link>
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-red-500" />
              Delete Task
            </AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete{" "}
              <strong>{taskToDelete?.task_name}</strong>? This action cannot be
              undone.
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
