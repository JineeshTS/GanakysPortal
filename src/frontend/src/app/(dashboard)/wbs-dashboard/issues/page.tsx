'use client'

import { useState, useEffect, useCallback } from 'react'
import { api } from '@/services/api'
import { useToast } from '@/hooks/use-toast'
import { PageHeader } from '@/components/layout/page-header'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import {
  AlertCircle,
  Bug,
  CheckCircle,
  ChevronLeft,
  Clock,
  FileCode,
  Filter,
  Loader2,
  Plus,
  RefreshCw,
  Search,
  Shield,
  XCircle,
  Zap,
  Database,
  Layout,
  Server,
  Settings,
  FileText,
} from 'lucide-react'
import Link from 'next/link'

// Types
interface WBSIssue {
  id: string
  issue_code: string
  title: string
  description: string | null
  category: string
  severity: string
  module: string | null
  file_path: string | null
  line_number: number | null
  status: string
  resolution: string | null
  resolved_at: string | null
  related_task_id: string | null
  created_at: string
  updated_at: string
}

interface IssueSummary {
  total: number
  by_status: Record<string, number>
  by_severity: Record<string, number>
  by_category: Record<string, number>
}

// Config
const severityConfig: Record<string, { color: string; icon: React.ReactNode; label: string }> = {
  critical: { color: 'bg-red-600 text-white', icon: <AlertCircle className="h-3.5 w-3.5" />, label: 'Critical' },
  high: { color: 'bg-orange-500 text-white', icon: <Zap className="h-3.5 w-3.5" />, label: 'High' },
  medium: { color: 'bg-yellow-500 text-white', icon: <Clock className="h-3.5 w-3.5" />, label: 'Medium' },
  low: { color: 'bg-slate-400 text-white', icon: <Clock className="h-3.5 w-3.5" />, label: 'Low' },
}

const statusConfig: Record<string, { color: string; icon: React.ReactNode; label: string }> = {
  open: { color: 'bg-red-100 text-red-700', icon: <AlertCircle className="h-3.5 w-3.5" />, label: 'Open' },
  in_progress: { color: 'bg-blue-100 text-blue-700', icon: <Clock className="h-3.5 w-3.5" />, label: 'In Progress' },
  resolved: { color: 'bg-green-100 text-green-700', icon: <CheckCircle className="h-3.5 w-3.5" />, label: 'Resolved' },
  wont_fix: { color: 'bg-slate-100 text-slate-700', icon: <XCircle className="h-3.5 w-3.5" />, label: "Won't Fix" },
  duplicate: { color: 'bg-purple-100 text-purple-700', icon: <FileCode className="h-3.5 w-3.5" />, label: 'Duplicate' },
}

const categoryConfig: Record<string, { color: string; icon: React.ReactNode; label: string }> = {
  bug: { color: 'bg-red-100 text-red-700', icon: <Bug className="h-3.5 w-3.5" />, label: 'Bug' },
  missing_feature: { color: 'bg-blue-100 text-blue-700', icon: <Plus className="h-3.5 w-3.5" />, label: 'Missing Feature' },
  security: { color: 'bg-orange-100 text-orange-700', icon: <Shield className="h-3.5 w-3.5" />, label: 'Security' },
  performance: { color: 'bg-yellow-100 text-yellow-700', icon: <Zap className="h-3.5 w-3.5" />, label: 'Performance' },
  ui: { color: 'bg-pink-100 text-pink-700', icon: <Layout className="h-3.5 w-3.5" />, label: 'UI' },
  api: { color: 'bg-purple-100 text-purple-700', icon: <Server className="h-3.5 w-3.5" />, label: 'API' },
  database: { color: 'bg-amber-100 text-amber-700', icon: <Database className="h-3.5 w-3.5" />, label: 'Database' },
  configuration: { color: 'bg-slate-100 text-slate-700', icon: <Settings className="h-3.5 w-3.5" />, label: 'Config' },
  documentation: { color: 'bg-cyan-100 text-cyan-700', icon: <FileText className="h-3.5 w-3.5" />, label: 'Docs' },
}

/**
 * CreateIssueDialog - Modal dialog for creating new WBS issues
 *
 * @component
 * @param {Object} props - Component props
 * @param {() => void} props.onCreated - Callback function invoked after an issue is successfully created.
 *                                        Typically used to refresh the issues list.
 *
 * @example
 * <CreateIssueDialog onCreated={() => fetchIssues()} />
 *
 * @description
 * Provides a form interface for creating new issues with fields for:
 * - Title (required)
 * - Description
 * - Category (bug, enhancement, performance, security, etc.)
 * - Severity (critical, high, medium, low)
 * - Module reference
 * - File path and line number for code-related issues
 * - Related task ID for WBS task linking
 */
