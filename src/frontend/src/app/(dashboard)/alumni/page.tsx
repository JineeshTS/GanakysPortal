'use client'

import { useState, useEffect, useCallback } from 'react'
import { PageHeader } from '@/components/layout/page-header'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Skeleton } from '@/components/ui/skeleton'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { useApi, useToast } from '@/hooks'
import {
  GraduationCap,
  FileText,
  Receipt,
  Download,
  Calendar,
  Briefcase,
  Building2,
  Clock,
  RefreshCw,
  IndianRupee,
  CheckCircle,
  AlertCircle,
  User,
  Mail,
  Phone,
  Award,
  ScrollText
} from 'lucide-react'

// Types
interface AlumniEmploymentSummary {
  employee_code: string
  full_name: string
  email?: string
  phone?: string
  department_name?: string
  designation_name?: string
  date_of_joining?: string
  date_of_exit?: string
  total_years_of_service?: number
  employment_status: string
}

interface AlumniExitInfo {
  exit_type: string
  resignation_date?: string
  last_working_day?: string
  reason_category?: string
  status: string
  rehire_eligible: boolean
  fnf_net_payable?: string
  fnf_status?: string
  fnf_payment_date?: string
}

interface AlumniDashboard {
  success: boolean
  employment_summary: AlumniEmploymentSummary
  payslips_count: number
  documents_count: number
  exit_info?: AlumniExitInfo
}

interface AlumniPayslip {
  id: string
  month: number
  year: number
  gross_salary: string
  net_salary: string
  status: string
  generated_at?: string
}

interface AlumniDocument {
  id: string
  document_name: string
  document_type: string
  category: string
  file_url?: string
  uploaded_at: string
}

interface PayslipsResponse {
  success: boolean
  data: AlumniPayslip[]
  meta: { page: number; limit: number; total: number }
}

interface DocumentsResponse {
  success: boolean
  data: AlumniDocument[]
  meta: { page: number; limit: number; total: number }
}

interface DocumentCategory {
  code: string
  name: string
}

interface CategoriesResponse {
  success: boolean
  data: DocumentCategory[]
}

interface YearsResponse {
  success: boolean
  data: number[]
}

const monthNames = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December'
]

const exitTypeLabels: Record<string, string> = {
  resignation: 'Resignation',
  termination: 'Termination',
  retirement: 'Retirement',
  end_of_contract: 'End of Contract',
  mutual_separation: 'Mutual Separation',
  absconding: 'Absconding',
  death: 'Death',
}

const statusColors: Record<string, string> = {
  completed: 'bg-green-100 text-green-800',
  fnf_processed: 'bg-green-100 text-green-800',
  paid: 'bg-green-100 text-green-800',
  approved: 'bg-blue-100 text-blue-800',
  pending: 'bg-yellow-100 text-yellow-800',
  draft: 'bg-gray-100 text-gray-800',
}

