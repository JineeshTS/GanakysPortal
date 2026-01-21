/**
 * TEST-003: Frontend Unit Test Agent
 * Validator Tests
 *
 * Tests for India-specific validation functions
 */
import { describe, it, expect } from 'vitest'
import {
  isValidEmail,
  isValidPhone,
  isValidPAN,
  getPANType,
  isValidAadhaar,
  formatAadhaar,
  isValidGSTIN,
  getStateFromGSTIN,
  isValidUAN,
  isValidIFSC,
  getBankFromIFSC,
  isValidBankAccount,
  isValidHSN,
  isValidPincode,
  validatePassword,
  isValidDate,
  isDateInFuture,
  isDateInPast,
  isAgeAbove18,
  isRequired,
  isMinLength,
  isMaxLength,
  isInRange,
} from '@/lib/validators'

// =============================================================================
// Email Validation Tests
// =============================================================================

describe('isValidEmail', () => {
  it('validates correct emails', () => {
    expect(isValidEmail('test@example.com')).toBe(true)
    expect(isValidEmail('user.name@domain.co.in')).toBe(true)
    expect(isValidEmail('admin@ganakys.com')).toBe(true)
  })

  it('rejects invalid emails', () => {
    expect(isValidEmail('invalid')).toBe(false)
    expect(isValidEmail('invalid@')).toBe(false)
    expect(isValidEmail('@domain.com')).toBe(false)
    expect(isValidEmail('test @example.com')).toBe(false)
  })
})

// =============================================================================
// Phone Validation Tests (Indian)
// =============================================================================

describe('isValidPhone', () => {
  it('validates 10-digit Indian mobile numbers', () => {
    expect(isValidPhone('9876543210')).toBe(true)
    expect(isValidPhone('8765432109')).toBe(true)
    expect(isValidPhone('7654321098')).toBe(true)
    expect(isValidPhone('6543210987')).toBe(true)
  })

  it('validates numbers with country code', () => {
    expect(isValidPhone('+919876543210')).toBe(true)
    expect(isValidPhone('919876543210')).toBe(true)
  })

  it('rejects invalid phone numbers', () => {
    expect(isValidPhone('1234567890')).toBe(false) // Starts with 1
    expect(isValidPhone('5678901234')).toBe(false) // Starts with 5
    expect(isValidPhone('98765432')).toBe(false)   // 8 digits
    expect(isValidPhone('98765432101')).toBe(false) // 11 digits
  })
})

// =============================================================================
// PAN Validation Tests
// =============================================================================

describe('isValidPAN', () => {
  it('validates correct PAN format', () => {
    expect(isValidPAN('ABCPK1234A')).toBe(true)
    expect(isValidPAN('AAACT1234B')).toBe(true)
    expect(isValidPAN('abcpk1234a')).toBe(true) // lowercase
  })

  it('rejects invalid PAN', () => {
    expect(isValidPAN('ABC1K1234A')).toBe(false)  // Number in 4th position
    expect(isValidPAN('ABCPK123A')).toBe(false)   // 3 digits
    expect(isValidPAN('ABCPK12345')).toBe(false)  // 5 digits
    expect(isValidPAN('ABCPK1234')).toBe(false)   // Missing last letter
  })
})

describe('getPANType', () => {
  it('identifies PAN holder type', () => {
    expect(getPANType('ABCPP1234A')).toBe('Individual')
    expect(getPANType('ABCPC1234A')).toBe('Company')
    expect(getPANType('ABCPH1234A')).toBe('HUF')
    expect(getPANType('ABCPF1234A')).toBe('Firm/LLP')
    expect(getPANType('ABCPT1234A')).toBe('Trust')
  })

  it('returns Invalid for invalid PAN', () => {
    expect(getPANType('INVALID')).toBe('Invalid')
  })
})

// =============================================================================
// Aadhaar Validation Tests
// =============================================================================

describe('isValidAadhaar', () => {
  it('validates 12-digit Aadhaar', () => {
    expect(isValidAadhaar('234567890123')).toBe(true)
    expect(isValidAadhaar('999988887777')).toBe(true)
  })

  it('validates Aadhaar with spaces', () => {
    expect(isValidAadhaar('2345 6789 0123')).toBe(true)
  })

  it('rejects Aadhaar starting with 0 or 1', () => {
    expect(isValidAadhaar('012345678901')).toBe(false)
    expect(isValidAadhaar('123456789012')).toBe(false)
  })

  it('rejects invalid length', () => {
    expect(isValidAadhaar('12345678901')).toBe(false)  // 11 digits
    expect(isValidAadhaar('1234567890123')).toBe(false) // 13 digits
  })
})

describe('formatAadhaar', () => {
  it('formats Aadhaar with spaces', () => {
    expect(formatAadhaar('234567890123')).toBe('2345 6789 0123')
  })

  it('handles already formatted Aadhaar', () => {
    expect(formatAadhaar('2345 6789 0123')).toBe('2345 6789 0123')
  })
})

