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
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Progress } from '@/components/ui/progress'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { formatCurrency, formatDate } from '@/lib/format'
import type { Opportunity } from '@/types'
import {
  Plus,
  Search,
  IndianRupee,
  Calendar,
  TrendingUp,
  Target,
  Filter,
  Edit,
  Trash2,
  Eye,
  Loader2,
  Briefcase,
  BarChart3,
  ArrowUpRight,
  Clock,
} from 'lucide-react'

// Opportunity stage configuration
const stageConfig: Record<string, { label: string; color: string; order: number }> = {
  prospecting: { label: 'Prospecting', color: 'bg-slate-100 text-slate-800', order: 1 },
  qualification: { label: 'Qualification', color: 'bg-blue-100 text-blue-800', order: 2 },
  needs_analysis: { label: 'Needs Analysis', color: 'bg-purple-100 text-purple-800', order: 3 },
  proposal: { label: 'Proposal', color: 'bg-yellow-100 text-yellow-800', order: 4 },
  negotiation: { label: 'Negotiation', color: 'bg-orange-100 text-orange-800', order: 5 },
  closed_won: { label: 'Closed Won', color: 'bg-green-100 text-green-800', order: 6 },
  closed_lost: { label: 'Closed Lost', color: 'bg-red-100 text-red-800', order: 7 },
}

// Mock data
const mockOpportunities: Opportunity[] = [
  {
    id: '1',
    company_id: 'comp-1',
    lead_id: 'lead-1',
    name: 'Tech Solutions - ERP Implementation',
    customer_id: 'cust-1',
    value: 2500000,
    probability: 75,
    expected_close_date: '2026-02-15',
    stage: 'proposal',
    assigned_to: 'user-1',
    notes: 'Complete ERP suite including HRMS, Finance, and CRM modules',
    created_at: '2026-01-05T09:30:00',
    updated_at: '2026-01-10T14:30:00',
  },
  {
    id: '2',
    company_id: 'comp-1',
    lead_id: 'lead-2',
    name: 'Global Mart - Payroll System',
    customer_id: 'cust-2',
    value: 850000,
    probability: 60,
    expected_close_date: '2026-02-28',
    stage: 'needs_analysis',
    assigned_to: 'user-1',
    notes: 'Payroll for 200+ employees with compliance requirements',
    created_at: '2026-01-03T11:00:00',
    updated_at: '2026-01-08T10:30:00',
  },
  {
    id: '3',
    company_id: 'comp-1',
    lead_id: 'lead-3',
    name: 'Innovate Tech - HRMS Module',
    customer_id: 'cust-3',
    value: 1200000,
    probability: 90,
    expected_close_date: '2026-01-25',
    stage: 'negotiation',
    assigned_to: 'user-2',
    notes: 'Final pricing discussions ongoing, highly likely to close',
    created_at: '2025-12-15T14:00:00',
    updated_at: '2026-01-12T16:00:00',
  },
  {
    id: '4',
    company_id: 'comp-1',
    lead_id: 'lead-4',
    name: 'Bharat Finance - Complete Suite',
    customer_id: 'cust-4',
    value: 3500000,
    probability: 80,
    expected_close_date: '2026-03-15',
    stage: 'proposal',
    assigned_to: 'user-1',
    notes: 'Enterprise deal with 3-year commitment',
    created_at: '2025-12-20T09:00:00',
    updated_at: '2026-01-06T11:00:00',
  },
  {
    id: '5',
    company_id: 'comp-1',
    name: 'Sunrise Industries - CRM',
    customer_id: 'cust-5',
    value: 650000,
    probability: 40,
    expected_close_date: '2026-03-30',
    stage: 'qualification',
    assigned_to: 'user-2',
    notes: 'Exploring CRM options, considering competitors',
    created_at: '2026-01-08T10:00:00',
    updated_at: '2026-01-10T09:00:00',
  },
  {
    id: '6',
    company_id: 'comp-1',
    name: 'Coastal Exports - Finance Module',
    customer_id: 'cust-6',
    value: 980000,
    probability: 100,
    expected_close_date: '2026-01-10',
    stage: 'closed_won',
    notes: 'Deal closed! Implementation starting next week',
    created_at: '2025-11-20T14:00:00',
    updated_at: '2026-01-10T16:00:00',
  },
]

