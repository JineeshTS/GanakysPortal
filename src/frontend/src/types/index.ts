// GanaPortal Type Definitions - India ERP
// FE-001: Core Types

// ============================================================================
// Base Types
// ============================================================================

export interface BaseEntity {
  id: string
  created_at: string
  updated_at: string
  created_by?: string
  updated_by?: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface ApiResponse<T> {
  success: boolean
  data?: T
  error?: string
  message?: string
}

// ============================================================================
// Auth Types
// ============================================================================

export interface User extends BaseEntity {
  email: string
  full_name: string
  phone?: string
  role: UserRole
  company_id: string
  employee_id?: string
  is_active: boolean
  is_verified: boolean
  last_login?: string
  avatar_url?: string
  preferences?: UserPreferences
}

export type UserRole =
  | 'super_admin'
  | 'company_admin'
  | 'hr_manager'
  | 'hr_executive'
  | 'finance_manager'
  | 'accountant'
  | 'employee'
  | 'viewer'

export interface UserPreferences {
  theme: 'light' | 'dark' | 'system'
  language: 'en' | 'hi' | 'kn' | 'ta' | 'te'
  date_format: 'DD/MM/YYYY' | 'MM/DD/YYYY' | 'YYYY-MM-DD'
  timezone: string
  notifications: NotificationPreferences
}

export interface NotificationPreferences {
  email: boolean
  push: boolean
  sms: boolean
  payslip_generated: boolean
  leave_approved: boolean
  attendance_reminder: boolean
}

export interface LoginRequest {
  email: string
  password: string
  remember_me?: boolean
}

export interface LoginResponse {
  access_token: string
  refresh_token: string
  token_type: 'bearer'
  expires_in: number
  user: User
}

export interface RegisterRequest {
  email: string
  password: string
  full_name: string
  phone?: string
  company_name: string
  company_gstin?: string
}

// ============================================================================
// Company Types
// ============================================================================

export interface Company extends BaseEntity {
  name: string
  legal_name: string
  gstin?: string
  pan: string
  tan?: string
  cin?: string
  establishment_code?: string
  pf_number?: string
  esi_number?: string
  pt_number?: string

  address: Address
  contact_email: string
  contact_phone: string
  website?: string
  logo_url?: string

  financial_year_start: number // 1-12, typically 4 for April
  currency: 'INR'

  settings: CompanySettings
}

export interface CompanySettings {
  payroll_cycle: 'monthly' | 'weekly' | 'biweekly'
  pay_day: number // 1-31
  attendance_required: boolean
  approval_workflow: boolean
  pf_enabled: boolean
  esi_enabled: boolean
  pt_enabled: boolean
  tds_enabled: boolean
  auto_calculate_arrears: boolean
}

export interface Address {
  line1: string
  line2?: string
  city: string
  state: IndianState
  pincode: string
  country: 'India'
}

export type IndianState =
  | 'Andhra Pradesh' | 'Arunachal Pradesh' | 'Assam' | 'Bihar'
  | 'Chhattisgarh' | 'Goa' | 'Gujarat' | 'Haryana' | 'Himachal Pradesh'
  | 'Jharkhand' | 'Karnataka' | 'Kerala' | 'Madhya Pradesh' | 'Maharashtra'
  | 'Manipur' | 'Meghalaya' | 'Mizoram' | 'Nagaland' | 'Odisha'
  | 'Punjab' | 'Rajasthan' | 'Sikkim' | 'Tamil Nadu' | 'Telangana'
  | 'Tripura' | 'Uttar Pradesh' | 'Uttarakhand' | 'West Bengal'
  | 'Delhi' | 'Jammu and Kashmir' | 'Ladakh' | 'Puducherry'
  | 'Andaman and Nicobar Islands' | 'Chandigarh' | 'Dadra and Nagar Haveli'
  | 'Daman and Diu' | 'Lakshadweep'

// ============================================================================
// Employee Types
// ============================================================================

export interface Employee extends BaseEntity {
  employee_code: string
  user_id?: string
  company_id: string

  // Personal Info
  first_name: string
  middle_name?: string
  last_name: string
  full_name: string
  date_of_birth: string
  gender: 'male' | 'female' | 'other'
  blood_group?: BloodGroup
  marital_status: 'single' | 'married' | 'divorced' | 'widowed'
  father_name: string

  // Contact
  personal_email?: string
  work_email: string
  mobile: string
  emergency_contact?: EmergencyContact

  // Address
  current_address: Address
  permanent_address: Address

  // Employment
  department_id: string
  designation_id: string
  reporting_to?: string
  date_of_joining: string
  date_of_exit?: string
  employment_type: EmploymentType
  employment_status: EmploymentStatus
  probation_end_date?: string
  notice_period_days: number

