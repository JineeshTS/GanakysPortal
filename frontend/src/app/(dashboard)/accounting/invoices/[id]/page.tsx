'use client';

/**
 * Invoice Detail Page
 */

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { DashboardLayout } from '@/components/layout/dashboard-layout';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Card,
  CardContent,
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
import type { Invoice, InvoiceStatus } from '@/types/accounting';

const statusColors: Record<InvoiceStatus, string> = {
  draft: 'bg-gray-100 text-gray-800',
  sent: 'bg-blue-100 text-blue-800',
  partially_paid: 'bg-yellow-100 text-yellow-800',
  paid: 'bg-green-100 text-green-800',
  overdue: 'bg-red-100 text-red-800',
  cancelled: 'bg-gray-100 text-gray-500',
};

export default function InvoiceDetailPage() {
  const params = useParams();
  const router = useRouter();
  const [invoice, setInvoice] = useState<Invoice | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const loadInvoice = async () => {
      if (!params.id) return;
      try {
        const data = await accountingApi.getInvoice(params.id as string);
        setInvoice(data);
      } catch (error) {
        console.error('Failed to load invoice:', error);
      } finally {
        setIsLoading(false);
      }
    };
    loadInvoice();
  }, [params.id]);

  const handleSendInvoice = async () => {
    if (!invoice) return;
    try {
      await accountingApi.sendInvoice(invoice.id);
      const data = await accountingApi.getInvoice(invoice.id);
      setInvoice(data);
    } catch (error) {
      console.error('Failed to send invoice:', error);
    }
  };

  const handleDownloadInvoice = async () => {
    if (!invoice) return;
    try {
      const blob = await accountingApi.downloadInvoice(invoice.id);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${invoice.invoice_number}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Failed to download invoice:', error);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const formatDate = (date: string) => {
    return new Date(date).toLocaleDateString('en-IN', {
      day: '2-digit',
      month: 'long',
      year: 'numeric',
    });
  };

  if (isLoading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-64">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
        </div>
      </DashboardLayout>
    );
  }

  if (!invoice) {
    return (
      <DashboardLayout>
        <div className="text-center py-12">
          <h2 className="text-xl font-semibold">Invoice not found</h2>
          <Link href="/accounting/invoices">
            <Button className="mt-4">Back to Invoices</Button>
          </Link>
        </div>
      </DashboardLayout>
    );
  }

  const subtotal = invoice.items?.reduce((sum, item) => sum + item.quantity * item.unit_price, 0) || 0;
  const totalTax = invoice.items?.reduce((sum, item) => sum + item.quantity * item.unit_price * (item.tax_rate / 100), 0) || 0;

  return (
    <DashboardLayout>
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href="/accounting/invoices">
              <Button variant="ghost" size="icon">
                <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                </svg>
              </Button>
            </Link>
            <div>
              <div className="flex items-center gap-3">
                <h1 className="text-2xl font-bold tracking-tight">{invoice.invoice_number}</h1>
                <Badge variant="secondary" className={statusColors[invoice.status]}>
                  {invoice.status === 'partially_paid' ? 'Partial' : invoice.status.charAt(0).toUpperCase() + invoice.status.slice(1)}
                </Badge>
              </div>
              <p className="text-muted-foreground">
                Created on {formatDate(invoice.created_at)}
              </p>
            </div>
          </div>
          <div className="flex gap-2">
            {invoice.status === 'draft' && (
              <>
                <Button variant="outline" onClick={() => router.push(`/accounting/invoices/${invoice.id}/edit`)}>
                  Edit
                </Button>
                <Button onClick={handleSendInvoice}>
                  <svg className="mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                  </svg>
                  Send Invoice
                </Button>
              </>
            )}
            {invoice.status !== 'draft' && (
              <>
                <Button variant="outline" onClick={handleDownloadInvoice}>
                  <svg className="mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  Download PDF
                </Button>
                {(invoice.status === 'sent' || invoice.status === 'overdue' || invoice.status === 'partially_paid') && (
                  <Link href={`/accounting/payments/new?invoice=${invoice.id}`}>
                    <Button>
                      <svg className="mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 9V7a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2m2 4h10a2 2 0 002-2v-6a2 2 0 00-2-2H9a2 2 0 00-2 2v6a2 2 0 002 2zm7-5a2 2 0 11-4 0 2 2 0 014 0z" />
                      </svg>
                      Record Payment
                    </Button>
                  </Link>
                )}
              </>
            )}
          </div>
        </div>

        {/* Invoice Details */}
        <div className="grid gap-6 md:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Bill To</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="font-medium">{invoice.customer_name}</div>
              {invoice.customer_email && (
                <div className="text-sm text-muted-foreground">{invoice.customer_email}</div>
              )}
              {invoice.billing_address && (
                <div className="text-sm text-muted-foreground mt-2">{invoice.billing_address}</div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-base">Invoice Info</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <div className="text-muted-foreground">Invoice Date</div>
                  <div className="font-medium">{formatDate(invoice.invoice_date)}</div>
                </div>
                <div>
                  <div className="text-muted-foreground">Due Date</div>
                  <div className="font-medium">{formatDate(invoice.due_date)}</div>
                </div>
                <div>
                  <div className="text-muted-foreground">Total Amount</div>
                  <div className="font-medium">{formatCurrency(invoice.total_amount)}</div>
                </div>
                <div>
                  <div className="text-muted-foreground">Balance Due</div>
                  <div className={`font-medium ${invoice.balance_due > 0 ? 'text-red-600' : 'text-green-600'}`}>
                    {formatCurrency(invoice.balance_due)}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Line Items */}
        <Card>
          <CardHeader>
            <CardTitle>Line Items</CardTitle>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Description</TableHead>
                  <TableHead className="text-right">Qty</TableHead>
                  <TableHead className="text-right">Unit Price</TableHead>
                  <TableHead className="text-right">Tax</TableHead>
                  <TableHead className="text-right">Amount</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {invoice.items?.map((item, index) => (
                  <TableRow key={index}>
                    <TableCell>{item.description}</TableCell>
                    <TableCell className="text-right">{item.quantity}</TableCell>
                    <TableCell className="text-right">{formatCurrency(item.unit_price)}</TableCell>
                    <TableCell className="text-right">{item.tax_rate}%</TableCell>
                    <TableCell className="text-right font-medium">{formatCurrency(item.amount)}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>

            {/* Totals */}
            <div className="mt-6 border-t pt-4">
              <div className="flex justify-end">
                <div className="w-64 space-y-2">
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Subtotal</span>
                    <span>{formatCurrency(subtotal)}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-muted-foreground">Tax</span>
                    <span>{formatCurrency(totalTax)}</span>
                  </div>
                  <div className="flex justify-between font-medium text-lg border-t pt-2">
                    <span>Total</span>
                    <span>{formatCurrency(invoice.total_amount)}</span>
                  </div>
                  {invoice.paid_amount > 0 && (
                    <>
                      <div className="flex justify-between text-sm text-green-600">
                        <span>Paid</span>
                        <span>-{formatCurrency(invoice.paid_amount)}</span>
                      </div>
                      <div className="flex justify-between font-medium text-lg border-t pt-2">
                        <span>Balance Due</span>
                        <span className={invoice.balance_due > 0 ? 'text-red-600' : 'text-green-600'}>
                          {formatCurrency(invoice.balance_due)}
                        </span>
                      </div>
                    </>
                  )}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Notes */}
        {invoice.notes && (
          <Card>
            <CardHeader>
              <CardTitle>Notes</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground whitespace-pre-wrap">{invoice.notes}</p>
            </CardContent>
          </Card>
        )}

        {/* Payment History */}
        {invoice.payments && invoice.payments.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>Payment History</CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Date</TableHead>
                    <TableHead>Reference</TableHead>
                    <TableHead>Method</TableHead>
                    <TableHead className="text-right">Amount</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {invoice.payments.map((payment, index) => (
                    <TableRow key={index}>
                      <TableCell>{formatDate(payment.payment_date)}</TableCell>
                      <TableCell>{payment.reference_number || '—'}</TableCell>
                      <TableCell className="capitalize">{payment.payment_method.replace('_', ' ')}</TableCell>
                      <TableCell className="text-right font-medium text-green-600">
                        {formatCurrency(payment.amount)}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        )}
      </div>
    </DashboardLayout>
  );
}
