'use client';

/**
 * Aging Report Page
 */

import { useState, useEffect } from 'react';
import Link from 'next/link';
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
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import accountingApi from '@/lib/api/accounting';

interface AgingEntry {
  id: string;
  name: string;
  document_number: string;
  document_date: string;
  due_date: string;
  total_amount: number;
  balance_due: number;
  days_overdue: number;
  current: number;
  days_1_30: number;
  days_31_60: number;
  days_61_90: number;
  days_over_90: number;
}

export default function AgingReportPage() {
  const [isLoading, setIsLoading] = useState(false);
  const [entries, setEntries] = useState<AgingEntry[]>([]);
  const [reportType, setReportType] = useState<'receivables' | 'payables'>('receivables');

  const loadReport = async () => {
    setIsLoading(true);
    try {
      const data = await accountingApi.getAgingReport(reportType) as AgingEntry[];
      setEntries(data);
    } catch (error) {
      console.error('Failed to load report:', error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadReport();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [reportType]);

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const totals = entries.reduce(
    (acc, entry) => ({
      current: acc.current + (entry.current || 0),
      days_1_30: acc.days_1_30 + (entry.days_1_30 || 0),
      days_31_60: acc.days_31_60 + (entry.days_31_60 || 0),
      days_61_90: acc.days_61_90 + (entry.days_61_90 || 0),
      days_over_90: acc.days_over_90 + (entry.days_over_90 || 0),
      total: acc.total + (entry.balance_due || 0),
    }),
    { current: 0, days_1_30: 0, days_31_60: 0, days_61_90: 0, days_over_90: 0, total: 0 }
  );

  return (
    <DashboardLayout>
      <div className="max-w-6xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href="/accounting">
              <Button variant="ghost" size="icon">
                <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                </svg>
              </Button>
            </Link>
            <div>
              <h1 className="text-2xl font-bold tracking-tight">Aging Report</h1>
              <p className="text-muted-foreground">
                {reportType === 'receivables' ? 'Accounts Receivable' : 'Accounts Payable'} aging analysis
              </p>
            </div>
          </div>
          <Select value={reportType} onValueChange={(v) => setReportType(v as 'receivables' | 'payables')}>
            <SelectTrigger className="w-[180px]">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="receivables">Receivables</SelectItem>
              <SelectItem value="payables">Payables</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Summary Cards */}
        <div className="grid gap-4 md:grid-cols-5">
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Current</CardDescription>
              <CardTitle className="text-xl text-green-600">
                {formatCurrency(totals.current)}
              </CardTitle>
            </CardHeader>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>1-30 Days</CardDescription>
              <CardTitle className="text-xl text-yellow-600">
                {formatCurrency(totals.days_1_30)}
              </CardTitle>
            </CardHeader>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>31-60 Days</CardDescription>
              <CardTitle className="text-xl text-orange-600">
                {formatCurrency(totals.days_31_60)}
              </CardTitle>
            </CardHeader>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>61-90 Days</CardDescription>
              <CardTitle className="text-xl text-red-600">
                {formatCurrency(totals.days_61_90)}
              </CardTitle>
            </CardHeader>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Over 90 Days</CardDescription>
              <CardTitle className="text-xl text-red-800">
                {formatCurrency(totals.days_over_90)}
              </CardTitle>
            </CardHeader>
          </Card>
        </div>

        {/* Report Table */}
        <Card>
          <CardHeader>
            <CardTitle>
              {reportType === 'receivables' ? 'Customer' : 'Vendor'} Aging Details
            </CardTitle>
            <CardDescription>
              Breakdown by aging bucket
            </CardDescription>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="py-8 text-center">
                <div className="h-8 w-8 mx-auto animate-spin rounded-full border-4 border-primary border-t-transparent" />
                <p className="mt-2 text-muted-foreground">Loading report...</p>
              </div>
            ) : entries.length === 0 ? (
              <div className="py-8 text-center">
                <svg className="mx-auto h-12 w-12 text-muted-foreground" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <h3 className="mt-2 font-medium">No outstanding {reportType}</h3>
                <p className="text-sm text-muted-foreground">
                  All {reportType === 'receivables' ? 'invoices' : 'bills'} are paid
                </p>
              </div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>{reportType === 'receivables' ? 'Customer' : 'Vendor'}</TableHead>
                    <TableHead>Document</TableHead>
                    <TableHead className="text-right">Current</TableHead>
                    <TableHead className="text-right">1-30</TableHead>
                    <TableHead className="text-right">31-60</TableHead>
                    <TableHead className="text-right">61-90</TableHead>
                    <TableHead className="text-right">&gt;90</TableHead>
                    <TableHead className="text-right">Total</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {entries.map((entry) => (
                    <TableRow key={entry.id}>
                      <TableCell className="font-medium">{entry.name}</TableCell>
                      <TableCell className="font-mono text-sm">{entry.document_number}</TableCell>
                      <TableCell className="text-right">
                        {entry.current ? formatCurrency(entry.current) : '—'}
                      </TableCell>
                      <TableCell className="text-right text-yellow-600">
                        {entry.days_1_30 ? formatCurrency(entry.days_1_30) : '—'}
                      </TableCell>
                      <TableCell className="text-right text-orange-600">
                        {entry.days_31_60 ? formatCurrency(entry.days_31_60) : '—'}
                      </TableCell>
                      <TableCell className="text-right text-red-600">
                        {entry.days_61_90 ? formatCurrency(entry.days_61_90) : '—'}
                      </TableCell>
                      <TableCell className="text-right text-red-800 font-medium">
                        {entry.days_over_90 ? formatCurrency(entry.days_over_90) : '—'}
                      </TableCell>
                      <TableCell className="text-right font-medium">
                        {formatCurrency(entry.balance_due)}
                      </TableCell>
                    </TableRow>
                  ))}
                  <TableRow className="border-t-2 font-bold">
                    <TableCell colSpan={2}>Total</TableCell>
                    <TableCell className="text-right">{formatCurrency(totals.current)}</TableCell>
                    <TableCell className="text-right text-yellow-600">{formatCurrency(totals.days_1_30)}</TableCell>
                    <TableCell className="text-right text-orange-600">{formatCurrency(totals.days_31_60)}</TableCell>
                    <TableCell className="text-right text-red-600">{formatCurrency(totals.days_61_90)}</TableCell>
                    <TableCell className="text-right text-red-800">{formatCurrency(totals.days_over_90)}</TableCell>
                    <TableCell className="text-right">{formatCurrency(totals.total)}</TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>

        {/* Aging Distribution Chart placeholder */}
        <Card>
          <CardHeader>
            <CardTitle>Aging Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-8 bg-muted rounded-lg overflow-hidden flex">
              {totals.total > 0 && (
                <>
                  <div
                    className="bg-green-500 h-full transition-all"
                    style={{ width: `${(totals.current / totals.total) * 100}%` }}
                    title={`Current: ${formatCurrency(totals.current)}`}
                  />
                  <div
                    className="bg-yellow-500 h-full transition-all"
                    style={{ width: `${(totals.days_1_30 / totals.total) * 100}%` }}
                    title={`1-30 Days: ${formatCurrency(totals.days_1_30)}`}
                  />
                  <div
                    className="bg-orange-500 h-full transition-all"
                    style={{ width: `${(totals.days_31_60 / totals.total) * 100}%` }}
                    title={`31-60 Days: ${formatCurrency(totals.days_31_60)}`}
                  />
                  <div
                    className="bg-red-500 h-full transition-all"
                    style={{ width: `${(totals.days_61_90 / totals.total) * 100}%` }}
                    title={`61-90 Days: ${formatCurrency(totals.days_61_90)}`}
                  />
                  <div
                    className="bg-red-800 h-full transition-all"
                    style={{ width: `${(totals.days_over_90 / totals.total) * 100}%` }}
                    title={`Over 90 Days: ${formatCurrency(totals.days_over_90)}`}
                  />
                </>
              )}
            </div>
            <div className="flex justify-between mt-2 text-xs text-muted-foreground">
              <span>Current</span>
              <span>1-30</span>
              <span>31-60</span>
              <span>61-90</span>
              <span>&gt;90 Days</span>
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}
