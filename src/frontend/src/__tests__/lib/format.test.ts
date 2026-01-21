/**
 * TEST-003: Frontend Unit Test Agent
 * Format Utility Tests
 *
 * Tests for India-specific formatting functions
 */
import { describe, it, expect } from 'vitest'
import {
  formatCurrency,
  formatIndianNumber,
  formatLakhs,
  formatCrores,
  formatCurrencySmart,
  formatDate,
  formatTime,
  formatRelativeTime,
  getMonthName,
  getFinancialYear,
  formatNumber,
  formatPercentage,
  formatPhone,
  formatPAN,
  formatGSTIN,
  truncate,
  capitalize,
  snakeToTitle,
  pluralize,
} from '@/lib/format'

// =============================================================================
// Currency Formatting Tests
// =============================================================================

describe('formatCurrency', () => {
  it('formats basic amount with rupee symbol', () => {
    expect(formatCurrency(1000)).toBe('₹1,000.00')
    expect(formatCurrency(50000)).toBe('₹50,000.00')
  })

  it('formats large amounts in Indian numbering system', () => {
    expect(formatCurrency(100000)).toBe('₹1,00,000.00')
    expect(formatCurrency(1000000)).toBe('₹10,00,000.00')
    expect(formatCurrency(10000000)).toBe('₹1,00,00,000.00')
  })

  it('handles negative amounts', () => {
    expect(formatCurrency(-5000)).toBe('-₹5,000.00')
  })

  it('handles null and undefined', () => {
    expect(formatCurrency(null)).toBe('-')
    expect(formatCurrency(undefined)).toBe('-')
  })

  it('supports options', () => {
    expect(formatCurrency(1000, { showSymbol: false })).toBe('1,000.00')
    expect(formatCurrency(1000, { decimals: 0 })).toBe('₹1,000')
    expect(formatCurrency(1000, { showSign: true })).toBe('+₹1,000.00')
  })
})

describe('formatIndianNumber', () => {
  it('formats numbers in Indian system (lakhs, crores)', () => {
    expect(formatIndianNumber(1000, 0)).toBe('1,000')
    expect(formatIndianNumber(10000, 0)).toBe('10,000')
    expect(formatIndianNumber(100000, 0)).toBe('1,00,000')
    expect(formatIndianNumber(1000000, 0)).toBe('10,00,000')
    expect(formatIndianNumber(10000000, 0)).toBe('1,00,00,000')
    expect(formatIndianNumber(100000000, 0)).toBe('10,00,00,000')
  })

  it('handles decimal places', () => {
    expect(formatIndianNumber(12345.67, 2)).toBe('12,345.67')
    expect(formatIndianNumber(123456.789, 2)).toBe('1,23,456.79')
  })
})

describe('formatLakhs', () => {
  it('converts to lakhs format', () => {
    expect(formatLakhs(100000)).toBe('1.00 L')
    expect(formatLakhs(500000)).toBe('5.00 L')
    expect(formatLakhs(1250000)).toBe('12.50 L')
  })
})

describe('formatCrores', () => {
  it('converts to crores format', () => {
    expect(formatCrores(10000000)).toBe('1.00 Cr')
    expect(formatCrores(50000000)).toBe('5.00 Cr')
    expect(formatCrores(125000000)).toBe('12.50 Cr')
  })
})

describe('formatCurrencySmart', () => {
  it('auto-selects format based on amount', () => {
    expect(formatCurrencySmart(50000)).toContain('₹')
    expect(formatCurrencySmart(500000)).toContain('L')
    expect(formatCurrencySmart(50000000)).toContain('Cr')
  })
})

// =============================================================================
// Date Formatting Tests
// =============================================================================

describe('formatDate', () => {
  it('formats date in Indian format (DD/MM/YYYY)', () => {
    const date = '2026-01-06'
    expect(formatDate(date)).toBe('06/01/2026')
  })

  it('supports long format', () => {
    const date = '2026-01-06'
    expect(formatDate(date, { format: 'long' })).toBe('06 Jan 2026')
  })

  it('supports ISO format', () => {
    const date = '2026-01-06'
    expect(formatDate(date, { format: 'iso' })).toBe('2026-01-06')
  })

  it('handles null and undefined', () => {
    expect(formatDate(null)).toBe('-')
    expect(formatDate(undefined)).toBe('-')
  })

  it('can show time', () => {
    const date = '2026-01-06T10:30:00'
    expect(formatDate(date, { showTime: true })).toContain('10:30')
  })
})

