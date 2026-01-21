'use client'

import * as React from 'react'
import { PageHeader } from '@/components/layout/page-header'
import { DataTable, Column } from '@/components/layout/data-table'
import { MonthYearPicker, DateRangePicker } from '@/components/forms/date-picker'
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { formatCurrency, getMonthName, formatDate, getFinancialYear } from '@/lib/format'
import {
  Download,
  FileSpreadsheet,
  FileText,
  Printer,
  Building,
  CreditCard,
  Shield,
  Users,
  Calendar,
  TrendingUp,
  Filter,
  Loader2
} from 'lucide-react'

// ============================================================================
// Types
// ============================================================================

interface ReportType {
  id: string
  name: string
  description: string
  icon: React.ElementType
  format: string[]
  category: 'payroll' | 'statutory' | 'summary'
}

interface PayrollRegisterEntry {
  employee_code: string
  employee_name: string
  department: string
  basic: number
  hra: number
  special_allowance: number
  other_earnings: number
  gross: number
  pf: number
  esi: number
  pt: number
  tds: number
  total_deductions: number
  net_salary: number
}

interface BankStatementEntry {
  employee_code: string
  employee_name: string
  bank_name: string
  account_number: string
  ifsc_code: string
  net_salary: number
}

interface PFECREntry {
  uan: string
  employee_name: string
  pf_wages: number
  eps_wages: number
  edli_wages: number
  epf_contribution: number
  eps_contribution: number
  epf_diff: number
  ncp_days: number
}

// ============================================================================
// Mock Data
// ============================================================================

const reportTypes: ReportType[] = [
  {
    id: 'payroll_register',
    name: 'Payroll Register',
    description: 'Complete payroll summary with all components',
    icon: FileSpreadsheet,
    format: ['xlsx', 'pdf'],
    category: 'payroll'
  },
  {
    id: 'bank_statement',
    name: 'Bank Statement',
    description: 'NEFT/RTGS payment file for salary credit',
    icon: CreditCard,
    format: ['xlsx', 'txt', 'csv'],
    category: 'payroll'
  },
  {
    id: 'pf_ecr',
    name: 'PF ECR Format',
    description: 'EPFO Electronic Challan cum Return format',
    icon: Shield,
    format: ['txt', 'xlsx'],
    category: 'statutory'
  },
  {
    id: 'esi_monthly',
    name: 'ESI Monthly',
    description: 'ESIC monthly contribution statement',
    icon: Shield,
    format: ['xlsx', 'pdf'],
    category: 'statutory'
  },
  {
    id: 'pt_monthly',
    name: 'PT Monthly',
    description: 'Professional Tax state-wise report',
    icon: Building,
    format: ['xlsx', 'pdf'],
    category: 'statutory'
  },
  {
    id: 'tds_summary',
    name: 'TDS Summary',
    description: 'Tax Deducted at Source summary',
    icon: FileText,
    format: ['xlsx', 'pdf'],
    category: 'statutory'
  },
  {
    id: 'department_summary',
    name: 'Department-wise Summary',
    description: 'Salary breakdown by department',
    icon: Users,
    format: ['xlsx', 'pdf'],
    category: 'summary'
  },
  {
    id: 'ytd_summary',
    name: 'YTD Summary',
    description: 'Year-to-date salary and deductions',
    icon: TrendingUp,
    format: ['xlsx', 'pdf'],
    category: 'summary'
  }
]

