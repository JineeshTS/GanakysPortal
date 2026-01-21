"use client"

import * as React from "react"
import { cn } from "@/lib/utils"
import { Label } from "@/components/ui/label"
import { Input } from "@/components/ui/input"
import { AlertCircle } from "lucide-react"

// ============================================================================
// Form Field Component
// ============================================================================

interface FormFieldProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label: string
  name: string
  error?: string
  hint?: string
  required?: boolean
  containerClassName?: string
}

export const FormField = React.forwardRef<HTMLInputElement, FormFieldProps>(
  ({ label, name, error, hint, required, containerClassName, className, ...props }, ref) => {
    return (
      <div className={cn("space-y-2", containerClassName)}>
        <Label htmlFor={name} className="flex items-center gap-1">
          {label}
          {required && <span className="text-destructive">*</span>}
        </Label>
        <Input
          ref={ref}
          id={name}
          name={name}
          className={cn(
            error && "border-destructive focus-visible:ring-destructive",
            className
          )}
          aria-invalid={!!error}
          aria-describedby={error ? `${name}-error` : hint ? `${name}-hint` : undefined}
          {...props}
        />
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
)

FormField.displayName = "FormField"

// ============================================================================
// Form Textarea Component
// ============================================================================

interface FormTextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  label: string
  name: string
  error?: string
  hint?: string
  required?: boolean
  containerClassName?: string
}

export const FormTextarea = React.forwardRef<HTMLTextAreaElement, FormTextareaProps>(
  ({ label, name, error, hint, required, containerClassName, className, ...props }, ref) => {
    return (
      <div className={cn("space-y-2", containerClassName)}>
        <Label htmlFor={name} className="flex items-center gap-1">
          {label}
          {required && <span className="text-destructive">*</span>}
        </Label>
        <textarea
          ref={ref}
          id={name}
          name={name}
          className={cn(
            "flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50",
            error && "border-destructive focus-visible:ring-destructive",
            className
          )}
          aria-invalid={!!error}
          aria-describedby={error ? `${name}-error` : hint ? `${name}-hint` : undefined}
          {...props}
        />
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
)

FormTextarea.displayName = "FormTextarea"

// ============================================================================
// Form Select Component
// ============================================================================

interface SelectOption {
  value: string
  label: string
  disabled?: boolean
}

interface FormSelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  label: string
  name: string
  options: SelectOption[]
  error?: string
  hint?: string
  required?: boolean
  placeholder?: string
  containerClassName?: string
}

export const FormSelect = React.forwardRef<HTMLSelectElement, FormSelectProps>(
  ({ label, name, options, error, hint, required, placeholder, containerClassName, className, ...props }, ref) => {
    return (
      <div className={cn("space-y-2", containerClassName)}>
        <Label htmlFor={name} className="flex items-center gap-1">
          {label}
          {required && <span className="text-destructive">*</span>}
        </Label>
        <select
          ref={ref}
          id={name}
          name={name}
          className={cn(
            "flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50",
            error && "border-destructive focus-visible:ring-destructive",
            className
          )}
          aria-invalid={!!error}
          aria-describedby={error ? `${name}-error` : hint ? `${name}-hint` : undefined}
          {...props}
        >
          {placeholder && (
            <option value="" disabled>
              {placeholder}
            </option>
          )}
          {options.map((option) => (
            <option key={option.value} value={option.value} disabled={option.disabled}>
              {option.label}
            </option>
          ))}
        </select>
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
)

FormSelect.displayName = "FormSelect"

// ============================================================================
// Form Checkbox Component
// ============================================================================

interface FormCheckboxProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'type'> {
  label: string
  name: string
  description?: string
  error?: string
  containerClassName?: string
}

export const FormCheckbox = React.forwardRef<HTMLInputElement, FormCheckboxProps>(
  ({ label, name, description, error, containerClassName, className, ...props }, ref) => {
    return (
      <div className={cn("space-y-2", containerClassName)}>
        <div className="flex items-start gap-3">
          <input
            ref={ref}
            type="checkbox"
            id={name}
            name={name}
            className={cn(
              "h-4 w-4 rounded border-input text-primary focus:ring-ring focus:ring-offset-2",
              error && "border-destructive",
              className
            )}
            aria-invalid={!!error}
            aria-describedby={error ? `${name}-error` : description ? `${name}-desc` : undefined}
            {...props}
          />
          <div className="space-y-1">
            <Label htmlFor={name} className="text-sm font-medium leading-none">
              {label}
            </Label>
            {description && (
              <p id={`${name}-desc`} className="text-sm text-muted-foreground">
                {description}
              </p>
            )}
          </div>
        </div>
        {error && (
          <p id={`${name}-error`} className="text-sm text-destructive flex items-center gap-1 ml-7">
            <AlertCircle className="h-3 w-3" />
            {error}
          </p>
        )}
      </div>
    )
  }
)

FormCheckbox.displayName = "FormCheckbox"

export default FormField