describe('formatTime', () => {
  it('formats time in 12-hour format', () => {
    expect(formatTime('2026-01-06T10:30:00')).toBe('10:30 AM')
    expect(formatTime('2026-01-06T14:30:00')).toBe('2:30 PM')
    expect(formatTime('2026-01-06T00:00:00')).toBe('12:00 AM')
  })

  it('handles null and undefined', () => {
    expect(formatTime(null)).toBe('-')
    expect(formatTime(undefined)).toBe('-')
  })
})

describe('getMonthName', () => {
  it('returns month name', () => {
    expect(getMonthName(1)).toBe('January')
    expect(getMonthName(4)).toBe('April')
    expect(getMonthName(12)).toBe('December')
  })

  it('returns short month name', () => {
    expect(getMonthName(1, true)).toBe('Jan')
    expect(getMonthName(4, true)).toBe('Apr')
    expect(getMonthName(12, true)).toBe('Dec')
  })
})

describe('getFinancialYear', () => {
  it('returns correct FY for April onwards', () => {
    const aprilDate = new Date(2025, 3, 15) // April 2025
    expect(getFinancialYear(aprilDate)).toBe('FY 2025-26')
  })

  it('returns correct FY for Jan-March', () => {
    const janDate = new Date(2026, 0, 15) // January 2026
    expect(getFinancialYear(janDate)).toBe('FY 2025-26')
  })
})

// =============================================================================
// Number Formatting Tests
// =============================================================================

describe('formatNumber', () => {
  it('formats numbers with Indian commas', () => {
    expect(formatNumber(100000)).toBe('1,00,000')
  })

  it('handles null and undefined', () => {
    expect(formatNumber(null)).toBe('-')
    expect(formatNumber(undefined)).toBe('-')
  })
})

describe('formatPercentage', () => {
  it('formats percentage with decimals', () => {
    expect(formatPercentage(12.5)).toBe('12.50%')
    expect(formatPercentage(100)).toBe('100.00%')
  })

  it('handles custom decimals', () => {
    expect(formatPercentage(12.345, 1)).toBe('12.3%')
    expect(formatPercentage(12.345, 0)).toBe('12%')
  })

  it('handles null and undefined', () => {
    expect(formatPercentage(null)).toBe('-')
  })
})

// =============================================================================
// Phone & ID Formatting Tests
// =============================================================================

describe('formatPhone', () => {
  it('formats 10-digit Indian phone numbers', () => {
    expect(formatPhone('9876543210')).toBe('+91 98765 43210')
  })

  it('formats numbers with country code', () => {
    expect(formatPhone('919876543210')).toBe('+91 98765 43210')
  })

  it('handles null and undefined', () => {
    expect(formatPhone(null)).toBe('-')
  })
})

describe('formatPAN', () => {
  it('formats PAN in uppercase', () => {
    expect(formatPAN('abcpk1234a')).toBe('ABCPK1234A')
  })

  it('handles null and undefined', () => {
    expect(formatPAN(null)).toBe('-')
  })
})

describe('formatGSTIN', () => {
  it('formats GSTIN in uppercase', () => {
    expect(formatGSTIN('29aabcg1234a1z5')).toBe('29AABCG1234A1Z5')
  })

  it('handles null and undefined', () => {
    expect(formatGSTIN(null)).toBe('-')
  })
})

// =============================================================================
// String Utility Tests
// =============================================================================

describe('truncate', () => {
  it('truncates long text with ellipsis', () => {
    expect(truncate('This is a very long text', 10)).toBe('This is...')
  })

  it('does not truncate short text', () => {
    expect(truncate('Short', 10)).toBe('Short')
  })
})

describe('capitalize', () => {
  it('capitalizes first letter', () => {
    expect(capitalize('hello')).toBe('Hello')
    expect(capitalize('HELLO')).toBe('Hello')
  })

  it('handles empty string', () => {
    expect(capitalize('')).toBe('')
  })
})

describe('snakeToTitle', () => {
  it('converts snake_case to Title Case', () => {
    expect(snakeToTitle('employee_status')).toBe('Employee Status')
    expect(snakeToTitle('date_of_birth')).toBe('Date Of Birth')
  })
})

describe('pluralize', () => {
  it('returns singular for count 1', () => {
    expect(pluralize(1, 'employee')).toBe('employee')
    expect(pluralize(1, 'day')).toBe('day')
  })

  it('returns plural for count > 1', () => {
    expect(pluralize(2, 'employee')).toBe('employees')
    expect(pluralize(5, 'day')).toBe('days')
  })

  it('supports custom plural', () => {
    expect(pluralize(2, 'person', 'people')).toBe('people')
  })
})
