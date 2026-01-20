'use client'

import { useState, useEffect, useCallback } from 'react'
import { PageHeader } from '@/components/layout/page-header'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Skeleton } from '@/components/ui/skeleton'
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
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { useApi, useToast } from '@/hooks'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog'
import {
  Briefcase,
  Plus,
  Search,
  Users,
  Clock,
  CheckCircle,
  XCircle,
  Calendar,
  MapPin,
  IndianRupee,
  MoreVertical,
  Eye,
  Mail,
  Phone,
  Edit,
  Trash2,
  UserPlus,
  Loader2,
  RefreshCw,
  Building2,
  Globe,
  FileText,
  Sparkles,
  AlertTriangle
} from 'lucide-react'

// Types
interface RecruitmentStats {
  total_openings: number
  open_positions: number
  total_candidates: number
  total_applications: number
  pending_interviews: number
  offers_extended: number
  hired_this_month: number
}

interface JobOpening {
  id: string
  company_id: string
  job_code: string
  title: string
  department_id?: string
  department_name?: string
  designation_id?: string
  designation_name?: string
  reporting_to_id?: string
  reporting_to_name?: string
  description?: string
  requirements?: string
  responsibilities?: string
  skills_required?: string
  experience_min: number
  experience_max?: number
  salary_min?: string
  salary_max?: string
  location?: string
  job_type: string
  status: string
  positions_total: number
  positions_filled: number
  posted_date?: string
  closing_date?: string
  is_remote: boolean
  applications_count: number
  created_at: string
  updated_at: string
}

interface Candidate {
  id: string
  company_id: string
  first_name: string
  last_name: string
  full_name: string
  email: string
  phone?: string
  date_of_birth?: string
  gender?: string
  current_location?: string
  preferred_location?: string
  resume_url?: string
  linkedin_url?: string
  portfolio_url?: string
  current_company?: string
  current_designation?: string
  current_salary?: string
  expected_salary?: string
  notice_period_days?: number
  total_experience_years?: string
  relevant_experience_years?: string
  highest_qualification?: string
  skills?: string
  source: string
  source_details?: string
  status: string
  rating?: number
  notes?: string
  employee_id?: string
  applications_count: number
  created_at: string
  updated_at: string
}

interface JobApplication {
  id: string
  company_id: string
  job_id: string
  job_title?: string
  candidate_id: string
  candidate_name?: string
  candidate_email?: string
  applied_date: string
  stage: string
  stage_updated_at: string
  expected_salary?: string
  available_from?: string
  cover_letter?: string
  screening_score?: number
  technical_score?: number
  hr_score?: number
  overall_rating?: number
  rejection_reason?: string
  notes?: string
  interviews_count: number
  created_at: string
  updated_at: string
}

interface JobListResponse {
  success: boolean
  data: JobOpening[]
  meta: { page: number; limit: number; total: number }
}

interface CandidateListResponse {
  success: boolean
  data: Candidate[]
  meta: { page: number; limit: number; total: number }
}

interface ApplicationListResponse {
  success: boolean
  data: JobApplication[]
  meta: { page: number; limit: number; total: number }
}

interface HireResponse {
  success: boolean
  message: string
  employee_id: string
  onboarding_session_id?: string
}

const stageColors: Record<string, string> = {
  applied: 'bg-gray-100 text-gray-800',
  screening: 'bg-gray-100 text-gray-800',
  phone_screen: 'bg-blue-100 text-blue-800',
  technical_round: 'bg-blue-100 text-blue-800',
  hr_round: 'bg-blue-100 text-blue-800',
  final_round: 'bg-purple-100 text-purple-800',
  offer_extended: 'bg-yellow-100 text-yellow-800',
  offer_accepted: 'bg-green-100 text-green-800',
  offer_rejected: 'bg-orange-100 text-orange-800',
  hired: 'bg-green-100 text-green-800',
  rejected: 'bg-red-100 text-red-800',
}

const statusColors: Record<string, string> = {
  draft: 'bg-gray-100 text-gray-800',
  open: 'bg-green-100 text-green-800',
  on_hold: 'bg-yellow-100 text-yellow-800',
  closed: 'bg-gray-100 text-gray-800',
  cancelled: 'bg-red-100 text-red-800',
}

const candidateStatusColors: Record<string, string> = {
  new: 'bg-blue-100 text-blue-800',
  screening: 'bg-gray-100 text-gray-800',
  shortlisted: 'bg-yellow-100 text-yellow-800',
  interview: 'bg-purple-100 text-purple-800',
  offer: 'bg-green-100 text-green-800',
  hired: 'bg-green-100 text-green-800',
  rejected: 'bg-red-100 text-red-800',
  withdrawn: 'bg-gray-100 text-gray-800',
}

const jobTypes: Record<string, string> = {
  full_time: 'Full-time',
  part_time: 'Part-time',
  contract: 'Contract',
  intern: 'Internship',
  consultant: 'Consultant',
}

const stageLabels: Record<string, string> = {
  applied: 'Applied',
  screening: 'Screening',
  phone_screen: 'Phone Screen',
  technical_round: 'Technical',
  hr_round: 'HR Round',
  final_round: 'Final Round',
  offer_extended: 'Offer Extended',
  offer_accepted: 'Offer Accepted',
  offer_rejected: 'Offer Rejected',
  hired: 'Hired',
  rejected: 'Rejected',
}