// Get probability color
function getProbabilityColor(probability: number): string {
  if (probability >= 75) return 'text-green-600'
  if (probability >= 50) return 'text-yellow-600'
  return 'text-red-600'
}

// Opportunity Dialog
function OpportunityDialog({
  open,
  onOpenChange,
  opportunity,
  onSave,
}: {
  open: boolean
  onOpenChange: (open: boolean) => void
  opportunity: Opportunity | null
  onSave: (opportunity: Opportunity) => void
}) {
  const api = useApi()
  const [formData, setFormData] = useState({
    name: '',
    value: '',
    probability: 50,
    expected_close_date: '',
    stage: 'prospecting',
    notes: '',
  })
  const [isSubmitting, setIsSubmitting] = useState(false)

  useEffect(() => {
    if (opportunity) {
      setFormData({
        name: opportunity.name,
        value: opportunity.value.toString(),
        probability: opportunity.probability,
        expected_close_date: opportunity.expected_close_date.split('T')[0],
        stage: opportunity.stage,
        notes: opportunity.notes || '',
      })
    } else {
      setFormData({
        name: '',
        value: '',
        probability: 50,
        expected_close_date: '',
        stage: 'prospecting',
        notes: '',
      })
    }
  }, [opportunity, open])

  const handleSubmit = async () => {
    if (!formData.name || !formData.value) return

    setIsSubmitting(true)
    try {
      const payload = {
        name: formData.name,
        value: parseFloat(formData.value),
        probability: formData.probability,
        expected_close_date: formData.expected_close_date,
        stage: formData.stage,
        notes: formData.notes || null,
      }

      let response
      if (opportunity) {
        response = await api.put(`/crm/opportunities/${opportunity.id}`, payload)
      } else {
        response = await api.post('/crm/opportunities', payload)
      }

      if (response) {
        onSave(response as Opportunity)
        onOpenChange(false)
      }
    } catch (error) {
      console.error('Failed to save opportunity:', error)
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[600px]">
        <DialogHeader>
          <DialogTitle>{opportunity ? 'Edit Opportunity' : 'Add New Opportunity'}</DialogTitle>
          <DialogDescription>
            {opportunity ? 'Update opportunity details' : 'Create a new sales opportunity'}
          </DialogDescription>
        </DialogHeader>
        <div className="grid gap-4 py-4">
          <div className="space-y-2">
            <Label htmlFor="name">Opportunity Name *</Label>
            <Input
              id="name"
              placeholder="Tech Solutions - ERP Implementation"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="value">Deal Value (INR) *</Label>
              <Input
                id="value"
                type="number"
                placeholder="1000000"
                value={formData.value}
                onChange={(e) => setFormData({ ...formData, value: e.target.value })}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="probability">Win Probability (%)</Label>
              <Input
                id="probability"
                type="number"
                min="0"
                max="100"
                value={formData.probability}
                onChange={(e) => setFormData({ ...formData, probability: parseInt(e.target.value) || 0 })}
              />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="stage">Stage</Label>
              <Select
                value={formData.stage}
                onValueChange={(value) => setFormData({ ...formData, stage: value })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select stage" />
                </SelectTrigger>
                <SelectContent>
                  {Object.entries(stageConfig).map(([value, { label }]) => (
                    <SelectItem key={value} value={value}>{label}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="expected_close_date">Expected Close Date</Label>
              <Input
                id="expected_close_date"
                type="date"
                value={formData.expected_close_date}
                onChange={(e) => setFormData({ ...formData, expected_close_date: e.target.value })}
              />
            </div>
          </div>
          <div className="space-y-2">
            <Label htmlFor="notes">Notes</Label>
            <Input
              id="notes"
              placeholder="Additional details about this opportunity..."
              value={formData.notes}
              onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
            />
          </div>
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)} disabled={isSubmitting}>
            Cancel
          </Button>
          <Button onClick={handleSubmit} disabled={isSubmitting || !formData.name || !formData.value}>
            {isSubmitting ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                {opportunity ? 'Updating...' : 'Creating...'}
              </>
            ) : (
              opportunity ? 'Update Opportunity' : 'Create Opportunity'
            )}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

// Opportunity Detail Dialog
function OpportunityDetailDialog({
  opportunity,
  open,
  onOpenChange,
  onEdit,
}: {
  opportunity: Opportunity | null
  open: boolean
  onOpenChange: (open: boolean) => void
  onEdit: () => void
}) {
  if (!opportunity) return null

  const weightedValue = (opportunity.value * opportunity.probability) / 100

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[650px]">
        <DialogHeader>
          <div className="flex items-start justify-between">
            <div>
              <DialogTitle className="text-xl">{opportunity.name}</DialogTitle>
              <DialogDescription className="flex items-center gap-2 mt-1">
                <Briefcase className="h-4 w-4" />
                Sales Opportunity
              </DialogDescription>
            </div>
            <Badge className={stageConfig[opportunity.stage]?.color || 'bg-gray-100'}>
              {stageConfig[opportunity.stage]?.label || opportunity.stage}
            </Badge>
          </div>
        </DialogHeader>

        <div className="space-y-6 py-4">
          {/* Value Info */}
          <div className="grid grid-cols-3 gap-4">
            <Card>
              <CardContent className="p-4">
                <div className="text-sm text-muted-foreground">Deal Value</div>
                <div className="text-xl font-bold mt-1">{formatCurrency(opportunity.value)}</div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4">
                <div className="text-sm text-muted-foreground">Win Probability</div>
                <div className={`text-xl font-bold mt-1 ${getProbabilityColor(opportunity.probability)}`}>
                  {opportunity.probability}%
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-4">
                <div className="text-sm text-muted-foreground">Weighted Value</div>
                <div className="text-xl font-bold mt-1">{formatCurrency(weightedValue)}</div>
              </CardContent>
            </Card>
          </div>

          {/* Progress */}
          <div className="space-y-2">
            <Label className="text-xs text-muted-foreground">Stage Progress</Label>
            <div className="space-y-1">
              <Progress value={(stageConfig[opportunity.stage]?.order / 6) * 100} className="h-2" />
              <div className="flex justify-between text-xs text-muted-foreground">
                <span>Prospecting</span>
                <span>Closed</span>
              </div>
            </div>
          </div>

          {/* Details */}
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1">
              <Label className="text-xs text-muted-foreground">Expected Close Date</Label>
              <div className="flex items-center gap-2">
                <Calendar className="h-4 w-4 text-muted-foreground" />
                <span>{formatDate(opportunity.expected_close_date)}</span>
              </div>
            </div>
            <div className="space-y-1">
              <Label className="text-xs text-muted-foreground">Created</Label>
              <div className="flex items-center gap-2">
                <Clock className="h-4 w-4 text-muted-foreground" />
                <span>{formatDate(opportunity.created_at, { format: 'long' })}</span>
              </div>
            </div>
          </div>

          {/* Notes */}
          {opportunity.notes && (
            <div className="space-y-1">
              <Label className="text-xs text-muted-foreground">Notes</Label>
              <div className="p-3 bg-muted/50 rounded-md text-sm">
                {opportunity.notes}
              </div>
            </div>
          )}
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Close
          </Button>
          <Button onClick={onEdit}>
            <Edit className="h-4 w-4 mr-2" />
            Edit Opportunity
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

export default function OpportunitiesPage() {
  const api = useApi()
  const [searchQuery, setSearchQuery] = useState('')
  const [stageFilter, setStageFilter] = useState<string>('all')
  const [opportunities, setOpportunities] = useState<Opportunity[]>(mockOpportunities)
  const [loading, setLoading] = useState(true)

  // Calculate stats
  const stats = {
    totalOpportunities: opportunities.length,
    totalValue: opportunities.reduce((sum, o) => sum + o.value, 0),
    weightedValue: opportunities.reduce((sum, o) => sum + (o.value * o.probability) / 100, 0),
    avgProbability: opportunities.length > 0
      ? Math.round(opportunities.reduce((sum, o) => sum + o.probability, 0) / opportunities.length)
      : 0,
    wonDeals: opportunities.filter(o => o.stage === 'closed_won').length,
  }

  // Dialogs state
  const [addDialogOpen, setAddDialogOpen] = useState(false)
  const [editDialogOpen, setEditDialogOpen] = useState(false)
  const [detailDialogOpen, setDetailDialogOpen] = useState(false)
  const [selectedOpportunity, setSelectedOpportunity] = useState<Opportunity | null>(null)

  // Fetch opportunities from API
  useEffect(() => {
    const fetchData = async () => {
      setLoading(true)
      try {
        const response = await api.get('/crm/opportunities?limit=100')
        if (response?.data && Array.isArray(response.data)) {
          setOpportunities(response.data.length > 0 ? response.data : mockOpportunities)
        }
      } catch (error) {
        console.error('Failed to fetch opportunities:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  // Filter opportunities
  const filteredOpportunities = opportunities.filter((opp) => {
    const matchesSearch = !searchQuery ||
      opp.name.toLowerCase().includes(searchQuery.toLowerCase())

    const matchesStage = stageFilter === 'all' || opp.stage === stageFilter

    return matchesSearch && matchesStage
  })

  const handleViewOpportunity = (opportunity: Opportunity) => {
    setSelectedOpportunity(opportunity)
    setDetailDialogOpen(true)
  }

  const handleEditOpportunity = (opportunity: Opportunity) => {
    setSelectedOpportunity(opportunity)
    setEditDialogOpen(true)
  }

  const handleOpportunitySaved = (savedOpportunity: Opportunity) => {
    if (selectedOpportunity) {
      setOpportunities(prev => prev.map(o => o.id === savedOpportunity.id ? savedOpportunity : o))
    } else {
      setOpportunities(prev => [savedOpportunity, ...prev])
    }
    setSelectedOpportunity(null)
  }

  const handleDeleteOpportunity = async (opportunity: Opportunity) => {
    if (!confirm('Are you sure you want to delete this opportunity?')) return

    try {
      const success = await api.delete(`/crm/opportunities/${opportunity.id}`)
      if (success) {
        setOpportunities(prev => prev.filter(o => o.id !== opportunity.id))
      }
    } catch (error) {
      console.error('Failed to delete opportunity:', error)
    }
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Sales Opportunities"
        description="Track and manage your sales opportunities"
        breadcrumbs={[
          { label: 'CRM', href: '/crm' },
          { label: 'Opportunities' },
        ]}
        actions={
          <Button onClick={() => setAddDialogOpen(true)}>
            <Plus className="h-4 w-4 mr-2" />
            Add Opportunity
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
            title="Total Opportunities"
            value={stats.totalOpportunities}
            icon={Briefcase}
            description="Active deals"
          />
          <StatCard
            title="Pipeline Value"
            value={formatCurrency(stats.totalValue)}
            icon={IndianRupee}
            description="Total deal value"
          />
          <StatCard
            title="Weighted Value"
            value={formatCurrency(stats.weightedValue)}
            icon={BarChart3}
            description="By probability"
          />
          <StatCard
            title="Avg Win Probability"
            value={`${stats.avgProbability}%`}
            icon={TrendingUp}
            description="Across all deals"
          />
          <StatCard
            title="Won Deals"
            value={stats.wonDeals}
            icon={Target}
            description="This period"
            trend={{ value: 12, label: 'vs last month' }}
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
                placeholder="Search opportunities..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-8"
              />
            </div>
            <Select value={stageFilter} onValueChange={setStageFilter}>
              <SelectTrigger className="w-[180px]">
                <Filter className="h-4 w-4 mr-2" />
                <SelectValue placeholder="Stage" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Stages</SelectItem>
                {Object.entries(stageConfig).map(([value, { label }]) => (
                  <SelectItem key={value} value={value}>{label}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Opportunities Table */}
      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Opportunity</TableHead>
                <TableHead>Stage</TableHead>
                <TableHead className="text-right">Deal Value</TableHead>
                <TableHead className="text-center">Probability</TableHead>
                <TableHead className="text-right">Weighted Value</TableHead>
                <TableHead>Expected Close</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredOpportunities.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={7} className="text-center py-8 text-muted-foreground">
                    No opportunities found
                  </TableCell>
                </TableRow>
              ) : (
                filteredOpportunities.map((opportunity) => (
                  <TableRow key={opportunity.id}>
                    <TableCell>
                      <div>
                        <p className="font-medium">{opportunity.name}</p>
                        {opportunity.notes && (
                          <p className="text-xs text-muted-foreground line-clamp-1">{opportunity.notes}</p>
                        )}
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge className={stageConfig[opportunity.stage]?.color || 'bg-gray-100'}>
                        {stageConfig[opportunity.stage]?.label || opportunity.stage}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-right font-medium">
                      {formatCurrency(opportunity.value)}
                    </TableCell>
                    <TableCell className="text-center">
                      <span className={`font-medium ${getProbabilityColor(opportunity.probability)}`}>
                        {opportunity.probability}%
                      </span>
                    </TableCell>
                    <TableCell className="text-right text-muted-foreground">
                      {formatCurrency((opportunity.value * opportunity.probability) / 100)}
                    </TableCell>
                    <TableCell>
                      <span className="text-sm">{formatDate(opportunity.expected_close_date)}</span>
                    </TableCell>
                    <TableCell className="text-right">
                      <div className="flex items-center justify-end gap-1">
                        <Button variant="ghost" size="icon" onClick={() => handleViewOpportunity(opportunity)}>
                          <Eye className="h-4 w-4" />
                        </Button>
                        <Button variant="ghost" size="icon" onClick={() => handleEditOpportunity(opportunity)}>
                          <Edit className="h-4 w-4" />
                        </Button>
                        <Button variant="ghost" size="icon" onClick={() => handleDeleteOpportunity(opportunity)}>
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

      {/* Stage Summary Cards */}
      <div className="grid gap-4 md:grid-cols-6">
        {Object.entries(stageConfig)
          .filter(([key]) => key !== 'closed_lost')
          .map(([stage, config]) => {
            const stageOpps = opportunities.filter(o => o.stage === stage)
            const stageValue = stageOpps.reduce((sum, o) => sum + o.value, 0)
            return (
              <Card key={stage}>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">
                    {config.label}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{stageOpps.length}</div>
                  <p className="text-xs text-muted-foreground mt-1">
                    {formatCurrency(stageValue)}
                  </p>
                </CardContent>
              </Card>
            )
          })}
      </div>

      {/* Dialogs */}
      <OpportunityDialog
        open={addDialogOpen}
        onOpenChange={setAddDialogOpen}
        opportunity={null}
        onSave={handleOpportunitySaved}
      />
      <OpportunityDialog
        open={editDialogOpen}
        onOpenChange={(open) => {
          setEditDialogOpen(open)
          if (!open) setSelectedOpportunity(null)
        }}
        opportunity={selectedOpportunity}
        onSave={handleOpportunitySaved}
      />
      <OpportunityDetailDialog
        opportunity={selectedOpportunity}
        open={detailDialogOpen}
        onOpenChange={(open) => {
          setDetailDialogOpen(open)
          if (!open) setSelectedOpportunity(null)
        }}
        onEdit={() => {
          setDetailDialogOpen(false)
          setEditDialogOpen(true)
        }}
      />
    </div>
  )
}
