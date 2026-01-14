'use client'

import { useState, useEffect, useCallback } from 'react'
import { useSearchParams } from 'next/navigation'
import { PageHeader } from '@/components/layout/page-header'
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Skeleton } from '@/components/ui/skeleton'
import { Progress } from '@/components/ui/progress'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Switch } from '@/components/ui/switch'
import { useToast, useAuthStore } from '@/hooks'
import {
  Building2,
  Briefcase,
  Users,
  TrendingUp,
  MapPin,
  Save,
  Loader2,
  Plus,
  Edit,
  Trash2,
  Calendar,
  DollarSign,
  Target,
  Globe,
  Layers,
  Sparkles,
  CheckCircle2,
  AlertCircle,
  Package,
  ChevronRight,
} from 'lucide-react'

// ============================================================================
// Types
// ============================================================================

interface ExtendedProfile {
  id?: string
  company_id?: string
  industry: string | null
  sub_industry: string | null
  company_stage: string | null
  founding_date: string | null
  funding_raised: number | null
  funding_currency: string
  last_funding_round: string | null
  employee_count_current: number
  employee_count_target: number | null
  target_employee_timeline_months: number | null
  growth_rate_percent: number | null
  remote_work_policy: string
  work_locations: string[]
  company_culture: string | null
  tech_focused: boolean
  org_structure_preference: string
  ai_org_builder_enabled: boolean
  last_ai_analysis_at: string | null
  created_at?: string
  updated_at?: string
}

interface Product {
  id: string
  company_id: string
  name: string
  description: string | null
  status: string
  product_type: string
  tech_stack: string[]
  target_market: string | null
  revenue_stage: string | null
  team_size_current: number
  team_size_needed: number | null
  launch_date: string | null
  priority: number
  is_primary: boolean
  created_at: string
  updated_at: string
}

interface SetupStatus {
  company_profile_complete: boolean
  extended_profile_complete: boolean
  products_added: number
  products_minimum: number
  departments_exist: boolean
  designations_exist: boolean
  overall_complete: boolean
  completion_percentage: number
  next_steps: string[]
}

// ============================================================================
// Constants
// ============================================================================

const INDUSTRIES = [
  { value: 'saas', label: 'SaaS' },
  { value: 'fintech', label: 'FinTech' },
  { value: 'edtech', label: 'EdTech' },
  { value: 'healthtech', label: 'HealthTech' },
  { value: 'ecommerce', label: 'E-commerce' },
  { value: 'logistics', label: 'Logistics' },
  { value: 'manufacturing', label: 'Manufacturing' },
  { value: 'consulting', label: 'Consulting' },
  { value: 'media', label: 'Media & Entertainment' },
  { value: 'gaming', label: 'Gaming' },
  { value: 'agritech', label: 'AgriTech' },
  { value: 'proptech', label: 'PropTech' },
  { value: 'hrtech', label: 'HR Tech' },
  { value: 'legaltech', label: 'LegalTech' },
  { value: 'cleantech', label: 'CleanTech' },
  { value: 'other', label: 'Other' },
]

const COMPANY_STAGES = [
  { value: 'idea', label: 'Idea Stage', description: '1-3 people' },
  { value: 'mvp', label: 'MVP', description: '3-10 people' },
  { value: 'seed', label: 'Seed Stage', description: '5-25 people' },
  { value: 'series_a', label: 'Series A', description: '15-60 people' },
  { value: 'series_b', label: 'Series B', description: '40-150 people' },
  { value: 'series_c', label: 'Series C', description: '100-300 people' },
  { value: 'growth', label: 'Growth Stage', description: '150-500 people' },
  { value: 'enterprise', label: 'Enterprise', description: '300+ people' },
]

const FUNDING_ROUNDS = [
  { value: 'bootstrapped', label: 'Bootstrapped' },
  { value: 'friends_family', label: 'Friends & Family' },
  { value: 'angel', label: 'Angel Round' },
  { value: 'pre_seed', label: 'Pre-Seed' },
  { value: 'seed', label: 'Seed' },
  { value: 'series_a', label: 'Series A' },
  { value: 'series_b', label: 'Series B' },
  { value: 'series_c', label: 'Series C' },
  { value: 'series_d', label: 'Series D+' },
  { value: 'ipo', label: 'IPO / Public' },
]

