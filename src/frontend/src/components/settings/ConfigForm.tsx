"use client"

import * as React from "react"
import { cn } from "@/lib/utils"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import { Input } from "@/components/ui/input"
import { AlertCircle, CheckCircle, Loader2, Save } from "lucide-react"

// ============================================================================
// India-specific Validation Patterns
// ============================================================================

export const INDIA_VALIDATION_PATTERNS = {
  // GSTIN: 2-digit state code + 10-char PAN + 1-char entity number + 'Z' + 1-char checksum
  GSTIN: /^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$/,

  // PAN: 5 letters + 4 digits + 1 letter
  PAN: /^[A-Z]{5}[0-9]{4}[A-Z]{1}$/,

  // TAN: 4 letters + 5 digits + 1 letter
  TAN: /^[A-Z]{4}[0-9]{5}[A-Z]{1}$/,

  // UAN: 12-digit universal account number
  UAN: /^[0-9]{12}$/,

  // ESIC Number: 17-digit number
  ESIC: /^[0-9]{17}$/,

  // PF Establishment Code: XX/XXX/XXXXXXX/XXX/XXXXXXX
  PF_CODE: /^[A-Z]{2}\/[A-Z]{3}\/\d{7}\/\d{3}\/\d{7}$/,

  // PIN Code: 6 digits
  PIN_CODE: /^[1-9][0-9]{5}$/,

  // Mobile: 10 digits starting with 6-9
  MOBILE: /^[6-9][0-9]{9}$/,

  // IFSC Code: 4 letters + 0 + 6 alphanumeric
  IFSC: /^[A-Z]{4}0[A-Z0-9]{6}$/,

  // Bank Account Number: 9-18 digits
  BANK_ACCOUNT: /^[0-9]{9,18}$/,

  // Aadhaar: 12 digits (not starting with 0 or 1)
  AADHAAR: /^[2-9][0-9]{11}$/
}

export function validateIndiaField(value: string, pattern: keyof typeof INDIA_VALIDATION_PATTERNS): boolean {
  return INDIA_VALIDATION_PATTERNS[pattern].test(value)
}

export function getIndiaFieldError(field: keyof typeof INDIA_VALIDATION_PATTERNS, value: string): string | null {
  if (!value) return null

  const errors: Record<string, string> = {
    GSTIN: 'Invalid GSTIN format. Expected format: 22AAAAA0000A1Z5',
    PAN: 'Invalid PAN format. Expected format: ABCDE1234F',
    TAN: 'Invalid TAN format. Expected format: ABCD12345E',
    UAN: 'Invalid UAN. Must be 12 digits',
    ESIC: 'Invalid ESIC number. Must be 17 digits',
    PF_CODE: 'Invalid PF Code. Expected format: XX/XXX/1234567/000/1234567',
    PIN_CODE: 'Invalid PIN code. Must be 6 digits',
    MOBILE: 'Invalid mobile number. Must be 10 digits starting with 6-9',
    IFSC: 'Invalid IFSC code. Expected format: ABCD0123456',
    BANK_ACCOUNT: 'Invalid account number. Must be 9-18 digits',
    AADHAAR: 'Invalid Aadhaar number. Must be 12 digits'
  }

  if (!validateIndiaField(value, field)) {
    return errors[field]
  }

  return null
}

// ============================================================================
// Config Form Component
// ============================================================================

interface ConfigFormProps {
  title: string
  description?: string
  children: React.ReactNode
  onSubmit?: (e: React.FormEvent) => void
  onReset?: () => void
  isLoading?: boolean
  isSaved?: boolean
  isDirty?: boolean
  className?: string
  footer?: React.ReactNode
}

export function ConfigForm({
  title,
  description,
  children,
  onSubmit,
  onReset,
  isLoading = false,
  isSaved = false,
  isDirty = false,
  className,
  footer
}: ConfigFormProps) {
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSubmit?.(e)
  }

  return (
    <Card className={className}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle>{title}</CardTitle>
            {description && <CardDescription className="mt-1">{description}</CardDescription>}
          </div>
          {isSaved && !isDirty && (
            <div className="flex items-center gap-1 text-green-600">
              <CheckCircle className="h-4 w-4" />
              <span className="text-sm">Saved</span>
            </div>
          )}
        </div>
      </CardHeader>
      <form onSubmit={handleSubmit}>
        <CardContent className="space-y-4">
          {children}
        </CardContent>
        {(onSubmit || footer) && (
          <CardFooter className="flex justify-between border-t pt-4">
            {footer || (
              <>
                <div>
                  {onReset && (
                    <Button type="button" variant="ghost" onClick={onReset} disabled={isLoading || !isDirty}>
                      Reset
                    </Button>
                  )}
                </div>
                <Button type="submit" disabled={isLoading || !isDirty}>
                  {isLoading ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Saving...
                    </>
                  ) : (
                    <>
                      <Save className="mr-2 h-4 w-4" />
                      Save Changes
                    </>
                  )}
                </Button>
              </>
            )}
          </CardFooter>
        )}
      </form>
    </Card>
  )
}

