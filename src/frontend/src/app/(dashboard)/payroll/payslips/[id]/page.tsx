'use client'

import * as React from 'react'
import { useParams, useRouter } from 'next/navigation'
import { PageHeader } from '@/components/layout/page-header'
import { PayslipView, PayslipData } from '@/components/payroll/PayslipView'
import { Button } from '@/components/ui/button'
import { useToast } from '@/hooks/use-toast'
import { ArrowLeft } from 'lucide-react'
import Link from 'next/link'

// ============================================================================
// Mock Data
// ============================================================================

const mockPayslip: PayslipData = {
  id: '1',
  employee_id: '1',
  employee_name: 'Rahul Kumar',
  employee_code: 'EMP001',
  designation: 'Senior Software Developer',
  department: 'Engineering',
  date_of_joining: '2022-06-15',
  pan: 'ABCDE1234F',
  uan: '100123456789',
  bank_account: 'XXXX XXXX 1234',
  bank_name: 'HDFC Bank - Koramangala Branch',

  // Period
  month: 1,
  year: 2026,
  working_days: 22,
  present_days: 21,
  lop_days: 1,

  // Earnings
  basic: 40000,
  hra: 20000,
  special_allowance: 15000,
  conveyance: 1600,
  medical: 1250,
  lta: 2000,
  other_allowances: 150,
  bonus: 0,
  incentive: 0,
  arrears: 0,
  reimbursements: 0,
  overtime: 0,
  total_earnings: 76364, // LOP adjusted from 80000

  // Deductions
  pf_employee: 4800, // 12% of Basic (40000)
  esi_employee: 0, // Not applicable (gross > 21000)
  pt: 200,
  tds: 8500,
  lwf: 0,
  other_deductions: 0,
  loan_recovery: 0,
  advance_recovery: 0,
  total_deductions: 13500,

  // Employer Contributions
  pf_employer: 4800,
  pf_employer_eps: 3332, // 8.33% of 40000
  pf_employer_epf: 1468, // 3.67% of 40000
  esi_employer: 0,
  gratuity_provision: 1923, // ~4.81% of Basic
  total_employer_contribution: 6723,

  // Net
  net_salary: 62864,
  gross_ctc: 91087, // Monthly CTC

  // YTD (10 months of current FY: Apr 2025 - Jan 2026)
  ytd_basic: 400000,
  ytd_gross: 800000,
  ytd_pf: 96000,
  ytd_pt: 2000,
  ytd_tds: 85000,
  ytd_net: 628640,

  // Status
  status: 'generated',
  generated_at: '2026-01-02T10:30:00Z',

  // Company
  company_name: 'TechCorp Solutions Pvt. Ltd.',
  company_address: '123, Tech Park, 5th Floor, Koramangala, Bangalore - 560034, Karnataka, India',
  company_gstin: '29AABCT1234A1ZA',
  company_pan: 'AABCT1234A',
  company_pf_number: 'KN/BAN/0012345',
  company_esi_number: '52-00-123456-000-0001'
}

// ============================================================================
// Component
// ============================================================================

export default function PayslipViewPage() {
  const params = useParams()
  const router = useRouter()
  const { toast } = useToast()
  const payslipId = params.id as string

  // In real app, fetch payslip by ID
  const [payslip] = React.useState<PayslipData>(mockPayslip)

  const handleDownload = () => {
    toast({
      title: 'Downloading Payslip',
      description: 'Your payslip PDF is being generated...',
    })
    // Simulate download
    setTimeout(() => {
      toast({
        title: 'Download Complete',
        description: 'Payslip has been downloaded successfully.',
        variant: 'success'
      })
    }, 1500)
  }

  const handleEmail = () => {
    toast({
      title: 'Sending Email',
      description: 'Payslip is being sent to your registered email...',
    })
    // Simulate email
    setTimeout(() => {
      toast({
        title: 'Email Sent',
        description: 'Payslip has been emailed successfully.',
        variant: 'success'
      })
    }, 1500)
  }

  const handlePrint = () => {
    window.print()
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <PageHeader
        title={`Payslip - ${payslip.employee_name}`}
        description={`${payslip.employee_code} | ${payslip.department}`}
        breadcrumbs={[
          { label: 'Dashboard', href: '/dashboard' },
          { label: 'Payroll', href: '/payroll' },
          { label: 'Payslips', href: '/payroll/payslips' },
          { label: payslip.employee_name }
        ]}
        actions={
          <Button variant="outline" asChild>
            <Link href="/payroll/payslips">
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Payslips
            </Link>
          </Button>
        }
      />

      {/* Payslip View */}
      <PayslipView
        payslip={payslip}
        onDownload={handleDownload}
        onEmail={handleEmail}
        onPrint={handlePrint}
        showActions={true}
      />
    </div>
  )
}
