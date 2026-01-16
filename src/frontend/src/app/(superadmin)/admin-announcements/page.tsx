'use client'

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import { Switch } from '@/components/ui/switch'
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
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog'
import { useApi, useToast } from '@/hooks'
import {
  Megaphone,
  Plus,
  MoreHorizontal,
  Edit,
  Trash2,
  Eye,
  EyeOff,
  Calendar,
  Users,
  AlertCircle,
  Info,
  CheckCircle,
  AlertTriangle,
  Send,
  Clock,
  Loader2,
} from 'lucide-react'
import { format, formatDistanceToNow } from 'date-fns'

type AnnouncementType = 'info' | 'warning' | 'success' | 'critical'
type AnnouncementTarget = 'all' | 'admins' | 'specific_plans' | 'specific_tenants'

interface Announcement {
  id: string
  title: string
  content: string
  type: AnnouncementType
  target: AnnouncementTarget
  targetPlans?: string[]
  targetTenants?: string[]
  isActive: boolean
  isDismissible: boolean
  startsAt: Date
  expiresAt?: Date
  createdAt: Date
  createdBy: string
  viewCount: number
  dismissCount: number
}

// Mock announcements data
const mockAnnouncements: Announcement[] = [
  {
    id: '1',
    title: 'Scheduled Maintenance - January 20, 2026',
    content: 'We will be performing scheduled maintenance on January 20, 2026 from 2:00 AM to 4:00 AM IST. During this time, the platform may be temporarily unavailable.',
    type: 'warning',
    target: 'all',
    isActive: true,
    isDismissible: true,
    startsAt: new Date('2026-01-18'),
    expiresAt: new Date('2026-01-21'),
    createdAt: new Date('2026-01-14'),
    createdBy: 'Platform Admin',
    viewCount: 1250,
    dismissCount: 890,
  },
  {
    id: '2',
    title: 'New Feature: AI Document Processing',
    content: 'We are excited to announce our new AI-powered document processing feature. Extract data from invoices, receipts, and contracts automatically with 99% accuracy.',
    type: 'info',
    target: 'specific_plans',
    targetPlans: ['Professional', 'Enterprise'],
    isActive: true,
    isDismissible: true,
    startsAt: new Date('2026-01-10'),
    createdAt: new Date('2026-01-10'),
    createdBy: 'Platform Admin',
    viewCount: 2340,
    dismissCount: 1500,
  },
  {
    id: '3',
    title: 'Critical Security Update Required',
    content: 'A critical security patch has been applied to all accounts. Please review your security settings and enable MFA if you have not already.',
    type: 'critical',
    target: 'admins',
    isActive: true,
    isDismissible: false,
    startsAt: new Date('2026-01-12'),
    createdAt: new Date('2026-01-12'),
    createdBy: 'Security Team',
    viewCount: 450,
    dismissCount: 0,
  },
  {
    id: '4',
    title: 'Holiday Support Hours',
    content: 'Our support team will have limited availability from December 24-26 and December 31 - January 1. For urgent issues, please email critical-support@ganakys.com.',
    type: 'info',
    target: 'all',
    isActive: false,
    isDismissible: true,
    startsAt: new Date('2025-12-20'),
    expiresAt: new Date('2026-01-02'),
    createdAt: new Date('2025-12-15'),
    createdBy: 'Platform Admin',
    viewCount: 3200,
    dismissCount: 2800,
  },
  {
    id: '5',
    title: 'GST Rate Update Completed',
    content: 'The GST rate tables have been updated to reflect the latest government notifications. All calculations will automatically use the new rates.',
    type: 'success',
    target: 'all',
    isActive: true,
    isDismissible: true,
    startsAt: new Date('2026-01-01'),
    createdAt: new Date('2026-01-01'),
    createdBy: 'Compliance Team',
    viewCount: 1800,
    dismissCount: 1200,
  },
]

const typeConfig: Record<AnnouncementType, { icon: React.ElementType; color: string; bgColor: string }> = {
  info: { icon: Info, color: 'text-blue-600', bgColor: 'bg-blue-100' },
  warning: { icon: AlertTriangle, color: 'text-yellow-600', bgColor: 'bg-yellow-100' },
  success: { icon: CheckCircle, color: 'text-green-600', bgColor: 'bg-green-100' },
  critical: { icon: AlertCircle, color: 'text-red-600', bgColor: 'bg-red-100' },
}

