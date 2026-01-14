'use client'

import * as React from 'react'
import { useRouter } from 'next/navigation'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { FormField, FormSelect, FormCheckbox } from '@/components/forms/form-field'
import { FileUpload } from '@/components/forms/file-upload'
import { cn } from '@/lib/utils'
import {
  isValidEmail,
  isValidPhone,
  isValidPAN,
  isValidAadhaar,
  isValidIFSC,
  isValidBankAccount,
  isValidPincode
} from '@/lib/validators'
import { BLOOD_GROUPS, GENDERS, MARITAL_STATUS, EMPLOYMENT_TYPES, INDIAN_STATES } from '@/lib/constants'
import {
  ChevronRight,
  ChevronLeft,
  Check,
  User,
  FileText,
  Briefcase,
  CreditCard,
  Upload,
  AlertCircle,
  Loader2
} from 'lucide-react'
import type { Employee, Address, BankDetails, EmergencyContact } from '@/types'

// ============================================================================
// Types
// ============================================================================

export interface EmployeeFormData {
  // Step 1: Personal Info
  first_name: string
  middle_name: string
  last_name: string
  date_of_birth: string
  gender: string
  blood_group: string
  marital_status: string
  father_name: string
  mobile: string
  personal_email: string
  work_email: string
  emergency_contact_name: string
  emergency_contact_relationship: string
  emergency_contact_phone: string
  current_address_line1: string
  current_address_line2: string
  current_address_city: string
  current_address_state: string
  current_address_pincode: string
  permanent_address_same: boolean
  permanent_address_line1: string
  permanent_address_line2: string
  permanent_address_city: string
  permanent_address_state: string
  permanent_address_pincode: string

  // Step 2: Identity Documents
  aadhaar: string
  pan: string
  passport_number: string
  passport_expiry: string

  // Step 3: Employment Details
  employee_code: string
  date_of_joining: string
  department_id: string
  designation_id: string
  reporting_to: string
  work_location: string
  employment_type: string
  probation_period_months: string
  notice_period_days: string

  // Step 4: Salary & Bank
  annual_ctc: string
  basic_percentage: string
  hra_percentage: string
  pf_opt_in: boolean
  esi_applicable: boolean
  bank_account_holder: string
  bank_account_number: string
  bank_name: string
  bank_branch: string
  bank_ifsc: string
  uan: string

  // Step 5: Documents
  photo: File[]
  aadhaar_doc: File[]
  pan_doc: File[]
  passport_doc: File[]
  offer_letter: File[]
  joining_report: File[]
  previous_employment_docs: File[]
}

interface EmployeeFormProps {
  initialData?: Partial<EmployeeFormData>
  onSubmit: (data: EmployeeFormData) => Promise<void>
  isEdit?: boolean
}

// Mock data
const departments = [
  { value: '1', label: 'Engineering' },
  { value: '2', label: 'HR' },
  { value: '3', label: 'Finance' },
  { value: '4', label: 'Marketing' },
  { value: '5', label: 'Operations' }
]

const designations = [
  { value: '1', label: 'Software Engineer' },
  { value: '2', label: 'Senior Software Engineer' },
  { value: '3', label: 'HR Executive' },
  { value: '4', label: 'Intern' },
  { value: '5', label: 'Manager' }
]

const managers = [
  { value: '10', label: 'Amit Patel' },
  { value: '11', label: 'Priya Sharma' },
  { value: '12', label: 'Vikram Singh' }
]

const workLocations = [
  { value: 'bangalore_hq', label: 'Bangalore HQ' },
  { value: 'mumbai', label: 'Mumbai Office' },
  { value: 'delhi', label: 'Delhi Office' },
  { value: 'remote', label: 'Remote' }
]

// ============================================================================
// Step Components
// ============================================================================

const steps = [
  { id: 1, name: 'Personal Info', icon: User },
  { id: 2, name: 'Identity Documents', icon: FileText },
  { id: 3, name: 'Employment Details', icon: Briefcase },
  { id: 4, name: 'Salary & Bank', icon: CreditCard },
  { id: 5, name: 'Documents Upload', icon: Upload }
]

// ============================================================================
// Main Component
// ============================================================================

