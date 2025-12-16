'use client';

/**
 * My Payslips Page
 */

import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { DashboardLayout } from '@/components/layout/dashboard-layout';
import { Button } from '@/components/ui/button';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import payrollApi from '@/lib/api/payroll';
import type { Payslip } from '@/types/payroll';

const monthNames = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December'
];

export default function MyPayslipsPage() {
  const router = useRouter();
  const [payslips, setPayslips] = useState<Payslip[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedYear, setSelectedYear] = useState(new Date().getFullYear());

  // Detail dialog
  const [detailDialogOpen, setDetailDialogOpen] = useState(false);
  const [selectedPayslip, setSelectedPayslip] = useState<Payslip | null>(null);
  const [isDownloading, setIsDownloading] = useState(false);

  const loadPayslips = useCallback(async () => {
    setIsLoading(true);
    try {
      const data = await payrollApi.getMyPayslips(selectedYear);
      setPayslips(data);
    } catch (error) {
      console.error('Failed to load payslips:', error);
    } finally {
      setIsLoading(false);
    }
  }, [selectedYear]);

  useEffect(() => {
    loadPayslips();
  }, [loadPayslips]);

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const openPayslipDetail = (payslip: Payslip) => {
    setSelectedPayslip(payslip);
    setDetailDialogOpen(true);
  };

  const handleDownloadPayslip = async () => {
    if (!selectedPayslip) return;

    setIsDownloading(true);
    try {
      const blob = await payrollApi.downloadPayslip(selectedPayslip.id);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `payslip_${monthNames[selectedPayslip.month - 1].toLowerCase()}_${selectedPayslip.year}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Failed to download payslip:', error);
    } finally {
      setIsDownloading(false);
    }
  };

  const years = [
    new Date().getFullYear() - 2,
    new Date().getFullYear() - 1,
    new Date().getFullYear(),
  ];

  // Calculate year totals
  const yearTotals = payslips.reduce(
    (acc, p) => ({
      gross: acc.gross + p.gross_salary,
      deductions: acc.deductions + p.total_deductions,
      net: acc.net + p.net_salary,
    }),
    { gross: 0, deductions: 0, net: 0 }
  );

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="icon" onClick={() => router.push('/payroll')}>
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
            </Button>
            <div>
              <h1 className="text-2xl font-bold tracking-tight">My Payslips</h1>
              <p className="text-muted-foreground">
                View and download your monthly payslips
              </p>
            </div>
          </div>
          <Select value={String(selectedYear)} onValueChange={(v) => setSelectedYear(parseInt(v))}>
            <SelectTrigger className="w-[120px]">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {years.map((year) => (
                <SelectItem key={year} value={String(year)}>
                  {year}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Year Summary */}
        <div className="grid gap-4 md:grid-cols-3">
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Total Gross ({selectedYear})</CardDescription>
              <CardTitle className="text-2xl">{formatCurrency(yearTotals.gross)}</CardTitle>
            </CardHeader>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Total Deductions</CardDescription>
              <CardTitle className="text-2xl text-red-600">{formatCurrency(yearTotals.deductions)}</CardTitle>
            </CardHeader>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Total Net Salary</CardDescription>
              <CardTitle className="text-2xl text-green-600">{formatCurrency(yearTotals.net)}</CardTitle>
            </CardHeader>
          </Card>
        </div>

        {/* Payslips Grid */}
        {isLoading ? (
          <div className="grid gap-4 md:grid-cols-3 lg:grid-cols-4">
            {[1, 2, 3, 4].map((i) => (
              <Card key={i}>
                <CardHeader>
                  <div className="h-5 w-20 bg-muted rounded animate-pulse" />
                </CardHeader>
                <CardContent>
                  <div className="h-8 w-24 bg-muted rounded animate-pulse" />
                </CardContent>
              </Card>
            ))}
          </div>
        ) : payslips.length === 0 ? (
          <Card>
            <CardContent className="py-8 text-center">
              <svg
                className="mx-auto h-12 w-12 text-muted-foreground"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                />
              </svg>
              <h3 className="mt-2 font-medium">No payslips found</h3>
              <p className="text-sm text-muted-foreground">
                No payslips available for {selectedYear}
              </p>
            </CardContent>
          </Card>
        ) : (
          <div className="grid gap-4 md:grid-cols-3 lg:grid-cols-4">
            {payslips.map((payslip) => (
              <Card
                key={payslip.id}
                className="cursor-pointer hover:shadow-md transition-shadow"
                onClick={() => openPayslipDetail(payslip)}
              >
                <CardHeader className="pb-2">
                  <CardTitle className="text-lg">
                    {monthNames[payslip.month - 1]}
                  </CardTitle>
                  <CardDescription>{payslip.year}</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-green-600">
                    {formatCurrency(payslip.net_salary)}
                  </div>
                  <div className="mt-2 text-xs text-muted-foreground">
                    <div className="flex justify-between">
                      <span>Gross:</span>
                      <span>{formatCurrency(payslip.gross_salary)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Deductions:</span>
                      <span className="text-red-600">-{formatCurrency(payslip.total_deductions)}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>

      {/* Payslip Detail Dialog */}
      <Dialog open={detailDialogOpen} onOpenChange={setDetailDialogOpen}>
        <DialogContent className="sm:max-w-lg">
          <DialogHeader>
            <DialogTitle>
              Payslip - {selectedPayslip && `${monthNames[selectedPayslip.month - 1]} ${selectedPayslip.year}`}
            </DialogTitle>
            <DialogDescription>
              Salary breakdown for the month
            </DialogDescription>
          </DialogHeader>

          {selectedPayslip && (
            <div className="space-y-4 max-h-[60vh] overflow-auto">
              {/* Summary */}
              <div className="grid grid-cols-3 gap-4">
                <div className="rounded-lg bg-muted p-3 text-center">
                  <div className="text-lg font-bold">{selectedPayslip.working_days}</div>
                  <div className="text-xs text-muted-foreground">Working Days</div>
                </div>
                <div className="rounded-lg bg-muted p-3 text-center">
                  <div className="text-lg font-bold">{selectedPayslip.days_worked}</div>
                  <div className="text-xs text-muted-foreground">Days Worked</div>
                </div>
                <div className="rounded-lg bg-red-50 dark:bg-red-900/20 p-3 text-center">
                  <div className="text-lg font-bold text-red-600">{selectedPayslip.lop_days}</div>
                  <div className="text-xs text-muted-foreground">LOP Days</div>
                </div>
              </div>

              {/* Earnings */}
              <div>
                <h4 className="font-medium mb-2 text-green-600">Earnings</h4>
                <div className="space-y-1 text-sm">
                  <div className="flex justify-between py-1">
                    <span>Basic Salary</span>
                    <span>{formatCurrency(selectedPayslip.basic_salary)}</span>
                  </div>
                  <div className="flex justify-between py-1">
                    <span>HRA</span>
                    <span>{formatCurrency(selectedPayslip.hra)}</span>
                  </div>
                  <div className="flex justify-between py-1">
                    <span>Special Allowance</span>
                    <span>{formatCurrency(selectedPayslip.special_allowance)}</span>
                  </div>
                  {selectedPayslip.other_earnings > 0 && (
                    <div className="flex justify-between py-1">
                      <span>Other Earnings</span>
                      <span>{formatCurrency(selectedPayslip.other_earnings)}</span>
                    </div>
                  )}
                  <div className="flex justify-between py-2 border-t font-medium">
                    <span>Total Earnings</span>
                    <span className="text-green-600">{formatCurrency(selectedPayslip.gross_salary)}</span>
                  </div>
                </div>
              </div>

              {/* Deductions */}
              <div>
                <h4 className="font-medium mb-2 text-red-600">Deductions</h4>
                <div className="space-y-1 text-sm">
                  {selectedPayslip.pf_employee > 0 && (
                    <div className="flex justify-between py-1">
                      <span>PF (Employee)</span>
                      <span>{formatCurrency(selectedPayslip.pf_employee)}</span>
                    </div>
                  )}
                  {selectedPayslip.esi_employee > 0 && (
                    <div className="flex justify-between py-1">
                      <span>ESI (Employee)</span>
                      <span>{formatCurrency(selectedPayslip.esi_employee)}</span>
                    </div>
                  )}
                  {selectedPayslip.professional_tax > 0 && (
                    <div className="flex justify-between py-1">
                      <span>Professional Tax</span>
                      <span>{formatCurrency(selectedPayslip.professional_tax)}</span>
                    </div>
                  )}
                  {selectedPayslip.tds > 0 && (
                    <div className="flex justify-between py-1">
                      <span>TDS</span>
                      <span>{formatCurrency(selectedPayslip.tds)}</span>
                    </div>
                  )}
                  {selectedPayslip.other_deductions > 0 && (
                    <div className="flex justify-between py-1">
                      <span>Other Deductions</span>
                      <span>{formatCurrency(selectedPayslip.other_deductions)}</span>
                    </div>
                  )}
                  <div className="flex justify-between py-2 border-t font-medium">
                    <span>Total Deductions</span>
                    <span className="text-red-600">{formatCurrency(selectedPayslip.total_deductions)}</span>
                  </div>
                </div>
              </div>

              {/* Net Salary */}
              <div className="rounded-lg bg-green-50 dark:bg-green-900/20 p-4">
                <div className="flex justify-between items-center">
                  <span className="font-medium">Net Salary</span>
                  <span className="text-2xl font-bold text-green-600">
                    {formatCurrency(selectedPayslip.net_salary)}
                  </span>
                </div>
              </div>

              {/* Employer Contributions */}
              {(selectedPayslip.pf_employer > 0 || selectedPayslip.esi_employer > 0) && (
                <div>
                  <h4 className="font-medium mb-2 text-muted-foreground">Employer Contributions</h4>
                  <div className="space-y-1 text-sm text-muted-foreground">
                    {selectedPayslip.pf_employer > 0 && (
                      <div className="flex justify-between py-1">
                        <span>PF (Employer)</span>
                        <span>{formatCurrency(selectedPayslip.pf_employer)}</span>
                      </div>
                    )}
                    {selectedPayslip.esi_employer > 0 && (
                      <div className="flex justify-between py-1">
                        <span>ESI (Employer)</span>
                        <span>{formatCurrency(selectedPayslip.esi_employer)}</span>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          )}

          <DialogFooter>
            <Button variant="outline" onClick={() => setDetailDialogOpen(false)}>
              Close
            </Button>
            <Button onClick={handleDownloadPayslip} disabled={isDownloading}>
              {isDownloading ? (
                'Downloading...'
              ) : (
                <>
                  <svg className="mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                  </svg>
                  Download PDF
                </>
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </DashboardLayout>
  );
}
