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
  DialogTrigger,
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
import { useApi, useToast, useAuth } from '@/hooks'
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
  Layers,
  Sparkles,
  CheckCircle2,
  AlertCircle,
  Package,
  ChevronRight,
  ChevronDown,
  Network,
  Search,
  RefreshCw,
  Wand2,
  Check,
  X,
  Clock,
  Settings,
  ArrowRight,
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

interface Department {
  id: string
  name: string
  code?: string
  parent_id?: string
  parent_name?: string
  head_employee_id?: string
  head_employee_name?: string
  is_active: boolean
  employee_count: number
}

interface Designation {
  id: string
  name: string
  code?: string
  level?: number
  is_active: boolean
  employee_count: number
}

interface Employee {
  id: string
  employee_code: string
  first_name: string
  last_name: string
  full_name: string
  department_id?: string
  department_name?: string
  designation_id?: string
  designation_name?: string
  reporting_to?: string
  reporting_to_name?: string
  employment_status: string
}

interface DashboardSummary {
  pending_recommendations: number
  total_departments: number
  total_designations: number
  ai_generated_departments: number
  ai_generated_designations: number
  headcount_current: number
  headcount_target: number
  recent_recommendations: Recommendation[]
}

interface Recommendation {
  id: string
  recommendation_type: string
  status: string
  priority: number
  confidence_score: number
  rationale: string
  recommendation_data: {
    summary: string
    total_headcount: number
    estimated_monthly_cost: number
    departments: DepartmentRec[]
    designations: DesignationRec[]
  }
  created_at: string
}

interface DepartmentRec {
  name: string
  code?: string
  description?: string
  headcount_target?: number
  rationale?: string
}

interface DesignationRec {
  name: string
  code?: string
  department: string
  level?: number
  description?: string
  experience_min: number
  experience_max?: number
  salary_min?: number
  salary_max?: number
  headcount_target: number
  priority: string
}

interface OrgNode {
  id: string
  name: string
  title: string
  employee: string
  children: OrgNode[]
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
  { value: 'office_first', label: 'Office First', description: 'Primarily office-based' },
]