const targetLabels: Record<AnnouncementTarget, string> = {
  all: 'All Users',
  admins: 'Tenant Admins Only',
  specific_plans: 'Specific Plans',
  specific_tenants: 'Specific Tenants',
}

export default function AnnouncementsPage() {
  const [announcements, setAnnouncements] = useState(mockAnnouncements)
  const [createDialogOpen, setCreateDialogOpen] = useState(false)
  const [editingAnnouncement, setEditingAnnouncement] = useState<Announcement | null>(null)
  const [filterStatus, setFilterStatus] = useState<'all' | 'active' | 'inactive'>('all')
  const [filterType, setFilterType] = useState<AnnouncementType | 'all'>('all')
  const { showToast } = useToast()
  const deleteApi = useApi()

  // Delete state
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false)
  const [announcementToDelete, setAnnouncementToDelete] = useState<Announcement | null>(null)
  const [isDeleting, setIsDeleting] = useState(false)

  // New announcement form state
  const [formData, setFormData] = useState({
    title: '',
    content: '',
    type: 'info' as AnnouncementType,
    target: 'all' as AnnouncementTarget,
    isDismissible: true,
    startsAt: format(new Date(), 'yyyy-MM-dd'),
    expiresAt: '',
  })

  const filteredAnnouncements = announcements.filter(a => {
    if (filterStatus === 'active' && !a.isActive) return false
    if (filterStatus === 'inactive' && a.isActive) return false
    if (filterType !== 'all' && a.type !== filterType) return false
    return true
  })

  const handleCreate = () => {
    const newAnnouncement: Announcement = {
      id: Date.now().toString(),
      title: formData.title,
      content: formData.content,
      type: formData.type,
      target: formData.target,
      isActive: true,
      isDismissible: formData.isDismissible,
      startsAt: new Date(formData.startsAt),
      expiresAt: formData.expiresAt ? new Date(formData.expiresAt) : undefined,
      createdAt: new Date(),
      createdBy: 'Platform Admin',
      viewCount: 0,
      dismissCount: 0,
    }
    setAnnouncements([newAnnouncement, ...announcements])
    setCreateDialogOpen(false)
    resetForm()
  }

  const handleToggleActive = (id: string) => {
    setAnnouncements(announcements.map(a =>
      a.id === id ? { ...a, isActive: !a.isActive } : a
    ))
  }

  const handleDeleteClick = (announcement: Announcement) => {
    setAnnouncementToDelete(announcement)
    setDeleteDialogOpen(true)
  }

  const handleDeleteConfirm = async () => {
    if (!announcementToDelete) return
    setIsDeleting(true)
    try {
      await deleteApi.delete(`/superadmin/announcements/${announcementToDelete.id}`)
      setAnnouncements(announcements.filter(a => a.id !== announcementToDelete.id))
      setDeleteDialogOpen(false)
      setAnnouncementToDelete(null)
      showToast("success", "Announcement deleted successfully")
    } catch (error) {
      console.error("Failed to delete announcement:", error)
      showToast("error", "Failed to delete announcement")
    } finally {
      setIsDeleting(false)
    }
  }

  const resetForm = () => {
    setFormData({
      title: '',
      content: '',
      type: 'info',
      target: 'all',
      isDismissible: true,
      startsAt: format(new Date(), 'yyyy-MM-dd'),
      expiresAt: '',
    })
  }

  const activeCount = announcements.filter(a => a.isActive).length
  const totalViews = announcements.reduce((sum, a) => sum + a.viewCount, 0)

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Announcements</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Manage platform-wide announcements and notifications
          </p>
        </div>
        <Dialog open={createDialogOpen} onOpenChange={setCreateDialogOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              Create Announcement
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>Create New Announcement</DialogTitle>
              <DialogDescription>
                Create a new announcement to display to platform users
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="title">Title</Label>
                <Input
                  id="title"
                  placeholder="Announcement title"
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="content">Content</Label>
                <Textarea
                  id="content"
                  placeholder="Announcement content..."
                  rows={4}
                  value={formData.content}
                  onChange={(e) => setFormData({ ...formData, content: e.target.value })}
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Type</Label>
                  <Select
                    value={formData.type}
                    onValueChange={(value: AnnouncementType) => setFormData({ ...formData, type: value })}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="info">
                        <div className="flex items-center gap-2">
                          <Info className="h-4 w-4 text-blue-600" />
                          Information
                        </div>
                      </SelectItem>
                      <SelectItem value="warning">
                        <div className="flex items-center gap-2">
                          <AlertTriangle className="h-4 w-4 text-yellow-600" />
                          Warning
                        </div>
                      </SelectItem>
                      <SelectItem value="success">
                        <div className="flex items-center gap-2">
                          <CheckCircle className="h-4 w-4 text-green-600" />
                          Success
                        </div>
                      </SelectItem>
                      <SelectItem value="critical">
                        <div className="flex items-center gap-2">
                          <AlertCircle className="h-4 w-4 text-red-600" />
                          Critical
                        </div>
                      </SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label>Target Audience</Label>
                  <Select
                    value={formData.target}
                    onValueChange={(value: AnnouncementTarget) => setFormData({ ...formData, target: value })}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Users</SelectItem>
                      <SelectItem value="admins">Tenant Admins Only</SelectItem>
                      <SelectItem value="specific_plans">Specific Plans</SelectItem>
                      <SelectItem value="specific_tenants">Specific Tenants</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="startsAt">Start Date</Label>
                  <Input
                    id="startsAt"
                    type="date"
                    value={formData.startsAt}
                    onChange={(e) => setFormData({ ...formData, startsAt: e.target.value })}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="expiresAt">Expiry Date (Optional)</Label>
                  <Input
                    id="expiresAt"
                    type="date"
                    value={formData.expiresAt}
                    onChange={(e) => setFormData({ ...formData, expiresAt: e.target.value })}
                  />
                </div>
              </div>
              <div className="flex items-center gap-2">
                <Switch
                  id="dismissible"
                  checked={formData.isDismissible}
                  onCheckedChange={(checked) => setFormData({ ...formData, isDismissible: checked })}
                />
                <Label htmlFor="dismissible">Allow users to dismiss this announcement</Label>
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setCreateDialogOpen(false)}>
                Cancel
              </Button>
              <Button onClick={handleCreate} disabled={!formData.title || !formData.content}>
                <Send className="h-4 w-4 mr-2" />
                Publish Announcement
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Total Announcements</p>
                <p className="text-2xl font-bold">{announcements.length}</p>
              </div>
              <Megaphone className="h-8 w-8 text-gray-400" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Active</p>
                <p className="text-2xl font-bold text-green-600">{activeCount}</p>
              </div>
              <Eye className="h-8 w-8 text-green-400" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Total Views</p>
                <p className="text-2xl font-bold">{totalViews.toLocaleString()}</p>
              </div>
              <Users className="h-8 w-8 text-blue-400" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Critical Active</p>
                <p className="text-2xl font-bold text-red-600">
                  {announcements.filter(a => a.isActive && a.type === 'critical').length}
                </p>
              </div>
              <AlertCircle className="h-8 w-8 text-red-400" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-4">
        <Select value={filterStatus} onValueChange={(v: 'all' | 'active' | 'inactive') => setFilterStatus(v)}>
          <SelectTrigger className="w-40">
            <SelectValue placeholder="Status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Status</SelectItem>
            <SelectItem value="active">Active</SelectItem>
            <SelectItem value="inactive">Inactive</SelectItem>
          </SelectContent>
        </Select>
        <Select value={filterType} onValueChange={(v: AnnouncementType | 'all') => setFilterType(v)}>
          <SelectTrigger className="w-40">
            <SelectValue placeholder="Type" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Types</SelectItem>
            <SelectItem value="info">Information</SelectItem>
            <SelectItem value="warning">Warning</SelectItem>
            <SelectItem value="success">Success</SelectItem>
            <SelectItem value="critical">Critical</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Announcements Table */}
      <Card>
        <CardHeader>
          <CardTitle>All Announcements</CardTitle>
          <CardDescription>
            Manage and monitor platform announcements
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Announcement</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Target</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Schedule</TableHead>
                <TableHead>Engagement</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredAnnouncements.map((announcement) => {
                const TypeIcon = typeConfig[announcement.type].icon
                return (
                  <TableRow key={announcement.id}>
                    <TableCell>
                      <div className="max-w-md">
                        <p className="font-medium truncate">{announcement.title}</p>
                        <p className="text-sm text-gray-500 truncate">{announcement.content}</p>
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full ${typeConfig[announcement.type].bgColor}`}>
                        <TypeIcon className={`h-3.5 w-3.5 ${typeConfig[announcement.type].color}`} />
                        <span className={`text-xs font-medium capitalize ${typeConfig[announcement.type].color}`}>
                          {announcement.type}
                        </span>
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <Users className="h-4 w-4 text-gray-400" />
                        <span className="text-sm">{targetLabels[announcement.target]}</span>
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge variant={announcement.isActive ? 'default' : 'secondary'}>
                        {announcement.isActive ? 'Active' : 'Inactive'}
                      </Badge>
                      {!announcement.isDismissible && (
                        <Badge variant="outline" className="ml-1">
                          Persistent
                        </Badge>
                      )}
                    </TableCell>
                    <TableCell>
                      <div className="text-sm">
                        <div className="flex items-center gap-1">
                          <Calendar className="h-3.5 w-3.5 text-gray-400" />
                          {format(announcement.startsAt, 'MMM d, yyyy')}
                        </div>
                        {announcement.expiresAt && (
                          <div className="flex items-center gap-1 text-gray-500">
                            <Clock className="h-3.5 w-3.5" />
                            Expires {format(announcement.expiresAt, 'MMM d')}
                          </div>
                        )}
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="text-sm">
                        <div className="flex items-center gap-1">
                          <Eye className="h-3.5 w-3.5 text-gray-400" />
                          {announcement.viewCount.toLocaleString()} views
                        </div>
                        {announcement.isDismissible && (
                          <div className="text-gray-500">
                            {announcement.dismissCount.toLocaleString()} dismissed
                          </div>
                        )}
                      </div>
                    </TableCell>
                    <TableCell className="text-right">
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="icon">
                            <MoreHorizontal className="h-4 w-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuItem onClick={() => setEditingAnnouncement(announcement)}>
                            <Edit className="h-4 w-4 mr-2" />
                            Edit
                          </DropdownMenuItem>
                          <DropdownMenuItem onClick={() => handleToggleActive(announcement.id)}>
                            {announcement.isActive ? (
                              <>
                                <EyeOff className="h-4 w-4 mr-2" />
                                Deactivate
                              </>
                            ) : (
                              <>
                                <Eye className="h-4 w-4 mr-2" />
                                Activate
                              </>
                            )}
                          </DropdownMenuItem>
                          <DropdownMenuItem
                            className="text-red-600"
                            onClick={() => handleDeleteClick(announcement)}
                          >
                            <Trash2 className="h-4 w-4 mr-2" />
                            Delete
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </TableCell>
                  </TableRow>
                )
              })}
            </TableBody>
          </Table>

          {filteredAnnouncements.length === 0 && (
            <div className="text-center py-12">
              <Megaphone className="h-12 w-12 text-gray-300 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900">No announcements found</h3>
              <p className="text-gray-500">Try adjusting your filters or create a new announcement.</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Preview Section */}
      <Card>
        <CardHeader>
          <CardTitle>Announcement Preview</CardTitle>
          <CardDescription>
            How announcements appear to users
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {announcements.filter(a => a.isActive).slice(0, 3).map((announcement) => {
            const TypeIcon = typeConfig[announcement.type].icon
            return (
              <div
                key={announcement.id}
                className={`p-4 rounded-lg border-l-4 ${
                  announcement.type === 'critical'
                    ? 'bg-red-50 border-red-500'
                    : announcement.type === 'warning'
                    ? 'bg-yellow-50 border-yellow-500'
                    : announcement.type === 'success'
                    ? 'bg-green-50 border-green-500'
                    : 'bg-blue-50 border-blue-500'
                }`}
              >
                <div className="flex items-start gap-3">
                  <TypeIcon className={`h-5 w-5 mt-0.5 ${typeConfig[announcement.type].color}`} />
                  <div className="flex-1">
                    <h4 className="font-medium">{announcement.title}</h4>
                    <p className="text-sm text-gray-600 mt-1">{announcement.content}</p>
                  </div>
                  {announcement.isDismissible && (
                    <Button variant="ghost" size="sm" className="text-gray-400 hover:text-gray-600">
                      Dismiss
                    </Button>
                  )}
                </div>
              </div>
            )
          })}
        </CardContent>
      </Card>

      {/* Delete Confirmation Dialog */}
      <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-red-500" />
              Delete Announcement
            </AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete <strong>{announcementToDelete?.title}</strong>?
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
  )
}