const mockPayrollRegister: PayrollRegisterEntry[] = [
  {
    employee_code: 'EMP001',
    employee_name: 'Rahul Kumar',
    department: 'Engineering',
    basic: 40000,
    hra: 20000,
    special_allowance: 15000,
    other_earnings: 5000,
    gross: 80000,
    pf: 4800,
    esi: 0,
    pt: 200,
    tds: 8500,
    total_deductions: 13500,
    net_salary: 66500
  },
  {
    employee_code: 'EMP002',
    employee_name: 'Priya Sharma',
    department: 'Engineering',
    basic: 50000,
    hra: 25000,
    special_allowance: 20000,
    other_earnings: 5000,
    gross: 100000,
    pf: 6000,
    esi: 0,
    pt: 200,
    tds: 12500,
    total_deductions: 18700,
    net_salary: 81300
  },
  {
    employee_code: 'EMP003',
    employee_name: 'Amit Patel',
    department: 'Sales',
    basic: 25000,
    hra: 12500,
    special_allowance: 7500,
    other_earnings: 5000,
    gross: 50000,
    pf: 3000,
    esi: 0,
    pt: 200,
    tds: 3500,
    total_deductions: 6700,
    net_salary: 43300
  },
  {
    employee_code: 'EMP004',
    employee_name: 'Sneha Reddy',
    department: 'HR',
    basic: 35000,
    hra: 17500,
    special_allowance: 12500,
    other_earnings: 5000,
    gross: 70000,
    pf: 4200,
    esi: 0,
    pt: 200,
    tds: 6500,
    total_deductions: 10900,
    net_salary: 59100
  },
  {
    employee_code: 'EMP005',
    employee_name: 'Vikram Singh',
    department: 'Finance',
    basic: 30000,
    hra: 15000,
    special_allowance: 10000,
    other_earnings: 5000,
    gross: 60000,
    pf: 3600,
    esi: 0,
    pt: 200,
    tds: 5000,
    total_deductions: 8800,
    net_salary: 51200
  }
]

const mockBankStatement: BankStatementEntry[] = [
  {
    employee_code: 'EMP001',
    employee_name: 'Rahul Kumar',
    bank_name: 'HDFC Bank',
    account_number: 'XXXX1234',
    ifsc_code: 'HDFC0001234',
    net_salary: 66500
  },
  {
    employee_code: 'EMP002',
    employee_name: 'Priya Sharma',
    bank_name: 'ICICI Bank',
    account_number: 'XXXX5678',
    ifsc_code: 'ICIC0005678',
    net_salary: 81300
  },
  {
    employee_code: 'EMP003',
    employee_name: 'Amit Patel',
    bank_name: 'SBI',
    account_number: 'XXXX9012',
    ifsc_code: 'SBIN0009012',
    net_salary: 43300
  },
  {
    employee_code: 'EMP004',
    employee_name: 'Sneha Reddy',
    bank_name: 'Axis Bank',
    account_number: 'XXXX3456',
    ifsc_code: 'UTIB0003456',
    net_salary: 59100
  },
  {
    employee_code: 'EMP005',
    employee_name: 'Vikram Singh',
    bank_name: 'HDFC Bank',
    account_number: 'XXXX7890',
    ifsc_code: 'HDFC0007890',
    net_salary: 51200
  }
]

const mockPFECR: PFECREntry[] = [
  {
    uan: '100123456789',
    employee_name: 'Rahul Kumar',
    pf_wages: 40000,
    eps_wages: 15000,
    edli_wages: 15000,
    epf_contribution: 4800,
    eps_contribution: 1250,
    epf_diff: 3550,
    ncp_days: 1
  },
  {
    uan: '100234567890',
    employee_name: 'Priya Sharma',
    pf_wages: 50000,
    eps_wages: 15000,
    edli_wages: 15000,
    epf_contribution: 6000,
    eps_contribution: 1250,
    epf_diff: 4750,
    ncp_days: 0
  },
  {
    uan: '100345678901',
    employee_name: 'Amit Patel',
    pf_wages: 25000,
    eps_wages: 15000,
    edli_wages: 15000,
    epf_contribution: 3000,
    eps_contribution: 1250,
    epf_diff: 1750,
    ncp_days: 2
  },
  {
    uan: '100456789012',
    employee_name: 'Sneha Reddy',
    pf_wages: 35000,
    eps_wages: 15000,
    edli_wages: 15000,
    epf_contribution: 4200,
    eps_contribution: 1250,
    epf_diff: 2950,
    ncp_days: 0
  },
  {
    uan: '100567890123',
    employee_name: 'Vikram Singh',
    pf_wages: 30000,
    eps_wages: 15000,
    edli_wages: 15000,
    epf_contribution: 3600,
    eps_contribution: 1250,
    epf_diff: 2350,
    ncp_days: 1
  }
]