  // Statutory
  pan: string
  aadhaar?: string
  uan?: string // Universal Account Number for PF
  pf_number?: string
  esi_number?: string

  // Bank
  bank_details: BankDetails

  // Salary
  salary_structure_id?: string
  ctc: number // Annual CTC

  // Documents
  photo_url?: string
  documents?: EmployeeDocument[]
}

export type BloodGroup = 'A+' | 'A-' | 'B+' | 'B-' | 'AB+' | 'AB-' | 'O+' | 'O-'

export type EmploymentType = 'full_time' | 'part_time' | 'contract' | 'intern' | 'consultant'

export type EmploymentStatus = 'active' | 'probation' | 'notice_period' | 'resigned' | 'terminated' | 'retired' | 'absconding'

export interface EmergencyContact {
  name: string
  relationship: string
  phone: string
}

export interface BankDetails {
  account_holder_name: string
  account_number: string
  bank_name: string
  branch_name: string
  ifsc_code: string
}

export interface EmployeeDocument {
  id: string
  type: DocumentType
  name: string
  url: string
  uploaded_at: string
  verified: boolean
}

export type DocumentType =
  | 'pan_card' | 'aadhaar_card' | 'passport' | 'driving_license'
  | 'offer_letter' | 'appointment_letter' | 'relieving_letter'
  | 'payslip' | 'form16' | 'education_certificate' | 'other'

// ============================================================================
// Department & Designation
// ============================================================================

export interface Department extends BaseEntity {
  name: string
  code: string
  description?: string
  parent_id?: string
  head_id?: string
  company_id: string
  is_active: boolean
  employee_count?: number
}

export interface Designation extends BaseEntity {
  name: string
  code: string
  description?: string
  level: number // For hierarchy
  department_id?: string
  company_id: string
  is_active: boolean
}

// ============================================================================
// Payroll Types
// ============================================================================

export interface SalaryStructure extends BaseEntity {
  name: string
  code: string
  description?: string
  company_id: string
  is_active: boolean
  components: SalaryComponent[]
  effective_from: string
}

export interface SalaryComponent {
  id: string
  name: string
  code: string
  type: 'earning' | 'deduction' | 'employer_contribution'
  calculation_type: 'fixed' | 'percentage' | 'formula'
  value: number
  percentage_of?: string // Component code for percentage calculation
  formula?: string
  is_taxable: boolean
  is_statutory: boolean
  statutory_type?: 'pf' | 'esi' | 'pt' | 'tds' | 'lwf'
}

export interface PayrollRun extends BaseEntity {
  company_id: string
  month: number // 1-12
  year: number
  status: PayrollStatus
  total_employees: number
  total_gross: number
  total_deductions: number
  total_net: number
  total_employer_cost: number
  processed_by?: string
  processed_at?: string
  approved_by?: string
  approved_at?: string
  paid_at?: string
}

export type PayrollStatus =
  | 'draft'
  | 'processing'
  | 'calculated'
  | 'pending_approval'
  | 'approved'
  | 'paid'
  | 'cancelled'

export interface PayrollEntry extends BaseEntity {
  payroll_run_id: string
  employee_id: string
  employee_name: string
  employee_code: string

  // Working Days
  working_days: number
  present_days: number
  paid_leaves: number
  unpaid_leaves: number
  holidays: number
  lop_days: number

  // Earnings
  basic: number
  hra: number
  special_allowance: number
  other_earnings: number
  arrears: number
  bonus: number
  total_earnings: number

  // Deductions
  pf_employee: number
  esi_employee: number
  pt: number
  tds: number
  other_deductions: number
  loan_recovery: number
  advance_recovery: number
  total_deductions: number

  // Employer Contributions
  pf_employer: number
  esi_employer: number
  total_employer_contribution: number

  // Net
  net_salary: number
  ctc_monthly: number

