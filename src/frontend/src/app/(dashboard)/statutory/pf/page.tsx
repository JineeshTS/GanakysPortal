"use client";

import { useState, useEffect } from "react";
import {
  FileText,
  Download,
  Upload,
  CheckCircle2,
  AlertCircle,
  Calculator,
  Users,
  Wallet,
  Loader2,
} from "lucide-react";
import { PageHeader } from "@/components/layout";
import { Button, Card, Badge, Select } from "@/components/ui";
import { useApi } from "@/hooks";

interface PFContribution {
  employee_id: string;
  employee_code: string;
  employee_name: string;
  uan: string | null;
  basic_wages: number;
  employee_pf: number;
  employer_pf: number;
  employer_eps: number;
  employer_edli: number;
  admin_charges: number;
  total_contribution: number;
}

interface PFSummary {
  month: string;
  year: number;
  establishment_id: string | null;
  total_employees: number;
  total_basic_wages: number;
  total_employee_pf: number;
  total_employer_pf: number;
  total_employer_eps: number;
  total_edli: number;
  total_admin_charges: number;
  grand_total: number;
  due_date: string;
  status: string;
  contributions: PFContribution[];
}

const months = [
  "January",
  "February",
  "March",
  "April",
  "May",
  "June",
  "July",
  "August",
  "September",
  "October",
  "November",
  "December",
];