const ORG_STRUCTURES = [
  { value: 'flat', label: 'Flat', description: 'Few management layers' },
  { value: 'hierarchical', label: 'Hierarchical', description: 'Traditional pyramid' },
  { value: 'matrix', label: 'Matrix', description: 'Multiple reporting lines' },
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
  'PostgreSQL', 'MySQL', 'MongoDB', 'Redis', 'AWS', 'GCP', 'Azure', 'Docker', 'Kubernetes',
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
  if (amount >= 10000000) return `₹${(amount / 10000000).toFixed(1)} Cr`
  if (amount >= 100000) return `₹${(amount / 100000).toFixed(1)} L`
  return new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(amount)
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

function getPriorityColor(priority: string): string {
  switch (priority) {
    case 'immediate': return 'bg-red-100 text-red-800'
    case 'next_quarter': return 'bg-yellow-100 text-yellow-800'
    case 'nice_to_have': return 'bg-green-100 text-green-800'
    default: return 'bg-gray-100 text-gray-800'
  }
}

function getStatusColor(status: string): string {
  switch (status) {
    case 'pending': return 'bg-blue-100 text-blue-800'
    case 'accepted': return 'bg-green-100 text-green-800'
    case 'rejected': return 'bg-red-100 text-red-800'
    default: return 'bg-gray-100 text-gray-800'
  }
}

function buildOrgTree(employees: Employee[]): OrgNode | null {
  if (employees.length === 0) return null
  const topEmployees = employees.filter(emp => !emp.reporting_to)

  const buildChildNodes = (parentId: string): OrgNode[] => {
    return employees
      .filter(emp => emp.reporting_to === parentId)
      .map(child => ({
        id: child.id,
        name: child.designation_name || 'Employee',
        title: child.designation_name || 'Employee',
        employee: child.full_name,
        children: buildChildNodes(child.id)
      }))
  }

  if (topEmployees.length === 1) {
    const root = topEmployees[0]
    return {
      id: root.id,
      name: root.designation_name || 'CEO',
      title: root.designation_name || 'CEO',
      employee: root.full_name,
      children: buildChildNodes(root.id)
    }
  }

  if (topEmployees.length > 1) {
    return {
      id: 'root',
      name: 'Organization',
      title: 'Organization',
      employee: 'Company',
      children: topEmployees.map(emp => ({
        id: emp.id,
        name: emp.designation_name || 'Manager',
        title: emp.designation_name || 'Manager',
        employee: emp.full_name,
        children: buildChildNodes(emp.id)
      }))
    }
  }

  return null
}

// ============================================================================
// Org Chart Component
// ============================================================================

function OrgNodeComponent({ node, level = 0 }: { node: OrgNode; level?: number }) {
  const [expanded, setExpanded] = useState(level < 2)
  const hasChildren = node.children && node.children.length > 0

  return (
    <div className={level > 0 ? 'ml-8 mt-2' : ''}>
      <div className="flex items-start gap-2">
        {hasChildren && (
          <button onClick={() => setExpanded(!expanded)} className="mt-3">
            {expanded ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
          </button>
        )}
        {!hasChildren && <div className="w-4" />}
        <Card className="flex-1 max-w-xs">
          <CardContent className="p-3">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-primary/10 rounded-full flex items-center justify-center">
                <span className="text-sm font-medium text-primary">
                  {node.employee?.split(' ').map(n => n[0]).join('').slice(0, 2)}
                </span>
              </div>
              <div>
                <p className="font-medium text-sm">{node.employee}</p>
                <p className="text-xs text-muted-foreground">{node.title}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
      {expanded && hasChildren && (
        <div className="border-l-2 border-muted ml-2">
          {node.children?.map((child) => (
            <OrgNodeComponent key={child.id} node={child} level={level + 1} />
          ))}
        </div>
      )}
    </div>
  )
}

// ============================================================================
// Main Component
// ============================================================================

export default function OrganizationSetupPage() {
  const searchParams = useSearchParams()
  const { fetchWithAuth } = useAuth()
  const { showToast } = useToast()
  const { get, post } = useApi()
  const API_BASE = process.env.NEXT_PUBLIC_API_URL || '/api/v1'

  // Tab state
  const initialTab = searchParams.get('tab') || 'profile'
  const [activeTab, setActiveTab] = useState(initialTab)

  // Loading states
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  const [isGenerating, setIsGenerating] = useState(false)

  // Profile state
  const [profile, setProfile] = useState<ExtendedProfile | null>(null)
  const [products, setProducts] = useState<Product[]>([])
  const [setupStatus, setSetupStatus] = useState<SetupStatus | null>(null)
  const [hasChanges, setHasChanges] = useState(false)

  // Organization state
  const [departments, setDepartments] = useState<Department[]>([])
  const [designations, setDesignations] = useState<Designation[]>([])
  const [employees, setEmployees] = useState<Employee[]>([])
  const [searchQuery, setSearchQuery] = useState('')

  // AI Org Builder state
  const [aiSummary, setAiSummary] = useState<DashboardSummary | null>(null)
  const [recommendations, setRecommendations] = useState<Recommendation[]>([])
  const [showGenerateDialog, setShowGenerateDialog] = useState(false)
  const [additionalContext, setAdditionalContext] = useState('')

  // Dialog states
  const [showProductDialog, setShowProductDialog] = useState(false)
  const [editingProduct, setEditingProduct] = useState<Product | null>(null)
  const [showDeptDialog, setShowDeptDialog] = useState(false)
  const [editingDept, setEditingDept] = useState<Department | null>(null)
  const [showDesigDialog, setShowDesigDialog] = useState(false)
  const [editingDesig, setEditingDesig] = useState<Designation | null>(null)

  // Form states
  const [productForm, setProductForm] = useState({
    name: '', description: '', status: 'active', product_type: 'product',
    tech_stack: [] as string[], target_market: '', revenue_stage: '',
    team_size_current: 0, team_size_needed: 0, is_primary: false, priority: 0,
  })
  const [deptForm, setDeptForm] = useState({ name: '', code: '', parent_id: '', head_employee_id: '' })
  const [desigForm, setDesigForm] = useState({ name: '', code: '', level: 1 })

  // API helpers - using fetchWithAuth for token refresh handling
  const apiGet = useCallback(async (endpoint: string) => {
    const response = await fetchWithAuth(`${API_BASE}${endpoint}`, {
      headers: { 'Content-Type': 'application/json' },
    })
    if (!response.ok) {
      if (response.status === 404) return null
      throw new Error('Request failed')
    }
    return response.json()
  }, [API_BASE, fetchWithAuth])

  const apiPost = useCallback(async (endpoint: string, data: any) => {
    const response = await fetchWithAuth(`${API_BASE}${endpoint}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    })
    if (!response.ok) {
      const err = await response.json().catch(() => ({}))
      throw new Error(err.detail || 'Request failed')
    }
    return response.json()
  }, [API_BASE, fetchWithAuth])

  const apiPut = useCallback(async (endpoint: string, data: any) => {
    const response = await fetchWithAuth(`${API_BASE}${endpoint}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    })
    if (!response.ok) {
      const err = await response.json().catch(() => ({}))
      throw new Error(err.detail || 'Request failed')
    }
    return response.json()
  }, [API_BASE, fetchWithAuth])

  const apiDelete = useCallback(async (endpoint: string) => {
    const response = await fetchWithAuth(`${API_BASE}${endpoint}`, {
      method: 'DELETE',
    })
    return response.ok
  }, [API_BASE, fetchWithAuth])

  // Fetch all data
  const fetchData = useCallback(async () => {
    setIsLoading(true)
    try {
      const [profileRes, productsRes, statusRes, deptsRes, desigsRes, empsRes, aiSummaryRes, recsRes] = await Promise.all([
        apiGet('/company/extended-profile').catch(() => null),
        apiGet('/company/products').catch(() => ({ data: [] })),
        apiGet('/company/setup-status').catch(() => null),
        apiGet('/departments?page=1&limit=100').catch(() => ({ data: [] })),
        apiGet('/departments/designations/?page=1&limit=100').catch(() => ({ data: [] })),
        apiGet('/employees?page=1&limit=200&status=active').catch(() => ({ data: [] })),
        get('/ai/org-builder/dashboard-summary').catch(() => null),
        get('/ai/org-builder/recommendations?limit=50').catch(() => ({ data: [] })),
      ])

      setProfile(profileRes || DEFAULT_PROFILE)
      setProducts((productsRes as any)?.data || [])
      setSetupStatus(statusRes as SetupStatus)
      setDepartments((deptsRes as any)?.data || [])
      setDesignations((desigsRes as any)?.data || [])
      setEmployees((empsRes as any)?.data || [])
      if (aiSummaryRes) setAiSummary(aiSummaryRes as DashboardSummary)
      if (recsRes) setRecommendations((recsRes as any).data || [])
    } catch (error) {
      console.error('Failed to load data:', error)
    } finally {
      setIsLoading(false)
    }
  }, [apiGet, get])

  useEffect(() => {
    fetchData()
  }, [fetchData])

  // Profile handlers
  const updateProfile = (field: keyof ExtendedProfile, value: any) => {
    setProfile(prev => prev ? { ...prev, [field]: value } : null)
    setHasChanges(true)
  }

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

  // Product handlers
  const openProductDialog = (product?: Product) => {
    if (product) {
      setEditingProduct(product)
      setProductForm({
        name: product.name, description: product.description || '', status: product.status,
        product_type: product.product_type, tech_stack: product.tech_stack || [],
        target_market: product.target_market || '', revenue_stage: product.revenue_stage || '',
        team_size_current: product.team_size_current, team_size_needed: product.team_size_needed || 0,
        is_primary: product.is_primary, priority: product.priority,
      })
    } else {
      setEditingProduct(null)
      setProductForm({
        name: '', description: '', status: 'active', product_type: 'product',
        tech_stack: [], target_market: '', revenue_stage: '',
        team_size_current: 0, team_size_needed: 0, is_primary: false, priority: 0,
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
      await apiDelete(`/company/products/${productId}`)
      showToast('success', 'Deleted', 'Product deleted successfully')
      await fetchData()
    } catch {
      showToast('error', 'Error', 'Failed to delete product')
    }
  }

  // Department handlers
  const openDeptDialog = (dept?: Department) => {
    if (dept) {
      setEditingDept(dept)
      setDeptForm({ name: dept.name, code: dept.code || '', parent_id: dept.parent_id || '', head_employee_id: dept.head_employee_id || '' })
    } else {
      setEditingDept(null)
      setDeptForm({ name: '', code: '', parent_id: '', head_employee_id: '' })
    }
    setShowDeptDialog(true)
  }

  const handleSaveDept = async () => {
    if (!deptForm.name) {
      showToast('error', 'Error', 'Department name is required')
      return
    }
    setIsSaving(true)
    try {
      const data = {
        name: deptForm.name,
        code: deptForm.code || undefined,
        parent_id: deptForm.parent_id || undefined,
        head_employee_id: deptForm.head_employee_id || undefined,
      }
      if (editingDept) {
        await apiPut(`/departments/${editingDept.id}`, data)
        showToast('success', 'Updated', 'Department updated successfully')
      } else {
        await apiPost('/departments', data)
        showToast('success', 'Created', 'Department created successfully')
      }
      setShowDeptDialog(false)
      await fetchData()
    } catch (error: any) {
      showToast('error', 'Error', error.message || 'Failed to save department')
    } finally {
      setIsSaving(false)
    }
  }

  const handleDeleteDept = async (deptId: string) => {
    if (!confirm('Are you sure you want to delete this department?')) return
    try {
      await apiDelete(`/departments/${deptId}`)
      showToast('success', 'Deleted', 'Department deleted')
      await fetchData()
    } catch {
      showToast('error', 'Error', 'Cannot delete department with employees')
    }
  }

  // Designation handlers
  const openDesigDialog = (desig?: Designation) => {
    if (desig) {
      setEditingDesig(desig)
      setDesigForm({ name: desig.name, code: desig.code || '', level: desig.level || 1 })
    } else {
      setEditingDesig(null)
      setDesigForm({ name: '', code: '', level: 1 })
    }
    setShowDesigDialog(true)
  }

  const handleSaveDesig = async () => {
    if (!desigForm.name) {
      showToast('error', 'Error', 'Designation name is required')
      return
    }
    setIsSaving(true)
    try {
      const data = { name: desigForm.name, code: desigForm.code || undefined, level: desigForm.level || undefined }
      if (editingDesig) {
        await apiPut(`/departments/designations/${editingDesig.id}`, data)
        showToast('success', 'Updated', 'Designation updated successfully')
      } else {
        await apiPost('/departments/designations/', data)
        showToast('success', 'Created', 'Designation created successfully')
      }
      setShowDesigDialog(false)
      await fetchData()
    } catch (error: any) {
      showToast('error', 'Error', error.message || 'Failed to save designation')
    } finally {
      setIsSaving(false)
    }
  }

  const handleDeleteDesig = async (desigId: string) => {
    if (!confirm('Are you sure you want to delete this designation?')) return
    try {
      await apiDelete(`/departments/designations/${desigId}`)
      showToast('success', 'Deleted', 'Designation deleted')
      await fetchData()
    } catch {
      showToast('error', 'Error', 'Cannot delete designation with employees')
    }
  }

  // AI Org Builder handlers
  const handleGenerate = async () => {
    setIsGenerating(true)
    try {
      const data = await post('/ai/org-builder/generate', {
        include_departments: true,
        include_designations: true,
        include_salary_ranges: true,
        additional_context: additionalContext || undefined
      }) as any
      if (data?.success) {
        showToast('success', 'Generated', 'Organization structure generated successfully')
        setShowGenerateDialog(false)
        setAdditionalContext('')
        await fetchData()
      }
    } catch (error: any) {
      showToast('error', 'Failed', error.message || 'Failed to generate structure')
    } finally {
      setIsGenerating(false)
    }
  }

  const handleAcceptRec = async (recId: string) => {
    try {
      const data = await post(`/ai/org-builder/recommendations/${recId}/accept`, {}) as any
      if (data?.success) {
        showToast('success', 'Accepted', `Created ${data.departments_created || 0} departments and ${data.designations_created || 0} designations`)
        await fetchData()
      }
    } catch (error: any) {
      showToast('error', 'Failed', error.message || 'Failed to accept recommendation')
    }
  }

  const handleRejectRec = async (recId: string) => {
    try {
      await post(`/ai/org-builder/recommendations/${recId}/reject`, { rejection_reason: 'Not suitable' })
      showToast('success', 'Rejected', 'Recommendation rejected')
      await fetchData()
    } catch (error: any) {
      showToast('error', 'Failed', error.message || 'Failed to reject recommendation')
    }
  }

  // Computed values
  const orgTree = buildOrgTree(employees)
  const filteredDepartments = departments.filter(d => d.name.toLowerCase().includes(searchQuery.toLowerCase()))
  const filteredDesignations = designations.filter(d => d.name.toLowerCase().includes(searchQuery.toLowerCase()))
  const pendingRecs = recommendations.filter(r => r.status === 'pending')
  const isProfileComplete = setupStatus?.extended_profile_complete && setupStatus?.company_profile_complete && (setupStatus?.products_added ?? 0) >= (setupStatus?.products_minimum ?? 1)

  // Loading state
  if (isLoading) {
    return (
      <div className="space-y-6">
        <PageHeader title="Organization" description="Loading..." />
        <div className="grid gap-4 md:grid-cols-4">
          {[1, 2, 3, 4].map(i => (
            <Card key={i}><CardContent className="p-6"><Skeleton className="h-8 w-24 mb-2" /><Skeleton className="h-4 w-32" /></CardContent></Card>
          ))}
        </div>
        <Skeleton className="h-96 w-full" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Organization"
        description="Configure your company profile, structure, and AI-powered recommendations"
        breadcrumbs={[
          { label: 'Dashboard', href: '/' },
          { label: 'Settings', href: '/settings' },
          { label: 'Organization' },
        ]}
        actions={
          <div className="flex items-center gap-3">
            {hasChanges && <Badge variant="outline" className="text-yellow-600 border-yellow-300">Unsaved Changes</Badge>}
            <Button onClick={handleSaveProfile} disabled={isSaving || !hasChanges}>
              {isSaving ? <><Loader2 className="mr-2 h-4 w-4 animate-spin" />Saving...</> : <><Save className="mr-2 h-4 w-4" />Save Changes</>}
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
                  {setupStatus.overall_complete ? <CheckCircle2 className="h-5 w-5 text-green-600" /> : <AlertCircle className="h-5 w-5 text-yellow-600" />}
                </div>
                <div>
                  <h3 className="font-medium">Setup Progress</h3>
                  <p className="text-sm text-muted-foreground">
                    {setupStatus.overall_complete ? 'Your organization setup is complete!' : 'Complete setup to use AI Org Builder'}
                  </p>
                </div>
              </div>
              <div className="text-right">
                <span className="text-2xl font-bold">{setupStatus.completion_percentage}%</span>
                <p className="text-sm text-muted-foreground">Complete</p>
              </div>
            </div>
            <Progress value={setupStatus.completion_percentage} className="h-2" />
          </CardContent>
        </Card>
      )}

      {/* Summary Stats */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-blue-100 rounded-full"><Building2 className="h-6 w-6 text-blue-600" /></div>
              <div>
                <p className="text-2xl font-bold">{departments.length}</p>
                <p className="text-sm text-muted-foreground">Departments</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-green-100 rounded-full"><Briefcase className="h-6 w-6 text-green-600" /></div>
              <div>
                <p className="text-2xl font-bold">{designations.length}</p>
                <p className="text-sm text-muted-foreground">Designations</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-purple-100 rounded-full"><Users className="h-6 w-6 text-purple-600" /></div>
              <div>
                <p className="text-2xl font-bold">{employees.length}</p>
                <p className="text-sm text-muted-foreground">Employees</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-orange-100 rounded-full"><Package className="h-6 w-6 text-orange-600" /></div>
              <div>
                <p className="text-2xl font-bold">{products.length}</p>
                <p className="text-sm text-muted-foreground">Products</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Main Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="flex-wrap">
          <TabsTrigger value="profile">Company Profile</TabsTrigger>
          <TabsTrigger value="products">Products {products.length > 0 && <Badge variant="secondary" className="ml-2">{products.length}</Badge>}</TabsTrigger>
          <TabsTrigger value="orgchart">Org Chart</TabsTrigger>
          <TabsTrigger value="departments">Departments {departments.length > 0 && <Badge variant="secondary" className="ml-2">{departments.length}</Badge>}</TabsTrigger>
          <TabsTrigger value="designations">Designations {designations.length > 0 && <Badge variant="secondary" className="ml-2">{designations.length}</Badge>}</TabsTrigger>
          <TabsTrigger value="ai-builder">AI Org Builder {pendingRecs.length > 0 && <Badge variant="secondary" className="ml-2">{pendingRecs.length}</Badge>}</TabsTrigger>
        </TabsList>

        {/* Company Profile Tab */}
        <TabsContent value="profile" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2"><Building2 className="h-4 w-4" />Industry & Stage</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Industry *</Label>
                  <Select value={profile?.industry || ''} onValueChange={(v) => updateProfile('industry', v)}>
                    <SelectTrigger><SelectValue placeholder="Select industry" /></SelectTrigger>
                    <SelectContent>{INDUSTRIES.map(i => <SelectItem key={i.value} value={i.value}>{i.label}</SelectItem>)}</SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label>Company Stage *</Label>
                  <Select value={profile?.company_stage || ''} onValueChange={(v) => updateProfile('company_stage', v)}>
                    <SelectTrigger><SelectValue placeholder="Select stage" /></SelectTrigger>
                    <SelectContent>{COMPANY_STAGES.map(s => <SelectItem key={s.value} value={s.value}>{s.label} - {s.description}</SelectItem>)}</SelectContent>
                  </Select>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2"><Users className="h-4 w-4" />Employee Planning</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="space-y-2">
                  <Label>Current Employees *</Label>
                  <Input type="number" value={profile?.employee_count_current || 0} onChange={(e) => updateProfile('employee_count_current', parseInt(e.target.value) || 0)} min={0} />
                </div>
                <div className="space-y-2">
                  <Label>Target Employees</Label>
                  <Input type="number" value={profile?.employee_count_target || ''} onChange={(e) => updateProfile('employee_count_target', e.target.value ? parseInt(e.target.value) : null)} placeholder="e.g., 50" />
                </div>
                <div className="space-y-2">
                  <Label>Timeline (Months)</Label>
                  <Input type="number" value={profile?.target_employee_timeline_months || ''} onChange={(e) => updateProfile('target_employee_timeline_months', e.target.value ? parseInt(e.target.value) : null)} placeholder="e.g., 12" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2"><Layers className="h-4 w-4" />Organization Preferences</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                {ORG_STRUCTURES.map(s => (
                  <button key={s.value} type="button" onClick={() => updateProfile('org_structure_preference', s.value)}
                    className={`p-4 border rounded-lg text-left transition-colors ${profile?.org_structure_preference === s.value ? 'border-primary bg-primary/5' : 'hover:border-primary/50'}`}>
                    <div className="font-medium">{s.label}</div>
                    <div className="text-sm text-muted-foreground">{s.description}</div>
                  </button>
                ))}
              </div>
              <div className="flex items-center justify-between p-4 border rounded-lg">
                <div>
                  <div className="font-medium">Tech-Focused Company</div>
                  <div className="text-sm text-muted-foreground">Higher ratio of engineering roles</div>
                </div>
                <Switch checked={profile?.tech_focused ?? true} onCheckedChange={(c) => updateProfile('tech_focused', c)} />
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Products Tab */}
        <TabsContent value="products" className="space-y-6">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div><CardTitle className="text-base">Products & Services</CardTitle><CardDescription>Define your products for AI recommendations</CardDescription></div>
                <Button onClick={() => openProductDialog()}><Plus className="h-4 w-4 mr-2" />Add Product</Button>
              </div>
            </CardHeader>
            <CardContent>
              {products.length === 0 ? (
                <div className="text-center py-12">
                  <Package className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                  <h3 className="text-lg font-medium mb-2">No Products Yet</h3>
                  <Button onClick={() => openProductDialog()}><Plus className="h-4 w-4 mr-2" />Add First Product</Button>
                </div>
              ) : (
                <div className="space-y-4">
                  {products.map(product => (
                    <div key={product.id} className="flex items-start justify-between p-4 border rounded-lg hover:bg-muted/50">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <h4 className="font-medium">{product.name}</h4>
                          {product.is_primary && <Badge>Primary</Badge>}
                          <Badge variant="outline">{product.product_type}</Badge>
                        </div>
                        {product.description && <p className="text-sm text-muted-foreground mb-2">{product.description}</p>}
                        <div className="flex flex-wrap gap-1">
                          {product.tech_stack?.map((tech, i) => <Badge key={i} variant="outline" className="text-xs">{tech}</Badge>)}
                        </div>
                      </div>
                      <div className="flex items-center gap-1 ml-4">
                        <Button variant="ghost" size="icon" onClick={() => openProductDialog(product)}><Edit className="h-4 w-4" /></Button>
                        <Button variant="ghost" size="icon" onClick={() => handleDeleteProduct(product.id)}><Trash2 className="h-4 w-4" /></Button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Org Chart Tab */}
        <TabsContent value="orgchart" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Organization Chart</CardTitle>
              <CardDescription>Visual hierarchy based on reporting relationships</CardDescription>
            </CardHeader>
            <CardContent className="overflow-x-auto">
              {orgTree ? (
                <OrgNodeComponent node={orgTree} />
              ) : (
                <div className="text-center py-12 text-muted-foreground">
                  <Network className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>No employees found to build org chart</p>
                  <p className="text-sm mt-2">Add employees with reporting relationships</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Departments Tab */}
        <TabsContent value="departments" className="space-y-6">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div><CardTitle>Departments</CardTitle><CardDescription>Manage company departments</CardDescription></div>
                <div className="flex items-center gap-2">
                  <div className="relative w-64">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                    <Input placeholder="Search..." value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)} className="pl-9" />
                  </div>
                  <Button onClick={() => openDeptDialog()}><Plus className="h-4 w-4 mr-2" />Add Department</Button>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              {filteredDepartments.length === 0 ? (
                <div className="text-center py-12">
                  <Building2 className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                  <p>No departments found</p>
                  <Button className="mt-4" onClick={() => openDeptDialog()}><Plus className="h-4 w-4 mr-2" />Create Department</Button>
                </div>
              ) : (
                <div className="border rounded-lg overflow-hidden">
                  <table className="w-full">
                    <thead className="bg-muted/50">
                      <tr>
                        <th className="text-left p-4 font-medium">Department</th>
                        <th className="text-left p-4 font-medium">Code</th>
                        <th className="text-left p-4 font-medium">Head</th>
                        <th className="text-center p-4 font-medium">Employees</th>
                        <th className="text-right p-4 font-medium">Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {filteredDepartments.map(dept => (
                        <tr key={dept.id} className="border-t hover:bg-muted/30">
                          <td className="p-4"><span className="font-medium">{dept.name}</span></td>
                          <td className="p-4"><Badge variant="outline">{dept.code || '-'}</Badge></td>
                          <td className="p-4">{dept.head_employee_name || '-'}</td>
                          <td className="p-4 text-center"><Badge variant="secondary">{dept.employee_count}</Badge></td>
                          <td className="p-4 text-right">
                            <Button variant="ghost" size="icon" onClick={() => openDeptDialog(dept)}><Edit className="h-4 w-4" /></Button>
                            <Button variant="ghost" size="icon" onClick={() => handleDeleteDept(dept.id)} disabled={dept.employee_count > 0}><Trash2 className="h-4 w-4" /></Button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Designations Tab */}
        <TabsContent value="designations" className="space-y-6">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div><CardTitle>Designations</CardTitle><CardDescription>Manage job titles and levels</CardDescription></div>
                <div className="flex items-center gap-2">
                  <div className="relative w-64">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                    <Input placeholder="Search..." value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)} className="pl-9" />
                  </div>
                  <Button onClick={() => openDesigDialog()}><Plus className="h-4 w-4 mr-2" />Add Designation</Button>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              {filteredDesignations.length === 0 ? (
                <div className="text-center py-12">
                  <Briefcase className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                  <p>No designations found</p>
                  <Button className="mt-4" onClick={() => openDesigDialog()}><Plus className="h-4 w-4 mr-2" />Create Designation</Button>
                </div>
              ) : (
                <div className="border rounded-lg overflow-hidden">
                  <table className="w-full">
                    <thead className="bg-muted/50">
                      <tr>
                        <th className="text-left p-4 font-medium">Title</th>
                        <th className="text-left p-4 font-medium">Code</th>
                        <th className="text-center p-4 font-medium">Level</th>
                        <th className="text-center p-4 font-medium">Employees</th>
                        <th className="text-right p-4 font-medium">Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {filteredDesignations.map(des => (
                        <tr key={des.id} className="border-t hover:bg-muted/30">
                          <td className="p-4"><span className="font-medium">{des.name}</span></td>
                          <td className="p-4"><Badge variant="outline">{des.code || '-'}</Badge></td>
                          <td className="p-4 text-center"><Badge variant="outline">L{des.level || 1}</Badge></td>
                          <td className="p-4 text-center"><Badge variant="secondary">{des.employee_count}</Badge></td>
                          <td className="p-4 text-right">
                            <Button variant="ghost" size="icon" onClick={() => openDesigDialog(des)}><Edit className="h-4 w-4" /></Button>
                            <Button variant="ghost" size="icon" onClick={() => handleDeleteDesig(des.id)} disabled={des.employee_count > 0}><Trash2 className="h-4 w-4" /></Button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* AI Org Builder Tab */}
        <TabsContent value="ai-builder" className="space-y-6">
          {!isProfileComplete ? (
            <Card className="max-w-2xl mx-auto">
              <CardContent className="p-8 text-center">
                <div className="w-16 h-16 bg-yellow-100 rounded-full flex items-center justify-center mx-auto mb-6">
                  <AlertCircle className="h-8 w-8 text-yellow-600" />
                </div>
                <h2 className="text-xl font-semibold mb-2">Complete Your Company Profile</h2>
                <p className="text-muted-foreground mb-6">Complete the Company Profile and Products tabs to use AI Org Builder.</p>
                {setupStatus && (
                  <div className="mb-6">
                    <div className="flex items-center justify-between mb-2 text-sm">
                      <span className="text-muted-foreground">Setup Progress</span>
                      <span className="font-medium">{setupStatus.completion_percentage}%</span>
                    </div>
                    <Progress value={setupStatus.completion_percentage} className="h-2" />
                  </div>
                )}
                <Button onClick={() => setActiveTab('profile')}><Settings className="h-4 w-4 mr-2" />Go to Company Profile</Button>
              </CardContent>
            </Card>
          ) : (
            <>
              <div className="flex justify-between items-center">
                <div>
                  <h2 className="text-lg font-semibold">AI Org Builder</h2>
                  <p className="text-muted-foreground">AI-powered organizational structure recommendations</p>
                </div>
                <Button onClick={() => setShowGenerateDialog(true)} disabled={isGenerating}>
                  {isGenerating ? <><Loader2 className="mr-2 h-4 w-4 animate-spin" />Generating...</> : <><Wand2 className="mr-2 h-4 w-4" />Generate Structure</>}
                </Button>
              </div>

              {pendingRecs.length === 0 ? (
                <Card>
                  <CardContent className="p-12 text-center">
                    <Sparkles className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                    <h3 className="text-lg font-medium mb-2">No Pending Recommendations</h3>
                    <p className="text-muted-foreground mb-4">Generate a new organization structure to get AI-powered recommendations.</p>
                    <Button onClick={() => setShowGenerateDialog(true)}><Wand2 className="mr-2 h-4 w-4" />Generate Structure</Button>
                  </CardContent>
                </Card>
              ) : (
                <div className="space-y-4">
                  {pendingRecs.map(rec => (
                    <Card key={rec.id} className="hover:shadow-md transition-shadow">
                      <CardHeader className="pb-3">
                        <div className="flex items-start justify-between">
                          <div className="flex items-center gap-3">
                            <div className="p-2 bg-primary/10 rounded-lg"><Sparkles className="h-5 w-5 text-primary" /></div>
                            <div>
                              <CardTitle className="text-base">{rec.recommendation_type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</CardTitle>
                              <CardDescription className="text-xs">{new Date(rec.created_at).toLocaleDateString('en-IN')}</CardDescription>
                            </div>
                          </div>
                          <Badge className={getStatusColor(rec.status)}>{rec.status}</Badge>
                        </div>
                      </CardHeader>
                      <CardContent className="pb-3">
                        <p className="text-sm text-muted-foreground line-clamp-2 mb-4">{rec.recommendation_data?.summary || rec.rationale}</p>
                        <div className="grid grid-cols-3 gap-4 text-center">
                          <div><p className="text-lg font-semibold">{rec.recommendation_data?.departments?.length || 0}</p><p className="text-xs text-muted-foreground">Departments</p></div>
                          <div><p className="text-lg font-semibold">{rec.recommendation_data?.designations?.length || 0}</p><p className="text-xs text-muted-foreground">Roles</p></div>
                          <div><p className="text-lg font-semibold">{rec.recommendation_data?.total_headcount || 0}</p><p className="text-xs text-muted-foreground">Headcount</p></div>
                        </div>
                      </CardContent>
                      <CardFooter className="pt-3 border-t">
                        <div className="flex justify-end w-full gap-2">
                          <Button variant="ghost" size="sm" onClick={() => handleRejectRec(rec.id)}><X className="h-4 w-4 mr-1" />Reject</Button>
                          <Button size="sm" onClick={() => handleAcceptRec(rec.id)}><Check className="h-4 w-4 mr-1" />Accept</Button>
                        </div>
                      </CardFooter>
                    </Card>
                  ))}
                </div>
              )}
            </>
          )}
        </TabsContent>
      </Tabs>

      {/* Product Dialog */}
      <Dialog open={showProductDialog} onOpenChange={setShowProductDialog}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>{editingProduct ? 'Edit Product' : 'Add Product'}</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Product Name *</Label>
                <Input value={productForm.name} onChange={(e) => setProductForm(p => ({ ...p, name: e.target.value }))} />
              </div>
              <div className="space-y-2">
                <Label>Type</Label>
                <Select value={productForm.product_type} onValueChange={(v) => setProductForm(p => ({ ...p, product_type: v }))}>
                  <SelectTrigger><SelectValue /></SelectTrigger>
                  <SelectContent>{PRODUCT_TYPES.map(t => <SelectItem key={t.value} value={t.value}>{t.label}</SelectItem>)}</SelectContent>
                </Select>
              </div>
            </div>
            <div className="space-y-2">
              <Label>Description</Label>
              <Textarea value={productForm.description} onChange={(e) => setProductForm(p => ({ ...p, description: e.target.value }))} rows={3} />
            </div>
            <div className="space-y-2">
              <Label>Tech Stack</Label>
              <div className="flex flex-wrap gap-2 p-3 border rounded-lg max-h-32 overflow-y-auto">
                {COMMON_TECH_STACKS.map(tech => (
                  <Badge key={tech} variant={productForm.tech_stack.includes(tech) ? 'default' : 'outline'} className="cursor-pointer"
                    onClick={() => setProductForm(p => ({ ...p, tech_stack: p.tech_stack.includes(tech) ? p.tech_stack.filter(t => t !== tech) : [...p.tech_stack, tech] }))}>
                    {tech}
                  </Badge>
                ))}
              </div>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowProductDialog(false)}>Cancel</Button>
            <Button onClick={handleSaveProduct} disabled={isSaving}>{isSaving ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : null}{editingProduct ? 'Update' : 'Create'}</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Department Dialog */}
      <Dialog open={showDeptDialog} onOpenChange={setShowDeptDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{editingDept ? 'Edit Department' : 'Create Department'}</DialogTitle>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div className="space-y-2">
              <Label>Department Name *</Label>
              <Input value={deptForm.name} onChange={(e) => setDeptForm(p => ({ ...p, name: e.target.value }))} />
            </div>
            <div className="space-y-2">
              <Label>Code</Label>
              <Input value={deptForm.code} onChange={(e) => setDeptForm(p => ({ ...p, code: e.target.value }))} placeholder="e.g., ENG" />
            </div>
            <div className="space-y-2">
              <Label>Parent Department</Label>
              <Select value={deptForm.parent_id} onValueChange={(v) => setDeptForm(p => ({ ...p, parent_id: v }))}>
                <SelectTrigger><SelectValue placeholder="Select parent (optional)" /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="">None</SelectItem>
                  {departments.filter(d => d.id !== editingDept?.id).map(d => <SelectItem key={d.id} value={d.id}>{d.name}</SelectItem>)}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label>Department Head</Label>
              <Select value={deptForm.head_employee_id} onValueChange={(v) => setDeptForm(p => ({ ...p, head_employee_id: v }))}>
                <SelectTrigger><SelectValue placeholder="Select head (optional)" /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="">None</SelectItem>
                  {employees.map(e => <SelectItem key={e.id} value={e.id}>{e.full_name}</SelectItem>)}
                </SelectContent>
              </Select>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowDeptDialog(false)}>Cancel</Button>
            <Button onClick={handleSaveDept} disabled={isSaving}>{isSaving ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : null}{editingDept ? 'Save' : 'Create'}</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Designation Dialog */}
      <Dialog open={showDesigDialog} onOpenChange={setShowDesigDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{editingDesig ? 'Edit Designation' : 'Create Designation'}</DialogTitle>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div className="space-y-2">
              <Label>Designation Name *</Label>
              <Input value={desigForm.name} onChange={(e) => setDesigForm(p => ({ ...p, name: e.target.value }))} />
            </div>
            <div className="space-y-2">
              <Label>Code</Label>
              <Input value={desigForm.code} onChange={(e) => setDesigForm(p => ({ ...p, code: e.target.value }))} placeholder="e.g., SWE" />
            </div>
            <div className="space-y-2">
              <Label>Level</Label>
              <Input type="number" value={desigForm.level} onChange={(e) => setDesigForm(p => ({ ...p, level: parseInt(e.target.value) || 1 }))} min={1} max={10} />
              <p className="text-xs text-muted-foreground">1 = Entry level, higher = senior</p>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowDesigDialog(false)}>Cancel</Button>
            <Button onClick={handleSaveDesig} disabled={isSaving}>{isSaving ? <Loader2 className="h-4 w-4 mr-2 animate-spin" /> : null}{editingDesig ? 'Save' : 'Create'}</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Generate Dialog */}
      <Dialog open={showGenerateDialog} onOpenChange={setShowGenerateDialog}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>Generate Organization Structure</DialogTitle>
            <DialogDescription>AI will analyze your company profile and products to recommend an optimal structure.</DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label>Additional Context (Optional)</Label>
              <Textarea placeholder="E.g., We're planning to expand internationally..." value={additionalContext} onChange={(e) => setAdditionalContext(e.target.value)} rows={4} />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowGenerateDialog(false)}>Cancel</Button>
            <Button onClick={handleGenerate} disabled={isGenerating}>
              {isGenerating ? <><Loader2 className="mr-2 h-4 w-4 animate-spin" />Generating...</> : <><Sparkles className="mr-2 h-4 w-4" />Generate</>}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
