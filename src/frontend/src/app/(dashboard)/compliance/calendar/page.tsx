"use client";

import * as React from "react";
import { useState, useEffect, useMemo, useCallback } from "react";
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
import { PageHeader } from "@/components/layout/page-header";
import { useApi, useToast } from "@/hooks";
import { cn } from "@/lib/utils";
import {
  Calendar,
  ChevronLeft,
  ChevronRight,
  Plus,
  Download,
  Clock,
  AlertTriangle,
  FileCheck,
  Shield,
  Scale,
  Building,
  Star,
  Info,
  Loader2,
  List,
  Grid,
} from "lucide-react";

// ============================================================================
// TypeScript Interfaces
// ============================================================================

interface ComplianceEvent {
  id: string;
  title: string;
  description?: string;
  due_date: string;
  category: "tax" | "labor" | "regulatory" | "environment" | "corporate";
  type: "filing" | "renewal" | "audit" | "inspection" | "review";
  status: "upcoming" | "due_soon" | "overdue" | "completed";
  entity: string;
  priority: "high" | "medium" | "low";
  reminder_days?: number;
}

interface CalendarDay {
  date: Date;
  isCurrentMonth: boolean;
  isToday: boolean;
  isWeekend: boolean;
  events: ComplianceEvent[];
}

// ============================================================================
// Constants
// ============================================================================

const DAYS_OF_WEEK = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

const MONTHS = [
  "January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December"
];

const categoryColors: Record<string, { bg: string; text: string; border: string }> = {
  tax: { bg: "bg-blue-100", text: "text-blue-800", border: "border-blue-300" },
  labor: { bg: "bg-green-100", text: "text-green-800", border: "border-green-300" },
  regulatory: { bg: "bg-purple-100", text: "text-purple-800", border: "border-purple-300" },
  environment: { bg: "bg-emerald-100", text: "text-emerald-800", border: "border-emerald-300" },
  corporate: { bg: "bg-orange-100", text: "text-orange-800", border: "border-orange-300" },
};

const statusColors: Record<string, string> = {
  upcoming: "bg-gray-500",
  due_soon: "bg-yellow-500",
  overdue: "bg-red-500",
  completed: "bg-green-500",
};

// ============================================================================
// Mock Data
// ============================================================================

const mockEvents: ComplianceEvent[] = [
  {
    id: "1",
    title: "GST Return Filing (GSTR-1)",
    description: "Monthly GST return for outward supplies",
    due_date: "2026-01-11",
    category: "tax",
    type: "filing",
    status: "completed",
    entity: "Gana Industries Pvt Ltd",
    priority: "high",
    reminder_days: 5,
  },
  {
    id: "2",
    title: "TDS Return Q3",
    due_date: "2026-01-31",
    category: "tax",
    type: "filing",
    status: "due_soon",
    entity: "Gana Industries Pvt Ltd",
    priority: "high",
    reminder_days: 7,
  },
  {
    id: "3",
    title: "EPF Monthly Return",
    description: "Employee Provident Fund monthly contribution filing",
    due_date: "2026-01-15",
    category: "labor",
    type: "filing",
    status: "due_soon",
    entity: "Gana Industries Pvt Ltd",
    priority: "medium",
    reminder_days: 3,
  },
  {
    id: "4",
    title: "ESI Monthly Return",
    due_date: "2026-01-15",
    category: "labor",
    type: "filing",
    status: "due_soon",
    entity: "Gana Industries Pvt Ltd",
    priority: "medium",
    reminder_days: 3,
  },
  {
    id: "5",
    title: "Factory License Renewal",
    description: "Annual factory license renewal for Pune unit",
    due_date: "2026-03-31",
    category: "regulatory",
    type: "renewal",
    status: "upcoming",
    entity: "Manufacturing Unit - Pune",
    priority: "high",
    reminder_days: 30,
  },
  {
    id: "6",
    title: "Pollution Control Certificate",
    due_date: "2026-06-30",
    category: "environment",
    type: "renewal",
    status: "upcoming",
    entity: "Manufacturing Unit - Pune",
    priority: "medium",
    reminder_days: 45,
  },
  {
    id: "7",
    title: "Annual Statutory Audit",
    description: "FY 2025-26 statutory audit by KPMG",
    due_date: "2026-04-15",
    category: "corporate",
    type: "audit",
    status: "upcoming",
    entity: "Gana Industries Pvt Ltd",
    priority: "high",
    reminder_days: 60,
  },
  {
    id: "8",
    title: "GST Return Filing (GSTR-3B)",
    due_date: "2026-01-20",
    category: "tax",
    type: "filing",
    status: "due_soon",
    entity: "Gana Industries Pvt Ltd",
    priority: "high",
    reminder_days: 5,
  },
  {
    id: "9",
    title: "Professional Tax Filing",
    due_date: "2026-01-25",
    category: "tax",
    type: "filing",
    status: "upcoming",
    entity: "Gana Industries Pvt Ltd",
    priority: "low",
    reminder_days: 3,
  },
  {
    id: "10",
    title: "Fire Safety Inspection",
    due_date: "2026-02-10",
    category: "regulatory",
    type: "inspection",
    status: "upcoming",
    entity: "Manufacturing Unit - Pune",
    priority: "high",
    reminder_days: 14,
  },
  {
    id: "11",
    title: "Internal Compliance Review",
    due_date: "2026-01-28",
    category: "corporate",
    type: "review",
    status: "upcoming",
    entity: "Gana Industries Pvt Ltd",
    priority: "medium",
    reminder_days: 7,
  },
];

