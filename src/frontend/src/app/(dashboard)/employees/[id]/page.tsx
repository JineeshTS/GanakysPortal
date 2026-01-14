'use client'

import * as React from 'react'
import Link from 'next/link'
import { useParams, useRouter } from 'next/navigation'
import { PageHeader } from '@/components/layout/page-header'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { formatCurrency, formatDate, formatPhone } from '@/lib/format'
import { formatAadhaar } from '@/lib/validators'
import { useApi } from '@/hooks'
import {
  Edit,
  Mail,
  Phone,
  MapPin,
  Calendar,
  Building2,
  Briefcase,
  CreditCard,
  FileText,
  Users,
  User,
  Heart,
  Droplet,
  AlertCircle,
  Download,
  Eye,
  CheckCircle,
  Clock,
  Package,
  Laptop,
  ArrowLeft,
  Printer,
  Loader2
} from 'lucide-react'
import type { Employee, EmploymentStatus, EmploymentType, EmployeeDocument, LeaveBalance } from '@/types'

// API response type
interface EmployeeApiResponse {
  id: string
  employee_code: string
  first_name: string
  middle_name: string | null
  last_name: string
  full_name: string
  date_of_birth: string | null
  gender: string | null
  date_of_joining: string
  department_name: string | null
  designation_name: string | null
  employment_status: string
  employment_type: string
  profile_photo_url: string | null
}

// Extended employee type for display
type DisplayEmployee = Employee & {
  department_name?: string
  designation_name?: string
  reporting_manager_name?: string
  work_location?: string
  probation_period_months?: number
  salary_structure?: {
    basic: number
    hra: number
    special_allowance: number
    pf_employee: number
    pf_employer: number
    professional_tax: number
    gross: number
    net: number
  }
  leaves?: LeaveBalance[]
  assets?: Array<{
    id: string
    name: string
    type: string
    serial_number: string
    assigned_date: string
    status: string
  }>
}

