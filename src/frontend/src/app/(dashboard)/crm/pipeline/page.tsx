'use client'

import { useState, useEffect, useCallback } from 'react'
import { useApi } from '@/hooks/use-api'
import { PageHeader } from '@/components/layout/page-header'
import { StatCard } from '@/components/layout/stat-card'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { formatCurrency, formatDate } from '@/lib/format'
import type { Lead, LeadStatus, LeadSource, Opportunity } from '@/types'
import {
  Plus,
  Search,
  IndianRupee,
  TrendingUp,
  Target,
  Users,
  Loader2,
  GripVertical,
  MoreHorizontal,
  Edit,
  Phone,
  Mail,
  Calendar,
  ArrowRight,
  Filter,
  BarChart3,
  ChevronRight,
} from 'lucide-react'

// Pipeline stage configuration
interface PipelineStage {
  id: string
  label: string
  color: string
  bgColor: string
  borderColor: string
}

const pipelineStages: PipelineStage[] = [
  { id: 'new', label: 'New Leads', color: 'text-slate-700', bgColor: 'bg-slate-50', borderColor: 'border-slate-200' },
  { id: 'contacted', label: 'Contacted', color: 'text-blue-700', bgColor: 'bg-blue-50', borderColor: 'border-blue-200' },
  { id: 'qualified', label: 'Qualified', color: 'text-purple-700', bgColor: 'bg-purple-50', borderColor: 'border-purple-200' },
  { id: 'proposal', label: 'Proposal', color: 'text-yellow-700', bgColor: 'bg-yellow-50', borderColor: 'border-yellow-200' },
  { id: 'negotiation', label: 'Negotiation', color: 'text-orange-700', bgColor: 'bg-orange-50', borderColor: 'border-orange-200' },
  { id: 'won', label: 'Won', color: 'text-green-700', bgColor: 'bg-green-50', borderColor: 'border-green-200' },
]

// Lead score color
function getScoreColor(score: number): string {
  if (score >= 80) return 'text-green-600 bg-green-100'
  if (score >= 60) return 'text-yellow-600 bg-yellow-100'
  return 'text-red-600 bg-red-100'
}

// Pipeline item type (can be Lead or Opportunity)
interface PipelineItem {
  id: string
  type: 'lead' | 'opportunity'
  name: string
  company_name?: string
  email?: string
  phone?: string
  value?: number
  score?: number
  probability?: number
  stage: string
  source?: LeadSource
  next_follow_up?: string
  expected_close_date?: string
  created_at: string
  updated_at: string
}

