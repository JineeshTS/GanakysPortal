'use client';

/**
 * Balance Sheet Report Page
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

interface BalanceSheetData {
  assets: {
    current: Record<string, number>;
    non_current: Record<string, number>;
    total: number;
  };
  liabilities: {
    current: Record<string, number>;
    non_current: Record<string, number>;
    total: number;
  };
  equity: {
    items: Record<string, number>;
    total: number;
  };
}

export default function BalanceSheetPage() {
  const [isLoading, setIsLoading] = useState(false);
  const [reportData, setReportData] = useState<BalanceSheetData | null>(null);
  const [asOfDate, setAsOfDate] = useState(new Date().toISOString().split('T')[0]);

  const loadReport = async () => {
    setIsLoading(true);
    try {
      const data = await accountingApi.getBalanceSheet(asOfDate) as unknown as BalanceSheetData;
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

  const renderSection = (title: string, items: Record<string, number>, color: string) => (
    <div className="space-y-2">
      <h4 className={`font-medium ${color}`}>{title}</h4>
      {Object.entries(items).map(([key, value]) => (
        <div key={key} className="flex justify-between py-1 pl-4">
          <span className="text-muted-foreground">
            {key.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')}
          </span>
          <span>{formatCurrency(value)}</span>
        </div>
      ))}
    </div>
  );

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
            <h1 className="text-2xl font-bold tracking-tight">Balance Sheet</h1>
            <p className="text-muted-foreground">
              Assets, liabilities, and equity summary
            </p>
          </div>
        </div>

        {/* Date Selection */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Report Date</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-end gap-4">
              <div className="space-y-2">
                <Label htmlFor="as_of_date">As of Date</Label>
                <Input
                  id="as_of_date"
                  type="date"
                  value={asOfDate}
                  onChange={(e) => setAsOfDate(e.target.value)}
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
          <Card>
            <CardHeader>
              <CardTitle>Balance Sheet</CardTitle>
              <CardDescription>
                As of {new Date(asOfDate).toLocaleDateString('en-IN', { day: '2-digit', month: 'long', year: 'numeric' })}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-8 md:grid-cols-2">
                {/* Assets */}
                <div className="space-y-6">
                  <h3 className="font-semibold text-lg border-b pb-2">Assets</h3>

                  {renderSection('Current Assets', reportData.assets?.current || {
                    cash_and_bank: 0,
                    accounts_receivable: 0,
                    inventory: 0,
                    prepaid_expenses: 0,
                  }, 'text-blue-700')}

                  <div className="flex justify-between py-2 border-t font-medium pl-4">
                    <span>Total Current Assets</span>
                    <span>
                      {formatCurrency(
                        Object.values(reportData.assets?.current || {}).reduce((a, b) => a + b, 0)
                      )}
                    </span>
                  </div>

                  {renderSection('Non-Current Assets', reportData.assets?.non_current || {
                    property_plant_equipment: 0,
                    intangible_assets: 0,
                    investments: 0,
                  }, 'text-blue-700')}

                  <div className="flex justify-between py-2 border-t font-medium pl-4">
                    <span>Total Non-Current Assets</span>
                    <span>
                      {formatCurrency(
                        Object.values(reportData.assets?.non_current || {}).reduce((a, b) => a + b, 0)
                      )}
                    </span>
                  </div>

                  <div className="flex justify-between py-3 border-t-2 font-bold text-lg">
                    <span>Total Assets</span>
                    <span className="text-blue-600">
                      {formatCurrency(reportData.assets?.total || 0)}
                    </span>
                  </div>
                </div>

                {/* Liabilities & Equity */}
                <div className="space-y-6">
                  <h3 className="font-semibold text-lg border-b pb-2">Liabilities & Equity</h3>

                  {renderSection('Current Liabilities', reportData.liabilities?.current || {
                    accounts_payable: 0,
                    accrued_expenses: 0,
                    short_term_debt: 0,
                    taxes_payable: 0,
                  }, 'text-red-700')}

                  <div className="flex justify-between py-2 border-t font-medium pl-4">
                    <span>Total Current Liabilities</span>
                    <span>
                      {formatCurrency(
                        Object.values(reportData.liabilities?.current || {}).reduce((a, b) => a + b, 0)
                      )}
                    </span>
                  </div>

                  {renderSection('Non-Current Liabilities', reportData.liabilities?.non_current || {
                    long_term_debt: 0,
                    deferred_tax: 0,
                  }, 'text-red-700')}

                  <div className="flex justify-between py-2 border-t font-medium pl-4">
                    <span>Total Non-Current Liabilities</span>
                    <span>
                      {formatCurrency(
                        Object.values(reportData.liabilities?.non_current || {}).reduce((a, b) => a + b, 0)
                      )}
                    </span>
                  </div>

                  <div className="flex justify-between py-2 border-t font-medium">
                    <span>Total Liabilities</span>
                    <span className="text-red-600">
                      {formatCurrency(reportData.liabilities?.total || 0)}
                    </span>
                  </div>

                  {renderSection("Shareholders' Equity", reportData.equity?.items || {
                    share_capital: 0,
                    retained_earnings: 0,
                    reserves: 0,
                  }, 'text-green-700')}

                  <div className="flex justify-between py-2 border-t font-medium pl-4">
                    <span>Total Equity</span>
                    <span className="text-green-600">
                      {formatCurrency(reportData.equity?.total || 0)}
                    </span>
                  </div>

                  <div className="flex justify-between py-3 border-t-2 font-bold text-lg">
                    <span>Total Liabilities & Equity</span>
                    <span className="text-blue-600">
                      {formatCurrency((reportData.liabilities?.total || 0) + (reportData.equity?.total || 0))}
                    </span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        ) : (
          <Card>
            <CardContent className="py-8 text-center">
              <p className="text-muted-foreground">Select a date and generate the report</p>
            </CardContent>
          </Card>
        )}
      </div>
    </DashboardLayout>
  );
}
