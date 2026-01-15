'use client'

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import { Switch } from '@/components/ui/switch'
import { Progress } from '@/components/ui/progress'
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
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from '@/components/ui/tabs'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
} from '@/components/ui/dropdown-menu'
import {
  Flag,
  Plus,
  MoreHorizontal,
  Edit,
  Trash2,
  Copy,
  Search,
  Users,
  Building2,
  Beaker,
  Rocket,
  History,
  ChevronRight,
  ToggleLeft,
  ToggleRight,
  Percent,
  AlertCircle,
} from 'lucide-react'
import { format } from 'date-fns'

type FlagStatus = 'enabled' | 'disabled' | 'percentage' | 'specific'
type RolloutStrategy = 'all' | 'percentage' | 'specific_tenants' | 'specific_plans' | 'beta_users'

interface FeatureFlag {
  id: string
  key: string
  name: string
  description: string
  category: string
  status: FlagStatus
  rolloutPercentage?: number
  targetTenants?: string[]
  targetPlans?: string[]
  createdAt: Date
  updatedAt: Date
  createdBy: string
  enabledCount: number
  totalTenants: number
}

interface FlagOverride {
  tenantId: string
  tenantName: string
  enabled: boolean
  overriddenAt: Date
  overriddenBy: string
}

// Mock feature flags data
const mockFlags: FeatureFlag[] = [
  {
    id: '1',
    key: 'ai_document_extraction',
    name: 'AI Document Extraction',
    description: 'Enable AI-powered document extraction for invoices, receipts, and contracts',
    category: 'AI Features',
    status: 'percentage',
    rolloutPercentage: 75,
    createdAt: new Date('2025-11-01'),
    updatedAt: new Date('2026-01-10'),
    createdBy: 'Platform Admin',
    enabledCount: 52,
    totalTenants: 68,
  },
  {
    id: '2',
    key: 'natural_language_queries',
    name: 'Natural Language Queries',
    description: 'Allow users to query data using natural language instead of filters',
    category: 'AI Features',
    status: 'specific',
    targetPlans: ['Professional', 'Enterprise'],
    createdAt: new Date('2025-10-15'),
    updatedAt: new Date('2026-01-05'),
    createdBy: 'Platform Admin',
    enabledCount: 35,
    totalTenants: 68,
  },
  {
    id: '3',
    key: 'advanced_analytics',
    name: 'Advanced Analytics Dashboard',
    description: 'Enable advanced analytics with predictive insights and trend analysis',
    category: 'Analytics',
    status: 'enabled',
    createdAt: new Date('2025-09-01'),
    updatedAt: new Date('2025-12-20'),
    createdBy: 'Platform Admin',
    enabledCount: 68,
    totalTenants: 68,
  },
  {
    id: '4',
    key: 'multi_currency_support',
    name: 'Multi-Currency Support',
    description: 'Support for multiple currencies with real-time exchange rates',
    category: 'Finance',
    status: 'enabled',
    createdAt: new Date('2025-08-15'),
    updatedAt: new Date('2025-11-10'),
    createdBy: 'Platform Admin',
    enabledCount: 68,
    totalTenants: 68,
  },
  {
    id: '5',
    key: 'mobile_app_beta',
    name: 'Mobile App Beta',
    description: 'Access to the new mobile app beta version',
    category: 'Platform',
    status: 'percentage',
    rolloutPercentage: 25,
    createdAt: new Date('2026-01-01'),
    updatedAt: new Date('2026-01-12'),
    createdBy: 'Platform Admin',
    enabledCount: 17,
    totalTenants: 68,
  },
  {
    id: '6',
    key: 'digital_signatures',
    name: 'Digital Signatures',
    description: 'Enable digital signature workflow for documents',
    category: 'Documents',
    status: 'disabled',
    createdAt: new Date('2025-12-01'),
    updatedAt: new Date('2025-12-01'),
    createdBy: 'Platform Admin',
    enabledCount: 0,
    totalTenants: 68,
  },
  {
    id: '7',
    key: 'bulk_operations',
    name: 'Bulk Operations',
    description: 'Enable bulk create, update, and delete operations',
    category: 'Platform',
    status: 'enabled',
    createdAt: new Date('2025-07-01'),
    updatedAt: new Date('2025-10-15'),
    createdBy: 'Platform Admin',
    enabledCount: 68,
    totalTenants: 68,
  },
  {
    id: '8',
    key: 'api_v2',
    name: 'API Version 2',
    description: 'Access to the new API v2 with improved performance and new endpoints',
    category: 'Platform',
    status: 'percentage',
    rolloutPercentage: 50,
    createdAt: new Date('2025-11-15'),
    updatedAt: new Date('2026-01-08'),
    createdBy: 'Platform Admin',
    enabledCount: 34,
    totalTenants: 68,
  },
]

