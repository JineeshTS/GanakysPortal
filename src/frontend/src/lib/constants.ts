// GanaPortal Constants
// FE-001: India-specific Constants

// ============================================================================
// Indian States with GST Codes
// ============================================================================

export const INDIAN_STATES = [
  { code: '01', name: 'Jammu & Kashmir', shortName: 'JK' },
  { code: '02', name: 'Himachal Pradesh', shortName: 'HP' },
  { code: '03', name: 'Punjab', shortName: 'PB' },
  { code: '04', name: 'Chandigarh', shortName: 'CH' },
  { code: '05', name: 'Uttarakhand', shortName: 'UK' },
  { code: '06', name: 'Haryana', shortName: 'HR' },
  { code: '07', name: 'Delhi', shortName: 'DL' },
  { code: '08', name: 'Rajasthan', shortName: 'RJ' },
  { code: '09', name: 'Uttar Pradesh', shortName: 'UP' },
  { code: '10', name: 'Bihar', shortName: 'BR' },
  { code: '11', name: 'Sikkim', shortName: 'SK' },
  { code: '12', name: 'Arunachal Pradesh', shortName: 'AR' },
  { code: '13', name: 'Nagaland', shortName: 'NL' },
  { code: '14', name: 'Manipur', shortName: 'MN' },
  { code: '15', name: 'Mizoram', shortName: 'MZ' },
  { code: '16', name: 'Tripura', shortName: 'TR' },
  { code: '17', name: 'Meghalaya', shortName: 'ML' },
  { code: '18', name: 'Assam', shortName: 'AS' },
  { code: '19', name: 'West Bengal', shortName: 'WB' },
  { code: '20', name: 'Jharkhand', shortName: 'JH' },
  { code: '21', name: 'Odisha', shortName: 'OD' },
  { code: '22', name: 'Chhattisgarh', shortName: 'CG' },
  { code: '23', name: 'Madhya Pradesh', shortName: 'MP' },
  { code: '24', name: 'Gujarat', shortName: 'GJ' },
  { code: '26', name: 'Dadra and Nagar Haveli', shortName: 'DN' },
  { code: '27', name: 'Maharashtra', shortName: 'MH' },
  { code: '29', name: 'Karnataka', shortName: 'KA' },
  { code: '30', name: 'Goa', shortName: 'GA' },
  { code: '31', name: 'Lakshadweep', shortName: 'LD' },
  { code: '32', name: 'Kerala', shortName: 'KL' },
  { code: '33', name: 'Tamil Nadu', shortName: 'TN' },
  { code: '34', name: 'Puducherry', shortName: 'PY' },
  { code: '35', name: 'Andaman and Nicobar Islands', shortName: 'AN' },
  { code: '36', name: 'Telangana', shortName: 'TS' },
  { code: '37', name: 'Andhra Pradesh', shortName: 'AP' },
  { code: '38', name: 'Ladakh', shortName: 'LA' }
] as const

// ============================================================================
// GST Rates
// ============================================================================

export const GST_RATES = [
  { value: 0, label: '0%' },
  { value: 5, label: '5%' },
  { value: 12, label: '12%' },
  { value: 18, label: '18%' },
  { value: 28, label: '28%' }
] as const

// ============================================================================
// TDS Sections
// ============================================================================

export const TDS_SECTIONS = [
  { code: '194A', description: 'Interest other than Interest on securities', rate: 10 },
  { code: '194C', description: 'Payment to Contractors', rate: 1 },
  { code: '194H', description: 'Commission or Brokerage', rate: 5 },
  { code: '194I', description: 'Rent', rate: 10 },
  { code: '194J', description: 'Professional/Technical Fees', rate: 10 },
  { code: '194Q', description: 'Purchase of Goods', rate: 0.1 }
] as const

// ============================================================================
// Statutory Rates
// ============================================================================

export const STATUTORY_RATES = {
  // PF Rates (as of FY 2025-26)
  pf: {
    employeeContribution: 12, // 12% of Basic
    employerContribution: 12, // 12% of Basic (8.33% EPS + 3.67% EPF)
    epsContribution: 8.33,
    epfContribution: 3.67,
    epsWageLimit: 15000, // Monthly EPS wage ceiling
    pfWageLimit: 15000, // Optional higher wage for voluntary PF
    adminCharges: 0.5, // EDLI admin charges
    edliCharges: 0.5
  },

  // ESI Rates
  esi: {
    employeeContribution: 0.75, // 0.75% of Gross
    employerContribution: 3.25, // 3.25% of Gross
    wageLimit: 21000 // Monthly wage limit for ESI
  },

  // Professional Tax (Karnataka)
  ptKarnataka: {
    slabs: [
      { min: 0, max: 15000, tax: 0 },
      { min: 15001, max: 999999999, tax: 200 }
    ],
    februaryTax: 300,
    annualLimit: 2500
  },

  // TDS for Salary (FY 2025-26)
  tdsNewRegime: {
    slabs: [
      { min: 0, max: 400000, rate: 0 },
      { min: 400001, max: 800000, rate: 5 },
      { min: 800001, max: 1200000, rate: 10 },
      { min: 1200001, max: 1600000, rate: 15 },
      { min: 1600001, max: 2000000, rate: 20 },
      { min: 2000001, max: 2400000, rate: 25 },
      { min: 2400001, max: 999999999, rate: 30 }
    ],
    standardDeduction: 75000,
    rebateLimit: 700000,
    cess: 4
  },

  tdsOldRegime: {
    slabs: [
      { min: 0, max: 250000, rate: 0 },
      { min: 250001, max: 500000, rate: 5 },
      { min: 500001, max: 1000000, rate: 20 },
      { min: 1000001, max: 999999999, rate: 30 }
    ],
    standardDeduction: 50000,
    rebateLimit: 500000,
    cess: 4
  }
} as const

