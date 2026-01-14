// GanaPortal Validation Utilities
// FE-001: India-specific Validators

// ============================================================================
// Email Validation
// ============================================================================

export function isValidEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

// ============================================================================
// Phone Validation (Indian)
// ============================================================================

export function isValidPhone(phone: string): boolean {
  // Remove spaces and dashes
  const cleaned = phone.replace(/[\s-]/g, '')

  // Indian mobile: 10 digits starting with 6-9
  const mobileRegex = /^[6-9]\d{9}$/

  // With country code
  const withCountryCode = /^(\+91|91)?[6-9]\d{9}$/

  return mobileRegex.test(cleaned) || withCountryCode.test(cleaned)
}

// ============================================================================
// PAN Validation
// ============================================================================

export function isValidPAN(pan: string): boolean {
  // PAN format: ABCDE1234F
  // 5 letters, 4 digits, 1 letter
  const panRegex = /^[A-Z]{5}[0-9]{4}[A-Z]{1}$/
  return panRegex.test(pan.toUpperCase())
}

export function getPANType(pan: string): string {
  if (!isValidPAN(pan)) return 'Invalid'

  const fourthChar = pan.charAt(3).toUpperCase()
  const types: Record<string, string> = {
    'P': 'Individual',
    'C': 'Company',
    'H': 'HUF',
    'A': 'AOP',
    'B': 'BOI',
    'G': 'Government',
    'J': 'Artificial Juridical Person',
    'L': 'Local Authority',
    'F': 'Firm/LLP',
    'T': 'Trust'
  }

  return types[fourthChar] || 'Unknown'
}

// ============================================================================
// Aadhaar Validation
// ============================================================================

export function isValidAadhaar(aadhaar: string): boolean {
  // Aadhaar: 12 digits, doesn't start with 0 or 1
  const cleaned = aadhaar.replace(/\s/g, '')
  const aadhaarRegex = /^[2-9]\d{11}$/
  return aadhaarRegex.test(cleaned)
}

export function formatAadhaar(aadhaar: string): string {
  const cleaned = aadhaar.replace(/\s/g, '')
  if (cleaned.length !== 12) return aadhaar

  return `${cleaned.slice(0, 4)} ${cleaned.slice(4, 8)} ${cleaned.slice(8)}`
}

// ============================================================================
// GSTIN Validation
// ============================================================================

export function isValidGSTIN(gstin: string): boolean {
  // GSTIN format: 2 state code + 10 PAN + 1 entity + 1 Z + 1 checksum
  // Example: 29ABCDE1234F1Z5
  const gstinRegex = /^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$/
  return gstinRegex.test(gstin.toUpperCase())
}

export function getStateFromGSTIN(gstin: string): string {
  if (!isValidGSTIN(gstin)) return 'Invalid'

  const stateCodes: Record<string, string> = {
    '01': 'Jammu & Kashmir',
    '02': 'Himachal Pradesh',
    '03': 'Punjab',
    '04': 'Chandigarh',
    '05': 'Uttarakhand',
    '06': 'Haryana',
    '07': 'Delhi',
    '08': 'Rajasthan',
    '09': 'Uttar Pradesh',
    '10': 'Bihar',
    '11': 'Sikkim',
    '12': 'Arunachal Pradesh',
    '13': 'Nagaland',
    '14': 'Manipur',
    '15': 'Mizoram',
    '16': 'Tripura',
    '17': 'Meghalaya',
    '18': 'Assam',
    '19': 'West Bengal',
    '20': 'Jharkhand',
    '21': 'Odisha',
    '22': 'Chhattisgarh',
    '23': 'Madhya Pradesh',
    '24': 'Gujarat',
    '26': 'Dadra and Nagar Haveli',
    '27': 'Maharashtra',
    '28': 'Andhra Pradesh (old)',
    '29': 'Karnataka',
    '30': 'Goa',
    '31': 'Lakshadweep',
    '32': 'Kerala',
    '33': 'Tamil Nadu',
    '34': 'Puducherry',
    '35': 'Andaman and Nicobar Islands',
    '36': 'Telangana',
    '37': 'Andhra Pradesh',
    '38': 'Ladakh'
  }

  const stateCode = gstin.slice(0, 2)
  return stateCodes[stateCode] || 'Unknown'
}

