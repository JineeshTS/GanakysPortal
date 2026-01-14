'use client'

import { useState, useEffect, useCallback } from 'react'
import { PageHeader } from '@/components/layout/page-header'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { useApi, useAuthStore } from '@/hooks'
import {
  Receipt,
  Download,
  IndianRupee,
  TrendingUp,
  Calendar,
  FileText,
  Wallet,
  MinusCircle,
  PlusCircle,
  AlertCircle
} from 'lucide-react'

interface PayslipItem {
  id: string
  employee_id: string
  payroll_run_id: string
  month: number
  year: number
  gross_earnings: number
  total_deductions: number
  net_pay: number
  status: string
  paid_on?: string
  earnings: PayComponent[]
  deductions: PayComponent[]
}

interface PayComponent {
  name: string
  amount: number
  type: string
}

interface PayslipListResponse {
  items: PayslipItem[]
  total: number
}

interface YTDSummary {
  employee_id: string
  year: number
  gross_earnings: number
  total_deductions: number
  net_pay: number
  pf_ytd: number
  esi_ytd: number
  pt_ytd: number
  tds_ytd: number
  months_processed: number
}

const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: 0,
  }).format(amount)
}

const monthNames = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December'
]

export default function MyPayslipsPage() {
  const [selectedYear, setSelectedYear] = useState('2025-26')
  const [selectedPayslip, setSelectedPayslip] = useState<PayslipItem | null>(null)
  const { user } = useAuthStore()

  // API hooks
  const { data: payslipsData, isLoading: isLoadingPayslips, error: payslipsError, get: getPayslips } = useApi<PayslipListResponse>()
  const { data: ytdData, isLoading: isLoadingYtd, get: getYtd } = useApi<YTDSummary>()

  // Fetch payslips
  const fetchData = useCallback(() => {
    if (user?.employee_id) {
      getPayslips(`/payroll/employee/${user.employee_id}/payslips`)
      getYtd(`/payroll/employee/${user.employee_id}/ytd`)
    }
  }, [user?.employee_id, getPayslips, getYtd])

  useEffect(() => {
    fetchData()
  }, [fetchData])

  // Select first payslip when data loads
  useEffect(() => {
    if (payslipsData?.items?.length && !selectedPayslip) {
      setSelectedPayslip(payslipsData.items[0])
    }
  }, [payslipsData, selectedPayslip])

  const payslips = payslipsData?.items || []
  const isLoading = isLoadingPayslips

  // Calculate totals from selected payslip
  const totalEarnings = selectedPayslip?.earnings?.reduce((sum, e) => sum + e.amount, 0) || selectedPayslip?.gross_earnings || 0
  const totalDeductions = selectedPayslip?.deductions?.reduce((sum, d) => sum + d.amount, 0) || selectedPayslip?.total_deductions || 0
  const netPay = selectedPayslip?.net_pay || (totalEarnings - totalDeductions)

  if (!user?.employee_id) {
    return (
      <div className="space-y-6">
        <PageHeader
          title="My Payslips"
          description="View and download your salary statements"
          icon={<Receipt className="h-6 w-6" />}
        />
        <Card>
          <CardContent className="pt-6">
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <AlertCircle className="h-12 w-12 text-muted-foreground mb-4" />
              <h3 className="text-lg font-semibold mb-2">No Employee Profile Found</h3>
              <p className="text-muted-foreground">Your user account is not linked to an employee record. Please contact HR.</p>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  if (isLoading) {
    return (
      <div className="space-y-6">
        <PageHeader
          title="My Payslips"
          description="View and download your salary statements"
          icon={<Receipt className="h-6 w-6" />}
        />
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map(i => (
            <Card key={i}>
              <CardContent className="pt-6">
                <Skeleton className="h-16 w-full" />
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <PageHeader
        title="My Payslips"
        description="View and download your salary statements"
        icon={<Receipt className="h-6 w-6" />}
        actions={
          <Select value={selectedYear} onValueChange={setSelectedYear}>
            <SelectTrigger className="w-40">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="2025-26">FY 2025-26</SelectItem>
              <SelectItem value="2024-25">FY 2024-25</SelectItem>
              <SelectItem value="2023-24">FY 2023-24</SelectItem>
            </SelectContent>
          </Select>
        }
      />

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-green-100 rounded-lg">
                <Wallet className="h-5 w-5 text-green-600" />
              </div>
              <div>
                <p className="text-2xl font-bold">{formatCurrency(totalEarnings)}</p>
                <p className="text-sm text-muted-foreground">Gross Salary</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-red-100 rounded-lg">
                <MinusCircle className="h-5 w-5 text-red-600" />
              </div>
              <div>
                <p className="text-2xl font-bold">{formatCurrency(totalDeductions)}</p>
                <p className="text-sm text-muted-foreground">Deductions</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-100 rounded-lg">
                <IndianRupee className="h-5 w-5 text-blue-600" />
              </div>
              <div>
                <p className="text-2xl font-bold">{formatCurrency(netPay)}</p>
                <p className="text-sm text-muted-foreground">Net Pay</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-purple-100 rounded-lg">
                <TrendingUp className="h-5 w-5 text-purple-600" />
              </div>
              <div>
                <p className="text-2xl font-bold">{formatCurrency(ytdData?.net_pay || 0)}</p>
                <p className="text-sm text-muted-foreground">YTD Earnings</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Payslip List */}
        <Card>
          <CardHeader>
            <CardTitle>Payslip History</CardTitle>
            <CardDescription>Select a month to view details</CardDescription>
          </CardHeader>
          <CardContent>
            {payslipsError ? (
              <div className="flex flex-col items-center justify-center py-8 text-center">
                <AlertCircle className="h-8 w-8 text-muted-foreground mb-2" />
                <p className="text-muted-foreground">{payslipsError}</p>
                <Button variant="outline" onClick={fetchData} className="mt-4">
                  Try Again
                </Button>
              </div>
            ) : payslips.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-8 text-center">
                <Receipt className="h-8 w-8 text-muted-foreground mb-2" />
                <p className="text-muted-foreground">No payslips found</p>
              </div>
            ) : (
              <div className="space-y-2">
                {payslips.map((payslip) => (
                  <button
                    key={payslip.id}
                    onClick={() => setSelectedPayslip(payslip)}
                    className={`w-full p-3 rounded-lg text-left transition-colors ${
                      selectedPayslip?.id === payslip.id
                        ? 'bg-primary text-primary-foreground'
                        : 'bg-muted/50 hover:bg-muted'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-medium">{monthNames[payslip.month - 1]} {payslip.year}</p>
                        <p className={`text-sm ${selectedPayslip?.id === payslip.id ? 'text-primary-foreground/80' : 'text-muted-foreground'}`}>
                          {formatCurrency(payslip.net_pay)}
                        </p>
                      </div>
                      <Badge
                        variant={selectedPayslip?.id === payslip.id ? 'secondary' : 'outline'}
                        className={payslip.status === 'paid' ? 'bg-green-100 text-green-800' : ''}
                      >
                        {payslip.status}
                      </Badge>
                    </div>
                  </button>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Salary Breakdown */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>
                  {selectedPayslip
                    ? `${monthNames[selectedPayslip.month - 1]} ${selectedPayslip.year}`
                    : 'Select a Payslip'}
                </CardTitle>
                <CardDescription>
                  {selectedPayslip
                    ? `Pay period: 01/${selectedPayslip.month.toString().padStart(2, '0')}/${selectedPayslip.year} - ${new Date(selectedPayslip.year, selectedPayslip.month, 0).getDate()}/${selectedPayslip.month.toString().padStart(2, '0')}/${selectedPayslip.year}`
                    : 'Select a month to view breakdown'}
                </CardDescription>
              </div>
              {selectedPayslip && (
                <Button>
                  <Download className="h-4 w-4 mr-2" />
                  Download PDF
                </Button>
              )}
            </div>
          </CardHeader>
          <CardContent>
            {!selectedPayslip ? (
              <div className="flex flex-col items-center justify-center py-12 text-center">
                <Receipt className="h-12 w-12 text-muted-foreground mb-4" />
                <p className="text-muted-foreground">Select a payslip from the list to view details</p>
              </div>
            ) : (
              <>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Earnings */}
                  <div>
                    <h3 className="font-semibold mb-3 flex items-center gap-2">
                      <PlusCircle className="h-4 w-4 text-green-600" />
                      Earnings
                    </h3>
                    <div className="space-y-2">
                      {selectedPayslip.earnings?.length > 0 ? (
                        selectedPayslip.earnings.map((item, idx) => (
                          <div key={idx} className="flex justify-between text-sm">
                            <span className="text-muted-foreground">{item.name}</span>
                            <span className="font-medium">{formatCurrency(item.amount)}</span>
                          </div>
                        ))
                      ) : (
                        <div className="flex justify-between text-sm">
                          <span className="text-muted-foreground">Total Earnings</span>
                          <span className="font-medium">{formatCurrency(selectedPayslip.gross_earnings)}</span>
                        </div>
                      )}
                      <div className="flex justify-between pt-2 border-t font-semibold text-green-600">
                        <span>Total Earnings</span>
                        <span>{formatCurrency(totalEarnings)}</span>
                      </div>
                    </div>
                  </div>

                  {/* Deductions */}
                  <div>
                    <h3 className="font-semibold mb-3 flex items-center gap-2">
                      <MinusCircle className="h-4 w-4 text-red-600" />
                      Deductions
                    </h3>
                    <div className="space-y-2">
                      {selectedPayslip.deductions?.length > 0 ? (
                        selectedPayslip.deductions.map((item, idx) => (
                          <div key={idx} className="flex justify-between text-sm">
                            <span className="text-muted-foreground">{item.name}</span>
                            <span className="font-medium">{formatCurrency(item.amount)}</span>
                          </div>
                        ))
                      ) : (
                        <div className="flex justify-between text-sm">
                          <span className="text-muted-foreground">Total Deductions</span>
                          <span className="font-medium">{formatCurrency(selectedPayslip.total_deductions)}</span>
                        </div>
                      )}
                      <div className="flex justify-between pt-2 border-t font-semibold text-red-600">
                        <span>Total Deductions</span>
                        <span>{formatCurrency(totalDeductions)}</span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Net Pay */}
                <div className="mt-6 p-4 bg-primary/10 rounded-lg">
                  <div className="flex items-center justify-between">
                    <span className="text-lg font-semibold">Net Pay</span>
                    <span className="text-2xl font-bold text-primary">{formatCurrency(netPay)}</span>
                  </div>
                  {selectedPayslip.paid_on && (
                    <p className="text-sm text-muted-foreground mt-1">
                      Paid on: {new Date(selectedPayslip.paid_on).toLocaleDateString('en-IN', { day: 'numeric', month: 'long', year: 'numeric' })}
                    </p>
                  )}
                </div>
              </>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Tax Documents */}
      <Card>
        <CardHeader>
          <CardTitle>Tax Documents</CardTitle>
          <CardDescription>Download your tax-related documents</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-4 border rounded-lg flex items-center justify-between">
              <div className="flex items-center gap-3">
                <FileText className="h-8 w-8 text-muted-foreground" />
                <div>
                  <p className="font-medium">Form 16</p>
                  <p className="text-sm text-muted-foreground">FY 2024-25</p>
                </div>
              </div>
              <Button variant="outline" size="sm">
                <Download className="h-4 w-4" />
              </Button>
            </div>
            <div className="p-4 border rounded-lg flex items-center justify-between">
              <div className="flex items-center gap-3">
                <FileText className="h-8 w-8 text-muted-foreground" />
                <div>
                  <p className="font-medium">Form 12BB</p>
                  <p className="text-sm text-muted-foreground">Investment Declaration</p>
                </div>
              </div>
              <Button variant="outline" size="sm">
                <Download className="h-4 w-4" />
              </Button>
            </div>
            <div className="p-4 border rounded-lg flex items-center justify-between">
              <div className="flex items-center gap-3">
                <FileText className="h-8 w-8 text-muted-foreground" />
                <div>
                  <p className="font-medium">Salary Certificate</p>
                  <p className="text-sm text-muted-foreground">On request</p>
                </div>
              </div>
              <Button variant="outline" size="sm">Request</Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
