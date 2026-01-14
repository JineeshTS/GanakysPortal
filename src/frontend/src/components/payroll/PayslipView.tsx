'use client'

import * as React from 'react'
import { cn } from '@/lib/utils'
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { formatCurrency, formatDate, getMonthName, getFinancialYear } from '@/lib/format'
import {
  Download,
  Mail,
  Printer,
  Building,
  User,
  Calendar,
  CreditCard,
  FileText,
  IndianRupee,
  TrendingUp,
  TrendingDown
} from 'lucide-react'

// ============================================================================
// Types
// ============================================================================

export interface PayslipData {
  id: string
  employee_id: string
  employee_name: string
  employee_code: string
  designation: string
  department: string
  date_of_joining: string
  pan: string
  uan: string
  bank_account: string
  bank_name: string

  // Period
  month: number
  year: number
  working_days: number
  present_days: number
  lop_days: number

  // Earnings
  basic: number
  hra: number
  special_allowance: number
  conveyance: number
  medical: number
  lta: number
  other_allowances: number
  bonus: number
  incentive: number
  arrears: number
  reimbursements: number
  overtime: number
  total_earnings: number

  // Deductions
  pf_employee: number
  esi_employee: number
  pt: number
  tds: number
  lwf: number
  other_deductions: number
  loan_recovery: number
  advance_recovery: number
  total_deductions: number

  // Employer Contributions
  pf_employer: number
  pf_employer_eps: number
  pf_employer_epf: number
  esi_employer: number
  gratuity_provision: number
  total_employer_contribution: number

  // Net
  net_salary: number
  gross_ctc: number

  // YTD
  ytd_basic: number
  ytd_gross: number
  ytd_pf: number
  ytd_pt: number
  ytd_tds: number
  ytd_net: number

  // Status
  status: 'generated' | 'emailed' | 'downloaded'
  generated_at: string

  // Company
  company_name: string
  company_address: string
  company_gstin?: string
  company_pan: string
  company_pf_number?: string
  company_esi_number?: string
}

export interface PayslipViewProps {
  payslip: PayslipData
  onDownload?: () => void
  onEmail?: () => void
  onPrint?: () => void
  showActions?: boolean
  compact?: boolean
}

// ============================================================================
// Earnings Section
// ============================================================================

interface EarningsSectionProps {
  payslip: PayslipData
}

function EarningsSection({ payslip }: EarningsSectionProps) {
  const earnings = [
    { label: 'Basic Salary', value: payslip.basic, show: true },
    { label: 'House Rent Allowance (HRA)', value: payslip.hra, show: true },
    { label: 'Special Allowance', value: payslip.special_allowance, show: true },
    { label: 'Conveyance Allowance', value: payslip.conveyance, show: payslip.conveyance > 0 },
    { label: 'Medical Allowance', value: payslip.medical, show: payslip.medical > 0 },
    { label: 'Leave Travel Allowance (LTA)', value: payslip.lta, show: payslip.lta > 0 },
    { label: 'Other Allowances', value: payslip.other_allowances, show: payslip.other_allowances > 0 },
    { label: 'Bonus', value: payslip.bonus, show: payslip.bonus > 0 },
    { label: 'Incentive', value: payslip.incentive, show: payslip.incentive > 0 },
    { label: 'Arrears', value: payslip.arrears, show: payslip.arrears > 0 },
    { label: 'Reimbursements', value: payslip.reimbursements, show: payslip.reimbursements > 0 },
    { label: 'Overtime Pay', value: payslip.overtime, show: payslip.overtime > 0 }
  ]

  return (
    <div className="space-y-2">
      <div className="flex items-center gap-2 mb-3">
        <TrendingUp className="h-4 w-4 text-green-600" />
        <h3 className="font-semibold text-green-700">Earnings</h3>
      </div>
      {earnings.filter(e => e.show).map((earning, index) => (
        <div key={index} className="flex justify-between py-1.5 border-b border-dashed last:border-0">
          <span className="text-sm text-gray-600">{earning.label}</span>
          <span className="font-medium">{formatCurrency(earning.value)}</span>
        </div>
      ))}
      <div className="flex justify-between py-2 bg-green-50 px-2 rounded font-semibold mt-2">
        <span>Total Earnings (A)</span>
        <span className="text-green-700">{formatCurrency(payslip.total_earnings)}</span>
      </div>
    </div>
  )
}

// ============================================================================
// Deductions Section
// ============================================================================

interface DeductionsSectionProps {
  payslip: PayslipData
}

