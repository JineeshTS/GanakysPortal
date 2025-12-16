'use client';

/**
 * Profit & Loss Report Page
 */

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { DashboardLayout } from '@/components/layout/dashboard-layout';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import accountingApi from '@/lib/api/accounting';

export default function ProfitLossReportPage() {
  const [isLoading, setIsLoading] = useState(false);
  const [reportData, setReportData] = useState<Record<string, number> | null>(null);

  // Date range
  const currentYear = new Date().getFullYear();
  const [startDate, setStartDate] = useState(`${currentYear}-04-01`);
  const [endDate, setEndDate] = useState(new Date().toISOString().split('T')[0]);

  const loadReport = async () => {
    setIsLoading(true);
    try {
      const data = await accountingApi.getProfitLoss(startDate, endDate);
      setReportData(data);
    } catch (error) {
      console.error('Failed to load report:', error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadReport();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const totalRevenue = reportData?.total_revenue || 0;
  const totalExpenses = reportData?.total_expenses || 0;
  const grossProfit = reportData?.gross_profit || 0;
  const netProfit = reportData?.net_profit || totalRevenue - totalExpenses;

  return (
    <DashboardLayout>
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center gap-4">
          <Link href="/accounting">
            <Button variant="ghost" size="icon">
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
            </Button>
          </Link>
          <div>
            <h1 className="text-2xl font-bold tracking-tight">Profit & Loss Statement</h1>
            <p className="text-muted-foreground">
              Income and expenses summary
            </p>
          </div>
        </div>

        {/* Date Range */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Report Period</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-end gap-4">
              <div className="space-y-2">
                <Label htmlFor="start_date">From</Label>
                <Input
                  id="start_date"
                  type="date"
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="end_date">To</Label>
                <Input
                  id="end_date"
                  type="date"
                  value={endDate}
                  onChange={(e) => setEndDate(e.target.value)}
                />
              </div>
              <Button onClick={loadReport} disabled={isLoading}>
                {isLoading ? 'Loading...' : 'Generate Report'}
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Report */}
        {isLoading ? (
          <Card>
            <CardContent className="py-8 text-center">
              <div className="h-8 w-8 mx-auto animate-spin rounded-full border-4 border-primary border-t-transparent" />
              <p className="mt-2 text-muted-foreground">Generating report...</p>
            </CardContent>
          </Card>
        ) : reportData ? (
          <>
            {/* Summary Cards */}
            <div className="grid gap-4 md:grid-cols-3">
              <Card>
                <CardHeader className="pb-2">
                  <CardDescription>Total Revenue</CardDescription>
                  <CardTitle className="text-2xl text-green-600">
                    {formatCurrency(totalRevenue)}
                  </CardTitle>
                </CardHeader>
              </Card>
              <Card>
                <CardHeader className="pb-2">
                  <CardDescription>Total Expenses</CardDescription>
                  <CardTitle className="text-2xl text-red-600">
                    {formatCurrency(totalExpenses)}
                  </CardTitle>
                </CardHeader>
              </Card>
              <Card>
                <CardHeader className="pb-2">
                  <CardDescription>Net Profit</CardDescription>
                  <CardTitle className={`text-2xl ${netProfit >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {formatCurrency(netProfit)}
                  </CardTitle>
                </CardHeader>
              </Card>
            </div>

            {/* Detailed Report */}
            <Card>
              <CardHeader>
                <CardTitle>Income Statement</CardTitle>
                <CardDescription>
                  {new Date(startDate).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' })}
                  {' - '}
                  {new Date(endDate).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' })}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-6">
                  {/* Revenue Section */}
                  <div>
                    <h3 className="font-semibold text-lg mb-3 text-green-700">Revenue</h3>
                    <div className="space-y-2 pl-4">
                      <div className="flex justify-between py-1">
                        <span>Sales Revenue</span>
                        <span>{formatCurrency(reportData.sales_revenue || 0)}</span>
                      </div>
                      <div className="flex justify-between py-1">
                        <span>Service Revenue</span>
                        <span>{formatCurrency(reportData.service_revenue || 0)}</span>
                      </div>
                      <div className="flex justify-between py-1">
                        <span>Other Income</span>
                        <span>{formatCurrency(reportData.other_income || 0)}</span>
                      </div>
                      <div className="flex justify-between py-2 border-t font-medium">
                        <span>Total Revenue</span>
                        <span className="text-green-600">{formatCurrency(totalRevenue)}</span>
                      </div>
                    </div>
                  </div>

                  {/* Cost of Goods Sold */}
                  <div>
                    <h3 className="font-semibold text-lg mb-3 text-orange-700">Cost of Goods Sold</h3>
                    <div className="space-y-2 pl-4">
                      <div className="flex justify-between py-1">
                        <span>Direct Costs</span>
                        <span>{formatCurrency(reportData.direct_costs || 0)}</span>
                      </div>
                      <div className="flex justify-between py-2 border-t font-medium">
                        <span>Gross Profit</span>
                        <span className="text-green-600">{formatCurrency(grossProfit)}</span>
                      </div>
                    </div>
                  </div>

                  {/* Operating Expenses */}
                  <div>
                    <h3 className="font-semibold text-lg mb-3 text-red-700">Operating Expenses</h3>
                    <div className="space-y-2 pl-4">
                      <div className="flex justify-between py-1">
                        <span>Salaries & Wages</span>
                        <span>{formatCurrency(reportData.salaries || 0)}</span>
                      </div>
                      <div className="flex justify-between py-1">
                        <span>Rent & Utilities</span>
                        <span>{formatCurrency(reportData.rent_utilities || 0)}</span>
                      </div>
                      <div className="flex justify-between py-1">
                        <span>Marketing & Advertising</span>
                        <span>{formatCurrency(reportData.marketing || 0)}</span>
                      </div>
                      <div className="flex justify-between py-1">
                        <span>Travel & Entertainment</span>
                        <span>{formatCurrency(reportData.travel || 0)}</span>
                      </div>
                      <div className="flex justify-between py-1">
                        <span>Professional Fees</span>
                        <span>{formatCurrency(reportData.professional_fees || 0)}</span>
                      </div>
                      <div className="flex justify-between py-1">
                        <span>Other Expenses</span>
                        <span>{formatCurrency(reportData.other_expenses || 0)}</span>
                      </div>
                      <div className="flex justify-between py-2 border-t font-medium">
                        <span>Total Operating Expenses</span>
                        <span className="text-red-600">{formatCurrency(totalExpenses)}</span>
                      </div>
                    </div>
                  </div>

                  {/* Net Profit */}
                  <div className="border-t-2 pt-4">
                    <div className="flex justify-between text-xl font-bold">
                      <span>Net Profit / (Loss)</span>
                      <span className={netProfit >= 0 ? 'text-green-600' : 'text-red-600'}>
                        {formatCurrency(netProfit)}
                      </span>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </>
        ) : (
          <Card>
            <CardContent className="py-8 text-center">
              <p className="text-muted-foreground">Select a date range and generate the report</p>
            </CardContent>
          </Card>
        )}
      </div>
    </DashboardLayout>
  );
}