// Fallback mock data for fields not yet in API
const mockEmployeeDefaults = {
  id: '1',
  employee_code: 'EMP001',
  first_name: 'Rajesh',
  middle_name: 'Kumar',
  last_name: 'Sharma',
  full_name: 'Rajesh Kumar Sharma',
  date_of_birth: '1990-05-15',
  gender: 'male',
  blood_group: 'O+',
  marital_status: 'married',
  father_name: 'Suresh Kumar Sharma',
  personal_email: 'rajesh.personal@gmail.com',
  work_email: 'rajesh.kumar@company.com',
  mobile: '9876543210',
  emergency_contact: {
    name: 'Priya Sharma',
    relationship: 'Wife',
    phone: '9876543211'
  },
  current_address: {
    line1: '123 MG Road',
    line2: 'Near Central Mall',
    city: 'Bangalore',
    state: 'Karnataka',
    pincode: '560001',
    country: 'India'
  },
  permanent_address: {
    line1: '456 Gandhi Nagar',
    city: 'Jaipur',
    state: 'Rajasthan',
    pincode: '302015',
    country: 'India'
  },
  department_id: '1',
  designation_id: '2',
  department_name: 'Engineering',
  designation_name: 'Senior Software Engineer',
  reporting_to: '10',
  reporting_manager_name: 'Amit Patel',
  date_of_joining: '2022-04-15',
  employment_type: 'full_time',
  employment_status: 'active',
  work_location: 'Bangalore HQ',
  probation_period_months: 6,
  probation_end_date: '2022-10-15',
  notice_period_days: 60,
  pan: 'ABCDE1234F',
  aadhaar: '234567891234',
  uan: '100123456789',
  pf_number: 'BGBNG/12345/123',
  esi_number: '',
  bank_details: {
    account_holder_name: 'Rajesh Kumar Sharma',
    account_number: '1234567890123456',
    bank_name: 'HDFC Bank',
    branch_name: 'MG Road Branch',
    ifsc_code: 'HDFC0001234'
  },
  ctc: 1800000,
  salary_structure: {
    basic: 75000,
    hra: 30000,
    special_allowance: 35000,
    pf_employee: 9000,
    pf_employer: 9000,
    professional_tax: 200,
    gross: 140000,
    net: 130800
  },
  photo_url: '',
  documents: [
    { id: '1', type: 'pan_card', name: 'PAN Card', url: '/docs/pan.pdf', uploaded_at: '2022-04-15T00:00:00Z', verified: true },
    { id: '2', type: 'aadhaar_card', name: 'Aadhaar Card', url: '/docs/aadhaar.pdf', uploaded_at: '2022-04-15T00:00:00Z', verified: true },
    { id: '3', type: 'offer_letter', name: 'Offer Letter', url: '/docs/offer.pdf', uploaded_at: '2022-04-15T00:00:00Z', verified: true },
    { id: '4', type: 'education_certificate', name: 'Degree Certificate', url: '/docs/degree.pdf', uploaded_at: '2022-04-15T00:00:00Z', verified: false },
    { id: '5', type: 'relieving_letter', name: 'Previous Employment Relieving Letter', url: '/docs/relieving.pdf', uploaded_at: '2022-04-15T00:00:00Z', verified: true }
  ],
  leaves: [
    { employee_id: '1', leave_type_code: 'CL', leave_type_name: 'Casual Leave', year: 2024, opening_balance: 12, credited: 0, used: 3, lapsed: 0, available: 9, pending_approval: 1 },
    { employee_id: '1', leave_type_code: 'SL', leave_type_name: 'Sick Leave', year: 2024, opening_balance: 12, credited: 0, used: 2, lapsed: 0, available: 10, pending_approval: 0 },
    { employee_id: '1', leave_type_code: 'EL', leave_type_name: 'Earned Leave', year: 2024, opening_balance: 5, credited: 15, used: 5, lapsed: 0, available: 15, pending_approval: 0 },
    { employee_id: '1', leave_type_code: 'CO', leave_type_name: 'Comp Off', year: 2024, opening_balance: 0, credited: 2, used: 1, lapsed: 0, available: 1, pending_approval: 0 }
  ],
  assets: [
    { id: '1', name: 'MacBook Pro 14"', type: 'Laptop', serial_number: 'C02X12345678', assigned_date: '2022-04-15', status: 'active' },
    { id: '2', name: 'Dell 27" Monitor', type: 'Monitor', serial_number: 'DEL98765432', assigned_date: '2022-04-15', status: 'active' },
    { id: '3', name: 'Logitech MX Master 3', type: 'Mouse', serial_number: 'LOG12345', assigned_date: '2022-04-15', status: 'active' },
    { id: '4', name: 'Apple Magic Keyboard', type: 'Keyboard', serial_number: 'APL54321', assigned_date: '2022-04-15', status: 'active' }
  ],
  created_at: '2022-04-15T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z'
}

// Leave history mock
const leaveHistory = [
  { id: '1', type: 'Casual Leave', from: '2024-01-15', to: '2024-01-16', days: 2, status: 'approved', reason: 'Personal work' },
  { id: '2', type: 'Sick Leave', from: '2024-02-10', to: '2024-02-11', days: 2, status: 'approved', reason: 'Fever' },
  { id: '3', type: 'Casual Leave', from: '2024-03-05', to: '2024-03-05', days: 1, status: 'approved', reason: 'Family function' },
  { id: '4', type: 'Earned Leave', from: '2024-04-01', to: '2024-04-05', days: 5, status: 'approved', reason: 'Vacation' },
  { id: '5', type: 'Casual Leave', from: '2024-12-25', to: '2024-12-25', days: 1, status: 'pending', reason: 'Christmas celebration' }
]

