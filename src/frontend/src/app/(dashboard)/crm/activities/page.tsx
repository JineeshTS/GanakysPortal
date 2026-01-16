'use client'

import { useState, useEffect } from 'react'
import { useApi } from '@/hooks/use-api'
import { PageHeader } from '@/components/layout/page-header'
import { StatCard } from '@/components/layout/stat-card'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { formatDate, formatTime, formatRelativeTime } from '@/lib/format'
import {
  Plus,
  Search,
  Phone,
  Mail,
  Calendar,
  Users,
  Filter,
  Edit,
  Trash2,
  Loader2,
  MessageSquare,
  Video,
  Clock,
  CheckCircle2,
  XCircle,
  AlertCircle,
  User,
  Building2,
  FileText,
  MoreHorizontal,
} from 'lucide-react'

// Activity types
type ActivityType = 'call' | 'email' | 'meeting' | 'task' | 'note'
type ActivityStatus = 'scheduled' | 'completed' | 'cancelled' | 'overdue'

interface Activity {
  id: string
  type: ActivityType
  subject: string
  description?: string
  contact_name: string
  company_name?: string
  lead_id?: string
  opportunity_id?: string
  scheduled_at: string
  completed_at?: string
  duration?: number // in minutes
  status: ActivityStatus
  outcome?: string
  assigned_to?: string
  created_at: string
  updated_at: string
}

// Activity type configuration
const activityTypeConfig: Record<ActivityType, { label: string; icon: React.ElementType; color: string }> = {
  call: { label: 'Call', icon: Phone, color: 'bg-blue-100 text-blue-800' },
  email: { label: 'Email', icon: Mail, color: 'bg-purple-100 text-purple-800' },
  meeting: { label: 'Meeting', icon: Video, color: 'bg-green-100 text-green-800' },
  task: { label: 'Task', icon: CheckCircle2, color: 'bg-yellow-100 text-yellow-800' },
  note: { label: 'Note', icon: FileText, color: 'bg-gray-100 text-gray-800' },
}

// Activity status configuration
const statusConfig: Record<ActivityStatus, { label: string; color: string; icon: React.ElementType }> = {
  scheduled: { label: 'Scheduled', color: 'bg-blue-100 text-blue-800', icon: Clock },
  completed: { label: 'Completed', color: 'bg-green-100 text-green-800', icon: CheckCircle2 },
  cancelled: { label: 'Cancelled', color: 'bg-gray-100 text-gray-800', icon: XCircle },
  overdue: { label: 'Overdue', color: 'bg-red-100 text-red-800', icon: AlertCircle },
}

