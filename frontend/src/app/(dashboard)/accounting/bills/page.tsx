'use client';

/**
 * Bills List Page
 */

import { useState, useEffect, useCallback } from 'react';
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
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Badge } from '@/components/ui/badge';
import accountingApi from '@/lib/api/accounting';
import type { Bill, BillStatus, Vendor } from '@/types/accounting';

const statusColors: Record<BillStatus, string> = {
  draft: 'bg-gray-100 text-gray-800',
  pending: 'bg-yellow-100 text-yellow-800',
  approved: 'bg-blue-100 text-blue-800',
  partially_paid: 'bg-orange-100 text-orange-800',
  paid: 'bg-green-100 text-green-800',
  overdue: 'bg-red-100 text-red-800',
};

export default function BillsPage() {
  const [bills, setBills] = useState<Bill[]>([]);
  const [vendors, setVendors] = useState<Vendor[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [total, setTotal] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 10;

  // Dialog state
  const [dialogOpen, setDialogOpen] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  // Form state
  const [formData, setFormData] = useState({
    vendor_id: '',
    bill_number: '',
    bill_date: new Date().toISOString().split('T')[0],
    due_date: '',
    description: '',
    amount: 0,
    tax_amount: 0,
  });

  const loadData = useCallback(async () => {
    setIsLoading(true);
    try {
      const [billsData, vendorsData] = await Promise.all([
        accountingApi.getBills({
          search: searchQuery || undefined,
          status: (statusFilter as BillStatus) || undefined,
          skip: (currentPage - 1) * pageSize,
          limit: pageSize,
        }),
        accountingApi.getVendors({ limit: 100 }),
      ]);
      setBills(billsData.items);
      setTotal(billsData.total);
      setVendors(vendorsData.items);
    } catch (error) {
      console.error('Failed to load data:', error);
    } finally {
      setIsLoading(false);
    }
  }, [searchQuery, statusFilter, currentPage]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleOpenDialog = () => {
    setFormData({
      vendor_id: '',
      bill_number: '',
      bill_date: new Date().toISOString().split('T')[0],
      due_date: '',
      description: '',
      amount: 0,
      tax_amount: 0,
    });
    setDialogOpen(true);
  };

  const handleSave = async () => {
    setIsSaving(true);
    try {
      await accountingApi.createBill({
        ...formData,
        total_amount: formData.amount + formData.tax_amount,
      });
      setDialogOpen(false);
      loadData();
    } catch (error) {
      console.error('Failed to create bill:', error);
    } finally {
      setIsSaving(false);
    }
  };

  const handleApproveBill = async (id: string) => {
    try {
      await accountingApi.approveBill(id);
      loadData();
    } catch (error) {
      console.error('Failed to approve bill:', error);
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
      month: 'short',
      year: 'numeric',
    });
  };

  const totalPages = Math.ceil(total / pageSize);

  return (
    <DashboardLayout>
      <div className="space-y-6">
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
              <h1 className="text-2xl font-bold tracking-tight">Bills</h1>
              <p className="text-muted-foreground">
                Manage vendor bills and payables
              </p>
            </div>
          </div>
          <Button onClick={handleOpenDialog}>
            <svg className="mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            Add Bill
          </Button>
        </div>

        {/* Filters */}
        <div className="flex gap-4">
          <div className="flex-1 max-w-sm">
            <Input
              placeholder="Search bills..."
              value={searchQuery}
              onChange={(e) => {
                setSearchQuery(e.target.value);
                setCurrentPage(1);
              }}
            />
          </div>
          <Select
            value={statusFilter}
            onValueChange={(v) => {
              setStatusFilter(v);
              setCurrentPage(1);
            }}
          >
            <SelectTrigger className="w-[150px]">
              <SelectValue placeholder="All Status" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="">All Status</SelectItem>
              <SelectItem value="draft">Draft</SelectItem>
              <SelectItem value="pending">Pending</SelectItem>
              <SelectItem value="approved">Approved</SelectItem>
              <SelectItem value="partially_paid">Partially Paid</SelectItem>
              <SelectItem value="paid">Paid</SelectItem>
              <SelectItem value="overdue">Overdue</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Table */}
        <div className="rounded-lg border bg-card">
          {isLoading ? (
            <div className="p-8 text-center">
              <div className="h-8 w-8 mx-auto animate-spin rounded-full border-4 border-primary border-t-transparent" />
              <p className="mt-2 text-muted-foreground">Loading bills...</p>
            </div>
          ) : bills.length === 0 ? (
            <div className="p-8 text-center">
              <svg className="mx-auto h-12 w-12 text-muted-foreground" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
              </svg>
              <h3 className="mt-2 font-medium">No bills found</h3>
              <p className="text-sm text-muted-foreground">
                {searchQuery || statusFilter ? 'Try adjusting your filters' : 'Add your first vendor bill'}
              </p>
              {!searchQuery && !statusFilter && (
                <Button className="mt-4" onClick={handleOpenDialog}>
                  Add Bill
                </Button>
              )}
            </div>
          ) : (
            <>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Bill #</TableHead>
                    <TableHead>Vendor</TableHead>
                    <TableHead>Date</TableHead>
                    <TableHead>Due Date</TableHead>
                    <TableHead className="text-right">Amount</TableHead>
                    <TableHead className="text-right">Balance</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {bills.map((bill) => (
                    <TableRow key={bill.id}>
                      <TableCell className="font-mono font-medium">{bill.bill_number}</TableCell>
                      <TableCell>{bill.vendor_name}</TableCell>
                      <TableCell>{formatDate(bill.bill_date)}</TableCell>
                      <TableCell>{formatDate(bill.due_date)}</TableCell>
                      <TableCell className="text-right font-medium">
                        {formatCurrency(bill.total_amount)}
                      </TableCell>
                      <TableCell className="text-right">
                        <span className={bill.balance_due > 0 ? 'text-orange-600 font-medium' : 'text-green-600'}>
                          {formatCurrency(bill.balance_due)}
                        </span>
                      </TableCell>
                      <TableCell>
                        <Badge variant="secondary" className={statusColors[bill.status]}>
                          {bill.status === 'partially_paid' ? 'Partial' : bill.status.charAt(0).toUpperCase() + bill.status.slice(1)}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-right">
                        <div className="flex justify-end gap-1">
                          {bill.status === 'pending' && (
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleApproveBill(bill.id)}
                            >
                              Approve
                            </Button>
                          )}
                          {(bill.status === 'approved' || bill.status === 'overdue' || bill.status === 'partially_paid') && (
                            <Link href={`/accounting/payments/new?bill=${bill.id}`}>
                              <Button variant="ghost" size="sm">
                                Pay
                              </Button>
                            </Link>
                          )}
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>

              {/* Pagination */}
              {totalPages > 1 && (
                <div className="flex items-center justify-between border-t px-4 py-3">
                  <div className="text-sm text-muted-foreground">
                    Showing {(currentPage - 1) * pageSize + 1} to {Math.min(currentPage * pageSize, total)} of {total}
                  </div>
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                      disabled={currentPage === 1}
                    >
                      Previous
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
                      disabled={currentPage === totalPages}
                    >
                      Next
                    </Button>
                  </div>
                </div>
              )}
            </>
          )}
        </div>

        {/* Add Bill Dialog */}
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogContent className="max-w-lg">
            <DialogHeader>
              <DialogTitle>Add Bill</DialogTitle>
              <DialogDescription>Record a new vendor bill</DialogDescription>
            </DialogHeader>

            <div className="grid gap-4 py-4">
              <div className="space-y-2">
                <Label htmlFor="vendor">Vendor *</Label>
                <Select
                  value={formData.vendor_id}
                  onValueChange={(v) => setFormData({ ...formData, vendor_id: v })}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Select vendor" />
                  </SelectTrigger>
                  <SelectContent>
                    {vendors.map((vendor) => (
                      <SelectItem key={vendor.id} value={vendor.id}>
                        {vendor.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="bill_number">Bill Number *</Label>
                  <Input
                    id="bill_number"
                    value={formData.bill_number}
                    onChange={(e) => setFormData({ ...formData, bill_number: e.target.value })}
                    placeholder="Vendor invoice number"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="bill_date">Bill Date</Label>
                  <Input
                    id="bill_date"
                    type="date"
                    value={formData.bill_date}
                    onChange={(e) => setFormData({ ...formData, bill_date: e.target.value })}
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="due_date">Due Date</Label>
                <Input
                  id="due_date"
                  type="date"
                  value={formData.due_date}
                  onChange={(e) => setFormData({ ...formData, due_date: e.target.value })}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="description">Description</Label>
                <Input
                  id="description"
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  placeholder="Bill description"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="amount">Amount *</Label>
                  <Input
                    id="amount"
                    type="number"
                    value={formData.amount}
                    onChange={(e) => setFormData({ ...formData, amount: parseFloat(e.target.value) || 0 })}
                    min={0}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="tax_amount">Tax Amount</Label>
                  <Input
                    id="tax_amount"
                    type="number"
                    value={formData.tax_amount}
                    onChange={(e) => setFormData({ ...formData, tax_amount: parseFloat(e.target.value) || 0 })}
                    min={0}
                  />
                </div>
              </div>

              <div className="text-right border-t pt-4">
                <div className="text-sm text-muted-foreground">Total Amount</div>
                <div className="text-xl font-bold">
                  {formatCurrency(formData.amount + formData.tax_amount)}
                </div>
              </div>
            </div>

            <DialogFooter>
              <Button variant="outline" onClick={() => setDialogOpen(false)} disabled={isSaving}>
                Cancel
              </Button>
              <Button
                onClick={handleSave}
                disabled={isSaving || !formData.vendor_id || !formData.bill_number || formData.amount <= 0}
              >
                {isSaving ? 'Saving...' : 'Add Bill'}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>
    </DashboardLayout>
  );
}