export default function EmployeeDetailPage() {
  const params = useParams()
  const router = useRouter()
  const [employee, setEmployee] = React.useState<DisplayEmployee | null>(null)
  const [isLoading, setIsLoading] = React.useState(true)
  const [activeTab, setActiveTab] = React.useState('personal')
  const api = useApi<EmployeeApiResponse>()

  // Fetch employee from API
  React.useEffect(() => {
    const fetchEmployee = async () => {
      if (!params.id) return
      setIsLoading(true)
      try {
        const result = await api.get(`/employees/${params.id}`)
        if (result) {
          // Merge API data with mock defaults for fields not yet in API
          const mergedEmployee: DisplayEmployee = {
            ...mockEmployeeDefaults,
            id: result.id,
            employee_code: result.employee_code,
            first_name: result.first_name,
            middle_name: result.middle_name || '',
            last_name: result.last_name,
            full_name: result.full_name,
            date_of_birth: result.date_of_birth || mockEmployeeDefaults.date_of_birth,
            gender: (result.gender?.toLowerCase() || 'male') as 'male' | 'female' | 'other',
            date_of_joining: result.date_of_joining,
            department_name: result.department_name || undefined,
            designation_name: result.designation_name || undefined,
            employment_status: result.employment_status as EmploymentStatus,
            employment_type: result.employment_type as EmploymentType,
            photo_url: result.profile_photo_url || ''
          }
          setEmployee(mergedEmployee)
        }
      } catch (error) {
        console.error('Failed to fetch employee:', error)
      } finally {
        setIsLoading(false)
      }
    }
    fetchEmployee()
  }, [params.id])

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  if (!employee) {
    return (
      <div className="text-center py-12">
        <h2 className="text-xl font-semibold">Employee not found</h2>
        <p className="text-muted-foreground mt-2">The employee you&apos;re looking for doesn&apos;t exist.</p>
      </div>
    )
  }

  const getStatusBadge = (status: EmploymentStatus) => {
    const statusConfig = {
      active: { label: 'Active', className: 'bg-green-100 text-green-800' },
      probation: { label: 'Probation', className: 'bg-blue-100 text-blue-800' },
      notice_period: { label: 'Notice Period', className: 'bg-yellow-100 text-yellow-800' },
      resigned: { label: 'Resigned', className: 'bg-gray-100 text-gray-800' },
      terminated: { label: 'Terminated', className: 'bg-red-100 text-red-800' },
      retired: { label: 'Retired', className: 'bg-purple-100 text-purple-800' },
      absconding: { label: 'Absconding', className: 'bg-red-100 text-red-800' }
    }

    const config = statusConfig[status] || statusConfig.active
    return <Badge className={config.className}>{config.label}</Badge>
  }

  const getTypeBadge = (type: EmploymentType) => {
    const typeConfig = {
      full_time: { label: 'Full Time', className: 'bg-blue-50 text-blue-700' },
      part_time: { label: 'Part Time', className: 'bg-purple-50 text-purple-700' },
      contract: { label: 'Contract', className: 'bg-orange-50 text-orange-700' },
      intern: { label: 'Intern', className: 'bg-teal-50 text-teal-700' },
      consultant: { label: 'Consultant', className: 'bg-pink-50 text-pink-700' }
    }

    const config = typeConfig[type] || typeConfig.full_time
    return <Badge variant="outline" className={config.className}>{config.label}</Badge>
  }

  const getDocumentTypeName = (type: string) => {
    const types: Record<string, string> = {
      pan_card: 'PAN Card',
      aadhaar_card: 'Aadhaar Card',
      passport: 'Passport',
      driving_license: 'Driving License',
      offer_letter: 'Offer Letter',
      appointment_letter: 'Appointment Letter',
      relieving_letter: 'Relieving Letter',
      payslip: 'Payslip',
      form16: 'Form 16',
      education_certificate: 'Education Certificate',
      other: 'Other'
    }
    return types[type] || type
  }

  const calculateExperience = (joiningDate: string) => {
    const start = new Date(joiningDate)
    const now = new Date()
    const years = Math.floor((now.getTime() - start.getTime()) / (365.25 * 24 * 60 * 60 * 1000))
    const months = Math.floor(((now.getTime() - start.getTime()) % (365.25 * 24 * 60 * 60 * 1000)) / (30.44 * 24 * 60 * 60 * 1000))

    if (years > 0) {
      return `${years} year${years > 1 ? 's' : ''} ${months} month${months > 1 ? 's' : ''}`
    }
    return `${months} month${months > 1 ? 's' : ''}`
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Employee Profile"
        breadcrumbs={[
          { label: 'Dashboard', href: '/' },
          { label: 'Employees', href: '/employees' },
          { label: employee.full_name }
        ]}
        actions={
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={() => window.print()}>
              <Printer className="h-4 w-4 mr-2" />
              Print
            </Button>
            <Button asChild>
              <Link href={`/employees/${params.id}/edit`}>
                <Edit className="h-4 w-4 mr-2" />
                Edit Employee
              </Link>
            </Button>
          </div>
        }
      />

      {/* Employee Header Card */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col md:flex-row items-start md:items-center gap-6">
            <div className="w-24 h-24 bg-primary/10 rounded-full flex items-center justify-center shrink-0">
              <span className="text-3xl font-semibold text-primary">
                {employee.first_name.charAt(0)}{employee.last_name.charAt(0)}
              </span>
            </div>
            <div className="flex-1">
              <div className="flex flex-col md:flex-row md:items-center gap-2 md:gap-4 mb-2">
                <h2 className="text-2xl font-bold">{employee.full_name}</h2>
                {getStatusBadge(employee.employment_status)}
                {getTypeBadge(employee.employment_type)}
              </div>
              <p className="text-muted-foreground mb-2">
                {employee.designation_name} - {employee.department_name}
              </p>
              <div className="flex flex-wrap gap-4 text-sm text-muted-foreground">
                <div className="flex items-center gap-1">
                  <CreditCard className="h-4 w-4" />
                  <span>{employee.employee_code}</span>
                </div>
                <div className="flex items-center gap-1">
                  <Mail className="h-4 w-4" />
                  <span>{employee.work_email}</span>
                </div>
                <div className="flex items-center gap-1">
                  <Phone className="h-4 w-4" />
                  <span>{formatPhone(employee.mobile)}</span>
                </div>
                <div className="flex items-center gap-1">
                  <Calendar className="h-4 w-4" />
                  <span>Joined {formatDate(employee.date_of_joining, { format: 'long' })}</span>
                </div>
                <div className="flex items-center gap-1">
                  <Clock className="h-4 w-4" />
                  <span>Experience: {calculateExperience(employee.date_of_joining)}</span>
                </div>
              </div>
            </div>
            <div className="text-right shrink-0">
              <p className="text-sm text-muted-foreground">Annual CTC</p>
              <p className="text-2xl font-bold text-primary">{formatCurrency(employee.ctc)}</p>
              <p className="text-sm text-muted-foreground">
                {formatCurrency((employee.salary_structure?.net || 0))}/month net
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid grid-cols-6 w-full max-w-3xl">
          <TabsTrigger value="personal">
            <User className="h-4 w-4 mr-2" />
            Personal
          </TabsTrigger>
          <TabsTrigger value="employment">
            <Briefcase className="h-4 w-4 mr-2" />
            Employment
          </TabsTrigger>
          <TabsTrigger value="documents">
            <FileText className="h-4 w-4 mr-2" />
            Documents
          </TabsTrigger>
          <TabsTrigger value="salary">
            <CreditCard className="h-4 w-4 mr-2" />
            Salary
          </TabsTrigger>
          <TabsTrigger value="leaves">
            <Calendar className="h-4 w-4 mr-2" />
            Leaves
          </TabsTrigger>
          <TabsTrigger value="assets">
            <Laptop className="h-4 w-4 mr-2" />
            Assets
          </TabsTrigger>
        </TabsList>

        {/* Personal Tab */}
        <TabsContent value="personal" className="space-y-6">
          <div className="grid gap-6 md:grid-cols-2">
            {/* Basic Information */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Basic Information</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-muted-foreground">Full Name</p>
                    <p className="font-medium">{employee.full_name}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Date of Birth</p>
                    <p className="font-medium">{formatDate(employee.date_of_birth, { format: 'long' })}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Gender</p>
                    <p className="font-medium capitalize">{employee.gender}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Blood Group</p>
                    <p className="font-medium flex items-center gap-1">
                      <Droplet className="h-4 w-4 text-red-500" />
                      {employee.blood_group || '-'}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Marital Status</p>
                    <p className="font-medium capitalize">{employee.marital_status}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Father's Name</p>
                    <p className="font-medium">{employee.father_name}</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Contact Information */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Contact Information</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-3">
                  <div className="flex items-center gap-3">
                    <Mail className="h-4 w-4 text-muted-foreground" />
                    <div>
                      <p className="text-sm text-muted-foreground">Work Email</p>
                      <p className="font-medium">{employee.work_email}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <Mail className="h-4 w-4 text-muted-foreground" />
                    <div>
                      <p className="text-sm text-muted-foreground">Personal Email</p>
                      <p className="font-medium">{employee.personal_email || '-'}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <Phone className="h-4 w-4 text-muted-foreground" />
                    <div>
                      <p className="text-sm text-muted-foreground">Mobile</p>
                      <p className="font-medium">{formatPhone(employee.mobile)}</p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Emergency Contact */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg flex items-center gap-2">
                  <AlertCircle className="h-5 w-5 text-red-500" />
                  Emergency Contact
                </CardTitle>
              </CardHeader>
              <CardContent>
                {employee.emergency_contact ? (
                  <div className="space-y-2">
                    <div>
                      <p className="text-sm text-muted-foreground">Name</p>
                      <p className="font-medium">{employee.emergency_contact.name}</p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Relationship</p>
                      <p className="font-medium">{employee.emergency_contact.relationship}</p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Phone</p>
                      <p className="font-medium">{formatPhone(employee.emergency_contact.phone)}</p>
                    </div>
                  </div>
                ) : (
                  <p className="text-muted-foreground">No emergency contact added</p>
                )}
              </CardContent>
            </Card>

            {/* Addresses */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Addresses</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <p className="text-sm text-muted-foreground flex items-center gap-1 mb-1">
                    <MapPin className="h-4 w-4" />
                    Current Address
                  </p>
                  <p className="font-medium">
                    {employee.current_address.line1}
                    {employee.current_address.line2 && <>, {employee.current_address.line2}</>}
                    <br />
                    {employee.current_address.city}, {employee.current_address.state} - {employee.current_address.pincode}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground flex items-center gap-1 mb-1">
                    <MapPin className="h-4 w-4" />
                    Permanent Address
                  </p>
                  <p className="font-medium">
                    {employee.permanent_address.line1}
                    {employee.permanent_address.line2 && <>, {employee.permanent_address.line2}</>}
                    <br />
                    {employee.permanent_address.city}, {employee.permanent_address.state} - {employee.permanent_address.pincode}
                  </p>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Employment Tab */}
        <TabsContent value="employment" className="space-y-6">
          <div className="grid gap-6 md:grid-cols-2">
            {/* Employment Details */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Employment Details</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-muted-foreground">Employee ID</p>
                    <p className="font-medium">{employee.employee_code}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Date of Joining</p>
                    <p className="font-medium">{formatDate(employee.date_of_joining, { format: 'long' })}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Department</p>
                    <p className="font-medium">{employee.department_name}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Designation</p>
                    <p className="font-medium">{employee.designation_name}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Employment Type</p>
                    <p>{getTypeBadge(employee.employment_type)}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Status</p>
                    <p>{getStatusBadge(employee.employment_status)}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Reporting Manager</p>
                    <p className="font-medium">{employee.reporting_manager_name || '-'}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Work Location</p>
                    <p className="font-medium">{employee.work_location || '-'}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Probation Period</p>
                    <p className="font-medium">{employee.probation_period_months} months</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Notice Period</p>
                    <p className="font-medium">{employee.notice_period_days} days</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Statutory Information */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Statutory Information</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-muted-foreground">PAN Number</p>
                    <p className="font-medium font-mono">{employee.pan}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Aadhaar Number</p>
                    <p className="font-medium font-mono">{employee.aadhaar ? formatAadhaar(employee.aadhaar) : '-'}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">UAN</p>
                    <p className="font-medium font-mono">{employee.uan || '-'}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">PF Number</p>
                    <p className="font-medium font-mono">{employee.pf_number || '-'}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">ESI Number</p>
                    <p className="font-medium font-mono">{employee.esi_number || 'Not Applicable'}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Documents Tab */}
        <TabsContent value="documents" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Documents</CardTitle>
              <CardDescription>All uploaded documents and verification status</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {employee.documents?.map((doc) => (
                  <div
                    key={doc.id}
                    className="flex items-center justify-between p-4 border rounded-lg"
                  >
                    <div className="flex items-center gap-4">
                      <div className="w-10 h-10 bg-muted rounded flex items-center justify-center">
                        <FileText className="h-5 w-5 text-muted-foreground" />
                      </div>
                      <div>
                        <p className="font-medium">{doc.name}</p>
                        <p className="text-sm text-muted-foreground">
                          {getDocumentTypeName(doc.type)} - Uploaded {formatDate(doc.uploaded_at, { format: 'long' })}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-4">
                      {doc.verified ? (
                        <Badge className="bg-green-100 text-green-800">
                          <CheckCircle className="h-3 w-3 mr-1" />
                          Verified
                        </Badge>
                      ) : (
                        <Badge className="bg-yellow-100 text-yellow-800">
                          <Clock className="h-3 w-3 mr-1" />
                          Pending
                        </Badge>
                      )}
                      <div className="flex gap-1">
                        <Button variant="ghost" size="icon">
                          <Eye className="h-4 w-4" />
                        </Button>
                        <Button variant="ghost" size="icon">
                          <Download className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Salary Tab */}
        <TabsContent value="salary" className="space-y-6">
          <div className="grid gap-6 md:grid-cols-2">
            {/* CTC Overview */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Compensation Overview</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex justify-between items-center pb-4 border-b">
                    <span className="text-muted-foreground">Annual CTC</span>
                    <span className="text-2xl font-bold text-primary">{formatCurrency(employee.ctc)}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-muted-foreground">Monthly Gross</span>
                    <span className="font-semibold">{formatCurrency(employee.salary_structure?.gross || 0)}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-muted-foreground">Monthly Net</span>
                    <span className="font-semibold text-green-600">{formatCurrency(employee.salary_structure?.net || 0)}</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Bank Details */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Bank Details</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div>
                    <p className="text-sm text-muted-foreground">Account Holder</p>
                    <p className="font-medium">{employee.bank_details.account_holder_name}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Account Number</p>
                    <p className="font-medium font-mono">{employee.bank_details.account_number}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Bank Name</p>
                    <p className="font-medium">{employee.bank_details.bank_name}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Branch</p>
                    <p className="font-medium">{employee.bank_details.branch_name}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">IFSC Code</p>
                    <p className="font-medium font-mono">{employee.bank_details.ifsc_code}</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Salary Breakdown */}
            <Card className="md:col-span-2">
              <CardHeader>
                <CardTitle className="text-lg">Monthly Salary Structure</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid md:grid-cols-2 gap-8">
                  {/* Earnings */}
                  <div>
                    <h4 className="font-medium mb-4 text-green-600">Earnings</h4>
                    <div className="space-y-3">
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Basic Salary</span>
                        <span className="font-medium">{formatCurrency(employee.salary_structure?.basic || 0)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">HRA</span>
                        <span className="font-medium">{formatCurrency(employee.salary_structure?.hra || 0)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Special Allowance</span>
                        <span className="font-medium">{formatCurrency(employee.salary_structure?.special_allowance || 0)}</span>
                      </div>
                      <div className="flex justify-between pt-3 border-t font-semibold">
                        <span>Total Earnings</span>
                        <span className="text-green-600">{formatCurrency(employee.salary_structure?.gross || 0)}</span>
                      </div>
                    </div>
                  </div>

                  {/* Deductions */}
                  <div>
                    <h4 className="font-medium mb-4 text-red-600">Deductions</h4>
                    <div className="space-y-3">
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">PF (Employee)</span>
                        <span className="font-medium">{formatCurrency(employee.salary_structure?.pf_employee || 0)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-muted-foreground">Professional Tax</span>
                        <span className="font-medium">{formatCurrency(employee.salary_structure?.professional_tax || 0)}</span>
                      </div>
                      <div className="flex justify-between pt-3 border-t font-semibold">
                        <span>Total Deductions</span>
                        <span className="text-red-600">
                          {formatCurrency((employee.salary_structure?.pf_employee || 0) + (employee.salary_structure?.professional_tax || 0))}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Leaves Tab */}
        <TabsContent value="leaves" className="space-y-6">
          {/* Leave Balance Cards */}
          <div className="grid gap-4 md:grid-cols-4">
            {employee.leaves?.map((leave) => (
              <Card key={leave.leave_type_code}>
                <CardContent className="pt-6">
                  <p className="text-sm text-muted-foreground mb-1">{leave.leave_type_name}</p>
                  <div className="flex items-end gap-2">
                    <span className="text-3xl font-bold text-primary">{leave.available}</span>
                    <span className="text-muted-foreground mb-1">/ {leave.opening_balance + leave.credited}</span>
                  </div>
                  <div className="mt-2 flex gap-4 text-xs text-muted-foreground">
                    <span>Used: {leave.used}</span>
                    {leave.pending_approval > 0 && (
                      <span className="text-yellow-600">Pending: {leave.pending_approval}</span>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Leave History */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Leave History</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {leaveHistory.map((leave) => (
                  <div
                    key={leave.id}
                    className="flex items-center justify-between p-4 border rounded-lg"
                  >
                    <div>
                      <p className="font-medium">{leave.type}</p>
                      <p className="text-sm text-muted-foreground">
                        {formatDate(leave.from, { format: 'long' })}
                        {leave.from !== leave.to && ` - ${formatDate(leave.to, { format: 'long' })}`}
                        {' '}({leave.days} day{leave.days > 1 ? 's' : ''})
                      </p>
                      <p className="text-sm text-muted-foreground">{leave.reason}</p>
                    </div>
                    <Badge className={
                      leave.status === 'approved' ? 'bg-green-100 text-green-800' :
                      leave.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                      'bg-red-100 text-red-800'
                    }>
                      {leave.status === 'approved' && <CheckCircle className="h-3 w-3 mr-1" />}
                      {leave.status === 'pending' && <Clock className="h-3 w-3 mr-1" />}
                      {leave.status.charAt(0).toUpperCase() + leave.status.slice(1)}
                    </Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Assets Tab */}
        <TabsContent value="assets" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Assigned Assets</CardTitle>
              <CardDescription>Company assets assigned to this employee</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {employee.assets?.map((asset) => (
                  <div
                    key={asset.id}
                    className="flex items-center justify-between p-4 border rounded-lg"
                  >
                    <div className="flex items-center gap-4">
                      <div className="w-10 h-10 bg-muted rounded flex items-center justify-center">
                        {asset.type === 'Laptop' ? (
                          <Laptop className="h-5 w-5 text-muted-foreground" />
                        ) : (
                          <Package className="h-5 w-5 text-muted-foreground" />
                        )}
                      </div>
                      <div>
                        <p className="font-medium">{asset.name}</p>
                        <p className="text-sm text-muted-foreground">
                          {asset.type} - S/N: {asset.serial_number}
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <Badge className={asset.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}>
                        {asset.status === 'active' ? 'Active' : 'Returned'}
                      </Badge>
                      <p className="text-sm text-muted-foreground mt-1">
                        Assigned: {formatDate(asset.assigned_date, { format: 'long' })}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
