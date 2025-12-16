/**
 * Format Utility Tests
 * WBS Reference: Task 30.1.2.1.3
 */
import { describe, it, expect } from 'vitest';

// Format utilities to test
const formatCurrency = (
  amount: number,
  currency: string = 'INR',
  locale: string = 'en-IN'
): string => {
  return new Intl.NumberFormat(locale, {
    style: 'currency',
    currency,
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(amount);
};

const formatDate = (
  date: string | Date,
  options?: Intl.DateTimeFormatOptions
): string => {
  const d = typeof date === 'string' ? new Date(date) : date;
  return d.toLocaleDateString('en-IN', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
    ...options,
  });
};

const formatNumber = (
  num: number,
  decimals: number = 0,
  locale: string = 'en-IN'
): string => {
  return new Intl.NumberFormat(locale, {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(num);
};

const formatPercentage = (value: number, decimals: number = 1): string => {
  return `${value.toFixed(decimals)}%`;
};

const maskPAN = (pan: string): string => {
  if (pan.length < 6) return pan;
  return pan.slice(0, 5) + '****' + pan.slice(-1);
};

const maskAadhaar = (aadhaar: string): string => {
  if (aadhaar.length < 4) return aadhaar;
  return 'XXXX-XXXX-' + aadhaar.slice(-4);
};

const maskBankAccount = (account: string): string => {
  if (account.length < 4) return account;
  return 'X'.repeat(account.length - 4) + account.slice(-4);
};

const truncateText = (text: string, maxLength: number): string => {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength - 3) + '...';
};

describe('Currency Formatting', () => {
  it('formats INR currency correctly', () => {
    expect(formatCurrency(1000)).toBe('₹1,000.00');
    expect(formatCurrency(1234567.89)).toBe('₹12,34,567.89');
    expect(formatCurrency(0)).toBe('₹0.00');
  });

  it('formats large amounts with Indian numbering', () => {
    expect(formatCurrency(100000)).toBe('₹1,00,000.00');
    expect(formatCurrency(10000000)).toBe('₹1,00,00,000.00');
  });

  it('handles negative amounts', () => {
    expect(formatCurrency(-5000)).toBe('-₹5,000.00');
  });

  it('formats USD correctly', () => {
    expect(formatCurrency(1000, 'USD', 'en-US')).toBe('$1,000.00');
  });
});

describe('Date Formatting', () => {
  it('formats date in Indian format', () => {
    const result = formatDate('2025-01-15');
    expect(result).toBe('15 Jan 2025');
  });

  it('formats Date objects', () => {
    const date = new Date(2025, 11, 25); // December 25, 2025
    const result = formatDate(date);
    expect(result).toBe('25 Dec 2025');
  });

  it('formats with custom options', () => {
    const result = formatDate('2025-06-20', {
      day: 'numeric',
      month: 'long',
      year: 'numeric',
    });
    expect(result).toBe('20 June 2025');
  });
});

describe('Number Formatting', () => {
  it('formats integers with Indian numbering', () => {
    expect(formatNumber(1000000)).toBe('10,00,000');
    expect(formatNumber(123456789)).toBe('12,34,56,789');
  });

  it('formats with decimal places', () => {
    expect(formatNumber(1234.5678, 2)).toBe('1,234.57');
    expect(formatNumber(1000, 2)).toBe('1,000.00');
  });

  it('handles zero', () => {
    expect(formatNumber(0)).toBe('0');
    expect(formatNumber(0, 2)).toBe('0.00');
  });
});

describe('Percentage Formatting', () => {
  it('formats percentage with decimals', () => {
    expect(formatPercentage(85.5)).toBe('85.5%');
    expect(formatPercentage(100)).toBe('100.0%');
  });

  it('formats with custom decimal places', () => {
    expect(formatPercentage(75.555, 2)).toBe('75.56%');
    expect(formatPercentage(50, 0)).toBe('50%');
  });
});

describe('PAN Masking', () => {
  it('masks PAN correctly', () => {
    expect(maskPAN('ABCDE1234F')).toBe('ABCDE****F');
  });

  it('handles short PAN', () => {
    expect(maskPAN('ABC')).toBe('ABC');
  });
});

describe('Aadhaar Masking', () => {
  it('masks Aadhaar correctly', () => {
    expect(maskAadhaar('123456789012')).toBe('XXXX-XXXX-9012');
  });

  it('handles short input', () => {
    expect(maskAadhaar('123')).toBe('123');
  });
});

describe('Bank Account Masking', () => {
  it('masks bank account correctly', () => {
    expect(maskBankAccount('1234567890')).toBe('XXXXXX7890');
    expect(maskBankAccount('9876543210123456')).toBe('XXXXXXXXXXXX3456');
  });

  it('handles short account number', () => {
    expect(maskBankAccount('123')).toBe('123');
  });
});

describe('Text Truncation', () => {
  it('truncates long text', () => {
    expect(truncateText('This is a very long text', 15)).toBe('This is a ve...');
  });

  it('does not truncate short text', () => {
    expect(truncateText('Short', 10)).toBe('Short');
  });

  it('handles exact length', () => {
    expect(truncateText('Exact', 5)).toBe('Exact');
  });
});
