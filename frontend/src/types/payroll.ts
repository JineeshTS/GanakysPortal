/**
 * Payroll Types
 */

export type PayrollRunStatus = 'draft' | 'processing' | 'completed' | 'approved' | 'paid';
export type PaymentMode = 'bank_transfer' | 'cheque' | 'cash';
export type TaxRegime = 'old' | 'new';

export interface PayrollRun {
  id: string;
  month: number;
  year: number;
  status: PayrollRunStatus;
  run_date: string;
  total_gross: number;
  total_deductions: number;
  total_net: number;
  employee_count: number;
  processed_by?: string;
  processed_at?: string;
  approved_by?: string;
  approved_at?: string;
  paid_at?: string;
  created_at: string;
  updated_at: string;
}

export interface Payslip {
  id: string;
  payroll_run_id: string;
  employee_id: string;
  employee_name: string;
  employee_code: string;
  month: number;
  year: number;
  working_days: number;
  days_worked: number;
  lop_days: number;

  // Earnings
  basic_salary: number;
  hra: number;
  special_allowance: number;
  other_earnings: number;
  gross_salary: number;

  // Deductions
  pf_employee: number;
  pf_employer: number;
  esi_employee: number;
  esi_employer: number;
  professional_tax: number;
  tds: number;
  other_deductions: number;
  total_deductions: number;

  net_salary: number;
  payment_mode: PaymentMode;
  bank_name?: string;
  account_number?: string;
  payment_reference?: string;
  paid_at?: string;

  created_at: string;
}

export interface SalaryStructure {
  id: string;
  employee_id: string;
  employee_name?: string;
  employee_code?: string;
  effective_from: string;
  effective_to?: string;
  basic_salary: number;
  hra_percentage: number;
  special_allowance: number;
  other_allowances: Record<string, number>;
  pf_applicable: boolean;
  esi_applicable: boolean;
  tax_regime: TaxRegime;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface TaxDeclaration {
  id: string;
  employee_id: string;
  financial_year: string;
  tax_regime: TaxRegime;
  section_80c: number;
  section_80d: number;
  section_80g: number;
  hra_exemption: number;
  lta_exemption: number;
  other_exemptions: Record<string, number>;
  total_investments: number;
  status: 'draft' | 'submitted' | 'verified';
  verified_by?: string;
  verified_at?: string;
  created_at: string;
  updated_at: string;
}

export interface Form16 {
  id: string;
  employee_id: string;
  employee_name: string;
  employee_code: string;
  financial_year: string;
  total_income: number;
  total_deductions: number;
  taxable_income: number;
  tax_payable: number;
  tds_deducted: number;
  generated_at: string;
  download_url: string;
}

export interface PayrollDashboardStats {
  current_month_payroll: number;
  pending_approvals: number;
  employees_paid: number;
  total_employees: number;
  ytd_payroll: number;
  average_salary: number;
}

export interface PayrollComponent {
  id: string;
  name: string;
  code: string;
  type: 'earning' | 'deduction';
  calculation_type: 'fixed' | 'percentage' | 'formula';
  value?: number;
  percentage_of?: string;
  is_taxable: boolean;
  is_active: boolean;
}

export interface PayrollListParams {
  status?: PayrollRunStatus;
  year?: number;
  skip?: number;
  limit?: number;
}

export interface PayslipListParams {
  payroll_run_id?: string;
  employee_id?: string;
  month?: number;
  year?: number;
  skip?: number;
  limit?: number;
}