// Mock data
const mockActivities: Activity[] = [
  {
    id: '1',
    type: 'call',
    subject: 'Initial Discovery Call',
    description: 'Discuss ERP requirements and budget',
    contact_name: 'Rajesh Kumar',
    company_name: 'Tech Solutions Pvt Ltd',
    lead_id: 'lead-1',
    scheduled_at: '2026-01-16T10:00:00',
    duration: 30,
    status: 'scheduled',
    assigned_to: 'user-1',
    created_at: '2026-01-15T09:00:00',
    updated_at: '2026-01-15T09:00:00',
  },
  {
    id: '2',
    type: 'email',
    subject: 'Proposal Follow-up',
    description: 'Send updated proposal with revised pricing',
    contact_name: 'Priya Sharma',
    company_name: 'Global Mart India',
    lead_id: 'lead-2',
    scheduled_at: '2026-01-15T14:00:00',
    completed_at: '2026-01-15T14:30:00',
    status: 'completed',
    outcome: 'Proposal sent, awaiting response',
    assigned_to: 'user-1',
    created_at: '2026-01-14T11:00:00',
    updated_at: '2026-01-15T14:30:00',
  },
  {
    id: '3',
    type: 'meeting',
    subject: 'Product Demo - HRMS Module',
    description: 'Demonstrate HRMS features to HR team',
    contact_name: 'Amit Patel',
    company_name: 'Innovate Tech Systems',
    lead_id: 'lead-3',
    scheduled_at: '2026-01-17T11:00:00',
    duration: 60,
    status: 'scheduled',
    assigned_to: 'user-2',
    created_at: '2026-01-10T14:00:00',
    updated_at: '2026-01-10T14:00:00',
  },
  {
    id: '4',
    type: 'call',
    subject: 'Contract Negotiation',
    description: 'Discuss final pricing and terms',
    contact_name: 'Sneha Reddy',
    company_name: 'Bharat Finance Ltd',
    opportunity_id: 'opp-1',
    scheduled_at: '2026-01-14T15:00:00',
    completed_at: '2026-01-14T15:45:00',
    duration: 45,
    status: 'completed',
    outcome: 'Agreed on 15% discount for 3-year commitment',
    assigned_to: 'user-1',
    created_at: '2026-01-12T09:00:00',
    updated_at: '2026-01-14T15:45:00',
  },
  {
    id: '5',
    type: 'task',
    subject: 'Prepare Custom Quote',
    description: 'Create customized pricing for 100 users',
    contact_name: 'Vikram Singh',
    company_name: 'Sunrise Industries',
    lead_id: 'lead-5',
    scheduled_at: '2026-01-13T17:00:00',
    status: 'overdue',
    assigned_to: 'user-1',
    created_at: '2026-01-11T10:00:00',
    updated_at: '2026-01-11T10:00:00',
  },
  {
    id: '6',
    type: 'note',
    subject: 'Meeting Notes - Requirements Discussion',
    description: 'Key requirements: Payroll integration, GST compliance, employee self-service portal',
    contact_name: 'Meera Nair',
    company_name: 'Coastal Exports',
    lead_id: 'lead-6',
    scheduled_at: '2026-01-12T12:00:00',
    completed_at: '2026-01-12T12:00:00',
    status: 'completed',
    assigned_to: 'user-2',
    created_at: '2026-01-12T12:00:00',
    updated_at: '2026-01-12T12:00:00',
  },
  {
    id: '7',
    type: 'meeting',
    subject: 'Quarterly Business Review',
    description: 'Review implementation progress and roadmap',
    contact_name: 'Arjun Mehta',
    company_name: 'Quick Retail Solutions',
    scheduled_at: '2026-01-20T10:00:00',
    duration: 90,
    status: 'scheduled',
    assigned_to: 'user-1',
    created_at: '2026-01-08T08:00:00',
    updated_at: '2026-01-08T08:00:00',
  },
  {
    id: '8',
    type: 'email',
    subject: 'Send Product Brochure',
    description: 'Share detailed product information and case studies',
    contact_name: 'Kavita Desai',
    company_name: 'Precision Manufacturing',
    lead_id: 'lead-8',
    scheduled_at: '2026-01-15T09:00:00',
    status: 'cancelled',
    assigned_to: 'user-2',
    created_at: '2026-01-05T10:00:00',
    updated_at: '2026-01-14T16:00:00',
  },
]

