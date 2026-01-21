'use client'

import { useState, useEffect, useCallback } from 'react'
import Link from 'next/link'
import { PageHeader } from '@/components/layout/page-header'
import { useAuth } from "@/hooks/use-auth"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  Bell,
  ChevronLeft,
  Search,
  RefreshCw,
  Loader2,
  Send,
  Plus,
  CheckCircle,
  XCircle,
  Clock,
  Users,
  User,
  Building,
  Eye,
  BarChart3,
  Megaphone,
  AlertCircle,
  Info,
} from 'lucide-react'

interface PushNotification {
  id: string
  title: string
  body: string
  notification_type: 'system' | 'alert' | 'workflow' | 'reminder' | 'announcement' | 'promotional'
  target_type: 'all' | 'user' | 'department' | 'role'
  target_id: string | null
  data: Record<string, any>
  priority: 'low' | 'normal' | 'high' | 'urgent'
  sent_count: number
  delivered_count: number
  read_count: number
  failed_count: number
  status: 'draft' | 'pending' | 'sending' | 'sent' | 'failed'
  scheduled_at: string | null
  sent_at: string | null
  created_at: string
  created_by_name: string
}

const typeConfig: Record<string, { icon: React.ReactNode; color: string; label: string }> = {
  system: { icon: <Info className="h-4 w-4" />, color: 'bg-blue-100 text-blue-800', label: 'System' },
  alert: { icon: <AlertCircle className="h-4 w-4" />, color: 'bg-red-100 text-red-800', label: 'Alert' },
  workflow: { icon: <Clock className="h-4 w-4" />, color: 'bg-purple-100 text-purple-800', label: 'Workflow' },
  reminder: { icon: <Bell className="h-4 w-4" />, color: 'bg-yellow-100 text-yellow-800', label: 'Reminder' },
  announcement: { icon: <Megaphone className="h-4 w-4" />, color: 'bg-green-100 text-green-800', label: 'Announcement' },
  promotional: { icon: <BarChart3 className="h-4 w-4" />, color: 'bg-orange-100 text-orange-800', label: 'Promotional' },
}

const statusConfig: Record<string, { color: string; label: string }> = {
  draft: { color: 'bg-gray-100 text-gray-800', label: 'Draft' },
  pending: { color: 'bg-yellow-100 text-yellow-800', label: 'Pending' },
  sending: { color: 'bg-blue-100 text-blue-800', label: 'Sending' },
  sent: { color: 'bg-green-100 text-green-800', label: 'Sent' },
  failed: { color: 'bg-red-100 text-red-800', label: 'Failed' },
}

const targetConfig: Record<string, { icon: React.ReactNode; label: string }> = {
  all: { icon: <Users className="h-4 w-4" />, label: 'All Users' },
  user: { icon: <User className="h-4 w-4" />, label: 'Specific User' },
  department: { icon: <Building className="h-4 w-4" />, label: 'Department' },
  role: { icon: <Users className="h-4 w-4" />, label: 'Role' },
}

