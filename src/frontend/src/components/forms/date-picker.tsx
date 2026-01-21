"use client"

import * as React from "react"
import { cn } from "@/lib/utils"
import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/button"
import { Calendar, ChevronLeft, ChevronRight, AlertCircle } from "lucide-react"

// ============================================================================
// Date Picker Component (Native with custom styling)
// ============================================================================

interface DatePickerProps {
  label: string
  name: string
  value?: string
  onChange?: (date: string) => void
  error?: string
  hint?: string
  required?: boolean
  min?: string
  max?: string
  disabled?: boolean
  className?: string
  containerClassName?: string
}

export function DatePicker({
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
  className,
  containerClassName
}: DatePickerProps) {
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    onChange?.(e.target.value)
  }

  return (
    <div className={cn("space-y-2", containerClassName)}>
      <Label htmlFor={name} className="flex items-center gap-1">
        {label}
        {required && <span className="text-destructive">*</span>}
      </Label>
      <div className="relative">
        <input
          type="date"
          id={name}
          name={name}
          value={value || ''}
          onChange={handleChange}
          min={min}
          max={max}
          disabled={disabled}
          className={cn(
            "flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50",
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
// Date Range Picker Component
// ============================================================================

interface DateRangePickerProps {
  label: string
  name: string
  startValue?: string
  endValue?: string
  onStartChange?: (date: string) => void
  onEndChange?: (date: string) => void
  error?: string
  required?: boolean
  disabled?: boolean
  className?: string
  containerClassName?: string
}

export function DateRangePicker({
  label,
  name,
  startValue,
  endValue,
  onStartChange,
  onEndChange,
  error,
  required,
  disabled,
  className,
  containerClassName
}: DateRangePickerProps) {
  return (
    <div className={cn("space-y-2", containerClassName)}>
      <Label className="flex items-center gap-1">
        {label}
        {required && <span className="text-destructive">*</span>}
      </Label>
      <div className={cn("flex items-center gap-2", className)}>
        <input
          type="date"
          id={`${name}-start`}
          name={`${name}-start`}
          value={startValue || ''}
          onChange={(e) => onStartChange?.(e.target.value)}
          max={endValue}
          disabled={disabled}
          className={cn(
            "flex h-10 flex-1 rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50",
            error && "border-destructive"
          )}
          aria-invalid={!!error}
        />
        <span className="text-muted-foreground">to</span>
        <input
          type="date"
          id={`${name}-end`}
          name={`${name}-end`}
          value={endValue || ''}
          onChange={(e) => onEndChange?.(e.target.value)}
          min={startValue}
          disabled={disabled}
          className={cn(
            "flex h-10 flex-1 rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50",
            error && "border-destructive"
          )}
          aria-invalid={!!error}
        />
      </div>
      {error && (
        <p className="text-sm text-destructive flex items-center gap-1">
          <AlertCircle className="h-3 w-3" />
          {error}
        </p>
      )}
    </div>
  )
}

// ============================================================================
// Month Year Picker Component (for Payroll)
// ============================================================================

interface MonthYearPickerProps {
  label: string
  name: string
  month?: number
  year?: number
  onMonthChange?: (month: number) => void
  onYearChange?: (year: number) => void
  error?: string
  required?: boolean
  disabled?: boolean
  className?: string
  containerClassName?: string
}

const months = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December'
]

export function MonthYearPicker({
  label,
  name,
  month,
  year,
  onMonthChange,
  onYearChange,
  error,
  required,
  disabled,
  className,
  containerClassName
}: MonthYearPickerProps) {
  const currentYear = new Date().getFullYear()
  const years = Array.from({ length: 10 }, (_, i) => currentYear - 5 + i)

  const handlePrevMonth = () => {
    if (!month || !year) return

    if (month === 1) {
      onMonthChange?.(12)
      onYearChange?.(year - 1)
    } else {
      onMonthChange?.(month - 1)
    }
  }

  const handleNextMonth = () => {
    if (!month || !year) return

    if (month === 12) {
      onMonthChange?.(1)
      onYearChange?.(year + 1)
    } else {
      onMonthChange?.(month + 1)
    }
  }

  return (
    <div className={cn("space-y-2", containerClassName)}>
      <Label className="flex items-center gap-1">
        {label}
        {required && <span className="text-destructive">*</span>}
      </Label>
      <div className={cn("flex items-center gap-2", className)}>
        <Button
          type="button"
          variant="outline"
          size="icon"
          onClick={handlePrevMonth}
          disabled={disabled}
        >
          <ChevronLeft className="h-4 w-4" />
        </Button>

        <select
          id={`${name}-month`}
          name={`${name}-month`}
          value={month || ''}
          onChange={(e) => onMonthChange?.(Number(e.target.value))}
          disabled={disabled}
          className={cn(
            "flex h-10 flex-1 rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50",
            error && "border-destructive"
          )}
        >
          <option value="">Select Month</option>
          {months.map((m, i) => (
            <option key={i} value={i + 1}>{m}</option>
          ))}
        </select>

        <select
          id={`${name}-year`}
          name={`${name}-year`}
          value={year || ''}
          onChange={(e) => onYearChange?.(Number(e.target.value))}
          disabled={disabled}
          className={cn(
            "flex h-10 w-24 rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50",
            error && "border-destructive"
          )}
        >
          <option value="">Year</option>
          {years.map((y) => (
            <option key={y} value={y}>{y}</option>
          ))}
        </select>

        <Button
          type="button"
          variant="outline"
          size="icon"
          onClick={handleNextMonth}
          disabled={disabled}
        >
          <ChevronRight className="h-4 w-4" />
        </Button>
      </div>
      {error && (
        <p className="text-sm text-destructive flex items-center gap-1">
          <AlertCircle className="h-3 w-3" />
          {error}
        </p>
      )}
    </div>
  )
}

export default DatePicker