  // Status
  status: 'calculated' | 'approved' | 'paid'
}

// ============================================================================
// Leave Types
// ============================================================================

export interface LeavePolicy extends BaseEntity {
  name: string
  code: string
  company_id: string
  is_active: boolean
  leave_types: LeaveType[]
}

export interface LeaveType {
  id: string
  name: string
  code: string
  annual_quota: number
  carry_forward_limit: number
  encashment_allowed: boolean
  is_paid: boolean
  applicable_to: EmploymentType[]
  requires_approval: boolean
  min_days: number
  max_days: number
  notice_days: number
  applicable_from_months: number // Months after joining
}

export interface LeaveBalance {
  employee_id: string
  leave_type_code: string
  leave_type_name: string
  year: number
  opening_balance: number
  credited: number
  used: number
  lapsed: number
  available: number
  pending_approval: number
}

export interface LeaveRequest extends BaseEntity {
  employee_id: string
  employee_name: string
  leave_type_code: string
  leave_type_name: string
  from_date: string
  to_date: string
  days: number
  half_day: boolean
  half_day_type?: 'first_half' | 'second_half'
  reason: string
  status: LeaveStatus
  applied_on: string
  approver_id?: string
  approver_name?: string
  approved_on?: string
  rejection_reason?: string
  documents?: string[]
}

export type LeaveStatus =
  | 'pending'
  | 'approved'
  | 'rejected'
  | 'cancelled'
  | 'partially_approved'

// ============================================================================
// Attendance Types
// ============================================================================

export interface AttendanceLog extends BaseEntity {
  employee_id: string
  date: string
  check_in?: string
  check_out?: string
  work_hours: number
  break_hours: number
  overtime_hours: number
  status: AttendanceStatus
  source: 'biometric' | 'manual' | 'mobile' | 'system'
  location?: GeoLocation
  notes?: string
  regularization_request_id?: string
}

export type AttendanceStatus =
  | 'present'
  | 'absent'
  | 'half_day'
  | 'on_leave'
  | 'holiday'
  | 'week_off'
  | 'work_from_home'
  | 'on_duty'
  | 'pending'

export interface GeoLocation {
  latitude: number
  longitude: number
  accuracy: number
  address?: string
}

export interface RegularizationRequest extends BaseEntity {
  employee_id: string
  date: string
  original_status: AttendanceStatus
  requested_status: AttendanceStatus
  check_in?: string
  check_out?: string
  reason: string
  status: 'pending' | 'approved' | 'rejected'
  approver_id?: string
  approved_on?: string
}

// ============================================================================
// Finance Types
// ============================================================================

export interface Account extends BaseEntity {
  code: string
  name: string
  type: AccountType
  parent_id?: string
  company_id: string
  balance: number
  is_active: boolean
  is_system: boolean
  gst_applicable: boolean
  hsn_code?: string
}

export type AccountType =
  | 'asset' | 'liability' | 'equity' | 'revenue' | 'expense'
  | 'bank' | 'cash' | 'receivable' | 'payable'

export interface JournalEntry extends BaseEntity {
  entry_number: string
  company_id: string
  date: string
  narration: string
  reference?: string
  status: 'draft' | 'posted' | 'reversed'
  lines: JournalLine[]
  total_debit: number
  total_credit: number
}

export interface JournalLine {
  id: string
  account_id: string
  account_name: string
  debit: number
  credit: number
  narration?: string
  cost_center_id?: string
}

// ============================================================================
// Invoice Types (Sales)
// ============================================================================

export interface Invoice extends BaseEntity {
  invoice_number: string
  company_id: string
  customer_id: string
  customer_name: string
  customer_gstin?: string

  invoice_date: string
  due_date: string

  // Place of Supply for GST
  place_of_supply: IndianState
  supply_type: 'intra_state' | 'inter_state' | 'export' | 'sez'

  items: InvoiceItem[]

  // Amounts
  subtotal: number
  discount: number
  taxable_amount: number
  cgst: number
  sgst: number
  igst: number
  cess: number
  total_tax: number
  round_off: number
  total: number

  // Payment
  amount_paid: number
  balance_due: number
  status: InvoiceStatus

  // E-Invoice
  irn?: string // Invoice Reference Number
  ack_number?: string
  ack_date?: string
  qr_code?: string

  notes?: string
  terms?: string
}

export interface InvoiceItem {
  id: string
  description: string
  hsn_code: string
  quantity: number
  unit: string
  rate: number
  discount: number
  taxable_amount: number
  gst_rate: number
  cgst: number
  sgst: number
  igst: number
  cess: number
  total: number
}

export type InvoiceStatus =
  | 'draft'
  | 'sent'
  | 'viewed'
  | 'partially_paid'
  | 'paid'
  | 'overdue'
  | 'cancelled'
  | 'bad_debt'

// ============================================================================
// Bill Types (Purchase)
// ============================================================================

export interface Bill extends BaseEntity {
  bill_number: string
  company_id: string
  vendor_id: string
  vendor_name: string
  vendor_gstin?: string
  vendor_pan?: string

  bill_date: string
  due_date: string

  place_of_supply: IndianState
  supply_type: 'intra_state' | 'inter_state' | 'import'

  items: BillItem[]

  // Amounts
  subtotal: number
  discount: number
  taxable_amount: number
  cgst: number
  sgst: number
  igst: number
  cess: number
  total_tax: number

  // TDS
  tds_section?: TDSSection
  tds_rate: number
  tds_amount: number

  round_off: number
  total: number
  net_payable: number // Total - TDS

  amount_paid: number
  balance_due: number
  status: BillStatus

