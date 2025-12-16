/**
 * Accounting Types
 */

export type CustomerType = 'corporate' | 'individual';
export type VendorType = 'supplier' | 'service_provider' | 'contractor';
export type InvoiceStatus = 'draft' | 'sent' | 'partially_paid' | 'paid' | 'overdue' | 'cancelled';
export type BillStatus = 'pending' | 'approved' | 'partially_paid' | 'paid' | 'cancelled';
export type PaymentMode = 'bank_transfer' | 'cheque' | 'cash' | 'upi' | 'card';
export type TransactionType = 'debit' | 'credit';

export interface Customer {
  id: string;
  code: string;
  name: string;
  type: CustomerType;
  email?: string;
  phone?: string;
  gstin?: string;
  pan?: string;
  billing_address?: string;
  shipping_address?: string;
  credit_limit: number;
  credit_days: number;
  outstanding_amount: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Vendor {
  id: string;
  code: string;
  name: string;
  type: VendorType;
  email?: string;
  phone?: string;
  gstin?: string;
  pan?: string;
  address?: string;
  bank_name?: string;
  account_number?: string;
  ifsc_code?: string;
  payment_terms: number;
  outstanding_amount: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Invoice {
  id: string;
  invoice_number: string;
  customer_id: string;
  customer_name?: string;
  invoice_date: string;
  due_date: string;
  subtotal: number;
  tax_amount: number;
  discount_amount: number;
  total_amount: number;
  paid_amount: number;
  balance_amount: number;
  status: InvoiceStatus;
  currency: string;
  notes?: string;
  items: InvoiceItem[];
  created_at: string;
  updated_at: string;
}

export interface InvoiceItem {
  id: string;
  invoice_id: string;
  description: string;
  hsn_sac_code?: string;
  quantity: number;
  unit_price: number;
  discount_percent: number;
  tax_percent: number;
  amount: number;
}

export interface Bill {
  id: string;
  bill_number: string;
  vendor_id: string;
  vendor_name?: string;
  bill_date: string;
  due_date: string;
  subtotal: number;
  tax_amount: number;
  total_amount: number;
  paid_amount: number;
  balance_amount: number;
  status: BillStatus;
  currency: string;
  notes?: string;
  items: BillItem[];
  created_at: string;
  updated_at: string;
}

export interface BillItem {
  id: string;
  bill_id: string;
  description: string;
  hsn_sac_code?: string;
  quantity: number;
  unit_price: number;
  tax_percent: number;
  amount: number;
}

export interface Payment {
  id: string;
  payment_number: string;
  payment_type: 'receipt' | 'payment';
  party_type: 'customer' | 'vendor';
  party_id: string;
  party_name?: string;
  payment_date: string;
  amount: number;
  payment_mode: PaymentMode;
  reference_number?: string;
  notes?: string;
  invoice_id?: string;
  bill_id?: string;
  created_at: string;
}

export interface Expense {
  id: string;
  expense_number: string;
  category: string;
  vendor_id?: string;
  vendor_name?: string;
  expense_date: string;
  amount: number;
  tax_amount: number;
  total_amount: number;
  payment_mode?: PaymentMode;
  description?: string;
  receipt_path?: string;
  status: 'pending' | 'approved' | 'rejected' | 'paid';
  submitted_by?: string;
  approved_by?: string;
  created_at: string;
}

export interface AccountingDashboardStats {
  total_receivables: number;
  total_payables: number;
  revenue_this_month: number;
  expenses_this_month: number;
  overdue_invoices: number;
  pending_bills: number;
  cash_balance: number;
  bank_balance: number;
}

export interface ChartOfAccount {
  id: string;
  code: string;
  name: string;
  type: 'asset' | 'liability' | 'equity' | 'income' | 'expense';
  parent_id?: string;
  is_group: boolean;
  balance: number;
  is_active: boolean;
}

export interface JournalEntry {
  id: string;
  entry_number: string;
  entry_date: string;
  narration: string;
  total_debit: number;
  total_credit: number;
  status: 'draft' | 'posted' | 'reversed';
  lines: JournalLine[];
  created_by?: string;
  created_at: string;
}

export interface JournalLine {
  id: string;
  account_id: string;
  account_name?: string;
  account_code?: string;
  debit_amount: number;
  credit_amount: number;
  narration?: string;
}

export interface ListParams {
  search?: string;
  status?: string;
  start_date?: string;
  end_date?: string;
  skip?: number;
  limit?: number;
}
