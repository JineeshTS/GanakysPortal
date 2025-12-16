'use client';

/**
 * Weekly Timesheet Page
 */

import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { DashboardLayout } from '@/components/layout/dashboard-layout';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import timesheetApi from '@/lib/api/timesheet';
import type {
  WeeklyTimesheetData,
  TimesheetEntry,
  TimesheetEntryRequest,
  TimesheetStatus,
  Project,
  ProjectTask,
} from '@/types/timesheet';

const statusColors: Record<TimesheetStatus, string> = {
  draft: 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300',
  submitted: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300',
  approved: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300',
  rejected: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300',
};

const daysOfWeek = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];

export default function WeeklyTimesheetPage() {
  const router = useRouter();
  const [weekData, setWeekData] = useState<WeeklyTimesheetData | null>(null);
  const [projects, setProjects] = useState<Project[]>([]);
  const [tasks, setTasks] = useState<ProjectTask[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Entry dialog state
  const [entryDialogOpen, setEntryDialogOpen] = useState(false);
  const [selectedDate, setSelectedDate] = useState<string>('');
  const [selectedEntry, setSelectedEntry] = useState<TimesheetEntry | null>(null);
  const [entryForm, setEntryForm] = useState<TimesheetEntryRequest>({
    date: '',
    project_id: '',
    task_id: '',
    hours: 0,
    is_billable: true,
    description: '',
  });

  // Get the start date of current week
  const getWeekStart = (date: Date = new Date()) => {
    const d = new Date(date);
    const day = d.getDay();
    const diff = d.getDate() - day + (day === 0 ? -6 : 1); // Monday as start
    return new Date(d.setDate(diff));
  };

  const [currentWeekStart, setCurrentWeekStart] = useState(getWeekStart());

  const loadWeekData = useCallback(async () => {
    const weekStartStr = currentWeekStart.toISOString().split('T')[0];
    setIsLoading(true);
    try {
      const [data, projectList] = await Promise.all([
        timesheetApi.getWeeklyTimesheet(weekStartStr),
        timesheetApi.getProjects(),
      ]);
      setWeekData(data);
      setProjects(projectList);
    } catch (error) {
      console.error('Failed to load timesheet:', error);
    } finally {
      setIsLoading(false);
    }
  }, [currentWeekStart]);

  useEffect(() => {
    loadWeekData();
  }, [loadWeekData]);

  const loadTasks = async (projectId: string) => {
    try {
      const taskList = await timesheetApi.getProjectTasks(projectId);
      setTasks(taskList);
    } catch (error) {
      console.error('Failed to load tasks:', error);
      setTasks([]);
    }
  };

  const navigateWeek = (direction: -1 | 1) => {
    const newDate = new Date(currentWeekStart);
    newDate.setDate(newDate.getDate() + direction * 7);
    setCurrentWeekStart(newDate);
  };

  const goToCurrentWeek = () => {
    setCurrentWeekStart(getWeekStart());
  };

  const getWeekDates = () => {
    const dates: string[] = [];
    for (let i = 0; i < 7; i++) {
      const date = new Date(currentWeekStart);
      date.setDate(date.getDate() + i);
      dates.push(date.toISOString().split('T')[0]);
    }
    return dates;
  };

  const weekDates = getWeekDates();

  const getEntriesForDate = (date: string): TimesheetEntry[] => {
    return weekData?.entries_by_day[date] || [];
  };

  const getDayTotal = (date: string): number => {
    return getEntriesForDate(date).reduce((sum, e) => sum + e.hours, 0);
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.getDate();
  };

  const isToday = (dateStr: string) => {
    return dateStr === new Date().toISOString().split('T')[0];
  };

  const openEntryDialog = (date: string, entry?: TimesheetEntry) => {
    setSelectedDate(date);
    setSelectedEntry(entry || null);
    setEntryForm({
      date,
      project_id: entry?.project_id || '',
      task_id: entry?.task_id || '',
      hours: entry?.hours || 0,
      is_billable: entry?.is_billable ?? true,
      description: entry?.description || '',
    });
    if (entry?.project_id) {
      loadTasks(entry.project_id);
    } else {
      setTasks([]);
    }
    setEntryDialogOpen(true);
  };

  const handleProjectChange = (projectId: string) => {
    setEntryForm({ ...entryForm, project_id: projectId, task_id: '' });
    if (projectId) {
      loadTasks(projectId);
      const project = projects.find((p) => p.id === projectId);
      if (project) {
        setEntryForm((prev) => ({ ...prev, is_billable: project.is_billable }));
      }
    } else {
      setTasks([]);
    }
  };

  const handleSaveEntry = async () => {
    if (!entryForm.project_id || entryForm.hours <= 0) return;
    if (!weekData?.timesheet?.id) return;

    setIsSaving(true);
    try {
      if (selectedEntry) {
        await timesheetApi.updateEntry(weekData.timesheet.id, selectedEntry.id, entryForm);
      } else {
        await timesheetApi.addEntry(weekData.timesheet.id, entryForm);
      }
      setEntryDialogOpen(false);
      loadWeekData();
    } catch (error) {
      console.error('Failed to save entry:', error);
    } finally {
      setIsSaving(false);
    }
  };

  const handleDeleteEntry = async () => {
    if (!selectedEntry || !weekData?.timesheet?.id) return;
    if (!confirm('Are you sure you want to delete this entry?')) return;

    setIsSaving(true);
    try {
      await timesheetApi.deleteEntry(weekData.timesheet.id, selectedEntry.id);
      setEntryDialogOpen(false);
      loadWeekData();
    } catch (error) {
      console.error('Failed to delete entry:', error);
    } finally {
      setIsSaving(false);
    }
  };

  const handleSubmitTimesheet = async () => {
    if (!weekData?.timesheet?.id) return;
    if (!confirm('Are you sure you want to submit this timesheet for approval?')) return;

    setIsSubmitting(true);
    try {
      await timesheetApi.submitTimesheet(weekData.timesheet.id);
      loadWeekData();
    } catch (error) {
      console.error('Failed to submit timesheet:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleRecallTimesheet = async () => {
    if (!weekData?.timesheet?.id) return;
    if (!confirm('Are you sure you want to recall this timesheet?')) return;

    setIsSubmitting(true);
    try {
      await timesheetApi.recallTimesheet(weekData.timesheet.id);
      loadWeekData();
    } catch (error) {
      console.error('Failed to recall timesheet:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCreateTimesheet = async () => {
    const weekStartStr = currentWeekStart.toISOString().split('T')[0];
    setIsLoading(true);
    try {
      await timesheetApi.createOrUpdateTimesheet(weekStartStr);
      loadWeekData();
    } catch (error) {
      console.error('Failed to create timesheet:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const canEdit = !weekData?.timesheet || weekData.timesheet.status === 'draft' || weekData.timesheet.status === 'rejected';

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold tracking-tight">Weekly Timesheet</h1>
            <p className="text-muted-foreground">
              Track your working hours for the week
            </p>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" onClick={() => router.push('/timesheet/history')}>
              <svg className="mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              History
            </Button>
            <Button variant="outline" onClick={() => router.push('/timesheet/approvals')}>
              <svg className="mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              Approvals
            </Button>
          </div>
        </div>

        {/* Week Navigation */}
        <Card>
          <CardContent className="py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <Button variant="outline" size="icon" onClick={() => navigateWeek(-1)}>
                  <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                  </svg>
                </Button>
                <div className="text-center">
                  <div className="font-semibold">
                    {currentWeekStart.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })} -{' '}
                    {new Date(currentWeekStart.getTime() + 6 * 24 * 60 * 60 * 1000).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}
                  </div>
                  <Button variant="link" size="sm" onClick={goToCurrentWeek} className="h-auto p-0">
                    Go to current week
                  </Button>
                </div>
                <Button variant="outline" size="icon" onClick={() => navigateWeek(1)}>
                  <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </Button>
              </div>

              <div className="flex items-center gap-4">
                {weekData?.timesheet && (
                  <Badge variant="secondary" className={statusColors[weekData.timesheet.status]}>
                    {weekData.timesheet.status.charAt(0).toUpperCase() + weekData.timesheet.status.slice(1)}
                  </Badge>
                )}
                <div className="text-right">
                  <div className="text-sm text-muted-foreground">Total Hours</div>
                  <div className="text-2xl font-bold">{weekData?.total_hours || 0}</div>
                </div>
                <div className="text-right">
                  <div className="text-sm text-muted-foreground">Billable</div>
                  <div className="text-2xl font-bold text-green-600">{weekData?.billable_hours || 0}</div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Timesheet Grid */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Time Entries</CardTitle>
                <CardDescription>Click on a day to add or edit entries</CardDescription>
              </div>
              {canEdit && weekData?.timesheet && weekData.total_hours > 0 && (
                <Button onClick={handleSubmitTimesheet} disabled={isSubmitting}>
                  {isSubmitting ? 'Submitting...' : 'Submit for Approval'}
                </Button>
              )}
              {weekData?.timesheet?.status === 'submitted' && (
                <Button variant="outline" onClick={handleRecallTimesheet} disabled={isSubmitting}>
                  {isSubmitting ? 'Recalling...' : 'Recall Timesheet'}
                </Button>
              )}
            </div>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="p-8 text-center">
                <div className="h-8 w-8 mx-auto animate-spin rounded-full border-4 border-primary border-t-transparent" />
                <p className="mt-2 text-muted-foreground">Loading timesheet...</p>
              </div>
            ) : !weekData?.timesheet ? (
              <div className="py-8 text-center">
                <svg
                  className="mx-auto h-12 w-12 text-muted-foreground"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
                <h3 className="mt-2 font-medium">No timesheet for this week</h3>
                <p className="text-sm text-muted-foreground">
                  Create a timesheet to start logging your hours
                </p>
                <Button className="mt-4" onClick={handleCreateTimesheet}>
                  Create Timesheet
                </Button>
              </div>
            ) : (
              <div className="grid grid-cols-7 gap-2">
                {weekDates.map((date, index) => {
                  const entries = getEntriesForDate(date);
                  const dayTotal = getDayTotal(date);
                  const isWeekend = index >= 5;

                  return (
                    <div
                      key={date}
                      className={`border rounded-lg p-3 min-h-[200px] ${
                        isToday(date) ? 'border-primary border-2' : ''
                      } ${isWeekend ? 'bg-muted/30' : ''}`}
                    >
                      <div className="flex items-center justify-between mb-2">
                        <div>
                          <div className="text-sm font-medium">{daysOfWeek[index]}</div>
                          <div className={`text-lg font-bold ${isToday(date) ? 'text-primary' : ''}`}>
                            {formatDate(date)}
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="text-sm text-muted-foreground">Hours</div>
                          <div className="font-semibold">{dayTotal}</div>
                        </div>
                      </div>

                      <div className="space-y-1">
                        {entries.map((entry) => (
                          <div
                            key={entry.id}
                            className={`p-2 rounded text-xs cursor-pointer hover:opacity-80 ${
                              entry.is_billable ? 'bg-green-100 dark:bg-green-900/30' : 'bg-gray-100 dark:bg-gray-800'
                            }`}
                            onClick={() => canEdit && openEntryDialog(date, entry)}
                          >
                            <div className="font-medium truncate">{entry.project_name || 'No project'}</div>
                            <div className="text-muted-foreground">{entry.hours}h</div>
                          </div>
                        ))}
                      </div>

                      {canEdit && (
                        <Button
                          variant="ghost"
                          size="sm"
                          className="w-full mt-2"
                          onClick={() => openEntryDialog(date)}
                        >
                          <svg className="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                          </svg>
                          Add
                        </Button>
                      )}
                    </div>
                  );
                })}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Entry Dialog */}
      <Dialog open={entryDialogOpen} onOpenChange={setEntryDialogOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>
              {selectedEntry ? 'Edit Time Entry' : 'Add Time Entry'}
            </DialogTitle>
            <DialogDescription>
              {new Date(selectedDate).toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })}
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4">
            <div className="space-y-2">
              <Label>Project *</Label>
              <Select
                value={entryForm.project_id || ''}
                onValueChange={handleProjectChange}
                disabled={isSaving}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select a project" />
                </SelectTrigger>
                <SelectContent>
                  {projects.map((project) => (
                    <SelectItem key={project.id} value={project.id}>
                      {project.code} - {project.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {tasks.length > 0 && (
              <div className="space-y-2">
                <Label>Task</Label>
                <Select
                  value={entryForm.task_id || ''}
                  onValueChange={(v) => setEntryForm({ ...entryForm, task_id: v })}
                  disabled={isSaving}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select a task (optional)" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="">No specific task</SelectItem>
                    {tasks.map((task) => (
                      <SelectItem key={task.id} value={task.id}>
                        {task.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            )}

            <div className="space-y-2">
              <Label>Hours *</Label>
              <Input
                type="number"
                min="0.5"
                max="24"
                step="0.5"
                value={entryForm.hours}
                onChange={(e) => setEntryForm({ ...entryForm, hours: parseFloat(e.target.value) || 0 })}
                disabled={isSaving}
              />
            </div>

            <div className="space-y-2">
              <Label>Description</Label>
              <Textarea
                placeholder="What did you work on?"
                value={entryForm.description}
                onChange={(e) => setEntryForm({ ...entryForm, description: e.target.value })}
                disabled={isSaving}
                rows={2}
              />
            </div>

            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="is_billable"
                checked={entryForm.is_billable}
                onChange={(e) => setEntryForm({ ...entryForm, is_billable: e.target.checked })}
                disabled={isSaving}
                className="h-4 w-4"
              />
              <Label htmlFor="is_billable" className="font-normal">
                Billable hours
              </Label>
            </div>
          </div>

          <DialogFooter className="flex justify-between">
            <div>
              {selectedEntry && (
                <Button
                  variant="destructive"
                  onClick={handleDeleteEntry}
                  disabled={isSaving}
                >
                  Delete
                </Button>
              )}
            </div>
            <div className="flex gap-2">
              <Button
                variant="outline"
                onClick={() => setEntryDialogOpen(false)}
                disabled={isSaving}
              >
                Cancel
              </Button>
              <Button
                onClick={handleSaveEntry}
                disabled={isSaving || !entryForm.project_id || entryForm.hours <= 0}
              >
                {isSaving ? 'Saving...' : 'Save'}
              </Button>
            </div>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </DashboardLayout>
  );
}