  notes?: string
}

export interface BillItem {
  id: string
  description: string
  hsn_code: string
  quantity: number
  unit: string
  rate: number
  discount: number
  taxable_amount: number
  gst_rate: number
  cgst: number
  sgst: number
  igst: number
  cess: number
  total: number
}

export type BillStatus =
  | 'draft'
  | 'approved'
  | 'partially_paid'
  | 'paid'
  | 'overdue'
  | 'cancelled'

export type TDSSection =
  | '194A' // Interest
  | '194C' // Contractor
  | '194H' // Commission
  | '194I' // Rent
  | '194J' // Professional Fees
  | '194Q' // Purchase of Goods

// ============================================================================
// CRM Types
// ============================================================================

export interface Lead extends BaseEntity {
  company_id: string
  name: string
  email?: string
  phone?: string
  company_name?: string
  source: LeadSource
  status: LeadStatus
  assigned_to?: string
  score?: number
  notes?: string
  next_follow_up?: string
}

export type LeadSource =
  | 'website' | 'referral' | 'social_media' | 'cold_call'
  | 'trade_show' | 'advertisement' | 'other'

export type LeadStatus =
  | 'new' | 'contacted' | 'qualified' | 'proposal'
  | 'negotiation' | 'won' | 'lost' | 'nurturing'

export interface Opportunity extends BaseEntity {
  company_id: string
  lead_id?: string
  name: string
  customer_id?: string
  value: number
  probability: number
  expected_close_date: string
  stage: string
  assigned_to?: string
  notes?: string
}

// ============================================================================
// Project Types
// ============================================================================

export interface Project extends BaseEntity {
  company_id: string
  name: string
  code: string
  description?: string
  customer_id?: string
  status: ProjectStatus
  start_date: string
  end_date?: string
  budget?: number
  actual_cost?: number
  manager_id?: string
  team_members: string[]
  milestones?: Milestone[]
}

export type ProjectStatus =
  | 'planning' | 'in_progress' | 'on_hold' | 'completed' | 'cancelled'

export interface Milestone extends BaseEntity {
  project_id: string
  name: string
  due_date: string
  completed_date?: string
  status: 'pending' | 'in_progress' | 'completed' | 'overdue'
}

export interface Task extends BaseEntity {
  project_id: string
  milestone_id?: string
  title: string
  description?: string
  assigned_to?: string
  priority: 'low' | 'medium' | 'high' | 'urgent'
  status: 'todo' | 'in_progress' | 'review' | 'done'
  due_date?: string
  estimated_hours?: number
  actual_hours?: number
}

// ============================================================================
// AI Types
// ============================================================================

export interface AIConversation extends BaseEntity {
  user_id: string
  company_id: string
  title?: string
  messages: AIMessage[]
  context?: string
  tokens_used: number
}

export interface AIMessage {
  id: string
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp: string
  model?: string
  tokens?: number
}

export interface AIUsage {
  company_id: string
  month: number
  year: number
  total_requests: number
  total_tokens: number
  total_cost: number
  quota_remaining: number
}

// ============================================================================
// Dashboard Types
// ============================================================================

export interface DashboardStats {
  total_employees: number
  employees_on_leave: number
  pending_leave_requests: number
  pending_reimbursements: number
  upcoming_birthdays: Employee[]
  upcoming_work_anniversaries: Employee[]
  attendance_today: AttendanceSummary
  payroll_status?: PayrollRun
}

export interface AttendanceSummary {
  total: number
  present: number
  absent: number
  on_leave: number
  work_from_home: number
  late: number
}

export interface FinanceDashboard {
  receivables: number
  payables: number
  cash_balance: number
  bank_balance: number
  revenue_this_month: number
  expenses_this_month: number
  overdue_invoices: number
  overdue_bills: number
  gst_liability: number
  tds_liability: number
}

// ============================================================================
// Form & Filter Types
// ============================================================================

export interface DateRange {
  from: string
  to: string
}

export interface PaginationParams {
  page: number
  page_size: number
  sort_by?: string
  sort_order?: 'asc' | 'desc'
}

export interface EmployeeFilters extends PaginationParams {
  search?: string
  department_id?: string
  designation_id?: string
  employment_type?: EmploymentType
  employment_status?: EmploymentStatus
  date_range?: DateRange
}

export interface PayrollFilters extends PaginationParams {
  month?: number
  year?: number
  status?: PayrollStatus
  department_id?: string
}

export interface LeaveFilters extends PaginationParams {
  employee_id?: string
  leave_type?: string
  status?: LeaveStatus
  date_range?: DateRange
}

export interface InvoiceFilters extends PaginationParams {
  customer_id?: string
  status?: InvoiceStatus
  date_range?: DateRange
}