// ============================================================================
// UAN Validation (Universal Account Number for PF)
// ============================================================================

export function isValidUAN(uan: string): boolean {
  // UAN: 12 digit number
  const uanRegex = /^\d{12}$/
  return uanRegex.test(uan.replace(/\s/g, ''))
}

// ============================================================================
// IFSC Validation
// ============================================================================

export function isValidIFSC(ifsc: string): boolean {
  // IFSC format: 4 letters (bank) + 0 + 6 alphanumeric (branch)
  const ifscRegex = /^[A-Z]{4}0[A-Z0-9]{6}$/
  return ifscRegex.test(ifsc.toUpperCase())
}

export function getBankFromIFSC(ifsc: string): string {
  if (!isValidIFSC(ifsc)) return 'Invalid'
  return ifsc.slice(0, 4).toUpperCase()
}

// ============================================================================
// Bank Account Validation
// ============================================================================

export function isValidBankAccount(accountNumber: string): boolean {
  // Indian bank account: 9-18 digits
  const cleaned = accountNumber.replace(/\s/g, '')
  return /^\d{9,18}$/.test(cleaned)
}

// ============================================================================
// HSN Code Validation
// ============================================================================

export function isValidHSN(hsn: string): boolean {
  // HSN: 2, 4, 6, or 8 digits
  return /^\d{2}$|^\d{4}$|^\d{6}$|^\d{8}$/.test(hsn)
}

// ============================================================================
// Pincode Validation
// ============================================================================

export function isValidPincode(pincode: string): boolean {
  // Indian pincode: 6 digits, doesn't start with 0
  return /^[1-9]\d{5}$/.test(pincode)
}

// ============================================================================
// Password Validation
// ============================================================================

export interface PasswordValidation {
  isValid: boolean
  errors: string[]
  strength: 'weak' | 'medium' | 'strong'
}

export function validatePassword(password: string): PasswordValidation {
  const errors: string[] = []

  if (password.length < 8) {
    errors.push('Password must be at least 8 characters')
  }
  if (!/[A-Z]/.test(password)) {
    errors.push('Password must contain an uppercase letter')
  }
  if (!/[a-z]/.test(password)) {
    errors.push('Password must contain a lowercase letter')
  }
  if (!/[0-9]/.test(password)) {
    errors.push('Password must contain a number')
  }
  if (!/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
    errors.push('Password must contain a special character')
  }

  let strength: 'weak' | 'medium' | 'strong' = 'weak'
  if (errors.length === 0) {
    strength = password.length >= 12 ? 'strong' : 'medium'
  } else if (errors.length <= 2) {
    strength = 'medium'
  }

  return {
    isValid: errors.length === 0,
    errors,
    strength
  }
}

// ============================================================================
// Date Validation
// ============================================================================

export function isValidDate(dateString: string): boolean {
  const date = new Date(dateString)
  return !isNaN(date.getTime())
}

export function isDateInFuture(dateString: string): boolean {
  const date = new Date(dateString)
  return date > new Date()
}

export function isDateInPast(dateString: string): boolean {
  const date = new Date(dateString)
  return date < new Date()
}

export function isAgeAbove18(dateOfBirth: string): boolean {
  const dob = new Date(dateOfBirth)
  const today = new Date()
  const age = today.getFullYear() - dob.getFullYear()
  const monthDiff = today.getMonth() - dob.getMonth()

  if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < dob.getDate())) {
    return age - 1 >= 18
  }

  return age >= 18
}

// ============================================================================
// Generic Validators
// ============================================================================

export function isRequired(value: unknown): boolean {
  if (value === null || value === undefined) return false
  if (typeof value === 'string') return value.trim().length > 0
  if (Array.isArray(value)) return value.length > 0
  return true
}

export function isMinLength(value: string, min: number): boolean {
  return value.length >= min
}

export function isMaxLength(value: string, max: number): boolean {
  return value.length <= max
}

export function isInRange(value: number, min: number, max: number): boolean {
  return value >= min && value <= max
}
