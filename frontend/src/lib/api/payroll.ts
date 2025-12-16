/**
 * Payroll API
 */

import api from './client';
import type {
  PayrollRun,
  Payslip,
  SalaryStructure,
  TaxDeclaration,
  Form16,
  PayrollDashboardStats,
  PayrollComponent,
  PayrollListParams,
  PayslipListParams,
  PayrollRunStatus,
} from '@/types/payroll';

interface PaginatedResponse<T> {
  items: T[];
  total: number;
  skip: number;
  limit: number;
}

export const payrollApi = {
  // Dashboard
  getDashboardStats: async (): Promise<PayrollDashboardStats> => {
    return api.get<PayrollDashboardStats>('/payroll/dashboard');
  },

  // Payroll Runs
  getPayrollRuns: async (params?: PayrollListParams): Promise<PaginatedResponse<PayrollRun>> => {
    const searchParams: Record<string, string> = {};
    if (params?.status) searchParams.status = params.status;
    if (params?.year) searchParams.year = String(params.year);
    if (params?.skip !== undefined) searchParams.skip = String(params.skip);
    if (params?.limit !== undefined) searchParams.limit = String(params.limit);

    return api.get<PaginatedResponse<PayrollRun>>('/payroll/runs', { params: searchParams });
  },

  getPayrollRun: async (id: string): Promise<PayrollRun> => {
    return api.get<PayrollRun>(`/payroll/runs/${id}`);
  },

  createPayrollRun: async (month: number, year: number): Promise<PayrollRun> => {
    return api.post<PayrollRun>('/payroll/runs', { month, year });
  },

  processPayrollRun: async (id: string): Promise<PayrollRun> => {
    return api.post<PayrollRun>(`/payroll/runs/${id}/process`, {});
  },

  approvePayrollRun: async (id: string): Promise<PayrollRun> => {
    return api.post<PayrollRun>(`/payroll/runs/${id}/approve`, {});
  },

  markAsPaid: async (id: string): Promise<PayrollRun> => {
    return api.post<PayrollRun>(`/payroll/runs/${id}/mark-paid`, {});
  },

  // Payslips
  getPayslips: async (params?: PayslipListParams): Promise<PaginatedResponse<Payslip>> => {
    const searchParams: Record<string, string> = {};
    if (params?.payroll_run_id) searchParams.payroll_run_id = params.payroll_run_id;
    if (params?.employee_id) searchParams.employee_id = params.employee_id;
    if (params?.month) searchParams.month = String(params.month);
    if (params?.year) searchParams.year = String(params.year);
    if (params?.skip !== undefined) searchParams.skip = String(params.skip);
    if (params?.limit !== undefined) searchParams.limit = String(params.limit);

    return api.get<PaginatedResponse<Payslip>>('/payroll/payslips', { params: searchParams });
  },

  getMyPayslips: async (year?: number): Promise<Payslip[]> => {
    const params = year ? { year: String(year) } : undefined;
    return api.get<Payslip[]>('/payroll/payslips/me', { params });
  },

  getPayslip: async (id: string): Promise<Payslip> => {
    return api.get<Payslip>(`/payroll/payslips/${id}`);
  },

  downloadPayslip: async (id: string): Promise<Blob> => {
    const token = localStorage.getItem('access_token');
    const response = await fetch(
      `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'}/payroll/payslips/${id}/download`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );

    if (!response.ok) {
      throw new Error('Failed to download payslip');
    }

    return response.blob();
  },

  // Salary Structures
  getSalaryStructures: async (employeeId?: string): Promise<SalaryStructure[]> => {
    const params = employeeId ? { employee_id: employeeId } : undefined;
    return api.get<SalaryStructure[]>('/payroll/salary-structures', { params });
  },

  getSalaryStructure: async (id: string): Promise<SalaryStructure> => {
    return api.get<SalaryStructure>(`/payroll/salary-structures/${id}`);
  },

  createSalaryStructure: async (data: Partial<SalaryStructure>): Promise<SalaryStructure> => {
    return api.post<SalaryStructure>('/payroll/salary-structures', data);
  },

  updateSalaryStructure: async (
    id: string,
    data: Partial<SalaryStructure>
  ): Promise<SalaryStructure> => {
    return api.patch<SalaryStructure>(`/payroll/salary-structures/${id}`, data);
  },

  // Tax Declarations
  getMyTaxDeclaration: async (financialYear?: string): Promise<TaxDeclaration> => {
    const params = financialYear ? { financial_year: financialYear } : undefined;
    return api.get<TaxDeclaration>('/payroll/tax-declarations/me', { params });
  },

  updateTaxDeclaration: async (data: Partial<TaxDeclaration>): Promise<TaxDeclaration> => {
    return api.put<TaxDeclaration>('/payroll/tax-declarations/me', data);
  },

  submitTaxDeclaration: async (): Promise<TaxDeclaration> => {
    return api.post<TaxDeclaration>('/payroll/tax-declarations/me/submit', {});
  },

  // Form 16
  getMyForm16: async (financialYear: string): Promise<Form16> => {
    return api.get<Form16>('/payroll/form16/me', { params: { financial_year: financialYear } });
  },

  downloadForm16: async (financialYear: string): Promise<Blob> => {
    const token = localStorage.getItem('access_token');
    const response = await fetch(
      `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'}/payroll/form16/me/download?financial_year=${financialYear}`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );

    if (!response.ok) {
      throw new Error('Failed to download Form 16');
    }

    return response.blob();
  },

  // Payroll Components (Settings)
  getPayrollComponents: async (): Promise<PayrollComponent[]> => {
    return api.get<PayrollComponent[]>('/payroll/components');
  },

  createPayrollComponent: async (data: Partial<PayrollComponent>): Promise<PayrollComponent> => {
    return api.post<PayrollComponent>('/payroll/components', data);
  },

  updatePayrollComponent: async (
    id: string,
    data: Partial<PayrollComponent>
  ): Promise<PayrollComponent> => {
    return api.patch<PayrollComponent>(`/payroll/components/${id}`, data);
  },

  togglePayrollComponent: async (id: string, isActive: boolean): Promise<PayrollComponent> => {
    return api.patch<PayrollComponent>(`/payroll/components/${id}`, { is_active: isActive });
  },
};

export default payrollApi;