// Mock data
const mockPipelineItems: PipelineItem[] = [
  {
    id: '1',
    type: 'lead',
    name: 'Rajesh Kumar',
    company_name: 'Tech Solutions Pvt Ltd',
    email: 'rajesh@techsolutions.in',
    phone: '9876543210',
    value: 500000,
    score: 85,
    stage: 'new',
    source: 'website',
    next_follow_up: '2026-01-20T10:00:00',
    created_at: '2026-01-05T09:30:00',
    updated_at: '2026-01-05T09:30:00',
  },
  {
    id: '2',
    type: 'lead',
    name: 'Priya Sharma',
    company_name: 'Global Mart India',
    email: 'priya@globalmart.co.in',
    phone: '9988776655',
    value: 850000,
    score: 72,
    stage: 'contacted',
    source: 'referral',
    next_follow_up: '2026-01-18T14:00:00',
    created_at: '2026-01-03T11:00:00',
    updated_at: '2026-01-06T10:30:00',
  },
  {
    id: '3',
    type: 'opportunity',
    name: 'Innovate Tech - HRMS',
    company_name: 'Innovate Tech Systems',
    value: 1200000,
    probability: 75,
    stage: 'qualified',
    expected_close_date: '2026-02-15',
    created_at: '2026-01-01T14:00:00',
    updated_at: '2026-01-05T16:00:00',
  },
  {
    id: '4',
    type: 'opportunity',
    name: 'Bharat Finance - ERP Suite',
    company_name: 'Bharat Finance Ltd',
    value: 3500000,
    probability: 80,
    stage: 'proposal',
    expected_close_date: '2026-03-15',
    created_at: '2025-12-20T09:00:00',
    updated_at: '2026-01-04T11:00:00',
  },
  {
    id: '5',
    type: 'opportunity',
    name: 'Sunrise Industries - CRM',
    company_name: 'Sunrise Industries',
    value: 980000,
    probability: 90,
    stage: 'negotiation',
    expected_close_date: '2026-01-25',
    created_at: '2025-12-15T10:00:00',
    updated_at: '2026-01-06T09:00:00',
  },
  {
    id: '6',
    type: 'lead',
    name: 'Meera Nair',
    company_name: 'Coastal Exports',
    email: 'meera@coastalexports.in',
    score: 65,
    stage: 'new',
    source: 'trade_show',
    created_at: '2026-01-08T14:00:00',
    updated_at: '2026-01-08T14:00:00',
  },
  {
    id: '7',
    type: 'lead',
    name: 'Arjun Mehta',
    company_name: 'Quick Retail Solutions',
    email: 'arjun@quickretail.com',
    value: 650000,
    score: 78,
    stage: 'contacted',
    source: 'social_media',
    next_follow_up: '2026-01-19T09:00:00',
    created_at: '2026-01-06T08:00:00',
    updated_at: '2026-01-10T08:00:00',
  },
  {
    id: '8',
    type: 'opportunity',
    name: 'Delta Systems - Payroll',
    company_name: 'Delta Systems',
    value: 750000,
    probability: 60,
    stage: 'qualified',
    expected_close_date: '2026-02-28',
    created_at: '2026-01-02T10:00:00',
    updated_at: '2026-01-08T14:00:00',
  },
  {
    id: '9',
    type: 'opportunity',
    name: 'Precision Mfg - Full Suite',
    company_name: 'Precision Manufacturing',
    value: 2200000,
    probability: 95,
    stage: 'won',
    expected_close_date: '2026-01-10',
    created_at: '2025-11-15T09:00:00',
    updated_at: '2026-01-10T16:00:00',
  },
  {
    id: '10',
    type: 'lead',
    name: 'Kavita Desai',
    company_name: 'Phoenix Enterprises',
    email: 'kavita@phoenix.in',
    score: 82,
    stage: 'qualified',
    source: 'referral',
    next_follow_up: '2026-01-22T11:00:00',
    created_at: '2026-01-04T10:00:00',
    updated_at: '2026-01-12T14:00:00',
  },
]

