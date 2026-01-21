'use client'

import * as React from 'react'
import { cn } from '@/lib/utils'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { formatCurrency, formatPercentage } from '@/lib/format'
import {
  Wallet,
  TrendingUp,
  TrendingDown,
  Building,
  Calculator,
  IndianRupee,
  PieChart,
  Info
} from 'lucide-react'

// ============================================================================
// Types
// ============================================================================

export interface SalaryComponent {
  code: string
  name: string
  type: 'earning' | 'deduction' | 'employer'
  amount: number
  percentage?: number
  percentageOf?: string
  isTaxable: boolean
  isStatutory: boolean
  statutoryType?: 'pf' | 'esi' | 'pt' | 'tds' | 'lwf' | 'gratuity'
  info?: string
}

export interface SalaryBreakdownData {
  ctc_annual: number
  ctc_monthly: number
  gross_monthly: number
  net_monthly: number
  earnings: SalaryComponent[]
  deductions: SalaryComponent[]
  employer_contributions: SalaryComponent[]
  tax_regime?: 'old' | 'new'
}

export interface SalaryBreakdownProps {
  data: SalaryBreakdownData
  showEmployerCost?: boolean
  showTaxInfo?: boolean
  variant?: 'default' | 'compact' | 'detailed'
  className?: string
}

// ============================================================================
// Statutory Info Cards
// ============================================================================

const statutoryInfo = {
  pf: {
    title: 'Provident Fund (PF)',
    description: 'Employee Provident Fund contribution',
    rates: [
      'Employee: 12% of Basic',
      'Employer: 12% of Basic (8.33% EPS + 3.67% EPF)',
      'Admin charges: 0.5% of Basic'
    ],
    ceiling: 'PF calculated on Basic up to Rs.15,000 (optional for higher)',
    color: 'blue'
  },
  esi: {
    title: 'Employee State Insurance (ESI)',
    description: 'Health insurance scheme',
    rates: [
      'Employee: 0.75% of Gross',
      'Employer: 3.25% of Gross'
    ],
    ceiling: 'Applicable if Gross <= Rs.21,000/month',
    color: 'green'
  },
  pt: {
    title: 'Professional Tax (PT)',
    description: 'State-imposed tax on professionals',
    rates: [
      'Karnataka: Rs.200/month (Rs.300 in Feb)',
      'Maharashtra: Up to Rs.200/month',
      'Tamil Nadu: Based on income slab'
    ],
    ceiling: 'Maximum Rs.2,500 per year',
    color: 'purple'
  },
  tds: {
    title: 'Tax Deducted at Source (TDS)',
    description: 'Income tax deduction',
    rates: [
      'Old Regime: Standard deduction + exemptions',
      'New Regime: Lower rates, no exemptions',
      'Calculated based on projected annual income'
    ],
    color: 'orange'
  },
  gratuity: {
    title: 'Gratuity',
    description: 'Retirement benefit after 5 years',
    rates: [
      'Formula: (Basic + DA) x 15/26 x Years',
      'Monthly provision: ~4.81% of Basic'
    ],
    ceiling: 'Maximum Rs.20 Lakh',
    color: 'teal'
  }
}

// ============================================================================
// Component: Earnings Breakdown
// ============================================================================

interface EarningsBreakdownProps {
  earnings: SalaryComponent[]
  totalGross: number
}

function EarningsBreakdown({ earnings, totalGross }: EarningsBreakdownProps) {
  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-center gap-2">
          <div className="h-8 w-8 rounded-full bg-green-100 flex items-center justify-center">
            <TrendingUp className="h-4 w-4 text-green-600" />
          </div>
          <div>
            <CardTitle className="text-base">Earnings</CardTitle>
            <CardDescription>Monthly salary components</CardDescription>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        {earnings.map((component, index) => (
          <div
            key={component.code}
            className="flex items-center justify-between py-2 border-b last:border-0"
          >
            <div className="flex items-center gap-2">
              <span className="text-sm">{component.name}</span>
              {component.isTaxable && (
                <Badge variant="outline" className="text-xs">Taxable</Badge>
              )}
              {component.percentage && (
                <span className="text-xs text-muted-foreground">
                  ({formatPercentage(component.percentage)} of {component.percentageOf || 'Basic'})
                </span>
              )}
            </div>
            <div className="text-right">
              <span className="font-medium">{formatCurrency(component.amount)}</span>
              <span className="text-xs text-muted-foreground block">
                {formatPercentage((component.amount / totalGross) * 100)} of Gross
              </span>
            </div>
          </div>
        ))}

        <div className="flex justify-between pt-3 border-t-2">
          <span className="font-semibold">Total Gross Salary</span>
          <span className="font-bold text-lg text-green-600">{formatCurrency(totalGross)}</span>
        </div>
      </CardContent>
    </Card>
  )
}

