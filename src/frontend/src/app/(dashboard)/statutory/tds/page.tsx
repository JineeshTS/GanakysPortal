"use client";

import { useState, useEffect } from "react";
import {
  Receipt,
  Download,
  Upload,
  CheckCircle2,
  AlertCircle,
  Calculator,
  Users,
  Wallet,
  FileText,
  Info,
  Loader2,
} from "lucide-react";
import { PageHeader } from "@/components/layout";
import { Button, Card, Badge, Select } from "@/components/ui";
import { useApi } from "@/hooks";

interface TDSDeduction {
  employee_id: string;
  employee_code: string;
  employee_name: string;
  pan: string | null;
  annual_income: number;
  taxable_income: number;
  tax_regime: "new" | "old";
  annual_tax: number;
  monthly_tds: number;
  tds_paid_ytd: number;
  tds_balance: number;
}

interface TDSSummary {
  quarter: string;
  financial_year: string;
  tan: string | null;
  total_employees: number;
  total_annual_income: number;
  total_annual_tax: number;
  total_tds_deducted: number;
  total_tds_deposited: number;
  tds_payable: number;
  filing_status: string;
  due_date: string;
  deductions: TDSDeduction[];
}

const quarters = [
  { value: "Q1", label: "Q1 (Apr-Jun)" },
  { value: "Q2", label: "Q2 (Jul-Sep)" },
  { value: "Q3", label: "Q3 (Oct-Dec)" },
  { value: "Q4", label: "Q4 (Jan-Mar)" },
];

