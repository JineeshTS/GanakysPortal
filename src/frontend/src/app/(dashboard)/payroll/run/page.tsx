'use client'

import * as React from 'react'
import { useRouter } from 'next/navigation'
import { PageHeader } from '@/components/layout/page-header'
import { PayrollWizard } from '@/components/payroll/PayrollWizard'
import { useToast } from '@/hooks/use-toast'
import { getMonthName } from '@/lib/format'

export default function PayrollRunPage() {
  const router = useRouter()
  const { toast } = useToast()

  const handleComplete = (data: { month: number; year: number }) => {
    toast({
      title: 'Payroll Submitted',
      description: `Payroll for ${getMonthName(data.month)} ${data.year} has been submitted for approval.`,
      variant: 'success'
    })
    router.push('/payroll')
  }

  const handleCancel = () => {
    router.push('/payroll')
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="Run Payroll"
        description="Process monthly payroll for employees"
        breadcrumbs={[
          { label: 'Dashboard', href: '/dashboard' },
          { label: 'Payroll', href: '/payroll' },
          { label: 'Run Payroll' }
        ]}
      />

      <PayrollWizard
        onComplete={handleComplete}
        onCancel={handleCancel}
      />
    </div>
  )
}