const REMOTE_POLICIES = [
  { value: 'fully_remote', label: 'Fully Remote', description: 'All employees work remotely' },
  { value: 'hybrid', label: 'Hybrid', description: 'Mix of remote and office work' },
  { value: 'office_first', label: 'Office First', description: 'Primarily office-based with some flexibility' },
]

const ORG_STRUCTURES = [
  { value: 'flat', label: 'Flat', description: 'Few management layers, direct communication' },
  { value: 'hierarchical', label: 'Hierarchical', description: 'Traditional pyramid structure' },
  { value: 'matrix', label: 'Matrix', description: 'Multiple reporting lines, project-based' },
]

const PRODUCT_TYPES = [
  { value: 'product', label: 'Product' },
  { value: 'service', label: 'Service' },
  { value: 'platform', label: 'Platform' },
]

const PRODUCT_STATUSES = [
  { value: 'active', label: 'Active' },
  { value: 'planned', label: 'Planned' },
  { value: 'deprecated', label: 'Deprecated' },
  { value: 'sunset', label: 'Sunset' },
]

const REVENUE_STAGES = [
  { value: 'pre_revenue', label: 'Pre-Revenue' },
  { value: 'early_revenue', label: 'Early Revenue' },
  { value: 'growth', label: 'Growth' },
  { value: 'mature', label: 'Mature' },
]

const COMMON_TECH_STACKS = [
  'React', 'Next.js', 'Vue.js', 'Angular', 'Node.js', 'Python', 'Django', 'FastAPI',
  'Java', 'Spring Boot', 'Go', 'Rust', 'Ruby on Rails', 'PHP', 'Laravel',
  'PostgreSQL', 'MySQL', 'MongoDB', 'Redis', 'Elasticsearch',
  'AWS', 'GCP', 'Azure', 'Docker', 'Kubernetes', 'Terraform',
  'React Native', 'Flutter', 'Swift', 'Kotlin',
]

const DEFAULT_PROFILE: ExtendedProfile = {
  industry: null,
  sub_industry: null,
  company_stage: null,
  founding_date: null,
  funding_raised: null,
  funding_currency: 'INR',
  last_funding_round: null,
  employee_count_current: 0,
  employee_count_target: null,
  target_employee_timeline_months: null,
  growth_rate_percent: null,
  remote_work_policy: 'hybrid',
  work_locations: [],
  company_culture: null,
  tech_focused: true,
  org_structure_preference: 'flat',
  ai_org_builder_enabled: true,
  last_ai_analysis_at: null,
}

// ============================================================================
// Helper Functions
// ============================================================================

function formatCurrency(amount: number | null): string {
  if (!amount) return '-'
  // Format in Lakhs/Crores for Indian market
  if (amount >= 10000000) {
    return `₹${(amount / 10000000).toFixed(1)} Cr`
  } else if (amount >= 100000) {
    return `₹${(amount / 100000).toFixed(1)} L`
  }
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(amount)
}

function getStageColor(stage: string | null): string {
  const colors: Record<string, string> = {
    idea: 'bg-gray-100 text-gray-800',
    mvp: 'bg-blue-100 text-blue-800',
    seed: 'bg-green-100 text-green-800',
    series_a: 'bg-yellow-100 text-yellow-800',
    series_b: 'bg-orange-100 text-orange-800',
    series_c: 'bg-red-100 text-red-800',
    growth: 'bg-purple-100 text-purple-800',
    enterprise: 'bg-indigo-100 text-indigo-800',
  }
  return colors[stage || ''] || 'bg-gray-100 text-gray-800'
}

// ============================================================================
// Main Component
// ============================================================================