// ============================================================================
// Leave Types
// ============================================================================

export const DEFAULT_LEAVE_TYPES = [
  { code: 'CL', name: 'Casual Leave', annual: 12, carryForward: 0, paid: true },
  { code: 'SL', name: 'Sick Leave', annual: 12, carryForward: 6, paid: true },
  { code: 'EL', name: 'Earned Leave', annual: 15, carryForward: 30, paid: true },
  { code: 'ML', name: 'Maternity Leave', annual: 182, carryForward: 0, paid: true },
  { code: 'PL', name: 'Paternity Leave', annual: 15, carryForward: 0, paid: true },
  { code: 'CO', name: 'Comp Off', annual: 0, carryForward: 0, paid: true },
  { code: 'LWP', name: 'Leave Without Pay', annual: 0, carryForward: 0, paid: false }
] as const

// ============================================================================
// Blood Groups
// ============================================================================

export const BLOOD_GROUPS = [
  'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'
] as const

// ============================================================================
// Gender Options
// ============================================================================

export const GENDERS = [
  { value: 'male', label: 'Male' },
  { value: 'female', label: 'Female' },
  { value: 'other', label: 'Other' }
] as const

// ============================================================================
// Marital Status
// ============================================================================

export const MARITAL_STATUS = [
  { value: 'single', label: 'Single' },
  { value: 'married', label: 'Married' },
  { value: 'divorced', label: 'Divorced' },
  { value: 'widowed', label: 'Widowed' }
] as const

// ============================================================================
// Employment Types
// ============================================================================

export const EMPLOYMENT_TYPES = [
  { value: 'full_time', label: 'Full Time' },
  { value: 'part_time', label: 'Part Time' },
  { value: 'contract', label: 'Contract' },
  { value: 'intern', label: 'Intern' },
  { value: 'consultant', label: 'Consultant' }
] as const

// ============================================================================
// Account Types (Chart of Accounts)
// ============================================================================

export const ACCOUNT_TYPES = [
  { value: 'asset', label: 'Asset' },
  { value: 'liability', label: 'Liability' },
  { value: 'equity', label: 'Equity' },
  { value: 'revenue', label: 'Revenue' },
  { value: 'expense', label: 'Expense' }
] as const

// ============================================================================
// Units of Measurement
// ============================================================================

export const UNITS = [
  { value: 'NOS', label: 'Numbers' },
  { value: 'PCS', label: 'Pieces' },
  { value: 'KGS', label: 'Kilograms' },
  { value: 'GMS', label: 'Grams' },
  { value: 'LTR', label: 'Litres' },
  { value: 'MTR', label: 'Meters' },
  { value: 'SQM', label: 'Square Meters' },
  { value: 'HRS', label: 'Hours' },
  { value: 'DAY', label: 'Days' },
  { value: 'MON', label: 'Months' }
] as const

// ============================================================================
// Status Colors
// ============================================================================

export const STATUS_COLORS = {
  success: 'bg-green-100 text-green-800',
  warning: 'bg-yellow-100 text-yellow-800',
  error: 'bg-red-100 text-red-800',
  info: 'bg-blue-100 text-blue-800',
  default: 'bg-gray-100 text-gray-800'
} as const

// ============================================================================
// API Endpoints
// ============================================================================

export const API_ENDPOINTS = {
  auth: {
    login: '/auth/login',
    logout: '/auth/logout',
    refresh: '/auth/refresh',
    register: '/auth/register',
    forgotPassword: '/auth/forgot-password',
    resetPassword: '/auth/reset-password'
  },
  employees: '/employees',
  departments: '/departments',
  designations: '/designations',
  payroll: '/payroll',
  leave: '/leave',
  attendance: '/attendance',
  invoices: '/invoices',
  bills: '/bills',
  accounts: '/accounts',
  journals: '/journals',
  projects: '/projects',
  tasks: '/tasks',
  leads: '/leads',
  opportunities: '/opportunities',
  ai: '/ai'
} as const
