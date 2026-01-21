"use client"

import * as React from "react"
import { cn } from "@/lib/utils"
import { useToastStore, type Toast } from "@/hooks/use-toast"
import { X, CheckCircle, AlertCircle, AlertTriangle, Info } from "lucide-react"

// ============================================================================
// Toast Provider Component
// ============================================================================

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const { toasts, removeToast } = useToastStore()

  return (
    <>
      {children}
      <ToastContainer toasts={toasts} onDismiss={removeToast} />
    </>
  )
}

// ============================================================================
// Toast Container Component
// ============================================================================

interface ToastContainerProps {
  toasts: Toast[]
  onDismiss: (id: string) => void
}

function ToastContainer({ toasts, onDismiss }: ToastContainerProps) {
  if (toasts.length === 0) return null

  return (
    <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2 max-w-md w-full pointer-events-none">
      {toasts.map((toast) => (
        <ToastItem key={toast.id} toast={toast} onDismiss={onDismiss} />
      ))}
    </div>
  )
}

// ============================================================================
// Toast Item Component
// ============================================================================

interface ToastItemProps {
  toast: Toast
  onDismiss: (id: string) => void
}

function ToastItem({ toast, onDismiss }: ToastItemProps) {
  const icons = {
    success: CheckCircle,
    error: AlertCircle,
    warning: AlertTriangle,
    info: Info
  }

  const colors = {
    success: 'border-green-500 bg-green-50 text-green-900 dark:bg-green-950 dark:text-green-100',
    error: 'border-red-500 bg-red-50 text-red-900 dark:bg-red-950 dark:text-red-100',
    warning: 'border-yellow-500 bg-yellow-50 text-yellow-900 dark:bg-yellow-950 dark:text-yellow-100',
    info: 'border-blue-500 bg-blue-50 text-blue-900 dark:bg-blue-950 dark:text-blue-100'
  }

  const iconColors = {
    success: 'text-green-500',
    error: 'text-red-500',
    warning: 'text-yellow-500',
    info: 'text-blue-500'
  }

  const Icon = icons[toast.type]

  return (
    <div
      className={cn(
        "pointer-events-auto flex items-start gap-3 rounded-lg border-l-4 p-4 shadow-lg animate-in slide-in-from-right-full duration-300",
        colors[toast.type]
      )}
      role="alert"
    >
      <Icon className={cn("h-5 w-5 flex-shrink-0 mt-0.5", iconColors[toast.type])} />

      <div className="flex-1 min-w-0">
        <p className="font-medium">{toast.title}</p>
        {toast.description && (
          <p className="mt-1 text-sm opacity-90">{toast.description}</p>
        )}
      </div>

      <button
        onClick={() => onDismiss(toast.id)}
        className="flex-shrink-0 rounded-md p-1 hover:bg-black/10 dark:hover:bg-white/10 transition-colors"
      >
        <X className="h-4 w-4" />
        <span className="sr-only">Dismiss</span>
      </button>
    </div>
  )
}

export default ToastProvider
