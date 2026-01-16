'use client'

import { useState, useEffect } from 'react'
import { useApi } from '@/hooks/use-api'
import { PageHeader } from '@/components/layout/page-header'
import { StatCard } from '@/components/layout/stat-card'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
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
import { formatCurrency, formatDate, formatPhone } from '@/lib/format'
import type { Lead, LeadStatus, LeadSource } from '@/types'
import {
  Plus,
  Search,
  Phone,
  Mail,
  Building2,
  Calendar,
  Users,
  TrendingUp,
  Target,
  Filter,
  MoreHorizontal,
  Edit,
  Trash2,
  Eye,
  Loader2,
  Star,
  UserPlus,
} from 'lucide-react'

// API Response Types
interface ApiLead {
  id: string
  lead_number: string
  company_name: string | null
  contact_name: string
  email: string | null
  phone: string | null
  mobile: string | null
  source: LeadSource
  status: LeadStatus
  score: number
  rating: string | null
  expected_value: string | null
  expected_close_date: string | null
  description: string | null
  notes?: string
  assigned_to: string | null
  created_at: string
  updated_at: string
}

interface ApiDashboard {
  total_leads: number
  new_leads_this_month: number
  leads_by_status: Record<string, number>
  leads_by_source: Record<string, number>
  conversion_rate: number
}

// Lead status configuration
const statusConfig: Record<LeadStatus, { label: string; color: string }> = {
  new: { label: 'New', color: 'bg-blue-100 text-blue-800' },
  contacted: { label: 'Contacted', color: 'bg-purple-100 text-purple-800' },
  qualified: { label: 'Qualified', color: 'bg-green-100 text-green-800' },
  proposal: { label: 'Proposal', color: 'bg-yellow-100 text-yellow-800' },
  negotiation: { label: 'Negotiation', color: 'bg-orange-100 text-orange-800' },
  won: { label: 'Won', color: 'bg-emerald-100 text-emerald-800' },
  lost: { label: 'Lost', color: 'bg-red-100 text-red-800' },
  nurturing: { label: 'Nurturing', color: 'bg-gray-100 text-gray-800' },
}

// Lead source labels
const sourceLabels: Record<LeadSource, string> = {
  website: 'Website',
  referral: 'Referral',
  social_media: 'Social Media',
  cold_call: 'Cold Call',
  trade_show: 'Trade Show',
  advertisement: 'Advertisement',
  other: 'Other',
}

// Lead score color
function getScoreColor(score: number): string {
  if (score >= 80) return 'text-green-600 bg-green-100'
  if (score >= 60) return 'text-yellow-600 bg-yellow-100'
  return 'text-red-600 bg-red-100'
}

// Helper function to convert API lead to local Lead type
function apiLeadToLead(apiLead: ApiLead): Lead {
  return {
    id: apiLead.id,
    company_id: '',
    name: apiLead.contact_name,
    email: apiLead.email || undefined,
    phone: apiLead.phone || apiLead.mobile || undefined,
    company_name: apiLead.company_name || undefined,
    source: apiLead.source,
    status: apiLead.status,
    score: apiLead.score,
    notes: apiLead.description || apiLead.notes,
    next_follow_up: apiLead.expected_close_date || undefined,
    assigned_to: apiLead.assigned_to || undefined,
    created_at: apiLead.created_at,
    updated_at: apiLead.updated_at,
  }
}

