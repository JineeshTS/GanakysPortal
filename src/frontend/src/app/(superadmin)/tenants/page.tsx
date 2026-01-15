'use client'

import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
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
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
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
  MoreVertical,
  Building2,
  Users,
  Eye,
  Ban,
  CheckCircle,
  AlertTriangle,
  ExternalLink,
  RefreshCw,
  UserPlus,
  Filter,
  Download,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react'

// Types
interface Tenant {
  id: string
  company_id: string
  company_name: string
  status: 'active' | 'suspended' | 'pending' | 'churned'
  health_status: 'healthy' | 'at_risk' | 'critical'
  plan_name: string
  employee_count: number
  user_count: number
  mrr: number
  last_active_at: string | null
  created_at: string
  tags: string[]
}

// Status Badge
function StatusBadge({ status }: { status: string }) {
  const variants: Record<string, { class: string; label: string }> = {
    active: { class: 'bg-green-100 text-green-700 border-green-200', label: 'Active' },
    suspended: { class: 'bg-red-100 text-red-700 border-red-200', label: 'Suspended' },
    pending: { class: 'bg-yellow-100 text-yellow-700 border-yellow-200', label: 'Pending' },
    churned: { class: 'bg-gray-100 text-gray-700 border-gray-200', label: 'Churned' },
  }

  const variant = variants[status] || variants.pending
  return <Badge variant="outline" className={variant.class}>{variant.label}</Badge>
}