// ============================================================================
// Component: Deductions Breakdown
// ============================================================================

interface DeductionsBreakdownProps {
  deductions: SalaryComponent[]
  totalDeductions: number
  showInfo?: boolean
}

function DeductionsBreakdown({ deductions, totalDeductions, showInfo }: DeductionsBreakdownProps) {
  const [expandedInfo, setExpandedInfo] = React.useState<string | null>(null)

  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-center gap-2">
          <div className="h-8 w-8 rounded-full bg-red-100 flex items-center justify-center">
            <TrendingDown className="h-4 w-4 text-red-600" />
          </div>
          <div>
            <CardTitle className="text-base">Deductions</CardTitle>
            <CardDescription>Statutory & other deductions</CardDescription>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        {deductions.map((component) => {
          const info = component.statutoryType ? statutoryInfo[component.statutoryType] : null

          return (
            <div key={component.code} className="space-y-2">
              <div className="flex items-center justify-between py-2 border-b">
                <div className="flex items-center gap-2">
                  <span className="text-sm">{component.name}</span>
                  {component.isStatutory && (
                    <Badge variant="secondary" className="text-xs">Statutory</Badge>
                  )}
                  {showInfo && info && (
                    <button
                      onClick={() => setExpandedInfo(
                        expandedInfo === component.code ? null : component.code
                      )}
                      className="text-muted-foreground hover:text-foreground"
                    >
                      <Info className="h-3.5 w-3.5" />
                    </button>
                  )}
                </div>
                <span className="font-medium text-red-600">
                  -{formatCurrency(component.amount)}
                </span>
              </div>

              {showInfo && expandedInfo === component.code && info && (
                <div className={cn(
                  "p-3 rounded-lg text-sm",
                  info.color === 'blue' && "bg-blue-50 text-blue-800",
                  info.color === 'green' && "bg-green-50 text-green-800",
                  info.color === 'purple' && "bg-purple-50 text-purple-800",
                  info.color === 'orange' && "bg-orange-50 text-orange-800"
                )}>
                  <p className="font-medium mb-2">{info.title}</p>
                  <ul className="space-y-1">
                    {info.rates.map((rate, i) => (
                      <li key={i} className="text-xs">{rate}</li>
                    ))}
                  </ul>
                  {info.ceiling && (
                    <p className="text-xs mt-2 opacity-75">{info.ceiling}</p>
                  )}
                </div>
              )}
            </div>
          )
        })}

        <div className="flex justify-between pt-3 border-t-2">
          <span className="font-semibold">Total Deductions</span>
          <span className="font-bold text-lg text-red-600">-{formatCurrency(totalDeductions)}</span>
        </div>
      </CardContent>
    </Card>
  )
}

// ============================================================================
// Component: Employer Contributions
// ============================================================================

interface EmployerContributionsBreakdownProps {
  contributions: SalaryComponent[]
  total: number
}

function EmployerContributionsBreakdown({ contributions, total }: EmployerContributionsBreakdownProps) {
  return (
    <Card className="bg-blue-50/50">
      <CardHeader className="pb-3">
        <div className="flex items-center gap-2">
          <div className="h-8 w-8 rounded-full bg-blue-100 flex items-center justify-center">
            <Building className="h-4 w-4 text-blue-600" />
          </div>
          <div>
            <CardTitle className="text-base">Employer Contributions</CardTitle>
            <CardDescription>Company-borne statutory costs</CardDescription>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-3">
        {contributions.map((component) => (
          <div
            key={component.code}
            className="flex items-center justify-between py-2 border-b border-blue-100 last:border-0"
          >
            <div className="flex items-center gap-2">
              <span className="text-sm">{component.name}</span>
              {component.percentage && (
                <span className="text-xs text-muted-foreground">
                  ({formatPercentage(component.percentage)} of {component.percentageOf || 'Basic'})
                </span>
              )}
            </div>
            <span className="font-medium text-blue-700">{formatCurrency(component.amount)}</span>
          </div>
        ))}

        <div className="flex justify-between pt-3 border-t-2 border-blue-200">
          <span className="font-semibold">Total Employer Cost</span>
          <span className="font-bold text-lg text-blue-700">{formatCurrency(total)}</span>
        </div>
      </CardContent>
    </Card>
  )
}

