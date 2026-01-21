// GanaPortal Formatting Utilities
// FE-001: India-specific Formatting

// ============================================================================
// Currency Formatting (INR)
// ============================================================================

/**
 * Format number as Indian Rupees
 * Uses Indian numbering system: 1,00,00,000
 */
export function formatCurrency(
  amount: number | null | undefined,
  options: {
    showSymbol?: boolean
    decimals?: number
    showSign?: boolean
  } = {}
): string {
  if (amount === null || amount === undefined) return '-'

  const { showSymbol = true, decimals = 2, showSign = false } = options

  const sign = showSign && amount > 0 ? '+' : ''
  const absAmount = Math.abs(amount)

  // Format with Indian numbering system
  const formatted = formatIndianNumber(absAmount, decimals)

  const prefix = showSymbol ? '₹' : ''
  const negativeSign = amount < 0 ? '-' : ''

  return `${negativeSign}${sign}${prefix}${formatted}`
}

/**
 * Format number in Indian numbering system
 * 1,00,00,000 format (lakhs and crores)
 */
export function formatIndianNumber(num: number, decimals: number = 2): string {
  const parts = num.toFixed(decimals).split('.')
  const integerPart = parts[0]
  const decimalPart = parts[1]

  // Indian numbering: last 3 digits, then groups of 2
  const lastThree = integerPart.slice(-3)
  const otherNumbers = integerPart.slice(0, -3)

  const formatted = otherNumbers !== ''
    ? otherNumbers.replace(/\B(?=(\d{2})+(?!\d))/g, ',') + ',' + lastThree
    : lastThree

  return decimals > 0 ? formatted + '.' + decimalPart : formatted
}

/**
 * Format as Lakhs (1,00,000)
 */
export function formatLakhs(amount: number): string {
  return (amount / 100000).toFixed(2) + ' L'
}

/**
 * Format as Crores (1,00,00,000)
 */
export function formatCrores(amount: number): string {
  return (amount / 10000000).toFixed(2) + ' Cr'
}

/**
 * Smart currency format - auto-selects format based on amount
 */
export function formatCurrencySmart(amount: number): string {
  if (amount >= 10000000) {
    return '₹' + formatCrores(amount)
  }
  if (amount >= 100000) {
    return '₹' + formatLakhs(amount)
  }
  return formatCurrency(amount)
}

// ============================================================================
// Date Formatting
// ============================================================================

/**
 * Format date in Indian format: DD/MM/YYYY
 */
export function formatDate(
  date: string | Date | null | undefined,
  options: {
    format?: 'short' | 'long' | 'iso'
    showTime?: boolean
  } = {}
): string {
  if (!date) return '-'

  const { format = 'short', showTime = false } = options
  const d = typeof date === 'string' ? new Date(date) : date

  if (isNaN(d.getTime())) return '-'

  const day = d.getDate().toString().padStart(2, '0')
  const month = (d.getMonth() + 1).toString().padStart(2, '0')
  const year = d.getFullYear()

  const months = [
    'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'
  ]

  let formatted: string

  switch (format) {
    case 'long':
      formatted = `${day} ${months[d.getMonth()]} ${year}`
      break
    case 'iso':
      formatted = `${year}-${month}-${day}`
      break
    case 'short':
    default:
      formatted = `${day}/${month}/${year}`
  }

  if (showTime) {
    const hours = d.getHours().toString().padStart(2, '0')
    const minutes = d.getMinutes().toString().padStart(2, '0')
    formatted += ` ${hours}:${minutes}`
  }

  return formatted
}

/**
 * Format time in 12-hour format
 */
export function formatTime(date: string | Date | null | undefined): string {
  if (!date) return '-'

  const d = typeof date === 'string' ? new Date(date) : date
  if (isNaN(d.getTime())) return '-'

  const hours = d.getHours()
  const minutes = d.getMinutes().toString().padStart(2, '0')
  const ampm = hours >= 12 ? 'PM' : 'AM'
  const hour12 = hours % 12 || 12

  return `${hour12}:${minutes} ${ampm}`
}

/**
 * Format relative time (e.g., "2 hours ago")
 */
export function formatRelativeTime(date: string | Date): string {
  const d = typeof date === 'string' ? new Date(date) : date
  const now = new Date()
  const diffMs = now.getTime() - d.getTime()
  const diffSecs = Math.floor(diffMs / 1000)
  const diffMins = Math.floor(diffSecs / 60)
  const diffHours = Math.floor(diffMins / 60)
  const diffDays = Math.floor(diffHours / 24)

  if (diffSecs < 60) return 'Just now'
  if (diffMins < 60) return `${diffMins} minute${diffMins > 1 ? 's' : ''} ago`
  if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`
  if (diffDays < 7) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`

  return formatDate(d)
}

/**
 * Get month name
 */
export function getMonthName(month: number, short: boolean = false): string {
  const months = short
    ? ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    : ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

  return months[month - 1] || ''
}

/**
 * Get financial year label (Indian FY: Apr-Mar)
 */
export function getFinancialYear(date?: Date): string {
  const d = date || new Date()
  const year = d.getFullYear()
  const month = d.getMonth() // 0-indexed

  // FY starts in April (month 3)
  if (month >= 3) {
    return `FY ${year}-${(year + 1).toString().slice(-2)}`
  }
  return `FY ${year - 1}-${year.toString().slice(-2)}`
}

// ============================================================================
// Number Formatting
// ============================================================================

/**
 * Format number with commas
 */
export function formatNumber(num: number | null | undefined): string {
  if (num === null || num === undefined) return '-'
  return formatIndianNumber(num, 0)
}

/**
 * Format percentage
 */
export function formatPercentage(
  value: number | null | undefined,
  decimals: number = 2
): string {
  if (value === null || value === undefined) return '-'
  return value.toFixed(decimals) + '%'
}

/**
 * Format phone number (Indian format)
 */
export function formatPhone(phone: string | null | undefined): string {
  if (!phone) return '-'

  // Remove all non-digits
  const digits = phone.replace(/\D/g, '')

  // Format as +91 XXXXX XXXXX
  if (digits.length === 10) {
    return `+91 ${digits.slice(0, 5)} ${digits.slice(5)}`
  }
  if (digits.length === 12 && digits.startsWith('91')) {
    return `+${digits.slice(0, 2)} ${digits.slice(2, 7)} ${digits.slice(7)}`
  }

  return phone
}

/**
 * Format PAN number (uppercase, add spaces)
 */
export function formatPAN(pan: string | null | undefined): string {
  if (!pan) return '-'
  return pan.toUpperCase()
}

/**
 * Format GSTIN
 */
export function formatGSTIN(gstin: string | null | undefined): string {
  if (!gstin) return '-'
  return gstin.toUpperCase()
}

// ============================================================================
// Utility Functions
// ============================================================================

/**
 * Truncate text with ellipsis
 */
export function truncate(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text
  return text.slice(0, maxLength - 3) + '...'
}

/**
 * Capitalize first letter
 */
export function capitalize(text: string): string {
  if (!text) return ''
  return text.charAt(0).toUpperCase() + text.slice(1).toLowerCase()
}

/**
 * Convert snake_case to Title Case
 */
export function snakeToTitle(text: string): string {
  return text
    .split('_')
    .map((word) => capitalize(word))
    .join(' ')
}

/**
 * Pluralize word
 */
export function pluralize(count: number, singular: string, plural?: string): string {
  return count === 1 ? singular : (plural || singular + 's')
}
