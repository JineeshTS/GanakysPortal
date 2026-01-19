"use client";

import { useState, useEffect } from "react";
import { useApi } from "@/hooks";
import {
  Clock,
  Plus,
  Save,
  Send,
  Calendar,
  ChevronLeft,
  ChevronRight,
  CheckCircle2,
  AlertCircle,
  Loader2,
  Trash2,
} from "lucide-react";
import { PageHeader, DataTable } from "@/components/layout";
import { Button, Card, Input, Select, Badge } from "@/components/ui";

interface TimesheetEntry {
  projectId: number;
  projectName: string;
  taskId: number;
  taskName: string;
  hours: number[];
  total: number;
}

// API Response interfaces
interface TimesheetResponse {
  id: string;
  user_id: string;
  week_start: string;
  week_end: string;
  status: "draft" | "submitted" | "approved" | "rejected";
  entries: TimesheetEntry[];
  total_hours: number;
  billable_hours: number;
}

interface ProjectsResponse {
  projects: { id: number; name: string }[];
}

interface TasksResponse {
  tasks: { id: number; projectId: number; name: string }[];
}

const mockProjects = [
  { id: 1, name: "GanaPortal Development" },
  { id: 2, name: "Client Website Redesign" },
  { id: 3, name: "Mobile App Development" },
];

const mockTasks = [
  { id: 1, projectId: 1, name: "Backend API Development" },
  { id: 2, projectId: 1, name: "Frontend UI Implementation" },
  { id: 3, projectId: 2, name: "Design Review" },
  { id: 4, projectId: 3, name: "Feature Development" },
];