// ============================================================================
// Component: Summary Card
// ============================================================================

interface SummaryCardProps {
  data: SalaryBreakdownData
}

function SummaryCard({ data }: SummaryCardProps) {
  const totalDeductions = data.deductions.reduce((sum, d) => sum + d.amount, 0)
  const totalEmployer = data.employer_contributions.reduce((sum, c) => sum + c.amount, 0)

  return (
    <Card className="bg-gradient-to-br from-primary/10 to-primary/5 border-primary/20">
      <CardContent className="pt-6">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
          <div className="space-y-1">
            <p className="text-sm text-muted-foreground">Annual CTC</p>
            <p className="text-2xl font-bold">{formatCurrency(data.ctc_annual)}</p>
          </div>
          <div className="space-y-1">
            <p className="text-sm text-muted-foreground">Monthly Gross</p>
            <p className="text-2xl font-bold">{formatCurrency(data.gross_monthly)}</p>
          </div>
          <div className="space-y-1">
            <p className="text-sm text-muted-foreground">Total Deductions</p>
            <p className="text-2xl font-bold text-red-600">-{formatCurrency(totalDeductions)}</p>
          </div>
          <div className="space-y-1">
            <p className="text-sm text-muted-foreground">Net Monthly</p>
            <p className="text-2xl font-bold text-green-600">{formatCurrency(data.net_monthly)}</p>
          </div>
        </div>

        <div className="mt-6 pt-4 border-t border-primary/20 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <IndianRupee className="h-5 w-5 text-primary" />
            <span className="font-medium">Total Cost to Company (Monthly)</span>
          </div>
          <span className="text-xl font-bold">{formatCurrency(data.ctc_monthly)}</span>
        </div>
      </CardContent>
    </Card>
  )
}

// ============================================================================
// Component: Tax Regime Comparison
// ============================================================================

interface TaxComparisonProps {
  grossAnnual: number
  basicAnnual: number
  currentRegime?: 'old' | 'new'
}

function TaxComparison({ grossAnnual, basicAnnual, currentRegime }: TaxComparisonProps) {
  // Simplified tax calculation for illustration
  const calculateOldRegime = () => {
    const standardDeduction = 50000
    const section80C = 150000 // PF, etc.
    const hra = basicAnnual * 0.4 // Assuming 40% of basic as HRA exemption
    const taxableIncome = grossAnnual - standardDeduction - section80C - hra

    // Old regime slabs
    let tax = 0
    if (taxableIncome > 1000000) tax += (taxableIncome - 1000000) * 0.3
    if (taxableIncome > 500000) tax += Math.min(taxableIncome - 500000, 500000) * 0.2
    if (taxableIncome > 250000) tax += Math.min(taxableIncome - 250000, 250000) * 0.05

    return { taxable: taxableIncome, tax: Math.max(0, tax) }
  }

  const calculateNewRegime = () => {
    const standardDeduction = 75000 // Updated for 2024
    const taxableIncome = grossAnnual - standardDeduction

    // New regime slabs (FY 2024-25)
    let tax = 0
    if (taxableIncome > 1500000) tax += (taxableIncome - 1500000) * 0.3
    if (taxableIncome > 1200000) tax += Math.min(taxableIncome - 1200000, 300000) * 0.2
    if (taxableIncome > 900000) tax += Math.min(taxableIncome - 900000, 300000) * 0.15
    if (taxableIncome > 600000) tax += Math.min(taxableIncome - 600000, 300000) * 0.1
    if (taxableIncome > 300000) tax += Math.min(taxableIncome - 300000, 300000) * 0.05

    // Rebate under section 87A for income up to 7 lakh
    if (taxableIncome <= 700000) tax = 0

    return { taxable: taxableIncome, tax: Math.max(0, tax) }
  }

  const oldRegime = calculateOldRegime()
  const newRegime = calculateNewRegime()
  const betterRegime = oldRegime.tax < newRegime.tax ? 'old' : 'new'

  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-center gap-2">
          <div className="h-8 w-8 rounded-full bg-orange-100 flex items-center justify-center">
            <Calculator className="h-4 w-4 text-orange-600" />
          </div>
          <div>
            <CardTitle className="text-base">Tax Regime Comparison</CardTitle>
            <CardDescription>Estimate based on current salary structure</CardDescription>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 gap-4">
          <div className={cn(
            "p-4 rounded-lg border-2",
            currentRegime === 'old' ? "border-primary bg-primary/5" : "border-muted"
          )}>
            <div className="flex items-center justify-between mb-2">
              <span className="font-medium">Old Regime</span>
              {betterRegime === 'old' && (
                <Badge variant="success" className="text-xs">Recommended</Badge>
              )}
            </div>
            <p className="text-sm text-muted-foreground mb-1">
              Taxable: {formatCurrency(Math.max(0, oldRegime.taxable))}
            </p>
            <p className="text-lg font-bold">
              Tax: {formatCurrency(oldRegime.tax)}/year
            </p>
            <p className="text-sm text-muted-foreground">
              Monthly TDS: {formatCurrency(oldRegime.tax / 12)}
            </p>
          </div>

          <div className={cn(
            "p-4 rounded-lg border-2",
            currentRegime === 'new' ? "border-primary bg-primary/5" : "border-muted"
          )}>
            <div className="flex items-center justify-between mb-2">
              <span className="font-medium">New Regime</span>
              {betterRegime === 'new' && (
                <Badge variant="success" className="text-xs">Recommended</Badge>
              )}
            </div>
            <p className="text-sm text-muted-foreground mb-1">
              Taxable: {formatCurrency(Math.max(0, newRegime.taxable))}
            </p>
            <p className="text-lg font-bold">
              Tax: {formatCurrency(newRegime.tax)}/year
            </p>
            <p className="text-sm text-muted-foreground">
              Monthly TDS: {formatCurrency(newRegime.tax / 12)}
            </p>
          </div>
        </div>

        <p className="text-xs text-muted-foreground mt-4">
          * This is an estimate. Actual tax may vary based on investments, exemptions, and other factors.
        </p>
      </CardContent>
    </Card>
  )
}

