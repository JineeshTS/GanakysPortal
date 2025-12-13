'use client';

/**
 * Trial Balance Report Page
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
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import accountingApi from '@/lib/api/accounting';
import type { ChartOfAccount } from '@/types/accounting';

export default function TrialBalancePage() {
  const [isLoading, setIsLoading] = useState(false);
  const [accounts, setAccounts] = useState<ChartOfAccount[]>([]);
  const [asOfDate, setAsOfDate] = useState(new Date().toISOString().split('T')[0]);

  const loadReport = async () => {
    setIsLoading(true);
    try {
      const data = await accountingApi.getTrialBalance(asOfDate);
      setAccounts(data);
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

  const totalDebits = accounts.reduce((sum, acc) => sum + (acc.debit_balance || 0), 0);
  const totalCredits = accounts.reduce((sum, acc) => sum + (acc.credit_balance || 0), 0);

  const accountsByType = accounts.reduce((grouped, account) => {
    const type = account.account_type || 'other';
    if (!grouped[type]) grouped[type] = [];
    grouped[type].push(account);
    return grouped;
  }, {} as Record<string, ChartOfAccount[]>);

  const typeLabels: Record<string, string> = {
    asset: 'Assets',
    liability: 'Liabilities',
    equity: 'Equity',
    revenue: 'Revenue',
    expense: 'Expenses',
    other: 'Other',
  };

  return (
    <DashboardLayout>
      <div className="max-w-5xl mx-auto space-y-6">
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
            <h1 className="text-2xl font-bold tracking-tight">Trial Balance</h1>
            <p className="text-muted-foreground">
              Account balances summary
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
        ) : accounts.length > 0 ? (
          <Card>
            <CardHeader>
              <CardTitle>Trial Balance</CardTitle>
              <CardDescription>
                As of {new Date(asOfDate).toLocaleDateString('en-IN', { day: '2-digit', month: 'long', year: 'numeric' })}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Account Code</TableHead>
                    <TableHead>Account Name</TableHead>
                    <TableHead className="text-right">Debit</TableHead>
                    <TableHead className="text-right">Credit</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {Object.entries(accountsByType).map(([type, accs]) => (
                    <>
                      <TableRow key={type} className="bg-muted/50">
                        <TableCell colSpan={4} className="font-semibold">
                          {typeLabels[type] || type}
                        </TableCell>
                      </TableRow>
                      {accs.map((account) => (
                        <TableRow key={account.id}>
                          <TableCell className="font-mono text-sm">{account.code}</TableCell>
                          <TableCell>{account.name}</TableCell>
                          <TableCell className="text-right">
                            {account.debit_balance ? formatCurrency(account.debit_balance) : '—'}
                          </TableCell>
                          <TableCell className="text-right">
                            {account.credit_balance ? formatCurrency(account.credit_balance) : '—'}
                          </TableCell>
                        </TableRow>
                      ))}
                    </>
                  ))}
                  <TableRow className="border-t-2 font-bold">
                    <TableCell colSpan={2}>Total</TableCell>
                    <TableCell className="text-right">{formatCurrency(totalDebits)}</TableCell>
                    <TableCell className="text-right">{formatCurrency(totalCredits)}</TableCell>
                  </TableRow>
                </TableBody>
              </Table>

              {totalDebits !== totalCredits && (
                <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
                  <p className="text-red-800 font-medium">
                    Warning: Trial balance is out of balance by {formatCurrency(Math.abs(totalDebits - totalCredits))}
                  </p>
                </div>
              )}

              {totalDebits === totalCredits && (
                <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
                  <p className="text-green-800 font-medium">
                    Trial balance is in balance
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        ) : (
          <Card>
            <CardContent className="py-8 text-center">
              <p className="text-muted-foreground">No account data found. Select a date and generate the report.</p>
            </CardContent>
          </Card>
        )}
      </div>
    </DashboardLayout>
  );
}