export function EmployeeForm({ initialData, onSubmit, isEdit = false }: EmployeeFormProps) {
  const router = useRouter()
  const [currentStep, setCurrentStep] = React.useState(1)
  const [isSubmitting, setIsSubmitting] = React.useState(false)
  const [errors, setErrors] = React.useState<Record<string, string>>({})

  const [formData, setFormData] = React.useState<EmployeeFormData>({
    // Step 1
    first_name: initialData?.first_name || '',
    middle_name: initialData?.middle_name || '',
    last_name: initialData?.last_name || '',
    date_of_birth: initialData?.date_of_birth || '',
    gender: initialData?.gender || '',
    blood_group: initialData?.blood_group || '',
    marital_status: initialData?.marital_status || '',
    father_name: initialData?.father_name || '',
    mobile: initialData?.mobile || '',
    personal_email: initialData?.personal_email || '',
    work_email: initialData?.work_email || '',
    emergency_contact_name: initialData?.emergency_contact_name || '',
    emergency_contact_relationship: initialData?.emergency_contact_relationship || '',
    emergency_contact_phone: initialData?.emergency_contact_phone || '',
    current_address_line1: initialData?.current_address_line1 || '',
    current_address_line2: initialData?.current_address_line2 || '',
    current_address_city: initialData?.current_address_city || '',
    current_address_state: initialData?.current_address_state || '',
    current_address_pincode: initialData?.current_address_pincode || '',
    permanent_address_same: initialData?.permanent_address_same || false,
    permanent_address_line1: initialData?.permanent_address_line1 || '',
    permanent_address_line2: initialData?.permanent_address_line2 || '',
    permanent_address_city: initialData?.permanent_address_city || '',
    permanent_address_state: initialData?.permanent_address_state || '',
    permanent_address_pincode: initialData?.permanent_address_pincode || '',

    // Step 2
    aadhaar: initialData?.aadhaar || '',
    pan: initialData?.pan || '',
    passport_number: initialData?.passport_number || '',
    passport_expiry: initialData?.passport_expiry || '',

    // Step 3
    employee_code: initialData?.employee_code || '',
    date_of_joining: initialData?.date_of_joining || '',
    department_id: initialData?.department_id || '',
    designation_id: initialData?.designation_id || '',
    reporting_to: initialData?.reporting_to || '',
    work_location: initialData?.work_location || '',
    employment_type: initialData?.employment_type || 'full_time',
    probation_period_months: initialData?.probation_period_months || '6',
    notice_period_days: initialData?.notice_period_days || '60',

    // Step 4
    annual_ctc: initialData?.annual_ctc || '',
    basic_percentage: initialData?.basic_percentage || '50',
    hra_percentage: initialData?.hra_percentage || '20',
    pf_opt_in: initialData?.pf_opt_in ?? true,
    esi_applicable: initialData?.esi_applicable ?? false,
    bank_account_holder: initialData?.bank_account_holder || '',
    bank_account_number: initialData?.bank_account_number || '',
    bank_name: initialData?.bank_name || '',
    bank_branch: initialData?.bank_branch || '',
    bank_ifsc: initialData?.bank_ifsc || '',
    uan: initialData?.uan || '',

    // Step 5
    photo: [],
    aadhaar_doc: [],
    pan_doc: [],
    passport_doc: [],
    offer_letter: [],
    joining_report: [],
    previous_employment_docs: []
  })

  const updateField = (field: keyof EmployeeFormData, value: unknown) => {
    setFormData(prev => ({ ...prev, [field]: value }))
    // Clear error when field is updated
    if (errors[field]) {
      setErrors(prev => {
        const newErrors = { ...prev }
        delete newErrors[field]
        return newErrors
      })
    }
  }

  const validateStep = (step: number): boolean => {
    const newErrors: Record<string, string> = {}

    switch (step) {
      case 1:
        if (!formData.first_name.trim()) newErrors.first_name = 'First name is required'
        if (!formData.last_name.trim()) newErrors.last_name = 'Last name is required'
        if (!formData.date_of_birth) newErrors.date_of_birth = 'Date of birth is required'
        if (!formData.gender) newErrors.gender = 'Gender is required'
        if (!formData.father_name.trim()) newErrors.father_name = "Father's name is required"
        if (!formData.mobile) {
          newErrors.mobile = 'Mobile number is required'
        } else if (!isValidPhone(formData.mobile)) {
          newErrors.mobile = 'Invalid mobile number'
        }
        if (!formData.work_email) {
          newErrors.work_email = 'Work email is required'
        } else if (!isValidEmail(formData.work_email)) {
          newErrors.work_email = 'Invalid email format'
        }
        if (formData.personal_email && !isValidEmail(formData.personal_email)) {
          newErrors.personal_email = 'Invalid email format'
        }
        if (!formData.current_address_line1.trim()) newErrors.current_address_line1 = 'Address is required'
        if (!formData.current_address_city.trim()) newErrors.current_address_city = 'City is required'
        if (!formData.current_address_state) newErrors.current_address_state = 'State is required'
        if (!formData.current_address_pincode) {
          newErrors.current_address_pincode = 'Pincode is required'
        } else if (!isValidPincode(formData.current_address_pincode)) {
          newErrors.current_address_pincode = 'Invalid pincode'
        }
        if (!formData.permanent_address_same) {
          if (!formData.permanent_address_line1.trim()) newErrors.permanent_address_line1 = 'Address is required'
          if (!formData.permanent_address_city.trim()) newErrors.permanent_address_city = 'City is required'
          if (!formData.permanent_address_state) newErrors.permanent_address_state = 'State is required'
          if (!formData.permanent_address_pincode) {
            newErrors.permanent_address_pincode = 'Pincode is required'
          } else if (!isValidPincode(formData.permanent_address_pincode)) {
            newErrors.permanent_address_pincode = 'Invalid pincode'
          }
        }
        if (formData.emergency_contact_phone && !isValidPhone(formData.emergency_contact_phone)) {
          newErrors.emergency_contact_phone = 'Invalid phone number'
        }
        break

      case 2:
        if (formData.aadhaar && !isValidAadhaar(formData.aadhaar)) {
          newErrors.aadhaar = 'Invalid Aadhaar number (12 digits, starts with 2-9)'
        }
        if (!formData.pan) {
          newErrors.pan = 'PAN is required'
        } else if (!isValidPAN(formData.pan)) {
          newErrors.pan = 'Invalid PAN format (e.g., ABCDE1234F)'
        }
        break

      case 3:
        if (!formData.employee_code.trim()) newErrors.employee_code = 'Employee ID is required'
        if (!formData.date_of_joining) newErrors.date_of_joining = 'Date of joining is required'
        if (!formData.department_id) newErrors.department_id = 'Department is required'
        if (!formData.designation_id) newErrors.designation_id = 'Designation is required'
        if (!formData.employment_type) newErrors.employment_type = 'Employment type is required'
        break

      case 4:
        if (!formData.annual_ctc) {
          newErrors.annual_ctc = 'Annual CTC is required'
        } else if (isNaN(Number(formData.annual_ctc)) || Number(formData.annual_ctc) <= 0) {
          newErrors.annual_ctc = 'Invalid CTC amount'
        }
        if (!formData.bank_account_holder.trim()) newErrors.bank_account_holder = 'Account holder name is required'
        if (!formData.bank_account_number) {
          newErrors.bank_account_number = 'Account number is required'
        } else if (!isValidBankAccount(formData.bank_account_number)) {
          newErrors.bank_account_number = 'Invalid account number (9-18 digits)'
        }
        if (!formData.bank_name.trim()) newErrors.bank_name = 'Bank name is required'
        if (!formData.bank_ifsc) {
          newErrors.bank_ifsc = 'IFSC code is required'
        } else if (!isValidIFSC(formData.bank_ifsc)) {
          newErrors.bank_ifsc = 'Invalid IFSC code (e.g., HDFC0001234)'
        }
        break

      case 5:
        // Documents are optional in most cases
        break
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleNext = () => {
    if (validateStep(currentStep)) {
      setCurrentStep(prev => Math.min(prev + 1, 5))
    }
  }

  const handlePrevious = () => {
    setCurrentStep(prev => Math.max(prev - 1, 1))
  }

  const handleSubmit = async () => {
    if (!validateStep(currentStep)) return

    setIsSubmitting(true)
    try {
      await onSubmit(formData)
    } catch (error) {
      console.error('Failed to save employee:', error)
    } finally {
      setIsSubmitting(false)
    }
  }

  // Calculate salary breakdown
  const salaryBreakdown = React.useMemo(() => {
    const annualCTC = Number(formData.annual_ctc) || 0
    const monthlyCTC = annualCTC / 12
    const basicPercentage = Number(formData.basic_percentage) || 50
    const hraPercentage = Number(formData.hra_percentage) || 20

    const basic = (monthlyCTC * basicPercentage) / 100
    const hra = (monthlyCTC * hraPercentage) / 100
    const specialAllowance = monthlyCTC - basic - hra

    const pfEmployee = formData.pf_opt_in ? Math.min(basic * 0.12, 1800) : 0
    const pfEmployer = formData.pf_opt_in ? Math.min(basic * 0.12, 1800) : 0

    const gross = basic + hra + specialAllowance
    const totalDeductions = pfEmployee
    const net = gross - totalDeductions

    return { basic, hra, specialAllowance, pfEmployee, pfEmployer, gross, totalDeductions, net }
  }, [formData.annual_ctc, formData.basic_percentage, formData.hra_percentage, formData.pf_opt_in])

  return (
    <div className="space-y-6">
      {/* Step Progress */}
      <Card>
        <CardContent className="pt-6">
          <nav aria-label="Progress">
            <ol className="flex items-center justify-between">
              {steps.map((step, index) => (
                <li key={step.id} className="relative flex-1">
                  <div className="flex items-center">
                    <div
                      className={cn(
                        'w-10 h-10 rounded-full flex items-center justify-center border-2 transition-colors',
                        currentStep > step.id
                          ? 'bg-primary border-primary text-primary-foreground'
                          : currentStep === step.id
                            ? 'border-primary text-primary'
                            : 'border-muted text-muted-foreground'
                      )}
                    >
                      {currentStep > step.id ? (
                        <Check className="h-5 w-5" />
                      ) : (
                        <step.icon className="h-5 w-5" />
                      )}
                    </div>
                    {index < steps.length - 1 && (
                      <div
                        className={cn(
                          'flex-1 h-0.5 mx-2',
                          currentStep > step.id ? 'bg-primary' : 'bg-muted'
                        )}
                      />
                    )}
                  </div>
                  <p className={cn(
                    'mt-2 text-xs font-medium text-center',
                    currentStep >= step.id ? 'text-primary' : 'text-muted-foreground'
                  )}>
                    {step.name}
                  </p>
                </li>
              ))}
            </ol>
          </nav>
        </CardContent>
      </Card>

      {/* Form Content */}
      <Card>
        <CardHeader>
          <CardTitle>
            Step {currentStep}: {steps[currentStep - 1].name}
          </CardTitle>
          <CardDescription>
            {currentStep === 1 && 'Enter the employee\'s personal and contact information'}
            {currentStep === 2 && 'Enter identity document details for statutory compliance'}
            {currentStep === 3 && 'Configure employment details and organizational structure'}
            {currentStep === 4 && 'Set up salary structure and bank details for payroll'}
            {currentStep === 5 && 'Upload required documents for employee records'}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {/* Step 1: Personal Info */}
          {currentStep === 1 && (
            <div className="space-y-8">
              {/* Basic Info */}
              <div>
                <h4 className="font-medium mb-4">Basic Information</h4>
                <div className="grid gap-4 md:grid-cols-3">
                  <FormField
                    label="First Name"
                    name="first_name"
                    value={formData.first_name}
                    onChange={(e) => updateField('first_name', e.target.value)}
                    error={errors.first_name}
                    required
                  />
                  <FormField
                    label="Middle Name"
                    name="middle_name"
                    value={formData.middle_name}
                    onChange={(e) => updateField('middle_name', e.target.value)}
                  />
                  <FormField
                    label="Last Name"
                    name="last_name"
                    value={formData.last_name}
                    onChange={(e) => updateField('last_name', e.target.value)}
                    error={errors.last_name}
                    required
                  />
                  <FormField
                    label="Date of Birth"
                    name="date_of_birth"
                    type="date"
                    value={formData.date_of_birth}
                    onChange={(e) => updateField('date_of_birth', e.target.value)}
                    error={errors.date_of_birth}
                    required
                  />
                  <FormSelect
                    label="Gender"
                    name="gender"
                    value={formData.gender}
                    onChange={(e) => updateField('gender', e.target.value)}
                    options={GENDERS.map(g => ({ value: g.value, label: g.label }))}
                    placeholder="Select gender"
                    error={errors.gender}
                    required
                  />
                  <FormSelect
                    label="Blood Group"
                    name="blood_group"
                    value={formData.blood_group}
                    onChange={(e) => updateField('blood_group', e.target.value)}
                    options={BLOOD_GROUPS.map(bg => ({ value: bg, label: bg }))}
                    placeholder="Select blood group"
                  />
                  <FormSelect
                    label="Marital Status"
                    name="marital_status"
                    value={formData.marital_status}
                    onChange={(e) => updateField('marital_status', e.target.value)}
                    options={MARITAL_STATUS.map(ms => ({ value: ms.value, label: ms.label }))}
                    placeholder="Select status"
                  />
                  <FormField
                    label="Father's Name"
                    name="father_name"
                    value={formData.father_name}
                    onChange={(e) => updateField('father_name', e.target.value)}
                    error={errors.father_name}
                    required
                  />
                </div>
              </div>

              {/* Contact Info */}
              <div>
                <h4 className="font-medium mb-4">Contact Information</h4>
                <div className="grid gap-4 md:grid-cols-3">
                  <FormField
                    label="Mobile Number"
                    name="mobile"
                    type="tel"
                    value={formData.mobile}
                    onChange={(e) => updateField('mobile', e.target.value)}
                    error={errors.mobile}
                    hint="10-digit Indian mobile number"
                    required
                  />
                  <FormField
                    label="Work Email"
                    name="work_email"
                    type="email"
                    value={formData.work_email}
                    onChange={(e) => updateField('work_email', e.target.value)}
                    error={errors.work_email}
                    required
                  />
                  <FormField
                    label="Personal Email"
                    name="personal_email"
                    type="email"
                    value={formData.personal_email}
                    onChange={(e) => updateField('personal_email', e.target.value)}
                    error={errors.personal_email}
                  />
                </div>
              </div>

              {/* Emergency Contact */}
              <div>
                <h4 className="font-medium mb-4">Emergency Contact</h4>
                <div className="grid gap-4 md:grid-cols-3">
                  <FormField
                    label="Contact Name"
                    name="emergency_contact_name"
                    value={formData.emergency_contact_name}
                    onChange={(e) => updateField('emergency_contact_name', e.target.value)}
                  />
                  <FormField
                    label="Relationship"
                    name="emergency_contact_relationship"
                    value={formData.emergency_contact_relationship}
                    onChange={(e) => updateField('emergency_contact_relationship', e.target.value)}
                  />
                  <FormField
                    label="Phone"
                    name="emergency_contact_phone"
                    type="tel"
                    value={formData.emergency_contact_phone}
                    onChange={(e) => updateField('emergency_contact_phone', e.target.value)}
                    error={errors.emergency_contact_phone}
                  />
                </div>
              </div>

              {/* Current Address */}
              <div>
                <h4 className="font-medium mb-4">Current Address</h4>
                <div className="grid gap-4 md:grid-cols-2">
                  <FormField
                    label="Address Line 1"
                    name="current_address_line1"
                    value={formData.current_address_line1}
                    onChange={(e) => updateField('current_address_line1', e.target.value)}
                    error={errors.current_address_line1}
                    required
                  />
                  <FormField
                    label="Address Line 2"
                    name="current_address_line2"
                    value={formData.current_address_line2}
                    onChange={(e) => updateField('current_address_line2', e.target.value)}
                  />
                  <FormField
                    label="City"
                    name="current_address_city"
                    value={formData.current_address_city}
                    onChange={(e) => updateField('current_address_city', e.target.value)}
                    error={errors.current_address_city}
                    required
                  />
                  <FormSelect
                    label="State"
                    name="current_address_state"
                    value={formData.current_address_state}
                    onChange={(e) => updateField('current_address_state', e.target.value)}
                    options={INDIAN_STATES.map(s => ({ value: s.name, label: s.name }))}
                    placeholder="Select state"
                    error={errors.current_address_state}
                    required
                  />
                  <FormField
                    label="Pincode"
                    name="current_address_pincode"
                    value={formData.current_address_pincode}
                    onChange={(e) => updateField('current_address_pincode', e.target.value)}
                    error={errors.current_address_pincode}
                    required
                  />
                </div>
              </div>

              {/* Permanent Address */}
              <div>
                <h4 className="font-medium mb-4">Permanent Address</h4>
                <FormCheckbox
                  label="Same as current address"
                  name="permanent_address_same"
                  checked={formData.permanent_address_same}
                  onChange={(e) => updateField('permanent_address_same', e.target.checked)}
                />
                {!formData.permanent_address_same && (
                  <div className="grid gap-4 md:grid-cols-2 mt-4">
                    <FormField
                      label="Address Line 1"
                      name="permanent_address_line1"
                      value={formData.permanent_address_line1}
                      onChange={(e) => updateField('permanent_address_line1', e.target.value)}
                      error={errors.permanent_address_line1}
                      required
                    />
                    <FormField
                      label="Address Line 2"
                      name="permanent_address_line2"
                      value={formData.permanent_address_line2}
                      onChange={(e) => updateField('permanent_address_line2', e.target.value)}
                    />
                    <FormField
                      label="City"
                      name="permanent_address_city"
                      value={formData.permanent_address_city}
                      onChange={(e) => updateField('permanent_address_city', e.target.value)}
                      error={errors.permanent_address_city}
                      required
                    />
                    <FormSelect
                      label="State"
                      name="permanent_address_state"
                      value={formData.permanent_address_state}
                      onChange={(e) => updateField('permanent_address_state', e.target.value)}
                      options={INDIAN_STATES.map(s => ({ value: s.name, label: s.name }))}
                      placeholder="Select state"
                      error={errors.permanent_address_state}
                      required
                    />
                    <FormField
                      label="Pincode"
                      name="permanent_address_pincode"
                      value={formData.permanent_address_pincode}
                      onChange={(e) => updateField('permanent_address_pincode', e.target.value)}
                      error={errors.permanent_address_pincode}
                      required
                    />
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Step 2: Identity Documents */}
          {currentStep === 2 && (
            <div className="space-y-6">
              <div className="grid gap-4 md:grid-cols-2">
                <FormField
                  label="Aadhaar Number"
                  name="aadhaar"
                  value={formData.aadhaar}
                  onChange={(e) => updateField('aadhaar', e.target.value.replace(/\D/g, '').slice(0, 12))}
                  error={errors.aadhaar}
                  hint="12-digit Aadhaar number (starts with 2-9)"
                  maxLength={12}
                />
                <FormField
                  label="PAN Number"
                  name="pan"
                  value={formData.pan}
                  onChange={(e) => updateField('pan', e.target.value.toUpperCase().slice(0, 10))}
                  error={errors.pan}
                  hint="Format: ABCDE1234F"
                  required
                  maxLength={10}
                />
                <FormField
                  label="Passport Number"
                  name="passport_number"
                  value={formData.passport_number}
                  onChange={(e) => updateField('passport_number', e.target.value.toUpperCase())}
                  hint="Optional"
                />
                <FormField
                  label="Passport Expiry Date"
                  name="passport_expiry"
                  type="date"
                  value={formData.passport_expiry}
                  onChange={(e) => updateField('passport_expiry', e.target.value)}
                  disabled={!formData.passport_number}
                />
              </div>

              <div className="p-4 bg-blue-50 rounded-lg">
                <div className="flex items-start gap-3">
                  <AlertCircle className="h-5 w-5 text-blue-600 mt-0.5" />
                  <div className="text-sm">
                    <p className="font-medium text-blue-900">Document Validation</p>
                    <p className="text-blue-700 mt-1">
                      Aadhaar and PAN are validated according to Indian government specifications.
                      Aadhaar must be 12 digits and start with 2-9. PAN must follow the format AAAAA0000A.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Step 3: Employment Details */}
          {currentStep === 3 && (
            <div className="space-y-6">
              <div className="grid gap-4 md:grid-cols-2">
                <FormField
                  label="Employee ID"
                  name="employee_code"
                  value={formData.employee_code}
                  onChange={(e) => updateField('employee_code', e.target.value.toUpperCase())}
                  error={errors.employee_code}
                  hint="Unique employee identifier"
                  required
                />
                <FormField
                  label="Date of Joining"
                  name="date_of_joining"
                  type="date"
                  value={formData.date_of_joining}
                  onChange={(e) => updateField('date_of_joining', e.target.value)}
                  error={errors.date_of_joining}
                  required
                />
                <FormSelect
                  label="Department"
                  name="department_id"
                  value={formData.department_id}
                  onChange={(e) => updateField('department_id', e.target.value)}
                  options={departments}
                  placeholder="Select department"
                  error={errors.department_id}
                  required
                />
                <FormSelect
                  label="Designation"
                  name="designation_id"
                  value={formData.designation_id}
                  onChange={(e) => updateField('designation_id', e.target.value)}
                  options={designations}
                  placeholder="Select designation"
                  error={errors.designation_id}
                  required
                />
                <FormSelect
                  label="Reporting Manager"
                  name="reporting_to"
                  value={formData.reporting_to}
                  onChange={(e) => updateField('reporting_to', e.target.value)}
                  options={managers}
                  placeholder="Select manager"
                />
                <FormSelect
                  label="Work Location"
                  name="work_location"
                  value={formData.work_location}
                  onChange={(e) => updateField('work_location', e.target.value)}
                  options={workLocations}
                  placeholder="Select location"
                />
                <FormSelect
                  label="Employment Type"
                  name="employment_type"
                  value={formData.employment_type}
                  onChange={(e) => updateField('employment_type', e.target.value)}
                  options={EMPLOYMENT_TYPES.map(et => ({ value: et.value, label: et.label }))}
                  error={errors.employment_type}
                  required
                />
                <FormField
                  label="Probation Period (months)"
                  name="probation_period_months"
                  type="number"
                  value={formData.probation_period_months}
                  onChange={(e) => updateField('probation_period_months', e.target.value)}
                  min={0}
                  max={24}
                />
                <FormField
                  label="Notice Period (days)"
                  name="notice_period_days"
                  type="number"
                  value={formData.notice_period_days}
                  onChange={(e) => updateField('notice_period_days', e.target.value)}
                  min={0}
                  max={180}
                />
              </div>
            </div>
          )}

          {/* Step 4: Salary & Bank */}
          {currentStep === 4 && (
            <div className="space-y-8">
              {/* Salary Structure */}
              <div>
                <h4 className="font-medium mb-4">Salary Structure</h4>
                <div className="grid gap-4 md:grid-cols-3">
                  <FormField
                    label="Annual CTC"
                    name="annual_ctc"
                    type="number"
                    value={formData.annual_ctc}
                    onChange={(e) => updateField('annual_ctc', e.target.value)}
                    error={errors.annual_ctc}
                    hint="Total annual cost to company"
                    required
                  />
                  <FormField
                    label="Basic (%)"
                    name="basic_percentage"
                    type="number"
                    value={formData.basic_percentage}
                    onChange={(e) => updateField('basic_percentage', e.target.value)}
                    min={40}
                    max={60}
                    hint="40-60% of CTC"
                  />
                  <FormField
                    label="HRA (%)"
                    name="hra_percentage"
                    type="number"
                    value={formData.hra_percentage}
                    onChange={(e) => updateField('hra_percentage', e.target.value)}
                    min={10}
                    max={50}
                    hint="% of CTC"
                  />
                </div>

                {/* Salary Breakdown Preview */}
                {formData.annual_ctc && (
                  <div className="mt-4 p-4 bg-muted rounded-lg">
                    <h5 className="font-medium mb-3">Monthly Salary Breakdown</h5>
                    <div className="grid gap-4 md:grid-cols-2">
                      <div>
                        <p className="text-sm text-muted-foreground">Earnings</p>
                        <div className="space-y-1 mt-2">
                          <div className="flex justify-between text-sm">
                            <span>Basic</span>
                            <span>Rs. {salaryBreakdown.basic.toLocaleString('en-IN', { maximumFractionDigits: 0 })}</span>
                          </div>
                          <div className="flex justify-between text-sm">
                            <span>HRA</span>
                            <span>Rs. {salaryBreakdown.hra.toLocaleString('en-IN', { maximumFractionDigits: 0 })}</span>
                          </div>
                          <div className="flex justify-between text-sm">
                            <span>Special Allowance</span>
                            <span>Rs. {salaryBreakdown.specialAllowance.toLocaleString('en-IN', { maximumFractionDigits: 0 })}</span>
                          </div>
                          <div className="flex justify-between font-medium pt-2 border-t">
                            <span>Gross</span>
                            <span>Rs. {salaryBreakdown.gross.toLocaleString('en-IN', { maximumFractionDigits: 0 })}</span>
                          </div>
                        </div>
                      </div>
                      <div>
                        <p className="text-sm text-muted-foreground">Deductions</p>
                        <div className="space-y-1 mt-2">
                          <div className="flex justify-between text-sm">
                            <span>PF (Employee)</span>
                            <span>Rs. {salaryBreakdown.pfEmployee.toLocaleString('en-IN', { maximumFractionDigits: 0 })}</span>
                          </div>
                          <div className="flex justify-between font-medium pt-2 border-t">
                            <span>Net Salary</span>
                            <span className="text-green-600">Rs. {salaryBreakdown.net.toLocaleString('en-IN', { maximumFractionDigits: 0 })}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                <div className="grid gap-4 md:grid-cols-2 mt-4">
                  <FormCheckbox
                    label="PF Opt-in"
                    name="pf_opt_in"
                    description="Employee will contribute to Provident Fund"
                    checked={formData.pf_opt_in}
                    onChange={(e) => updateField('pf_opt_in', e.target.checked)}
                  />
                  <FormCheckbox
                    label="ESI Applicable"
                    name="esi_applicable"
                    description="Employee is eligible for ESI (gross <= Rs. 21,000)"
                    checked={formData.esi_applicable}
                    onChange={(e) => updateField('esi_applicable', e.target.checked)}
                  />
                </div>
              </div>

              {/* Bank Details */}
              <div>
                <h4 className="font-medium mb-4">Bank Details</h4>
                <div className="grid gap-4 md:grid-cols-2">
                  <FormField
                    label="Account Holder Name"
                    name="bank_account_holder"
                    value={formData.bank_account_holder}
                    onChange={(e) => updateField('bank_account_holder', e.target.value)}
                    error={errors.bank_account_holder}
                    required
                  />
                  <FormField
                    label="Account Number"
                    name="bank_account_number"
                    value={formData.bank_account_number}
                    onChange={(e) => updateField('bank_account_number', e.target.value.replace(/\D/g, ''))}
                    error={errors.bank_account_number}
                    hint="9-18 digit account number"
                    required
                  />
                  <FormField
                    label="Bank Name"
                    name="bank_name"
                    value={formData.bank_name}
                    onChange={(e) => updateField('bank_name', e.target.value)}
                    error={errors.bank_name}
                    required
                  />
                  <FormField
                    label="Branch Name"
                    name="bank_branch"
                    value={formData.bank_branch}
                    onChange={(e) => updateField('bank_branch', e.target.value)}
                  />
                  <FormField
                    label="IFSC Code"
                    name="bank_ifsc"
                    value={formData.bank_ifsc}
                    onChange={(e) => updateField('bank_ifsc', e.target.value.toUpperCase().slice(0, 11))}
                    error={errors.bank_ifsc}
                    hint="Format: XXXX0XXXXXX"
                    required
                    maxLength={11}
                  />
                  <FormField
                    label="UAN (if existing)"
                    name="uan"
                    value={formData.uan}
                    onChange={(e) => updateField('uan', e.target.value.replace(/\D/g, '').slice(0, 12))}
                    hint="12-digit Universal Account Number for PF"
                    maxLength={12}
                  />
                </div>
              </div>
            </div>
          )}

          {/* Step 5: Documents Upload */}
          {currentStep === 5 && (
            <div className="space-y-6">
              <div className="grid gap-6 md:grid-cols-2">
                <FileUpload
                  label="Employee Photo"
                  name="photo"
                  accept="image/*"
                  maxSize={2}
                  value={formData.photo}
                  onChange={(files) => updateField('photo', files)}
                  hint="Passport size photo (max 2MB)"
                />
                <FileUpload
                  label="Aadhaar Card"
                  name="aadhaar_doc"
                  accept=".pdf,.jpg,.jpeg,.png"
                  maxSize={5}
                  value={formData.aadhaar_doc}
                  onChange={(files) => updateField('aadhaar_doc', files)}
                />
                <FileUpload
                  label="PAN Card"
                  name="pan_doc"
                  accept=".pdf,.jpg,.jpeg,.png"
                  maxSize={5}
                  value={formData.pan_doc}
                  onChange={(files) => updateField('pan_doc', files)}
                />
                <FileUpload
                  label="Passport"
                  name="passport_doc"
                  accept=".pdf,.jpg,.jpeg,.png"
                  maxSize={5}
                  value={formData.passport_doc}
                  onChange={(files) => updateField('passport_doc', files)}
                  hint="Optional"
                />
                <FileUpload
                  label="Offer Letter"
                  name="offer_letter"
                  accept=".pdf"
                  maxSize={5}
                  value={formData.offer_letter}
                  onChange={(files) => updateField('offer_letter', files)}
                />
                <FileUpload
                  label="Joining Report"
                  name="joining_report"
                  accept=".pdf"
                  maxSize={5}
                  value={formData.joining_report}
                  onChange={(files) => updateField('joining_report', files)}
                />
                <FileUpload
                  label="Previous Employment Documents"
                  name="previous_employment_docs"
                  accept=".pdf"
                  maxSize={10}
                  maxFiles={5}
                  multiple
                  value={formData.previous_employment_docs}
                  onChange={(files) => updateField('previous_employment_docs', files)}
                  hint="Relieving letter, experience letter, payslips, etc."
                />
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Navigation Buttons */}
      <div className="flex justify-between">
        <Button
          variant="outline"
          onClick={currentStep === 1 ? () => router.back() : handlePrevious}
        >
          <ChevronLeft className="h-4 w-4 mr-2" />
          {currentStep === 1 ? 'Cancel' : 'Previous'}
        </Button>

        {currentStep < 5 ? (
          <Button onClick={handleNext}>
            Next
            <ChevronRight className="h-4 w-4 ml-2" />
          </Button>
        ) : (
          <Button onClick={handleSubmit} disabled={isSubmitting}>
            {isSubmitting ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Saving...
              </>
            ) : (
              <>
                <Check className="h-4 w-4 mr-2" />
                {isEdit ? 'Update Employee' : 'Create Employee'}
              </>
            )}
          </Button>
        )}
      </div>
    </div>
  )
}

export default EmployeeForm
