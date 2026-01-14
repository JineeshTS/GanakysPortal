"use client"

import * as React from "react"
import { cn } from "@/lib/utils"
import { Label } from "@/components/ui/label"
import { AlertCircle } from "lucide-react"

// ============================================================================
// Currency Input Component (INR)
// ============================================================================

interface CurrencyInputProps {
  label: string
  name: string
  value?: number
  onChange?: (value: number | undefined) => void
  error?: string
  hint?: string
  required?: boolean
  min?: number
  max?: number
  disabled?: boolean
  placeholder?: string
  currency?: string
  className?: string
  containerClassName?: string
}

export function CurrencyInput({
  label,
  name,
  value,
  onChange,
  error,
  hint,
  required,
  min,
  max,
  disabled,
  placeholder = "0.00",
  currency = "₹",
  className,
  containerClassName
}: CurrencyInputProps) {
  const [displayValue, setDisplayValue] = React.useState<string>('')

  // Format number for display
  React.useEffect(() => {
    if (value !== undefined && value !== null) {
      setDisplayValue(formatIndianNumber(value))
    } else {
      setDisplayValue('')
    }
  }, [value])

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const rawValue = e.target.value.replace(/[^0-9.]/g, '')

    // Allow only one decimal point
    const parts = rawValue.split('.')
    let cleanValue = parts[0]
    if (parts.length > 1) {
      cleanValue += '.' + parts[1].slice(0, 2) // Max 2 decimal places
    }

    setDisplayValue(cleanValue)

    const numericValue = parseFloat(cleanValue)
    if (!isNaN(numericValue)) {
      onChange?.(numericValue)
    } else if (cleanValue === '') {
      onChange?.(undefined)
    }
  }

  const handleBlur = () => {
    if (value !== undefined && value !== null) {
      setDisplayValue(formatIndianNumber(value))
    }
  }

  const handleFocus = () => {
    if (value !== undefined && value !== null) {
      setDisplayValue(String(value))
    }
  }

  return (
    <div className={cn("space-y-2", containerClassName)}>
      <Label htmlFor={name} className="flex items-center gap-1">
        {label}
        {required && <span className="text-destructive">*</span>}
      </Label>
      <div className="relative">
        <span className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground">
          {currency}
        </span>
        <input
          type="text"
          inputMode="decimal"
          id={name}
          name={name}
          value={displayValue}
          onChange={handleChange}
          onBlur={handleBlur}
          onFocus={handleFocus}
          disabled={disabled}
          placeholder={placeholder}
          className={cn(
            "flex h-10 w-full rounded-md border border-input bg-background pl-8 pr-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 text-right",
            error && "border-destructive focus-visible:ring-destructive",
            className
          )}
          aria-invalid={!!error}
          aria-describedby={error ? `${name}-error` : hint ? `${name}-hint` : undefined}
        />
      </div>
      {error && (
        <p id={`${name}-error`} className="text-sm text-destructive flex items-center gap-1">
          <AlertCircle className="h-3 w-3" />
          {error}
        </p>
      )}
      {hint && !error && (
        <p id={`${name}-hint`} className="text-sm text-muted-foreground">
          {hint}
        </p>
      )}
    </div>
  )
}

// ============================================================================
// Percentage Input Component
// ============================================================================

interface PercentageInputProps {
  label: string
  name: string
  value?: number
  onChange?: (value: number | undefined) => void
  error?: string
  hint?: string
  required?: boolean
  min?: number
  max?: number
  disabled?: boolean
  placeholder?: string
  className?: string
  containerClassName?: string
}

export function PercentageInput({
  label,
  name,
  value,
  onChange,
  error,
  hint,
  required,
  min = 0,
  max = 100,
  disabled,
  placeholder = "0.00",
  className,
  containerClassName
}: PercentageInputProps) {
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const rawValue = e.target.value.replace(/[^0-9.]/g, '')

    const parts = rawValue.split('.')
    let cleanValue = parts[0]
    if (parts.length > 1) {
      cleanValue += '.' + parts[1].slice(0, 2)
    }

    const numericValue = parseFloat(cleanValue)
    if (!isNaN(numericValue)) {
      const clampedValue = Math.min(Math.max(numericValue, min), max)
      onChange?.(clampedValue)
    } else if (cleanValue === '') {
      onChange?.(undefined)
    }
  }

  return (
    <div className={cn("space-y-2", containerClassName)}>
      <Label htmlFor={name} className="flex items-center gap-1">
        {label}
        {required && <span className="text-destructive">*</span>}
      </Label>
      <div className="relative">
        <input
          type="text"
          inputMode="decimal"
          id={name}
          name={name}
          value={value !== undefined ? String(value) : ''}
          onChange={handleChange}
          disabled={disabled}
          placeholder={placeholder}
          className={cn(
            "flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 pr-8 text-right",
            error && "border-destructive focus-visible:ring-destructive",
            className
          )}
          aria-invalid={!!error}
          aria-describedby={error ? `${name}-error` : hint ? `${name}-hint` : undefined}
        />
        <span className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground">
          %
        </span>
      </div>
      {error && (
        <p id={`${name}-error`} className="text-sm text-destructive flex items-center gap-1">
          <AlertCircle className="h-3 w-3" />
          {error}
        </p>
      )}
      {hint && !error && (
        <p id={`${name}-hint`} className="text-sm text-muted-foreground">
          {hint}
        </p>
      )}
    </div>
  )
}

// ============================================================================
// Helper: Format number in Indian numbering system
// ============================================================================

function formatIndianNumber(num: number): string {
  const parts = num.toFixed(2).split('.')
  const integerPart = parts[0]
  const decimalPart = parts[1]

  // Indian numbering: 1,00,00,000 format
  const lastThree = integerPart.slice(-3)
  const otherNumbers = integerPart.slice(0, -3)

  const formatted = otherNumbers !== ''
    ? otherNumbers.replace(/\B(?=(\d{2})+(?!\d))/g, ',') + ',' + lastThree
    : lastThree

  return formatted + '.' + decimalPart
}

export default CurrencyInput