export default function AlumniPage() {
  const [activeTab, setActiveTab] = useState('overview')
  const [selectedYear, setSelectedYear] = useState<string>('all')
  const [selectedCategory, setSelectedCategory] = useState<string>('all')
  const { showToast } = useToast()

  // API hooks
  const { data: dashboardData, isLoading: isLoadingDashboard, get: getDashboard } = useApi<AlumniDashboard>()
  const { data: payslipsData, isLoading: isLoadingPayslips, get: getPayslips } = useApi<PayslipsResponse>()
  const { data: documentsData, isLoading: isLoadingDocs, get: getDocuments } = useApi<DocumentsResponse>()
  const { data: categoriesData, get: getCategories } = useApi<CategoriesResponse>()
  const { data: yearsData, get: getYears } = useApi<YearsResponse>()

  // Fetch data
  const fetchData = useCallback(() => {
    getDashboard('/alumni/dashboard')
    getCategories('/alumni/documents/categories')
    getYears('/alumni/years')
  }, [getDashboard, getCategories, getYears])

  useEffect(() => {
    fetchData()
  }, [fetchData])

  // Fetch payslips when year changes
  useEffect(() => {
    const url = selectedYear === 'all'
      ? '/alumni/payslips?page=1&limit=50'
      : `/alumni/payslips?page=1&limit=50&year=${selectedYear}`
    getPayslips(url)
  }, [selectedYear, getPayslips])

  // Fetch documents when category changes
  useEffect(() => {
    const url = selectedCategory === 'all'
      ? '/alumni/documents?page=1&limit=50'
      : `/alumni/documents?page=1&limit=50&category=${selectedCategory}`
    getDocuments(url)
  }, [selectedCategory, getDocuments])

  const dashboard = dashboardData
  const payslips = payslipsData?.data || []
  const documents = documentsData?.data || []
  const categories = categoriesData?.data || []
  const years = yearsData?.data || []

  const handleDownload = (fileUrl?: string, documentName?: string) => {
    if (!fileUrl) {
      showToast('error', 'Document file not available')
      return
    }
    // Open file URL in new tab
    window.open(fileUrl, '_blank')
    showToast('success', `Downloading ${documentName || 'document'}`)
  }

  const formatCurrency = (amount?: string | number) => {
    if (!amount) return '0'
    const num = typeof amount === 'string' ? parseFloat(amount) : amount
    return new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 0 }).format(num)
  }

  // Loading state
  if (isLoadingDashboard) {
    return (
      <div className="space-y-6">
        <PageHeader
          title="Alumni Portal"
          description="Access your employment history, documents, and payslips"
          icon={<GraduationCap className="h-6 w-6" />}
        />
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {[1, 2, 3].map((i) => (
            <Card key={i}>
              <CardContent className="pt-6">
                <Skeleton className="h-24 w-full" />
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

  if (!dashboard) {
    return (
      <div className="space-y-6">
        <PageHeader
          title="Alumni Portal"
          description="Access your employment history, documents, and payslips"
          icon={<GraduationCap className="h-6 w-6" />}
        />
        <Card>
          <CardContent className="pt-6 text-center py-12">
            <AlertCircle className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
            <p className="text-muted-foreground">Unable to load your employment information</p>
            <Button className="mt-4" onClick={fetchData}>
              <RefreshCw className="h-4 w-4 mr-2" />
              Retry
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  const { employment_summary, payslips_count, documents_count, exit_info } = dashboard
  const isExEmployee = ['resigned', 'terminated', 'retired'].includes(employment_summary.employment_status)

  return (
    <div className="space-y-6">
      <PageHeader
        title="Alumni Portal"
        description="Access your employment history, documents, and payslips"
        icon={<GraduationCap className="h-6 w-6" />}
        actions={
          <Button variant="outline" onClick={fetchData}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
        }
      />

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="payslips">Payslips ({payslips_count})</TabsTrigger>
          <TabsTrigger value="documents">Documents ({documents_count})</TabsTrigger>
          {exit_info && <TabsTrigger value="exit">Exit Details</TabsTrigger>}
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="mt-4 space-y-6">
          {/* Employment Summary Card */}
          <Card>
            <CardHeader>
              <CardTitle>Employment Summary</CardTitle>
              <CardDescription>Your employment history with the organization</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <div className="space-y-4">
                  <div className="flex items-center gap-3">
                    <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center">
                      <span className="text-2xl font-bold text-primary">
                        {employment_summary.full_name.split(' ').map(n => n[0]).join('').slice(0, 2)}
                      </span>
                    </div>
                    <div>
                      <p className="font-semibold text-lg">{employment_summary.full_name}</p>
                      <p className="text-sm text-muted-foreground">{employment_summary.employee_code}</p>
                      <Badge className={
                        isExEmployee ? 'bg-gray-100 text-gray-800' : 'bg-green-100 text-green-800'
                      }>
                        {employment_summary.employment_status.charAt(0).toUpperCase() +
                          employment_summary.employment_status.slice(1)}
                      </Badge>
                    </div>
                  </div>
                </div>
                <div className="space-y-3">
                  <div className="flex items-center gap-2 text-sm">
                    <Building2 className="h-4 w-4 text-muted-foreground" />
                    <span className="text-muted-foreground">Department:</span>
                    <span className="font-medium">{employment_summary.department_name || '-'}</span>
                  </div>
                  <div className="flex items-center gap-2 text-sm">
                    <Briefcase className="h-4 w-4 text-muted-foreground" />
                    <span className="text-muted-foreground">Designation:</span>
                    <span className="font-medium">{employment_summary.designation_name || '-'}</span>
                  </div>
                  {employment_summary.email && (
                    <div className="flex items-center gap-2 text-sm">
                      <Mail className="h-4 w-4 text-muted-foreground" />
                      <span>{employment_summary.email}</span>
                    </div>
                  )}
                </div>
                <div className="space-y-3">
                  <div className="flex items-center gap-2 text-sm">
                    <Calendar className="h-4 w-4 text-muted-foreground" />
                    <span className="text-muted-foreground">Joined:</span>
                    <span className="font-medium">
                      {employment_summary.date_of_joining
                        ? new Date(employment_summary.date_of_joining).toLocaleDateString('en-IN')
                        : '-'}
                    </span>
                  </div>
                  {employment_summary.date_of_exit && (
                    <div className="flex items-center gap-2 text-sm">
                      <Calendar className="h-4 w-4 text-muted-foreground" />
                      <span className="text-muted-foreground">Last day:</span>
                      <span className="font-medium">
                        {new Date(employment_summary.date_of_exit).toLocaleDateString('en-IN')}
                      </span>
                    </div>
                  )}
                  <div className="flex items-center gap-2 text-sm">
                    <Clock className="h-4 w-4 text-muted-foreground" />
                    <span className="text-muted-foreground">Tenure:</span>
                    <span className="font-medium">
                      {employment_summary.total_years_of_service
                        ? `${employment_summary.total_years_of_service} years`
                        : '-'}
                    </span>
                  </div>
                </div>
                <div className="space-y-3">
                  <div className="flex items-center gap-2 text-sm">
                    <Receipt className="h-4 w-4 text-muted-foreground" />
                    <span className="text-muted-foreground">Payslips:</span>
                    <span className="font-medium">{payslips_count}</span>
                  </div>
                  <div className="flex items-center gap-2 text-sm">
                    <FileText className="h-4 w-4 text-muted-foreground" />
                    <span className="text-muted-foreground">Documents:</span>
                    <span className="font-medium">{documents_count}</span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Quick Stats */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card className="cursor-pointer hover:shadow-md transition-shadow" onClick={() => setActiveTab('payslips')}>
              <CardContent className="pt-6">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-blue-100 rounded-lg">
                    <Receipt className="h-5 w-5 text-blue-600" />
                  </div>
                  <div>
                    <p className="text-2xl font-bold">{payslips_count}</p>
                    <p className="text-sm text-muted-foreground">Payslips Available</p>
                  </div>
                </div>
              </CardContent>
            </Card>
            <Card className="cursor-pointer hover:shadow-md transition-shadow" onClick={() => setActiveTab('documents')}>
              <CardContent className="pt-6">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-green-100 rounded-lg">
                    <FileText className="h-5 w-5 text-green-600" />
                  </div>
                  <div>
                    <p className="text-2xl font-bold">{documents_count}</p>
                    <p className="text-sm text-muted-foreground">Documents Available</p>
                  </div>
                </div>
              </CardContent>
            </Card>
            {exit_info && (
              <Card className="cursor-pointer hover:shadow-md transition-shadow" onClick={() => setActiveTab('exit')}>
                <CardContent className="pt-6">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-purple-100 rounded-lg">
                      <Award className="h-5 w-5 text-purple-600" />
                    </div>
                    <div>
                      <p className="text-lg font-bold">
                        {exit_info.rehire_eligible ? 'Eligible for Rehire' : 'Exit Completed'}
                      </p>
                      <p className="text-sm text-muted-foreground">
                        {exitTypeLabels[exit_info.exit_type] || exit_info.exit_type}
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </TabsContent>

        {/* Payslips Tab */}
        <TabsContent value="payslips" className="mt-4">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Payslips</CardTitle>
                  <CardDescription>Download your historical payslips</CardDescription>
                </div>
                <Select value={selectedYear} onValueChange={setSelectedYear}>
                  <SelectTrigger className="w-40">
                    <SelectValue placeholder="Filter by year" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Years</SelectItem>
                    {years.map((year) => (
                      <SelectItem key={year} value={year.toString()}>{year}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </CardHeader>
            <CardContent>
              {isLoadingPayslips ? (
                <Skeleton className="h-64 w-full" />
              ) : payslips.length === 0 ? (
                <div className="text-center py-12 text-muted-foreground">
                  <Receipt className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>No payslips found</p>
                </div>
              ) : (
                <div className="border rounded-lg overflow-hidden">
                  <table className="w-full">
                    <thead className="bg-muted/50">
                      <tr>
                        <th className="text-left p-4 font-medium">Month/Year</th>
                        <th className="text-right p-4 font-medium">Gross Salary</th>
                        <th className="text-right p-4 font-medium">Net Salary</th>
                        <th className="text-center p-4 font-medium">Status</th>
                        <th className="text-right p-4 font-medium">Action</th>
                      </tr>
                    </thead>
                    <tbody>
                      {payslips.map((payslip) => (
                        <tr key={payslip.id} className="border-t hover:bg-muted/30">
                          <td className="p-4 font-medium">
                            {monthNames[payslip.month - 1]} {payslip.year}
                          </td>
                          <td className="p-4 text-right">{formatCurrency(payslip.gross_salary)}</td>
                          <td className="p-4 text-right font-medium">{formatCurrency(payslip.net_salary)}</td>
                          <td className="p-4 text-center">
                            <Badge className={statusColors[payslip.status] || 'bg-gray-100'}>
                              {payslip.status}
                            </Badge>
                          </td>
                          <td className="p-4 text-right">
                            <Button variant="outline" size="sm">
                              <Download className="h-3 w-3 mr-1" />
                              Download
                            </Button>
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

        {/* Documents Tab */}
        <TabsContent value="documents" className="mt-4">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Documents</CardTitle>
                  <CardDescription>Access your letters, tax documents, and certificates</CardDescription>
                </div>
                <Select value={selectedCategory} onValueChange={setSelectedCategory}>
                  <SelectTrigger className="w-48">
                    <SelectValue placeholder="Filter by category" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Categories</SelectItem>
                    {categories.map((cat) => (
                      <SelectItem key={cat.code} value={cat.code}>{cat.name}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </CardHeader>
            <CardContent>
              {isLoadingDocs ? (
                <Skeleton className="h-64 w-full" />
              ) : documents.length === 0 ? (
                <div className="text-center py-12 text-muted-foreground">
                  <FileText className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>No documents found</p>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {documents.map((doc) => (
                    <Card key={doc.id} className="hover:shadow-md transition-shadow">
                      <CardContent className="p-4">
                        <div className="flex items-start gap-3">
                          <div className="p-2 bg-muted rounded-lg">
                            <ScrollText className="h-5 w-5 text-muted-foreground" />
                          </div>
                          <div className="flex-1 min-w-0">
                            <p className="font-medium truncate">{doc.document_name}</p>
                            <p className="text-xs text-muted-foreground mt-1">
                              {categories.find(c => c.code === doc.category)?.name || doc.category}
                            </p>
                            <p className="text-xs text-muted-foreground">
                              {new Date(doc.uploaded_at).toLocaleDateString('en-IN')}
                            </p>
                          </div>
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => handleDownload(doc.file_url, doc.document_name)}
                          >
                            <Download className="h-4 w-4" />
                          </Button>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Exit Details Tab */}
        {exit_info && (
          <TabsContent value="exit" className="mt-4">
            <Card>
              <CardHeader>
                <CardTitle>Exit Details</CardTitle>
                <CardDescription>Information about your separation from the organization</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <h3 className="font-semibold">Separation Information</h3>
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <p className="text-muted-foreground">Exit Type</p>
                        <p className="font-medium">{exitTypeLabels[exit_info.exit_type] || exit_info.exit_type}</p>
                      </div>
                      <div>
                        <p className="text-muted-foreground">Status</p>
                        <Badge className={statusColors[exit_info.status] || 'bg-gray-100'}>
                          {exit_info.status.replace('_', ' ')}
                        </Badge>
                      </div>
                      {exit_info.resignation_date && (
                        <div>
                          <p className="text-muted-foreground">Resignation Date</p>
                          <p className="font-medium">{new Date(exit_info.resignation_date).toLocaleDateString('en-IN')}</p>
                        </div>
                      )}
                      {exit_info.last_working_day && (
                        <div>
                          <p className="text-muted-foreground">Last Working Day</p>
                          <p className="font-medium">{new Date(exit_info.last_working_day).toLocaleDateString('en-IN')}</p>
                        </div>
                      )}
                      {exit_info.reason_category && (
                        <div className="col-span-2">
                          <p className="text-muted-foreground">Reason</p>
                          <p className="font-medium">{exit_info.reason_category}</p>
                        </div>
                      )}
                      <div>
                        <p className="text-muted-foreground">Rehire Eligibility</p>
                        <div className="flex items-center gap-2">
                          {exit_info.rehire_eligible ? (
                            <>
                              <CheckCircle className="h-4 w-4 text-green-600" />
                              <span className="text-green-600 font-medium">Eligible</span>
                            </>
                          ) : (
                            <>
                              <AlertCircle className="h-4 w-4 text-red-600" />
                              <span className="text-red-600 font-medium">Not Eligible</span>
                            </>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                  <div className="space-y-4">
                    <h3 className="font-semibold">Full & Final Settlement</h3>
                    {exit_info.fnf_net_payable ? (
                      <div className="space-y-4">
                        <div className="p-4 bg-muted/50 rounded-lg">
                          <p className="text-sm text-muted-foreground">Net Payable Amount</p>
                          <p className="text-2xl font-bold text-primary">{formatCurrency(exit_info.fnf_net_payable)}</p>
                        </div>
                        <div className="grid grid-cols-2 gap-4 text-sm">
                          <div>
                            <p className="text-muted-foreground">F&F Status</p>
                            <Badge className={statusColors[exit_info.fnf_status || ''] || 'bg-gray-100'}>
                              {exit_info.fnf_status || 'Pending'}
                            </Badge>
                          </div>
                          {exit_info.fnf_payment_date && (
                            <div>
                              <p className="text-muted-foreground">Payment Date</p>
                              <p className="font-medium">{new Date(exit_info.fnf_payment_date).toLocaleDateString('en-IN')}</p>
                            </div>
                          )}
                        </div>
                      </div>
                    ) : (
                      <div className="p-4 bg-muted/30 rounded-lg text-center text-muted-foreground">
                        <IndianRupee className="h-8 w-8 mx-auto mb-2 opacity-50" />
                        <p>F&F settlement details not available</p>
                      </div>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        )}
      </Tabs>
    </div>
  )
}
