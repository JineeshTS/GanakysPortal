"use client"

import { create } from 'zustand'

// ============================================================================
// Toast Types
// ============================================================================

export interface Toast {
  id: string
  title: string
  description?: string
  type: 'success' | 'error' | 'warning' | 'info'
  duration?: number
}

interface ToastState {
  toasts: Toast[]
  addToast: (toast: Omit<Toast, 'id'>) => void
  removeToast: (id: string) => void
  clearToasts: () => void
}

// ============================================================================
// Toast Store
// ============================================================================

export const useToastStore = create<ToastState>((set) => ({
  toasts: [],

  addToast: (toast) => {
    const id = `toast-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
    const newToast: Toast = { ...toast, id }

    set((state) => ({
      toasts: [...state.toasts, newToast]
    }))

    // Auto remove after duration (default 5 seconds)
    const duration = toast.duration ?? 5000
    if (duration > 0) {
      setTimeout(() => {
        set((state) => ({
          toasts: state.toasts.filter((t) => t.id !== id)
        }))
      }, duration)
    }
  },

  removeToast: (id) => {
    set((state) => ({
      toasts: state.toasts.filter((t) => t.id !== id)
    }))
  },

  clearToasts: () => {
    set({ toasts: [] })
  }
}))

// ============================================================================
// Toast Hook
// ============================================================================

export function useToast() {
  const { addToast, removeToast, clearToasts, toasts } = useToastStore()

  const toast = {
    success: (title: string, description?: string) => {
      addToast({ type: 'success', title, description })
    },

    error: (title: string, description?: string) => {
      addToast({ type: 'error', title, description, duration: 8000 })
    },

    warning: (title: string, description?: string) => {
      addToast({ type: 'warning', title, description })
    },

    info: (title: string, description?: string) => {
      addToast({ type: 'info', title, description })
    },

    custom: (toast: Omit<Toast, 'id'>) => {
      addToast(toast)
    },

    dismiss: (id: string) => {
      removeToast(id)
    },

    dismissAll: () => {
      clearToasts()
    }
  }

  // Helper function for simplified usage: showToast('success', 'Title', 'Description')
  const showToast = (type: 'success' | 'error' | 'warning' | 'info', title: string, description?: string) => {
    addToast({ type, title, description, duration: type === 'error' ? 8000 : 5000 })
  }

  return { toast, toasts, showToast }
}

// ============================================================================
// API Error Toast Helper
// ============================================================================

export function showApiError(error: unknown, fallbackMessage: string = 'An error occurred') {
  const { addToast } = useToastStore.getState()

  let message = fallbackMessage

  if (error instanceof Error) {
    message = error.message
  } else if (typeof error === 'string') {
    message = error
  } else if (error && typeof error === 'object' && 'detail' in error) {
    message = String((error as { detail: unknown }).detail)
  }

  addToast({
    type: 'error',
    title: 'Error',
    description: message,
    duration: 8000
  })
}