export default function MobileNotificationsPage() {
  const [isLoading, setIsLoading] = useState(true)
  const [notifications, setNotifications] = useState<PushNotification[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [search, setSearch] = useState('')
  const [typeFilter, setTypeFilter] = useState<string>('all')
  const [statusFilter, setStatusFilter] = useState<string>('all')

  const [createDialogOpen, setCreateDialogOpen] = useState(false)
  const [detailDialogOpen, setDetailDialogOpen] = useState(false)
  const [selectedNotification, setSelectedNotification] = useState<PushNotification | null>(null)
  const [isSending, setIsSending] = useState(false)

  // Form state
  const [formData, setFormData] = useState({
    title: '',
    body: '',
    notification_type: 'announcement',
    target_type: 'all',
    priority: 'normal',
  })

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || '/api/v1'

  const fetchNotifications = useCallback(async () => {
    setIsLoading(true)
    try {
      const params = new URLSearchParams()
      params.set('page', page.toString())
      params.set('limit', '20')
      if (typeFilter !== 'all') params.set('notification_type', typeFilter)

      const res = await fetchWithAuth(`${apiUrl}/mobile/notifications?${params.toString()}`)
      if (res.ok) {
        const data = await res.json()
        setNotifications(data.data || [])
        setTotal(data.meta?.total || 0)
      }
    } catch (err) {
      console.error('Failed to fetch notifications:', err)
    } finally {
      setIsLoading(false)
    }
  }, [apiUrl, page, typeFilter])

  useEffect(() => {
    fetchNotifications()
  }, [fetchNotifications])

  const handleSendNotification = async () => {
    setIsSending(true)
    try {
      const res = await fetchWithAuth(`${apiUrl}/mobile/notifications`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      })
      if (res.ok) {
        setCreateDialogOpen(false)
        setFormData({ title: '', body: '', notification_type: 'announcement', target_type: 'all', priority: 'normal' })
        fetchNotifications()
      }
    } catch (err) {
      console.error('Failed to send notification:', err)
    } finally {
      setIsSending(false)
    }
  }

  // Mock data for demo
  const mockNotifications: PushNotification[] = [
    { id: '1', title: 'New Leave Request', body: 'You have a new leave request pending approval from Rahul Sharma', notification_type: 'workflow', target_type: 'user', target_id: '123', data: {}, priority: 'high', sent_count: 1, delivered_count: 1, read_count: 1, failed_count: 0, status: 'sent', scheduled_at: null, sent_at: '2026-01-17T10:30:00Z', created_at: '2026-01-17T10:30:00Z', created_by_name: 'System' },
    { id: '2', title: 'Monthly Report Available', body: 'The December 2025 financial report is now available for review', notification_type: 'announcement', target_type: 'all', target_id: null, data: {}, priority: 'normal', sent_count: 156, delivered_count: 142, read_count: 89, failed_count: 14, status: 'sent', scheduled_at: null, sent_at: '2026-01-15T09:00:00Z', created_at: '2026-01-15T09:00:00Z', created_by_name: 'Admin' },
    { id: '3', title: 'System Maintenance', body: 'Scheduled maintenance on Sunday 2:00 AM - 4:00 AM IST', notification_type: 'system', target_type: 'all', target_id: null, data: {}, priority: 'high', sent_count: 156, delivered_count: 150, read_count: 120, failed_count: 6, status: 'sent', scheduled_at: null, sent_at: '2026-01-14T18:00:00Z', created_at: '2026-01-14T18:00:00Z', created_by_name: 'System Admin' },
    { id: '4', title: 'Expense Report Reminder', body: 'Please submit your expense reports for January by end of day', notification_type: 'reminder', target_type: 'department', target_id: 'finance', data: {}, priority: 'normal', sent_count: 45, delivered_count: 43, read_count: 30, failed_count: 2, status: 'sent', scheduled_at: null, sent_at: '2026-01-13T08:00:00Z', created_at: '2026-01-13T08:00:00Z', created_by_name: 'Finance Manager' },
    { id: '5', title: 'Security Alert', body: 'Unusual login activity detected from a new device', notification_type: 'alert', target_type: 'user', target_id: '456', data: {}, priority: 'urgent', sent_count: 1, delivered_count: 1, read_count: 0, failed_count: 0, status: 'sent', scheduled_at: null, sent_at: '2026-01-17T11:00:00Z', created_at: '2026-01-17T11:00:00Z', created_by_name: 'Security System' },
  ]

  const displayNotifications = notifications.length > 0 ? notifications : mockNotifications

  // Stats
  const totalSent = mockNotifications.reduce((sum, n) => sum + n.sent_count, 0)
  const totalDelivered = mockNotifications.reduce((sum, n) => sum + n.delivered_count, 0)
  const totalRead = mockNotifications.reduce((sum, n) => sum + n.read_count, 0)
  const deliveryRate = totalSent > 0 ? Math.round((totalDelivered / totalSent) * 100) : 0

  return (
    <div className="space-y-6">
      <PageHeader
        title="Push Notifications"
        description="Send and manage push notifications to mobile users"
        actions={
          <div className="flex gap-2">
            <Link href="/mobile">
              <Button variant="outline">
                <ChevronLeft className="h-4 w-4 mr-1" />
                Back
              </Button>
            </Link>
            <Button onClick={() => setCreateDialogOpen(true)}>
              <Plus className="h-4 w-4 mr-2" />
              Send Notification
            </Button>
          </div>
        }
      />

      {/* Stats */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-primary/10">
                <Send className="h-5 w-5 text-primary" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Total Sent</p>
                <p className="text-2xl font-bold">{totalSent.toLocaleString()}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-green-100">
                <CheckCircle className="h-5 w-5 text-green-600" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Delivered</p>
                <p className="text-2xl font-bold">{totalDelivered.toLocaleString()}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-blue-100">
                <Eye className="h-5 w-5 text-blue-600" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Read</p>
                <p className="text-2xl font-bold">{totalRead.toLocaleString()}</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-4">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-purple-100">
                <BarChart3 className="h-5 w-5 text-purple-600" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Delivery Rate</p>
                <p className="text-2xl font-bold">{deliveryRate}%</p>
              </div>
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
                  placeholder="Search notifications..."
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  className="pl-8"
                />
              </div>
            </div>
            <Select value={typeFilter} onValueChange={setTypeFilter}>
              <SelectTrigger className="w-[150px]">
                <SelectValue placeholder="Type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Types</SelectItem>
                <SelectItem value="system">System</SelectItem>
                <SelectItem value="alert">Alert</SelectItem>
                <SelectItem value="workflow">Workflow</SelectItem>
                <SelectItem value="reminder">Reminder</SelectItem>
                <SelectItem value="announcement">Announcement</SelectItem>
              </SelectContent>
            </Select>
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-[150px]">
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="sent">Sent</SelectItem>
                <SelectItem value="pending">Pending</SelectItem>
                <SelectItem value="failed">Failed</SelectItem>
              </SelectContent>
            </Select>
            <Button variant="outline" onClick={fetchNotifications} disabled={isLoading}>
              <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Loading */}
      {isLoading && (
        <Card className="p-8 flex items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <span className="ml-2">Loading notifications...</span>
        </Card>
      )}

      {/* Notifications Table */}
      {!isLoading && (
        <Card>
          <CardContent className="p-0">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Notification</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Target</TableHead>
                  <TableHead className="text-right">Sent</TableHead>
                  <TableHead className="text-right">Delivered</TableHead>
                  <TableHead className="text-right">Read</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Sent At</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {displayNotifications.map((notification) => {
                  const type = typeConfig[notification.notification_type] || typeConfig.system
                  const status = statusConfig[notification.status] || statusConfig.sent
                  const target = targetConfig[notification.target_type] || targetConfig.all

                  return (
                    <TableRow
                      key={notification.id}
                      className="cursor-pointer hover:bg-muted/50"
                      onClick={() => { setSelectedNotification(notification); setDetailDialogOpen(true); }}
                    >
                      <TableCell>
                        <div className="max-w-[300px]">
                          <p className="font-medium truncate">{notification.title}</p>
                          <p className="text-xs text-muted-foreground truncate">{notification.body}</p>
                        </div>
                      </TableCell>
                      <TableCell>
                        <Badge className={type.color}>
                          {type.icon}
                          <span className="ml-1">{type.label}</span>
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <div className="flex items-center gap-1 text-sm">
                          {target.icon}
                          <span>{target.label}</span>
                        </div>
                      </TableCell>
                      <TableCell className="text-right font-medium">{notification.sent_count}</TableCell>
                      <TableCell className="text-right text-green-600">{notification.delivered_count}</TableCell>
                      <TableCell className="text-right text-blue-600">{notification.read_count}</TableCell>
                      <TableCell>
                        <Badge className={status.color}>{status.label}</Badge>
                      </TableCell>
                      <TableCell className="text-sm text-muted-foreground">
                        {notification.sent_at ? new Date(notification.sent_at).toLocaleString() : '-'}
                      </TableCell>
                    </TableRow>
                  )
                })}
              </TableBody>
            </Table>

            {displayNotifications.length === 0 && (
              <div className="text-center py-12">
                <Bell className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                <p className="text-muted-foreground">No notifications found</p>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Create Notification Dialog */}
      <Dialog open={createDialogOpen} onOpenChange={setCreateDialogOpen}>
        <DialogContent className="sm:max-w-[500px]">
          <DialogHeader>
            <DialogTitle>Send Push Notification</DialogTitle>
            <DialogDescription>
              Send a notification to mobile app users
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div>
              <Label>Title</Label>
              <Input
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                placeholder="Notification title"
                className="mt-1"
              />
            </div>
            <div>
              <Label>Message</Label>
              <Textarea
                value={formData.body}
                onChange={(e) => setFormData({ ...formData, body: e.target.value })}
                placeholder="Notification message"
                className="mt-1"
                rows={3}
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label>Type</Label>
                <Select
                  value={formData.notification_type}
                  onValueChange={(v) => setFormData({ ...formData, notification_type: v })}
                >
                  <SelectTrigger className="mt-1">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="announcement">Announcement</SelectItem>
                    <SelectItem value="system">System</SelectItem>
                    <SelectItem value="alert">Alert</SelectItem>
                    <SelectItem value="reminder">Reminder</SelectItem>
                    <SelectItem value="workflow">Workflow</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div>
                <Label>Priority</Label>
                <Select
                  value={formData.priority}
                  onValueChange={(v) => setFormData({ ...formData, priority: v })}
                >
                  <SelectTrigger className="mt-1">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="low">Low</SelectItem>
                    <SelectItem value="normal">Normal</SelectItem>
                    <SelectItem value="high">High</SelectItem>
                    <SelectItem value="urgent">Urgent</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div>
              <Label>Target Audience</Label>
              <Select
                value={formData.target_type}
                onValueChange={(v) => setFormData({ ...formData, target_type: v })}
              >
                <SelectTrigger className="mt-1">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Users</SelectItem>
                  <SelectItem value="department">Department</SelectItem>
                  <SelectItem value="role">Role</SelectItem>
                  <SelectItem value="user">Specific User</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setCreateDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleSendNotification} disabled={isSending || !formData.title || !formData.body}>
              {isSending ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Sending...
                </>
              ) : (
                <>
                  <Send className="mr-2 h-4 w-4" />
                  Send Notification
                </>
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Detail Dialog */}
      <Dialog open={detailDialogOpen} onOpenChange={setDetailDialogOpen}>
        <DialogContent className="sm:max-w-[500px]">
          <DialogHeader>
            <DialogTitle>Notification Details</DialogTitle>
          </DialogHeader>
          {selectedNotification && (
            <div className="space-y-4 py-4">
              <div>
                <Label className="text-xs text-muted-foreground">Title</Label>
                <p className="font-medium">{selectedNotification.title}</p>
              </div>
              <div>
                <Label className="text-xs text-muted-foreground">Message</Label>
                <p className="text-sm">{selectedNotification.body}</p>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label className="text-xs text-muted-foreground">Type</Label>
                  <Badge className={typeConfig[selectedNotification.notification_type]?.color}>
                    {typeConfig[selectedNotification.notification_type]?.label}
                  </Badge>
                </div>
                <div>
                  <Label className="text-xs text-muted-foreground">Priority</Label>
                  <p className="text-sm capitalize">{selectedNotification.priority}</p>
                </div>
              </div>
              <div className="grid grid-cols-4 gap-4 pt-2 border-t">
                <div className="text-center">
                  <p className="text-2xl font-bold">{selectedNotification.sent_count}</p>
                  <p className="text-xs text-muted-foreground">Sent</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-green-600">{selectedNotification.delivered_count}</p>
                  <p className="text-xs text-muted-foreground">Delivered</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-blue-600">{selectedNotification.read_count}</p>
                  <p className="text-xs text-muted-foreground">Read</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-red-600">{selectedNotification.failed_count}</p>
                  <p className="text-xs text-muted-foreground">Failed</p>
                </div>
              </div>
              <div className="text-xs text-muted-foreground pt-2 border-t">
                <p>Created by: {selectedNotification.created_by_name}</p>
                <p>Sent at: {selectedNotification.sent_at ? new Date(selectedNotification.sent_at).toLocaleString() : 'Not sent'}</p>
              </div>
            </div>
          )}
          <DialogFooter>
            <Button variant="outline" onClick={() => setDetailDialogOpen(false)}>
              Close
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