// Health Badge
function HealthBadge({ status }: { status: string }) {
  const variants: Record<string, { class: string; icon: React.ReactNode }> = {
    healthy: {
      class: 'bg-green-50 text-green-700',
      icon: <CheckCircle className="h-3 w-3 mr-1" />,
    },
    at_risk: {
      class: 'bg-yellow-50 text-yellow-700',
      icon: <AlertTriangle className="h-3 w-3 mr-1" />,
    },
    critical: {
      class: 'bg-red-50 text-red-700',
      icon: <AlertTriangle className="h-3 w-3 mr-1" />,
    },
  }

  const variant = variants[status] || variants.healthy
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${variant.class}`}>
      {variant.icon}
      {status.charAt(0).toUpperCase() + status.slice(1).replace('_', ' ')}
    </span>
  )
}

export default function TenantsPage() {
  const [isLoading, setIsLoading] = useState(true)
  const [tenants, setTenants] = useState<Tenant[]>([])
  const [searchQuery, setSearchQuery] = useState('')
  const [statusFilter, setStatusFilter] = useState('all')
  const [healthFilter, setHealthFilter] = useState('all')
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [selectedTenant, setSelectedTenant] = useState<Tenant | null>(null)
  const [showDetailDialog, setShowDetailDialog] = useState(false)
  const [showSuspendDialog, setShowSuspendDialog] = useState(false)
  const [suspendReason, setSuspendReason] = useState('')

  const fetchTenants = async () => {
    setIsLoading(true)
    try {
      // Mock data - in production would fetch from API
      await new Promise((resolve) => setTimeout(resolve, 500))

      const mockTenants: Tenant[] = [
        {
          id: '1',
          company_id: 'c1',
          company_name: 'Acme Corporation',
          status: 'active',
          health_status: 'healthy',
          plan_name: 'Professional',
          employee_count: 150,
          user_count: 25,
          mrr: 44850,
          last_active_at: '2026-01-14T10:30:00Z',
          created_at: '2025-06-15T00:00:00Z',
          tags: ['enterprise', 'priority'],
        },
        {
          id: '2',
          company_id: 'c2',
          company_name: 'Tech Solutions Ltd',
          status: 'active',
          health_status: 'at_risk',
          plan_name: 'Starter',
          employee_count: 45,
          user_count: 8,
          mrr: 8955,
          last_active_at: '2026-01-10T14:20:00Z',
          created_at: '2025-09-01T00:00:00Z',
          tags: ['startup'],
        },
        {
          id: '3',
          company_id: 'c3',
          company_name: 'Global Industries',
          status: 'active',
          health_status: 'healthy',
          plan_name: 'Enterprise',
          employee_count: 500,
          user_count: 75,
          mrr: 199500,
          last_active_at: '2026-01-14T09:00:00Z',
          created_at: '2025-03-10T00:00:00Z',
          tags: ['enterprise', 'manufacturing'],
        },
        {
          id: '4',
          company_id: 'c4',
          company_name: 'StartupXYZ',
          status: 'pending',
          health_status: 'healthy',
          plan_name: 'Free',
          employee_count: 5,
          user_count: 2,
          mrr: 0,
          last_active_at: '2026-01-13T16:45:00Z',
          created_at: '2026-01-10T00:00:00Z',
          tags: ['trial'],
        },
        {
          id: '5',
          company_id: 'c5',
          company_name: 'Old Company Inc',
          status: 'suspended',
          health_status: 'critical',
          plan_name: 'Professional',
          employee_count: 80,
          user_count: 15,
          mrr: 0,
          last_active_at: '2025-12-01T00:00:00Z',
          created_at: '2024-06-01T00:00:00Z',
          tags: [],
        },
        {
          id: '6',
          company_id: 'c6',
          company_name: 'Healthcare Plus',
          status: 'active',
          health_status: 'healthy',
          plan_name: 'Enterprise',
          employee_count: 320,
          user_count: 48,
          mrr: 127680,
          last_active_at: '2026-01-14T11:00:00Z',
          created_at: '2025-01-20T00:00:00Z',
          tags: ['healthcare', 'compliance'],
        },
      ]

      setTenants(mockTenants)
      setTotalPages(3)
    } catch (err) {
      console.error('Failed to fetch tenants:', err)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchTenants()
  }, [page, statusFilter, healthFilter])

  const filteredTenants = tenants.filter((tenant) => {
    const matchesSearch =
      tenant.company_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      tenant.tags.some((tag) => tag.toLowerCase().includes(searchQuery.toLowerCase()))
    const matchesStatus = statusFilter === 'all' || tenant.status === statusFilter
    const matchesHealth = healthFilter === 'all' || tenant.health_status === healthFilter
    return matchesSearch && matchesStatus && matchesHealth
  })

  const handleSuspendTenant = async () => {
    if (!selectedTenant || !suspendReason) return
    // Would call API to suspend tenant
    console.log('Suspending tenant:', selectedTenant.id, 'Reason:', suspendReason)
    setShowSuspendDialog(false)
    setSuspendReason('')
    setSelectedTenant(null)
    fetchTenants()
  }

  const handleActivateTenant = async (tenant: Tenant) => {
    // Would call API to activate tenant
    console.log('Activating tenant:', tenant.id)
    fetchTenants()
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold">Tenant Management</h1>
          <p className="text-muted-foreground">Manage all platform tenants</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={fetchTenants} disabled={isLoading}>
            <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
          <Button variant="outline">
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-green-100 rounded-lg">
                <Building2 className="h-5 w-5 text-green-600" />
              </div>
              <div>
                <p className="text-2xl font-bold">
                  {tenants.filter((t) => t.status === 'active').length}
                </p>
                <p className="text-sm text-muted-foreground">Active Tenants</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-yellow-100 rounded-lg">
                <AlertTriangle className="h-5 w-5 text-yellow-600" />
              </div>
              <div>
                <p className="text-2xl font-bold">
                  {tenants.filter((t) => t.health_status === 'at_risk').length}
                </p>
                <p className="text-sm text-muted-foreground">At Risk</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-100 rounded-lg">
                <Users className="h-5 w-5 text-blue-600" />
              </div>
              <div>
                <p className="text-2xl font-bold">
                  {tenants.reduce((sum, t) => sum + t.employee_count, 0).toLocaleString()}
                </p>
                <p className="text-sm text-muted-foreground">Total Employees</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-purple-100 rounded-lg">
                <Building2 className="h-5 w-5 text-purple-600" />
              </div>
              <div>
                <p className="text-2xl font-bold">
                  {tenants.filter((t) => t.status === 'pending').length}
                </p>
                <p className="text-sm text-muted-foreground">Pending Activation</p>
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
                placeholder="Search by name or tag..."
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
                <SelectItem value="active">Active</SelectItem>
                <SelectItem value="pending">Pending</SelectItem>
                <SelectItem value="suspended">Suspended</SelectItem>
                <SelectItem value="churned">Churned</SelectItem>
              </SelectContent>
            </Select>
            <Select value={healthFilter} onValueChange={setHealthFilter}>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Health" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Health</SelectItem>
                <SelectItem value="healthy">Healthy</SelectItem>
                <SelectItem value="at_risk">At Risk</SelectItem>
                <SelectItem value="critical">Critical</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Tenants Table */}
      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Company</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Health</TableHead>
                <TableHead>Plan</TableHead>
                <TableHead className="text-right">Employees</TableHead>
                <TableHead className="text-right">MRR</TableHead>
                <TableHead>Last Active</TableHead>
                <TableHead className="w-[50px]"></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {isLoading ? (
                <TableRow>
                  <TableCell colSpan={8} className="text-center py-8">
                    <RefreshCw className="h-6 w-6 animate-spin mx-auto text-muted-foreground" />
                    <p className="mt-2 text-sm text-muted-foreground">Loading tenants...</p>
                  </TableCell>
                </TableRow>
              ) : filteredTenants.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={8} className="text-center py-8">
                    <Building2 className="h-8 w-8 mx-auto text-muted-foreground" />
                    <p className="mt-2 text-muted-foreground">No tenants found</p>
                  </TableCell>
                </TableRow>
              ) : (
                filteredTenants.map((tenant) => (
                  <TableRow key={tenant.id}>
                    <TableCell>
                      <div>
                        <p className="font-medium">{tenant.company_name}</p>
                        <div className="flex gap-1 mt-1">
                          {tenant.tags.slice(0, 2).map((tag) => (
                            <Badge key={tag} variant="secondary" className="text-xs">
                              {tag}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    </TableCell>
                    <TableCell>
                      <StatusBadge status={tenant.status} />
                    </TableCell>
                    <TableCell>
                      <HealthBadge status={tenant.health_status} />
                    </TableCell>
                    <TableCell>{tenant.plan_name}</TableCell>
                    <TableCell className="text-right">{tenant.employee_count}</TableCell>
                    <TableCell className="text-right font-medium">
                      ₹{tenant.mrr.toLocaleString()}
                    </TableCell>
                    <TableCell>
                      {tenant.last_active_at
                        ? new Date(tenant.last_active_at).toLocaleDateString()
                        : '-'}
                    </TableCell>
                    <TableCell>
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="icon">
                            <MoreVertical className="h-4 w-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuLabel>Actions</DropdownMenuLabel>
                          <DropdownMenuItem
                            onClick={() => {
                              setSelectedTenant(tenant)
                              setShowDetailDialog(true)
                            }}
                          >
                            <Eye className="h-4 w-4 mr-2" />
                            View Details
                          </DropdownMenuItem>
                          <DropdownMenuItem>
                            <UserPlus className="h-4 w-4 mr-2" />
                            Impersonate User
                          </DropdownMenuItem>
                          <DropdownMenuItem>
                            <ExternalLink className="h-4 w-4 mr-2" />
                            Open Dashboard
                          </DropdownMenuItem>
                          <DropdownMenuSeparator />
                          {tenant.status === 'suspended' ? (
                            <DropdownMenuItem
                              onClick={() => handleActivateTenant(tenant)}
                              className="text-green-600"
                            >
                              <CheckCircle className="h-4 w-4 mr-2" />
                              Activate Tenant
                            </DropdownMenuItem>
                          ) : (
                            <DropdownMenuItem
                              onClick={() => {
                                setSelectedTenant(tenant)
                                setShowSuspendDialog(true)
                              }}
                              className="text-red-600"
                            >
                              <Ban className="h-4 w-4 mr-2" />
                              Suspend Tenant
                            </DropdownMenuItem>
                          )}
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>

          {/* Pagination */}
          <div className="flex items-center justify-between px-4 py-4 border-t">
            <p className="text-sm text-muted-foreground">
              Showing {filteredTenants.length} of {tenants.length} tenants
            </p>
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setPage(page - 1)}
                disabled={page === 1}
              >
                <ChevronLeft className="h-4 w-4" />
              </Button>
              <span className="text-sm">
                Page {page} of {totalPages}
              </span>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setPage(page + 1)}
                disabled={page === totalPages}
              >
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Tenant Detail Dialog */}
      <Dialog open={showDetailDialog} onOpenChange={setShowDetailDialog}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>{selectedTenant?.company_name}</DialogTitle>
            <DialogDescription>Tenant details and management</DialogDescription>
          </DialogHeader>

          {selectedTenant && (
            <Tabs defaultValue="overview" className="mt-4">
              <TabsList>
                <TabsTrigger value="overview">Overview</TabsTrigger>
                <TabsTrigger value="subscription">Subscription</TabsTrigger>
                <TabsTrigger value="activity">Activity</TabsTrigger>
              </TabsList>

              <TabsContent value="overview" className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-muted-foreground">Status</p>
                    <StatusBadge status={selectedTenant.status} />
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Health</p>
                    <HealthBadge status={selectedTenant.health_status} />
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Employees</p>
                    <p className="font-medium">{selectedTenant.employee_count}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Users</p>
                    <p className="font-medium">{selectedTenant.user_count}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Created</p>
                    <p className="font-medium">
                      {new Date(selectedTenant.created_at).toLocaleDateString()}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Last Active</p>
                    <p className="font-medium">
                      {selectedTenant.last_active_at
                        ? new Date(selectedTenant.last_active_at).toLocaleDateString()
                        : 'Never'}
                    </p>
                  </div>
                </div>
              </TabsContent>

              <TabsContent value="subscription" className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-muted-foreground">Plan</p>
                    <p className="font-medium">{selectedTenant.plan_name}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">MRR</p>
                    <p className="font-medium">₹{selectedTenant.mrr.toLocaleString()}</p>
                  </div>
                </div>
              </TabsContent>

              <TabsContent value="activity" className="space-y-4">
                <p className="text-muted-foreground">Recent activity will appear here.</p>
              </TabsContent>
            </Tabs>
          )}

          <DialogFooter>
            <Button variant="outline" onClick={() => setShowDetailDialog(false)}>
              Close
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Suspend Dialog */}
      <Dialog open={showSuspendDialog} onOpenChange={setShowSuspendDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Suspend Tenant</DialogTitle>
            <DialogDescription>
              Are you sure you want to suspend {selectedTenant?.company_name}? Users will lose
              access immediately.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div>
              <label className="text-sm font-medium">Suspension Reason</label>
              <Input
                placeholder="Enter reason for suspension..."
                value={suspendReason}
                onChange={(e) => setSuspendReason(e.target.value)}
                className="mt-1.5"
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowSuspendDialog(false)}>
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={handleSuspendTenant}
              disabled={!suspendReason}
            >
              Suspend Tenant
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