const mockOverrides: FlagOverride[] = [
  {
    tenantId: '1',
    tenantName: 'Acme Corporation',
    enabled: true,
    overriddenAt: new Date('2026-01-10'),
    overriddenBy: 'Platform Admin',
  },
  {
    tenantId: '2',
    tenantName: 'TechStart Industries',
    enabled: false,
    overriddenAt: new Date('2026-01-08'),
    overriddenBy: 'Platform Admin',
  },
  {
    tenantId: '3',
    tenantName: 'Global Services Ltd',
    enabled: true,
    overriddenAt: new Date('2026-01-05'),
    overriddenBy: 'Support Team',
  },
]

const categories = ['All', 'AI Features', 'Analytics', 'Finance', 'Documents', 'Platform']

const statusConfig: Record<FlagStatus, { label: string; color: string; icon: React.ElementType }> = {
  enabled: { label: 'Enabled', color: 'bg-green-100 text-green-700', icon: ToggleRight },
  disabled: { label: 'Disabled', color: 'bg-gray-100 text-gray-700', icon: ToggleLeft },
  percentage: { label: 'Percentage', color: 'bg-blue-100 text-blue-700', icon: Percent },
  specific: { label: 'Specific', color: 'bg-purple-100 text-purple-700', icon: Users },
}