function DeductionsSection({ payslip }: DeductionsSectionProps) {
  const deductions = [
    {
      label: 'Provident Fund (PF) - 12%',
      value: payslip.pf_employee,
      show: payslip.pf_employee > 0,
      info: 'Employee contribution to EPF'
    },
    {
      label: 'ESI - 0.75%',
      value: payslip.esi_employee,
      show: payslip.esi_employee > 0,
      info: 'Applicable if gross <= Rs.21,000'
    },
    {
      label: 'Professional Tax (PT)',
      value: payslip.pt,
      show: payslip.pt > 0,
      info: 'State-wise slab based'
    },
    {
      label: 'TDS (Income Tax)',
      value: payslip.tds,
      show: payslip.tds > 0,
      info: 'As per declared tax regime'
    },
    {
      label: 'Labour Welfare Fund (LWF)',
      value: payslip.lwf,
      show: payslip.lwf > 0,
      info: 'State-wise contribution'
    },
    {
      label: 'Other Deductions',
      value: payslip.other_deductions,
      show: payslip.other_deductions > 0
    },
    {
      label: 'Loan Recovery',
      value: payslip.loan_recovery,
      show: payslip.loan_recovery > 0
    },
    {
      label: 'Advance Recovery',
      value: payslip.advance_recovery,
      show: payslip.advance_recovery > 0
    }
  ]

  return (
    <div className="space-y-2">
      <div className="flex items-center gap-2 mb-3">
        <TrendingDown className="h-4 w-4 text-red-600" />
        <h3 className="font-semibold text-red-700">Deductions</h3>
      </div>
      {deductions.filter(d => d.show).map((deduction, index) => (
        <div key={index} className="flex justify-between py-1.5 border-b border-dashed last:border-0">
          <span className="text-sm text-gray-600">{deduction.label}</span>
          <span className="font-medium text-red-600">-{formatCurrency(deduction.value)}</span>
        </div>
      ))}
      <div className="flex justify-between py-2 bg-red-50 px-2 rounded font-semibold mt-2">
        <span>Total Deductions (B)</span>
        <span className="text-red-700">-{formatCurrency(payslip.total_deductions)}</span>
      </div>
    </div>
  )
}

// ============================================================================
// Employer Contributions Section
// ============================================================================

interface EmployerContributionsProps {
  payslip: PayslipData
}

function EmployerContributions({ payslip }: EmployerContributionsProps) {
  return (
    <div className="space-y-2">
      <div className="flex items-center gap-2 mb-3">
        <Building className="h-4 w-4 text-blue-600" />
        <h3 className="font-semibold text-blue-700">Employer Contributions</h3>
      </div>

      {payslip.pf_employer > 0 && (
        <>
          <div className="flex justify-between py-1.5 border-b border-dashed">
            <span className="text-sm text-gray-600">PF - EPS (8.33%)</span>
            <span className="font-medium">{formatCurrency(payslip.pf_employer_eps)}</span>
          </div>
          <div className="flex justify-between py-1.5 border-b border-dashed">
            <span className="text-sm text-gray-600">PF - EPF (3.67%)</span>
            <span className="font-medium">{formatCurrency(payslip.pf_employer_epf)}</span>
          </div>
        </>
      )}

      {payslip.esi_employer > 0 && (
        <div className="flex justify-between py-1.5 border-b border-dashed">
          <span className="text-sm text-gray-600">ESI (3.25%)</span>
          <span className="font-medium">{formatCurrency(payslip.esi_employer)}</span>
        </div>
      )}

      {payslip.gratuity_provision > 0 && (
        <div className="flex justify-between py-1.5 border-b border-dashed">
          <span className="text-sm text-gray-600">Gratuity Provision</span>
          <span className="font-medium">{formatCurrency(payslip.gratuity_provision)}</span>
        </div>
      )}

      <div className="flex justify-between py-2 bg-blue-50 px-2 rounded font-semibold mt-2">
        <span>Total Employer Cost</span>
        <span className="text-blue-700">{formatCurrency(payslip.total_employer_contribution)}</span>
      </div>
    </div>
  )
}

// ============================================================================
// YTD Summary Section
// ============================================================================

interface YTDSummaryProps {
  payslip: PayslipData
}

