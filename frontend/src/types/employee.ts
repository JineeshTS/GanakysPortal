/**
 * Employee Types
 */

export type EmploymentStatus = 'active' | 'probation' | 'notice_period' | 'resigned' | 'terminated';
export type EmploymentType = 'full_time' | 'part_time' | 'contract' | 'intern';
export type Gender = 'male' | 'female' | 'other';
export type MaritalStatus = 'single' | 'married' | 'divorced' | 'widowed';

export interface Employee {
  id: string;
  user_id: string;
  employee_code: string;
  first_name: string;
  middle_name?: string;
  last_name: string;
  date_of_birth?: string;
  gender?: Gender;
  blood_group?: string;
  marital_status?: MaritalStatus;
  nationality?: string;
  profile_photo_path?: string;
  onboarding_status: string;
  onboarding_completed_at?: string;
  created_at: string;
  updated_at: string;

  // Related data
  contact?: EmployeeContact;
  identity?: EmployeeIdentity;
  bank?: EmployeeBank;
  employment?: EmployeeEmployment;
}

export interface EmployeeContact {
  personal_email?: string;
  personal_phone?: string;
  emergency_contact_name?: string;
  emergency_contact_phone?: string;
  emergency_contact_relation?: string;
  current_address?: string;
  permanent_address?: string;
  is_same_as_current: boolean;
}

export interface EmployeeIdentity {
  pan_number?: string;
  aadhaar_number?: string;
  passport_number?: string;
  passport_expiry?: string;
  driving_license?: string;
  voter_id?: string;
}

export interface EmployeeBank {
  bank_name?: string;
  branch_name?: string;
  account_number?: string;
  ifsc_code?: string;
  account_type?: string;
  is_primary: boolean;
}

export interface EmployeeEmployment {
  department_id?: string;
  department_name?: string;
  designation_id?: string;
  designation_name?: string;
  reporting_manager_id?: string;
  reporting_manager_name?: string;
  employment_type: EmploymentType;
  date_of_joining: string;
  probation_end_date?: string;
  confirmation_date?: string;
  date_of_exit?: string;
  exit_reason?: string;
  notice_period_days?: number;
  current_status: EmploymentStatus;
}

export interface Department {
  id: string;
  name: string;
  code: string;
  description?: string;
  head_employee_id?: string;
  is_active: boolean;
}

export interface Designation {
  id: string;
  name: string;
  code: string;
  department_id?: string;
  level?: number;
  is_active: boolean;
}

export interface EmployeeDocument {
  id: string;
  employee_id: string;
  document_type: string;
  file_name: string;
  file_path: string;
  file_size: number;
  mime_type: string;
  description?: string;
  uploaded_by: string;
  is_verified: boolean;
  verified_by?: string;
  verified_at?: string;
  created_at: string;
}

export interface EmployeeCreateRequest {
  email: string;
  first_name: string;
  middle_name?: string;
  last_name: string;
  date_of_birth?: string;
  gender?: Gender;
  department_id?: string;
  designation_id?: string;
  reporting_manager_id?: string;
  employment_type: EmploymentType;
  date_of_joining: string;
}

export interface EmployeeListParams {
  search?: string;
  department_id?: string;
  designation_id?: string;
  status?: EmploymentStatus;
  skip?: number;
  limit?: number;
}