// Mock data for demo
const mockLeads: Lead[] = [
  {
    id: '1',
    company_id: 'comp-1',
    name: 'Rajesh Kumar',
    email: 'rajesh@techsolutions.in',
    phone: '9876543210',
    company_name: 'Tech Solutions Pvt Ltd',
    source: 'website',
    status: 'new',
    score: 85,
    notes: 'Interested in payroll module',
    next_follow_up: '2026-01-20T10:00:00',
    created_at: '2026-01-05T09:30:00',
    updated_at: '2026-01-05T09:30:00',
  },
  {
    id: '2',
    company_id: 'comp-1',
    name: 'Priya Sharma',
    email: 'priya@globalmart.co.in',
    phone: '9988776655',
    company_name: 'Global Mart India',
    source: 'referral',
    status: 'contacted',
    score: 72,
    notes: 'Looking for complete ERP',
    next_follow_up: '2026-01-18T14:00:00',
    assigned_to: 'user-1',
    created_at: '2026-01-03T11:00:00',
    updated_at: '2026-01-06T10:30:00',
  },
  {
    id: '3',
    company_id: 'comp-1',
    name: 'Amit Patel',
    email: 'amit@innovatetech.com',
    phone: '8877665544',
    company_name: 'Innovate Tech Systems',
    source: 'cold_call',
    status: 'qualified',
    score: 90,
    notes: '50+ employees, need HRMS',
    next_follow_up: '2026-01-19T11:00:00',
    assigned_to: 'user-1',
    created_at: '2026-01-01T14:00:00',
    updated_at: '2026-01-05T16:00:00',
  },
  {
    id: '4',
    company_id: 'comp-1',
    name: 'Sneha Reddy',
    email: 'sneha@bharatfinance.in',
    phone: '7766554433',
    company_name: 'Bharat Finance Ltd',
    source: 'trade_show',
    status: 'proposal',
    score: 95,
    notes: 'Sent proposal for 100 users',
    next_follow_up: '2026-01-22T10:00:00',
    assigned_to: 'user-2',
    created_at: '2025-12-20T09:00:00',
    updated_at: '2026-01-04T11:00:00',
  },
  {
    id: '5',
    company_id: 'comp-1',
    name: 'Vikram Singh',
    email: 'vikram@sunriseindustries.co.in',
    phone: '6655443322',
    company_name: 'Sunrise Industries',
    source: 'advertisement',
    status: 'negotiation',
    score: 88,
    notes: 'Negotiating pricing for 3-year contract',
    next_follow_up: '2026-01-17T15:00:00',
    assigned_to: 'user-1',
    created_at: '2025-12-15T10:00:00',
    updated_at: '2026-01-06T09:00:00',
  },
]

