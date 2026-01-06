/**
 * Formatting Utility Functions
 *
 * Centralized formatting utilities for names, currency, and dates.
 */

/**
 * Get initials from a name or names
 * @param nameOrFirstName - Full name string or first name
 * @param lastName - Optional last name (if first parameter is first name)
 * @returns Uppercase initials (2 characters)
 *
 * @example
 * getInitials('John Doe') // 'JD'
 * getInitials('John', 'Doe') // 'JD'
 * getInitials('John') // 'JO'
 * getInitials() // 'U'
 */
export function getInitials(nameOrFirstName?: string, lastName?: string): string {
  // If no name provided, return default
  if (!nameOrFirstName) return 'U';

  // If lastName is provided, use firstName + lastName
  if (lastName) {
    return `${nameOrFirstName.charAt(0)}${lastName.charAt(0)}`.toUpperCase();
  }

  // Otherwise, treat first parameter as full name
  const parts = nameOrFirstName.split(' ');
  return parts.length > 1
    ? `${parts[0][0]}${parts[1][0]}`.toUpperCase()
    : nameOrFirstName.substring(0, 2).toUpperCase();
}

/**
 * Format a number as currency
 * @param amount - The amount to format
 * @param currency - Currency code (default: 'INR')
 * @returns Formatted currency string
 *
 * @example
 * formatCurrency(1000) // '₹1,000'
 * formatCurrency(1500.50, 'USD') // '$1,501'
 */
export function formatCurrency(amount: number, currency: string = 'INR'): string {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency,
    maximumFractionDigits: 0,
  }).format(amount);
}

/**
 * Format a date string or Date object
 * @param date - Date string or Date object to format
 * @param format - Format style ('short' or 'long', default: 'short')
 * @returns Formatted date string
 *
 * @example
 * formatDate('2024-01-15') // '15 Jan 2024'
 * formatDate(new Date()) // '06 Jan 2026'
 * formatDate('2024-01-15', 'long') // 'January 15, 2024'
 */
export function formatDate(date: string | Date, format: 'short' | 'long' = 'short'): string {
  const dateObj = typeof date === 'string' ? new Date(date) : date;

  if (format === 'long') {
    return dateObj.toLocaleDateString('en-IN', {
      day: 'numeric',
      month: 'long',
      year: 'numeric',
    });
  }

  return dateObj.toLocaleDateString('en-IN', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  });
}
