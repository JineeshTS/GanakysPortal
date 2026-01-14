'use client'

import * as React from 'react'
import { useParams, useRouter } from 'next/navigation'
import { PageHeader } from '@/components/layout/page-header'
import { EmployeeForm, EmployeeFormData } from '@/components/employees/EmployeeForm'
import { LoadingSpinner } from '@/components/layout/loading-spinner'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { useToast } from '@/hooks/use-toast'
import { useApi } from '@/hooks'
import { formatDate, formatRelativeTime } from '@/lib/format'
import { History, User } from 'lucide-react'

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

// Mock employee data - would come from API
const mockEmployeeData: Partial<EmployeeFormData> & {
  id: string
  full_name: string
  change_history: Array<{
    id: string
    field: string
    old_value: string
    new_value: string
    changed_by: string
    changed_at: string
  }>
} = {
  id: '1',
  full_name: 'Rajesh Kumar Sharma',
  first_name: 'Rajesh',
  middle_name: 'Kumar',
  last_name: 'Sharma',
  date_of_birth: '1990-05-15',
  gender: 'male',
  blood_group: 'O+',
  marital_status: 'married',
  father_name: 'Suresh Kumar Sharma',
  mobile: '9876543210',
  personal_email: 'rajesh.personal@gmail.com',
  work_email: 'rajesh.kumar@company.com',
  emergency_contact_name: 'Priya Sharma',
  emergency_contact_relationship: 'Wife',
  emergency_contact_phone: '9876543211',
  current_address_line1: '123 MG Road',
  current_address_line2: 'Near Central Mall',
  current_address_city: 'Bangalore',
  current_address_state: 'Karnataka',
  current_address_pincode: '560001',
  permanent_address_same: false,
  permanent_address_line1: '456 Gandhi Nagar',
  permanent_address_city: 'Jaipur',
  permanent_address_state: 'Rajasthan',
  permanent_address_pincode: '302015',
  aadhaar: '234567891234',
  pan: 'ABCDE1234F',
  passport_number: 'J1234567',
  passport_expiry: '2028-05-15',
  employee_code: 'EMP001',
  date_of_joining: '2022-04-15',
  department_id: '1',
  designation_id: '2',
  reporting_to: '10',
  work_location: 'bangalore_hq',
  employment_type: 'full_time',
  probation_period_months: '6',
  notice_period_days: '60',
  annual_ctc: '1800000',
  basic_percentage: '50',
  hra_percentage: '20',
  pf_opt_in: true,
  esi_applicable: false,
  bank_account_holder: 'Rajesh Kumar Sharma',
  bank_account_number: '1234567890123456',
  bank_name: 'HDFC Bank',
  bank_branch: 'MG Road Branch',
  bank_ifsc: 'HDFC0001234',
  uan: '100123456789',
  change_history: [
    {
      id: '1',
      field: 'designation_id',
      old_value: 'Software Engineer',
      new_value: 'Senior Software Engineer',
      changed_by: 'HR Admin',
      changed_at: '2024-01-15T10:30:00Z'
    },
    {
      id: '2',
      field: 'annual_ctc',
      old_value: '1500000',
      new_value: '1800000',
      changed_by: 'HR Admin',
      changed_at: '2024-01-15T10:30:00Z'
    },
    {
      id: '3',
      field: 'current_address_line1',
      old_value: '100 Brigade Road',
      new_value: '123 MG Road',
      changed_by: 'Self',
      changed_at: '2023-11-20T14:15:00Z'
    },
    {
      id: '4',
      field: 'bank_account_number',
      old_value: '************3456',
      new_value: '************6789',
      changed_by: 'Self',
      changed_at: '2023-08-10T09:00:00Z'
    }
  ]
}