// Add/Edit Lead Dialog
function LeadDialog({
  open,
  onOpenChange,
  lead,
  onSave,
}: {
  open: boolean
  onOpenChange: (open: boolean) => void
  lead: Lead | null
  onSave: (lead: Lead) => void
}) {
  const api = useApi()
  const [formData, setFormData] = useState({
    contact_name: '',
    company_name: '',
    email: '',
    phone: '',
    source: 'website' as LeadSource,
    status: 'new' as LeadStatus,
    score: 50,
    notes: '',
  })
  const [isSubmitting, setIsSubmitting] = useState(false)

  useEffect(() => {
    if (lead) {
      setFormData({
        contact_name: lead.name,
        company_name: lead.company_name || '',
        email: lead.email || '',
        phone: lead.phone || '',
        source: lead.source,
        status: lead.status,
        score: lead.score || 50,
        notes: lead.notes || '',
      })
    } else {
      setFormData({
        contact_name: '',
        company_name: '',
        email: '',
        phone: '',
        source: 'website',
        status: 'new',
        score: 50,
        notes: '',
      })
    }
  }, [lead, open])

  const handleSubmit = async () => {
    if (!formData.contact_name) return

    setIsSubmitting(true)
    try {
      const payload = {
        contact_name: formData.contact_name,
        company_name: formData.company_name || null,
        email: formData.email || null,
        phone: formData.phone || null,
        source: formData.source,
        status: formData.status,
        score: formData.score,
        description: formData.notes || null,
      }

      let response
      if (lead) {
        response = await api.put(`/crm/leads/${lead.id}`, payload)
      } else {
        response = await api.post('/crm/leads', payload)
      }

      if (response) {
        onSave(apiLeadToLead(response as ApiLead))
        onOpenChange(false)
      }
    } catch (error) {
      console.error('Failed to save lead:', error)
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[600px]">
        <DialogHeader>
          <DialogTitle>{lead ? 'Edit Lead' : 'Add New Lead'}</DialogTitle>
          <DialogDescription>
            {lead ? 'Update lead information' : 'Enter lead details to add to your pipeline'}
          </DialogDescription>
        </DialogHeader>
        <div className="grid gap-4 py-4">
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
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                placeholder="rajesh@company.in"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="phone">Phone</Label>
              <Input
                id="phone"
                placeholder="9876543210"
                value={formData.phone}
                onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
              />
            </div>
          </div>
          <div className="grid grid-cols-3 gap-4">
            <div className="space-y-2">
              <Label htmlFor="source">Lead Source</Label>
              <Select
                value={formData.source}
                onValueChange={(value) => setFormData({ ...formData, source: value as LeadSource })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select source" />
                </SelectTrigger>
                <SelectContent>
                  {Object.entries(sourceLabels).map(([value, label]) => (
                    <SelectItem key={value} value={value}>{label}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="status">Status</Label>
              <Select
                value={formData.status}
                onValueChange={(value) => setFormData({ ...formData, status: value as LeadStatus })}
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
            <div className="space-y-2">
              <Label htmlFor="score">Lead Score (0-100)</Label>
              <Input
                id="score"
                type="number"
                min="0"
                max="100"
                value={formData.score}
                onChange={(e) => setFormData({ ...formData, score: parseInt(e.target.value) || 0 })}
              />
            </div>
          </div>
          <div className="space-y-2">
            <Label htmlFor="notes">Notes</Label>
            <Input
              id="notes"
              placeholder="Initial requirements, budget, timeline..."
              value={formData.notes}
              onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
            />
          </div>
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)} disabled={isSubmitting}>
            Cancel
          </Button>
          <Button onClick={handleSubmit} disabled={isSubmitting || !formData.contact_name}>
            {isSubmitting ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                {lead ? 'Updating...' : 'Creating...'}
              </>
            ) : (
              lead ? 'Update Lead' : 'Add Lead'
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

// Lead Detail Dialog
function LeadDetailDialog({
  lead,
  open,
  onOpenChange,
  onEdit,
}: {
  lead: Lead | null
  open: boolean
  onOpenChange: (open: boolean) => void
  onEdit: () => void
}) {
  if (!lead) return null

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[600px]">
        <DialogHeader>
          <div className="flex items-start justify-between">
            <div>
              <DialogTitle className="text-xl">{lead.name}</DialogTitle>
              <DialogDescription className="flex items-center gap-2 mt-1">
                <Building2 className="h-4 w-4" />
                {lead.company_name || 'No company'}
              </DialogDescription>
            </div>
            {lead.score !== undefined && (
              <Badge className={`text-lg px-3 py-1 ${getScoreColor(lead.score)}`}>
                {lead.score}
              </Badge>
            )}
          </div>
        </DialogHeader>

        <div className="space-y-6 py-4">
          {/* Contact Info */}
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1">
              <Label className="text-xs text-muted-foreground">Email</Label>
              <div className="flex items-center gap-2">
                <Mail className="h-4 w-4 text-muted-foreground" />
                {lead.email ? (
                  <a href={`mailto:${lead.email}`} className="text-blue-600 hover:underline">
                    {lead.email}
                  </a>
                ) : (
                  <span className="text-muted-foreground">Not provided</span>
                )}
              </div>
            </div>
            <div className="space-y-1">
              <Label className="text-xs text-muted-foreground">Phone</Label>
              <div className="flex items-center gap-2">
                <Phone className="h-4 w-4 text-muted-foreground" />
                {lead.phone ? (
                  <a href={`tel:${lead.phone}`} className="text-blue-600 hover:underline">
                    {formatPhone(lead.phone)}
                  </a>
                ) : (
                  <span className="text-muted-foreground">Not provided</span>
                )}
              </div>
            </div>
          </div>

          {/* Status & Source */}
          <div className="grid grid-cols-3 gap-4">
            <div className="space-y-1">
              <Label className="text-xs text-muted-foreground">Status</Label>
              <Badge className={statusConfig[lead.status].color}>
                {statusConfig[lead.status].label}
              </Badge>
            </div>
            <div className="space-y-1">
              <Label className="text-xs text-muted-foreground">Source</Label>
              <div className="text-sm capitalize">{sourceLabels[lead.source]}</div>
            </div>
            <div className="space-y-1">
              <Label className="text-xs text-muted-foreground">Next Follow-up</Label>
              <div className="flex items-center gap-2 text-sm">
                <Calendar className="h-4 w-4 text-muted-foreground" />
                {lead.next_follow_up ? formatDate(lead.next_follow_up) : 'Not scheduled'}
              </div>
            </div>
          </div>

          {/* Notes */}
          {lead.notes && (
            <div className="space-y-1">
              <Label className="text-xs text-muted-foreground">Notes</Label>
              <div className="p-3 bg-muted/50 rounded-md text-sm">
                {lead.notes}
              </div>
            </div>
          )}

          {/* Timeline */}
          <div className="space-y-2">
            <Label className="text-xs text-muted-foreground">Timeline</Label>
            <div className="border rounded-md p-3 space-y-3">
              <div className="flex gap-3 text-sm">
                <div className="w-1 bg-green-500 rounded-full" />
                <div>
                  <p className="font-medium">Lead created</p>
                  <p className="text-xs text-muted-foreground">{formatDate(lead.created_at, { format: 'long', showTime: true })}</p>
                </div>
              </div>
              {lead.updated_at !== lead.created_at && (
                <div className="flex gap-3 text-sm">
                  <div className="w-1 bg-blue-500 rounded-full" />
                  <div>
                    <p className="font-medium">Last updated</p>
                    <p className="text-xs text-muted-foreground">{formatDate(lead.updated_at, { format: 'long', showTime: true })}</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Close
          </Button>
          <Button onClick={onEdit}>
            <Edit className="h-4 w-4 mr-2" />
            Edit Lead
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

export default function LeadsPage() {
  const api = useApi()
  const [searchQuery, setSearchQuery] = useState('')
  const [statusFilter, setStatusFilter] = useState<string>('all')
  const [sourceFilter, setSourceFilter] = useState<string>('all')
  const [leads, setLeads] = useState<Lead[]>(mockLeads)
  const [loading, setLoading] = useState(true)
  const [stats, setStats] = useState({
    totalLeads: 42,
    newThisMonth: 12,
    qualifiedLeads: 18,
    conversionRate: 28.5,
  })

  // Dialogs state
  const [addDialogOpen, setAddDialogOpen] = useState(false)
  const [editDialogOpen, setEditDialogOpen] = useState(false)
  const [detailDialogOpen, setDetailDialogOpen] = useState(false)
  const [selectedLead, setSelectedLead] = useState<Lead | null>(null)

  // Fetch leads from API
  useEffect(() => {
    const fetchData = async () => {
      setLoading(true)
      try {
        const leadsResponse = await api.get('/crm/leads?limit=100')
        if (leadsResponse?.data && Array.isArray(leadsResponse.data)) {
          const apiLeads = leadsResponse.data.map(apiLeadToLead)
          setLeads(apiLeads.length > 0 ? apiLeads : mockLeads)
        }

        const dashboardResponse = await api.get('/crm/dashboard') as ApiDashboard | null
        if (dashboardResponse) {
          setStats({
            totalLeads: dashboardResponse.total_leads || stats.totalLeads,
            newThisMonth: dashboardResponse.new_leads_this_month || stats.newThisMonth,
            qualifiedLeads: dashboardResponse.leads_by_status?.qualified || 18,
            conversionRate: dashboardResponse.conversion_rate || stats.conversionRate,
          })
        }
      } catch (error) {
        console.error('Failed to fetch leads:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  // Filter leads
  const filteredLeads = leads.filter((lead) => {
    const matchesSearch = !searchQuery ||
      lead.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      lead.company_name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
      lead.email?.toLowerCase().includes(searchQuery.toLowerCase())

    const matchesStatus = statusFilter === 'all' || lead.status === statusFilter
    const matchesSource = sourceFilter === 'all' || lead.source === sourceFilter

    return matchesSearch && matchesStatus && matchesSource
  })

  const handleViewLead = (lead: Lead) => {
    setSelectedLead(lead)
    setDetailDialogOpen(true)
  }

  const handleEditLead = (lead: Lead) => {
    setSelectedLead(lead)
    setEditDialogOpen(true)
  }

  const handleLeadSaved = (savedLead: Lead) => {
    if (selectedLead) {
      // Update existing lead
      setLeads(prev => prev.map(l => l.id === savedLead.id ? savedLead : l))
    } else {
      // Add new lead
      setLeads(prev => [savedLead, ...prev])
      setStats(prev => ({
        ...prev,
        totalLeads: prev.totalLeads + 1,
        newThisMonth: prev.newThisMonth + 1,
      }))
    }
    setSelectedLead(null)
  }

  const handleDeleteLead = async (lead: Lead) => {
    if (!confirm('Are you sure you want to delete this lead?')) return

    try {
      const success = await api.delete(`/crm/leads/${lead.id}`)
      if (success) {
        setLeads(prev => prev.filter(l => l.id !== lead.id))
      }
    } catch (error) {
      console.error('Failed to delete lead:', error)
    }
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Lead Management"
        description="Track and manage your sales leads"
        breadcrumbs={[
          { label: 'CRM', href: '/crm' },
          { label: 'Leads' },
        ]}
        actions={
          <Button onClick={() => setAddDialogOpen(true)}>
            <Plus className="h-4 w-4 mr-2" />
            Add Lead
          </Button>
        }
      />

      {/* Stats */}
      {loading ? (
        <div className="flex items-center justify-center h-24">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-4">
          <StatCard
            title="Total Leads"
            value={stats.totalLeads}
            icon={Users}
            description={`${stats.newThisMonth} new this month`}
          />
          <StatCard
            title="New Leads"
            value={stats.newThisMonth}
            icon={UserPlus}
            description="This month"
            trend={{ value: 15, label: 'vs last month' }}
          />
          <StatCard
            title="Qualified Leads"
            value={stats.qualifiedLeads}
            icon={Star}
            description="Ready for proposal"
          />
          <StatCard
            title="Conversion Rate"
            value={`${stats.conversionRate}%`}
            icon={TrendingUp}
            description="Lead to customer"
            trend={{ value: 2.3, label: 'vs last month' }}
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
                placeholder="Search leads..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-8"
              />
            </div>
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
            <Select value={sourceFilter} onValueChange={setSourceFilter}>
              <SelectTrigger className="w-[150px]">
                <Filter className="h-4 w-4 mr-2" />
                <SelectValue placeholder="Source" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Sources</SelectItem>
                {Object.entries(sourceLabels).map(([value, label]) => (
                  <SelectItem key={value} value={value}>{label}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Leads Table */}
      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Lead</TableHead>
                <TableHead>Company</TableHead>
                <TableHead>Contact</TableHead>
                <TableHead>Source</TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="text-center">Score</TableHead>
                <TableHead>Next Follow-up</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredLeads.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={8} className="text-center py-8 text-muted-foreground">
                    No leads found
                  </TableCell>
                </TableRow>
              ) : (
                filteredLeads.map((lead) => (
                  <TableRow key={lead.id}>
                    <TableCell>
                      <p className="font-medium">{lead.name}</p>
                    </TableCell>
                    <TableCell>
                      <p className="text-muted-foreground">{lead.company_name || '-'}</p>
                    </TableCell>
                    <TableCell>
                      <div className="text-xs space-y-0.5">
                        {lead.email && <p>{lead.email}</p>}
                        {lead.phone && <p className="text-muted-foreground">{formatPhone(lead.phone)}</p>}
                      </div>
                    </TableCell>
                    <TableCell>
                      <span className="text-sm capitalize">{sourceLabels[lead.source]}</span>
                    </TableCell>
                    <TableCell>
                      <Badge className={statusConfig[lead.status].color}>
                        {statusConfig[lead.status].label}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-center">
                      {lead.score !== undefined && (
                        <Badge className={getScoreColor(lead.score)}>
                          {lead.score}
                        </Badge>
                      )}
                    </TableCell>
                    <TableCell>
                      {lead.next_follow_up ? (
                        <span className="text-sm text-blue-600">{formatDate(lead.next_follow_up)}</span>
                      ) : (
                        <span className="text-muted-foreground">-</span>
                      )}
                    </TableCell>
                    <TableCell className="text-right">
                      <div className="flex items-center justify-end gap-1">
                        <Button variant="ghost" size="icon" onClick={() => handleViewLead(lead)}>
                          <Eye className="h-4 w-4" />
                        </Button>
                        <Button variant="ghost" size="icon" onClick={() => handleEditLead(lead)}>
                          <Edit className="h-4 w-4" />
                        </Button>
                        <Button variant="ghost" size="icon" onClick={() => handleDeleteLead(lead)}>
                          <Trash2 className="h-4 w-4 text-red-500" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Dialogs */}
      <LeadDialog
        open={addDialogOpen}
        onOpenChange={setAddDialogOpen}
        lead={null}
        onSave={handleLeadSaved}
      />
      <LeadDialog
        open={editDialogOpen}
        onOpenChange={(open) => {
          setEditDialogOpen(open)
          if (!open) setSelectedLead(null)
        }}
        lead={selectedLead}
        onSave={handleLeadSaved}
      />
      <LeadDetailDialog
        lead={selectedLead}
        open={detailDialogOpen}
        onOpenChange={(open) => {
          setDetailDialogOpen(open)
          if (!open) setSelectedLead(null)
        }}
        onEdit={() => {
          setDetailDialogOpen(false)
          setEditDialogOpen(true)
        }}
      />
    </div>
  )
}