function CreateIssueDialog({ onCreated }: { onCreated: () => void }) {
  const [open, setOpen] = useState(false)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const { toast } = useToast()
  const [form, setForm] = useState({
    title: '',
    description: '',
    category: 'bug',
    severity: 'medium',
    module: '',
    file_path: '',
    line_number: '',
    related_task_id: '',
  })

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || '/api/v1'

  const handleSubmit = async () => {
    if (!form.title.trim()) return

    setIsSubmitting(true)
    try {
      await api.post('/wbs/issues', {
        ...form,
        line_number: form.line_number ? Math.max(1, parseInt(form.line_number)) : null,
        module: form.module || null,
        file_path: form.file_path || null,
        related_task_id: form.related_task_id || null,
      })

      // api.post throws on error, so if we reach here, it succeeded
      toast.success('Issue Created', 'The issue has been logged successfully')
      setOpen(false)
      setForm({
        title: '',
        description: '',
        category: 'bug',
        severity: 'medium',
        module: '',
        file_path: '',
        line_number: '',
        related_task_id: '',
      })
      onCreated()
    } catch (err) {
      console.error('Failed to create issue:', err)
      const message = err instanceof Error ? err.message : 'Failed to create issue'
      toast.error('Create Failed', message)
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button>
          <Plus className="h-4 w-4 mr-2" />
          New Issue
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-[600px]">
        <DialogHeader>
          <DialogTitle>Create New Issue</DialogTitle>
          <DialogDescription>
            Log a new issue discovered during code review
          </DialogDescription>
        </DialogHeader>
        <div className="space-y-4 py-4">
          <div className="space-y-2">
            <Label>Title *</Label>
            <Input
              value={form.title}
              onChange={(e) => setForm({ ...form, title: e.target.value })}
              placeholder="Brief description of the issue"
            />
          </div>
          <div className="space-y-2">
            <Label>Description</Label>
            <Textarea
              value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
              placeholder="Detailed description, steps to reproduce, etc."
              rows={3}
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label>Category</Label>
              <Select value={form.category} onValueChange={(v) => setForm({ ...form, category: v })}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {Object.entries(categoryConfig).map(([key, config]) => (
                    <SelectItem key={key} value={key}>{config.label}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label>Severity</Label>
              <Select value={form.severity} onValueChange={(v) => setForm({ ...form, severity: v })}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="critical">Critical</SelectItem>
                  <SelectItem value="high">High</SelectItem>
                  <SelectItem value="medium">Medium</SelectItem>
                  <SelectItem value="low">Low</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label>Module</Label>
              <Input
                value={form.module}
                onChange={(e) => setForm({ ...form, module: e.target.value })}
                placeholder="e.g., auth, payroll, crm"
              />
            </div>
            <div className="space-y-2">
              <Label>Related Task ID</Label>
              <Input
                value={form.related_task_id}
                onChange={(e) => setForm({ ...form, related_task_id: e.target.value })}
                placeholder="e.g., P04-FIN-INV-T001"
              />
            </div>
          </div>
          <div className="grid grid-cols-3 gap-4">
            <div className="space-y-2 col-span-2">
              <Label>File Path</Label>
              <Input
                value={form.file_path}
                onChange={(e) => setForm({ ...form, file_path: e.target.value })}
                placeholder="e.g., backend/app/api/v1/endpoints/auth.py"
              />
            </div>
            <div className="space-y-2">
              <Label>Line #</Label>
              <Input
                type="number"
                min="1"
                max="10000000"
                value={form.line_number}
                onChange={(e) => {
                  const value = e.target.value
                  // Only allow positive integers
                  if (value === '' || (/^\d+$/.test(value) && parseInt(value) >= 1)) {
                    setForm({ ...form, line_number: value })
                  }
                }}
                placeholder="123"
              />
            </div>
          </div>
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={() => setOpen(false)}>Cancel</Button>
          <Button onClick={handleSubmit} disabled={isSubmitting || !form.title.trim()}>
            {isSubmitting ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
            Create Issue
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

export default function IssuesPage() {
  const [isLoading, setIsLoading] = useState(true)
  const [issues, setIssues] = useState<WBSIssue[]>([])
  const [summary, setSummary] = useState<IssueSummary | null>(null)
  const [updatingIssue, setUpdatingIssue] = useState<string | null>(null)
  const { toast } = useToast()

  // Filters
  const [statusFilter, setStatusFilter] = useState('all')
  const [severityFilter, setSeverityFilter] = useState('all')
  const [categoryFilter, setCategoryFilter] = useState('all')
  const [searchQuery, setSearchQuery] = useState('')

  const fetchData = useCallback(async () => {
    setIsLoading(true)
    try {
      // Fetch summary - uses api client with auth headers
      const summaryData = await api.get<IssueSummary>('/wbs/issues/summary')
      setSummary(summaryData)

      // Fetch issues with filters
      const params = new URLSearchParams()
      if (statusFilter !== 'all') params.set('status', statusFilter)
      if (severityFilter !== 'all') params.set('severity', severityFilter)
      if (categoryFilter !== 'all') params.set('category', categoryFilter)
      if (searchQuery) params.set('search', searchQuery)

      const issuesData = await api.get<WBSIssue[]>(`/wbs/issues?${params.toString()}`)
      setIssues(issuesData)
    } catch (err) {
      console.error('Failed to fetch issues:', err)
      const message = err instanceof Error ? err.message : 'Failed to load issues'
      toast.error('Load Failed', message)
    } finally {
      setIsLoading(false)
    }
  }, [statusFilter, severityFilter, categoryFilter, searchQuery, toast])

  useEffect(() => {
    fetchData()
  }, [fetchData])

  const handleStatusChange = async (issueCode: string, newStatus: string) => {
    if (updatingIssue) return // Prevent concurrent updates

    // Find the issue and store previous state for rollback
    const issueIndex = issues.findIndex(i => i.issue_code === issueCode)
    if (issueIndex === -1) return

    const previousStatus = issues[issueIndex].status

    // Optimistic update - immediately update UI
    setIssues(prev => prev.map(issue =>
      issue.issue_code === issueCode
        ? { ...issue, status: newStatus }
        : issue
    ))

    setUpdatingIssue(issueCode)
    try {
      await api.patch(`/wbs/issues/${issueCode}`, { status: newStatus })
      toast.success('Status Updated', `Issue ${issueCode} marked as ${newStatus.replace('_', ' ')}`)
      // Refresh to get any server-side changes (e.g., resolved_at timestamp)
      fetchData()
    } catch (err) {
      // Rollback on failure
      setIssues(prev => prev.map(issue =>
        issue.issue_code === issueCode
          ? { ...issue, status: previousStatus }
          : issue
      ))
      console.error('Failed to update issue:', err)
      const message = err instanceof Error ? err.message : 'Failed to update issue status'
      toast.error('Update Failed', message)
    } finally {
      setUpdatingIssue(null)
    }
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Issue Tracker"
        description="Track and manage issues discovered during code review"
        actions={
          <div className="flex gap-2">
            <Link href="/wbs-dashboard">
              <Button variant="outline">
                <ChevronLeft className="h-4 w-4 mr-1" />
                Dashboard
              </Button>
            </Link>
            <Button variant="outline" onClick={fetchData} disabled={isLoading}>
              <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
            <CreateIssueDialog onCreated={fetchData} />
          </div>
        }
      />

      {/* Summary Cards */}
      <div className="grid gap-4 md:grid-cols-5">
        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center justify-between">
              <p className="text-sm text-muted-foreground">Total Issues</p>
              <p className="text-2xl font-bold">{summary?.total || 0}</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center justify-between">
              <p className="text-sm text-muted-foreground">Open</p>
              <p className="text-2xl font-bold text-red-600">{summary?.by_status?.open || 0}</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center justify-between">
              <p className="text-sm text-muted-foreground">In Progress</p>
              <p className="text-2xl font-bold text-blue-600">{summary?.by_status?.in_progress || 0}</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center justify-between">
              <p className="text-sm text-muted-foreground">Critical</p>
              <p className="text-2xl font-bold text-red-600">{summary?.by_severity?.critical || 0}</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center justify-between">
              <p className="text-sm text-muted-foreground">Resolved</p>
              <p className="text-2xl font-bold text-green-600">{summary?.by_status?.resolved || 0}</p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="pt-4">
          <div className="flex flex-wrap gap-4">
            <div className="flex-1 min-w-[200px]">
              <div className="relative">
                <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search issues..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-8"
                />
              </div>
            </div>
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-[140px]">
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="open">Open</SelectItem>
                <SelectItem value="in_progress">In Progress</SelectItem>
                <SelectItem value="resolved">Resolved</SelectItem>
                <SelectItem value="wont_fix">Won't Fix</SelectItem>
                <SelectItem value="duplicate">Duplicate</SelectItem>
              </SelectContent>
            </Select>
            <Select value={severityFilter} onValueChange={setSeverityFilter}>
              <SelectTrigger className="w-[140px]">
                <SelectValue placeholder="Severity" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Severity</SelectItem>
                <SelectItem value="critical">Critical</SelectItem>
                <SelectItem value="high">High</SelectItem>
                <SelectItem value="medium">Medium</SelectItem>
                <SelectItem value="low">Low</SelectItem>
              </SelectContent>
            </Select>
            <Select value={categoryFilter} onValueChange={setCategoryFilter}>
              <SelectTrigger className="w-[150px]">
                <SelectValue placeholder="Category" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Categories</SelectItem>
                {Object.entries(categoryConfig).map(([key, config]) => (
                  <SelectItem key={key} value={key}>{config.label}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Loading */}
      {isLoading && (
        <Card className="p-8 flex items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <span className="ml-2">Loading issues...</span>
        </Card>
      )}

      {/* Issues Table */}
      {!isLoading && (
        <Card>
          <CardContent className="p-0">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-[100px]">Code</TableHead>
                  <TableHead>Title</TableHead>
                  <TableHead className="w-[100px]">Category</TableHead>
                  <TableHead className="w-[100px]">Severity</TableHead>
                  <TableHead className="w-[100px]">Module</TableHead>
                  <TableHead className="w-[120px]">Status</TableHead>
                  <TableHead className="w-[100px]">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {issues.map((issue) => {
                  const severity = severityConfig[issue.severity] || severityConfig.medium
                  const status = statusConfig[issue.status] || statusConfig.open
                  const category = categoryConfig[issue.category] || categoryConfig.bug

                  return (
                    <TableRow key={issue.id}>
                      <TableCell>
                        <Badge variant="outline" className="font-mono text-xs">
                          {issue.issue_code}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <div>
                          <p className="font-medium text-sm">{issue.title}</p>
                          {issue.file_path && (
                            <p className="text-xs text-muted-foreground font-mono truncate max-w-[300px]">
                              {issue.file_path}{issue.line_number ? `:${issue.line_number}` : ''}
                            </p>
                          )}
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge className={`text-xs ${category.color}`}>
                          {category.icon}
                          <span className="ml-1">{category.label}</span>
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <Badge className={`text-xs ${severity.color}`}>
                          {severity.label}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <span className="text-sm text-muted-foreground">{issue.module || '-'}</span>
                      </TableCell>
                      <TableCell>
                        <Select
                          value={issue.status}
                          onValueChange={(v) => handleStatusChange(issue.issue_code, v)}
                          disabled={updatingIssue !== null}
                        >
                          <SelectTrigger className="h-8 w-[110px]">
                            {updatingIssue === issue.issue_code ? (
                              <Loader2 className="h-4 w-4 animate-spin" />
                            ) : (
                              <Badge className={`text-xs ${status.color}`}>
                                {status.label}
                              </Badge>
                            )}
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="open">Open</SelectItem>
                            <SelectItem value="in_progress">In Progress</SelectItem>
                            <SelectItem value="resolved">Resolved</SelectItem>
                            <SelectItem value="wont_fix">Won't Fix</SelectItem>
                            <SelectItem value="duplicate">Duplicate</SelectItem>
                          </SelectContent>
                        </Select>
                      </TableCell>
                      <TableCell>
                        {issue.related_task_id && (
                          <Link href={`/wbs-dashboard/tasks?search=${issue.related_task_id}`}>
                            <Button variant="ghost" size="sm">
                              <FileCode className="h-4 w-4" />
                            </Button>
                          </Link>
                        )}
                      </TableCell>
                    </TableRow>
                  )
                })}
              </TableBody>
            </Table>

            {issues.length === 0 && (
              <div className="text-center py-12">
                <Bug className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                <p className="text-muted-foreground">No issues found</p>
                <p className="text-sm text-muted-foreground mt-1">
                  Issues will appear here as they are discovered
                </p>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  )
}
