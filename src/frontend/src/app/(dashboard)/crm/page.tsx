'use client'

import { useState, useEffect } from 'react'
import { useApi } from '@/hooks/use-api'
import { PageHeader } from '@/components/layout/page-header'
import { StatCard } from '@/components/layout/stat-card'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
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
import { formatCurrency, formatDate, formatPhone } from '@/lib/format'
import type { Lead, LeadStatus, LeadSource } from '@/types'
import {
  Plus,
  Search,
  Phone,
  Mail,
  Building2,
  Calendar,
  User,
  TrendingUp,
  Target,
  Users,
  IndianRupee,
  ChevronRight,
  MoreHorizontal,
  Edit,
  Trash2,
  PhoneCall,
  MessageSquare,
  GripVertical,
  Loader2,
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
  total_customers: number
  new_customers_this_month: number
  pipeline_value: string
  weighted_pipeline_value: string
  won_this_month: number
  won_value_this_month: string
  lost_this_month: number
  conversion_rate: number
  average_deal_size: string
}

// Lead pipeline stages
const pipelineStages: { id: LeadStatus; label: string; color: string }[] = [
  { id: 'new', label: 'New Leads', color: 'bg-slate-100 border-slate-300' },
  { id: 'contacted', label: 'Contacted', color: 'bg-blue-50 border-blue-300' },
  { id: 'qualified', label: 'Qualified', color: 'bg-purple-50 border-purple-300' },
  { id: 'proposal', label: 'Proposal', color: 'bg-yellow-50 border-yellow-300' },
  { id: 'negotiation', label: 'Negotiation', color: 'bg-orange-50 border-orange-300' },
  { id: 'won', label: 'Won', color: 'bg-green-50 border-green-300' },
  { id: 'lost', label: 'Lost', color: 'bg-red-50 border-red-300' },
]

// Mock leads data
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
    next_follow_up: '2026-01-07T10:00:00',
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
    next_follow_up: '2026-01-08T14:00:00',
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
    next_follow_up: '2026-01-09T11:00:00',
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
    next_follow_up: '2026-01-10T10:00:00',
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
    next_follow_up: '2026-01-07T15:00:00',
    assigned_to: 'user-1',
    created_at: '2025-12-15T10:00:00',
    updated_at: '2026-01-06T09:00:00',
  },
  {
    id: '6',
    company_id: 'comp-1',
    name: 'Meera Nair',
    email: 'meera@coastalexports.in',
    phone: '9900112233',
    company_name: 'Coastal Exports',
    source: 'website',
    status: 'won',
    score: 100,
    notes: 'Closed deal - 75 users',
    created_at: '2025-11-20T14:00:00',
    updated_at: '2025-12-28T16:00:00',
  },
  {
    id: '7',
    company_id: 'comp-1',
    name: 'Arjun Mehta',
    email: 'arjun@quickretail.com',
    phone: '8811223344',
    company_name: 'Quick Retail Solutions',
    source: 'referral',
    status: 'new',
    score: 65,
    notes: 'Initial inquiry via website',
    next_follow_up: '2026-01-08T09:00:00',
    created_at: '2026-01-06T08:00:00',
    updated_at: '2026-01-06T08:00:00',
  },
  {
    id: '8',
    company_id: 'comp-1',
    name: 'Kavita Desai',
    email: 'kavita@precisionmfg.in',
    phone: '7722334455',
    company_name: 'Precision Manufacturing',
    source: 'social_media',
    status: 'contacted',
    score: 78,
    notes: 'Scheduled demo for next week',
    next_follow_up: '2026-01-12T11:00:00',
    assigned_to: 'user-2',
    created_at: '2026-01-02T10:00:00',
    updated_at: '2026-01-05T14:00:00',
  },
  {
    id: '9',
    company_id: 'comp-1',
    name: 'Suresh Iyer',
    email: 'suresh@deltasystems.co.in',
    phone: '9933445566',
    company_name: 'Delta Systems',
    source: 'cold_call',
    status: 'lost',
    score: 45,
    notes: 'Chose competitor - budget constraints',
    created_at: '2025-12-01T09:00:00',
    updated_at: '2025-12-20T11:00:00',
  },
]