export default function FeatureFlagsPage() {
  const [flags, setFlags] = useState(mockFlags)
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('All')
  const [createDialogOpen, setCreateDialogOpen] = useState(false)
  const [selectedFlag, setSelectedFlag] = useState<FeatureFlag | null>(null)
  const [overrideDialogOpen, setOverrideDialogOpen] = useState(false)

  // Form state
  const [formData, setFormData] = useState({
    key: '',
    name: '',
    description: '',
    category: 'Platform',
    status: 'disabled' as FlagStatus,
    rolloutPercentage: 0,
  })

  const filteredFlags = flags.filter(flag => {
    const matchesSearch =
      flag.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      flag.key.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesCategory = selectedCategory === 'All' || flag.category === selectedCategory
    return matchesSearch && matchesCategory
  })

  const handleToggleFlag = (id: string) => {
    setFlags(flags.map(flag => {
      if (flag.id === id) {
        const newStatus = flag.status === 'enabled' ? 'disabled' : 'enabled'
        return {
          ...flag,
          status: newStatus,
          enabledCount: newStatus === 'enabled' ? flag.totalTenants : 0,
          updatedAt: new Date(),
        }
      }
      return flag
    }))
  }

  const handleCreate = () => {
    const newFlag: FeatureFlag = {
      id: Date.now().toString(),
      key: formData.key,
      name: formData.name,
      description: formData.description,
      category: formData.category,
      status: formData.status,
      rolloutPercentage: formData.rolloutPercentage,
      createdAt: new Date(),
      updatedAt: new Date(),
      createdBy: 'Platform Admin',
      enabledCount: 0,
      totalTenants: 68,
    }
    setFlags([newFlag, ...flags])
    setCreateDialogOpen(false)
    resetForm()
  }

  const handleDelete = (id: string) => {
    setFlags(flags.filter(f => f.id !== id))
  }

  const resetForm = () => {
    setFormData({
      key: '',
      name: '',
      description: '',
      category: 'Platform',
      status: 'disabled',
      rolloutPercentage: 0,
    })
  }

  const enabledFlags = flags.filter(f => f.status === 'enabled').length
  const rolloutFlags = flags.filter(f => f.status === 'percentage').length

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Feature Flags</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Control feature rollouts and tenant access to platform features
          </p>
        </div>
        <Dialog open={createDialogOpen} onOpenChange={setCreateDialogOpen}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              Create Flag
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-lg">
            <DialogHeader>
              <DialogTitle>Create Feature Flag</DialogTitle>
              <DialogDescription>
                Create a new feature flag to control access to platform features
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="key">Flag Key</Label>
                <Input
                  id="key"
                  placeholder="e.g., new_dashboard_beta"
                  value={formData.key}
                  onChange={(e) => setFormData({ ...formData, key: e.target.value.toLowerCase().replace(/\s+/g, '_') })}
                />
                <p className="text-xs text-gray-500">Use snake_case for the flag key</p>
              </div>
              <div className="space-y-2">
                <Label htmlFor="name">Display Name</Label>
                <Input
                  id="name"
                  placeholder="New Dashboard Beta"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="description">Description</Label>
                <Textarea
                  id="description"
                  placeholder="Describe what this feature flag controls..."
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Category</Label>
                  <Select
                    value={formData.category}
                    onValueChange={(value) => setFormData({ ...formData, category: value })}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {categories.filter(c => c !== 'All').map(cat => (
                        <SelectItem key={cat} value={cat}>{cat}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label>Initial Status</Label>
                  <Select
                    value={formData.status}
                    onValueChange={(value: FlagStatus) => setFormData({ ...formData, status: value })}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="disabled">Disabled</SelectItem>
                      <SelectItem value="enabled">Enabled (All)</SelectItem>
                      <SelectItem value="percentage">Percentage Rollout</SelectItem>
                      <SelectItem value="specific">Specific Tenants</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              {formData.status === 'percentage' && (
                <div className="space-y-2">
                  <Label>Rollout Percentage: {formData.rolloutPercentage}%</Label>
                  <Input
                    type="range"
                    min={0}
                    max={100}
                    value={formData.rolloutPercentage}
                    onChange={(e) => setFormData({ ...formData, rolloutPercentage: parseInt(e.target.value) })}
                    className="w-full"
                  />
                </div>
              )}
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setCreateDialogOpen(false)}>
                Cancel
              </Button>
              <Button onClick={handleCreate} disabled={!formData.key || !formData.name}>
                Create Flag
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
                <p className="text-sm text-gray-500">Total Flags</p>
                <p className="text-2xl font-bold">{flags.length}</p>
              </div>
              <Flag className="h-8 w-8 text-gray-400" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Enabled</p>
                <p className="text-2xl font-bold text-green-600">{enabledFlags}</p>
              </div>
              <ToggleRight className="h-8 w-8 text-green-400" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">In Rollout</p>
                <p className="text-2xl font-bold text-blue-600">{rolloutFlags}</p>
              </div>
              <Rocket className="h-8 w-8 text-blue-400" />
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-500">Overrides</p>
                <p className="text-2xl font-bold text-purple-600">{mockOverrides.length}</p>
              </div>
              <Building2 className="h-8 w-8 text-purple-400" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-4">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
          <Input
            placeholder="Search flags..."
            className="pl-10"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
        <div className="flex gap-2">
          {categories.map(cat => (
            <Button
              key={cat}
              variant={selectedCategory === cat ? 'default' : 'outline'}
              size="sm"
              onClick={() => setSelectedCategory(cat)}
            >
              {cat}
            </Button>
          ))}
        </div>
      </div>

      {/* Feature Flags Table */}
      <Card>
        <CardHeader>
          <CardTitle>Feature Flags</CardTitle>
          <CardDescription>
            Manage feature availability across the platform
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Feature</TableHead>
                <TableHead>Key</TableHead>
                <TableHead>Category</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Rollout</TableHead>
                <TableHead>Last Updated</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredFlags.map((flag) => {
                const StatusIcon = statusConfig[flag.status].icon
                const rolloutPercent = flag.status === 'enabled'
                  ? 100
                  : flag.status === 'disabled'
                  ? 0
                  : flag.status === 'percentage'
                  ? flag.rolloutPercentage || 0
                  : Math.round((flag.enabledCount / flag.totalTenants) * 100)

                return (
                  <TableRow key={flag.id}>
                    <TableCell>
                      <div>
                        <p className="font-medium">{flag.name}</p>
                        <p className="text-sm text-gray-500 max-w-xs truncate">{flag.description}</p>
                      </div>
                    </TableCell>
                    <TableCell>
                      <code className="px-2 py-1 bg-gray-100 dark:bg-gray-800 rounded text-sm">
                        {flag.key}
                      </code>
                    </TableCell>
                    <TableCell>
                      <Badge variant="outline">{flag.category}</Badge>
                    </TableCell>
                    <TableCell>
                      <div className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full ${statusConfig[flag.status].color}`}>
                        <StatusIcon className="h-3.5 w-3.5" />
                        <span className="text-xs font-medium">
                          {statusConfig[flag.status].label}
                          {flag.status === 'percentage' && ` (${flag.rolloutPercentage}%)`}
                        </span>
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="w-32">
                        <div className="flex items-center justify-between text-xs mb-1">
                          <span>{flag.enabledCount} tenants</span>
                          <span>{rolloutPercent}%</span>
                        </div>
                        <Progress value={rolloutPercent} className="h-2" />
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="text-sm text-gray-500">
                        {format(flag.updatedAt, 'MMM d, yyyy')}
                      </div>
                    </TableCell>
                    <TableCell className="text-right">
                      <div className="flex items-center justify-end gap-2">
                        <Switch
                          checked={flag.status === 'enabled'}
                          onCheckedChange={() => handleToggleFlag(flag.id)}
                          disabled={flag.status === 'percentage' || flag.status === 'specific'}
                        />
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button variant="ghost" size="icon">
                              <MoreHorizontal className="h-4 w-4" />
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end">
                            <DropdownMenuItem onClick={() => setSelectedFlag(flag)}>
                              <Edit className="h-4 w-4 mr-2" />
                              Edit Flag
                            </DropdownMenuItem>
                            <DropdownMenuItem onClick={() => {
                              setSelectedFlag(flag)
                              setOverrideDialogOpen(true)
                            }}>
                              <Building2 className="h-4 w-4 mr-2" />
                              Manage Overrides
                            </DropdownMenuItem>
                            <DropdownMenuItem>
                              <History className="h-4 w-4 mr-2" />
                              View History
                            </DropdownMenuItem>
                            <DropdownMenuItem onClick={() => navigator.clipboard.writeText(flag.key)}>
                              <Copy className="h-4 w-4 mr-2" />
                              Copy Key
                            </DropdownMenuItem>
                            <DropdownMenuSeparator />
                            <DropdownMenuItem
                              className="text-red-600"
                              onClick={() => handleDelete(flag.id)}
                            >
                              <Trash2 className="h-4 w-4 mr-2" />
                              Delete Flag
                            </DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </div>
                    </TableCell>
                  </TableRow>
                )
              })}
            </TableBody>
          </Table>

          {filteredFlags.length === 0 && (
            <div className="text-center py-12">
              <Flag className="h-12 w-12 text-gray-300 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900">No feature flags found</h3>
              <p className="text-gray-500">Try adjusting your search or create a new flag.</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Override Management Dialog */}
      <Dialog open={overrideDialogOpen} onOpenChange={setOverrideDialogOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>
              Tenant Overrides - {selectedFlag?.name}
            </DialogTitle>
            <DialogDescription>
              Override feature flag settings for specific tenants
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div className="flex items-center gap-4">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input placeholder="Search tenants..." className="pl-10" />
              </div>
              <Button variant="outline">
                <Plus className="h-4 w-4 mr-2" />
                Add Override
              </Button>
            </div>

            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Tenant</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Overridden</TableHead>
                  <TableHead>By</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {mockOverrides.map((override) => (
                  <TableRow key={override.tenantId}>
                    <TableCell>
                      <div className="flex items-center gap-2">
                        <Building2 className="h-4 w-4 text-gray-400" />
                        {override.tenantName}
                      </div>
                    </TableCell>
                    <TableCell>
                      <Badge variant={override.enabled ? 'default' : 'secondary'}>
                        {override.enabled ? 'Enabled' : 'Disabled'}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-sm text-gray-500">
                      {format(override.overriddenAt, 'MMM d, yyyy')}
                    </TableCell>
                    <TableCell className="text-sm text-gray-500">
                      {override.overriddenBy}
                    </TableCell>
                    <TableCell className="text-right">
                      <Button variant="ghost" size="sm">
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setOverrideDialogOpen(false)}>
              Close
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Quick Tips */}
      <Card className="bg-blue-50 dark:bg-blue-900/20 border-blue-200">
        <CardContent className="pt-6">
          <div className="flex items-start gap-4">
            <Beaker className="h-6 w-6 text-blue-600" />
            <div>
              <h4 className="font-medium text-blue-900 dark:text-blue-100">Feature Flag Best Practices</h4>
              <ul className="mt-2 text-sm text-blue-700 dark:text-blue-200 space-y-1">
                <li>• Use percentage rollouts for gradual feature releases to minimize risk</li>
                <li>• Always disable flags before deleting them to ensure clean removal</li>
                <li>• Use tenant overrides for beta testing with specific customers</li>
                <li>• Document the purpose of each flag in the description field</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
