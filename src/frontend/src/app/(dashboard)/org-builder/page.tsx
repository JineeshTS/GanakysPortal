'use client'

import { useState, useEffect, useCallback } from 'react'
import { PageHeader } from '@/components/layout/page-header'
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Progress } from '@/components/ui/progress'
import { Skeleton } from '@/components/ui/skeleton'
import { Textarea } from '@/components/ui/textarea'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog'
import { useApi, useToast } from '@/hooks'
import {
  Sparkles,
  Building2,
  Briefcase,
  Users,
  RefreshCw,
  Loader2,
  Check,
  X,
  ChevronDown,
  ChevronRight,
  Clock,
  AlertCircle,
  Wand2,
  Target,
  TrendingUp,
  DollarSign,
  Settings,
  ArrowRight,
} from 'lucide-react'

// Types
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
  items_count?: number
  items_pending?: number
  items_accepted?: number
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
  requirements?: string
  responsibilities?: string
  skills_required?: string
  experience_min: number
  experience_max?: number
  salary_min?: number
  salary_max?: number
  headcount_target: number
  priority: string
  rationale?: string
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

// Format currency in Indian style
function formatCurrency(amount: number): string {
  if (!amount) return '-'
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(amount)
}

// Priority badge colors
function getPriorityColor(priority: string): string {
  switch (priority) {
    case 'immediate': return 'bg-red-100 text-red-800'
    case 'next_quarter': return 'bg-yellow-100 text-yellow-800'
    case 'nice_to_have': return 'bg-green-100 text-green-800'
    default: return 'bg-gray-100 text-gray-800'
  }
}

// Status badge colors
function getStatusColor(status: string): string {
  switch (status) {
    case 'pending': return 'bg-blue-100 text-blue-800'
    case 'accepted': return 'bg-green-100 text-green-800'
    case 'rejected': return 'bg-red-100 text-red-800'
    case 'merged': return 'bg-purple-100 text-purple-800'
    default: return 'bg-gray-100 text-gray-800'
  }
}

