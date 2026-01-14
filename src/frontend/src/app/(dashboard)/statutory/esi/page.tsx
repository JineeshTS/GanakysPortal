"use client";

import { useState, useEffect } from "react";
import {
  Heart,
  Download,
  Upload,
  CheckCircle2,
  AlertCircle,
  Calculator,
  Users,
  Wallet,
  Info,
  Loader2,
} from "lucide-react";
import { PageHeader } from "@/components/layout";
import { Button, Card, Badge, Select } from "@/components/ui";
import { useApi } from "@/hooks";

interface ESIContribution {
  employee_id: string;
  employee_code: string;
  employee_name: string;
  ip_number: string | null;
  gross_wages: number;
  esi_applicable: boolean;
  employee_esi: number;
  employer_esi: number;
  total_esi: number;
  present_days: number;
}

interface ESISummary {
  month: string;
  year: number;
  establishment_code: string | null;
  total_employees: number;
  esi_applicable_count: number;
  total_gross_wages: number;
  total_employee_esi: number;
  total_employer_esi: number;
  grand_total: number;
  due_date: string;
  status: string;
  contributions: ESIContribution[];
}

const months = [
  "January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December",
];

export default function ESIPage() {
  const [selectedMonth, setSelectedMonth] = useState(String(new Date().getMonth() + 1));
  const [selectedYear, setSelectedYear] = useState(String(new Date().getFullYear()));
  const [isGenerated, setIsGenerated] = useState(false);

  const { data: esiData, isLoading, error, get } = useApi<ESISummary>();

  // Fetch ESI data when month/year changes
  useEffect(() => {
    get(`/statutory/esi/summary?month=${selectedMonth}&year=${selectedYear}`);
  }, [selectedMonth, selectedYear, get]);

  const contributions = esiData?.contributions || [];
  const applicableEmployees = contributions.filter((emp) => emp.esi_applicable);
  const totals = {
    grossSalary: esiData?.total_gross_wages || 0,
    employeeESI: esiData?.total_employee_esi || 0,
    employerESI: esiData?.total_employer_esi || 0,
    totalESI: esiData?.grand_total || 0,
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat("en-IN", {
      style: "currency",
      currency: "INR",
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const handleGenerate = async () => {
    await get(`/statutory/esi/summary?month=${selectedMonth}&year=${selectedYear}`);
    setIsGenerated(true);
  };

  return (
    <div className="space-y-6">
      <PageHeader
        title="ESI Contribution"
        description="Employee State Insurance contribution and return filing"
        icon={<Heart className="h-6 w-6" />}
        actions={
          <div className="flex gap-2">
            {isGenerated && (
              <>
                <Button variant="outline">
                  <Download className="h-4 w-4 mr-2" />
                  Download Return
                </Button>
                <Button>
                  <Upload className="h-4 w-4 mr-2" />
                  Upload to ESIC
                </Button>
              </>
            )}
          </div>
        }
      />

      {/* ESI Info Banner */}
      <Card className="p-4 bg-info/5 border-info">
        <div className="flex items-start gap-3">
          <Info className="h-5 w-5 text-info mt-0.5" />
          <div className="text-sm">
            <p className="font-medium text-info">ESI Applicability</p>
            <p className="text-muted-foreground mt-1">
              ESI is applicable for employees with gross salary ≤ Rs.21,000/month.
              <br />
              <span className="font-medium">Employee: 0.75%</span> |{" "}
              <span className="font-medium">Employer: 3.25%</span> |{" "}
              <span className="font-medium">Total: 4%</span>
            </p>
          </div>
        </div>
      </Card>

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
          <Button onClick={handleGenerate} disabled={isLoading}>
            {isLoading ? (
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
            ) : (
              <Calculator className="h-4 w-4 mr-2" />
            )}
            Generate ESI Return
          </Button>
        </div>
      </Card>

      {/* Loading State */}
      {isLoading && (
        <Card className="p-8 flex items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <span className="ml-2">Loading ESI data...</span>
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
            Total Employees
          </div>
          <div className="text-2xl font-bold">{esiData?.total_employees || 0}</div>
        </Card>
        <Card className="p-4">
          <div className="text-sm text-muted-foreground">ESI Applicable</div>
          <div className="text-2xl font-bold text-primary">{esiData?.esi_applicable_count || 0}</div>
        </Card>
        <Card className="p-4">
          <div className="text-sm text-muted-foreground">Employee ESI (0.75%)</div>
          <div className="text-2xl font-bold">{formatCurrency(totals.employeeESI)}</div>
        </Card>
        <Card className="p-4">
          <div className="text-sm text-muted-foreground">Employer ESI (3.25%)</div>
          <div className="text-2xl font-bold">{formatCurrency(totals.employerESI)}</div>
        </Card>
        <Card className="p-4 bg-primary/5 border-primary">
          <div className="flex items-center gap-2 text-primary text-sm">
            <Wallet className="h-4 w-4" />
            Total ESI
          </div>
          <div className="text-2xl font-bold text-primary">{formatCurrency(totals.totalESI)}</div>
        </Card>
      </div>

      {/* Employee-wise ESI Table */}
      <Card>
        <div className="p-4 border-b">
          <h3 className="font-semibold">Employee-wise ESI Contribution</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b bg-muted/50">
                <th className="px-4 py-3 text-left font-medium">Employee</th>
                <th className="px-4 py-3 text-left font-medium">IP Number</th>
                <th className="px-4 py-3 text-right font-medium">Gross Salary</th>
                <th className="px-4 py-3 text-center font-medium">Days</th>
                <th className="px-4 py-3 text-center font-medium">Applicable</th>
                <th className="px-4 py-3 text-right font-medium">Employee ESI</th>
                <th className="px-4 py-3 text-right font-medium">Employer ESI</th>
                <th className="px-4 py-3 text-right font-medium">Total</th>
              </tr>
            </thead>
            <tbody>
              {contributions.map((emp) => (
                <tr key={emp.employee_id} className={`border-b ${!emp.esi_applicable ? "bg-muted/30" : ""}`}>
                  <td className="px-4 py-3">
                    <div className="font-medium">{emp.employee_name}</div>
                    <div className="text-sm text-muted-foreground">{emp.employee_code}</div>
                  </td>
                  <td className="px-4 py-3 font-mono text-sm">{emp.ip_number || "-"}</td>
                  <td className="px-4 py-3 text-right">
                    {formatCurrency(emp.gross_wages)}
                    {emp.gross_wages > 21000 && (
                      <span className="text-xs text-warning ml-1">(&gt; 21K)</span>
                    )}
                  </td>
                  <td className="px-4 py-3 text-center">{emp.present_days}</td>
                  <td className="px-4 py-3 text-center">
                    {emp.esi_applicable ? (
                      <Badge variant="success">
                        <CheckCircle2 className="h-3 w-3 mr-1" />
                        Yes
                      </Badge>
                    ) : (
                      <Badge variant="secondary">
                        <AlertCircle className="h-3 w-3 mr-1" />
                        No
                      </Badge>
                    )}
                  </td>
                  <td className="px-4 py-3 text-right">
                    {emp.esi_applicable ? formatCurrency(emp.employee_esi) : "-"}
                  </td>
                  <td className="px-4 py-3 text-right">
                    {emp.esi_applicable ? formatCurrency(emp.employer_esi) : "-"}
                  </td>
                  <td className="px-4 py-3 text-right font-semibold">
                    {emp.esi_applicable ? formatCurrency(emp.total_esi) : "-"}
                  </td>
                </tr>
              ))}
            </tbody>
            <tfoot>
              <tr className="bg-muted/50 font-semibold">
                <td colSpan={2} className="px-4 py-3">
                  Total ({applicableEmployees.length} applicable employees)
                </td>
                <td className="px-4 py-3 text-right">{formatCurrency(totals.grossSalary)}</td>
                <td className="px-4 py-3 text-center">-</td>
                <td className="px-4 py-3 text-center">-</td>
                <td className="px-4 py-3 text-right">{formatCurrency(totals.employeeESI)}</td>
                <td className="px-4 py-3 text-right">{formatCurrency(totals.employerESI)}</td>
                <td className="px-4 py-3 text-right text-primary">
                  {formatCurrency(totals.totalESI)}
                </td>
              </tr>
            </tfoot>
          </table>
        </div>
      </Card>

      {/* Contribution Period Info */}
      <Card className="p-4">
        <h3 className="font-semibold mb-3">ESI Contribution Periods</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-4 bg-muted/50 rounded-lg">
            <div className="font-medium">April - September</div>
            <div className="text-sm text-muted-foreground mt-1">
              Contribution period for benefit period October - March
            </div>
          </div>
          <div className="p-4 bg-muted/50 rounded-lg">
            <div className="font-medium">October - March</div>
            <div className="text-sm text-muted-foreground mt-1">
              Contribution period for benefit period April - September
            </div>
          </div>
        </div>
      </Card>

      {/* Success Message */}
      {isGenerated && (
        <Card className="p-4 bg-success/5 border-success">
          <div className="flex items-start gap-4">
            <CheckCircle2 className="h-6 w-6 text-success mt-0.5" />
            <div>
              <h3 className="font-semibold text-success">ESI Return Generated Successfully</h3>
              <p className="text-sm text-muted-foreground mt-1">
                ESI return for {months[parseInt(selectedMonth) - 1]} {selectedYear} has been
                generated. You can download and upload it to the ESIC Portal.
              </p>
              <div className="mt-3 flex gap-4 text-sm">
                <div>
                  <span className="text-muted-foreground">Due Date:</span>{" "}
                  <span className="font-medium">15th Feb 2026</span>
                </div>
                <div>
                  <span className="text-muted-foreground">Total Payable:</span>{" "}
                  <span className="font-medium text-primary">{formatCurrency(totals.totalESI)}</span>
                </div>
              </div>
            </div>
          </div>
        </Card>
      )}
    </div>
  );
}
