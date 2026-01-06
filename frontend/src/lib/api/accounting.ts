/**
 * Accounting API
 */

import api from './client';
import type {
  Customer,
  Vendor,
  Invoice,
  Bill,
  Payment,
  Expense,
  AccountingDashboardStats,
  ChartOfAccount,
  JournalEntry,
  ListParams,
  InvoiceStatus,
  BillStatus,
} from '@/types/accounting';

interface PaginatedResponse<T> {
  items: T[];
  total: number;
  skip: number;
  limit: number;
}

export const accountingApi = {
  // Dashboard
  getDashboardStats: async (): Promise<AccountingDashboardStats> => {
    return api.get<AccountingDashboardStats>('/accounting/dashboard');
  },

  // Customers
  getCustomers: async (params?: ListParams): Promise<PaginatedResponse<Customer>> => {
    const searchParams: Record<string, string> = {};
    if (params?.search) searchParams.search = params.search;
    if (params?.skip !== undefined) searchParams.skip = String(params.skip);
    if (params?.limit !== undefined) searchParams.limit = String(params.limit);
    return api.get<PaginatedResponse<Customer>>('/accounting/customers', { params: searchParams });
  },

  getCustomer: async (id: string): Promise<Customer> => {
    return api.get<Customer>(`/accounting/customers/${id}`);
  },

  createCustomer: async (data: Partial<Customer>): Promise<Customer> => {
    return api.post<Customer>('/accounting/customers', data);
  },

  updateCustomer: async (id: string, data: Partial<Customer>): Promise<Customer> => {
    return api.patch<Customer>(`/accounting/customers/${id}`, data);
  },

  // Vendors
  getVendors: async (params?: ListParams): Promise<PaginatedResponse<Vendor>> => {
    const searchParams: Record<string, string> = {};
    if (params?.search) searchParams.search = params.search;
    if (params?.skip !== undefined) searchParams.skip = String(params.skip);
    if (params?.limit !== undefined) searchParams.limit = String(params.limit);
    return api.get<PaginatedResponse<Vendor>>('/accounting/vendors', { params: searchParams });
  },

  getVendor: async (id: string): Promise<Vendor> => {
    return api.get<Vendor>(`/accounting/vendors/${id}`);
  },

  createVendor: async (data: Partial<Vendor>): Promise<Vendor> => {
    return api.post<Vendor>('/accounting/vendors', data);
  },

  updateVendor: async (id: string, data: Partial<Vendor>): Promise<Vendor> => {
    return api.patch<Vendor>(`/accounting/vendors/${id}`, data);
  },

  // Invoices
  getInvoices: async (params?: ListParams & { status?: InvoiceStatus }): Promise<PaginatedResponse<Invoice>> => {
    const searchParams: Record<string, string> = {};
    if (params?.search) searchParams.search = params.search;
    if (params?.status) searchParams.status = params.status;
    if (params?.start_date) searchParams.start_date = params.start_date;
    if (params?.end_date) searchParams.end_date = params.end_date;
    if (params?.skip !== undefined) searchParams.skip = String(params.skip);
    if (params?.limit !== undefined) searchParams.limit = String(params.limit);
    return api.get<PaginatedResponse<Invoice>>('/accounting/invoices', { params: searchParams });
  },

  getInvoice: async (id: string): Promise<Invoice> => {
    return api.get<Invoice>(`/accounting/invoices/${id}`);
  },

  createInvoice: async (data: Partial<Invoice>): Promise<Invoice> => {
    return api.post<Invoice>('/accounting/invoices', data);
  },

  updateInvoice: async (id: string, data: Partial<Invoice>): Promise<Invoice> => {
    return api.patch<Invoice>(`/accounting/invoices/${id}`, data);
  },

  sendInvoice: async (id: string): Promise<Invoice> => {
    return api.post<Invoice>(`/accounting/invoices/${id}/send`, {});
  },

  downloadInvoice: async (id: string): Promise<Blob> => {
    return api.downloadBlob(`/accounting/invoices/${id}/download`);
  },

  // Bills
  getBills: async (params?: ListParams & { status?: BillStatus }): Promise<PaginatedResponse<Bill>> => {
    const searchParams: Record<string, string> = {};
    if (params?.search) searchParams.search = params.search;
    if (params?.status) searchParams.status = params.status;
    if (params?.start_date) searchParams.start_date = params.start_date;
    if (params?.end_date) searchParams.end_date = params.end_date;
    if (params?.skip !== undefined) searchParams.skip = String(params.skip);
    if (params?.limit !== undefined) searchParams.limit = String(params.limit);
    return api.get<PaginatedResponse<Bill>>('/accounting/bills', { params: searchParams });
  },

  getBill: async (id: string): Promise<Bill> => {
    return api.get<Bill>(`/accounting/bills/${id}`);
  },

  createBill: async (data: Partial<Bill>): Promise<Bill> => {
    return api.post<Bill>('/accounting/bills', data);
  },

  approveBill: async (id: string): Promise<Bill> => {
    return api.post<Bill>(`/accounting/bills/${id}/approve`, {});
  },

  // Payments
  getPayments: async (params?: ListParams): Promise<PaginatedResponse<Payment>> => {
    const searchParams: Record<string, string> = {};
    if (params?.start_date) searchParams.start_date = params.start_date;
    if (params?.end_date) searchParams.end_date = params.end_date;
    if (params?.skip !== undefined) searchParams.skip = String(params.skip);
    if (params?.limit !== undefined) searchParams.limit = String(params.limit);
    return api.get<PaginatedResponse<Payment>>('/accounting/payments', { params: searchParams });
  },

  createPayment: async (data: Partial<Payment>): Promise<Payment> => {
    return api.post<Payment>('/accounting/payments', data);
  },

  // Expenses
  getExpenses: async (params?: ListParams): Promise<PaginatedResponse<Expense>> => {
    const searchParams: Record<string, string> = {};
    if (params?.search) searchParams.search = params.search;
    if (params?.status) searchParams.status = params.status;
    if (params?.start_date) searchParams.start_date = params.start_date;
    if (params?.end_date) searchParams.end_date = params.end_date;
    if (params?.skip !== undefined) searchParams.skip = String(params.skip);
    if (params?.limit !== undefined) searchParams.limit = String(params.limit);
    return api.get<PaginatedResponse<Expense>>('/accounting/expenses', { params: searchParams });
  },

  getExpense: async (id: string): Promise<Expense> => {
    return api.get<Expense>(`/accounting/expenses/${id}`);
  },

  createExpense: async (data: Partial<Expense>): Promise<Expense> => {
    return api.post<Expense>('/accounting/expenses', data);
  },

  approveExpense: async (id: string): Promise<Expense> => {
    return api.post<Expense>(`/accounting/expenses/${id}/approve`, {});
  },

  // Chart of Accounts
  getChartOfAccounts: async (): Promise<ChartOfAccount[]> => {
    return api.get<ChartOfAccount[]>('/accounting/chart-of-accounts');
  },

  // Journal Entries
  getJournalEntries: async (params?: ListParams): Promise<PaginatedResponse<JournalEntry>> => {
    const searchParams: Record<string, string> = {};
    if (params?.start_date) searchParams.start_date = params.start_date;
    if (params?.end_date) searchParams.end_date = params.end_date;
    if (params?.skip !== undefined) searchParams.skip = String(params.skip);
    if (params?.limit !== undefined) searchParams.limit = String(params.limit);
    return api.get<PaginatedResponse<JournalEntry>>('/accounting/journal-entries', { params: searchParams });
  },

  createJournalEntry: async (data: Partial<JournalEntry>): Promise<JournalEntry> => {
    return api.post<JournalEntry>('/accounting/journal-entries', data);
  },

  postJournalEntry: async (id: string): Promise<JournalEntry> => {
    return api.post<JournalEntry>(`/accounting/journal-entries/${id}/post`, {});
  },

  // Reports
  getTrialBalance: async (asOfDate?: string): Promise<ChartOfAccount[]> => {
    const params = asOfDate ? { as_of_date: asOfDate } : undefined;
    return api.get<ChartOfAccount[]>('/accounting/reports/trial-balance', { params });
  },

  getProfitLoss: async (startDate: string, endDate: string): Promise<Record<string, number>> => {
    return api.get<Record<string, number>>('/accounting/reports/profit-loss', {
      params: { start_date: startDate, end_date: endDate },
    });
  },

  getBalanceSheet: async (asOfDate: string): Promise<Record<string, unknown>> => {
    return api.get<Record<string, unknown>>('/accounting/reports/balance-sheet', {
      params: { as_of_date: asOfDate },
    });
  },

  getAgingReport: async (type: 'receivables' | 'payables'): Promise<unknown[]> => {
    return api.get<unknown[]>(`/accounting/reports/aging/${type}`);
  },
};

export default accountingApi;