// ============================================================================
// Helper Functions
// ============================================================================

function getCalendarDays(year: number, month: number, events: ComplianceEvent[]): CalendarDay[] {
  const firstDayOfMonth = new Date(year, month, 1);
  const lastDayOfMonth = new Date(year, month + 1, 0);
  const startDate = new Date(firstDayOfMonth);
  startDate.setDate(startDate.getDate() - startDate.getDay());

  const endDate = new Date(lastDayOfMonth);
  const daysToAdd = 6 - endDate.getDay();
  endDate.setDate(endDate.getDate() + daysToAdd);

  const today = new Date();
  today.setHours(0, 0, 0, 0);

  const days: CalendarDay[] = [];
  const currentDate = new Date(startDate);

  while (currentDate <= endDate) {
    const dateStr = currentDate.toISOString().split("T")[0];
    const dayEvents = events.filter((e) => e.due_date === dateStr);

    days.push({
      date: new Date(currentDate),
      isCurrentMonth: currentDate.getMonth() === month,
      isToday: currentDate.getTime() === today.getTime(),
      isWeekend: currentDate.getDay() === 0 || currentDate.getDay() === 6,
      events: dayEvents,
    });

    currentDate.setDate(currentDate.getDate() + 1);
  }

  return days;
}

// ============================================================================
// Compliance Calendar Page
// ============================================================================

