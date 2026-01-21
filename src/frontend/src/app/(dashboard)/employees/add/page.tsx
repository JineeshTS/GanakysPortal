'use client'

import * as React from 'react'
import { useRouter } from 'next/navigation'
import { PageHeader } from '@/components/layout/page-header'
import { EmployeeForm, EmployeeFormData } from '@/components/employees/EmployeeForm'
import { useToast } from '@/hooks/use-toast'
import { useApi } from '@/hooks'

export default function AddEmployeePage() {
  const router = useRouter()
  const { toast } = useToast()
  const api = useApi()

  const handleSubmit = async (data: EmployeeFormData) => {
    try {
      // Build API request
      const requestData = {
        employee_code: data.employee_code,
        first_name: data.first_name,
        middle_name: data.middle_name || null,
        last_name: data.last_name,
        date_of_birth: data.date_of_birth || null,
        gender: data.gender || null,
        date_of_joining: data.date_of_joining,
        department_id: data.department_id || null,
        designation_id: data.designation_id || null,
        reporting_to: data.reporting_to || null,
        employment_type: data.employment_type || 'full_time'
      }

      const result = await api.post('/employees', requestData)

      if (result) {
        toast({
          title: 'Employee Created',
          description: `${data.first_name} ${data.last_name} has been added successfully.`,
          variant: 'success'
        })
        router.push('/employees')
      }
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to create employee. Please try again.',
        variant: 'destructive'
      })
      throw error
    }
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Add New Employee"
        description="Onboard a new employee with complete details"
        breadcrumbs={[
          { label: 'Dashboard', href: '/' },
          { label: 'Employees', href: '/employees' },
          { label: 'Add Employee' }
        ]}
      />

      <EmployeeForm onSubmit={handleSubmit} />
    </div>
  )
}