// Department summary data
const departmentSummary = [
  { department: 'Engineering', employees: 25, gross: 1450000, deductions: 348000, net: 1102000 },
  { department: 'Sales', employees: 8, gross: 420000, deductions: 84000, net: 336000 },
  { department: 'HR', employees: 5, gross: 280000, deductions: 56000, net: 224000 },
  { department: 'Finance', employees: 4, gross: 240000, deductions: 48000, net: 192000 },
  { department: 'Marketing', employees: 5, gross: 320000, deductions: 64000, net: 256000 }
]

// ============================================================================
// Component
// ============================================================================

export default function PayrollReportsPage() {
  const currentDate = new Date()
  const [selectedMonth, setSelectedMonth] = React.useState(currentDate.getMonth() + 1)
  const [selectedYear, setSelectedYear] = React.useState(currentDate.getFullYear())
  const [selectedReport, setSelectedReport] = React.useState<string>('payroll_register')
  const [isGenerating, setIsGenerating] = React.useState(false)
  const [activeTab, setActiveTab] = React.useState('payroll')

  const financialYear = getFinancialYear(new Date(selectedYear, selectedMonth - 1))

  // Handle report generation
  const handleGenerateReport = async (format: string) => {
    setIsGenerating(true)
    // Simulate report generation
    await new Promise(resolve => setTimeout(resolve, 2000))
    setIsGenerating(false)
  }

  // Payroll Register columns
  const payrollRegisterColumns: Column<PayrollRegisterEntry>[] = [
    { key: 'employee_code', header: 'Code', accessor: 'employee_code' },
    { key: 'employee_name', header: 'Name', accessor: 'employee_name' },
    { key: 'department', header: 'Dept', accessor: 'department' },
    { key: 'basic', header: 'Basic', className: 'text-right', headerClassName: 'text-right', accessor: (row) => formatCurrency(row.basic) },
    { key: 'hra', header: 'HRA', className: 'text-right', headerClassName: 'text-right', accessor: (row) => formatCurrency(row.hra) },
    { key: 'special', header: 'Special', className: 'text-right', headerClassName: 'text-right', accessor: (row) => formatCurrency(row.special_allowance) },
    { key: 'gross', header: 'Gross', className: 'text-right font-medium', headerClassName: 'text-right', accessor: (row) => formatCurrency(row.gross) },
    { key: 'pf', header: 'PF', className: 'text-right', headerClassName: 'text-right', accessor: (row) => formatCurrency(row.pf) },
    { key: 'tds', header: 'TDS', className: 'text-right', headerClassName: 'text-right', accessor: (row) => formatCurrency(row.tds) },
    { key: 'net', header: 'Net Pay', className: 'text-right font-medium text-green-600', headerClassName: 'text-right', accessor: (row) => formatCurrency(row.net_salary) }
  ]

  // Bank Statement columns
  const bankStatementColumns: Column<BankStatementEntry>[] = [
    { key: 'employee_code', header: 'Code', accessor: 'employee_code' },
    { key: 'employee_name', header: 'Name', accessor: 'employee_name' },
    { key: 'bank_name', header: 'Bank', accessor: 'bank_name' },
    { key: 'account_number', header: 'Account No.', accessor: 'account_number' },
    { key: 'ifsc_code', header: 'IFSC', accessor: 'ifsc_code' },
    { key: 'net_salary', header: 'Amount', className: 'text-right font-medium', headerClassName: 'text-right', accessor: (row) => formatCurrency(row.net_salary) }
  ]

  // PF ECR columns
  const pfEcrColumns: Column<PFECREntry>[] = [
    { key: 'uan', header: 'UAN', accessor: 'uan' },
    { key: 'employee_name', header: 'Name', accessor: 'employee_name' },
    { key: 'pf_wages', header: 'PF Wages', className: 'text-right', headerClassName: 'text-right', accessor: (row) => formatCurrency(row.pf_wages) },
    { key: 'eps_wages', header: 'EPS Wages', className: 'text-right', headerClassName: 'text-right', accessor: (row) => formatCurrency(row.eps_wages) },
    { key: 'epf', header: 'EPF (12%)', className: 'text-right', headerClassName: 'text-right', accessor: (row) => formatCurrency(row.epf_contribution) },
    { key: 'eps', header: 'EPS (8.33%)', className: 'text-right', headerClassName: 'text-right', accessor: (row) => formatCurrency(row.eps_contribution) },
    { key: 'epf_diff', header: 'EPF Diff', className: 'text-right', headerClassName: 'text-right', accessor: (row) => formatCurrency(row.epf_diff) },
    { key: 'ncp_days', header: 'NCP Days', className: 'text-center', headerClassName: 'text-center', accessor: 'ncp_days' }
  ]

  const currentReport = reportTypes.find(r => r.id === selectedReport)

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <PageHeader
        title="Payroll Reports"
        description="Generate and download payroll and statutory reports"
        breadcrumbs={[
          { label: 'Dashboard', href: '/dashboard' },
          { label: 'Payroll', href: '/payroll' },
          { label: 'Reports' }
        ]}
      />

      {/* Period Selection */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
            <MonthYearPicker
              label="Report Period"
              name="report-period"
              month={selectedMonth}
              year={selectedYear}
              onMonthChange={setSelectedMonth}
              onYearChange={setSelectedYear}
            />
            <div className="flex items-center gap-4">
              <div className="text-right">
                <p className="text-sm text-muted-foreground">Financial Year</p>
                <p className="font-semibold">{financialYear}</p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Report Categories */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="payroll">Payroll Reports</TabsTrigger>
          <TabsTrigger value="statutory">Statutory Reports</TabsTrigger>
          <TabsTrigger value="summary">Summary Reports</TabsTrigger>
        </TabsList>

        <TabsContent value="payroll" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {reportTypes.filter(r => r.category === 'payroll').map(report => (
              <Card
                key={report.id}
                className={`cursor-pointer transition-all ${selectedReport === report.id ? 'ring-2 ring-primary' : ''}`}
                onClick={() => setSelectedReport(report.id)}
              >
                <CardHeader className="pb-2">
                  <div className="flex items-center gap-3">
                    <div className="h-10 w-10 rounded-lg bg-primary/10 flex items-center justify-center">
                      <report.icon className="h-5 w-5 text-primary" />
                    </div>
                    <div>
                      <CardTitle className="text-base">{report.name}</CardTitle>
                      <CardDescription className="text-xs">{report.description}</CardDescription>
                    </div>
                  </div>
                </CardHeader>
                <CardFooter className="pt-2">
                  <div className="flex items-center gap-2">
                    {report.format.map(fmt => (
                      <Badge key={fmt} variant="secondary" className="text-xs uppercase">
                        {fmt}
                      </Badge>
                    ))}
                  </div>
                </CardFooter>
              </Card>
            ))}
          </div>

          {/* Payroll Register Preview */}
          {selectedReport === 'payroll_register' && (
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>Payroll Register - {getMonthName(selectedMonth)} {selectedYear}</CardTitle>
                    <CardDescription>Complete payroll summary for all employees</CardDescription>
                  </div>
                  <div className="flex items-center gap-2">
                    <Button variant="outline" size="sm" onClick={() => handleGenerateReport('xlsx')} disabled={isGenerating}>
                      {isGenerating ? <Loader2 className="h-4 w-4 animate-spin" /> : <Download className="h-4 w-4 mr-2" />}
                      Excel
                    </Button>
                    <Button variant="outline" size="sm" onClick={() => handleGenerateReport('pdf')} disabled={isGenerating}>
                      <FileText className="h-4 w-4 mr-2" />
                      PDF
                    </Button>
                    <Button variant="outline" size="sm">
                      <Printer className="h-4 w-4 mr-2" />
                      Print
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <DataTable
                  data={mockPayrollRegister}
                  columns={payrollRegisterColumns}
                  keyExtractor={(row) => row.employee_code}
                />
                <div className="mt-4 flex justify-between pt-4 border-t">
                  <span className="font-semibold">Total ({mockPayrollRegister.length} employees)</span>
                  <span className="font-bold text-green-600">
                    {formatCurrency(mockPayrollRegister.reduce((sum, r) => sum + r.net_salary, 0))}
                  </span>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Bank Statement Preview */}
          {selectedReport === 'bank_statement' && (
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>Bank Statement - {getMonthName(selectedMonth)} {selectedYear}</CardTitle>
                    <CardDescription>NEFT/RTGS payment file for salary disbursement</CardDescription>
                  </div>
                  <div className="flex items-center gap-2">
                    <Button variant="outline" size="sm" onClick={() => handleGenerateReport('xlsx')} disabled={isGenerating}>
                      <Download className="h-4 w-4 mr-2" />
                      Excel
                    </Button>
                    <Button variant="outline" size="sm" onClick={() => handleGenerateReport('txt')} disabled={isGenerating}>
                      <FileText className="h-4 w-4 mr-2" />
                      Bank Format
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <DataTable
                  data={mockBankStatement}
                  columns={bankStatementColumns}
                  keyExtractor={(row) => row.employee_code}
                />
                <div className="mt-4 flex justify-between pt-4 border-t">
                  <span className="font-semibold">Total Transfer Amount</span>
                  <span className="font-bold text-green-600">
                    {formatCurrency(mockBankStatement.reduce((sum, r) => sum + r.net_salary, 0))}
                  </span>
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="statutory" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {reportTypes.filter(r => r.category === 'statutory').map(report => (
              <Card
                key={report.id}
                className={`cursor-pointer transition-all ${selectedReport === report.id ? 'ring-2 ring-primary' : ''}`}
                onClick={() => setSelectedReport(report.id)}
              >
                <CardHeader className="pb-2">
                  <div className="flex items-center gap-3">
                    <div className="h-10 w-10 rounded-lg bg-blue-100 flex items-center justify-center">
                      <report.icon className="h-5 w-5 text-blue-600" />
                    </div>
                    <div>
                      <CardTitle className="text-base">{report.name}</CardTitle>
                      <CardDescription className="text-xs">{report.description}</CardDescription>
                    </div>
                  </div>
                </CardHeader>
                <CardFooter className="pt-2">
                  <div className="flex items-center gap-2">
                    {report.format.map(fmt => (
                      <Badge key={fmt} variant="secondary" className="text-xs uppercase">
                        {fmt}
                      </Badge>
                    ))}
                  </div>
                </CardFooter>
              </Card>
            ))}
          </div>

          {/* PF ECR Preview */}
          {selectedReport === 'pf_ecr' && (
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>PF ECR Format - {getMonthName(selectedMonth)} {selectedYear}</CardTitle>
                    <CardDescription>EPFO Electronic Challan cum Return</CardDescription>
                  </div>
                  <div className="flex items-center gap-2">
                    <Button variant="outline" size="sm" onClick={() => handleGenerateReport('txt')} disabled={isGenerating}>
                      <Download className="h-4 w-4 mr-2" />
                      ECR Text
                    </Button>
                    <Button variant="outline" size="sm" onClick={() => handleGenerateReport('xlsx')} disabled={isGenerating}>
                      <FileSpreadsheet className="h-4 w-4 mr-2" />
                      Excel
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <DataTable
                  data={mockPFECR}
                  columns={pfEcrColumns}
                  keyExtractor={(row) => row.uan}
                />
                <div className="mt-4 grid grid-cols-3 gap-4 pt-4 border-t">
                  <div>
                    <p className="text-sm text-muted-foreground">Total EPF Contribution</p>
                    <p className="font-bold">{formatCurrency(mockPFECR.reduce((sum, r) => sum + r.epf_contribution, 0))}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Total EPS Contribution</p>
                    <p className="font-bold">{formatCurrency(mockPFECR.reduce((sum, r) => sum + r.eps_contribution, 0))}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground">Total PF Amount</p>
                    <p className="font-bold text-blue-600">{formatCurrency(mockPFECR.reduce((sum, r) => sum + r.epf_contribution + r.eps_contribution, 0))}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* ESI Monthly Report */}
          {selectedReport === 'esi_monthly' && (
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>ESI Monthly Contribution - {getMonthName(selectedMonth)} {selectedYear}</CardTitle>
                    <CardDescription>ESIC Monthly Statement</CardDescription>
                  </div>
                  <div className="flex items-center gap-2">
                    <Button variant="outline" size="sm" onClick={() => handleGenerateReport('xlsx')} disabled={isGenerating}>
                      <Download className="h-4 w-4 mr-2" />
                      Download
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="p-8 text-center text-muted-foreground">
                  <Shield className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>No ESI eligible employees for this period</p>
                  <p className="text-sm mt-2">ESI is applicable for employees with gross salary &lt;= Rs.21,000</p>
                </div>
              </CardContent>
            </Card>
          )}

          {/* PT Monthly Report */}
          {selectedReport === 'pt_monthly' && (
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>Professional Tax - {getMonthName(selectedMonth)} {selectedYear}</CardTitle>
                    <CardDescription>State-wise PT deduction report</CardDescription>
                  </div>
                  <div className="flex items-center gap-2">
                    <Button variant="outline" size="sm" onClick={() => handleGenerateReport('xlsx')} disabled={isGenerating}>
                      <Download className="h-4 w-4 mr-2" />
                      Download
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="p-4 bg-muted/50 rounded-lg">
                    <div className="flex justify-between items-center">
                      <div>
                        <p className="font-medium">Karnataka</p>
                        <p className="text-sm text-muted-foreground">47 employees</p>
                      </div>
                      <div className="text-right">
                        <p className="font-bold">{formatCurrency(9400)}</p>
                        <p className="text-xs text-muted-foreground">Rs.200 per employee</p>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* TDS Summary Report */}
          {selectedReport === 'tds_summary' && (
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>TDS Summary - {getMonthName(selectedMonth)} {selectedYear}</CardTitle>
                    <CardDescription>Tax Deducted at Source</CardDescription>
                  </div>
                  <div className="flex items-center gap-2">
                    <Button variant="outline" size="sm" onClick={() => handleGenerateReport('xlsx')} disabled={isGenerating}>
                      <Download className="h-4 w-4 mr-2" />
                      Download
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="p-4 bg-blue-50 rounded-lg">
                    <p className="text-sm text-blue-700">Old Regime</p>
                    <p className="text-2xl font-bold text-blue-800">{formatCurrency(58200)}</p>
                    <p className="text-xs text-blue-600 mt-1">18 employees</p>
                  </div>
                  <div className="p-4 bg-purple-50 rounded-lg">
                    <p className="text-sm text-purple-700">New Regime</p>
                    <p className="text-2xl font-bold text-purple-800">{formatCurrency(98000)}</p>
                    <p className="text-xs text-purple-600 mt-1">29 employees</p>
                  </div>
                </div>
                <div className="mt-4 p-4 bg-orange-50 rounded-lg border border-orange-200">
                  <div className="flex justify-between items-center">
                    <div>
                      <p className="font-medium text-orange-800">Total TDS Liability</p>
                      <p className="text-xs text-orange-600">Due by 7th of next month</p>
                    </div>
                    <p className="text-2xl font-bold text-orange-800">{formatCurrency(156200)}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="summary" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {reportTypes.filter(r => r.category === 'summary').map(report => (
              <Card
                key={report.id}
                className={`cursor-pointer transition-all ${selectedReport === report.id ? 'ring-2 ring-primary' : ''}`}
                onClick={() => setSelectedReport(report.id)}
              >
                <CardHeader className="pb-2">
                  <div className="flex items-center gap-3">
                    <div className="h-10 w-10 rounded-lg bg-green-100 flex items-center justify-center">
                      <report.icon className="h-5 w-5 text-green-600" />
                    </div>
                    <div>
                      <CardTitle className="text-base">{report.name}</CardTitle>
                      <CardDescription className="text-xs">{report.description}</CardDescription>
                    </div>
                  </div>
                </CardHeader>
                <CardFooter className="pt-2">
                  <div className="flex items-center gap-2">
                    {report.format.map(fmt => (
                      <Badge key={fmt} variant="secondary" className="text-xs uppercase">
                        {fmt}
                      </Badge>
                    ))}
                  </div>
                </CardFooter>
              </Card>
            ))}
          </div>

          {/* Department Summary */}
          {selectedReport === 'department_summary' && (
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>Department-wise Summary - {getMonthName(selectedMonth)} {selectedYear}</CardTitle>
                    <CardDescription>Salary distribution by department</CardDescription>
                  </div>
                  <div className="flex items-center gap-2">
                    <Button variant="outline" size="sm" onClick={() => handleGenerateReport('xlsx')} disabled={isGenerating}>
                      <Download className="h-4 w-4 mr-2" />
                      Excel
                    </Button>
                    <Button variant="outline" size="sm" onClick={() => handleGenerateReport('pdf')} disabled={isGenerating}>
                      <FileText className="h-4 w-4 mr-2" />
                      PDF
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {departmentSummary.map((dept, index) => (
                    <div key={index} className="p-4 bg-muted/50 rounded-lg">
                      <div className="flex items-center justify-between mb-2">
                        <div>
                          <p className="font-medium">{dept.department}</p>
                          <p className="text-sm text-muted-foreground">{dept.employees} employees</p>
                        </div>
                        <p className="text-xl font-bold text-green-600">{formatCurrency(dept.net)}</p>
                      </div>
                      <div className="grid grid-cols-3 gap-4 text-sm">
                        <div>
                          <span className="text-muted-foreground">Gross: </span>
                          <span className="font-medium">{formatCurrency(dept.gross)}</span>
                        </div>
                        <div>
                          <span className="text-muted-foreground">Deductions: </span>
                          <span className="font-medium text-red-600">-{formatCurrency(dept.deductions)}</span>
                        </div>
                        <div>
                          <span className="text-muted-foreground">Net: </span>
                          <span className="font-medium text-green-600">{formatCurrency(dept.net)}</span>
                        </div>
                      </div>
                    </div>
                  ))}
                  <div className="p-4 bg-primary/10 rounded-lg border-2 border-primary/20">
                    <div className="flex justify-between items-center">
                      <div>
                        <p className="font-semibold">Total</p>
                        <p className="text-sm text-muted-foreground">
                          {departmentSummary.reduce((sum, d) => sum + d.employees, 0)} employees
                        </p>
                      </div>
                      <p className="text-2xl font-bold text-primary">
                        {formatCurrency(departmentSummary.reduce((sum, d) => sum + d.net, 0))}
                      </p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* YTD Summary */}
          {selectedReport === 'ytd_summary' && (
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>Year-to-Date Summary - {financialYear}</CardTitle>
                    <CardDescription>April {selectedYear > 3 ? selectedYear : selectedYear - 1} to {getMonthName(selectedMonth)} {selectedYear}</CardDescription>
                  </div>
                  <div className="flex items-center gap-2">
                    <Button variant="outline" size="sm" onClick={() => handleGenerateReport('xlsx')} disabled={isGenerating}>
                      <Download className="h-4 w-4 mr-2" />
                      Excel
                    </Button>
                    <Button variant="outline" size="sm" onClick={() => handleGenerateReport('pdf')} disabled={isGenerating}>
                      <FileText className="h-4 w-4 mr-2" />
                      PDF
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="p-4 bg-muted/50 rounded-lg">
                    <p className="text-sm text-muted-foreground">YTD Gross Salary</p>
                    <p className="text-xl font-bold">{formatCurrency(18950000)}</p>
                  </div>
                  <div className="p-4 bg-muted/50 rounded-lg">
                    <p className="text-sm text-muted-foreground">YTD PF Contribution</p>
                    <p className="text-xl font-bold text-blue-600">{formatCurrency(4548000)}</p>
                  </div>
                  <div className="p-4 bg-muted/50 rounded-lg">
                    <p className="text-sm text-muted-foreground">YTD TDS Deducted</p>
                    <p className="text-xl font-bold text-orange-600">{formatCurrency(1562000)}</p>
                  </div>
                  <div className="p-4 bg-muted/50 rounded-lg">
                    <p className="text-sm text-muted-foreground">YTD Net Paid</p>
                    <p className="text-xl font-bold text-green-600">{formatCurrency(14262000)}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>
      </Tabs>
    </div>
  )
}