export default function ComplianceCalendarPage() {
  const [events, setEvents] = useState<ComplianceEvent[]>(mockEvents);
  const [currentDate, setCurrentDate] = useState(new Date());
  const [viewMode, setViewMode] = useState<"month" | "week">("month");
  const [isLoading, setIsLoading] = useState(true);
  const [selectedDay, setSelectedDay] = useState<CalendarDay | null>(null);
  const [showDayDialog, setShowDayDialog] = useState(false);
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState("all");

  // Form state for creating events
  const [formData, setFormData] = useState({
    title: "",
    description: "",
    due_date: "",
    category: "tax",
    type: "filing",
    entity: "Gana Industries Pvt Ltd",
    priority: "medium",
    reminder_days: "7",
  });

  const { showToast } = useToast();
  const calendarApi = useApi();

  const year = currentDate.getFullYear();
  const month = currentDate.getMonth();

  // Fetch calendar events
  useEffect(() => {
    const fetchEvents = async () => {
      setIsLoading(true);
      try {
        const startDate = `${year}-${String(month + 1).padStart(2, "0")}-01`;
        const endDate = `${year}-${String(month + 1).padStart(2, "0")}-31`;
        const result = await calendarApi.get(
          `/compliance/calendar?start_date=${startDate}&end_date=${endDate}`
        );
        if (result && result.events) {
          setEvents(result.events);
        }
      } catch (error) {
        showToast("error", "Failed to fetch calendar events");
      } finally {
        setIsLoading(false);
      }
    };

    fetchEvents();
  }, [year, month]);

  // Filter events by category
  const filteredEvents = useMemo(() => {
    if (selectedCategory === "all") return events;
    return events.filter((e) => e.category === selectedCategory);
  }, [events, selectedCategory]);

  // Get calendar days
  const calendarDays = useMemo(() => {
    return getCalendarDays(year, month, filteredEvents);
  }, [year, month, filteredEvents]);

  // Get week view days (current week)
  const weekDays = useMemo(() => {
    const today = new Date();
    const startOfWeek = new Date(today);
    startOfWeek.setDate(today.getDate() - today.getDay());

    return Array.from({ length: 7 }, (_, i) => {
      const date = new Date(startOfWeek);
      date.setDate(startOfWeek.getDate() + i);
      const dateStr = date.toISOString().split("T")[0];
      return {
        date,
        isToday: date.toDateString() === today.toDateString(),
        isWeekend: date.getDay() === 0 || date.getDay() === 6,
        events: filteredEvents.filter((e) => e.due_date === dateStr),
      };
    });
  }, [filteredEvents]);

  // Navigation
  const goToPreviousMonth = () => {
    setCurrentDate(new Date(year, month - 1, 1));
  };

  const goToNextMonth = () => {
    setCurrentDate(new Date(year, month + 1, 1));
  };

  const goToToday = () => {
    setCurrentDate(new Date());
  };

  // Handle day click
  const handleDayClick = (day: CalendarDay) => {
    if (day.events.length > 0) {
      setSelectedDay(day);
      setShowDayDialog(true);
    }
  };

  // Handle event creation
  const handleCreateEvent = async () => {
    try {
      const newEvent: ComplianceEvent = {
        id: `EVT-${Date.now()}`,
        title: formData.title,
        description: formData.description,
        due_date: formData.due_date,
        category: formData.category as ComplianceEvent["category"],
        type: formData.type as ComplianceEvent["type"],
        status: "upcoming",
        entity: formData.entity,
        priority: formData.priority as ComplianceEvent["priority"],
        reminder_days: parseInt(formData.reminder_days),
      };

      setEvents([...events, newEvent]);
      setIsCreateDialogOpen(false);
      setFormData({
        title: "",
        description: "",
        due_date: "",
        category: "tax",
        type: "filing",
        entity: "Gana Industries Pvt Ltd",
        priority: "medium",
        reminder_days: "7",
      });
      showToast("success", "Compliance event added successfully");
    } catch (error) {
      showToast("error", "Failed to add compliance event");
    }
  };

  // Get category icon
  const getCategoryIcon = (category: string) => {
    const icons: Record<string, React.ReactNode> = {
      tax: <FileCheck className="h-4 w-4" />,
      labor: <Building className="h-4 w-4" />,
      regulatory: <Scale className="h-4 w-4" />,
      environment: <Shield className="h-4 w-4" />,
      corporate: <Star className="h-4 w-4" />,
    };
    return icons[category] || <FileCheck className="h-4 w-4" />;
  };

  // Format date
  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString("en-IN", {
      day: "2-digit",
      month: "short",
      year: "numeric",
    });
  };

  // Get upcoming events for sidebar
  const upcomingEvents = useMemo(() => {
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    return filteredEvents
      .filter((e) => new Date(e.due_date) >= today && e.status !== "completed")
      .sort((a, b) => new Date(a.due_date).getTime() - new Date(b.due_date).getTime())
      .slice(0, 5);
  }, [filteredEvents]);

  // Get overdue events
  const overdueEvents = useMemo(() => {
    return filteredEvents.filter((e) => e.status === "overdue");
  }, [filteredEvents]);

  // Get events due this week
  const thisWeekEvents = useMemo(() => {
    const today = new Date();
    const endOfWeek = new Date(today);
    endOfWeek.setDate(today.getDate() + 7);
    return filteredEvents.filter((e) => {
      const dueDate = new Date(e.due_date);
      return dueDate >= today && dueDate <= endOfWeek && e.status !== "completed";
    });
  }, [filteredEvents]);

  return (
    <div className="flex flex-col gap-6 p-6">
      <PageHeader
        title="Compliance Calendar"
        description="View and manage compliance due dates and deadlines"
        breadcrumbs={[
          { label: "Dashboard", href: "/" },
          { label: "Compliance", href: "/compliance" },
          { label: "Calendar" },
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
                  Add Event
                </Button>
              </DialogTrigger>
              <DialogContent className="max-w-lg">
                <DialogHeader>
                  <DialogTitle>Add Compliance Event</DialogTitle>
                  <DialogDescription>
                    Add a new compliance deadline or event to the calendar
                  </DialogDescription>
                </DialogHeader>
                <div className="grid gap-4 py-4">
                  <div className="space-y-2">
                    <Label>Event Title</Label>
                    <Input
                      placeholder="Enter event title"
                      value={formData.title}
                      onChange={(e) =>
                        setFormData({ ...formData, title: e.target.value })
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
                          <SelectItem value="tax">Tax</SelectItem>
                          <SelectItem value="labor">Labor</SelectItem>
                          <SelectItem value="regulatory">Regulatory</SelectItem>
                          <SelectItem value="environment">Environment</SelectItem>
                          <SelectItem value="corporate">Corporate</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="space-y-2">
                      <Label>Type</Label>
                      <Select
                        value={formData.type}
                        onValueChange={(value) =>
                          setFormData({ ...formData, type: value })
                        }
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="Select type" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="filing">Filing</SelectItem>
                          <SelectItem value="renewal">Renewal</SelectItem>
                          <SelectItem value="audit">Audit</SelectItem>
                          <SelectItem value="inspection">Inspection</SelectItem>
                          <SelectItem value="review">Review</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
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
                  <div className="space-y-2">
                    <Label>Entity</Label>
                    <Select
                      value={formData.entity}
                      onValueChange={(value) =>
                        setFormData({ ...formData, entity: value })
                      }
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select entity" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="Gana Industries Pvt Ltd">
                          Gana Industries Pvt Ltd
                        </SelectItem>
                        <SelectItem value="Manufacturing Unit - Pune">
                          Manufacturing Unit - Pune
                        </SelectItem>
                        <SelectItem value="Manufacturing Unit - Chennai">
                          Manufacturing Unit - Chennai
                        </SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <Label>Description (Optional)</Label>
                    <Textarea
                      placeholder="Enter event description"
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
                  <Button onClick={handleCreateEvent}>Add Event</Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
          </div>
        }
      />

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Main Calendar */}
        <div className="lg:col-span-3">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center gap-2">
                  <Calendar className="h-5 w-5" />
                  Compliance Calendar
                </CardTitle>
                <div className="flex items-center gap-2">
                  {/* View Toggle */}
                  <div className="flex border rounded-lg">
                    <Button
                      variant={viewMode === "month" ? "default" : "ghost"}
                      size="sm"
                      onClick={() => setViewMode("month")}
                      className="rounded-r-none"
                    >
                      <Grid className="h-4 w-4 mr-1" />
                      Month
                    </Button>
                    <Button
                      variant={viewMode === "week" ? "default" : "ghost"}
                      size="sm"
                      onClick={() => setViewMode("week")}
                      className="rounded-l-none"
                    >
                      <List className="h-4 w-4 mr-1" />
                      Week
                    </Button>
                  </div>
                  {/* Category Filter */}
                  <Select value={selectedCategory} onValueChange={setSelectedCategory}>
                    <SelectTrigger className="w-[140px]">
                      <SelectValue placeholder="Category" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Categories</SelectItem>
                      <SelectItem value="tax">Tax</SelectItem>
                      <SelectItem value="labor">Labor</SelectItem>
                      <SelectItem value="regulatory">Regulatory</SelectItem>
                      <SelectItem value="environment">Environment</SelectItem>
                      <SelectItem value="corporate">Corporate</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              {/* Month Navigation */}
              <div className="flex items-center justify-between mt-4">
                <div className="flex items-center gap-2">
                  <Button variant="outline" size="icon" onClick={goToPreviousMonth}>
                    <ChevronLeft className="h-4 w-4" />
                  </Button>
                  <h2 className="text-lg font-semibold min-w-[180px] text-center">
                    {MONTHS[month]} {year}
                  </h2>
                  <Button variant="outline" size="icon" onClick={goToNextMonth}>
                    <ChevronRight className="h-4 w-4" />
                  </Button>
                </div>
                <Button variant="outline" size="sm" onClick={goToToday}>
                  Today
                </Button>
              </div>
            </CardHeader>

            <CardContent>
              {isLoading ? (
                <div className="flex items-center justify-center py-24">
                  <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
                  <span className="ml-2 text-muted-foreground">
                    Loading calendar...
                  </span>
                </div>
              ) : viewMode === "month" ? (
                /* Monthly Calendar Grid */
                <div className="border rounded-lg overflow-hidden">
                  {/* Days of Week Header */}
                  <div className="grid grid-cols-7 bg-muted">
                    {DAYS_OF_WEEK.map((day, index) => (
                      <div
                        key={day}
                        className={cn(
                          "p-2 text-center text-sm font-medium border-b",
                          (index === 0 || index === 6) && "text-muted-foreground"
                        )}
                      >
                        {day}
                      </div>
                    ))}
                  </div>

                  {/* Calendar Days */}
                  <div className="grid grid-cols-7">
                    {calendarDays.map((day, index) => {
                      const hasEvents = day.events.length > 0;

                      return (
                        <div
                          key={index}
                          className={cn(
                            "min-h-[100px] p-1 border-b border-r cursor-pointer transition-colors",
                            "hover:bg-muted/50",
                            !day.isCurrentMonth && "bg-muted/30 text-muted-foreground",
                            day.isWeekend && day.isCurrentMonth && "bg-gray-50",
                            day.isToday && "ring-2 ring-primary ring-inset"
                          )}
                          onClick={() => handleDayClick(day)}
                        >
                          {/* Date Number */}
                          <div
                            className={cn(
                              "text-sm font-medium mb-1",
                              day.isToday && "text-primary font-bold"
                            )}
                          >
                            {day.date.getDate()}
                          </div>

                          {/* Event Markers */}
                          {hasEvents && (
                            <div className="space-y-0.5">
                              {day.events.slice(0, 3).map((event) => {
                                const colors =
                                  categoryColors[event.category] ||
                                  categoryColors.tax;
                                return (
                                  <div
                                    key={event.id}
                                    className={cn(
                                      "text-[10px] px-1 py-0.5 rounded truncate",
                                      colors.bg,
                                      colors.text,
                                      "border",
                                      colors.border
                                    )}
                                  >
                                    <div className="flex items-center gap-1">
                                      <span
                                        className={cn(
                                          "w-1.5 h-1.5 rounded-full flex-shrink-0",
                                          statusColors[event.status]
                                        )}
                                      />
                                      <span className="truncate">{event.title}</span>
                                    </div>
                                  </div>
                                );
                              })}
                              {day.events.length > 3 && (
                                <div className="text-[10px] text-muted-foreground px-1">
                                  +{day.events.length - 3} more
                                </div>
                              )}
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                </div>
              ) : (
                /* Weekly View */
                <div className="space-y-4">
                  {weekDays.map((day, index) => (
                    <div
                      key={index}
                      className={cn(
                        "border rounded-lg p-4",
                        day.isToday && "ring-2 ring-primary",
                        day.isWeekend && "bg-muted/30"
                      )}
                    >
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center gap-2">
                          <span
                            className={cn(
                              "text-lg font-semibold",
                              day.isToday && "text-primary"
                            )}
                          >
                            {DAYS_OF_WEEK[day.date.getDay()]}
                          </span>
                          <span className="text-muted-foreground">
                            {day.date.toLocaleDateString("en-IN", {
                              day: "numeric",
                              month: "short",
                            })}
                          </span>
                          {day.isToday && (
                            <Badge variant="outline" className="ml-2">
                              Today
                            </Badge>
                          )}
                        </div>
                        <span className="text-sm text-muted-foreground">
                          {day.events.length} event(s)
                        </span>
                      </div>
                      {day.events.length > 0 ? (
                        <div className="space-y-2">
                          {day.events.map((event) => {
                            const colors =
                              categoryColors[event.category] || categoryColors.tax;
                            return (
                              <div
                                key={event.id}
                                className={cn(
                                  "p-3 rounded-lg border",
                                  colors.bg,
                                  colors.border
                                )}
                              >
                                <div className="flex items-center justify-between">
                                  <div className="flex items-center gap-2">
                                    {getCategoryIcon(event.category)}
                                    <span className="font-medium">{event.title}</span>
                                  </div>
                                  <div className="flex items-center gap-2">
                                    <Badge
                                      className={cn(
                                        "capitalize",
                                        event.status === "completed" &&
                                          "bg-green-500",
                                        event.status === "due_soon" &&
                                          "bg-yellow-500",
                                        event.status === "overdue" && "bg-red-500",
                                        event.status === "upcoming" && "bg-gray-500"
                                      )}
                                    >
                                      {event.status.replace("_", " ")}
                                    </Badge>
                                  </div>
                                </div>
                                <p className="text-sm text-muted-foreground mt-1">
                                  {event.entity}
                                </p>
                              </div>
                            );
                          })}
                        </div>
                      ) : (
                        <p className="text-sm text-muted-foreground text-center py-4">
                          No compliance events scheduled
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              )}

              {/* Legend */}
              <div className="mt-4 flex flex-wrap gap-4 text-sm border-t pt-4">
                <span className="text-xs text-muted-foreground">Categories:</span>
                {Object.entries(categoryColors).map(([category, colors]) => (
                  <div key={category} className="flex items-center gap-1">
                    <span
                      className={cn(
                        "w-3 h-3 rounded",
                        colors.bg,
                        "border",
                        colors.border
                      )}
                    />
                    <span className="text-xs capitalize">{category}</span>
                  </div>
                ))}
              </div>

              <div className="mt-2 flex flex-wrap gap-4 text-sm">
                <span className="text-xs text-muted-foreground">Status:</span>
                {Object.entries(statusColors).map(([status, color]) => (
                  <div key={status} className="flex items-center gap-1">
                    <span className={cn("w-2 h-2 rounded-full", color)} />
                    <span className="text-xs capitalize">{status.replace("_", " ")}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Overdue Alert */}
          {overdueEvents.length > 0 && (
            <Card className="border-red-200 bg-red-50">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium flex items-center gap-2 text-red-800">
                  <AlertTriangle className="h-4 w-4" />
                  Overdue ({overdueEvents.length})
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {overdueEvents.slice(0, 3).map((event) => (
                    <div
                      key={event.id}
                      className="p-2 bg-white rounded border border-red-200"
                    >
                      <p className="text-sm font-medium text-red-800">
                        {event.title}
                      </p>
                      <p className="text-xs text-red-600">
                        Due: {formatDate(event.due_date)}
                      </p>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Due This Week */}
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <Clock className="h-4 w-4 text-yellow-500" />
                Due This Week ({thisWeekEvents.length})
              </CardTitle>
            </CardHeader>
            <CardContent>
              {thisWeekEvents.length > 0 ? (
                <div className="space-y-2">
                  {thisWeekEvents.map((event) => {
                    const colors =
                      categoryColors[event.category] || categoryColors.tax;
                    return (
                      <div
                        key={event.id}
                        className={cn(
                          "p-2 rounded border",
                          colors.bg,
                          colors.border
                        )}
                      >
                        <div className="flex items-center gap-2">
                          {getCategoryIcon(event.category)}
                          <span className="text-sm font-medium">{event.title}</span>
                        </div>
                        <p className="text-xs text-muted-foreground mt-1">
                          {formatDate(event.due_date)}
                        </p>
                      </div>
                    );
                  })}
                </div>
              ) : (
                <p className="text-sm text-muted-foreground text-center py-4">
                  No compliance events due this week
                </p>
              )}
            </CardContent>
          </Card>

          {/* Upcoming Events */}
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <Star className="h-4 w-4 text-blue-500" />
                Upcoming Deadlines
              </CardTitle>
              <CardDescription>Next 5 compliance events</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {upcomingEvents.map((event) => {
                  const colors =
                    categoryColors[event.category] || categoryColors.tax;
                  return (
                    <div
                      key={event.id}
                      className="flex items-center justify-between p-2 rounded bg-muted/50 border"
                    >
                      <div className="flex items-center gap-2">
                        <span
                          className={cn(
                            "w-2 h-2 rounded-full",
                            colors.bg,
                            colors.border,
                            "border"
                          )}
                        />
                        <span className="text-sm truncate max-w-[120px]">
                          {event.title}
                        </span>
                      </div>
                      <Badge variant="outline" className="text-xs">
                        {formatDate(event.due_date)}
                      </Badge>
                    </div>
                  );
                })}
              </div>
            </CardContent>
          </Card>

          {/* Quick Stats */}
          <Card>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <Info className="h-4 w-4 text-gray-500" />
                This Month Summary
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Total Events</span>
                  <span className="font-medium">{filteredEvents.length}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Completed</span>
                  <span className="font-medium text-green-600">
                    {filteredEvents.filter((e) => e.status === "completed").length}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Due Soon</span>
                  <span className="font-medium text-yellow-600">
                    {filteredEvents.filter((e) => e.status === "due_soon").length}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Overdue</span>
                  <span className="font-medium text-red-600">
                    {overdueEvents.length}
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Day Details Dialog */}
      <Dialog open={showDayDialog} onOpenChange={setShowDayDialog}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Calendar className="h-5 w-5" />
              {selectedDay &&
                selectedDay.date.toLocaleDateString("en-IN", {
                  weekday: "long",
                  day: "numeric",
                  month: "long",
                  year: "numeric",
                })}
            </DialogTitle>
            <DialogDescription>
              {selectedDay?.isToday && "Today - "}
              {selectedDay?.events.length || 0} compliance event(s)
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 py-4">
            {selectedDay?.events.map((event) => {
              const colors =
                categoryColors[event.category] || categoryColors.tax;
              return (
                <div
                  key={event.id}
                  className={cn(
                    "p-4 rounded-lg border",
                    colors.bg,
                    colors.border
                  )}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      {getCategoryIcon(event.category)}
                      <span className="font-medium">{event.title}</span>
                    </div>
                    <Badge
                      className={cn(
                        "capitalize",
                        event.status === "completed" && "bg-green-500",
                        event.status === "due_soon" && "bg-yellow-500",
                        event.status === "overdue" && "bg-red-500",
                        event.status === "upcoming" && "bg-gray-500"
                      )}
                    >
                      {event.status.replace("_", " ")}
                    </Badge>
                  </div>
                  {event.description && (
                    <p className="text-sm text-muted-foreground mt-2">
                      {event.description}
                    </p>
                  )}
                  <div className="grid grid-cols-2 gap-2 mt-3 text-sm">
                    <div>
                      <span className="text-muted-foreground">Category:</span>{" "}
                      <span className="capitalize">{event.category}</span>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Type:</span>{" "}
                      <span className="capitalize">{event.type}</span>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Entity:</span>{" "}
                      {event.entity}
                    </div>
                    <div>
                      <span className="text-muted-foreground">Priority:</span>{" "}
                      <Badge
                        variant="outline"
                        className={cn(
                          event.priority === "high" && "bg-red-100 text-red-800",
                          event.priority === "medium" &&
                            "bg-yellow-100 text-yellow-800",
                          event.priority === "low" && "bg-green-100 text-green-800"
                        )}
                      >
                        {event.priority}
                      </Badge>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setShowDayDialog(false)}>
              Close
            </Button>
            <Button asChild variant="outline">
              <Link href="/compliance/tasks">View Tasks</Link>
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
