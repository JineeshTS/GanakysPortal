'use client';

/**
 * Form 16 Page
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
import payrollApi from '@/lib/api/payroll';
import type { Form16 } from '@/types/payroll';

export default function Form16Page() {
  const router = useRouter();
  const [form16, setForm16] = useState<Form16 | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isDownloading, setIsDownloading] = useState(false);
  const [error, setError] = useState('');

  // Financial year options
  const currentYear = new Date().getFullYear();
  const currentMonth = new Date().getMonth();
  const defaultFY = currentMonth >= 3 ? `${currentYear - 1}-${currentYear}` : `${currentYear - 2}-${currentYear - 1}`;
  const [selectedFY, setSelectedFY] = useState(defaultFY);

  const fyOptions = [
    `${currentYear - 2}-${currentYear - 1}`,
    `${currentYear - 1}-${currentYear}`,
  ];

  const loadForm16 = useCallback(async () => {
    setIsLoading(true);
    setError('');
    try {
      const data = await payrollApi.getMyForm16(selectedFY);
      setForm16(data);
    } catch (err) {
      console.error('Failed to load Form 16:', err);
      setForm16(null);
      setError('Form 16 is not available for this financial year');
    } finally {
      setIsLoading(false);
    }
  }, [selectedFY]);

  useEffect(() => {
    loadForm16();
  }, [loadForm16]);

  const handleDownload = async () => {
    setIsDownloading(true);
    try {
      const blob = await payrollApi.downloadForm16(selectedFY);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `form16_${selectedFY.replace('-', '_')}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      console.error('Failed to download Form 16:', err);
    } finally {
      setIsDownloading(false);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0,
    }).format(amount);
  };

  return (
    <DashboardLayout>
      <div className="max-w-2xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="icon" onClick={() => router.push('/payroll')}>
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
            </Button>
            <div>
              <h1 className="text-2xl font-bold tracking-tight">Form 16</h1>
              <p className="text-muted-foreground">
                Download your annual tax certificate
              </p>
            </div>
          </div>
          <Select value={selectedFY} onValueChange={setSelectedFY}>
            <SelectTrigger className="w-[140px]">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {fyOptions.map((fy) => (
                <SelectItem key={fy} value={fy}>
                  FY {fy}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {isLoading ? (
          <Card>
            <CardContent className="py-8 text-center">
              <div className="h-8 w-8 mx-auto animate-spin rounded-full border-4 border-primary border-t-transparent" />
              <p className="mt-2 text-muted-foreground">Loading Form 16...</p>
            </CardContent>
          </Card>
        ) : error ? (
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
              <h3 className="mt-2 font-medium">Form 16 Not Available</h3>
              <p className="text-sm text-muted-foreground">{error}</p>
            </CardContent>
          </Card>
        ) : form16 && (
          <>
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>Form 16 - Certificate of TDS</CardTitle>
                    <CardDescription>Financial Year {selectedFY}</CardDescription>
                  </div>
                  <Button onClick={handleDownload} disabled={isDownloading}>
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
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="rounded-lg bg-muted p-4">
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="text-muted-foreground">Employee Name</span>
                        <div className="font-medium">{form16.employee_name}</div>
                      </div>
                      <div>
                        <span className="text-muted-foreground">Employee Code</span>
                        <div className="font-medium">{form16.employee_code}</div>
                      </div>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <div className="flex justify-between py-2 border-b">
                      <span>Total Income</span>
                      <span className="font-medium">{formatCurrency(form16.total_income)}</span>
                    </div>
                    <div className="flex justify-between py-2 border-b">
                      <span>Total Deductions</span>
                      <span className="font-medium text-green-600">- {formatCurrency(form16.total_deductions)}</span>
                    </div>
                    <div className="flex justify-between py-2 border-b">
                      <span>Taxable Income</span>
                      <span className="font-medium">{formatCurrency(form16.taxable_income)}</span>
                    </div>
                    <div className="flex justify-between py-2 border-b">
                      <span>Tax Payable</span>
                      <span className="font-medium text-red-600">{formatCurrency(form16.tax_payable)}</span>
                    </div>
                    <div className="flex justify-between py-2 bg-muted rounded-lg px-3">
                      <span className="font-medium">TDS Deducted</span>
                      <span className="font-bold text-green-600">{formatCurrency(form16.tds_deducted)}</span>
                    </div>
                  </div>

                  {form16.generated_at && (
                    <div className="text-xs text-muted-foreground text-right">
                      Generated on {new Date(form16.generated_at).toLocaleDateString()}
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-base">Important Information</CardTitle>
              </CardHeader>
              <CardContent className="text-sm text-muted-foreground space-y-2">
                <p>
                  Form 16 is a certificate issued by your employer certifying the Tax Deducted at Source (TDS)
                  from your salary during the financial year.
                </p>
                <p>
                  This document is essential for filing your Income Tax Return (ITR). Please keep it safe
                  for your records.
                </p>
              </CardContent>
            </Card>
          </>
        )}
      </div>
    </DashboardLayout>
  );
}
