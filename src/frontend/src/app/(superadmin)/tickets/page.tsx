'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { Textarea } from '@/components/ui/textarea'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
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
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  Search,
  HeadphonesIcon,
  Clock,
  AlertTriangle,
  CheckCircle,
  MessageSquare,
  RefreshCw,
  Send,
  User,
  Building2,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react'

// Types
interface Ticket {
  id: string
  ticket_number: string
  subject: string
  description: string
  company_name: string | null
  contact_email: string
  status: 'open' | 'in_progress' | 'waiting_customer' | 'resolved' | 'closed'
  priority: 'low' | 'medium' | 'high' | 'urgent' | 'critical'
  assigned_to_name: string | null
  created_at: string
  updated_at: string
  responses: TicketResponse[]
}

interface TicketResponse {
  id: string
  content: string
  admin_name: string | null
  user_name: string | null
  is_internal: boolean
  created_at: string
}

// Status Badge
function StatusBadge({ status }: { status: string }) {
  const variants: Record<string, { class: string; label: string }> = {
    open: { class: 'bg-blue-100 text-blue-700 border-blue-200', label: 'Open' },
    in_progress: { class: 'bg-yellow-100 text-yellow-700 border-yellow-200', label: 'In Progress' },
    waiting_customer: { class: 'bg-purple-100 text-purple-700 border-purple-200', label: 'Waiting' },
    resolved: { class: 'bg-green-100 text-green-700 border-green-200', label: 'Resolved' },
    closed: { class: 'bg-gray-100 text-gray-700 border-gray-200', label: 'Closed' },
  }
  const variant = variants[status] || variants.open
  return <Badge variant="outline" className={variant.class}>{variant.label}</Badge>
}