export default function EditEmployeePage() {
  const params = useParams()
  const router = useRouter()
  const { toast } = useToast()
  const [employee, setEmployee] = React.useState<typeof mockEmployeeData | null>(null)
  const [isLoading, setIsLoading] = React.useState(true)
  const [showHistory, setShowHistory] = React.useState(false)
  const api = useApi<EmployeeApiResponse>()
  const updateApi = useApi()

  // Fetch employee data from API
  React.useEffect(() => {
    const fetchEmployee = async () => {
      if (!params.id) return
      try {
        const result = await api.get(`/employees/${params.id}`)
        if (result) {
          // Merge API data with mock defaults for fields not yet in API
          setEmployee({
            ...mockEmployeeData,
            id: result.id,
            full_name: result.full_name,
            first_name: result.first_name,
            middle_name: result.middle_name || '',
            last_name: result.last_name,
            date_of_birth: result.date_of_birth || mockEmployeeData.date_of_birth,
            gender: result.gender?.toLowerCase() || 'male',
            date_of_joining: result.date_of_joining,
            employee_code: result.employee_code
          })
        }
      } catch (error) {
        toast({
          title: 'Error',
          description: 'Failed to load employee data.',
          variant: 'destructive'
        })
      } finally {
        setIsLoading(false)
      }
    }

    fetchEmployee()
  }, [params.id])

  const handleSubmit = async (data: EmployeeFormData) => {
    try {
      // Build update request
      const updateData = {
        first_name: data.first_name,
        middle_name: data.middle_name || null,
        last_name: data.last_name,
        date_of_birth: data.date_of_birth || null,
        gender: data.gender || null,
        marital_status: data.marital_status || null,
        department_id: data.department_id || null,
        designation_id: data.designation_id || null,
        reporting_to: data.reporting_to || null,
        employment_status: undefined // Not updating status through this form
      }

      const result = await updateApi.put(`/employees/${params.id}`, updateData)

      if (result) {
        toast({
          title: 'Employee Updated',
          description: `${data.first_name} ${data.last_name}'s profile has been updated.`,
          variant: 'success'
        })
        router.push(`/employees/${params.id}`)
      }
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to update employee. Please try again.',
        variant: 'destructive'
      })
      throw error
    }
  }

  const getFieldLabel = (field: string): string => {
    const labels: Record<string, string> = {
      first_name: 'First Name',
      last_name: 'Last Name',
      designation_id: 'Designation',
      department_id: 'Department',
      annual_ctc: 'Annual CTC',
      current_address_line1: 'Current Address',
      bank_account_number: 'Bank Account',
      mobile: 'Mobile Number',
      work_email: 'Work Email'
    }
    return labels[field] || field.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  if (!employee) {
    return (
      <div className="text-center py-12">
        <h2 className="text-xl font-semibold">Employee not found</h2>
        <p className="text-muted-foreground mt-2">The employee you're looking for doesn't exist.</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title={`Edit Employee: ${employee.full_name}`}
        description="Update employee information and track changes"
        breadcrumbs={[
          { label: 'Dashboard', href: '/' },
          { label: 'Employees', href: '/employees' },
          { label: employee.full_name, href: `/employees/${params.id}` },
          { label: 'Edit' }
        ]}
        actions={
          <button
            onClick={() => setShowHistory(!showHistory)}
            className="flex items-center gap-2 px-3 py-2 text-sm border rounded-md hover:bg-muted"
          >
            <History className="h-4 w-4" />
            {showHistory ? 'Hide' : 'Show'} Change History
          </button>
        }
      />

      {/* Change History */}
      {showHistory && employee.change_history && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <History className="h-5 w-5" />
              Change History
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {employee.change_history.map((change) => (
                <div
                  key={change.id}
                  className="flex items-start justify-between p-4 border rounded-lg"
                >
                  <div className="flex items-start gap-4">
                    <div className="w-8 h-8 bg-muted rounded-full flex items-center justify-center">
                      <User className="h-4 w-4" />
                    </div>
                    <div>
                      <p className="font-medium">{getFieldLabel(change.field)}</p>
                      <p className="text-sm text-muted-foreground mt-1">
                        Changed from{' '}
                        <span className="font-medium text-red-600 line-through">{change.old_value}</span>
                        {' '}to{' '}
                        <span className="font-medium text-green-600">{change.new_value}</span>
                      </p>
                      <p className="text-xs text-muted-foreground mt-1">
                        by {change.changed_by}
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-muted-foreground">
                      {formatRelativeTime(change.changed_at)}
                    </p>
                    <p className="text-xs text-muted-foreground">
                      {formatDate(change.changed_at, { format: 'long', showTime: true })}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      <EmployeeForm
        initialData={employee}
        onSubmit={handleSubmit}
        isEdit
      />
    </div>
  )
}