export default function PFPage() {
  const [selectedMonth, setSelectedMonth] = useState(String(new Date().getMonth() + 1));
  const [selectedYear, setSelectedYear] = useState(String(new Date().getFullYear()));
  const [isGenerated, setIsGenerated] = useState(false);

  const { data: pfData, isLoading, error, get } = useApi<PFSummary>();

  // Fetch PF data when month/year changes
  useEffect(() => {
    get(`/statutory/pf/summary?month=${selectedMonth}&year=${selectedYear}`);
  }, [selectedMonth, selectedYear, get]);

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat("en-IN", {
      style: "currency",
      currency: "INR",
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const handleGenerate = async () => {
    await get(`/statutory/pf/summary?month=${selectedMonth}&year=${selectedYear}`);
    setIsGenerated(true);
  };

  const contributions = pfData?.contributions || [];
  const totals = {
    pfWage: pfData?.total_basic_wages || 0,
    employeePF: pfData?.total_employee_pf || 0,
    employerEPF: pfData?.total_employer_pf || 0,
    employerEPS: pfData?.total_employer_eps || 0,
    employerTotal: (pfData?.total_employer_pf || 0) + (pfData?.total_employer_eps || 0),
    totalPF: pfData?.grand_total || 0,
    adminCharges: pfData?.total_admin_charges || 0,
    edli: pfData?.total_edli || 0,
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="Provident Fund ECR"
        description="Generate and download PF Electronic Challan cum Return"
        icon={FileText}
        actions={
          <div className="flex gap-2">
            {isGenerated && (
              <>
                <Button variant="outline">
                  <Download className="h-4 w-4 mr-2" />
                  Download ECR
                </Button>
                <Button>
                  <Upload className="h-4 w-4 mr-2" />
                  Upload to EPFO
                </Button>
              </>
            )}
          </div>
        }
      />

      {/* Period Selection */}
      <Card className="p-4">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <label className="text-sm font-medium">Month:</label>
            <Select value={selectedMonth} onValueChange={setSelectedMonth}>
              {months.map((month, index) => (
                <option key={index} value={(index + 1).toString()}>
                  {month}
                </option>
              ))}
            </Select>
          </div>
          <div className="flex items-center gap-2">
            <label className="text-sm font-medium">Year:</label>
            <Select value={selectedYear} onValueChange={setSelectedYear}>
              <option value="2026">2026</option>
              <option value="2025">2025</option>
              <option value="2024">2024</option>
            </Select>
          </div>
          <Button onClick={handleGenerate}>
            <Calculator className="h-4 w-4 mr-2" />
            Generate ECR
          </Button>
        </div>
      </Card>

      {/* Loading State */}
      {isLoading && (
        <Card className="p-8 flex items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <span className="ml-2">Loading PF data...</span>
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
          <div className="text-2xl font-bold">{pfData?.total_employees || 0}</div>
        </Card>
        <Card className="p-4">
          <div className="text-sm text-muted-foreground">Total PF Wage</div>
          <div className="text-2xl font-bold">{formatCurrency(totals.pfWage)}</div>
        </Card>
        <Card className="p-4">
          <div className="text-sm text-muted-foreground">Employee PF (12%)</div>
          <div className="text-2xl font-bold text-primary">{formatCurrency(totals.employeePF)}</div>
        </Card>
        <Card className="p-4">
          <div className="text-sm text-muted-foreground">Employer Total (12%)</div>
          <div className="text-2xl font-bold text-primary">{formatCurrency(totals.employerTotal)}</div>
        </Card>
        <Card className="p-4 bg-primary/5 border-primary">
          <div className="flex items-center gap-2 text-primary text-sm">
            <Wallet className="h-4 w-4" />
            Total PF
          </div>
          <div className="text-2xl font-bold text-primary">{formatCurrency(totals.totalPF)}</div>
        </Card>
      </div>

      {/* Employer Contribution Breakdown */}
      <Card className="p-4">
        <h3 className="font-semibold mb-4">Employer Contribution Breakdown</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-4 bg-muted/50 rounded-lg">
            <div className="text-sm text-muted-foreground">EPF (3.67%)</div>
            <div className="text-xl font-bold">{formatCurrency(totals.employerEPF)}</div>
            <div className="text-xs text-muted-foreground mt-1">
              Goes to Employee PF Account
            </div>
          </div>
          <div className="p-4 bg-muted/50 rounded-lg">
            <div className="text-sm text-muted-foreground">EPS (8.33%)</div>
            <div className="text-xl font-bold">{formatCurrency(totals.employerEPS)}</div>
            <div className="text-xs text-muted-foreground mt-1">
              Capped at Rs.1,250 per employee
            </div>
          </div>
          <div className="p-4 bg-muted/50 rounded-lg">
            <div className="text-sm text-muted-foreground">Admin Charges (0.5%)</div>
            <div className="text-xl font-bold">{formatCurrency(totals.adminCharges)}</div>
            <div className="text-xs text-muted-foreground mt-1">
              EPFO Administrative Charges
            </div>
          </div>
        </div>
      </Card>

      {/* Employee-wise PF Table */}
      <Card>
        <div className="p-4 border-b">
          <h3 className="font-semibold">Employee-wise PF Contribution</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b bg-muted/50">
                <th className="px-4 py-3 text-left font-medium">Employee</th>
                <th className="px-4 py-3 text-left font-medium">UAN</th>
                <th className="px-4 py-3 text-right font-medium">PF Wage</th>
                <th className="px-4 py-3 text-right font-medium">Employee PF</th>
                <th className="px-4 py-3 text-right font-medium">Employer EPF</th>
                <th className="px-4 py-3 text-right font-medium">Employer EPS</th>
                <th className="px-4 py-3 text-right font-medium">Total</th>
                <th className="px-4 py-3 text-center font-medium">Status</th>
              </tr>
            </thead>
            <tbody>
              {contributions.map((emp) => (
                <tr key={emp.employee_id} className="border-b">
                  <td className="px-4 py-3">
                    <div className="font-medium">{emp.employee_name}</div>
                    <div className="text-sm text-muted-foreground">{emp.employee_code}</div>
                  </td>
                  <td className="px-4 py-3 font-mono text-sm">{emp.uan || "-"}</td>
                  <td className="px-4 py-3 text-right">{formatCurrency(emp.basic_wages)}</td>
                  <td className="px-4 py-3 text-right">{formatCurrency(emp.employee_pf)}</td>
                  <td className="px-4 py-3 text-right">{formatCurrency(emp.employer_pf)}</td>
                  <td className="px-4 py-3 text-right">
                    {formatCurrency(emp.employer_eps)}
                    {emp.basic_wages > 15000 && (
                      <span className="text-xs text-warning ml-1">(capped)</span>
                    )}
                  </td>
                  <td className="px-4 py-3 text-right font-semibold">
                    {formatCurrency(emp.total_contribution)}
                  </td>
                  <td className="px-4 py-3 text-center">
                    {emp.uan ? (
                      <Badge variant="success">
                        <CheckCircle2 className="h-3 w-3 mr-1" />
                        Active
                      </Badge>
                    ) : (
                      <Badge variant="warning">
                        <AlertCircle className="h-3 w-3 mr-1" />
                        No UAN
                      </Badge>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
            <tfoot>
              <tr className="bg-muted/50 font-semibold">
                <td colSpan={2} className="px-4 py-3">
                  Total ({contributions.length} employees)
                </td>
                <td className="px-4 py-3 text-right">{formatCurrency(totals.pfWage)}</td>
                <td className="px-4 py-3 text-right">{formatCurrency(totals.employeePF)}</td>
                <td className="px-4 py-3 text-right">{formatCurrency(totals.employerEPF)}</td>
                <td className="px-4 py-3 text-right">{formatCurrency(totals.employerEPS)}</td>
                <td className="px-4 py-3 text-right text-primary">
                  {formatCurrency(totals.totalPF)}
                </td>
                <td className="px-4 py-3 text-center">-</td>
              </tr>
            </tfoot>
          </table>
        </div>
      </Card>

      {/* ECR File Info */}
      {isGenerated && (
        <Card className="p-4 bg-success/5 border-success">
          <div className="flex items-start gap-4">
            <CheckCircle2 className="h-6 w-6 text-success mt-0.5" />
            <div>
              <h3 className="font-semibold text-success">ECR Generated Successfully</h3>
              <p className="text-sm text-muted-foreground mt-1">
                ECR file for {months[parseInt(selectedMonth) - 1]} {selectedYear} has been
                generated. You can download and upload it to the EPFO Unified Portal.
              </p>
              <div className="mt-3 flex gap-4 text-sm">
                <div>
                  <span className="text-muted-foreground">File:</span>{" "}
                  <span className="font-mono">ECR_01_{selectedMonth}_{selectedYear}.txt</span>
                </div>
                <div>
                  <span className="text-muted-foreground">Due Date:</span>{" "}
                  <span className="font-medium">15th Feb 2026</span>
                </div>
              </div>
            </div>
          </div>
        </Card>
      )}
    </div>
  );
}