// ============================================================================
// Main Component
// ============================================================================

export function SalaryBreakdown({
  data,
  showEmployerCost = true,
  showTaxInfo = true,
  variant = 'default',
  className
}: SalaryBreakdownProps) {
  const totalDeductions = data.deductions.reduce((sum, d) => sum + d.amount, 0)
  const totalEmployer = data.employer_contributions.reduce((sum, c) => sum + c.amount, 0)

  // Get basic salary for tax calculation
  const basicComponent = data.earnings.find(e => e.code === 'basic')
  const basicMonthly = basicComponent?.amount || 0

  if (variant === 'compact') {
    return (
      <Card className={className}>
        <CardContent className="pt-6">
          <div className="space-y-4">
            {/* Earnings Summary */}
            <div className="flex justify-between">
              <span className="text-muted-foreground">Gross Salary</span>
              <span className="font-medium text-green-600">{formatCurrency(data.gross_monthly)}</span>
            </div>

            {/* Key Deductions */}
            {data.deductions.slice(0, 4).map(d => (
              <div key={d.code} className="flex justify-between">
                <span className="text-muted-foreground">{d.name}</span>
                <span className="font-medium text-red-600">-{formatCurrency(d.amount)}</span>
              </div>
            ))}

            <div className="border-t pt-4 flex justify-between">
              <span className="font-semibold">Net Salary</span>
              <span className="font-bold text-lg">{formatCurrency(data.net_monthly)}</span>
            </div>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <div className={cn("space-y-6", className)}>
      {/* Summary Card */}
      <SummaryCard data={data} />

      {/* Main Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <EarningsBreakdown earnings={data.earnings} totalGross={data.gross_monthly} />
        <DeductionsBreakdown
          deductions={data.deductions}
          totalDeductions={totalDeductions}
          showInfo={showTaxInfo}
        />
      </div>

      {/* Employer Contributions */}
      {showEmployerCost && data.employer_contributions.length > 0 && (
        <EmployerContributionsBreakdown
          contributions={data.employer_contributions}
          total={totalEmployer}
        />
      )}

      {/* Tax Comparison */}
      {showTaxInfo && variant === 'detailed' && (
        <TaxComparison
          grossAnnual={data.gross_monthly * 12}
          basicAnnual={basicMonthly * 12}
          currentRegime={data.tax_regime}
        />
      )}
    </div>
  )
}

export default SalaryBreakdown