export default function OrgBuilderPage() {
  const { get, post } = useApi()
  const { showToast } = useToast()

  const [isLoading, setIsLoading] = useState(true)
  const [isGenerating, setIsGenerating] = useState(false)
  const [summary, setSummary] = useState<DashboardSummary | null>(null)
  const [recommendations, setRecommendations] = useState<Recommendation[]>([])
  const [selectedRec, setSelectedRec] = useState<Recommendation | null>(null)
  const [showDetailDialog, setShowDetailDialog] = useState(false)
  const [showGenerateDialog, setShowGenerateDialog] = useState(false)
  const [additionalContext, setAdditionalContext] = useState('')
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({})
  const [setupStatus, setSetupStatus] = useState<SetupStatus | null>(null)

  // Fetch data on mount
  useEffect(() => {
    let mounted = true

    const loadData = async () => {
      setIsLoading(true)
      try {
        // First check setup status
        const statusData = await get('/company/setup-status').catch(() => null)
        if (mounted && statusData) {
          setSetupStatus(statusData as SetupStatus)
        }

        // Only fetch org-builder data if prerequisites are met
        const [summaryData, recsData] = await Promise.all([
          get('/ai/org-builder/dashboard-summary'),
          get('/ai/org-builder/recommendations?limit=50')
        ])

        if (mounted) {
          if (summaryData) setSummary(summaryData as DashboardSummary)
          if (recsData) setRecommendations((recsData as any).data || [])
        }
      } catch (error) {
        console.error('Failed to load data:', error)
      } finally {
        if (mounted) setIsLoading(false)
      }
    }

    loadData()
    return () => { mounted = false }
  }, [get])

  // Refresh data
  const refreshData = async () => {
    try {
      const [summaryData, recsData] = await Promise.all([
        get('/ai/org-builder/dashboard-summary'),
        get('/ai/org-builder/recommendations?limit=50')
      ])
      if (summaryData) setSummary(summaryData as DashboardSummary)
      if (recsData) setRecommendations((recsData as any).data || [])
    } catch (error) {
      console.error('Failed to refresh data:', error)
    }
  }

  // Generate org structure
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
        await refreshData()
      }
    } catch (error: any) {
      showToast('error', 'Failed', error.message || 'Failed to generate structure')
    } finally {
      setIsGenerating(false)
    }
  }

  // Accept recommendation
  const handleAccept = async (recId: string) => {
    try {
      const data = await post(`/ai/org-builder/recommendations/${recId}/accept`, {}) as any

      if (data?.success) {
        showToast('success', 'Accepted', `Created ${data.departments_created || 0} departments and ${data.designations_created || 0} designations`)
        setShowDetailDialog(false)
        await refreshData()
      }
    } catch (error: any) {
      showToast('error', 'Failed', error.message || 'Failed to accept recommendation')
    }
  }

  // Reject recommendation
  const handleReject = async (recId: string) => {
    try {
      await post(`/ai/org-builder/recommendations/${recId}/reject`, {
        rejection_reason: 'Not suitable for current needs'
      })
      showToast('success', 'Rejected', 'Recommendation rejected')
      setShowDetailDialog(false)
      await refreshData()
    } catch (error: any) {
      showToast('error', 'Failed', error.message || 'Failed to reject recommendation')
    }
  }

  // Toggle section expansion
  const toggleSection = (key: string) => {
    setExpandedSections(prev => ({ ...prev, [key]: !prev[key] }))
  }

  if (isLoading) {
    return (
      <div className="space-y-6">
        <PageHeader title="AI Org Builder" description="Loading..." />
        <div className="grid gap-4 md:grid-cols-4">
          {[1, 2, 3, 4].map(i => (
            <Card key={i}>
              <CardContent className="p-6">
                <Skeleton className="h-8 w-16 mb-2" />
                <Skeleton className="h-4 w-24" />
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    )
  }

  // Check prerequisites - show setup required message if profile is incomplete
  const isProfileComplete = setupStatus?.extended_profile_complete &&
    setupStatus?.company_profile_complete &&
    (setupStatus?.products_added ?? 0) >= (setupStatus?.products_minimum ?? 1)

  if (!isProfileComplete) {
    return (
      <div className="space-y-6">
        <PageHeader
          title="AI Org Builder"
          description="AI-powered organizational structure recommendations"
          breadcrumbs={[
            { label: "Dashboard", href: "/" },
            { label: "HRMS" },
            { label: "AI Org Builder" }
          ]}
        />

        <Card className="max-w-2xl mx-auto">
          <CardContent className="p-8 text-center">
            <div className="w-16 h-16 bg-yellow-100 rounded-full flex items-center justify-center mx-auto mb-6">
              <AlertCircle className="h-8 w-8 text-yellow-600" />
            </div>
            <h2 className="text-xl font-semibold mb-2">Complete Your Company Profile</h2>
            <p className="text-muted-foreground mb-6">
              To use the AI Org Builder, you need to complete your company profile first.
              This helps the AI generate accurate organizational recommendations tailored to your business.
            </p>

            {setupStatus && (
              <div className="mb-6">
                <div className="flex items-center justify-between mb-2 text-sm">
                  <span className="text-muted-foreground">Setup Progress</span>
                  <span className="font-medium">{setupStatus.completion_percentage}%</span>
                </div>
                <Progress value={setupStatus.completion_percentage} className="h-2" />
              </div>
            )}

            {setupStatus?.next_steps && setupStatus.next_steps.length > 0 && (
              <div className="bg-muted rounded-lg p-4 mb-6 text-left">
                <h3 className="font-medium mb-2 flex items-center gap-2">
                  <Settings className="h-4 w-4" />
                  Next Steps
                </h3>
                <ul className="space-y-2">
                  {setupStatus.next_steps.map((step, index) => (
                    <li key={index} className="flex items-center gap-2 text-sm text-muted-foreground">
                      <ChevronRight className="h-4 w-4 flex-shrink-0" />
                      {step}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            <div className="flex flex-col sm:flex-row gap-3 justify-center">
              <Button
                size="lg"
                onClick={() => window.location.href = '/settings/company-profile'}
                className="gap-2"
              >
                Complete Company Profile
                <ArrowRight className="h-4 w-4" />
              </Button>
              {(setupStatus?.products_added ?? 0) < (setupStatus?.products_minimum ?? 1) && (
                <Button
                  size="lg"
                  variant="outline"
                  onClick={() => window.location.href = '/settings/company-profile?tab=products'}
                  className="gap-2"
                >
                  Add Products
                  <ArrowRight className="h-4 w-4" />
                </Button>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  const pendingRecs = recommendations.filter(r => r.status === 'pending')

  return (
    <div className="space-y-6">
      <PageHeader
        title="AI Org Builder"
        description="AI-powered organizational structure recommendations"
        breadcrumbs={[
          { label: "Dashboard", href: "/" },
          { label: "HRMS" },
          { label: "AI Org Builder" }
        ]}
        actions={
          <Button onClick={() => setShowGenerateDialog(true)} disabled={isGenerating}>
            {isGenerating ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Generating...
              </>
            ) : (
              <>
                <Wand2 className="mr-2 h-4 w-4" />
                Generate Structure
              </>
            )}
          </Button>
        }
      />

      {/* Stats Cards */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-blue-100 rounded-full">
                <Sparkles className="h-6 w-6 text-blue-600" />
              </div>
              <div>
                <p className="text-2xl font-bold">{summary?.pending_recommendations || 0}</p>
                <p className="text-sm text-muted-foreground">Pending Suggestions</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-green-100 rounded-full">
                <Building2 className="h-6 w-6 text-green-600" />
              </div>
              <div>
                <p className="text-2xl font-bold">{summary?.total_departments || 0}</p>
                <p className="text-sm text-muted-foreground">Departments</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-purple-100 rounded-full">
                <Briefcase className="h-6 w-6 text-purple-600" />
              </div>
              <div>
                <p className="text-2xl font-bold">{summary?.total_designations || 0}</p>
                <p className="text-sm text-muted-foreground">Designations</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center gap-4">
              <div className="p-3 bg-orange-100 rounded-full">
                <Users className="h-6 w-6 text-orange-600" />
              </div>
              <div>
                <div className="flex items-baseline gap-1">
                  <p className="text-2xl font-bold">{summary?.headcount_current || 0}</p>
                  <p className="text-sm text-muted-foreground">/ {summary?.headcount_target || '-'}</p>
                </div>
                <p className="text-sm text-muted-foreground">Headcount</p>
              </div>
            </div>
            {summary?.headcount_target && summary.headcount_target > 0 && (
              <Progress
                value={(summary.headcount_current / summary.headcount_target) * 100}
                className="mt-3"
              />
            )}
          </CardContent>
        </Card>
      </div>

      {/* Main Content */}
      <Tabs defaultValue="pending" className="space-y-4">
        <TabsList>
          <TabsTrigger value="pending">
            Pending
            {pendingRecs.length > 0 && (
              <Badge variant="secondary" className="ml-2">{pendingRecs.length}</Badge>
            )}
          </TabsTrigger>
          <TabsTrigger value="all">All Recommendations</TabsTrigger>
        </TabsList>

        <TabsContent value="pending" className="space-y-4">
          {pendingRecs.length === 0 ? (
            <Card>
              <CardContent className="p-12 text-center">
                <Sparkles className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                <h3 className="text-lg font-medium mb-2">No Pending Recommendations</h3>
                <p className="text-muted-foreground mb-4">
                  Generate a new organization structure to get AI-powered recommendations.
                </p>
                <Button onClick={() => setShowGenerateDialog(true)}>
                  <Wand2 className="mr-2 h-4 w-4" />
                  Generate Structure
                </Button>
              </CardContent>
            </Card>
          ) : (
            pendingRecs.map(rec => (
              <RecommendationCard
                key={rec.id}
                recommendation={rec}
                onView={() => { setSelectedRec(rec); setShowDetailDialog(true); }}
                onAccept={() => handleAccept(rec.id)}
                onReject={() => handleReject(rec.id)}
              />
            ))
          )}
        </TabsContent>

        <TabsContent value="all" className="space-y-4">
          {recommendations.length === 0 ? (
            <Card>
              <CardContent className="p-12 text-center">
                <Clock className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                <h3 className="text-lg font-medium">No Recommendations Yet</h3>
                <p className="text-muted-foreground">Generate your first organization structure.</p>
              </CardContent>
            </Card>
          ) : (
            recommendations.map(rec => (
              <RecommendationCard
                key={rec.id}
                recommendation={rec}
                onView={() => { setSelectedRec(rec); setShowDetailDialog(true); }}
                onAccept={() => handleAccept(rec.id)}
                onReject={() => handleReject(rec.id)}
              />
            ))
          )}
        </TabsContent>
      </Tabs>

      {/* Generate Dialog */}
      <Dialog open={showGenerateDialog} onOpenChange={setShowGenerateDialog}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>Generate Organization Structure</DialogTitle>
            <DialogDescription>
              AI will analyze your company profile, products, and growth plans to recommend an optimal organization structure.
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Additional Context (Optional)</label>
              <Textarea
                placeholder="E.g., We're planning to expand into international markets..."
                value={additionalContext}
                onChange={(e) => setAdditionalContext(e.target.value)}
                rows={4}
              />
              <p className="text-xs text-muted-foreground">
                Provide any specific requirements or constraints for the AI to consider.
              </p>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowGenerateDialog(false)}>
              Cancel
            </Button>
            <Button onClick={handleGenerate} disabled={isGenerating}>
              {isGenerating ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Generating...
                </>
              ) : (
                <>
                  <Sparkles className="mr-2 h-4 w-4" />
                  Generate
                </>
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Detail Dialog */}
      {selectedRec && (
        <Dialog open={showDetailDialog} onOpenChange={setShowDetailDialog}>
          <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle className="flex items-center gap-2">
                <Sparkles className="h-5 w-5" />
                {selectedRec.recommendation_type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
              </DialogTitle>
              <DialogDescription>
                {selectedRec.recommendation_data?.summary || selectedRec.rationale}
              </DialogDescription>
            </DialogHeader>

            <div className="space-y-6 py-4">
              {/* Stats */}
              <div className="grid grid-cols-3 gap-4">
                <div className="p-4 bg-muted rounded-lg text-center">
                  <p className="text-2xl font-bold">{selectedRec.recommendation_data?.departments?.length || 0}</p>
                  <p className="text-sm text-muted-foreground">Departments</p>
                </div>
                <div className="p-4 bg-muted rounded-lg text-center">
                  <p className="text-2xl font-bold">{selectedRec.recommendation_data?.designations?.length || 0}</p>
                  <p className="text-sm text-muted-foreground">Roles</p>
                </div>
                <div className="p-4 bg-muted rounded-lg text-center">
                  <p className="text-2xl font-bold">{selectedRec.recommendation_data?.total_headcount || 0}</p>
                  <p className="text-sm text-muted-foreground">Total Headcount</p>
                </div>
              </div>

              {/* Departments */}
              {selectedRec.recommendation_data?.departments?.length > 0 && (
                <div className="space-y-2">
                  <button
                    className="flex items-center gap-2 font-medium w-full text-left"
                    onClick={() => toggleSection('departments')}
                  >
                    {expandedSections['departments'] ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
                    <Building2 className="h-4 w-4" />
                    Departments ({selectedRec.recommendation_data.departments.length})
                  </button>
                  {expandedSections['departments'] && (
                    <div className="grid gap-2 pl-6">
                      {selectedRec.recommendation_data.departments.map((dept, i) => (
                        <div key={i} className="p-3 border rounded-lg">
                          <p className="font-medium">{dept.name}</p>
                          {dept.description && <p className="text-sm text-muted-foreground">{dept.description}</p>}
                          {dept.headcount_target && (
                            <Badge variant="outline" className="mt-2">Target: {dept.headcount_target}</Badge>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {/* Designations */}
              {selectedRec.recommendation_data?.designations?.length > 0 && (
                <div className="space-y-2">
                  <button
                    className="flex items-center gap-2 font-medium w-full text-left"
                    onClick={() => toggleSection('designations')}
                  >
                    {expandedSections['designations'] ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
                    <Briefcase className="h-4 w-4" />
                    Roles ({selectedRec.recommendation_data.designations.length})
                  </button>
                  {expandedSections['designations'] && (
                    <div className="grid gap-2 pl-6">
                      {selectedRec.recommendation_data.designations.map((desig, i) => (
                        <div key={i} className="p-3 border rounded-lg">
                          <div className="flex items-start justify-between">
                            <div>
                              <p className="font-medium">{desig.name}</p>
                              <p className="text-sm text-muted-foreground">{desig.department}</p>
                            </div>
                            <Badge className={getPriorityColor(desig.priority)}>{desig.priority}</Badge>
                          </div>
                          {desig.description && (
                            <p className="text-sm mt-2 line-clamp-2">{desig.description}</p>
                          )}
                          <div className="flex gap-4 mt-2 text-xs text-muted-foreground">
                            <span>Exp: {desig.experience_min}-{desig.experience_max || desig.experience_min + 5} yrs</span>
                            {desig.salary_min && desig.salary_max && (
                              <span>Salary: {formatCurrency(desig.salary_min)} - {formatCurrency(desig.salary_max)}</span>
                            )}
                            <span>Headcount: {desig.headcount_target}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {/* Monthly Cost */}
              {selectedRec.recommendation_data?.estimated_monthly_cost && (
                <div className="p-4 bg-blue-50 rounded-lg flex items-center gap-4">
                  <DollarSign className="h-8 w-8 text-blue-600" />
                  <div>
                    <p className="text-sm text-blue-600 font-medium">Estimated Monthly Cost</p>
                    <p className="text-xl font-bold text-blue-800">
                      {formatCurrency(selectedRec.recommendation_data.estimated_monthly_cost)}
                    </p>
                  </div>
                </div>
              )}
            </div>

            <DialogFooter>
              {selectedRec.status === 'pending' && (
                <>
                  <Button variant="outline" onClick={() => handleReject(selectedRec.id)}>
                    <X className="mr-2 h-4 w-4" />
                    Reject
                  </Button>
                  <Button onClick={() => handleAccept(selectedRec.id)}>
                    <Check className="mr-2 h-4 w-4" />
                    Accept & Apply
                  </Button>
                </>
              )}
              {selectedRec.status !== 'pending' && (
                <Button variant="outline" onClick={() => setShowDetailDialog(false)}>
                  Close
                </Button>
              )}
            </DialogFooter>
          </DialogContent>
        </Dialog>
      )}
    </div>
  )
}

// Recommendation Card Component
interface RecommendationCardProps {
  recommendation: Recommendation
  onView: () => void
  onAccept: () => void
  onReject: () => void
}

function RecommendationCard({ recommendation, onView, onAccept, onReject }: RecommendationCardProps) {
  const rec = recommendation
  const data = rec.recommendation_data

  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-primary/10 rounded-lg">
              <Sparkles className="h-5 w-5 text-primary" />
            </div>
            <div>
              <CardTitle className="text-base">
                {rec.recommendation_type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
              </CardTitle>
              <CardDescription className="text-xs">
                {new Date(rec.created_at).toLocaleDateString('en-IN', {
                  day: 'numeric',
                  month: 'short',
                  year: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit'
                })}
              </CardDescription>
            </div>
          </div>
          <Badge className={getStatusColor(rec.status)}>{rec.status}</Badge>
        </div>
      </CardHeader>
      <CardContent className="pb-3">
        <p className="text-sm text-muted-foreground line-clamp-2 mb-4">
          {data?.summary || rec.rationale}
        </p>
        <div className="grid grid-cols-4 gap-4 text-center">
          <div>
            <p className="text-lg font-semibold">{data?.departments?.length || 0}</p>
            <p className="text-xs text-muted-foreground">Departments</p>
          </div>
          <div>
            <p className="text-lg font-semibold">{data?.designations?.length || 0}</p>
            <p className="text-xs text-muted-foreground">Roles</p>
          </div>
          <div>
            <p className="text-lg font-semibold">{data?.total_headcount || 0}</p>
            <p className="text-xs text-muted-foreground">Headcount</p>
          </div>
          <div>
            <p className="text-lg font-semibold">{Math.round((rec.confidence_score || 0.8) * 100)}%</p>
            <p className="text-xs text-muted-foreground">Confidence</p>
          </div>
        </div>
      </CardContent>
      <CardFooter className="pt-3 border-t">
        <div className="flex justify-between w-full">
          <Button variant="outline" size="sm" onClick={onView}>
            View Details
          </Button>
          {rec.status === 'pending' && (
            <div className="flex gap-2">
              <Button variant="ghost" size="sm" onClick={onReject}>
                <X className="h-4 w-4 mr-1" />
                Reject
              </Button>
              <Button size="sm" onClick={onAccept}>
                <Check className="h-4 w-4 mr-1" />
                Accept
              </Button>
            </div>
          )}
        </div>
      </CardFooter>
    </Card>
  )
}