export default function CompanyProfilePage() {
  const searchParams = useSearchParams()
  const { accessToken } = useAuthStore()
  const { showToast } = useToast()
  const API_BASE = process.env.NEXT_PUBLIC_API_URL || '/api/v1'

  // Get initial tab from URL
  const initialTab = searchParams.get('tab') || 'profile'
  const [activeTab, setActiveTab] = useState(initialTab)

  // State
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  const [profile, setProfile] = useState<ExtendedProfile | null>(null)
  const [products, setProducts] = useState<Product[]>([])
  const [setupStatus, setSetupStatus] = useState<SetupStatus | null>(null)
  const [hasChanges, setHasChanges] = useState(false)

  // Product dialog state
  const [showProductDialog, setShowProductDialog] = useState(false)
  const [editingProduct, setEditingProduct] = useState<Product | null>(null)
  const [productForm, setProductForm] = useState({
    name: '',
    description: '',
    status: 'active',
    product_type: 'product',
    tech_stack: [] as string[],
    target_market: '',
    revenue_stage: '',
    team_size_current: 0,
    team_size_needed: 0,
    is_primary: false,
    priority: 0,
  })

  // API helper functions
  const apiGet = useCallback(async (endpoint: string) => {
    const response = await fetch(`${API_BASE}${endpoint}`, {
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json',
      },
    })
    if (!response.ok) {
      if (response.status === 404) return null
      throw new Error('Request failed')
    }
    return response.json()
  }, [API_BASE, accessToken])

  const apiPost = useCallback(async (endpoint: string, data: any) => {
    const response = await fetch(`${API_BASE}${endpoint}`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    })
    if (!response.ok) {
      const err = await response.json().catch(() => ({}))
      throw new Error(err.detail || 'Request failed')
    }
    return response.json()
  }, [API_BASE, accessToken])

  const apiPut = useCallback(async (endpoint: string, data: any) => {
    const response = await fetch(`${API_BASE}${endpoint}`, {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${accessToken}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    })
    if (!response.ok) {
      const err = await response.json().catch(() => ({}))
      throw new Error(err.detail || 'Request failed')
    }
    return response.json()
  }, [API_BASE, accessToken])

  // Fetch data on mount
  const fetchData = useCallback(async () => {
    setIsLoading(true)
    try {
      const [profileRes, productsRes, statusRes] = await Promise.all([
        apiGet('/company/extended-profile').catch(() => null),
        apiGet('/company/products').catch(() => ({ data: [] })),
        apiGet('/company/setup-status').catch(() => null),
      ])

      if (profileRes) {
        setProfile(profileRes as ExtendedProfile)
      } else {
        setProfile(DEFAULT_PROFILE)
      }

      if (productsRes) {
        setProducts((productsRes as any).data || [])
      }

      if (statusRes) {
        setSetupStatus(statusRes as SetupStatus)
      }
    } catch (error) {
      console.error('Failed to load data:', error)
    } finally {
      setIsLoading(false)
    }
  }, [apiGet])

  useEffect(() => {
    fetchData()
  }, [fetchData])

  // Update profile field
  const updateProfile = (field: keyof ExtendedProfile, value: any) => {
    setProfile(prev => prev ? { ...prev, [field]: value } : null)
    setHasChanges(true)
  }

  // Save profile
  const handleSaveProfile = async () => {
    if (!profile) return

    setIsSaving(true)
    try {
      await apiPost('/company/extended-profile', profile)
      showToast('success', 'Saved', 'Company profile updated successfully')
      setHasChanges(false)
      await fetchData()
    } catch (error: any) {
      showToast('error', 'Error', error.message || 'Failed to save profile')
    } finally {
      setIsSaving(false)
    }
  }

  // Product CRUD
  const openProductDialog = (product?: Product) => {
    if (product) {
      setEditingProduct(product)
      setProductForm({
        name: product.name,
        description: product.description || '',
        status: product.status,
        product_type: product.product_type,
        tech_stack: product.tech_stack || [],
        target_market: product.target_market || '',
        revenue_stage: product.revenue_stage || '',
        team_size_current: product.team_size_current,
        team_size_needed: product.team_size_needed || 0,
        is_primary: product.is_primary,
        priority: product.priority,
      })
    } else {
      setEditingProduct(null)
      setProductForm({
        name: '',
        description: '',
        status: 'active',
        product_type: 'product',
        tech_stack: [],
        target_market: '',
        revenue_stage: '',
        team_size_current: 0,
        team_size_needed: 0,
        is_primary: false,
        priority: 0,
      })
    }
    setShowProductDialog(true)
  }

  const handleSaveProduct = async () => {
    if (!productForm.name.trim()) {
      showToast('error', 'Error', 'Product name is required')
      return
    }

    setIsSaving(true)
    try {
      if (editingProduct) {
        await apiPut(`/company/products/${editingProduct.id}`, productForm)
        showToast('success', 'Updated', 'Product updated successfully')
      } else {
        await apiPost('/company/products', productForm)
        showToast('success', 'Created', 'Product created successfully')
      }
      setShowProductDialog(false)
      await fetchData()
    } catch (error: any) {
      showToast('error', 'Error', error.message || 'Failed to save product')
    } finally {
      setIsSaving(false)
    }
  }

  const handleDeleteProduct = async (productId: string) => {
    if (!confirm('Are you sure you want to delete this product?')) return

    try {
      const response = await fetch(`${API_BASE}/company/products/${productId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${accessToken}`,
        },
      })
      if (response.ok) {
        showToast('success', 'Deleted', 'Product deleted successfully')
        await fetchData()
      } else {
        throw new Error('Delete failed')
      }
    } catch (error) {
      showToast('error', 'Error', 'Failed to delete product')
    }
  }

  const toggleTechStack = (tech: string) => {
    setProductForm(prev => ({
      ...prev,
      tech_stack: prev.tech_stack.includes(tech)
        ? prev.tech_stack.filter(t => t !== tech)
        : [...prev.tech_stack, tech],
    }))
  }

  // Loading state
  if (isLoading) {
    return (
      <div className="space-y-6">
        <PageHeader
          title="Company Profile"
          description="Loading..."
        />
        <div className="grid gap-6 md:grid-cols-4">
          {[1, 2, 3, 4].map(i => (
            <Card key={i}>
              <CardContent className="p-6">
                <Skeleton className="h-8 w-24 mb-2" />
                <Skeleton className="h-4 w-32" />
              </CardContent>
            </Card>
          ))}
        </div>
        <Skeleton className="h-96 w-full" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Company Profile"
        description="Configure your company details for AI-powered organizational recommendations"
        breadcrumbs={[
          { label: 'Dashboard', href: '/' },
          { label: 'Settings', href: '/settings' },
          { label: 'Company Profile' },
        ]}
        actions={
          <div className="flex items-center gap-3">
            {hasChanges && (
              <Badge variant="outline" className="text-yellow-600 border-yellow-300">
                Unsaved Changes
              </Badge>
            )}
            <Button onClick={handleSaveProfile} disabled={isSaving || !hasChanges}>
              {isSaving ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Saving...
                </>
              ) : (
                <>
                  <Save className="mr-2 h-4 w-4" />
                  Save Changes
                </>
              )}
            </Button>
          </div>
        }
      />

      {/* Setup Progress */}
      {setupStatus && (
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className={`p-2 rounded-full ${setupStatus.overall_complete ? 'bg-green-100' : 'bg-yellow-100'}`}>
                  {setupStatus.overall_complete ? (
                    <CheckCircle2 className="h-5 w-5 text-green-600" />
                  ) : (
                    <AlertCircle className="h-5 w-5 text-yellow-600" />
                  )}
                </div>
                <div>
                  <h3 className="font-medium">Setup Progress</h3>
                  <p className="text-sm text-muted-foreground">
                    {setupStatus.overall_complete
                      ? 'Your company profile is complete!'
                      : `Complete your profile to use AI Org Builder`}
                  </p>
                </div>
              </div>
              <div className="text-right">
                <span className="text-2xl font-bold">{setupStatus.completion_percentage}%</span>
                <p className="text-sm text-muted-foreground">Complete</p>
              </div>
            </div>
            <Progress value={setupStatus.completion_percentage} className="h-2" />
            {setupStatus.next_steps.length > 0 && (
              <div className="mt-4 flex flex-wrap gap-2">
                {setupStatus.next_steps.map((step, i) => (
                  <Badge key={i} variant="outline" className="text-xs">
                    <ChevronRight className="h-3 w-3 mr-1" />
                    {step}
                  </Badge>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Summary Cards */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-blue-100 rounded-full">
                <Building2 className="h-6 w-6 text-blue-600" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Industry</p>
                <p className="text-lg font-semibold capitalize">
                  {profile?.industry?.replace('_', ' ') || 'Not Set'}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-green-100 rounded-full">
                <TrendingUp className="h-6 w-6 text-green-600" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Stage</p>
                <Badge className={getStageColor(profile?.company_stage || null)}>
                  {profile?.company_stage?.replace('_', ' ').toUpperCase() || 'Not Set'}
                </Badge>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-purple-100 rounded-full">
                <Users className="h-6 w-6 text-purple-600" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Employees</p>
                <div className="flex items-baseline gap-1">
                  <p className="text-lg font-semibold">{profile?.employee_count_current || 0}</p>
                  {profile?.employee_count_target && (
                    <p className="text-sm text-muted-foreground">/ {profile.employee_count_target}</p>
                  )}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-orange-100 rounded-full">
                <Package className="h-6 w-6 text-orange-600" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Products</p>
                <p className="text-lg font-semibold">{products.length}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Main Content Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList>
          <TabsTrigger value="profile">Company Profile</TabsTrigger>
          <TabsTrigger value="products">
            Products & Services
            {products.length > 0 && (
              <Badge variant="secondary" className="ml-2">{products.length}</Badge>
            )}
          </TabsTrigger>
          <TabsTrigger value="ai-settings">AI Settings</TabsTrigger>
        </TabsList>

        {/* Profile Tab */}
        <TabsContent value="profile" className="space-y-6">
          {/* Industry & Stage */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <Building2 className="h-4 w-4" />
                Industry & Stage
              </CardTitle>
              <CardDescription>
                This information helps AI generate industry-appropriate organizational structures
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Industry *</Label>
                  <Select
                    value={profile?.industry || ''}
                    onValueChange={(v) => updateProfile('industry', v)}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select your industry" />
                    </SelectTrigger>
                    <SelectContent>
                      {INDUSTRIES.map(ind => (
                        <SelectItem key={ind.value} value={ind.value}>{ind.label}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label>Sub-Industry</Label>
                  <Input
                    value={profile?.sub_industry || ''}
                    onChange={(e) => updateProfile('sub_industry', e.target.value)}
                    placeholder="e.g., B2B SaaS, Consumer FinTech"
                  />
                </div>

                <div className="space-y-2">
                  <Label>Company Stage *</Label>
                  <Select
                    value={profile?.company_stage || ''}
                    onValueChange={(v) => updateProfile('company_stage', v)}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select your stage" />
                    </SelectTrigger>
                    <SelectContent>
                      {COMPANY_STAGES.map(stage => (
                        <SelectItem key={stage.value} value={stage.value}>
                          <div className="flex items-center justify-between w-full">
                            <span>{stage.label}</span>
                            <span className="text-xs text-muted-foreground ml-2">{stage.description}</span>
                          </div>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label>Founding Date</Label>
                  <Input
                    type="date"
                    value={profile?.founding_date || ''}
                    onChange={(e) => updateProfile('founding_date', e.target.value)}
                  />
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Funding */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <DollarSign className="h-4 w-4" />
                Funding Information
              </CardTitle>
              <CardDescription>
                Funding stage helps determine appropriate org structure and salary benchmarks
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="space-y-2">
                  <Label>Last Funding Round</Label>
                  <Select
                    value={profile?.last_funding_round || ''}
                    onValueChange={(v) => updateProfile('last_funding_round', v)}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select round" />
                    </SelectTrigger>
                    <SelectContent>
                      {FUNDING_ROUNDS.map(round => (
                        <SelectItem key={round.value} value={round.value}>{round.label}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div className="space-y-2">
                  <Label>Total Funding Raised (INR)</Label>
                  <Input
                    type="number"
                    value={profile?.funding_raised || ''}
                    onChange={(e) => updateProfile('funding_raised', e.target.value ? parseInt(e.target.value) : null)}
                    placeholder="e.g., 50000000 (5 Cr)"
                  />
                  {profile?.funding_raised && (
                    <p className="text-xs text-muted-foreground">
                      {formatCurrency(profile.funding_raised)}
                    </p>
                  )}
                </div>

                <div className="space-y-2">
                  <Label>Growth Rate (%)</Label>
                  <Input
                    type="number"
                    value={profile?.growth_rate_percent || ''}
                    onChange={(e) => updateProfile('growth_rate_percent', e.target.value ? parseFloat(e.target.value) : null)}
                    placeholder="e.g., 150"
                    min={0}
                    max={1000}
                  />
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Employee Planning */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <Users className="h-4 w-4" />
                Employee Planning
              </CardTitle>
              <CardDescription>
                Define your current team size and growth targets for AI headcount recommendations
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="space-y-2">
                  <Label>Current Employees *</Label>
                  <Input
                    type="number"
                    value={profile?.employee_count_current || 0}
                    onChange={(e) => updateProfile('employee_count_current', parseInt(e.target.value) || 0)}
                    min={0}
                  />
                </div>

                <div className="space-y-2">
                  <Label>Target Employees</Label>
                  <Input
                    type="number"
                    value={profile?.employee_count_target || ''}
                    onChange={(e) => updateProfile('employee_count_target', e.target.value ? parseInt(e.target.value) : null)}
                    placeholder="e.g., 50"
                    min={0}
                  />
                </div>

                <div className="space-y-2">
                  <Label>Timeline (Months)</Label>
                  <Input
                    type="number"
                    value={profile?.target_employee_timeline_months || ''}
                    onChange={(e) => updateProfile('target_employee_timeline_months', e.target.value ? parseInt(e.target.value) : null)}
                    placeholder="e.g., 12"
                    min={1}
                    max={60}
                  />
                </div>
              </div>

              {profile?.employee_count_current && profile?.employee_count_target && (
                <div className="p-4 bg-muted rounded-lg">
                  <div className="flex justify-between mb-2">
                    <span className="text-sm">Headcount Progress</span>
                    <span className="text-sm font-medium">
                      {Math.round((profile.employee_count_current / profile.employee_count_target) * 100)}%
                    </span>
                  </div>
                  <Progress
                    value={(profile.employee_count_current / profile.employee_count_target) * 100}
                    className="h-2"
                  />
                  <p className="text-xs text-muted-foreground mt-2">
                    Need to hire {profile.employee_count_target - profile.employee_count_current} more people
                    {profile.target_employee_timeline_months && ` in ${profile.target_employee_timeline_months} months`}
                  </p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* Work Setup */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <MapPin className="h-4 w-4" />
                Work Setup
              </CardTitle>
              <CardDescription>
                Remote policy affects org structure recommendations and role design
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-3">
                <Label>Remote Work Policy *</Label>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                  {REMOTE_POLICIES.map(policy => (
                    <button
                      key={policy.value}
                      type="button"
                      onClick={() => updateProfile('remote_work_policy', policy.value)}
                      className={`p-4 border rounded-lg text-left transition-colors ${
                        profile?.remote_work_policy === policy.value
                          ? 'border-primary bg-primary/5'
                          : 'border-muted hover:border-primary/50'
                      }`}
                    >
                      <div className="font-medium">{policy.label}</div>
                      <div className="text-sm text-muted-foreground">{policy.description}</div>
                    </button>
                  ))}
                </div>
              </div>

              <div className="space-y-2">
                <Label>Work Locations</Label>
                <Input
                  value={profile?.work_locations?.join(', ') || ''}
                  onChange={(e) => updateProfile('work_locations', e.target.value.split(',').map(s => s.trim()).filter(Boolean))}
                  placeholder="e.g., Bangalore, Mumbai, Remote"
                />
                <p className="text-xs text-muted-foreground">Separate multiple locations with commas</p>
              </div>
            </CardContent>
          </Card>

          {/* Organization Preferences */}
          <Card>
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <Layers className="h-4 w-4" />
                Organization Preferences
              </CardTitle>
              <CardDescription>
                Structure preference guides AI in recommending departments and reporting lines
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-3">
                <Label>Preferred Org Structure *</Label>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                  {ORG_STRUCTURES.map(structure => (
                    <button
                      key={structure.value}
                      type="button"
                      onClick={() => updateProfile('org_structure_preference', structure.value)}
                      className={`p-4 border rounded-lg text-left transition-colors ${
                        profile?.org_structure_preference === structure.value
                          ? 'border-primary bg-primary/5'
                          : 'border-muted hover:border-primary/50'
                      }`}
                    >
                      <div className="font-medium">{structure.label}</div>
                      <div className="text-sm text-muted-foreground">{structure.description}</div>
                    </button>
                  ))}
                </div>
              </div>

              <div className="flex items-center justify-between p-4 border rounded-lg">
                <div>
                  <div className="font-medium">Tech-Focused Company</div>
                  <div className="text-sm text-muted-foreground">
                    Higher ratio of engineering and product roles
                  </div>
                </div>
                <Switch
                  checked={profile?.tech_focused ?? true}
                  onCheckedChange={(checked) => updateProfile('tech_focused', checked)}
                />
              </div>

              <div className="space-y-2">
                <Label>Company Culture (Optional)</Label>
                <Textarea
                  value={profile?.company_culture || ''}
                  onChange={(e) => updateProfile('company_culture', e.target.value)}
                  placeholder="Describe your company culture, values, and work style..."
                  rows={3}
                />
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Products Tab */}
        <TabsContent value="products" className="space-y-6">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="text-base flex items-center gap-2">
                    <Package className="h-4 w-4" />
                    Products & Services
                  </CardTitle>
                  <CardDescription>
                    Define your products to help AI recommend relevant teams and roles
                  </CardDescription>
                </div>
                <Button onClick={() => openProductDialog()}>
                  <Plus className="h-4 w-4 mr-2" />
                  Add Product
                </Button>
              </div>
            </CardHeader>
            <CardContent>
              {products.length === 0 ? (
                <div className="text-center py-12">
                  <Package className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                  <h3 className="text-lg font-medium mb-2">No Products Yet</h3>
                  <p className="text-muted-foreground mb-4">
                    Add your products or services to get better AI recommendations
                  </p>
                  <Button onClick={() => openProductDialog()}>
                    <Plus className="h-4 w-4 mr-2" />
                    Add First Product
                  </Button>
                </div>
              ) : (
                <div className="space-y-4">
                  {products.map(product => (
                    <div
                      key={product.id}
                      className="flex items-start justify-between p-4 border rounded-lg hover:bg-muted/50 transition-colors"
                    >
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <h4 className="font-medium">{product.name}</h4>
                          {product.is_primary && (
                            <Badge variant="default" className="text-xs">Primary</Badge>
                          )}
                          <Badge variant="outline" className="text-xs capitalize">
                            {product.product_type}
                          </Badge>
                          <Badge
                            variant={product.status === 'active' ? 'default' : 'secondary'}
                            className="text-xs capitalize"
                          >
                            {product.status}
                          </Badge>
                        </div>
                        {product.description && (
                          <p className="text-sm text-muted-foreground mb-2">{product.description}</p>
                        )}
                        <div className="flex flex-wrap gap-1 mb-2">
                          {product.tech_stack?.map((tech, i) => (
                            <Badge key={i} variant="outline" className="text-xs">
                              {tech}
                            </Badge>
                          ))}
                        </div>
                        <div className="flex gap-4 text-xs text-muted-foreground">
                          {product.team_size_current > 0 && (
                            <span>Team: {product.team_size_current} people</span>
                          )}
                          {product.team_size_needed && (
                            <span>Needs: {product.team_size_needed} people</span>
                          )}
                          {product.revenue_stage && (
                            <span className="capitalize">{product.revenue_stage.replace('_', ' ')}</span>
                          )}
                        </div>
                      </div>
                      <div className="flex items-center gap-1 ml-4">
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => openProductDialog(product)}
                        >
                          <Edit className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => handleDeleteProduct(product.id)}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* AI Settings Tab */}
        <TabsContent value="ai-settings" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <Sparkles className="h-4 w-4" />
                AI Org Builder Settings
              </CardTitle>
              <CardDescription>
                Configure how AI generates organizational recommendations
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between p-4 border rounded-lg">
                <div>
                  <div className="font-medium">Enable AI Org Builder</div>
                  <div className="text-sm text-muted-foreground">
                    Allow AI to generate organizational structure recommendations
                  </div>
                </div>
                <Switch
                  checked={profile?.ai_org_builder_enabled ?? true}
                  onCheckedChange={(checked) => updateProfile('ai_org_builder_enabled', checked)}
                />
              </div>

              {profile?.last_ai_analysis_at && (
                <div className="p-4 bg-muted rounded-lg">
                  <div className="flex items-center gap-2 text-sm">
                    <Calendar className="h-4 w-4 text-muted-foreground" />
                    <span className="text-muted-foreground">Last AI Analysis:</span>
                    <span className="font-medium">
                      {new Date(profile.last_ai_analysis_at).toLocaleDateString('en-IN', {
                        day: 'numeric',
                        month: 'short',
                        year: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit',
                      })}
                    </span>
                  </div>
                </div>
              )}

              <div className="p-4 bg-blue-50 dark:bg-blue-950/20 rounded-lg">
                <h4 className="font-medium flex items-center gap-2 mb-2">
                  <Sparkles className="h-4 w-4 text-blue-600" />
                  How AI Uses Your Profile
                </h4>
                <ul className="text-sm text-muted-foreground space-y-1">
                  <li>- Industry patterns determine core departments (e.g., Engineering, Product, Sales)</li>
                  <li>- Company stage influences headcount recommendations</li>
                  <li>- Funding information affects salary range suggestions</li>
                  <li>- Products help identify required tech roles and team sizes</li>
                  <li>- Remote policy impacts role design and team structure</li>
                </ul>
              </div>

              <Button
                className="w-full"
                variant="outline"
                onClick={() => window.location.href = '/org-builder'}
              >
                <Sparkles className="h-4 w-4 mr-2" />
                Go to AI Org Builder
                <ChevronRight className="h-4 w-4 ml-auto" />
              </Button>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Product Dialog */}
      <Dialog open={showProductDialog} onOpenChange={setShowProductDialog}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>
              {editingProduct ? 'Edit Product' : 'Add Product'}
            </DialogTitle>
            <DialogDescription>
              Define your product or service details for AI-powered team recommendations
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4 py-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Product Name *</Label>
                <Input
                  value={productForm.name}
                  onChange={(e) => setProductForm(prev => ({ ...prev, name: e.target.value }))}
                  placeholder="e.g., Mobile App"
                />
              </div>

              <div className="space-y-2">
                <Label>Type</Label>
                <Select
                  value={productForm.product_type}
                  onValueChange={(v) => setProductForm(prev => ({ ...prev, product_type: v }))}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {PRODUCT_TYPES.map(type => (
                      <SelectItem key={type.value} value={type.value}>{type.label}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="space-y-2">
              <Label>Description</Label>
              <Textarea
                value={productForm.description}
                onChange={(e) => setProductForm(prev => ({ ...prev, description: e.target.value }))}
                placeholder="Describe what this product does..."
                rows={3}
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Status</Label>
                <Select
                  value={productForm.status}
                  onValueChange={(v) => setProductForm(prev => ({ ...prev, status: v }))}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {PRODUCT_STATUSES.map(status => (
                      <SelectItem key={status.value} value={status.value}>{status.label}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label>Revenue Stage</Label>
                <Select
                  value={productForm.revenue_stage}
                  onValueChange={(v) => setProductForm(prev => ({ ...prev, revenue_stage: v }))}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select stage" />
                  </SelectTrigger>
                  <SelectContent>
                    {REVENUE_STAGES.map(stage => (
                      <SelectItem key={stage.value} value={stage.value}>{stage.label}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="space-y-2">
              <Label>Tech Stack</Label>
              <div className="flex flex-wrap gap-2 p-3 border rounded-lg max-h-32 overflow-y-auto">
                {COMMON_TECH_STACKS.map(tech => (
                  <Badge
                    key={tech}
                    variant={productForm.tech_stack.includes(tech) ? 'default' : 'outline'}
                    className="cursor-pointer"
                    onClick={() => toggleTechStack(tech)}
                  >
                    {tech}
                  </Badge>
                ))}
              </div>
              <p className="text-xs text-muted-foreground">
                Click to select technologies used in this product
              </p>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Current Team Size</Label>
                <Input
                  type="number"
                  value={productForm.team_size_current}
                  onChange={(e) => setProductForm(prev => ({ ...prev, team_size_current: parseInt(e.target.value) || 0 }))}
                  min={0}
                />
              </div>

              <div className="space-y-2">
                <Label>Team Size Needed</Label>
                <Input
                  type="number"
                  value={productForm.team_size_needed}
                  onChange={(e) => setProductForm(prev => ({ ...prev, team_size_needed: parseInt(e.target.value) || 0 }))}
                  min={0}
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label>Target Market</Label>
              <Input
                value={productForm.target_market}
                onChange={(e) => setProductForm(prev => ({ ...prev, target_market: e.target.value }))}
                placeholder="e.g., SMBs in India, Enterprise globally"
              />
            </div>

            <div className="flex items-center justify-between p-3 border rounded-lg">
              <div>
                <div className="font-medium">Primary Product</div>
                <div className="text-sm text-muted-foreground">
                  Mark as your main product or service
                </div>
              </div>
              <Switch
                checked={productForm.is_primary}
                onCheckedChange={(checked) => setProductForm(prev => ({ ...prev, is_primary: checked }))}
              />
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setShowProductDialog(false)}>
              Cancel
            </Button>
            <Button onClick={handleSaveProduct} disabled={isSaving}>
              {isSaving ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Saving...
                </>
              ) : (
                <>
                  <Save className="h-4 w-4 mr-2" />
                  {editingProduct ? 'Update' : 'Create'} Product
                </>
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
