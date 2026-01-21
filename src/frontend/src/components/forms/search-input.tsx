"use client"

import * as React from "react"
import { cn } from "@/lib/utils"
import { Search, X } from "lucide-react"
import { useDebounce } from "@/hooks"

// ============================================================================
// Search Input Component
// ============================================================================

interface SearchInputProps {
  value?: string
  onChange?: (value: string) => void
  onSearch?: (value: string) => void
  placeholder?: string
  debounceMs?: number
  className?: string
  showClearButton?: boolean
  autoFocus?: boolean
}

export function SearchInput({
  value: controlledValue,
  onChange,
  onSearch,
  placeholder = "Search...",
  debounceMs = 300,
  className,
  showClearButton = true,
  autoFocus = false
}: SearchInputProps) {
  const [internalValue, setInternalValue] = React.useState(controlledValue || '')
  const debouncedValue = useDebounce(internalValue, debounceMs)

  // Sync with controlled value
  React.useEffect(() => {
    if (controlledValue !== undefined) {
      setInternalValue(controlledValue)
    }
  }, [controlledValue])

  // Trigger search on debounced value change
  React.useEffect(() => {
    onSearch?.(debouncedValue)
  }, [debouncedValue, onSearch])

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value
    setInternalValue(newValue)
    onChange?.(newValue)
  }

  const handleClear = () => {
    setInternalValue('')
    onChange?.('')
    onSearch?.('')
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      onSearch?.(internalValue)
    }
    if (e.key === 'Escape') {
      handleClear()
    }
  }

  return (
    <div className={cn("relative", className)}>
      <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
      <input
        type="search"
        value={internalValue}
        onChange={handleChange}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        autoFocus={autoFocus}
        className={cn(
          "flex h-10 w-full rounded-md border border-input bg-background pl-10 pr-10 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
        )}
      />
      {showClearButton && internalValue && (
        <button
          type="button"
          onClick={handleClear}
          className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
        >
          <X className="h-4 w-4" />
          <span className="sr-only">Clear search</span>
        </button>
      )}
    </div>
  )
}

export default SearchInput