export default function RecruitmentPage() {
  const [searchQuery, setSearchQuery] = useState('')
  const [activeTab, setActiveTab] = useState('openings')
  const [isNewJobOpen, setIsNewJobOpen] = useState(false)
  const [isNewCandidateOpen, setIsNewCandidateOpen] = useState(false)
  const [isApplyOpen, setIsApplyOpen] = useState(false)
  const [isHireOpen, setIsHireOpen] = useState(false)
  const [selectedJob, setSelectedJob] = useState<JobOpening | null>(null)
  const [selectedCandidate, setSelectedCandidate] = useState<Candidate | null>(null)
  const [selectedApplication, setSelectedApplication] = useState<JobApplication | null>(null)
  const { showToast } = useToast()

  // Form states
  const [newJobForm, setNewJobForm] = useState({
    title: '',
    description: '',
    requirements: '',
    responsibilities: '',
    location: '',
    job_type: 'full_time',
    experience_min: 0,
    experience_max: 0,
    salary_min: '',
    salary_max: '',
    positions_total: 1,
    is_remote: false,
  })

  const [newCandidateForm, setNewCandidateForm] = useState({
    first_name: '',
    last_name: '',
    email: '',
    phone: '',
    current_location: '',
    current_company: '',
    current_designation: '',
    current_salary: '',
    expected_salary: '',
    notice_period_days: 30,
    total_experience_years: '',
    highest_qualification: '',
    skills: '',
    source: 'direct',
    notes: '',
  })

  const [applyForm, setApplyForm] = useState({
    job_id: '',
    candidate_id: '',
    expected_salary: '',
    cover_letter: '',
  })

  const [hireForm, setHireForm] = useState({
    application_id: '',
    date_of_joining: '',
    employment_type: 'full_time',
    create_onboarding: true,
  })

  // API hooks
  const { data: statsData, isLoading: isLoadingStats, get: getStats } = useApi<RecruitmentStats>()
  const { data: jobsData, isLoading: isLoadingJobs, get: getJobs } = useApi<JobListResponse>()
  const { data: candidatesData, isLoading: isLoadingCandidates, get: getCandidates } = useApi<CandidateListResponse>()
  const { data: applicationsData, isLoading: isLoadingApplications, get: getApplications } = useApi<ApplicationListResponse>()
  const { isLoading: isCreatingJob, post: createJob, error: createJobError } = useApi<JobOpening>()
  const { isLoading: isGeneratingAI, post: generateAI } = useApi<{ description: string; requirements: string; responsibilities: string; skills_required: string; experience_min: number; experience_max: number; salary_min: number; salary_max: number }>()
  const { isLoading: isCreatingCandidate, post: createCandidate } = useApi<Candidate>()
  const { isLoading: isCreatingApplication, post: createApplication } = useApi<JobApplication>()
  const { isLoading: isHiring, post: hireCandidate } = useApi<HireResponse>()
  const { put: updateJob } = useApi<JobOpening>()
  const { put: updateApplication } = useApi<JobApplication>()
  const deleteJobApi = useApi()
  const deleteCandidateApi = useApi()

  // Local state for data management
  const [localJobs, setLocalJobs] = useState<JobOpening[]>([])
  const [localCandidates, setLocalCandidates] = useState<Candidate[]>([])

  // Delete state for jobs
  const [deleteJobDialogOpen, setDeleteJobDialogOpen] = useState(false)
  const [jobToDelete, setJobToDelete] = useState<JobOpening | null>(null)
  const [isDeletingJob, setIsDeletingJob] = useState(false)

  // Delete state for candidates
  const [deleteCandidateDialogOpen, setDeleteCandidateDialogOpen] = useState(false)
  const [candidateToDelete, setCandidateToDelete] = useState<Candidate | null>(null)
  const [isDeletingCandidate, setIsDeletingCandidate] = useState(false)

  const handleDeleteJobClick = (job: JobOpening) => {
    setJobToDelete(job)
    setDeleteJobDialogOpen(true)
  }

  const handleDeleteJobConfirm = async () => {
    if (!jobToDelete) return
    setIsDeletingJob(true)
    try {
      await deleteJobApi.delete(`/recruitment/jobs/${jobToDelete.id}`)
      setLocalJobs(localJobs.filter(j => j.id !== jobToDelete.id))
      setDeleteJobDialogOpen(false)
      setJobToDelete(null)
      showToast('success', 'Job opening deleted successfully')
    } catch (error) {
      showToast('error', 'Failed to delete job opening')
    } finally {
      setIsDeletingJob(false)
    }
  }

  const handleDeleteCandidateClick = (candidate: Candidate) => {
    setCandidateToDelete(candidate)
    setDeleteCandidateDialogOpen(true)
  }

  const handleDeleteCandidateConfirm = async () => {
    if (!candidateToDelete) return
    setIsDeletingCandidate(true)
    try {
      await deleteCandidateApi.delete(`/recruitment/candidates/${candidateToDelete.id}`)
      setLocalCandidates(localCandidates.filter(c => c.id !== candidateToDelete.id))
      setDeleteCandidateDialogOpen(false)
      setCandidateToDelete(null)
      showToast('success', 'Candidate deleted successfully')
    } catch (error) {
      showToast('error', 'Failed to delete candidate')
    } finally {
      setIsDeletingCandidate(false)
    }
  }

  // Fetch data
  const fetchData = useCallback(() => {
    getStats('/recruitment/stats')
    getJobs('/recruitment/jobs?page=1&limit=50')
    getCandidates('/recruitment/candidates?page=1&limit=50')
    getApplications('/recruitment/applications?page=1&limit=100')
  }, [getStats, getJobs, getCandidates, getApplications])

  useEffect(() => {
    fetchData()
  }, [fetchData])

  // Sync API data to local state
  useEffect(() => {
    if (jobsData?.data) {
      setLocalJobs(jobsData.data)
    }
  }, [jobsData])

  useEffect(() => {
    if (candidatesData?.data) {
      setLocalCandidates(candidatesData.data)
    }
  }, [candidatesData])

  // Stats
  const stats = statsData || {
    total_openings: 0,
    open_positions: 0,
    total_candidates: 0,
    total_applications: 0,
    pending_interviews: 0,
    offers_extended: 0,
    hired_this_month: 0,
  }

  const jobs = localJobs.length > 0 ? localJobs : (jobsData?.data || [])
  const candidates = localCandidates.length > 0 ? localCandidates : (candidatesData?.data || [])
  const applications = applicationsData?.data || []

  // Filter jobs by search
  const filteredJobs = jobs.filter(job => {
    if (!searchQuery) return true
    return (
      job.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      job.job_code.toLowerCase().includes(searchQuery.toLowerCase()) ||
      job.location?.toLowerCase().includes(searchQuery.toLowerCase())
    )
  })

  // Filter candidates by search
  const filteredCandidates = candidates.filter(candidate => {
    if (!searchQuery) return true
    return (
      candidate.full_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      candidate.email.toLowerCase().includes(searchQuery.toLowerCase()) ||
      candidate.current_company?.toLowerCase().includes(searchQuery.toLowerCase())
    )
  })

  // Handlers
  const handleAIGenerate = async () => {
    if (!newJobForm.title) {
      showToast('error', 'Please enter a job title first')
      return
    }

    showToast('info', 'AI is generating job details...')
    const result = await generateAI('/recruitment/jobs/ai-generate', {
      title: newJobForm.title,
      job_type: newJobForm.job_type,
      location: newJobForm.location || undefined,
      is_remote: newJobForm.is_remote,
    })

    if (result) {
      setNewJobForm(prev => ({
        ...prev,
        description: result.description || prev.description,
        requirements: result.requirements || prev.requirements,
        responsibilities: result.responsibilities || prev.responsibilities,
        experience_min: result.experience_min ?? prev.experience_min,
        experience_max: result.experience_max ?? prev.experience_max,
        salary_min: result.salary_min?.toString() || prev.salary_min,
        salary_max: result.salary_max?.toString() || prev.salary_max,
      }))
      showToast('success', 'AI generated job details! Review and edit as needed.')
    } else {
      showToast('error', 'Failed to generate job details. Please fill manually.')
    }
  }

  const handleCreateJob = async () => {
    if (!newJobForm.title) {
      showToast('error', 'Please enter a job title')
      return
    }

    const result = await createJob('/recruitment/jobs', {
      ...newJobForm,
      salary_min: newJobForm.salary_min ? parseFloat(newJobForm.salary_min) : undefined,
      salary_max: newJobForm.salary_max ? parseFloat(newJobForm.salary_max) : undefined,
    })

    if (result) {
      showToast('success', 'Job opening created successfully')
      setIsNewJobOpen(false)
      setNewJobForm({
        title: '',
        description: '',
        requirements: '',
        responsibilities: '',
        location: '',
        job_type: 'full_time',
        experience_min: 0,
        experience_max: 0,
        salary_min: '',
        salary_max: '',
        positions_total: 1,
        is_remote: false,
      })
      fetchData()
    } else {
      showToast('error', createJobError || 'Failed to create job. Please try again.')
    }
  }

  const handlePublishJob = async (jobId: string) => {
    const result = await updateJob(`/recruitment/jobs/${jobId}`, { status: 'open' })
    if (result) {
      showToast('success', 'Job published successfully')
      fetchData()
    }
  }

  const handleCreateCandidate = async () => {
    if (!newCandidateForm.first_name || !newCandidateForm.last_name || !newCandidateForm.email) {
      showToast('error', 'Please enter name and email')
      return
    }

    const result = await createCandidate('/recruitment/candidates', {
      ...newCandidateForm,
      current_salary: newCandidateForm.current_salary ? parseFloat(newCandidateForm.current_salary) : undefined,
      expected_salary: newCandidateForm.expected_salary ? parseFloat(newCandidateForm.expected_salary) : undefined,
      total_experience_years: newCandidateForm.total_experience_years ? parseFloat(newCandidateForm.total_experience_years) : undefined,
    })

    if (result) {
      showToast('success', 'Candidate added successfully')
      setIsNewCandidateOpen(false)
      setNewCandidateForm({
        first_name: '',
        last_name: '',
        email: '',
        phone: '',
        current_location: '',
        current_company: '',
        current_designation: '',
        current_salary: '',
        expected_salary: '',
        notice_period_days: 30,
        total_experience_years: '',
        highest_qualification: '',
        skills: '',
        source: 'direct',
        notes: '',
      })
      fetchData()
    }
  }

  const handleApplyToJob = async () => {
    if (!applyForm.job_id || !applyForm.candidate_id) {
      showToast('error', 'Please select a job and candidate')
      return
    }

    const result = await createApplication('/recruitment/applications', {
      job_id: applyForm.job_id,
      candidate_id: applyForm.candidate_id,
      expected_salary: applyForm.expected_salary ? parseFloat(applyForm.expected_salary) : undefined,
      cover_letter: applyForm.cover_letter || undefined,
    })

    if (result) {
      showToast('success', 'Application created successfully')
      setIsApplyOpen(false)
      setApplyForm({
        job_id: '',
        candidate_id: '',
        expected_salary: '',
        cover_letter: '',
      })
      fetchData()
    }
  }

  const handleMoveStage = async (applicationId: string, newStage: string) => {
    const result = await updateApplication(`/recruitment/applications/${applicationId}`, { stage: newStage })
    if (result) {
      showToast('success', `Application moved to ${stageLabels[newStage] || newStage}`)
      fetchData()
    }
  }

  const handleHire = async () => {
    if (!hireForm.application_id || !hireForm.date_of_joining) {
      showToast('error', 'Please fill all required fields')
      return
    }

    const result = await hireCandidate('/recruitment/hire', {
      application_id: hireForm.application_id,
      date_of_joining: hireForm.date_of_joining,
      employment_type: hireForm.employment_type,
      create_onboarding: hireForm.create_onboarding,
    })

    if (result) {
      showToast('success', result.message || 'Candidate hired successfully!')
      setIsHireOpen(false)
      setHireForm({
        application_id: '',
        date_of_joining: '',
        employment_type: 'full_time',
        create_onboarding: true,
      })
      fetchData()
    }
  }

  const formatSalary = (min?: string, max?: string) => {
    if (!min && !max) return 'Not disclosed'
    const formatNum = (num: string) => {
      const n = parseFloat(num)
      if (n >= 100000) return `${(n / 100000).toFixed(1)} LPA`
      if (n >= 1000) return `${(n / 1000).toFixed(0)}K`
      return num
    }
    if (min && max) return `${formatNum(min)} - ${formatNum(max)}`
    if (min) return `From ${formatNum(min)}`
    return `Up to ${formatNum(max!)}`
  }

  // Loading skeleton
  if (isLoadingStats || isLoadingJobs || isLoadingCandidates) {
    return (
      <div className="space-y-6">
        <PageHeader
          title="Recruitment"
          description="Manage job openings and candidate pipeline"
          icon={Briefcase}
        />
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map((i) => (
            <Card key={i}>
              <CardContent className="pt-6">
                <Skeleton className="h-16 w-full" />
              </CardContent>
            </Card>
          ))}
        </div>
        <Card>
          <CardContent className="pt-6">
            <Skeleton className="h-64 w-full" />
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Recruitment"
        description="Manage job openings and candidate pipeline"
        icon={Briefcase}
        actions={
          <div className="flex gap-2">
            <Button variant="outline" onClick={fetchData}>
              <RefreshCw className="h-4 w-4 mr-2" />
              Refresh
            </Button>
            <Dialog open={isNewJobOpen} onOpenChange={setIsNewJobOpen}>
              <DialogTrigger asChild>
                <Button>
                  <Plus className="h-4 w-4 mr-2" />
                  Post New Job
                </Button>
              </DialogTrigger>
              <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
                <DialogHeader>
                  <DialogTitle>Create Job Opening</DialogTitle>
                  <DialogDescription>Create a new job opening for your company</DialogDescription>
                </DialogHeader>
                <div className="grid gap-4 py-4">
                  <div className="grid gap-2">
                    <Label>Job Title *</Label>
                    <div className="flex gap-2">
                      <Input
                        value={newJobForm.title}
                        onChange={(e) => setNewJobForm({ ...newJobForm, title: e.target.value })}
                        placeholder="e.g., Senior Software Engineer"
                        className="flex-1"
                      />
                      <Button
                        type="button"
                        variant="outline"
                        onClick={handleAIGenerate}
                        disabled={isGeneratingAI || !newJobForm.title}
                        className="shrink-0"
                      >
                        {isGeneratingAI ? (
                          <Loader2 className="h-4 w-4 animate-spin mr-2" />
                        ) : (
                          <Sparkles className="h-4 w-4 mr-2" />
                        )}
                        AI Fill
                      </Button>
                    </div>
                    <p className="text-xs text-muted-foreground">Enter job title and click "AI Fill" to auto-generate description, requirements, and salary range</p>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="grid gap-2">
                      <Label>Job Type</Label>
                      <Select
                        value={newJobForm.job_type}
                        onValueChange={(v) => setNewJobForm({ ...newJobForm, job_type: v })}
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          {Object.entries(jobTypes).map(([value, label]) => (
                            <SelectItem key={value} value={value}>{label}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="grid gap-2">
                      <Label>Location</Label>
                      <Input
                        value={newJobForm.location}
                        onChange={(e) => setNewJobForm({ ...newJobForm, location: e.target.value })}
                        placeholder="e.g., Bengaluru, Mumbai"
                      />
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="grid gap-2">
                      <Label>Min Experience (years)</Label>
                      <Input
                        type="number"
                        value={newJobForm.experience_min}
                        onChange={(e) => setNewJobForm({ ...newJobForm, experience_min: parseInt(e.target.value) || 0 })}
                      />
                    </div>
                    <div className="grid gap-2">
                      <Label>Max Experience (years)</Label>
                      <Input
                        type="number"
                        value={newJobForm.experience_max}
                        onChange={(e) => setNewJobForm({ ...newJobForm, experience_max: parseInt(e.target.value) || 0 })}
                      />
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="grid gap-2">
                      <Label>Min Salary (Annual)</Label>
                      <Input
                        type="number"
                        value={newJobForm.salary_min}
                        onChange={(e) => setNewJobForm({ ...newJobForm, salary_min: e.target.value })}
                        placeholder="e.g., 1500000"
                      />
                    </div>
                    <div className="grid gap-2">
                      <Label>Max Salary (Annual)</Label>
                      <Input
                        type="number"
                        value={newJobForm.salary_max}
                        onChange={(e) => setNewJobForm({ ...newJobForm, salary_max: e.target.value })}
                        placeholder="e.g., 2500000"
                      />
                    </div>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="grid gap-2">
                      <Label>Positions</Label>
                      <Input
                        type="number"
                        value={newJobForm.positions_total}
                        onChange={(e) => setNewJobForm({ ...newJobForm, positions_total: parseInt(e.target.value) || 1 })}
                        min={1}
                      />
                    </div>
                    <div className="grid gap-2 items-center">
                      <Label>Remote Work</Label>
                      <div className="flex items-center gap-2">
                        <input
                          type="checkbox"
                          checked={newJobForm.is_remote}
                          onChange={(e) => setNewJobForm({ ...newJobForm, is_remote: e.target.checked })}
                          className="h-4 w-4"
                        />
                        <span className="text-sm">Allow remote work</span>
                      </div>
                    </div>
                  </div>
                  <div className="grid gap-2">
                    <Label>Job Description</Label>
                    <Textarea
                      value={newJobForm.description}
                      onChange={(e) => setNewJobForm({ ...newJobForm, description: e.target.value })}
                      rows={3}
                      placeholder="Describe the role and responsibilities..."
                    />
                  </div>
                  <div className="grid gap-2">
                    <Label>Requirements</Label>
                    <Textarea
                      value={newJobForm.requirements}
                      onChange={(e) => setNewJobForm({ ...newJobForm, requirements: e.target.value })}
                      rows={3}
                      placeholder="Skills and qualifications required..."
                    />
                  </div>
                </div>
                <DialogFooter>
                  <Button variant="outline" onClick={() => setIsNewJobOpen(false)}>Cancel</Button>
                  <Button onClick={handleCreateJob} disabled={isCreatingJob}>
                    {isCreatingJob ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
                    Create Job
                  </Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
          </div>
        }
      />

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-green-100 rounded-lg">
                <Briefcase className="h-5 w-5 text-green-600" />
              </div>
              <div>
                <p className="text-2xl font-bold">{stats.open_positions}</p>
                <p className="text-sm text-muted-foreground">Open Positions</p>
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
                <p className="text-2xl font-bold">{stats.total_candidates}</p>
                <p className="text-sm text-muted-foreground">Total Candidates</p>
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
                <p className="text-2xl font-bold">{stats.pending_interviews}</p>
                <p className="text-sm text-muted-foreground">Pending Interviews</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-purple-100 rounded-lg">
                <CheckCircle className="h-5 w-5 text-purple-600" />
              </div>
              <div>
                <p className="text-2xl font-bold">{stats.hired_this_month}</p>
                <p className="text-sm text-muted-foreground">Hired This Month</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="openings">Job Openings ({jobs.length})</TabsTrigger>
          <TabsTrigger value="candidates">Candidates ({candidates.length})</TabsTrigger>
          <TabsTrigger value="pipeline">Pipeline ({applications.length})</TabsTrigger>
        </TabsList>

        <TabsContent value="openings" className="mt-4">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Job Openings</CardTitle>
                  <CardDescription>Manage open positions</CardDescription>
                </div>
                <div className="relative w-64">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <Input
                    placeholder="Search jobs..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-9"
                  />
                </div>
              </div>
            </CardHeader>
            <CardContent>
              {filteredJobs.length === 0 ? (
                <div className="text-center py-12 text-muted-foreground">
                  <Briefcase className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>No job openings found</p>
                  <Button className="mt-4" onClick={() => setIsNewJobOpen(true)}>
                    <Plus className="h-4 w-4 mr-2" />
                    Create First Job
                  </Button>
                </div>
              ) : (
                <div className="space-y-4">
                  {filteredJobs.map((job) => (
                    <div key={job.id} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                      <div className="flex items-start justify-between">
                        <div>
                          <div className="flex items-center gap-2">
                            <h3 className="font-semibold">{job.title}</h3>
                            <Badge className={statusColors[job.status]}>{job.status}</Badge>
                            {job.is_remote && <Badge variant="outline"><Globe className="h-3 w-3 mr-1" />Remote</Badge>}
                          </div>
                          <p className="text-sm text-muted-foreground mt-1">{job.job_code}</p>
                          <div className="flex items-center gap-4 mt-2 text-sm text-muted-foreground">
                            {job.location && (
                              <span className="flex items-center gap-1">
                                <MapPin className="h-3 w-3" /> {job.location}
                              </span>
                            )}
                            <span className="flex items-center gap-1">
                              <Briefcase className="h-3 w-3" /> {jobTypes[job.job_type] || job.job_type}
                            </span>
                            <span className="flex items-center gap-1">
                              <IndianRupee className="h-3 w-3" /> {formatSalary(job.salary_min, job.salary_max)}
                            </span>
                            <span className="flex items-center gap-1">
                              <Users className="h-3 w-3" /> {job.positions_filled}/{job.positions_total} filled
                            </span>
                          </div>
                        </div>
                        <div className="text-right">
                          <p className="text-2xl font-bold text-primary">{job.applications_count}</p>
                          <p className="text-xs text-muted-foreground">applicants</p>
                          <div className="flex gap-2 mt-2">
                            {job.status === 'draft' && (
                              <Button variant="default" size="sm" onClick={() => handlePublishJob(job.id)}>
                                Publish
                              </Button>
                            )}
                            <Button variant="outline" size="sm">
                              <Eye className="h-3 w-3 mr-1" /> View
                            </Button>
                            {job.status === 'cancelled' && (
                              <Button
                                variant="outline"
                                size="sm"
                                className="text-red-600 hover:text-red-700 hover:bg-red-50"
                                onClick={() => handleDeleteJobClick(job)}
                              >
                                <Trash2 className="h-3 w-3 mr-1" /> Delete
                              </Button>
                            )}
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="candidates" className="mt-4">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>All Candidates</CardTitle>
                  <CardDescription>Review and manage applicants</CardDescription>
                </div>
                <div className="flex gap-2">
                  <div className="relative w-64">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                    <Input
                      placeholder="Search candidates..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="pl-9"
                    />
                  </div>
                  <Dialog open={isNewCandidateOpen} onOpenChange={setIsNewCandidateOpen}>
                    <DialogTrigger asChild>
                      <Button>
                        <UserPlus className="h-4 w-4 mr-2" />
                        Add Candidate
                      </Button>
                    </DialogTrigger>
                    <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
                      <DialogHeader>
                        <DialogTitle>Add Candidate</DialogTitle>
                        <DialogDescription>Add a new candidate to your talent pool</DialogDescription>
                      </DialogHeader>
                      <div className="grid gap-4 py-4">
                        <div className="grid grid-cols-2 gap-4">
                          <div className="grid gap-2">
                            <Label>First Name *</Label>
                            <Input
                              value={newCandidateForm.first_name}
                              onChange={(e) => setNewCandidateForm({ ...newCandidateForm, first_name: e.target.value })}
                            />
                          </div>
                          <div className="grid gap-2">
                            <Label>Last Name *</Label>
                            <Input
                              value={newCandidateForm.last_name}
                              onChange={(e) => setNewCandidateForm({ ...newCandidateForm, last_name: e.target.value })}
                            />
                          </div>
                        </div>
                        <div className="grid grid-cols-2 gap-4">
                          <div className="grid gap-2">
                            <Label>Email *</Label>
                            <Input
                              type="email"
                              value={newCandidateForm.email}
                              onChange={(e) => setNewCandidateForm({ ...newCandidateForm, email: e.target.value })}
                            />
                          </div>
                          <div className="grid gap-2">
                            <Label>Phone</Label>
                            <Input
                              value={newCandidateForm.phone}
                              onChange={(e) => setNewCandidateForm({ ...newCandidateForm, phone: e.target.value })}
                            />
                          </div>
                        </div>
                        <div className="grid grid-cols-2 gap-4">
                          <div className="grid gap-2">
                            <Label>Current Company</Label>
                            <Input
                              value={newCandidateForm.current_company}
                              onChange={(e) => setNewCandidateForm({ ...newCandidateForm, current_company: e.target.value })}
                            />
                          </div>
                          <div className="grid gap-2">
                            <Label>Current Designation</Label>
                            <Input
                              value={newCandidateForm.current_designation}
                              onChange={(e) => setNewCandidateForm({ ...newCandidateForm, current_designation: e.target.value })}
                            />
                          </div>
                        </div>
                        <div className="grid grid-cols-2 gap-4">
                          <div className="grid gap-2">
                            <Label>Current Salary (Annual)</Label>
                            <Input
                              type="number"
                              value={newCandidateForm.current_salary}
                              onChange={(e) => setNewCandidateForm({ ...newCandidateForm, current_salary: e.target.value })}
                            />
                          </div>
                          <div className="grid gap-2">
                            <Label>Expected Salary (Annual)</Label>
                            <Input
                              type="number"
                              value={newCandidateForm.expected_salary}
                              onChange={(e) => setNewCandidateForm({ ...newCandidateForm, expected_salary: e.target.value })}
                            />
                          </div>
                        </div>
                        <div className="grid grid-cols-2 gap-4">
                          <div className="grid gap-2">
                            <Label>Total Experience (years)</Label>
                            <Input
                              type="number"
                              value={newCandidateForm.total_experience_years}
                              onChange={(e) => setNewCandidateForm({ ...newCandidateForm, total_experience_years: e.target.value })}
                            />
                          </div>
                          <div className="grid gap-2">
                            <Label>Notice Period (days)</Label>
                            <Input
                              type="number"
                              value={newCandidateForm.notice_period_days}
                              onChange={(e) => setNewCandidateForm({ ...newCandidateForm, notice_period_days: parseInt(e.target.value) || 0 })}
                            />
                          </div>
                        </div>
                        <div className="grid gap-2">
                          <Label>Location</Label>
                          <Input
                            value={newCandidateForm.current_location}
                            onChange={(e) => setNewCandidateForm({ ...newCandidateForm, current_location: e.target.value })}
                          />
                        </div>
                        <div className="grid gap-2">
                          <Label>Skills</Label>
                          <Input
                            value={newCandidateForm.skills}
                            onChange={(e) => setNewCandidateForm({ ...newCandidateForm, skills: e.target.value })}
                            placeholder="e.g., Python, JavaScript, React"
                          />
                        </div>
                        <div className="grid gap-2">
                          <Label>Source</Label>
                          <Select
                            value={newCandidateForm.source}
                            onValueChange={(v) => setNewCandidateForm({ ...newCandidateForm, source: v })}
                          >
                            <SelectTrigger>
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="direct">Direct</SelectItem>
                              <SelectItem value="linkedin">LinkedIn</SelectItem>
                              <SelectItem value="referral">Referral</SelectItem>
                              <SelectItem value="job_portal">Job Portal</SelectItem>
                              <SelectItem value="agency">Agency</SelectItem>
                              <SelectItem value="campus">Campus</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                        <div className="grid gap-2">
                          <Label>Notes</Label>
                          <Textarea
                            value={newCandidateForm.notes}
                            onChange={(e) => setNewCandidateForm({ ...newCandidateForm, notes: e.target.value })}
                            rows={2}
                          />
                        </div>
                      </div>
                      <DialogFooter>
                        <Button variant="outline" onClick={() => setIsNewCandidateOpen(false)}>Cancel</Button>
                        <Button onClick={handleCreateCandidate} disabled={isCreatingCandidate}>
                          {isCreatingCandidate ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
                          Add Candidate
                        </Button>
                      </DialogFooter>
                    </DialogContent>
                  </Dialog>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              {filteredCandidates.length === 0 ? (
                <div className="text-center py-12 text-muted-foreground">
                  <Users className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>No candidates found</p>
                  <Button className="mt-4" onClick={() => setIsNewCandidateOpen(true)}>
                    <UserPlus className="h-4 w-4 mr-2" />
                    Add First Candidate
                  </Button>
                </div>
              ) : (
                <div className="border rounded-lg overflow-hidden">
                  <table className="w-full">
                    <thead className="bg-muted/50">
                      <tr>
                        <th className="text-left p-4 font-medium">Candidate</th>
                        <th className="text-left p-4 font-medium">Current Role</th>
                        <th className="text-left p-4 font-medium">Experience</th>
                        <th className="text-center p-4 font-medium">Status</th>
                        <th className="text-center p-4 font-medium">Rating</th>
                        <th className="text-right p-4 font-medium">Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {filteredCandidates.map((candidate) => (
                        <tr key={candidate.id} className="border-t hover:bg-muted/30">
                          <td className="p-4">
                            <div>
                              <p className="font-medium">{candidate.full_name}</p>
                              <div className="flex items-center gap-2 text-xs text-muted-foreground">
                                <Mail className="h-3 w-3" /> {candidate.email}
                              </div>
                              {candidate.phone && (
                                <div className="flex items-center gap-2 text-xs text-muted-foreground">
                                  <Phone className="h-3 w-3" /> {candidate.phone}
                                </div>
                              )}
                            </div>
                          </td>
                          <td className="p-4">
                            <p className="text-sm">{candidate.current_designation || '-'}</p>
                            <p className="text-xs text-muted-foreground">{candidate.current_company || '-'}</p>
                          </td>
                          <td className="p-4 text-muted-foreground">
                            {candidate.total_experience_years ? `${candidate.total_experience_years} years` : '-'}
                          </td>
                          <td className="p-4 text-center">
                            <Badge className={candidateStatusColors[candidate.status] || 'bg-gray-100'}>
                              {candidate.status}
                            </Badge>
                            {candidate.employee_id && (
                              <Badge className="ml-2 bg-green-100 text-green-800">Hired</Badge>
                            )}
                          </td>
                          <td className="p-4 text-center">
                            {candidate.rating ? (
                              <>
                                <span className="font-medium">{candidate.rating}</span>
                                <span className="text-yellow-500 ml-1">★</span>
                              </>
                            ) : '-'}
                          </td>
                          <td className="p-4 text-right">
                            <div className="flex justify-end gap-2">
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => {
                                  setApplyForm({ ...applyForm, candidate_id: candidate.id })
                                  setIsApplyOpen(true)
                                }}
                                disabled={!!candidate.employee_id}
                              >
                                Apply to Job
                              </Button>
                              {candidate.status === 'withdrawn' && !candidate.employee_id && (
                                <Button
                                  variant="outline"
                                  size="sm"
                                  className="text-red-600 hover:text-red-700 hover:bg-red-50"
                                  onClick={() => handleDeleteCandidateClick(candidate)}
                                >
                                  <Trash2 className="h-4 w-4" />
                                </Button>
                              )}
                            </div>
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

        <TabsContent value="pipeline" className="mt-4">
          <Card className="mb-4">
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle>Recruitment Pipeline</CardTitle>
                <Dialog open={isHireOpen} onOpenChange={setIsHireOpen}>
                  <DialogTrigger asChild>
                    <Button>
                      <UserPlus className="h-4 w-4 mr-2" />
                      Hire Candidate
                    </Button>
                  </DialogTrigger>
                  <DialogContent>
                    <DialogHeader>
                      <DialogTitle>Hire Candidate</DialogTitle>
                      <DialogDescription>
                        Create employee record and start onboarding
                      </DialogDescription>
                    </DialogHeader>
                    <div className="grid gap-4 py-4">
                      <div className="grid gap-2">
                        <Label>Select Application *</Label>
                        <Select
                          value={hireForm.application_id}
                          onValueChange={(v) => setHireForm({ ...hireForm, application_id: v })}
                        >
                          <SelectTrigger>
                            <SelectValue placeholder="Select an application" />
                          </SelectTrigger>
                          <SelectContent>
                            {applications
                              .filter(a => ['offer_accepted', 'offer_extended', 'final_round'].includes(a.stage))
                              .map(app => (
                                <SelectItem key={app.id} value={app.id}>
                                  {app.candidate_name} - {app.job_title} ({stageLabels[app.stage]})
                                </SelectItem>
                              ))}
                          </SelectContent>
                        </Select>
                      </div>
                      <div className="grid gap-2">
                        <Label>Date of Joining *</Label>
                        <Input
                          type="date"
                          value={hireForm.date_of_joining}
                          onChange={(e) => setHireForm({ ...hireForm, date_of_joining: e.target.value })}
                        />
                      </div>
                      <div className="grid gap-2">
                        <Label>Employment Type</Label>
                        <Select
                          value={hireForm.employment_type}
                          onValueChange={(v) => setHireForm({ ...hireForm, employment_type: v })}
                        >
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            {Object.entries(jobTypes).map(([value, label]) => (
                              <SelectItem key={value} value={value}>{label}</SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                      </div>
                      <div className="flex items-center gap-2">
                        <input
                          type="checkbox"
                          checked={hireForm.create_onboarding}
                          onChange={(e) => setHireForm({ ...hireForm, create_onboarding: e.target.checked })}
                          className="h-4 w-4"
                        />
                        <Label>Create onboarding session</Label>
                      </div>
                    </div>
                    <DialogFooter>
                      <Button variant="outline" onClick={() => setIsHireOpen(false)}>Cancel</Button>
                      <Button onClick={handleHire} disabled={isHiring}>
                        {isHiring ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
                        Hire & Create Employee
                      </Button>
                    </DialogFooter>
                  </DialogContent>
                </Dialog>
              </div>
            </CardHeader>
          </Card>

          <div className="grid grid-cols-5 gap-4">
            {['applied', 'screening', 'technical_round', 'offer_extended', 'hired'].map((stage) => (
              <Card key={stage} className="min-h-[400px]">
                <CardHeader className="pb-2">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-sm">{stageLabels[stage] || stage}</CardTitle>
                    <Badge variant="secondary">
                      {applications.filter(a => a.stage === stage).length}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent className="space-y-2">
                  {applications.filter(a => a.stage === stage).map((app) => (
                    <Card key={app.id} className="cursor-pointer hover:shadow-md">
                      <CardContent className="p-3">
                        <p className="font-medium text-sm">{app.candidate_name}</p>
                        <p className="text-xs text-muted-foreground">{app.job_title}</p>
                        <div className="flex items-center justify-between mt-2">
                          {app.overall_rating ? (
                            <span className="text-xs">
                              {app.overall_rating}★
                            </span>
                          ) : <span />}
                          <Select
                            value={app.stage}
                            onValueChange={(newStage) => handleMoveStage(app.id, newStage)}
                          >
                            <SelectTrigger className="h-6 text-xs w-auto">
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              <SelectItem value="applied">Applied</SelectItem>
                              <SelectItem value="screening">Screening</SelectItem>
                              <SelectItem value="technical_round">Technical</SelectItem>
                              <SelectItem value="hr_round">HR Round</SelectItem>
                              <SelectItem value="offer_extended">Offer</SelectItem>
                              <SelectItem value="offer_accepted">Accepted</SelectItem>
                              <SelectItem value="hired">Hired</SelectItem>
                              <SelectItem value="rejected">Rejected</SelectItem>
                            </SelectContent>
                          </Select>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>
      </Tabs>

      {/* Apply to Job Dialog */}
      <Dialog open={isApplyOpen} onOpenChange={setIsApplyOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Apply to Job</DialogTitle>
            <DialogDescription>Create an application for a job opening</DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div className="grid gap-2">
              <Label>Select Job *</Label>
              <Select
                value={applyForm.job_id}
                onValueChange={(v) => setApplyForm({ ...applyForm, job_id: v })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select a job opening" />
                </SelectTrigger>
                <SelectContent>
                  {jobs.filter(j => j.status === 'open').map(job => (
                    <SelectItem key={job.id} value={job.id}>
                      {job.title} ({job.job_code})
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="grid gap-2">
              <Label>Select Candidate *</Label>
              <Select
                value={applyForm.candidate_id}
                onValueChange={(v) => setApplyForm({ ...applyForm, candidate_id: v })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select a candidate" />
                </SelectTrigger>
                <SelectContent>
                  {candidates.filter(c => !c.employee_id).map(cand => (
                    <SelectItem key={cand.id} value={cand.id}>
                      {cand.full_name} ({cand.email})
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="grid gap-2">
              <Label>Expected Salary</Label>
              <Input
                type="number"
                value={applyForm.expected_salary}
                onChange={(e) => setApplyForm({ ...applyForm, expected_salary: e.target.value })}
                placeholder="Annual salary expectation"
              />
            </div>
            <div className="grid gap-2">
              <Label>Cover Letter</Label>
              <Textarea
                value={applyForm.cover_letter}
                onChange={(e) => setApplyForm({ ...applyForm, cover_letter: e.target.value })}
                rows={3}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsApplyOpen(false)}>Cancel</Button>
            <Button onClick={handleApplyToJob} disabled={isCreatingApplication}>
              {isCreatingApplication ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
              Create Application
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete Job Confirmation Dialog */}
      <AlertDialog open={deleteJobDialogOpen} onOpenChange={setDeleteJobDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-red-500" />
              Delete Job Opening
            </AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete the job opening <strong>{jobToDelete?.title}</strong> ({jobToDelete?.job_code})?
              This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={isDeletingJob}>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDeleteJobConfirm}
              disabled={isDeletingJob}
              className="bg-red-600 hover:bg-red-700 focus:ring-red-600"
            >
              {isDeletingJob ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Deleting...
                </>
              ) : (
                'Delete'
              )}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      {/* Delete Candidate Confirmation Dialog */}
      <AlertDialog open={deleteCandidateDialogOpen} onOpenChange={setDeleteCandidateDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-red-500" />
              Delete Candidate
            </AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete <strong>{candidateToDelete?.full_name}</strong>?
              This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={isDeletingCandidate}>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDeleteCandidateConfirm}
              disabled={isDeletingCandidate}
              className="bg-red-600 hover:bg-red-700 focus:ring-red-600"
            >
              {isDeletingCandidate ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Deleting...
                </>
              ) : (
                'Delete'
              )}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  )
}