// Add/Edit Activity Dialog
function ActivityDialog({
  open,
  onOpenChange,
  activity,
  onSave,
}: {
  open: boolean
  onOpenChange: (open: boolean) => void
  activity: Activity | null
  onSave: (activity: Activity) => void
}) {
  const api = useApi()
  const [formData, setFormData] = useState({
    type: 'call' as ActivityType,
    subject: '',
    description: '',
    contact_name: '',
    company_name: '',
    scheduled_at: '',
    scheduled_time: '',
    duration: 30,
    status: 'scheduled' as ActivityStatus,
    outcome: '',
  })
  const [isSubmitting, setIsSubmitting] = useState(false)

  useEffect(() => {
    if (activity) {
      const scheduledDate = new Date(activity.scheduled_at)
      setFormData({
        type: activity.type,
        subject: activity.subject,
        description: activity.description || '',
        contact_name: activity.contact_name,
        company_name: activity.company_name || '',
        scheduled_at: scheduledDate.toISOString().split('T')[0],
        scheduled_time: scheduledDate.toTimeString().slice(0, 5),
        duration: activity.duration || 30,
        status: activity.status,
        outcome: activity.outcome || '',
      })
    } else {
      const now = new Date()
      now.setHours(now.getHours() + 1, 0, 0, 0)
      setFormData({
        type: 'call',
        subject: '',
        description: '',
        contact_name: '',
        company_name: '',
        scheduled_at: now.toISOString().split('T')[0],
        scheduled_time: now.toTimeString().slice(0, 5),
        duration: 30,
        status: 'scheduled',
        outcome: '',
      })
    }
  }, [activity, open])

  const handleSubmit = async () => {
    if (!formData.subject || !formData.contact_name) return

    setIsSubmitting(true)
    try {
      const scheduledAt = `${formData.scheduled_at}T${formData.scheduled_time}:00`
      const payload = {
        type: formData.type,
        subject: formData.subject,
        description: formData.description || null,
        contact_name: formData.contact_name,
        company_name: formData.company_name || null,
        scheduled_at: scheduledAt,
        duration: formData.duration,
        status: formData.status,
        outcome: formData.outcome || null,
      }

      let response
      if (activity) {
        response = await api.put(`/crm/activities/${activity.id}`, payload)
      } else {
        response = await api.post('/crm/activities', payload)
      }

      if (response) {
        onSave(response as Activity)
        onOpenChange(false)
      }
    } catch (error) {
      console.error('Failed to save activity:', error)
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[600px]">
        <DialogHeader>
          <DialogTitle>{activity ? 'Edit Activity' : 'Schedule Activity'}</DialogTitle>
          <DialogDescription>
            {activity ? 'Update activity details' : 'Schedule a new activity with a contact'}
          </DialogDescription>
        </DialogHeader>
        <div className="grid gap-4 py-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="type">Activity Type</Label>
              <Select
                value={formData.type}
                onValueChange={(value) => setFormData({ ...formData, type: value as ActivityType })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select type" />
                </SelectTrigger>
                <SelectContent>
                  {Object.entries(activityTypeConfig).map(([value, { label }]) => (
                    <SelectItem key={value} value={value}>{label}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="status">Status</Label>
              <Select
                value={formData.status}
                onValueChange={(value) => setFormData({ ...formData, status: value as ActivityStatus })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select status" />
                </SelectTrigger>
                <SelectContent>
                  {Object.entries(statusConfig).map(([value, { label }]) => (
                    <SelectItem key={value} value={value}>{label}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
          <div className="space-y-2">
            <Label htmlFor="subject">Subject *</Label>
            <Input
              id="subject"
              placeholder="Discovery Call with Tech Solutions"
              value={formData.subject}
              onChange={(e) => setFormData({ ...formData, subject: e.target.value })}
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="contact_name">Contact Name *</Label>
              <Input
                id="contact_name"
                placeholder="Rajesh Kumar"
                value={formData.contact_name}
                onChange={(e) => setFormData({ ...formData, contact_name: e.target.value })}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="company_name">Company Name</Label>
              <Input
                id="company_name"
                placeholder="Tech Solutions Pvt Ltd"
                value={formData.company_name}
                onChange={(e) => setFormData({ ...formData, company_name: e.target.value })}
              />
            </div>
          </div>
          <div className="grid grid-cols-3 gap-4">
            <div className="space-y-2">
              <Label htmlFor="scheduled_at">Date</Label>
              <Input
                id="scheduled_at"
                type="date"
                value={formData.scheduled_at}
                onChange={(e) => setFormData({ ...formData, scheduled_at: e.target.value })}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="scheduled_time">Time</Label>
              <Input
                id="scheduled_time"
                type="time"
                value={formData.scheduled_time}
                onChange={(e) => setFormData({ ...formData, scheduled_time: e.target.value })}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="duration">Duration (min)</Label>
              <Input
                id="duration"
                type="number"
                min="5"
                step="5"
                value={formData.duration}
                onChange={(e) => setFormData({ ...formData, duration: parseInt(e.target.value) || 30 })}
              />
            </div>
          </div>
          <div className="space-y-2">
            <Label htmlFor="description">Description</Label>
            <Input
              id="description"
              placeholder="Notes about this activity..."
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            />
          </div>
          {formData.status === 'completed' && (
            <div className="space-y-2">
              <Label htmlFor="outcome">Outcome</Label>
              <Input
                id="outcome"
                placeholder="What was the result of this activity?"
                value={formData.outcome}
                onChange={(e) => setFormData({ ...formData, outcome: e.target.value })}
              />
            </div>
          )}
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)} disabled={isSubmitting}>
            Cancel
          </Button>
          <Button onClick={handleSubmit} disabled={isSubmitting || !formData.subject || !formData.contact_name}>
            {isSubmitting ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                {activity ? 'Updating...' : 'Scheduling...'}
              </>
            ) : (
              activity ? 'Update Activity' : 'Schedule Activity'
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

// Timeline Item Component
function TimelineItem({ activity }: { activity: Activity }) {
  const TypeIcon = activityTypeConfig[activity.type].icon
  const StatusIcon = statusConfig[activity.status].icon

  return (
    <div className="flex gap-4 pb-6 last:pb-0">
      <div className="flex flex-col items-center">
        <div className={`p-2 rounded-full ${activityTypeConfig[activity.type].color}`}>
          <TypeIcon className="h-4 w-4" />
        </div>
        <div className="w-0.5 bg-border flex-1 mt-2" />
      </div>
      <div className="flex-1 pb-2">
        <div className="flex items-start justify-between">
          <div>
            <p className="font-medium">{activity.subject}</p>
            <div className="flex items-center gap-2 mt-1 text-sm text-muted-foreground">
              <User className="h-3 w-3" />
              <span>{activity.contact_name}</span>
              {activity.company_name && (
                <>
                  <span>at</span>
                  <Building2 className="h-3 w-3" />
                  <span>{activity.company_name}</span>
                </>
              )}
            </div>
          </div>
          <Badge className={statusConfig[activity.status].color}>
            <StatusIcon className="h-3 w-3 mr-1" />
            {statusConfig[activity.status].label}
          </Badge>
        </div>
        {activity.description && (
          <p className="text-sm text-muted-foreground mt-2">{activity.description}</p>
        )}
        {activity.outcome && (
          <div className="mt-2 p-2 bg-green-50 rounded-md text-sm">
            <span className="font-medium text-green-700">Outcome: </span>
            <span className="text-green-600">{activity.outcome}</span>
          </div>
        )}
        <div className="flex items-center gap-4 mt-2 text-xs text-muted-foreground">
          <div className="flex items-center gap-1">
            <Calendar className="h-3 w-3" />
            <span>{formatDate(activity.scheduled_at)}</span>
          </div>
          <div className="flex items-center gap-1">
            <Clock className="h-3 w-3" />
            <span>{formatTime(activity.scheduled_at)}</span>
          </div>
          {activity.duration && (
            <span>{activity.duration} min</span>
          )}
        </div>
      </div>
    </div>
  )
}

export default function ActivitiesPage() {
  const api = useApi()
  const [searchQuery, setSearchQuery] = useState('')
  const [typeFilter, setTypeFilter] = useState<string>('all')
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [activeTab, setActiveTab] = useState('list')
  const [activities, setActivities] = useState<Activity[]>(mockActivities)
  const [loading, setLoading] = useState(true)

  // Calculate stats
  const today = new Date().toISOString().split('T')[0]
  const stats = {
    totalActivities: activities.length,
    todayActivities: activities.filter(a => a.scheduled_at.startsWith(today)).length,
    completedThisWeek: activities.filter(a => a.status === 'completed').length,
    overdueActivities: activities.filter(a => a.status === 'overdue').length,
    scheduledCalls: activities.filter(a => a.type === 'call' && a.status === 'scheduled').length,
  }

  // Dialogs state
  const [addDialogOpen, setAddDialogOpen] = useState(false)
  const [editDialogOpen, setEditDialogOpen] = useState(false)
  const [selectedActivity, setSelectedActivity] = useState<Activity | null>(null)

  // Fetch activities from API
  useEffect(() => {
    const fetchData = async () => {
      setLoading(true)
      try {
        const response = await api.get('/crm/activities?limit=100')
        if (response?.data && Array.isArray(response.data)) {
          setActivities(response.data.length > 0 ? response.data : mockActivities)
        }
      } catch (error) {
        console.error('Failed to fetch activities:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  // Filter activities
  const filteredActivities = activities.filter((activity) => {
    const matchesSearch = !searchQuery ||
      activity.subject.toLowerCase().includes(searchQuery.toLowerCase()) ||
      activity.contact_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      activity.company_name?.toLowerCase().includes(searchQuery.toLowerCase())

    const matchesType = typeFilter === 'all' || activity.type === typeFilter
    const matchesStatus = statusFilter === 'all' || activity.status === statusFilter

    return matchesSearch && matchesType && matchesStatus
  })

  // Sort by scheduled date (most recent first for timeline)
  const sortedActivities = [...filteredActivities].sort(
    (a, b) => new Date(b.scheduled_at).getTime() - new Date(a.scheduled_at).getTime()
  )

  // Upcoming activities (scheduled, not overdue)
  const upcomingActivities = filteredActivities
    .filter(a => a.status === 'scheduled')
    .sort((a, b) => new Date(a.scheduled_at).getTime() - new Date(b.scheduled_at).getTime())

  const handleEditActivity = (activity: Activity) => {
    setSelectedActivity(activity)
    setEditDialogOpen(true)
  }

  const handleActivitySaved = (savedActivity: Activity) => {
    if (selectedActivity) {
      setActivities(prev => prev.map(a => a.id === savedActivity.id ? savedActivity : a))
    } else {
      setActivities(prev => [savedActivity, ...prev])
    }
    setSelectedActivity(null)
  }

  const handleDeleteActivity = async (activity: Activity) => {
    if (!confirm('Are you sure you want to delete this activity?')) return

    try {
      const success = await api.delete(`/crm/activities/${activity.id}`)
      if (success) {
        setActivities(prev => prev.filter(a => a.id !== activity.id))
      }
    } catch (error) {
      console.error('Failed to delete activity:', error)
    }
  }

  const handleMarkComplete = async (activity: Activity) => {
    try {
      const payload = {
        ...activity,
        status: 'completed' as ActivityStatus,
        completed_at: new Date().toISOString(),
      }
      const response = await api.put(`/crm/activities/${activity.id}`, payload)
      if (response) {
        setActivities(prev => prev.map(a => a.id === activity.id ? { ...a, ...payload } : a))
      }
    } catch (error) {
      console.error('Failed to mark activity as complete:', error)
    }
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Activity Tracking"
        description="Log and track all customer interactions"
        breadcrumbs={[
          { label: 'CRM', href: '/crm' },
          { label: 'Activities' },
        ]}
        actions={
          <Button onClick={() => setAddDialogOpen(true)}>
            <Plus className="h-4 w-4 mr-2" />
            Log Activity
          </Button>
        }
      />

      {/* Stats */}
      {loading ? (
        <div className="flex items-center justify-center h-24">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-5">
          <StatCard
            title="Total Activities"
            value={stats.totalActivities}
            icon={MessageSquare}
            description="All time"
          />
          <StatCard
            title="Today"
            value={stats.todayActivities}
            icon={Calendar}
            description="Scheduled today"
          />
          <StatCard
            title="Completed"
            value={stats.completedThisWeek}
            icon={CheckCircle2}
            description="This week"
          />
          <StatCard
            title="Overdue"
            value={stats.overdueActivities}
            icon={AlertCircle}
            description="Need attention"
            trend={stats.overdueActivities > 0 ? { value: -stats.overdueActivities, type: 'decrease' } : undefined}
          />
          <StatCard
            title="Scheduled Calls"
            value={stats.scheduledCalls}
            icon={Phone}
            description="Upcoming"
          />
        </div>
      )}

      {/* Filters */}
      <Card>
        <CardContent className="p-4">
          <div className="flex flex-wrap gap-4">
            <div className="relative flex-1 min-w-[200px]">
              <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search activities..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-8"
              />
            </div>
            <Select value={typeFilter} onValueChange={setTypeFilter}>
              <SelectTrigger className="w-[150px]">
                <Filter className="h-4 w-4 mr-2" />
                <SelectValue placeholder="Type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Types</SelectItem>
                {Object.entries(activityTypeConfig).map(([value, { label }]) => (
                  <SelectItem key={value} value={value}>{label}</SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-[150px]">
                <Filter className="h-4 w-4 mr-2" />
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                {Object.entries(statusConfig).map(([value, { label }]) => (
                  <SelectItem key={value} value={value}>{label}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Main Content */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="list">List View</TabsTrigger>
          <TabsTrigger value="timeline">Timeline</TabsTrigger>
          <TabsTrigger value="upcoming">Upcoming</TabsTrigger>
        </TabsList>

        {/* List View */}
        <TabsContent value="list" className="mt-4">
          <Card>
            <CardContent className="p-0">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Type</TableHead>
                    <TableHead>Subject</TableHead>
                    <TableHead>Contact</TableHead>
                    <TableHead>Scheduled</TableHead>
                    <TableHead>Duration</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredActivities.length === 0 ? (
                    <TableRow>
                      <TableCell colSpan={7} className="text-center py-8 text-muted-foreground">
                        No activities found
                      </TableCell>
                    </TableRow>
                  ) : (
                    filteredActivities.map((activity) => {
                      const TypeIcon = activityTypeConfig[activity.type].icon
                      return (
                        <TableRow key={activity.id}>
                          <TableCell>
                            <div className={`inline-flex items-center gap-1.5 px-2 py-1 rounded-md ${activityTypeConfig[activity.type].color}`}>
                              <TypeIcon className="h-3 w-3" />
                              <span className="text-xs">{activityTypeConfig[activity.type].label}</span>
                            </div>
                          </TableCell>
                          <TableCell>
                            <p className="font-medium">{activity.subject}</p>
                            {activity.description && (
                              <p className="text-xs text-muted-foreground line-clamp-1">{activity.description}</p>
                            )}
                          </TableCell>
                          <TableCell>
                            <div className="text-sm">
                              <p>{activity.contact_name}</p>
                              {activity.company_name && (
                                <p className="text-xs text-muted-foreground">{activity.company_name}</p>
                              )}
                            </div>
                          </TableCell>
                          <TableCell>
                            <div className="text-sm">
                              <p>{formatDate(activity.scheduled_at)}</p>
                              <p className="text-xs text-muted-foreground">{formatTime(activity.scheduled_at)}</p>
                            </div>
                          </TableCell>
                          <TableCell>
                            {activity.duration ? `${activity.duration} min` : '-'}
                          </TableCell>
                          <TableCell>
                            <Badge className={statusConfig[activity.status].color}>
                              {statusConfig[activity.status].label}
                            </Badge>
                          </TableCell>
                          <TableCell className="text-right">
                            <div className="flex items-center justify-end gap-1">
                              {activity.status === 'scheduled' && (
                                <Button
                                  variant="ghost"
                                  size="icon"
                                  onClick={() => handleMarkComplete(activity)}
                                  title="Mark Complete"
                                >
                                  <CheckCircle2 className="h-4 w-4 text-green-500" />
                                </Button>
                              )}
                              <Button variant="ghost" size="icon" onClick={() => handleEditActivity(activity)}>
                                <Edit className="h-4 w-4" />
                              </Button>
                              <Button variant="ghost" size="icon" onClick={() => handleDeleteActivity(activity)}>
                                <Trash2 className="h-4 w-4 text-red-500" />
                              </Button>
                            </div>
                          </TableCell>
                        </TableRow>
                      )
                    })
                  )}
                </TableBody>
                </Table>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Timeline View */}
        <TabsContent value="timeline" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Activity Timeline</CardTitle>
            </CardHeader>
            <CardContent>
              {sortedActivities.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  No activities found
                </div>
              ) : (
                <div className="space-y-0">
                  {sortedActivities.map((activity) => (
                    <TimelineItem key={activity.id} activity={activity} />
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Upcoming View */}
        <TabsContent value="upcoming" className="mt-4">
          <div className="grid gap-4 md:grid-cols-2">
            {/* Today's Activities */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg flex items-center gap-2">
                  <Calendar className="h-5 w-5" />
                  Today
                </CardTitle>
              </CardHeader>
              <CardContent>
                {upcomingActivities.filter(a => a.scheduled_at.startsWith(today)).length === 0 ? (
                  <p className="text-muted-foreground text-sm">No activities scheduled for today</p>
                ) : (
                  <div className="space-y-3">
                    {upcomingActivities
                      .filter(a => a.scheduled_at.startsWith(today))
                      .map((activity) => {
                        const TypeIcon = activityTypeConfig[activity.type].icon
                        return (
                          <div
                            key={activity.id}
                            className="flex items-center gap-3 p-3 bg-muted/50 rounded-lg"
                          >
                            <div className={`p-2 rounded-full ${activityTypeConfig[activity.type].color}`}>
                              <TypeIcon className="h-4 w-4" />
                            </div>
                            <div className="flex-1 min-w-0">
                              <p className="font-medium text-sm truncate">{activity.subject}</p>
                              <p className="text-xs text-muted-foreground">
                                {formatTime(activity.scheduled_at)} - {activity.contact_name}
                              </p>
                            </div>
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleMarkComplete(activity)}
                            >
                              <CheckCircle2 className="h-4 w-4" />
                            </Button>
                          </div>
                        )
                      })}
                  </div>
                )}
              </CardContent>
            </Card>

            {/* This Week */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg flex items-center gap-2">
                  <Clock className="h-5 w-5" />
                  This Week
                </CardTitle>
              </CardHeader>
              <CardContent>
                {upcomingActivities.filter(a => !a.scheduled_at.startsWith(today)).length === 0 ? (
                  <p className="text-muted-foreground text-sm">No upcoming activities this week</p>
                ) : (
                  <div className="space-y-3">
                    {upcomingActivities
                      .filter(a => !a.scheduled_at.startsWith(today))
                      .slice(0, 5)
                      .map((activity) => {
                        const TypeIcon = activityTypeConfig[activity.type].icon
                        return (
                          <div
                            key={activity.id}
                            className="flex items-center gap-3 p-3 bg-muted/50 rounded-lg"
                          >
                            <div className={`p-2 rounded-full ${activityTypeConfig[activity.type].color}`}>
                              <TypeIcon className="h-4 w-4" />
                            </div>
                            <div className="flex-1 min-w-0">
                              <p className="font-medium text-sm truncate">{activity.subject}</p>
                              <p className="text-xs text-muted-foreground">
                                {formatDate(activity.scheduled_at)} at {formatTime(activity.scheduled_at)}
                              </p>
                            </div>
                          </div>
                        )
                      })}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>

      {/* Dialogs */}
      <ActivityDialog
        open={addDialogOpen}
        onOpenChange={setAddDialogOpen}
        activity={null}
        onSave={handleActivitySaved}
      />
      <ActivityDialog
        open={editDialogOpen}
        onOpenChange={(open) => {
          setEditDialogOpen(open)
          if (!open) setSelectedActivity(null)
        }}
        activity={selectedActivity}
        onSave={handleActivitySaved}
      />
    </div>
  )
}