function YTDSummary({ payslip }: YTDSummaryProps) {
  const financialYear = getFinancialYear(new Date(payslip.year, payslip.month - 1))

  return (
    <Card className="bg-gray-50">
      <CardHeader className="pb-2">
        <CardTitle className="text-sm">Year-to-Date Summary ({financialYear})</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          <div>
            <p className="text-xs text-muted-foreground">YTD Basic</p>
            <p className="font-semibold">{formatCurrency(payslip.ytd_basic)}</p>
          </div>
          <div>
            <p className="text-xs text-muted-foreground">YTD Gross</p>
            <p className="font-semibold">{formatCurrency(payslip.ytd_gross)}</p>
          </div>
          <div>
            <p className="text-xs text-muted-foreground">YTD PF</p>
            <p className="font-semibold text-blue-600">{formatCurrency(payslip.ytd_pf)}</p>
          </div>
          <div>
            <p className="text-xs text-muted-foreground">YTD PT</p>
            <p className="font-semibold">{formatCurrency(payslip.ytd_pt)}</p>
          </div>
          <div>
            <p className="text-xs text-muted-foreground">YTD TDS</p>
            <p className="font-semibold text-orange-600">{formatCurrency(payslip.ytd_tds)}</p>
          </div>
          <div>
            <p className="text-xs text-muted-foreground">YTD Net</p>
            <p className="font-semibold text-green-600">{formatCurrency(payslip.ytd_net)}</p>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

// ============================================================================
// Main Payslip View Component
// ============================================================================

export function PayslipView({
  payslip,
  onDownload,
  onEmail,
  onPrint,
  showActions = true,
  compact = false
}: PayslipViewProps) {
  return (
    <div className="space-y-6">
      {/* Header Actions */}
      {showActions && (
        <div className="flex items-center justify-end gap-2 print:hidden">
          {onPrint && (
            <Button variant="outline" size="sm" onClick={onPrint}>
              <Printer className="h-4 w-4 mr-2" />
              Print
            </Button>
          )}
          {onEmail && (
            <Button variant="outline" size="sm" onClick={onEmail}>
              <Mail className="h-4 w-4 mr-2" />
              Email
            </Button>
          )}
          {onDownload && (
            <Button size="sm" onClick={onDownload}>
              <Download className="h-4 w-4 mr-2" />
              Download PDF
            </Button>
          )}
        </div>
      )}

      {/* Main Payslip Card */}
      <Card className="border-2">
        {/* Company Header */}
        <CardHeader className="border-b bg-primary/5">
          <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4">
            <div>
              <CardTitle className="text-xl">{payslip.company_name}</CardTitle>
              <CardDescription className="mt-1">{payslip.company_address}</CardDescription>
              <div className="flex flex-wrap gap-4 mt-2 text-sm">
                {payslip.company_gstin && (
                  <span>GSTIN: {payslip.company_gstin}</span>
                )}
                <span>PAN: {payslip.company_pan}</span>
                {payslip.company_pf_number && (
                  <span>PF: {payslip.company_pf_number}</span>
                )}
              </div>
            </div>
            <div className="text-right">
              <Badge variant="outline" className="text-lg px-3 py-1">
                Payslip
              </Badge>
              <p className="text-lg font-semibold mt-2">
                {getMonthName(payslip.month)} {payslip.year}
              </p>
            </div>
          </div>
        </CardHeader>

        <CardContent className="p-6 space-y-6">
          {/* Employee Details */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 p-4 bg-muted/50 rounded-lg">
            <div className="flex items-start gap-2">
              <User className="h-4 w-4 text-muted-foreground mt-0.5" />
              <div>
                <p className="text-xs text-muted-foreground">Employee Name</p>
                <p className="font-medium">{payslip.employee_name}</p>
                <p className="text-sm text-muted-foreground">{payslip.employee_code}</p>
              </div>
            </div>
            <div className="flex items-start gap-2">
              <Building className="h-4 w-4 text-muted-foreground mt-0.5" />
              <div>
                <p className="text-xs text-muted-foreground">Designation</p>
                <p className="font-medium">{payslip.designation}</p>
                <p className="text-sm text-muted-foreground">{payslip.department}</p>
              </div>
            </div>
            <div className="flex items-start gap-2">
              <Calendar className="h-4 w-4 text-muted-foreground mt-0.5" />
              <div>
                <p className="text-xs text-muted-foreground">Date of Joining</p>
                <p className="font-medium">{formatDate(payslip.date_of_joining)}</p>
              </div>
            </div>
            <div className="flex items-start gap-2">
              <FileText className="h-4 w-4 text-muted-foreground mt-0.5" />
              <div>
                <p className="text-xs text-muted-foreground">PAN / UAN</p>
                <p className="font-medium">{payslip.pan}</p>
                <p className="text-sm text-muted-foreground">{payslip.uan}</p>
              </div>
            </div>
          </div>

          {/* Bank Details */}
          <div className="flex items-center gap-4 p-3 bg-blue-50 rounded-lg">
            <CreditCard className="h-5 w-5 text-blue-600" />
            <div>
              <p className="text-sm text-blue-700">Bank Account: {payslip.bank_account}</p>
              <p className="text-xs text-blue-600">{payslip.bank_name}</p>
            </div>
          </div>

          {/* Working Days */}
          <div className="grid grid-cols-3 gap-4 p-4 bg-muted/50 rounded-lg">
            <div className="text-center">
              <p className="text-sm text-muted-foreground">Working Days</p>
              <p className="text-xl font-semibold">{payslip.working_days}</p>
            </div>
            <div className="text-center">
              <p className="text-sm text-muted-foreground">Days Worked</p>
              <p className="text-xl font-semibold text-green-600">{payslip.present_days}</p>
            </div>
            <div className="text-center">
              <p className="text-sm text-muted-foreground">LOP Days</p>
              <p className={cn(
                "text-xl font-semibold",
                payslip.lop_days > 0 ? "text-red-600" : ""
              )}>
                {payslip.lop_days}
              </p>
            </div>
          </div>

          {/* Earnings and Deductions */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <EarningsSection payslip={payslip} />
            <DeductionsSection payslip={payslip} />
          </div>

          {/* Net Salary */}
          <div className="p-4 bg-primary/10 rounded-lg border-2 border-primary/20">
            <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
              <div>
                <p className="text-sm text-muted-foreground">Net Salary (A - B)</p>
                <p className="text-3xl font-bold text-primary">
                  {formatCurrency(payslip.net_salary)}
                </p>
                <p className="text-sm text-muted-foreground mt-1">
                  (Rupees {numberToWords(payslip.net_salary)} Only)
                </p>
              </div>
              <div className="flex items-center gap-2">
                <IndianRupee className="h-8 w-8 text-primary/50" />
              </div>
            </div>
          </div>

          {/* Employer Contributions */}
          {!compact && (
            <EmployerContributions payslip={payslip} />
          )}

          {/* CTC */}
          <div className="flex justify-between p-3 bg-gray-100 rounded-lg">
            <span className="font-medium">Gross Monthly CTC</span>
            <span className="font-bold text-lg">{formatCurrency(payslip.gross_ctc)}</span>
          </div>
        </CardContent>

        {/* Footer */}
        <CardFooter className="border-t bg-muted/30 flex-col items-start text-xs text-muted-foreground">
          <p>This is a system generated payslip and does not require signature.</p>
          <p className="mt-1">Generated on: {formatDate(payslip.generated_at, { format: 'long', showTime: true })}</p>
        </CardFooter>
      </Card>

      {/* YTD Summary */}
      {!compact && <YTDSummary payslip={payslip} />}
    </div>
  )
}

// ============================================================================
// Helper Function: Number to Words (Indian format)
// ============================================================================

function numberToWords(num: number): string {
  if (num === 0) return 'Zero'

  const ones = ['', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine',
    'Ten', 'Eleven', 'Twelve', 'Thirteen', 'Fourteen', 'Fifteen', 'Sixteen', 'Seventeen', 'Eighteen', 'Nineteen']
  const tens = ['', '', 'Twenty', 'Thirty', 'Forty', 'Fifty', 'Sixty', 'Seventy', 'Eighty', 'Ninety']

  const numToWords = (n: number): string => {
    if (n < 20) return ones[n]
    if (n < 100) return tens[Math.floor(n / 10)] + (n % 10 ? ' ' + ones[n % 10] : '')
    if (n < 1000) return ones[Math.floor(n / 100)] + ' Hundred' + (n % 100 ? ' ' + numToWords(n % 100) : '')
    if (n < 100000) return numToWords(Math.floor(n / 1000)) + ' Thousand' + (n % 1000 ? ' ' + numToWords(n % 1000) : '')
    if (n < 10000000) return numToWords(Math.floor(n / 100000)) + ' Lakh' + (n % 100000 ? ' ' + numToWords(n % 100000) : '')
    return numToWords(Math.floor(n / 10000000)) + ' Crore' + (n % 10000000 ? ' ' + numToWords(n % 10000000) : '')
  }

  const rupees = Math.floor(num)
  const paise = Math.round((num - rupees) * 100)

  let result = numToWords(rupees) + ' Rupees'
  if (paise > 0) {
    result += ' and ' + numToWords(paise) + ' Paise'
  }

  return result
}

export default PayslipView