// =============================================================================
// GSTIN Validation Tests
// =============================================================================

describe('isValidGSTIN', () => {
  it('validates correct GSTIN format', () => {
    expect(isValidGSTIN('29AABCG1234A1Z5')).toBe(true)
    expect(isValidGSTIN('27AABCM1234A1Z5')).toBe(true)
    expect(isValidGSTIN('07AABCD1234A1Z5')).toBe(true)
  })

  it('validates lowercase GSTIN', () => {
    expect(isValidGSTIN('29aabcg1234a1z5')).toBe(true)
  })

  it('rejects invalid GSTIN', () => {
    expect(isValidGSTIN('123456789012345')).toBe(false)
    expect(isValidGSTIN('29AABCG1234A1Z')).toBe(false)  // Missing last digit
    expect(isValidGSTIN('29AABCG1234A1X5')).toBe(false) // 'X' instead of 'Z'
  })
})

describe('getStateFromGSTIN', () => {
  it('returns correct state name', () => {
    expect(getStateFromGSTIN('29AABCG1234A1Z5')).toBe('Karnataka')
    expect(getStateFromGSTIN('27AABCM1234A1Z5')).toBe('Maharashtra')
    expect(getStateFromGSTIN('07AABCD1234A1Z5')).toBe('Delhi')
    expect(getStateFromGSTIN('33AABCT1234A1Z5')).toBe('Tamil Nadu')
  })

  it('returns Invalid for invalid GSTIN', () => {
    expect(getStateFromGSTIN('INVALID')).toBe('Invalid')
  })
})

// =============================================================================
// UAN Validation Tests
// =============================================================================

describe('isValidUAN', () => {
  it('validates 12-digit UAN', () => {
    expect(isValidUAN('101234567890')).toBe(true)
    expect(isValidUAN('100000000001')).toBe(true)
  })

  it('validates UAN with spaces', () => {
    expect(isValidUAN('1012 3456 7890')).toBe(true)
  })

  it('rejects invalid UAN', () => {
    expect(isValidUAN('1012345678')).toBe(false)    // 10 digits
    expect(isValidUAN('10123456789012')).toBe(false) // 14 digits
    expect(isValidUAN('10AB34567890')).toBe(false)   // Letters
  })
})

// =============================================================================
// IFSC Validation Tests
// =============================================================================

describe('isValidIFSC', () => {
  it('validates correct IFSC format', () => {
    expect(isValidIFSC('SBIN0001234')).toBe(true)
    expect(isValidIFSC('HDFC0000123')).toBe(true)
    expect(isValidIFSC('ICIC0001234')).toBe(true)
  })

  it('validates lowercase IFSC', () => {
    expect(isValidIFSC('sbin0001234')).toBe(true)
  })

  it('rejects invalid IFSC', () => {
    expect(isValidIFSC('SBIN1001234')).toBe(false)  // 5th char not 0
    expect(isValidIFSC('SBI0001234')).toBe(false)   // 3 letter bank code
    expect(isValidIFSC('SBINN001234')).toBe(false)  // 5 letter bank code
  })
})

describe('getBankFromIFSC', () => {
  it('extracts bank code from IFSC', () => {
    expect(getBankFromIFSC('SBIN0001234')).toBe('SBIN')
    expect(getBankFromIFSC('HDFC0000123')).toBe('HDFC')
  })

  it('returns Invalid for invalid IFSC', () => {
    expect(getBankFromIFSC('INVALID')).toBe('Invalid')
  })
})

// =============================================================================
// Bank Account Validation Tests
// =============================================================================

describe('isValidBankAccount', () => {
  it('validates bank account numbers (9-18 digits)', () => {
    expect(isValidBankAccount('123456789')).toBe(true)       // 9 digits
    expect(isValidBankAccount('1234567890123456')).toBe(true) // 16 digits
    expect(isValidBankAccount('123456789012345678')).toBe(true) // 18 digits
  })

  it('rejects invalid account numbers', () => {
    expect(isValidBankAccount('12345678')).toBe(false)        // 8 digits
    expect(isValidBankAccount('1234567890123456789')).toBe(false) // 19 digits
    expect(isValidBankAccount('123ABC789')).toBe(false)       // Letters
  })
})

// =============================================================================
// HSN Code Validation Tests
// =============================================================================

describe('isValidHSN', () => {
  it('validates HSN codes (2, 4, 6, 8 digits)', () => {
    expect(isValidHSN('99')).toBe(true)      // 2 digits
    expect(isValidHSN('9983')).toBe(true)    // 4 digits
    expect(isValidHSN('998314')).toBe(true)  // 6 digits
    expect(isValidHSN('99831400')).toBe(true) // 8 digits
  })

  it('rejects invalid HSN codes', () => {
    expect(isValidHSN('9')).toBe(false)       // 1 digit
    expect(isValidHSN('999')).toBe(false)     // 3 digits
    expect(isValidHSN('99831')).toBe(false)   // 5 digits
    expect(isValidHSN('9983140')).toBe(false) // 7 digits
  })
})