export default function TDSPage() {
  const [selectedQuarter, setSelectedQuarter] = useState("Q3");
  const [selectedYear, setSelectedYear] = useState("2025-26");
  const [isGenerated, setIsGenerated] = useState(false);

  const { data: tdsData, isLoading, error, get } = useApi<TDSSummary>();

  // Fetch TDS data when quarter/year changes
  useEffect(() => {
    get(`/statutory/tds/summary?quarter=${selectedQuarter}&financial_year=${selectedYear}`);
  }, [selectedQuarter, selectedYear, get]);

  const deductions = tdsData?.deductions || [];
  const totals = {
    annualIncome: tdsData?.total_annual_income || 0,
    annualTax: tdsData?.total_annual_tax || 0,
    monthlyTDS: 0,
    tdsPaid: tdsData?.total_tds_deducted || 0,
    tdsBalance: tdsData?.tds_payable || 0,
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat("en-IN", {
      style: "currency",
      currency: "INR",
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const handleGenerate = async () => {
    await get(`/statutory/tds/summary?quarter=${selectedQuarter}&financial_year=${selectedYear}`);
    setIsGenerated(true);
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="TDS Management"
        description="Tax Deducted at Source - 24Q Filing & Form 16 Generation"
        icon={<Receipt className="h-6 w-6" />}
        actions={
          <div className="flex gap-2">
            <Button variant="outline">
              <FileText className="h-4 w-4 mr-2" />
              Generate Form 16
            </Button>
            {isGenerated && (
              <Button>
                <Download className="h-4 w-4 mr-2" />
                Download 24Q
              </Button>
            )}
          </div>
        }
      />

      {/* Tax Regime Info */}
      <Card className="p-4 bg-info/5 border-info">
        <div className="flex items-start gap-3">
          <Info className="h-5 w-5 text-info mt-0.5" />
          <div className="text-sm">
            <p className="font-medium text-info">New Tax Regime (FY 2024-25)</p>
            <p className="text-muted-foreground mt-1">
              0-3L: 0% | 3-7L: 5% | 7-10L: 10% | 10-12L: 15% | 12-15L: 20% | 15L+: 30%
              <br />
              Standard Deduction: Rs.75,000 | Health & Education Cess: 4%
            </p>
          </div>
        </div>
      </Card>

      {/* Period Selection */}
      <Card className="p-4">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <label className="text-sm font-medium">Quarter:</label>
            <Select value={selectedQuarter} onValueChange={setSelectedQuarter}>
              {quarters.map((q) => (
                <option key={q.value} value={q.value}>
                  {q.label}
                </option>
              ))}
            </Select>
          </div>
          <div className="flex items-center gap-2">
            <label className="text-sm font-medium">Financial Year:</label>
            <Select value={selectedYear} onValueChange={setSelectedYear}>
              <option value="2025-26">2025-26</option>
              <option value="2024-25">2024-25</option>
              <option value="2023-24">2023-24</option>
            </Select>
          </div>
          <Button onClick={handleGenerate} disabled={isLoading}>
            {isLoading ? (
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
            ) : (
              <Calculator className="h-4 w-4 mr-2" />
            )}
            Generate 24Q
          </Button>
        </div>
      </Card>

      {/* Loading State */}
      {isLoading && (
        <Card className="p-8 flex items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <span className="ml-2">Loading TDS data...</span>
        </Card>
      )}

      {/* Error State */}
      {error && (
        <Card className="p-4 bg-destructive/5 border-destructive">
          <div className="flex items-center gap-2 text-destructive">
            <AlertCircle className="h-5 w-5" />
            <span>{error}</span>
          </div>
        </Card>
      )}

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <Card className="p-4">
          <div className="flex items-center gap-2 text-muted-foreground text-sm">
            <Users className="h-4 w-4" />
            Employees
          </div>
          <div className="text-2xl font-bold">{tdsData?.total_employees || 0}</div>
        </Card>
        <Card className="p-4">
          <div className="text-sm text-muted-foreground">Total Annual Income</div>
          <div className="text-2xl font-bold">{formatCurrency(totals.annualIncome)}</div>
        </Card>
        <Card className="p-4">
          <div className="text-sm text-muted-foreground">Total Annual Tax</div>
          <div className="text-2xl font-bold">{formatCurrency(totals.annualTax)}</div>
        </Card>
        <Card className="p-4">
          <div className="text-sm text-muted-foreground">TDS Deducted (YTD)</div>
          <div className="text-2xl font-bold text-success">{formatCurrency(totals.tdsPaid)}</div>
        </Card>
        <Card className="p-4 bg-warning/5 border-warning">
          <div className="flex items-center gap-2 text-warning text-sm">
            <Wallet className="h-4 w-4" />
            TDS Balance
          </div>
          <div className="text-2xl font-bold text-warning">{formatCurrency(totals.tdsBalance)}</div>
        </Card>
      </div>

      {/* Employee-wise TDS Table */}
      <Card>
        <div className="p-4 border-b">
          <h3 className="font-semibold">Employee-wise TDS Summary</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b bg-muted/50">
                <th className="px-4 py-3 text-left font-medium">Employee</th>
                <th className="px-4 py-3 text-left font-medium">PAN</th>
                <th className="px-4 py-3 text-center font-medium">Regime</th>
                <th className="px-4 py-3 text-right font-medium">Annual Income</th>
                <th className="px-4 py-3 text-right font-medium">Taxable Income</th>
                <th className="px-4 py-3 text-right font-medium">Annual Tax</th>
                <th className="px-4 py-3 text-right font-medium">Monthly TDS</th>
                <th className="px-4 py-3 text-right font-medium">TDS Paid</th>
                <th className="px-4 py-3 text-right font-medium">Balance</th>
              </tr>
            </thead>
            <tbody>
              {deductions.map((emp) => (
                <tr key={emp.employee_id} className="border-b">
                  <td className="px-4 py-3">
                    <div className="font-medium">{emp.employee_name}</div>
                    <div className="text-sm text-muted-foreground">{emp.employee_code}</div>
                  </td>
                  <td className="px-4 py-3 font-mono text-sm">{emp.pan || "-"}</td>
                  <td className="px-4 py-3 text-center">
                    <Badge variant={emp.tax_regime === "new" ? "success" : "secondary"}>
                      {emp.tax_regime.toUpperCase()}
                    </Badge>
                  </td>
                  <td className="px-4 py-3 text-right">{formatCurrency(emp.annual_income)}</td>
                  <td className="px-4 py-3 text-right">{formatCurrency(emp.taxable_income)}</td>
                  <td className="px-4 py-3 text-right">{formatCurrency(emp.annual_tax)}</td>
                  <td className="px-4 py-3 text-right">{formatCurrency(emp.monthly_tds)}</td>
                  <td className="px-4 py-3 text-right text-success">
                    {formatCurrency(emp.tds_paid_ytd)}
                  </td>
                  <td className="px-4 py-3 text-right font-semibold text-warning">
                    {formatCurrency(emp.tds_balance)}
                  </td>
                </tr>
              ))}
            </tbody>
            <tfoot>
              <tr className="bg-muted/50 font-semibold">
                <td colSpan={3} className="px-4 py-3">
                  Total ({deductions.length} employees)
                </td>
                <td className="px-4 py-3 text-right">{formatCurrency(totals.annualIncome)}</td>
                <td className="px-4 py-3 text-right">-</td>
                <td className="px-4 py-3 text-right">{formatCurrency(totals.annualTax)}</td>
                <td className="px-4 py-3 text-right">{formatCurrency(totals.monthlyTDS)}</td>
                <td className="px-4 py-3 text-right text-success">
                  {formatCurrency(totals.tdsPaid)}
                </td>
                <td className="px-4 py-3 text-right text-warning">
                  {formatCurrency(totals.tdsBalance)}
                </td>
              </tr>
            </tfoot>
          </table>
        </div>
      </Card>

      {/* Filing Schedule */}
      <Card className="p-4">
        <h3 className="font-semibold mb-3">TDS Filing Schedule (Form 24Q)</h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="p-4 bg-muted/50 rounded-lg">
            <div className="font-medium">Q1 (Apr-Jun)</div>
            <div className="text-sm text-muted-foreground">Due: 31st July</div>
          </div>
          <div className="p-4 bg-muted/50 rounded-lg">
            <div className="font-medium">Q2 (Jul-Sep)</div>
            <div className="text-sm text-muted-foreground">Due: 31st October</div>
          </div>
          <div className="p-4 bg-primary/10 rounded-lg border border-primary">
            <div className="font-medium text-primary">Q3 (Oct-Dec)</div>
            <div className="text-sm text-muted-foreground">Due: 31st January</div>
          </div>
          <div className="p-4 bg-muted/50 rounded-lg">
            <div className="font-medium">Q4 (Jan-Mar)</div>
            <div className="text-sm text-muted-foreground">Due: 31st May</div>
          </div>
        </div>
      </Card>

      {/* Success Message */}
      {isGenerated && (
        <Card className="p-4 bg-success/5 border-success">
          <div className="flex items-start gap-4">
            <CheckCircle2 className="h-6 w-6 text-success mt-0.5" />
            <div>
              <h3 className="font-semibold text-success">Form 24Q Generated Successfully</h3>
              <p className="text-sm text-muted-foreground mt-1">
                TDS return for {selectedQuarter} of FY {selectedYear} has been generated.
                Download and upload to TRACES portal.
              </p>
              <div className="mt-3 flex gap-4 text-sm">
                <div>
                  <span className="text-muted-foreground">File:</span>{" "}
                  <span className="font-mono">24Q_{selectedQuarter}_{selectedYear.replace("-", "_")}.txt</span>
                </div>
                <div>
                  <span className="text-muted-foreground">Due Date:</span>{" "}
                  <span className="font-medium">31st January 2026</span>
                </div>
              </div>
            </div>
          </div>
        </Card>
      )}
    </div>
  );
}
