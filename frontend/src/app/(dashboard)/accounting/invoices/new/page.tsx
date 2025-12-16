'use client';

/**
 * Create Invoice Page
 */

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { DashboardLayout } from '@/components/layout/dashboard-layout';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
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
import type { Customer, InvoiceItem } from '@/types/accounting';

interface LineItem extends Omit<InvoiceItem, 'id' | 'invoice_id'> {
  key: string;
}

export default function NewInvoicePage() {
  const router = useRouter();
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);

  // Form state
  const [customerId, setCustomerId] = useState('');
  const [invoiceDate, setInvoiceDate] = useState(new Date().toISOString().split('T')[0]);
  const [dueDate, setDueDate] = useState('');
  const [notes, setNotes] = useState('');
  const [items, setItems] = useState<LineItem[]>([
    { key: '1', description: '', quantity: 1, unit_price: 0, tax_rate: 18, amount: 0 },
  ]);

  useEffect(() => {
    const loadCustomers = async () => {
      try {
        const data = await accountingApi.getCustomers({ limit: 100 });
        setCustomers(data.items);
      } catch (error) {
        console.error('Failed to load customers:', error);
      } finally {
        setIsLoading(false);
      }
    };
    loadCustomers();
  }, []);

  // Calculate due date based on customer payment terms
  useEffect(() => {
    const customer = customers.find((c) => c.id === customerId);
    if (customer && invoiceDate) {
      const date = new Date(invoiceDate);
      date.setDate(date.getDate() + (customer.payment_terms || 30));
      setDueDate(date.toISOString().split('T')[0]);
    }
  }, [customerId, invoiceDate, customers]);

  const calculateItemAmount = (item: LineItem) => {
    const subtotal = item.quantity * item.unit_price;
    const tax = subtotal * (item.tax_rate / 100);
    return subtotal + tax;
  };

  const updateItem = (key: string, field: keyof LineItem, value: string | number) => {
    setItems((prev) =>
      prev.map((item) => {
        if (item.key !== key) return item;
        const updated = { ...item, [field]: value };
        updated.amount = calculateItemAmount(updated);
        return updated;
      })
    );
  };

  const addItem = () => {
    setItems((prev) => [
      ...prev,
      { key: String(Date.now()), description: '', quantity: 1, unit_price: 0, tax_rate: 18, amount: 0 },
    ]);
  };

  const removeItem = (key: string) => {
    if (items.length > 1) {
      setItems((prev) => prev.filter((item) => item.key !== key));
    }
  };

  const subtotal = items.reduce((sum, item) => sum + item.quantity * item.unit_price, 0);
  const totalTax = items.reduce((sum, item) => sum + item.quantity * item.unit_price * (item.tax_rate / 100), 0);
  const total = subtotal + totalTax;

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const handleSave = async (asDraft: boolean) => {
    if (!customerId || items.every((i) => !i.description)) {
      return;
    }

    setIsSaving(true);
    try {
      const invoice = await accountingApi.createInvoice({
        customer_id: customerId,
        invoice_date: invoiceDate,
        due_date: dueDate,
        notes,
        items: items.filter((i) => i.description).map(({ key, ...item }) => item),
      });

      if (!asDraft) {
        await accountingApi.sendInvoice(invoice.id);
      }

      router.push('/accounting/invoices');
    } catch (error) {
      console.error('Failed to create invoice:', error);
    } finally {
      setIsSaving(false);
    }
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

  return (
    <DashboardLayout>
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center gap-4">
          <Link href="/accounting/invoices">
            <Button variant="ghost" size="icon">
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
            </Button>
          </Link>
          <div>
            <h1 className="text-2xl font-bold tracking-tight">New Invoice</h1>
            <p className="text-muted-foreground">Create a new sales invoice</p>
          </div>
        </div>

        {/* Customer & Dates */}
        <Card>
          <CardHeader>
            <CardTitle>Invoice Details</CardTitle>
            <CardDescription>Select customer and set invoice dates</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-3">
              <div className="space-y-2">
                <Label htmlFor="customer">Customer *</Label>
                <Select value={customerId} onValueChange={setCustomerId}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select customer" />
                  </SelectTrigger>
                  <SelectContent>
                    {customers.map((customer) => (
                      <SelectItem key={customer.id} value={customer.id}>
                        {customer.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="invoice_date">Invoice Date</Label>
                <Input
                  id="invoice_date"
                  type="date"
                  value={invoiceDate}
                  onChange={(e) => setInvoiceDate(e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="due_date">Due Date</Label>
                <Input
                  id="due_date"
                  type="date"
                  value={dueDate}
                  onChange={(e) => setDueDate(e.target.value)}
                />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Line Items */}
        <Card>
          <CardHeader>
            <CardTitle>Line Items</CardTitle>
            <CardDescription>Add products or services to the invoice</CardDescription>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-[40%]">Description</TableHead>
                  <TableHead className="w-[12%]">Qty</TableHead>
                  <TableHead className="w-[15%]">Unit Price</TableHead>
                  <TableHead className="w-[12%]">Tax %</TableHead>
                  <TableHead className="w-[15%] text-right">Amount</TableHead>
                  <TableHead className="w-[6%]"></TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {items.map((item) => (
                  <TableRow key={item.key}>
                    <TableCell>
                      <Input
                        value={item.description}
                        onChange={(e) => updateItem(item.key, 'description', e.target.value)}
                        placeholder="Item description"
                      />
                    </TableCell>
                    <TableCell>
                      <Input
                        type="number"
                        value={item.quantity}
                        onChange={(e) => updateItem(item.key, 'quantity', parseInt(e.target.value) || 0)}
                        min={1}
                      />
                    </TableCell>
                    <TableCell>
                      <Input
                        type="number"
                        value={item.unit_price}
                        onChange={(e) => updateItem(item.key, 'unit_price', parseFloat(e.target.value) || 0)}
                        min={0}
                      />
                    </TableCell>
                    <TableCell>
                      <Select
                        value={String(item.tax_rate)}
                        onValueChange={(v) => updateItem(item.key, 'tax_rate', parseInt(v))}
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="0">0%</SelectItem>
                          <SelectItem value="5">5%</SelectItem>
                          <SelectItem value="12">12%</SelectItem>
                          <SelectItem value="18">18%</SelectItem>
                          <SelectItem value="28">28%</SelectItem>
                        </SelectContent>
                      </Select>
                    </TableCell>
                    <TableCell className="text-right font-medium">
                      {formatCurrency(item.amount)}
                    </TableCell>
                    <TableCell>
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => removeItem(item.key)}
                        disabled={items.length === 1}
                      >
                        <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>

            <Button variant="outline" className="mt-4" onClick={addItem}>
              <svg className="mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
              Add Line Item
            </Button>

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
                    <span>{formatCurrency(total)}</span>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Notes */}
        <Card>
          <CardHeader>
            <CardTitle>Notes</CardTitle>
            <CardDescription>Additional notes or terms (optional)</CardDescription>
          </CardHeader>
          <CardContent>
            <textarea
              className="w-full min-h-[100px] rounded-md border border-input bg-background px-3 py-2 text-sm"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Payment terms, bank details, or any other notes..."
            />
          </CardContent>
        </Card>

        {/* Actions */}
        <div className="flex justify-end gap-4">
          <Link href="/accounting/invoices">
            <Button variant="outline">Cancel</Button>
          </Link>
          <Button
            variant="outline"
            onClick={() => handleSave(true)}
            disabled={isSaving || !customerId}
          >
            {isSaving ? 'Saving...' : 'Save as Draft'}
          </Button>
          <Button onClick={() => handleSave(false)} disabled={isSaving || !customerId}>
            {isSaving ? 'Creating...' : 'Create & Send'}
          </Button>
        </div>
      </div>
    </DashboardLayout>
  );
}