// Priority Badge
function PriorityBadge({ priority }: { priority: string }) {
  const variants: Record<string, { class: string }> = {
    low: { class: 'bg-gray-100 text-gray-700' },
    medium: { class: 'bg-blue-100 text-blue-700' },
    high: { class: 'bg-yellow-100 text-yellow-700' },
    urgent: { class: 'bg-orange-100 text-orange-700' },
    critical: { class: 'bg-red-100 text-red-700' },
  }
  const variant = variants[priority] || variants.medium
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${variant.class}`}>
      {priority.charAt(0).toUpperCase() + priority.slice(1)}
    </span>
  )
}

export default function TicketsPage() {
  const [isLoading, setIsLoading] = useState(true)
  const [tickets, setTickets] = useState<Ticket[]>([])
  const [searchQuery, setSearchQuery] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')
  const [priorityFilter, setPriorityFilter] = useState('all')
  const [selectedTicket, setSelectedTicket] = useState<Ticket | null>(null)
  const [showDetailDialog, setShowDetailDialog] = useState(false)
  const [newResponse, setNewResponse] = useState('')
  const [isInternal, setIsInternal] = useState(false)
  const [page, setPage] = useState(1)

  const fetchTickets = async () => {
    setIsLoading(true)
    try {
      await new Promise((resolve) => setTimeout(resolve, 500))

      const mockTickets: Ticket[] = [
        {
          id: '1',
          ticket_number: 'TKT-2026-000001',
          subject: 'Cannot access payroll module',
          description: 'Getting error 403 when trying to access payroll. Need urgent help.',
          company_name: 'Acme Corporation',
          contact_email: 'hr@acme.com',
          status: 'open',
          priority: 'high',
          assigned_to_name: null,
          created_at: '2026-01-14T08:30:00Z',
          updated_at: '2026-01-14T08:30:00Z',
          responses: [],
        },
        {
          id: '2',
          ticket_number: 'TKT-2026-000002',
          subject: 'Feature request: Custom reports',
          description: 'Would like to have custom report builder functionality.',
          company_name: 'Tech Solutions Ltd',
          contact_email: 'admin@techsolutions.com',
          status: 'in_progress',
          priority: 'medium',
          assigned_to_name: 'Support Agent',
          created_at: '2026-01-13T14:20:00Z',
          updated_at: '2026-01-14T09:15:00Z',
          responses: [
            {
              id: 'r1',
              content: 'Thank you for your suggestion. We are reviewing this feature request.',
              admin_name: 'Support Agent',
              user_name: null,
              is_internal: false,
              created_at: '2026-01-14T09:15:00Z',
            },
          ],
        },
        {
          id: '3',
          ticket_number: 'TKT-2026-000003',
          subject: 'Billing discrepancy',
          description: 'Invoice amount does not match subscription plan.',
          company_name: 'Global Industries',
          contact_email: 'finance@global.com',
          status: 'waiting_customer',
          priority: 'urgent',
          assigned_to_name: 'Billing Support',
          created_at: '2026-01-12T10:00:00Z',
          updated_at: '2026-01-13T16:00:00Z',
          responses: [
            {
              id: 'r2',
              content: 'We have reviewed your invoice. The difference is due to pro-rated charges for the employee count increase.',
              admin_name: 'Billing Support',
              user_name: null,
              is_internal: false,
              created_at: '2026-01-13T11:00:00Z',
            },
            {
              id: 'r3',
              content: 'Please provide the detailed breakdown.',
              admin_name: null,
              user_name: 'Finance Team',
              is_internal: false,
              created_at: '2026-01-13T14:00:00Z',
            },
          ],
        },
        {
          id: '4',
          ticket_number: 'TKT-2026-000004',
          subject: 'API rate limit issue',
          description: 'Getting rate limited on our integration. Need limit increase.',
          company_name: 'Healthcare Plus',
          contact_email: 'dev@healthplus.com',
          status: 'resolved',
          priority: 'high',
          assigned_to_name: 'Tech Support',
          created_at: '2026-01-11T09:00:00Z',
          updated_at: '2026-01-12T15:00:00Z',
          responses: [],
        },
        {
          id: '5',
          ticket_number: 'TKT-2026-000005',
          subject: 'Login issues after password reset',
          description: 'User cannot login after resetting password.',
          company_name: 'StartupXYZ',
          contact_email: 'support@startupxyz.com',
          status: 'open',
          priority: 'critical',
          assigned_to_name: null,
          created_at: '2026-01-14T10:00:00Z',
          updated_at: '2026-01-14T10:00:00Z',
          responses: [],
        },
      ]

      setTickets(mockTickets)
    } catch (err) {
      console.error('Failed to fetch tickets:', err)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchTickets()
  }, [])

  const filteredTickets = tickets.filter((ticket) => {
    const matchesSearch =
      ticket.subject.toLowerCase().includes(searchQuery.toLowerCase()) ||
      ticket.ticket_number.toLowerCase().includes(searchQuery.toLowerCase()) ||
      ticket.company_name?.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesStatus = statusFilter === 'all' || ticket.status === statusFilter
    const matchesPriority = priorityFilter === 'all' || ticket.priority === priorityFilter
    return matchesSearch && matchesStatus && matchesPriority
  })

  const openTickets = tickets.filter((t) => ['open', 'in_progress', 'waiting_customer'].includes(t.status))
  const criticalTickets = tickets.filter((t) => t.priority === 'critical' && t.status !== 'closed')

  const handleAddResponse = async () => {
    if (!selectedTicket || !newResponse.trim()) return
    console.log('Adding response to ticket:', selectedTicket.id, {
      content: newResponse,
      is_internal: isInternal,
    })
    setNewResponse('')
    // Would refresh ticket details
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold">Support Tickets</h1>
          <p className="text-muted-foreground">Manage customer support requests</p>
        </div>
        <Button onClick={fetchTickets} variant="outline" disabled={isLoading}>
          <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </div>

      {/* Stats */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-100 rounded-lg">
                <HeadphonesIcon className="h-5 w-5 text-blue-600" />
              </div>
              <div>
                <p className="text-2xl font-bold">{openTickets.length}</p>
                <p className="text-sm text-muted-foreground">Open Tickets</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-red-100 rounded-lg">
                <AlertTriangle className="h-5 w-5 text-red-600" />
              </div>
              <div>
                <p className="text-2xl font-bold">{criticalTickets.length}</p>
                <p className="text-sm text-muted-foreground">Critical</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-yellow-100 rounded-lg">
                <Clock className="h-5 w-5 text-yellow-600" />
              </div>
              <div>
                <p className="text-2xl font-bold">4.2h</p>
                <p className="text-sm text-muted-foreground">Avg Resolution</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-green-100 rounded-lg">
                <CheckCircle className="h-5 w-5 text-green-600" />
              </div>
              <div>
                <p className="text-2xl font-bold">
                  {tickets.filter((t) => t.status === 'resolved').length}
                </p>
                <p className="text-sm text-muted-foreground">Resolved Today</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search tickets..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-9"
              />
            </div>
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Statuses</SelectItem>
                <SelectItem value="open">Open</SelectItem>
                <SelectItem value="in_progress">In Progress</SelectItem>
                <SelectItem value="waiting_customer">Waiting</SelectItem>
                <SelectItem value="resolved">Resolved</SelectItem>
                <SelectItem value="closed">Closed</SelectItem>
              </SelectContent>
            </Select>
            <Select value={priorityFilter} onValueChange={setPriorityFilter}>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Priority" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Priorities</SelectItem>
                <SelectItem value="critical">Critical</SelectItem>
                <SelectItem value="urgent">Urgent</SelectItem>
                <SelectItem value="high">High</SelectItem>
                <SelectItem value="medium">Medium</SelectItem>
                <SelectItem value="low">Low</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Tickets Table */}
      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Ticket</TableHead>
                <TableHead>Company</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Priority</TableHead>
                <TableHead>Assigned To</TableHead>
                <TableHead>Created</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {isLoading ? (
                <TableRow>
                  <TableCell colSpan={6} className="text-center py-8">
                    <RefreshCw className="h-6 w-6 animate-spin mx-auto text-muted-foreground" />
                  </TableCell>
                </TableRow>
              ) : filteredTickets.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} className="text-center py-8">
                    <HeadphonesIcon className="h-8 w-8 mx-auto text-muted-foreground" />
                    <p className="mt-2 text-muted-foreground">No tickets found</p>
                  </TableCell>
                </TableRow>
              ) : (
                filteredTickets.map((ticket) => (
                  <TableRow
                    key={ticket.id}
                    className="cursor-pointer hover:bg-muted/50"
                    onClick={() => {
                      setSelectedTicket(ticket)
                      setShowDetailDialog(true)
                    }}
                  >
                    <TableCell>
                      <div>
                        <p className="font-medium">{ticket.subject}</p>
                        <p className="text-xs text-muted-foreground">{ticket.ticket_number}</p>
                      </div>
                    </TableCell>
                    <TableCell>{ticket.company_name || '-'}</TableCell>
                    <TableCell>
                      <StatusBadge status={ticket.status} />
                    </TableCell>
                    <TableCell>
                      <PriorityBadge priority={ticket.priority} />
                    </TableCell>
                    <TableCell>{ticket.assigned_to_name || 'Unassigned'}</TableCell>
                    <TableCell>
                      {new Date(ticket.created_at).toLocaleDateString()}
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>

          <div className="flex items-center justify-between px-4 py-4 border-t">
            <p className="text-sm text-muted-foreground">
              Showing {filteredTickets.length} tickets
            </p>
            <div className="flex items-center gap-2">
              <Button variant="outline" size="sm" disabled={page === 1}>
                <ChevronLeft className="h-4 w-4" />
              </Button>
              <span className="text-sm">Page {page}</span>
              <Button variant="outline" size="sm">
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Ticket Detail Dialog */}
      <Dialog open={showDetailDialog} onOpenChange={setShowDetailDialog}>
        <DialogContent className="max-w-3xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <span>{selectedTicket?.ticket_number}</span>
              {selectedTicket && <StatusBadge status={selectedTicket.status} />}
              {selectedTicket && <PriorityBadge priority={selectedTicket.priority} />}
            </DialogTitle>
            <DialogDescription>{selectedTicket?.subject}</DialogDescription>
          </DialogHeader>

          {selectedTicket && (
            <div className="space-y-6 mt-4">
              {/* Ticket Info */}
              <div className="grid grid-cols-2 gap-4 p-4 bg-muted/50 rounded-lg">
                <div className="flex items-center gap-2">
                  <Building2 className="h-4 w-4 text-muted-foreground" />
                  <span className="text-sm">{selectedTicket.company_name || 'Unknown'}</span>
                </div>
                <div className="flex items-center gap-2">
                  <User className="h-4 w-4 text-muted-foreground" />
                  <span className="text-sm">{selectedTicket.contact_email}</span>
                </div>
              </div>

              {/* Description */}
              <div>
                <h4 className="font-medium mb-2">Description</h4>
                <p className="text-sm text-muted-foreground">{selectedTicket.description}</p>
              </div>

              {/* Conversation */}
              <div>
                <h4 className="font-medium mb-4">Conversation</h4>
                <div className="space-y-4">
                  {selectedTicket.responses.length === 0 ? (
                    <p className="text-sm text-muted-foreground text-center py-4">
                      No responses yet
                    </p>
                  ) : (
                    selectedTicket.responses.map((resp) => (
                      <div
                        key={resp.id}
                        className={`p-4 rounded-lg ${
                          resp.admin_name
                            ? 'bg-primary/5 border-l-4 border-primary'
                            : 'bg-muted/50'
                        } ${resp.is_internal ? 'border-l-4 border-yellow-400' : ''}`}
                      >
                        <div className="flex items-center justify-between mb-2">
                          <span className="font-medium text-sm">
                            {resp.admin_name || resp.user_name || 'System'}
                            {resp.is_internal && (
                              <Badge variant="outline" className="ml-2 text-xs">
                                Internal
                              </Badge>
                            )}
                          </span>
                          <span className="text-xs text-muted-foreground">
                            {new Date(resp.created_at).toLocaleString()}
                          </span>
                        </div>
                        <p className="text-sm">{resp.content}</p>
                      </div>
                    ))
                  )}
                </div>
              </div>

              {/* Add Response */}
              <div className="space-y-3 pt-4 border-t">
                <Textarea
                  placeholder="Write your response..."
                  value={newResponse}
                  onChange={(e) => setNewResponse(e.target.value)}
                  rows={3}
                />
                <div className="flex items-center justify-between">
                  <label className="flex items-center gap-2 text-sm">
                    <input
                      type="checkbox"
                      checked={isInternal}
                      onChange={(e) => setIsInternal(e.target.checked)}
                      className="rounded"
                    />
                    Internal note (not visible to customer)
                  </label>
                  <Button onClick={handleAddResponse} disabled={!newResponse.trim()}>
                    <Send className="h-4 w-4 mr-2" />
                    Send Response
                  </Button>
                </div>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  )
}