// Pipeline statistics
const pipelineStats = {
  totalLeads: 42,
  newThisMonth: 12,
  conversionRate: 28.5,
  avgDealSize: 245000,
  pipelineValue: 4850000,
  wonThisMonth: 3,
  lostThisMonth: 2,
}

// Lead source icons
const sourceIcons: Record<LeadSource, React.ReactNode> = {
  website: <Building2 className="h-3 w-3" />,
  referral: <Users className="h-3 w-3" />,
  social_media: <MessageSquare className="h-3 w-3" />,
  cold_call: <PhoneCall className="h-3 w-3" />,
  trade_show: <Target className="h-3 w-3" />,
  advertisement: <TrendingUp className="h-3 w-3" />,
  other: <MoreHorizontal className="h-3 w-3" />,
}

// Lead score color
function getScoreColor(score: number): string {
  if (score >= 80) return 'text-green-600 bg-green-100'
  if (score >= 60) return 'text-yellow-600 bg-yellow-100'
  return 'text-red-600 bg-red-100'
}

// Lead card component
function LeadCard({ lead, onClick }: { lead: Lead; onClick: () => void }) {
  return (
    <Card
      className="cursor-pointer hover:shadow-md transition-all group"
      onClick={onClick}
    >
      <CardContent className="p-3">
        <div className="flex items-start justify-between mb-2">
          <div className="flex-1 min-w-0">
            <p className="font-medium text-sm truncate">{lead.name}</p>
            <p className="text-xs text-muted-foreground truncate">
              {lead.company_name}
            </p>
          </div>
          <div className="flex items-center gap-1 ml-2">
            {lead.score && (
              <Badge variant="outline" className={`text-xs ${getScoreColor(lead.score)}`}>
                {lead.score}
              </Badge>
            )}
            <Button variant="ghost" size="icon" className="h-6 w-6 opacity-0 group-hover:opacity-100">
              <MoreHorizontal className="h-3 w-3" />
            </Button>
          </div>
        </div>

        <div className="space-y-1 text-xs text-muted-foreground">
          {lead.email && (
            <div className="flex items-center gap-1 truncate">
              <Mail className="h-3 w-3 flex-shrink-0" />
              <span className="truncate">{lead.email}</span>
            </div>
          )}
          {lead.phone && (
            <div className="flex items-center gap-1">
              <Phone className="h-3 w-3 flex-shrink-0" />
              <span>{formatPhone(lead.phone)}</span>
            </div>
          )}
        </div>

        <div className="flex items-center justify-between mt-3 pt-2 border-t">
          <div className="flex items-center gap-1 text-xs text-muted-foreground">
            {sourceIcons[lead.source]}
            <span className="capitalize">{lead.source.replace('_', ' ')}</span>
          </div>
          {lead.next_follow_up && (
            <div className="flex items-center gap-1 text-xs">
              <Calendar className="h-3 w-3 text-muted-foreground" />
              <span className="text-blue-600">{formatDate(lead.next_follow_up)}</span>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}

// Pipeline column component
function PipelineColumn({
  stage,
  leads,
  onLeadClick,
}: {
  stage: typeof pipelineStages[0]
  leads: Lead[]
  onLeadClick: (lead: Lead) => void
}) {
  const stageLeads = leads.filter((l) => l.status === stage.id)

  return (
    <div className={`flex-shrink-0 w-72 rounded-lg border ${stage.color}`}>
      <div className="p-3 border-b bg-white/50 rounded-t-lg">
        <div className="flex items-center justify-between">
          <h3 className="font-medium text-sm">{stage.label}</h3>
          <Badge variant="secondary" className="text-xs">
            {stageLeads.length}
          </Badge>
        </div>
      </div>
      <div className="p-2 space-y-2 max-h-[calc(100vh-400px)] overflow-y-auto">
        {stageLeads.map((lead) => (
          <LeadCard key={lead.id} lead={lead} onClick={() => onLeadClick(lead)} />
        ))}
        {stageLeads.length === 0 && (
          <div className="text-center py-4 text-xs text-muted-foreground">
            No leads in this stage
          </div>
        )}
      </div>
    </div>
  )
}

// Add Lead Dialog
function AddLeadDialog({
  open,
  onOpenChange,
  onLeadCreated
}: {
  open: boolean
  onOpenChange: (open: boolean) => void
  onLeadCreated?: (lead: Lead) => void
}) {
  const api = useApi()
  const [formData, setFormData] = useState({
    contact_name: '',
    company_name: '',
    email: '',
    phone: '',
    source: 'website' as LeadSource,
    notes: '',
    expected_value: ''
  })
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleSubmit = async () => {
    if (!formData.contact_name) return

    setIsSubmitting(true)
    try {
      const response = await api.post('/crm/leads', {
        contact_name: formData.contact_name,
        company_name: formData.company_name || null,
        email: formData.email || null,
        phone: formData.phone || null,
        source: formData.source,
        description: formData.notes || null,
        expected_value: formData.expected_value ? parseFloat(formData.expected_value) : null
      })

      if (response && onLeadCreated) {
        onLeadCreated(apiLeadToLead(response as ApiLead))
      }

      // Reset form
      setFormData({
        contact_name: '',
        company_name: '',
        email: '',
        phone: '',
        source: 'website',
        notes: '',
        expected_value: ''
      })
      onOpenChange(false)
    } catch (error) {
      console.error('Failed to create lead:', error)
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>Add New Lead</DialogTitle>
          <DialogDescription>
            Enter lead details to add to your pipeline
          </DialogDescription>
        </DialogHeader>
        <div className="grid gap-4 py-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="name">Contact Name *</Label>
              <Input
                id="name"
                placeholder="Rajesh Kumar"
                value={formData.contact_name}
                onChange={(e) => setFormData({ ...formData, contact_name: e.target.value })}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="company">Company Name</Label>
              <Input
                id="company"
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
          <div className="grid grid-cols-2 gap-4">
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
                  <SelectItem value="website">Website</SelectItem>
                  <SelectItem value="referral">Referral</SelectItem>
                  <SelectItem value="social_media">Social Media</SelectItem>
                  <SelectItem value="cold_call">Cold Call</SelectItem>
                  <SelectItem value="trade_show">Trade Show</SelectItem>
                  <SelectItem value="advertisement">Advertisement</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="expected_value">Expected Value (₹)</Label>
              <Input
                id="expected_value"
                type="number"
                placeholder="500000"
                value={formData.expected_value}
                onChange={(e) => setFormData({ ...formData, expected_value: e.target.value })}
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
                Creating...
              </>
            ) : (
              'Add Lead'
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
}: {
  lead: Lead | null
  open: boolean
  onOpenChange: (open: boolean) => void
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
                {lead.company_name}
              </DialogDescription>
            </div>
            {lead.score && (
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
                <a href={`mailto:${lead.email}`} className="text-blue-600 hover:underline">
                  {lead.email}
                </a>
              </div>
            </div>
            <div className="space-y-1">
              <Label className="text-xs text-muted-foreground">Phone</Label>
              <div className="flex items-center gap-2">
                <Phone className="h-4 w-4 text-muted-foreground" />
                <a href={`tel:${lead.phone}`} className="text-blue-600 hover:underline">
                  {formatPhone(lead.phone)}
                </a>
              </div>
            </div>
          </div>

          {/* Status & Source */}
          <div className="grid grid-cols-3 gap-4">
            <div className="space-y-1">
              <Label className="text-xs text-muted-foreground">Status</Label>
              <Select defaultValue={lead.status}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {pipelineStages.map((stage) => (
                    <SelectItem key={stage.id} value={stage.id}>
                      {stage.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-1">
              <Label className="text-xs text-muted-foreground">Source</Label>
              <div className="flex items-center gap-2 h-9 px-3 border rounded-md bg-muted/50">
                {sourceIcons[lead.source]}
                <span className="capitalize text-sm">{lead.source.replace('_', ' ')}</span>
              </div>
            </div>
            <div className="space-y-1">
              <Label className="text-xs text-muted-foreground">Next Follow-up</Label>
              <div className="flex items-center gap-2 h-9 px-3 border rounded-md">
                <Calendar className="h-4 w-4 text-muted-foreground" />
                <span className="text-sm">
                  {lead.next_follow_up ? formatDate(lead.next_follow_up) : 'Not scheduled'}
                </span>
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
            <Label className="text-xs text-muted-foreground">Activity Timeline</Label>
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

        <DialogFooter className="gap-2">
          <Button variant="outline" className="gap-2">
            <PhoneCall className="h-4 w-4" />
            Call
          </Button>
          <Button variant="outline" className="gap-2">
            <Mail className="h-4 w-4" />
            Email
          </Button>
          <Button variant="outline" className="gap-2">
            <Edit className="h-4 w-4" />
            Edit
          </Button>
          <Button className="gap-2">
            <ChevronRight className="h-4 w-4" />
            Move Stage
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
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

export default function CRMPage() {
  const api = useApi()
  const [searchQuery, setSearchQuery] = useState('')
  const [activeTab, setActiveTab] = useState('pipeline')
  const [addDialogOpen, setAddDialogOpen] = useState(false)
  const [selectedLead, setSelectedLead] = useState<Lead | null>(null)
  const [detailDialogOpen, setDetailDialogOpen] = useState(false)
  const [leads, setLeads] = useState<Lead[]>(mockLeads)
  const [stats, setStats] = useState(pipelineStats)
  const [loading, setLoading] = useState(true)

  // Fetch leads and dashboard data from API
  useEffect(() => {
    const fetchData = async () => {
      setLoading(true)
      try {
        // Fetch leads
        const leadsResponse = await api.get('/crm/leads?limit=100')
        if (leadsResponse?.data && Array.isArray(leadsResponse.data)) {
          const apiLeads = leadsResponse.data.map(apiLeadToLead)
          // Merge with mock data if API returns empty (for demo)
          setLeads(apiLeads.length > 0 ? apiLeads : mockLeads)
        }

        // Fetch dashboard metrics
        const dashboardResponse = await api.get('/crm/dashboard') as ApiDashboard | null
        if (dashboardResponse) {
          setStats({
            totalLeads: dashboardResponse.total_leads || pipelineStats.totalLeads,
            newThisMonth: dashboardResponse.new_leads_this_month || pipelineStats.newThisMonth,
            conversionRate: dashboardResponse.conversion_rate || pipelineStats.conversionRate,
            avgDealSize: parseFloat(dashboardResponse.average_deal_size) || pipelineStats.avgDealSize,
            pipelineValue: parseFloat(dashboardResponse.pipeline_value) || pipelineStats.pipelineValue,
            wonThisMonth: dashboardResponse.won_this_month || pipelineStats.wonThisMonth,
            lostThisMonth: dashboardResponse.lost_this_month || pipelineStats.lostThisMonth,
          })
        }
      } catch (error) {
        console.error('Failed to fetch CRM data:', error)
        // Keep mock data on error
      } finally {
        setLoading(false)
      }
    }

    fetchData()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []) // Run only once on mount

  const filteredLeads = leads.filter((lead) => {
    if (!searchQuery) return true
    const query = searchQuery.toLowerCase()
    return (
      lead.name.toLowerCase().includes(query) ||
      lead.company_name?.toLowerCase().includes(query) ||
      lead.email?.toLowerCase().includes(query)
    )
  })

  const handleLeadClick = (lead: Lead) => {
    setSelectedLead(lead)
    setDetailDialogOpen(true)
  }

  const handleLeadCreated = (newLead: Lead) => {
    setLeads((prevLeads) => [newLead, ...prevLeads])
    // Update stats
    setStats((prevStats) => ({
      ...prevStats,
      totalLeads: prevStats.totalLeads + 1,
      newThisMonth: prevStats.newThisMonth + 1
    }))
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="CRM & Sales Pipeline"
        description="Manage leads, opportunities, and customer relationships"
        actions={
          <div className="flex gap-2">
            <div className="relative">
              <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search leads..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-8 w-64"
              />
            </div>
            <Button onClick={() => setAddDialogOpen(true)}>
              <Plus className="h-4 w-4 mr-2" />
              Add Lead
            </Button>
          </div>
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
            title="Total Leads"
            value={stats.totalLeads}
            icon={Users}
            description={`${stats.newThisMonth} new this month`}
          />
          <StatCard
            title="Pipeline Value"
            value={formatCurrency(stats.pipelineValue)}
            icon={IndianRupee}
            description="Active opportunities"
          />
          <StatCard
            title="Conversion Rate"
            value={`${stats.conversionRate}%`}
            icon={TrendingUp}
            description="Lead to customer"
            trend="up"
            trendValue="+2.3%"
          />
          <StatCard
            title="Won This Month"
            value={stats.wonThisMonth}
            icon={Target}
            description={formatCurrency(stats.avgDealSize * stats.wonThisMonth)}
          />
          <StatCard
            title="Avg Deal Size"
            value={formatCurrency(stats.avgDealSize)}
            icon={IndianRupee}
            description="Per customer"
          />
        </div>
      )}

      {/* Pipeline / List View */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="pipeline">Pipeline View</TabsTrigger>
          <TabsTrigger value="list">List View</TabsTrigger>
        </TabsList>

        <TabsContent value="pipeline" className="mt-4">
          <div className="flex gap-4 overflow-x-auto pb-4">
            {pipelineStages
              .filter((s) => s.id !== 'lost') // Hide lost from main pipeline
              .map((stage) => (
                <PipelineColumn
                  key={stage.id}
                  stage={stage}
                  leads={filteredLeads}
                  onLeadClick={handleLeadClick}
                />
              ))}
          </div>
        </TabsContent>

        <TabsContent value="list" className="mt-4">
          <Card>
            <CardContent className="p-0">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b bg-muted/50">
                      <th className="text-left p-3 text-xs font-medium text-muted-foreground">Lead</th>
                      <th className="text-left p-3 text-xs font-medium text-muted-foreground">Company</th>
                      <th className="text-left p-3 text-xs font-medium text-muted-foreground">Contact</th>
                      <th className="text-left p-3 text-xs font-medium text-muted-foreground">Source</th>
                      <th className="text-left p-3 text-xs font-medium text-muted-foreground">Status</th>
                      <th className="text-center p-3 text-xs font-medium text-muted-foreground">Score</th>
                      <th className="text-left p-3 text-xs font-medium text-muted-foreground">Next Follow-up</th>
                      <th className="text-right p-3 text-xs font-medium text-muted-foreground">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredLeads.map((lead) => (
                      <tr
                        key={lead.id}
                        className="border-b hover:bg-muted/30 cursor-pointer"
                        onClick={() => handleLeadClick(lead)}
                      >
                        <td className="p-3">
                          <p className="font-medium text-sm">{lead.name}</p>
                        </td>
                        <td className="p-3">
                          <p className="text-sm text-muted-foreground">{lead.company_name || '-'}</p>
                        </td>
                        <td className="p-3">
                          <div className="text-xs space-y-0.5">
                            {lead.email && <p>{lead.email}</p>}
                            {lead.phone && <p className="text-muted-foreground">{formatPhone(lead.phone)}</p>}
                          </div>
                        </td>
                        <td className="p-3">
                          <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
                            {sourceIcons[lead.source]}
                            <span className="capitalize">{lead.source.replace('_', ' ')}</span>
                          </div>
                        </td>
                        <td className="p-3">
                          <Badge variant="outline" className="text-xs capitalize">
                            {lead.status}
                          </Badge>
                        </td>
                        <td className="p-3 text-center">
                          {lead.score && (
                            <Badge className={`text-xs ${getScoreColor(lead.score)}`}>
                              {lead.score}
                            </Badge>
                          )}
                        </td>
                        <td className="p-3">
                          {lead.next_follow_up ? (
                            <p className="text-xs text-blue-600">{formatDate(lead.next_follow_up)}</p>
                          ) : (
                            <p className="text-xs text-muted-foreground">-</p>
                          )}
                        </td>
                        <td className="p-3 text-right">
                          <Button variant="ghost" size="icon" className="h-8 w-8">
                            <MoreHorizontal className="h-4 w-4" />
                          </Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Dialogs */}
      <AddLeadDialog
        open={addDialogOpen}
        onOpenChange={setAddDialogOpen}
        onLeadCreated={handleLeadCreated}
      />
      <LeadDetailDialog
        lead={selectedLead}
        open={detailDialogOpen}
        onOpenChange={setDetailDialogOpen}
      />
    </div>
  )
}