// ============================================================================
// Config Form Field Component
// ============================================================================

interface ConfigFormFieldProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label: string
  name: string
  error?: string
  hint?: string
  required?: boolean
  indiaValidation?: keyof typeof INDIA_VALIDATION_PATTERNS
}

export const ConfigFormField = React.forwardRef<HTMLInputElement, ConfigFormFieldProps>(
  ({ label, name, error, hint, required, indiaValidation, className, onChange, ...props }, ref) => {
    const [internalError, setInternalError] = React.useState<string | null>(null)

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      const value = e.target.value.toUpperCase()
      e.target.value = value

      if (indiaValidation && value) {
        const validationError = getIndiaFieldError(indiaValidation, value)
        setInternalError(validationError)
      } else {
        setInternalError(null)
      }

      onChange?.(e)
    }

    const displayError = error || internalError

    return (
      <div className="space-y-2">
        <Label htmlFor={name} className="flex items-center gap-1">
          {label}
          {required && <span className="text-destructive">*</span>}
        </Label>
        <Input
          ref={ref}
          id={name}
          name={name}
          className={cn(
            displayError && "border-destructive focus-visible:ring-destructive",
            indiaValidation && "uppercase",
            className
          )}
          onChange={indiaValidation ? handleChange : onChange}
          aria-invalid={!!displayError}
          aria-describedby={displayError ? `${name}-error` : hint ? `${name}-hint` : undefined}
          {...props}
        />
        {displayError && (
          <p id={`${name}-error`} className="text-sm text-destructive flex items-center gap-1">
            <AlertCircle className="h-3 w-3" />
            {displayError}
          </p>
        )}
        {hint && !displayError && (
          <p id={`${name}-hint`} className="text-sm text-muted-foreground">
            {hint}
          </p>
        )}
      </div>
    )
  }
)

ConfigFormField.displayName = "ConfigFormField"

// ============================================================================
// Config Form Row Component
// ============================================================================

interface ConfigFormRowProps {
  children: React.ReactNode
  columns?: 2 | 3 | 4
  className?: string
}

export function ConfigFormRow({ children, columns = 2, className }: ConfigFormRowProps) {
  const gridCols = {
    2: 'grid-cols-1 md:grid-cols-2',
    3: 'grid-cols-1 md:grid-cols-3',
    4: 'grid-cols-1 md:grid-cols-2 lg:grid-cols-4'
  }

  return (
    <div className={cn("grid gap-4", gridCols[columns], className)}>
      {children}
    </div>
  )
}

// ============================================================================
// Config Toggle Component
// ============================================================================

interface ConfigToggleProps {
  label: string
  description?: string
  checked: boolean
  onChange: (checked: boolean) => void
  disabled?: boolean
}

export function ConfigToggle({ label, description, checked, onChange, disabled }: ConfigToggleProps) {
  return (
    <div className="flex items-center justify-between py-3 border-b last:border-b-0">
      <div className="space-y-0.5">
        <Label className="text-sm font-medium">{label}</Label>
        {description && (
          <p className="text-sm text-muted-foreground">{description}</p>
        )}
      </div>
      <button
        type="button"
        role="switch"
        aria-checked={checked}
        disabled={disabled}
        onClick={() => onChange(!checked)}
        className={cn(
          "relative inline-flex h-6 w-11 items-center rounded-full transition-colors",
          "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2",
          checked ? "bg-primary" : "bg-muted",
          disabled && "opacity-50 cursor-not-allowed"
        )}
      >
        <span
          className={cn(
            "inline-block h-5 w-5 transform rounded-full bg-white shadow-lg transition-transform",
            checked ? "translate-x-5" : "translate-x-0.5"
          )}
        />
      </button>
    </div>
  )
}

export default ConfigForm