// =============================================================================
// Pincode Validation Tests
// =============================================================================

describe('isValidPincode', () => {
  it('validates Indian pincodes', () => {
    expect(isValidPincode('560001')).toBe(true)
    expect(isValidPincode('400001')).toBe(true)
    expect(isValidPincode('110001')).toBe(true)
  })

  it('rejects pincodes starting with 0', () => {
    expect(isValidPincode('060001')).toBe(false)
  })

  it('rejects invalid length', () => {
    expect(isValidPincode('56000')).toBe(false)   // 5 digits
    expect(isValidPincode('5600001')).toBe(false) // 7 digits
  })
})

// =============================================================================
// Password Validation Tests
// =============================================================================

describe('validatePassword', () => {
  it('validates strong password', () => {
    const result = validatePassword('SecurePass123!')
    expect(result.isValid).toBe(true)
    expect(result.errors).toHaveLength(0)
    expect(result.strength).toBe('strong')
  })

  it('validates medium password', () => {
    const result = validatePassword('Pass123!')
    expect(result.isValid).toBe(true)
    expect(result.strength).toBe('medium')
  })

  it('reports missing requirements', () => {
    const result = validatePassword('weak')
    expect(result.isValid).toBe(false)
    expect(result.errors).toContain('Password must be at least 8 characters')
    expect(result.errors).toContain('Password must contain an uppercase letter')
    expect(result.errors).toContain('Password must contain a number')
    expect(result.errors).toContain('Password must contain a special character')
  })
})

// =============================================================================
// Date Validation Tests
// =============================================================================

describe('isValidDate', () => {
  it('validates correct dates', () => {
    expect(isValidDate('2026-01-06')).toBe(true)
    expect(isValidDate('2025-12-31')).toBe(true)
  })

  it('rejects invalid dates', () => {
    expect(isValidDate('invalid')).toBe(false)
    expect(isValidDate('2026-13-01')).toBe(false) // Month 13
  })
})

describe('isDateInFuture', () => {
  it('identifies future dates', () => {
    expect(isDateInFuture('2030-01-01')).toBe(true)
  })

  it('identifies past dates', () => {
    expect(isDateInFuture('2020-01-01')).toBe(false)
  })
})

describe('isDateInPast', () => {
  it('identifies past dates', () => {
    expect(isDateInPast('2020-01-01')).toBe(true)
  })

  it('identifies future dates', () => {
    expect(isDateInPast('2030-01-01')).toBe(false)
  })
})

describe('isAgeAbove18', () => {
  it('validates age above 18', () => {
    expect(isAgeAbove18('1990-01-01')).toBe(true)
    expect(isAgeAbove18('2000-01-01')).toBe(true)
  })

  it('rejects age below 18', () => {
    expect(isAgeAbove18('2015-01-01')).toBe(false)
    expect(isAgeAbove18('2020-01-01')).toBe(false)
  })
})

// =============================================================================
// Generic Validator Tests
// =============================================================================

describe('isRequired', () => {
  it('validates non-empty values', () => {
    expect(isRequired('test')).toBe(true)
    expect(isRequired(123)).toBe(true)
    expect(isRequired([1, 2, 3])).toBe(true)
  })

  it('rejects empty values', () => {
    expect(isRequired('')).toBe(false)
    expect(isRequired('   ')).toBe(false)
    expect(isRequired(null)).toBe(false)
    expect(isRequired(undefined)).toBe(false)
    expect(isRequired([])).toBe(false)
  })
})

describe('isMinLength', () => {
  it('validates minimum length', () => {
    expect(isMinLength('hello', 3)).toBe(true)
    expect(isMinLength('hi', 2)).toBe(true)
  })

  it('rejects below minimum', () => {
    expect(isMinLength('hi', 5)).toBe(false)
  })
})

describe('isMaxLength', () => {
  it('validates maximum length', () => {
    expect(isMaxLength('hello', 10)).toBe(true)
    expect(isMaxLength('hi', 2)).toBe(true)
  })

  it('rejects above maximum', () => {
    expect(isMaxLength('hello world', 5)).toBe(false)
  })
})

describe('isInRange', () => {
  it('validates values in range', () => {
    expect(isInRange(5, 1, 10)).toBe(true)
    expect(isInRange(1, 1, 10)).toBe(true)  // min boundary
    expect(isInRange(10, 1, 10)).toBe(true) // max boundary
  })

  it('rejects values outside range', () => {
    expect(isInRange(0, 1, 10)).toBe(false)
    expect(isInRange(11, 1, 10)).toBe(false)
  })
})