export default function TimesheetPage() {
  const [currentWeek, setCurrentWeek] = useState(new Date());
  const mockEntries: TimesheetEntry[] = [
    {
      projectId: 1,
      projectName: "GanaPortal Development",
      taskId: 1,
      taskName: "Backend API Development",
      hours: [8, 8, 8, 8, 8, 0, 0],
      total: 40,
    },
    {
      projectId: 1,
      projectName: "GanaPortal Development",
      taskId: 2,
      taskName: "Frontend UI Implementation",
      hours: [0, 0, 0, 0, 0, 4, 0],
      total: 4,
    },
  ];
  const [entries, setEntries] = useState<TimesheetEntry[]>(mockEntries);
  const [status, setStatus] = useState<"draft" | "submitted" | "approved">("draft");

  const { data: timesheetData, isLoading, error, get: getTimesheet } = useApi<TimesheetResponse>();
  const { data: projectsData, get: getProjects } = useApi<ProjectsResponse>();

  // Fetch timesheet data when week changes
  useEffect(() => {
    const weekStart = getWeekDates()[0].toISOString().split('T')[0];
    getTimesheet(`/timesheet?week_start=${weekStart}`);
    getProjects('/projects');
  }, [currentWeek, getTimesheet, getProjects]);

  // Update entries when API data loads
  useEffect(() => {
    if (timesheetData?.entries) {
      setEntries(timesheetData.entries);
      setStatus(timesheetData.status as "draft" | "submitted" | "approved");
    }
  }, [timesheetData]);

  const projects = projectsData?.projects || mockProjects;

  const weekDays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];

  const getWeekDates = () => {
    const startOfWeek = new Date(currentWeek);
    const day = startOfWeek.getDay();
    const diff = startOfWeek.getDate() - day + (day === 0 ? -6 : 1);
    startOfWeek.setDate(diff);

    return weekDays.map((_, index) => {
      const date = new Date(startOfWeek);
      date.setDate(startOfWeek.getDate() + index);
      return date;
    });
  };

  const weekDates = getWeekDates();

  const formatDate = (date: Date) => {
    return date.toLocaleDateString("en-IN", { day: "numeric", month: "short" });
  };

  const handleHoursChange = (entryIndex: number, dayIndex: number, value: string) => {
    const hours = parseFloat(value) || 0;
    const newEntries = [...entries];
    newEntries[entryIndex].hours[dayIndex] = Math.min(24, Math.max(0, hours));
    newEntries[entryIndex].total = newEntries[entryIndex].hours.reduce((a, b) => a + b, 0);
    setEntries(newEntries);
  };

  const addNewRow = () => {
    setEntries([
      ...entries,
      {
        projectId: 0,
        projectName: "",
        taskId: 0,
        taskName: "",
        hours: [0, 0, 0, 0, 0, 0, 0],
        total: 0,
      },
    ]);
  };

  const removeRow = (index: number) => {
    if (entries.length > 1) {
      const newEntries = entries.filter((_, i) => i !== index);
      setEntries(newEntries);
    }
  };

  const getDailyTotals = () => {
    return weekDays.map((_, dayIndex) =>
      entries.reduce((sum, entry) => sum + entry.hours[dayIndex], 0)
    );
  };

  const getWeeklyTotal = () => {
    return entries.reduce((sum, entry) => sum + entry.total, 0);
  };

  const dailyTotals = getDailyTotals();
  const weeklyTotal = getWeeklyTotal();

  return (
    <div className="space-y-6">
      <PageHeader
        title="Timesheet"
        description="Track your work hours by project and task"
        icon={Clock}
        actions={
          <div className="flex gap-2">
            <Button variant="outline" onClick={() => {}}>
              <Save className="h-4 w-4 mr-2" />
              Save Draft
            </Button>
            <Button onClick={() => setStatus("submitted")} disabled={status !== "draft"}>
              <Send className="h-4 w-4 mr-2" />
              Submit for Approval
            </Button>
          </div>
        }
      />

      {/* Loading State */}
      {isLoading && (
        <Card className="p-8 flex items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <span className="ml-2">Loading timesheet...</span>
        </Card>
      )}

      {/* Error State */}
      {error && (
        <Card className="p-4 border-red-200 bg-red-50">
          <div className="flex items-center gap-2 text-red-600">
            <AlertCircle className="h-5 w-5" />
            <span>{error}</span>
          </div>
        </Card>
      )}

      {/* Week Navigation */}
      <Card className="p-4">
        <div className="flex items-center justify-between">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => {
              const newDate = new Date(currentWeek);
              newDate.setDate(newDate.getDate() - 7);
              setCurrentWeek(newDate);
            }}
          >
            <ChevronLeft className="h-4 w-4 mr-1" />
            Previous Week
          </Button>

          <div className="flex items-center gap-4">
            <Calendar className="h-5 w-5 text-muted-foreground" />
            <span className="font-semibold">
              {formatDate(weekDates[0])} - {formatDate(weekDates[6])}
            </span>
            <Badge
              variant={
                status === "approved"
                  ? "success"
                  : status === "submitted"
                  ? "warning"
                  : "secondary"
              }
            >
              {status === "approved" && <CheckCircle2 className="h-3 w-3 mr-1" />}
              {status === "submitted" && <AlertCircle className="h-3 w-3 mr-1" />}
              {status.charAt(0).toUpperCase() + status.slice(1)}
            </Badge>
          </div>

          <Button
            variant="ghost"
            size="sm"
            onClick={() => {
              const newDate = new Date(currentWeek);
              newDate.setDate(newDate.getDate() + 7);
              setCurrentWeek(newDate);
            }}
          >
            Next Week
            <ChevronRight className="h-4 w-4 ml-1" />
          </Button>
        </div>
      </Card>

      {/* Timesheet Grid */}
      <Card>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b bg-muted/50">
                <th className="px-4 py-3 text-left font-medium w-48">Project</th>
                <th className="px-4 py-3 text-left font-medium w-48">Task</th>
                {weekDays.map((day, index) => (
                  <th key={day} className="px-2 py-3 text-center font-medium w-20">
                    <div>{day}</div>
                    <div className="text-xs text-muted-foreground">
                      {formatDate(weekDates[index])}
                    </div>
                  </th>
                ))}
                <th className="px-4 py-3 text-center font-medium w-20">Total</th>
                <th className="px-2 py-3 text-center font-medium w-12"></th>
              </tr>
            </thead>
            <tbody>
              {entries.map((entry, entryIndex) => (
                <tr key={entryIndex} className="border-b">
                  <td className="px-4 py-2">
                    <Select
                      value={entry.projectId.toString()}
                      onValueChange={(value) => {
                        const newEntries = [...entries];
                        newEntries[entryIndex].projectId = parseInt(value);
                        newEntries[entryIndex].projectName =
                          mockProjects.find((p) => p.id === parseInt(value))?.name || "";
                        setEntries(newEntries);
                      }}
                      disabled={status !== "draft"}
                    >
                      <option value="0">Select Project</option>
                      {mockProjects.map((project) => (
                        <option key={project.id} value={project.id.toString()}>
                          {project.name}
                        </option>
                      ))}
                    </Select>
                  </td>
                  <td className="px-4 py-2">
                    <Select
                      value={entry.taskId.toString()}
                      onValueChange={(value) => {
                        const newEntries = [...entries];
                        newEntries[entryIndex].taskId = parseInt(value);
                        newEntries[entryIndex].taskName =
                          mockTasks.find((t) => t.id === parseInt(value))?.name || "";
                        setEntries(newEntries);
                      }}
                      disabled={status !== "draft"}
                    >
                      <option value="0">Select Task</option>
                      {mockTasks
                        .filter((t) => t.projectId === entry.projectId)
                        .map((task) => (
                          <option key={task.id} value={task.id.toString()}>
                            {task.name}
                          </option>
                        ))}
                    </Select>
                  </td>
                  {entry.hours.map((hours, dayIndex) => (
                    <td key={dayIndex} className="px-2 py-2">
                      <Input
                        type="number"
                        min="0"
                        max="24"
                        step="0.5"
                        value={hours || ""}
                        onChange={(e) =>
                          handleHoursChange(entryIndex, dayIndex, e.target.value)
                        }
                        className="w-16 text-center"
                        disabled={status !== "draft"}
                      />
                    </td>
                  ))}
                  <td className="px-4 py-2 text-center font-semibold">{entry.total}h</td>
                  <td className="px-2 py-2 text-center">
                    {status === "draft" && entries.length > 1 && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => removeRow(entryIndex)}
                        className="text-red-500 hover:text-red-700 hover:bg-red-50 p-1 h-8 w-8"
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    )}
                  </td>
                </tr>
              ))}

              {/* Daily Totals Row */}
              <tr className="bg-muted/50 font-semibold">
                <td colSpan={2} className="px-4 py-3 text-right">
                  Daily Totals
                </td>
                {dailyTotals.map((total, index) => (
                  <td
                    key={index}
                    className={`px-2 py-3 text-center ${
                      total > 8 ? "text-warning" : total === 8 ? "text-success" : ""
                    }`}
                  >
                    {total}h
                  </td>
                ))}
                <td className="px-4 py-3 text-center text-primary">{weeklyTotal}h</td>
                <td></td>
              </tr>
            </tbody>
          </table>
        </div>

        {status === "draft" && (
          <div className="p-4 border-t">
            <Button variant="outline" size="sm" onClick={addNewRow}>
              <Plus className="h-4 w-4 mr-2" />
              Add Row
            </Button>
          </div>
        )}
      </Card>

      {/* Summary Card */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="p-4">
          <div className="text-sm text-muted-foreground">Total Hours</div>
          <div className="text-2xl font-bold">{weeklyTotal}h</div>
        </Card>
        <Card className="p-4">
          <div className="text-sm text-muted-foreground">Billable Hours</div>
          <div className="text-2xl font-bold text-success">{weeklyTotal}h</div>
        </Card>
        <Card className="p-4">
          <div className="text-sm text-muted-foreground">Projects</div>
          <div className="text-2xl font-bold">
            {new Set(entries.map((e) => e.projectId).filter((id) => id > 0)).size}
          </div>
        </Card>
        <Card className="p-4">
          <div className="text-sm text-muted-foreground">Status</div>
          <div className="text-2xl font-bold capitalize">{status}</div>
        </Card>
      </div>
    </div>
  );
}