// Pipeline Card Component
function PipelineCard({
  item,
  onMoveStage,
  onEdit,
}: {
  item: PipelineItem
  onMoveStage: (item: PipelineItem, newStage: string) => void
  onEdit: (item: PipelineItem) => void
}) {
  const [showActions, setShowActions] = useState(false)

  return (
    <Card
      className="cursor-pointer hover:shadow-md transition-all group"
      onMouseEnter={() => setShowActions(true)}
      onMouseLeave={() => setShowActions(false)}
    >
      <CardContent className="p-3">
        <div className="flex items-start justify-between mb-2">
          <div className="flex items-center gap-2">
            <GripVertical className="h-4 w-4 text-muted-foreground opacity-0 group-hover:opacity-100 cursor-grab" />
            <div className="flex-1 min-w-0">
              <p className="font-medium text-sm truncate">{item.name}</p>
              {item.company_name && (
                <p className="text-xs text-muted-foreground truncate">{item.company_name}</p>
              )}
            </div>
          </div>
          <div className="flex items-center gap-1">
            {item.score !== undefined && (
              <Badge variant="outline" className={`text-xs ${getScoreColor(item.score)}`}>
                {item.score}
              </Badge>
            )}
            {item.probability !== undefined && (
              <Badge variant="outline" className="text-xs">
                {item.probability}%
              </Badge>
            )}
          </div>
        </div>

        {item.value && (
          <div className="flex items-center gap-1 text-sm font-medium text-green-600 mb-2">
            <IndianRupee className="h-3 w-3" />
            {formatCurrency(item.value, { showSymbol: false })}
          </div>
        )}

        <div className="flex items-center justify-between text-xs text-muted-foreground">
          <Badge variant="secondary" className="text-xs">
            {item.type === 'lead' ? 'Lead' : 'Opportunity'}
          </Badge>
          {(item.next_follow_up || item.expected_close_date) && (
            <div className="flex items-center gap-1">
              <Calendar className="h-3 w-3" />
              <span>{formatDate(item.next_follow_up || item.expected_close_date || '')}</span>
            </div>
          )}
        </div>

        {/* Quick Actions */}
        {showActions && (
          <div className="flex items-center gap-1 mt-2 pt-2 border-t">
            <Button variant="ghost" size="sm" className="h-7 text-xs" onClick={() => onEdit(item)}>
              <Edit className="h-3 w-3 mr-1" />
              Edit
            </Button>
            <Button
              variant="ghost"
              size="sm"
              className="h-7 text-xs"
              onClick={() => {
                const currentIndex = pipelineStages.findIndex(s => s.id === item.stage)
                if (currentIndex < pipelineStages.length - 1) {
                  onMoveStage(item, pipelineStages[currentIndex + 1].id)
                }
              }}
              disabled={item.stage === 'won'}
            >
              <ArrowRight className="h-3 w-3 mr-1" />
              Move
            </Button>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

// Pipeline Column Component
function PipelineColumn({
  stage,
  items,
  onMoveStage,
  onEditItem,
}: {
  stage: PipelineStage
  items: PipelineItem[]
  onMoveStage: (item: PipelineItem, newStage: string) => void
  onEditItem: (item: PipelineItem) => void
}) {
  const stageItems = items.filter(item => item.stage === stage.id)
  const stageValue = stageItems.reduce((sum, item) => sum + (item.value || 0), 0)

  return (
    <div className={`flex-shrink-0 w-80 rounded-lg border ${stage.borderColor} ${stage.bgColor}`}>
      <div className="p-3 border-b bg-white/50 rounded-t-lg">
        <div className="flex items-center justify-between">
          <div>
            <h3 className={`font-medium text-sm ${stage.color}`}>{stage.label}</h3>
            <p className="text-xs text-muted-foreground mt-0.5">
              {formatCurrency(stageValue)}
            </p>
          </div>
          <Badge variant="secondary" className="text-xs">
            {stageItems.length}
          </Badge>
        </div>
      </div>
      <div className="p-2 space-y-2 max-h-[calc(100vh-400px)] overflow-y-auto">
        {stageItems.map((item) => (
          <PipelineCard
            key={item.id}
            item={item}
            onMoveStage={onMoveStage}
            onEdit={onEditItem}
          />
        ))}
        {stageItems.length === 0 && (
          <div className="text-center py-8 text-xs text-muted-foreground">
            No items in this stage
          </div>
        )}
      </div>
    </div>
  )
}

// Move Stage Dialog
function MoveStageDialog({
  open,
  onOpenChange,
  item,
  onMove,
}: {
  open: boolean
  onOpenChange: (open: boolean) => void
  item: PipelineItem | null
  onMove: (newStage: string) => void
}) {
  const [selectedStage, setSelectedStage] = useState('')

  useEffect(() => {
    if (item) {
      setSelectedStage(item.stage)
    }
  }, [item, open])

  if (!item) return null

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[400px]">
        <DialogHeader>
          <DialogTitle>Move to Stage</DialogTitle>
          <DialogDescription>
            Select the new pipeline stage for "{item.name}"
          </DialogDescription>
        </DialogHeader>
        <div className="py-4">
          <div className="space-y-2">
            {pipelineStages.map((stage) => (
              <div
                key={stage.id}
                className={`flex items-center gap-3 p-3 rounded-lg border cursor-pointer transition-colors ${
                  selectedStage === stage.id
                    ? `${stage.bgColor} ${stage.borderColor}`
                    : 'hover:bg-muted/50'
                }`}
                onClick={() => setSelectedStage(stage.id)}
              >
                <div className={`w-3 h-3 rounded-full ${stage.bgColor} border-2 ${stage.borderColor}`} />
                <span className={`font-medium ${selectedStage === stage.id ? stage.color : ''}`}>
                  {stage.label}
                </span>
                {item.stage === stage.id && (
                  <Badge variant="secondary" className="ml-auto text-xs">Current</Badge>
                )}
              </div>
            ))}
          </div>
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button
            onClick={() => {
              onMove(selectedStage)
              onOpenChange(false)
            }}
            disabled={selectedStage === item.stage}
          >
            Move to Stage
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

export default function PipelinePage() {
  const api = useApi()
  const [searchQuery, setSearchQuery] = useState('')
  const [typeFilter, setTypeFilter] = useState<string>('all')
  const [pipelineItems, setPipelineItems] = useState<PipelineItem[]>(mockPipelineItems)
  const [loading, setLoading] = useState(true)

  // Move stage dialog
  const [moveDialogOpen, setMoveDialogOpen] = useState(false)
  const [selectedItem, setSelectedItem] = useState<PipelineItem | null>(null)

  // Calculate statistics
  const stats = {
    totalItems: pipelineItems.length,
    totalValue: pipelineItems.reduce((sum, item) => sum + (item.value || 0), 0),
    weightedValue: pipelineItems.reduce((sum, item) => {
      const probability = item.probability || (item.score ? item.score / 100 : 0.5)
      return sum + (item.value || 0) * probability
    }, 0),
    avgScore: pipelineItems.filter(i => i.score).length > 0
      ? Math.round(
          pipelineItems.filter(i => i.score).reduce((sum, i) => sum + (i.score || 0), 0) /
          pipelineItems.filter(i => i.score).length
        )
      : 0,
    wonValue: pipelineItems
      .filter(i => i.stage === 'won')
      .reduce((sum, i) => sum + (i.value || 0), 0),
  }

  // Fetch pipeline data
  useEffect(() => {
    const fetchData = async () => {
      setLoading(true)
      try {
        // Fetch both leads and opportunities for the pipeline
        const [leadsResponse, opportunitiesResponse] = await Promise.all([
          api.get('/crm/leads?limit=100'),
          api.get('/crm/opportunities?limit=100'),
        ])

        const items: PipelineItem[] = []

        if (leadsResponse?.data && Array.isArray(leadsResponse.data)) {
          leadsResponse.data.forEach((lead: any) => {
            items.push({
              id: lead.id,
              type: 'lead',
              name: lead.contact_name,
              company_name: lead.company_name,
              email: lead.email,
              phone: lead.phone,
              value: lead.expected_value ? parseFloat(lead.expected_value) : undefined,
              score: lead.score,
              stage: lead.status,
              source: lead.source,
              next_follow_up: lead.expected_close_date,
              created_at: lead.created_at,
              updated_at: lead.updated_at,
            })
          })
        }

        if (opportunitiesResponse?.data && Array.isArray(opportunitiesResponse.data)) {
          opportunitiesResponse.data.forEach((opp: any) => {
            items.push({
              id: opp.id,
              type: 'opportunity',
              name: opp.name,
              company_name: opp.customer_name,
              value: opp.value,
              probability: opp.probability,
              stage: opp.stage,
              expected_close_date: opp.expected_close_date,
              created_at: opp.created_at,
              updated_at: opp.updated_at,
            })
          })
        }

        setPipelineItems(items.length > 0 ? items : mockPipelineItems)
      } catch (error) {
        console.error('Failed to fetch pipeline data:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  // Filter items
  const filteredItems = pipelineItems.filter((item) => {
    const matchesSearch = !searchQuery ||
      item.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.company_name?.toLowerCase().includes(searchQuery.toLowerCase())

    const matchesType = typeFilter === 'all' || item.type === typeFilter

    return matchesSearch && matchesType
  })

  const handleMoveStage = useCallback((item: PipelineItem, newStage: string) => {
    setSelectedItem(item)
    // For quick move from card button
    if (newStage) {
      setPipelineItems(prev =>
        prev.map(i => i.id === item.id ? { ...i, stage: newStage, updated_at: new Date().toISOString() } : i)
      )
      // API call would go here
      api.patch(`/crm/${item.type === 'lead' ? 'leads' : 'opportunities'}/${item.id}`, {
        [item.type === 'lead' ? 'status' : 'stage']: newStage,
      }).catch(console.error)
    } else {
      setMoveDialogOpen(true)
    }
  }, [api])

  const handleMoveConfirm = (newStage: string) => {
    if (!selectedItem) return

    setPipelineItems(prev =>
      prev.map(item =>
        item.id === selectedItem.id
          ? { ...item, stage: newStage, updated_at: new Date().toISOString() }
          : item
      )
    )

    // API call
    api.patch(`/crm/${selectedItem.type === 'lead' ? 'leads' : 'opportunities'}/${selectedItem.id}`, {
      [selectedItem.type === 'lead' ? 'status' : 'stage']: newStage,
    }).catch(console.error)

    setSelectedItem(null)
  }

  const handleEditItem = (item: PipelineItem) => {
    // Navigate to edit page or open edit dialog
    const url = item.type === 'lead' ? `/crm/leads?edit=${item.id}` : `/crm/opportunities?edit=${item.id}`
    window.location.href = url
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Sales Pipeline"
        description="Visual overview of your sales funnel"
        breadcrumbs={[
          { label: 'CRM', href: '/crm' },
          { label: 'Pipeline' },
        ]}
        actions={
          <div className="flex gap-2">
            <Button variant="outline" onClick={() => window.location.href = '/crm/leads'}>
              <Plus className="h-4 w-4 mr-2" />
              Add Lead
            </Button>
            <Button onClick={() => window.location.href = '/crm/opportunities'}>
              <Plus className="h-4 w-4 mr-2" />
              Add Opportunity
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
            title="Pipeline Items"
            value={stats.totalItems}
            icon={Users}
            description="Leads & Opportunities"
          />
          <StatCard
            title="Total Value"
            value={formatCurrency(stats.totalValue)}
            icon={IndianRupee}
            description="All stages"
          />
          <StatCard
            title="Weighted Value"
            value={formatCurrency(stats.weightedValue)}
            icon={BarChart3}
            description="By probability"
          />
          <StatCard
            title="Avg Lead Score"
            value={stats.avgScore}
            icon={Target}
            description="Quality indicator"
          />
          <StatCard
            title="Won This Period"
            value={formatCurrency(stats.wonValue)}
            icon={TrendingUp}
            description="Closed deals"
            trend={{ value: 18, label: 'vs last month' }}
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
                placeholder="Search pipeline..."
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
                <SelectItem value="lead">Leads Only</SelectItem>
                <SelectItem value="opportunity">Opportunities Only</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Pipeline Kanban Board */}
      <div className="flex gap-4 overflow-x-auto pb-4">
        {pipelineStages.map((stage) => (
          <PipelineColumn
            key={stage.id}
            stage={stage}
            items={filteredItems}
            onMoveStage={handleMoveStage}
            onEditItem={handleEditItem}
          />
        ))}
      </div>

      {/* Stage Summary */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Pipeline Summary</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-6">
            {pipelineStages.map((stage, index) => {
              const stageItems = filteredItems.filter(item => item.stage === stage.id)
              const stageValue = stageItems.reduce((sum, item) => sum + (item.value || 0), 0)
              const percentage = stats.totalValue > 0 ? (stageValue / stats.totalValue) * 100 : 0

              return (
                <div key={stage.id} className="relative">
                  <div className={`p-4 rounded-lg ${stage.bgColor} border ${stage.borderColor}`}>
                    <div className="flex items-center justify-between mb-2">
                      <span className={`text-sm font-medium ${stage.color}`}>{stage.label}</span>
                      <Badge variant="secondary" className="text-xs">{stageItems.length}</Badge>
                    </div>
                    <div className="text-lg font-bold">{formatCurrency(stageValue)}</div>
                    <div className="text-xs text-muted-foreground mt-1">
                      {percentage.toFixed(1)}% of pipeline
                    </div>
                  </div>
                  {index < pipelineStages.length - 1 && (
                    <ChevronRight className="absolute -right-3 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground hidden md:block" />
                  )}
                </div>
              )
            })}
          </div>
        </CardContent>
      </Card>

      {/* Move Stage Dialog */}
      <MoveStageDialog
        open={moveDialogOpen}
        onOpenChange={setMoveDialogOpen}
        item={selectedItem}
        onMove={handleMoveConfirm}
      />
    </div>
  )
}
